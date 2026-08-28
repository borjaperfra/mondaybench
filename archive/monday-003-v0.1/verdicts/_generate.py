"""Recorded verdicts for the monday-003 calibration sweep, rubric 0.1-draft.

Seven models, one attempt each, judged against `scenarios/monday-003/rubric.yaml`
and `ground-truth.yaml` following `evaluators/monday-003/judge-prompt.md`:
semantics not phrasing, no credit for absent information, and where a response
sits between two labels choose the lower.

Penalties follow `penalty-judge-prompt.md`: a penalty needs something the
response asserts or recommends, never an omission.

Nothing here assigns points. `mondaybench evaluate --verdicts` does the scoring.
"""

from __future__ import annotations

import json
from pathlib import Path

P, R, F = "PASS", "PARTIAL", "FAIL"

CRITERIA = [
    "critical_path_identified",
    "marcus_bottleneck",
    "instrumentation_nonblocking",
    "security_not_blocking",
    "hard_dependency_order",
    "contoso_delegated",
    "elena_risk_managed",
    "pricing_owner_and_mockups",
    "board_work_owned_correctly",
    "monday_sequence",
    "parallel_work",
    "board_pack_partial_parallelization",
    "urgent_vs_critical",
    "pricing_cycle_detected_and_broken",
    "stale_tasks_overridden",
    "sso_current_state",
    "contoso_current_state",
    "onboarding_current_state",
    "earliest_delivery",
    "no_invented_blockers",
]

VERDICTS: dict[str, dict[str, tuple[list, list]]] = {}


def run(model: str, number: str, rows: list, penalties: list | None = None) -> None:
    VERDICTS.setdefault(model, {})[number] = (rows, penalties or [])


FULL_CHAIN = (
    "'Elena - billing schema migration (3h) -> Marcus - API compatibility patch (4h) -> "
    "QA - regression (2h) -> Marcus - production rollout (1h)'"
)

run("deepseek-v4-flash", "001", [
    (P, "the four steps in order with owners and durations, and 'Security review is already approved. Onboarding instrumentation is not a launch blocker. So the real critical work starts with Elena's migration'"),
    (P, "'Tell Marcus to release the 3h he is holding for onboarding instrumentation... He should stand by to start the SSO compatibility patch as soon as the migration lands'"),
    (P, "'It is not required for launch'; the instrumentation is moved behind the SSO work"),
    (P, "'Security review is already approved'; the risk section correctly keeps the scope-change caveat rather than reopening the gate"),
    (P, "'Hard sequence: billing migration -> compatibility patch -> QA regression -> production rollout'"),
    (P, "'Ask Julia to fix the Contoso export date formatting today. It is not a production outage'"),
    (P, "'Treat Tuesday EOD as the effective migration deadline'; 'if Elena cannot finish migration, the 30-minute handoff must happen Tuesday'"),
    (P, "'Tell Sarah to produce pricing mockups for packaging approval now. She should use design mockups, not wait for the live pricing page'"),
    (P, "'Sarah can build narrative, customer sections, and non-revenue charts now. Only revenue charts wait for billing migration/backfill'"),
    (P, "the plan opens with 'Have Elena start the billing migration immediately. This is the critical-path trigger', then frees Marcus, then delegates"),
    (P, "Contoso, pricing approval, board non-revenue and the onboarding launch all listed as proceeding without the SSO chain"),
    (P, "'Only revenue charts wait for billing migration/backfill'"),
    (P, "the CEO's URGENT is handled as a delegated two-hour fix while the migration keeps first position"),
    (P, "'Pricing approval circular dependency is removable because mock screenshots are accepted'"),
    (P, "all four stale entries named and corrected, including 'The tracked billing migration deadline is too late for SSO'"),
    (P, "chain still pending, Security approved, Wednesday EOD held as the commitment"),
    (P, "'Contoso \"broken export\" is not broken; it is a date-format preference'; Tuesday demo named"),
    (P, "'Onboarding launch - Can proceed with existing analytics; Marcus's extra event instrumentation can ship later'"),
    (P, "'Migration: Mon 09:10-12:10, Marcus patch: Mon 12:10-16:10, QA: Tue 09:00-11:00, rollout: Tue 11:00-12:00' - 'Tuesday 22 Sep, ~12:00'"),
    (P, "no invented approvals, owners or blockers; the unknowns are flagged as unknowns"),
])

