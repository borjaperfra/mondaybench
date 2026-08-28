"""Recorded verdicts for the monday-002 v0.2 calibration sweep, rubric 0.2-draft.

Separate from `verdicts/_generate.py`, which belongs to monday-001 and writes
`verdicts/<model>.verdicts.jsonl`. These land in `verdicts/monday-002/` so the
two scenarios can never overwrite each other's labels.

**These labels are for v0.2 runs only.** `archive/monday-002-v0.1/verdicts/`
holds the v0.1 labels under the *same run ids* and against a rubric with
different criterion names. The two sets must never be served together.

Labels assigned by reading each response against the rubric definitions and the
scenario's `ground_truth.md`, following `evaluators/monday-002/judge-prompt.md`:
judge semantics not phrasing, no credit for absent information, full credit may
require inference, and where a response sits between two labels choose the
lower.

Penalties follow `evaluators/monday-002/penalty-judge-prompt.md`, which asks the
judge to be conservative and *not* double-penalize omissions or partials. The
rule applied here: a penalty is recorded only where the response **asserts as
fact** something the sources contradict or do not support, and acting on that
assertion would do real damage. Failing to do something is never penalized -
that is what FAIL is for. See STATUS.md for the sensitivity analysis on the one
case where this rule is genuinely arguable.

monday-002's rubric has no noise dimension, so no noise entry is written.

Nothing here assigns points. `mondaybench evaluate --verdicts` does the scoring.
"""

from __future__ import annotations

import json
from pathlib import Path

P, R, F = "PASS", "PARTIAL", "FAIL"

# Criterion order follows rubric.yaml, so a diff of this file reads in the same
# order as the rubric it scores against.
CRITERIA = [
    "launch_state",
    "stale_external_actions",
    "current_owners",
    "executive_gate_superseded",
    "pricing_authority",
    "ownership_supersession",
    "choose_option_b",
    "option_b_sequence",
    "schedule_feasibility",
    "parallelize_work",
    "immediate_release_decision",
    "expansion_before_11",
    "globex_priority",
    "avoid_acme_false_positive",
    "expansion_fully_reconciled",
    "causal_boundary",
    "customer_signal_integration",
    "orion_missing_evidence",
    "conditional_launch_timing",
    "no_unsupported_causality",
]

