from __future__ import annotations

import pytest

from mondaybench.scenarios import NOISE_DIMENSION
from mondaybench.schemas import PenaltyViolation
from mondaybench.scoring import (
    build_breakdown,
    score_criteria,
    score_false_actions,
    score_penalties,
)


def _all(rubric, label: str):
    return {c.id: (label, "evidence", "reason") for c in rubric.criteria}


def _no_false_actions(rubric):
    return {a.id: (False, None) for a in rubric.noise.false_actions}


# --------------------------------------------------------------------------
# label -> points mapping
# --------------------------------------------------------------------------


def test_pass_awards_full_points(rubric):
    results = score_criteria(rubric, _all(rubric, "PASS"))
    for criterion in rubric.criteria:
        assert results[criterion.id].points_awarded == criterion.points_pass


def test_partial_awards_partial_points(rubric):
    results = score_criteria(rubric, _all(rubric, "PARTIAL"))
    for criterion in rubric.criteria:
        assert results[criterion.id].points_awarded == criterion.points_partial


def test_fail_awards_zero(rubric):
    results = score_criteria(rubric, _all(rubric, "FAIL"))
    assert all(r.points_awarded == 0 for r in results.values())


def test_fractional_points_survive(rubric):
    # umbrella_action is the 7 / 3.5 / 0 criterion
    results = score_criteria(rubric, _all(rubric, "PARTIAL"))
    assert results["umbrella_action"].points_awarded == 3.5
    assert results["churn_numbers"].points_awarded == 1.5


def test_missing_verdict_raises_rather_than_defaulting(rubric):
    verdicts = _all(rubric, "PASS")
    del verdicts["contoso_action"]
    with pytest.raises(KeyError, match="contoso_action"):
        score_criteria(rubric, verdicts)


# --------------------------------------------------------------------------
# noise resistance
# --------------------------------------------------------------------------


def test_no_false_actions_keeps_full_noise_points(rubric):
    _, score = score_false_actions(rubric, _no_false_actions(rubric))
    assert score == rubric.noise.starting_points == 10


def test_each_false_action_deducts_two(rubric):
    triggered = _no_false_actions(rubric)
    triggered["lunch"] = (True, "suggests deciding lunch")
    triggered["icon"] = (True, "reopens the icon debate")
    results, score = score_false_actions(rubric, triggered)
    assert score == 6
    assert results["lunch"].points == -2
    assert results["icon"].triggered is True
    assert results["acme_active"].triggered is False


def test_noise_floors_at_zero(rubric):
    triggered = {a.id: (True, "x") for a in rubric.noise.false_actions}
    _, score = score_false_actions(rubric, triggered)
    assert score == rubric.noise.minimum_points == 0


# --------------------------------------------------------------------------
# global penalties
# --------------------------------------------------------------------------


def test_no_violations_means_no_penalty(rubric):
    penalties = score_penalties(rubric, [])
    assert penalties.total == 0
    assert penalties.capped is False


def test_penalty_points_come_from_the_rubric(rubric):
    penalties = score_penalties(
        rubric,
        [
            PenaltyViolation(type="MATERIAL_HALLUCINATION", evidence="e", reason="r"),
            PenaltyViolation(type="PROHIBITED_ACTION", evidence="e", reason="r"),
        ],
    )
    assert penalties.total == -15
    assert penalties.capped is False
    assert [i.points for i in penalties.items] == [-5, -10]


def test_penalties_are_capped_at_twenty(rubric):
    violations = [
        PenaltyViolation(type="PROHIBITED_ACTION", evidence="e", reason="r") for _ in range(4)
    ]
    penalties = score_penalties(rubric, violations)
    assert penalties.raw_total == -40
    assert penalties.total == -20
    assert penalties.capped is True


def test_unknown_penalty_type_raises(rubric):
    class Rogue:
        type = "SOMETHING_ELSE"
        evidence = None
        reason = None

    with pytest.raises(KeyError):
        score_penalties(rubric, [Rogue()])  # type: ignore[list-item]


# --------------------------------------------------------------------------
# aggregation
# --------------------------------------------------------------------------


def test_perfect_response_scores_one_hundred(rubric):
    breakdown = build_breakdown(
        rubric,
        criterion_verdicts=_all(rubric, "PASS"),
        false_actions=_no_false_actions(rubric),
        violations=[],
    )
    assert breakdown.base_score == 100
    assert breakdown.final_score == 100


def test_dimension_totals_match_the_rubric_maximums(rubric):
    breakdown = build_breakdown(
        rubric,
        criterion_verdicts=_all(rubric, "PASS"),
        false_actions=_no_false_actions(rubric),
        violations=[],
    )
    for name, max_points in rubric.dimension_max.items():
        assert breakdown.dimensions[name].score == max_points
        assert breakdown.dimensions[name].max_score == max_points