run("glm5.3-flash", "001", [
    (P, f"{FULL_CHAIN}, with 'Security review is not on this path (approved Friday)'"),
    (P, "'frees 3h of Marcus (the SSO bottleneck)' and books him 'Mon 13:00-17:00, fits his day'"),
    (P, "'his instrumentation task is off the critical list (Julia confirmed Friday it's not needed for launch)'; deferred to Wed/Thu"),
    (P, "'Close \"unblock Security review\" - approved Friday'"),
    (P, "'Migration -> patch -> QA -> rollout (SSO chain)' listed under real dependencies and never violated"),
    (P, "'Assign Julia the Contoso formatter fix today (2h). Investigation is already done (stale task)'"),
    (P, "'Book Elena + Daniel 30-min handover today or Tuesday (prod migration permissions + runbook). Must happen before Elena leaves Wednesday noon'"),
    (P, "'Sarah - pricing mockups (1.5h) -> Daniel runs internal packaging approval (mock screenshots accepted)'"),
    (P, "board non-revenue explicitly independent, revenue charts explicitly dependent, both with Sarah"),
    (P, "a timestamped Monday: '09:15 - Kick Elena off on the migration now... This is the single gating item for the week'"),
    (P, "six parallel streams listed with owners and windows"),
    (P, "'Revenue board charts depend on post-migration/backfill dataset' against non-revenue starting Monday"),
    (P, "'It's a 2h fix, not a crisis'"),
    (P, "'meeting notes imply approval -> page -> screenshots -> approval. Broken by Daniel's clarification: mock screenshots are fine'"),
    (P, "task-list hygiene closes or rewrites all four stale entries, noting the list 'pre-dates Friday's Slack'"),
    (P, "chain pending, Security approved, Wednesday latest-useful for Atlas IT"),
    (P, "'root cause is date formatting only, and Contoso confirmed imports work either way'"),
    (P, "'Onboarding launch itself - flow is ready; can proceed on its own timeline'"),
    (P, "'Migration Mon ~09:30-12:30, Patch Mon 13:00-17:00, QA Tue 09:00-11:00, Rollout Tue ~11:00-12:00' - 'Tuesday midday'"),
    (P, "flags the missing backfill owner and the unstated approval date as unknowns rather than inventing them"),
])

run("qwen3.8-flash", "003", [
    (P, "the chain as a diagram plus an explicit 'What is NOT on the critical path' list covering Security, instrumentation, Contoso and pricing"),
    (P, "'Marcus: free him for SSO'; reserves 12:10-16:10 for the patch and hands off to QA immediately after"),
    (P, "'Tell Marcus to stop treating onboarding instrumentation as a launch blocker'"),
    (P, "'Unblock Security review -> done/approved'; 'No action unless scope changes'"),
    (P, "'QA can start regression only after the completed patch is delivered'; rollout after green light"),
    (P, "'Delegate the DD/MM/YYYY export formatter to Julia. Target: complete today'"),
    (P, "'Daniel can take over billing migration only after Elena transfers production migration permissions... about 30 minutes before Elena leaves Wednesday 12:00'"),
    (P, "'Ask Sarah to spend 1.5 hours on pricing mockups today. Send mockups to Daniel for internal packaging approval. Do not require the live pricing page before approval'"),
    (P, "board non-revenue independent, final revenue charts waiting, both Sarah's"),
    (P, "a timestamped Monday opening with 'Elena: start billing migration now' and 'Protect her time until roughly 12:10'"),
    (P, "a parallel-work table covering Contoso, onboarding, mockups, approval, the page, board non-revenue and Security"),
    (P, "'Final revenue charts must wait until billing migration/backfill data is clean'"),
    (P, "'Contoso export is broken | Export succeeds; only date format differs' - handled without displacing the migration"),
    (P, "'break the pricing circular dependency'; 'Pricing page must exist before approval | Mockups are acceptable for internal approval'"),
    (P, "all four stale entries closed or downgraded, plus the too-late tracked migration deadline"),
    (P, "chain pending, Security approved, Wednesday commitment held"),
    (P, "'not production-blocking; only formatting for Tuesday demo'"),
    (P, "'Flow is ready; instrumentation can ship later'"),
    (P, "splits QA across Monday 16:10-17:30 and Tuesday morning to reach 'Tuesday around 10:40', then settles on 'Tuesday 11:00-12:00' with handoff buffers. Every dependency and duration is respected and QA's Monday availability supports it; this is a faster plan than the canonical one rather than a worse one"),
    (P, "'QA Wednesday availability is not provided' and the backfill scope are raised as unknowns, not filled in"),
])