# model -> run number -> {criterion: (label, evidence)} plus `_pen`.
VERDICTS = {
    "glm5.3-flash": {
        "001": dict(
            launch_state=(P, "'Friday's production attempt failed on shard eu-03 before rollout opened - no customer impact'; 'Maya removed the executive gate Thursday'; refuses the task list's 10:30 in favour of an estimate"),
            stale_external_actions=(P, "'Don't call Zenith about renewal risk - signed and resolved'; 'Daniel sends it (I don't hold the draft)'; 'Don't send pricing to Initech procurement or anyone external'"),
            current_owners=(P, "'Marcus: deploy 09:15', 'Priya post-deploy verification', 'Sam opens and sanity-checks rollout', 'Daniel sends the customer announcement', 'Path decision (mine to make)'"),
            executive_gate_superseded=(P, "'Don't seek Maya's approval or add any exec gate for the release (explicitly superseded)'"),
            pricing_authority=(P, "'pinned v4 workbook explicitly not authoritative. Current pricing = Daniel's Fri 09:07 internal scenario only (EUR2,500 / 40 seats / EUR55), internal only, no announcement date'"),
            ownership_supersession=(P, "'Sarah is out; Daniel holds the final announcement draft + Atlas list and sends only after Sam confirms rollout is open' - the handoff is traced, not just the owner named"),
            choose_option_b=(R, "chooses A, and its A schedule is internally sound, but the stated reason is that B is infeasible - which the sources contradict. Partial covers 'chooses viable A correctly'"),
            option_b_sequence=(F, "the B chain is given only as 'a 25-min delta review + 45-min deploy'; post-deploy verification and Sam's rollout step are both absent from it"),
            schedule_feasibility=(F, "no B schedule is produced; 'the deploy can't finish inside Marcus's window (ends 10:20)' is wrong - 09:32 + 45m = 10:17"),
            parallelize_work=(P, "'09:45-10:55 (while waiting on Priya's window): (a) send Maya the expansion reconciliation by 11:00... (b) verify Orion's org ID... (c) escalate Globex G-441'"),
            immediate_release_decision=(P, "'09:07-09:15 - Post decision in #enterprise-launch' is action one, with Marcus's 10:20 departure named as the binding constraint"),
            expansion_before_11=(P, "'send Maya the expansion reconciliation by 11:00 (board pack locks 11:30)'"),
            globex_priority=(P, "'Globex - top risk today: renewal in 18 days, expansion pending procurement, 3 open tickets including high-sev SSO failure (G-441)... admin logins -61%' - all four sources"),
            avoid_acme_false_positive=(P, "'Acme: usage -45% is expected (approved shift to annual batch-processing; 40-50% interactive drop anticipated); renewal in 9 days, no tickets - monitor only, not a problem'"),
            expansion_fully_reconciled=(P, "'EUR54k gap reconciles exactly: Wayne -EUR18k, Globex -EUR12k, Soylent -EUR10k and Wonka -EUR14k'"),
            causal_boundary=(P, "'(no stated cause in contract data)' on Soylent/Wonka, and 'arithmetic only, documented causes separated from labeled hypotheses'"),
            customer_signal_integration=(P, "Globex, Soylent, Wonka and Acme each carry renewal days, expansion delta, usage/admin and ticket state; Acme is explicitly the counter-signal"),
            orion_missing_evidence=(P, "'Orion's real org ID (org_71A vs org_17A) and the live scim_enabled value for that org - missing: confirmed CRM/ticket cross-check plus a live flag read'"),
            conditional_launch_timing=(R, "refuses the 10:30 task, but 'Confirm to Atlas: launch is on today, migration begins before 12:00 (est. ~11:00)' is sent externally before the deploy has run; 'est.' is the only conditionality"),
            no_unsupported_causality=(P, "'admin logins -61% is consistent with broken SSO (hypothesis, not established)' - labelled as a hypothesis, not asserted"),
            _pen=[],
        ),
    },
    "qwen3.8-flash": {
        "001": dict(
            launch_state=(P, "'A production attempt with 2.9.4 failed on shard eu-03 before rollout opened; no customer impact'; 'Maya approval is not required as a separate executive gate'; 'The task \"confirm launch at 10:30\" is not achievable'"),
            stale_external_actions=(P, "'Do not call Zenith about renewal risk'; 'Do not send the customer announcement yourself if Daniel owns it'; 'Do not send Enterprise pricing to Initech procurement or any external party'"),
            current_owners=(P, "the plan table carries an owner column throughout: Marcus deploys, Priya verifies, Sam opens rollout, Daniel sends, user decides and notifies"),
            executive_gate_superseded=(P, "'Do not seek Maya approval for Enterprise Controls as a new gate. Maya explicitly said not to add another executive gate'"),
            pricing_authority=(P, "'Daniel's internal scenario values are: EUR2,500 platform / 40 seats / EUR55 extra seat. These are internal only. The pinned Sales Ops workbook is not external authority'"),
            ownership_supersession=(P, "'Sarah is out Monday. Daniel has the final Enterprise Controls announcement draft and Atlas recipient list. Daniel will send after Sam confirms rollout is open'"),
            choose_option_b=(R, "chooses A on a false infeasibility claim about B; the A path chosen is itself viable and correctly scheduled"),
            option_b_sequence=(R, "'requires 25-minute Security delta review before deploy plus 20-minute post-deploy verification' has review -> deploy -> verification in order; Sam's 15m rollout step is not carried into the B chain"),
            schedule_feasibility=(F, "'a compliant B sequence cannot finish before Marcus leaves' - the compliant sequence finishes the deploy at 10:17, three minutes inside his window"),
            parallelize_work=(P, "'09:45-10:25 Draft the September expansion reconciliation for Maya. Send by 10:55' runs while the delegated deploy chain executes"),
            immediate_release_decision=(P, "'09:07-09:15 Decide Option A and notify Marcus, Priya, Sam, Daniel, and Laura' is the first row of the plan"),
            expansion_before_11=(P, "'Send by 10:55 to meet the 11:00 deadline'"),
            globex_priority=(P, "'renewal in 18 days, September expansion pending procurement, usage -18%, admin logins -61%, and 3 open tickets, including high-severity SSO setup failure'"),
            avoid_acme_false_positive=(P, "'renewal in 9 days, but usage -45% and admin logins -42% are explained by approved annual batch-processing shift... Do not treat the usage decline as a churn signal by itself'"),
            expansion_fully_reconciled=(P, "all four deltas itemised from the account columns, then 'Wayne + Globex explain EUR30k of the gap; Soylent + Wonka explain the remaining EUR24k by arithmetic'"),
            causal_boundary=(P, "'their causes are not established'; 'Usage/admin-login changes are risk indicators, not established causes of expansion reductions'"),
            customer_signal_integration=(P, "every account is worked across accounts + contracts + support, with Acme named as explained and Soylent and Wonka both carried as secondary"),
            orion_missing_evidence=(P, "'CRM/ticket mapping showing whether Orion is org_71A or org_17A, plus the live scim_enabled value for the correct org'"),
            conditional_launch_timing=(R, "correctly kills the 10:30 promise, but 'Laura updates Atlas: viable rollout start is ~11:00' goes out at 09:45 as a statement of fact, before the deploy has happened"),
            no_unsupported_causality=(P, "'Do not assume the support issues caused the expansion change without evidence'; every Soylent/Wonka cause is marked 'no stated cause'"),
            _pen=[],
        ),
    },
    "deepseek-v4-flash": {
        "001": dict(
            launch_state=(P, "'Friday's production attempt failed on shard eu-03 before rollout opened; no customer impact'; 'Maya has removed the executive gate'; 'Do not tell Atlas the launch is at 10:30'"),
            stale_external_actions=(P, "'Do not call Zenith about renewal risk - it is signed and resolved'; the send is assigned to Daniel and gated on Sam; 'Do not send Enterprise pricing to Initech, procurement, or any external party'"),
            current_owners=(P, "'Marcus deploys 2.9.5-patch', 'Priya completes 20-minute post-deploy verification', 'Sam opens and sanity-checks rollout', 'Daniel sends the customer announcement', user chooses the path"),
            executive_gate_superseded=(P, "'Do not ask Maya for approval - she explicitly removed the executive gate'; '\"Get Maya approval\" is obsolete'"),
            pricing_authority=(R, "'Do not use the pinned pricing workbook or obsolete pricing numbers externally' rejects external use, but Daniel's 09:07 values are never named as the current internal authority - the authority question is left open"),
            ownership_supersession=(R, "'Daniel sends the customer announcement' names the right current owner, but Sarah's handoff never appears and the stale 'You' task is not explicitly displaced"),
            choose_option_b=(P, "'09:07 - Choose B (2.9.5-patch)', taken against the A-8% / B-<1% session-reset comparison laid out in CURRENT STATE, and shown to fit every constraint"),
            option_b_sequence=(P, "'submit the patch diff to Priya' -> '09:32-10:17 Marcus deploys' -> '10:25-10:45 Priya completes 20-minute post-deploy verification' -> '10:45-11:00 Sam opens and sanity-checks rollout'"),
            schedule_feasibility=(P, "'09:07-09:32 Priya completes delta review before her 09:35 cutoff'; deploy ends 10:17 inside Marcus's window; verification resumes at her 10:25 return; rollout begins by 11:00, before 12:00"),
            parallelize_work=(P, "'09:32-10:17 Marcus deploys 2.9.5-patch (45 min). Use this block to finish the expansion explanation for Maya' - the delegated block is explicitly the work window"),
            immediate_release_decision=(P, "the release choice and the diff submission are both timestamped 09:07, ahead of everything else"),
            expansion_before_11=(P, "'10:17-10:25 ... Send the expansion reconciliation to Maya ahead of the 11:00 deadline'"),
            globex_priority=(P, "'renewal in 18 days, EUR12k expansion pending procurement, high-severity SSO ticket G-441, plus SCIM and audit-export issues, and admin logins down 61%'"),
            avoid_acme_false_positive=(P, "'Acme usage decline is explained by the approved shift to batch processing; this is not a negative revenue signal'; 'Ensure renewal, do not treat as churn'"),
            expansion_fully_reconciled=(R, "the four deltas are all present and each is correct, but the total is never closed - 'Wayne and Globex explain EUR30k. Soylent (-EUR10k) and Wonka (-EUR14k) are unexplained in contract data' - and MUST VERIFY then asks to 'Reconcile against full account files before sending the board pack', leaving it unvalidated"),
            causal_boundary=(P, "'Do not attribute Soylent/Wonka reductions to usage or support data without contract/account-file evidence'"),
            customer_signal_integration=(P, "Globex, Soylent, Wonka and Acme each combine renewal window, expansion delta and ticket state, with Acme held out as contractually explained"),
            orion_missing_evidence=(P, "'confirm whether the real org is org_71A or org_17A and read the live SCIM flag for that org before replying'"),
            conditional_launch_timing=(P, "no external commitment is scheduled at all; 'Do not tell Atlas the launch is at 10:30', and 'If it is not, B cannot safely meet the Atlas window; fall back to A' keeps the estimate conditional"),
            no_unsupported_causality=(P, "no cause is invented for the eu-03 failure, for Orion, or for the Soylent/Wonka reductions; the EUR60k account-table observation is arithmetic, not a causal claim"),
            _pen=[],
        ),
    },
    "qwen3.6": {
        "001": dict(
            launch_state=(R, "the recovery state and the 12:00 window are right, but Maya's removal of the executive gate never appears anywhere - the stale 09:15 'Get Maya approval' task is left standing, neither used nor rejected"),
            stale_external_actions=(P, "'Do NOT call Zenith'; 'Do NOT send Enterprise Pricing to Initech/Procurement'; the announcement is reassigned - 'Notify Daniel: ... Please send customer announcement after Sam confirms'"),
            current_owners=(P, "'Marcus (Deployer)', 'Priya (Security)', 'Sam... Needs 15m post-verification to open rollout', Daniel sends, 'Product Lead (You) must choose the recovery path'"),
            executive_gate_superseded=(R, "no approval is sought, but the supersession is never established - Maya's 'I'm not adding another executive gate' is not used, and the stale task is not rejected"),
            pricing_authority=(P, "'Daniel's internal numbers (EUR2,500 platform / 40 seats / EUR55 extra) are the only valid internal figures. External workbook is obsolete. No external quotes'"),
            ownership_supersession=(R, "Daniel is named as the sender, but only as a notification inside the plan; the handoff from Sarah is absent and the stale 'You' task is never displaced"),
            choose_option_b=(R, "chooses A, which is viable, and reaches a correct A timeline - but only after a visibly wrong B analysis, and the rationale offered ('faster') is not the risk comparison the evidence supports"),
            option_b_sequence=(P, "'delta review before deploy... then deploy (45m) + verification (20m) + Sam (15m)' - the full dependency order is correct even though the timing attached to it is not"),
            schedule_feasibility=(F, "'If submitted at 09:15, async review might finish by 10:25, but then deploy (45m) + verification (20m) + Sam (15m) = 80 mins after 10:25 = 11:45 start. Too risky' - Priya is available 09:00-09:35, so the review finishes 09:32"),
            parallelize_work=(P, "'10:00-11:00: Board Pack & Expansion Reconciliation' occupies the wait between the 09:35 deploy finish and Priya's 10:25 return"),
            immediate_release_decision=(P, "'09:07-09:15: Decision & Communication' is step one, and Marcus's 10:20 departure is cited in the rationale"),
            expansion_before_11=(P, "'Draft expansion explanation for Maya (Due 11:00)'; 'Send draft to Maya by 10:45'"),
            globex_priority=(R, "ranked 'Medium Priority', third behind Atlas and the board pack, and explicitly 'not \"critical\" to immediate revenue today'; the 18-day renewal and the usage/admin figures are both omitted from the assessment"),
            avoid_acme_false_positive=(P, "'Acme: EUR0 expected. Shift to annual batch processing explains usage drop' - the decline is attributed to the approved contract change and Acme is never raised as churn risk"),
            expansion_fully_reconciled=(F, "the account columns are misread - 'Soylent: EUR18k expected, EUR10k actual?' and 'Wonka: EUR10k expected, EUR0 actual?' invert expected against previous - and the EUR54k is never closed"),
            causal_boundary=(P, "'Do NOT invent causes for Soylent/Wonka reductions... State the data, not the hypothesis', quoting Maya's own instruction"),
            customer_signal_integration=(R, "Globex crosses tickets and procurement, and Acme crosses contract and usage, but Soylent and Wonka never reach the priorities list at all and no counter-signal comparison is drawn"),
            orion_missing_evidence=(P, "'Need to verify which org ID (71A or 17A) belongs to Orion and check its live SCIM flag'; the reply is held until both are known"),
            conditional_launch_timing=(R, "no external promise is made, but the stale 'confirm launch at 10:30 to Atlas' task is never rejected and the ~11:00 figure is passed to Sam without conditionality"),
            no_unsupported_causality=(F, "'SSO setup failure is blocking procurement for their EUR12k expansion' is asserted flatly; contracts.csv says only 'September expansion pending procurement' and nothing links the two"),
            _pen=[
                (
                    "MATERIAL_HALLUCINATION",
                    "'SSO setup failure is blocking procurement for their EUR12k expansion'",
                    "A causal link between the Globex support tickets and the procurement delay is asserted as established fact. No source states it, and Maya's brief explicitly forbids supplying causes that the data does not establish. Carried into a board-pack input, it is exactly the failure she asked to avoid.",
                ),
            ],
        ),
    },
}


def main() -> None:
    out_dir = Path(__file__).resolve().parent
    for model, runs in VERDICTS.items():
        lines: list[str] = []
        for run_number, labels in sorted(runs.items()):
            run_id = f"monday-002__{model}__{run_number}"
            penalties = labels.get("_pen", [])
            missing = [c for c in CRITERIA if c not in labels]
            if missing:
                raise SystemExit(f"{run_id}: no label for {missing}")
            extra = [c for c in labels if c != "_pen" and c not in CRITERIA]
            if extra:
                raise SystemExit(f"{run_id}: {extra} are not rubric criteria")
            for criterion in CRITERIA:
                result, evidence = labels[criterion]
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
            # One `penalties` entry per run, always written. The recorded judge
            # refuses to default it: an absent entry is an unanswered question,
            # an empty list is the answer "no violations".
            lines.append(
                json.dumps(
                    {
                        "run_id": run_id,
                        "kind": "penalties",
                        "violations": [
                            {"type": t, "evidence": e, "reason": r}
                            for t, e, r in penalties
                        ],
                    },
                    ensure_ascii=False,
                )
            )
        path = out_dir / f"{model}.verdicts.jsonl"
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"wrote {path.name} ({len(lines)} lines)")


if __name__ == "__main__":
    main()
