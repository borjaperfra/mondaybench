"""Recorded verdicts for the monday-002 calibration sweep, rubric 0.1-draft.

Separate from `verdicts/_generate.py`, which belongs to monday-001 and writes
`verdicts/<model>.verdicts.jsonl`. These land in `verdicts/monday-002/` so the
two scenarios can never overwrite each other's labels — the run ids differ, but
the filenames would not.

Labels assigned by reading each response against the rubric definitions and the
scenario's `ground_truth.md`, following `evaluators/monday-002/judge-prompt.md`:
judge only what the candidate states or clearly implies, no credit for absent
information, and where a response sits between two labels choose the lower.

monday-002's rubric has no noise dimension, so no noise entry is written; the
evaluator never asks for one.

Nothing here assigns points. `mondaybench evaluate --verdicts` does the scoring.
"""

from __future__ import annotations

import json
from pathlib import Path

P, R, F = "PASS", "PARTIAL", "FAIL"

# Criterion order follows rubric.yaml, so a diff of this file reads in the same
# order as the rubric it scores against.
CRITERIA = [
    "launch_current_blocker",
    "ceo_approval_superseded",
    "zenith_resolved",
    "comms_owner_daniel",
    "pricing_current_state",
    "launch_time_unconfirmed",
    "stale_ceo_task_rejected",
    "stale_zenith_task_rejected",
    "stale_pricing_artifact_rejected",
    "ownership_chain_resolved",
    "launch_unblock_action",
    "expansion_analysis_action",
    "orion_verify_action",
    "no_prohibited_user_actions",
    "dependency_chain",
    "earliest_unblocker",
    "no_premature_downstream",
    "orion_genuine_uncertainty",
    "no_launch_time_guess",
    "no_root_cause_guess",
    "expansion_gap_reconciled",
]

