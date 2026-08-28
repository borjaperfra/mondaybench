"""What makes a run official, and how many are still needed.

A run is official evidence only if it was produced under the exact published
conditions. Anything else is kept but excluded, with the reason recorded - a run
that silently slips into an official battery is worse than one that is missing.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

from .config import ModelConfig
from .runner import find_runs, load_run
from .schemas import BenchmarkRun

OFFICIAL_RUNS = 3


@dataclass
class RunVerdict:
    """Whether one stored run counts as official evidence."""

    path: Path
    run: BenchmarkRun | None
    reasons: list[str] = field(default_factory=list)

    @property
    def official(self) -> bool:
        return self.run is not None and not self.reasons

    @property
    def run_number(self) -> int | None:
        return self.run.run_number if self.run else None


def qualify_run(
    run: BenchmarkRun,
    *,
    path: Path,
    expected_prompt_sha256: str,
    model: ModelConfig | None,
    scenario_id: str,
) -> RunVerdict:
    """Check one run against the published conditions.

    Deliberately strict and deliberately explicit: every rejection carries a
    reason a reader can check against the file.
    """
    reasons: list[str] = []

    if run.scenario_id != scenario_id:
        reasons.append(f"scenario is {run.scenario_id!r}, expected {scenario_id!r}")

    if run.scenario_prompt_sha256 != expected_prompt_sha256:
        reasons.append(
            f"prompt hash {run.scenario_prompt_sha256[:12]} != published "
            f"{expected_prompt_sha256[:12]} - generated against different inputs"
        )

    if not run.response.strip():
        reasons.append("response is empty")

    # A truncated response is still evaluated as returned, but it is not evidence
    # of what the model would have said, so it cannot anchor an official score.
    if run.finish_reason == "length":
        reasons.append("finish_reason=length: output was truncated by the token budget")

    if run.generation.unsupported_parameters:
        reasons.append(
            "provider rejected configured parameters: "
            + ", ".join(run.generation.unsupported_parameters)
        )

    if model is not None:
        if run.model.model_id != model.model_id:
            reasons.append(
                f"model_id {run.model.model_id!r} != configured {model.model_id!r}"
            )
        if run.generation.temperature != model.temperature:
            reasons.append(
                f"temperature {run.generation.temperature} != configured {model.temperature}"
            )
        if run.generation.max_output_tokens != model.max_output_tokens:
            reasons.append(
                f"max_output_tokens {run.generation.max_output_tokens} != configured "
                f"{model.max_output_tokens}"
            )
        if run.model.provider != model.provider:
            reasons.append(
                f"provider {run.model.provider!r} != configured {model.provider!r}"
            )

    return RunVerdict(path=path, run=run, reasons=reasons)


@dataclass
class ModelPlan:
    """What exists and what still has to be generated for one model."""

    model_slug: str
    official: list[RunVerdict] = field(default_factory=list)
    rejected: list[RunVerdict] = field(default_factory=list)
    target: int = OFFICIAL_RUNS

    @property
    def have(self) -> int:
        return len(self.official)

    @property
    def missing(self) -> int:
        return max(0, self.target - self.have)

    @property
    def complete(self) -> bool:
        return self.have >= self.target

    def next_run_numbers(self) -> list[int]:
        """Run numbers to generate, skipping every number already on disk.

        Never reuses a number, so an existing file is never at risk of being
        overwritten even when it was rejected.
        """
        taken = {
            v.run_number
            for v in (*self.official, *self.rejected)
            if v.run_number is not None
        }
        numbers: list[int] = []
        candidate = 1
        while len(numbers) < self.missing:
            if candidate not in taken:
                numbers.append(candidate)
            candidate += 1
        return numbers


def _response_digest(run: BenchmarkRun) -> str:
    return hashlib.sha256(run.response.encode("utf-8")).hexdigest()


def plan_model(
    *,
    scenario_id: str,
    model_slug: str,
    model: ModelConfig | None,
    expected_prompt_sha256: str,
    target: int = OFFICIAL_RUNS,
    root: Path | None = None,
) -> ModelPlan:
    plan = ModelPlan(model_slug=model_slug, target=target)
    candidates: list[RunVerdict] = []

    for path in find_runs(scenario_id, model_slug, root):
        try:
            run = load_run(path)
        except Exception as exc:  # noqa: BLE001 - a corrupt file is a rejection, not a crash
            plan.rejected.append(RunVerdict(path=path, run=None, reasons=[f"unreadable: {exc}"]))
            continue
        candidates.append(
            qualify_run(
                run,
                path=path,
                expected_prompt_sha256=expected_prompt_sha256,
                model=model,
                scenario_id=scenario_id,
            )
        )

    # Three official runs must be three *samples*. Both endpoints cache a
    # response for an identical prompt, and a cached duplicate returned in under
    # a second would deflate run_range and sigma to zero while looking like a
    # third data point. This check is independent of the `caching: false` flag in
    # models.yaml, so a cache hit cannot reach a published score even if the flag
    # stops being honoured. The earliest run keeps its place; later duplicates
    # are rejected.
    candidates.sort(key=lambda v: v.run_number or 0)
    seen: dict[str, int | None] = {}
    for verdict in candidates:
        if verdict.run is None:
            continue
        digest = _response_digest(verdict.run)
        if digest in seen:
            verdict.reasons.append(
                f"response is byte-identical to run "
                f"{seen[digest]:03d} - a cached duplicate, not an independent sample"
            )
        else:
            seen[digest] = verdict.run_number

    for verdict in candidates:
        (plan.official if verdict.official else plan.rejected).append(verdict)
    plan.official.sort(key=lambda v: v.run_number or 0)
    return plan


def plan_battery(
    *,
    scenario_id: str,
    model_slugs: list[str],
    models: dict[str, ModelConfig],
    expected_prompt_sha256: str,
    target: int = OFFICIAL_RUNS,
    root: Path | None = None,
) -> dict[str, ModelPlan]:
    return {
        slug: plan_model(
            scenario_id=scenario_id,
            model_slug=slug,
            model=models.get(slug),
            expected_prompt_sha256=expected_prompt_sha256,
            target=target,
            root=root,
        )
        for slug in model_slugs
    }
