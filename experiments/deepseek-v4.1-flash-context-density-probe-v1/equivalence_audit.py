"""Prove the three levels are the same problem before any API call.

    python equivalence_audit.py

Writes `equivalence-audit.json` and `prompts/hashes.json`, and fails loudly if
any invariant breaks. It refuses to write the hashes file when the audit fails,
so a broken instrument cannot be frozen by accident.

## The two invariants, and why they are enough

1. **Every anchor appears exactly once in every level, character for
   character.** So no level is missing a relevant fact, no level has an extra
   one, and no level paraphrases one into something subtly different.

2. **Every occurrence of a protected term lies inside an anchor.** The protected
   terms are the seven task names, the three people, the shared resource, the
   optional item and the word for the exercise itself. So no filler sentence, in
   any level, can state, imply, weaken or contradict a fact about the tasks or
   the people. Filler is structurally incapable of touching the problem.

Together these turn "the same problem with more context" from a claim into a
checked property. What the levels are then free to differ in is exactly what
this experiment varies: total volume, how far apart related facts sit, and how
much plausible irrelevant material surrounds them.

## What is measured, not asserted

Dispersion is reported rather than assumed: for every level the audit records
each anchor's character offset, the span between the first and last anchor, the
mean gap between consecutive anchors, and - the number that matters most for
this hypothesis - the distance between each stale fact and the update that
supersedes it.
"""

from __future__ import annotations

import hashlib
import json
import statistics
from pathlib import Path

from anchors import ANCHORS, BINDING, FAMILIES, PROTECTED_TERMS

HERE = Path(__file__).resolve().parent
PROMPTS = HERE / "prompts"
LEVELS = ("compact", "medium", "dense")

#: stale fact -> the update that supersedes it. The distance between the two is
#: the core quantity this experiment varies.
SUPERSESSION_PAIRS = [
    ("C17_stale_index_owner", "C18_update_index_owner"),
    ("C19_stale_window_nadia", "C20_update_window_nadia"),
    ("C21_stale_perms_order", "C22_update_perms_order"),
    ("C28_stale_alarm", "C29_alarm_explained"),
]


def read_level(level: str) -> str:
    return (PROMPTS / f"{level}.txt").read_bytes().decode("utf-8")


def anchor_spans(text: str) -> tuple[dict, list[str]]:
    """Offset of each anchor, plus complaints about counts that are not one."""
    spans: dict[str, tuple[int, int]] = {}
    problems: list[str] = []
    for key, sentence in ANCHORS.items():
        count = text.count(sentence)
        if count != 1:
            problems.append(f"{key}: appears {count} times, expected exactly 1")
            if count == 0:
                continue
        start = text.index(sentence)
        spans[key] = (start, start + len(sentence))
    return spans, problems


def protected_term_violations(text: str, spans: dict) -> list[dict]:
    """Occurrences of a protected term that sit outside every anchor."""
    allowed = sorted(spans.values())
    violations = []
    for term in PROTECTED_TERMS:
        start = 0
        while True:
            found = text.find(term, start)
            if found == -1:
                break
            end = found + len(term)
            inside = any(a <= found and end <= b for a, b in allowed)
            if not inside:
                line_number = text.count("\n", 0, found) + 1
                line_start = text.rfind("\n", 0, found) + 1
                line_end = text.find("\n", found)
                violations.append({
                    "term": term,
                    "offset": found,
                    "line": line_number,
                    "context": text[line_start:line_end if line_end != -1 else None][:160],
                })
            start = end
    return violations


def dispersion(text: str, spans: dict) -> dict:
    offsets = sorted(start for start, _ in spans.values())
    gaps = [b - a for a, b in zip(offsets, offsets[1:])]
    return {
        "chars": len(text),
        "estimated_tokens_chars_over_4": round(len(text) / 4),
        "lines": text.count("\n") + 1,
        "first_anchor_offset": offsets[0] if offsets else None,
        "last_anchor_offset": offsets[-1] if offsets else None,
        "anchor_span_chars": (offsets[-1] - offsets[0]) if len(offsets) > 1 else 0,
        "mean_gap_between_anchors": round(statistics.fmean(gaps)) if gaps else 0,
        "median_gap_between_anchors": round(statistics.median(gaps)) if gaps else 0,
        "max_gap_between_anchors": max(gaps) if gaps else 0,
        "supersession_distances_chars": {
            f"{stale} -> {update}": (spans[update][0] - spans[stale][0])
            for stale, update in SUPERSESSION_PAIRS
            if stale in spans and update in spans
        },
    }


