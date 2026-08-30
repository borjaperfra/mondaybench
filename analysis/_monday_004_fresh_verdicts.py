"""Recorded verdicts for the monday-004 fresh calibration, rubric 0.3.

    python analysis/_monday_004_fresh_verdicts.py

Writes `verdicts/monday-004/calibration-v0.3.jsonl`.

Seven runs, one per model, all generated under the 96,000-token safety ceiling
and all NON_BINDING. Judged in an interactive Claude Code session against
rubric-0.3.yaml and ground-truth.yaml; every figure cited below was checked
against the CSVs. Zero API calls during scoring.
"""

from __future__ import annotations

import json
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "verdicts" / "monday-004" / "calibration-v0.3.jsonl"

RUNS = {
    "qwen3.8": "monday-004__qwen3.8-flash__002",
    "glm5.3": "monday-004__glm5.3-flash__002",
    "deepseek": "monday-004__deepseek-v4-flash__003",
    "mimo": "monday-004__mimo-v2.5__003",
    "glm5.2": "monday-004__glm5.2__002",
    "qwen3.6": "monday-004__qwen3.6__002",
    "gemma4": "monday-004__gemma4__002",
}

P, T, F = "PASS", "PARTIAL", "FAIL"
V: dict[tuple[str, str], tuple[str, str, str]] = {}

# Penalties, keyed by model. Empty for every model not listed.
#
# Both entries are the scenario's central trap and the first example the penalty
# prompt names: "cutting, exiting or defunding SMB on the strength of the 22.2%
# logo churn rate". Both are also priced at FAIL under `segment_recommendation`,
# and that overlap is deliberate - a recommendation leadership could act on is
# worse than a weak answer, which is the whole reason PROHIBITED_ACTION exists
# alongside the criterion. The v0.1 battery charged the same thing the same way
# on GLM 5.2 and Qwen 3.6.
#
# Deliberately not charged, for the record:
#   - MIMO's four wrong figures. The prompt excludes "a figure that is wrong but
#     which nothing in the response depends on", and none of the four carries a
#     recommendation. Priced at FAIL under `figures_carried_correctly`.
#   - Qwen 3.6's "Enterprise is 89% of gross profit" (it is 79%), which carries
#     "do NOT reduce investment in Enterprise". The correct figure supports the
#     same conclusion, so the recommendation does not stand on the mistake.
#   - Qwen 3.6's "revamp or sunset" for Starter: two options offered as needing a
#     strategy, not an action recommended, and reached from plan economics it
#     computed correctly rather than from a data artifact.
#   - Gemma 4's "Enterprise is the most economically efficient plan". Wrong, and
#     priced at FAIL under `absolute_vs_scalable_economics`, but its figures are
#     right - the error is interpretive, not numeric.
PENALTIES: dict[str, list[dict[str, str]]] = {
    "deepseek": [{
        "type": "PROHIBITED_ACTION",
        "evidence": "'Reduce incremental investment in SMB. The data supports reducing new SMB "
                    "acquisition spend until retention improves. SMB had ~20.5% ARR churn in one "
                    "month' - the first of its three recommendations to leadership.",
        "reason": "Recommends reducing SMB acquisition spend on the churn rate, which is the "
                  "action the pack rules out. Its own figures show SMB new logos adding "
                  "EUR 133.2k against EUR 123.6k churned - net positive, not 'barely offset' - "
                  "and the pack contains no segment-level cost data with which to justify a "
                  "reduction. Naming the option in order to reject it would have been correct; "
                  "this tells leadership to do it.",
    }],
    "glm5.2": [{
        "type": "PROHIBITED_ACTION",
        "evidence": "'Decision 1 - Finance: reduce investment in SMB, specifically SMB/starter ... "
                    "Action: Reduce paid acquisition targeting SMB/starter.'",
        "reason": "Recommends defunding part of the SMB segment on Starter-plan economics and a "
                  "churn count. The best-argued version of this answer in the battery - it "
                  "separates SMB/pro from SMB/starter, computes the Starter economics correctly "
                  "and preserves the rest of the segment - but the pack has no segment-level "
                  "economics, and it never says so before acting.",
    }],
}


def add(model, criterion, result, evidence, reason):
    V[(model, criterion)] = (result, evidence, reason)


