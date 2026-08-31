"""Benchmarking a new model against a frozen suite.

The situation this exists for: the suite is closed, seven models are on the
board, and an eighth needs a Monday Score. Nothing about the first seven may be
regenerated, rejudged or recomputed - their scores are a published claim, and
re-running them would be both expensive and a different experiment.

That is achievable because of how the score is defined. A model's Monday Score
is the mean of its own official runs on each scenario; no term in it depends on
any other model. So a challenger needs 5 scenarios x 3 runs = 15 generations and
one judging pass, and every existing number stays exactly where it is - a
property this module reports on rather than assumes.

WHAT THIS MODULE DOES NOT DO. It does not generate and it does not judge. It
reports what exists, what qualifies, and what is left - so the campaign can be
resumed after an interruption without guessing, and so the state of a
half-finished challenger is legible at any point.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .config import (
    ConfigError,
    apply_endpoint_overrides,
    endpoint_overrides_for,
    load_models,
    repo_root,
    resolve_evaluator,
)
from .freeze import load_manifest
from .official import OFFICIAL_RUNS, ModelPlan, plan_model
from .scenarios import list_scenario_ids, load_scenario


class ChallengeError(Exception):
    """Raised when a challenger cannot be planned against the suite."""


@dataclass
class ScenarioStatus:
    scenario_id: str
    evaluator: str
    prompt_sha256: str
    target: int
    plan: ModelPlan
    evaluations: int
    on_leaderboard: bool

    @property
    def official(self) -> int:
        return len(self.plan.official)

    @property
    def runs_needed(self) -> int:
        return max(0, self.target - self.official)

    @property
    def judgements_needed(self) -> int:
        """Official runs with no evaluation yet - what can be judged right now."""
        return max(0, self.official - self.evaluations)

    @property
    def judgements_remaining(self) -> int:
        """Judging still owed for a complete battery, including runs not yet
        generated. `judgements_needed` is what is actionable today; this is the
        total left in the campaign, which is what a plan needs."""
        return max(0, self.target - self.evaluations)

    @property
    def complete(self) -> bool:
        return (
            self.official >= self.target
            and self.evaluations >= self.target
            and self.on_leaderboard
        )

    @property
    def stage(self) -> str:
        if self.complete:
            return "published"
        if self.official >= self.target and self.evaluations >= self.target:
            return "awaiting leaderboard"
        if self.official >= self.target:
            return "awaiting judging"
        if self.official or self.plan.rejected:
            return "generating"
        return "not started"


@dataclass
class ChallengeStatus:
    model_slug: str
    display_name: str
    suite_version: str | None
    scenarios: list[ScenarioStatus] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def runs_needed(self) -> int:
        return sum(s.runs_needed for s in self.scenarios)

    @property
    def judgements_needed(self) -> int:
        return sum(s.judgements_needed for s in self.scenarios)

    @property
    def eligible_for_overall(self) -> bool:
        """A model ranks only with an official score on EVERY scenario."""
        return bool(self.scenarios) and all(s.complete for s in self.scenarios)

    @property
    def judgements_remaining(self) -> int:
        return sum(s.judgements_remaining for s in self.scenarios)

    @property
    def criteria_to_judge(self) -> int:
        """Criterion verdicts left in the whole campaign. This is the number that
        decides how long the judging session is, so it counts runs that do not
        exist yet rather than only the ones sitting on disk."""
        return sum(
            s.judgements_remaining * _criterion_count(s.scenario_id) for s in self.scenarios
        )


def _criterion_count(scenario_id: str) -> int:
    return len(load_scenario(scenario_id).rubric.criteria)


def evaluation_count(evaluator: str, scenario_id: str, model_slug: str, root: Path | None) -> int:
    directory = (
        (root or repo_root()) / "evaluations" / evaluator / scenario_id / model_slug
    )
    if not directory.is_dir():
        return 0
    return len(list(directory.glob("*.json")))


def official_evaluator(scenario_id: str, root: Path | None = None) -> str:
    """Which evaluator scored this scenario's published board.

    Read from the board itself rather than from `resolve_evaluator`, which finds
    an evaluator by its declared `scenario_id`. `evaluator-opus5-v0.1` declares
    none - monday-001 predates the convention - so resolution for that one
    scenario falls through to a hardcoded fallback constant in the CLI. The
    published leaderboard records the evaluator that actually produced it, which
    is the authoritative answer for all five and needs no fallback.
    """
    import json

    path = leaderboard_path(scenario_id, root)
    if path.is_file():
        recorded = json.loads(path.read_text(encoding="utf-8")).get("evaluator")
        if recorded:
            return str(recorded)
    try:
        resolved = resolve_evaluator(scenario_id, None, "")
    except ConfigError as exc:
        raise ChallengeError(str(exc)) from exc
    if not resolved:
        raise ChallengeError(
            f"cannot determine the official evaluator for {scenario_id}: it has no published "
            f"leaderboard and no evaluator declares it"
        )
    return resolved


def leaderboard_path(scenario_id: str, root: Path | None = None) -> Path:
    base = root or repo_root()
    # monday-001 predates the per-scenario directory layout.
    return (
        base / "leaderboard" / "leaderboard.json"
        if scenario_id == "monday-001"
        else base / "leaderboard" / scenario_id / "leaderboard.json"
    )


def on_leaderboard(scenario_id: str, model_slug: str, root: Path | None = None) -> bool:
    import json

    path = leaderboard_path(scenario_id, root)
    if not path.is_file():
        return False
    payload = json.loads(path.read_text(encoding="utf-8"))
    return any(m.get("model_slug") == model_slug for m in payload.get("models", []))


def suite_scenarios(version: str | None = None, root: Path | None = None) -> list[str]:
    """The scenarios a suite release covers, or every frozen scenario."""
    if version is not None:
        from .suite import load_suite_manifest

        manifest = load_suite_manifest(version, root)
        if manifest is None:
            raise ChallengeError(f"no manifest for suite v{version}")
        return [s["id"] for s in manifest["scenarios"]]
    return list_scenario_ids()


def status_for(
    model_slug: str,
    *,
    suite_version: str | None = "1.0",
    root: Path | None = None,
) -> ChallengeStatus:
    root = root or repo_root()
    base_models = load_models()
    model = base_models.get(model_slug)

    status = ChallengeStatus(
        model_slug=model_slug,
        display_name=model.display_name if model else model_slug,
        suite_version=suite_version,
    )
    if model is None:
        status.notes.append(
            f"{model_slug!r} is not in models.yaml. Add it there first - the registry is what "
            f"decides which endpoint and model id a slug means, and a run generated without "
            f"one cannot be qualified."
        )

    for scenario_id in suite_scenarios(suite_version, root):
        manifest = load_manifest(root / "scenarios" / scenario_id)
        if manifest is None:
            raise ChallengeError(f"{scenario_id} is not frozen")
        loaded = load_scenario(scenario_id)
        evaluator = official_evaluator(scenario_id, root)

        # Per-scenario endpoint overrides must be applied before qualification.
        # A model's provider is part of what `qualify_run` checks, and
        # monday-004/qwen3.6 was deliberately served from NaN while Helmcode was
        # unreachable. Qualifying it against the unscoped registry rejects three
        # published runs and reports an incumbent as incomplete.
        scoped = apply_endpoint_overrides(
            base_models, endpoint_overrides_for(scenario_id)
        )

        plan = plan_model(
            scenario_id=scenario_id,
            model_slug=model_slug,
            model=scoped.get(model_slug),
            expected_prompt_sha256=manifest.prompt_sha256,
            target=loaded.official_runs or OFFICIAL_RUNS,
            root=root,
            expected_max_output_tokens=loaded.safety_ceiling_tokens,
        )
        status.scenarios.append(
            ScenarioStatus(
                scenario_id=scenario_id,
                evaluator=evaluator,
                prompt_sha256=manifest.prompt_sha256,
                target=loaded.official_runs or OFFICIAL_RUNS,
                plan=plan,
                evaluations=evaluation_count(evaluator, scenario_id, model_slug, root),
                on_leaderboard=on_leaderboard(scenario_id, model_slug, root),
            )
        )
    return status


def incumbents(root: Path | None = None, suite_version: str | None = "1.0") -> list[str]:
    """Models already published on every scenario in the suite."""
    import json

    root = root or repo_root()
    scenarios = suite_scenarios(suite_version, root)
    sets: list[set[str]] = []
    for scenario_id in scenarios:
        path = leaderboard_path(scenario_id, root)
        if not path.is_file():
            return []
        payload = json.loads(path.read_text(encoding="utf-8"))
        sets.append({m["model_slug"] for m in payload.get("models", [])})
    return sorted(set.intersection(*sets)) if sets else []


def next_overall_revision(root: Path | None = None) -> tuple[int, int]:
    """The (version, revision) a new model should be published under."""
    from .overall import load_releases

    releases = load_releases(root=root)
    base = max(r.version for r in releases.values())
    revisions = [r.revision for r in releases.values() if r.version == base]
    return base, max(revisions) + 1


def draft_revision_block(
    model_slug: str, root: Path | None = None, suite_version: str | None = "1.0"
) -> str:
    """The YAML block to append to overall-releases.yaml for a new challenger.

    Generated rather than hand-written: the scenario pins must match the base
    release exactly, and retyping five prompt hashes is precisely the kind of
    thing that produces a release nobody can reproduce.
    """
    from .overall import load_releases

    version, revision = next_overall_revision(root)
    base = load_releases(root=root)[version]
    incumbent_list = incumbents(root, suite_version)

    lines = [
        f"  - overall_version: {version}",
        f"    revision: {revision}",
        f'    label: "Overall v{version}.{revision} — {len(incumbent_list) + 1} models"',
        "    status: draft",
        f"    aggregation: {base.aggregation}",
        "    note: >",
        f"      Same {len(base.scenario_ids)} scenarios as Overall v{version}, same arithmetic,",
        f"      one more competitor: {model_slug}. Overall v{version} is unchanged and stays",
        "      the citable artifact for the seven-model field; this revision adds a row",
        "      without moving one. No existing model was regenerated or rejudged - a",
        "      Monday Score is the mean of a model's own runs, so a new entrant cannot",
        "      move an incumbent's score, and check_sample_provenance is what proves the",
        "      incumbent evidence was not touched.",
        "    scenarios:",
    ]
    for pin in base.scenarios:
        lines.append(f"      - id: {pin.id}")
        lines.append(f"        prompt_sha256: {pin.prompt_sha256}")
        lines.append(f'        rubric_version: "{pin.rubric_version}"')
    return "\n".join(lines) + "\n"
