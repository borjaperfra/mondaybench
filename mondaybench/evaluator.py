"""Turn one immutable raw run into one auditable evaluation.

Judge classifies, `scoring.py` counts, this module orchestrates and persists.
Re-running the evaluator on existing runs never touches `runs/`.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import EvaluatorConfig, repo_root
from .deterministic import find_disagreements, run_checks
from .contract import (
    CONTRACT_SCHEMA_VERSION,
    judge_contract,
    judge_contract_fingerprint,
)
from .judge import Judge, judge_prompt_fingerprint
from .scenarios import Scenario
from .schemas import Evaluation, JudgeRecord
from .scoring import build_breakdown


def evaluations_root(root: Path | None = None, suite_version: str | None = None) -> Path:
    """Where evaluations for a suite version live.

    v1.0 has no version segment - its paths are what the release manifest pins,
    and adding one would move every file it hashes. Every later release gets its
    own subtree, so a re-stamp is additive and can never overwrite what came
    before.
    """
    base = (root or repo_root()) / "evaluations"
    return base if suite_version in (None, "1.0") else base / f"v{suite_version}"


def evaluations_dir(
    evaluator_id: str,
    scenario_id: str,
    model_slug: str,
    root: Path | None = None,
    suite_version: str | None = None,
) -> Path:
    return evaluations_root(root, suite_version) / evaluator_id / scenario_id / model_slug


def evaluation_path(
    evaluator_id: str,
    scenario_id: str,
    model_slug: str,
    run_number: int,
    root: Path | None = None,
    suite_version: str | None = None,
) -> Path:
    directory = evaluations_dir(evaluator_id, scenario_id, model_slug, root, suite_version)
    return directory / f"run-{run_number:03d}.json"


def resolve_ground_truth(ground_truth: dict[str, Any], paths: list[str]) -> dict[str, Any]:
    """Slice the answer key down to the facts one criterion needs.

    Paths are dotted, e.g. `critical_actions.contoso`. A path that does not
    resolve is an evaluator configuration error, not a silent omission.
    """
    excerpt: dict[str, Any] = {}
    for path in paths:
        node: Any = ground_truth
        for part in path.split("."):
            if not isinstance(node, dict) or part not in node:
                raise KeyError(f"ground-truth path {path!r} does not resolve")
            node = node[part]
        excerpt[path] = node
    return excerpt


def evaluate_run(
    *,
    scenario: Scenario,
    evaluator: EvaluatorConfig,
    run: Any,
    judge: Judge | None = None,
    root: Path | None = None,
    write: bool = True,
    suite_version: str | None = None,
    judge_session_id: str | None = None,
    migrated_from: str | None = None,
) -> Evaluation:
    """Evaluate one `BenchmarkRun` and (by default) persist the result."""
    judge = judge or Judge(evaluator, scenario_id=scenario.id, rubric=scenario.rubric)
    rubric = scenario.rubric
    response = run.response

    # A ground-truth map slices the answer key per criterion, which is the
    # stronger setup: the judge cannot be swayed by facts the criterion is not
    # about. It requires a structured answer key with dotted paths. Where the
    # scenario ships prose instead, there is nothing to slice and the judge is
    # given the whole document - recorded on the evaluation so the difference is
    # visible rather than assumed.
    sliced_ground_truth = bool(evaluator.ground_truth_map)
    if sliced_ground_truth:
        missing_map = [c.id for c in rubric.criteria if c.id not in evaluator.ground_truth_map]
        if missing_map:
            raise KeyError(
                f"evaluator {evaluator.id}: ground_truth_map has no entry for "
                f"{', '.join(missing_map)}"
            )

    whole_ground_truth: dict[str, Any] = (
        scenario.ground_truth
        if scenario.ground_truth
        else {"ground_truth": scenario.ground_truth_text}
    )

    criterion_verdicts: dict[str, tuple[str, str | None, str | None]] = {}
    labels: dict[str, Any] = {}
    for criterion in rubric.criteria:
        excerpt = (
            resolve_ground_truth(scenario.ground_truth, evaluator.ground_truth_map[criterion.id])
            if sliced_ground_truth
            else whole_ground_truth
        )
        verdict = judge.judge_criterion(criterion, excerpt, response)
        criterion_verdicts[criterion.id] = (verdict.result, verdict.evidence, verdict.reason)
        labels[criterion.id] = verdict.result

    # Noise is a dimension in monday-001 and absent in monday-002, where the
    # same risk is scored inside the criteria and the penalties instead.
    if rubric.noise is not None:
        noise_verdict = judge.judge_noise(rubric.noise.false_actions, response)
        false_actions = {item.id: (item.triggered, item.evidence) for item in noise_verdict.items}
    else:
        false_actions = {}

    # The penalty judge needs the evidence the model was shown, not just the
    # answer key - see the note on `penalty_prompt`. Sources are joined in the
    # order scenario.yaml declares, matching what the model received.
    source_material = "\n\n".join(
        f"--- {name} ---\n{scenario.source_text[name].strip()}" for name in scenario.sources
    )
    penalty_verdict = judge.judge_penalties(
        scenario.ground_truth, response, source_material=source_material
    )

    # The contract this evaluation was produced under. Computed from the
    # scenario as loaded (against this evaluator's rubric file) rather than from
    # global module state, which is the whole point of the v1.1 change.
    contract_fingerprint = judge_contract_fingerprint(judge_contract(scenario, evaluator))

    breakdown = build_breakdown(
        rubric,
        criterion_verdicts=criterion_verdicts,
        false_actions=false_actions,
        violations=penalty_verdict.violations,
    )

    evaluation = Evaluation(
        evaluator_id=evaluator.id,
        benchmark_version=scenario.benchmark_version,
        rubric_version=rubric.version,
        scenario_id=scenario.id,
        run_id=run.run_id,
        model_slug=run.model.slug,
        scenario_prompt_sha256=run.scenario_prompt_sha256,
        timestamp_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        judge=JudgeRecord(
            provider=evaluator.provider,
            model_id=judge.model_id,
            temperature=evaluator.temperature,
            effort=evaluator.effort,
            unsupported_parameters=list(judge.stats.unsupported_parameters or []),
            prompt_fingerprint=judge_prompt_fingerprint(),
            route="recorded" if getattr(judge, "verdict_source", None) else "api",
            verdict_source=getattr(judge, "verdict_source", None),
            contract_fingerprint=contract_fingerprint,
            contract_schema_version=CONTRACT_SCHEMA_VERSION,
            judge_session_id=judge_session_id,
        ),
        suite_version=suite_version,
        migrated_from=migrated_from,
        dimensions=breakdown.dimensions,
        criteria=breakdown.criteria,
        false_actions=breakdown.false_actions,
        penalties=breakdown.penalties,
        deterministic_checks=run_checks(response),
        disagreements=find_disagreements(response, labels),
        base_score=breakdown.base_score,
        final_score=breakdown.final_score,
    )

    if write:
        write_evaluation(evaluation, run.run_number, root=root)
    return evaluation


def write_evaluation(
    evaluation: Evaluation, run_number: int, root: Path | None = None
) -> Path:
    target = evaluation_path(
        evaluation.evaluator_id,
        evaluation.scenario_id,
        evaluation.model_slug,
        run_number,
        root,
        evaluation.suite_version,
    )
    # A re-stamp is create-new by construction. Refusing here rather than in the
    # caller means no code path can overwrite an evaluation that already exists,
    # which is the guarantee the whole migration rests on.
    if evaluation.suite_version and target.exists():
        raise FileExistsError(
            f"{target} already exists; a versioned evaluation is never overwritten"
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(evaluation.model_dump(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8", newline="\n",
    )
    return target


def load_evaluation(path: Path) -> Evaluation:
    return Evaluation.model_validate_json(path.read_text(encoding="utf-8"))


def find_evaluations(
    evaluator_id: str,
    scenario_id: str,
    model_slug: str,
    root: Path | None = None,
    suite_version: str | None = None,
) -> list[Path]:
    directory = evaluations_dir(evaluator_id, scenario_id, model_slug, root, suite_version)
    if not directory.is_dir():
        return []
    return sorted(directory.glob("run-*.json"))


def models_with_evaluations(
    evaluator_id: str,
    scenario_id: str,
    root: Path | None = None,
    suite_version: str | None = None,
) -> list[str]:
    directory = evaluations_root(root, suite_version) / evaluator_id / scenario_id
    if not directory.is_dir():
        return []
    return sorted(p.name for p in directory.iterdir() if p.is_dir() and any(p.glob("run-*.json")))


# --------------------------------------------------------------------------
# Review file (--review)
# --------------------------------------------------------------------------


def build_review(evaluation: Evaluation, response: str) -> str:
    """A concise human-audit view: everything that is not a clean PASS."""
    lines: list[str] = []
    lines.append(f"# Review - {evaluation.run_id}")
    lines.append("")
    lines.append(f"Evaluator: {evaluation.evaluator_id}")
    lines.append(f"Judge: {evaluation.judge.provider} / {evaluation.judge.model_id}")
    if evaluation.judge.unsupported_parameters:
        lines.append(
            f"Judge parameters dropped as unsupported: "
            f"{', '.join(evaluation.judge.unsupported_parameters)}"
        )
    lines.append(f"Base score: {evaluation.base_score}  Final score: {evaluation.final_score}")
    lines.append("")

    non_pass = {k: v for k, v in evaluation.criteria.items() if v.result != "PASS"}
    lines.append(f"## Non-PASS criteria ({len(non_pass)})")
    lines.append("")
    if not non_pass:
        lines.append("(none)")
    for cid, result in non_pass.items():
        lines.append(
            f"- **{cid}** = {result.result} "
            f"({result.points_awarded}/{result.points_possible})"
        )
        if result.reason:
            lines.append(f"  - reason: {result.reason}")
        if result.evidence:
            lines.append(f"  - evidence: {result.evidence}")
    lines.append("")

    triggered = {k: v for k, v in evaluation.false_actions.items() if v.triggered}
    lines.append(f"## Triggered false actions ({len(triggered)})")
    lines.append("")
    if not triggered:
        lines.append("(none)")
    for aid, action in triggered.items():
        lines.append(f"- **{aid}** ({action.points}): {action.description}")
        if action.evidence:
            lines.append(f"  - evidence: {action.evidence}")
    lines.append("")

    lines.append(f"## Penalties ({len(evaluation.penalties.items)})")
    lines.append("")
    if not evaluation.penalties.items:
        lines.append("(none)")
    for item in evaluation.penalties.items:
        lines.append(f"- **{item.type}** ({item.points})")
        if item.reason:
            lines.append(f"  - reason: {item.reason}")
        if item.evidence:
            lines.append(f"  - evidence: {item.evidence}")
    if evaluation.penalties.capped:
        lines.append(
            f"- raw total {evaluation.penalties.raw_total} capped to {evaluation.penalties.total}"
        )
    lines.append("")

    dismissed = evaluation.penalties.dismissed
    lines.append(f"## Considered and dismissed ({len(dismissed)})")
    lines.append("")
    lines.append("_Raised by the judge, classified as not materially misleading. No points._")
    lines.append("")
    if not dismissed:
        lines.append("(none)")
    for item in dismissed:
        lines.append(f"- **{item.type}**")
        if item.reason:
            lines.append(f"  - reason: {item.reason}")
        if item.evidence:
            lines.append(f"  - evidence: {item.evidence}")
    lines.append("")

    lines.append(f"## Judge / matcher disagreements ({len(evaluation.disagreements)})")
    lines.append("")
    if not evaluation.disagreements:
        lines.append("(none)")
    for disagreement in evaluation.disagreements:
        lines.append(f"- {disagreement.message}")
    lines.append("")

    lines.append("## Full response")
    lines.append("")
    lines.append(response)
    lines.append("")
    return "\n".join(lines)


def write_review(
    evaluation: Evaluation, response: str, run_number: int, root: Path | None = None
) -> Path:
    directory = evaluations_dir(
        evaluation.evaluator_id, evaluation.scenario_id, evaluation.model_slug, root
    )
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / f"run-{run_number:03d}.review.md"
    target.write_text(build_review(evaluation, response), encoding="utf-8", newline="\n")
    return target
