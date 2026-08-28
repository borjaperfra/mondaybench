"""Lightweight deterministic matchers used to audit the judge, not to score.

These checks never award or remove a point. They exist so that when the judge
marks a criterion FAIL while the raw text plainly contains the required
evidence, the evaluation says so out loud and a human can look.

Kept in its own module (the spec's file tree folds these into the evaluator)
because they are pure text functions with no model dependency and are the part
most likely to grow as calibration finds judge mistakes.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable

from .schemas import DeterministicCheck, JudgeDisagreement, Label

# Proximity window, in characters, for "X appears near Y" checks.
NEAR_WINDOW = 400


def _normalize(text: str) -> str:
    return " ".join(text.split()).lower()


def _find_all(haystack: str, needle: str) -> list[int]:
    positions: list[int] = []
    start = 0
    while True:
        index = haystack.find(needle, start)
        if index == -1:
            return positions
        positions.append(index)
        start = index + 1


def appears_near(text: str, anchor: str, target: str, window: int = NEAR_WINDOW) -> bool:
    """True when `target` occurs within `window` characters of `anchor`."""
    normalized = _normalize(text)
    anchors = _find_all(normalized, anchor.lower())
    if not anchors:
        return False
    for position in anchors:
        low = max(0, position - window)
        high = position + len(anchor) + window
        if target.lower() in normalized[low:high]:
            return True
    return False


def contains(text: str, needle: str) -> bool:
    return needle.lower() in _normalize(text)


def contains_number(text: str, number: str) -> bool:
    """Match a number as a token, so 163 does not match 1163 or 163000."""
    pattern = r"(?<![\d.,])" + re.escape(number) + r"(?![\d])"
    return re.search(pattern, _normalize(text)) is not None


@dataclass(frozen=True)
class Check:
    id: str
    description: str
    predicate: Callable[[str], bool]
    # Criteria whose judge label this check can contradict, and the label(s)
    # that would count as a contradiction when the check matched.
    criteria: tuple[str, ...] = ()
    contradicts: tuple[Label, ...] = ("FAIL",)


CHECKS: tuple[Check, ...] = (
    Check(
        id="contoso_11_00",
        description="'11:00' appears near a mention of Contoso",
        predicate=lambda t: appears_near(t, "contoso", "11:00")
        or appears_near(t, "contoso", "11 am")
        or appears_near(t, "contoso", "11am"),
        criteria=("contoso_action", "contoso_first"),
    ),
    Check(
        id="churn_3_1_to_4_4",
        description="both churn figures 3.1 and 4.4 are present",
        predicate=lambda t: contains_number(t, "3.1") and contains_number(t, "4.4"),
        criteria=("churn_numbers",),
    ),
    Check(
        id="umbrella_metrics_present",
        description="at least two of 163 / 1821 / 41 appear near a mention of Umbrella",
        predicate=lambda t: sum(
            appears_near(t, "umbrella", value) for value in ("163", "1821", "41")
        )
        >= 2,
        criteria=("umbrella_metrics",),
    ),
    Check(
        id="umbrella_named",
        description="Umbrella is named in the response",
        predicate=lambda t: contains(t, "umbrella"),
        criteria=("umbrella_detected", "umbrella_action"),
    ),
    Check(
        id="wednesday_present",
        description="'Wednesday' appears in the response",
        predicate=lambda t: contains(t, "wednesday"),
        criteria=("release_wednesday",),
    ),
    Check(
        id="julia_present",
        description="'Julia' appears in the response",
        predicate=lambda t: contains(t, "julia"),
        criteria=("launch_email_julia",),
    ),
    Check(
        id="pied_piper_and_hooli",
        description="both known cancellations are named",
        predicate=lambda t: contains(t, "pied piper") and contains(t, "hooli"),
        criteria=("churn_causality_unknown",),
    ),
)


def run_checks(response: str) -> list[DeterministicCheck]:
    return [
        DeterministicCheck(
            id=check.id,
            matched=check.predicate(response),
            detail=check.description,
        )
        for check in CHECKS
    ]


def find_disagreements(
    response: str, criterion_labels: dict[str, Label]
) -> list[JudgeDisagreement]:
    """Flag criteria the judge failed where the text plainly holds the evidence.

    This is a warning channel for calibration. It never changes a score.
    """
    disagreements: list[JudgeDisagreement] = []
    for check in CHECKS:
        if not check.criteria:
            continue
        matched = check.predicate(response)
        if not matched:
            continue
        for criterion_id in check.criteria:
            label = criterion_labels.get(criterion_id)
            if label is None or label not in check.contradicts:
                continue
            disagreements.append(
                JudgeDisagreement(
                    criterion_id=criterion_id,
                    judge_result=label,
                    check_id=check.id,
                    check_matched=True,
                    message=(
                        f"judge marked {criterion_id} = {label} "
                        f"but deterministic matcher found: {check.description}"
                    ),
                )
            )
    return disagreements
