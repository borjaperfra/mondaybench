"""Deterministic scoring of the cutover answer. No LLM judge.

    python scorer.py     runs the self-tests

The answer is a clock time and the prompt demands a final line `ANSWER: HH:MM`,
identically in all three levels. The rules below are the ones from phase 1b,
unchanged, because changing the scorer between phases would make the phases
incomparable:

1. Markdown decoration is stripped first, so `**ANSWER: 16:00**` is an answer
   rather than a parse failure.
2. Every `ANSWER:` line is collected, not only the last.
3. Values are normalised to minutes-of-day; 24-hour, `16.00`, `16:00:00` and
   `4:00 pm` all normalise to the same thing.
4. Surviving values that disagree with each other are **UNPARSEABLE**. The
   prompt asked for one answer and choosing among several would be
   interpretation.
5. Exactly one surviving value is compared with the key.

## The fourth outcome

`BUDGET_EXHAUSTED` is decided outside this module, from `finish_reason` and from
the provider error kind, never from the text. A response that stopped because it
ran out of output budget is a failed attempt at the task and is counted as a
failure in the success rate - but it is reported in its own column and never
merged into INCORRECT, because "answered wrongly" and "never finished thinking"
are different behaviours with different implications.
"""

from __future__ import annotations

import re

ANSWER_LINE = re.compile(r"^[ \t>-]*ANSWER[ \t]*:[ \t]*(.*)$", re.IGNORECASE | re.MULTILINE)
DECORATION = re.compile(r"[*`#_]")
_TIME = re.compile(r"\b(?P<h>[01]?\d|2[0-3])[:.](?P<m>[0-5]\d)(?::[0-5]\d)?\s*"
                   r"(?P<ap>[ap]\.?m\.?)?", re.IGNORECASE)

#: Outcomes, in the order they are reported.
OUTCOMES = ("CORRECT", "INCORRECT", "UNPARSEABLE", "BUDGET_EXHAUSTED")


def _normalise_time(value: str) -> str | None:
    found = set()
    for match in _TIME.finditer(value):
        hour, minute = int(match.group("h")), int(match.group("m"))
        marker = (match.group("ap") or "").lower().replace(".", "")
        if marker:
            if hour < 1 or hour > 12:
                continue
            hour = (12 if hour == 12 else hour + 12) if marker == "pm" else (
                0 if hour == 12 else hour)
        if 0 <= hour <= 23:
            found.add(hour * 60 + minute)
    if len(found) != 1:
        return None
    minutes = found.pop()
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def score(text: str, answer_key: str) -> dict:
    """CORRECT / INCORRECT / UNPARSEABLE, with the parse recorded."""
    cleaned = DECORATION.sub("", text or "")
    raw = [m.group(1).strip() for m in ANSWER_LINE.finditer(cleaned)]
    normalised = [v for v in (_normalise_time(value) for value in raw) if v is not None]
    distinct = sorted(set(normalised))
    expected = _normalise_time(answer_key)
    if not distinct:
        return {"verdict": "UNPARSEABLE", "parsed_answer": None,
                "expected_answer": expected, "answer_lines_found": len(raw),
                "answer_lines_raw": raw[:5]}
    if len(distinct) > 1:
        return {"verdict": "UNPARSEABLE", "parsed_answer": distinct,
                "expected_answer": expected, "answer_lines_found": len(raw),
                "answer_lines_raw": raw[:5]}
    parsed = distinct[0]
    return {"verdict": "CORRECT" if parsed == expected else "INCORRECT",
            "parsed_answer": parsed, "expected_answer": expected,
            "answer_lines_found": len(raw), "answer_lines_raw": raw[:5]}


def outcome(scored_verdict: str, finish_reason: str | None,
            provider_error_kind: str | None = None) -> str:
    """The reported outcome, with budget exhaustion taking precedence.

    A response that hit the output ceiling is BUDGET_EXHAUSTED whether or not
    something parseable came out of it, because the run did not complete on its
    own terms. `empty_final_answer` - reasoning delivered, turn ended, no answer
    - is recorded the same way: no answer was produced.
    """
    if provider_error_kind in ("truncated_by_budget", "empty_final_answer"):
        return "BUDGET_EXHAUSTED"
    if finish_reason == "length":
        return "BUDGET_EXHAUSTED"
    return scored_verdict


SELF_TESTS = [
    ("ANSWER: 16:00", "CORRECT", "16:00"),
    ("some reasoning\n\nANSWER: 16:00\n", "CORRECT", "16:00"),
    ("**ANSWER: 16:00**", "CORRECT", "16:00"),
    ("ANSWER: 16.00", "CORRECT", "16:00"),
    ("ANSWER: 16:00:00", "CORRECT", "16:00"),
    ("ANSWER: 4:00 pm", "CORRECT", "16:00"),
    ("> ANSWER: 16:00", "CORRECT", "16:00"),
    ("ANSWER: 15:45", "INCORRECT", "15:45"),
    ("ANSWER: 18:30", "INCORRECT", "18:30"),
    ("ANSWER: 16:00\nANSWER: 16:00", "CORRECT", "16:00"),
    ("ANSWER: 16:00\nANSWER: 15:45", "UNPARSEABLE", ["15:45", "16:00"]),
    ("The verification ends at 16:00 but no answer line", "UNPARSEABLE", None),
    ("ANSWER: it cannot be done in the window", "UNPARSEABLE", None),
    ("ANSWER: impossible", "UNPARSEABLE", None),
    ("", "UNPARSEABLE", None),
]

OUTCOME_TESTS = [
    ("CORRECT", "stop", None, "CORRECT"),
    ("INCORRECT", "stop", None, "INCORRECT"),
    ("UNPARSEABLE", "stop", None, "UNPARSEABLE"),
    ("CORRECT", "length", None, "BUDGET_EXHAUSTED"),
    ("UNPARSEABLE", "length", None, "BUDGET_EXHAUSTED"),
    ("UNPARSEABLE", None, "truncated_by_budget", "BUDGET_EXHAUSTED"),
    ("UNPARSEABLE", None, "empty_final_answer", "BUDGET_EXHAUSTED"),
    ("UNPARSEABLE", None, "error", "UNPARSEABLE"),
]

if __name__ == "__main__":
    failures = 0
    for text, want_verdict, want_parse in SELF_TESTS:
        got = score(text, "16:00")
        ok = got["verdict"] == want_verdict and got["parsed_answer"] == want_parse
        failures += not ok
        print(f"{'ok  ' if ok else 'FAIL'} {text.replace(chr(10), '|')[:46]:<48} "
              f"-> {got['verdict']:<12} {got['parsed_answer']}")
    print()
    for verdict, finish, kind, want in OUTCOME_TESTS:
        got = outcome(verdict, finish, kind)
        ok = got == want
        failures += not ok
        print(f"{'ok  ' if ok else 'FAIL'} outcome({verdict}, finish={finish}, "
              f"kind={kind}) -> {got}")
    total = len(SELF_TESTS) + len(OUTCOME_TESTS)
    print(f"\n{total - failures}/{total} self-tests passed")
    raise SystemExit(1 if failures else 0)
