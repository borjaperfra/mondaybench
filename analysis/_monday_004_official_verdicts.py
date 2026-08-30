"""Recorded verdicts for the monday-004 OFFICIAL battery, rubric 0.3.

    python analysis/_monday_004_official_verdicts.py

Writes `verdicts/monday-004/official.jsonl`.

Three runs per model for seven models, all generated after the freeze under the
96,000-token safety ceiling, all against prompt
3a0cbb569ca4f711b8907177af9204cec267d26f35f732829df56b03ed23ef99.

The calibration battery is NOT in here and must never be: rubric 0.3 was written
while reading those responses, so they cannot also be the evidence it publishes.
They live in `archive/monday-004-v0.3-calibration/`, and
`leaderboard.check_calibration_overlap` refuses to publish if one leaks back.

Judged in an interactive Claude Code session against `rubric-0.3.yaml` and
`ground-truth.yaml`; every figure cited was checked against the CSVs. Zero API
calls.
"""

from __future__ import annotations

import json
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "verdicts" / "monday-004" / "official.jsonl"

# model slug -> the three post-freeze run numbers that make up its battery.
RUNS: dict[str, list[int]] = {
    "gemma4": [3, 4, 5],
    "deepseek-v4-flash": [4, 5, 6],
    "glm5.3-flash": [3, 4, 5],
    "glm5.2": [3, 4],
    "mimo-v2.5": [4, 5, 6],
    "qwen3.8-flash": [3, 4, 6],
}

P, T, F = "PASS", "PARTIAL", "FAIL"

# (model slug, run number, criterion id) -> (result, evidence, reason)
V: dict[tuple[str, int, str], tuple[str, str, str]] = {}
# (model slug, run number) -> list of violations
PENALTIES: dict[tuple[str, int], list[dict[str, str]]] = {}


def add(model: str, run: int, criterion: str, result: str, evidence: str, reason: str) -> None:
    V[(model, run, criterion)] = (result, evidence, reason)


# Two readings of the frozen rubric that every verdict below depends on, written
# down because they are judgment calls and a reader should be able to disagree
# with them in one place rather than twenty-one.
#
# 1. `figures_carried_correctly` charges wrong FIGURES - a number that does not
#    match the pack, or a number attached to the wrong population. It does not
#    charge wrong INFERENCES drawn from correct figures: "no plan exceeds its
#    included allowance" reads three plan averages that are all quoted
#    correctly, and the error is in treating an average as a distribution.
#    Every other criterion in this rubric exists to price inference; if this one
#    priced it too, a single mistake would cost twice.
#
#    NOTE: the shipped criterion text does not say this. The design note
#    (analysis/monday-004-rubric-v0.3.md) does - "an error another criterion
#    already prices is not charged again" - and the calibration was scored that
#    way, but the sentence never made it into rubric-0.3.yaml before the freeze.
#    The rubric is frozen, so it stays as it is and the reading is recorded here
#    instead. It is the one place where this battery's scoring rests on a
#    document outside the frozen artifact, and it should be folded into the
#    criterion text in any future rubric revision.
#
# 2. `segment_recommendation` is SMB-specific, as written: FAIL is "Recommends
#    cutting, exiting or defunding SMB". A response that recommends reducing a
#    DIFFERENT segment has not done the thing this criterion forbids, however
#    thin its grounds, and lands at PARTIAL. The rubric could have been written
#    to cover any segment; it was not, and it is frozen.


# =========================================================================
# Gemma 4
# =========================================================================
# Three runs that diverge sharply on arithmetic while keeping the same memo
# shape - run-003 and run-005 reproduce the plan table exactly, run-004 gets
# five of its six margins wrong - and on the acquisition decision, where
# run-005 recommends the one action the pack rules out.

# --- run-003 -------------------------------------------------------------
add("gemma4", 3, "duplicate_detected", F,
    "no repeated transaction id anywhere in the response",
    "The duplicate is not mentioned.")
add("gemma4", 3, "annual_prepayment_normalized", P,
    "'October revenue was bolstered by a EUR 120k annual upfront payment from Gringotts, masking "
    "underlying churn' and a table separating 'Subscription Revenue' from 'Total Cash Inflow'",
    "Identifies the invoice and separates it out of the subscription line, which is one of the "
    "treatments the criterion accepts. No monthly equivalent is stated.")
add("gemma4", 3, "headline_vs_recurring_growth", T,
    "'September Subscription Revenue: EUR 659,000 / October: EUR 659,500 (Flat)' against "
    "'October Total Cash Inflow: EUR 779,500'",
    "Contrasts a cash basis with a subscription basis and labels both, but neither figure is a "
    "total in the pack - EUR 659,500 is the enterprise plan alone - so the raw +12% the headline "
    "would report is never computed. The wrong figures are charged separately.")
add("gemma4", 3, "revenue_conclusion", P,
    "'Revenue is stable but driven by a single massive event' as the opening line of the "
    "executive summary",
    "The conclusion the criterion asks for - underlying revenue flat, the reported growth "
    "non-recurring - stated to leadership with figures behind it. That the figures are wrong is "
    "charged under figures_carried_correctly, not here.")
add("gemma4", 3, "segment_retention_quantified", T,
    "'SMB: High churn risk. Four SMB customers churned in October alone (Slate-rock, "
    "Mega-lo-mart, Dinoco, Buy-n-large)'; Enterprise 'low churn'; Mid-market 'churn (Nakatomi)'",
    "The churned logos are placed in the right segments, but no rate is computed on any basis "
    "and the segments are never ranked on retention.")
add("gemma4", 3, "sample_size_arr_context", F,
    "churn is described only as 'high churn risk' and 'low individual ARR'",
    "No ARR, no denominator and no comparison with what SMB added or with the Mid-market loss.")
add("gemma4", 3, "acme_false_positive_avoided", T,
    "'planned shift to batch processing' and, in the uncertainties, 'we cannot confirm if this "
    "will lead to a revenue decrease at renewal'",
    "Names the migration and does not treat Acme as a churn risk, but offers no second metric - "
    "tokens or revenue - to show the workload moved rather than shrank.")
add("gemma4", 3, "no_churn_overreach", P,
    "'We cannot definitively say why SMB churn is high (is it product fit, price, or support "
    "quality?), only that it is happening'",
    "Names the gap instead of filling it.")
add("gemma4", 3, "raw_attribution_not_equivalent_new_business", F,
    "the channel table reports 'Attributed ARR (Oct)' and 'Avg. ARR/Conv' with no split",
    "Expansion is never separated from new business, and the paid-search expansion block is "
    "never mentioned.")
add("gemma4", 3, "existing_customer_expansion_removed", F,
    "no new-logo view of any channel",
    "The split is never made, so the ranking never reverses.")
add("gemma4", 3, "conversion_rate_vs_absolute_volume", F,
    "the funnel table carries October only - Paid Search 900/58/6.4%, Content 330/34/10.3%, "
    "Partner 75/17/22.7%, Outbound 195/11/5.6%",
    "Every October figure is exact and September is absent, so neither the falling conversion "
    "rate nor the rising absolute conversions can be seen.")
add("gemma4", 3, "no_unsupported_channel_scale_decision", P,
    "'Growth should not simply increase spend on the highest volume channel (Paid Search)' with "
    "'total channel spend (marketing cost) is not provided in the data'",
    "This criterion asks about Paid Search specifically: it declines to scale it and names the "
    "missing input. That its Partner recommendation is unconditioned is charged under "
    "acquisition_recommendation.")
add("gemma4", 3, "cac_payback_unavailable", P,
    "'Cannot be fully calculated because total channel spend (marketing cost) is not provided "
    "in the data'",
    "Refused, with the missing input named.")
add("gemma4", 3, "contribution_calculated", P,
    "EUR 194,700 / EUR 41,500 / EUR 10,300 under an explicit 'Revenue - Infra - Support'",
    "All three exact.")
add("gemma4", 3, "margin_calculated_or_correctly_compared", P,
    "29.5% / 62.7% / 32.2%",
    "All three correct and correctly ordered.")
add("gemma4", 3, "absolute_vs_scalable_economics", P,
    "'Weakest Plan: Enterprise (on a percentage basis). While it brings in the most absolute "
    "Euros, the margin is only 29.5%' against 'Strongest Plan: Pro ... 62.7% margin'",
    "Holds both halves explicitly and keeps the summary consistent with the analysis.")
add("gemma4", 3, "plan_trajectory_evidence", F,
    "no usage trajectory and no reference to included request volumes anywhere",
    "Neither growth nor the distribution against the allowance is examined.")
add("gemma4", 3, "product_focus_supported", T,
    "'Engineering focus should be directed toward the Pro plan ... it is the most profitable "
    "engine for growth', with 'a growing customer base (8 to 9)' as the second reason",
    "The right plan, argued from margin and a customer count. The usage growth, the rate-limit "
    "tickets and the accounts over their allowance - the signals that make the case - are absent.")
add("gemma4", 3, "customer_id_alias_resolved", F,
    "Wayne appears only in a list of accounts with support tickets; no account-level usage join "
    "is attempted anywhere",
    "The alias is neither resolved nor noticed.")
add("gemma4", 3, "support_normalized", F,
    "support cost appears in the plan table as an absolute (EUR 168,000 / 8,600 / 10,300) and "
    "the recommendation reads 'Address the spike in API Error and Performance tickets for "
    "Enterprise customers'",
    "No rate against any denominator, and the one support conclusion it draws is argued from "
    "Enterprise's raw ticket volume - which is lower per customer than Pro's.")
add("gemma4", 3, "figures_carried_correctly", F,
    "'September Subscription Revenue: EUR 659,000 / October: EUR 659,500' is the enterprise "
    "plan, not subscriptions; 'October Total Cash Inflow: EUR 779,500' is that figure plus the "
    "annual invoice and matches no total in the pack (raw EUR 892,900, deduplicated EUR 873,400); "
    "'Attributed ARR (Oct)' gives Paid Search EUR 193,200 and Partner EUR 132,000",
    "Repeated incorrect figures across different sections, and the headline conclusion that "
    "revenue is 'stable' rests on the first pair. The plan table and the October funnel are exact.")
add("gemma4", 3, "cross_table_customer_signal", T,
    "Acme read across usage and the operational note, with the renewal implication drawn",
    "One account from two sources. No account is assembled from three or more tables, and "
    "Soylent is not mentioned.")
add("gemma4", 3, "causal_boundary", F,
    "Soylent appears nowhere in the response",
    "None of the three simultaneous movements is reported, so the pattern is never seen.")
add("gemma4", 3, "segment_recommendation", P,
    "'Do not cut Enterprise. Instead, investigate the SMB segment's high churn rate and low "
    "margins to determine if the cost of acquisition/support is sustainable for that tier.'",
    "Does not cut SMB, recommends investigating it, and names acquisition cost as the input "
    "needed - which is the PASS bar exactly, even though the segment framing is reached via "
    "Enterprise.")
add("gemma4", 3, "acquisition_recommendation", T,
    "'Shift/Increase budget toward the Partner channel. It delivers the highest quality leads "
    "and the best conversion rates.'",
    "Names the right channel, but reaches it through conversion rate and ARR per conversion "
    "because the new-logo correction is never made, and does not condition the spend.")
add("gemma4", 3, "product_recommendation", P,
    "'Prioritize the Pro plan roadmap'",
    "Single, actionable and consistent with its own section 4.")
add("gemma4", 3, "uncertainty_discipline", P,
    "four items: CAC spend, the causal gap behind SMB churn, Acme's renewal impact, and the "
    "expansion-booking lag in acquisition.csv",
    "All real gaps in this pack, and nothing is presented as known that is not.")

# --- run-004 -------------------------------------------------------------
add("gemma4", 4, "duplicate_detected", F,
    "no repeated transaction id anywhere in the response",
    "The duplicate is not mentioned.")
add("gemma4", 4, "annual_prepayment_normalized", F,
    "'Revenue Growth is driven by expansion and new annual contracts, not organic subscription "
    "growth' - the Gringotts invoice is never identified",
    "Gestures at annual contracts without finding the EUR 120,000 invoice, its monthly "
    "equivalent or its effect on the month.")
add("gemma4", 4, "headline_vs_recurring_growth", F,
    "'While headline revenue appears stable' with no revenue figure anywhere in the response",
    "Neither basis is computed, so there is no comparison to make.")
add("gemma4", 4, "revenue_conclusion", T,
    "'Revenue Growth is driven by expansion and new annual contracts, not organic subscription "
    "growth'",
    "The right direction, stated first, with nothing quantified behind it and the annual invoice "
    "never located.")
add("gemma4", 4, "segment_retention_quantified", T,
    "'SMB Churn: We are seeing active churn in the SMB segment (Slate-rock, Mega-lo-mart, "
    "Dinoco, Buy-n-large all churned in October)' and a three-line segment summary",
    "The churned logos are placed correctly, but no rate on any basis and no ranking.")
add("gemma4", 4, "sample_size_arr_context", F,
    "'SMB: Low ARR, high churn rate' with no figure",
    "None of the three contexts the criterion asks for is present.")
add("gemma4", 4, "acme_false_positive_avoided", T,
    "'a massive usage drop at Acme Corp (-45% requests) in October is a major red flag. While "
    "this is partially explained by their move to batch processing (estimated 40-50% reduction), "
    "the drop in request volume is significant.'",
    "Finds the migration and quotes the note's own 40-50% estimate, then still books the move as "
    "a red flag rather than the non-event the pack explains.")
add("gemma4", 4, "no_churn_overreach", P,
    "'We cannot definitively say if the Mid-market support spike is causing churn or if churn is "
    "causing the support spike'",
    "Refuses the causal claim and names the direction problem explicitly.")
add("gemma4", 4, "raw_attribution_not_equivalent_new_business", F,
    "attributed revenue is used as-is throughout the acquisition section",
    "Expansion is never separated and the paid-search expansion block is never mentioned.")
add("gemma4", 4, "existing_customer_expansion_removed", F,
    "no new-logo view of any channel",
    "The split is never made.")
add("gemma4", 4, "conversion_rate_vs_absolute_volume", F,
    "October conversion rates only: Content 10.3%, Partner 22.7%, Paid Search 6.4%, Outbound 5.6%",
    "Correct for October and September is absent, so the movement in either direction is invisible.")
add("gemma4", 4, "no_unsupported_channel_scale_decision", T,
    "'Increase spend on the Partner channel. It has the highest conversion rate (22.7%) and the "
    "highest revenue per lead.'",
    "Recommends increasing spend on a revenue-per-lead figure it computed wrongly and without "
    "conditioning on the cost data it flags as missing two sections later. Partner is at least "
    "the channel the corrected view favours.")
add("gemma4", 4, "cac_payback_unavailable", T,
    "'We cannot calculate true CAC Payback because the marketing spend (cost) per channel was "
    "not provided in the data pack. We have used Revenue per Lead as a proxy.' followed by a "
    "four-row proxy table",
    "The refusal and the missing input are both right, and then it computes the proxy - which "
    "the criterion places at PARTIAL - on figures that are themselves wrong, including "
    "EUR 1,110,000 of partner revenue that does not exist.")
add("gemma4", 4, "contribution_calculated", T,
    "'Enterprise EUR 204,700 | Pro EUR 41,500 | Starter EUR 17,100' for October, and "
    "EUR 211,200 / EUR 43,500 / EUR 8,300 for September",
    "One of six figures is right - October is EUR 194,700 / EUR 41,500 / EUR 10,300 - but the "
    "cost-adjusted calculation is performed for every plan on the right definition, which is "
    "more than the FAIL bar of comparing plans on revenue alone.")
add("gemma4", 4, "margin_calculated_or_correctly_compared", T,
    "'31.2% / 62.7% / 53.4%'",
    "Margins are given for all three plans and the ordering is right, but two figures are "
    "materially wrong: the correct margins are 29.5% / 62.7% / 32.2%, and Starter is out by 21 "
    "points in the direction that makes the plan look healthy.")
add("gemma4", 4, "absolute_vs_scalable_economics", P,
    "'While it generates the most absolute profit, its margin percentage is the lowest (approx. "
    "31%)' against 'Pro: This is the sweet spot. It has the highest margin percentage'",
    "The distinction is held and correctly directed, even though the underlying figures are wrong.")
add("gemma4", 4, "plan_trajectory_evidence", F,
    "'healthy usage-to-cost ratios' with no usage figure, no growth rate and no reference to "
    "included request volumes",
    "Neither trajectory nor distribution is examined.")
add("gemma4", 4, "product_focus_supported", T,
    "'The Pro plan deserves the most engineering focus. It is the most economically efficient "
    "and shows the best balance of scale and margin.'",
    "The right plan on margin and a vague scaling claim. None of the usage, rate-limit or "
    "over-allowance signals is present.")
add("gemma4", 4, "customer_id_alias_resolved", F,
    "'Hooli are growing (+22%), others like Soylent are declining (-27%)' - Wayne Enterprises "
    "appears nowhere",
    "Two accounts are read from usage, but the billing-to-usage join that the alias breaks is "
    "never attempted, so the alias is neither resolved nor noticed.")
add("gemma4", 4, "support_normalized", F,
    "'high support overhead' for Mid-market and 'the primary drivers of high-severity tickets in "
    "the Mid-market and Enterprise segments'",
    "No rate against any denominator anywhere, and the segment conclusion rests on raw counts.")
add("gemma4", 4, "figures_carried_correctly", F,
    "'Partner: EUR 1,110,000 / 135 leads = EUR 8,222/lead' when partner's attributed ARR across "
    "both months is EUR 166,800; 'Paid Search: EUR 332,800' when it is EUR 274,800; and five of "
    "the six plan-margin figures wrong",
    "Repeated incorrect figures across three different sections, and both the plan conclusion "
    "and the channel recommendation stand on them.")
add("gemma4", 4, "cross_table_customer_signal", T,
    "'Hooli are growing (+22%), others like Soylent are declining (-27%)'",
    "Soylent's usage decline is correct and it is the right account to notice, but only usage is "
    "read: its downgrade and its ticket spike are both absent.")
add("gemma4", 4, "causal_boundary", F,
    "'others like Soylent are declining (-27%)' - the only one of Soylent's three movements the "
    "response reports; its ticket spike and its invoice cut are both absent",
    "The criterion is about Soylent's three simultaneous movements, and reporting only one of "
    "them is the FAIL bar as written. Its clean statement of the causal limit elsewhere - 'we "
    "cannot definitively say if the Mid-market support spike is causing churn' - is about a "
    "different, segment-level pattern.")
add("gemma4", 4, "segment_recommendation", T,
    "'Do not reduce investment in Mid-market yet ... However, investigate the high support "
    "costs/ticket volume in this segment.'",
    "Does not recommend cutting SMB, which keeps it off FAIL, but answers about Mid-market and "
    "leaves SMB without a next step or a statement of what the pack cannot settle.")
add("gemma4", 4, "acquisition_recommendation", T,
    "'Increase spend on the Partner channel ... If Partner leads are scarce, the second priority "
    "should be Content'",
    "The right two channels in the right order, reached through conversion rate and a wrong "
    "revenue-per-lead rather than the new-logo correction, and not conditioned on the cost gap.")
add("gemma4", 4, "product_recommendation", P,
    "'Focus engineering on the Pro plan'",
    "Single, actionable and consistent with its own section 4.")
add("gemma4", 4, "uncertainty_discipline", T,
    "four items: the causal direction between support and churn, whether Acme's drop is entirely "
    "batching, the missing channel spend, and the expansion-booking lag",
    "The four gaps are real and material. But this criterion also requires that the response "
    "invent no figures anywhere, and 'Partner: EUR 1,110,000 / 135 leads' is a channel total "
    "nearly seven times the EUR 166,800 in the pack.")

# --- run-005 -------------------------------------------------------------
add("gemma4", 5, "duplicate_detected", F,
    "no repeated transaction id anywhere in the response",
    "The duplicate is not mentioned.")
add("gemma4", 5, "annual_prepayment_normalized", T,
    "'October revenue was bolstered by a large annual upfront payment from Gringotts (EUR 120k), "
    "which masks the underlying monthly subscription trends'",
    "Identifies the invoice and states the direction of the distortion, but never gives the "
    "monthly equivalent and never excludes it from a figure.")
add("gemma4", 5, "headline_vs_recurring_growth", F,
    "'Headline revenue is heavily skewed by the Enterprise segment' with no revenue total on any "
    "basis",
    "Neither the raw nor the recurring figure is computed, so no comparison exists.")
add("gemma4", 5, "revenue_conclusion", T,
    "'Headline revenue is heavily skewed by the Enterprise segment' plus the Gringotts note",
    "Identifies a real distortion and carries it into the summary, but never confronts the "
    "growth number the pack would otherwise report.")
add("gemma4", 5, "segment_retention_quantified", T,
    "'the loss of Nakatomi (churned Oct) represents a loss of EUR 180k ARR' and 'Four SMB "
    "customers churned in October (Slate-rock, Mega-lo-mart, Dinoco, Buy-n-large)'",
    "Correct placement and one correct ARR figure, but no rate on any basis for any segment and "
    "no ranking.")
add("gemma4", 5, "sample_size_arr_context", T,
    "'the loss of Nakatomi ... EUR 180k ARR' against 'Enterprise: Drives ~90% of total ARR'",
    "Sizes the Mid-market loss and gives Enterprise's share, but never sizes the SMB churn it "
    "calls a high risk, so the comparison the criterion asks for is only half made.")
add("gemma4", 5, "acme_false_positive_avoided", T,
    "'a 45% drop in request volume in October due to a shift to batch processing' and, in the "
    "uncertainties, 'a known operational shift (batching), not necessarily a loss of customer "
    "interest, which could skew health metrics if not interpreted correctly'",
    "States the explanation confidently and warns against the exact misreading the trap invites, "
    "but offers no second metric to corroborate that the workload moved rather than shrank.")
add("gemma4", 5, "no_churn_overreach", P,
    "'We cannot definitively say if the drop in Acme Corp's usage caused a revenue drop, as the "
    "revenue file shows they are still paying their monthly subscription'",
    "Claims no cause the pack does not record, for churn or for the usage decline.")
add("gemma4", 5, "raw_attribution_not_equivalent_new_business", T,
    "'Note: Paid Search includes high-value expansion bookings (e.g., Stark Industries, Umbrella "
    "Health), making its per lead value significantly higher than others.'",
    "Sees the contamination and names two of the four expanding accounts, then never quantifies "
    "it and recommends increasing paid-search spend anyway.")
add("gemma4", 5, "existing_customer_expansion_removed", F,
    "no new-logo ARR figure for any channel",
    "Having identified that expansion inflates paid search, it never removes it, so the ranking "
    "never reverses.")
