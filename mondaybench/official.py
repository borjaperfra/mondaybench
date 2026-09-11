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
from .runner import archived_run_numbers, find_runs, load_run
from . import reasoning as reasoning_check
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


# Generation ceiling status, recorded as qualification evidence from
# monday-004 onwards.
#
# The token-budget audit established that the configured ceiling is not a shared
# compute budget: helmcode/deepseek-v4-flash and nan/mimo-v2.5 stop at it
# exactly, nan/qwen3.8-flash exceeds it by up to 84%, and the other four never
# approached it. So the question qualification asks is NOT "did the provider
# respect the parameter" - it demonstrably does not, consistently - but "did our
# ceiling stop this answer before it finished".
CEILING_NON_BINDING = "NON_BINDING"
CEILING_BOUND = "BOUND"
CEILING_UNOBSERVABLE = "UNOBSERVABLE"


def generation_ceiling_status(run: BenchmarkRun) -> str:
    """Whether our safety ceiling bound this generation.

    BOUND means the answer stopped because it ran out of ceiling: the provider
    said so with `finish_reason=length`, or the completion landed exactly on the
    configured value. Either way the response is not evidence of what the model
    would have said.

    Delivered usage ABOVE the ceiling is NOT bound. It means the provider did
    not apply the parameter, which the audit documents for one endpoint and
    which is not the candidate's doing. Rejecting it would fail a model for a
    provider's implementation choice.
    """
    ceiling = run.generation.safety_ceiling_tokens or run.generation.max_output_tokens
    delivered = run.usage.output_tokens if run.usage else None

    if run.finish_reason == "length":
        return CEILING_BOUND
    if delivered is None or not ceiling:
        return CEILING_UNOBSERVABLE
    if delivered >= ceiling:
        # Landed exactly on it without the provider saying `length`: the same
        # defect, reported differently. Above it is a different thing entirely.
        return CEILING_BOUND if delivered == ceiling else CEILING_NON_BINDING
    return CEILING_NON_BINDING


def qualify_run(
    run: BenchmarkRun,
    *,
    path: Path,
    expected_prompt_sha256: str,
    model: ModelConfig | None,
    scenario_id: str,
    expected_max_output_tokens: int | None = None,
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
    #
    # Stated as the ceiling status from monday-004 onwards. The rule is
    # unchanged - a run our ceiling stopped does not qualify - but the reason now
    # says which of the three states it is in, and a provider that simply
    # ignored the parameter is explicitly not a rejection.
    ceiling_status = generation_ceiling_status(run)
    if ceiling_status == CEILING_BOUND:
        reasons.append(
            f"generation_ceiling_status={CEILING_BOUND}: output was truncated by the "
            f"configured safety ceiling before the answer was complete "
            f"(finish_reason={run.finish_reason})"
        )

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
        # The ceiling a run was generated under must match the one the scenario
        # configures, so a battery cannot mix two of them. `expected` lets a
        # caller supply a per-scenario ceiling; without one this is the model
        # default, which is what monday-001..003 were generated under and why
        # they go on qualifying unchanged.
        expected_ceiling = (
            expected_max_output_tokens
            if expected_max_output_tokens is not None
            else model.max_output_tokens
        )
        #
        # A run that records NO ceiling is not compared. Silence is not a
        # different value: it means the runtime never exposed one, and holding
        # that against the run would be refusing it for the absence of evidence
        # rather than for evidence of a problem. This is the same rule the
        # reasoning check already applies - "only a positively observed absence
        # disqualifies" - applied to the same kind of missing telemetry.
        #
        # THE COST, stated rather than buried: this check is one of the two
        # defences against scoring a truncated answer as a complete one, and the
        # other (`finish_reason == "length"`) is equally unobservable on a
        # runtime that reports neither. For such a run, the evidence that the
        # answer finished on its own terms comes from the runtime's own
        # completion events, recorded in `provider_metadata`, not from this
        # harness. Authorised for the Codex challenger on 2026-09-11.
        if (
            run.generation.max_output_tokens is not None
            and run.generation.max_output_tokens != expected_ceiling
        ):
            reasons.append(
                f"max_output_tokens (safety ceiling) {run.generation.max_output_tokens} "
                f"!= configured {expected_ceiling}"
            )
        if run.model.provider != model.provider:
            reasons.append(
                f"provider {run.model.provider!r} != configured {model.provider!r}"
            )

    # A reasoning model that came back without reasoning did not run under the
    # regime the other runs of that model used, so its score is not comparable
    # with theirs. This is the same class of defect as a gateway cache hit, and
    # it is rejected the same way: the file stays, the score stays readable, the
    # run just stops counting. Discovered on monday-002/qwen3.8-flash/run-002,
    # which scored 66.5 against 93.0 and 100.0 on zero reasoning tokens.
    #
    # Only a positively observed absence disqualifies. A provider that reports
    # no reasoning signal at all leaves the run qualified and is surfaced
    # separately - refusing it would be inventing evidence.
    status, tokens = reasoning_check.classify(run)
    if reasoning_check.disqualifies(status):
        reasons.append(
            f"{reasoning_check.REASONING_NOT_DELIVERED}: reasoning was requested but the "
            f"provider returned {tokens} reasoning tokens, so this run is not in the same "
            f"regime as the model's other runs"
        )

    return RunVerdict(path=path, run=run, reasons=reasons)


def reasoning_status(run: BenchmarkRun) -> str:
    """DELIVERED / NOT_DELIVERED / NOT_REQUESTED / UNOBSERVABLE for one run."""
    return reasoning_check.classify(run)[0]


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

    # Numbers used by archived batteries for this model. Kept on the plan so
    # `next_run_numbers` can avoid them: a reused number would give a new
    # response an existing run id, and recorded verdicts are keyed by run id.
    reserved: set[int] = field(default_factory=set)

    def next_run_numbers(self) -> list[int]:
        """Run numbers to generate, skipping every number already used.

        Never reuses a number, so an existing file is never at risk of being
        overwritten even when it was rejected - and never reuses a number an
        archived battery already spent, which would collide on run id.
        """
        taken = {
            v.run_number
            for v in (*self.official, *self.rejected)
            if v.run_number is not None
        } | self.reserved
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
    expected_max_output_tokens: int | None = None,
) -> ModelPlan:
    plan = ModelPlan(
        model_slug=model_slug,
        target=target,
        reserved=archived_run_numbers(scenario_id, model_slug, root),
    )
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
                expected_max_output_tokens=expected_max_output_tokens,
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
    expected_max_output_tokens: int | None = None,
) -> dict[str, ModelPlan]:
    return {
        slug: plan_model(
            scenario_id=scenario_id,
            expected_max_output_tokens=expected_max_output_tokens,
            model_slug=slug,
            model=models.get(slug),
            expected_prompt_sha256=expected_prompt_sha256,
            target=target,
            root=root,
        )
        for slug in model_slugs
    }
