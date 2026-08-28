"""Recorded verdicts for the monday-003 OFFICIAL battery, rubric 0.3.

Seven models, three runs each, all generated after the freeze against the frozen
prompt `aaf788f309d955d2b427c86fe7d95d2bbf88575fde7306adcfd74b0ec4a4103f`.

None of the calibration responses are reused. The v0.3 rubric was designed while
reading the v0.2 and v0.3-calibration responses, so those cannot also be the
evidence it publishes; they are archived under
`archive/monday-003-v0.3-calibration/` with their own verdicts.

Judged following `evaluators/monday-003/judge-prompt.md`: semantics not phrasing,
no credit for absent information, either chain may be nominated as the critical
path, a criterion may be satisfied by what the plan does as well as by what the
prose asserts, `factual_plan_accuracy` is scored against `factual_anchors` and
nothing else, and where a response sits between two labels choose the lower.

Penalties follow `penalty-judge-prompt.md`: a penalty needs something the
response asserts or recommends, never an omission. Keeping Marcus on both
engineering items is recorded in the answer key as feasible and is priced by the
rubric, never by a dependency penalty.

WARNING for anyone reading this later. Rubric 0.3 is shared with
`archive/monday-003-v0.3-calibration/verdicts/`, so those files would replay
against these runs without raising an error and would score the wrong text: they
are keyed by run id, and `monday-003__<model>__001` names a different response
there. Official runs are served only from this directory.

Nothing here assigns points. `mondaybench evaluate --verdicts` does the scoring.
"""

from __future__ import annotations

import json
from pathlib import Path

P, R, F = "PASS", "PARTIAL", "FAIL"

CRITERIA = [
    "sso_chain",
    "contoso_blocker_chain",
    "pricing_dependency",
    "security_state_stale",
    "board_dependency",
    "scarce_resource_allocation",
    "marcus_reserved_for_sso",
    "formatter_ownership",
    "elena_migration_fallback",
    "monday_plan",
    "concurrent_sso_and_contoso",
    "pricing_board_parallel",
    "formatting_urgent_not_blocking",
    "contoso_compliance_is_urgent",
    "stale_task_list_overridden",
    "sso_state_reconstructed",
    "onboarding_state_reconstructed",
    "contoso_state_separated",
    "factual_plan_accuracy",
    "earliest_feasible_delivery",
    "uncertainty_discipline",
]

VERDICTS: dict[str, dict[str, tuple[list, list]]] = {}


def run(model: str, number: str, rows: list, penalties: list | None = None) -> None:
    VERDICTS.setdefault(model, {})[number] = (rows, penalties or [])


# ---------------------------------------------------------------------------
# DeepSeek V4 Flash - 95.0 / 95.0 / 95.0. The most consistent model in the
# battery, and the only one whose three runs land on the same number.
# ---------------------------------------------------------------------------

run("deepseek-v4-flash", "001", [
    (P, "'Enterprise SSO | Elena schema migration (3h) -> Marcus SSO compatibility patch (4h) -> QA regression (2h) -> Marcus production rollout (1h) | Wed EOD'"),
    (P, "'Contoso compliance | Elena schema migration (3h) -> Daniel Contoso permission patch (3.5h + 0.5h Marcus walkthrough) -> Julia compliance export (1h) | Tue 16:00'; the format fix is a separate parallel item"),
    (R, "has the mockup route - 'Use design mockups for the approval pack if available so she does not wait for live screenshots' - but never states that packaging approval gates the public page"),
    (P, "'Security review for Enterprise SSO is already approved (Maya's Friday email)' and 'mark security review as complete'"),
    (P, "'Once it lands, Elena kicks off the 90-minute backfill'; the migration is listed as blocking 'the revenue board backfill'"),
    (P, "'Contoso's permission patch should be reassigned to Daniel. If Marcus takes it, his 2h becomes a bottleneck on the SSO path for no reason', with the 30-minute walkthrough booked for the morning"),
    (P, "'Protect Marcus for the SSO compatibility patch... Do not pull him into Contoso or onboarding instrumentation'"),
    (P, "'Have Julia fix the export date format today for the Contoso Tuesday demo'"),
    (R, "'Elena is out from Wednesday noon - the migration and backfill must happen before then. Our plan does this Monday' names the constraint and schedules around it, but the production-permission transfer and the Daniel fallback are absent"),
    (P, "eight numbered actions, tracker correction first, Elena started second, every delegation issued this morning"),
    (P, "'Daniel's Contoso permission patch and Marcus's SSO compatibility patch can proceed in parallel after the schema migration'"),
    (P, "'Point Sarah at parallel delivery - pricing page, board pack non-revenue work, and packaging approval pack'"),
    (P, "'Contoso's export is not broken. There are two separate issues: date formatting and delegated-admin permissions' and 'not a production break - it is a format preference plus a permission bug'"),
    (P, "'Reply to Contoso and the CEO now - confirm the compliance export will be delivered by Tuesday 16:00'"),
    (P, "Security marked complete, instrumentation removed as a launch blocker, and the Contoso ticket split into its two real items"),
    (P, "chain outstanding, Security approved, Wednesday EOD intact"),
    (P, "'onboarding instrumentation is not required for launch', with the onboarding launch work sitting with Julia"),
    (P, "'Contoso's export is not broken. There are two separate issues' - and only the permission bug gates the Tuesday delivery"),
    (P, "every anchor it uses is intact: the four SSO durations, Daniel at 3.5h plus a half-hour walkthrough, Marcus at 2h, the 1h export, the 90-minute backfill, Marcus unavailable Tue 09:00-13:00, Elena out from Wednesday noon, Tue 16:00 and Wed EOD"),
    (P, "'Enterprise SSO: Tuesday 14:00 - ... Marcus rolls out immediately after his Atlas session ends at 13:00', which is the lower bound exactly"),
    (P, "names the QA-defect window against Marcus's blocked Tuesday morning, the risk that a 30-minute walkthrough is not enough, and the unknown of whether Sarah has mockups at all"),
])

run("deepseek-v4-flash", "002", [
    (P, "'Enterprise SSO critical path: billing_schema_migration -> Marcus compatibility patch -> QA regression -> production rollout' with a clock slot against each step"),
    (P, "'Contoso compliance critical path: billing_schema_migration -> Contoso permission patch -> Contoso compliance export'; the format fix runs in parallel and gates nothing"),
    (P, "'Sarah builds the packaging approval pack from mockups and submits before 12:00. Do not wait for the pricing page; Priya confirmed mockups are acceptable' and 'only the public pricing page waits for approval'"),
    (P, "'Security review for Enterprise SSO is already approved - the tracker is stale' and 'Maya approved the current scope on Friday'"),
    (P, "'Elena kicks off billing_backfill at 12:10; it completes by 13:40' with 'revenue charts after the backfill completes'"),
    (P, "'Contoso permission patch should not stay on Marcus. Marcus is the only person who can do the SSO compatibility patch, so Daniel should own the Contoso patch. Daniel still needs a 30-minute handoff from Marcus'"),
    (P, "'Marcus is the only person who can do the SSO compatibility patch' and 'Marcus's 3h hold should be released'"),
    (P, "'Julia starts export format fix now... This gets Contoso to DD/MM/YYYY for Peter's demo'"),
    (F, "Elena's Wednesday-noon departure, the production-permission transfer and the Daniel fallback appear nowhere in the plan or the risks; the only Elena instruction is to start the migration"),
    (P, "eight numbered actions on a 09:10 clock, migration first, every delegation issued before the migration lands"),
    (P, "'12:40-16:10: Daniel: contoso_permission_patch' against '12:40-16:40: Marcus: api_compatibility_patch' - the two chains run side by side out of the same root"),
    (P, "'Sarah's non-revenue board pack and pricing page work can proceed while the packaging approval is pending', with the approval pack submitted before noon"),
    (P, "'Date format request from Peter - cosmetic, for Tuesday's demo'"),
    (P, "'Delegated-admin permission bug - real blocker for Anja's compliance export, hard deadline Tuesday 16:00', delivered Monday 17:10"),
    (P, "all four: Security marked approved, instrumentation demoted, the Contoso ticket reassigned and split, and Sarah told not to wait for the page"),
    (P, "chain outstanding, Security approved for the current scope, and the Wednesday EOD commitment met by Tuesday"),
    (P, "'Onboarding instrumentation is not a launch blocker... Marcus has 3h incorrectly held for it', with 'Julia's onboarding launch is independent'"),
    (P, "'Contoso export broken is actually two separate issues: 1. Date format request from Peter - cosmetic... 2. Delegated-admin permission bug - real blocker'"),
    (P, "the arithmetic is exact and every anchor survives: migration 09:10-12:10, backfill 12:10-13:40, walkthrough 12:10-12:40, Daniel 12:40-16:10 at his 3.5h rate, Julia 16:10-17:10, Marcus 12:40-16:40, QA Tue 09:00-11:00, rollout Tue 13:00-14:00 behind the Atlas session, Tue 16:00 CET and the noon committee cutoff"),
    (P, "'Enterprise SSO production rollout: Tuesday 14:00' - the lower bound, supported by the schedule it gives"),
    (P, "'There is no explicit QA step for the Contoso permission patch. Julia should verify the export using a delegated-admin token before sending' - the sharpest unknown in this run"),
])