add("gemma4", 5, "conversion_rate_vs_absolute_volume", T,
    "the two-month table: Paid Search 8.6% -> 6.4%, Content 11.9% -> 10.3%, Partner 25.0% -> "
    "22.6%, Outbound 6.2% -> 5.6%",
    "The falling rate is shown for every channel, which is half the point. Absolute conversions "
    "are given for October only, so the rise in conversions alongside the falling rate is never "
    "read.")
add("gemma4", 5, "no_unsupported_channel_scale_decision", F,
    "'Decision Support: Increase spend on Paid Search. While Partner has a higher conversion "
    "rate, Paid Search is successfully capturing both new logos and massive expansion revenue "
    "from existing Enterprise clients.'",
    "Recommends scaling the one channel the pack rules out, on the attributed revenue it had "
    "itself flagged as contaminated by expansion, and without the cost data it says elsewhere is "
    "missing.")
add("gemma4", 5, "cac_payback_unavailable", P,
    "'The CFO's request for CAC payback cannot be fully fulfilled because marketing spend (cost) "
    "per channel is not provided in the dataset.'",
    "Refused, with the missing input named.")
add("gemma4", 5, "contribution_calculated", P,
    "EUR 194,700 / EUR 41,500 / EUR 10,300, with the cost column EUR 464,800 / 24,700 / 21,700",
    "All exact, including the combined cost figures.")
add("gemma4", 5, "margin_calculated_or_correctly_compared", P,
    "29.5% / 62.7% / 32.2%",
    "All three correct.")
add("gemma4", 5, "absolute_vs_scalable_economics", T,
    "'The Pro plan is the most economically efficient. However, the Enterprise plan is the most "
    "expensive to run' followed by 'Engineering focus should be on the Enterprise plan ... "
    "Protecting this EUR 659k/month revenue is the priority.'",
    "States the distinction correctly and then argues the product decision from the absolute "
    "revenue figure, which is the confusion the criterion exists to catch.")
add("gemma4", 5, "plan_trajectory_evidence", F,
    "no usage trajectory and no reference to included request volumes",
    "Neither growth nor the distribution against the allowance is examined.")
add("gemma4", 5, "product_focus_supported", F,
    "'Direct Engineering focus to the Enterprise Plan ... Protecting this EUR 659k/month revenue "
    "is the priority.'",
    "A plan other than Pro is acceptable only when the case does not rest on absolute revenue. "
    "Here the revenue figure is the stated priority and the stability argument rests on raw "
    "ticket counts.")
add("gemma4", 5, "customer_id_alias_resolved", F,
    "Wayne appears only in a list of accounts with high-severity tickets; no account-level usage "
    "join is attempted",
    "The alias is neither resolved nor noticed.")
add("gemma4", 5, "support_normalized", F,
    "'Support data shows a high concentration of High severity tickets ... among Enterprise "
    "clients (Acme, Stark, Wayne, Umbrella)'",
    "No rate against any denominator, and the engineering recommendation is argued from "
    "Enterprise's raw ticket volume - 2.50 per customer against Pro's 3.11.")
add("gemma4", 5, "figures_carried_correctly", T,
    "the plan table and both cost columns are exact, the two-month conversion rates are right to "
    "a tenth, Nakatomi's EUR 180k is right and 'Enterprise drives ~90% of total ARR' is hedged "
    "against an actual 87%. The 'Avg. Attributed ARR' column gives Partner EUR 132,000, which is "
    "Vandelay's whole contract rather than an average",
    "One mislabelled column in an otherwise accurate response, and nothing rests on it.")
add("gemma4", 5, "cross_table_customer_signal", T,
    "Acme across usage, the operational note and revenue; Nakatomi across the churn list and ARR",
    "Two accounts read from two sources each. No account is built from three or more tables, and "
    "Soylent is absent.")
add("gemma4", 5, "causal_boundary", F,
    "Soylent appears nowhere in the response",
    "None of the three simultaneous movements is reported, so the pattern is never seen.")
add("gemma4", 5, "segment_recommendation", T,
    "'Do NOT reduce investment in any customer segment yet ... Instead, pivot SMB strategy "
    "toward Starter automation to reduce support overhead.'",
    "Refuses the cut and gives a concrete next step, but the PASS bar also asks that the missing "
    "input be named - acquisition cost, lifetime value, retention drivers or segment economics - "
    "and this names none of them. It prescribes an action instead of an investigation.")
add("gemma4", 5, "acquisition_recommendation", F,
    "'Increase spend on Paid Search. It is the primary driver for both new logos and high-value "
    "expansion.'",
    "The wrong channel, on the raw attribution it had itself flagged as contaminated, and "
    "against its own table showing paid search with the worst conversion rate and the steepest "
    "decline.")
add("gemma4", 5, "product_recommendation", P,
    "'Direct Engineering focus to the Enterprise Plan'",
    "Single and actionable, and consistent with its own section 4. Whether it is the right plan "
    "is priced under product_focus_supported.")
add("gemma4", 5, "uncertainty_discipline", P,
    "four items: missing channel spend, the Acme causal claim, the batching interpretation risk, "
    "and untracked expansion timing",
    "All real, and no figure is presented as known that is not.")

PENALTIES[("gemma4", 5)] = [{
    "type": "PROHIBITED_ACTION",
    "evidence": "'Decision Support: Increase spend on Paid Search.' and, in the recommendations, "
                "'Increase spend on Paid Search. It is the primary driver for both new logos and "
                "high-value expansion.'",
    "reason": "Materially increasing paid-search spend on raw attributed revenue is the second "
              "action the pack rules out, and this response reaches it after correctly noting in "
              "its own table footnote that paid search's attributed revenue is inflated by "
              "expansion bookings from existing enterprise accounts. Its own figures also show "
              "paid search with the worst conversion rate of the four channels and the steepest "
              "decline. Naming the option to reject it would have been right; this tells "
              "leadership to do it.",
}]


# =========================================================================
# DeepSeek V4 Flash
# =========================================================================
# The most arithmetically reliable model in the battery - across three runs I
# found two wrong figures, and both are already priced by another criterion.
# What separates the runs is judgment: run-004 pauses Mid-market acquisition,
# run-005 reduces SMB/Starter, run-006 refuses to move any spend at all.

# --- run-004 -------------------------------------------------------------
add("deepseek-v4-flash", 4, "duplicate_detected", P,
    "'October revenue.csv includes ... a duplicate Soylent transaction (same transaction ID from "
    "Stripe and billing_sync). I used plans.csv for MRR and excluded one-time/PS revenue.'",
    "Identified with both sources named, and the analysis is built on a basis that excludes it.")
add("deepseek-v4-flash", 4, "annual_prepayment_normalized", P,
    "'October revenue.csv includes a EUR 120k annual prepay from Gringotts ... I used plans.csv "
    "for MRR and excluded one-time/PS revenue'",
    "Identified and explicitly excluded, with the treatment stated. The EUR 10k monthly "
    "equivalent is not given.")
add("deepseek-v4-flash", 4, "headline_vs_recurring_growth", T,
    "'Reported October plan MRR is EUR 757.7k vs EUR 746.1k in September (+1.6%), but that "
    "includes customers who churned during October. Active MRR at end-October is EUR 732.4k, a "
    "-1.8% decline.'",
    "Two bases, each labelled with exactly what it contains, and the gap between them shown. The "
    "raw invoiced comparison the headline would be built on is never computed, so the largest "
    "distortion is stepped around rather than measured.")
add("deepseek-v4-flash", 4, "revenue_conclusion", P,
    "'Headline MRR is flat-to-down once churn is adjusted' as the first line of the summary",
    "Leads the brief and carries its figures.")
add("deepseek-v4-flash", 4, "segment_retention_quantified", T,
    "the active-MRR table - Enterprise EUR 565.0k flat, Mid-market EUR 142.0k -> EUR 127.5k "
    "(-10.2%), SMB EUR 39.1k -> EUR 39.9k (+2.0%) - plus churned ARR of EUR 303.6k itemised by "
    "account",
    "Quantifies segment movement on a stated basis and ranks the three, but the basis is net "
    "revenue movement rather than retention: SMB's four churns are offset by its five new logos, "
    "so no churn or retention rate is given for any segment.")
add("deepseek-v4-flash", 4, "sample_size_arr_context", P,
    "'Churned ARR: ... EUR 303.6k / New logo ARR: ... EUR 133.2k / Net ARR impact: -EUR 170.4k' "
    "and 'SMB churned 4 customers but added 5 new logos, so active MRR was roughly flat'",
    "Sizes the churn in ARR, nets it against new business, and sets SMB's four small losses "
    "against Mid-market's single large one. Every figure exact.")
add("deepseek-v4-flash", 4, "acme_false_positive_avoided", P,
    "'Acme's request volume fell 45% after moving to batch workloads, while token volume only "
    "fell 12%' and 'Acme's request drop is a workload change, not churn'",
    "Migration plus the token figure that shows the workload moved rather than shrank.")
add("deepseek-v4-flash", 4, "no_churn_overreach", P,
    "Soylent's downgrade and ticket spike are reported together as 'a clear account-health red "
    "flag' with no reason attached to any churn",
    "Claims no cause the pack does not record.")
add("deepseek-v4-flash", 4, "raw_attribution_not_equivalent_new_business", P,
    "'Most October paid-search attributed revenue came from expansions of existing customers "
    "(Stark, Umbrella, Globex), not new logos' and 'Expansion bookings ... total EUR 216k'",
    "The split is stated, the accounts named, and the EUR 216k October expansion total is exact.")
add("deepseek-v4-flash", 4, "existing_customer_expansion_removed", P,
    "the new-logo ACV table: Partner 2 / EUR 166.8k / EUR 83.4k, Paid search 2 / EUR 64.8k / "
    "EUR 32.4k, Content 3 / EUR 91.2k / EUR 30.4k, Outbound 2 / EUR 56.4k / EUR 28.2k",
    "Every figure exact, the ranking reversed against attributed revenue, and the small sample "
    "flagged.")
add("deepseek-v4-flash", 4, "conversion_rate_vs_absolute_volume", P,
    "'Paid search volume jumped 73% but conversion rate fell from 8.5% to 6.4%'",
    "Both movements in one sentence, with an exact two-month table behind them.")
add("deepseek-v4-flash", 4, "no_unsupported_channel_scale_decision", P,
    "'Increase spend on the Partner channel, but only after validating cost data ... run a "
    "small, controlled increase in partner spend and track trial-to-paid conversion and CAC "
    "before scaling'",
    "Conditions every euro of new spend on the data the pack does not contain.")
add("deepseek-v4-flash", 4, "cac_payback_unavailable", P,
    "'Cannot be calculated. The data pack does not include spend by channel.'",
    "Refused, with the missing input named.")
add("deepseek-v4-flash", 4, "contribution_calculated", P,
    "EUR 212.0k / 42.5k / 8.4k for September and EUR 194.7k / 41.5k / 10.3k for October",
    "All six exact, with the revenue and cost columns behind them.")
add("deepseek-v4-flash", 4, "margin_calculated_or_correctly_compared", P,
    "32.2% / 67.5% / 34.9% and 29.5% / 62.7% / 32.2%",
    "All six correct.")
add("deepseek-v4-flash", 4, "absolute_vs_scalable_economics", P,
    "'Enterprise plan has the lowest margin and it deteriorated ... This is a cost-efficiency "
    "problem, not a revenue problem' against 'Pro plan has the highest margin'",
    "Holds both halves and routes each to its own workstream - engineering to Pro, cost "
    "investigation to Enterprise.")
add("deepseek-v4-flash", 4, "plan_trajectory_evidence", P,
    "'Enterprise plan: 3 customers exceeded included requests in September (Acme, Stark, Wayne). "
    "In October, only Stark and Wayne exceeded ... Pro plan: 1 customer exceeded in September "
    "(Wonka). In October, 3: Wonka, Aperture, and Vandelay.'",
    "Reads the distribution against the allowance account by account across both months, for all "
    "three plans, and ties the Pro movement to the rate-limit tickets.")
add("deepseek-v4-flash", 4, "product_focus_supported", P,
    "'Focus engineering on the Pro plan ... rate-limit tickets more than doubled, and more "
    "customers are exceeding included requests. Address capacity/limits, especially for Wonka, "
    "Aperture, and Vandelay.'",
    "Margin, ticket trajectory and three named accounts, with Enterprise sent to cost work "
    "instead of being confused for a product problem.")
add("deepseek-v4-flash", 4, "customer_id_alias_resolved", P,
    "Wayne appears in the enterprise over-allowance list for both months with usage that is only "
    "reachable through the alias, and 'Prestige' appears among the Pro rate-limit accounts",
    "Both aliases resolved in practice, though neither is described.")
add("deepseek-v4-flash", 4, "support_normalized", T,
    "'Rate-limit tickets by plan: Pro plan went from 5 in September to 13 in October' and "
    "'Wonka alone had 4 rate-limit tickets in October'",
    "Correct counts and a real within-plan trajectory, but no rate against any denominator and "
    "no comparison across plans. It avoids the raw-count trap without doing the normalisation.")
add("deepseek-v4-flash", 4, "figures_carried_correctly", P,
    "checked against the CSVs: the segment MRR walk, churned and new-logo ARR itemised by "
    "account, the EUR 216k October expansion total, all eight funnel rates, the full new-logo ACV "
    "table, all twelve plan-economics figures, both cost deltas, Hooli's +EUR 3k and the "
    "over-allowance accounts for both months",
    "No incorrect figure. 'October shows no partner customer conversions yet in acquisition.csv' "
    "is also right, and is the sharpest observation in the battery about partner's sample.")
add("deepseek-v4-flash", 4, "cross_table_customer_signal", P,
    "'Soylent downgraded from EUR 22k/mo to EUR 19.5k/mo and generated 8 support tickets in "
    "October, including a critical API error' alongside its usage decline",
    "One account assembled from revenue, support and usage with every figure correct.")
add("deepseek-v4-flash", 4, "causal_boundary", P,
    "the Soylent trio reported together as 'a clear account-health red flag', and 'Acme's request "
    "drop is a workload change, not churn ... so the revenue/usage impact is unclear'",
    "Assembles the pattern, escalates it, and asserts no mechanism.")
add("deepseek-v4-flash", 4, "segment_recommendation", T,
    "'Reduce incremental investment in the Mid-market segment ... pause new Mid-market "
    "acquisition spend until retention and account health improve.' SMB is described as "
    "'treading water' with 'replacement revenue coming in' and is not cut.",
    "It does not cut SMB, which is what this criterion forbids, and it gives SMB no next step "
    "either - the PARTIAL bar. What it does instead is recommend a reduction in a different "
    "segment on one month of movement in a ten-customer population driven by a single churn, "
    "having itself noted that segment-level costs are not in the pack. The rubric does not "
    "reach that, and it is frozen.")
add("deepseek-v4-flash", 4, "acquisition_recommendation", P,
    "'Increase spend on the Partner channel, but only after validating cost data ... Partner has "
    "the highest trial conversion rate (~23-25%) and the highest average new-logo ACV (EUR 83.4k)'",
    "Names the channel the corrected new-logo view favours, on the corrected figure, and gates "
    "the spend on the missing cost data.")
add("deepseek-v4-flash", 4, "product_recommendation", P,
    "'Focus engineering on the Pro plan'",
    "Single, actionable, consistent with its own section 4.")
add("deepseek-v4-flash", 4, "uncertainty_discipline", P,
    "eight items including the funnel/acquisition linkage gap, plans.csv counting churned "
    "customers, the equal-cost-per-customer assumption behind segment allocation, and the small "
    "partner sample",
    "Every gap real, several beyond the answer key, and the one methodological assumption it had "
    "to make is stated as an assumption.")

# --- run-005 -------------------------------------------------------------
add("deepseek-v4-flash", 5, "duplicate_detected", P,
    "'INV-2026-10-0209 for Soylent appears twice, once from stripe and once from billing_sync. "
    "October revenue should be deduplicated.' - and the headline uses the deduplicated EUR 873.4k",
    "Identified by invoice id and both sources, and excluded from the figure it reports.")
add("deepseek-v4-flash", 5, "annual_prepayment_normalized", P,
    "'inflated by Gringotts' EUR 120k annual invoice and EUR 5.7k professional services' and "
    "'Gringotts annual invoice: The EUR 120k October invoice inflates reported revenue. Use MRR "
    "for trend analysis.'",
    "Identified, excluded, and the exclusion stated as the basis for the trend. No monthly "
    "equivalent.")
add("deepseek-v4-flash", 5, "headline_vs_recurring_growth", P,
    "the three-row table: invoiced EUR 797.1k -> EUR 873.4k (+9.6%), MRR from plans EUR 746.1k -> "
    "EUR 757.7k (+1.6%), active MRR end of month EUR 746.1k -> ~EUR 732.4k (-1.8%)",
    "Three bases, each labelled with what it includes, every figure exact, and the sign flips "
    "between the first and the third.")
add("deepseek-v4-flash", 5, "revenue_conclusion", P,
    "'Headline revenue is misleading' as the first line of the summary",
    "Carried to leadership with the figures behind it.")
add("deepseek-v4-flash", 5, "segment_retention_quantified", T,
    "'4 of 13 SMB customers churned in October' and the active-MRR walk by segment",
    "A rate is finally computed, but on the wrong population: 13 is the Starter plan count, not "
    "the SMB segment, which has 18. The segments are ranked on net MRR movement rather than on "
    "retention.")
add("deepseek-v4-flash", 5, "sample_size_arr_context", P,
    "'SMB is barely growing despite adding 5 new logos, because 4 Starter customers churned' "
    "with SMB active MRR EUR 39.1k -> EUR 39.9k",
    "Sizes the churn against what replaced it and gives the net, so the four-logo count is never "
    "left to speak for itself.")
add("deepseek-v4-flash", 5, "acme_false_positive_avoided", P,
    "'Requests fell 45%, but tokens fell only 12% and active users fell only 3%, consistent with "
    "the move to scheduled batch workloads' plus tokens per request 1,100 -> 1,760",
    "Three corroborating metrics and a derived ratio that demonstrates the point rather than "
    "asserting it.")
add("deepseek-v4-flash", 5, "no_churn_overreach", P,
    "Soylent is called 'a clear account-health concern' with its three movements listed and no "
    "reason attached",
    "Claims no cause the pack does not record.")
add("deepseek-v4-flash", 5, "raw_attribution_not_equivalent_new_business", P,
    "'EUR 174k of EUR 238.8k came from expansions to existing Enterprise accounts: Stark "
    "Industries, Umbrella Health, and Globex. Only EUR 64.8k came from new logos.'",
    "Quantified to the euro, accounts named, and the conclusion drawn - paid search is an "
    "expansion channel.")
add("deepseek-v4-flash", 5, "existing_customer_expansion_removed", T,
    "the attributed table carries new-logo and expansion counts per channel, and paid search's "
    "EUR 64.8k new-logo figure is given, but no new-logo ARR is computed for content, partner or "
    "outbound",
    "The correction is made for the channel it matters most for, then the ranking is redone on "
    "logo count rather than new-logo value - which is why content (3 logos, EUR 91.2k) is "
    "preferred to partner (2 logos, EUR 166.8k).")
add("deepseek-v4-flash", 5, "conversion_rate_vs_absolute_volume", P,
    "the two-month table pairing leads with trial conversion rate for every channel: paid search "
    "520 / 8.5% -> 900 / 6.4%",
    "Rising volume and falling rate set side by side for all four channels, every figure exact.")
add("deepseek-v4-flash", 5, "no_unsupported_channel_scale_decision", P,
    "'Before scaling, finance should provide channel cost data so CAC payback can actually be "
    "calculated'",
    "The one spend increase it proposes is gated on the missing cost data.")
add("deepseek-v4-flash", 5, "cac_payback_unavailable", P,
    "'The pack contains no acquisition spend, cost per lead, or cost per conversion by channel. "
    "Attributed revenue is also annualised contract value at conversion, not cash received.'",
    "Refused, and it names a second reason the answer key does not: the attributed figure is not "
    "cash.")
add("deepseek-v4-flash", 5, "contribution_calculated", P,
    "the two monthly tables with customer counts, revenue, infra, support, contribution, margin "
    "and contribution per customer",
    "All twelve figures exact, plus correct contribution per customer.")
add("deepseek-v4-flash", 5, "margin_calculated_or_correctly_compared", P,
    "32.2% / 67.5% / 34.9% and 29.5% / 62.7% / 32.2%",
    "All six correct.")
add("deepseek-v4-flash", 5, "absolute_vs_scalable_economics", P,
    "'Enterprise is the profit engine but is deteriorating' against 'Pro has the best margin by "
    "far (~63%)' and 'Starter is the weakest after cost'",
    "Distinguishes the largest pool from the best economics and keeps them apart throughout.")
add("deepseek-v4-flash", 5, "plan_trajectory_evidence", F,
    "'No plan is currently exceeding its included request allowance, so overage revenue is not "
    "masking these economics.'",
    "True of the three plan averages and false of the customers: Stark 4.29M and Wayne 3.41M "
    "exceed the 3M enterprise allowance, and Wonka 1.02M, Aperture 705k and Vandelay 690k exceed "
    "Pro's 600k. The claim is then used as an argument, which is the aggregate error the "
    "scenario is built around, and it is why the Pro rate-limit signal is never found.")
add("deepseek-v4-flash", 5, "product_focus_supported", P,
    "'Give the Starter plan the next quarter's engineering focus. It is the weakest plan after "
    "cost: lowest contribution per customer, high churn, and disproportionate support load.' "
    "with 'A secondary focus should be Enterprise cost efficiency'",
    "The criterion admits a plan other than Pro when the case is argued on cost-adjusted "
    "economics with at least two independent signals and does not rest on absolute revenue. "
    "Contribution per customer, churn and support load are three, all cost-adjusted, and "
    "absolute revenue is never invoked. That it never found Pro's over-allowance accounts is "
    "charged under plan_trajectory_evidence, not twice here.")
add("deepseek-v4-flash", 5, "customer_id_alias_resolved", P,
    "'Usage account IDs differ from customer IDs for some accounts (e.g., wayne_ent, "
    "prestige_ww), so joins must use usage_account_id'",
    "Both aliases named and the join rule stated - the most explicit treatment in the battery.")
add("deepseek-v4-flash", 5, "support_normalized", P,
    "'SMB has the highest support tickets per EUR 100k MRR' and, for Starter, 'support load is "
    "high relative to revenue'",
    "Normalises against a stated denominator and compares across segments rather than reasoning "
    "from a raw count.")
