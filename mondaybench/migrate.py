"""Re-stamp recorded evaluations under a later suite release.

WHAT THIS IS. A RE-SCORE, not a re-judge. For every evaluation a release
already holds, it re-reads the SAME recorded verdict file, replays the SAME
labels through the SAME deterministic scoring code, and writes a NEW evaluation
carrying the scenario-specific judge contract fingerprint. No model is called
and no label is re-derived.

WHY THAT IS THE RIGHT SHAPE. The defect suite v1.1 exists to repair is a
metadata stamp: `judge_prompt_fingerprint()` hashed global repository state, so
a model judged today could not share a board with incumbents judged before the
penalty vocabulary grew. Nothing about the labels was ever in question. Fixing a
stamp by re-deriving thousands of judgments would move every published number to
repair something that is not a number.

WHAT MAKES IT SAFE. Three things, all enforced rather than promised:

  * the target path is versioned, and `write_evaluation` refuses to overwrite a
    versioned evaluation that already exists;
  * nothing under the source release is opened for writing;
  * `verify_migration` compares every criterion label, every false action, every
    penalty and every score between old and new, and the migration is only
    reported as successful when the count of changed judgments is zero.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .config import EvaluatorConfig, load_evaluator, repo_root
from .evaluator import (
    evaluate_run,
    evaluation_path,
    find_evaluations,
    load_evaluation,
    models_with_evaluations,
)
from .judge import JudgeError
from .recorded_judge import RecordedJudge, VerdictStore
from .runner import load_run, run_path
from .scenarios import load_scenario
from .schemas import Evaluation


class MigrationError(Exception):
    """A migration could not be performed, or could not be proved label-preserving."""


def verdict_files(scenario_id: str, model_slug: str, root: Path | None = None) -> list[Path]:
    """Every recorded verdict file that could hold this model's labels.

    monday-001's verdicts sit at `verdicts/<model>.verdicts.jsonl`; later
    scenarios use `verdicts/<scenario>/`, and monday-004 and monday-005 keep the
    seven incumbents together in `official.jsonl` with each challenger in its
    own file. All of them are candidates; the run id decides which one answers.
    """
    base = (root or repo_root()) / "verdicts"
    found: list[Path] = []
    if scenario_id == "monday-001":
        candidate = base / f"{model_slug}.verdicts.jsonl"
        if candidate.exists():
            found.append(candidate)
    directory = base / scenario_id
    if directory.is_dir():
        for name in (f"{model_slug}.verdicts.jsonl", "official.jsonl"):
            candidate = directory / name
            if candidate.exists():
                found.append(candidate)
    return found


def store_for(scenario_id: str, model_slug: str, run_id: str,
              root: Path | None = None) -> tuple[VerdictStore, Path]:
    """The verdict file that actually carries this run, and its loaded store."""
    for path in verdict_files(scenario_id, model_slug, root):
        store = VerdictStore.load(path)
        if any(key[0] == run_id for key in store.criteria):
            return store, path
    raise MigrationError(
        f"no recorded verdicts found for {run_id}; a re-stamp cannot invent labels"
    )


@dataclass
class MigratedRun:
    run_id: str
    scenario_id: str
    model_slug: str
    source_evaluation: str
    target_evaluation: str
    verdict_source: str
    old_score: float
    new_score: float
    old_contract: str | None
    new_contract: str | None
    criterion_labels_changed: list[str] = field(default_factory=list)
    false_actions_changed: list[str] = field(default_factory=list)
    penalties_changed: bool = False
    points_changed: list[str] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return not (
            self.criterion_labels_changed
            or self.false_actions_changed
            or self.penalties_changed
            or self.points_changed
            or abs(self.old_score - self.new_score) > 1e-9
        )


def _penalty_signature(evaluation: Evaluation) -> str:
    """Everything a penalty verdict asserts, in a comparable form."""
    return json.dumps(
        {
            "items": sorted(
                (i.type, i.points, i.evidence, i.reason) for i in evaluation.penalties.items
            ),
            "dismissed": sorted(
                (i.type, i.evidence, i.reason) for i in evaluation.penalties.dismissed
            ),
            "total": evaluation.penalties.total,
            "capped": evaluation.penalties.capped,
        },
        sort_keys=True,
        default=str,
    )


def compare(old: Evaluation, new: Evaluation) -> MigratedRun:
    """Prove, field by field, that a re-stamp changed no judgment."""
    changed_labels = [
        cid for cid, result in old.criteria.items()
        if cid not in new.criteria or new.criteria[cid].result != result.result
    ]
    changed_points = [
        cid for cid, result in old.criteria.items()
        if cid in new.criteria
        and abs(new.criteria[cid].points_awarded - result.points_awarded) > 1e-9
    ]
    changed_actions = [
        aid for aid, action in old.false_actions.items()
        if aid not in new.false_actions
        or new.false_actions[aid].triggered != action.triggered
    ]
    return MigratedRun(
        run_id=old.run_id,
        scenario_id=old.scenario_id,
        model_slug=old.model_slug,
        source_evaluation="",
        target_evaluation="",
        verdict_source=new.judge.verdict_source or "",
        old_score=old.final_score,
        new_score=new.final_score,
        old_contract=old.judge.contract_fingerprint,
        new_contract=new.judge.contract_fingerprint,
        criterion_labels_changed=changed_labels,
        false_actions_changed=changed_actions,
        penalties_changed=_penalty_signature(old) != _penalty_signature(new),
        points_changed=changed_points,
    )


def migrate_scenario(
    *,
    scenario_id: str,
    evaluator_id: str,
    target_suite_version: str,
    source_suite_version: str | None = None,
    models: list[str] | None = None,
    root: Path | None = None,
    write: bool = True,
) -> list[MigratedRun]:
    """Re-stamp every recorded evaluation of one scenario into a later release."""
    evaluator: EvaluatorConfig = load_evaluator(evaluator_id)
    scenario = load_scenario(scenario_id, rubric_file=evaluator.rubric_file)

    slugs = models or models_with_evaluations(evaluator_id, scenario_id, root, source_suite_version)
    results: list[MigratedRun] = []

    for slug in slugs:
        for source in find_evaluations(evaluator_id, scenario_id, slug, root, source_suite_version):
            old = load_evaluation(source)
            run_number = int(source.stem.split("-")[1])
            raw_path = run_path(scenario_id, slug, run_number, root)
            if not raw_path.exists():
                raise MigrationError(
                    f"{old.run_id}: raw output {raw_path} is missing; a re-stamp reuses the "
                    f"frozen generation and cannot proceed without it"
                )
            run = load_run(raw_path)
            if run.run_id != old.run_id:
                raise MigrationError(
                    f"{source} claims {old.run_id} but {raw_path} holds {run.run_id}"
                )

            store, verdict_path = store_for(scenario_id, slug, old.run_id, root)
            judge = RecordedJudge(evaluator, store, source=verdict_path.name)
            judge.bind(old.run_id)
            try:
                new = evaluate_run(
                    scenario=scenario,
                    evaluator=evaluator,
                    run=run,
                    judge=judge,
                    root=root,
                    write=write,
                    suite_version=target_suite_version,
                    # Never invented. The recorded judge's session identity was
                    # not captured when these labels were produced, and a
                    # migration is not entitled to guess it.
                    judge_session_id=None,
                    migrated_from=str(source.relative_to(root or repo_root())).replace("\\", "/"),
                )
            except (JudgeError, KeyError) as exc:
                raise MigrationError(f"{old.run_id}: {exc}") from exc

            comparison = compare(old, new)
            comparison.source_evaluation = str(
                source.relative_to(root or repo_root())).replace("\\", "/")
            comparison.target_evaluation = str(
                evaluation_path(evaluator_id, scenario_id, slug, run.run_number, root,
                                target_suite_version).relative_to(root or repo_root())
            ).replace("\\", "/")
            comparison.verdict_source = verdict_path.name
            results.append(comparison)

    return results


def verify_migration(results: list[MigratedRun]) -> dict[str, Any]:
    """The gate. A migration is only successful when nothing judged changed."""
    dirty = [r for r in results if not r.clean]
    return {
        "evaluations_migrated": len(results),
        "criterion_labels_changed": sum(len(r.criterion_labels_changed) for r in results),
        "false_action_judgments_changed": sum(len(r.false_actions_changed) for r in results),
        "penalty_verdicts_changed": sum(1 for r in results if r.penalties_changed),
        "awarded_points_changed": sum(len(r.points_changed) for r in results),
        "run_scores_changed": sum(
            1 for r in results if abs(r.old_score - r.new_score) > 1e-9),
        "clean": not dirty,
        "offenders": [
            {
                "run_id": r.run_id,
                "criterion_labels_changed": r.criterion_labels_changed,
                "false_actions_changed": r.false_actions_changed,
                "penalties_changed": r.penalties_changed,
                "points_changed": r.points_changed,
                "old_score": r.old_score,
                "new_score": r.new_score,
            }
            for r in dirty
        ],
    }