run("deepseek-v4-flash", "003", [
    (P, "'billing_schema_migration (Elena) -> api_compatibility_patch (Marcus) -> sso_regression (QA) -> sso_production_rollout (Marcus)' as a code block, called 'the controlling path'"),
    (P, "'Parallel Contoso path after the same migration: billing_schema_migration -> 30-min Marcus walkthrough -> contoso_permission_patch (Daniel) -> contoso_compliance_export (Julia)'"),
    (P, "'Pricing page cannot go public until packaging approval clears, but the approval pack can be submitted before the page is live' with 'Priya said mockups are acceptable, so she should not wait for the live pricing page'"),
    (P, "'Mark Security review as complete. Maya already approved the current scope; no re-review required'"),
    (P, "'Board revenue charts wait for the billing backfill, not just the migration' - the distinction stated outright"),
    (P, "'Marcus is the bottleneck, so reassign the Contoso permission patch to Daniel and keep Marcus focused on the SSO compatibility patch', with the walkthrough at 12:10-12:40"),
    (P, "'Four focused hours. Do not delegate this; Marcus is the only person who can complete it', and the instrumentation removed as a launch blocker"),
    (P, "'Contoso date-format fix - Julia, 2 hours. Independent of the migration and permission patch; needed for Tuesday's demo'"),
    (F, "Elena's Wednesday-noon departure, the permission transfer and the Daniel fallback are absent; the risks cover the migration overrun but not who executes if she is gone"),
    (P, "eight numbered actions with clock windows, stale tracker first, Elena at 09:10-12:10, and the walkthrough slotted into Marcus's forced wait"),
    (P, "'Daniel: contoso_permission_patch, ~3.5 hours' running against 'Marcus builds SSO compatibility patch - Marcus, ~12:40-16:40'"),
    (P, "'Sarah prepares the packaging approval pack using mockups... She can continue the pricing page and board pack non-revenue sections in parallel'"),
    (P, "'Contoso broken export is not broken: it is a date-format preference plus a separate delegated-admin permission bug'"),
    (P, "'Contoso compliance export needs the permission patch first. Deadline is Tuesday 16:00'"),
    (P, "all four corrected in the opening action: instrumentation removed, Security marked complete, the Contoso ticket split, and Sarah freed from the live page"),
    (P, "chain outstanding, Security approved, and 'SSO remains on track for Wednesday EOD, with Tuesday afternoon as the likely delivery'"),
    (P, "'Onboarding launch - Julia can complete it before Friday noon; it does not depend on Marcus's instrumentation'"),
    (P, "'not broken: it is a date-format preference plus a separate delegated-admin permission bug', with only the permission bug on the dated chain"),
    (P, "no substitutions: the four SSO durations, Daniel at 3.5h, the 30-minute walkthrough, the 90-minute backfill, Marcus's Tuesday 09:00-13:00 absence, Tue 16:00, Wed EOD and the noon committee cutoff are all carried correctly"),
    (P, "'Marcus is unavailable Tuesday 09:00-13:00 for the Atlas pre-rollout session, so earliest realistic SSO delivery is Tuesday 14:00' - the bound, with the reason for it"),
    (P, "flags that it is assuming Elena has no competing meetings, that the QA estimate is conditional, and that a 30-minute handoff may not be enough for Daniel"),
])

# ---------------------------------------------------------------------------
# GLM 5.2
# ---------------------------------------------------------------------------

run("glm5.2", "001", [
    (P, "the dependency table gives compatibility patch <- migration, regression <- patch, rollout <- regression, with 'Elena is the single upstream bottleneck'"),
    (P, "'contoso_compliance_export | contoso_permission_patch | Will clear Mon ~14:30'; the formatter sits in parallel work with no dependant"),
    (R, "'pricing_page public | packaging committee approval' gives the gate, but the pack is scheduled for 'Tuesday morning' after the page is built and Priya's mockup line is never used"),
    (P, "'Confirm Security review is closed. Maya's Friday 16:48 email approved Enterprise SSO for the current scope... The task list entry unblock Security review is stale'"),
    (P, "'board_pack_revenue | billing backfill complete | Will clear Mon ~14:00'"),
    (R, "recognises the contention - 'Marcus is the single point of failure for SSO compat patch, contoso_permission_patch, and SSO rollout' - but never engages the substitute for the substitutable item: Daniel appears only as the migration backup, and the stated reason is 'his module, fastest path' rather than a comparison"),
    (R, "'Marcus's 3h held capacity is released to SSO' and 'Nobody else knows the account-mapping branch', but the freed capacity then goes to the Contoso patch and pushes the compatibility work into Tuesday"),
    (P, "'Tell Julia to also do contoso_export_formatter (2h, date format) today - independent, needed for Tue demo'"),
    (P, "'Schedule Elena to Daniel migration handover (30min) for Tuesday, so Daniel can execute if a re-run is needed after Elena leaves Wed noon'"),
    (P, "a numbered day: 09:30 migration, Marcus sequenced from 12:30, Julia and Sarah briefed in the same block"),
    (R, "'12:30-14:30: contoso_permission_patch (2h)... 14:30-17:30: begin API compatibility patch' - the two chains are serialised through one person"),
    (P, "'Sarah - pricing_page (3h) and board_pack_non_revenue (4h). Independent of billing'"),
    (P, "'contoso_export_formatter (2h, date format change). Independent of permission patch; just needs to ship before Tue demo', against the compliance export as the contractual item"),
    (P, "'file delivered Mon ~15:30, ahead of Tue 16:00 contractual deadline'"),
    (P, "Security closed, instrumentation released, and the Contoso ticket handled as its two real items"),
    (P, "chain outstanding, Security cleared for the current scope, Wednesday EOD intact"),
    (P, "'Julia - onboarding_launch prep (2h). Launch-ready; instrumentation no longer a blocker'"),
    (P, "the formatter is parallel work for the Tuesday demo while only the permission patch gates the contractual export"),
    (P, "no substitutions: 'Elena available Mon full day, Tue full day, Wed only until 12:00', the four durations, Daniel at 3.5h + 0.5h, Tue 16:00, Thu 17:00 for the page, Fri 10:00 for the board and Fri 12:00 for onboarding are all correct"),
    (P, "'Main critical path (SSO) earliest realistic completion: Tuesday end of day' - late because of the allocation, but consistent with its own schedule and with Marcus unavailable until 13:00"),
    (P, "eight substantive unknowns, including that the permission fix is 'not yet validated end-to-end with a real delegated-admin token' and that the tracker will mislead anyone who reads it without context"),
])

run("glm5.2", "002", [
    (P, "'Elena: billing schema migration (3h) -> Marcus: SSO compatibility patch (4h) -> QA: SSO regression (2h) -> Marcus: production rollout (1h). Total: 10h of dependent work'"),
    (P, "'A second, shorter critical path shares the same first link: Elena: billing migration -> Daniel: Contoso permission patch (3.5h + 0.5h Marcus walk) -> Julia: compliance export (1h) - hard deadline Tue 16:00'"),
    (R, "'Pricing page public | Packaging committee approval' gives the gate, but the plan is 'Pricing page (3h) -> then approval pack (1.5h with screenshots)' and the mockup route is never found"),
    (P, "'Maya's Friday 16:48 email confirms SSO security review is approved and closed for the current scope... The task list (last edited Friday 14:20) still shows it as outstanding - that's stale'"),
    (P, "'Board revenue charts (2h) - wait for backfill (~14:00 today)'"),
    (P, "'Reassign contoso_permission_patch from Marcus to Daniel. Marcus is the bottleneck for SSO; Daniel can take the Contoso patch (3.5h) but needs a 30-min walk with Marcus on the delegated-admin path first. Schedule that walk for 09:30-10:00'"),
    (P, "'Marcus is the bottleneck for SSO'; 'the branch is Marcus's'; and 'Marcus can drop or defer the 3h hold'"),
    (P, "'Export formatter (2h, DD/MM/YYYY) - for Tuesday demo. Independent of the permission patch; do it this morning'"),
    (P, "'Elena to Daniel runbook handoff (30 min): schedule before Wednesday noon as insurance, but not needed if migration lands today'"),
    (P, "a nine-step ordered day opening with 'Message Elena now - start billing migration immediately'"),
    (P, "'Daniel then starts the patch once Elena's migration lands (~12:30) -> done ~16:00' against Marcus '4h focused -> done ~16:30 today'"),
    (P, "'Board pack non-revenue sections (4h) - start today, independent' with the pricing page running alongside"),
    (P, "'Export formatter... for Tuesday demo' separated throughout from 'a contractual obligation (section 8.3, Tue 16:00 CET)'"),
    (P, "'This is a contractual obligation (section 8.3, Tue 16:00 CET) on a EUR 110k ARR account - confirming today is important'"),
    (P, "Security closed, instrumentation cleared, and the Contoso work split into the formatter and the permission patch"),
    (P, "chain outstanding, Security approved, and Laura told Wednesday EOD remains on track"),
    (P, "'onboarding launch prep: flow is launch-ready; launch support moved to her'"),
    (P, "the formatter is parallel work with no dependant while the compliance export is gated by the permission patch and carries the contractual date"),
    (R, "one substitution: the delivery table reads 'Billing migration + backfill | Wed 15:00'. The stated external deadline is Thursday 2026-09-24 15:00. Its own plan lands the migration Monday, so nothing downstream moves"),
    (P, "'SSO production rollout | Wed 17:00 | Tue ~14:00 (QA Tue morning; Marcus free after 13:00 Atlas session)' - the lower bound"),
    (P, "seven unknowns including Daniel's unfamiliarity with the branch, the conditional QA estimate, and whether the compliance file needs the new date format"),
])