# model -> run number -> {criterion: (label, evidence)} plus `_pen`.
VERDICTS = {
    "glm5.3-flash": {
        "001": dict(
            launch_current_blocker=(P, "'Marcus deploys 2.9.5-patch to production <- the only current hard blocker'; CEO approval and staging sign-off both named as superseded"),
            ceo_approval_superseded=(P, "'Maya's separate CEO approval is no longer required (she rescinded it Thursday evening; confirmed by email)'"),
            zenith_resolved=(P, "'Zenith: resolved. Renewal signed Friday - 24 months, EUR96k ARR. Export fix validated by the customer. Laura owns follow-up'; the Monday call is voided as stale"),
            comms_owner_daniel=(P, "'Customer announcement: reassigned to Daniel... No Product involvement'; 'Do NOT do today: ... send the customer announcement'"),
            pricing_current_state=(P, "'Thursday spreadsheets and the pinned file are stale. Current internal-only numbers (Daniel, Fri 09:13)... No external pricing until a public announcement, which has no date'"),
            launch_time_unconfirmed=(P, "'not launched, no confirmed time'; 'Sam has retired Monday 15:00 as an external commitment'"),
            stale_ceo_task_rejected=(P, "'Clean the task tracker: void stale tasks (Maya approval, ...)'"),
            stale_zenith_task_rejected=(P, "the same cleanup voids the 'Zenith call' task"),
            stale_pricing_artifact_rejected=(P, "prefers Daniel's 09:13 numbers over the pinned final-named file and refuses the Initech send"),
            ownership_chain_resolved=(R, "'reassigned to Daniel' and 'Sarah is out Monday' imply the handover, but the You -> Sarah -> Daniel chain is never traced"),
            launch_unblock_action=(R, "ownership is exactly right ('You do not deploy, verify, or open rollout yourself') and the chain is complete, but the launch is action #2 - the expansion analysis is placed above it"),
            expansion_analysis_action=(P, "#1: 'Send Maya the first-cut expansion analysis: gap fully attributed (Wayne 18k, Globex 12k, Soylent 10k, Wonka 14k)'"),
            orion_verify_action=(P, "#3: 'Verify Orion's org ID and live SCIM flag state with Sam/Laura before any update goes to the customer'"),
            no_prohibited_user_actions=(P, "'Do NOT do today: send pricing to Initech, confirm any launch time externally, or send the customer announcement'; stale tasks are voided, not executed"),
            dependency_chain=(P, "'Marcus deploys 2.9.5-patch -> Priya post-deploy verification -> Sam opens rollout -> Daniel sends announcement'"),
            earliest_unblocker=(P, "the deploy is marked '<- the only current hard blocker'"),
            no_premature_downstream=(P, "'Nothing downstream moves until (1) succeeds'"),
            orion_genuine_uncertainty=(R, "'still unresolved... Not yet verified' names both conflicting sources and refuses to lean, but never says the supplied evidence cannot settle it"),
            no_launch_time_guess=(P, "'no confirmed time'; 'Verify nothing was promised before anyone communicates a new time' - no replacement time invented"),
            no_root_cause_guess=(P, "reports the shard the deploy failed on, straight from deployments.csv, and invents no cause for it or for Orion"),
            expansion_gap_reconciled=(P, "'EUR54k gap: Wayne -18k and Globex -12k plus Soylent -10k and Wonka -14k = EUR54k. The previously unexplained EUR24k is Soylent + Wonka'; causes explicitly left open"),
            _pen=[],
        ),
    },
    "qwen3.8-flash": {
        "001": dict(
            launch_current_blocker=(P, "'Current blocker: production deployment/verification of the patched SSO migration is not complete'; CEO approval and staging sign-off listed under 'Superseded blockers'"),
            ceo_approval_superseded=(P, "'Maya's separate CEO approval is no longer required; this changed Thursday 17:51'"),
            zenith_resolved=(P, "'Resolved. Audit-log export fix was validated. Renewal signed: 24 months, EUR96k ARR. Laura owns post-renewal follow-up; Monday escalation call is not needed'"),
            comms_owner_daniel=(P, "'Customer announcement: Daniel owns the send; Product has no send action'"),
            pricing_current_state=(P, "'Thursday/pinned spreadsheets are stale', current internal numbers listed, 'No external pricing may be sent until a public pricing announcement. No public announcement date is set'"),
            launch_time_unconfirmed=(P, "'There is no confirmed Monday 15:00 external launch time'; 'Do not confirm Monday 15:00 externally'"),
            stale_ceo_task_rejected=(P, "'Close stale launch tasks: Get Maya's separate approval'"),
            stale_zenith_task_rejected=(P, "'Close stale launch tasks: ... Call Zenith'"),
            stale_pricing_artifact_rejected=(P, "stale pinned file named, Daniel's 09:13 numbers used instead, and the Initech send refused"),
            ownership_chain_resolved=(P, "names all three links: 'Product-owned announcement' among the superseded tasks, 'Sarah's Monday absence: Daniel has taken the announcement ownership'"),
            launch_unblock_action=(P, "action #1, 'verify/coordinate, not personally own', walking Marcus -> Priya -> Sam -> Daniel with ownership held correctly at each step"),
            expansion_analysis_action=(P, "#3: 'Produce a first-cut explanation for Maya by Monday afternoon' with Wayne/Globex confirmed and Soylent/Wonka as the candidate remainder"),
            orion_verify_action=(P, "#2: 'Verify Orion's org ID and current SCIM feature flag state'; holds customer communication until resolved"),
            no_prohibited_user_actions=(P, "no prohibited action recommended; pricing send, 15:00 confirmation, Zenith call and Maya approval are all explicitly closed or refused"),
            dependency_chain=(P, "'Marcus deploys the patch -> production deployment succeeds -> Priya runs post-deploy Security verification -> Sam opens rollout -> Daniel sends customer announcement'"),
            earliest_unblocker=(R, "puts 'Confirm Priya accepts the 2.9.5-patch path or requires review' as step 1, ahead of the redeploy, so the earliest actionable step it names is not the deploy"),
            no_premature_downstream=(P, "'If production deployment succeeds, notify Priya'; 'After Priya confirms verification, confirm Sam can open rollout'; announcement gated on Sam"),
            orion_genuine_uncertainty=(R, "'Unverified', both sources quoted, no lean either way - but never states that the supplied evidence is insufficient to settle it"),
            no_launch_time_guess=(P, "'no confirmed Monday 15:00 external launch time'; 'Do not promise Monday 15:00 externally'; no replacement time offered"),
            no_root_cause_guess=(P, "'Determine whether dashboard lag or wrong org explains the conflict' repeats Laura's own two hypotheses as things to test, and asserts neither"),
            expansion_gap_reconciled=(P, "'Confirmed delays: Wayne EUR18k + Globex EUR12k = EUR30k. Account data shows Soylent down EUR10k and Wonka down EUR14k, which would explain the remaining EUR24k' - full arithmetic, causes withheld"),
            _pen=[],
        ),
    },
    "deepseek-v4-flash": {
        "001": dict(
            launch_current_blocker=(P, "'Current blocker: production deployment has not completed successfully; patch is ready but not deployed'"),
            ceo_approval_superseded=(P, "'Maya's separate CEO approval is no longer a required gate. Security sign-off is sufficient'"),
            zenith_resolved=(P, "'Resolved. Audit-log export was fixed and validated by the customer. Renewal signed: 24 months, EUR96k ARR. The Monday call is cancelled'"),
            comms_owner_daniel=(P, "'Customer announcement send is owned by Daniel, not Product'; 'Do not send the customer announcement'"),
            pricing_current_state=(P, "'All spreadsheets, including enterprise-pricing-v4-final.xlsx and the pinned file, are stale'; current numbers given; 'No external pricing can be shared until the public pricing announcement'"),
            launch_time_unconfirmed=(P, "'Sam no longer promises Monday 15:00 externally... there is no confirmed launch time'"),
            stale_ceo_task_rejected=(P, "'Do not ask Maya for approval'; listed under no-action as no longer required"),
            stale_zenith_task_rejected=(P, "'The Monday call is cancelled'"),
            stale_pricing_artifact_rejected=(P, "names the final-titled and pinned files as stale, uses Daniel's numbers, refuses the external send"),
            ownership_chain_resolved=(R, "'owned by Daniel, not Product' gets the final owner, but Sarah never appears and the handover chain is not resolved"),
            launch_unblock_action=(P, "action #1 'Coordinate/unblock', walking Marcus -> Priya -> Sam with the user coordinating rather than executing"),
            expansion_analysis_action=(P, "#2: 'Send a first cut to Maya and Daniel by Monday afternoon. Use the account data: EUR30k + EUR24k = EUR54k gap fully explained'"),
            orion_verify_action=(P, "#3: 'confirm the correct Orion org ID and check the live feature flag before any further Orion communication'"),
            no_prohibited_user_actions=(P, "'Do not ask Maya for approval. Do not send the customer announcement. Do not confirm any external launch time'; pricing send refused"),
            dependency_chain=(P, "'1. Marcus deploys 2.9.5-patch successfully. 2. Priya completes post-deploy Security verification. 3. Sam opens rollout. 4. Daniel sends the customer announcement'"),
            earliest_unblocker=(P, "'Current blocker: production deployment has not completed successfully', and the deploy is step 1"),
            no_premature_downstream=(P, "'No external launch time should be promised before step 3. No customer announcement before step 4'"),
            orion_genuine_uncertainty=(R, "'Conflicting evidence remains... before trusting either report' refuses both readings, but stops short of saying the supplied sources cannot settle it"),
            no_launch_time_guess=(P, "'there is no confirmed launch time'; 'do not treat 15:00 as a commitment'; no replacement time invented"),
            no_root_cause_guess=(P, "'Laura may have tested a different org' is hedged, filed under MUST VERIFY, and traces to Laura's own Slack message rather than being invented"),
            expansion_gap_reconciled=(P, "'Remaining EUR24k is explained by reduced expected expansion at Soylent (from EUR28k to EUR18k) and Wonka (from EUR24k to EUR10k)' - the only run to quote the from/to figures; no cause invented"),
            _pen=[],
        ),
    },
    "qwen3.6": {
        "001": dict(
            launch_current_blocker=(P, "'The current blockers are: (1) Successful production deployment of the patch, and (2) Post-deploy Security verification by Priya'; CEO approval named as no longer required"),
            ceo_approval_superseded=(P, "'CEO approval is no longer required (Security sign-off is sufficient)'"),
            zenith_resolved=(P, "'Resolved. Laura confirmed the audit-log export fix was validated and the 24-month, EUR96k renewal is signed. No call needed'"),
            comms_owner_daniel=(P, "'Daniel (Finance) owns the customer announcement send on Monday once Sam confirms rollout is open. You do not need to send it'"),
            pricing_current_state=(P, "'The previous spreadsheet (enterprise-pricing-v4-final.xlsx) is stale. Current internal working numbers are... Do not share externally. No public announcement date exists'"),
            launch_time_unconfirmed=(P, "'The launch is not scheduled for Monday 15:00'; 'Do not confirm Monday 15:00 launch externally'"),
            stale_ceo_task_rejected=(P, "'Do NOT seek Maya's explicit launch approval (Security sign-off is sufficient)'"),
            stale_zenith_task_rejected=(P, "'Do NOT call Zenith (Renewal signed)'"),
            stale_pricing_artifact_rejected=(P, "names the stale final-titled file, uses Daniel's numbers, and blocks any external use"),
            ownership_chain_resolved=(R, "gets Daniel as the owner and flags the announcement as reassigned, but Sarah is never mentioned anywhere in the briefing"),
            launch_unblock_action=(P, "#1 'Coordinate Enterprise Launch Deployment': contact Marcus, then coordinate Priya's verification, then inform Sam - coordinating rather than executing"),
            expansion_analysis_action=(P, "#2: 'Analyze the EUR24k unexplained gap. Use the Accounts data to verify if the reductions at Soylent (-EUR10k) and Wonka (-EUR14k) account for the remainder'"),
            orion_verify_action=(P, "#3: 'verify the specific Orion Org ID and the current state of the SCIM feature flag... rather than relying on dashboard snapshots or customer reports'"),
            no_prohibited_user_actions=(P, "a dedicated 'Do NOT Do' block covering the Zenith call, Maya approval, the announcement send and the 15:00 confirmation"),
            dependency_chain=(P, "'1. Marcus deploys patch. 2. Priya performs post-deploy security verification. 3. Sam verifies rollout readiness. 4. Daniel sends customer announcement'"),
            earliest_unblocker=(P, "'Primary Blocker: Production Deployment Failure. The SSO migration patch is ready but not deployed', and the deploy is step 1"),
            no_premature_downstream=(P, "'Once deployed, coordinate with Priya'; the chain is respected and nothing downstream is advised early"),
            orion_genuine_uncertainty=(R, "'Status is ambiguous' with both sources quoted and no lean, but never says the supplied evidence cannot resolve it"),
            no_launch_time_guess=(P, "'The launch is not scheduled for Monday 15:00'; speculates only that the target is 'likely missed' and invents no replacement time"),
            no_root_cause_guess=(P, "no cause offered for the deploy failure or the Orion discrepancy; the Soylent/Wonka question is posed rather than answered"),
            expansion_gap_reconciled=(R, "has every number - EUR180k/EUR126k/EUR54k, EUR30k from Wayne+Globex, Soylent -EUR10k and Wonka -EUR14k - but still labels EUR24k the 'Unexplained Gap' and asks to 'verify if' those two account for it, so the reconciliation is never closed"),
            _pen=[],
        ),
    },
}


def main() -> None:
    out = Path(__file__).parent
    if not VERDICTS:
        print("  no verdicts recorded yet - nothing written")
        return
    for model, runs in VERDICTS.items():
        lines: list[str] = []
        for run_number, verdicts in sorted(runs.items()):
            run_id = f"monday-002__{model}__{run_number}"
            missing = [c for c in CRITERIA if c not in verdicts]
            if missing:
                raise SystemExit(f"{run_id}: no label for {', '.join(missing)}")
            for criterion_id in CRITERIA:
                label, reason = verdicts[criterion_id]
                lines.append(
                    json.dumps(
                        {
                            "run_id": run_id,
                            "criterion_id": criterion_id,
                            "result": label,
                            "evidence": reason,
                            "reason": reason,
                        },
                        ensure_ascii=False,
                    )
                )
            lines.append(
                json.dumps(
                    {"run_id": run_id, "kind": "penalties", "violations": verdicts["_pen"]},
                    ensure_ascii=False,
                )
            )
        (out / f"{model}.verdicts.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"  verdicts/monday-002/{model}.verdicts.jsonl  ({len(lines)} entries)")


if __name__ == "__main__":
    main()
