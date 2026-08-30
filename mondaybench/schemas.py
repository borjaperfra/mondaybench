"""Pydantic models for every artifact MondayBench writes to disk.

Two schemas matter: the immutable raw generation (`BenchmarkRun`) and the
evaluation (`Evaluation`). Both carry `schema_version` so future readers can
tell what they are looking at.
"""

from __future__ import annotations

from typing import Any, Literal, get_args

from pydantic import BaseModel, ConfigDict, Field

Label = Literal["PASS", "PARTIAL", "FAIL"]
# The shared penalty vocabulary. A rubric may name a penalty in its own terms -
# `scenarios.PENALTY_KEY_TO_TYPE` maps those names onto these - but the stored
# type is always one of these, so a penalty means the same thing in every
# scenario and on every leaderboard.
#
# monday-002 v0.2 added MAJOR_PLANNING_ERROR: a schedule or dependency order
# that cannot actually happen. monday-004 adds the two an analysis scenario
# needs and a planning scenario has no use for: a numeric or data mistake that
# drives the analysis, and a causal claim the evidence does not support. Neither
# is a planning error and neither is a hallucination - the figures and the
# correlation are both really in the data; what is wrong is the handling.
PenaltyType = Literal[
    "MATERIAL_HALLUCINATION",
    "PROHIBITED_ACTION",
    "MAJOR_PLANNING_ERROR",
    "MAJOR_CONTRADICTION",
    "MAJOR_DATA_ERROR",
    "UNSUPPORTED_CAUSALITY",
]

# One source for the four places that used to carry their own copy of the list:
# the judge's JSON schema, the judge's reply validation, the recorded judge's
# reply validation, and the tests. Adding a type in one place and forgetting
# another is how a verdict becomes unreadable by the code that has to score it.
PENALTY_TYPE_VALUES: tuple[str, ...] = get_args(PenaltyType)


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


# --------------------------------------------------------------------------
# runs/<scenario>/<model>/run-XXX.json
# --------------------------------------------------------------------------


class RunModel(Strict):
    slug: str
    display_name: str
    provider: str
    model_id: str


class RunGeneration(Strict):
    temperature: float | None
    max_output_tokens: int
    # Kept for the runs written before the reasoning audit. It held the model's
    # *declared* capability and was mistaken for an observation; new runs carry
    # `reasoning_requested` and `RunReasoning` instead. Never read this to
    # decide whether reasoning happened - see mondaybench/reasoning.py.
    reasoning_enabled: bool
    # Recorded when the provider rejects a parameter the config asked for
    # (e.g. Anthropic Opus 5 rejects `temperature`), per IMPLEMENTATION.md s5.
    unsupported_parameters: list[str] = Field(default_factory=list)
    system_prompt_sent: bool = True

    # --- effective configuration, added after the monday-002 audit ----------
    # All default to None so every run written before this exists still loads.
    top_p: float | None = None
    # The regime this run was supposed to belong to, from the configuration.
    # Not evidence that the provider honoured it.
    reasoning_requested: bool | None = None
    reasoning_mode: str | None = None
    reasoning_effort: str | None = None
    # Hash of the exact system prompt text; the empty string hashes to a real
    # value, so "no system prompt" and "not recorded" stay distinguishable.
    system_prompt_sha256: str | None = None
    # Provider-specific body sent alongside the standard parameters.
    extra_body: dict[str, Any] = Field(default_factory=dict)
    # Fingerprint of everything above that shapes the generation. Two runs
    # sharing it were asked for under the same effective configuration.
    config_sha256: str | None = None

    # --- generation ceiling, added after the monday-004 token-budget audit ---
    # `max_output_tokens` above is the value that reaches the wire as the legacy
    # Chat Completions `max_tokens`. The audit established that providers do not
    # apply that field consistently to reasoning models: two of seven stop at it
    # exactly, one exceeds it by up to 84%, and four never approached it. So it
    # is NOT a shared compute budget and must not be described as one.
    #
    # `safety_ceiling_tokens` records the same number under the name that says
    # what it is: a limit set high enough not to bind a normal generation, so a
    # runaway is capped and a successful answer is not. `ceiling_semantics`
    # records that what the provider does with it is provider-specific.
    #
    # Both default to None so every run written before monday-004 still loads
    # and still means exactly what it meant.
    safety_ceiling_tokens: int | None = None
    ceiling_semantics: str | None = None


class RunReasoning(Strict):
    """What the provider actually did, as opposed to what was configured.

    `status` is one of DELIVERED / NOT_DELIVERED / NOT_REQUESTED / UNOBSERVABLE.
    `tokens` is None when the provider reported no reasoning signal at all,
    which is materially different from reporting zero.
    """

    requested: bool
    status: str
    tokens: int | None = None
    # Which signal established delivery. `explicit_*` came from the provider;
    # `derived_pre_answer_stream` was reconstructed from a run's own timings
    # and is labelled so it is never mistaken for something the adapter
    # recorded at the time. See mondaybench/reasoning.py.
    evidence: str | None = None
    # Structural, not content: how many reasoning deltas the adapter saw. None
    # on every run written before the adapter counted them.
    stream_observed: bool | None = None
    stream_event_count: int | None = None


