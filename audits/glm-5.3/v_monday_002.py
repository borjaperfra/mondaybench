"""monday-002 "Moving Targets" verdicts for glm5.3 - rubric 0.2, 20 criteria.

All three runs choose Option A. Ground truth's answer is B: Priya's delta review
is asynchronous from a submitted diff (slack.md 11:18 and her email), and Marcus
had both recovery approaches prepared on Friday (slack.md 14:18), so the review
can run 09:07-09:32 inside Priya's first window and Marcus can deploy 09:32-10:17
inside his. B carries <1% session-reset risk against A's 8%. A is time-viable,
which is exactly what the PARTIAL band on `choose_option_b` is for.

No penalty is recorded on any of the three. Each infeasibility claim is a wrong
INFERENCE over supplied constraints that are themselves quoted correctly, not an
invented fact, and every recommended plan is executable. The cost is carried by
choose_option_b, option_b_sequence and schedule_feasibility.
"""
P, R, F = "PASS", "PARTIAL", "FAIL"

VERDICTS = {
    "001": dict(
        launch_state=(P, "'Friday's production attempt failed on shard eu-03 before rollout opened'; 'Rollout is still closed'; 'Path decision is mine (no exec gate)'"),
        stale_external_actions=(P, "'Do not call Zenith about renewal risk - renewed and closed'; 'Do not send pricing to Initech procurement or any external party'; 'Do not send the customer announcement ... it is Daniel's send, not mine'"),
        current_owners=(P, "Marcus deploys, Priya verifies, Sam opens rollout, Daniel sends the announcement, the user decides the path and coordinates"),
        executive_gate_superseded=(P, "'Maya has twice declined to add an approval step'; 'Do not request Maya's approval as a gate - she explicitly removed it'; the 'Maya approval' task is listed as superseded"),
        pricing_authority=(P, "'pinned v4 workbook is non-authoritative; Daniel's 09:07 numbers are internal-only; nothing external until a public announcement (no date set)'"),
        ownership_supersession=(P, "'Daniel holds the final announcement draft + Atlas list and sends only after Sam confirms rollout is open'"),
        choose_option_b=(R, "chooses A, which is time-viable, and schedules it correctly - but on the false ground that 'B cannot physically complete today'. The 25-minute delta review can run 09:07-09:32 inside Priya's first window, leaving Marcus 09:32-10:17 for the 45-minute deploy. A's 8% session-reset risk is accepted where B's is under 1%"),
        option_b_sequence=(R, "no B sequence is produced, but the gating dependency is stated - 'never deploy it before Priya's delta review' - and the rest of the chain (deploy, post-deploy verification, Sam rollout) is ordered correctly for the path chosen"),
        schedule_feasibility=(R, "the A schedule is coherent and fits Marcus 09:15-09:35, Priya 10:25-10:45, Sam 10:45-11:00 and the before-12 window; no feasible B schedule is produced and B's feasibility is computed wrongly"),
        parallelize_work=(P, "'09:45-10:55 - Expansion reconciliation to Maya (due 11:00) using the Priya-unavailable window' while the delegated deploy runs"),
        immediate_release_decision=(P, "'09:07-09:15 - Decide and dispatch' is the first action, on the stated ground that Marcus's window opens 09:15 and closes 10:20"),
        expansion_before_11=(P, "'09:45-10:55 - Expansion reconciliation to Maya (due 11:00; board locks 11:30)'"),
        globex_priority=(P, "'Globex (top priority): renewal in 18 days, expansion pending procurement, 3 open tickets including high-sev SSO blocking admins, admin logins -61%' - renewal, expansion, admin usage and support read together"),
        avoid_acme_false_positive=(P, "'Acme's -45% usage is contractually explained (batch-processing shift) - not a problem'; listed under 'Not problems today'"),
        expansion_fully_reconciled=(P, "'gap EUR54k = Wayne EUR18k + Globex EUR12k + Soylent EUR10k + Wonka EUR14k' - closes to the full 54"),
        causal_boundary=(P, "'Stated causes exist only for Wayne (Oct move, signed amendment) and Globex (procurement pending)'; 'Do not attribute causes to Soylent/Wonka reductions in the board pack'"),
        customer_signal_integration=(P, "Globex, Acme, Wonka and Soylent each read across accounts, contracts and support; renewal days, usage, admin logins and ticket severity all match the files"),
        orion_missing_evidence=(P, "'Do not send any Orion status until the org ID and live flag are confirmed'; names both org_17A vs org_71A and the live scim_enabled read"),
        conditional_launch_timing=(F, "'~09:40 - Confirm to Atlas (via Laura): launch is on today; rollout opens ~10:45-11:00, inside their window' - a firm external commitment to a rollout window, issued before Priya's verification and Sam's rollout have happened, with no conditionality anywhere in the response. PARTIAL is for a non-firm promise with thin conditionality; this is a firm one"),
        no_unsupported_causality=(R, "'Soylent: -22%/-28% plus a medium ticket citing slower onboarding. Possible link (hypothesis only)' - an unsupported cause offered, but explicitly as a hypothesis, which is the PARTIAL band exactly"),
        _noise={},
        _pen=[],
    ),
    "002": dict(
        launch_state=(P, "'Friday's production attempt failed on shard eu-03 before rollout opened - no customer impact'; 'Product (me) picks the path'; Maya's gate superseded"),
        stale_external_actions=(P, "'Don't call Zenith about renewal risk'; 'Don't send anything to Initech procurement or quote pricing externally'; 'Don't send the customer announcement yourself - Daniel owns it'"),
        current_owners=(P, "'Availability: Marcus 09:15-10:20 only; Priya 09:00-09:35 and 10:25-12:30; Sam and Daniel 09:00-12:30' with the matching assignments; Daniel sends, Sam opens rollout, Priya verifies"),
        executive_gate_superseded=(P, "'Maya has explicitly declined another executive gate, so the get Maya approval by 09:15 task is superseded'"),
        pricing_authority=(P, "'Pinned v4 workbook is explicitly not authoritative; Daniel's 09:07 scenario (EUR2,500 / 40 seats / EUR55) is internal-only' - both figures match slack 09:07 exactly"),
        ownership_supersession=(P, "'Daniel holds Julia's final draft + Atlas recipient list and sends only after Sam confirms rollout is open'"),
        choose_option_b=(R, "chooses A, which is time-viable, and argues it on schedule slack rather than on a false impossibility. Still the wrong call: it charges the 25-minute delta review against Marcus's 65-minute window when the review is asynchronous and does not need him, and it accepts 8% session-reset risk over B's under 1%"),
        option_b_sequence=(R, "the delta-review gate is stated - 'Don't deploy 2.9.5-patch or anything changing code from 2.9.4 without Priya's delta review' - but no B sequence is laid out; the chosen chain is otherwise correctly ordered"),
        schedule_feasibility=(R, "a coherent A schedule that respects every window and the 12:00 deadline; B's slack is miscomputed as 'near-zero' by charging Marcus for review time he is not needed for"),
        parallelize_work=(P, "'09:50-10:50 - Build expansion reconciliation' and '09:45-10:20 - Escalate Globex G-441' both run while the deploy is delegated"),
        immediate_release_decision=(P, "'09:07-09:15 - Post decision in #enterprise-launch' is the first item, with Marcus's 09:15 start as the driver"),
        expansion_before_11=(P, "'send to Maya by ~10:50 (deadline 11:00; board locks 11:30)'"),
        globex_priority=(P, "'Globex (top): Renewal in 18 days, EUR12k expansion stuck in procurement, 3 open tickets including a high-sev SSO blocker (G-441) consistent with the -61% admin-login drop'"),
        avoid_acme_false_positive=(P, "'The usage drop matches the contractually approved batch-processing shift - not a churn signal; just confirm renewal mechanics'"),
        expansion_fully_reconciled=(P, "'Target EUR180k vs expected EUR126k (gap EUR54k). Wayne EUR18k + Globex EUR12k = EUR30k documented. Soylent EUR10k + Wonka EUR14k have no stated cause' - all four components, closing to 54"),
        causal_boundary=(P, "'Don't invent causes for the Soylent/Wonka reductions in the board reconciliation'; documented causes are attached only to Wayne and Globex"),
        customer_signal_integration=(P, "Globex, Soylent, Wonka and Acme each combine renewal days, expansion delta, usage/admin movement and tickets; every figure matches accounts.csv, contracts.csv and support.csv"),
        orion_missing_evidence=(P, "'need the ticket record and a live flag read before any reply' - names the canonical org ID and the live scim_enabled value"),
        conditional_launch_timing=(R, "'Confirm to Atlas via Laura: launch on for today, rollout ETA ~11:00, inside their window; final confirm when Sam opens' - labelled an ETA and deferred to Sam's confirmation, so not a firm promise, but 'launch on for today' is still asserted before verification"),
        no_unsupported_causality=(P, "the one link offered is hedged as correlation - G-441 'consistent with the -61% admin-login drop' - and Wonka is explicitly 'no assumed cause'; nothing about production, Orion or a customer is invented"),
        _noise={},
        _pen=[],
    ),
    "003": dict(
        launch_state=(P, "'Build 2.9.4 is staging-verified'; 'Friday's production attempt failed on shard eu-03 before rollout opened - no customer impact'; 'Product (me) picks'"),
        stale_external_actions=(P, "'Don't call Zenith about renewal risk'; 'Don't send pricing to Initech procurement or anyone external'; 'Don't send the Enterprise Controls customer announcement - Daniel owns it'"),
        current_owners=(P, "Marcus deploys, Priya verifies, Sam opens rollout, Daniel sends, the user decides - each named with its window"),
        executive_gate_superseded=(P, "'Maya approval task is superseded - she removed the executive gate Thursday'"),
        pricing_authority=(P, "'Only Daniel's Fri 09:07 values (EUR2,500 platform / 40 seats / EUR55 per extra seat) are current - internal only. Pinned v4 workbook is explicitly not authoritative'"),
        ownership_supersession=(P, "'Sarah out Monday; Daniel holds the final draft + Atlas list and sends only after Sam confirms rollout is open'"),
        choose_option_b=(R, "chooses A, which is time-viable, with a correct A schedule - but rejects B as 'infeasible' on the added premise that 'the diff comes from Marcus, who starts 09:15'. Marcus had both approaches prepared on Friday and Priya's review is asynchronous from a submitted diff, so the review can start at 09:07. The lower-risk option is discarded"),
        option_b_sequence=(R, "'Option B needs a 25-min delta review first' states the gate, and the executed chain (deploy, post-deploy verification, Sam rollout) is correctly ordered; no B sequence is produced"),
        schedule_feasibility=(R, "the A schedule fits every window with the 12:00 deadline explicitly checked; B's feasibility is computed against a start time the sources do not impose"),
        parallelize_work=(P, "'09:45-10:30 - Expansion reconciliation to Maya' plus Orion and Globex in the same window while the deploy is delegated"),
        immediate_release_decision=(P, "'09:07-09:12 - Decide and post' is the first action"),
        expansion_before_11=(P, "'09:45-10:30 - Expansion reconciliation to Maya (deadline 11:00; board pack locks 11:30)'"),
        globex_priority=(P, "'Globex (top): Renewal in 18 days + high-sev SSO ticket blocking admin setup + admin logins -61%. The expansion slip is explained (procurement) - the live risk is G-441'"),
        avoid_acme_false_positive=(P, "'the usage drop matches the contractually approved batch-processing shift - routine tracking, not escalation'; 'don't frame Acme's usage drop as churn'"),
        expansion_fully_reconciled=(P, "'EUR54k = Wayne -EUR18k + Globex -EUR12k + Soylent -EUR10k and Wonka -EUR14k'"),
        causal_boundary=(P, "'lead with arithmetic (EUR54k = 18+12+10+14), state causes only where documented ... list Soylent/Wonka as unexplained amounts, hypotheses clearly separated'"),
        customer_signal_integration=(P, "Globex, Wonka, Soylent and Acme each built from accounts, contracts and support together; Wayne, Stark and Zenith correctly set aside"),
        orion_missing_evidence=(P, "'need the CRM/ticket mapping plus a fresh flag read; no evidence currently settles it'"),
        conditional_launch_timing=(P, "'rollout expected ~11:00, final confirmation once Sam opens', reinforced by 'Don't tell Atlas launched before verification passes and rollout opens; don't promise 10:30'"),
        no_unsupported_causality=(P, "'Whether Globex's SSO failures are driving the admin-login decline - plausible but unproven; keep out of the board pack's causal claims' - raised as unknown and not relied on"),
        _noise={},
        _pen=[],
    ),
}