run("glm5.2", "003", [
    (R, "the four SSO steps are in order, but the chain is written as 'billing_schema_migration -> billing_backfill -> api_compatibility_patch -> ...', inserting the backfill as a prerequisite of the patch. The dependency table below it says the patch is blocked by the migration alone, so the response contradicts itself on the point"),
    (P, "'A second, shorter chain shares the same root: billing_schema_migration -> contoso_permission_patch (2h) -> contoso_compliance_export (1h) - due Tue 16:00'"),
    (R, "'pricing_page going public | packaging committee approval' gives the gate, but the pack is assembled 'from screenshots' after the page and the mockup route is never used"),
    (P, "'Close the stale Security review blocker on SSO. Maya's Friday 16:48 email approved the scope with no re-review for in-scope fixes'"),
    (P, "'board_pack_revenue | billing_backfill | Backfill ~13:45 today'"),
    (R, "prices the substitute exactly - 'Daniel could take contoso_permission_patch (3.5h + 30m with Marcus) but not the SSO compatibility work' - and lists him as 'free unless we choose to route contoso_permission_patch to him', then keeps it on Marcus with no comparison. The cost is a full day: its own estimate moves the rollout to Wednesday 09:00-10:00"),
    (R, "releases the instrumentation and states that nobody else has touched the branch since the spike, but spends the protected Monday afternoon on the substitutable Contoso patch"),
    (P, "'Julia - contoso_export_formatter (2h): pure date-string/fixture change, independent of permission patch. Do today'"),
    (P, "'Schedule Elena to Daniel 30-min migration handover for Tuesday morning as insurance, before Elena leaves Wed 12:00'"),
    (P, "nine ordered actions opening at 09:15 with the migration, every owner briefed in the same block"),
    (R, "'Marcus does contoso_permission_patch (2h) first... then starts api_compatibility_patch' - serialised through one person while Daniel is recorded as free"),
    (P, "'Sarah - pricing_page (3h) -> packaging_approval_pack (1.5h): self-contained chain' and 'board_pack_non_revenue (4h): independent of billing'"),
    (P, "'pure date-string/fixture change, independent of permission patch' against the compliance export as the dated contractual item"),
    (P, "'contoso_compliance_export (Julia, 1h) - Monday after permission patch... due Tue 16:00'"),
    (P, "Security closed, instrumentation deprioritised, and the Contoso ticket handled as two separate fixes"),
    (P, "chain outstanding, Security cleared, Wednesday EOD intact"),
    (P, "'Julia - onboarding_launch (2h): launch-ready, no Marcus dependency. Schedule for any time before Fri 12:00'"),
    (P, "the formatter has no dependant; only the permission patch gates the Tuesday delivery"),
    (P, "no substitutions anywhere: migration 09:15-12:15, backfill 13:45, the split compatibility patch adding to exactly 4h, Daniel at 3.5h + 30m, Elena leaving Wed 12:00, Tue 16:00, Thu 17:00, Fri 10:00, Fri 12:00 and the Wed 17:00 commitment are all correct"),
    (F, "'SSO production rollout: Wed 09:00-10:00 (Tue evening too tight given Marcus's 13:00 start; Wed morning is clean)' and 'Enterprise SSO delivered: Wed ~10:00'. Tuesday 14:00 is reachable; the answer key does not credit Wednesday presented as the earliest when Tuesday is available. The Wednesday is a consequence of its own allocation, which is priced separately"),
    (P, "seven unknowns including whether Julia could run the export via a Northstar admin token, and that the backfill is assumed rather than verified to fix the double-counting"),
])

# ---------------------------------------------------------------------------
# Gemma 4 - the only non-reasoning model that consistently gets the allocation
# right, and the only model that reopens a closed gate in two runs out of three.
# ---------------------------------------------------------------------------

run("gemma4", "001", [
    (P, "'Path A (Atlas SSO): Elena (Billing Migration) -> Marcus (Compatibility Patch) -> QA (Regression) -> Marcus (Production Rollout)'"),
    (P, "'Path B (Contoso Compliance): Elena (Billing Migration) -> Marcus (Permission Patch) -> Julia (Export File)', with the formatter kept off it"),
    (F, "pricing appears only as 'Ensure she is working on the pricing_page and packaging_approval_pack to hit the 12:00 committee cutoff tomorrow'. No approval gate on the public page, and no use of the mockup allowance"),
    (F, "reopens the closed gate: 'Check the status of the Security Review mentioned in Friday's notes. If it is still outstanding, I must escalate/resolve it to prevent a late-week stall', with the risk section reporting the status as unknown"),
    (P, "'The board_pack_revenue depends on the billing_backfill being complete'"),
    (P, "'Reassign contoso_permission_patch from Marcus to Daniel. Reasoning: Marcus is the bottleneck for both SSO and Contoso. Daniel can do the work in 3.5 hours (vs Marcus's 2) once Elena's migration lands. This preserves Marcus's capacity for the SSO compatibility patch' - the cost of the substitution priced exactly"),
    (P, "'This preserves Marcus's capacity for the SSO compatibility patch', with 'Marcus's instrumentation is no longer a blocker'"),
    (P, "'Task Julia with the contoso_export_formatter (2 hours). This is a nice-to-have for a demo, not a compliance blocker'"),
    (P, "'If Elena's migration slips past Wednesday 12:00, Daniel must be ready to take over, but we need to confirm he has the 30-minute handover scheduled'"),
    (R, "five ordered instructions but no clock times, and the reassignment is action 1 while starting the migration is action 4"),
    (P, "the ownership summary splits Daniel onto Contoso and Marcus onto SSO, so the two chains run side by side once the migration lands"),
    (P, "'Onboarding: Julia can proceed with the launch', 'Board Pack: Sarah can complete all non-revenue sections', 'Pricing: Sarah can build the page and prepare the approval pack'"),
    (P, "'This is a nice-to-have for a demo, not a compliance blocker'"),
    (R, "'ensure Contoso's Tuesday deadline is met' and 'Contoso Compliance Export: Tuesday afternoon' - the commitment is named but left undated, and its own estimate could fall after 16:00"),
    (R, "the instrumentation is cleared and the Contoso ticket split, but Security is re-raised as an open gate and the pricing entry is untouched"),
    (R, "chain outstanding and Wednesday intact, but Security is reported as unknown when it is closed"),
    (P, "'Onboarding: Julia can proceed with the launch; Marcus's instrumentation is no longer a blocker'"),
    (P, "'a nice-to-have for a demo, not a compliance blocker' against Path B, where only the permission patch reaches the compliance export"),
    (P, "the values it uses are right: Daniel at 3.5 hours against Marcus at 2, the 2-hour formatter, the 30-minute handover and Elena's Wednesday 12:00. Its Security claim is a wrong state, priced by security_state_stale"),
    (F, "'Enterprise SSO (Atlas): Wednesday EOD (Meeting the commitment, provided Marcus has the 4 hours for the patch and 2 hours for QA/Rollout after Elena lands the migration).' Tuesday 14:00 is reachable under its own ordering, and no schedule is offered"),
    (R, "the resource risk is named accurately, but a settled fact is filed as unknown: 'The status of the outstanding security review for SSO is unknown'"),
], [
    (
        "PROHIBITED_ACTION",
        "'Unblock SSO (Immediate): Check the status of the Security Review mentioned in Friday's notes. If it is still outstanding, I must escalate/resolve it to prevent a late-week stall.'",
        "Maya's Friday 16:48 email closes the review for the current scope and exempts permission-check and configuration fixes from re-review. The response directs work against a gate that is shut and, in the risks, makes clearing it a condition of the rollout.",
    ),
])

run("gemma4", "002", [
    (P, "the numbered sequence carries the four SSO steps in order with their dependencies - 'Marcus: SSO API compatibility patch (4h) - Dependent on Elena', 'QA: SSO regression (2h) - Dependent on Marcus (Patch)', 'Marcus: SSO production rollout (1h) - Dependent on QA'"),
    (P, "'Elena (Schema) -> Marcus (Permission Patch) -> Julia (Export File) -> Delivery', with 'The contoso_permission_patch is blocking the compliance export required by Tuesday 16:00 CET'"),
    (R, "'The Pricing Page launch is blocked by Priya's committee approval' gives the gate, but the approval pack is never freed from the page and mockups are not mentioned"),
    (R, "quotes Maya's approval - 'We do not know why the security review is still outstanding on the checklist despite Maya's email saying the implementation scope was approved' - but still books time to 'investigate the outstanding security review status to ensure it doesn't stall the Wednesday rollout'"),
    (P, "'The Board Pack revenue charts are blocked by the billing_backfill (1.5h), which is blocked by the schema migration'"),
    (F, "'Direct Marcus to stop working on onboarding instrumentation and prioritize the contoso_permission_patch' - the contested engineer keeps the one item that has a substitute, and Daniel does not appear anywhere in the plan"),
    (R, "takes him off the instrumentation but hands him the substitutable Contoso work, so the capacity freed does not go to the work only he can do"),
    (P, "'Assign Julia to fix the date format (contoso_export_formatter) today. This is a low-complexity task for a high-value account and must be done before Tuesday's demo'"),
    (P, "'If Elena's migration slips to Wednesday morning, we must ensure the 30-minute handover to Daniel happens before her 12:00 departure to avoid a total stall'"),
    (R, "five instructions with no clock times, and the Marcus pivot is issued before the migration is confirmed started"),
    (R, "Marcus is given the permission patch and then the compatibility patch, so the two chains run one after the other"),
    (P, "'Sarah can complete all non-revenue sections (4h) immediately' and 'Sarah can build the pricing page and prepare the approval pack'"),
    (R, "the fix goes to Julia in parallel and displaces nothing, but 'low-complexity task for a high-value account' stops short of saying the export works or the request is cosmetic"),
    (P, "'the Contoso Compliance Export (Tuesday 16:00 CET)' named in the critical path and carried into the delivery estimate"),
    (R, "the instrumentation is cleared and the Contoso ticket split, but Security is still being chased and the pricing entry is untouched"),
    (R, "the chain and the Wednesday commitment are right; Security is reported as unexplained rather than closed"),
    (P, "'Julia can proceed with the onboarding launch (2h) as Marcus's instrumentation is no longer required for launch'"),
    (P, "the formatter is parallel work for the demo; the permission patch is what blocks the Tuesday 16:00 delivery"),
    (P, "no substituted values: the 1.5-hour backfill, Tuesday 16:00 CET, the 12:00 committee window, Elena's 12:00 Wednesday departure and the stated durations are all correct"),
    (F, "'Atlas Enterprise SSO: Wednesday EOD (Matches commitment...)'. Tuesday 14:00 is reachable, and no schedule is offered for the Wednesday either"),
    (R, "no inventions, and the Marcus overload is named accurately, but a settled fact is filed as an open question"),
])

