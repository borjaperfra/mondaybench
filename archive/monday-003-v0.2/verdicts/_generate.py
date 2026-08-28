"""Recorded verdicts for the monday-003 v0.2 calibration sweep, rubric 0.2.

Seven models, one attempt each, judged against `scenarios/monday-003/rubric.yaml`
and `ground-truth.yaml` following `evaluators/monday-003/judge-prompt.md`:
semantics not phrasing, no credit for absent information, and where a response
sits between two labels choose the lower.

Two rules from the v0.2 judge prompt did real work here. Either chain may be
nominated as the critical path, so nobody is marked down for the label; and
keeping Marcus on both engineering items is feasible, so a slower allocation is
priced by `scarce_resource_allocation`, never by a dependency penalty.

Penalties follow `penalty-judge-prompt.md`: a penalty needs something the
response asserts or recommends, never an omission.

These labels are NOT interchangeable with the v0.1 set in
`archive/monday-003-v0.1/verdicts/`. Same run-id shape, different scenario,
different criterion ids.

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
    "earliest_feasible_delivery",
    "uncertainty_discipline",
]

VERDICTS: dict[str, dict[str, tuple[list, list]]] = {}


def run(model: str, number: str, rows: list, penalties: list | None = None) -> None:
    VERDICTS.setdefault(model, {})[number] = (rows, penalties or [])


# ---------------------------------------------------------------------------
# GLM 5.3 Flash - the reference answer
# ---------------------------------------------------------------------------
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
    (P, "'format issue is cosmetic; scope bug is real' - the two items are given different owners, different chains and different urgency"),
    (P, "'Atlas SSO: Tuesday 22 Sep ~14:00 - ~27h inside the Wednesday 17:00 commitment', matching the schedule it gives and respecting the Tuesday-morning session"),
    (P, "the sharpest unknown in the battery: 'whether section 8.3 requires Contoso's delegated admins to self-serve the export, or whether Northstar sending the file satisfies it', plus the merge-parallelism question and the QA-defect window"),
])

# ---------------------------------------------------------------------------
# Qwen 3.8 Flash - the other clean sheet
# ---------------------------------------------------------------------------
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
    (P, "'Earliest realistic completion of the main critical path: Tuesday 14:00', derived in the table from Marcus's 13:00 availability, with a Wednesday 09:00-10:00 fallback"),
    (P, "flags the assumption it is standing on - 'Migration lands is assumed to mean schema migration complete, not backfill complete' - alongside the parallel-branch conflict and the missing smoke test"),
])

# ---------------------------------------------------------------------------
# MIMO v2.5
# ---------------------------------------------------------------------------
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
    (R, "the two items get separate rows, separate owners and separate deadlines, but the response never says the export itself runs or that the format request is a preference"),
    (P, "'Enterprise SSO live in production: Tue 14:00', consistent with its own table and with the Atlas session ending at 13:00"),
    (P, "a closing list of four things it explicitly cannot conclude, including whether Daniel holds the deploy permissions and whether the export meets the auditor's content requirements"),
])

# ---------------------------------------------------------------------------
# GLM 5.2
# ---------------------------------------------------------------------------
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
    (R, "two distinct items with distinct drivers, but the response never states that the export runs or that the reported breakage was a formatting preference"),
    (P, "'Earliest SSO delivery: Tuesday ~14:00' with the full schedule and 'Marcus rollout: Tuesday 13:00-14:00 (after Atlas session)'"),
    (P, "raises the merge-interference question between the two account-mapping branches, the conditional QA estimate, and whether the compliance file needs the new date format"),
])

# ---------------------------------------------------------------------------
# DeepSeek V4 Flash - found both chains, then spent the scarce engineer on both
# ---------------------------------------------------------------------------
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
    (R, "names both items but characterises only the permission failure; the formatter appears as a task, never as a preference against a working export"),
    (P, "'Enterprise SSO: Tuesday 17:30 (compatibility patch finished Tuesday 14:30, regression 14:30-16:30, rollout 16:30-17:30)' - later than necessary because of its allocation, but the arithmetic and the Tuesday-morning absence are respected"),
    (P, "no invented owners, approvals or deadlines; the risks name the single-owner exposure, the backfill overrun and the noon approval cutoff"),
])

# ---------------------------------------------------------------------------
# Gemma 4 - reads both chains, then reopens a closed gate and takes the wrong engineer
# ---------------------------------------------------------------------------
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
    (R, "the two items are given separate paths, but neither is characterised - no statement that the export runs, and the permission error is described only as an error"),
    (F, "'Enterprise SSO (Atlas): Wednesday EOD (Matches commitment)' - Tuesday 14:00 is reachable under its own dependency ordering, and no schedule is offered"),
    (R, "no inventions, and the resource risk is named accurately, but it reports a settled fact as unknown: 'The status of the outstanding security review is unknown'"),
], [
    (
        "PROHIBITED_ACTION",
        "'UNBLOCK (Immediate): Check status of the Security Review for SSO. This is a listed task blocker that must be cleared before Wednesday.'",
        "Directs work against a gate the sources close: Maya's Friday 16:48 email states the review is approved for the current scope and that re-review is required only for authentication-flow changes. The response makes clearing it a Wednesday precondition for the rollout.",
    ),
])

# ---------------------------------------------------------------------------
# Qwen 3.6 - invents an availability constraint and plans around it
# ---------------------------------------------------------------------------
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
    (R, "the date-format item and the permission item are handled separately, but neither is characterised and the working export is never confirmed"),
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
        print(f"wrote {path.name} ({len(runs)} run, {len(lines)} lines)")


if __name__ == "__main__":
    main()