# ---------------------------------------------------------------- qwen3.8 ---
add("qwen3.8", "duplicate_detected", P, "both rows quoted verbatim, the stripe row of 2026-10-01 and the billing_sync twin of 2026-10-02", "Identified and excluded; the deduped October total of EUR 873.4k is the one it works from.")
add("qwen3.8", "annual_prepayment_normalized", P, "'October invoice: EUR 120,000 for 12 months. Monthly equivalent: EUR 10,000 ... overstates October economic revenue by EUR 110,000'", "Invoice, monthly equivalent and timing effect all stated.")
add("qwen3.8", "headline_vs_recurring_growth", P, "the four-row table: raw deduped +9.6%, raw with duplicate +12.0%, normalized MRR +1.6%, forward active MRR -1.8%", "Every basis labelled with what is in it, and the gap attributed to the annual invoice, the duplicate, the advance invoices and the services drop.")
add("qwen3.8", "revenue_conclusion", P, "'October's raw revenue spike is not real growth' as the first line of the bottom line", "Carried to leadership with figures behind it.")
add("qwen3.8", "segment_retention_quantified", P, "logo churn by segment (0%, 10%, 30.8%) and ARR churn (0%, 10.6%, 26.3%) side by side, plus NRR excluding new logos of 100% / 89.8% / 73.7%", "Three correct bases, all labelled as segment, populations ranked, and the interpretation follows from them.")
add("qwen3.8", "sample_size_arr_context", P, "'Four SMB Starter churns removed EUR 123.6k ARR. But five October new logos added EUR 133.2k ARR, all SMB. SMB forward MRR is slightly up EUR 0.8k' against Mid-market's -EUR 14.5k on two accounts", "Sizes the churn, nets it, and puts the Mid-market loss beside it.")
add("qwen3.8", "acme_false_positive_avoided", P, "'Requests: 4.200m -> 2.310m = -45.0% / Tokens: 4,620m -> 4,066m = -12.0% / Tokens per request: 1,100 -> 1,760'", "Three figures against the stated migration, and it generalises the lesson to the metric rather than only to the account.")
add("qwen3.8", "no_churn_overreach", P, "'This suggests low engagement before churn, but the sample is small' and 'No channel-to-churn linkage'", "Names the pattern, refuses the cause, and flags that the channel of churned accounts is not even recorded.")
add("qwen3.8", "raw_attribution_not_equivalent_new_business", P, "'EUR 210k expansion ARR attributed, including Hooli, Stark, Umbrella, and Globex' against its new-logo ARR of EUR 64.8k", "The split is stated and the accounts named.")
add("qwen3.8", "existing_customer_expansion_removed", P, "new-logo ARR table: Partner EUR 166.8k, Content EUR 91.2k, Paid search EUR 64.8k, Outbound EUR 56.4k, total EUR 379.2k", "Every figure exact and the ranking reversed against the raw table.")
add("qwen3.8", "conversion_rate_vs_absolute_volume", P, "the two-month funnel table plus 'paid-search trial rate fell from 8.5% to 6.4%' on lead volume 520 -> 900", "Both movements present and read against each other.")
add("qwen3.8", "no_unsupported_channel_scale_decision", P, "'Do not increase spend on any acquisition channel based on this pack' with five numbered prerequisites", "Refuses the increase and names exactly what would change the answer.")
add("qwen3.8", "cac_payback_unavailable", P, "the payback formula written out, then each input checked against the pack and found missing", "'Until then, any CAC payback by channel number would be fabricated.'")
add("qwen3.8", "contribution_calculated", P, "all six month-plan combinations: 212.0, 194.7, 42.5, 41.5, 8.4, 10.3", "Formula stated, every figure exact.")
add("qwen3.8", "margin_calculated_or_correctly_compared", P, "32.2% / 29.5% / 67.5% / 62.7% / 34.9% / 32.2%, plus blended 35.2% -> 32.5%", "All correct including the blended figure.")
add("qwen3.8", "absolute_vs_scalable_economics", P, "'Enterprise is 87% of October reported MRR ... But its margin is the lowest' with contribution per customer EUR 13.9k against Pro's EUR 4.61k, and the product decision routed to Pro while Enterprise gets cost work", "Holds both halves and says which question each answers.")
add("qwen3.8", "plan_trajectory_evidence", P, "'requests 3.465m to 3.977m, +14.8%' and the three named accounts over the 600k allowance - Wonka 1.020m, Aperture 705k, Vandelay 690k", "Growth and distribution both quantified; the accounts are read, not the average.")
add("qwen3.8", "product_focus_supported", P, "'Give the Pro plan the next quarter's primary product/engineering focus' on margin, contribution per customer, +14.8% usage, rate-limit tickets 5 -> 13 and the over-limit accounts", "Five signals, and Enterprise explicitly routed to cost work instead.")
add("qwen3.8", "customer_id_alias_resolved", P, "'Enterprise requests excluding Acme: Sep 26.54m - 4.20m = 22.34m'. The 26.54m enterprise-plan total is only reachable with wayne_ent's 3.10m joined; without it the figure is 23.44m", "The join was done. The alias is not described, but the arithmetic cannot be produced without it.")
add("qwen3.8", "support_normalized", P, "'Oct tickets per active customer' per segment: Enterprise 25/8 = 3.13, Mid-market 23/9 = 2.56, SMB 26/14 = 1.86", "Normalises on a stated denominator, on active customers, and never reasons from a raw count. All six ticket totals are exact.")
add("qwen3.8", "figures_carried_correctly", T, "'Total tokens grew from 32.435m to 33.937m, +4.6%'. October is exact; September is 32.1345m, so the growth is +5.6%", "One aggregate wrong by 0.9% and the derived rate by a full point, outside the stated tolerance. Everything else checkable is exact - the ARR bridge, GRR/NRR, all six contribution figures, the attribution split, all six ticket totals, the utilisation percentages and 'Enterprise requests excluding Acme +8.0%'. No decision rests on the token line.")
add("qwen3.8", "cross_table_customer_signal", P, "Soylent across usage, revenue and support; Acme across usage, tokens, revenue and contract end", "Several account-level findings from three or more tables, each with its figures.")
add("qwen3.8", "causal_boundary", P, "'This is enough for diagnosis, but not enough for strong causal claims' with the Soylent trio reported together as a risk signal", "Assembles the pattern and refuses the mechanism.")
add("qwen3.8", "segment_recommendation", P, "'Do not reduce investment in any customer segment this week ... Cutting SMB acquisition would likely remove the only segment adding customers'", "Refuses the cut, quantifies why, and gives a next step per segment.")
add("qwen3.8", "acquisition_recommendation", P, "'Do not increase spend on any acquisition channel based on this pack' with Partner named as the best observed ARR per lead and five prerequisites listed", "Follows the corrected view and conditions everything on the missing cost data.")
add("qwen3.8", "product_recommendation", P, "'Give the Pro plan the next quarter's primary product/engineering focus'", "Single, actionable, consistent with section 4.")
add("qwen3.8", "uncertainty_discipline", P, "twelve items including no overage pricing, no channel-to-churn linkage and plan counts not being active-only", "All material, several beyond the answer key, nothing invented.")