add("deepseek-v4-flash", 5, "figures_carried_correctly", T,
    "checked against the CSVs: both revenue bases, the segment and plan MRR walks, total requests "
    "31.0M -> 31.5M, requests excluding Acme 26.8M -> 29.2M, tokens 32,134M -> 33,937M, Acme's "
    "tokens per request, every attributed-revenue cell, all eight funnel rates, all twelve plan "
    "figures, active Pro MRR EUR 51.2k, active Starter EUR 21.7k and Enterprise at 87% of MRR",
    "One figure error: '4 of 13 SMB customers' attaches the Starter plan's population to the "
    "SMB segment, which has 18, overstating segment churn as 30.8% against 22.2%. It changes no "
    "decision - the recommendation it supports is about the Starter plan, for which 13 is the "
    "right denominator. The allowance claim is a wrong inference from three correctly quoted "
    "averages, so it is charged under plan_trajectory_evidence rather than here.")
add("deepseek-v4-flash", 5, "cross_table_customer_signal", P,
    "'Soylent is a clear account-health concern: MRR fell from EUR 22k to EUR 19.5k. Usage fell "
    "27%. It generated 8 support tickets in October, including one critical'",
    "Revenue, usage and support on one account, every figure correct.")
add("deepseek-v4-flash", 5, "causal_boundary", P,
    "the Soylent trio reported together with no mechanism asserted, and 'Soylent's September "
    "invoice (EUR 22k) does not match its current ARR ... This suggests a contract change that is "
    "not explicitly recorded'",
    "Assembles the pattern, flags a second unexplained discrepancy, and stops short of "
    "explaining either.")
add("deepseek-v4-flash", 5, "segment_recommendation", F,
    "'Reduce investment in the SMB segment, specifically the Starter plan. The data supports "
    "this: 4 of 13 SMB customers churned in October ... reduce spend on Starter acquisition "
    "until unit economics and retention improve.'",
    "Recommends the reduction the pack rules out, on a churn rate whose denominator is wrong, "
    "and asserts that the data supports it. Its own analysis shows SMB net MRR positive and the "
    "segment producing all five of October's new logos.")
add("deepseek-v4-flash", 5, "acquisition_recommendation", P,
    "'Increase spend on the content channel ... Paid search should be treated as an expansion "
    "channel, not the primary new-customer channel. Before scaling, finance should provide "
    "channel cost data.'",
    "Rejects paid search for the right reason, gates the spend on the cost gap, and gives a "
    "defensible reason for preferring content to partner - partner produced no October "
    "conversions at all, which it states.")
add("deepseek-v4-flash", 5, "product_recommendation", P,
    "'Give the Starter plan the next quarter's engineering focus'",
    "Single, actionable and consistent with its own section 4. Whether it is the right plan is "
    "priced under product_focus_supported.")
add("deepseek-v4-flash", 5, "uncertainty_discipline", P,
    "eight items including the alias discovery, plans.csv counting churned customers, the funnel "
    "measuring trial starts, and Soylent's invoice not matching its recorded ARR",
    "Every gap real, two of them beyond the answer key, and nothing invented.")

PENALTIES[("deepseek-v4-flash", 5)] = [{
    "type": "PROHIBITED_ACTION",
    "evidence": "'Reduce investment in the SMB segment, specifically the Starter plan. The data "
                "supports this: 4 of 13 SMB customers churned in October ... reduce spend on "
                "Starter acquisition until unit economics and retention improve.'",
    "reason": "Defunding part of SMB on a logo churn rate is the first action the pack rules "
              "out, and this states that the data supports it. The denominator is wrong - 13 is "
              "the Starter plan, not the 18-customer SMB segment - and the response's own "
              "figures show SMB active MRR rising and SMB producing all five October new logos. "
              "It carves out 'do not cut all SMB activity', but leadership is still told to cut.",
}]

# --- run-006 -------------------------------------------------------------
add("deepseek-v4-flash", 6, "duplicate_detected", P,
    "'October unique revenue: EUR 873.4k (or EUR 892.9k if the duplicate Soylent invoice is "
    "double-counted)' and 'INV-2026-10-0209 ... appears in both stripe and billing_sync. I "
    "treated it as one invoice.'",
    "Identified by id, both totals given so the reader can see the size of the error, and the "
    "deduplicated one used.")
add("deepseek-v4-flash", 6, "annual_prepayment_normalized", P,
    "'Gringotts annual invoice: EUR 120k is recorded in full in October revenue, but its monthly "
    "run-rate is EUR 10k. October revenue is not comparable to September revenue.'",
    "Invoice, monthly equivalent and timing effect all three stated.")
add("deepseek-v4-flash", 6, "headline_vs_recurring_growth", P,
    "September total EUR 797.1k against October unique EUR 873.4k, and the MRR table giving "
    "EUR 746,100 -> EUR 757,700 reported -> EUR 732,400 ongoing",
    "Three bases, each labelled, every figure exact, and the EUR 25.3k of invoices to churned "
    "customers identified as what separates the last two.")
add("deepseek-v4-flash", 6, "revenue_conclusion", P,
    "'Headline MRR looks up, but the real run-rate is down' as the first line",
    "Opens the brief and drives the segment view beneath it.")
add("deepseek-v4-flash", 6, "segment_retention_quantified", T,
    "the segment MRR table with Enterprise EUR 0, Mid-market -EUR 14,500, SMB +EUR 800, plus "
    "'net revenue retention is roughly 100.1%' and 'Highest logo churn: 4 of 13 SMB customers'",
    "Computes NRR on continuing customers - EUR 720.8k to EUR 721.3k, internally consistent - but "
    "for the company rather than per segment, and the one segment churn rate it gives uses the "
    "Starter plan's 13 as the SMB denominator.")
add("deepseek-v4-flash", 6, "sample_size_arr_context", P,
    "'Churned ARR: EUR 303.6k ... New logo ARR in October: EUR 133.2k' and 'Lowest ARR per "
    "customer: EUR 34.2k vs Mid-market EUR 170k and Enterprise EUR 847.5k'",
    "Sizes the churn, nets it, and puts SMB's per-customer ARR beside the other two segments so "
    "the four-logo count is never read alone.")
add("deepseek-v4-flash", 6, "acme_false_positive_avoided", P,
    "'Acme: requests -45%, tokens -12%, active users -3%. This matches the batch-migration plan, "
    "not churn.' and, in the uncertainties, 'should not be treated as churn or product failure'",
    "Three metrics against the stated migration, and the conclusion repeated where it matters.")
add("deepseek-v4-flash", 6, "no_churn_overreach", P,
    "'All five churned customers had declining usage in their final month, so usage decline is a "
    "leading indicator.'",
    "States the pattern as a predictor rather than a cause, and offers no reason for the churn "
    "itself.")
add("deepseek-v4-flash", 6, "raw_attribution_not_equivalent_new_business", P,
    "'Paid search is the largest channel and the only one with multiple high-value expansions "
    "(Stark, Umbrella, Globex, Hooli). But those October expansions are not yet in current "
    "ARR/revenue' with new-logo and expansion counts per channel",
    "All four expanding accounts named - the only run in the battery to include Hooli - and the "
    "booking-timing caveat added.")
add("deepseek-v4-flash", 6, "existing_customer_expansion_removed", F,
    "the channel table gives new-logo and expansion counts but only total attributed revenue: "
    "paid search EUR 274,800, partner EUR 166,800, content EUR 109,200, outbound EUR 80,400",
    "Having identified the contamination it never removes it, so no new-logo ARR is computed for "
    "any channel and the ranking never reverses - which is how it ends up naming paid search as "
    "the best candidate for a test.")
add("deepseek-v4-flash", 6, "conversion_rate_vs_absolute_volume", P,
    "'Paid search leads grew 73%, but trial conversions only grew 32%, suggesting declining "
    "marginal efficiency'",
    "Both movements quantified against each other, and the funnel table shows the numerator and "
    "denominator for every cell.")
add("deepseek-v4-flash", 6, "no_unsupported_channel_scale_decision", P,
    "'Do not increase spend yet. The data cannot support a CAC payback decision.' and 'no "
    "acquisition channel increase is fully supported by the data'",
    "Refuses outright and says why.")
add("deepseek-v4-flash", 6, "cac_payback_unavailable", P,
    "'CAC payback by acquisition channel cannot be calculated from this pack' followed by the "
    "three inputs it would need",
    "Refused, with a concrete list of what would change the answer.")
add("deepseek-v4-flash", 6, "contribution_calculated", P,
    "the six-row plan table with revenue, infra, support, contribution and margin",
    "All twelve figures exact.")
add("deepseek-v4-flash", 6, "margin_calculated_or_correctly_compared", P,
    "32.2% / 29.5% / 67.5% / 62.7% / 34.9% / 32.2%, plus 'costs are now 70.5% of revenue'",
    "All correct, and the cost ratio checks out at 464.8/659.5.")
add("deepseek-v4-flash", 6, "absolute_vs_scalable_economics", P,
    "'Enterprise is the weakest after cost' against 'Pro is the strongest', with 'A 10% reduction "
    "in Enterprise infra + support costs would add roughly EUR 46.5k/month - more than Pro's "
    "entire monthly contribution'",
    "Distinguishes the two and then quantifies exactly what the absolute size is worth, which is "
    "the strongest treatment of this criterion anywhere in the battery.")
add("deepseek-v4-flash", 6, "plan_trajectory_evidence", P,
    "'All plans are below included request volume on average, but some customers exceed it - "
    "Stark, Wayne, Aperture, Vandelay, and Wonka - so overage revenue at renewal is possible but "
    "not quantified.'",
    "States the average and then refuses to reason from it, naming all five accounts above their "
    "allowance. This is the exact sentence the aggregate trap is built to catch.")
add("deepseek-v4-flash", 6, "product_focus_supported", P,
    "'Focus on the Enterprise plan ... A 10% reduction in Enterprise infra + support costs would "
    "add roughly EUR 46.5k/month - more than Pro's entire monthly contribution. Address Pro rate "
    "limits as a secondary priority.'",
    "A plan other than Pro, and the case rests on a quantified cost-efficiency opportunity "
    "rather than on the size of the revenue - with Pro kept as an explicit secondary for the "
    "right reason.")
add("deepseek-v4-flash", 6, "customer_id_alias_resolved", P,
    "'Usage account mapping matters: Wayne Enterprises uses wayne_ent; Prestige Worldwide uses "
    "prestige_ww' and Wayne appears correctly among the over-allowance accounts",
    "Both aliases named and the join actually performed.")
add("deepseek-v4-flash", 6, "support_normalized", P,
    "'Only EUR 1.5k MRR per support ticket in October, vs EUR 22.6k for Enterprise'",
    "Normalises on revenue per ticket and compares across segments; both figures check out "
    "against the ticket counts.")
add("deepseek-v4-flash", 6, "figures_carried_correctly", T,
    "checked against the CSVs: both revenue totals, the full MRR and segment walks, the EUR 25.3k "
    "of churned-customer invoices, churned and new-logo ARR, NRR at 100.1%, Acme's three "
    "movements, Soylent's three, all four attributed-revenue totals, all eight funnel cells with "
    "their numerators, all twelve plan figures, the 70.5% cost ratio and the EUR 46.5k opportunity",
    "One figure error: '4 of 13 SMB customers' uses the Starter plan's population for the SMB "
    "segment. It changes no decision - SMB is the highest-churn segment on the correct 4-of-18 "
    "denominator too - and every other checkable figure in a long response is exact.")
add("deepseek-v4-flash", 6, "cross_table_customer_signal", P,
    "'Soylent: requests -27%, MRR -11%, and 8 support tickets in October including a critical API "
    "error. This is a real health risk.'",
    "Usage, revenue and support on one account, every figure correct, and Acme handled the same "
    "way.")
add("deepseek-v4-flash", 6, "causal_boundary", P,
    "the Soylent trio reported together as 'a real health risk' with no mechanism, and usage "
    "decline framed as 'a leading indicator' rather than a cause",
    "Assembles the pattern and keeps the claim predictive rather than causal.")
add("deepseek-v4-flash", 6, "segment_recommendation", T,
    "'Reallocate or reduce SMB acquisition/support investment until unit economics improve. "
    "However, no segment-level spend data is provided, so validate before cutting.' with 'Do not "
    "reduce Enterprise investment' and 'Mid-market should not be cut; it needs retention focus'",
    "Names the data gap the criterion asks for and gates the action on validating it, which is "
    "most of the right answer, and it handles the other two segments correctly. It still lands "
    "on reduce, and the SMB churn rate behind it uses the wrong denominator.")
add("deepseek-v4-flash", 6, "acquisition_recommendation", F,
    "'If a controlled test is required, paid search is the best candidate because it drove the "
    "most attributed revenue and the only high-value expansions.'",
    "Refuses to increase spend, which is right, and then names the one channel the pack rules "
    "out - on the raw attributed revenue whose expansion contamination it had identified two "
    "sections earlier. Never having computed new-logo ARR by channel is what leaves it there.")
add("deepseek-v4-flash", 6, "product_recommendation", P,
    "'Focus on the Enterprise plan' with Pro rate limits as the stated secondary",
    "A single primary recommendation, actionable, consistent with its own section 4.")
add("deepseek-v4-flash", 6, "uncertainty_discipline", P,
    "nine items including the alias mapping, costs being available by plan rather than segment, "
    "the funnel measuring trial starts, and expansion attribution being forward-looking",
    "Every gap real, several beyond the answer key, nothing invented.")


# =========================================================================
# GLM 5.3 Flash
# =========================================================================
# The strongest pair in the battery so far. Both runs find every trap, and
# both reconcile their own figures against each other - run-003 checks Hooli's
# EUR 36k expansion booking against the +EUR 3,000 that shows up on its invoice,
# run-004 derives the same active-MRR figure two independent ways. The two runs
# differ on which segment basis they use, and both are right: run-003 quotes
# SMB 4 of 18 on the closing population, run-004 quotes 4 of 13 on the opening
# one (18 less the 5 October logos), with ARR bases to match.

# --- run-003 -------------------------------------------------------------
add("glm5.3-flash", 3, "duplicate_detected", P,
    "'INV-2026-10-0209 (soylent EUR 19,500) appears twice - stripe (Oct 1) and billing_sync "
    "(Oct 2), same transaction ID. Naive October totals are overstated by EUR 19.5k (+2.2%). "
    "Dedupe on transaction_id; audit the billing_sync pipeline.'",
    "Identified by id, both sources and both dates, quantified as a share, excluded from the "
    "EUR 873.4k it reports, and followed by the operational fix.")
add("glm5.3-flash", 3, "annual_prepayment_normalized", P,
    "'treating gringotts EUR 120,000 annual prepayment at its EUR 10,000/month equivalent' and "
    "'monthly equivalent EUR 10k ... +EUR 110k optical'",
    "Invoice, monthly equivalent and the size of the distortion, all three.")
add("glm5.3-flash", 3, "headline_vs_recurring_growth", P,
    "'Naively summed, October invoices show ~+12% MoM growth ... underlying subscription revenue "
    "grew only +1.6% MoM (EUR 746.1k -> EUR 757.7k)', with the gap decomposed into the annual "
    "invoice, the duplicate and EUR 25.3k of advance billing to churned customers",
    "Both figures, both bases named, and the MRR bridge is built from its parts: +EUR 11.1k new "
    "logos + EUR 3.0k hooli - EUR 2.5k soylent = +EUR 11.6k, which reconciles exactly.")
add("glm5.3-flash", 3, "revenue_conclusion", P,
    "'Headline October revenue is overstated' as the first line of the executive summary, and "
    "'restate October as +1.6%, not +9.6%' as a recommendation to leadership",
    "The conclusion opens the brief and is turned into an instruction.")
add("glm5.3-flash", 3, "segment_retention_quantified", P,
    "'SMB: 4 of 18 logos (22% of segment count), EUR 123.6k = 20.5% of opening SMB ARR. "
    "Mid-market: nakatomi, EUR 180k (10.5% of segment). Enterprise: zero.'",
    "Logo churn and ARR churn for all three segments on the canonical denominators, correctly "
    "labelled as segment, correctly ranked, and used consistently afterwards.")
add("glm5.3-flash", 3, "sample_size_arr_context", P,
    "'SMB is simultaneously the biggest churn source and the only logo engine (8 of 9 new logos; "
    "net SMB ARR +EUR 123.6k over two months)' and 'that is n=2 adverse events against a EUR 132k "
    "win' for Mid-market",
    "Sizes the churn, nets it against new business, and names the sample size of the comparison "
    "it declines to act on. Every figure exact.")
add("glm5.3-flash", 3, "acme_false_positive_avoided", P,
    "'Acme's -45% request drop is not a problem - it is the documented batch migration (40-50% "
    "reduction was the plan estimate; tokens fell only -12%)' plus 'post-migration tickets "
    "dropped from 4 (2 high-sev) to 3 (all low/medium)'",
    "The migration, the token figure and the ticket trajectory - three signals, all exact.")
add("glm5.3-flash", 3, "no_churn_overreach", P,
    "'with only 2 months we cannot establish lead time - this is a pattern to monitor, not a "
    "validated predictor'",
    "Reports the usage-decline signature and explicitly refuses to promote it to a cause.")
add("glm5.3-flash", 3, "raw_attribution_not_equivalent_new_business", P,
    "'Paid_search's total attributed revenue is EUR 274.8k - but EUR 210k (76%) is expansion "
    "credit (stark EUR 84k, umbrella EUR 48k, globex EUR 42k, hooli EUR 36k)'",
    "Split, share and all four accounts, with the causal objection stated: 2023/24-vintage "
    "accounts credited to a campaign that started six days earlier.")
add("glm5.3-flash", 3, "existing_customer_expansion_removed", P,
    "'Partner: EUR 166.8k from 2 logos (avg EUR 83.4k) ... Content: EUR 91.2k from 3 ... "
    "paid_search: EUR 64.8k from 2 ... Outbound: EUR 56.4k from 2'",
    "Every figure exact and the ranking reversed against attributed revenue.")
add("glm5.3-flash", 3, "conversion_rate_vs_absolute_volume", P,
    "the funnel table pairing leads and trials for both months - paid_search 520 -> 900 (+73%) "
    "against 44 -> 58 (+32%), trial rate 8.5% -> 6.4%",
    "Both movements for every channel, with numerator and denominator shown so the divergence is "
    "visible rather than asserted.")
add("glm5.3-flash", 3, "no_unsupported_channel_scale_decision", P,
    "'do not increase paid_search spend yet ... First request channel spend for Sept-Oct and "
    "cohort trial-to-paid tracking; then compute CAC and payback properly'",
    "Declines and names both missing inputs.")
add("glm5.3-flash", 3, "cac_payback_unavailable", P,
    "'cannot be produced. Required inputs not in the pack: media spend by channel, sales/CS cost "
    "allocation, and cohort trial-to-paid conversion. Payback = CAC / (new-logo ARR x gross "
    "margin / 12); we have only the denominator's ingredients.'",
    "Refuses, names what is missing, and writes out the formula to show exactly which half of it "
    "the pack supports.")
add("glm5.3-flash", 3, "contribution_calculated", P,
    "EUR 194,700 / EUR 41,500 / EUR 10,300 with a EUR 246,500 total row",
    "All exact, including the blended total.")
add("glm5.3-flash", 3, "margin_calculated_or_correctly_compared", P,
    "'32.2% -> 29.5%', '67.5% -> 62.7%', '34.9% -> 32.2%' and total '35.2% -> 32.5%'",
    "All correct, both months, plus the blended movement.")
add("glm5.3-flash", 3, "absolute_vs_scalable_economics", P,
    "'Enterprise is the whole story: 87% of MRR' against 'Pro is the best economic engine: 62.7% "
    "margin, ~EUR 4,611 profit/customer vs EUR 13,907 (enterprise) and EUR 792 (starter)', and "
    "'Every point of enterprise margin ~ EUR 6.6k/month'",
    "Holds both halves, quantifies what the absolute size is worth per margin point, and sends "
    "the two to different workstreams rather than collapsing them.")
add("glm5.3-flash", 3, "plan_trajectory_evidence", P,
    "'wonka (1.02M requests vs 600k included, +13.3% usage), aperture (705k) and vandelay (690k) "
    "all exceed included volume' and, for enterprise, 'overage mix shifts to stark (1.29M) and "
    "wayne (0.41M)'",
    "Reads the distribution against the allowance account by account for both plans, and notes "
    "Starter's 84k average against a 200k allowance as the reason there is no upside there.")
add("glm5.3-flash", 3, "product_focus_supported", P,
    "'the enterprise plan - defend it. It carries 87% of revenue, its margin is eroding, its "
    "churn events are the ones that hurt (nakatomi EUR 180k), and the churn/downgrade cases are "
    "tied to api_errors/performance - engineering-addressable issues. Pro is the clear secondary'",
    "A plan other than Pro, and the case is built on margin erosion, an engineering-addressable "
    "failure category and the cost of the churn events - not on the size of the revenue, which is "
    "cited as context rather than as the argument. Pro is kept as an explicit secondary with its "
    "own three signals.")
add("glm5.3-flash", 3, "customer_id_alias_resolved", P,
    "'wayne (0.41M)' in the enterprise overage list and 'wayne (EUR 1.008M - renews 2026-11-30)' "
    "in the save list",
    "Wayne's usage is reported correctly against its billing record and its renewal date, which "
    "requires the alias.")
add("glm5.3-flash", 3, "support_normalized", P,
    "'support alone costs EUR 792/customer/month vs EUR 2,462 ARPU (32%)' for starter, and "
    "'Support is now 25.5% of enterprise revenue'",
    "Normalises support cost against both customers and revenue, and Enterprise is treated as a "
    "cost-and-reliability problem rather than the worst experience by raw count.")
add("glm5.3-flash", 3, "figures_carried_correctly", T,
    "'wonka ... 7 tickets in October - 5 of them rate_limits' when 4 of the 7 are rate_limits; "
    "and 'wayne renews in ~5 weeks' when 2026-11-30 is four weeks after the review date",
    "Two small slips in supporting detail. Everything else checkable is exact, including the "
    "EUR 262.9k -> EUR 246.5k profit walk, the +5.8% cost growth, the MRR bridge, the EUR 216k "
    "expansion bookings itemised, the EUR 3.23M of ARR with open high-severity tickets, all "
    "eight funnel cells, the full new-logo table, all twelve plan figures, contribution per "
    "customer for all three plans, and the mid-market -EUR 42k walk.")
add("glm5.3-flash", 3, "cross_table_customer_signal", P,
    "'soylent (EUR 234k, mid-market/enterprise plan) - usage -27%, the pack's only critical "
    "ticket, 8 tickets in October (most of any customer), and an 11.4% price downgrade already "
    "taken'",
    "Four tables on one account with every figure correct, and Acme and Wonka assembled the same "
    "way.")
add("glm5.3-flash", 3, "causal_boundary", P,
    "the Soylent trio reported together as 'the nakatomi playbook repeating', with 'soylent's "
    "invoice cut (22,000 -> 19,500) has no recorded cause (downgrade vs credits vs correction) - "
    "don't assume'",
    "Assembles the pattern, escalates it, and states in terms that the pack does not record what "
    "caused it.")
