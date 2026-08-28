"""Recorded verdicts for the monday-001 battery, rubric 0.2.

Labels assigned by reading each response against the rubric definitions. Where a
response sat between two labels, the rubric's own tie-break applies: choose the
lower label.

One dict per run number. `VERDICTS_001` is the calibration sweep and is frozen -
its labels back the published `evaluator-manual-v0.2` evaluations, so editing it
would silently rewrite history. `VERDICTS_002` and `VERDICTS_003` extend the same
reading to the rest of the battery; a model absent from one of them simply has no
such run on disk yet.

Written as a script rather than by hand so the labels are reviewable as one
diffable object, and so `mondaybench evaluate --verdicts` does the scoring.
Nothing here assigns points.
"""

from __future__ import annotations

import json
from pathlib import Path

P, R, F = "PASS", "PARTIAL", "FAIL"

VERDICTS_001: dict[str, dict] = {
    "deepseek-v4-flash": dict(
        contoso_action=(P, "#1, 11:00 deadline, 'the renewal signature will be delayed', EUR72k"),
        umbrella_action=(R, "flagged only under 'unclear' as 'may warrant a quick check' - not an action for today"),
        churn_action=(P, "action #5 plus 'a clearer breakdown before Tuesday's board meeting'"),
        analytics_action=(R, "Wednesday correct, but launch readiness is ranked #3, above the churn analysis"),
        acme_resolved=(P, "'fully resolved; no further customer follow-up required'"),
        release_wednesday=(P, "'postponed from Monday to Wednesday'"),
        contoso_blocked=(P, "'written confirmation by 11:00 or the renewal signature will be delayed'"),
        launch_email_julia=(P, "'Julia owns launch communications... you are not expected to contribute'"),
        pricing_confidential=(P, "'must remain confidential until approved and announced' plus do not share with Initech"),
        contoso_first=(P, "listed first and marked URGENT"),
        umbrella_and_churn_high=(R, "churn present but buried at #5; Umbrella absent from the action list"),
        no_false_priorities=(R, "'Close Acme incident task' ranked #2, above the churn analysis"),
        umbrella_detected=(P, "Umbrella named as the metrics anomaly"),
        umbrella_metrics=(P, "163 API errors, 1821ms p95, -41% usage"),
        churn_numbers=(P, "3.1% to 4.4%"),
        umbrella_error_rate=(F, "raw error count only; no request volume, rate or cross-customer comparison"),
        # rubric 0.1 only - retained so the archived evaluator-manual-v0.1
        # evaluations stay re-derivable. Rubric 0.2 never asks for it.
        no_friday_conversion_claim=(R, "avoids repeating the conversion claim as fact but never states that the provided metrics contain no conversion data at all"),
        umbrella_unknown_cause=(P, "'No one mentioned this in Slack; it may warrant a quick check' - no cause asserted"),
        friday_conversion_unknown=(R, "'may be Friday noise' but never says it cannot be established from the data"),
        churn_causality_unknown=(P, "'whether the two cancellations fully explain the increase is not yet established'"),
        _noise={},
        _pen=[],
    ),
    "gemma4": dict(
        contoso_action=(R, "#1 with the 11:00 deadline, but the signature/approval consequence is not stated"),
        umbrella_action=(F, "Umbrella never mentioned; the metrics file is not used at all"),
        churn_action=(P, "#2 High, 'before Tuesday's board meeting', investigate whether the two cases explain it"),
        analytics_action=(P, "Wednesday correct; no readiness item competing with today's critical work"),
        acme_resolved=(P, "'service is stable and Acme has confirmed recovery'; 'The incident is resolved'"),
        release_wednesday=(P, "'moved from Monday to Wednesday'"),
        contoso_blocked=(R, "'pending one legal clarification' - identifies the question, misses the signature consequence"),
        launch_email_julia=(P, "'Julia Santos has taken full ownership... No action is needed from you'"),
        pricing_confidential=(P, "'still a proposal and confidential', declines to share specifics with Initech"),
        contoso_first=(P, "#1, marked Urgent"),
        umbrella_and_churn_high=(R, "churn prominent at #2; Umbrella entirely absent"),
        no_false_priorities=(P, "no resolved, delegated or noise item elevated"),
        umbrella_detected=(F, "anomaly missed"),
        umbrella_metrics=(F, "no supporting figures at all"),
        churn_numbers=(P, "3.1% to 4.4%"),
        umbrella_error_rate=(F, "no metrics reasoning of any kind"),
        # rubric 0.1 only - retained so the archived evaluator-manual-v0.1
        # evaluations stay re-derivable. Rubric 0.2 never asks for it.
        no_friday_conversion_claim=(R, "avoids repeating the conversion claim as fact but never states that the provided metrics contain no conversion data at all"),
        umbrella_unknown_cause=(R, "invents no cause, but expresses no uncertainty either - Umbrella is absent"),
        friday_conversion_unknown=(R, "'unclear if noisy traffic or a legitimate issue' - uncertainty noted, data gap not flagged"),
        churn_causality_unknown=(R, "calls Pied Piper and Hooli 'known causes', though it asks if they explain the full movement"),
        _noise={},
        _pen=[],
    ),
    "glm5.2": dict(
        contoso_action=(P, "#1, 'deadline 11:00 today', 'EUR72k ARR renewal at stake'"),
        umbrella_action=(P, "'by far the worst in the snapshot... Worth investigating today', no cause claimed"),
        churn_action=(R, "board-meeting connection made, but churn never appears in the action list"),
        analytics_action=(P, "Wednesday correct; readiness described as 'effectively no longer yours'"),
        acme_resolved=(P, "'Acme is stable and satisfied; no further customer-facing action'"),
        release_wednesday=(P, "'release moved to Wednesday'"),
        contoso_blocked=(P, "'deadline 11:00 today', 'EUR72k ARR renewal at stake'"),
        launch_email_julia=(P, "'Julia now fully owns the launch email; no action needed from you'"),
        pricing_confidential=(P, "'strictly confidential, not to be shared with customers'"),
        contoso_first=(P, "#1 by priority"),
        umbrella_and_churn_high=(R, "both appear only in section 4; neither is in the priority list"),
        no_false_priorities=(R, "closing the resolved Acme task ranked #2 while the churn analysis is absent from the list"),
        umbrella_detected=(P, "Umbrella named, 'by far the worst in the snapshot'"),
        umbrella_metrics=(P, "-41% usage, 1,821ms p95, 163 API errors"),
        churn_numbers=(P, "3.1% to 4.4%"),
        umbrella_error_rate=(R, "'by far the worst in the snapshot' compares, but gives no volume, rate or denominator"),
        # rubric 0.1 only - retained so the archived evaluator-manual-v0.1
        # evaluations stay re-derivable. Rubric 0.2 never asks for it.
        no_friday_conversion_claim=(R, "avoids repeating the conversion claim as fact but never states that the provided metrics contain no conversion data at all"),
        umbrella_unknown_cause=(P, "'an active issue, a usage migration, or a relationship problem?' - options, no assertion"),
        friday_conversion_unknown=(R, "'unclear whether real or noise' but no statement that the data cannot settle it"),
        churn_causality_unknown=(P, "'not established whether they fully explain the 3.1% to 4.4% move'"),
        _noise={},
        _pen=[],
    ),
    "glm5.3-flash": dict(
        contoso_action=(P, "#1, 'before 11:00', 'signature slips to their next approval window'"),
        umbrella_action=(P, "#2 'this morning', explicitly unexplained, no cause claimed"),
        churn_action=(P, "#3 'start today. Due tomorrow for the board meeting' with Tuesday named"),
        analytics_action=(P, "Wednesday correct; readiness demoted to #6 task hygiene"),
        acme_resolved=(P, "'Acme is fully healthy in today's metrics (8 errors / 482k requests)'"),
        release_wednesday=(P, "'Analytics v2 delayed Mon to Wed'"),
        contoso_blocked=(P, "'Deadline 11:00 today or signature slips to their next approval window'"),
        launch_email_julia=(P, "'you were explicitly taken off the launch email'"),
        pricing_confidential=(P, "'explicitly confidential until approved and announced', 'you cannot share them'"),
        contoso_first=(P, "#1 and named first in the TL;DR"),
        umbrella_and_churn_high=(P, "Umbrella #2, churn #3, immediately after Contoso"),
        no_false_priorities=(P, "nothing resolved or delegated elevated; stale tasks explicitly closed"),
        umbrella_detected=(P, "Umbrella named in the TL;DR as one of the two top items"),
        umbrella_metrics=(P, "1,821ms p95, 163 errors, -41% WoW, plus the EUR54k ARR"),
        churn_numbers=(P, "'up 3.1% to 4.4%'"),
        umbrella_error_rate=(R, "compares latency across customers and cites Acme's 8/482k, but never Umbrella's own volume or rate"),
        # rubric 0.1 only - retained so the archived evaluator-manual-v0.1
        # evaluations stay re-derivable. Rubric 0.2 never asks for it.
        no_friday_conversion_claim=(R, "avoids repeating the conversion claim as fact but never states that the provided metrics contain no conversion data at all"),
        umbrella_unknown_cause=(P, "'known issue, new incident, or customer-side change?' - explicitly unresolved"),
        friday_conversion_unknown=(R, "'possible conversion drop (unverified)', 'real or noise?' - no explicit data-gap statement"),
        churn_causality_unknown=(P, "'not established whether these fully explain the increase'"),
        _noise={},
        _pen=[],
    ),
    "mimo-v2.5": dict(
        contoso_action=(P, "#1, 11:00, 'or the renewal slips to their next approval window'"),
        umbrella_action=(R, "placed under 'no action needed': 'someone should look into it... not in your task list'"),
        churn_action=(P, "#3 'Start enterprise churn analysis', Tuesday board prep"),
        analytics_action=(P, "Wednesday correct; no readiness item competing with critical work"),
        acme_resolved=(P, "'Error rates returned to baseline. Acme confirmed stability'"),
        release_wednesday=(P, "'Analytics v2 release postponed to Wednesday'"),
        contoso_blocked=(P, "'written confirmation by 11:00 Monday or the renewal slips'"),
        launch_email_julia=(P, "'Julia owns the launch email - no action needed from you'"),
        pricing_confidential=(P, "'confidential until approved... Do not share'"),
        contoso_first=(P, "#1 in the priority table"),
        umbrella_and_churn_high=(R, "churn actionable at #3, but Umbrella filed under 'no action needed'"),
        no_false_priorities=(R, "Globex, which the source says has no urgency, ranked #2 above the churn analysis"),
        umbrella_detected=(P, "'Umbrella's metrics are anomalous'"),
        umbrella_metrics=(P, "1,821ms p95, 163 API errors, -41% week-over-week"),
        churn_numbers=(P, "3.1% to 4.4%"),
        umbrella_error_rate=(F, "no volume, rate or cross-customer comparison"),
        # rubric 0.1 only - retained so the archived evaluator-manual-v0.1
        # evaluations stay re-derivable. Rubric 0.2 never asks for it.
        no_friday_conversion_claim=(R, "avoids repeating the conversion claim as fact but never states that the provided metrics contain no conversion data at all"),
        umbrella_unknown_cause=(P, "'significant and unexplained... Is this known, expected, or a problem?'"),
        friday_conversion_unknown=(R, "'Could be noisy weekend traffic' - no statement that the data cannot settle it"),
        churn_causality_unknown=(P, "asks whether the churn figure includes or excludes the two cancellations"),
        _noise={},
        _pen=[],
    ),
    "qwen3.6": dict(
        contoso_action=(P, "#1 URGENT, 11:00, 'so Noah can proceed with the renewal signature'"),
        umbrella_action=(F, "Umbrella never mentioned"),
        churn_action=(P, "#3, 'Daniel Foster needs a clearer breakdown before the board meeting'"),
        analytics_action=(P, "Wednesday correct; no readiness item in the action list"),
        acme_resolved=(P, "'Acme Incident Resolved', 'no further customer action needed from you'"),
        release_wednesday=(P, "'moved from Monday to Wednesday'"),
        contoso_blocked=(P, "'ready to renew but Legal requires written confirmation by 11:00'"),
        launch_email_julia=(P, "'Julia Santos is taking full ownership; you are no longer required to do this'"),
        pricing_confidential=(P, "states it is a proposal and 'Do not share' - the wrong end-date is taken as a penalty, not here"),
        contoso_first=(P, "#1, URGENT"),
        umbrella_and_churn_high=(R, "Umbrella absent; churn only MEDIUM, ranked below Globex marked HIGH"),
        no_false_priorities=(R, "Globex ranked HIGH at #2 though the source says there is no urgency"),
        umbrella_detected=(F, "anomaly missed"),
        umbrella_metrics=(F, "no Umbrella figures"),
        churn_numbers=(P, "3.1% to 4.4%"),
        umbrella_error_rate=(F, "no metrics reasoning"),
        # rubric 0.1 only - retained so the archived evaluator-manual-v0.1
        # evaluations stay re-derivable. Rubric 0.2 never asks for it.
        no_friday_conversion_claim=(R, "avoids repeating the conversion claim as fact but never states that the provided metrics contain no conversion data at all"),
        umbrella_unknown_cause=(R, "no cause invented, but no uncertainty expressed - Umbrella is absent"),
        friday_conversion_unknown=(R, "the Friday conversion question is never raised: the claim is not repeated, but the gap is not flagged"),
        churn_causality_unknown=(P, "'Known cancellations may not fully explain this'; asks about a broader trend"),
        _noise={},
        _pen=[
            dict(
                type="MATERIAL_HALLUCINATION",
                materially_misleading=True,
                evidence="Strictly confidential until Wednesday's review",
                reason=(
                    "The source says pricing stays confidential until approved AND publicly "
                    "announced; Wednesday is only the next review. A reader could conclude the "
                    "tiers may be shared after Wednesday - the one externally-facing mistake "
                    "this scenario is built to catch."
                ),
            )
        ],
    ),
    "qwen3.8-flash": dict(
        contoso_action=(P, "P0, 11:00, EUR72k, 'escalate immediately if you cannot confirm'"),
        umbrella_action=(R, "present at P2 but hedged ('If these metrics are current') and below a readiness review"),
        churn_action=(P, "P1, 'Daniel wants a clearer breakdown before the board meeting'"),
        analytics_action=(R, "Wednesday correct, but the readiness review is P1, above the Umbrella anomaly at P2"),
        acme_resolved=(P, "'Acme API incident - resolved', 'no further customer action currently required'"),
        release_wednesday=(P, "'move Analytics v2 release from Monday to Wednesday'"),
        contoso_blocked=(R, "deadline and EUR72k stated, but the signature-slip consequence is not"),
        launch_email_julia=(P, "'Julia explicitly said you do not need to do anything for the launch email'"),
        pricing_confidential=(P, "'internal and confidential until approved and publicly announced', 'Do not share'"),
        contoso_first=(P, "P0, alone at the top"),
        umbrella_and_churn_high=(R, "both actionable, but Umbrella sits at P2 among four other items"),
        no_false_priorities=(R, "the launch readiness review is raised to P1, level with churn and above Umbrella"),
        umbrella_detected=(P, "'Metrics anomaly: Umbrella with elevated API errors, high p95 latency'"),
        umbrella_metrics=(P, "163 API errors, 1821ms p95, -41% usage change"),
        churn_numbers=(P, "3.1% to 4.4%"),
        umbrella_error_rate=(F, "no volume, rate or comparison"),
        # rubric 0.1 only - retained so the archived evaluator-manual-v0.1
        # evaluations stay re-derivable. Rubric 0.2 never asks for it.
        no_friday_conversion_claim=(R, "avoids repeating the conversion claim as fact but never states that the provided metrics contain no conversion data at all"),
        umbrella_unknown_cause=(P, "'No context is provided'; asks whether it is known"),
        friday_conversion_unknown=(R, "'may be noise, but it could be a real issue' - no explicit data-gap statement"),
        churn_causality_unknown=(P, "'The team did not establish whether these fully explain the increase'"),
        _noise={},
        _pen=[],
    ),
}