# ----------------------------------------------------------------- glm5.3 ---
add("glm5.3", "duplicate_detected", P, "'INV-2026-10-0209 (soylent, EUR 19,500) appears twice - stripe 1 Oct and billing_sync 2 Oct, same transaction ID. October revenue overstated EUR 19.5k (+2.2%) unless deduped'", "Identified, quantified as a share, and removed from the bridge.")
add("glm5.3", "annual_prepayment_normalized", P, "'Gringotts annual (12 mo, prepaid) ... EUR 120,000 ... EUR 10,000/mo equivalent'", "Named in the revenue bridge and used at its monthly value throughout.")
add("glm5.3", "headline_vs_recurring_growth", P, "'Invoiced revenue looks up ~12% MoM (EUR 797.1k -> EUR 892.9k) ... Underlying monthly-equivalent recurring revenue grew just +1.6% (EUR 746.1k -> EUR 757.7k)'", "Both figures, both bases named, and the +1.6% decomposed exactly into hooli +3,000, soylent -2,500 and five new logos +11,100.")
add("glm5.3", "revenue_conclusion", P, "'October's headline revenue growth is an accounting artifact, not growth' as the opening line", "First thing leadership reads, with the figures behind it.")
add("glm5.3", "segment_retention_quantified", P, "'SMB: 4 of 18 logos churned (22%); 20.5% of SMB ARR gone in one month. Mid-market: 1 of 10 (nakatomi, 10.5% of MM ARR). Enterprise: zero.'", "Logo churn and ARR churn for all three segments, correctly labelled and correctly ranked.")
add("glm5.3", "sample_size_arr_context", P, "'SMB is the candidate on paper (5.4% of ARR, 22% logo churn in Oct) - but it produced 8 of 9 new logos and was net ARR-positive (+EUR 247.2k new vs -EUR 123.6k churned)'", "Denominator, ARR and the offset, all exact; 8 of 9 new logos being SMB is correct.")
add("glm5.3", "acme_false_positive_avoided", P, "'-45% requests sits inside the 40-50% estimate ... tokens -12% only; tickets de-escalated. Note tokens/request rose 1.1 -> 1.76 - batch calls are heavier, confirming the workload moved rather than shrank'", "Three signals plus a derived ratio that proves the point rather than asserting it.")
add("glm5.3", "no_churn_overreach", P, "'Unrecorded causes: churn reasons are not captured; soylent's downgrade is inferred from tickets/usage, not confirmed'", "States the limit of its own inference explicitly.")
add("glm5.3", "raw_attribution_not_equivalent_new_business", P, "'Paid_search's EUR 210k is entirely expansion (hooli, stark, umbrella, globex) - i.e., the marketing platform is crediting multi-year enterprise accounts' growth to ad clicks'", "Quantified, named, and the causal objection stated.")
add("glm5.3", "existing_customer_expansion_removed", P, "'New-logo ARR by channel (2 months): partner EUR 166.8k, content EUR 91.2k, paid_search EUR 64.8k, outbound EUR 56.4k'", "Exact and ranked, with the caveat that one logo is 79% of partner's total.")
add("glm5.3", "conversion_rate_vs_absolute_volume", P, "'paid_search's efficiency declined as volume scaled (+73% leads, -2.1pts conversion) - a diminishing-returns signal'", "Both movements stated together.")
add("glm5.3", "no_unsupported_channel_scale_decision", P, "'Acquisition decision - no spend increase yet. Do not scale paid_search on attributed revenue' with three named prerequisites", "Refused and specified.")
add("glm5.3", "cac_payback_unavailable", P, "'CAC payback by channel (CFO ask): not computable. The pack contains no channel spend' followed by the framework it would use once spend exists", "Refuses the number and offers the method, which is the right shape of answer.")
add("glm5.3", "contribution_calculated", P, "'enterprise EUR 194,700 (29.5%), pro EUR 41,500 (62.7%), starter EUR 10,300 (32.2%)' with September beside it", "All six exact.")
add("glm5.3", "margin_calculated_or_correctly_compared", P, "the same table plus 'Total gross margin fell EUR 16.4k MoM (35.2% -> 32.5%)'", "All margins correct, including the blended movement.")
add("glm5.3", "absolute_vs_scalable_economics", P, "'Pro plan: the strongest unit economics (EUR 4,611 margin/customer/mo vs EUR 13,907 enterprise, EUR 792 starter - but at 63-68% margin %)' and 'Enterprise ... is a protect problem: reliability + cost-to-serve, not new features'", "Holds both halves and assigns each to the decision it answers.")
add("glm5.3", "plan_trajectory_evidence", P, "'wonka 1.02M requests vs 600k included (170%, renewal 17 Mar), aperture 705k vs 600k (118%, renewal 14 Apr)' and wayne 3.41M vs 3M", "Reads the accounts across two plans and ties each to its renewal date.")
add("glm5.3", "product_focus_supported", P, "'the pro plan deserves next quarter's product focus - best margins, healthy demand, and unmet demand at plan limits' with rate-limit tickets and the over-limit accounts", "Multiple signals, and it runs the enterprise workstream in parallel rather than confusing size with priority.")
add("glm5.3", "customer_id_alias_resolved", P, "'wayne-enterprises, EUR 1.008M ARR (11.5% of total), renews 30 Nov ... It also ran 3.41M requests vs 3M included'", "Wayne's usage reported correctly and tied to its billing record.")
add("glm5.3", "support_normalized", P, "'support cost is EUR 12,000/customer/month (25.5% of revenue) and rose EUR 9k in a month with essentially flat revenue' against starter's 32% of revenue", "Cost normalised against both customers and revenue, and Enterprise is treated as a cost-to-serve problem rather than the worst experience by raw count.")
add("glm5.3", "figures_carried_correctly", T, "'rate-limit tickets doubled (5 -> 12), 100% on pro' - the October count is 13; and 'starter +41% cost on +2 tickets' - starter tickets rose from 7 to 11, which is +4", "Two off-by-small counts in supporting statistics, neither decision-changing. Everything else checkable is exact: 59 -> 74 tickets, unresolved 20 -> 24, api-error tickets 10 -> 12, blended margin 35.2% -> 32.5%, SMB new ARR EUR 247.2k, Mid-market -EUR 42k, duff-brewing EUR 162k renewing 5 Dec, wayne at 11.5% of ARR.")
add("glm5.3", "cross_table_customer_signal", P, "'soylent ... usage -27%, a critical ticket, already downgraded EUR 264k -> EUR 234k ARR' and 'every churner had a visible usage decline in-month'", "Accounts assembled from customers, usage, revenue and support with the figures stated.")
add("glm5.3", "causal_boundary", P, "'soylent's downgrade is inferred from tickets/usage, not confirmed' with the three movements reported together", "Pattern assembled, escalated, and the limit stated.")
add("glm5.3", "segment_recommendation", P, "'do not cut Enterprise or Mid-market ... SMB is the candidate on paper but it produced 8 of 9 new logos and was net ARR-positive. Redirect SMB acquisition spend into retention rather than cutting the segment'", "Refuses the cut on quantified grounds and replaces it with an action, having also stated that segment-level cost is not derivable from the pack.")
add("glm5.3", "acquisition_recommendation", P, "'no spend increase yet ... run a bounded partner test ... Required first: channel spend data, expansion bookings excluded from channel attribution, and trial-to-paid tracking'", "Names partner on the corrected basis and conditions the spend on three specific gaps.")
add("glm5.3", "product_recommendation", P, "'Product focus: pro plan - overage/upgrade mechanics and rate-limit experience'", "Single, actionable, consistent with section 4.")
add("glm5.3", "uncertainty_discipline", P, "ten items including the CS allocation methodology, the snapshot semantics of arr_eur for churned customers, and the unquantified pricing implications of batch workloads", "Every gap real, several beyond the answer key, nothing invented.")