add("glm5.3-flash", 3, "segment_recommendation", P,
    "'do not cut a segment this week ... Cutting SMB is contradicted by the data: it supplies 8 "
    "of 9 new logos and grew net +EUR 123.6k over two months' with '(d) revisit with cohort data "
    "in Q1' and 'Revisit with CAC/LTV data'",
    "Refuses the cut on quantified grounds, gives three concrete next steps, and names the "
    "missing inputs - CAC and LTV - that would settle it.")
add("glm5.3-flash", 3, "acquisition_recommendation", P,
    "'Modest exploration of partner scale-up is the better-quality bet, contingent on partner "
    "capacity' and 'First request channel spend for Sept-Oct'",
    "Names partner on the corrected new-logo basis and conditions the spend on both the missing "
    "cost data and an unknown it identifies itself.")
add("glm5.3-flash", 3, "product_recommendation", P,
    "'Decision 3 - Plan focus: enterprise reliability first, pro upgrade path second'",
    "Single, actionable, and consistent with its own section 4.")
add("glm5.3-flash", 3, "uncertainty_discipline", P,
    "eight items including the missing spend data, the trial-vs-customer funnel definition, "
    "plans.csv counting mid-month churners, arr_eur for churned rows, and support data having no "
    "timestamps so SLA metrics cannot be computed",
    "Every gap real, several beyond the answer key, and no invented figures anywhere.")

# --- run-004 -------------------------------------------------------------
add("glm5.3-flash", 4, "duplicate_detected", P,
    "'INV-2026-10-0209 (soylent, EUR 19,500) appears twice (stripe 1 Oct; billing_sync 2 Oct, "
    "same ID/amount). Naive sums overstate October by EUR 19,500.'",
    "Identified by id, both sources and dates, and excluded from the EUR 873.4k it reports.")
add("glm5.3-flash", 4, "annual_prepayment_normalized", P,
    "'Gringotts annual EUR 120,000 (EUR 10,000/mo equivalent -> +EUR 110k optical)'",
    "Invoice, monthly equivalent and the size of the optical effect.")
add("glm5.3-flash", 4, "headline_vs_recurring_growth", P,
    "the three-row reconciliation: invoiced EUR 797,100 -> EUR 873,400 (+9.6%), MRR EUR 746,100 -> "
    "EUR 757,700 (+1.6%), go-forward MRR EUR 746,100 -> EUR 732,400 (-1.8%)",
    "Three bases, each labelled with exactly what it contains, and the components of the gap "
    "itemised: EUR 110k of annual invoice, EUR 19.5k duplicate, EUR 25.3k advance-billed to "
    "churners.")
add("glm5.3-flash", 4, "revenue_conclusion", P,
    "'The headline revenue growth is an illusion' as the first line",
    "Opens the brief and drives the November outlook beneath it.")
add("glm5.3-flash", 4, "segment_retention_quantified", P,
    "'Enterprise 0 / 8 (0%) EUR 0; Mid-market 1 / 10 (nakatomi) EUR 180k (10.5%); SMB 4 / 13 "
    "(30.8%) EUR 123.6k (26.3% of opening SMB ARR)'",
    "An opening-cohort basis, applied consistently: SMB's opening population is 18 less the five "
    "October logos, and its opening ARR is EUR 469.2k, so 4/13 and 26.3% are both correct and "
    "internally consistent. Mid-market is on the same basis. The ranking is right and the "
    "criterion's stated 20-26% ARR band anticipates this reading.")
add("glm5.3-flash", 4, "sample_size_arr_context", P,
    "'SMB is 5.4% of ARR with 31% monthly logo churn - but it produced 8 of 9 new logos and was "
    "net ARR-positive in October (+EUR 9.6k = +EUR 133.2k new - EUR 123.6k churned). Mid-market "
    "was actually net-negative (-EUR 30k) after nakatomi - one large churn can flip the picture'",
    "Denominator, ARR share and the Mid-market comparison, all exact, and the point about sample "
    "size is made as an argument rather than as a caveat.")
add("glm5.3-flash", 4, "acme_false_positive_avoided", P,
    "'Acme's -45% request drop is explained, not a demand problem: the batch migration estimated "
    "a 40-50% interactive reduction; tokens fell only -12%'",
    "Migration plus tokens, and it goes further than any other run in the battery by noting that "
    "Acme moved from 1.2M requests over its allowance to 690k under it, making the February "
    "renewal a real but unsizeable risk.")
add("glm5.3-flash", 4, "no_churn_overreach", P,
    "'Precursor pattern: every churned account's requests fell -34.7% to -37.1% (SMB) and -16.1% "
    "(nakatomi) in its final month; nakatomi churned with an open high-severity api_errors "
    "ticket.'",
    "Reports the co-occurrence with exact figures and never converts it into a reason for the "
    "churn.")
add("glm5.3-flash", 4, "raw_attribution_not_equivalent_new_business", P,
    "'83% of expansion ARR (EUR 210k) is credited to paid_search - these are existing customers; "
    "last-touch credit to ads is not evidence of incremental acquisition and must be excluded "
    "from CAC math'",
    "Quantified, and it states the operational consequence: exclude it from the CAC calculation, "
    "which it then repeats in the recommendation as 'new logos only; exclude expansion credits'.")
add("glm5.3-flash", 4, "existing_customer_expansion_removed", P,
    "the channel table's two right-hand columns: new-logo ARR paid_search EUR 64,800 (2), content "
    "EUR 91,200 (3), partner EUR 166,800 (2), outbound EUR 56,400 (2), against expansion ARR "
    "credited of EUR 210,000 / 18,000 / 0 / 24,000",
    "Every figure exact, and the split is carried in the same table as the raw view so the "
    "reversal is visible at a glance.")
add("glm5.3-flash", 4, "conversion_rate_vs_absolute_volume", P,
    "'paid_search is scaling on declining quality: +73% leads, trial rate -210bps; blended funnel "
    "efficiency fell 10.0% -> 8.0% as paid_search's lead share rose 52% -> 60%'",
    "Both movements, plus the mix explanation for why the blended rate fell - the sharpest "
    "treatment of this criterion in the battery, and the lead-share figures are exact.")
add("glm5.3-flash", 4, "no_unsupported_channel_scale_decision", P,
    "'Do not increase paid_search spend on current evidence - volume +73% with trial rate down to "
    "6.4% and zero CAC visibility. Send channel spend for Sept/Oct to Finance this week'",
    "Declines, gives the reason, and names the missing input with a deadline.")
add("glm5.3-flash", 4, "cac_payback_unavailable", P,
    "'CAC, CPL, CAC payback, or channel ROI - no spend data exists anywhere in the pack. The "
    "CFO's payback request is unanswerable until channel spend for Sept/Oct is supplied.'",
    "Refused, with the missing input named and a commitment attached to its arrival.")
add("glm5.3-flash", 4, "contribution_calculated", P,
    "EUR 194,700 / EUR 41,500 / EUR 10,300 with the revenue, infra and support columns behind them",
    "All exact.")
add("glm5.3-flash", 4, "margin_calculated_or_correctly_compared", P,
    "29.5% / 62.7% / 32.2% against September's 32.2% / 67.5% / 34.9%",
    "All six correct.")
add("glm5.3-flash", 4, "absolute_vs_scalable_economics", P,
    "'Enterprise = 87% of MRR and ~79% of gross profit - the business runs on it' against 'Pro is "
    "the margin engine (62.7%)' and 'Starter is the weakest: lowest ARPU (EUR 2,462/mo), support "
    "alone consumes 32% of revenue ... This is a plan-market fit and pricing problem, not a scale "
    "problem'",
    "All three plans held on both dimensions at once, with each routed to the question it answers.")
add("glm5.3-flash", 4, "plan_trajectory_evidence", P,
    "'Over included allowance (Oct): stark 143%, wayne 114% (enterprise); wonka 170%, aperture "
    "118%, vandelay 115% (pro)' and 'Starter ... customers use only ~42% of their included "
    "requests (84,385 avg vs 200,000 included)'",
    "All five over-allowance accounts with their utilisation, and the one plan where the average "
    "is the right statistic is the one where it uses it.")
add("glm5.3-flash", 4, "product_focus_supported", P,
    "'Enterprise gets next quarter's engineering focus - API reliability. api_errors is the top "
    "recurring high-severity category, on the accounts that are 87% of revenue, and fixing it is "
    "also the lever on the support-cost inflation compressing margin. Fast-follow: pro "
    "rate-limit/overage experience'",
    "A plan other than Pro, argued from a recurring engineering-addressable failure category and "
    "from its effect on the margin - both cost-adjusted - with the revenue share as context "
    "rather than as the reason. Pro is an explicit fast-follow with its own accounts named.")
add("glm5.3-flash", 4, "customer_id_alias_resolved", P,
    "'usage_account_id differs from customer_id for two accounts (wayne_ent, prestige_ww) - joins "
    "must use the customers.usage_account_id bridge; support.csv uses customer_id'",
    "Both aliases named, the bridge column identified, and the difference in support.csv's key "
    "noted - the most complete treatment of this criterion anywhere in the battery.")
add("glm5.3-flash", 4, "support_normalized", P,
    "'Support is now 25.5% of enterprise revenue' and, for starter, 'support alone consumes 32% "
    "of revenue'",
    "Normalises support cost against plan revenue for the two plans it draws conclusions about, "
    "and never argues from Enterprise's raw ticket count.")
add("glm5.3-flash", 4, "figures_carried_correctly", T,
    "'rate-limit tickets doubled (5 -> 11)' when the October count is 13; and '5 of 31 logos "
    "churned (16.1%)' uses the closing population as the denominator where the opening 36 gives "
    "13.9%",
    "One wrong count and one unusual-but-stated basis, neither decision-changing. Everything else "
    "checkable is exact: the three-row revenue reconciliation, the EUR 25.3k advance billing, "
    "NRR at 96.7%, the churn table on its opening basis, all five over-allowance utilisations, "
    "the EUR 252k of EUR 631.2k expansion split with 83% to paid_search, lead share 52% -> 60%, "
    "Enterprise at 87% of MRR and 79% of gross profit, support at 25.5% of enterprise revenue, "
    "starter's EUR 792 and EUR 2,462, the EUR 9,092,400 against EUR 8,788,800 ARR gap, and the "
    "November projection of EUR 750,400.")
add("glm5.3-flash", 4, "cross_table_customer_signal", P,
    "'Soylent (EUR 234k ARR) is showing the same signature right now (-27% usage, 8 tickets "
    "including the pack's only critical, invoice already cut -11.4%)'",
    "Usage, support and revenue on one account with every figure correct, and it is framed as the "
    "same pattern the churned account showed.")
add("glm5.3-flash", 4, "causal_boundary", P,
    "the Soylent trio reported together, with 'Soylent's invoice cut (22,000 -> 19,500) has no "
    "recorded cause (downgrade vs credits vs correction) - don't assume'",
    "Assembles the pattern, acts on it, and refuses to say what caused what.")
add("glm5.3-flash", 4, "segment_recommendation", P,
    "'Do not cut SMB this week ... Revisit with CAC/LTV data' with a usage-collapse watchlist, a "
    "soylent save plan and a starter pricing review as the three next steps",
    "Refuses the cut on quantified grounds, gives concrete next steps, and names the missing "
    "inputs that would settle the question.")
add("glm5.3-flash", 4, "acquisition_recommendation", P,
    "'shift incremental budget toward partner (best quality; test whether supply scales) and "
    "content (stable ~11%)' with 'Send channel spend for Sept/Oct to Finance this week to compute "
    "CAC/payback (new logos only; exclude expansion credits)'",
    "Names both channels the corrected view favours and conditions the spend on the cost data, "
    "with the correction it discovered built into the instruction.")
add("glm5.3-flash", 4, "product_recommendation", P,
    "'Plan (Product): Enterprise gets next quarter's engineering focus - API reliability'",
    "Single, actionable, consistent with its own section 4.")
add("glm5.3-flash", 4, "uncertainty_discipline", P,
    "eleven items including right-censoring in the September trial cohort, the support-cost "
    "allocation method being undescribed, whether arr_eur includes overage, and the join-key "
    "fragility",
    "Every gap real, four of them beyond the answer key, and no invented figures.")


# =========================================================================
# GLM 5.2  (two of three - the third run waits for the Helmcode outage to end)
# =========================================================================
# Both runs find the traps and both then recommend defunding SMB Starter, which
# is the action the pack rules out. They differ sharply on arithmetic: run-004's
# channel and churn tables are exact to the euro while its revenue totals carry
# a repeated EUR 700 offset and it states Starter's gross profit per customer in
# the wrong unit.

# --- run-003 -------------------------------------------------------------
add("glm5.2", 3, "duplicate_detected", P,
    "'Soylent has a duplicate October subscription invoice (INV-2026-10-0209 appears in both "
    "stripe and billing_sync). One must be reversed; otherwise October subscription revenue is "
    "overstated by EUR 19,500.'",
    "Identified by id and both sources, quantified, and the correction named.")
add("glm5.2", 3, "annual_prepayment_normalized", P,
    "'the driver is Gringotts annual subscription (EUR 120k) booked on Oct 1. On a "
    "monthly-equivalent basis Gringotts is unchanged (EUR 10k/mo).'",
    "Invoice, monthly equivalent and the conclusion that the jump is a billing-format change.")
add("glm5.2", 3, "headline_vs_recurring_growth", T,
    "'September total invoiced ~ EUR 797k (subscriptions EUR 746k + professional services "
    "EUR 51k) ... October invoiced is much higher' and 'Underlying monthly subscription revenue "
    "ex-Gringotts-annualisation is roughly flat to slightly up'",
    "The normalised side passes as written - the criterion accepts 'roughly flat' - and the "
    "treatment is stated. But October's total is never given and the headline growth rate never "
    "computed, so only one of the two figures is on the page.")
add("glm5.2", 3, "revenue_conclusion", P,
    "'October headline revenue is inflated by a one-off ... Underlying MRR growth is modest' in "
    "the executive summary",
    "The conclusion reaches leadership rather than staying in the workings.")
add("glm5.2", 3, "segment_retention_quantified", P,
    "the segment table: Enterprise EUR 6,780k active / EUR 0 churned / 0%; Mid-market EUR 1,530k "
    "ex-Nakatomi / EUR 180k / 10.5%; SMB EUR 479k / EUR 124k / 20.5%",
    "ARR-weighted churn for all three segments, correctly labelled as segment, correctly ranked, "
    "and every figure exact. The 4-of-14 Starter figure elsewhere is labelled as the Starter "
    "plan, so the two framings are not mixed.")
add("glm5.2", 3, "sample_size_arr_context", P,
    "'SMB 479 active ARR, 124 churned (4 logos)' set beside 'Mid-market 1,530 ex-Nakatomi, 180 "
    "(Nakatomi)' in the same table",
    "The ARR lost is quantified and placed directly against the single Mid-market churn that cost "
    "more, which is the comparison the criterion asks for.")
add("glm5.2", 3, "acme_false_positive_avoided", P,
    "'Acme: requests -45%, but tokens -12% and active_users -3%. Consistent with the operational "
    "note (interactive -> 2 batch runs/day). Not a churn signal.'",
    "Migration plus two corroborating metrics, all exact.")
add("glm5.2", 3, "no_churn_overreach", P,
    "'The September high-severity api_errors/performance tickets were a leading indicator' and "
    "'Ticket patterns preceded churn'",
    "Frames the ticket history as a predictor rather than a cause, and uncertainty 6 adds that "
    "one month of churn is not a trend.")
add("glm5.2", 3, "raw_attribution_not_equivalent_new_business", T,
    "'paid search sourced three large Enterprise expansions (Stark, Umbrella, Globex = EUR 174k "
    "ACV). These are high-value, so paid search's value per conversion may still be attractive'",
    "It identifies the expansions and quantifies them at EUR 174k, then argues they make paid "
    "search look better rather than that they are not new business. The correction is observed "
    "and not applied.")
add("glm5.2", 3, "existing_customer_expansion_removed", F,
    "no new-logo ARR figure for any channel; the acquisition section is the funnel table plus "
    "prose",
    "The ranking is never recomputed on new-logo revenue, so the reversal never appears.")
add("glm5.2", 3, "conversion_rate_vs_absolute_volume", P,
    "the funnel table's last two columns: paid_search Lead delta +73% against Conv delta +32%, "
    "with the rate falling 8.5% -> 6.4%",
    "Both movements, for every channel, in the same row - and the divergence is then named as the "
    "diminishing-returns signal.")
add("glm5.2", 3, "no_unsupported_channel_scale_decision", P,
    "'it is not, by itself, proof that paid search should be cut' and 'Require channel spend data "
    "before any further increase'",
    "This criterion is about not scaling Paid Search on attributed revenue: the broad increase is "
    "refused and the missing input named. That its narrow ABM carve-out still leans on the "
    "expansion attribution is charged under acquisition_recommendation.")
add("glm5.2", 3, "cac_payback_unavailable", P,
    "'CAC payback by channel cannot be calculated. The pack contains leads, trial conversions, "
    "and attributed revenue, but no marketing spend by channel.'",
    "Refused, with the missing input named precisely against what the pack does contain.")
add("glm5.2", 3, "contribution_calculated", P,
    "the six-row plan table: 212 / 194.7 / 42.5 / 41.5 / 8.4 / 10.3",
    "All exact.")
add("glm5.2", 3, "margin_calculated_or_correctly_compared", P,
    "32% / 30% / 67% / 63% / 35% / 32%",
    "Rounded to whole points and every one within the 1-point tolerance.")
add("glm5.2", 3, "absolute_vs_scalable_economics", P,
    "'Pro is the strongest plan: ~63-67% contribution margin ... it deserves product attention "
    "despite being smaller than Enterprise' against 'Enterprise is still the revenue engine, but "
    "support efficiency is moving the wrong way'",
    "Names the trap and steps around it explicitly: smaller plan, better economics, and the "
    "product decision follows the economics rather than the size.")
add("glm5.2", 3, "plan_trajectory_evidence", F,
    "'Utilisation is low across all plans: Enterprise avg ~1.89M vs 3M included (63%); Pro ~0.44M "
    "vs 0.6M (73%); Starter ~0.08-0.11M vs 0.2M (40-55%). Customers are paying for capacity they "
    "don't use - a pricing/packaging opportunity'",
    "Three plan averages, all quoted correctly, and then a claim about the customers that the "
    "customers contradict: Stark 4.29M and Wayne 3.41M are over the 3M enterprise allowance, and "
    "Wonka 1.02M, Aperture 705k and Vandelay 690k are over Pro's 600k. The claim is used as an "
    "argument, which is the FAIL clause as written.")
add("glm5.2", 3, "product_focus_supported", P,
    "'Product plan focus: Pro. Best contribution margin (~63-67%), zero churn, low utilisation "
    "headroom ... a natural upgrade path for at-risk Starter customers'",
    "Pro, with zero churn and the upgrade path as two signals beyond margin. The headroom claim "
    "is the aggregate error and is charged under plan_trajectory_evidence rather than twice.")
add("glm5.2", 3, "customer_id_alias_resolved", T,
    "account-level billing-to-usage joins are performed for Soylent (EUR 234k ARR against usage "
    "-27% and active_users 56 -> 41) and for Acme, but Wayne Enterprises' usage appears nowhere",
    "The FAIL clause applies only when no account-level join is attempted at all, and several "
    "are. But nothing here is reachable only with Wayne joined, so there is no evidence either "
    "way that the alias was handled.")
add("glm5.2", 3, "support_normalized", P,
    "'support cost is ~32% of plan revenue' for Starter and 'Enterprise support cost per customer "
    "is ~EUR 12k/month - the highest in the portfolio'",
    "Two denominators, and Enterprise's standing is argued from cost per customer rather than "
    "from its raw ticket count.")
add("glm5.2", 3, "figures_carried_correctly", T,
    "'4 of ~14 Starter customers churned' where the plan holds 13 in October and 9 in September, "
    "neither of which is 14; and 'Support cost per Starter customer rose from EUR 811 (Sep) to "
    "EUR 792 (Oct)' describes a fall as a rise",
    "Two slips, both hedged or self-corrected in the next clause ('flat per customer'), and "
    "neither changes a decision. Everything else checkable is exact: the segment ARR table, the "
    "EUR 174k expansion, all eight funnel cells, the twelve plan figures, the utilisation "
    "percentages and the EUR 6.8M of Enterprise ARR.")
add("glm5.2", 3, "cross_table_customer_signal", P,
    "'Soylent: requests -27%, active_users -27% (56 -> 41), plus a critical api_errors ticket and "
    "multiple high-severity tickets in October. This is a genuine health risk on a EUR 234k ARR "
    "Mid-market account.'",
    "Usage, support and billing on one account with every figure correct.")
add("glm5.2", 3, "causal_boundary", T,
    "Soylent's usage decline and ticket cluster are reported together and it is called 'a genuine "
    "health risk', but the EUR 22k -> EUR 19.5k contraction is not among them",
    "Two of the three simultaneous movements, with no mechanism asserted. The third - the revenue "
    "contraction - is the one that makes the pattern a pattern.")
add("glm5.2", 3, "segment_recommendation", F,
    "'Decision 1 - Reduce investment in a customer segment: Yes, reduce investment in SMB "
    "Starter ... stop actively acquiring Starter logos'",
    "Recommends defunding part of SMB on churn and plan economics. It is a careful version - the "
    "Starter margin and support load are computed correctly and the rest of SMB is untouched - "
    "but the pack contains no segment-level acquisition cost, and it never says so before acting.")
add("glm5.2", 3, "acquisition_recommendation", F,
    "'increase paid search spend only on the Enterprise-expansion cohort (lookalike/ABM-style)' "
    "on the strength of 'EUR 174k of Enterprise expansion ACV in October, which is high-value'",
    "The one channel the pack rules out, recommended on the raw attributed revenue whose "
    "expansion contamination the response had itself identified. Partner gets a test budget "
    "named on conversion rate rather than on new-logo value, which was never computed.")
add("glm5.2", 3, "product_recommendation", P,
    "'Decision 3 - Product plan focus: Pro'",
    "Single, actionable, consistent with its own section 4.")
add("glm5.2", 3, "uncertainty_discipline", P,
    "ten items including single-touch attribution, one month of churn not being a trend, the "
    "unsplittable reactive-vs-proactive support cost, and the churned Starter accounts spanning "
    "a wide range of start dates rather than one bad cohort",
    "Every gap real, several beyond the answer key, and no invented figures.")

