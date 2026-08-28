"""Recorded verdicts for the monday-003 v0.3 calibration, rubric 0.3.

Two runs per model against one prompt.

  run-001  the response generated during the v0.2 sweep, RESCORED under rubric
           0.3. The candidate sources did not change between 0.2 and 0.3 - the
           rendered prompt still hashes to aaf788f3… - so these are valid
           samples of this prompt, and rescoring them isolates the rubric
           effect from run-to-run variance.
  run-002  a fresh generation, so v0.3 is not calibrated only on the responses
           its rubric was designed against.

Nineteen criteria carry the same definitions they had in 0.2, so run-001 carries
the same labels for them. Two do not:

  * `contoso_state_separated` was rewritten to score the operational
    distinction rather than a form of words. Every run-001 label was
    re-derived under the new definition.
  * `factual_plan_accuracy` is new. Every run-001 label is new, judged against
    `factual_anchors` in the answer key.

Judged following `evaluators/monday-003/judge-prompt.md`: semantics not
phrasing, no credit for absent information, either chain may be nominated as the
critical path, and where a response sits between two labels choose the lower.

Penalties follow `penalty-judge-prompt.md`: a penalty needs something the
response asserts or recommends, never an omission.

These labels are NOT interchangeable with the v0.1 set in
`archive/monday-003-v0.1/verdicts/` (different scenario, disjoint criterion ids)
nor with the v0.2 set in `archive/monday-003-v0.2/verdicts/` (same criterion ids
for nineteen of twenty-one, different definitions for the rest).

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


# ===========================================================================
# run-001 - the v0.2 responses, rescored under rubric 0.3
# ===========================================================================

run("glm5.3-flash", "001", [
    (P, "'Chain A - Atlas Enterprise SSO': migration Mon 09:00-12:00, compatibility Mon 12:30-16:30, QA Tue 09:00-11:00, rollout Tue 13:00-14:00, with owners and the reason each step waits"),
    (P, "'Chain B - Contoso compliance export': same migration root, permission patch, then 'Julia - produce & send export, 1h'; the date-format fix is listed separately under parallel work"),
    (P, "'Mockups are acceptable per Priya, so the pack isn't blocked on a live page' and 'Pricing approval - process gate only: submit before 12:00 for same-day sign-off', with the public page following on Wednesday"),
    (P, "'Approved Fri 16:48 for current scope (account-mapping rewrite + tenant permission model). Permission-check fixes inside scope need no re-review' and the tracker item is closed"),
    (P, "'Verify backfill kicked off (1.5h, automated) -> unblocks Sarah's revenue charts'"),
    (P, "'Reassign contoso_permission_patch Marcus -> Daniel (Rachel invited reassignment; Daniel knows the model from SCIM; Marcus is the bottleneck and the compatibility patch cannot move off him)', with the 30-minute walkthrough booked for 09:30"),
    (P, "'Marcus is the constraint. Fix: permission patch -> Daniel; instrumentation hold released. His remaining load fits: Mon 12:30-16:30, Tue 13:00-14:00'"),
    (P, "'Julia - date-format fix, 2h, Mon AM (independent; needed for Tuesday demo - preference, not contractual)'"),
    (P, "'if not landed by Tue 12:00, Elena does the 30-min Daniel handoff immediately - she leaves Wed noon; Daniel can execute Wed AM'"),
    (P, "an 09:15 start on the migration, the reassignment and the walkthrough in the same quarter hour, then customer replies, tracker hygiene and a 13:30 backfill check"),
    (P, "Daniel on the permission patch from noon while Marcus runs the compatibility patch 12:30-16:30; neither chain waits for the other"),
    (P, "'Sarah - pricing page 3h + approval pack 1.5h Mon' and 'board pack non-revenue, 4h, Mon/Tue', both independent of the engineering work"),
    (P, "'CEO update on Contoso: format issue is cosmetic; scope bug is real, fix scheduled, deadline safe'"),
    (P, "'Reply to Anja Weber - she asked for confirmation today: delivery before Tue 16:00 CET', with the chain scheduled to land Monday afternoon"),
    (P, "a dedicated 'Tracker hygiene' block closing all four: Security, instrumentation, the launch-support owner and the Contoso investigation"),
    (P, "the chain still outstanding, Security closed for the current scope, and 'Wednesday EOD remains the Atlas commitment' confirmed back to Laura"),
    (P, "'descope onboarding instrumentation from launch (Julia confirmed Fri) and release Marcus's 3h hold; move onboarding launch support Marcus -> Julia per Friday's decision'"),
    (P, "'format issue is cosmetic; scope bug is real, fix scheduled, deadline safe' - and structurally, the formatter sits in parallel work owned by Julia while only the permission patch gates the Tuesday delivery"),
    (R, "one substitution: 'Daniel can execute Wed AM, still ahead of the Wed 15:00 external milestone'. The billing migration's external deadline is Thursday 2026-09-24 15:00. Every other anchor it uses is correct, and the contingency conclusion survives the correction, so the plan is not materially altered"),
    (P, "'Atlas SSO: Tuesday 22 Sep ~14:00 - ~27h inside the Wednesday 17:00 commitment', matching the schedule it gives and respecting the Tuesday-morning session"),
    (P, "the sharpest unknown in the battery: 'whether section 8.3 requires Contoso's delegated admins to self-serve the export, or whether Northstar sending the file satisfies it', plus the merge-parallelism question and the QA-defect window"),
])

run("qwen3.8-flash", "001", [
    (P, "a step table giving the four SSO steps with owners, durations, earliest start and earliest finish, and 'Primary critical path: Elena migration -> Marcus SSO compatibility -> QA regression -> Marcus SSO rollout'"),
    (P, "'Contoso deadline path: Elena migration -> Marcus 30-min handoff -> Daniel permission patch -> Julia compliance export'; the format fix sits in parallel work"),
    (P, "'Pricing page must be live before packaging approval - Stale. Priya confirmed mockups are acceptable' and 'Pricing page public launch depends on packaging approval clearing'"),
    (P, "'Stale. Maya closed review Friday 16:48. Permission-check and configuration fixes inside approved scope do not need re-review'"),
    (P, "'Board revenue charts depend on billing backfill completion', with the backfill scheduled Mon 12:10-13:40"),
    (P, "'Reassign contoso_permission_patch from Marcus to Daniel. Rachel updates ticket. Marcus supports with 30-minute handoff', and the table prices Daniel at 3.5h against Marcus's 2h"),
    (P, "'Cannot delegate SSO compatibility work. Must protect time for SSO compatibility and rollout' plus 'Remove onboarding instrumentation and onboarding launch support from his critical path'"),
    (P, "'Julia - Contoso date-format fix. 2 hours. Not blocking production; needed for Tuesday demo'"),
    (P, "'If migration slips, Daniel needs 30 minutes of production-permission/runbook transfer before Wednesday noon'"),
    (P, "a 09:10 start on the migration, corrections at 09:15, the reassignment at 09:20 and every delegation issued before 09:35"),
    (P, "'12:40 Daniel starts Contoso permission patch. Marcus starts SSO compatibility patch' - the two chains run side by side out of the same root"),
    (P, "'Sarah - packaging approval pack. Does not require a live page' and 'Sarah - board non-revenue sections. Can proceed now'"),
    (P, "'Date format: non-blocking, demo preference' listed under false or stale blockers, handled by Julia in parallel"),
    (P, "'Delegated-admin permission error: blocking contractual compliance export' with 'Real blocker for Tuesday 16:00 contractual compliance export' and delivery scheduled Mon 17:10"),
    (P, "all four named at 09:15 and again under 'False or stale blockers', including the launch-support owner move"),
    (P, "the chain outstanding, Security closed, and the Atlas Wednesday EOD commitment met by Tuesday"),
    (P, "'Marcus onboarding launch support - Stale. Meeting notes moved launch support to Julia' and instrumentation deferred as not a launch blocker"),
    (P, "'Contoso broken export is one issue - It is two issues: Date format: non-blocking, demo preference. Delegated-admin permission error: blocking contractual compliance export'"),
    (P, "every anchor it uses is carried through intact - the four SSO durations, Daniel at 3.5h plus a half-hour handoff, the backfill at 90 minutes, Marcus unavailable until Tuesday 13:00, Elena's Wednesday-noon cutoff, Tuesday 16:00 CET and Friday 12:00 for onboarding. No substitutions found"),
    (P, "'Earliest realistic completion of the main critical path: Tuesday 14:00', derived in the table from Marcus's 13:00 availability, with a Wednesday 09:00-10:00 fallback"),
    (P, "flags the assumption it is standing on - 'Migration lands is assumed to mean schema migration complete, not backfill complete' - alongside the parallel-branch conflict and the missing smoke test"),
])

run("mimo-v2.5", "001", [
    (P, "'Path B - Enterprise SSO' written out as a four-step chain with durations, '~10h sequential. Completes Tuesday ~14:00'"),
    (P, "'Path A - Contoso Compliance Export': migration -> Daniel permission patch -> deploy -> Julia export -> deliver"),
    (R, "gets the gate - 'Packaging approval: Tue afternoon (if submitted before 12:00)' ahead of 'Pricing page public: Tue EOD' - but treats the pack as blocked on the page ('packaging_approval_pack | Sarah | pricing_page done') and never finds the mockup route"),
    (P, "'Security review is already approved (Maya, Fri 16:48) - the task tracker is stale' and the blocker table strikes it through as resolved"),
    (P, "'Sarah: board_pack_revenue | billing_backfill (automated, 90 min) | Mon ~14:00'"),
    (P, "'Key decision: Reassign contoso_permission_patch from Marcus to Daniel. Daniel was in the permission model two weeks ago, needs only a 30-min walk from Marcus, and his 3.5h runs in parallel with Marcus's 4h compatibility patch'"),
    (P, "'Marcus is a single point of failure for SSO. The compatibility branch is his rewrite - nobody else has been inside it... Mitigate: Protect his afternoon. No other assignments', with the instrumentation demoted to post-launch enrichment"),
    (P, "'Message Julia: Start contoso_export_formatter (date format, 2h) immediately - independent'"),
    (P, "risk 6: 'Elena's Wednesday departure without Daniel handoff... She said she needs 30 min... Action: Schedule the handoff for Tuesday or Wednesday morning at the latest'"),
    (P, "a numbered 09:10-17:00 sequence starting with the Security correction and 'Message Elena: Start billing_schema_migration now. Nothing else matters until this lands', plus a full per-person allocation table"),
    (P, "the allocation table runs Daniel on the permission patch and Marcus on the compatibility patch through the same Monday afternoon"),
    (P, "'Sarah | pricing_page (3h) | board_pack_non_revenue (4h)' Monday, and board_pack_revenue as soon as the backfill lands"),
    (R, "handles it correctly - Julia, 2h, Monday morning, 'None' dependency - but never states that the reported breakage is cosmetic or that the file imports correctly"),
    (P, "'Path A - Contoso Compliance Export (contractual, Tue 16:00 CET)' and 'Critical path delivery (Contoso): Monday 17:00 - 23 hours ahead of contractual deadline'"),
    (P, "Security and instrumentation struck out in the blocker table, and onboarding launch reassigned to Julia in the parallel-work table"),
    (P, "the chain outstanding, Security closed Friday 16:48, and the Wednesday EOD commitment confirmed to Laura"),
    (P, "'Onboarding instrumentation - Not a launch blocker. De-prioritize; ship post-launch' with 'onboarding_launch | Julia | None confirmed'"),
    (P, "rescored under the 0.3 definition: the two items have separate owners, separate chains and separate deadlines, only the permission fix gates the contractual delivery ('Path A' ends in 'deliver to Contoso'), and the formatter carries dependency 'None'. The distinction is unambiguous in the plan even though the prose never asserts that the export runs"),
    (P, "the anchors it uses survive intact - Daniel 3.5h plus the 30-minute walk, the backfill at 90 minutes, Marcus's Atlas session, Tue 16:00 CET, Friday 10:00 for the board. The 'no hard external deadline this week' cell is attached to packaging_approval_pack, which genuinely carries none, so it is not a substitution"),
    (P, "'Enterprise SSO live in production: Tue 14:00', consistent with its own table and with the Atlas session ending at 13:00"),
    (P, "a closing list of four things it explicitly cannot conclude, including whether Daniel holds the deploy permissions and whether the export meets the auditor's content requirements"),
])

run("glm5.2", "001", [
    (P, "'Elena: billing schema migration (3h) -> Marcus: SSO compatibility patch (4h) -> QA: SSO regression (2h) -> Marcus: production rollout (1h)' with 'The billing schema migration is the shared root'"),
    (P, "'Contoso permission patch gates compliance export file production (Julia)' and the chain branches 'off the same root but runs on a parallel person'"),
    (F, "inverts the gate and misses the shortcut: 'Pricing page build gates packaging approval pack (screenshots needed)', with the pack scheduled for Tuesday once the page exists; Priya's line that mockups are acceptable is never used"),
    (P, "'Security review for SSO is already approved (Maya's email, Friday 16:48). Remove from blocker list' and 'permission/config fixes are in-scope'"),
    (P, "'board revenue charts (Sarah, via backfill)' and 'Backfill completes ~14:00 Monday'"),
    (P, "'Daniel takes contoso_permission_patch (3.5h). He knows the permission model from SCIM work. Needs 30 min walkthrough with Marcus, scheduled for 12:30', with the reason that it 'runs on a parallel person, so it doesn't extend the SSO critical path'"),
    (R, "frees him - 'release Marcus's 3h hold', 'These two stale items are... consuming Marcus's capacity' - and keeps him on the patch, but never states that the compatibility work has no substitute"),
    (P, "'Do contoso_export_formatter (2h) this morning - for Contoso's Tuesday demo (Peter's request)'"),
    (R, "has the mechanics - 'Daniel needs the 30-min permission transfer and runbook walkthrough' - but frames it as something to do 'if it slips beyond Wednesday noon', when Elena is gone by then"),
    (P, "09:15 stale corrections, 09:20 Elena starts, 09:25 Daniel briefed, 09:30 Julia directed, 12:30 walkthrough, 13:00 Marcus starts"),
    (P, "'Daniel works 13:00-16:30' against 'Marcus starts SSO compatibility patch... Done ~17:00 Monday'"),
    (P, "'Start pricing_page (3h) today. Begin board_pack_non_revenue (4h) in parallel'"),
    (P, "separates the demo request from the contractual one throughout: 'Contoso demo formatter: Julia, Monday morning' against 'Contoso compliance export... hard contractual deadline'"),
    (P, "'Contoso compliance export (Tuesday 16:00 CET, hard contractual deadline)' with 'Reply to Anja: confirmation that file will be delivered Monday EOD'"),
    (P, "Security, instrumentation and the launch-support owner all corrected explicitly at 09:15 and under 'Not actually blocking (stale)'"),
    (P, "chain outstanding, Security approved for current scope, Wednesday EOD confirmed to Laura"),
    (P, "'core flow is ready; launch support is now Julia's' and instrumentation released"),
    (P, "rescored under the 0.3 definition: 'Contoso demo formatter: Julia, Monday morning' sits in parallel work with no dependant, while 'Contoso compliance export (Tuesday 16:00 CET, hard contractual deadline)' is gated only by the permission patch. Which one threatens Tuesday is never in doubt"),
    (P, "no substitutions: the durations, the 30-minute walkthrough, the 90-minute backfill, Elena's Wednesday noon, the Atlas session, Tue 16:00 CET and Friday 12:00 are all carried correctly. Its pricing error is a wrong gate, priced by pricing_dependency, not a wrong value"),
    (P, "'Earliest SSO delivery: Tuesday ~14:00' with the full schedule and 'Marcus rollout: Tuesday 13:00-14:00 (after Atlas session)'"),
    (P, "raises the merge-interference question between the two account-mapping branches, the conditional QA estimate, and whether the compliance file needs the new date format"),
])

run("deepseek-v4-flash", "001", [
    (P, "the four SSO steps in order with owners and durations, and 'QA - sso_regression (2h) -> after compatibility patch', 'Marcus - sso_production_rollout (1h) -> after regression'"),
    (P, "'The Contoso export (Julia, 1h) runs after the permission patch but is not on the SSO critical path'"),
    (R, "'Packaging approval: Can be submitted with mockups, so no need to wait for live page' - the mockup route is there, but the response never states that approval gates the public page"),
    (P, "'Security review: Already approved (Maya's email), no blocker'"),
    (P, "'Board pack revenue charts: After backfill (Monday 13:30)', with Elena kicking the backfill off at 12:00"),
    (F, "keeps the substitutable work on the contested engineer and rules the substitute out explicitly: '13:00 - Marcus starts contoso_permission_patch (2h)' and 'Daniel: available for support, but not needed on critical path', while Daniel's 3.5h offer sits unused in the sources"),
    (R, "releases the instrumentation - 'not a blocker, can be deprioritized' - but then spends his Monday afternoon on the Contoso patch and pushes the compatibility work into Tuesday"),
    (P, "'Julia: contoso_export_formatter (formatting change) - independent'"),
    (F, "Elena's Wednesday departure, the production-permission transfer and the Daniel fallback appear nowhere in the plan or the risks"),
    (R, "starts with the migration and delegates Sarah's work in the morning, but loses the afternoon to the wrong engineer and double-books Julia at 15:00 for both the formatter and the compliance export"),
    (R, "'The permission patch and compatibility patch are sequential because both require Marcus' - the two chains are explicitly serialised through one person"),
    (P, "'Sarah works on pricing_page (3h) and packaging_approval_pack (1.5h)... board_pack_non_revenue (4h) in parallel'"),
    (R, "keeps the format fix with Julia and off the critical work, but never says it is cosmetic or that the customer confirmed the file imports"),
    (P, "'Contoso compliance deadline: Tuesday 16:00 CET - hard deadline; must complete permission patch and export by then'"),
    (P, "Security cleared, instrumentation deprioritised, the approval pack freed from the page, and the onboarding launch given to Julia"),
    (P, "chain outstanding, Security approved, Wednesday EOD intact"),
    (P, "'Julia: onboarding_launch (2h) - onboarding is ready, can launch anytime' and 'Marcus: onboarding_instrumentation (3h) - not a blocker'"),
    (P, "rescored under the 0.3 definition: the formatter is listed under PARALLEL WORK as 'independent' with no dependant, while 'Contoso compliance deadline: Tuesday 16:00 CET - hard deadline; must complete permission patch and export by then' ties the dated commitment to the permission fix alone"),
    (P, "no substitutions: the four SSO durations, Marcus's 2h on the permission patch, the 90-minute backfill, the Tuesday 09:00-13:00 Atlas session, Tue 16:00 CET and the noon approval cutoff are all correct, and its 15:00-17:30 arithmetic is right. The Julia double-booking is a scheduling fault, priced by monday_plan"),
    (P, "'Enterprise SSO: Tuesday 17:30 (compatibility patch finished Tuesday 14:30, regression 14:30-16:30, rollout 16:30-17:30)' - later than necessary because of its allocation, but the arithmetic and the Tuesday-morning absence are respected"),
    (P, "no invented owners, approvals or deadlines; the risks name the single-owner exposure, the backfill overrun and the noon approval cutoff"),
])

run("gemma4", "001", [
    (P, "'Path A (Atlas SSO): Elena (Billing Schema Migration) -> Marcus (Compatibility Patch) -> QA (Regression) -> Marcus (Production Rollout)'"),
    (P, "'Path B (Contoso Compliance): Elena (Billing Schema Migration) -> Marcus (Permission Patch) -> Julia (File Generation/Send)'"),
    (P, "'Sarah can build the pricing page and prepare the packaging approval pack (mockups are acceptable per Priya)' and 'Pricing Page launch is blocked by Priya's committee approval'"),
    (F, "reopens the closed gate: 'Check status of the Security Review for SSO. This is a listed task blocker that must be cleared before Wednesday' and 'if it is not cleared by Tuesday, the SSO rollout is at risk'. Maya's Friday 16:48 approval is never read"),
    (P, "'Board Revenue Charts are blocked by the Billing Backfill'"),
    (F, "'Instruct Marcus to pivot from onboarding instrumentation to the contoso_permission_patch' - the contested engineer is put on the one item that has a substitute, and Daniel appears only as a 30-minute consultation"),
    (R, "takes him off the instrumentation but does not protect the capacity: the SSO compatibility patch is never assigned a slot anywhere in the plan"),
    (P, "'Assign Julia to the contoso_export_formatter (2h). This satisfies the demo request for Tuesday and can be done in parallel'"),
    (F, "Elena's Wednesday departure, the permission transfer and the Daniel fallback are absent; the only Elena action is 'Ensure Elena starts the billing_schema_migration today'"),
    (R, "no times and the wrong order - the Marcus pivot is action 1 and starting the migration is action 4, filed under MONITOR"),
    (R, "the format fix and the board work run in parallel, but the two engineering chains are effectively serialised through Marcus and the SSO patch is never scheduled"),
    (P, "'Sarah can build the pricing page and prepare the packaging approval pack' and 'Sarah can complete all non-revenue sections of the board pack'"),
    (R, "the format work goes to Julia in parallel and displaces nothing, but the response never says the export is working or the request cosmetic"),
    (P, "'Path B is the most time-sensitive due to the Tuesday 16:00 CET deadline'"),
    (R, "instrumentation and the pricing order are corrected; Security is re-raised as an open gate and the Contoso task is only partly updated"),
    (R, "chain outstanding and Wednesday intact, but Security is reported as unknown when it is closed"),
    (P, "'Julia can proceed with the onboarding launch (instrumentation is no longer a blocker)'"),
    (P, "rescored under the 0.3 definition: the formatter is under PARALLEL WORK and appears in none of the four numbered blockers, while 'Blocker 2: The Contoso Compliance Export is blocked by the Permission Patch' and 'Path B is the most time-sensitive due to the Tuesday 16:00 CET deadline' put the permission defect alone on the dated commitment"),
    (P, "few values are used and all of them are right: Marcus unavailable Tuesday 09:00-13:00, the formatter at 2 hours, Tuesday 16:00 CET, the Atlas Wednesday EOD commitment, the backfill gating the revenue charts. Its Security claim is a state error, priced by security_state_stale, not a substituted value"),
    (F, "'Enterprise SSO (Atlas): Wednesday EOD (Matches commitment)' - Tuesday 14:00 is reachable under its own dependency ordering, and no schedule is offered"),
    (R, "no inventions, and the resource risk is named accurately, but it reports a settled fact as unknown: 'The status of the outstanding security review is unknown'"),
], [
    (
        "PROHIBITED_ACTION",
        "'UNBLOCK (Immediate): Check status of the Security Review for SSO. This is a listed task blocker that must be cleared before Wednesday.'",
        "Directs work against a gate the sources close: Maya's Friday 16:48 email states the review is approved for the current scope and that re-review is required only for authentication-flow changes. The response makes clearing it a Wednesday precondition for the rollout.",
    ),
])

run("qwen3.6", "001", [
    (P, "'Elena: Billing Schema Migration (3 hours) ... Marcus: SSO Compatibility Patch (4 hours). Blocked by #1 ... QA: SSO Regression. Blocked by #2 ... Marcus: SSO Production Rollout. Blocked by #3'"),
    (P, "'Once Daniel fixes the permission check, Julia can generate and send the file (1 hour)', with the date-format fix listed separately as independent"),
    (R, "'Prepare the submission pack (margin, structure, mockups)' and 'Pricing Page Public Launch: Blocked by Packaging Approval' - but it also directs 'Ensure it is built so she can take screenshots for Priya's committee', keeping the page-first order it just contradicted"),
    (R, "sees both records and refuses to resolve them: 'This is a contradiction. Unknown: Is the security review actually closed in the system? If not, it may block the SSO rollout checklist. Action: Verify with Noah or Maya'"),
    (P, "'Board Revenue Charts (Sarah): Blocked by Billing Backfill (Elena). Backfill runs 90 mins after migration'"),
    (R, "makes the right assignment - 'Assign Daniel to fix the delegated admin permission check (3.5 hours)... Daniel needs 30 mins with Marcus' - but justifies it only as workstream separation, and then contradicts it in the risks by listing 'Contoso Permission Fix (2h)' among Marcus's load"),
    (R, "names the constraint - 'Marcus's unique code ownership' - and defers the instrumentation, but spends the analysis considering whether to delay the migration to keep Marcus free 'for Contoso support if needed'"),
    (P, "'Assign Julia to fix the date format in the exporter (2 hours)'"),
    (R, "has the transfer and the fallback but misdates the window: 'schedule a 30-min slot for Tuesday morning before her 12:00 cutoff' - the cutoff is Wednesday 12:00"),
    (R, "the morning is spent deliberating rather than starting: the migration is pushed to 13:00 after an explicit reversal, and the reasoning for the delay rests on a Monday absence that does not exist"),
    (R, "both chains do move - Daniel and Julia on Contoso while SSO proceeds - but the SSO sequencing collapses into overlapping Monday-afternoon slots"),
    (P, "'Board Pack (Sarah): Non-revenue sections can proceed today', 'Pricing Page (Sarah): Build the page. Independent of SSO', 'Packaging Approval (Sarah): Prepare the submission pack'"),
    (R, "'Contoso Date Format (Julia): Can start immediately today. Independent of SSO' - kept off the committed work, but never characterised as a preference against a working export"),
    (P, "'Contoso has a contractual deadline (Tuesday 16:00 CET) and an internal demo (Tuesday). This is a distinct workstream from SSO', filed as 'Highest Business Risk'"),
    (R, "defers the instrumentation and moves launch support to Julia, but leaves Security open and keeps the page-before-approval order"),
    (R, "the chain and the Wednesday commitment are right; Security is left unresolved"),
    (P, "'Onboarding Launch: Ready (Julia)' with the instrumentation deferred per Friday's chat"),
    (R, "rescored under the 0.3 definition and still short of it: the two items get different owners and only the export carries the contractual date, but the plan opens with a single '09:00-10:30: Unblock Contoso (Highest Business Risk)' block that assigns both fixes under one 'contractual deadline' justification, leaving which one threatens Tuesday ambiguous at the point of decision"),
    (F, "two substitutions, one of them load-bearing. 'Marcus is unavailable Monday 09:00-13:00 (Atlas session)' contradicts availability.csv and Marcus's own message, and the whole Monday plan is built on it; 'a 30-min slot for Tuesday morning before her 12:00 cutoff' moves Elena's Wednesday-noon departure to Tuesday"),
    (F, "'Earliest Realistic Completion: Wednesday Morning (if Monday slips) or Tuesday EOD (if Monday goes perfectly)' - hedged onto Wednesday, and the Tuesday variant rests on a Monday schedule in which the compatibility patch and the migration run at the same time"),
    (R, "the risk section is otherwise honest, but the plan is built on an availability constraint the response invented and then treated as fact"),
], [
    (
        "MATERIAL_HALLUCINATION",
        "'Constraint: Marcus is unavailable Monday 09:00-13:00 (Atlas session) and Tuesday 09:00-13:00 (Atlas session).'",
        "The Atlas pre-rollout session is Tuesday only, in both Marcus's Monday 08:29 message and availability.csv, which shows him available 09:00-17:30 on Monday. The invented Monday absence is asserted as fact and drives the decision to push the migration to 13:00.",
    ),
    (
        "MAJOR_PLANNING_ERROR",
        "'Direct Elena to start Migration Monday 13:00' together with 'if Elena starts migration Mon 13:00, Marcus patches Mon PM' and 'Marcus can do the patch Monday afternoon (13:00-17:00 is 4.5 hours, enough for 4h work + handoff)'.",
        "The recommended plan starts the compatibility patch at the same moment as the three-hour migration it depends on. Marcus's own Friday statement is that he cannot finish the compatibility work until the migration lands.",
    ),
    (
        "MAJOR_CONTRADICTION",
        "'Direct Elena to start Migration Monday 13:00' against 'Since we are pushing migration to Tuesday, the revenue charts are blocked until Wednesday' and 'If migration lands Tuesday, backfill runs Tuesday PM, charts ready Wednesday'.",
        "Both the Monday start and the Tuesday start are directed in the same response, and the downstream board-pack plan is built on the Tuesday one. A reader cannot tell which instruction to follow.",
    ),
])



# ===========================================================================
# run-002 - fresh generations under rubric 0.3
# ===========================================================================

run("glm5.3-flash", "002", [
    (P, "'Chain B - Atlas Enterprise SSO (Wed EOD commitment): migration -> Marcus compatibility patch (4h) -> QA regression (2h) -> Marcus production rollout (1h)'"),
    (P, "'Chain A - Contoso compliance export (tightest deadline: Tue 16:00 CET, contractual, auditor window): migration -> delegated-admin permission patch (Daniel 3.5h + 0.5h Marcus walkthrough) -> Julia produces & sends file (1h)'"),
    (P, "'build the packaging approval pack using mockups (Priya confirmed they are acceptable - do not wait for the live page) and submit before 12:00 for same-day clearance', with 'do not serialize page -> screenshots -> approval' under blockers"),
    (P, "'Security review was closed Friday 16:48 (Maya's email - approved, in-scope fixes exempt from re-review). The release checklist and task list are out of date'"),
    (P, "'Chain C - Board revenue charts (Fri 10:00): migration -> backfill (1.5h, automated after Elena kicks off) -> Sarah revenue charts (2h)'"),
    (P, "'Reassign contoso_permission_patch Marcus -> Daniel (Rachel invited this; Marcus is pinned on the SSO patch and unavailable Tue AM). Marcus reviews Daniel's PR before it lands'"),
    (P, "'release his 3h onboarding-instrumentation hold - not a launch blocker' with 'Marcus is pinned on the SSO patch' given as the reason the permission work has to move to someone else"),
    (P, "'Julia: ... Date-format fix Tue 09:00-11:00 (before the Tue afternoon demo)' and 'formatter fix (after compliance file is sent - same exporter, don't risk it)'"),
    (P, "'Elena leaves Wed 12:00 - only material if migration slips to Wednesday. Cheap insurance: book the 30-min Daniel handover Tuesday PM; cancel if migration lands Monday'"),
    (P, "every delegation issued between 09:15 and 09:40, opening with 'Confirm Elena starts the schema migration now - it gates everything'"),
    (P, "Daniel developing the permission patch from 09:30 while Marcus starts the compatibility patch the moment the migration lands, with 'Daniel: can develop the permission patch before the migration lands; it only goes in after'"),
    (P, "'Sarah: pricing page build (3h), approval pack via mockups, board non-revenue (4h) - all independent of engineering'"),
    (P, "'a two-line update separating the two broken export issues: (a) date format - cosmetic, Tue AM fix; (b) delegated-admin scope - real blocker, fix in flight'"),
    (P, "'Confirm to Anja (Contoso) today, as she requested, that the compliance export lands before Tue 16:00'"),
    (P, "'Close stale items: security-review task, investigate Contoso exports (diagnosed), onboarding-instrumentation blocker flag', with the pricing order corrected by the mockup instruction"),
    (P, "the chain outstanding, Security closed Friday 16:48, and Laura told SSO is on track for the Wednesday commitment"),
    (P, "'Onboarding instrumentation is also no longer a launch blocker (Julia decoupled it Friday)' and 'Julia ... Owns onboarding launch (due Fri 12:00)'"),
    (P, "'(a) date format - cosmetic, Tue AM fix; (b) delegated-admin scope - real blocker, fix in flight' - the separation is both stated and built into the plan"),
    (R, "the closest call in the battery. No deadline is misquoted, but the pricing contingency reads 'submission slips to Tue 12:00 -> approval Wed AM -> page still public by Wed 17:00 but buffer nearly gone'. The page is due Thursday 17:00, so publishing Wednesday leaves a full day; 'buffer nearly gone' only holds if the deadline is taken to be Wednesday. Immaterial - the plan works either way - so PARTIAL, not FAIL"),
    (P, "'Atlas SSO live: Tuesday ~14:00 (QA 09:00-11:00; Marcus rollout 13:00-14:00)', with a Wednesday fallback that still meets the commitment"),
    (P, "six substantive unknowns including the definition of 'migration lands', the merge-conflict risk between the two branches, whether section 8.3 requires the customer to run the export themselves, and 'if it triggers auth-flow changes, Maya's email requires security re-review - the one thing that could genuinely threaten Wednesday'"),
])

run("glm5.2", "002", [
    (P, "'billing_schema_migration (Elena, 3h) ... api_compatibility_patch (Marcus, 4h) ... sso_regression (QA, 2h) ... sso_production_rollout (Marcus, 1h)' in order, with 'the entire week is gated by Elena's billing schema migration'"),
    (P, "'contoso_permission_patch (Marcus, 2h) - Monday after schema lands' then 'contoso_compliance_export (Julia, 1h) - Monday after permission patch'; the formatter sits in parallel work"),
    (R, "has the gate - 'Pricing page: cannot go public until packaging approval clears' - but keeps the page first: 'Once the page is built, assemble the packaging approval pack (1.5h)'. Priya's mockup line is never used"),
    (P, "'Security review for Enterprise SSO - approved Friday 16:48 by Maya; covers current scope including the account-mapping rewrite and tenant permission model. No re-review required'"),
    (P, "'Board pack revenue charts: wait for the backfill (Monday PM) to avoid double-counted expansion events'"),
    (R, "detects the contention and prices the substitute exactly - 'Daniel: available as backup for contoso_permission_patch (3.5h + 0.5h walkthrough with Marcus)' - then declines to use him and serialises both patches through Marcus, with no reason given for preferring that. The stated justification is only 'Contoso deadline is Tuesday 16:00, so this goes first'"),
    (R, "'Release his 3h held for onboarding instrumentation; it is not a launch blocker' - but the capacity freed is spent on the substitutable Contoso patch, pushing the compatibility work into Tuesday, and the response never states that the compatibility work has no substitute"),
    (P, "'Do the export formatter change (2h) today for Peter's Tuesday demo'"),
    (P, "'if it slips past Tuesday, Daniel takes over (30-min transfer, no current production permissions). Elena leaves Wednesday noon - no room for a Wednesday retry by her'"),
    (P, "a numbered day starting with a 15-minute tracker cleanup and 'Start Elena on billing schema migration now (Elena, 3h, 09:30-12:30)', with every other owner briefed before 10:00"),
    (R, "the two chains are run one after the other through one person: 'after Elena's schema lands (~12:30): (a) contoso_permission_patch 2h, then (b) api_compatibility_patch'"),
    (P, "'continue pricing page (3h) and non-revenue board pack (4h) in parallel'"),
    (P, "'contoso_export_formatter (2h, for Tuesday demo)' kept in parallel work against 'Contoso compliance export ... ahead of Tuesday 16:00' as the contractual item"),
    (P, "'Reply to Anja at Contoso - confirm delegated-admin fix is in flight and the Q3 compliance export will be delivered ahead of Tuesday 16:00'"),
    (P, "'Clean up the stale task tracker': Security approved, instrumentation not a launch blocker, and the Contoso investigation already diagnosed"),
    (P, "chain outstanding, Security approved for current scope, and Laura told Wednesday EOD is on track"),
    (P, "'Onboarding launch (2h, ready now, Friday 12:00 deadline) is hers to ship anytime this week' with the instrumentation hold released"),
    (P, "the formatter is in parallel work for 'Peter's Tuesday demo' while only the permission patch gates the contractual export; which one threatens Tuesday is never in doubt"),
    (R, "one substitution: the delivery table reads 'Billing migration + backfill | Wed 15:00'. The stated external deadline is Thursday 2026-09-24 15:00. It changes nothing downstream - its own plan lands the migration Monday - so the plan is not materially altered"),
    (P, "'Enterprise SSO production rollout | Wed 17:00 | Tue ~17:00' - late because of its allocation, but consistent with its own schedule and with Marcus unavailable until Tuesday 13:00"),
    (P, "raises the conditional QA estimate, whether the formatter and the compliance export are the same file, the 12:00 committee cutoff, and 'I cannot confirm from the available evidence whether Daniel has conflicting commitments'"),
])

run("mimo-v2.5", "002", [
    (P, "the ASCII critical-path diagram: 'Elena: schema migration (3h)' -> 'Marcus: SSO compatibility (4h)' -> 'QA: regression (2h)' -> 'Marcus: prod rollout (1h)' with times against each"),
    (P, "the same diagram's left branch: migration -> 'Marcus: Contoso patch (2h)' -> 'Julia: compliance export (1h)' -> 'SEND TO CONTOSO', with the date-format fix listed under parallel work as independent"),
    (R, "'Packaging committee availability... If they are not [available], the pricing page can't go public this week' gives the gate, but the dependency table says 'packaging_approval_pack | pricing_page' and the mockup route is never found"),
    (P, "'Security review: Approved (Maya, Fri 16:48). No re-review needed unless auth flow changes', struck through in the stale-task list"),
    (P, "'board_pack_revenue | billing_backfill | Elena (automated) | Mon 13:40'"),
    (F, "denies the substitute exists: 'There is no other person who can own either patch - the account-mapping branch is Marcus's exclusively', and serialises both patches through him. Daniel's offer of 3.5 hours plus a half-hour walkthrough is in the sources and is never engaged"),
    (R, "releases the instrumentation and states the no-substitute ground for the compatibility patch, but does not protect the capacity: Marcus is given 5.5 hours of afternoon coding and the SSO work is pushed into Tuesday behind the Contoso patch"),
    (P, "'Contoso date format fix (DD/MM/YYYY) | Julia | Mon 09:10-11:10 | Independent of permission patch'"),
    (P, "'10:00 Coordinate Elena -> Daniel: permission transfer + runbook walk (30 min). Do it now while both are fresh, not last-minute before Elena's Wednesday departure'"),
    (P, "an 09:10 start on the migration - 'This is the #1 unlock' - with every other owner briefed by 09:30 and gate checks at 12:10, 14:10 and 15:15"),
    (R, "the two chains are serialised through one person: 'Marcus must do the Contoso patch first (Tuesday deadline) then immediately pivot to the SSO compatibility patch'"),
    (P, "'Pricing page build | Sarah | Mon, ~3h | Start now, no blockers' and 'Board pack - non-revenue sections | Sarah | Mon-Tue, ~4h'"),
    (P, "'Contoso export broken: Diagnosed. Not actually broken - imports work. Two separate fixable issues'"),
    (P, "'Reply to Anja Weber (Contoso): confirm the delegated-admin permission fix is in progress, compliance export will be delivered well before Tuesday 16:00 CET'"),
    (P, "all three struck through explicitly under 'Close stale task list items immediately'"),
    (P, "chain outstanding, Security approved Friday 16:48, and Laura confirmed for the Wednesday EOD commitment"),
    (P, "'Onboarding event instrumentation | Marcus | NOT a launch blocker. Do after critical path work is done' with 'Onboarding launch prep | Julia | Tue-Thu'"),
    (P, "'Not actually broken - imports work. Two separate fixable issues', with only the permission patch feeding 'SEND TO CONTOSO' in the diagram"),
    (F, "two substituted deadlines, both used to compute buffers it then reports: 'Billing schema migration | Mon 12:10 | Wed 15:00 | ~51h' - the stated deadline is Thursday 15:00 - and 'Pricing page | Mon ~12:10 | Wed EOD | ~29h', where the page is due Thursday 17:00"),
    (P, "'SSO production rollout | Tue ~16:30' - consistent with its own diagram and with Marcus unavailable until Tuesday 13:00"),
    (R, "nine risks, most of them substantive, but the plan rests on one unsupported claim it treats as fact - that nobody but Marcus can own either patch - and every allocation decision follows from it"),
], [
    (
        "MATERIAL_HALLUCINATION",
        "'There is no other person who can own either patch - the account-mapping branch is Marcus's exclusively.'",
        "Daniel states in #support-escalations that he was in the permission model two weeks ago for the SCIM work, can take the Contoso patch, and needs three and a half hours plus half an hour with Marcus. The claim is material: it is the stated reason both patches are serialised through one engineer, which pushes the SSO rollout from Tuesday 14:00 to Tuesday 16:30.",
    ),
])

run("gemma4", "002", [
    (R, "'Path A (SSO): Elena (Billing Migration: 3h) -> Backfill (1.5h) -> Marcus (Compatibility Patch: 4h) -> QA (Regression: 2h) -> Marcus (Rollout: 1h)'. The four real steps are in order, but the backfill is inserted as a prerequisite of the compatibility patch; it gates only the board revenue charts, and the insertion adds 90 minutes to the path"),
    (P, "'Path B (Contoso Compliance): Elena (Billing Migration) -> Marcus (Permission Patch: 2h) -> Julia (Export File: 1h)', with the formatter kept off it"),
    (P, "'Sarah can build the pricing page and mockups for the committee' and 'Pricing Page launch is blocked by Priya's committee approval'"),
    (F, "reopens the closed gate again: 'Identify the owner of the Security Review for SSO and force a resolution today', and under risks 'We know it is outstanding on the checklist, but we do not know who owns it or why it hasn't been cleared'. Maya's Friday 16:48 email is never read"),
    (P, "'Board Blocker: Revenue charts are blocked by the completion of the billing backfill'"),
    (F, "'Confirm with Marcus that he will prioritize the contoso_permission_patch immediately after Elena's migration lands' - the contested engineer keeps the one item with a substitute, and Daniel is used only as the billing-migration backup"),
    (R, "takes him off the instrumentation - 'no longer a blocker' - and names him as the single point of failure, but hands him the substitutable Contoso work and never schedules the compatibility patch he alone can do"),
    (P, "'Assign Julia to handle the Contoso Export Formatter (2h) for the Tuesday demo after she completes the compliance export task'"),
    (P, "'Instruct Daniel to prepare to take over the Billing Migration if Elena cannot finish it by Tuesday EOD, ensuring he meets Elena for the 30-min handoff', with the midday Wednesday departure named in the risks"),
    (R, "no clock times, and starting the root dependency is not an action at all this time - Elena appears only as 'Primary' in an ownership list while the first instruction is about Marcus"),
    (R, "the format fix and the board work run in parallel, but the two engineering chains are serialised through Marcus"),
    (P, "'Assign Sarah to complete the Pricing Page and Packaging Pack today' and 'Sarah can complete all non-revenue sections of the board pack'"),
    (R, "sequences the formatter behind the compliance export so it displaces nothing, but never says the export runs or that the request is cosmetic"),
    (P, "'the Contoso Compliance deadline (Tuesday 16:00 CET)' named in the critical path and carried into the delivery estimate"),
    (R, "instrumentation and the pricing order are corrected, Security is re-raised as an open gate, and the Contoso investigation is only partly updated"),
    (R, "chain outstanding and Wednesday intact, but Security is reported as unknown when it is closed"),
    (P, "'Julia can proceed with the launch (existing analytics are sufficient; Marcus's instrumentation is no longer a blocker)'"),
    (P, "'Contoso Blocker: Julia cannot deliver the compliance file until Marcus fixes the delegated-admin permission check', with the formatter in parallel work and absent from all four numbered blockers"),
    (P, "the values it uses are right: Marcus blocked Tuesday 09:00-13:00, the stated durations, Tuesday 16:00 CET, the Atlas Wednesday EOD commitment, the backfill gating the revenue charts. Its backfill-before-patch claim is a wrong relationship, priced by sso_chain, and its Security claim a wrong state, priced by security_state_stale"),
    (F, "'Enterprise SSO: Wednesday EOD (Matches commitment, provided Marcus uses his afternoon on Tuesday/Wednesday effectively)' - Tuesday 14:00 is reachable under its own ordering, and no schedule is offered"),
    (R, "no inventions, and the single-point-of-failure risk is named accurately, but it reports a settled fact as unknown"),
], [
    (
        "PROHIBITED_ACTION",
        "'UNBLOCK (Product): Identify the owner of the Security Review for SSO and force a resolution today.'",
        "Maya's Friday 16:48 email closes the review for the current scope and exempts permission-check and configuration fixes from re-review. The response directs work against a gate that is shut, and its risk section makes clearing it a condition of the Wednesday rollout.",
    ),
])

run("qwen3.6", "002", [
    (R, "the SSO steps are in order - migration, compatibility patch, QA regression, production rollout - but the chain is headed by a step that does not exist: '1. Monday AM: Product unblocks Security Review (Prerequisite for SSO)'"),
    (R, "'Secondary Critical Path: Contoso Compliance Export' gets the permission fix and the file generation in order, but then couples the formatter to the delivery: 'Date Format Fix (Julia) is independent but must be combined with the permission fix for the final file'"),
    (F, "pricing does not appear anywhere in the response - no packaging approval, no committee, no page. Neither half of the criterion is addressed"),
    (F, "makes the closed review the first item on its critical path and directs 'Contact Maya (Security) immediately... Get written confirmation or a quick Slack approval to remove the outstanding status', calling it 'a hard blocker for the SSO release checklist'"),
    (P, "'Revenue charts depend on Billing Backfill (Elena, post-migration)'"),
    (R, "assigns Daniel with the walkthrough scheduled - 'Assign Daniel to contoso_permission_patch. Schedule a 30-minute sync with Marcus' - but misprices him as '2.5 hrs: 3.5 hrs work - 0.5 hrs with Marcus', subtracting the handoff from his own estimate instead of adding it"),
    (R, "keeps the compatibility patch with Marcus and notes the instrumentation is not a launch blocker, but never states that the work has no substitute, and lets his Monday drain while the migration waits until 13:00"),
    (P, "'Julia: Start contoso_export_formatter (date format) immediately. This is independent of the permission fix'"),
    (P, "'If she slips, Daniel needs the 30-min handoff before she leaves Wednesday noon'"),
    (R, "the morning goes to chasing a closed Security review and the root dependency is not started until 13:00, which is what pushes the whole SSO chain into Wednesday"),
    (R, "Daniel and Marcus do work different chains, but the Contoso patch is scheduled from 12:00 and finished by 15:00 while the migration it depends on runs 13:00-16:00"),
    (R, "Sarah gets the board non-revenue work, but the entire pricing workstream is missing from the parallel plan"),
    (R, "the formatter runs in parallel and displaces nothing, but it is never characterised as a preference against a working export"),
    (P, "'Contoso deadline is Tuesday 16:00 CET. We need the fix in place by Monday EOD to allow Julia to test/generate the file'"),
    (R, "the instrumentation is overridden, but Security is promoted back to a blocker and the pricing entries are not addressed at all"),
    (R, "the chain and the Wednesday commitment are right; Security is treated as an open prerequisite"),
    (P, "'Julia owns launch support. Marcus's instrumentation is not a blocker'"),
    (R, "the two items have different owners and only the permission fix gates the export, but 'must be combined with the permission fix for the final file' leaves the formatter looking like part of the contractual delivery"),
    (R, "one substitution: Daniel is priced at '2.5 hrs effective' by subtracting the half-hour walkthrough from his 3.5-hour estimate, when the sources add it. The Contoso delivery still lands Monday under either reading, so the plan is not materially altered"),
    (F, "'Enterprise SSO (Atlas): Wednesday EOD' with the rollout on Wednesday - Tuesday 14:00 is reachable, and the delay is caused by its own decision to hold the migration until 13:00"),
    (R, "the risk section is honest and invents nothing, but it files a settled fact as a high risk: 'if Security re-opens the review, it kills the Wednesday SSO deadline'"),
], [
    (
        "PROHIBITED_ACTION",
        "'09:10 - 10:00: Unblock Security Review (SSO). Contact Maya (Security) immediately... Get written confirmation or a quick Slack approval to remove the outstanding status. Why: This is a hard blocker for the SSO release checklist.'",
        "Maya's Friday 16:48 email closes the review for the current scope. The response makes clearing it the first hour of the day and the first step of its critical path, spending the morning on a gate that is already open.",
    ),
    (
        "MAJOR_PLANNING_ERROR",
        "'Daniel: contoso_permission_patch (2.5 hrs effective). Starts after Marcus handoff (~12:00)' and 'If Daniel finishes patch by 15:00 Monday, Julia can fix format and generate by 17:00 Monday', against 'Elena: billing_schema_migration (3 hrs). Starts ~13:00 Monday'.",
        "The permission patch is scheduled to start, finish and be handed to Julia before the schema migration it depends on has landed. Marcus states in #support-escalations that the patch sits on the same account-mapping layer and can only go in after the migration.",
    ),
])

run("qwen3.8-flash", "002", [
    (P, "'billing_schema_migration -> api_compatibility_patch -> sso_regression -> sso_production_rollout' under the Atlas Wed EOD heading, with a clock schedule for every step"),
    (P, "'billing_schema_migration -> contoso_permission_patch -> contoso_compliance_export. This is the true contractual blocker'; the date-format work is a separate parallel item"),
    (P, "'Packaging approval blocks public pricing page. Unblock: Sarah submits approval pack with mockups before 12:00', and risk 9 names Sarah's own plan as the thing to override"),
    (P, "'Security review: Not blocking. Maya's email confirms approval for current scope. Permission-check and configuration fixes inside approved scope do not need re-review'"),
    (P, "'Kick off / monitor billing reconciliation backfill. Owner: Elena. Purpose: Unblocks final board revenue charts'"),
    (P, "detects it by name - 'Critical shared resource: Marcus. He is the only realistic owner for SSO compatibility, and he is also the fastest owner for the Contoso permission patch' - and resolves it deliberately the other way: Marcus takes the permission patch at his 2-hour rate, Daniel is armed as a triggered fallback ('If permission patch slips, activate Daniel'), and the reason is stated twice, as speed and as merge risk ('If Daniel takes permission instead, parallel work may create merge/dependency risk'). Both commitments are met - Contoso Mon 15:10, SSO Tue 16:40 - with the stated durations respected throughout"),
    (R, "states the constraint exactly - 'Only realistic owner for SSO compatibility... Needs protection Monday afternoon' - and releases the 3-hour instrumentation hold, but then spends that protected afternoon on the substitutable Contoso patch, which is what moves the rollout from 14:00 to 16:40"),
    (P, "'Start Contoso date-format fix: 2026-09-21 -> 21/09/2026. Owner: Julia. Needed for Tuesday demo'"),
    (P, "'Tue 11:30-12:00 Elena transfers production migration permissions/runbook to Daniel as contingency', ahead of her Wednesday-noon departure"),
    (P, "seven actions all timestamped 09:10, opening with 'Start billing schema migration now - unblocks SSO, Contoso permission fix, and board revenue data'"),
    (R, "Julia's export does run alongside Marcus's SSO work, but the two engineering items are serial through one person: the compatibility patch does not start until the permission patch is finished at 14:10"),
    (P, "'Start pricing page / mockups for packaging approval. Owner: Sarah' and 'Board non-revenue content can proceed immediately'"),
    (P, "'Contoso date-format request: Already handled by Julia; not a production blocker', and 'The broken export is not broken for import'"),
    (P, "'Reply to Anja and CEO: delegated-admin export will be delivered by Tue 16:00; internal plan is to deliver early'"),
    (P, "all four: Security marked approved, instrumentation removed from the blocker list, the Contoso investigation split into its two real items, and Sarah's page-first approval plan called out as stale in risk 9"),
    (P, "chain outstanding, Security approved for the current scope, and Laura told SSO is on track for Wed EOD"),
    (P, "'Onboarding instrumentation: Remove from launch blocker list; schedule after SSO/Contoso critical path' with 'Julia: Onboarding launch readiness can happen Monday midday'"),
    (P, "'The broken export is not broken for import; the real issue is delegated-admin permission, plus a separate date-format preference for Tuesday's demo'"),
    (P, "every anchor it uses is intact: the four SSO durations summing to 4h across a split it accounts for exactly (Mon 14:10-17:30 plus Tue 13:00-13:40), the 2h permission patch, the 1h export, the 90-minute backfill, Marcus unavailable until Tue 13:00, Elena out from Wed noon, Tue 16:00 CET, Wed 17:00, and the 12:00 committee cutoff"),
    (P, "'Enterprise SSO production rollout: Tuesday 16:40' with the full schedule behind it, dependencies in order and the Tuesday-morning absence respected, plus a stated fallback if the 4-hour patch cannot be split"),
    (P, "ten numbered unknowns, including whether the 4-hour patch can be split at all, whether the permission patch needs its own deploy step, and whether the compliance file must carry the new date format"),
])

run("deepseek-v4-flash", "002", [
    (P, "'billing_schema_migration -> api_compatibility_patch (Marcus) -> sso_regression (QA) -> sso_production_rollout (Marcus)' under the Atlas commitment"),
    (P, "'billing_schema_migration -> contoso_permission_patch (Marcus) -> contoso_compliance_export (Julia)', with the formatter listed separately as independent"),
    (R, "'Pricing approval: Committee may request changes; not on critical path but could delay public launch' gives the gate, but the plan is page-first - 'Pricing page (3h) - build it, then create the approval pack (1.5h)' - and the mockup route is never used"),
    (P, "'Security review: Already approved (Maya's email) - no action needed'"),
    (P, "'Board pack: Friday morning (revenue charts after backfill, which completes Monday)'"),
    (R, "detects the contention this time - 'the two paths diverge but share Marcus's time on Tuesday afternoon' - and engages the substitute in the risks, but declines him on a reason that does not hold: 'Daniel could assist but would need Marcus's time for a walkthrough, which is scarce on Tuesday'. Marcus's Monday is free and Daniel is idle all day; the resulting plan lands the contractual export at exactly 16:00 on a deadline the customer states cannot move"),
    (R, "deprioritises the instrumentation but gives the freed Tuesday to the substitutable Contoso patch, and never states that the compatibility work has no substitute"),
    (P, "'Contoso export formatter (2h) - independent, needed for Tuesday demo. Owner: Julia'"),
    (P, "'She is available only until Wednesday noon, so any delay must be absorbed by Daniel (requires 30-min handover)'"),
    (P, "'09:10 Start billing schema migration immediately (3h)' with Julia and Sarah delegated in the same slot and Marcus queued for 12:10"),
    (R, "the chains are split across days rather than run together: Monday is SSO only, and the Contoso patch waits until Tuesday 13:00 although Daniel is free on Monday and Marcus finishes at 16:10"),
    (P, "'Pricing page (3h) - build it, then create the approval pack (1.5h) and submit to Priya' plus 'board pack non-revenue sections (any time)'"),
    (R, "keeps the formatter with Julia and off the committed work, but never says the export runs or that the request is a preference"),
    (P, "'Contoso hard deadline: Export must be delivered by Tuesday 16:00 CET. This requires the permission patch to be done by 15:00 and Julia's 1-hour export to start immediately after'"),
    (P, "Security closed, instrumentation deprioritised, and onboarding launch support given to Julia"),
    (P, "chain outstanding, Security closed, Wednesday EOD intact"),
    (P, "'Onboarding: Julia owns launch support; Marcus's instrumentation is not a blocker - deprioritize'"),
    (P, "'Contoso export formatter - independent, needed for Tuesday demo' against 'Contoso hard deadline: Export must be delivered by Tuesday 16:00 CET', which only the permission patch gates"),
    (P, "no substitutions: the four SSO durations, the 2h permission patch, the 1h export, the 90-minute backfill, Tuesday 09:00-13:00, Wednesday noon, the 30-minute handover, Tue 16:00 CET and the 3h/1.5h pricing items are all carried correctly. Its 'won't be done before 17:30' remark about a patch its own table ends at 16:10 is an internal slip, not a substituted value"),
    (P, "'Enterprise SSO production rollout: Tuesday 17:00 (after regression Tuesday morning and rollout 16:00-17:00)' - late because of the allocation, but the ordering and the Tuesday-morning absence are respected"),
    (P, "no invented owners, approvals or deadlines; the risks name the migration overrun, the Daniel walkthrough cost, and unconfirmed QA availability"),
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