def main() -> int:
    key = json.loads((HERE / "answer-key.json").read_text(encoding="utf-8"))
    per_level = {}
    problems: list[str] = []

    for level in LEVELS:
        text = read_level(level)
        spans, count_problems = anchor_spans(text)
        violations = protected_term_violations(text, spans)
        problems += [f"{level}: {p}" for p in count_problems]
        problems += [f"{level}: protected term '{v['term']}' outside any anchor at "
                     f"line {v['line']}: {v['context']!r}" for v in violations]
        per_level[level] = {
            "file": f"prompts/{level}.txt",
            "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "bytes": len(text.encode("utf-8")),
            "anchors_found": len(spans),
            "anchors_expected": len(ANCHORS),
            "protected_term_violations": violations,
            "dispersion": dispersion(text, spans),
            "anchor_offsets": {k: v[0] for k, v in sorted(spans.items(),
                                                          key=lambda kv: kv[1][0])},
        }

    constraint_map = {
        anchor: {
            "family": FAMILIES[anchor],
            "binding_on_the_answer": anchor in BINDING,
            "sentence": ANCHORS[anchor],
            "offset_in": {level: per_level[level]["anchor_offsets"].get(anchor)
                          for level in LEVELS},
            "present_in_all_levels": all(anchor in per_level[level]["anchor_offsets"]
                                         for level in LEVELS),
            "identical_wording_in_all_levels": True,
        }
        for anchor in ANCHORS
    }

    all_present = all(entry["present_in_all_levels"] for entry in constraint_map.values())
    no_violations = all(not per_level[level]["protected_term_violations"]
                        for level in LEVELS)
    audit = {
        "generated_utc": __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "what_this_proves": [
            "every relevant fact is a fixed sentence shared verbatim by all three "
            "levels, appearing exactly once in each",
            "every mention of a task, a person or the shared resource sits inside "
            "one of those sentences, so no filler can affect the problem",
            "the answer key is therefore the same for all three levels by "
            "construction, not by inspection",
        ],
        "what_this_does_not_prove": [
            "that the three levels are equally easy to read. They are not, and "
            "that is the variable under test",
            "that a model will treat them as the same problem. That is the "
            "measurement",
        ],
        "answer_key": key["answer"],
        "answer_type": key["answer_type"],
        "answer_identical_across_levels": True,
        "constraints_total": len(ANCHORS) - 2,   # the two question anchors are not constraints
        "constraints_binding_on_the_answer": sum(
            1 for entry in constraint_map.values() if entry["binding_on_the_answer"]),
        "no_relevant_constraint_added_only_to_medium_or_dense": all_present,
        "no_relevant_constraint_removed_from_any_level": all_present,
        "no_distractor_can_change_the_solution": no_violations,
        "no_new_ambiguity_introduced": no_violations and all_present,
        "constraint_map": constraint_map,
        "levels": per_level,
        "problems": problems,
        "verdict": "CLEAN" if not problems else "FAILED",
    }
    (HERE / "equivalence-audit.json").write_text(json.dumps(audit, indent=2),
                                                 encoding="utf-8")

    print(f"{'level':<9} {'bytes':>7} {'est tok':>8} {'anchors':>8} "
          f"{'span':>7} {'mean gap':>9} {'max gap':>8}  violations")
    for level in LEVELS:
        entry = per_level[level]
        disp = entry["dispersion"]
        print(f"{level:<9} {entry['bytes']:>7} "
              f"{disp['estimated_tokens_chars_over_4']:>8} "
              f"{entry['anchors_found']:>3}/{entry['anchors_expected']:<4} "
              f"{disp['anchor_span_chars']:>7} {disp['mean_gap_between_anchors']:>9} "
              f"{disp['max_gap_between_anchors']:>8}  "
              f"{len(entry['protected_term_violations'])}")

    print("\nsupersession distances (chars between the stale fact and its update):")
    for stale, update in SUPERSESSION_PAIRS:
        row = "  " + f"{stale.split('_', 1)[1]:<22}"
        for level in LEVELS:
            value = per_level[level]["dispersion"]["supersession_distances_chars"].get(
                f"{stale} -> {update}")
            row += f" {level}={value!s:>7}"
        print(row)

    print(f"\nverdict: {audit['verdict']}")
    if problems:
        print(f"\n{len(problems)} problem(s):")
        for problem in problems[:40]:
            print(f"  - {problem}")
        print("\nhashes NOT written; the instrument is not frozen.")
        return 1

    hashes = {
        level: {"file": per_level[level]["file"],
                "sha256": per_level[level]["sha256"],
                "bytes": per_level[level]["bytes"],
                "estimated_tokens": per_level[level]["dispersion"][
                    "estimated_tokens_chars_over_4"]}
        for level in LEVELS
    }
    hashes["answer_key"] = key["answer"]
    hashes["frozen"] = True
    (PROMPTS / "hashes.json").write_text(json.dumps(hashes, indent=2), encoding="utf-8")
    print("wrote -> equivalence-audit.json, prompts/hashes.json (FROZEN)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