# --------------------------------------------------------------- deepseek ---
add("deepseek", "duplicate_detected", P, "'INV-2026-10-0209 appears twice - once from Stripe and once from billing_sync. If not deduplicated, October revenue is overstated by EUR 19.5k'", "Identified and excluded; its October total of EUR 873.4k is the deduped one.")
add("deepseek", "annual_prepayment_normalized", P, "'Gringotts' annual invoice of EUR 120k, which is really 12 months of EUR 10k MRR. That alone inflates October cash revenue by ~EUR 110k'", "Invoice, monthly equivalent and timing effect all stated.")
add("deepseek", "headline_vs_recurring_growth", P, "the invoiced table EUR 797.1k -> EUR 873.4k, plans MRR EUR 746.1k -> EUR 757.7k, and forward MRR EUR 732.4k, '-EUR 13.7k / 1.8% decline'", "Three bases, each labelled, and the gap attributed to the annual invoice and the advance invoices.")
add("deepseek", "revenue_conclusion", P, "'October headline revenue looks higher, but the underlying business did not grow'", "Opens the summary and carries its figures.")
add("deepseek", "segment_retention_quantified", P, "'Enterprise 0 / EUR 0 / 0%; Mid-market 1 / EUR 180k / ~10.5%; SMB 4 / EUR 123.6k / ~20.5%'", "ARR-weighted churn for all three segments, correctly computed and ranked, with the churned logo counts beside it.")
add("deepseek", "sample_size_arr_context", P, "'New SMB logos in October added EUR 133.2k ARR, but SMB churn was EUR 123.6k, so SMB is treading water at best'", "Sizes the churn and nets it against new business.")
add("deepseek", "acme_false_positive_avoided", P, "'Acme's request volume fell 45%, but the operational note says this was an expected move ... Tokens only fell ~12%, so this is not a demand collapse'", "Migration plus the token figure that shows the workload stayed.")
add("deepseek", "no_churn_overreach", T, "'Nakatomi churned after high-severity API error and performance tickets ... Reliability issues likely contributed, though we cannot prove causation from this pack.'", "Offers a cause and immediately labels it unprovable. That is the PARTIAL band rather than the PASS bar, which asks that no cause be claimed.")
add("deepseek", "raw_attribution_not_equivalent_new_business", P, "'Paid search is not proven as a new-customer channel. Its October attributed revenue is dominated by expansions of existing customers - Stark Industries, Umbrella Health, Globex, and Hooli'", "The split is in its channel table: EUR 274.8k attributed, EUR 64.8k new-logo, EUR 210.0k expansion.")
add("deepseek", "existing_customer_expansion_removed", P, "the channel table gives attributed, new-logo and expansion ARR for all four channels, every figure exact", "The ranking reverses and it says so.")
add("deepseek", "conversion_rate_vs_absolute_volume", P, "'funnel conversion fell from 8.5% to 6.4% as volume increased'", "Both movements in one sentence, with the two-month table behind it.")
add("deepseek", "no_unsupported_channel_scale_decision", P, "'Before scaling any channel, the Growth team should get channel spend data so CAC payback can actually be calculated'", "Declines to scale paid search and names the missing input.")
add("deepseek", "cac_payback_unavailable", P, "'CAC payback cannot be calculated from this data. We have no marketing spend by channel'", "Stated plainly with the missing input named.")
add("deepseek", "contribution_calculated", P, "October 194.7 / 41.5 / 10.3 with September 212.0 / 42.5 / 8.4 beside it", "All six exact.")
add("deepseek", "margin_calculated_or_correctly_compared", P, "29.5% / 62.7% / 32.2% and 32.2% / 67.5% / 34.9%", "All six correct.")
add("deepseek", "absolute_vs_scalable_economics", P, "'The Pro plan is the most profitable by margin but is showing rate-limit stress. Enterprise is the largest profit pool, but its contribution margin is eroding' with the product decision going to Pro", "Holds both halves and sends the product question to the margin side, the cost question to Enterprise.")
add("deepseek", "plan_trajectory_evidence", P, "'Enterprise: average usage is below the 3M included requests, but Stark (4.29M) and Wayne (3.41M) exceed it. Pro: average is below 600k, but Aperture (705k), Vandelay (690k), and Wonka (1.02M) exceed it. Starter: no customer exceeds'", "Reads the distribution against the average for all three plans, correctly, and repeats the lesson in the uncertainties: 'usage averages hide overage distribution'.")
add("deepseek", "product_focus_supported", P, "'Give the Pro plan the next engineering focus ... highest-margin plan and is growing, but showing rate-limit and overage stress. Three of nine Pro customers exceed included request volume, and rate-limit tickets more than doubled'", "Three signals beyond margin, with Enterprise explicitly deferred.")
add("deepseek", "customer_id_alias_resolved", P, "'Wayne (3.41M)' in the enterprise over-limit list", "Wayne's usage reported correctly against its billing record, so the alias was resolved.")
add("deepseek", "support_normalized", T, "'Pro support tickets rose from 19 in September to 28 in October. Pro rate-limit tickets rose from 5 to 13.'", "Correct counts and a within-plan trend, but no rate against any denominator and no comparison across plans. It avoids the raw-count trap without doing the normalisation the criterion asks for.")
add("deepseek", "figures_carried_correctly", P, "October subscriptions EUR 867.7k, total contribution EUR 262.9k -> EUR 246.5k, cost growth EUR 17.8k, Mid-market ARR churn 10.5%, SMB 20.5%, Pro tickets 19 -> 28, rate-limits 5 -> 13, and all five over-limit accounts", "Every checkable figure is correct. The previous run's aggregate error - 'all plans are below included request volumes' - is gone, replaced by the account-level reading.")
add("deepseek", "cross_table_customer_signal", P, "'Soylent is at risk: usage fell 27%, it downgraded from EUR 22k to EUR 19.5k MRR, and it had a critical API error ticket plus multiple high-severity tickets in October'", "One account from three tables with the figures stated.")
add("deepseek", "causal_boundary", P, "the Soylent trio reported together, and 'though we cannot prove causation from this pack' stated for the equivalent Nakatomi pattern", "Assembles the pattern and states the limit.")
add("deepseek", "segment_recommendation", F, "'Reduce incremental investment in SMB. The data supports reducing new SMB acquisition spend until retention improves.'", "Recommends the reduction. Its own figures show SMB adding EUR 133.2k of new ARR against EUR 123.6k churned - net positive, not 'treading water' - and it never states that the segment economics needed to justify a reduction are absent from the pack.")
add("deepseek", "acquisition_recommendation", P, "'Increase spend on content, not paid search ... Partner has the best conversion rate and highest-value new logos, but volume is very small' with the spend-data condition", "Follows the corrected new-logo view, names partner's strength, conditions the spend.")
add("deepseek", "product_recommendation", P, "'Give the Pro plan the next engineering focus'", "Single and consistent with section 4.")
add("deepseek", "uncertainty_discipline", P, "nine items including 'usage averages hide overage distribution' and 'support ticket counts are not cost-weighted'", "All real, and the aggregate caveat is one the answer key treats as a bonus observation.")