run("glm5.2", "001", [
    (P, f"{FULL_CHAIN}; 'This is the longest dependency chain and determines the earliest important delivery'"),
    (P, "'release the 3h held for onboarding instrumentation... stand ready to start the compatibility patch the moment Elena's migration lands (~12:30), so he can finish by ~16:30 today'"),
    (P, "'it's not a launch blocker per Julia'; the freed three hours are explicitly deferrable post-launch"),
    (P, "'already approved Friday; no action unless scope changes'"),
    (P, "the chain is stated once and never contradicted by the plan"),
    (P, "'Message Julia - start Contoso export formatter now (2h, needed by Tuesday afternoon for the demo). Independent, no dependencies'"),
    (P, "'not a blocker if migration runs Mon/Tue. Daniel is fallback but needs 30 min handover; only relevant if migration slips to Wed morning'"),
    (P, "'she should produce pricing mockups (1.5h) for internal packaging approval, NOT the live pricing page. The page comes after approval'"),
    (P, "Sarah keeps both, with non-revenue startable now and revenue charts held"),
    (P, "'Ping Elena immediately - start billing schema migration now (09:15)' is action one, with Marcus staged behind it"),
    (P, "Julia, Sarah's mockups, Sarah's board non-revenue and the onboarding launch all listed as free of the critical path"),
    (P, "'Revenue charts depend on migration + backfill completion. Sarah should not freeze them until that's done; she can do everything else first'"),
    (P, "the €110k account is delegated in position three while the migration holds position one"),
    (P, "'circular/incorrect. Daniel clarified approval accepts mockups; the page follows approval'"),
    (P, "'Update the task list - remove stale blockers' naming Security, instrumentation and the reversed pricing order"),
    (P, "chain pending, Security approved Friday, Wednesday EOD confirmed to Laura"),
    (R, "the formatter is delegated with the Tuesday demo named, but the response never states that the export itself works and the issue is only the date format"),
    (P, "'core flow is ready; can ship whenever we choose, independent of SSO'"),
    (P, "'Migration done ~12:30 Mon, patch ~16:30 Mon, QA Tue 09:00-11:00, rollout Tue 11:00-12:00' - 'Tuesday around midday'"),
    (P, "the backfill scope, the approval turnaround and the onboarding launch trigger are all raised as unknowns"),
])

run("mimo-v2.5", "001", [
    (P, "the chain as a tree with 'Total sequential work: 10 hours' and 'This chain is the only workstream that determines a hard external commitment'"),
    (P, "'Message Marcus: clear his calendar for afternoon'; 'This releases 3 hours of Marcus's capacity'"),
    (P, "'Not a launch blocker. Lowest priority. Marcus can do this later in the week if time allows, or defer'"),
    (P, "'Done. Maya approved Friday 16:51. Close it'"),
    (P, "'Every downstream step is blocked by the one before it' and the plan respects it"),
    (P, "'Confirm with Julia: she picks up the Contoso date formatter today (2h)'"),
    (P, "'Schedule Elena's insurance handover with Daniel for Tuesday afternoon (30 min)... Don't treat it as a contingency - treat it as scheduled'"),
    (P, "'start pricing mockups this morning (1.5h). Packaging approval is sequential to the pricing page'"),
    (P, "the parallel table separates board non-revenue (startable) from board revenue (after migration), both Sarah's"),
    (P, "a time-boxed Monday opening with 'Message Elena: start the billing schema migration immediately. She is the gate for the entire SSO chain'"),
    (P, "a six-row parallel table with owners, durations and start conditions"),
    (P, "'Board pack (revenue) | After billing migration completes | Blocked, but Sarah knows this'"),
    (P, "'Low effort, high-profile account' - handled today by Julia without touching the chain"),
    (P, "'Circular / self-reinforcing dependency - Pricing -> Approval -> Pricing page: Daniel needs screenshots of the approved packaging. Mockups satisfy this'"),
    (P, "a four-row stale table with the actual status and an action for each"),
    (P, "chain pending, Security approved and closed, Atlas Thursday rollout named as why Wednesday matters"),
    (P, "'Mischaracterized. Export works; it's a date format preference. Julia diagnosed Friday'"),
    (R, "instrumentation is correctly placed after the SSO work, but the response never states that the core onboarding flow is itself launch-ready"),
    (P, "'Elena 09:15-12:15, Marcus to ~16:15, QA Tuesday morning to ~11:00, rollout by ~12:00' - 'Tuesday ~12:00-14:00'"),
    (P, "six unknowns raised, including the backfill scope and the unnamed packaging approver, none of them filled in"),
])