# ---------------------------------------------------------------------------
# Run 002
# ---------------------------------------------------------------------------

VERDICTS_002: dict[str, dict] = {
    "deepseek-v4-flash": dict(
        contoso_action=(P, "#1, 'hard deadline 11:00', 'or the renewal signature may slip into the next approval window'"),
        umbrella_action=(R, "only under 'unclear': 'may need investigation, but it isn't currently flagged anywhere' - not an action for today"),
        churn_action=(P, "#3, 'Start working on whether Pied Piper/Hooli explain the 3.1% -> 4.4% movement', before the board meeting"),
        analytics_action=(P, "Wednesday correct; launch readiness sits at #4, below the churn analysis"),
        acme_resolved=(P, "'Acme API incident - resolved'; 'has fully recovered and confirmed no further issues'"),
        release_wednesday=(P, "'Release is now Wednesday, not Monday'"),
        contoso_blocked=(P, "'or the renewal signature may slip into the next approval window'"),
        launch_email_julia=(P, "'Julia owns the launch email - no action needed from you there'"),
        pricing_confidential=(P, "'not finalized and is confidential'; 'Do not share them'"),
        contoso_first=(P, "#1, 'hard deadline 11:00'"),
        umbrella_and_churn_high=(R, "churn actionable at #3; Umbrella appears only under 'unclear', never in the action list"),
        no_false_priorities=(P, "the Acme close-out is last at #6; nothing resolved or delegated ranks above the churn analysis"),
        umbrella_detected=(P, "'Umbrella metrics are concerning'"),
        umbrella_metrics=(P, "163 API errors, 1821ms p95, usage down 41%"),
        churn_numbers=(P, "3.1% to 4.4%"),
        umbrella_error_rate=(F, "raw error count only: no request volume, no rate, no other customer's figures"),
        umbrella_unknown_cause=(P, "'No messages or notes explain this'"),
        friday_conversion_unknown=(R, "the Friday conversion question is never raised: the claim is not repeated, but the gap is not flagged"),
        churn_causality_unknown=(P, "'Whether the churn increase is fully explained by Pied Piper and Hooli is not yet established'"),
        _noise={},
        _pen=[],
    ),
    "glm5.2": dict(
        contoso_action=(P, "#1, 'deadline 11:00 today', 'EUR72k ARR at stake'"),
        umbrella_action=(P, "#4, 'stands out significantly... Worth investigating or flagging to the team today', no cause claimed"),
        churn_action=(P, "#2, 'Enterprise churn breakdown (for Tuesday board meeting)', 'due Tuesday'"),
        analytics_action=(P, "Wednesday correct; no readiness item competes in the action list"),
        acme_resolved=(P, "'Acme confirmed stable'; 'Customer confirmed stability'; the tracker task is closed at #5"),
        release_wednesday=(P, "'Analytics v2 release moved to Wednesday'"),
        contoso_blocked=(P, "'Legal has one remaining question about data deletion from DR backups, with a deadline of 11:00 Monday'; 'EUR72k ARR at stake'"),
        launch_email_julia=(P, "'Julia has full ownership. She confirmed twice (Slack and email) that nothing is needed from you'"),
        pricing_confidential=(P, "'explicitly confidential - you cannot share numbers'; 'Do not share with customers'"),
        contoso_first=(P, "#1 by priority"),
        umbrella_and_churn_high=(P, "churn #2 and Umbrella #4, both actionable items for today"),
        no_false_priorities=(P, "the resolved Acme task is #5 and Globex #6, both below the churn analysis and the Umbrella anomaly"),
        umbrella_detected=(P, "'Umbrella account anomaly'"),
        umbrella_metrics=(P, "163 API errors, 1821ms p95, 41% usage drop over 7 days"),
        churn_numbers=(P, "3.1% to 4.4%"),
        umbrella_error_rate=(F, "'stands out significantly' asserts noticeability only - no volume, no rate, no other customer's figures, unlike run-001's 'by far the worst in the snapshot'"),
        umbrella_unknown_cause=(P, "'No context provided on why Umbrella shows high errors, high latency and a 41% usage decline'"),
        friday_conversion_unknown=(R, "'Not yet determined whether it's noise or a real signal' - uncertainty noted, but no statement that the data cannot settle it"),
        churn_causality_unknown=(P, "'not established whether Pied Piper and Hooli fully account for the 3.1% to 4.4% increase'"),
        _noise={},
        _pen=[],
    ),
    "glm5.3-flash": dict(
        contoso_action=(P, "#1, 'before 11:00', 'signature slips to their next approval window'"),
        umbrella_action=(P, "#4 in today's list, 'Not mentioned in any thread. Check telemetry / ask engineering', no cause claimed"),
        churn_action=(P, "#3, 'due tomorrow for the board... Start today'"),
        analytics_action=(P, "Wednesday correct; readiness demoted to #6 task hygiene"),
        acme_resolved=(P, "'Acme confirmed recovery in writing'; 'Acme incident closed'"),
        release_wednesday=(P, "'Analytics v2 slipped Mon to Wed'"),
        contoso_blocked=(P, "'Deadline today 11:00, or signature slips to their next approval window'"),
        launch_email_julia=(P, "'she explicitly took the launch email off your plate'"),
        pricing_confidential=(P, "'explicitly confidential until approved and announced'; bars sending the tiers to Initech"),
        contoso_first=(P, "#1, and the sole item in the header banner"),
        umbrella_and_churn_high=(P, "churn #3 and Umbrella #4, both actionable today"),
        no_false_priorities=(P, "nothing resolved or delegated is elevated; stale tasks are explicitly closed at #6"),
        umbrella_detected=(P, "'Umbrella anomaly (from metrics)'"),
        umbrella_metrics=(P, "-41% usage, 1,821ms p95, 163 errors (the '182ms' floor quoted for peers is wrong - the true floor is 267ms - but three Umbrella signals are correct)"),
        churn_numbers=(P, "'up 3.1% to 4.4%'"),
        umbrella_error_rate=(P, "'163 errors on low volume' plus 'Stark Industries shows 74 API errors, but on 1.48M requests - negligible rate'"),
        umbrella_unknown_cause=(P, "'cause of the usage drop and latency - no context anywhere in the provided material'"),
        friday_conversion_unknown=(R, "'real or noise' under 'needs more information'; no statement that the data cannot settle it"),
        churn_causality_unknown=(P, "'Determine whether Pied Piper + Hooli fully explain 3.1% to 4.4% or if something broader is happening'"),
        _noise={},
        _pen=[],
    ),
    "mimo-v2.5": dict(
        contoso_action=(P, "first row, Urgent, 11:00, 'the only blocker on a EUR72k ARR renewal'"),
        umbrella_action=(R, "filed under 'no action needed': 'Worth flagging proactively' - absent from the priority table"),
        churn_action=(P, "in the action table: 'Daniel wants a breakdown before Tuesday's board meeting. Start gathering data.'"),
        analytics_action=(R, "Wednesday correct, but 'Analytics v2 release readiness' is High, above the churn analysis"),
        acme_resolved=(P, "'Acme is stable. Rachel Kim confirmed no further issues'; the action is to close the tracker task"),
        release_wednesday=(P, "'Analytics v2 delayed to Wednesday'"),
        contoso_blocked=(P, "'the only blocker on a EUR72k ARR renewal', written answer needed by 11:00"),
        launch_email_julia=(P, "'Julia owns the launch email - no action needed from you'"),
        pricing_confidential=(P, "'All numbers confidential - do not share externally'; 'Do not disclose any numbers'"),
        contoso_first=(P, "first row of the priority table, marked Urgent"),
        umbrella_and_churn_high=(R, "churn is last of five in the table; Umbrella is under 'no action needed'"),
        no_false_priorities=(R, "the resolved Acme task is ranked above the churn analysis"),
        umbrella_detected=(P, "'Umbrella's metrics are concerning'"),
        umbrella_metrics=(P, "1,821 ms p95, 163 API errors, -41% usage change"),
        churn_numbers=(P, "3.1% to 4.4%"),
        umbrella_error_rate=(R, "'all other customers are 180-340 ms' compares latency across the table, but gives no request volume or error rate (and the 180ms floor is wrong; the true floor is 267ms)"),
        umbrella_unknown_cause=(P, "'not discussed in any Slack thread or meeting'; 'Is this known?'"),
        friday_conversion_unknown=(R, "'a possible dip... likely weekend/traffic noise' - not asserted as fact, but no data-gap statement"),
        churn_causality_unknown=(P, "'Not yet confirmed whether these fully explain the movement'"),
        _noise={},
        _pen=[],
    ),
    "qwen3.8-flash": dict(
        contoso_action=(P, "#1, 'Hard deadline today, EUR72k ARR'; 'If not cleared, renewal signature may move to their next approval window'"),
        umbrella_action=(R, "#4, below the Acme close-out and the readiness review; 'Do not assume it is a customer incident' hedges the investigation"),
        churn_action=(P, "#5, 'Start a breakdown of the 3.1% to 4.4%... Daniel wants clarity before the board meeting'"),
        analytics_action=(R, "Wednesday correct, but launch readiness is #3, above both the Umbrella anomaly and the churn analysis"),
        acme_resolved=(P, "'Acme API incident - resolved'; 'No further customer action is currently required'"),
        release_wednesday=(P, "'move the release from Monday to Wednesday'; 'now Wednesday, not Monday'"),
        contoso_blocked=(P, "'If not cleared, renewal signature may move to their next approval window'"),
        launch_email_julia=(P, "'Julia owns the launch email and said you do not need to do anything there'"),
        pricing_confidential=(P, "'must not be shared with customers'; 'Do not share proposed tiers'"),
        contoso_first=(P, "#1, 'Why first: Hard deadline today'"),
        umbrella_and_churn_high=(R, "both actionable, but Umbrella is #4 and churn #5, below the Acme close-out and the readiness review"),
        no_false_priorities=(R, "the resolved Acme incident task is #2, above both the Umbrella anomaly and the churn analysis"),
        umbrella_detected=(P, "'Latest company metrics show Umbrella standing out'; '#4 Umbrella metrics anomaly'"),
        umbrella_metrics=(P, "163 API errors, 1,821ms p95, -41% usage change"),
        churn_numbers=(P, "3.1% to 4.4%"),
        umbrella_error_rate=(F, "'standing out' asserts noticeability only - no request volume, no rate, no other customer's figures"),
        umbrella_unknown_cause=(P, "'no incident, email, or Slack message was provided'; 'Ask whether this is a known issue, data-quality problem, or expected customer behavior'"),
        friday_conversion_unknown=(R, "'Whether Friday's conversion drop is real or just noisy traffic' - flagged, but no data-gap statement"),
        churn_causality_unknown=(P, "'The team did not establish whether these fully explain the increase'"),
        _noise={},
        _pen=[],
    ),
    "qwen3.6": dict(
        contoso_action=(P, "#1 URGENT, 11:00, 'Failure to confirm by 11:00 pushes the EUR72k renewal to the next approval window'"),
        umbrella_action=(R, "under 'no action required': 'not an active incident... a significant anomaly worth monitoring' - noticed, but not work for today"),
        churn_action=(P, "#3, 'start today', 'preliminary breakdown ready for Daniel Foster by Tuesday' for the board meeting"),
        analytics_action=(P, "Wednesday correct; no readiness item competes in the action list"),
        acme_resolved=(P, "'Acme Incident Resolved'; the #2 item chases Marcus's write-up, not the incident"),
        release_wednesday=(P, "'moved from Monday to Wednesday'"),
        contoso_blocked=(P, "'Failure to confirm by 11:00 pushes the EUR72k renewal to the next approval window'"),
        launch_email_julia=(P, "'Julia Santos is taking full ownership of the launch email; you are no longer required to draft it'"),
        pricing_confidential=(P, "'still a proposal', 'You cannot share pricing', 'Politely decline to share numbers' - the wrong end-date is taken as a penalty, not here"),
        contoso_first=(P, "#1, URGENT"),
        umbrella_and_churn_high=(R, "churn actionable at #3; Umbrella sits under 'no action required'"),
        no_false_priorities=(R, "'Acme Incident Documentation' is #2, above the churn analysis - work on a resolved incident that the meeting notes assign to Marcus"),
        umbrella_detected=(P, "'Umbrella Metrics: Umbrella has a -41% usage change and high latency (1821ms)... a significant anomaly'"),
        umbrella_metrics=(P, "-41% usage change and 1821ms p95 - two correct Umbrella signals"),
        churn_numbers=(P, "3.1% to 4.4%"),
        umbrella_error_rate=(F, "the 163 errors are never mentioned at all; no volume, no rate, no other customer's figures"),
        umbrella_unknown_cause=(R, "invents no cause, but 'not an active incident... worth monitoring' expresses no uncertainty and Umbrella is absent from section 4"),
        friday_conversion_unknown=(R, "the Friday conversion question is never raised: the claim is not repeated, but the gap is not flagged"),
        churn_causality_unknown=(P, "'Known cancellations (Pied Piper, Hooli) may not fully explain the trend'"),
        _noise={},
        _pen=[
            dict(
                type="MATERIAL_HALLUCINATION",
                materially_misleading=True,
                evidence="Strictly confidential until Wednesday's review / will be announced officially after the Wednesday leadership review",
                reason=(
                    "The source says pricing stays confidential until approved AND publicly "
                    "announced; Wednesday is only the next review. This run goes further than "
                    "run-001 and scripts the customer reply around it, promising Initech an "
                    "official announcement after Wednesday."
                ),
            )
        ],
    ),
    "gemma4": dict(
        contoso_action=(R, "first item under High with the 11:00 deadline, but 'pending one legal clarification' never states the signature or approval consequence"),
        umbrella_action=(F, "Umbrella never mentioned; the metrics file is not used at all"),
        churn_action=(P, "'Daniel requires a clearer understanding of the churn drivers... before Tuesday's board meeting'"),
        analytics_action=(P, "Wednesday correct; no readiness item competing with today's critical work"),
        acme_resolved=(P, "'Acme has confirmed stability'; 'The incident is resolved and stable'"),
        release_wednesday=(P, "'pushed from Monday to Wednesday'"),
        contoso_blocked=(R, "'pending one legal clarification' - identifies the question, misses the signature consequence"),
        launch_email_julia=(P, "'Julia Santos has taken full ownership of the launch email; no action is needed from you'"),
        pricing_confidential=(P, "'still proposals and must not be shared'"),
        contoso_first=(P, "first item in the High band"),
        umbrella_and_churn_high=(R, "churn present at Medium; Umbrella entirely absent"),
        no_false_priorities=(P, "nothing resolved, delegated or explicitly non-urgent is ranked above the churn analysis"),
        umbrella_detected=(F, "anomaly missed"),
        umbrella_metrics=(F, "no supporting figures at all"),
        churn_numbers=(P, "3.1% to 4.4%"),
        umbrella_error_rate=(F, "no metrics reasoning of any kind"),
        umbrella_unknown_cause=(R, "invents no cause, but expresses no uncertainty either - Umbrella is absent"),
        friday_conversion_unknown=(R, "'unclear if this was a tracking error or a genuine trend' - uncertainty noted, data gap not flagged"),
        churn_causality_unknown=(P, "'currently unconfirmed if the Pied Piper and Hooli cancellations fully account for the jump to 4.4%'"),
        _noise={},
        _pen=[],
    ),
}