class RunUsage(Strict):
    input_tokens: int | None = None
    output_tokens: int | None = None
    reasoning_tokens: int | None = None


class RunPerformance(Strict):
    ttft_ms: float | None = None
    ttfa_ms: float | None = None
    total_latency_ms: float | None = None
    tokens_per_second: float | None = None


class RunEconomics(Strict):
    input_cost_usd: float | None = None
    output_cost_usd: float | None = None
    total_cost_usd: float | None = None


class RunProviderMetadata(Strict):
    request_id: str | None = None
    raw_usage: dict[str, Any] = Field(default_factory=dict)


class BenchmarkRun(Strict):
    schema_version: Literal["1"] = "1"
    benchmark_version: str
    scenario_id: str
    scenario_prompt_sha256: str

    run_id: str
    run_number: int

    model: RunModel
    generation: RunGeneration
    # Optional so every pre-audit run still validates.
    reasoning: RunReasoning | None = None

    timestamp_utc: str

    usage: RunUsage
    performance: RunPerformance
    economics: RunEconomics

    response: str
    finish_reason: str | None = None

    provider_metadata: RunProviderMetadata


# --------------------------------------------------------------------------
# Judge wire formats - what the judge model is contractually asked to return
# --------------------------------------------------------------------------


class CriterionVerdict(Strict):
    """Judge output for one atomic rubric criterion."""

    result: Label
    evidence: str | None = None
    reason: str | None = None


class NoiseItem(Strict):
    id: str
    triggered: bool
    evidence: str | None = None


class NoiseVerdict(Strict):
    items: list[NoiseItem]


class PenaltyViolation(Strict):
    type: PenaltyType
    evidence: str | None = None
    reason: str | None = None
    # The judge must assert this explicitly. Asking it to stay silent about
    # non-violations did not work - it returned entries whose own reason read
    # "Not a violation-level issue on its own" and "Minor attribution difference
    # only". Classifying is something a judge does reliably; self-censoring is
    # not. Python drops the entries where this is false.
    materially_misleading: bool = True


class PenaltyVerdict(Strict):
    violations: list[PenaltyViolation] = Field(default_factory=list)


# --------------------------------------------------------------------------
# evaluations/<evaluator>/<scenario>/<model>/run-XXX.json
# --------------------------------------------------------------------------


class JudgeRecord(Strict):
    provider: str
    model_id: str
    temperature: float | None
    effort: str | None = None
    unsupported_parameters: list[str] = Field(default_factory=list)
    # Hash of the judge prompt templates and verdict schemas. Two evaluations
    # sharing an evaluator_id but differing here were judged by different
    # instructions and must not be aggregated together.
    prompt_fingerprint: str | None = None
    # How the labels reached the pipeline: an API call, or a recorded verdict
    # file. Same model can be reached either way, and it matters which.
    route: str | None = None
    verdict_source: str | None = None


class DimensionScore(Strict):
    score: float
    max_score: float


class CriterionResult(Strict):
    result: Label
    points_awarded: float
    points_possible: float
    evidence: str | None = None
    reason: str | None = None


class FalseActionResult(Strict):
    triggered: bool
    points: float
    evidence: str | None = None
    description: str


class PenaltyItem(Strict):
    type: PenaltyType
    points: float
    evidence: str | None = None
    reason: str | None = None


class Penalties(Strict):
    items: list[PenaltyItem] = Field(default_factory=list)
    # Candidates the judge raised but classified as not materially misleading.
    # Kept for audit: a dropped penalty should be visible, not invisible.
    dismissed: list[PenaltyItem] = Field(default_factory=list)
    raw_total: float = 0.0
    total: float = 0.0
    capped: bool = False


class DeterministicCheck(Strict):
    id: str
    matched: bool
    detail: str | None = None


class JudgeDisagreement(Strict):
    criterion_id: str
    judge_result: Label
    check_id: str
    check_matched: bool
    message: str


class Evaluation(Strict):
    schema_version: Literal["1"] = "1"
    evaluator_id: str
    benchmark_version: str
    # Points come from the rubric, so the rubric version is part of what a score
    # means. Two evaluations scored under different rubrics are not comparable
    # even with an identical judge - the same failure mode the judge fingerprint
    # guards against, one layer up.
    rubric_version: str | None = None
    scenario_id: str
    run_id: str
    model_slug: str
    scenario_prompt_sha256: str
    timestamp_utc: str

    judge: JudgeRecord

    dimensions: dict[str, DimensionScore]
    criteria: dict[str, CriterionResult]
    false_actions: dict[str, FalseActionResult]
    penalties: Penalties

    deterministic_checks: list[DeterministicCheck] = Field(default_factory=list)
    disagreements: list[JudgeDisagreement] = Field(default_factory=list)

    base_score: float
    final_score: float