run("gemma4", "003", [
    (R, "the four SSO steps are in order, but the chain reads 'Elena: Billing schema migration (3h) -> Elena: Reconciliation backfill (1.5h) -> Marcus: Contoso permission patch AND SSO compatibility patch -> QA -> Marcus rollout', and the blocker list repeats it: 'SSO Compatibility Patch: Blocked by Elena's schema migration and backfill'. The backfill gates the board revenue charts, not the patch, and the insertion adds 90 minutes to the path"),
    (P, "'Contoso's compliance export is also on a tight path, requiring the permission patch to land before Julia can finish the file (1h)'"),
    (R, "'Pricing Page Launch: Blocked by Priya's committee approval' gives the gate; the mockup allowance is not used"),
    (F, "'Check the status of the Security Review on the release checklist. If it is still outstanding, I must resolve this to prevent a late-week stall', with 'We do not know why it is outstanding or how long it will take to clear'"),
    (P, "'Board Revenue Charts: Blocked by the billing backfill'"),
    (R, "'Reassign contoso_permission_patch to Daniel. While Marcus is the owner, Daniel is available and the task is a blocker for both Contoso and SSO' makes the right call, but the half-hour walkthrough Daniel needs is never scheduled, and section 1 still shows Marcus doing both patches"),
    (P, "'Marcus is the single point of failure for the SSO compatibility patch' with 'Onboarding Instrumentation: it is not a launch blocker and should be deprioritized if he is needed for SSO'"),
    (P, "'Task Julia to complete the contoso_export_formatter (2h) today. This satisfies the nice-to-have demo request for Tuesday'"),
    (P, "'If Elena's migration slips to Wednesday, we rely on a 30-minute handover before she leaves at noon. If that fails, the entire critical path shifts to Thursday/Friday'"),
    (R, "five instructions, no clock times, and the reassignment is issued before the migration is confirmed started"),
    (R, "the allocation puts Daniel on Contoso and Marcus on SSO, but section 1 contradicts it by giving Marcus both patches"),
    (P, "'Sarah can build the pricing page and prepare the approval pack while waiting for committee windows' and 'Sarah can complete all non-revenue sections of the board pack'"),
    (P, "'This satisfies the nice-to-have demo request for Tuesday and clears her plate'"),
    (R, "'ensure Contoso's Tuesday deadline is met' with 'Contoso Compliance Export: Tuesday morning' - named but left undated"),
    (R, "the instrumentation is deprioritised and the Contoso ticket split, but Security is re-raised and the pricing entry is untouched"),
    (R, "chain outstanding and Wednesday intact, but Security is reported as unknown"),
    (P, "'Julia can proceed with the onboarding_launch (2h) as Marcus's instrumentation is no longer a blocker'"),
    (P, "'Contoso Compliance Export: Blocked by the permission patch' while the formatter is parallel work with no dependant"),
    (P, "the values it uses are right - the 2-hour formatter, the 1-hour export, the 30-minute handover, Elena leaving at noon, the three hours Marcus is holding. Its backfill claim is a wrong relationship, priced by sso_chain, and its Security claim a wrong state, priced by security_state_stale"),
    (F, "'Enterprise SSO: Wednesday EOD (matches Atlas commitment, provided Marcus is not further delayed by the Tuesday technical session)'. Tuesday 14:00 is reachable and no schedule is offered"),
    (R, "no inventions, and the Elena handover risk is stated well, but a settled fact is filed as an open question"),
], [
    (
        "PROHIBITED_ACTION",
        "'Unblock SSO (Immediate): Check the status of the Security Review on the release checklist. If it is still outstanding, I must resolve this to prevent a late-week stall.'",
        "Maya's Friday 16:48 email closes the review for the current scope. The response directs work against a gate that is shut and reports its status as unknown in the risks, spending product time on a precondition that has already been met.",
    ),
])

# ---------------------------------------------------------------------------
# GLM 5.3 Flash - the widest spread in the battery: 97.5 / 81.0 / 100.0
# ---------------------------------------------------------------------------

run("glm5.3-flash", "001", [
    (P, "'Elena: billing schema migration (3h) -> Marcus: SSO compatibility patch (4h) -> QA: regression (2h) -> Marcus: production rollout (1h)' with an indicative clock timeline"),
    (P, "'Contoso's contractual compliance export (due Tue 16:00 CET, auditor window - cannot move) needs the delegated-admin permission patch deployed, which Marcus says can only go in after the same migration lands'"),
    (P, "'Priya accepts mockups - don't serialize the approval pack behind the live page' and 'Packaging approval -> pricing page going public (not the build)'"),
    (P, "'close unblock Security review (Maya approved Fri 16:48)' and 'Stale blockers to close now: Security review (done)'"),
    (P, "'Schema migration -> blocks SSO patch completion, permission-patch deployment, backfill -> revenue charts'"),
    (P, "'Reassign contoso_permission_patch Marcus -> Daniel (Rachel invited this). Marcus must go straight into the 4h SSO patch at ~13:00; Daniel is free all week. Book Marcus's 30-min walkthrough with Daniel this morning'"),
    (P, "'Marcus is sole owner of the account-mapping branch and rollout - mitigated via Daniel reassignment + instrumentation descope'"),
    (P, "'Julia - date-format fix + fixtures (2h)'"),
    (P, "'Elena out Wed noon-Fri: only matters if migration slips. Decision point Tue 15:00 - if not landed, do the 30-min Daniel handover Tue EOD'"),
    (P, "a timed table from 09:15 to 12:00 with the migration confirmed first and every delegation issued before 10:00"),
    (P, "'Daniel - write permission patch now; only deployment waits on the migration' against Marcus on the compatibility patch from 13:00"),
    (P, "'Sarah - approval pack with mockups (submit <12:00); board non-revenue (4h); pricing page build (3h) - build now, public go-live gated on approval only'"),
    (P, "'Friday's broken export = two things - date format (Julia, 2h, today) + real permission bug (in progress today)'"),
    (P, "'Reply to Anja Weber confirming delivery before Tue 16:00 CET'"),
    (P, "all four: Security closed, instrumentation descoped, the Contoso ticket split, and 'live-page screenshots for Priya (mockups suffice)' listed as a stale blocker"),
    (P, "chain outstanding, Security done, and the Wednesday EOD commitment reconfirmed to Laura"),
    (P, "'remove onboarding instrumentation as launch blocker (Julia descoped it - frees 3h of Marcus)' with the launch work sitting with Julia"),
    (P, "'date format (demo, cosmetic) vs delegated-admin export (contractual, Tue 16:00)'"),
    (R, "one substitution: 'Pricing page public: Wed (deadline Wed 17:00)'. The page is due Thursday 17:00. Everything else it uses is right, and the plan does not move on the correction"),
    (P, "'SSO live ~Tue 14:00 - ~1.5 days buffer before Wed EOD', derived from a schedule that respects the Tuesday-morning session"),
    (P, "six unknowns including whether the permission fix extends the tenant permission model enough to reopen Maya's review, and whether Daniel holds production deploy rights"),
])