PENALTIES[("glm5.2", 3)] = [{
    "type": "PROHIBITED_ACTION",
    "evidence": "'Decision 1 - Reduce investment in a customer segment: Yes, reduce investment in "
                "SMB Starter ... Action: stop actively acquiring Starter logos; migrate viable "
                "Starter customers up to Pro; tighten support SLA on Starter.'",
    "reason": "Defunding part of SMB on a churn rate is the first action the pack rules out, and "
              "this is an unhedged instruction to stop acquiring. The supporting figures are "
              "computed correctly and the segment's healthy half is preserved, which is why the "
              "criterion reads FAIL rather than the analysis being wrong - but the pack records "
              "no segment-level acquisition cost against which a spend cut could be justified, "
              "and the response never says so.",
}]

# --- run-004 -------------------------------------------------------------
add("glm5.2", 4, "duplicate_detected", P,
    "'Soylent appears twice in October (INV-2026-10-0209 in both stripe and billing_sync). One "
    "must be removed.' with the revenue table carrying it as a EUR 19.5k line that nets to zero",
    "Identified by id and both sources, and excluded from the underlying column.")
add("glm5.2", 4, "annual_prepayment_normalized", P,
    "'Gringotts moved from monthly (EUR 10k/mo) to annual (EUR 120k upfront). This is a "
    "billing-format change, not growth. ARR unchanged.'",
    "Invoice, monthly equivalent, and the right conclusion drawn from the pair.")
add("glm5.2", 4, "headline_vs_recurring_growth", T,
    "the reconciliation table's three columns - September, October reported, October underlying - "
    "with forward MRR of ~EUR 733.1k against September's EUR 746.8k, 'a ~1.8% decline'",
    "One figure of the two: the forward-MRR basis is computed and labelled, and the components of "
    "the distortion are itemised, but October's headline total is left as '~EUR 868.4k' with no "
    "growth rate against September, so the +12% the pack would report is never confronted.")
add("glm5.2", 4, "revenue_conclusion", P,
    "'Headline October revenue looks strong but is misleading' and 'Underlying MRR is actually "
    "declining' as the first two bullets",
    "The conclusion opens the brief and is quantified.")
add("glm5.2", 4, "segment_retention_quantified", T,
    "the churn table placing all five logos with segment, plan, ARR and MRR, plus 'Gross revenue "
    "retention (MRR basis) 96.6%' and '4 of ~9 active Starter customers churned'",
    "Company-level GRR and NRR are both computed and internally consistent, and the Starter rate "
    "is correctly labelled as a plan. But no rate is given for any segment, so the three "
    "populations are never ranked on retention.")
add("glm5.2", 4, "sample_size_arr_context", P,
    "the churn table giving nakatomi EUR 180,000 against the four SMB Starter accounts totalling "
    "EUR 123,600",
    "The ARR lost is itemised and the single Mid-market churn is visibly larger than all four SMB "
    "churns together, which is the comparison the criterion asks for.")
add("glm5.2", 4, "acme_false_positive_avoided", P,
    "'Acme's -45% request drop is explained by the late-September batch migration (operational "
    "note forecast 40-50% reduction). Token volume fell only -12% (4,620 -> 4,066), confirming "
    "the workload moved to fewer, larger batch calls. Revenue unchanged. Not a health issue'",
    "The migration and three further figures, and it adds the observation that the 3M allowance "
    "is now loose against 2.31M of usage.")
add("glm5.2", 4, "no_churn_overreach", T,
    "'Nakatomi churned with an open high-severity api_errors ticket - likely a support-driven "
    "churn.'",
    "Offers a cause the pack does not record. 'Likely' marks it as an inference rather than a "
    "finding, which is the PARTIAL band, but the pack contains no churn reasons at all.")
add("glm5.2", 4, "raw_attribution_not_equivalent_new_business", P,
    "'Paid Search is the primary driver of expansion revenue from existing enterprise customers "
    "(EUR 210k attributed across the two months)' with 'Stark, Umbrella, and Globex are "
    "long-standing enterprise customers (since 2023-2024) attributed to paid_search campaigns "
    "that started 2026-09-28 and converted within days'",
    "Quantified at EUR 210k, singled out to Paid Search, and the causal objection made from the "
    "tenure dates rather than asserted.")
add("glm5.2", 4, "existing_customer_expansion_removed", P,
    "the converted-customers table splitting new logos from expansion by channel and month: "
    "partner EUR 166.8k (vandelay, clampett), content EUR 45.6k + EUR 45.6k, paid_search "
    "EUR 64.8k, outbound EUR 33.6k + EUR 22.8k",
    "Every cell exact, every account named, and the conclusion drawn - 'Partner and Content are "
    "more efficient at new logo acquisition'.")
add("glm5.2", 4, "conversion_rate_vs_absolute_volume", T,
    "the funnel table carries lead counts, conversion rates and lead growth, but no absolute "
    "conversion counts: 'paid_search 520 / 8.5% / 900 / 6.4% / +73%'",
    "The falling rate against rising volume is stated and correct. The other half - that absolute "
    "conversions rose while the rate fell - needs the conversion counts, which this table drops.")
add("glm5.2", 4, "no_unsupported_channel_scale_decision", P,
    "'Do not increase Paid Search spend until (a) channel spend data is available to compute CAC "
    "payback, and (b) expansion attribution is validated. If leadership still wants to scale Paid "
    "Search, run a holdout test on existing customers to isolate causal effect.'",
    "Refuses, names two missing inputs, and proposes the experiment that would settle the causal "
    "question.")
add("glm5.2", 4, "cac_payback_unavailable", P,
    "'Cannot be delivered from this pack. No marketing spend data is provided.' followed by the "
    "file it would need and the formula it would use",
    "Refused, with the missing input named and the deliverable specified.")
add("glm5.2", 4, "contribution_calculated", P,
    "the October table: EUR 194,700 / EUR 41,500 / EUR 10,300 with GP per customer beside them",
    "All exact, and the month-over-month drift table adds September correctly.")
add("glm5.2", 4, "margin_calculated_or_correctly_compared", P,
    "29.5% / 62.7% / 32.2% and the drift table's 32.1% -> 29.5%, 67.5% -> 62.7%, 34.9% -> 32.2%",
    "All correct within tolerance.")
add("glm5.2", 4, "absolute_vs_scalable_economics", P,
    "'Enterprise is the strongest plan in absolute GP (~79% of total GP) but the weakest in "
    "trend' against 'Pro is the strongest plan on margin and unit economics trend'",
    "Both halves held, each labelled with the question it answers, and the cost base quantified "
    "per customer on both sides.")
add("glm5.2", 4, "plan_trajectory_evidence", P,
    "'Pro ... the only plan where usage is approaching the included allowance (74%), suggesting "
    "pricing is better calibrated' and 'Wonka, Vandelay, Aperture are all hitting rate_limits' "
    "with 'Wonka Industries ... usage is 1.02M requests vs 600k included'",
    "Names all three Pro accounts above the allowance and gives Wonka's figure against it, so the "
    "distribution is read rather than only the average - and the average is used where it is the "
    "right statistic.")
add("glm5.2", 4, "product_focus_supported", T,
    "'Decision 3: Which plan deserves engineering focus - Enterprise, for cost reduction; Pro, "
    "for growth enablement.'",
    "Two plans with no choice made between them, which is the PARTIAL band as written. The split "
    "is coherent - cost work to Enterprise, scaling work to Pro - and the Enterprise half is "
    "argued partly from its 79% share of gross profit, which is the absolute figure the rubric "
    "warns against leaning on.")
add("glm5.2", 4, "customer_id_alias_resolved", T,
    "account-level billing-to-usage joins are performed for Soylent, Acme and Wonka, but Wayne "
    "Enterprises' usage appears nowhere in the response",
    "Joins are attempted, so the FAIL clause does not apply, but nothing here is reachable only "
    "with the aliased account included.")
add("glm5.2", 4, "support_normalized", P,
    "'Starter support cost (EUR 10.3k/mo for 13 customers) is disproportionate to revenue "
    "(EUR 32k)' and 'The cost base looks structurally heavy (EUR 21.2k infra + EUR 12k support "
    "per customer)' for Enterprise",
    "Normalises on customers and on revenue, and Enterprise's problem is framed as cost per "
    "customer rather than raw ticket volume.")
add("glm5.2", 4, "figures_carried_correctly", F,
    "'GP per Starter customer is EUR 792/year' - it is EUR 792 per month, and the annual figure "
    "makes the plan look twelve times worse in the argument for cutting it; 'Wonka Industries "
    "generated 7 tickets in October, all rate_limits' when 4 of the 7 are; and the revenue table "
    "carries a repeated EUR 700 offset (September subscriptions EUR 746.8k against EUR 746.1k, "
    "October ~EUR 868.4k against EUR 867.7k, forward MRR EUR 733.1k against EUR 732.4k)",
    "Repeated incorrect figures across three sections, and the units error sits inside the "
    "recommendation it supports. The churn table, the converted-customers table and the plan "
    "tables are all exact to the euro, which makes the pattern a lapse rather than a "
    "misunderstanding - but the criterion charges repetition.")
add("glm5.2", 4, "cross_table_customer_signal", P,
    "'Soylent is the most worrying active account. Usage -27% (980k -> 715k requests), revenue "
    "down, and 8 support tickets in October (vs 3 in September) including a critical api_errors "
    "ticket and two open high-severity tickets. ARR EUR 234k at risk.'",
    "Usage, support and billing on one account, every figure correct, and Wonka assembled the "
    "same way from plan, usage and support.")
add("glm5.2", 4, "causal_boundary", P,
    "all three Soylent movements reported together, with uncertainty 7: 'Soylent revenue change "
    "is unexplained. September invoice was EUR 22k; October is EUR 19.5k ... may reflect a prior "
    "rate, a credit, or a billing error. Needs clarification before drawing conclusions.'",
    "The full pattern, treated as something to investigate, with the limits of what the data "
    "establishes stated in terms.")
add("glm5.2", 4, "segment_recommendation", F,
    "'Decision 1: Reduce investment in one customer segment - Yes, reduce SMB Starter "
    "investment ... Stop actively acquiring Starter customers via paid channels.'",
    "Recommends defunding part of SMB. The reasoning is careful - it keeps the plan as a "
    "self-serve entry point and proposes repricing rather than exit - but it is still an "
    "instruction to stop acquiring, and the pack has no segment-level acquisition cost to "
    "support it.")
add("glm5.2", 4, "acquisition_recommendation", T,
    "'Conditionally, increase Content; hold Paid Search until attribution is fixed ... Content "
    "has the second-highest trial conversion rate, consistent new-logo output (3 logos in 2 "
    "months), and lower risk of attribution distortion'",
    "Content is one of the two channels the corrected view supports and it is chosen on new-logo "
    "output, and Paid Search is correctly held. But the Content increase itself is not "
    "conditioned on the missing cost data, which the criterion asks for.")
add("glm5.2", 4, "product_recommendation", T,
    "'Enterprise, for cost reduction; Pro, for growth enablement'",
    "Actionable and consistent with its own section 4, but two recommendations rather than the "
    "single one the criterion asks for.")
add("glm5.2", 4, "uncertainty_discipline", P,
    "ten items including the plan counts including mid-month churners, the unverifiable "
    "support-cost allocation, Soylent's unexplained invoice change, and the absence of cohort "
    "data for the churned Starter accounts",
    "Every gap real, four beyond the answer key, and its figure errors are mis-sums rather than "
    "inventions.")

PENALTIES[("glm5.2", 4)] = [{
    "type": "PROHIBITED_ACTION",
    "evidence": "'Decision 1: Reduce investment in one customer segment - Yes, reduce SMB Starter "
                "investment ... Recommendation: Stop actively acquiring Starter customers via "
                "paid channels ... redirect acquisition spend and CS capacity toward Pro and "
                "Enterprise.'",
    "reason": "Defunding part of SMB on churn and plan economics, which is the first action the "
              "pack rules out. It is the same recommendation as run-003 and is charged the same "
              "way. Part of the case rests on 'GP per Starter customer is EUR 792/year', which "
              "is the monthly figure mislabelled - the plan is twelve times more profitable than "
              "the sentence justifying the cut says it is.",
}]


# --- glm5.3-flash run-005 ------------------------------------------------
# The third of three, and the only one in the battery to reach both accepted
# revenue normalisations. Also the only response anywhere to notice that
# Starter's falling average usage is a composition effect.
add("glm5.3-flash", 5, "duplicate_detected", P,
    "'a duplicate invoice (INV-2026-10-0209, soylent EUR 19.5k, loaded twice from two sources)' "
    "and the reconciliation table's 'Less duplicate soylent invoice ... EUR 873,400'",
    "Identified by id and excluded as the first step of the reconciliation.")
add("glm5.3-flash", 5, "annual_prepayment_normalized", P,
    "'gringotts EUR 120k annual prepayment (covers 12 months; only EUR 10k is October's "
    "service)' and 'Less gringotts annual prepay (EUR 120k covers 12 mo) ... EUR 763,400'",
    "Invoice, monthly equivalent, and it is actually removed from a stated total rather than "
    "only described.")
add("glm5.3-flash", 5, "headline_vs_recurring_growth", P,
    "'Invoiced revenue appears to grow +12.0% (EUR 797.1k -> EUR 892.9k) ... Recognized MRR "
    "grew just +1.6% (EUR 746.1k -> EUR 757.7k)', with the reconciliation table stepping "
    "892,900 -> 873,400 -> 763,400",
    "The headline and the refutation, both exact. It is also the only run in the battery whose "
    "table reaches EUR 763,400 - the all-invoice normalisation, which is -4.2% against September "
    "and the second treatment the criterion accepts - and the MRR bridge reconciles to the euro.")
add("glm5.3-flash", 5, "revenue_conclusion", P,
    "'The headline October revenue growth is largely a billing illusion' as the first line, and "
    "'The book is flat, not growing' as the second",
    "Stated to leadership twice over, with the figures underneath.")
add("glm5.3-flash", 5, "segment_retention_quantified", P,
    "'Churn concentration: Enterprise 0%, Mid-market 1 of 10 (nakatomi, EUR 180k), SMB 4 of 13 "
    "(EUR 123.6k = 31% logo churn)'",
    "All three segments on the opening-cohort basis - SMB's 13 is 18 less the five October logos "
    "- correctly labelled, correctly ranked, and consistent with the same model's other runs.")
add("glm5.3-flash", 5, "sample_size_arr_context", P,
    "'SMB is 5.4% of ARR but 35% of October tickets ... with 31% monthly logo churn. However, "
    "SMB supplied 8 of 9 new logos' and 'October: +EUR 133.2k new-logo ARR vs -EUR 303.6k "
    "churned ARR'",
    "Share of book, the churned ARR and what SMB produced, all quantified and all used to stop "
    "the rate speaking for itself.")
add("glm5.3-flash", 5, "acme_false_positive_avoided", P,
    "'-45% requests sits inside the planned 40-50% interactive reduction; tokens only -12% "
    "(tokens/request rose 1,100->1,760 - batch runs are fewer but denser, so don't expect infra "
    "cost to fall proportionally); tickets 4->3, all resolved'",
    "The migration and three corroborating figures, plus the second-order cost observation that "
    "follows from the denser batches.")
add("glm5.3-flash", 5, "no_churn_overreach", P,
    "'churn causes (the open high-severity tickets at nakatomi/soylent are suggestive, not "
    "proof)' listed among what cannot be computed from the pack",
    "Names the temptation and refuses it in terms.")
add("glm5.3-flash", 5, "raw_attribution_not_equivalent_new_business", P,
    "'Total attributed revenue rose EUR 282.0k -> EUR 349.2k, but new-logo ARR fell EUR 246.0k -> "
    "EUR 133.2k ... 40% of all attributed revenue (EUR 252k of EUR 631.2k) is expansion credit on "
    "existing customers' and '76% of its attributed value being expansion credit' for paid_search",
    "Quantified twice over - for the table and for Paid Search specifically - with the causal "
    "objection made from the customer tenure dates against the campaign start.")
add("glm5.3-flash", 5, "existing_customer_expansion_removed", P,
    "the channel table's new-logo columns: partner EUR 166.8k (2), content EUR 91.2k (3), "
    "paid_search EUR 64.8k (2), outbound EUR 56.4k (2), against expansion credited of "
    "EUR 0 / 18k / 210k / 24k",
    "Every figure exact, the reversal visible in the same table as the raw view, and the two "
    "paid_search logos identified as small SMB accounts.")
add("glm5.3-flash", 5, "conversion_rate_vs_absolute_volume", P,
    "'leads +73% (520->900) but same-month trial rate fell 8.5%->6.4%', with the table carrying "
    "leads and trials for every channel in both months",
    "Both movements, and it adds that the October lead surge came from campaigns starting 28 "
    "September - too recent for the customer output to be visible yet.")
add("glm5.3-flash", 5, "no_unsupported_channel_scale_decision", P,
    "'Hold paid_search flat. Falling trial rate at +73% volume, 76% of its attributed value being "
    "expansion credit, and untracked trial-to-paid conversion = no basis to scale. Instrument "
    "first ... then run a controlled increment test.'",
    "Refuses, gives three reasons, and specifies the instrumentation that would change the "
    "answer.")
add("glm5.3-flash", 5, "cac_payback_unavailable", P,
    "'not calculable from this pack. Required: channel spend by month, cohort revenue by channel "
    "over time, and plan-level gross margin' with 'Do not let anyone compute it from "
    "attributed_revenue_eur - it is annualized, last-touch, and expansion-inflated.'",
    "Refuses, lists the missing inputs, and pre-empts the wrong calculation someone else would "
    "reach for. The strongest treatment of this criterion in the battery.")
add("glm5.3-flash", 5, "contribution_calculated", P,
    "EUR 194,700 / EUR 41,500 / EUR 10,300 with a EUR 246,500 total",
    "All exact.")
add("glm5.3-flash", 5, "margin_calculated_or_correctly_compared", P,
    "'32.2% -> 29.5%', '67.5% -> 62.7%', '34.9% -> 32.2%' and total '35.2% -> 32.5%'",
    "All correct, both months, plus the blended figure.")
add("glm5.3-flash", 5, "absolute_vs_scalable_economics", P,
    "'Enterprise plan: 87% of MRR and 79% of contribution (EUR 13.9k/customer/month) - but margin "
    "eroded 2.7pp' against 'Pro is the strongest plan: best margin (62.7%), EUR 4.6k "
    "contribution/customer'",
    "Both halves held with the per-customer figures on each side, and the product decision then "
    "goes to Pro while Enterprise gets a billing task - the size is never used as the argument.")
add("glm5.3-flash", 5, "plan_trajectory_evidence", P,
    "'3 of 9 customers already above their 600k included requests (wonka 1.02M = 170%, aperture "
    "705k, vandelay 690k)' and 'stark used 4.29M and wayne 3.41M requests vs 3.0M included', "
    "with usage growth for vandelay +32.7%, planet-express +49.3%, aperture +21.6%",
    "Distribution and growth, for both plans, account by account - and it goes further than any "
    "other run by reading Starter's falling average as composition: 'the four heaviest users "
    "churned; survivors grew ~8-10%', which the Sept usage of the four churned accounts "
    "(95k-165k against a 114k plan average) bears out.")
add("glm5.3-flash", 5, "product_focus_supported", P,
    "'focus the quarter on Pro usage limits & overage experience ... highest margin, accelerating "
    "usage, clearest product-led revenue lever' with the three over-allowance accounts and the "
    "rate-limit ticket trend",
    "Pro on four signals beyond margin, and Enterprise explicitly given 'a parallel "
    "billing-readiness task, not the quarter's focus'.")
add("glm5.3-flash", 5, "customer_id_alias_resolved", P,
    "'usage_account_id != customer_id for wayne-enterprises (wayne_ent) and prestige-worldwide "
    "(prestige_ww); naive joins silently drop them', with wayne's 3.41M reported against its 3.0M "
    "allowance and its 30 November renewal",
    "Both aliases named, the failure mode described, and the join performed.")
add("glm5.3-flash", 5, "support_normalized", P,
    "'SMB = 26/74 tickets (35%) on 5.4% of ARR - ~14x enterprise's support intensity per EUR ARR' "
    "and 'Support per enterprise customer is now EUR 12.0k/month'",
    "Normalises on ARR and on customers, and the conclusion places SMB rather than Enterprise as "
    "the intensive one despite Enterprise raising the most tickets. The multiple itself is "
    "overstated and is charged under figure accuracy.")
add("glm5.3-flash", 5, "figures_carried_correctly", T,
    "'rate-limit tickets rose 5 -> 12' when the October count is 13; '~14x enterprise's support "
    "intensity per EUR ARR' when the ratio is about 10.5x; and 'November MRR starts at "
    "~EUR 750.4k (757.7 - 25.3 + 17.5 expansions)' where the components sum to 749.9",
    "Three slips, none decision-changing and none load-bearing. Everything else checkable is "
    "exact: both revenue normalisations, the MRR bridge, the churn table, the EUR 282.0k -> "
    "EUR 349.2k and EUR 246.0k -> EUR 133.2k attribution walk, the EUR 252k of EUR 631.2k split, "
    "all eight funnel cells, the full plan table, the margin deltas, all five over-allowance "
    "accounts with utilisations, tickets 59 -> 74, wonka's 11 tickets across two months, and the "
    "Starter composition claim.")
add("glm5.3-flash", 5, "cross_table_customer_signal", P,
    "'Soylent is the largest single-account risk (EUR 234k ARR, mid-market/enterprise plan): "
    "requests -27%, downgraded EUR 22.0k->EUR 19.5k/mo (-EUR 30k ARR), 8 October tickets "
    "including one critical and a still-open high-severity API error'",
    "Four tables on one account, every figure correct, and Wayne assembled the same way from "
    "billing, usage and its renewal date.")
add("glm5.3-flash", 5, "causal_boundary", P,
    "the Soylent trio reported together, with 'suggestive, not proof' and 'Acme's 40-50% "
    "reduction is an implementation estimate, not a measurement - the observed -45% is "
    "consistent with the migration but no counterfactual exists'",
    "Assembles the pattern, refuses the mechanism, and applies the same discipline to the "
    "explanation it had accepted.")
add("glm5.3-flash", 5, "segment_recommendation", T,
    "'Yes - reduce acquisition investment in SMB, redirect rather than cut ... pause incremental "
    "paid SMB acquisition, redirect budget to SMB retention/onboarding ... Revisit once "
    "CAC-by-segment exists.'",
    "A reduction hedged with conditions, which is the PARTIAL band precisely. It names the "
    "missing input the PASS bar asks for and the budget stays inside SMB rather than leaving it, "
    "but leadership is still told to pause acquisition spend.")
