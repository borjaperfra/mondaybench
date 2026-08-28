"""Pydantic models for every artifact MondayBench writes to disk.

Two schemas matter: the immutable raw generation (`BenchmarkRun`) and the
evaluation (`Evaluation`). Both carry `schema_version` so future readers can
tell what they are looking at.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

Label = Literal["PASS", "PARTIAL", "FAIL"]
# monday-002 v0.2 adds MAJOR_PLANNING_ERROR: a schedule or dependency order that
# cannot actually happen. The other three are shared with monday-001's rubric.
PenaltyType = Literal[
    "MATERIAL_HALLUCINATION",
    "PROHIBITED_ACTION",
    "MAJOR_PLANNING_ERROR",
    "MAJOR_CONTRADICTION",
]


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
    reasoning_enabled: bool
    # Recorded when the provider rejects a parameter the config asked for
    # (e.g. Anthropic Opus 5 rejects `temperature`), per IMPLEMENTATION.md s5.
    unsupported_parameters: list[str] = Field(default_factory=list)
    system_prompt_sent: bool = True


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