run("glm5.3-flash", "002", [
    (P, "'Chain B - Enterprise SSO (committed Wed EOD, Atlas IT starts Thu): Elena migration (3h) -> compatibility patch (Marcus, 4h) -> QA regression (2h) -> production rollout (Marcus, 1h)'"),
    (P, "'Chain A - Contoso compliance export (hard deadline Tue 16:00 CET): Elena migration (3h) -> permission patch (Marcus, 2h) -> Julia produces & sends export (1h)'"),
    (P, "'submit packaging approval pack using mockups before 12:00 (same-day clearance; mockups explicitly acceptable - don't wait for the live page)' and 'Packaging approval blocks public pricing page'"),
    (P, "'Security review: approved Friday (Maya's email). Permission/config fixes in scope don't need re-review'"),
    (P, "'Board revenue charts (Sarah, 2h): can start ~13:30 Monday once backfill completes'"),
    (R, "detects it - 'Marcus is the shared resource across both chains' - and prices the substitute as a contingency: 'if Marcus slips, Daniel takes the permission patch (3.5h + 0.5h Marcus walkthrough)'. But the substitutable work stays with Marcus and the only reason offered is the ordering one, 'earlier external deadline'; why Marcus rather than Daniel is never argued, and the rollout moves out to 15:30-16:30"),
    (R, "'Release the instrumentation hold' and 'only Marcus knows the account-mapping branch', but the freed capacity goes to the Contoso patch at 12:00-14:00"),
    (P, "'Julia: Contoso date formatter (2h) today (Peter wants it before Tue afternoon)'"),
    (P, "'ask her to do the 30-min Daniel handover today or Tuesday as contingency - don't leave it to Wednesday morning'"),
    (P, "a nine-row ordered table opening at 09:15 with 'start the migration now', every owner briefed by 09:30"),
    (R, "'permission patch 12:00-14:00, then compatibility patch 14:00-17:30 + Tue 13:00-13:30' - the two chains run one after the other through one person"),
    (P, "'Sarah: approval pack w/ mockups (submit <12:00), pricing page, board non-revenue (4h)'"),
    (R, "keeps the formatter with Julia and off the dated chain - Chain A contains only the permission patch - but never characterises the format request as cosmetic or the export as working"),
    (P, "'Reply to Anja Weber confirming delivery ahead of Tue 16:00 CET (target: Monday EOD)'"),
    (P, "all four: Security closed, instrumentation released, the Contoso ticket handled as two issues, and Sarah freed from the live page"),
    (P, "chain outstanding, Security approved Friday, Wednesday EOD commitment held"),
    (P, "'Onboarding instrumentation: Julia confirmed not needed for launch' with the launch prep sitting with Julia"),
    (P, "Chain A carries only the permission patch and the contractual date; the formatter is parallel work with no dependant"),
    (F, "two substituted deadlines, both used as planning targets: 'onboarding launch prep (deadline Thu 12:00)' - it is Friday 12:00, repeated as 'Thu deadline' in the parallel-work list - and 'pricing page (Wed 17:00 deadline)' - it is Thursday 17:00"),
    (P, "'rollout Tuesday ~15:30-16:30 (QA Tue 13:30-15:30, rollout immediately after)', consistent with its own schedule and with Marcus unavailable until 13:00"),
    (P, "eight unknowns, including the sharpest reading in the battery of the backfill ambiguity: 'Marcus said the patches need the schema change landed - I've assumed the 90-min backfill does not need to complete before the permission/compatibility patches merge'"),
])

run("glm5.3-flash", "003", [
    (P, "'Path A - Atlas Enterprise SSO (committed Wed 17:00): Elena schema migration (3h) -> Marcus compatibility patch (4h, Marcus only - no backup exists) -> QA regression (2h) -> Marcus production rollout (1h)'"),
    (P, "'Path B - Contoso compliance export (contractual, Tue 16:00 CET): Elena schema migration -> permission patch (Daniel 3.5h + 0.5h Marcus walkthrough) -> Julia produces & sends export (1h)'"),
    (P, "'Priya accepts mockups, so don't wait on a live page' and 'Packaging approval doesn't need the live page - mockups accepted', with the page going public after clearance"),
    (P, "'security review closed Friday 16:48 (Maya's email - the Friday 14:00 meeting note is outdated)' - the only response to name the stale record as well as the current one"),
    (P, "'Revenue charts unblocked once backfill completes (~14:00) - start today or Tuesday'"),
    (P, "'Reassign contoso_permission_patch Marcus -> Daniel (Rachel offered; Marcus must be freed for the SSO patch). Marcus contributes 30 min, not 2h', with 'Path B has a second viable worker (Daniel)... but only if we take the patch off Marcus'"),
    (P, "'Marcus compatibility patch (4h, Marcus only - no backup exists)' and 'Marcus's 3h instrumentation hold: release it - not a launch blocker'"),
    (P, "'Exporter date-format fix (2h) - independent, due before Tue PM demo' owned by Julia"),
    (P, "'Contingency trigger: if migration hasn't landed by Tue midday, Elena transfers production migration permissions to Daniel (30 min) before she leaves Wed 12:00. Don't book preemptively; watch for the trigger'"),
    (P, "a timed table from 09:15, migration at 09:30, and the walkthrough scheduled into what it calls 'Marcus's forced wait time'"),
    (P, "'Daniel: can write the permission patch during the migration; it only lands after' with 'Marcus starts SSO patch immediately' at 12:30"),
    (P, "'Build pricing page (3h), then approval pack (1.5h)... Submit today PM -> clears Tue AM' alongside board non-revenue"),
    (P, "'Contoso date format doesn't block production/import - demo preference only'"),
    (P, "'Email Anja Weber confirming compliance export delivery before Tue 16:00 (she asked for confirmation today)'"),
    (P, "all four: Security closed against the outdated meeting note, instrumentation descoped, the Contoso report split into permission check plus date format, and the approval pack freed from the page"),
    (P, "chain outstanding, Security closed for the current scope, Wed 17:00 commitment reconfirmed to Laura"),
    (P, "'onboarding launch tasks (2h, due Fri 12:00) - schedule Tue/Wed' with the instrumentation released"),
    (P, "'Contoso issue is a delegated-admin permission check + date format, not data loss' and 'date format doesn't block production/import'"),
    (P, "every anchor correct, including the two that caught three other models: 'deadline Thu 17:00' for the pricing page and 'due Fri 12:00' for onboarding. Also Wed 17:00, Tue 16:00 CET, Fri 10:00, Daniel at 3.5h + 0.5h, Marcus's Tuesday absence and Elena's Wed 12:00 departure"),
    (P, "'Enterprise SSO live Tuesday ~14:00 (migration Mon 12:30 -> patch Mon 17:00 -> QA Tue 11:00 -> rollout Tue 13:00-14:00). That's ~27h ahead of the Wed 17:00 commitment'"),
    (P, "six unknowns closing with 'None of these can be verified from the available evidence', and a structural risk it declines to pretend it can mitigate: 'nobody but Marcus can do the compatibility patch (per Elena). No mitigation available this week'"),
])

# ---------------------------------------------------------------------------
# MIMO v2.5
# ---------------------------------------------------------------------------

run("mimo-v2.5", "001", [
    (P, "the ASCII tree: 'Elena: Schema migration (3h) -> Marcus: SSO compatibility patch (4h) -> QA: regression (2h) -> Marcus: rollout (1h)'"),
    (P, "the tree's second branch: 'Daniel: Contoso permission patch (3.5h) -> Julia: compliance export (1h)'; the formatter is separate parallel work"),
    (R, "'Page can't go public until approval clears, but build can start' gives the gate, but the plan is 'pricing page now -> approval pack' and the mockup route is never used"),
    (P, "'Update the release checklist: mark security review DONE (Maya's approval landed Friday 16:48, after the Friday meeting logged it as outstanding)'"),
    (P, "'Backfill completion (~14:00) | Elena (automated) | Sarah (revenue charts for board pack)'"),
    (P, "'contoso_permission_patch assigned to Marcus, who is needed for SSO -> Reassign to Daniel. Marcus gives 30-min walk-through, then hands off'"),
    (P, "'he starts the SSO compatibility patch the moment Elena's schema lands (~12:15). No other work this afternoon', with the instrumentation removed as a launch blocker"),
    (P, "'Contoso date-format fix | Julia | 2h | Independent. Peter confirmed it's cosmetic, not blocking'"),
    (P, "'Elena's unavailability Wed noon to Fri... Elena should do the 30-min handoff with Daniel on Tuesday or Wednesday morning. This is insurance'"),
    (P, "ten timed actions from 09:10, migration second, every owner confirmed by 09:30"),
    (P, "the tree branches after the migration: Daniel on Contoso, Marcus on SSO, neither waiting on the other"),
    (P, "'Packaging page build | Sarah | 3h' and 'Board pack (non-revenue) | Sarah | 4h | No dependency on billing data'"),
    (P, "'Contoso broken export (date format) - Peter confirmed it imports fine; it's a cosmetic preference for a Tuesday demo, not a production issue'"),
    (P, "'Send Contoso (Anja Weber): confirm compliance export will be delivered by Tuesday morning' against the Tue 16:00 CET deadline"),
    (P, "Security marked done, instrumentation removed, and the Contoso export split from the permission bug"),
    (P, "chain outstanding, Security approved Friday 16:48, Wed EOD intact"),
    (P, "'Onboarding launch prep | Julia | 2h | Fri 12:00 | Flow is ready'"),
    (P, "'it's a cosmetic preference for a Tuesday demo, not a production issue', with only the permission patch feeding the compliance export"),
    (F, "two substituted deadlines, both used to compute the buffers it reports: 'Billing schema migration | 3h | Wed 15:00' - the stated deadline is Thursday 15:00 - and 'Packaging page build | Wed EOD' with 'Pricing page live | Wed AM | Wed EOD', where the page is due Thursday 17:00"),
    (P, "'Enterprise SSO (live in prod) | Tue ~14:00 | Wed EOD (27h buffer)'"),
    (P, "a risk table with an explicit 'What I don't know' row naming three things it cannot settle from the sources"),
])

