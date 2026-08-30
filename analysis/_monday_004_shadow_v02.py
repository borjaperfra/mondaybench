"""Build the rubric-0.2 shadow verdicts from the recorded v0.1 verdicts.

    python analysis/_monday_004_shadow_v02.py

Writes `verdicts/monday-004/shadow-v0.2.jsonl`.

No response was re-read blind. The v0.1 labels were produced against the same
six responses in the same session, and for the eighteen criteria whose text did
not change they are carried across unaltered - re-labelling identical text
against identical wording would only add noise. What IS re-judged is stated
here, one entry per change, with the reasoning that produced it:

  * `segment_churn_math` -> `segment_retention_quantified`: rewritten criterion,
    six fresh labels.
  * `absolute_vs_scalable_economics`: new criterion, six fresh labels.
  * `plan_trajectory_evidence`: new criterion, six fresh labels.
  * `enterprise_revenue_not_margin`: removed from the rubric, labels dropped.
  * `support_normalized`: the criterion now names support cost as a share of
    plan revenue as an acceptable denominator. Two runs used exactly that and
    were held at PARTIAL under wording that did not list it; both are re-judged.

Everything else keeps its v0.1 label and simply scores against a different
point value where the weight moved.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
V01 = REPO_ROOT / "verdicts" / "monday-004" / "calibration.jsonl"
OUT = REPO_ROOT / "verdicts" / "monday-004" / "shadow-v0.2.jsonl"

RUNS = {
    "qwen3.8-flash": "monday-004__qwen3.8-flash__001",
    "glm5.3-flash": "monday-004__glm5.3-flash__001",
    "glm5.2": "monday-004__glm5.2__001",
    "deepseek-v4-flash": "monday-004__deepseek-v4-flash__002",
    "gemma4": "monday-004__gemma4__001",
    "qwen3.6": "monday-004__qwen3.6__001",
}

DROPPED = {"enterprise_revenue_not_margin", "segment_churn_math"}

# --- re-judged criteria ----------------------------------------------------
# (model, criterion) -> (result, evidence, reason)

NEW: dict[tuple[str, str], tuple[str, str, str]] = {
    # ---- segment_retention_quantified (rewritten) -------------------------
    ("qwen3.8-flash", "segment_retention_quantified"): (
        "PASS",
        "'SMB churned ARR EUR 123.6k on a September base of EUR 469.2k, about 26.3% monthly gross churn', with per-segment NRR of 100.0% (Enterprise) / 89.8% (Mid-market) / 102.0% (SMB) and every churned logo placed in its segment",
        "Quantifies retention on two correct and clearly labelled bases, ranks the populations, and the figures carry the interpretation it then draws. v0.1 held this at PARTIAL for not producing logo churn specifically; the rewritten criterion no longer demands one representation.",
    ),
    ("glm5.3-flash", "segment_retention_quantified"): (
        "PASS",
        "the churn table places all five churned logos with segment, plan and ARR, and the segment table gives net ARR movement - Enterprise flat, Mid-market -EUR 174k, SMB +EUR 9.6k net on EUR 123.6k churned against EUR 247.2k new",
        "Churned ARR is given per segment and the movement is ranked, both labelled as segment. Same upgrade as above and for the same reason.",
    ),
    ("glm5.2", "segment_retention_quantified"): (
        "PARTIAL",
        "'SMB churned 4 of 14 customers in October ... 28.6% MoM churn' against the correctly labelled 'Starter ... highest churn (4 of 13 in October)'",
        "The plan framing is right and labelled but incomplete - no Pro or Enterprise plan rate, so the plans cannot be ranked - and the segment denominator is wrong: SMB has 18 customers and 13 at the start of October, neither of which is 14. The error does not change which population is worst, which is the PARTIAL bar rather than the FAIL bar.",
    ),
    ("deepseek-v4-flash", "segment_retention_quantified"): (
        "PARTIAL",
        "'SMB churn rate is high: 4 of 4 churned customers were SMB Starter, representing ~20.5% of SMB ARR' - against its own churn list, which places Nakatomi as a fifth, Mid-market, churn",
        "The ARR-weighted rate is correct (123,600 / 602,400 = 20.5%) and is an accepted basis, but the sentence asserts all churn was SMB and is contradicted by the response's own table two paragraphs earlier. Ranking survives only because the table corrects it.",
    ),
    ("gemma4", "segment_retention_quantified"): (
        "FAIL",
        "'SMB Segment: Rapidly expanding in customer count (from 9 in Sept to 13 in Oct)' - the Starter plan's counts labelled as the SMB segment - and no churn or retention figure anywhere",
        "No quantification on any basis, and the one count given is a plan count presented as a segment count with nothing else to correct it.",
    ),
    ("qwen3.6", "segment_retention_quantified"): (
        "PARTIAL",
        "'SMB Churn: 4 SMB customers churned in October ... Total lost ARR: EUR 123,600' followed by 'Total Churned Revenue (Oct): EUR 15,000 (Nakatomi) + EUR 123,600 (SMB) = EUR 138,600/month lost'",
        "The SMB churn is quantified in ARR and the logos are placed correctly, but no rate is computed on any basis, the populations are never ranked, and the aggregate adds a monthly figure to an annual one.",
    ),
    # ---- absolute_vs_scalable_economics (new) -----------------------------
    ("qwen3.8-flash", "absolute_vs_scalable_economics"): (
        "PASS",
        "'Enterprise contributes the most absolute profit, but its margin declined and its issues look more commercial/account-management than product-engineering' with contribution per customer EUR 13.9k against Pro's EUR 4.6k and margins 29.5% against 62.7%",
        "Holds both halves, states which question each answers, and routes the product decision to the margin side while routing the revenue-protection work to Enterprise.",
    ),
    ("glm5.3-flash", "absolute_vs_scalable_economics"): (
        "PARTIAL",
        "'Enterprise is where the money and the risk are: 87% of MRR, eroding margin' and 'Pro is the margin engine', followed by 'next quarter's engineering focus goes to the enterprise plan ... defending 87% of MRR and a falling margin'",
        "Draws the contrast cleanly and then leans on the absolute figure for exactly the decision the criterion says it does not answer. The falling margin is a genuine second reason, which keeps this off FAIL.",
    ),
    ("glm5.2", "absolute_vs_scalable_economics"): (
        "PASS",
        "'Enterprise generates the most absolute cash (194.7k), but it is expensive to maintain (low 29.5% margin)' and 'Pro is the star of unit economics', with the per-customer table giving 15,143 / 13,907 against 5,313 / 4,611",
        "Both halves held, the distinction used, and the product recommendation follows the margin side.",
    ),
    ("deepseek-v4-flash", "absolute_vs_scalable_economics"): (
        "PARTIAL",
        "'Enterprise plan is 87% of revenue but has the lowest margin and is deteriorating' followed by 'Enterprise plan deserves the most attention. It generates the majority of revenue and contribution.'",
        "The contrast is drawn and then the product-priority decision is argued from the absolute figure, which is the failure mode this criterion exists to separate. The margin erosion is offered as a second reason, so PARTIAL rather than FAIL.",
    ),
    ("gemma4", "absolute_vs_scalable_economics"): (
        "PASS",
        "'Enterprise generates the most absolute cash (194.7k), but it is expensive to maintain (low 29.5% margin)' and 'While Enterprise brings the most revenue, the Pro plan has superior unit economics'",
        "States both figures and says explicitly which one the product question takes. That it reaches this on a revenue picture that is otherwise wrong is priced in the revenue dimension, not here.",
    ),
    ("qwen3.6", "absolute_vs_scalable_economics"): (
        "PASS",
        "'The Enterprise plan is the largest revenue driver but the least profitable' with 'Enterprise: Needs cost optimization (infra and support), not feature expansion' against 'Pro: This is the sweet spot'",
        "Holds both halves and routes the engineering decision away from size on the strength of the margin.",
    ),
    # ---- plan_trajectory_evidence (new) -----------------------------------
    ("qwen3.8-flash", "plan_trajectory_evidence"): (
        "PASS",
        "'Pro requests: 3.465M September to 3.977M October = +14.8%' and the table of Pro customers above included volume - Wonka 1.02M, Vandelay 0.69M, Aperture 0.705M against 0.60M - plus the Enterprise equivalents",
        "Both trajectory signals quantified, and the distribution is read rather than the plan average: it states the average utilisation at 73.6% and then lists the three accounts above the line.",
    ),
    ("glm5.3-flash", "plan_trajectory_evidence"): (
        "PASS",
        "'The 600k included-requests ceiling is below actual usage for wonka (1.02M), aperture (705k), and vandelay (690k), all of whom should be on enterprise'",
        "The three accounts over the allowance identified correctly with figures. Reads the accounts, not the average.",
    ),
    ("glm5.2", "plan_trajectory_evidence"): (
        "PASS",
        "'wonka at 1.02M requests is genuinely over the limit and should be on enterprise' against 'Several of these (prestige 545k, oscorp 198k, pied 186k, planet 112k) are below the 600k included-requests ceiling'",
        "Explicitly separates the accounts above the allowance from those below it and uses the distinction to argue that the rate-limit signal is not purely a volume story.",
    ),
    ("deepseek-v4-flash", "plan_trajectory_evidence"): (
        "FAIL",
        "'All plans are below included request volumes, so no overage revenue is being generated.'",
        "The claim is true of the three plan averages and false of the customers: two Enterprise accounts and three Pro accounts are above their included volume. It is the aggregate error the scenario is built around, it is stated as fact, and it removes the upside half of the Pro case from the response's own reasoning.",
    ),
    ("gemma4", "plan_trajectory_evidence"): (
        "PARTIAL",
        "'Engineering should focus on features that drive Pro users toward Enterprise tiers or increasing the included requests ceiling to capture more value'",
        "Identifies the ceiling as the lever without a single figure behind it, and no usage trajectory for any plan.",
    ),
    ("qwen3.6", "plan_trajectory_evidence"): (
        "PARTIAL",
        "'The Pro plan is the most efficient. It has good margins and is growing (9 customers in Oct vs 8 in Sep)' with 'healthy usage growth' asserted and never quantified",
        "One quantified adoption signal for one plan, and the usage trajectory the criterion asks for is asserted rather than computed. The included-volume distribution is never examined.",
    ),
    # ---- support_normalized (denominators clarified) ----------------------
    ("glm5.3-flash", "support_normalized"): (
        "PASS",
        "'support cost runs at ~32% of plan revenue (vs. 25% for enterprise)' and 'Enterprise has 8 of 14 customers with high-severity api_errors or performance tickets in October'",
        "Normalises on two denominators the rewritten criterion names - cost against plan revenue, and affected customers against plan size - and its conclusion puts Starter, not Enterprise, at the top of the burden. Held at PARTIAL under v0.1 only because that wording listed tickets-per-customer, per-user and per-request and not cost-per-revenue.",
    ),
    ("qwen3.6", "support_normalized"): (
        "PASS",
        "'Enterprise: Support Cost EUR 168,000. This is 25.5% of revenue' against 'Starter: Support Cost EUR 10,300. 32.2% of revenue ... low-value customers are consuming disproportionate support resources'",
        "Support cost as a share of plan revenue, computed for all three plans, with Enterprise explicitly not the worst. Same wording gap as above.",
    ),
}


def main() -> None:
    lines = [
        "# MondayBench #004 - SHADOW verdicts under PROPOSED rubric 0.2.",
        "#",
        "# Generated by analysis/_monday_004_shadow_v02.py from the recorded v0.1",
        "# verdicts. Eighteen criteria are unchanged in wording and keep their v0.1",
        "# label; five are re-judged and one is dropped, all listed in that script.",
        "#",
        "# Replay with:",
        "#   mondaybench evaluate --scenario monday-004 --all-models \\",
        "#       --evaluator evaluator-opus5-v0.4-calibration-2 \\",
        "#       --verdicts verdicts/monday-004/shadow-v0.2.jsonl",
        "#",
        "# This is a shadow scoring of existing responses. No model was regenerated.",
    ]

    carried = 0
    for raw in V01.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        entry = json.loads(line)
        run_id = entry["run_id"]
        slug = run_id.split("__")[1]
        if RUNS.get(slug) != run_id:
            continue  # a rejected run that was never scored
        if entry.get("kind") == "penalties":
            lines.append(json.dumps(entry, ensure_ascii=False))
            continue
        cid = entry["criterion_id"]
        if cid in DROPPED:
            continue
        override = NEW.get((slug, cid))
        if override:
            result, evidence, reason = override
            entry = {
                "run_id": run_id,
                "kind": "criterion",
                "criterion_id": cid,
                "result": result,
                "evidence": evidence,
                "reason": reason,
            }
        else:
            carried += 1
        lines.append(json.dumps(entry, ensure_ascii=False))

    # The two criteria that exist only in 0.2.
    for slug, run_id in RUNS.items():
        for cid in ("segment_retention_quantified", "absolute_vs_scalable_economics", "plan_trajectory_evidence"):
            result, evidence, reason = NEW[(slug, cid)]
            lines.append(
                json.dumps(
                    {
                        "run_id": run_id,
                        "kind": "criterion",
                        "criterion_id": cid,
                        "result": result,
                        "evidence": evidence,
                        "reason": reason,
                    },
                    ensure_ascii=False,
                )
            )

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {OUT.relative_to(REPO_ROOT)}")
    print(f"  {carried} criterion labels carried over unchanged")
    print(f"  {len(NEW)} labels re-judged or newly judged")


if __name__ == "__main__":
    main()
