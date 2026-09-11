"""Deterministic scorers for the microtests. No LLM is used to score anything.

    python scorers.py     runs the self-tests

Every prompt ends by demanding a final line of the form `ANSWER: ...`, so
parsing is a mechanical operation on that line and nothing else. Three answer
types, all closed-form: an exact clock time, an exact option letter, an exact
set of IDs.

## The rules, fixed before any response existed

1. Markdown decoration (`*`, backticks, `#`) is stripped from the whole
   response first. A model that writes `**ANSWER: D**` has answered D, and
   scoring that as UNPARSEABLE would measure formatting, not reasoning.
2. Every line matching `ANSWER:` is collected, not just the last one.
3. Each captured value is normalised by answer type. A value that yields
   nothing (no time, no letter, no ID) is discarded.
4. If the surviving normalised values disagree with each other, the result is
   **UNPARSEABLE**. The prompt asked for one answer; picking among several
   would be interpretation, and interpretation is what a deterministic scorer
   exists to avoid.
5. Exactly one surviving value is compared against the key: **CORRECT** on an
   exact match, **INCORRECT** otherwise.
6. No ANSWER line, or no value that normalises, is **UNPARSEABLE**.

UNPARSEABLE is therefore a real outcome and is always reported separately from
INCORRECT. Collapsing the two would let a formatting change look like a quality
change.
"""

from __future__ import annotations

import re

ANSWER_LINE = re.compile(r"^[ \t>-]*ANSWER[ \t]*:[ \t]*(.*)$", re.IGNORECASE | re.MULTILINE)
DECORATION = re.compile(r"[*`#_]")

_TIME = re.compile(r"\b(?P<h>[01]?\d|2[0-3])[:.](?P<m>[0-5]\d)(?::[0-5]\d)?\s*"
                   r"(?P<ap>[ap]\.?m\.?)?", re.IGNORECASE)
_LETTER = re.compile(r"(?<![A-Za-z])([A-D])(?![A-Za-z])", re.IGNORECASE)
# The canonical shape a model uses when it restates the option it picked:
# "D", "D)", "(D)", "D - none of ...". The letter it leads with is the answer,
# even when the option's own text quotes other letters. Without this, mt-02's
# correct option ("None of A, B or C") would score UNPARSEABLE precisely
# because it is the correct one, which would bias the measurement.
_LEADING_LETTER = re.compile(r"^\s*\(?\s*([A-Da-d])\s*\)?(?![A-Za-z])")
_ID = re.compile(r"\bR(\d+)\b", re.IGNORECASE)


def _strip_decoration(text: str) -> str:
    return DECORATION.sub("", text or "")


def _norm_time(value: str):
    """A single clock time as minutes-of-day, or None."""
    found = set()
    for match in _TIME.finditer(value):
        hour, minute = int(match.group("h")), int(match.group("m"))
        marker = (match.group("ap") or "").lower().replace(".", "")
        if marker:
            if hour < 1 or hour > 12:
                continue
            if marker == "pm":
                hour = 12 if hour == 12 else hour + 12
            else:
                hour = 0 if hour == 12 else hour
        if 0 <= hour <= 23:
            found.add(hour * 60 + minute)
    if len(found) != 1:
        return None
    minutes = found.pop()
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def _norm_choice(value: str):
    """A single option letter A-D, or None.

    The value's leading option letter wins when it has one; otherwise exactly
    one distinct letter must appear anywhere in the value.
    """
    leading = _LEADING_LETTER.match(value)
    if leading:
        return leading.group(1).upper()
    letters = {m.group(1).upper() for m in _LETTER.finditer(value)}
    if len(letters) != 1:
        return None
    return letters.pop()


def _norm_idset(value: str):
    """The set of request IDs, normalised and sorted, or None if empty."""
    ids = {f"R{int(m.group(1))}" for m in _ID.finditer(value)}
    if not ids:
        return None
    return ",".join(sorted(ids, key=lambda s: int(s[1:])))


NORMALISERS = {"time": _norm_time, "choice": _norm_choice, "idset": _norm_idset}


def normalise_key(answer, answer_type: str) -> str:
    """The answer key in the same normal form the parser produces."""
    if answer_type == "idset":
        ids = answer if isinstance(answer, list) else [answer]
        return ",".join(sorted((str(i).upper() for i in ids), key=lambda s: int(s[1:])))
    if answer_type == "time":
        return _norm_time(str(answer))
    return _norm_choice(str(answer))