# ------------------------------------------------------------------- mimo ---
add("mimo", "duplicate_detected", P, "the two rows tabulated with sources and dates, plus 'The billing_sync source strongly suggests a system re-import ... must be investigated and reversed if confirmed'", "Identified exactly, and it is the only response to ask whether the customer was actually charged twice.")
add("mimo", "annual_prepayment_normalized", P, "'In September Gringotts was invoiced EUR 10,000; in October it was invoiced EUR 120,000 (12 months prepaid) ... it inflates October's cash invoice total by EUR 110,000'", "Invoice, monthly equivalent and effect all stated.")
add("mimo", "headline_vs_recurring_growth", T, "'Raw invoiced revenue is not a reliable MoM comparison this month' followed by a normalised table showing only MRR EUR 746,100 -> EUR 757,700 (+1.6%)", "The normalised figure and both distortions are right, and the EUR 110,000 effect is quantified, but the raw comparison the headline would be built on is never computed, so the size of the gap is never shown.")
add("mimo", "revenue_conclusion", P, "'Headline MRR grew +1.6% month-over-month, but the topline masks three problems that need action this week'", "The conclusion opens the brief and drives the actions.")
add("mimo", "segment_retention_quantified", T, "the churn table places all five logos with segment, plan and ARR, and the headcount table gives Enterprise 8 -> 8, Mid-market 10 -> 9, SMB 13 -> 14", "Populations and losses are correct and correctly placed, but no churn or retention rate is computed on any basis, so the segments are never ranked on retention.")
add("mimo", "sample_size_arr_context", P, "'Nine new logos added EUR 379K ARR in the period. Net ARR movement is positive at +EUR 75.6K' and 'the highest-value churned customer (Nakatomi, EUR 180K) was replaced by six lower-value new logos'", "Sizes the churn against new business and draws the Mid-market comparison the criterion asks for.")
add("mimo", "acme_false_positive_avoided", P, "'Acme's requests fell 45%, exactly in line with the operational note about the batch migration. Revenue (EUR 78K/month) is unchanged and the contract runs to February 2027. This is a non-issue.'", "Migration plus revenue and contract term.")
add("mimo", "no_churn_overreach", P, "the causal-claims table: 'Support quality caused Nakatomi's churn - we have no exit survey, no CSM notes ... suggestive, not causal'", "Names the claim it is refusing to make.")
add("mimo", "raw_attribution_not_equivalent_new_business", P, "'The four expansions attributed to paid search are for existing enterprise/mid-market customers (Stark, Umbrella, Globex, Hooli) - the channel may be receiving last-touch credit for organic expansion rather than truly causing it'", "The EUR 210K is separated in its channel table and the causal objection is stated.")
add("mimo", "existing_customer_expansion_removed", P, "the channel table splits new logos and expansions by month: Partner 2 / EUR 166,800, Content 1+2 / EUR 91,200, Paid Search 0+2 / EUR 64,800, Outbound 1+1 / EUR 56,400", "Every figure exact and Partner identified as the highest-value new-logo channel.")
add("mimo", "conversion_rate_vs_absolute_volume", P, "'Lead volumes rose across all channels, but trial conversion rates declined across all channels'", "Both movements stated in one sentence with the table behind them.")
add("mimo", "no_unsupported_channel_scale_decision", P, "'Do not blindly increase paid search spend ... request spend data and trial-to-paid conversion tracking before making channel investment decisions'", "Refuses the increase and names the missing inputs.")
add("mimo", "cac_payback_unavailable", P, "'CAC payback by channel cannot be calculated. This requires: 1. Marketing spend by channel (not provided) 2. Trial-to-paid conversion rates (not tracked) 3. Time-to-close data (not provided)'", "Enumerated and refused.")
add("mimo", "contribution_calculated", P, "the plan table with 194,700 / 41,500 / 10,300 and a total row of 246,500", "All exact, including the blended total.")
add("mimo", "margin_calculated_or_correctly_compared", P, "29.5% / 62.7% / 32.2% with the 32.5% blended figure and margin per euro of revenue", "Correct, and expressed two ways.")
add("mimo", "absolute_vs_scalable_economics", P, "'Each customer generates strong absolute margin (EUR 13.9K/month) but at only 29.5%' and 'the enterprise plan's declining margin ... is primarily a cost-management and account-health issue, not a product-engineering issue'", "Holds both halves and routes each to its own decision.")
add("mimo", "plan_trajectory_evidence", P, "the usage-versus-included table with 'Pro ... 74% utilisation, over-limit customers 3 (Wonka 170%, Aperture 118%, Vandelay 115%)'", "Reads the Pro distribution against the average and quantifies each account. The Enterprise row of that table is wrong and is charged under figure accuracy, not here.")
add("mimo", "product_focus_supported", P, "'The Pro plan. Three reasons: highest margin, most growth potential; product friction is concentrated here; usage growth is strongest' with Vandelay +32.7%, Aperture +21.6%", "Three signals with figures, and Enterprise explicitly excluded as an engineering priority.")
add("mimo", "customer_id_alias_resolved", P, "'Enterprise | EUR 296,800 | 26,436,400 | EUR 0.0112' in the infrastructure cost-intensity table. That request total is only reachable with wayne_ent joined; without it the figure is 23,026,400", "The join was done, even though the alias is never named.")
add("mimo", "support_normalized", P, "support cost per customer of EUR 12,000 / EUR 956 / EUR 792, and 'Support costs alone consume 32% of revenue' for Starter", "Two denominators, computed across all three plans, and Enterprise is never called the worst experience on a raw count.")
add("mimo", "figures_carried_correctly", F, "'Over-limit Customers: Enterprise 0' when Stark (4.29M) and Wayne (3.41M) both exceed 3M; 'Wonka alone filed 8 rate-limit tickets in October' when it filed 4; 'SMB seg 13 -> 14 (+1, net of 5 churn, 6 new)' when SMB had 4 churns and 5 new logos; 'SMB is generating all new-logo growth (6 of 6 new logos)' when 8 of the 9 new logos were SMB", "Four incorrect figures in four different sections, which is the FAIL band's 'repeated incorrect figures across different parts'. None is decision-changing on its own and the Pro figures that carry the recommendation are exact, but the errors are not confined to one lapse.")
add("mimo", "cross_table_customer_signal", P, "the Soylent table: requests 980K -> 715K, invoice EUR 22,000 -> EUR 19,500, tickets 3 -> 8 with severity, plus the duplicate invoice", "One account assembled from four tables with every figure correct.")
add("mimo", "causal_boundary", P, "section 6.3, a dedicated table of causal claims not supported by the data, covering Nakatomi, paid search and the new starter cohort", "The most explicit treatment in the battery: it names the claims it will not make and why.")
add("mimo", "segment_recommendation", P, "'Do not reduce investment in the SMB segment. SMB is generating all new-logo growth ... The issue is not acquisition volume but retention and onboarding' plus 'Review SMB Starter unit economics at renewal'", "Refuses the cut with reasoning, and gives the investigation the answer key asks for.")
add("mimo", "acquisition_recommendation", T, "'Increase content marketing spend ... Partner channel is most efficient but low-volume; paid search shows signs of saturation'", "Identifies Partner's efficiency and refuses paid search, but the content increase it does recommend is not itself conditioned on the missing cost data, which it raises only in a separate section.")
add("mimo", "product_recommendation", P, "'Prioritise Pro plan engineering work - raise included request limit, improve rate-limit UX, enable overage billing'", "Single, actionable, consistent with section 4.")
add("mimo", "uncertainty_discipline", P, "three tables covering data-quality problems, metrics that cannot be calculated and causal claims not supported, including cost-to-serve by segment", "Every gap real, the segment-cost gap is the one the answer key names, and nothing is invented.")