def test_all_fail_scores_zero_but_keeps_noise_points(rubric):
    breakdown = build_breakdown(
        rubric,
        criterion_verdicts=_all(rubric, "FAIL"),
        false_actions=_no_false_actions(rubric),
        violations=[],
    )
    # A response that answers nothing still triggers no false actions.
    assert breakdown.dimensions[NOISE_DIMENSION].score == 10
    assert breakdown.base_score == 10


def test_final_score_never_goes_below_zero(rubric):
    breakdown = build_breakdown(
        rubric,
        criterion_verdicts=_all(rubric, "FAIL"),
        false_actions={a.id: (True, "x") for a in rubric.noise.false_actions},
        violations=[
            PenaltyViolation(type="PROHIBITED_ACTION", evidence="e", reason="r") for _ in range(3)
        ],
    )
    assert breakdown.base_score == 0
    assert breakdown.penalties.total == -20
    assert breakdown.final_score == 0


def test_penalties_subtract_from_base(rubric):
    breakdown = build_breakdown(
        rubric,
        criterion_verdicts=_all(rubric, "PASS"),
        false_actions=_no_false_actions(rubric),
        violations=[PenaltyViolation(type="MAJOR_CONTRADICTION", evidence="e", reason="r")],
    )
    assert breakdown.base_score == 100
    assert breakdown.final_score == 95


def test_a_verbose_all_partial_response_scores_about_half(rubric):
    # Rule 5: verbosity must not be rewarded. Half-credit labels give half marks.
    breakdown = build_breakdown(
        rubric,
        criterion_verdicts=_all(rubric, "PARTIAL"),
        false_actions=_no_false_actions(rubric),
        violations=[],
    )
    non_noise_max = sum(
        v for k, v in rubric.dimension_max.items() if k != NOISE_DIMENSION
    )
    assert breakdown.base_score == pytest.approx(non_noise_max / 2 + 10)


# --------------------------------------------------------------------------
# materially_misleading: the judge classifies, Python filters
# --------------------------------------------------------------------------
#
# Calibration produced penalty entries whose own reasons read "Not a
# violation-level issue on its own" and "Minor attribution difference only" -
# and they still cost 5 points each. Instructing the judge to stay silent about
# non-violations did not work. It now classifies each candidate explicitly and
# the filtering happens here.


def test_dismissed_candidates_cost_nothing(rubric):
    penalties = score_penalties(
        rubric,
        [
            PenaltyViolation(
                type="MATERIAL_HALLUCINATION",
                evidence="Sarah Mitchell (Contoso legal)",
                reason="Minor attribution difference only.",
                materially_misleading=False,
            )
        ],
    )
    assert penalties.total == 0
    assert penalties.items == []
    # But it stays visible to a reviewer rather than vanishing.
    assert len(penalties.dismissed) == 1
    assert penalties.dismissed[0].points == 0.0
    assert "Minor attribution" in (penalties.dismissed[0].reason or "")


def test_real_and_dismissed_candidates_are_separated(rubric):
    penalties = score_penalties(
        rubric,
        [
            PenaltyViolation(
                type="PROHIBITED_ACTION",
                evidence="send the pricing to Initech",
                reason="explicitly forbidden",
                materially_misleading=True,
            ),
            PenaltyViolation(
                type="MATERIAL_HALLUCINATION",
                evidence="paraphrase",
                reason="reasonable compression",
                materially_misleading=False,
            ),
        ],
    )
    assert penalties.total == -10
    assert len(penalties.items) == 1
    assert len(penalties.dismissed) == 1


def test_all_dismissed_leaves_the_score_untouched(rubric):
    breakdown = build_breakdown(
        rubric,
        criterion_verdicts=_all(rubric, "PASS"),
        false_actions=_no_false_actions(rubric),
        violations=[
            PenaltyViolation(
                type="MATERIAL_HALLUCINATION",
                evidence="e",
                reason="minor",
                materially_misleading=False,
            )
            for _ in range(4)
        ],
    )
    assert breakdown.base_score == 100
    assert breakdown.final_score == 100
    assert len(breakdown.penalties.dismissed) == 4


def test_unclassified_candidate_still_scores(rubric):
    """A judge that omits the field must not get a free pass for the model.

    Defaulting to "not a violation" would let a malformed verdict erase a real
    penalty silently. Defaulting to scoring it is the safe direction.
    """
    violation = PenaltyViolation(type="MAJOR_CONTRADICTION", evidence="e", reason="r")
    assert violation.materially_misleading is True
    assert score_penalties(rubric, [violation]).total == -5


def test_the_cap_applies_only_to_scored_violations(rubric):
    violations = [
        PenaltyViolation(
            type="PROHIBITED_ACTION", evidence="e", reason="r", materially_misleading=True
        )
        for _ in range(4)
    ] + [
        PenaltyViolation(
            type="PROHIBITED_ACTION", evidence="e", reason="r", materially_misleading=False
        )
        for _ in range(5)
    ]
    penalties = score_penalties(rubric, violations)
    assert penalties.raw_total == -40  # the four real ones
    assert penalties.total == -20  # capped
    assert len(penalties.dismissed) == 5