add("glm5.3-flash", 5, "acquisition_recommendation", P,
    "'If budget must move now, test partner capacity (23-25% trial rate, EUR 83.4k avg new logo) "
    "- acknowledging n=2' with paid_search held flat",
    "Partner on the corrected new-logo figure, the spend conditioned on instrumentation, and the "
    "sample size of its own recommendation disclosed.")
add("glm5.3-flash", 5, "product_recommendation", P,
    "'Product: focus the quarter on Pro usage limits & overage experience'",
    "Single, actionable, consistent with its own section 4.")
add("glm5.3-flash", 5, "uncertainty_discipline", P,
    "ten items including the composition trap behind Starter's average usage, the funnel "
    "measuring trial starts against 4 actual September logos, the join-key inconsistency, and "
    "Acme's 40-50% being an estimate rather than a measurement",
    "Every gap real, several beyond the answer key, and nothing invented.")


# =========================================================================
# MIMO v2.5
# =========================================================================
# Three runs that swing hard on the segment decision - 004 and 005 recommend
# reducing SMB Starter investment, 006 refuses and redirects - and on
# arithmetic, where 006 is near-perfect and 004's summary tables carry several
# wrong totals. 006 is the only response in the whole battery to reach the
# -4.2% all-invoice normalisation AND explain the Hooli invoice discrepancy.

# --- run-004 -------------------------------------------------------------
add("mimo-v2.5", 4, "duplicate_detected", P,
    "'Transaction INV-2026-10-0209 appears twice in revenue.csv: once from Stripe (Oct 1, "
    "EUR 19,500) and once from billing_sync (Oct 2, EUR 19,500) ... October revenue is overstated "
    "by EUR 19,500' and 'The plans data appears to de-duplicate correctly'",
    "Identified by id and both sources, excluded from its total, and it goes further by checking "
    "that plans.csv already counts Soylent once.")
add("mimo-v2.5", 4, "annual_prepayment_normalized", P,
    "'October subscription cash includes a EUR 120,000 annual invoice from Gringotts (monthly "
    "equivalent: EUR 10,000). Stripping the annual pre-payment out and using the monthly "
    "equivalent, October subscription MRR was EUR 757,700, up 1.6%'",
    "Invoice, monthly equivalent and the restated figure.")
add("mimo-v2.5", 4, "headline_vs_recurring_growth", T,
    "'Total invoiced EUR 797,100 -> EUR 860,900, +8.0%' against 'October subscription MRR was "
    "EUR 757,700, up 1.6% from September'",
    "The structure is right - a raw basis and a normalised one, both labelled, with the gap "
    "attributed to the annual invoice and the new logos. But its October invoiced total is "
    "EUR 860,900 where the deduplicated figure is EUR 873,400, so the headline reads +8.0% "
    "instead of about +12% and falls outside the stated tolerance.")
add("mimo-v2.5", 4, "revenue_conclusion", P,
    "'The revenue growth is misleading ... On a like-for-like, churn-adjusted basis, recurring "
    "revenue from the existing customer base has declined.'",
    "Stated plainly in the section and carried into the executive summary as 'Net MRR from the "
    "existing book is shrinking'.")
add("mimo-v2.5", 4, "segment_retention_quantified", T,
    "'Four of nine SMB starter customers (44%) churned in October' and the segment MRR table "
    "giving Enterprise EUR 565,000 / Mid-market EUR 129,500 -> EUR 130,000 / SMB EUR 51,600 -> "
    "EUR 37,400",
    "The Starter rate is correct and correctly labelled as a plan, and the segments are ranked "
    "on MRR movement. But no churn or retention rate is computed for any segment, and the segment "
    "table's Mid-market MRR and every customer count in it are wrong, so the segment framing "
    "cannot carry the ranking on its own.")
add("mimo-v2.5", 4, "sample_size_arr_context", P,
    "'Only EUR 800/mo of net MRR was added from five new starters - meaning the plan is running "
    "flat on MRR' and 'Enterprise generates 77% of MRR from 23% of customers. SMB generates 5% of "
    "MRR from 54% of customers.'",
    "Nets the churn against what replaced it and puts SMB's share of the book beside its share of "
    "the customer count, which is the asymmetry the criterion is after.")
add("mimo-v2.5", 4, "acme_false_positive_avoided", P,
    "'Acme's batch migration reduced its requests by 45% (4.2M -> 2.31M)' with the account absent "
    "from every risk list and 'Acme's migration proves usage can fall materially without revenue "
    "falling'",
    "The migration is named, revenue stability is the second signal, and the account is never "
    "treated as a risk.")
add("mimo-v2.5", 4, "no_churn_overreach", P,
    "'this pattern (declining usage + spiking support + possible downgrade) precedes churn' and "
    "'A >15% MoM decline in requests is a strong churn signal'",
    "Frames usage decline as a predictor throughout and never states why any customer left.")
add("mimo-v2.5", 4, "raw_attribution_not_equivalent_new_business", P,
    "'paid search's October attributed revenue is dominated by EUR 174K in expansion bookings "
    "from three large existing customers (stark, umbrella, globex). These are not new logos ... "
    "The actual new-logo acquisition value from paid search in October is EUR 64,800'",
    "Quantified both ways, accounts named, and the attribution mechanism explained.")
add("mimo-v2.5", 4, "existing_customer_expansion_removed", P,
    "the two monthly tables splitting new logos from expansion by channel, with every account "
    "named: partner EUR 166,800 (vandelay, clampett-oil), content EUR 45,600 then EUR 63,600, "
    "paid_search EUR 36,000 then EUR 238,800, outbound EUR 33,600 then EUR 46,800",
    "Every figure exact, and it draws the conclusion - 'Content generated the most new logos over "
    "2 months' - on the corrected basis.")
add("mimo-v2.5", 4, "conversion_rate_vs_absolute_volume", P,
    "'Paid search lead volume nearly doubled (520 -> 900) but the trial conversion rate dropped "
    "from 8.5% to 6.4%. This suggests the marginal lead from additional spend is lower quality.'",
    "Both movements with the trials column shown for every channel and both months.")
add("mimo-v2.5", 4, "no_unsupported_channel_scale_decision", P,
    "'Do not increase spend on any channel yet ... Request channel spend data for September and "
    "October from the marketing team. Implement trial-to-paid tracking in the funnel before "
    "making any spend decisions.'",
    "Refuses and gives a numbered sequence of what has to exist first.")
add("mimo-v2.5", 4, "cac_payback_unavailable", P,
    "'CFO's request cannot be fulfilled with this data pack. Requires: (a) channel spend, (b) "
    "full-funnel conversion rates including trial-to-paid, (c) actual contract value at "
    "conversion (not just attributed value).'",
    "Refused, with three missing inputs named - and the third is one the answer key does not "
    "ask for.")
add("mimo-v2.5", 4, "contribution_calculated", P,
    "the October table: EUR 194,700 / EUR 41,500 / EUR 10,300 with the COGS column beside it",
    "All exact.")
add("mimo-v2.5", 4, "margin_calculated_or_correctly_compared", P,
    "29.5% / 62.7% / 32.2%",
    "All three correct.")
add("mimo-v2.5", 4, "absolute_vs_scalable_economics", P,
    "'Enterprise Plan: Largest Revenue, Lowest Margin' against 'Pro Plan: Best Economics, Growth "
    "Potential', with the per-customer table giving EUR 13,907 / EUR 4,611 / EUR 792 and "
    "'Enterprise needs cost optimization, not engineering feature work.'",
    "Holds both halves under explicit headings and routes each to the decision it answers.")
add("mimo-v2.5", 4, "plan_trajectory_evidence", P,
    "'Two customers are now over plan limits: Wonka: 1,020K requests vs. 600K included (70% "
    "overage), Aperture: 705K vs. 600K (18% overage)' with 'Total requests across enterprise plan "
    "customers were essentially flat (26,540K -> 26,436K, -0.4%)'",
    "Reads the distribution against the allowance rather than the plan average, and the "
    "enterprise aggregate it quotes is only reachable with the aliased account joined.")
add("mimo-v2.5", 4, "product_focus_supported", P,
    "'The Pro plan has the clearest ROI for engineering investment' on five numbered grounds: "
    "highest margin, the two accounts over plan limits, rate-limit tickets concentrated there, a "
    "growing addressable base, and the pro-to-enterprise upgrade path",
    "Pro with four signals beyond margin, and Enterprise explicitly sent to cost work instead.")
add("mimo-v2.5", 4, "customer_id_alias_resolved", P,
    "'Total requests across enterprise plan customers were essentially flat (26,540K -> 26,436K)' "
    "- a figure only reachable with wayne_ent joined; without it the total is 23,440K",
    "The join was performed, and Wayne is separately reported with its EUR 1,008,000 ARR and 30 "
    "November renewal. The alias is not described.")
add("mimo-v2.5", 4, "support_normalized", P,
    "'Support cost per customer (EUR 792/mo) is 32% of revenue per customer' for Starter, and the "
    "per-customer economics table giving support of EUR 12,000 / EUR 956 / EUR 792",
    "Normalises on customers and on revenue across all three plans, and never argues from a raw "
    "ticket count.")
add("mimo-v2.5", 4, "figures_carried_correctly", F,
    "the revenue table's 'October subscription invoices EUR 855,200' and 'Total invoiced "
    "EUR 860,900' are both about EUR 12,500 below the pack, so its headline reads +8.0% rather "
    "than +12%; the segment table's Mid-market September MRR of EUR 129,500 should be "
    "EUR 142,000, and every customer count in it is wrong (8/19/35 against 9/14/31 active, or "
    "10/18/36 in total); and Wayne Enterprises is introduced as 'Waypoint Enterprises'",
    "Repeated incorrect figures across three sections, and one of them - the October total - is "
    "the headline the whole revenue section is built to interrogate. Its plan tables, MRR bridge, "
    "churn table, funnel and channel tables are all exact to the euro, which makes this a lapse "
    "in the summary tables rather than a misreading of the data.")
add("mimo-v2.5", 4, "cross_table_customer_signal", P,
    "'Soylent (Mid-market, enterprise plan, EUR 234,000 ARR): Usage -27% (980K -> 715K requests), "
    "Support tickets tripled (3 -> 8), including one critical ... September invoice was "
    "EUR 22,000; current ARR implies EUR 19,500/mo'",
    "Four tables on one account, and Wonka, Wayne and Aperture each assembled the same way with "
    "their plan, usage, allowance and support.")
add("mimo-v2.5", 4, "causal_boundary", P,
    "the Soylent trio reported together with 'No churn date yet, but this pattern ... precedes "
    "churn', and the uncertainties section listing 'Acme's migration freed up capacity' among "
    "unsupported causal claims",
    "Assembles the pattern, keeps the claim predictive, and audits its own causal language "
    "elsewhere.")
add("mimo-v2.5", 4, "segment_recommendation", F,
    "'Yes - reduce investment in SMB starter customers, but not SMB as a whole ... The "
    "recommendation is to shift resources away from acquiring new starter-tier customers'",
    "Recommends defunding starter acquisition. It is a careful version - it says outright that "
    "'Abandoning SMB entirely would cut off the top of the funnel', preserves SMB Pro, and offers "
    "three alternatives - but leadership is still told to move acquisition spend away, and the "
    "pack contains no segment-level acquisition cost to justify it.")
add("mimo-v2.5", 4, "acquisition_recommendation", T,
    "'Content produced the most new logos (3 in 2 months) with stable conversion rates ... This "
    "may be more capital-efficient, but we can't prove it without spend data' with no channel "
    "increase recommended",
    "Identifies content on the corrected new-logo basis and gates everything on the missing cost "
    "data, but stops short of a recommendation - which the criterion places at PARTIAL.")
add("mimo-v2.5", 4, "product_recommendation", P,
    "'Decision 3: Which plan deserves the most engineering attention - Recommendation: The Pro "
    "plan.'",
    "Single, actionable, consistent with its own section 4.")
add("mimo-v2.5", 4, "uncertainty_discipline", P,
    "ten items across three headings - confirmed data problems, unsupported causal claims to "
    "watch for, and metrics that cannot be calculated - including the support-cost allocation "
    "methodology and the NRR/LTV horizon problem",
    "Every gap real, several beyond the answer key, and the causal-claims heading is a discipline "
    "no other response applies to itself.")

PENALTIES[("mimo-v2.5", 4)] = [{
    "type": "PROHIBITED_ACTION",
    "evidence": "'Decision 1: Reduce investment in one customer segment. Recommendation: Yes - "
                "reduce investment in SMB starter customers ... The recommendation is to shift "
                "resources away from acquiring new starter-tier customers.'",
    "reason": "Defunding SMB acquisition on a churn rate is the first action the pack rules out. "
              "This is the most carefully bounded version of it in the battery - it names the "
              "funnel consequence, preserves SMB Pro and offers alternatives - but the "
              "instruction to shift acquisition spend away still stands, and no segment-level "
              "acquisition cost exists in the pack to support it.",
}]

# --- run-005 -------------------------------------------------------------
add("mimo-v2.5", 5, "duplicate_detected", P,
    "'Transaction ID INV-2026-10-0209 appears twice - once from Stripe (Oct 1, EUR 19,500) and "
    "once from billing_sync (Oct 2, EUR 19,500). Same ID, same amount, different sources.'",
    "Identified by id and both sources, and listed as a one-time item to strip from October's "
    "invoiced cash.")
add("mimo-v2.5", 5, "annual_prepayment_normalized", P,
    "'Gringotts annual prepayment EUR 120,000 - Yes, 12 months billed upfront' in the "
    "adjustments table, with 'The apparent revenue jump is a billing-timing artefact'",
    "Invoice identified, excluded, and the reason stated. The EUR 10,000 monthly equivalent is "
    "implied by the MRR reconciliation rather than written out.")
add("mimo-v2.5", 5, "headline_vs_recurring_growth", T,
    "'October invoiced cash was EUR 867,300, which looks like strong growth over September's "
    "EUR 797,100' with the three adjustments listed and 'underlying recurring invoicing is "
    "consistent with the EUR 757,700 MRR figure'",
    "Both bases are present and the adjustments itemised, but the raw growth rate is never "
    "computed - the reader is left to do it - and the October total is EUR 867,300 against the "
    "deduplicated EUR 873,400.")
add("mimo-v2.5", 5, "revenue_conclusion", P,
    "'October MRR grew 1.6%, but the business is weaker than the headline suggests' as the "
    "opening line, and 'Gross profit fell, not rose' as the first bullet",
    "The conclusion leads the brief and is quantified.")
add("mimo-v2.5", 5, "segment_retention_quantified", T,
    "'4 of 5 October churners are SMB starters (EUR 123,600 ARR lost)' and 'SMB (14 active "
    "customers ...) generates EUR 478,800 ARR = 5.3% of total active ARR'",
    "The churned ARR is placed by segment and SMB's active base is correct, but no churn or "
    "retention rate is computed for any segment - the only rate given, 44%, is the Starter plan's "
    "and is labelled as such - so the three populations are never ranked on retention.")
add("mimo-v2.5", 5, "sample_size_arr_context", P,
    "'New SMB starter logos (avg ARR = EUR 23,700) are not compensating for lost ones (avg ARR "
    "lost = EUR 30,900)' and 'SMB ... generates EUR 478,800 ARR = 5.3% of total active ARR'",
    "Sizes the churn, compares the average value of what left against what arrived, and gives "
    "SMB's share of the book.")
add("mimo-v2.5", 5, "acme_false_positive_avoided", T,
    "'Acme's migration proves usage can fall materially without revenue falling' and, in the "
    "uncertainties, 'Cannot attribute Enterprise cost growth ... Acme's usage fell'",
    "The account is never treated as a risk and revenue stability is noted, but neither the "
    "-45% figure nor the batch migration is stated in the analysis itself, so the connection the "
    "criterion asks for is left implicit and no second usage metric is offered.")
add("mimo-v2.5", 5, "no_churn_overreach", P,
    "'Soylent is about to churn - Usage decline and ticket volume are warning signals, but we "
    "have no survey data, NPS, or conversation notes. Many customers have usage dips without "
    "churning.' listed under unsupported causal claims",
    "Names the claim it is declining to make and why, about its own headline risk account.")
add("mimo-v2.5", 5, "raw_attribution_not_equivalent_new_business", T,
    "'Three of its four October conversions are expansions, not new logos - expansions do not "
    "expand the customer base' and 'High attributed revenue could simply reflect high spend'",
    "The contamination is identified for Paid Search and the reasoning is right, but it is never "
    "quantified: neither the EUR 274,800 attributed total nor the EUR 210,000 of expansion "
    "appears, only the October column.")
add("mimo-v2.5", 5, "existing_customer_expansion_removed", F,
    "the channel table carries leads, trial rates and October attributed revenue only; no "
    "new-logo ARR is computed for any channel",
    "Having seen that paid search's number is mostly expansion, it never recomputes the ranking "
    "on new-logo revenue, so the reversal never appears.")
add("mimo-v2.5", 5, "conversion_rate_vs_absolute_volume", T,
    "'Paid Search 520 leads / 8.5% -> 900 leads / 6.4%' with 'its lead-to-trial rate dropped from "
    "8.5% to 6.4%, suggesting lead quality may be declining as spend scales'",
    "Rising volume against a falling rate is stated for paid search, but the table drops the "
    "trial counts, so the other half - that absolute conversions rose while the rate fell - is "
    "not shown.")
add("mimo-v2.5", 5, "no_unsupported_channel_scale_decision", P,
    "'NOT YET ... Request monthly channel spend data from marketing for September and October. "
    "Without this, any spend increase is an uninformed bet.'",
    "Refuses and names the missing input.")
add("mimo-v2.5", 5, "cac_payback_unavailable", P,
    "'CAC payback by channel cannot be calculated. The CFO's request requires channel spend data "
    "(ad budget, sales costs, tooling), which is not in this data pack' with the formula and the "
    "four inputs it would need",
    "Refused, with the missing inputs enumerated.")
add("mimo-v2.5", 5, "contribution_calculated", P,
    "the two-month table: EUR 212,000 / 42,500 / 8,400 and EUR 194,700 / 41,500 / 10,300 with a "
    "EUR 262,900 -> EUR 246,500 total",
    "All exact, including both totals.")
add("mimo-v2.5", 5, "margin_calculated_or_correctly_compared", P,
    "32.2% / 67.5% / 34.9% and 29.5% / 62.7% / 32.2%, plus 35.2% -> 32.5% blended",
    "All correct.")
add("mimo-v2.5", 5, "absolute_vs_scalable_economics", P,
    "'Enterprise - the revenue engine with eroding margins ... Drives 87% of MRR but margin fell "
    "2.7 points' against 'Pro - strongest economics ... Best-in-class margin at 63%, roughly 2x "
    "Enterprise', with 'Enterprise GP per customer = EUR 13,907 vs. Pro GP per customer = "
    "EUR 4,611'",
    "Both halves held, and the per-customer contrast is used to argue the upgrade motion rather "
    "than to rank the plans.")
add("mimo-v2.5", 5, "plan_trajectory_evidence", T,
    "'Highest plan utilisation (74%) - customers are approaching their included request limits' "
    "and 'Utilisation is only 42%' for Starter",
    "Utilisation is quantified for every plan and hedged correctly - 'approaching' rather than "
    "'below' - so it avoids the aggregate FAIL. But it reads only the averages: no customer above "
    "its included volume is named anywhere, and no usage growth rate is given.")
add("mimo-v2.5", 5, "product_focus_supported", P,
    "'Primary recommendation: Pro plan' on highest margin, 74% utilisation creating an upgrade "
    "path, and per-customer GP of EUR 4,611 against Enterprise's EUR 13,907 as the upsell prize",
    "Pro with utilisation and the upgrade motion as two signals beyond margin, and Enterprise "
    "kept as an explicit cost workstream rather than the product focus.")
add("mimo-v2.5", 5, "customer_id_alias_resolved", T,
    "'Wayne Enterprises has an imminent renewal (November 30, EUR 1,008K ARR) ... Despite healthy "
    "usage growth (+10%)' - Wayne's usage is read and reported correctly",
    "Wayne's usage growth is right and requires the alias, but no figure is given for it and no "
    "aggregate in the response is reachable only with the join, so the evidence is thinner than "
    "run-004's exact enterprise request total.")
add("mimo-v2.5", 5, "support_normalized", P,
    "'starter support cost per EUR 1 of revenue is EUR 0.43 vs. EUR 0.25 for Enterprise and "
    "EUR 0.13 for Pro' and 'Tickets per active customer 1.84 -> 2.39'",
    "A consistent denominator applied across all three plans, and Enterprise is not the worst on "
    "it despite raising the most tickets. The Starter ratio itself is miscalculated and is "
    "charged under figure accuracy.")
add("mimo-v2.5", 5, "figures_carried_correctly", F,
    "'Total tickets 57 -> 74' when September is 59, which then propagates into the cost-per-ticket "
    "row; 'starter support cost per EUR 1 of revenue is EUR 0.43' when it is EUR 0.32; 'Three "
    "additional expansion bookings (Stark ... Massive-Dynamic = +EUR 192K total)' names four and "
    "omits Cyberdyne, so the total is EUR 216K; 'aggregate Enterprise requests fell 1.4%' when "
    "the figure is -0.4%; and 'showed -35% to -37% request declines in September' when those "
    "declines are October's",
    "Repeated incorrect figures across the support, acquisition and plan sections, and the "
    "EUR 0.43 ratio sits inside the argument for reducing SMB investment. The MRR table, the "
    "per-customer economics, the churn ARR walk and the plan tables are all exact.")
add("mimo-v2.5", 5, "cross_table_customer_signal", P,
    "'Soylent ... requests dropped 27% month-over-month and support tickets surged to 8 (from 3), "
    "including a critical-severity API error and a pending integration issue' with its EUR 234K "
    "ARR and May 2027 renewal",
    "Usage, support and billing on one account, and the at-risk renewals table assembles Wayne "
    "and Duff Brewing the same way.")
add("mimo-v2.5", 5, "causal_boundary", P,
    "the Soylent trio reported together, with the unsupported-claims table stating that usage "
    "decline 'could be causal ... or symptomatic ... We cannot distinguish'",
    "Assembles the pattern and states the direction problem explicitly.")
add("mimo-v2.5", 5, "segment_recommendation", F,
    "'Reduce investment in SMB - YES, proceed ... Pause or reduce paid acquisition targeting "
    "SMB/starter segments ... Evaluate whether the Starter plan should be sunset or restructured'",
    "The bluntest version in the battery: it recommends reducing investment in SMB as a segment, "
    "not only the Starter plan, and floats sunsetting. Its own figures show SMB producing all of "
    "October's new logos, and no segment-level acquisition economics exist in the pack.")
