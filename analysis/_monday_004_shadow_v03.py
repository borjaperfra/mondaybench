"""Build the rubric-0.3 shadow verdicts from the rubric-0.2 shadow verdicts.

    python analysis/_monday_004_shadow_v03.py

Writes `verdicts/monday-004/shadow-v0.3.jsonl`.

v0.3 differs from v0.2 by exactly one new criterion and three repricings. A
reprice changes no label, so every v0.2 label is carried across unchanged and
only `figures_carried_correctly` is judged fresh - six labels, each written out
below with the figures it rests on.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
V02 = REPO_ROOT / "verdicts" / "monday-004" / "shadow-v0.2.jsonl"
OUT = REPO_ROOT / "verdicts" / "monday-004" / "shadow-v0.3.jsonl"

RUNS = {
    "qwen3.8-flash": "monday-004__qwen3.8-flash__001",
    "glm5.3-flash": "monday-004__glm5.3-flash__001",
    "glm5.2": "monday-004__glm5.2__001",
    "deepseek-v4-flash": "monday-004__deepseek-v4-flash__002",
    "gemma4": "monday-004__gemma4__001",
    "qwen3.6": "monday-004__qwen3.6__001",
}

FIGURES = {
    "qwen3.8-flash": (
        "PARTIAL",
        "'Pro tokens: 2,725.5M September to 2,783.9M October = +2.1%' (September is 2,425.5M) and 'Pro active users: 338 September to 364 October' (288 and 331)",
        "Three incorrect figures, all inside the Pro plan's usage block, and the wrong September token value produces a +2.1% trajectory that reads against the +14.8% request trajectory the same response states correctly two lines above. No decision rests on any of them: the Pro recommendation is carried by the request growth, the margin and the three accounts over their included volume, all of which are exact. That is the PARTIAL band - non-decision-changing slips with the recommendation still standing. A stricter reading is available and would be defensible: the FAIL band names 'repeated incorrect figures', and three is repeated. It is graded PARTIAL because the three are one lapse in one sub-table rather than errors spread across the analysis, and because the divergence they create is not a stated self-contradiction - a falling tokens-per-request ratio is a real phenomenon elsewhere in this pack.",
    ),
    "glm5.3-flash": (
        "PARTIAL",
        "'Enterprise has 8 of 14 customers with high-severity api_errors or performance tickets in October (stark, wayne, umbrella, contoso, initech, cyberdyne, soylent, plus nakatomi before churn)' - the correct count is 7; nakatomi is on the pro plan, not enterprise",
        "One slip: a pro-plan customer counted inside an enterprise-plan statistic, moving 7 to 8. Everything else checkable is exact, including support volume 59 to 74, unresolved backlog 20 to 24, api-error tickets 10 to 12, blended margin 35.2% to 32.5%, SMB new ARR EUR 247.2k and Mid-market -EUR 42k. Nothing rests on the 8. Not charged under `support_normalized`, which passed on the cost-against-revenue comparison rather than on this figure.",
    ),
    "glm5.2": (
        "PASS",
        "per-customer economics 15,143 / 13,907 / 5,313 / 4,611 / 933 / 792, the full two-month attribution table, new SMB logo ACV EUR 26.6k against EUR 30.9k churned, SMB 5.4% of active ARR - all exact",
        "Its one figure error, 'SMB churned 4 of 14 customers ... 28.6% MoM churn', is the error `segment_retention_quantified` already prices at PARTIAL and is not charged twice. Nothing else it relies on is wrong.",
    ),
    "deepseek-v4-flash": (
        "PASS",
        "revenue table 797,100 / 873,400 / 746,100 / 757,700 / 732,400, all six contribution and margin figures, the October attribution split, active Starter MRR EUR 24.1k to EUR 21.7k - all exact",
        "Its two errors are both already priced: '4 of 4 churned customers were SMB Starter' under `segment_retention_quantified`, and 'All plans are below included request volumes' under `plan_trajectory_evidence`, where it is the FAIL. Neither is charged again here, and no third error exists.",
    ),
    "gemma4": (
        "FAIL",
        "'September Total Revenue: EUR 673,100 ... October Total Revenue: EUR 754,400'. Neither figure is any total in the pack: the raw sums are 797,100 and 892,900, the deduplicated October is 873,400, and the recurring pair is 746,100 and 757,700",
        "Two revenue totals that match nothing on any basis, and the executive summary's claim of 'high-growth revenue' rests on them. This is not the same error the revenue criteria price: those price the failure to normalise, and a response can fail to normalise while still summing correctly - DeepSeek did exactly that. Producing a total that is arithmetically unreachable from the file is a separate defect and nothing else in the rubric looks at it.",
    ),
    "qwen3.6": (
        "PARTIAL",
        "'September Subscription Revenue: EUR 646,100 ... October Subscription Revenue: EUR 657,700' against its own later 'Total MRR (Oct): EUR 757,700 ... Total MRR (Sep): EUR 746,100', both taken from plans.csv and both correct",
        "Two wrong totals contradicted by its own correct figures three paragraphs later, never reconciled. Held at PARTIAL rather than FAIL because `revenue_conclusion` already cited this contradiction as part of why it is PARTIAL there, so charging the full weight here would be paying twice for one lapse. The units error, adding EUR 15,000 of MRR to EUR 123,600 of ARR, is priced under `sample_size_arr_context`.",
    ),
}


def main() -> None:
    lines = [
        "# MondayBench #004 - SHADOW verdicts under PROPOSED rubric 0.3.",
        "#",
        "# Generated by analysis/_monday_004_shadow_v03.py from the rubric-0.2",
        "# shadow verdicts. v0.3 adds one criterion and reprices three; a reprice",
        "# changes no label, so only `figures_carried_correctly` is judged fresh.",
        "#",
        "#   mondaybench evaluate --scenario monday-004 --all-models \\",
        "#       --evaluator evaluator-opus5-v0.4-calibration-3 \\",
        "#       --verdicts verdicts/monday-004/shadow-v0.3.jsonl",
    ]
    carried = 0
    for raw in V02.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        lines.append(line)
        carried += 1

    for slug, run_id in RUNS.items():
        result, evidence, reason = FIGURES[slug]
        lines.append(
            json.dumps(
                {
                    "run_id": run_id,
                    "kind": "criterion",
                    "criterion_id": "figures_carried_correctly",
                    "result": result,
                    "evidence": evidence,
                    "reason": reason,
                },
                ensure_ascii=False,
            )
        )

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {OUT.relative_to(REPO_ROOT)}")
    print(f"  {carried} entries carried from the v0.2 shadow")
    print(f"  {len(FIGURES)} figures_carried_correctly labels judged fresh")


if __name__ == "__main__":
    main()