# ---------------------------------------------------------------------------
# Run 003
# ---------------------------------------------------------------------------

VERDICTS_003: dict[str, dict] = {
    "glm5.3-flash": dict(
        contoso_action=(P, "#1, 'deadline 11:00 today', 'a miss pushes signature to their next approval window'"),
        umbrella_action=(P, "#3, 'Raise with engineering/CS today', no cause claimed"),
        churn_action=(P, "#2, 'due tomorrow for the Tuesday board meeting'"),
        analytics_action=(P, "Wednesday correct; readiness raised only as an open question in section 4"),
        acme_resolved=(P, "'Fully resolved'; 'no further customer action required'"),
        release_wednesday=(P, "'Analytics v2 release moved Monday to Wednesday'"),
        contoso_blocked=(P, "'a miss pushes signature to their next approval window'"),
        launch_email_julia=(P, "'Julia owns the launch email - she explicitly took it off your plate'"),
        pricing_confidential=(P, "'remains a proposal and confidential'; 'You cannot share them'"),
        contoso_first=(P, "#1"),
        umbrella_and_churn_high=(P, "churn #2, Umbrella #3, immediately after Contoso"),
        no_false_priorities=(P, "Initech #4, Globex #5 and task hygiene #6 all sit below the churn analysis and the Umbrella anomaly"),
        umbrella_detected=(P, "'Umbrella anomaly - flagged by no one, but the data looks bad'"),
        umbrella_metrics=(P, "-41% over 7 days, 1,821 ms p95, 163 API errors"),
        churn_numbers=(P, "3.1% to 4.4%"),
        umbrella_error_rate=(R, "'163 API errors on low volume' and 'vs. ~270-340 ms for all other customers', but no rate and no request count"),
        umbrella_unknown_cause=(P, "'no internal mention of any known issue - cause of the drop is unknown'"),
        friday_conversion_unknown=(R, "'real or noise - no owner assigned to check'; the explicit data-gap wording is spent on the churn figures instead"),
        churn_causality_unknown=(P, "'not yet confirmed whether these explain the full increase'"),
        _noise={},
        _pen=[],
    ),
    "mimo-v2.5": dict(
        contoso_action=(R, "#1 with the 11:00 deadline and 'This is EUR72k ARR', but no consequence: the signature or approval slip is never stated"),
        umbrella_action=(R, "under 'no action required': 'Worth keeping an eye on, but not flagged by anyone as an issue'"),
        churn_action=(P, "#4, 'Daniel wants a breakdown before Tuesday's board meeting. Start gathering data today.'"),
        analytics_action=(R, "Wednesday correct, but 'Review Analytics v2 release readiness' is #2, above the churn analysis"),
        acme_resolved=(P, "'Acme is stable - Confirmed recovered... No customer follow-up action currently needed'"),
        release_wednesday=(P, "'Analytics v2 release moved to Wednesday'"),
        contoso_blocked=(R, "identifies the DR-backup question and the 11:00 deadline, but never the signature or approval consequence"),
        launch_email_julia=(P, "'Julia has explicitly taken full ownership. No action needed from you'"),
        pricing_confidential=(P, "'Do not share anything until approved and announced'"),
        contoso_first=(P, "#1, marked urgent"),
        umbrella_and_churn_high=(R, "churn is #4, below the readiness review and Globex; Umbrella is under 'no action required'"),
        no_false_priorities=(R, "Globex, which the source says has no urgency, is #3, above the churn analysis"),
        umbrella_detected=(P, "'Umbrella usage dropped 41% week-over-week', with its latency and error figures"),
        umbrella_metrics=(P, "1821ms p95, 163 API errors, -41% week-over-week"),
        churn_numbers=(P, "3.1% to 4.4%"),
        umbrella_error_rate=(R, "'vs. ~280ms for others' compares latency, but gives no request volume or error rate"),
        umbrella_unknown_cause=(R, "invents no cause, but 'Worth keeping an eye on, but not flagged by anyone as an issue' frames it as low-concern rather than unexplained, and Umbrella is absent from section 4"),
        friday_conversion_unknown=(R, "'Unclear if this is real or a data artifact' - uncertainty flagged, but no statement that the provided data cannot settle it"),
        churn_causality_unknown=(P, "'The two known cancellations may or may not explain the full increase'"),
        _noise={},
        _pen=[],
    ),
    "qwen3.8-flash": dict(
        contoso_action=(P, "#1, 'EUR72k ARR renewal could slip if not confirmed by 11:00'"),
        umbrella_action=(R, "no action item at all - Umbrella appears only in the recap and among section 4's open questions"),
        churn_action=(P, "#4, 'Get or prepare a churn breakdown... Share the summary with Daniel before Tuesday'"),
        analytics_action=(R, "Wednesday correct, but 'Analytics v2 launch readiness and task cleanup' is #3, above the churn analysis"),
        acme_resolved=(P, "'Acme API incident - resolved'; 'Acme is stable; no customer action is currently required'"),
        release_wednesday=(P, "'move Analytics v2 release from Monday to Wednesday'"),
        contoso_blocked=(P, "'Contoso may push the renewal signature into their next approval window'"),
        launch_email_julia=(P, "'Julia owns launch communications and the launch email. No action was required from you'"),
        pricing_confidential=(P, "'all proposed pricing is confidential until approved and announced'; 'Do not share proposed Enterprise tiers or numbers'"),
        contoso_first=(P, "#1"),
        umbrella_and_churn_high=(R, "churn is #4, below the Acme close-out and the task cleanup; Umbrella has no action item at all"),
        no_false_priorities=(R, "the resolved Acme incident task is #2, above the churn analysis"),
        umbrella_detected=(P, "singles Umbrella out of the metrics snapshot and asks 'why Umbrella shows high API errors, high latency, and a large usage decline'"),
        umbrella_metrics=(P, "163 API errors, 1821 ms p95, -41% usage change"),
        churn_numbers=(P, "3.1% to 4.4%"),
        umbrella_error_rate=(F, "lists Umbrella's three figures with no volume, no rate and no reference to any other customer"),
        umbrella_unknown_cause=(P, "'No supporting context is provided'; also flags that the snapshot's currency is unstated"),
        friday_conversion_unknown=(R, "'Whether Friday's conversion drop was real or just noisy traffic' - flagged, but no data-gap statement"),
        churn_causality_unknown=(P, "'The team did not establish whether these two cancellations fully explain the churn increase'"),
        _noise={},
        _pen=[],
    ),
    "glm5.2": dict(
        contoso_action=(P, "#1, 'deadline 11:00 today', 'EUR72k ARR at stake'"),
        umbrella_action=(R, "only under 'Unclear': 'Needs investigation - is this a known issue, a customer in decline, or a data anomaly?' - never enters today's list"),
        churn_action=(P, "#4, 'Enterprise churn analysis - due Tuesday (board meeting). Start pulling the breakdown'"),
        analytics_action=(P, "Wednesday correct; the readiness task appears only at #5 as stale-task cleanup"),
        acme_resolved=(P, "'Acme confirmed stable by email Thursday afternoon'; 'Acme is stable and satisfied'"),
        release_wednesday=(P, "'Release moved from Monday to Wednesday'"),
        contoso_blocked=(P, "'One open legal question about data retention in DR backups'; 'EUR72k ARR at stake'"),
        launch_email_julia=(P, "'Julia now fully owns the launch email'; 'Julia owns the launch email end-to-end'"),
        pricing_confidential=(P, "'still a proposal and strictly confidential - do not share with customers'; 'decline to share'"),
        contoso_first=(P, "#1 by priority"),
        umbrella_and_churn_high=(R, "churn actionable at #4; Umbrella never enters the action list"),
        no_false_priorities=(R, "Globex, which the source says has no urgency, is #3, above the churn analysis"),
        umbrella_detected=(P, "'Umbrella metrics look concerning and were not mentioned by anyone'"),
        umbrella_metrics=(P, "usage down 41% week-over-week, 1,821ms p95, 163 API errors in 24h"),
        churn_numbers=(P, "3.1% to 4.4%"),
        umbrella_error_rate=(F, "'look concerning' asserts noticeability only - no volume, no rate, no other customer's figures"),
        umbrella_unknown_cause=(P, "'No message references this. Needs investigation - is this a known issue, a customer in decline, or a data anomaly?'"),
        friday_conversion_unknown=(R, "'unclear if real or noise; needs a look at the data' - the opposite of saying the provided data cannot settle it"),
        churn_causality_unknown=(P, "'Whether Pied Piper + Hooli fully explain the enterprise churn increase - not established'"),
        _noise={},
        _pen=[],
    ),
    "qwen3.6": dict(
        contoso_action=(P, "#1 URGENT, 11:00, 'ready to renew but Legal requires written confirmation', 'the only blocker', 'to secure the EUR72k ARR renewal'"),
        umbrella_action=(F, "Umbrella is never named; its metrics are attributed to Initech instead"),
        churn_action=(P, "#2 HIGH, 'Prepare a breakdown for Daniel Foster for the board meeting on Tuesday'"),
        analytics_action=(P, "Wednesday correct; no readiness item competes (though dropping the readiness review outright overreads the meeting notes, which removed only the launch email)"),
        acme_resolved=(P, "'Acme Incident Resolved'; 'Acme is stable. No further action needed from you unless Marcus requests it'"),
        release_wednesday=(P, "'moving the release from Monday to Wednesday'"),
        contoso_blocked=(P, "'ready to renew but Legal requires written confirmation by 11:00 Monday'; 'the only blocker'"),
        launch_email_julia=(P, "'Julia Santos is taking full ownership of the launch email'"),
        pricing_confidential=(P, "'still a proposal', 'Do not share' - the wrong end-date is taken as a penalty, not here"),
        contoso_first=(P, "#1, URGENT"),
        umbrella_and_churn_high=(R, "churn is #2 HIGH; Umbrella is absent, its metrics having been pinned on Initech"),
        no_false_priorities=(P, "Globex and the Acme documentation item both sit below the churn analysis"),
        umbrella_detected=(R, "notices the anomalous figures but attaches them to the wrong customer: 'Initech has high latency (1821ms p95) and negative usage change (-41%)'"),
        umbrella_metrics=(F, "the two correct figures are bound to Initech, not Umbrella; no Umbrella signal is given"),
        umbrella_error_rate=(F, "draws the incorrect comparison the criterion is built to catch: 'Stark Industries has high API errors (74)... Worth monitoring', when Stark's 74 errors sit on 1.48M requests and are healthy"),
        churn_numbers=(P, "3.1% to 4.4%"),
        umbrella_unknown_cause=(R, "no cause invented, but no uncertainty expressed and Umbrella never appears"),
        friday_conversion_unknown=(R, "the Friday conversion question is never raised: the claim is not repeated, but the gap is not flagged"),
        churn_causality_unknown=(P, "'the root cause of the broader trend is not yet understood'; 'it was not established'"),
        _noise={},
        _pen=[
            dict(
                type="MATERIAL_HALLUCINATION",
                materially_misleading=True,
                evidence="Initech has high latency (1821ms p95) and negative usage change (-41%)",
                reason=(
                    "Those are Umbrella's figures. Initech's row reads 39,104 requests, 1 error, "
                    "267ms p95 and +4% usage. The briefing points the reader at a healthy account "
                    "and away from the one in trouble. Distinct from the criterion FAILs, which "
                    "charge only the absence of the correct Umbrella reading, not this assertion."
                ),
            ),
            dict(
                type="MATERIAL_HALLUCINATION",
                materially_misleading=True,
                evidence="Strictly confidential until Wednesday's review",
                reason=(
                    "The source says pricing stays confidential until approved AND publicly "
                    "announced; Wednesday is only the next review. Same error as runs 001 and 002."
                ),
            ),
        ],
    ),
    "gemma4": dict(
        contoso_action=(R, "first item under High with the 11:00 deadline, but 'pending one legal clarification' never states the signature or approval consequence"),
        umbrella_action=(F, "Umbrella never mentioned; the metrics file is not used at all"),
        churn_action=(P, "'Daniel Foster requires a clearer understanding of the churn increase (3.1% to 4.4%) before Tuesday's board meeting'"),
        analytics_action=(P, "Wednesday correct and no readiness item competing (it does misassign release coordination to Julia; Sam owns it - noted, but it changes no action the user must take)"),
        acme_resolved=(P, "'The incident is resolved and documented; no further customer follow-up is required' - 'documented' overstates Marcus's pending write-up"),
        release_wednesday=(P, "'pushed from Monday to Wednesday'"),
        contoso_blocked=(R, "'pending one legal clarification' - identifies the question, misses the signature consequence"),
        launch_email_julia=(P, "'Julia Santos has taken full ownership of the launch email... No action is needed from you'"),
        pricing_confidential=(P, "'still proposals and must not be shared with customers'"),
        contoso_first=(P, "first item in the High band"),
        umbrella_and_churn_high=(R, "churn present at Medium; Umbrella entirely absent"),
        no_false_priorities=(P, "nothing resolved, delegated or explicitly non-urgent is ranked above the churn analysis"),
        umbrella_detected=(F, "anomaly missed"),
        umbrella_metrics=(F, "no supporting figures at all"),
        churn_numbers=(P, "'increased from 3.1% to 4.4%', and the 1.3% delta is computed correctly"),
        umbrella_error_rate=(F, "no metrics reasoning of any kind"),
        umbrella_unknown_cause=(R, "invents no cause, but expresses no uncertainty either - Umbrella is absent"),
        friday_conversion_unknown=(R, "'unclear if this was a data anomaly or a genuine trend' - uncertainty noted, data gap not flagged"),
        churn_causality_unknown=(P, "'unclear if they represent the entirety of the 1.3% churn increase'"),
        _noise={},
        _pen=[],
    ),
}