run("mimo-v2.5", "002", [
    (P, "the code-block chain with clock windows: 'Marcus: api_compatibility_patch (4h, 12:00->16:00) -> QA: sso_regression (2h, Tue 09:00->11:00) -> Marcus: sso_production_rollout (1h, Tue 13:00->14:00)'"),
    (P, "'Daniel: contoso_permission_patch (3.5h, 12:00->15:30) -> Julia: contoso_compliance_export (1h, 15:30->16:30) <- DEADLINE: Tue 16:00'"),
    (R, "'Pricing approval pack depends on pricing page' with 'Screenshots needed for approval pack submission' - the gate is implied by 'Pricing page live | Tuesday EOD (post-approval)', but the mockup route is missed"),
    (P, "'Security review for SSO - RESOLVED - Maya approved Friday 16:48. Tracker is stale'"),
    (P, "'Board pack revenue charts depend on billing backfill - Backfill done Monday ~13:30'"),
    (P, "'Daniel has recent context (SCIM work). Using him here frees Marcus for the SSO work only he can do', with the walkthrough at 09:30"),
    (P, "'Protect Marcus's SSO time. He's the only person on that branch' and 'Marcus has 3h freed up'"),
    (P, "'Brief Julia: start with contoso_export_formatter (date format, 2h, independent)'"),
    (P, "'Ensure Daniel gets the migration runbook handoff (30 min) Monday or Tuesday as backup', against 'Elena leaves Wednesday noon'"),
    (P, "a fifteen-row timed plan from 09:10 with checkpoints at 12:00, 15:30, 16:00 and 16:30"),
    (P, "'After Elena's schema lands at noon, both paths fan out in parallel using Daniel (Contoso) and Marcus (SSO)'"),
    (P, "'board_pack_non_revenue | Sarah | Mon 09:10-13:10' and 'pricing_page | Sarah | Mon 13:10-16:10'"),
    (R, "handles the formatter correctly - Julia, 2h, independent, 'Decouples the date fix from the permission fix' - but never states that the reported breakage is cosmetic or that the file imports"),
    (P, "'Reply to Anja (Contoso compliance): confirm delivery before Tuesday 16:00... EUR 110k ARR + contractual obligation'"),
    (P, "Security and instrumentation struck through as resolved, and the Contoso ticket handled as its two real items"),
    (P, "chain outstanding, Security resolved, and Laura confirmed for Wednesday EOD"),
    (P, "'Onboarding launch | Tuesday or Wednesday | Friday 12:00' with the instrumentation flag removed"),
    (P, "the diagram gives the export a single upstream - the permission patch - while the formatter sits in parallel work"),
    (P, "no substitutions, including the two anchors that caught its sibling run: 'Billing schema migration + backfill | Thursday (work item)' and 'Pricing page live | Thursday'. Durations, the Tuesday absence, Elena's Wednesday noon, Tue 16:00 CET, Fri 10:00 and Fri 12:00 are all correct"),
    (P, "'Enterprise SSO (live in production) | Tuesday 14:00 | Wednesday EOD | ~27h'"),
    (P, "eight risks led by the best catch in the battery: 'Contoso permission patch has no tracked production deploy step. The SSO path has an explicit 1h rollout task; Contoso doesn't. Julia can't run the compliance export until the fix is live'"),
])

run("mimo-v2.5", "003", [
    (P, "the step table gives migration, compatibility patch, regression and rollout in order with owners, durations and windows"),
    (P, "'Contoso permission patch must land before Julia can produce the compliance export - Marcus finishes permission patch ~14:15; Julia starts compliance export immediately after'"),
    (R, "'Pricing page must be built before approval pack (screenshots needed)' with the gate implied by 'Packaging approval | Before pricing page goes live'; the mockup route is never found"),
    (P, "'Confirm security review is closed. Maya approved it Friday 16:48 but the release checklist still shows outstanding as of Friday's meeting'"),
    (P, "'Board revenue charts depend on post-backfill data - Backfill completes ~13:45 Monday'"),
    (R, "detects it - 'Marcus is the shared resource between the Contoso permission patch and the SSO compatibility patch' - and gives a reason for the order, 'its deadline has less float'. But Daniel is used only as the migration backup, never considered for the patch, and the ownership choice is never argued"),
    (R, "declares the instrumentation not launch-blocking but then schedules Marcus on it 09:15-12:15 as 'fill work', and hands him the substitutable Contoso patch as well"),
    (P, "'contoso_export_formatter (date fix) | Julia | Mon 09:15-11:15 | Independent of schema change'"),
    (P, "'Coordinate with Elena to hand off migration permissions + runbook to Daniel on Tuesday morning... Elena vanishes Wednesday noon. Daniel is the designated backup and doesn't yet have production migration permissions'"),
    (P, "eight ordered actions opening with 'Confirm Elena has started the billing schema migration NOW'"),
    (R, "'I am placing the Contoso permission patch first' - the two chains run through Marcus one after the other while Daniel is free"),
    (P, "'pricing_page | Sarah | Mon 09:15-12:15 | No dependencies' with the board non-revenue work running alongside"),
    (R, "'The format fix is independent and clears Contoso's Tuesday demo ask' - correctly kept off the committed work, but never characterised as a preference against a working export"),
    (P, "'Reply to Anja Weber confirming delivery of the compliance export by Tuesday 16:00 CET. Our plan delivers it Monday ~15:15'"),
    (P, "Security closed, instrumentation declared non-blocking, and the Contoso work handled as its two items"),
    (P, "chain outstanding, Security closed, Wednesday EOD intact"),
    (P, "'onboarding_launch | Julia | Anytime Tue-Fri | Flow is ready. Deadline Friday 12:00'"),
    (P, "the formatter is independent parallel work; only the permission patch gates the contractual export"),
    (P, "no substitutions: the split compatibility patch adds to exactly 4h, QA 13:45-15:45, rollout 15:45-16:45 behind the Atlas session, backfill 12:15-13:45, and Thu 17:00, Fri 12:00, Fri 10:00, Tue 16:00 CET and Elena's Wednesday noon are all correct"),
    (P, "'Enterprise SSO | Tue ~16:45 | Wed EOD | ~24 hours of buffer' - later than the bound because of the allocation, but supported by its own schedule and respecting the Tuesday morning"),
    (P, "eight risks including that the Contoso patch has no listed deployment step and that a >4h compatibility patch leaves zero buffer"),
])

# ---------------------------------------------------------------------------
# Qwen 3.6
# ---------------------------------------------------------------------------

run("qwen3.6", "001", [
    (P, "'Elena performs Billing Schema Migration (3h) -> Marcus performs SSO Compatibility Patch (4h). Depends on #1 -> QA performs Regression (2h). Depends on #2 -> Marcus performs Production Rollout (1h). Depends on #3'"),
    (P, "'The Contoso Permission Patch... is technically dependent on the same account-mapping layer that Elena's migration lands', with Julia producing the file after Daniel's patch; the formatter is separate"),
    (F, "'Packaging Approval Pack (Sarah): 1.5 hours. Independent.' Neither half is addressed: no gate on the public page and no use of the mockup allowance"),
    (R, "'Assume approved... but Noah/Product must confirm with Maya if there is any ambiguity', and the risk section still asks whether the patch touches the auth flow"),
    (F, "the backfill appears nowhere; the board revenue dependency is not raised at all"),
    (P, "'Reassign contoso_permission_patch from Marcus to Daniel. Reasoning: Marcus explicitly stated Daniel can take it (3.5h) and Daniel was in the relevant SCIM work. Marcus is needed for the SSO patch which is on the critical path'"),
    (R, "keeps Marcus on the SSO work and cites 'Marcus's specific code ownership', but never releases the three hours he is holding for the instrumentation"),
    (P, "'Julia executes the Contoso Export Formatter fix (2h). This is independent of the backend permission patch and can be done in parallel'"),
    (R, "'She is available until 12:00 Wednesday, but doing it Monday clears the path' names the constraint, but the production-permission transfer and the Daniel fallback are missing"),
    (R, "the handoff sequencing contradicts itself - Daniel is told to work 13:00-17:30 while the Marcus walkthrough is described as 'likely sequential' after the four-hour patch"),
    (P, "'Daniel's Contoso Permission Patch: 3.5 hours. Runs in parallel with Marcus's SSO Patch (after the 30-min handoff)'"),
    (P, "'Board Pack (Sarah): Non-revenue sections (4h) and Pricing Page (3h). Independent of billing migration'"),
    (R, "'Independent of backend permission fixes. Can be done Monday' keeps it off the committed work, but the response never characterises it as a preference against a working export"),
    (P, "'Contoso Compliance Export: Tuesday 16:00 CET... Can be completed Monday. Julia can generate the file Monday afternoon'"),
    (R, "the Contoso ticket is split into its two real items, but Security is left as something to confirm, the instrumentation is not addressed, and the pricing entry is untouched"),
    (R, "the chain and the Wednesday commitment are right; Security is left unresolved"),
    (P, "'Onboarding Launch (Julia): 2 hours. Marcus is no longer blocking this (Julia confirmed analytics are sufficient). Julia can own this'"),
    (P, "the formatter is independent of the backend fix; only the permission patch gates the compliance export"),
    (F, "two substitutions. 'Marcus still needs 2h to walk Daniel through the delegated-admin path' - the walkthrough is 30 minutes, as the same response says twice elsewhere. And the delivery arithmetic runs QA to 18:00 on a Monday when the QA window closes at 17:30"),
    (F, "'Enterprise SSO (Atlas): Monday EOD... Rollout at 18:00+.' Ten hours of dependent work cannot fit into Monday from 09:10, and the fallback offered, 'Tuesday morning', is a window in which the rollout owner is in the Atlas session"),
    (R, "the risk section is otherwise sound, but the plan rests on an invented two-hour walkthrough that the same response contradicts"),
])