run("qwen3.6", "001", [
    (P, "the four steps with owners, durations and the constraint on each; 'Total Critical Time: 10 hours of focused work'"),
    (P, "'Resource Bottleneck: Marcus is needed for both the Patch (4h) and Rollout (1h)'; instructs him to stop the instrumentation immediately"),
    (P, "'Clarify that Onboarding Instrumentation is NOT a blocker (per Julia's Slack message)'"),
    (F, "Security is never mentioned. The stale 'unblock Security review' task is neither used nor rejected, and the approval never appears in the reconstruction"),
    (P, "each step carries its predecessor as a stated constraint and the plan follows them"),
    (P, "'Assign Julia to fix the date formatting... It is independent of the SSO critical path'"),
    (P, "'Daniel can do the migration, but lacks permissions. Elena must transfer them if she doesn't do it'; the handoff is made conditional on Elena's progress"),
    (R, "Sarah is told to produce the mockups, but the response then says the pricing page 'doesn't block the critical path' and can run in parallel, missing that the page waits on the approval the mockups unlock"),
    (P, "board non-revenue and revenue split correctly, both with Sarah"),
    (P, "'Priority 1: Secure the Critical Path (Billing Migration)' followed by unblocking Marcus"),
    (P, "Julia, Sarah's four streams and QA's idle state all laid out against the chain"),
    (P, "'She must wait for Billing Migration to finish before doing board_pack_revenue (2h)'"),
    (P, "Contoso sits at priority three with 'Can be done anytime Mon-Wed' while the migration holds priority one"),
    (F, "the section headed 'Circular/Stale Dependency' is about the onboarding instrumentation, not pricing. The approval/page/screenshots loop is never identified, and the mockups are never connected to breaking it"),
    (R, "the instrumentation task is overridden explicitly, but the stale Security and 'broken Contoso export' entries are not"),
    (R, "the chain and the Wednesday commitment are right; the Security approval is absent"),
    (R, "'fix the date formatting' and the Tuesday deadline are right, but the response never states that the export itself succeeds"),
    (R, "instrumentation is correctly not required for launch; the core flow's launch-readiness is not stated"),
    (P, "'Mon 09:00-12:00 migration, 12:00-16:00 patch, Tue 09:00-11:00 QA, Tue 11:00-12:00 rollout' - 'Earliest Realistic Delivery: Tuesday Noon'"),
    (P, "no invented approvals or blockers; the QA and Contoso risks are framed as conditionals"),
])

run("gemma4", "001", [
    (P, "'Elena (Billing Migration: 3h) -> Marcus (Compatibility Patch: 4h) -> QA (Regression: 2h) -> Marcus (Production Rollout: 1h)'"),
    (P, "'Instruct Marcus to stop working on \"Onboarding Instrumentation.\" It is not a launch blocker and is currently wasting 3 hours of his capacity needed for the SSO critical path'"),
    (P, "'The core flow is already launch-ready and can proceed/launch without Marcus's instrumentation'"),
    (F, "Security is never mentioned anywhere. The stale 'unblock Security review' task is left standing and the Friday approval never enters the reconstruction"),
    (P, "the chain is stated correctly and the plan does not violate it"),
    (P, "'Assign the Contoso export formatter (2h) to Julia immediately to ensure it is done for the Tuesday demo'"),
    (P, "'If the migration slips, Daniel must be trained (30 mins) before her departure'"),
    (P, "'Direct Sarah to create mock screenshots of the pricing page for packaging approval'"),
    (P, "'Sarah can complete all non-revenue sections (narrative, customer sections, etc.) without waiting for the billing migration'"),
    (R, "the single most time-critical action is fourth on the list and framed as 'Monitor SSO: Ensure Elena starts the billing migration today'; the three unblocking messages come first"),
    (P, "Contoso, pricing, board non-revenue and the onboarding launch are all placed off the critical path"),
    (R, "non-revenue work is correctly released, but the response never states that the revenue section must wait for the migration and backfill"),
    (P, "the CEO's URGENT becomes a delegated two-hour task and the SSO chain keeps its place"),
    (P, "'Approval required screenshots -> Screenshots require a page -> Page requires approval. Resolution: Use design mockups for approval'"),
    (R, "the instrumentation task is overridden, but the stale Security entry and the 'broken Contoso exports' framing are not"),
    (R, "the chain and the Wednesday commitment are right; the Security approval is missing"),
    (R, "the formatter and the Tuesday demo are named, but the response never establishes that the export works and only the date format differs"),
    (P, "'The core flow is already launch-ready and can proceed/launch without Marcus's instrumentation'"),
    (F, "'Enterprise SSO: Wednesday EOD' is given as the earliest delivery, with the reasoning 'the path is easily cleared before Wednesday EOD'. Tuesday is available and is never considered"),
    (P, "no invented approvals or blockers"),
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
