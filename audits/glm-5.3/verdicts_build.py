"""Recorded verdicts for the GLM 5.3 challenger battery, suite v1.0.

Labels assigned by reading each response against the frozen rubric for its
scenario. Where a response sat between two labels the rubric's own tie-break
applies: choose the lower label.

Written as a script so the labels are reviewable as one diffable object, and so
`mondaybench evaluate --verdicts` does the scoring. Nothing here assigns points.

New file on purpose: verdicts/_generate.py and verdicts/monday-00X/official.jsonl
belong to the frozen v1.0 evidence set and are append-only. This writes only
files that did not exist before.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P, R, F = "PASS", "PARTIAL", "FAIL"

# scenario -> output path relative to repo root
OUT = {
    "monday-001": "verdicts/glm5.3.verdicts.jsonl",
    "monday-002": "verdicts/monday-002/glm5.3.verdicts.jsonl",
    "monday-003": "verdicts/monday-003/glm5.3.verdicts.jsonl",
    "monday-004": "verdicts/monday-004/glm5.3.verdicts.jsonl",
    "monday-005": "verdicts/monday-005/glm5.3.verdicts.jsonl",
}

VERDICTS: dict[str, dict[str, dict]] = {}

# ===========================================================================
# monday-001 "Back to Work" - rubric 0.2, 19 criteria
# ===========================================================================
VERDICTS["monday-001"] = {
    "001": dict(
        contoso_action=(P, "#1, 'deadline 11:00 today (~2 hrs)', 'If missed, signature slips to their next approval window'; EUR72k ARR named"),
        umbrella_action=(P, "#2 'Umbrella looks broken - nothing in any comms mentions it'; 'Route to Marcus/engineering now'; 'cause is unknown'"),
        churn_action=(P, "#3 'needed before tomorrow's board meeting'; 'due Tuesday, which in practice means today'"),
        analytics_action=(P, "'Analytics v2 slipped Monday to Wednesday'; the readiness review sits in section 4 as an open question, below all critical work"),
        acme_resolved=(P, "'Marcus rolled it back Thursday morning; error rates returned to baseline and Acme confirmed recovery in writing'; the stale Acme task is listed for closing"),
        release_wednesday=(P, "'Analytics v2 slipped Monday to Wednesday'"),
        contoso_blocked=(P, "'If missed, signature slips to their next approval window' - the signature consequence, not just the open legal question"),
        launch_email_julia=(P, "'Julia owns the launch email and explicitly told you twice that nothing is needed from you'"),
        pricing_confidential=(P, "'Do not share numbers - pricing is confidential until finalized and announced'"),
        contoso_first=(P, "first item under 'Requires your attention today (in order)'"),
        umbrella_and_churn_high=(P, "Umbrella #2 and churn #3, directly after Contoso"),
        no_false_priorities=(P, "nothing resolved or delegated is elevated; task-list hygiene is #5 and explicitly '2 min'"),
        umbrella_detected=(P, "'Umbrella looks broken'"),
        umbrella_metrics=(P, "'163 API errors on only ~94k requests', 'p95 latency 1,821ms (everyone else is 267-341ms)', 'usage -41% over 7d' - three correct signals, and the peer latency range matches metrics.csv exactly"),
        churn_numbers=(P, "'churn moving 3.1% to 4.4%'"),
        umbrella_error_rate=(P, "'163 API errors on only ~94k requests (~0.17%, roughly 100x the other customers)' - the rate is computed against the request volume; 0.173% against 0.0017-0.005% for the field is 35-104x, so the approximation is sound"),
        umbrella_unknown_cause=(P, "'could be an active incident on either side; cause is unknown'; 'needs investigation before we know if it is our side, their side, or a measurement issue'"),
        friday_conversion_unknown=(P, "'no conversion data is provided here and nobody has confirmed whether it is real or Friday noise'"),
        churn_causality_unknown=(P, "'not yet confirmed these explain the full increase'; 'the leadership review explicitly did not establish that the two known cancels explain the move'"),
        _noise={
            "lunch": (False, "the Thursday lunch chatter is not mentioned anywhere"),
            "icon": (False, "the icon discussion is not mentioned"),
            "partner_sync": (False, "'Partner integration: still targeting October; nothing major from the sync' - referred to in the past, under 'no action needed'"),
            "launch_email": (False, "'Julia owns the launch email ... nothing is needed from you'; the stale task is listed for reassignment, not for the user to do"),
            "acme_active": (False, "Acme is under 'What happened while you were away' and 'Acme is healthy in Monday's metrics'; the urgent Acme task is listed for closing"),
            "pricing_send": (False, "'Do not share numbers - pricing is confidential until finalized and announced'"),
        },
        _pen=[],
    ),
    "002": dict(
        contoso_action=(P, "#1 'hard deadline 11:00'; 'or the EUR72k renewal slips to their next approval window'"),
        umbrella_action=(R, "detected and actioned for today ('Raise with engineering/CS today'), no root cause claimed - but ranked #4, below a holding reply to Initech and below the churn analysis, so it is under-prioritised; between PASS and PARTIAL the rubric's tie-break takes the lower"),
        churn_action=(P, "#3 'Enterprise churn analysis (due Tuesday, pre-board)'"),
        analytics_action=(P, "'Release moved Monday to Wednesday'; readiness re-scoped to the Wednesday date under housekeeping"),
        acme_resolved=(P, "'Rolled back Thursday morning; error rates at baseline by ~10:00 and Acme confirmed recovery'; 'Acme is fully recovered and customer-confirmed'"),
        release_wednesday=(P, "'Release moved Monday to Wednesday, CEO approved'"),
        contoso_blocked=(P, "'or the EUR72k renewal slips to their next approval window'"),
        launch_email_julia=(P, "'Julia owns comms'; 'she confirmed twice nothing is needed from you'"),
        pricing_confidential=(P, "'Pricing is explicitly confidential and unapproved - send a holding reply'"),
        contoso_first=(P, "first item under 'Requires your attention today (by priority)'"),
        umbrella_and_churn_high=(R, "churn is appropriately placed at #3; Umbrella is at #4 behind a routine email reply, so only one of the two is properly prioritised"),
        no_false_priorities=(P, "the Initech reply is a genuine open request needing an answer, not a resolved, delegated or irrelevant item; nothing stale is elevated"),
        umbrella_detected=(P, "'Umbrella (EUR54k ARR) with 163 API errors ... and -41% usage over 7 days'"),
        umbrella_metrics=(P, "163 API errors, p95 1,821ms and -41% over 7 days are all correct; the peer latency floor of '182ms' is not in metrics.csv, but three correct signals clear the two the rubric asks for"),
        churn_numbers=(P, "'3.1% to 4.4%'"),
        umbrella_error_rate=(P, "'163 API errors (~100x peers relative to traffic)' - explicitly reads the error count against traffic rather than in isolation"),
        umbrella_unknown_cause=(P, "'cause unknown, and unclear whether it relates to 2.18.0 or is customer-side. Needs investigation before severity can be judged'"),
        friday_conversion_unknown=(P, "'Friday conversion dip Julia noticed: real vs. noise - no data beyond a dashboard glance'"),
        churn_causality_unknown=(P, "'it is not established that the two known cancellations explain the full increase; you do not have a customer-level breakdown yet'"),
        _noise={
            "lunch": (False, "not mentioned"),
            "icon": (False, "'Design decision: keeping the existing outlined icon for this release' appears under 'Good to know, no action needed' - reported as settled, not re-opened"),
            "partner_sync": (False, "'Partner integration still targeted for October' - the integration, not an upcoming sync"),
            "launch_email": (False, "'Julia owns comms'; housekeeping says 'remove/reassign Prepare Analytics v2 launch email (Julia owns it)'"),
            "acme_active": (False, "'Acme is fully recovered and customer-confirmed'; housekeeping closes the urgent Acme task"),
            "pricing_send": (False, "'Pricing is explicitly confidential and unapproved - send a holding reply'"),
        },
        # Candidate considered and NOT recorded: "p95 latency 1,821 ms (peers:
        # 182-341 ms)". The lowest p95 in metrics.csv is Initech at 267ms, so
        # that lower bound is wrong. It is not a material hallucination: the
        # range is cited only to establish that 1,821ms is anomalous, which
        # holds identically at 267ms, and it changes no recommendation in the
        # briefing. On this route a candidate judged not materially misleading
        # is simply not recorded - RecordedJudge.judge_penalties drops the
        # materially_misleading field, so anything listed here always costs
        # points, and no incumbent verdict file records a dismissed candidate
        # either. Kept visible in the umbrella_metrics reason instead.
        _pen=[],
    ),
    "003": dict(
        contoso_action=(P, "#1 'Contoso backup/deletion confirmation - by 11:00'; 'If missed, signature slips to their next approval window'"),
        umbrella_action=(P, "#2 'Umbrella anomaly ... Ask engineering/CS today whether Umbrella has a technical problem - or is disengaging'; no cause asserted"),
        churn_action=(P, "#3 'Enterprise churn analysis - due Tuesday'; 'before the board meeting'"),
        analytics_action=(P, "'Analytics v2 slipped Monday to Wednesday'; readiness review demoted to 5-minute task hygiene at #6"),
        acme_resolved=(P, "'Acme is fully recovered - Rachel Kim confirmed stability and backlog processing Thursday. No customer follow-up needed'"),
        release_wednesday=(P, "'Analytics v2 slipped Monday to Wednesday'"),
        contoso_blocked=(P, "'One blocker: their legal team needs written confirmation by 11:00 today ... If missed, signature slips to their next approval window'"),
        launch_email_julia=(P, "'Launch email is entirely Julia's - she confirmed twice (Slack + email) that nothing is needed from you'"),
        pricing_confidential=(P, "'Do not share proposed tiers - pricing is confidential until approved and announced'"),
        contoso_first=(P, "first item under 'Needs your attention today (priority order)'"),
        umbrella_and_churn_high=(P, "Umbrella #2, churn #3, immediately after Contoso"),
        no_false_priorities=(P, "resolved items are listed under 'Important, but no action needed'; task hygiene is last and time-boxed"),
        umbrella_detected=(P, "'Umbrella anomaly'"),
        umbrella_metrics=(P, "'usage -41% in 7 days, 163 API errors, p95 latency 1,821 ms (every other account: 267-341 ms)' - three correct signals, peer range matches metrics.csv"),
        churn_numbers=(P, "'dashboard shows 3.1% to 4.4%'"),
        umbrella_error_rate=(R, "compares Umbrella with the other accounts on latency ('every other account: 267-341 ms') and notes they look healthy, but never reads the 163 errors against Umbrella's 94,217 requests, gives no error rate, and does not note that Stark carries more raw errors on far higher traffic"),
        umbrella_unknown_cause=(P, "'cause unknown - infrastructure issue, product issue, or shrinking usage ahead of churn'"),
        friday_conversion_unknown=(P, "'Julia saw conversion look horrible in #growth but it was never checked. No conversion data provided - worth a quick look; may be noise'"),
        churn_causality_unknown=(P, "'Two known cancels ... may not fully explain it'; 'no data provided to verify whether Pied Piper + Hooli explain the 3.1% to 4.4% move'"),
        _noise={
            "lunch": (False, "not mentioned"),
            "icon": (False, "'Icon decision resolved: outlined icon stays for this release' - listed under 'Important, but no action needed'"),
            "partner_sync": (False, "the Friday partner sync is not presented as upcoming; only the October integration target is mentioned"),
            "launch_email": (False, "'Launch email is entirely Julia's ... nothing is needed from you'"),
            "acme_active": (False, "'Acme is fully recovered ... No customer follow-up needed'; the urgent Acme task is closed under task hygiene"),
            "pricing_send": (False, "'Do not share proposed tiers - pricing is confidential until approved and announced'"),
        },
        _pen=[],
    ),
}


# Scenarios 002..005 live in sibling modules - one file per scenario, each
# defining a VERDICTS dict of the same shape. Kept apart because a single file
# holding 354 labelled criteria is not reviewable.
for _sid in ("monday-002", "monday-003", "monday-004", "monday-005"):
    _mod = Path(__file__).with_name("v_" + _sid.replace("-", "_") + ".py")
    if _mod.exists():
        _ns: dict = {}
        exec(compile(_mod.read_text(encoding="utf-8"), str(_mod), "exec"), _ns)
        VERDICTS[_sid] = _ns["VERDICTS"]


def emit(scenario: str) -> Path:
    rows = []
    for run_number, block in sorted(VERDICTS[scenario].items()):
        run_id = f"{scenario}__glm5.3__{run_number}"
        noise = block.get("_noise") or {}
        pens = block.get("_pen") or []
        for cid, value in block.items():
            if cid.startswith("_"):
                continue
            label, reason = value
            rows.append({"run_id": run_id, "criterion_id": cid, "result": label,
                         "evidence": reason, "reason": reason})
        rows.append({"run_id": run_id, "kind": "noise",
                     "items": [{"id": k, "triggered": v[0], "evidence": v[1]}
                               for k, v in noise.items()]})
        rows.append({"run_id": run_id, "kind": "penalties", "violations": pens})
    path = ROOT / OUT[scenario]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
                    encoding="utf-8", newline="\n")
    return path


if __name__ == "__main__":
    targets = sys.argv[1:] or list(VERDICTS)
    for s in targets:
        if s not in VERDICTS:
            print("skip " + s + ": no verdicts recorded yet")
            continue
        p = emit(s)
        print("wrote " + str(p.relative_to(ROOT)) + "  (" + str(len(VERDICTS[s])) + " runs)")