run("qwen3.6", "002", [
    (P, "'Elena: Billing Schema Migration (3 hours) -> Marcus: SSO Compatibility Patch (4 hours). Blocked until Elena's migration lands -> QA: SSO Regression -> Marcus: SSO Production Rollout'"),
    (P, "'Once Daniel's patch is ready (est. Monday PM), Julia performs the export and sends it to Contoso. This meets the Tuesday 16:00 CET deadline'; the formatter is a separate directive"),
    (R, "'Creating the Packaging Approval Pack (1.5 hours). Can be done once the Pricing Page is built or via mockups (Priya accepts mockups)' has the mockup route, but the response never states that approval gates the public page"),
    (P, "'The Security Review task in the Task List is stale. The email from Maya (Friday 16:48) explicitly states the review is closed and approved for the current scope. This task should be closed immediately'"),
    (R, "'Explicitly tell her not to build the revenue charts until Elena confirms the billing migration is complete' - the dependency is on the migration alone; the backfill is never named"),
    (P, "'Reassign contoso_permission_patch from Marcus to Daniel. Marcus is blocked on the schema migration anyway, and Daniel has the context', with the sync booked for 10:00-10:30"),
    (R, "keeps Marcus available for the SSO patch, but the instrumentation hold is never addressed and no substitutability ground is given"),
    (P, "'Direct Julia to fix the contoso_export_formatter (2 hours) immediately. This is a simple format string change'"),
    (F, "Elena's Wednesday-noon departure, the production-permission transfer and the Daniel migration fallback are all absent; the only guidance is 'she must complete this by Tuesday EOD latest'"),
    (R, "the morning is spent on triage and Marcus is explicitly parked - 'If Marcus is free after 13:00, he should not start the SSO patch yet' - which pushes the SSO chain into Tuesday and Wednesday"),
    (R, "Daniel and Julia do work the Contoso chain while SSO waits, but the SSO patch is deferred to 'Tue PM/Wed AM' rather than run alongside"),
    (P, "'Sarah: Building non-revenue sections of the Board Pack', 'Building the Pricing Page (3 hours)', 'Creating the Packaging Approval Pack (1.5 hours)'"),
    (R, "'This is a simple format string change' and it is kept off the contractual path, but the working export is never confirmed"),
    (P, "'the delegated admin fix is required for the contractual Tuesday 16:00 delivery. Prioritize Daniel's patch for the 16:00 deadline'"),
    (R, "Security is closed and the Contoso ticket is split, but the instrumentation entry is never addressed and the pricing entry is untouched"),
    (P, "chain outstanding, Security closed and the task removed, Wednesday EOD intact"),
    (R, "'The task list says Marcus owns onboarding launch support. Julia owns the flow' gets the ownership move, but the instrumentation status is never stated"),
    (P, "the date fix and the permission bug are separate items with different owners, and only the permission fix carries the contractual deadline"),
    (F, "three substitutions. 'Marcus is available 09:00-13:00' is written into the Monday plan - that is his Tuesday window; Monday he is available 09:00-17:30. 'Daniel to start the contoso_permission_patch (3.5 hours total, including Marcus sync)' folds the half-hour walkthrough into Daniel's own estimate. And the tenant-owner fallback is offered without the fact that she is on leave until October"),
    (F, "'Enterprise SSO (Wednesday EOD): Earliest: Wednesday EOD.' Tuesday 14:00 is reachable, and the response's own reason for Wednesday is a Monday it chose to leave idle"),
    (R, "the risk list is reasonable, but the contingency it offers for a contractual deadline rests on an account the sources say nobody can operate until October"),
], [
    (
        "MATERIAL_HALLUCINATION",
        "'If the permission patch isn't done by Monday EOD, Julia can still generate the file using the tenant owner account (as per her earlier note: \"Their tenant owner account works\").'",
        "Anja's Monday 07:52 email states that only the tenant owner account can produce the export and that she is on leave until October. The response offers that account as the fallback for a contractual Tuesday 16:00 delivery without the fact that removes it, and additionally attributes Rachel's line to Julia.",
    ),
])

run("qwen3.6", "003", [
    (P, "'Elena completes Billing Schema Migration (3h) -> Marcus performs Compatibility Patch (4h). Depends on #1 -> QA Regression (2h). Depends on #2 -> Marcus performs Production Rollout (1h). Depends on #3'"),
    (P, "'Secondary Critical Path: Contoso Compliance Export (Tuesday 16:00 CET): Fix permission check (Daniel, 3.5h + 0.5h sync with Marcus) -> Julia produces/export file (1h) -> Delivery'"),
    (F, "'Sarah: packaging_approval_pack (1.5h). Independent.' and 'Sarah: pricing_page (3h). Independent.' Neither the approval gate nor the mockup allowance appears"),
    (R, "lays the discrepancy out fairly - Maya's approval against the meeting note - but resolves it into 'You must clarify this immediately. Is it a technical block or a checkbox?' rather than closing it"),
    (P, "'board_pack_revenue (2h) is blocked by Elena's billing migration and backfill'"),
    (P, "Daniel owns the patch with the half-hour sync scheduled, and the response does the capacity arithmetic that justifies it: 'Marcus is needed for the Contoso sync (0.5h) and the SSO patch (4h). Total 4.5h'"),
    (P, "'Explicitly tell Marcus: Drop onboarding instrumentation this week. It is not a launch blocker. Focus 100% on SSO and Contoso', after showing his week would otherwise run to 7.5h"),
    (P, "'Julia: contoso_export_formatter (2h). Independent of Contoso permission fix... Can start immediately'"),
    (P, "'She said Daniel can take over... I need 30 mins with him. She should do this sync today to de-risk her Wednesday absence'"),
    (P, "a timed morning that starts the migration first and books the Marcus-Daniel sync at 09:30 so Daniel is ready when the schema lands"),
    (R, "Daniel and Marcus do work different chains, but Daniel is scheduled 10:00-13:30 on a patch the sources say can only go in after a migration that runs until ~12:30-13:30"),
    (P, "'Sarah: board_pack_non_revenue (4h). Independent of billing migration', with the pricing page and approval pack alongside"),
    (R, "kept off the committed work, but the reason offered is invented rather than read: 'formatting is client-side or separate logic'"),
    (P, "'Secondary Critical Path: Contoso Compliance Export (Tuesday 16:00 CET)' with the delivery step dated"),
    (R, "the instrumentation is dropped and the launch-support owner corrected, but Security is left open and the pricing entry untouched"),
    (R, "the chain and the Wednesday commitment are right; Security is filed as an unresolved discrepancy"),
    (P, "'Julia said Launch support moves from Marcus to Julia with immediate effect. So this is done', with the instrumentation dropped"),
    (P, "the formatter is independent; the permission fix is what carries the Tuesday 16:00 delivery"),
    (P, "no substituted values: 'Marcus is available 09:00-17:30 Monday' is correct, Daniel is priced at 3.5h + 0.5h, the four durations hold, and Elena's Wednesday absence is stated correctly"),
    (R, "the primary answer is right - 'Tuesday 13:30 CET... Realistic: Tuesday 14:00 CET' with a schedule behind it - but it is offered alongside an 'Optimistic: Monday 18:00 CET' that ten hours of dependent work cannot reach"),
    (R, "the risk section is the strongest of this model's three runs, but it asserts a mechanism it cannot know ('formatting is client-side or separate logic') and leaves a settled fact filed as a discrepancy"),
], [
    (
        "MAJOR_PLANNING_ERROR",
        "'Contoso Sync: Daniel needs 3.5h. If Marcus syncs with Daniel at 09:30, Daniel can work 10:00-13:30. This works.' against 'Elena finishes migration ~12:30-13:30. Marcus can start patch ~13:30.'",
        "The permission patch is scheduled to start at 10:00 and finish at 13:30, overlapping the schema migration it depends on. Marcus states in #support-escalations that the patch sits on the same account-mapping layer and can only go in after the migration lands; this run never records that dependency.",
    ),
])

# ---------------------------------------------------------------------------
# Qwen 3.8 Flash - three qualifying runs: 001, 002 and 007. Attempts 003 to 006
# were refused by the reasoning guard and are documented in
# runs/monday-003/qwen3.8-flash/REJECTED-ATTEMPTS.md. Run 007 was generated at
# the identical configuration fingerprint as all six before it.
# ---------------------------------------------------------------------------

run("qwen3.8-flash", "001", [
    (P, "'Critical path B - Enterprise SSO, due Wed 23 Sep EOD: Elena billing schema migration 3h -> Marcus SSO compatibility patch 4h -> QA/Sam SSO regression 2h -> Marcus production rollout 1h'"),
    (P, "'Critical path A - Contoso compliance export, due Tue 22 Sep 16:00 CET: Elena migration -> Daniel delegated-admin permission patch 3.5h with 30m Marcus walkthrough -> Julia produce/send compliance export 1h'"),
    (P, "'Packaging approval not cleared | Public pricing page' with 'mockups/screenshots - live page not required' and 'Pricing approval needing live page: not true; mockups are acceptable'"),
    (P, "'Security review: closed and approved. Permission/config fixes inside approved scope do not need re-review unless auth flow changes'"),
    (P, "'Billing backfill not complete | Final revenue charts | Elena starts backfill after migration'"),
    (P, "'Bottleneck: Marcus. Decision: Reassign the Contoso permission patch to Daniel, with Marcus support, to protect Marcus for SSO', with the walkthrough at 09:10-09:40"),
    (P, "'12:10-16:10 - Marcus: SSO compatibility patch. Do not start onboarding instrumentation unless SSO rollout is already complete and no risk remains'"),
    (P, "'09:10-11:10 - Julia: Change Contoso exporter date format and fixtures for DD/MM/YYYY demo request'"),
    (F, "Elena's Wednesday-noon departure, the production-permission transfer and the Daniel migration fallback appear nowhere - not in the plan, not in the blocker table, and not in ten numbered risks"),
    (P, "every action timestamped from 09:10, with the migration, the walkthrough, the formatter and the approval pack all started in the same window"),
    (P, "'12:10-16:10 - Marcus' against '12:10-15:40 - Daniel', with an escalation path if the branches cannot be isolated"),
    (P, "'Sarah: packaging approval pack using mockups, not live page' and 'Sarah: board pack non-revenue sections'"),
    (P, "'Contoso export broken: production export works; issue is delegated-admin permission bug plus demo date-format preference'"),
    (P, "'Confirm to Anja/CEO/Peter: delegated-admin fix is scheduled; compliance export will be delivered by Tue 16:00, target today'"),
    (P, "all four listed under 'Stale / false blockers': Security, instrumentation, the Contoso report, and 'Pricing approval needing live page: not true'"),
    (P, "chain outstanding, SEC-4471 approved for the current scope, Wed 23 Sep EOD intact"),
    (P, "'Onboarding instrumentation is not a launch blocker; tracker is stale' with 'Julia: onboarding launch prep'"),
    (P, "'Contractual blocker: delegated admins cannot run tenant export. Demo request: date format... not a production blocker'"),
    (P, "no substitutions, including a QA split that adds to exactly two hours across Monday 16:10-17:30 and Tuesday 09:00-10:00. Marcus's Tuesday absence, Tue 22 Sep 16:00 CET, Wed 23 Sep EOD, the 90-minute backfill and the noon committee cutoff are all correct"),
    (P, "'Earliest realistic rollout completion: Tuesday ~14:00' with the four-step sequence and the reason the rollout cannot be earlier"),
    (P, "ten numbered unknowns including the branch-isolation risk, whether QA needs two continuous hours, and whether Anja's contractual file needs the demo format"),
])