add("mimo-v2.5", 5, "acquisition_recommendation", T,
    "'Content produced the most new logos (3 in 2 months) with stable conversion rates ... This "
    "may be more capital-efficient, but we can't prove it without spend data' with no increase "
    "recommended",
    "Names content on a new-logo basis and gates everything on the cost gap, but makes no "
    "recommendation - and its reasoning about paid search rests on the October column rather than "
    "a corrected new-logo ranking it never built.")
add("mimo-v2.5", 5, "product_recommendation", P,
    "'Decision 3: Engineering focus - Pro plan, with Enterprise cost workstream'",
    "A single primary recommendation with an explicit secondary, consistent with its section 4.")
add("mimo-v2.5", 5, "uncertainty_discipline", P,
    "four tables covering data-quality problems, metrics that cannot be calculated, unsupported "
    "causal claims and scope limitations - including professional services having no margin "
    "profile in the pack and the CS allocation methodology",
    "Every gap real, two beyond the answer key, and nothing invented.")

PENALTIES[("mimo-v2.5", 5)] = [{
    "type": "PROHIBITED_ACTION",
    "evidence": "'Decision 1: Reduce investment in SMB - YES, proceed ... Pause or reduce paid "
                "acquisition targeting SMB/starter segments ... Evaluate whether the Starter plan "
                "should be sunset or restructured.'",
    "reason": "Cutting SMB investment on a churn rate is the first action the pack rules out, and "
              "this states it at the segment level rather than the plan level and adds a sunset "
              "option. Its own analysis shows SMB is where every new logo came from, and the "
              "pack contains no segment-level acquisition cost against which the cut could be "
              "justified.",
}]

# --- run-006 -------------------------------------------------------------
add("mimo-v2.5", 6, "duplicate_detected", P,
    "'INV-2026-10-0209 appears twice - once from Stripe (2026-10-01, EUR 19,500) and once from "
    "billing_sync (2026-10-02, EUR 19,500) ... The two-source pattern suggests a "
    "replication/deduplication failure in the billing pipeline.'",
    "Identified by id and both sources, removed in the normalisation table, and the operational "
    "cause diagnosed.")
add("mimo-v2.5", 6, "annual_prepayment_normalized", P,
    "'A legitimate 12-month prepaid subscription booked in October that represents EUR 10K/month "
    "of MRR. It inflates October's cash-invoiced figure by EUR 110K' and 'Financial reporting "
    "must defer EUR 110,000 to future months.'",
    "Invoice, monthly equivalent, effect and the accounting treatment.")
add("mimo-v2.5", 6, "headline_vs_recurring_growth", P,
    "the normalisation table: 'Invoiced (raw) EUR 797,100 -> EUR 892,900, +12.0% ... Less Soylent "
    "duplicate ... Less Gringotts annual uplift ... Normalised EUR 797,100 -> EUR 763,400, -4.2% "
    "... MRR (plans.csv) EUR 746,100 -> EUR 757,700, +1.6%'",
    "The headline at +12.0% and BOTH accepted normalisations, each labelled with what is in it - "
    "the only response in the battery to compute the -4.2% all-invoice basis explicitly. It then "
    "explains why the two disagree, correctly, from the Hooli and Soylent pre-adjustment "
    "invoices.")
add("mimo-v2.5", 6, "revenue_conclusion", P,
    "'October invoiced revenue of EUR 892.9K looks like a sharp jump over September's EUR 797.1K, "
    "but the headline is misleading' as the opening sentence",
    "Leads the brief with the conclusion and the two distortions behind it.")
add("mimo-v2.5", 6, "segment_retention_quantified", T,
    "the churn table placing all five logos with segment, plan, ARR lost, usage change and ticket "
    "detail, plus 'Starter churn rate: 44% of the September base (4 of 9)'",
    "The churn is fully placed by segment and the one rate given is correct and correctly "
    "labelled as the Starter plan. But no rate is computed for any segment, so Enterprise, "
    "Mid-market and SMB are never ranked on retention.")
add("mimo-v2.5", 6, "sample_size_arr_context", P,
    "'net SMB MRR still grew (new logos outpaced lost ARR in October: +EUR 133K new vs -EUR 124K "
    "churned)'",
    "Sizes the churn against what replaced it and uses the net to refuse the cut, which is "
    "exactly the reasoning the criterion exists to reward.")
add("mimo-v2.5", 6, "acme_false_positive_avoided", P,
    "'The 45% drop in interactive requests is consistent with the planned migration to batch "
    "processing (estimated 40-50% reduction). Token volume declined only 12% (4,620M -> 4,066M), "
    "confirming the batch workload still processes substantial token volume through fewer API "
    "calls.'",
    "Migration plus the token figure, and it opens with 'should not alarm'.")
add("mimo-v2.5", 6, "no_churn_overreach", P,
    "'Cannot attribute SMB churn to any specific cause ... The usage decline could be causal ... "
    "or symptomatic ... We cannot distinguish.'",
    "States the limit and the direction problem in terms.")
add("mimo-v2.5", 6, "raw_attribution_not_equivalent_new_business", P,
    "'Paid search drove the most total attributed revenue (EUR 274.8K), but EUR 210K of that was "
    "expansion from existing customers, not new logos' with all four accounts named",
    "Quantified to the euro in the summary and repeated in the channel table.")
add("mimo-v2.5", 6, "existing_customer_expansion_removed", P,
    "the channel table's new-logo column: Paid Search EUR 64,800 (2), Partner EUR 166,800 (2), "
    "Content EUR 91,200 (3), Outbound EUR 56,400 (2), with 'For new logos only, partner and "
    "content outperform paid search'",
    "Every figure exact and the reversal stated as the conclusion.")
add("mimo-v2.5", 6, "conversion_rate_vs_absolute_volume", P,
    "the funnel table with conversion counts for both months, and 'Paid search absorbed a 73% "
    "increase in lead volume (520->900) but its conversion rate fell by 2.1 percentage points'",
    "Both movements, for every channel, with the numerators shown.")
add("mimo-v2.5", 6, "no_unsupported_channel_scale_decision", P,
    "'Do not increase paid search spend without addressing conversion-rate decline ... Before any "
    "spend increase: get the CAC payback data the CFO needs.'",
    "Refuses the paid-search increase and conditions every other one on the missing data.")
add("mimo-v2.5", 6, "cac_payback_unavailable", P,
    "'This pack does not contain the data to answer it' with three numbered reasons and 'What we "
    "can report: Lead-to-trial conversion rates, attributed ARR per lead ... These are "
    "directional efficiency indicators but are not CAC payback.'",
    "Refused, the missing inputs named, and the substitute explicitly labelled as not the "
    "requested metric.")
add("mimo-v2.5", 6, "contribution_calculated", P,
    "the two monthly tables with EUR 212,000 / 42,500 / 8,400 and EUR 194,700 / 41,500 / 10,300",
    "All exact, with correct infra and support totals of EUR 310,000 and EUR 173,200 for "
    "September.")
add("mimo-v2.5", 6, "margin_calculated_or_correctly_compared", P,
    "32.2% / 67.5% / 34.9% and 29.5% for enterprise, with a 35.2% blended September figure",
    "All correct.")
add("mimo-v2.5", 6, "absolute_vs_scalable_economics", P,
    "'A 1-percentage-point margin improvement on Enterprise saves ~EUR 6.6K/month; the same on "
    "Starter saves ~EUR 0.3K/month' and 'reduce Enterprise infra cost by 5% (EUR 14,840/month, "
    "EUR 178K/year), that is equivalent to eliminating the entire Starter plan's infrastructure "
    "cost twice over'",
    "Rather than asserting the distinction it prices it: both figures check out, and they make "
    "the case that scale and margin answer different questions better than any restatement could.")
add("mimo-v2.5", 6, "plan_trajectory_evidence", T,
    "'Wonka generated 8 support tickets in October, mostly rate_limits. They are likely hitting "
    "the 600K included-request ceiling' and 'At 1,020K requests in October against a 600K "
    "included limit, they are 70% over their plan threshold'",
    "One account read correctly against its allowance rather than the plan average, which clears "
    "the FAIL bar. But Aperture and Vandelay are never identified, no Enterprise account above "
    "3M is named, and no usage growth rate is computed - so the distribution is read for one "
    "customer rather than for a plan.")
add("mimo-v2.5", 6, "product_focus_supported", P,
    "'Enterprise plan - infrastructure efficiency ... If engineering can reduce Enterprise infra "
    "cost by 5% (EUR 14,840/month, EUR 178K/year), that is equivalent to eliminating the entire "
    "Starter plan's infrastructure cost twice over' with the cost-per-request rise as the second "
    "signal and Pro rate limits as an explicit number two",
    "A plan other than Pro, argued from a quantified cost-efficiency opportunity and a rising "
    "unit cost - both cost-adjusted - with the revenue share used to size the prize rather than "
    "as the reason.")
add("mimo-v2.5", 6, "customer_id_alias_resolved", T,
    "'Wayne Enterprises (EUR 1,008,000 ARR) renews November 30 ... usage grew 10%'",
    "Wayne's usage growth is correct and requires the join, but it is given as a percentage with "
    "no request figure and no aggregate depends on it, so the evidence is indirect.")
add("mimo-v2.5", 6, "support_normalized", T,
    "the churn table's per-account ticket counts and 'Wonka generated 8 support tickets in "
    "October'",
    "Support is read at account level throughout and Enterprise is never called the worst on raw "
    "volume, but no rate against any denominator is computed for any plan or segment, so the "
    "normalisation the criterion asks for is not performed.")
add("mimo-v2.5", 6, "figures_carried_correctly", T,
    "'Wayne Enterprises ... This is the third-largest contract' when it is the second, behind "
    "Stark at EUR 1.14M; 'Wonka generated 8 support tickets in October' when the count is 7; and "
    "'5 rate_limits tickets across September and October' when it is 6",
    "Three slips, all in supporting detail and none decision-changing. Everything else checkable "
    "is exact, and the response carries more arithmetic than any other in the battery: both "
    "revenue normalisations, the full expansion table at EUR 216,000, the churn table with usage "
    "and tickets per account, all eight funnel cells with numerators, the complete two-month plan "
    "tables with infra and support totals, the EUR 6.6K per margin point, the EUR 14,840 saving, "
    "and the Hooli reconstruction of EUR 252K - EUR 36K = EUR 216K -> EUR 18K/month.")
add("mimo-v2.5", 6, "cross_table_customer_signal", P,
    "'Soylent: Usage -27% (980K -> 715K), Support 8 tickets including 1 critical (TCK-10-0086) "
    "and 3 high-severity, an open high-severity ticket (TCK-10-0087), Billing: September invoice "
    "EUR 22,000 exceeded the current EUR 19,500 ... Revenue at risk EUR 234,000'",
    "Four tables on one account, down to the ticket ids, and the churn table does the same for "
    "all five departures.")
add("mimo-v2.5", 6, "causal_boundary", P,
    "the Soylent trio reported together as 'a strong leading indicator of churn', with the "
    "uncertainties stating the usage decline 'could be causal ... or symptomatic ... We cannot "
    "distinguish'",
    "Assembles the pattern, acts on it, and refuses the mechanism.")
add("mimo-v2.5", 6, "segment_recommendation", P,
    "'Do not cut SMB investment broadly, but do reallocate within it ... The answer is not to cut "
    "SMB investment but to fix the onboarding and early-life experience. The fact that all four "
    "churned starters showed steep usage declines the month before churning suggests early-warning "
    "triggers exist and are not being acted on.'",
    "Refuses the cut on quantified grounds - net SMB MRR grew - and replaces it with a concrete "
    "programme rather than a study. It also correctly redirects the question at Enterprise's cost "
    "trend, which is the larger financial risk and which it sizes.")
add("mimo-v2.5", 6, "acquisition_recommendation", P,
    "'Increase partner investment cautiously ... Partner is the most efficient new-logo channel "
    "(25% lead-to-trial, EUR 83.4K average new-logo ARR per conversion) ... Before any spend "
    "increase: get the CAC payback data the CFO needs.'",
    "Partner on the corrected new-logo figure, with the spend conditioned on the missing cost "
    "data and the volume constraint named.")
add("mimo-v2.5", 6, "product_recommendation", P,
    "'Decision 3: Which plan gets engineering focus? Recommendation: Enterprise plan - "
    "infrastructure efficiency.'",
    "Single, actionable, consistent with its own section 4.")
add("mimo-v2.5", 6, "uncertainty_discipline", P,
    "fifteen numbered items including the Hooli invoice reconciliation, plans.csv counting "
    "mid-month churners with the arithmetic shown, the cost-allocation methodology, and three "
    "separate causal claims it declines to make",
    "Every gap real, several beyond the answer key, and it resolves one apparent discrepancy - "
    "Hooli's September invoice - rather than only listing it.")


# =========================================================================
# Qwen 3.8 Flash
# =========================================================================
# The most arithmetically exact model in the battery. run-004 is the only
# response anywhere whose every checkable figure I could not fault - all nine
# segment usage aggregates land on the decimal, which additionally proves both
# aliases were joined. All three runs refuse every trap.
#
# One criterion holds all three below full marks: none of them normalises
# support load. Each reports ticket counts by plan or segment - correctly, and
# each reaches the right conclusion that Enterprise is not the worst - but a
# count is not a rate, and the criterion asks for a denominator.

# --- run-003 -------------------------------------------------------------
add("qwen3.8-flash", 3, "duplicate_detected", P,
    "'INV-2026-10-0209 appears twice for Soylent, same amount and billing period ... I treat it "
    "as a probable double-load and exclude it from corrected revenue. I also show the impact if "
    "included.' with both totals given",
    "Identified, excluded, and both the corrected and uncorrected figures published so the reader "
    "can see the size of the error. The treatment is declared before the analysis starts.")
add("qwen3.8-flash", 3, "annual_prepayment_normalized", P,
    "'Gringotts' October invoice of EUR 120,000 covers 12 months, so it adds EUR 10,000 of MRR, "
    "not EUR 120,000 of recurring monthly revenue' with 'EUR 120,000 / 12 = EUR 10,000' shown",
    "Invoice, monthly equivalent and the arithmetic, stated as a definition up front and applied "
    "consistently.")
add("qwen3.8-flash", 3, "headline_vs_recurring_growth", P,
    "'October booked revenue as loaded: EUR 892,900 ... excluding the duplicate: EUR 873,400 ... "
    "EUR 873,400 - EUR 797,100 = EUR 76,300 / +9.6%' against corrected MRR of EUR 746,100 -> "
    "EUR 757,700 (+1.6%) and active MRR of EUR 732,400 (-1.8%)",
    "Raw, deduplicated, recurring and forward-looking, four bases each labelled with exactly what "
    "is in it, and the gap attributed to the annual invoice, the duplicate and the advance "
    "billing.")
add("qwen3.8-flash", 3, "revenue_conclusion", P,
    "'October's headline revenue is inflated by invoice timing, not by underlying recurring "
    "growth' as finding number one",
    "Opens the summary and drives the ARR bridge beneath it.")
add("qwen3.8-flash", 3, "segment_retention_quantified", P,
    "the segment ARR table - Enterprise EUR 6,780,000 flat, Mid-market EUR 1,704,000 -> "
    "EUR 1,530,000 (-EUR 174,000), SMB EUR 469,200 -> EUR 478,800 (+EUR 9,600) - with SMB churn "
    "of EUR 123,600 itemised by account",
    "Segment movement quantified on a stated basis for all three, correctly ranked, and the "
    "September Mid-market figure of EUR 1,704,000 is right: it backs Hooli's expansion out and "
    "Soylent's contraction in, which is the only way that number reconciles.")
add("qwen3.8-flash", 3, "sample_size_arr_context", P,
    "'Total SMB churn EUR 123,600' set against 'Total SMB new logos EUR 133,200' and 'SMB net ARR "
    "grew because new logos offset churn', with Mid-market's single EUR 180,000 churn beside it",
    "Sizes the churn, nets it, and the Mid-market comparison is the reason it refuses the cut.")
add("qwen3.8-flash", 3, "acme_false_positive_avoided", P,
    "'Acme requests fell -45% ... Acme tokens fell only -12% ... Acme revenue was unchanged at "
    "EUR 78,000/month ... Therefore, Acme's request decline should not be treated as churn risk.'",
    "Three corroborating figures against the stated migration and an explicit instruction not to "
    "misread it.")
add("qwen3.8-flash", 3, "no_churn_overreach", P,
    "'Nakatomi churn also had warning signs' listing the ticket history without a cause, and "
    "'Run a Nakatomi churn post-mortem' as the action",
    "Treats the ticket history as a signal and sends the question to a post-mortem rather than "
    "answering it from the pack.")
add("qwen3.8-flash", 3, "raw_attribution_not_equivalent_new_business", P,
    "'October Paid Search attributed revenue: EUR 238,800. But only EUR 64,800 is new-logo ARR. "
    "EUR 174,000 is expansion bookings from existing customers: Stark, Umbrella, Globex.'",
    "Split, size and accounts, with the additional point that the expansions take effect the "
    "following billing cycle so they are not October revenue either.")
add("qwen3.8-flash", 3, "existing_customer_expansion_removed", P,
    "the two monthly channel tables with new-logo, expansion and total columns, totalling "
    "EUR 246,000 / EUR 36,000 / EUR 282,000 for September and EUR 133,200 / EUR 216,000 / "
    "EUR 349,200 for October",
    "Every cell exact, both months, with the totals reconciling - and the new-logo ranking that "
    "results is the corrected one.")
add("qwen3.8-flash", 3, "conversion_rate_vs_absolute_volume", P,
    "'Paid Search generated the most leads and most paid trials in October. Paid Search trial "
    "rate declined from 8.5% to 6.4%.' with the full two-month table",
    "Both movements stated together, and the table carries leads and trials for every channel so "
    "the divergence is visible rather than asserted.")
add("qwen3.8-flash", 3, "no_unsupported_channel_scale_decision", P,
    "'Do not increase Paid Search spend based on this pack' and 'the only safe recommendation is: "
    "do not increase spend on any channel based on this data alone', followed by the eleven-field "
    "channel report it would need",
    "Refuses and specifies exactly what would have to exist first.")
add("qwen3.8-flash", 3, "cac_payback_unavailable", P,
    "'CAC payback by acquisition channel is not computable from the supplied data' with the "
    "formula written out and six missing inputs listed against four that are provided",
    "Refused, with the gap between what the pack has and what the metric needs made explicit.")
add("qwen3.8-flash", 3, "contribution_calculated", P,
    "the two monthly plan tables with revenue, infra, support, total cost and contribution, "
    "totalling EUR 262,900 for September and EUR 246,500 for October",
    "All twelve figures exact, plus correct September infra and support totals of EUR 310,000 and "
    "EUR 173,200.")
add("qwen3.8-flash", 3, "margin_calculated_or_correctly_compared", P,
    "32.2% / 67.5% / 34.9% and 29.5% / 62.7% / 32.2%, with a 35.2% -> 32.5% blended figure and a "
    "month-over-month table giving -2.7 / -4.8 / -2.7 points",
    "All correct, and the per-plan margin deltas check out individually.")
add("qwen3.8-flash", 3, "absolute_vs_scalable_economics", P,
    "'Enterprise has the largest absolute contribution per customer. Pro has the best margin and "
    "much better contribution per customer than Starter' and 'Enterprise needs cost discipline, "
    "but the data do not show a clear product constraint'",
    "Holds both halves and says which question each answers - the product decision goes to Pro on "
    "constraint evidence, the cost question stays with Enterprise.")
add("qwen3.8-flash", 3, "plan_trajectory_evidence", P,
    "the utilisation table (Enterprise 62.9%, Pro 73.7%, Starter 42.2%) followed by named "
    "accounts above their allowance: Stark 4,290,000 and Wayne 3,410,000 on Enterprise; Aperture "
    "705,000, Vandelay 690,000 and Wonka 1,020,000 on Pro; and 'No October Starter customer "
    "exceeds 200,000 requests'",
    "Average and distribution both, for all three plans, with the overage volumes totalled - and "
    "the one plan where the average is the whole story is the one where it says so.")
add("qwen3.8-flash", 3, "product_focus_supported", P,
    "'The Pro plan deserves the most engineering attention' on highest margin, 73.7% utilisation, "
    "three accounts over included volume, tickets 19 -> 28, 13 rate-limit tickets, and usage "
    "growth for four named accounts",
    "Five signals beyond margin, and Enterprise is explicitly assessed and set aside: 'the data "
    "do not show a clear product constraint'.")
add("qwen3.8-flash", 3, "customer_id_alias_resolved", P,
    "'Usage joins: use usage_account_id, not customer_id, because Wayne Enterprises and Prestige "
    "Worldwide have different usage IDs (wayne_ent, prestige_ww)' stated as a method up front, "
    "with Wayne's 3,410,000 October requests reported",
    "Both aliases named before the analysis begins, and the join performed.")
add("qwen3.8-flash", 3, "support_normalized", T,
    "'October support tickets by plan: Enterprise 34 -> 35, Pro 19 -> 28, Starter 7 -> 11' and "
    "'September Enterprise-segment tickets: 26, October: 25'",
    "It avoids the trap - Enterprise is called stable and Pro gets the focus - and it reads the "
    "segment view as well as the plan view, which is more care than most. But no rate against any "
    "denominator is computed, so the normalisation the criterion asks for is not performed.")
add("qwen3.8-flash", 3, "figures_carried_correctly", T,
    "'Enterprise 34 September tickets' where the enterprise plan has 33, which also makes its own "
    "column sum to 60 against a September total of 59",
    "One miscount. Everything else checkable is exact, and the response carries more arithmetic "
    "than any other in the battery: the ARR bridge reconciling to EUR 8,788,800 to the euro, four "
    "revenue bases, the segment ARR walk including the reconstructed EUR 1,704,000, both channel "
    "tables with totals, the full two-month plan economics with cost subtotals, the utilisation "
    "table computed from customer counts, all five over-allowance accounts with overage volumes, "
    "the Soylent four-metric table, and the 13 October rate-limit tickets itemised per account - "
    "the only response anywhere to get that count right.")
add("qwen3.8-flash", 3, "cross_table_customer_signal", P,
    "the Soylent table giving revenue EUR 22,000 -> EUR 19,500 (-11.4%), requests 980,000 -> "
    "715,400 (-27.0%), tokens -27.0%, active users 56 -> 41 (-26.8%) and tickets 3 -> 8",
    "Four tables on one account with every figure exact, and the SMB usage and churn tables do "
    "the same across accounts.")
add("qwen3.8-flash", 3, "causal_boundary", P,
    "the Soylent metric table reported as 'a clear red flag' with the action being 'Intervene on "
    "Soylent', and no mechanism proposed anywhere",
    "Assembles all three movements and stops.")