# ----------------------------------------------------------------- glm5.2 ---
add("glm5.2", "duplicate_detected", P, "'INV-2026-10-0209 appears twice - once from stripe dated 2026-10-01 and once from billing_sync dated 2026-10-02 - same amount (EUR 19,500), same invoice ID ... summing revenue.csv naively would double-count'", "Identified exactly, with the correct observation that plans.csv already counts it once.")
add("glm5.2", "annual_prepayment_normalized", P, "'Gringotts moved to annual billing in October (EUR 120,000 invoice for 12 months). This is a one-time EUR 120k cash inflow in October but does not change MRR (still EUR 10k/month)'", "Invoice identified and held at its monthly value.")
add("glm5.2", "headline_vs_recurring_growth", T, "'October MRR per the plans file was EUR 757,700 ... up EUR 11,600 vs. September. That headline is flattered by invoicing timing'", "The normalised figure is right and the distortions are all identified, but the raw invoiced comparison - EUR 797.1k against EUR 892.9k - is never computed, so the +12% the pack would otherwise report is never set against the +1.6%.")
add("glm5.2", "revenue_conclusion", P, "'The headline numbers look stable, but the underlying picture is deteriorating' with a projected November MRR of ~EUR 750,400", "Leads the brief and is carried into the recommendations.")
add("glm5.2", "segment_retention_quantified", T, "'Gross churn in October: 5 customers, EUR 303,600 ARR - 1 mid-market pro customer (Nakatomi, EUR 180k) + 4 SMB starter customers (EUR 123.6k combined). That's 44% of September's starter customer base.'", "The Starter plan rate is correct and correctly labelled (4 of 9), and churned ARR is placed by segment, but no rate is given for the other plans or for any segment, so the populations are never ranked on retention.")
add("glm5.2", "sample_size_arr_context", P, "'the plan replaced EUR 123,600 of churned ARR with EUR 94,800 of new ARR' and 'SMB pro: 5 stable customers, EUR 218.4k ARR'", "Sizes the churn in ARR and separates the healthy part of the segment from the unhealthy one, both figures exact.")
add("glm5.2", "acme_false_positive_avoided", P, "'Acme's request volume dropped 45% (4.2M -> 2.31M) but tokens only dropped 12% (4,620M -> 4,066M) - they're processing similar work in fewer, larger calls'", "Migration plus tokens plus active users, and the second-order overage observation.")
add("glm5.2", "no_churn_overreach", P, "'No causal claim can be made about why the 4 SMB starter customers churned (no exit surveys). The usage decline is correlated with churn, not necessarily causal'", "Explicit.")
add("glm5.2", "raw_attribution_not_equivalent_new_business", P, "'Paid search is also credited with EUR 210,000 of expansion ARR ... But Stark, Umbrella, and Globex have been Northstar customers since 2023-2024 - the causal claim that paid search acquired their expansion is hard to defend'", "Quantified, named, and the attribution model challenged.")
add("glm5.2", "existing_customer_expansion_removed", P, "the new-logos-only table: Partner EUR 166,800 (EUR 83,400/logo), Content EUR 91,200, Outbound EUR 56,400, Paid search EUR 64,800, with ACV per lead", "Exact, ranked on new-logo economics, and extended to a per-lead measure.")
add("glm5.2", "conversion_rate_vs_absolute_volume", F, "the funnel table is 'Sept + Oct combined' - Partner 135 leads / 32 trials / 23.7%, Paid search 1,420 / 102 / 7.2% - with no monthly split anywhere in the response", "Combining the two months erases the movement entirely: neither the falling conversion rate nor the rising absolute conversions is reported, and the pack's central funnel observation is never made.")
add("glm5.2", "no_unsupported_channel_scale_decision", P, "'Do not treat paid-search's expansion attribution (EUR 210k) as a reason to invest more in paid search' and, on partner, 'we don't know whether the ceiling is spend or partner capacity'", "Refuses to scale paid search and states the unknown that bounds the alternative.")
add("glm5.2", "cac_payback_unavailable", P, "'Cannot be delivered from this pack. No marketing spend data is included ... Without that, any payback number would be invented'", "Refused, with the missing input named and a list of what it can produce instead.")
add("glm5.2", "contribution_calculated", P, "the two-month table with 212,000 / 194,700 / 42,500 / 41,500 / 8,400 / 10,300", "All six exact.")
add("glm5.2", "margin_calculated_or_correctly_compared", P, "32.2% -> 29.5%, 67.5% -> 62.7%, 34.9% -> 32.2% with the delta in percentage points", "All six correct.")
add("glm5.2", "absolute_vs_scalable_economics", T, "'Enterprise - Largest absolute contribution (EUR 194.7k/mo) but margins are declining' with per-customer contribution EUR 13,907 / EUR 4,611 / EUR 792, followed by 'Focus engineering on the Enterprise plan ... the largest revenue and contribution base - the most absolute value at risk'", "Both halves are present and correct, and then the product decision is argued from the absolute figure - the first bullet of its own justification. The margin erosion is a real second reason, which keeps this off FAIL.")
add("glm5.2", "plan_trajectory_evidence", F, "'No plan is hitting its included ceiling - no overage revenue should be expected at renewal, which further weakens the case for the starter plan's economics'", "True of the three plan averages it tabulates and false of the customers: Stark 4.29M and Wayne 3.41M exceed the 3M enterprise allowance, and Wonka 1.02M, Aperture 705k and Vandelay 690k exceed the 600k Pro allowance. The claim is then used as an argument, which is the aggregate error the scenario is built around.")
add("glm5.2", "product_focus_supported", T, "'Focus engineering on the Enterprise plan' on largest revenue and contribution at risk, declining margins, support cost per customer, and 63% utilisation", "A plan other than Pro is allowed only when the case does not rest on absolute revenue; the first reason offered is that Enterprise is the largest base. The margin erosion and the support cost per customer are genuine independent signals, so PARTIAL rather than FAIL.")
add("glm5.2", "customer_id_alias_resolved", P, "'Wayne Enterprises (renewing Nov 30) grew requests 10% and active users 10% in October'", "Wayne's usage reported correctly against its billing record.")
add("glm5.2", "support_normalized", P, "'Carrying disproportionate support cost (EUR 12,000/customer vs. EUR 955 for pro)' and 'Support cost is 32% of revenue - disproportionate' for starter", "Normalises support cost against customers and against revenue for all three plans, and never argues from a raw ticket count.")
add("glm5.2", "figures_carried_correctly", T, "'New logos (5) | +EUR 113,200' in the ARR movement table - the five October new logos total EUR 133,200; and 'wayne-enterprises ... the third-largest account' when it is the second, behind Stark at EUR 1.14M", "Two slips, neither decision-changing. Everything else checkable is exact, including 44% of the September starter base, EUR 94,800 of replacement ARR, EUR 218.4k of SMB pro ARR, enterprise support cost rising EUR 9k on +2 tickets, and every figure in the funnel and attribution tables.")
add("glm5.2", "cross_table_customer_signal", P, "'Soylent - usage -27%, plan downgrade -EUR 30k ARR, 3 -> 8 tickets (incl. a critical api_error), active users 56 -> 41. Distressed.'", "Four tables on one account, every figure correct.")
add("glm5.2", "causal_boundary", P, "'No causal claim can be made ... The usage decline is correlated with churn, not necessarily causal - but it's the best leading indicator we have'", "Pattern assembled and the limit stated precisely.")
add("glm5.2", "segment_recommendation", F, "'Decision 1 - Finance: reduce investment in SMB, specifically SMB/starter ... Reduce paid acquisition targeting SMB/starter.'", "Recommends the reduction. It is the best-argued version of this answer in the battery - it separates SMB/pro from SMB/starter explicitly, computes the Starter economics correctly and preserves the rest of the segment - but it still recommends a cut, and it never states that segment-level economics are absent from the pack.")
add("glm5.2", "acquisition_recommendation", P, "'Increase spend on Partner, but tiered: start with a 25-50% budget test to validate that lead volume scales with spend' with the paid-search attribution explicitly rejected", "Names partner on the corrected new-logo basis and bounds the spend on a stated unknown.")
add("glm5.2", "product_recommendation", P, "'Decision 3 - Product: focus engineering on the Enterprise plan' with three named workstreams", "Single, actionable, consistent with its own section 4.")
add("glm5.2", "uncertainty_discipline", P, "ten items including the CS-allocation caveat on support cost, churned customers retaining arr_eur, and plan counts including mid-month churners", "All real and several beyond the answer key.")