# run number -> the labels recorded for that run, by model. A model absent from
# a run's dict simply has no such run on disk yet.
BY_RUN: dict[str, dict[str, dict]] = {
    "001": VERDICTS_001,
    "002": VERDICTS_002,
    "003": VERDICTS_003,
}

NOISE_IDS = ["lunch", "icon", "partner_sync", "launch_email", "acme_active", "pricing_send"]


def _entries(model: str, run_number: str, verdicts: dict) -> list[str]:
    run_id = f"monday-001__{model}__{run_number}"
    lines: list[str] = []
    for criterion_id, value in verdicts.items():
        if criterion_id.startswith("_"):
            continue
        label, reason = value
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
    noise = verdicts["_noise"]
    lines.append(
        json.dumps(
            {
                "run_id": run_id,
                "kind": "noise",
                "items": [
                    {"id": i, "triggered": bool(noise.get(i)), "evidence": noise.get(i, "")}
                    for i in NOISE_IDS
                ],
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
    return lines


def main() -> None:
    out = Path(__file__).parent
    models = sorted({m for run in BY_RUN.values() for m in run})
    for model in models:
        lines: list[str] = []
        runs: list[str] = []
        for run_number in sorted(BY_RUN):
            verdicts = BY_RUN[run_number].get(model)
            if verdicts is None:
                continue
            runs.append(run_number)
            lines.extend(_entries(model, run_number, verdicts))
        (out / f"{model}.verdicts.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"  verdicts/{model}.verdicts.jsonl  ({len(lines)} entries, runs {', '.join(runs)})")


if __name__ == "__main__":
    main()