run("qwen3.8-flash", "002", [
    (P, "a four-row table with owner, duration, earliest window and rationale per step, ending 'Earliest realistic SSO completion: Tuesday 14:00'"),
    (P, "'Tightest-deadline branch - Contoso compliance export' as a five-row table: Marcus-to-Daniel handoff, migration, Daniel's patch, an optional Marcus merge buffer, then Julia's export against the Tue 16:00 CET contractual deadline"),
    (P, "'Public pricing page depends on packaging approval. Approval pack can be submitted with mockups, but public page still cannot go live until committee clears it'"),
    (P, "'Security review is closed - Maya approved current scope. Permission-check and configuration fixes inside the approved scope do not need re-review'"),
    (P, "'billing_schema_migration -> billing_backfill -> board_pack_revenue' written out as a dependency chain"),
    (P, "'Contoso permission patch is currently assigned to Marcus - should be reassigned to Daniel. Marcus only needs 30 minutes for handoff and optional review/merge'"),
    (P, "'Marcus is the only realistic owner of SSO compatibility work. Branch is his account-mapping rewrite. Nobody else has been inside it since the spike. He must not be pulled into Contoso implementation'"),
    (P, "'09:10-11:10 | Contoso export formatter | Julia | Cosmetic/demo fix, independent'"),
    (P, "'Elena's Wednesday departure creates a fallback risk. If migration slips, Daniel needs a 30-minute production-permission/runbook handoff before Elena leaves Wednesday noon. Schedule that contingency if migration is not complete by Monday EOD'"),
    (P, "an eight-row immediate-actions table at 09:10 followed by a fourteen-row execution timetable, with a gate check at 12:10 and an EOD status check"),
    (P, "'12:10-16:10 | SSO API compatibility patch | Marcus | Protected, no Contoso implementation' against '12:10-15:40 | Contoso permission patch | Daniel | Reassigned from Marcus'"),
    (P, "'Sarah - pricing page: 3h, independent of billing/SSO', 'Sarah - board pack non-revenue: 4h, independent of billing backfill'"),
    (P, "'Contoso broken export is not import-breaking - Peter confirmed current export imports correctly. The real urgent issue is delegated-admin permission failure'"),
    (P, "'Send Contoso comms: real issue is delegated-admin permission, not broken import; permission patch targeted today; compliance export targeted today'"),
    (P, "five stale items corrected, covering all four urgent entries plus the launch-support owner: 'Marcus should not own launch support - meeting notes already moved launch support to Julia'"),
    (P, "chain outstanding, Security closed, and Atlas told SSO is on track for Tuesday afternoon ahead of Wednesday EOD"),
    (P, "'Onboarding instrumentation is not a launch blocker' and 'Julia - onboarding launch: 2h, no longer blocked by Marcus instrumentation'"),
    (P, "'Contoso broken export is not import-breaking... The real urgent issue is delegated-admin permission failure', with only the permission patch on the dated chain"),
    (P, "every anchor correct, including the two that caught four other runs: 'Billing schema migration | Mon 12:10 | Thu 15:00' and 'Public pricing page | Thu 17:00'. Also Tue 16:00 CET, Fri 12:00, Fri 10:00, Daniel at 3.5h, the 90-minute backfill and Marcus's Tuesday 09:00-13:00 absence"),
    (P, "'Earliest realistic completion: Tuesday 14:00' with the four-step path, plus two buffered fallbacks that each remain inside the Wednesday commitment"),
    (P, "nine unknowns, including whether the stated durations cover production deployment, whether QA needs Marcus during the Atlas session, and that 'availability windows do not specify breaks or timezone alignment'"),
])


run("qwen3.8-flash", "007", [
    (P, "'Enterprise SSO: schema -> Marcus's compatibility patch -> QA regression -> production rollout', written out again as numbered steps 4-6 with clock targets"),
    (P, "'Contoso contractual export: schema -> delegated-admin permission patch -> Julia produces/sends export', with the date-format fix listed separately under parallel work"),
    (P, "'Pricing approval | Not blocked by live page. Mockups are acceptable. Sarah submits before 12:00 for same-day committee clearance' and 'it cannot go public until Priya's committee clears it'"),
    (P, "'Security review | Not a blocker. Maya confirmed review is closed and approved for current scope. Update release checklist; no re-review unless auth flow changes'"),
    (P, "'Board revenue charts | Blocked until billing backfill completes. Backfill target done Mon 13:40'"),
    (R, "detects the contention outright - 'Marcus is the only person who can do the SSO compatibility patch, and he is also fastest on the Contoso permission patch' - and resolves it by sequencing him through both, on a reason that covers the order rather than the ownership: 'This is the fastest path to the Tuesday 16:00 contractual export'. Daniel is held as the billing backup only, never considered for the permission patch, and the compatibility work is pushed to 14:10 as a result"),
    (R, "states the ground - 'Only Marcus can do it' - and releases the instrumentation, but the capacity that frees goes to the substitutable Contoso patch, which moves the rollout from an achievable Tuesday afternoon to 16:40"),
    (P, "'Julia fixes the Contoso export date format for Tuesday's demo', 09:10-11:10"),
    (P, "'Daniel: remain billing backup; no action unless migration slips. If it slips, he needs a 30m handoff with Elena before Wednesday noon'"),
    (P, "a fully timed Monday from 09:10, migration started first, and every other owner given a window before 10:40"),
    (R, "Julia's export does overlap Marcus's SSO work, but the two engineering items run one after the other through one person: permission patch 12:10-14:10, compatibility patch from 14:10"),
    (P, "'Sarah builds the packaging approval pack... submits to Priya before 12:00' with board non-revenue sections and the pricing page build alongside"),
    (P, "'Contoso date format | Not a production blocker. It is a Tuesday demo request'"),
    (P, "'I confirm to Anja/CEO that the delegated-admin permission issue will be fixed and the compliance export delivered today. I separate this from the date-format demo request', against the Tuesday 16:00 CET contractual deadline"),
    (P, "all four in one action: 'Security review is closed/approved, onboarding instrumentation is not a launch blocker, pricing approval can use mockups, not live-page screenshots', plus Rachel splitting the Contoso ticket"),
    (P, "chain outstanding, Security closed for the current scope, and Laura told SSO is tracking for Wednesday EOD"),
    (P, "'Julia: schedule onboarding launch support for Wed 09:00-11:00; instrumentation is not required'"),
    (P, "'Contoso compliance export | Blocked by delegated-admin permission bug, not by date format' beside 'Contoso date format | Not a production blocker'"),
    (P, "every anchor intact: the four SSO durations with a split that adds to exactly 4h, Marcus at 2h on the permission patch, Julia at 1h, the 90-minute backfill, Sarah's 1.5-hour pack, Marcus unavailable Tue 09:00-13:00, Elena's Wednesday noon, Tue 16:00 CET, Wednesday EOD, Friday noon for onboarding and the 12:00 committee cutoff"),
    (P, "'Best realistic case: Tue 16:40 if Marcus can split the 4h compatibility patch. Conservative case: Wed 12:00 if the 4h compatibility patch must be continuous' - the Wednesday is offered as a conditional fallback, not as the earliest, and the Tuesday figure is supported by its own schedule"),
    (P, "nine unknowns including whether 'about four focused hours' means consecutive hours, the merge order between the formatter and the permission patch, and an explicit timezone assumption"),
])


def main() -> None:
    out_dir = Path(__file__).resolve().parent
    for model, runs in VERDICTS.items():
        lines: list[str] = []
        for run_number, (rows, penalties) in sorted(runs.items()):
            run_id = f"monday-003__{model}__{run_number}"
            if len(rows) != len(CRITERIA):
                raise SystemExit(f"{run_id}: {len(rows)} labels for {len(CRITERIA)} criteria")
            for criterion, (result, evidence) in zip(CRITERIA, rows):
                lines.append(
                    json.dumps(
                        {
                            "run_id": run_id,
                            "criterion_id": criterion,
                            "result": result,
                            "evidence": evidence,
                            "reason": evidence,
                        },
                        ensure_ascii=False,
                    )
                )
            lines.append(
                json.dumps(
                    {
                        "run_id": run_id,
                        "kind": "penalties",
                        "violations": [
                            {"type": t, "evidence": e, "reason": r} for t, e, r in penalties
                        ],
                    },
                    ensure_ascii=False,
                )
            )
        path = out_dir / f"{model}.verdicts.jsonl"
        path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        print(f"wrote {path.name} ({len(runs)} run(s), {len(lines)} lines)")


if __name__ == "__main__":
    main()