# ---------------------------------------------------------------- qwen3.6 ---
add("qwen3.6", "duplicate_detected", F, "no repeated transaction id anywhere; the data-issues section raises six other concerns", "The duplicate is not mentioned.")
add("qwen3.6", "annual_prepayment_normalized", F, "revenue is taken from plans.csv throughout - 'Total Monthly Recurring Revenue (MRR) from Plans' - and the EUR 120,000 twelve-month Gringotts invoice appears nowhere", "Reaches a recurring figure without ever identifying or normalising the annual invoice.")
add("qwen3.6", "headline_vs_recurring_growth", T, "'September: EUR 746,100 ... October: EUR 757,700 ... Growth: +1.5% MRR' and 'The headline MRR growth (+1.5%) is misleading'", "The normalised figure is right and correctly labelled, but the raw invoiced comparison it should be set against is never computed.")
add("qwen3.6", "revenue_conclusion", T, "'The headline MRR growth (+1.5%) is misleading. It is driven by new SMB acquisitions offsetting significant SMB churn and one-off revenue loss.'", "Right direction and a real driver, but the reported number leadership would otherwise quote is never confronted.")
add("qwen3.6", "segment_retention_quantified", T, "'SMB Churn Rate: 5 out of 13 active SMB customers in Oct had churned ... This is a 38% monthly churn rate for the SMB segment' - against its own churn list, which places Nakatomi in Mid-market", "A rate is computed and SMB is correctly identified as worst, but the numerator counts a Mid-market churn inside SMB and contradicts the table three paragraphs above it.")
add("qwen3.6", "sample_size_arr_context", T, "each churned logo is listed with its ARR, and 'Enterprise is 87% of revenue and 89% of gross profit'", "The churned ARR is itemised, but SMB's own base is never given and the comparison drawn is Enterprise's share of profit rather than what the SMB churn actually cost.")
add("qwen3.6", "acme_false_positive_avoided", P, "'Usage dropped 45% (4.2M to 2.31M requests). This aligns with the operational note about moving to batch runs. Revenue remained stable (EUR 78k/mo)'", "Migration plus unchanged revenue.")
add("qwen3.6", "no_churn_overreach", P, "'SMB Churn Cause: We know SMBs are churning, but we don't know why. Is it price? Product? Support?'", "Names the gap instead of filling it.")
add("qwen3.6", "raw_attribution_not_equivalent_new_business", T, "'Oct: 58 conversions. Includes 3 expansions (Stark EUR 84k, Umbrella EUR 48k, Globex EUR 42k) and 4 new logos'", "Separates the expansions and names them, but never states the EUR 274.8k attributed total or what share of it is not new business.")
add("qwen3.6", "existing_customer_expansion_removed", T, "per-channel notes give new logos and expansions - 'Partner: Sept: 2 new logos (Vandelay EUR 132k, Clampett EUR 34.8k). Avg EUR 83.4k' - with no channel total or ranking", "The split is done per channel but never carried through to a new-logo ranking, so the reversal against the raw table is never shown.")
add("qwen3.6", "conversion_rate_vs_absolute_volume", P, "the two-month funnel table and 'Paid Search has the highest volume but declining conversion rate (8.5% -> 6.4%)'", "Both movements stated together.")
add("qwen3.6", "no_unsupported_channel_scale_decision", P, "'Do not increase spend on Paid Search until we understand the CAC payback period'", "Refuses the increase and names the missing metric.")
add("qwen3.6", "cac_payback_unavailable", P, "'CAC Payback Cannot Be Calculated: The acquisition data does not include marketing spend'", "Stated with the missing input named.")
add("qwen3.6", "contribution_calculated", P, "the October table with 194,700 / 41,500 / 10,300 under an explicit cost breakdown", "All three exact.")
add("qwen3.6", "margin_calculated_or_correctly_compared", P, "29.5% / 62.7% / 32.2%", "All three correct and correctly ordered.")
add("qwen3.6", "absolute_vs_scalable_economics", T, "'Enterprise: Highest Revenue ... Profit EUR 194.7k' against 'Pro: Highest Margin 62.7% ... The Pro plan is the most efficient', followed by 'Product focus should be on the Enterprise plan'", "Both halves are held and correctly stated, and then the product decision goes to Enterprise on the strength of its being the profit driver.")
add("qwen3.6", "plan_trajectory_evidence", T, "'Enterprise: Avg 1.89M requests/customer. Included: 3M. Most are under quota' and the same treatment for Pro and Starter", "Utilisation is quantified per plan from the averages and hedged with 'most', which keeps it off the FAIL clause, but the accounts above their allowance are never identified and no usage growth rate is computed.")
add("qwen3.6", "product_focus_supported", T, "'Product focus should be on the Enterprise plan' in the summary against 'Focus on Enterprise and Pro, Revamp or Sunset Starter' in section 5", "Two different answers in one response, and the Enterprise case is argued from its being the revenue and profit driver rather than from cost-adjusted economics.")
add("qwen3.6", "customer_id_alias_resolved", F, "Wayne Enterprises appears nowhere; usage is discussed only for Acme, Soylent and Nakatomi, and the plan figures are taken from plans.csv rather than joined", "No account-level join between billing and usage was attempted, so the alias is neither resolved nor noticed.")
add("qwen3.6", "support_normalized", T, "'Starter: High Support Cost: EUR 10.3k. This is 32% of revenue'", "One plan normalised against revenue, with no comparison across plans.")
add("qwen3.6", "figures_carried_correctly", F, "'5 out of 13 active SMB customers ... 38%'; 'Nakatomi ... 4 tickets in Sept, 2 in Oct' when September was 3; 'Enterprise is 87% of revenue and 89% of gross profit' when its share of contribution is 79%; 'we lose EUR 78k/mo revenue and EUR 24.7k/mo infra cost' - EUR 24.7k is the Pro plan's total cost, not Acme's infrastructure", "Four incorrect figures in four different sections, one of which - the 89% profit share - is used to argue against reducing Enterprise investment.")
add("qwen3.6", "cross_table_customer_signal", T, "'Soylent (Mid-market/Pro): Usage dropped 27%. Revenue dropped from EUR 22k to EUR 19.5k' - Soylent is on the enterprise plan, not Pro", "Two tables joined at account level with correct figures, but the plan is wrong and the support signal is missing, so the three-table picture is never assembled.")
add("qwen3.6", "causal_boundary", T, "'Soylent: Usage dropped 27%. Revenue dropped ... This suggests they are hitting usage caps or downgrading.'", "Offers a mechanism as a suggestion rather than asserting it, but the ticket spike is absent and the epistemic limit is never stated for this account.")
add("qwen3.6", "segment_recommendation", T, "'Do NOT reduce investment in the Enterprise segment yet' with no SMB recommendation, and 'The Starter plan is losing money and customers; it needs a revamp or sunset strategy'", "It does not recommend cutting SMB, which keeps it off FAIL, but it answers the segment question about Enterprise instead, offers no next step for SMB, and floats sunsetting Starter as one of three options.")
add("qwen3.6", "acquisition_recommendation", P, "'Do NOT increase spend on Paid Search immediately ... The Partner channel has a higher conversion rate and brings in higher-value logos (Vandelay) ... Consider increasing Partner spend if the pipeline allows' with 'Finance must calculate CAC by channel'", "Names Partner, refuses paid search, and conditions the alternative on the missing cost data.")
add("qwen3.6", "product_recommendation", T, "'Product focus should be on the Enterprise plan' against section 5's 'Focus on Enterprise and Pro'", "A recommendation is made but it is not single and it contradicts its own section 4 conclusion that Pro is the most efficient.")
add("qwen3.6", "uncertainty_discipline", P, "six items including support cost attribution, Acme's overage terms, expansion attribution and the SMB churn cause", "All real gaps in this pack, and no figure is presented as known that is not.")

