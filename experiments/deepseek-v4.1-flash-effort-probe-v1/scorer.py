"""Deterministic scoring of one frozen arithmetic exercise. No LLM judge.

THE EXERCISE (frozen-prompt.txt) has one objectively correct answer. A: 2h, then
B: 3h (B waits for A), then C: 1h (C cannot overlap B, and there is one worker
anyway). Six hours of work from 09:00, inside an 8h day, so the last task
finishes at **15:00**.

## Why two scorers and not one

The prompt says "Give only the finish time of the last task", so a bare `15:00`
is the expected shape. But a longer answer that walks the schedule mentions
11:00 and 14:00 on the way, and any rule that reads those is guessing at intent.
Two rules are applied to every sample and both are recorded:

* `strict` - the set of DISTINCT times in the response. Exactly {15:00} is
  CORRECT; exactly one other time is INCORRECT; more than one distinct time is
  UNPARSEABLE, because the response did not answer the question as asked and
  choosing among its numbers would be an interpretation.
* `last_time` - the last time token in the response, the usual "final answer
  comes last" convention. Reported as a robustness check, never as the headline.

Both are pure functions of the text. Neither can drift between variants, and the
strict rule is the primary because it refuses ambiguity instead of resolving it.

`strict` is deliberately the conservative one: if `reasoning_effort=high` makes
responses more verbose, that shows up as UNPARSEABLE rather than being quietly
scored as correct, and the two scorers side by side make that visible.

## Recognised time formats

    15:00   15.00   15h   3:00 pm   3 pm   3pm   15:00:00
    "three o'clock" and other prose numerals are NOT recognised and make the
    response UNPARSEABLE under `strict` if no digit time is present at all.

Bare integers ("15", "3") are NOT read as times: the prompt contains durations
("2h, 3h, 1h") and a bare number is not unambiguously a clock time.
"""

from __future__ import annotations

import re

CORRECT_MINUTES = 15 * 60  # 15:00

# 15:00 / 15.00 / 15:00:00, optionally followed by am/pm
_COLON = re.compile(r"\b(?P<h>[01]?\d|2[0-3])[:.](?P<m>[0-5]\d)(?::[0-5]\d)?\s*(?P<ap>[ap]\.?m\.?)?",
                    re.IGNORECASE)
# 15h / 3 pm / 3pm  (hour with an explicit marker, never a bare integer)
_HOUR_ONLY = re.compile(r"\b(?P<h>[01]?\d|2[0-3])\s*(?:h\b|(?P<ap>[ap]\.?m\.?))", re.IGNORECASE)


def _to_minutes(hour: int, minute: int, ampm: str | None) -> int | None:
    if ampm:
        marker = ampm.lower().replace(".", "")
        if hour < 1 or hour > 12:
            return None
        if marker == "pm":
            hour = 12 if hour == 12 else hour + 12
        else:
            hour = 0 if hour == 12 else hour
    if not (0 <= hour <= 23):
        return None
    return hour * 60 + minute


def find_times(text: str) -> list[int]:
    """Every clock time in the text, in order of appearance, as minutes-of-day.

    Overlapping matches are avoided by consuming the colon forms first and
    blanking the spans they occupied, so `15:00` is never also read as `15h`.
    """
    found: list[tuple[int, int]] = []
    remaining = list(text)
    for match in _COLON.finditer(text):
        minutes = _to_minutes(int(match.group("h")), int(match.group("m")), match.group("ap"))
        if minutes is not None:
            found.append((match.start(), minutes))
        for i in range(match.start(), match.end()):
            remaining[i] = " "
    for match in _HOUR_ONLY.finditer("".join(remaining)):
        minutes = _to_minutes(int(match.group("h")), 0, match.group("ap"))
        if minutes is not None:
            found.append((match.start(), minutes))
    return [m for _, m in sorted(found)]


def score_strict(text: str) -> str:
    """CORRECT / INCORRECT / UNPARSEABLE from the set of distinct times."""
    times = find_times(text or "")
    distinct = sorted(set(times))
    if not distinct:
        return "UNPARSEABLE"
    if len(distinct) > 1:
        return "UNPARSEABLE"
    return "CORRECT" if distinct[0] == CORRECT_MINUTES else "INCORRECT"


def score_last_time(text: str) -> str:
    """CORRECT / INCORRECT / UNPARSEABLE from the last time mentioned."""
    times = find_times(text or "")
    if not times:
        return "UNPARSEABLE"
    return "CORRECT" if times[-1] == CORRECT_MINUTES else "INCORRECT"


def score(text: str) -> dict[str, object]:
    times = find_times(text or "")
    return {
        "strict": score_strict(text),
        "last_time": score_last_time(text),
        "times_found_minutes": times,
        "distinct_times_minutes": sorted(set(times)),
    }


SELF_TEST = [
    ("15:00", "CORRECT", "CORRECT"),
    ("15.00", "CORRECT", "CORRECT"),
    ("3:00 pm", "CORRECT", "CORRECT"),
    ("3pm", "CORRECT", "CORRECT"),
    ("15h", "CORRECT", "CORRECT"),
    ("The last task finishes at 15:00.", "CORRECT", "CORRECT"),
    ("17:00", "INCORRECT", "INCORRECT"),
    ("18:00", "INCORRECT", "INCORRECT"),
    ("A ends 11:00, B ends 14:00, C ends 15:00", "UNPARSEABLE", "CORRECT"),
    ("A ends 11:00, B 14:00, C 16:00", "UNPARSEABLE", "INCORRECT"),
    ("three o'clock", "UNPARSEABLE", "UNPARSEABLE"),
    ("", "UNPARSEABLE", "UNPARSEABLE"),
    ("15", "UNPARSEABLE", "UNPARSEABLE"),
    ("15:00:00", "CORRECT", "CORRECT"),
    ("Finish: 15:00 (15:00)", "CORRECT", "CORRECT"),
]

if __name__ == "__main__":
    failures = 0
    for text, want_strict, want_last in SELF_TEST:
        got_strict, got_last = score_strict(text), score_last_time(text)
        ok = got_strict == want_strict and got_last == want_last
        failures += not ok
        print(f"{'ok ' if ok else 'FAIL'} {text!r:<45} strict={got_strict:<11} last={got_last}")
    print(f"\n{len(SELF_TEST) - failures}/{len(SELF_TEST)} self-tests passed")
    raise SystemExit(1 if failures else 0)