def score(text: str, answer, answer_type: str) -> dict:
    """CORRECT / INCORRECT / UNPARSEABLE, with the parse recorded."""
    normaliser = NORMALISERS[answer_type]
    cleaned = _strip_decoration(text)
    raw_values = [m.group(1).strip() for m in ANSWER_LINE.finditer(cleaned)]
    normalised = [v for v in (normaliser(value) for value in raw_values) if v is not None]
    distinct = sorted(set(normalised))
    expected = normalise_key(answer, answer_type)

    if not distinct:
        verdict = "UNPARSEABLE"
        parsed = None
    elif len(distinct) > 1:
        verdict = "UNPARSEABLE"
        parsed = distinct
    else:
        parsed = distinct[0]
        verdict = "CORRECT" if parsed == expected else "INCORRECT"
    return {
        "verdict": verdict,
        "parsed_answer": parsed,
        "expected_answer": expected,
        "answer_lines_found": len(raw_values),
        "answer_lines_raw": raw_values[:5],
    }


SELF_TESTS = [
    # (text, answer, type, expected verdict, expected parse)
    ("ANSWER: 12:45", "12:45", "time", "CORRECT", "12:45"),
    ("blah\nANSWER: 12:45\n", "12:45", "time", "CORRECT", "12:45"),
    ("**ANSWER: 12:45**", "12:45", "time", "CORRECT", "12:45"),
    ("ANSWER: 12.45", "12:45", "time", "CORRECT", "12:45"),
    ("ANSWER: 12:45:00", "12:45", "time", "CORRECT", "12:45"),
    ("ANSWER: 12:15", "12:45", "time", "INCORRECT", "12:15"),
    ("The answer is 12:45 but I forgot the line", "12:45", "time", "UNPARSEABLE", None),
    ("ANSWER: 12:45\nANSWER: 12:15", "12:45", "time", "UNPARSEABLE", ["12:15", "12:45"]),
    ("ANSWER: 12:45\nANSWER: 12:45", "12:45", "time", "CORRECT", "12:45"),
    ("ANSWER: somewhere around noon", "12:45", "time", "UNPARSEABLE", None),
    ("ANSWER: D", "D", "choice", "CORRECT", "D"),
    ("ANSWER: D)", "D", "choice", "CORRECT", "D"),
    ("answer: d", "D", "choice", "CORRECT", "D"),
    ("ANSWER: (D) None of A, B or C", "D", "choice", "CORRECT", "D"),
    ("ANSWER: D - none of A, B or C", "D", "choice", "CORRECT", "D"),
    ("ANSWER: B) Plan 2 only", "D", "choice", "INCORRECT", "B"),
    ("ANSWER: None of A, B or C", "D", "choice", "UNPARSEABLE", None),
    ("ANSWER: Plan 2 only", "D", "choice", "UNPARSEABLE", None),
    ("ANSWER: B", "D", "choice", "INCORRECT", "B"),
    ("> ANSWER: D", "D", "choice", "CORRECT", "D"),
    ("ANSWER: R1,R2,R4", ["R1", "R2", "R4"], "idset", "CORRECT", "R1,R2,R4"),
    ("ANSWER: R4, R2, R1", ["R1", "R2", "R4"], "idset", "CORRECT", "R1,R2,R4"),
    ("ANSWER: r1,r2,r4", ["R1", "R2", "R4"], "idset", "CORRECT", "R1,R2,R4"),
    ("ANSWER: R1,R2", ["R1", "R2", "R4"], "idset", "INCORRECT", "R1,R2"),
    ("ANSWER: R2,R4,R5", ["R1", "R2", "R4"], "idset", "INCORRECT", "R2,R4,R5"),
    ("ANSWER: none", ["R1", "R2", "R4"], "idset", "UNPARSEABLE", None),
]

if __name__ == "__main__":
    failures = 0
    for text, answer, answer_type, want_verdict, want_parse in SELF_TESTS:
        got = score(text, answer, answer_type)
        ok = got["verdict"] == want_verdict and got["parsed_answer"] == want_parse
        failures += not ok
        shown = text.replace("\n", "\\n")
        print(f"{'ok  ' if ok else 'FAIL'} {shown[:42]:<44} -> {got['verdict']:<11} "
              f"{got['parsed_answer']}")
    print(f"\n{len(SELF_TESTS) - failures}/{len(SELF_TESTS)} self-tests passed")
    raise SystemExit(1 if failures else 0)