# ----------------------------------------------------------------- gemma4 ---
add("gemma4", "duplicate_detected", F, "no repeated transaction id is mentioned anywhere", "The duplicate is not mentioned.")
add("gemma4", "annual_prepayment_normalized", P, "'October revenue is heavily influenced by a EUR 120k annual invoice from Gringotts. Excluding this one-time cash event, monthly recurring revenue (MRR) remains relatively stable.'", "Identifies the annual invoice and excludes it, stating the exclusion - one of the treatments the criterion accepts.")
add("gemma4", "headline_vs_recurring_growth", T, "'Excluding this one-time cash event, monthly recurring revenue (MRR) remains relatively stable'", "Establishes that the headline overstates and names the cause, but gives no figure on either side, so the size of the distortion is never shown.")
add("gemma4", "revenue_conclusion", T, "'While total revenue is bolstered by a large annual contract from Gringotts ... MRR remains relatively stable'", "The right conclusion, carried into the summary, with nothing quantified behind it.")
add("gemma4", "segment_retention_quantified", T, "'SMB: High churn rate in October (4 customers churned: Slate-rock, Mega-lo-mart, Dinoco, Buy-n-large)' and 'Mid-Market: Stable, but showing signs of churn (Nakatomi)'", "The churned logos are placed in the right segments, but no rate is computed on any basis and the segments are never ranked.")
add("gemma4", "sample_size_arr_context", F, "churn is described qualitatively - 'High churn rate in October' - with no ARR, no denominator and no comparison", "None of the three contexts the criterion asks for is present.")
add("gemma4", "acme_false_positive_avoided", T, "'the operational notes suggest this is due to a shift to batch processing (which is expected)' and 'tokens_m did drop from 4620 to 4066, which is a ~12% drop' - against the summary's 'Enterprise segment health is declining due to a significant usage drop from a major client'", "The migration and the token figure are both there and correct, but the executive summary still books the decline as declining segment health.")
add("gemma4", "no_churn_overreach", P, "churn is reported with named customers and no reason attached to any of it", "Claims no cause the pack does not record.")
add("gemma4", "raw_attribution_not_equivalent_new_business", F, "the acquisition section contains the funnel table only; attributed revenue and expansion are never mentioned", "No adjustment is attempted because the attribution data is never opened.")
add("gemma4", "existing_customer_expansion_removed", F, "no new-logo view of any channel", "The split is never made.")
add("gemma4", "conversion_rate_vs_absolute_volume", T, "the funnel table carries leads and conversions for both months, and the prose says only 'Partner is the most efficient channel for conversion. Paid Search is the primary engine for volume/scale.'", "Both figures are on the page but the movement is never read: neither the falling rate nor the rising absolute conversions is stated.")
add("gemma4", "no_unsupported_channel_scale_decision", P, "'Hold on increasing spend until Marketing provides the Spend figures. We need to calculate the ROI/Payback.'", "Refuses the increase and names the missing input.")
add("gemma4", "cac_payback_unavailable", P, "'We cannot calculate the CFO's requested CAC Payback without the marketing spend data'", "Stated with the missing input named.")
add("gemma4", "contribution_calculated", P, "the October table with EUR 194,700 / EUR 41,500 / EUR 10,300 under 'Revenue - Infra - Support'", "All three exact.")
add("gemma4", "margin_calculated_or_correctly_compared", P, "29.5% / 62.7% / 32.2%", "All three correct.")
add("gemma4", "absolute_vs_scalable_economics", F, "'the Enterprise plan is the most economically efficient, despite high absolute costs' in the executive summary, against section 4's 'The Pro plan is the most economically robust, boasting a 62.7% margin'", "The summary states the opposite of its own analysis and gets the direction wrong: Enterprise has the worst margin of the three. Absolute contribution and margin are never distinguished.")
add("gemma4", "plan_trajectory_evidence", F, "no usage trajectory for any plan and no reference to included request volumes anywhere in the response", "Neither growth nor the included-volume distribution is examined.")
add("gemma4", "product_focus_supported", T, "'Focus on the Pro plan. It has the best unit economics' followed by 'Alternatively ... focus on automating support/onboarding for the Starter plan'", "Recommends Pro on margin alone and then offers an alternative without choosing between them.")
add("gemma4", "customer_id_alias_resolved", F, "Wayne Enterprises appears nowhere and no account-level usage join is attempted", "The alias is neither resolved nor noticed.")
add("gemma4", "support_normalized", T, "'The Starter plan has the lowest absolute margin and a high support-to-revenue ratio (Support costs are ~32% of its revenue)'", "One plan normalised against revenue, with no comparison across plans.")
add("gemma4", "figures_carried_correctly", P, "the plan economics table, the two-month funnel table and the Acme token figures 4620 -> 4066 are all exact; content's 12.0% September conversion is 11.92% rounded", "No incorrect figure. Its wrong claim about Enterprise being the most efficient plan is a conclusion, not a figure, and is charged under absolute_vs_scalable_economics.")
add("gemma4", "cross_table_customer_signal", T, "'Acme-corp ... 45% drop in request volume' read against the operational note and, in the uncertainties, against tokens_m", "Usage and context joined for one account, but no third table and no account built from customers, usage and support together.")
add("gemma4", "causal_boundary", F, "Soylent is not mentioned anywhere in the response", "None of the three simultaneous movements is reported, so the pattern is never seen.")
add("gemma4", "segment_recommendation", T, "'Do not reduce investment in Enterprise yet' with no recommendation on SMB despite having flagged its high churn", "It does not recommend cutting SMB, which keeps it off FAIL, but it answers the segment question about Enterprise and leaves SMB without a next step or a statement of what is missing.")
add("gemma4", "acquisition_recommendation", T, "'If the goal is pure volume, Paid Search is the lever; if the goal is efficiency, Partner is the lever' with spend held pending the missing figures", "Names Partner as the efficiency lever and conditions the spend, but reaches it through conversion rate alone because the new-logo correction is never made.")
add("gemma4", "product_recommendation", T, "'Focus on the Pro plan ... Alternatively, if the goal is to protect the bottom line, engineering should focus on automating support/onboarding for the Starter plan'", "Two recommendations rather than one, and both sit against an executive summary that names Enterprise as the most efficient plan.")
add("gemma4", "uncertainty_discipline", P, "four items covering missing CAC data, attribution timing, the limits of the Acme explanation and the open-ticket backlog", "All real, and no figure anywhere in the response is invented.")


def main() -> None:
    lines = [
        "# MondayBench #004 - fresh calibration verdicts, rubric 0.3.",
        "#",
        "# Seven runs, one per model, all generated under the 96,000-token safety",
        "# ceiling and all generation_ceiling_status=NON_BINDING. Produced in an",
        "# interactive Claude Code session; zero API calls during scoring.",
        "#",
        "#   mondaybench evaluate --scenario monday-004 --all-models \\",
        "#       --evaluator evaluator-opus5-v0.4-calibration-3 \\",
        "#       --verdicts verdicts/monday-004/calibration-v0.3.jsonl --review",
    ]
    for model, run_id in RUNS.items():
        for (m, cid), (result, evidence, reason) in V.items():
            if m != model:
                continue
            lines.append(json.dumps({
                "run_id": run_id, "kind": "criterion", "criterion_id": cid,
                "result": result, "evidence": evidence, "reason": reason,
            }, ensure_ascii=False))
        lines.append(json.dumps({
            "run_id": run_id,
            "kind": "penalties",
            "violations": PENALTIES.get(model, []),
        }, ensure_ascii=False))

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    counts: dict[str, list[str]] = {}
    for (m, _), (r, _, _) in V.items():
        counts.setdefault(m, []).append(r)
    print(f"wrote {OUT}")
    for m, rs in counts.items():
        print(f"  {m:<10} {len(rs)} criteria  PASS {rs.count('PASS')}  PARTIAL {rs.count('PARTIAL')}  FAIL {rs.count('FAIL')}")


if __name__ == "__main__":
    main()
