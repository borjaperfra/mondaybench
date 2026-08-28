"""Deterministic label-to-points conversion.

This module is the only place points are assigned. The judge produces labels;
Python produces numbers. Nothing here calls a model.
"""

from __future__ import annotations

from dataclasses import dataclass

from .scenarios import NOISE_DIMENSION, Rubric
from .schemas import (
    CriterionResult,
    DimensionScore,
    FalseActionResult,
    Penalties,
    PenaltyItem,
    PenaltyViolation,
)


@dataclass(frozen=True)
class ScoreBreakdown:
    dimensions: dict[str, DimensionScore]
    criteria: dict[str, CriterionResult]
    false_actions: dict[str, FalseActionResult]
    penalties: Penalties
    base_score: float
    final_score: float


def _round(value: float) -> float:
    """Keep fractional points exact to two places without float drift."""
    return round(value + 0.0, 2)


def score_criteria(
    rubric: Rubric, verdicts: dict[str, tuple[str, str | None, str | None]]
) -> dict[str, CriterionResult]:
    """Map each criterion's label to points.

    `verdicts` maps criterion id -> (label, evidence, reason). Every criterion in
    the rubric must be present: a missing judge result is never silently
    defaulted to FAIL or to PASS.
    """
    results: dict[str, CriterionResult] = {}
    for criterion in rubric.criteria:
        if criterion.id not in verdicts:
            raise KeyError(f"no judge verdict for criterion {criterion.id!r}")
        label, evidence, reason = verdicts[criterion.id]
        results[criterion.id] = CriterionResult(
            result=label,  # type: ignore[arg-type]
            points_awarded=_round(criterion.points_for(label)),
            points_possible=_round(criterion.points_pass),
            evidence=evidence,
            reason=reason,
        )
    return results


def score_false_actions(
    rubric: Rubric, triggered: dict[str, tuple[bool, str | None]]
) -> tuple[dict[str, FalseActionResult], float]:
    """Apply the noise-resistance deduction ladder.

    Starts at `starting_points`, deducts per triggered false action, floors at
    `minimum_points`.
    """
    noise = rubric.noise
    if noise is None:
        # No noise dimension in this rubric. Returning 0 rather than a full
        # score keeps `aggregate` from adding points for a dimension that does
        # not exist; it never reaches a score because `dimension_max` has no
        # entry for it either.
        return {}, 0.0
    results: dict[str, FalseActionResult] = {}
    hits = 0
    for action in noise.false_actions:
        was_triggered, evidence = triggered.get(action.id, (False, None))
        if was_triggered:
            hits += 1
        results[action.id] = FalseActionResult(
            triggered=was_triggered,
            points=_round(-noise.deduction_per_false_action) if was_triggered else 0.0,
            evidence=evidence,
            description=action.description,
        )
    score = max(
        noise.minimum_points,
        noise.starting_points - hits * noise.deduction_per_false_action,
    )
    return results, _round(score)


def score_penalties(rubric: Rubric, violations: list[PenaltyViolation]) -> Penalties:
    """Convert violations to negative points, capped at the rubric maximum.

    Only candidates the judge classified as `materially_misleading` cost points.
    The rest are kept in `dismissed` so a dropped penalty stays visible to a
    reviewer - the filtering happens here, in Python, not by asking the judge to
    stay quiet about what it noticed.

    The cap applies to the total, not per type, so a response cannot lose more
    than `maximum_global_penalty` however many violations it accrues.
    """
    items: list[PenaltyItem] = []
    dismissed: list[PenaltyItem] = []
    raw_total = 0.0

    for violation in violations:
        definition = rubric.penalties.get(violation.type)
        if definition is None:
            raise KeyError(f"rubric defines no penalty of type {violation.type!r}")
        if not violation.materially_misleading:
            dismissed.append(
                PenaltyItem(
                    type=violation.type,
                    points=0.0,
                    evidence=violation.evidence,
                    reason=violation.reason,
                )
            )
            continue
        items.append(
            PenaltyItem(
                type=violation.type,
                points=_round(definition.points),
                evidence=violation.evidence,
                reason=violation.reason,
            )
        )
        raw_total += definition.points

    magnitude = abs(raw_total)
    capped = magnitude > rubric.maximum_global_penalty
    total = -min(magnitude, rubric.maximum_global_penalty)
    return Penalties(
        items=items,
        dismissed=dismissed,
        raw_total=_round(raw_total),
        total=_round(total),
        capped=capped,
    )


def aggregate(
    rubric: Rubric,
    criteria: dict[str, CriterionResult],
    noise_score: float,
    penalties: Penalties,
) -> tuple[dict[str, DimensionScore], float, float]:
    """Sum criteria into dimensions, then dimensions into base and final scores."""
    dimensions: dict[str, DimensionScore] = {}
    for name, max_points in rubric.dimension_max.items():
        if name == NOISE_DIMENSION and rubric.noise is not None:
            dimensions[name] = DimensionScore(score=noise_score, max_score=_round(max_points))
            continue
        earned = sum(criteria[c.id].points_awarded for c in rubric.criteria_for(name))
        dimensions[name] = DimensionScore(score=_round(earned), max_score=_round(max_points))

    base_score = _round(sum(d.score for d in dimensions.values()))
    final_score = _round(max(0.0, base_score + penalties.total))
    return dimensions, base_score, final_score


def build_breakdown(
    rubric: Rubric,
    *,
    criterion_verdicts: dict[str, tuple[str, str | None, str | None]],
    false_actions: dict[str, tuple[bool, str | None]],
    violations: list[PenaltyViolation],
) -> ScoreBreakdown:
    criteria = score_criteria(rubric, criterion_verdicts)
    noise_results, noise_score = score_false_actions(rubric, false_actions)
    penalties = score_penalties(rubric, violations)
    dimensions, base_score, final_score = aggregate(rubric, criteria, noise_score, penalties)
    return ScoreBreakdown(
        dimensions=dimensions,
        criteria=criteria,
        false_actions=noise_results,
        penalties=penalties,
        base_score=base_score,
        final_score=final_score,
    )
