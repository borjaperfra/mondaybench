"""Phase C: pick the instrument by looking at baseline only.

    python calibrate.py --stage 5      5 baseline samples per candidate
    python calibrate.py --stage 10     top up promising candidates to 10
    python calibrate.py --select       apply the selection rule, freeze the choice

`reasoning_effort` is never sent here. There is no flag for it and `effort` is
hard-coded to None at the single call site, so difficulty cannot be tuned
against the treatment even by accident. That is the whole point of calibrating
on baseline alone.

Promotion rule, fixed in advance: 5/5 is treated as probably saturated and 0/5
or 1/5 as probably too hard; 2, 3 or 4 correct out of 5 earns a top-up to 10
samples. The target band on 10 samples is 50-80% and the acceptable band is
40-85%.

A candidate is never edited after its results are seen. If it lands outside the
band it is discarded and the next designed candidate is used. No new candidate
is invented after seeing data.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import probe_lib as lib

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw" / "calibration.jsonl"

STAGE1_N = 5
STAGE2_N = 10
PROMOTE_CORRECT = {2, 3, 4}          # out of STAGE1_N
TARGET_BAND = (0.50, 0.80)
ACCEPTABLE_BAND = (0.40, 0.85)
SELECTION_TARGET = 0.65


def candidates() -> list[str]:
    return sorted(lib.answer_keys())


def existing() -> list[dict]:
    return lib.read_jsonl(RAW)


def counts(rows: list[dict], test_id: str) -> dict:
    """Per-candidate tallies, with both readings of a budget-exhausted sample.

    A sample can end without a scored verdict for two very different reasons. An
    infrastructure failure says nothing about the model. But `truncated_by_budget`
    - the provider closed with `finish_reason=length` after spending the whole
    output budget on reasoning and emitting no answer - is model behaviour, and
    on a *quality* metric it is arguably a failed attempt at the task.

    The pre-registered rule excludes non-OK samples from the statistics, so
    `success_rate` follows it. `success_rate_counting_unanswered` is reported
    beside it so the alternative reading is visible rather than decided
    silently, because for one candidate here the two readings disagree.
    """
    slots = [r for r in rows if r["microtest_id"] == test_id]
    mine = [r for r in slots if r["status"] == "OK"]
    verdicts = [r["verdict"] for r in mine]
    budget_exhausted = [
        r for r in slots
        if r["status"] != "OK"
        and any(a.get("kind") in ("truncated_by_budget", "empty_final_answer")
                for a in r.get("attempts", []))
    ]
    infra_failed = [r for r in slots if r["status"] != "OK" and r not in budget_exhausted]
    denominator_with_unanswered = len(mine) + len(budget_exhausted)
    return {
        "n": len(mine),
        "n_slots": len(slots),
        "correct": verdicts.count("CORRECT"),
        "incorrect": verdicts.count("INCORRECT"),
        "unparseable": verdicts.count("UNPARSEABLE"),
        "budget_exhausted_no_answer": len(budget_exhausted),
        "infrastructure_failed": len(infra_failed),
        "success_rate": round(verdicts.count("CORRECT") / len(mine), 4) if mine else None,
        "success_rate_counting_unanswered": (
            round(verdicts.count("CORRECT") / denominator_with_unanswered, 4)
            if denominator_with_unanswered else None),
        "wrong_answers": sorted({str(r["parsed_answer"]) for r in mine
                                 if r["verdict"] == "INCORRECT"}),
    }


def run_stage(target_n: int, only: list[str] | None) -> None:
    model = lib.load_model()
    provider = lib.build_provider(model)
    rows = existing()
    for test_id in candidates():
        if only is not None and test_id not in only:
            continue
        have = counts(rows, test_id)["n"]
        for index in range(have, target_n):
            sample_id = f"cal-{test_id[3:5]}-{index + 1:02d}"
            record = lib.one_call(
                provider, model,
                test_id=test_id,
                effort=None,            # baseline only. Never anything else here.
                sample_id=sample_id,
                variant="baseline",
                phase="calibration",
            )
            lib.append(RAW, record)
            rows.append(record)
            lib.print_row(record)


def report(rows: list[dict]) -> dict:
    table = {}
    for test_id in candidates():
        stats = counts(rows, test_id)
        rate = stats["success_rate"]
        if stats["n"] == 0:
            verdict = "not run"
        elif stats["n"] < STAGE2_N:
            # Judged on the rate, not on a raw count: a slot lost to a
            # non-scored sample must not turn 4/4 correct into "promising".
            if rate == 1.0:
                verdict = "saturated"
            elif rate is not None and rate <= 0.2:
                verdict = "too hard"
            elif stats["correct"] in PROMOTE_CORRECT:
                verdict = "promote"
            else:
                verdict = "inconclusive at stage 1"
        elif rate is None:
            verdict = "no data"
        elif ACCEPTABLE_BAND[0] <= rate <= ACCEPTABLE_BAND[1]:
            verdict = ("in target band" if TARGET_BAND[0] <= rate <= TARGET_BAND[1]
                       else "in acceptable band")
        elif rate > ACCEPTABLE_BAND[1]:
            verdict = "too easy"
        else:
            verdict = "too hard"
        table[test_id] = {**stats, "stage_verdict": verdict,
                          "answer_key": lib.answer_keys()[test_id]["answer"],
                          "prompt_sha256": lib.answer_keys()[test_id]["prompt_sha256"]}
    return table


def cmd_select(rows: list[dict]) -> int:
    table = report(rows)
    eligible = [
        test_id for test_id, stats in table.items()
        if stats["n"] >= STAGE2_N and stats["success_rate"] is not None
        and ACCEPTABLE_BAND[0] <= stats["success_rate"] <= ACCEPTABLE_BAND[1]
    ]
    if not eligible:
        # Where the two readings of a non-scored sample disagree about band
        # membership, say so explicitly instead of resolving it here.
        alternative = {
            test_id: stats["success_rate_counting_unanswered"]
            for test_id, stats in table.items()
            if stats["success_rate_counting_unanswered"] is not None
            and stats["success_rate"] is not None
            and stats["success_rate_counting_unanswered"] != stats["success_rate"]
        }
        in_band_under_alternative = {
            test_id: rate for test_id, rate in alternative.items()
            if ACCEPTABLE_BAND[0] <= rate <= ACCEPTABLE_BAND[1]
        }
        out = {
            "selected": None,
            "reason": "no candidate landed in the acceptable 40-85% baseline band "
                      "under the pre-registered scoring rule",
            "instruction_followed": "STOP - no calibrated instrument, and no new "
                                    "candidate is invented after seeing results",
            "alternative_reading": {
                "what": "counting a sample that spent the whole output budget on "
                        "reasoning and returned no answer as a failed attempt "
                        "rather than excluding it",
                "rates_that_change": alternative,
                "would_be_in_acceptable_band": in_band_under_alternative,
                "not_applied": True,
                "why_not_applied": "the exclusion rule was fixed before the data "
                                   "existed, and switching to the reading that "
                                   "manufactures an eligible candidate after seeing "
                                   "the results is exactly the move the "
                                   "pre-registration exists to prevent",
                "needs_a_human_decision": bool(in_band_under_alternative),
            },
            "candidates": table,
        }
        (HERE / "calibration-result.json").write_text(json.dumps(out, indent=2),
                                                      encoding="utf-8")
        print("\nSTOP: no candidate in the 40-85% band.")
        return 1

    # The selection rule, in the order it was specified.
    def sort_key(test_id: str):
        stats = table[test_id]
        return (
            abs(stats["success_rate"] - SELECTION_TARGET),      # 1: closest to 65%
            -len(stats["wrong_answers"]),                       # 2: error diversity
            lib.answer_keys()[test_id]["prompt_bytes"],          # 3: shorter prompt
            0 if lib.answer_keys()[test_id]["answer_type"] in ("choice", "time") else 1,
        )

    ranked = sorted(eligible, key=sort_key)
    chosen = ranked[0]
    out = {
        "selected": chosen,
        "selection_rule": [
            "1. baseline success rate closest to 0.65",
            "2. greater diversity of distinct wrong answers",
            "3. shorter prompt",
            "4. least ambiguous scorer (exact choice/time before set)",
        ],
        "ranking": [{"microtest_id": t, "success_rate": table[t]["success_rate"],
                     "distinct_wrong_answers": table[t]["wrong_answers"],
                     "prompt_bytes": lib.answer_keys()[t]["prompt_bytes"]}
                    for t in ranked],
        "eligible": eligible,
        "candidates": table,
        "frozen_from_here": ["prompt", "answer key", "scorer", "generation config",
                             "max tokens", "system prompt", "route", "streaming",
                             "retry behaviour"],
    }
    (HERE / "calibration-result.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nselected: {chosen} (baseline {table[chosen]['success_rate']})")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", type=int, choices=[STAGE1_N, STAGE2_N])
    parser.add_argument("--select", action="store_true")
    args = parser.parse_args()

    rows = existing()
    if args.stage == STAGE1_N:
        run_stage(STAGE1_N, None)
    elif args.stage == STAGE2_N:
        promote = [t for t, s in report(existing()).items() if s["stage_verdict"] == "promote"]
        print(f"promoting to {STAGE2_N} samples: {promote or 'nothing'}\n")
        if promote:
            run_stage(STAGE2_N, promote)
    elif args.select:
        return cmd_select(rows)
    else:
        parser.print_help()
        return 1

    rows = existing()
    table = report(rows)
    print(f"\n{'microtest':<24} {'n':>3} {'ok':>3} {'bad':>4} {'unp':>4} {'rate':>6}  "
          f"verdict")
    for test_id, stats in table.items():
        print(f"{test_id:<24} {stats['n']:>3} {stats['correct']:>3} "
              f"{stats['incorrect']:>4} {stats['unparseable']:>4} "
              f"{str(stats['success_rate']):>6}  {stats['stage_verdict']}"
              + (f"   wrong={stats['wrong_answers']}" if stats["wrong_answers"] else ""))
    (HERE / "calibration-progress.json").write_text(json.dumps(table, indent=2),
                                                    encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