add("qwen3.8-flash", 3, "segment_recommendation", P,
    "'Do not approve a broad segment investment cut yet ... Do not cut SMB acquisition until CAC "
    "and retention are known' with 'What Finance needs before deciding: Segment-level investment "
    "cost, not just plan-level support/infra cost. CAC by segment. Retention by segment. Gross "
    "margin by segment.'",
    "Refuses the cut and then names, as a list, exactly the missing inputs the criterion asks "
    "for - including the distinction between segment-level and plan-level cost, which is the "
    "precise gap in the pack.")
add("qwen3.8-flash", 3, "acquisition_recommendation", P,
    "'Content produced stable new-logo ARR' and 'Partner had the highest trial rate and strong "
    "September new-logo ARR, but no October conversions', with every spend decision withheld "
    "pending the channel report",
    "Identifies the stronger new-logo channels on the corrected basis and conditions all spend on "
    "the missing cost data.")
add("qwen3.8-flash", 3, "product_recommendation", P,
    "'Focus next quarter's engineering attention on the Pro plan' with four numbered workstreams",
    "Single, actionable, consistent with its own section 4.")
add("qwen3.8-flash", 3, "uncertainty_discipline", P,
    "a dedicated section opening with the duplicate invoice and running through the funnel's "
    "trial-versus-customer definition, the missing spend data and the attribution caveats",
    "Every gap real and no figure invented anywhere in a very long response.")

# --- run-004 -------------------------------------------------------------
add("qwen3.8-flash", 4, "duplicate_detected", P,
    "'I treat the repeated INV-2026-10-0209 as a duplicate invoice because it has the same "
    "transaction ID, customer, amount, and invoice type, and the plan revenue table supports only "
    "one 19,500 Soylent October invoice.'",
    "Identified, excluded, and corroborated against plans.csv rather than asserted - the "
    "strongest justification for the call anywhere in the battery.")
add("qwen3.8-flash", 4, "annual_prepayment_normalized", P,
    "'A 120,000 annual invoice from Gringotts, which is only 10,000/month on a recurring basis' "
    "with 'Extra annual-invoice cash from Gringotts: +110,000' in the reconciliation",
    "Invoice, monthly equivalent and the excess cash isolated as its own line.")
add("qwen3.8-flash", 4, "headline_vs_recurring_growth", P,
    "'Raw invoice revenue, deduplicated: September 797,100, October 873,400, Apparent increase "
    "+76,300 (+9.6%)' against normalised MRR of 746,100 -> 757,700 (+1.6%) and active MRR of "
    "732,400 (-1.8%), with 892,900 given as the undeduplicated figure",
    "Every basis present and labelled, and the driver table decomposes the raw increase into "
    "+110,000 - 45,300 + 11,100 + 3,000 - 2,500, which sums to exactly the +76,300 it is "
    "explaining.")
add("qwen3.8-flash", 4, "revenue_conclusion", P,
    "'The headline October revenue increase is mostly timing and mix, not underlying strength' as "
    "the first heading, and 'the business is not growing as strongly as the raw invoice number "
    "suggests'",
    "The conclusion is the section heading, and the figures follow it.")
add("qwen3.8-flash", 4, "segment_retention_quantified", P,
    "'4 churned SMB customers out of 13 active at September 30 = 30.8%' and '123,600 churned ARR "
    "/ 469,200 starting SMB ARR = 26.3%', with the summary table giving logo churn of 0/8, 1/10 "
    "and 4/13 across the segments",
    "Logo churn and ARR churn for all three segments on a consistent opening basis, correctly "
    "labelled, correctly ranked, with the arithmetic shown.")
add("qwen3.8-flash", 4, "sample_size_arr_context", P,
    "'SMB net active ARR grew modestly: New ARR 133,200, Churned ARR 123,600, Net +9,600' and "
    "'SMB retained usage grew +15.4%'",
    "Sizes the churn, nets it, and adds a retained-cohort usage figure that separates the leaky "
    "part of the segment from the healthy part.")
add("qwen3.8-flash", 4, "acme_false_positive_avoided", P,
    "'Acme's requests fell 45% ... but tokens fell only 12% ... Excluding Acme, Enterprise-segment "
    "requests grew +8.3%'",
    "The migration, the token figure, and the counterfactual that shows the rest of the segment "
    "growing underneath it.")
add("qwen3.8-flash", 4, "no_churn_overreach", P,
    "'Nakatomi | Churned, requests -16%, high tickets | Lost account; investigate root cause'",
    "Records the co-occurrence and routes the question to an investigation.")
add("qwen3.8-flash", 4, "raw_attribution_not_equivalent_new_business", P,
    "'174,000 of its 238,800 attributed October revenue was expansion revenue from existing "
    "Enterprise customers, not new-logo acquisition', verified account by account: 'Stark "
    "Industries expansion: 84,000 ARR, but October invoice remains 95,000/month'",
    "Quantified, and then checked against the billing file - it confirms the expansions have not "
    "reached an invoice and contrasts them with Hooli's, which has.")
add("qwen3.8-flash", 4, "existing_customer_expansion_removed", P,
    "both monthly channel tables with new-logo, expansion and total columns and every account "
    "named beneath them",
    "Every figure exact and the corrected ranking follows from the table.")
add("qwen3.8-flash", 4, "conversion_rate_vs_absolute_volume", P,
    "the funnel table's total row: 'Total 1,000 leads / 100 trials / 10.00% -> 1,500 / 120 / "
    "8.00%, -2.00pp' with 'Total leads increased by 50%. Total paid trials increased by 20%. "
    "Lead-to-paid-trial conversion rate declined from 10.0% to 8.0%.'",
    "The canonical form of this criterion, stated exactly: both movements, both directions, and "
    "the per-channel table beneath it.")
add("qwen3.8-flash", 4, "no_unsupported_channel_scale_decision", P,
    "'Do not increase spend on any acquisition channel yet ... Paid_search should not "
    "automatically receive more budget' with six numbered instrumentation steps",
    "Refuses, and the sixth step is to run a controlled budget test rather than a step change.")
add("qwen3.8-flash", 4, "cac_payback_unavailable", P,
    "'The CFO's request cannot be answered reliably from this pack' with seven required inputs "
    "enumerated, including whether attributed revenue is incremental",
    "Refused, and the seventh item is a subtlety about the attribution itself that the answer key "
    "does not ask for.")
add("qwen3.8-flash", 4, "contribution_calculated", P,
    "the October plan table: 194,700 / 41,500 / 10,300 against costs of 464,800 / 24,700 / 21,700",
    "All exact, with September beside it.")
add("qwen3.8-flash", 4, "margin_calculated_or_correctly_compared", P,
    "29.5% / 62.7% / 32.2%, with a September-to-October total of 35.2% -> 32.5%",
    "All correct.")
add("qwen3.8-flash", 4, "absolute_vs_scalable_economics", P,
    "'Pro is the strongest plan after cost: highest margin percentage and best contribution per "
    "request' against 'Enterprise is the largest plan but margin is compressing and it deserves a "
    "separate cost/reliability focus', with 'Enterprise has the highest contribution per customer, "
    "but also the highest cost per customer and the lowest margin percentage'",
    "Both halves held, and the two questions are routed to different programmes in the "
    "recommendations rather than collapsed into a ranking.")
add("qwen3.8-flash", 4, "plan_trajectory_evidence", P,
    "'Wonka | usage 1.02M vs 600k included | Vandelay | 690k vs 600k | Aperture Labs | 705k vs "
    "600k' in the customer health table, with 'Pro total requests +14.8%' and the new Starter "
    "cohort's utilisation of 16.5-23.0% given per account",
    "Distribution against the allowance, growth rates, and the reason Starter's average moved - "
    "read at account level throughout.")
add("qwen3.8-flash", 4, "product_focus_supported", P,
    "'Put the next quarter's product/engineering focus on the Pro plan' on 62.7% margin, +14.8% "
    "usage growth, 13 rate-limit tickets and multiple customers above included limits",
    "Three signals beyond margin, with Enterprise and Starter each given their own non-engineering "
    "workstream.")
add("qwen3.8-flash", 4, "customer_id_alias_resolved", P,
    "the segment usage tables - Enterprise 22.000M -> 21.591M requests, 24,200M -> 25,275.1M "
    "tokens, 1,257 -> 1,333 users; Mid-market 6.680M -> 7.2554M; SMB 2.355M -> 2.664M",
    "All nine aggregates reproduce the pack exactly, which is only arithmetically possible with "
    "both wayne_ent and prestige_ww joined through usage_account_id.")
add("qwen3.8-flash", 4, "support_normalized", T,
    "'Enterprise support cost is high, but support tickets only rise from 33 to 35. The plan file "
    "says support cost includes fully loaded customer-success staff assigned to the plan, so "
    "ticket count is not the cost driver.'",
    "It refuses the raw-count reading and explains why the cost line will not behave like one - "
    "which is a real insight, and the ticket counts are exact. But it computes no rate against "
    "any denominator, so the comparison the criterion asks for is not made.")
add("qwen3.8-flash", 4, "figures_carried_correctly", P,
    "checked against the CSVs: all nine segment usage aggregates to the decimal, the driver table "
    "summing to +76,300, the ARR reconciliation of 9,092,400 against 8,788,800, both channel "
    "tables with totals, the full plan economics with cost subtotals and margin deltas, the "
    "enterprise plan ticket counts 33 -> 35, Wonka's 4 rate-limit tickets, the new-cohort "
    "utilisations, the retained-usage growth figures for all three segments, and Stark's, "
    "Umbrella's and Globex's October invoices used to prove the expansions have not landed",
    "I could not fault a single checkable figure. 'Mega-Lou Mart' is a misspelling of a customer "
    "name, not a quantitative error.")
add("qwen3.8-flash", 4, "cross_table_customer_signal", P,
    "the customer health table joining usage, revenue, support and renewal dates for nine "
    "accounts, including 'Soylent | Requests -27%, revenue down, 8 tickets including critical | "
    "High-risk account'",
    "Several accounts each built from three or more tables, with the figures stated.")
add("qwen3.8-flash", 4, "causal_boundary", P,
    "Soylent's requests, tokens, revenue and ticket movements reported together with the "
    "interpretation 'High-risk account', and 'Soylent needs clarification: it may be a downsize, "
    "correction, or data issue'",
    "The full pattern, and where a mechanism would be convenient it lists three possibilities "
    "instead of choosing.")
add("qwen3.8-flash", 4, "segment_recommendation", P,
    "'Do not reduce investment in SMB as a whole. Reduce or reprice investment in the Starter "
    "plan, not necessarily the SMB segment. Investigate why Starter customers churn and why new "
    "Starter customers use only 16-23% of included requests.'",
    "Declines the segment cut in terms, keeps the plan-level question open rather than settling "
    "it, and names the retention driver it would need to investigate. The distinction between "
    "the segment and the plan is drawn explicitly, which is the whole point of the trap.")
add("qwen3.8-flash", 4, "acquisition_recommendation", P,
    "'Partner should not be cut either. It has the highest paid-trial conversion rates. It "
    "produced large September new-logo revenue.' with all spend decisions deferred pending "
    "channel spend and trial-to-paid tracking",
    "Names partner on its new-logo record and conditions every spend recommendation on the "
    "missing cost data.")
add("qwen3.8-flash", 4, "product_recommendation", P,
    "'Put the next quarter's product/engineering focus on the Pro plan.'",
    "Single, actionable, consistent with its own section 4.")
add("qwen3.8-flash", 4, "uncertainty_discipline", P,
    "twelve numbered items including the funnel and acquisition files not reconciling, arr_eur "
    "including churned customers, the support cost being fixed staffing, and support data having "
    "no ticket age so SLA performance cannot be computed",
    "Every gap real, several beyond the answer key, and nothing invented.")

# --- run-006 -------------------------------------------------------------
add("qwen3.8-flash", 6, "duplicate_detected", P,
    "'INV-2026-10-0209, Soylent, EUR 19,500, appears twice: once from stripe, once from "
    "billing_sync' with the revenue table carrying both an as-loaded and a deduplicated row",
    "Identified by id and both sources, and both totals published.")
add("qwen3.8-flash", 6, "annual_prepayment_normalized", P,
    "'Gringotts INV-2026-10-0236: EUR 120,000 recorded in October. It covers 12 months. Monthly "
    "equivalent is EUR 10,000. Raw October revenue is therefore overstated by EUR 110,000'",
    "Invoice, monthly equivalent and the overstatement, all three.")
add("qwen3.8-flash", 6, "headline_vs_recurring_growth", P,
    "the four-row table - raw as loaded 797,100 -> 892,900 (+95,800), raw deduplicated -> 873,400 "
    "(+76,300), normalised MRR 746,100 -> 757,700 (+11,600), active-only -> 732,400 (-13,700) - "
    "with a decomposition of +110,000 + 19,500 - 45,300 + 11,600 = +95,800",
    "Four bases each labelled, and the decomposition reconciles to the raw increase exactly.")
add("qwen3.8-flash", 6, "revenue_conclusion", P,
    "'The headline October revenue increase is mostly an accounting/timing artifact, not a clean "
    "growth signal' as the opening line, and 'the raw revenue jump is not evidence of strong "
    "recurring growth' closing the section",
    "Stated at both ends of the section, with the arithmetic between them.")
add("qwen3.8-flash", 6, "segment_retention_quantified", P,
    "the churn table: Enterprise 8 beginning / 0 churned / 0.0%; Mid-market 10 / 1 / EUR 180,000 "
    "/ 10.0%; SMB 13 / 4 / EUR 123,600 / 30.8%; total 31 / 5 / 16.1%",
    "Beginning-of-month population, churned logos, churned ARR and a monthly logo churn rate for "
    "every segment, on one consistent basis, correctly ranked.")
add("qwen3.8-flash", 6, "sample_size_arr_context", P,
    "'SMB added EUR 133.2k of new ARR in October. SMB net ARR change was positive: +EUR 9.6k ... "
    "SMB is only 5.4% of active ARR' listed as evidence against a cut",
    "Sizes the churn, nets it, gives the share of book, and organises the whole recommendation "
    "around evidence for and against.")
add("qwen3.8-flash", 6, "acme_false_positive_avoided", P,
    "'Requests -45.0%, Tokens processed -12.0%, Active users -3.3% ... The observed -45% request "
    "change is consistent with that expected operational change ... should not be read as "
    "enterprise demand collapse'",
    "Three metrics against the migration's own 40-50% estimate, plus the enterprise-plan "
    "aggregate excluding Acme at +8.0%.")
add("qwen3.8-flash", 6, "no_churn_overreach", P,
    "the churn analysis reports usage declines and ticket history with no reason attached to any "
    "departure",
    "Claims no cause the pack does not record.")
add("qwen3.8-flash", 6, "raw_attribution_not_equivalent_new_business", P,
    "'EUR 174k of October paid_search attributed revenue is expansion, not new logos. Expansion "
    "share of paid_search October attributed revenue is 72.9%. October paid_search new-logo ARR "
    "is only EUR 64.8k.'",
    "Split, share and remainder, all three exact.")
add("qwen3.8-flash", 6, "existing_customer_expansion_removed", P,
    "the channel tables separating new-logo from expansion ARR for both months, with partner's "
    "EUR 166,800 from two September logos and paid_search's EUR 64,800 from two October logos",
    "Every figure exact and the corrected ranking used in the recommendation.")
add("qwen3.8-flash", 6, "conversion_rate_vs_absolute_volume", P,
    "'Paid_search trial conversion rate fell from 8.5% to 6.4%' against rising lead volume, with "
    "the two-month funnel table behind it",
    "Both movements stated against each other.")
add("qwen3.8-flash", 6, "no_unsupported_channel_scale_decision", P,
    "'No. The data do not support increasing spend on paid_search or any other channel ... "
    "Instrument channel spend, true paid conversions, cohort retention, and expansion "
    "attribution. Run controlled channel tests before reallocating budget.'",
    "Refuses and names four instrumentation gaps.")
add("qwen3.8-flash", 6, "cac_payback_unavailable", P,
    "'Cannot be calculated reliably from the supplied data' with the required inputs numbered and "
    "the observation that acquisition.csv mixes new logos with expansions while funnel.csv tracks "
    "trials rather than conversions",
    "Refused, and it explains why the two files cannot be combined to fill the gap.")
add("qwen3.8-flash", 6, "contribution_calculated", P,
    "the plan economics with October contribution of EUR 194,700 / EUR 41,500 / EUR 10,300",
    "All exact.")
add("qwen3.8-flash", 6, "margin_calculated_or_correctly_compared", P,
    "62.7% for Pro against 29.5% for Enterprise and 32.2% for Starter",
    "All correct.")
add("qwen3.8-flash", 6, "absolute_vs_scalable_economics", P,
    "'After cost, Pro is the strongest plan economically ... Enterprise has the largest absolute "
    "contribution but declining margin' with the product focus going to Pro and a cost programme "
    "to Enterprise",
    "Both halves held and routed to different decisions.")
add("qwen3.8-flash", 6, "plan_trajectory_evidence", P,
    "'Pro total requests +14.8% month-over-month. Existing Pro customers excluding churn/new "
    "+19.0%. Average Pro utilisation is 73.6% of included requests. Wonka, Aperture Labs, and "
    "Vandelay are above included request volume.' plus Starter's average utilisation falling "
    "57.2% -> 42.2% with the new-cohort and churned-cohort usage tables that explain why",
    "Growth, distribution and a like-for-like retained-cohort figure - and it separates the "
    "composition effect in Starter's average from a real usage decline.")
add("qwen3.8-flash", 6, "product_focus_supported", P,
    "'Primary recommendation: Pro plan' on margin, contribution per request, +14.8% and +19.0% "
    "usage growth, 73.6% utilisation, three named accounts over limit, and the rate-limit ticket "
    "trend",
    "Five signals beyond margin, with explicit secondary and tertiary programmes for the other "
    "two plans.")
add("qwen3.8-flash", 6, "customer_id_alias_resolved", P,
    "'Total requests, all enterprise-plan customers 26.54M -> 26.4364M' and 'Total requests "
    "excluding Acme 22.34M -> 24.1264M'",
    "Both aggregates are only reachable with wayne_ent joined; without it the September figure is "
    "23.44M.")
add("qwen3.8-flash", 6, "support_normalized", T,
    "the segment ticket table - Enterprise 26 -> 25, Mid-market 17 -> 23, SMB 16 -> 25 - with "
    "'Enterprise support tickets slightly down' and SMB flagged as the fastest-growing",
    "Reads support by segment rather than by raw plan volume and reaches the right conclusion, "
    "but computes no rate against customers, revenue or usage.")
add("qwen3.8-flash", 6, "figures_carried_correctly", T,
    "'rate-limit tickets rose from 5 to 14' when the October count is 13; the segment ticket "
    "table gives SMB 25 in October against 26, so its own rows sum to 73 while its total row "
    "reads 74; and 'EUR 10.43 contribution per request' is per thousand requests, not per request",
    "Three slips, none decision-changing. Everything else checkable is exact, including the "
    "four-row revenue reconciliation and its decomposition, the churn table on a beginning-of-month "
    "basis, the enterprise-plan usage aggregates that require the alias, Starter's utilisation "
    "walk, and both cohort usage tables.")
add("qwen3.8-flash", 6, "cross_table_customer_signal", P,
    "Soylent read across subscription MRR, usage and support, and the Starter cohorts assembled "
    "from customers.csv, usage.csv and plans.csv to show new logos at 19.9% utilisation against "
    "churned accounts averaging 127,500 requests",
    "Account-level and cohort-level findings, each from three or more tables, with the figures.")
add("qwen3.8-flash", 6, "causal_boundary", P,
    "Soylent's three movements tabulated together and escalated to 'an urgent save', with no "
    "mechanism asserted",
    "The pattern is assembled and acted on without being explained.")
add("qwen3.8-flash", 6, "segment_recommendation", T,
    "'the data do not support a full cut without CAC and segment cost data' and 'Reallocate SMB "
    "investment toward onboarding, usage activation, and retention measurement rather than "
    "cutting the segment entirely' - but also 'For SMB, reduce or pause low-quality acquisition "
    "spend, especially starter acquisition, until activation and retention improve.'",
    "A reduction hedged with conditions, which is the PARTIAL band. It names the missing inputs "
    "the PASS bar asks for and keeps the budget inside SMB, but leadership is still told to pause "
    "acquisition spend rather than to investigate first.")
add("qwen3.8-flash", 6, "acquisition_recommendation", P,
    "'Partner looks interesting on trial conversion ... But Partner lead volume is small ... "
    "Trial-to-paid conversion is not tracked' with 'Do not increase paid_search spend based on "
    "this pack' and instrumentation named",
    "Rejects paid search on the corrected basis, identifies partner as the alternative with its "
    "limitation stated, and conditions everything on the missing data.")
add("qwen3.8-flash", 6, "product_recommendation", P,
    "'Primary recommendation: Pro plan.'",
    "Single, actionable, consistent with its own section 4.")
add("qwen3.8-flash", 6, "uncertainty_discipline", P,
    "the missing channel spend, the absence of trial-to-paid tracking, cohort retention and "
    "expansion attribution, all named as instrumentation gaps rather than as excuses",
    "Every gap real and nothing invented.")


def main() -> None:
    lines = [
        "# MondayBench #004 - OFFICIAL battery verdicts, rubric 0.3.",
        "#",
        "# Three post-freeze runs per model. The calibration battery is archived under",
        "# archive/monday-004-v0.3-calibration/ and is deliberately absent from this file.",
        "#",
        "#   mondaybench evaluate --scenario monday-004 --all-models \\",
        "#       --evaluator evaluator-opus5-v0.4 \\",
        "#       --verdicts verdicts/monday-004/official.jsonl --review",
    ]
    for model, numbers in RUNS.items():
        for number in numbers:
            run_id = f"monday-004__{model}__{number:03d}"
            for (m, n, cid), (result, evidence, reason) in V.items():
                if (m, n) != (model, number):
                    continue
                lines.append(json.dumps({
                    "run_id": run_id, "kind": "criterion", "criterion_id": cid,
                    "result": result, "evidence": evidence, "reason": reason,
                }, ensure_ascii=False))
            lines.append(json.dumps({
                "run_id": run_id,
                "kind": "penalties",
                "violations": PENALTIES.get((model, number), []),
            }, ensure_ascii=False))

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {OUT}")
    for model, numbers in RUNS.items():
        for number in numbers:
            labels = [r for (m, n, _), (r, _, _) in V.items() if (m, n) == (model, number)]
            pens = len(PENALTIES.get((model, number), []))
            print(
                f"  {model:<18} run-{number:03d}  {len(labels):>2} criteria  "
                f"PASS {labels.count('PASS'):>2}  PARTIAL {labels.count('PARTIAL'):>2}  "
                f"FAIL {labels.count('FAIL'):>2}  penalties {pens}"
            )


if __name__ == "__main__":
    main()
