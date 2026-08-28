"""Recorded verdicts for the monday-001 battery at 32,000 tokens, rubric 0.2.

Labels assigned by reading each response against the rubric definitions. Where a
response sits between two labels, the rubric's own tie-break applies: choose the
lower label.

One dict per run number. A model absent from one of them simply has no such run
on disk yet.

Written as a script rather than by hand so the labels are reviewable as one
diffable object, and so `mondaybench evaluate --verdicts` does the scoring.
Nothing here assigns points.

THIS FILE STARTS EMPTY ON PURPOSE. The 16,000-token battery and the 315 verdicts
that labelled it are under `archive/budget-16000/`. Those labels are keyed by run
id, and this battery reuses the same run ids for different responses, so they
must not be copied across - every run here is read and labelled again.
"""

from __future__ import annotations

import json
from pathlib import Path

P, R, F = "PASS", "PARTIAL", "FAIL"

VERDICTS_001: dict[str, dict] = {
    "gemma4": dict(
        contoso_action=(R, "first item under High with the 11:00 deadline, but 'ready to renew pending a single legal clarification' states sequence, not jeopardy: nothing says what happens if 11:00 is missed"),
        umbrella_action=(F, "Umbrella never mentioned; the metrics file is not used at all"),
        churn_action=(P, "second High item, 'Daniel requires a clearer understanding of the churn drivers before the board meeting on Tuesday'"),
        analytics_action=(P, "Wednesday correct; no readiness item competing with today's critical work"),
        acme_resolved=(P, "'A rollback was completed, and Acme has confirmed stability'; 'The incident is resolved and documented' - 'documented' overstates Marcus's pending write-up"),
        release_wednesday=(P, "'pushed from Monday to Wednesday'"),
        contoso_blocked=(R, "'pending a single legal clarification' - identifies the question, misses the signature or approval consequence"),
        launch_email_julia=(P, "'Julia Santos has taken full ownership of the launch email; no action is needed from you'"),
        pricing_confidential=(P, "'still proposals. Do not share these numbers with customers'"),
        contoso_first=(P, "first item in the High band"),
        umbrella_and_churn_high=(R, "churn is a High item; Umbrella is entirely absent"),
        no_false_priorities=(P, "nothing resolved, delegated or explicitly non-urgent ranks above the churn analysis; Globex is Medium, below it"),
        umbrella_detected=(F, "anomaly missed"),
        umbrella_metrics=(F, "no supporting figures at all"),
        churn_numbers=(P, "3.1% to 4.4%"),
        umbrella_error_rate=(F, "no metrics reasoning of any kind"),
        umbrella_unknown_cause=(R, "invents no cause, but expresses no uncertainty either - Umbrella is absent"),
        friday_conversion_unknown=(R, "'currently unconfirmed if this was a data anomaly or a trend' - uncertainty noted, data gap not flagged"),
        churn_causality_unknown=(P, "'unclear if the Pied Piper and Hooli cancellations fully account for the jump to 4.4%'"),
        _noise={},
        _pen=[],
    ),
    "qwen3.6": dict(
        contoso_action=(P, "#1 URGENT, 'Failure to confirm by 11:00 pushes the EUR72k renewal signature to the next approval window'"),
        umbrella_action=(R, "under 'does not require action': 'a potential churn risk, though not explicitly flagged as urgent... Worth keeping in mind' - noticed, but not work for today"),
        churn_action=(P, "#2 HIGH, 'Begin analyzing the drivers of the 3.1% to 4.4% churn increase'; 'Daniel Foster needs this breakdown before the board meeting'"),
        analytics_action=(P, "Wednesday correct; the readiness task is pushed to LOW task-list cleanup, below the churn analysis"),
        acme_resolved=(P, "'Acme Incident Resolved'; 'Acme is stable. No further action needed from you unless Marcus requests input'"),
        release_wednesday=(P, "'moving the release from Monday to Wednesday'"),
        contoso_blocked=(P, "'ready to renew but Legal requires written confirmation'; 'Failure to confirm by 11:00 pushes the EUR72k renewal signature to the next approval window'"),
        launch_email_julia=(P, "'Julia Santos is taking full ownership of the launch email; you are no longer required to do this'"),
        pricing_confidential=(P, "'still a proposal', 'You cannot share the new Enterprise pricing tiers', 'Do not provide rough numbers' - the wrong end-date is taken as a penalty, not here"),
        contoso_first=(P, "#1, URGENT"),
        umbrella_and_churn_high=(R, "churn actionable at #2 HIGH; Umbrella filed under 'does not require action'"),
        no_false_priorities=(P, "Globex, Initech and the task cleanup all sit below the churn analysis; nothing resolved or delegated is elevated"),
        umbrella_detected=(P, "'Umbrella Metrics: Umbrella has high latency (1821ms p95) and negative usage change (-41%)'"),
        umbrella_metrics=(P, "1821ms p95 and -41% usage - two correct Umbrella signals"),
        churn_numbers=(P, "3.1% to 4.4%"),
        umbrella_error_rate=(F, "the 163 errors are never mentioned; no volume, no rate, no other customer's figures"),
        umbrella_unknown_cause=(R, "no cause asserted as established, but no uncertainty expressed either, and Umbrella is absent from section 4"),
        friday_conversion_unknown=(R, "the Friday conversion question is never raised: the claim is not repeated, but the gap is not flagged"),
        churn_causality_unknown=(P, "'it is unclear if these explain the full movement'; 'Determine if Pied Piper and Hooli are the sole causes'"),
        _noise={},
        _pen=[
            dict(
                type="MATERIAL_HALLUCINATION",
                materially_misleading=True,
                evidence="Strictly confidential until Wednesday's review / state that new tiers are under review and will be announced publicly soon",
                reason=(
                    "The source says pricing stays confidential until approved AND publicly "
                    "announced; Wednesday is only the next review, and no announcement is "
                    "scheduled at all. The error is written into the reply the user is told to "
                    "send Initech, so it leaves the company."
                ),
            )
        ],
    ),
    "glm5.2": dict(
        contoso_action=(P, "#1, 'deadline 11:00 today', 'EUR72k ARR at stake; if not confirmed today, renewal signature slips to their next approval window'"),
        umbrella_action=(R, "in today's list but last of six and in the lowest band, below the Acme close-out and Globex: strong substance ('may indicate a serious issue or at-risk account'), badly under-prioritized"),
        churn_action=(P, "#3, 'due Tuesday, board meeting', 'Pull the churn breakdown today'"),
        analytics_action=(P, "Wednesday correct; the readiness task appears only in section 4 as an open question"),
        acme_resolved=(P, "'Rachel Kim (Acme) confirmed recovery Thursday afternoon'; 'Incident is resolved'"),
        release_wednesday=(P, "'Analytics v2 launch moved to Wednesday'"),
        contoso_blocked=(P, "'if not confirmed today, renewal signature slips to their next approval window'"),
        launch_email_julia=(P, "'Julia owns the launch email; she confirmed you're not needed on that'"),
        pricing_confidential=(P, "'do not share numbers externally until finalized and announced'; '#2 Mark Benson (Initech) email - do NOT share pricing'"),
        contoso_first=(P, "#1, top of the priority list"),
        umbrella_and_churn_high=(R, "churn well placed at #3, but the Umbrella investigation is buried at #6"),
        no_false_priorities=(F, "two false priorities outrank the Umbrella investigation: the resolved Acme task close-out at #4 and Globex at #5, which the source says has no urgency"),
        umbrella_detected=(P, "'Company metrics show Umbrella with unusually high p95 latency... This stands out sharply vs. all other customers'"),
        umbrella_metrics=(P, "1,821 ms p95, 163 API errors, -41% usage change over 7 days"),
        churn_numbers=(P, "3.1% to 4.4%"),
        umbrella_error_rate=(R, "'1,821 ms vs. ~300 ms baseline' and 'p95 latency 6x higher than peers' quote the other customers' values, but no request volume and no error rate"),
        umbrella_unknown_cause=(P, "'Is this a product issue, a customer-side change, or a churn-risk signal?' - options offered, none asserted"),
        friday_conversion_unknown=(R, "'Is it noise or a real signal? Needs a look at the dashboard' - uncertainty flagged, but no statement that the provided data cannot settle it"),
        churn_causality_unknown=(P, "'Not yet clear whether these fully explain the movement'"),
        _noise={},
        _pen=[],
    ),
    "mimo-v2.5": dict(
        contoso_action=(P, "#1, 'deadline 11:00 today', 'Noah flagged this as the only blocker on a EUR72k ARR renewal'"),
        umbrella_action=(R, "only under 'Unclear': 'Worth investigating - is there an active issue, or was this just a quiet week?' - never enters today's list"),
        churn_action=(P, "third in today's list, 'needed before Tuesday's board meeting', 'You should start pulling data today'"),
        analytics_action=(P, "Wednesday correct; no readiness item competing with today's critical work"),
        acme_resolved=(P, "'Acme confirmed full recovery via email (Rachel Kim, Thursday 12:37)'; 'resolved and stable'"),
        release_wednesday=(P, "'moving the release from Monday to Wednesday'; 'releasing Wednesday, not Monday'"),
        contoso_blocked=(P, "'the only blocker on a EUR72k ARR renewal'"),
        launch_email_julia=(P, "'Julia confirmed she does not need anything from you on the launch email'"),
        pricing_confidential=(P, "'All numbers remain strictly confidential'; 'Do not share any pricing details'"),
        contoso_first=(P, "#1, marked urgent, at the top of the priority list"),
        umbrella_and_churn_high=(R, "churn actionable in today's list; Umbrella appears only under 'Unclear'"),
        no_false_priorities=(P, "Globex is last in the list, below the churn analysis, and the stale Acme and launch-email tasks are named as cleanup rather than priorities"),
        umbrella_detected=(P, "'Umbrella is not mentioned anywhere in Slack, emails, or meetings, but their metrics are concerning'"),
        umbrella_metrics=(P, "163 API errors, 1,821 ms p95, 41% drop in usage over 7 days"),
        churn_numbers=(P, "3.1% to 4.4%"),
        umbrella_error_rate=(R, "'roughly 6x higher than any other customer' positions Umbrella against the rest of the table, but on latency only - no request volume and no error rate"),
        umbrella_unknown_cause=(P, "'Nobody flagged this. Worth investigating - is there an active issue, or was this just a quiet week?'"),
        friday_conversion_unknown=(R, "'flagged as potentially noisy Friday traffic. Worth revisiting next week' - not repeated as fact, but no data-gap statement"),
        churn_causality_unknown=(P, "'Unclear if these fully explain the increase'; 'Are there other cancellations beyond Pied Piper and Hooli?'"),
        _noise={},
        _pen=[],
    ),
    "deepseek-v4-flash": dict(
        contoso_action=(P, "#1, 'urgent, 11:00 deadline', 'This is the only blocker on EUR72k ARR'"),
        umbrella_action=(P, "#2 in today's list, 'No one has mentioned it. Check whether this is a real incident or a data issue' - no cause claimed"),
        churn_action=(P, "#3, 'due before Tuesday's board meeting. Pull the breakdown Daniel asked for'"),
        analytics_action=(P, "Wednesday correct; readiness appears only in #6 housekeeping, 'should align with Wednesday, not Monday'"),
        acme_resolved=(P, "'Acme confirmed recovery'; 'Acme is stable and the customer confirmed recovery; no follow-up needed'"),
        release_wednesday=(P, "'Release moved from Monday to Wednesday'"),
        contoso_blocked=(P, "'Only blocker is legal's request for written confirmation... due 11:00 Monday'"),
        launch_email_julia=(P, "'Julia owns the launch email; no action needed from you'"),
        pricing_confidential=(P, "'still confidential and not finalized'; 'Do not share it'; 'confidential until approved and announced'"),
        contoso_first=(P, "#1 by priority"),
        umbrella_and_churn_high=(P, "Umbrella #2 and churn #3, immediately after Contoso"),
        no_false_priorities=(P, "Globex and the stale-task housekeeping are #5 and #6, below both critical items"),
        umbrella_detected=(P, "'Umbrella metrics anomaly'"),
        umbrella_metrics=(P, "163 API errors, 1,821ms p95, -41% usage change"),
        churn_numbers=(P, "3.1% to 4.4%"),
        umbrella_error_rate=(F, "the three figures are given in isolation: no request volume, no rate, no reference to any other customer"),
        umbrella_unknown_cause=(P, "'No one has mentioned it. Check whether this is a real incident or a data issue'; 'no context for the error/latency/usage spike'"),
        friday_conversion_unknown=(R, "'possibly noise, not yet investigated'; 'real or noise? Needs a quick check' - flagged, but no statement that the provided data cannot settle it"),
        churn_causality_unknown=(P, "'Whether the two known enterprise cancellations fully explain the churn increase - needs deeper analysis'"),
        _noise={},
        _pen=[],
    ),
    "qwen3.8-flash": dict(
        contoso_action=(P, "#1, 'due 11:00 today'; 'Contoso renewal is nearly done, but has a Monday 11:00 blocker', EUR72k ARR"),
        umbrella_action=(P, "#2 in today's list, 'Check whether this is a real customer issue, a data issue, or expected behavior' - no cause claimed"),
        churn_action=(P, "#4, 'Start the breakdown Daniel asked for' before Tuesday's board meeting"),
        analytics_action=(P, "Wednesday correct; the readiness question sits at #5 as task cleanup, below the churn analysis"),
        acme_resolved=(P, "'Acme P1 API incident resolved'; 'Acme is stable. No further customer action currently required'"),
        release_wednesday=(P, "'Analytics v2 release moved from Monday to Wednesday'"),
        contoso_blocked=(P, "'has a Monday 11:00 blocker'; 'the only current blocker is the legal/data retention confirmation'"),
        launch_email_julia=(P, "'Julia explicitly said you do not need to do anything on the launch email'"),
        pricing_confidential=(P, "'internal only and must not be shared until approved and announced'; 'Do not send proposed Enterprise pricing'"),
        contoso_first=(P, "#1 by priority"),
        umbrella_and_churn_high=(P, "Umbrella #2 and churn #4 of eight, both prominent actionable items after Contoso"),
        no_false_priorities=(R, "the resolved Acme incident close-out is #3, above the churn analysis"),
        umbrella_detected=(P, "'Umbrella metrics anomaly'"),
        umbrella_metrics=(P, "163 API errors, 1821ms p95 latency, -41% 7-day usage change"),
        churn_numbers=(P, "3.1% to 4.4%"),
        umbrella_error_rate=(F, "the three figures are given in isolation: no request volume, no rate, no reference to any other customer"),
        umbrella_unknown_cause=(P, "'no context was provided'; 'may indicate a real issue' framed as one of three possibilities"),
        friday_conversion_unknown=(R, "'The team suspected noisy traffic, but it has not been investigated' - flagged, but no statement that the provided data cannot settle it"),
        churn_causality_unknown=(P, "'Not established whether these fully explain the increase'"),
        _noise={},
        _pen=[],
    ),
    "glm5.3-flash": dict(
        contoso_action=(P, "#1, 'deadline 11:00 (~2h)', 'If it slips, the renewal moves to their next approval window - escalate early rather than miss silently'"),
        umbrella_action=(P, "#3, 'Investigate Umbrella... with zero context anywhere. Could be technical or a churn signal - check monitoring, support inbox, recent comms'"),
        churn_action=(P, "#2, 'needed before Tuesday's board... the board meets Tuesday, so effectively today'"),
        analytics_action=(P, "Wednesday correct; the readiness review appears only in section 4 as an open question"),
        acme_resolved=(P, "'Acme confirmed recovery by email'; 'Acme is fully recovered and grateful; only open thread is Marcus's incident doc (his task)'"),
        release_wednesday=(P, "'Analytics v2 slipped Mon to Wed'"),
        contoso_blocked=(P, "'If it slips, the renewal moves to their next approval window'"),
        launch_email_julia=(P, "'Julia owns the launch email - she explicitly said nothing is needed from you'"),
        pricing_confidential=(P, "'explicitly confidential until finalized and announced'; 'do not send pricing'"),
        contoso_first=(P, "#1 by priority"),
        umbrella_and_churn_high=(P, "churn #2 and Umbrella #3, immediately after Contoso"),
        no_false_priorities=(P, "the Globex reply and the stale-task closures are bundled last as 'quick wins', below every critical item"),
        umbrella_detected=(P, "'Umbrella anomaly (from metrics)... Worst on every metric, and not mentioned anywhere in Slack or email'"),
        umbrella_metrics=(P, "-41% over 7d, 1821ms p95, 163 API errors, plus the EUR54k ARR"),
        churn_numbers=(P, "3.1% to 4.4%"),
        umbrella_error_rate=(R, "'1821ms (vs ~300 for everyone else)' quotes the peers' latency and 'Stark/Contoso error rates negligible' reaches for the rate idea, but no request volume and no rate figure - the 163-against-94,217 reading is never made"),
        umbrella_unknown_cause=(P, "'zero context anywhere. Could be technical or a churn signal'; 'no information on cause at all'"),
        friday_conversion_unknown=(P, "'Julia thought conversion tanked Friday; no conversion data was shared' - names the gap in the provided material directly"),
        churn_causality_unknown=(P, "'whether the two known cancellations fully explain 3.1 to 4.4% - need the customer-level churn list'"),
        _noise={},
        _pen=[],
    ),
}

VERDICTS_002: dict[str, dict] = {
    "gemma4": dict(
        contoso_action=(R, "first item under High, 'Deadline: 11:00', 'Noah has flagged this as urgent' - but 'nearly complete, pending one technical clarification' states no consequence and the EUR72k is never mentioned"),
        umbrella_action=(F, "Umbrella never mentioned; the metrics file is not used at all"),
        churn_action=(P, "second High item, 'before the board meeting on Tuesday', 'determine if the Pied Piper/Hooli cases explain the full 1.3% jump'"),
        analytics_action=(P, "Wednesday correct; no readiness item competing with today's critical work"),
        acme_resolved=(P, "'service was stabilized by Thursday morning. Acme has confirmed they are back to normal'"),
        release_wednesday=(P, "'moved from Monday to Wednesday'"),
        contoso_blocked=(R, "'nearly complete, pending one technical clarification' - identifies the question (and miscalls it technical rather than legal), misses the signature consequence"),
        launch_email_julia=(P, "'Julia Santos has taken full ownership of the launch email; no action is needed from you'"),
        pricing_confidential=(P, "'still in the proposal stage. Do not share these numbers with customers'"),
        contoso_first=(P, "first item in the High band"),
        umbrella_and_churn_high=(R, "churn is a High item; Umbrella is entirely absent"),
        no_false_priorities=(P, "nothing resolved, delegated or explicitly non-urgent ranks above the churn analysis"),
        umbrella_detected=(F, "anomaly missed"),
        umbrella_metrics=(F, "no supporting figures at all"),
        churn_numbers=(P, "3.1% to 4.4%, and the 1.3% delta is computed correctly"),
        umbrella_error_rate=(F, "no metrics reasoning of any kind"),
        umbrella_unknown_cause=(R, "invents no cause, but expresses no uncertainty either - Umbrella is absent"),
        friday_conversion_unknown=(R, "'currently unconfirmed if this was a data anomaly or a genuine trend' - uncertainty noted, data gap not flagged"),
        churn_causality_unknown=(P, "'the full driver of the increase is still being investigated'; 'determine if the Pied Piper/Hooli cases explain the full 1.3% jump'"),
        _noise={},
        _pen=[],
    ),
    "qwen3.6": dict(
        contoso_action=(P, "#1 URGENT, 11:00, 'ready to renew but Legal requires written confirmation... the only blocker', 'to secure the EUR72k renewal'"),
        umbrella_action=(R, "under 'No Action Required': 'Umbrella has high latency (1821ms) and negative usage change (-41%); monitor for risk'"),
        churn_action=(P, "#3, 'Begin analyzing the 4.4% churn rate... Prepare findings for Daniel Foster', tied to the board meeting"),
        analytics_action=(P, "Wednesday correct; the readiness task is dropped in LOW cleanup (on the wrong premise that Julia owns it - she owns comms, the readiness review is still the user's)"),
        acme_resolved=(P, "'Acme Incident Resolved'; 'Acme has confirmed stability. No further customer action needed'"),
        release_wednesday=(P, "'moved from Monday to Wednesday'"),
        contoso_blocked=(P, "'ready to renew but Legal requires written confirmation by 11:00 AM Monday... the only blocker'"),
        launch_email_julia=(P, "'Julia Santos is taking full ownership of the launch email; you are no longer required to do this'"),
        pricing_confidential=(P, "'still a proposal', 'Do not share' - the wrong end-date is taken as a penalty, not here"),
        contoso_first=(P, "#1, URGENT"),
        umbrella_and_churn_high=(R, "churn is #3, below Globex; Umbrella is under 'No Action Required'"),
        no_false_priorities=(R, "Globex, which the source says has no urgency, is #2 High, above the churn analysis"),
        umbrella_detected=(P, "'Umbrella has high latency (1821ms) and negative usage change (-41%)'"),
        umbrella_metrics=(P, "1821ms p95 and -41% usage - two correct Umbrella signals"),
        churn_numbers=(P, "3.1% to 4.4%"),
        umbrella_error_rate=(F, "draws the incorrect comparison the criterion is built to catch: 'Contoso has high API errors (22)', when 22 errors on 821,334 requests is 0.003% and healthy; Umbrella's own errors and volume are never connected"),
        umbrella_unknown_cause=(R, "'monitor for risk' invents no cause but expresses no uncertainty either; Umbrella is absent from section 4"),
        friday_conversion_unknown=(R, "the Friday conversion question is never raised: the claim is not repeated, but the gap is not flagged"),
        churn_causality_unknown=(P, "'Known cancellations (Pied Piper, Hooli) may not fully explain this'"),
        _noise={},
        _pen=[
            dict(
                type="MATERIAL_HALLUCINATION",
                materially_misleading=True,
                evidence="Strictly confidential until Wednesday's review / state that pricing is under review and will be communicated officially soon",
                reason=(
                    "The source says pricing stays confidential until approved AND publicly "
                    "announced; Wednesday is only the next review. A reader could conclude the "
                    "tiers may be shared after Wednesday."
                ),
            )
        ],
    ),
    "glm5.2": dict(
        contoso_action=(P, "#1, 'deadline 11:00 today', 'EUR72k ARR at stake'"),
        umbrella_action=(F, "Umbrella is never mentioned; the CSV is opened only to check that Initech is healthy"),
        churn_action=(P, "#2, 'due Tuesday, board meeting', 'Pull the logo-level churn breakdown'"),
        analytics_action=(P, "Wednesday correct; the readiness task sits in #4 stale-task cleanup, below the churn analysis"),
        acme_resolved=(P, "'Acme confirmed recovery by ~10:00 Thursday'; 'Acme incident fully resolved'"),
        release_wednesday=(P, "'Analytics v2 release moved to Wednesday'"),
        contoso_blocked=(P, "'Legal has one open question on data retention... needs written confirmation by Monday 11:00'; 'EUR72k ARR at stake'"),
        launch_email_julia=(P, "'Julia now owns the launch email end-to-end'"),
        pricing_confidential=(P, "'All numbers remain confidential'; 'cannot share proposed Enterprise tiers; they're internal until approved and announced'"),
        contoso_first=(P, "#1 by priority"),
        umbrella_and_churn_high=(R, "churn is well placed at #2; Umbrella never appears at all"),
        no_false_priorities=(P, "the stale-task cleanup, Globex and the pricing review all sit below the churn analysis"),
        umbrella_detected=(F, "the anomaly is missed entirely - the only customer row it reads is Initech's, and it reads it correctly as healthy"),
        umbrella_metrics=(F, "no Umbrella figures"),
        churn_numbers=(P, "3.1% to 4.4%"),
        umbrella_error_rate=(F, "no Umbrella reasoning at all"),
        umbrella_unknown_cause=(R, "invents no cause, but expresses no uncertainty either - Umbrella is absent"),
        friday_conversion_unknown=(R, "'noise or real? Worth a quick look at today's numbers before escalating' - uncertainty flagged, no data-gap statement"),
        churn_causality_unknown=(P, "'Unclear if these fully explain the movement'"),
        _noise={},
        _pen=[],
    ),
    "mimo-v2.5": dict(
        contoso_action=(P, "#1, 'deadline 11:00 AM', 'the only blocker on a EUR72k renewal', 'She needs a response by 11:00 today or the renewal moves to their next approval window', 'Do this first'"),
        umbrella_action=(R, "in today's list but last of five and in the lowest band, below Globex: 'Worth determining whether this is known, expected, or an active issue'"),
        churn_action=(P, "#2, 'Daniel wants a breakdown before tomorrow's board meeting'"),
        analytics_action=(P, "Wednesday correct; release readiness raised only as an open question in section 4"),
        acme_resolved=(P, "'Acme confirmed stability... no lingering issues'; 'Acme incident is fully resolved'"),
        release_wednesday=(P, "'moving the release from Monday to Wednesday'; 'release is Wednesday, not today'"),
        contoso_blocked=(P, "'or the renewal moves to their next approval window'"),
        launch_email_julia=(P, "'Julia owns the launch email. No action needed from you on launch communications'"),
        pricing_confidential=(P, "'All numbers remain strictly confidential'; 'Do not share with anyone outside the team'"),
        contoso_first=(P, "#1, marked urgent, 'Do this first'"),
        umbrella_and_churn_high=(R, "churn well placed at #2, but the Umbrella investigation is last at #5, below Globex"),
        no_false_priorities=(R, "Globex, which the source says has no urgency, is #4, above the Umbrella investigation"),
        umbrella_detected=(P, "'Umbrella anomaly - investigate or flag'"),
        umbrella_metrics=(P, "163 API errors, 1,821ms p95, 41% usage decline over 7 days"),
        churn_numbers=(P, "3.1% to 4.4%"),
        umbrella_error_rate=(R, "'vs. ~280-340ms for other customers' quotes the peers' latency, and Stark is named with its 1.48M requests and called healthy - but the errors are never read against traffic: no rate, no Umbrella volume, and Stark's own 74 errors go unmentioned"),
        umbrella_unknown_cause=(P, "'Why is usage down 41% with elevated errors and latency? No one has flagged this - is it a known account issue, an active incident, or something else?'"),
        friday_conversion_unknown=(R, "'may have dipped but likely noise... worth revisiting this week' - not asserted as fact, but no data-gap statement"),
        churn_causality_unknown=(P, "'not yet clear whether these fully explain the increase'"),
        _noise={},
        _pen=[],
    ),
    "deepseek-v4-flash": dict(
        contoso_action=(P, "#1, 'before 11:00 today', 'the only thing blocking a EUR72k ARR renewal'"),
        umbrella_action=(R, "only under 'unclear': 'Umbrella metrics look anomalous... Needs an explanation' - never enters today's list"),
        churn_action=(P, "#4, 'Daniel wants a clearer breakdown before Tuesday's board meeting'"),
        analytics_action=(P, "Wednesday correct, and the readiness review is explicitly deferred to the Wednesday release rather than done today; its placement is charged under no_false_priorities, not twice"),
        acme_resolved=(P, "'Acme confirmed they've been stable since ~10am Thu'; 'the incident is closed from a customer perspective'"),
        release_wednesday=(P, "'the release was moved from Monday to Wednesday'"),
        contoso_blocked=(P, "'Noah flagged this as the only remaining blocker'; 'the only thing blocking a EUR72k ARR renewal'"),
        launch_email_julia=(P, "'Julia owns the launch email and communications'; 'fully owned by Julia - you don't need to draft it'"),
        pricing_confidential=(P, "'remain a proposal', 'keep the numbers internal', 'Do not share the proposed pricing', 'confidential until approved and announced'"),
        contoso_first=(P, "#1 by priority"),
        umbrella_and_churn_high=(R, "churn actionable at #4; Umbrella appears only under 'unclear'"),
        no_false_priorities=(R, "the #3 task-cleanup bundle, which closes the resolved Acme task, is ranked above the churn analysis"),
        umbrella_detected=(P, "'Umbrella metrics look anomalous'"),
        umbrella_metrics=(P, "163 API errors, 1,821ms p95, -41% 7-day usage change"),
        churn_numbers=(P, "3.1% to 4.4%"),
        umbrella_error_rate=(F, "the three figures are given in isolation: no request volume, no rate, no reference to any other customer"),
        umbrella_unknown_cause=(P, "'No one mentioned this in Slack or email. Needs an explanation'"),
        friday_conversion_unknown=(R, "'Not confirmed whether real or just noisy Friday traffic' - flagged, but no statement that the provided data cannot settle it"),
        churn_causality_unknown=(P, "'not confirmed whether they fully explain the increase'"),
        _noise={},
        _pen=[],
    ),
    "qwen3.8-flash": dict(
        contoso_action=(P, "#1, 'due 11:00 today', 'EUR72k ARR renewal is blocked on one legal confirmation, and the deadline is hard'; 'prepare for renewal to slip'"),
        umbrella_action=(P, "#2, 'check today', 'a severe combination of high API errors, very high latency, and a large usage drop, with no Slack/email context'; 'open a quick investigation today'"),
        churn_action=(P, "#4, 'start today', 'Leadership wants a clearer explanation before the board meeting, and the task is due Tuesday'"),
        analytics_action=(P, "Wednesday correct; the readiness item is #5 status-update work, below the churn analysis"),
        acme_resolved=(P, "'Acme confirmed stability by around 10:00 Thursday'; 'No further customer action currently required'"),
        release_wednesday=(P, "'Analytics v2 release moved from Monday to Wednesday'"),
        contoso_blocked=(P, "'EUR72k ARR renewal is blocked on one legal confirmation'; 'prepare for renewal to slip'"),
        launch_email_julia=(P, "'Julia Santos owns launch communications. You are explicitly not needed for the launch email'"),
        pricing_confidential=(P, "'must not be shared with customers until approved and announced'; 'Do not send the proposed tiers'"),
        contoso_first=(P, "#1 by priority"),
        umbrella_and_churn_high=(P, "Umbrella #2 and churn #4 of eight, both prominent actionable items after Contoso"),
        no_false_priorities=(R, "the resolved Acme incident close-out is #3, above the churn analysis"),
        umbrella_detected=(P, "'Umbrella metrics anomaly'; the metrics block singles Umbrella out from the other six customers"),
        umbrella_metrics=(P, "163 API errors, 1821ms p95 latency, -41% usage change"),
        churn_numbers=(P, "3.1% to 4.4%"),
        umbrella_error_rate=(R, "names Stark and its 74 API errors and correctly calls it healthy, and clears the other five rows - but the reason given is 'normal latency and +9% usage', never traffic: no request volume, no error rate, so the point of the comparison is missed"),
        umbrella_unknown_cause=(P, "'with no Slack/email context'; 'Is the Umbrella anomaly customer-specific, incident-related, or a data reporting issue?'"),
        friday_conversion_unknown=(R, "'may have been noisy traffic; check next week' - not asserted as fact, but no data-gap statement"),
        churn_causality_unknown=(P, "'Not yet established whether these fully explain the increase'"),
        _noise={},
        _pen=[],
    ),
    "glm5.3-flash": dict(
        contoso_action=(P, "#1, 'before 11:00 (~2h from now)'; 'Deadline: today 11:00, or signature slips to their next approval window'"),
        umbrella_action=(P, "#2, 'flag to engineering', 'Nobody has mentioned this anywhere. EUR54k ARR account possibly in trouble' - no cause claimed"),
        churn_action=(P, "#3, 'start today. Board meets tomorrow... realistically it needs to be done today'"),
        analytics_action=(P, "Wednesday correct; the readiness review is #6 task hygiene"),
        acme_resolved=(P, "'Acme (Rachel Kim) confirmed recovery in writing'; 'Acme is fully recovered and appreciative'"),
        release_wednesday=(P, "'Analytics v2 slipped Mon to Wed'"),
        contoso_blocked=(P, "'Deadline: today 11:00, or signature slips to their next approval window'"),
        launch_email_julia=(P, "'Julia owns all launch comms - she explicitly took the launch email off your plate'"),
        pricing_confidential=(P, "'explicitly confidential until approved and announced'; 'You cannot share the proposed tiers'"),
        contoso_first=(P, "#1 by priority"),
        umbrella_and_churn_high=(P, "Umbrella #2 and churn #3, immediately after Contoso"),
        no_false_priorities=(P, "Initech #4, Globex #5 and task hygiene #6 all sit below the critical items"),
        umbrella_detected=(P, "'Umbrella anomaly - flag to engineering'"),
        umbrella_metrics=(P, "-41% week-over-week, 1821 ms p95, 163 API errors, plus the EUR54k ARR"),
        churn_numbers=(P, "3.1% to 4.4%"),
        umbrella_error_rate=(R, "'1821 ms (~6x other customers)' positions Umbrella against the peers on latency, but no request volume and no error rate"),
        umbrella_unknown_cause=(P, "'Nobody has mentioned this anywhere'; 'no context anywhere on the usage drop - technical problem, churn risk, or expected?'"),
        friday_conversion_unknown=(R, "'Julia saw weak conversion Friday but suspects noisy traffic; no owner assigned' - flagged, but no statement that the provided data cannot settle it"),
        churn_causality_unknown=(P, "'may not fully explain the move'; 'if Pied Piper + Hooli explain the move or if something broader is happening'"),
        _noise={},
        _pen=[],
    ),
}

VERDICTS_003: dict[str, dict] = {
    "gemma4": dict(
        contoso_action=(P, "first item under High, 'Deadline: 11:00', 'This is critical for a EUR72k ARR renewal' - the renewal is put in jeopardy, not merely sequenced behind the question"),
        umbrella_action=(F, "Umbrella never mentioned; the metrics file is not used at all"),
        churn_action=(P, "second High item, 'before Tuesday's board meeting', 'determine if the Pied Piper/Hooli cases explain the full 1.3% jump'"),
        analytics_action=(P, "Wednesday correct; no readiness item competing with today's critical work"),
        acme_resolved=(P, "'A rollback was successful, and Acme has confirmed stability'"),
        release_wednesday=(P, "'pushed from Monday to Wednesday'"),
        contoso_blocked=(P, "'nearly complete, pending one legal clarification' plus 'This is critical for a EUR72k ARR renewal'"),
        launch_email_julia=(P, "'Julia Santos has taken full ownership of the launch email; no action is needed from you'"),
        pricing_confidential=(P, "'still proposals. Do not share these numbers with customers'"),
        contoso_first=(P, "first item in the High band"),
        umbrella_and_churn_high=(R, "churn is a High item; Umbrella is entirely absent"),
        no_false_priorities=(P, "nothing resolved, delegated or explicitly non-urgent ranks above the churn analysis"),
        umbrella_detected=(F, "anomaly missed"),
        umbrella_metrics=(F, "no supporting figures at all"),
        churn_numbers=(P, "3.1% to 4.4%, and the 1.3% delta is computed correctly"),
        umbrella_error_rate=(F, "no metrics reasoning of any kind"),
        umbrella_unknown_cause=(R, "invents no cause, but expresses no uncertainty either - Umbrella is absent"),
        friday_conversion_unknown=(R, "'unclear if this was a data anomaly or a genuine trend' - uncertainty noted, data gap not flagged"),
        churn_causality_unknown=(P, "'the full driver of the trend is still being investigated'; 'determine if the Pied Piper/Hooli cases explain the full 1.3% jump'"),
        _noise={},
        _pen=[],
    ),
    "qwen3.6": dict(
        contoso_action=(P, "#1 URGENT, 'Failure to confirm by 11:00 pushes the EUR72k ARR renewal to the next approval window'"),
        umbrella_action=(R, "under 'does not require action': 'Worth monitoring, but no immediate action required unless it impacts churn'"),
        churn_action=(P, "#3 'Due Tuesday', 'Begin analyzing the 3.1% to 4.4% churn increase', 'Daniel Foster needs this for the board meeting'"),
        analytics_action=(P, "Wednesday correct; the readiness task is dropped in LOW cleanup (on the wrong premise that Julia owns it - she owns comms, not the readiness review)"),
        acme_resolved=(P, "'Acme Incident Resolved'; 'Resolved. Marcus Webb is writing incident notes. No further customer action required'"),
        release_wednesday=(P, "'moved from Monday to Wednesday'"),
        contoso_blocked=(P, "'ready to renew but Legal requires written confirmation... the only blocker'; 'pushes the EUR72k ARR renewal to the next approval window'"),
        launch_email_julia=(P, "'Julia Santos is taking full ownership of the launch email'"),
        pricing_confidential=(P, "'strictly confidential'; 'Do not share any numbers with customers... until officially announced'; 'Do not send' - and unlike runs 001 and 002, the end-date is stated correctly"),
        contoso_first=(P, "#1, URGENT"),
        umbrella_and_churn_high=(R, "churn is #3 MEDIUM, below Globex; Umbrella carries no action"),
        no_false_priorities=(R, "Globex, which the source says has no urgency, is #2 HIGH, above the churn analysis"),
        umbrella_detected=(P, "'Umbrella shows significant negative usage change (-41%) and high latency (1821ms p95)'"),
        umbrella_metrics=(P, "-41% usage and 1821ms p95 - two correct Umbrella signals"),
        churn_numbers=(P, "3.1% to 4.4%"),
        umbrella_error_rate=(F, "the 163 errors are never mentioned; no volume, no rate, no other customer's figures"),
        umbrella_unknown_cause=(R, "invents no cause, but 'Worth monitoring, but no immediate action required' expresses no uncertainty and Umbrella is absent from section 4"),
        friday_conversion_unknown=(R, "the Friday conversion question is never raised: the claim is not repeated, but the gap is not flagged"),
        churn_causality_unknown=(P, "'Known cancellations (Pied Piper, Hooli) may not fully explain this'; 'unclear if there are other smaller cancellations contributing'"),
        _noise={},
        _pen=[],
    ),
    "glm5.2": dict(
        contoso_action=(P, "#1, 'deadline 11:00 today', 'Noah flagged this as the only blocker on a EUR72k ARR renewal'"),
        umbrella_action=(R, "only under 'Unclear': 'Worth investigating whether this is a known issue or an emerging one' - never enters today's list"),
        churn_action=(P, "#2, 'due Tuesday', 'before the board meeting', 'start pulling the churn data and segmenting by reason/customer today'"),
        analytics_action=(P, "Wednesday correct; the readiness task appears only in #5 stale-task cleanup (misassigned there to Julia/Sam - it is still the user's task)"),
        acme_resolved=(P, "'Acme confirmed stable by Thursday afternoon'; 'Acme incident is fully resolved and the customer is satisfied'"),
        release_wednesday=(P, "'Analytics v2 release moved to Wednesday'"),
        contoso_blocked=(P, "'Noah flagged this as the only blocker on a EUR72k ARR renewal'"),
        launch_email_julia=(P, "'Julia has taken full ownership of the launch email'"),
        pricing_confidential=(P, "'All numbers remain confidential'; 'proposed pricing is confidential and must not be shared'"),
        contoso_first=(P, "#1 by priority"),
        umbrella_and_churn_high=(R, "churn well placed at #2; Umbrella appears only under 'Unclear'"),
        no_false_priorities=(P, "Initech, Globex and the stale-task cleanup all sit below the churn analysis"),
        umbrella_detected=(P, "'Umbrella metrics look concerning and were not mentioned by anyone'"),
        umbrella_metrics=(P, "1,821ms p95, 163 API errors in 24h, usage down 41% over 7 days"),
        churn_numbers=(P, "3.1% to 4.4%"),
        umbrella_error_rate=(R, "'roughly 5-6x other customers' positions Umbrella against the rest of the table, but on latency only - no request volume and no error rate"),
        umbrella_unknown_cause=(P, "'No incident or account discussion found. Worth investigating whether this is a known issue or an emerging one'"),
        friday_conversion_unknown=(R, "'Whether the Friday conversion dip is real or noise... no one has followed up' - flagged, but no statement that the provided data cannot settle it"),
        churn_causality_unknown=(P, "'Unclear if these fully explain the increase'"),
        _noise={},
        _pen=[],
    ),
    "mimo-v2.5": dict(
        contoso_action=(P, "first row, Urgent, '11:00 today', 'EUR72k ARR renewal depends on this'"),
        umbrella_action=(R, "in the table but at Medium with the deadline 'This week', not today: 'It warrants investigation'"),
        churn_action=(R, "the board deadline is stated ('Need a fuller breakdown for Tuesday's board meeting'), but the analysis never enters the action table - it is filed under 'no action required from you' as 'Analysis task is yours for Tuesday'"),
        analytics_action=(P, "Wednesday correct; no readiness item competing with today's critical work"),
        acme_resolved=(P, "'Acme confirmed full recovery'; 'Acme incident is fully resolved'"),
        release_wednesday=(P, "'Release moved from Monday to Wednesday'; 'ships Wednesday, not Monday'"),
        contoso_blocked=(P, "'EUR72k ARR renewal depends on this'; 'The only blocker is the legal point above'"),
        launch_email_julia=(P, "'Julia is handling the launch email - no action required from you'"),
        pricing_confidential=(P, "'not finalized and is confidential - do not share any numbers'; 'Do not share externally under any circumstances'"),
        contoso_first=(P, "first row of the priority table, marked Urgent, and repeated as 'Your immediate action'"),
        umbrella_and_churn_high=(R, "both are covered in substance with correct figures and deadlines, but neither is an actionable item for today: Umbrella is Medium/'This week' and churn is not in the table at all"),
        no_false_priorities=(R, "Globex, which the source says has no urgency, is High/Today, above the Umbrella investigation, while the churn analysis is left out of the table"),
        umbrella_detected=(P, "'The metrics dashboard shows Umbrella at -41% usage change (7d), 163 API errors, and 1,821ms p95 latency'"),
        umbrella_metrics=(P, "-41% usage change, 163 API errors, 1,821ms p95"),
        churn_numbers=(P, "3.1% to 4.4%"),
        umbrella_error_rate=(F, "the three figures are given in isolation: no request volume, no rate, and no reference to any other customer"),
        umbrella_unknown_cause=(P, "'No one has raised this. Is this a known issue, a customer-side change, or something we're missing?'"),
        friday_conversion_unknown=(R, "'Real or noise? Julia flagged it but deferred to this week' - flagged, but no statement that the provided data cannot settle it"),
        churn_causality_unknown=(P, "'at least partially explanatory, but the full picture is not yet established'"),
        _noise={},
        _pen=[],
    ),
    "deepseek-v4-flash": dict(
        contoso_action=(P, "#1, 'before 11:00', 'Noah flagged this as the only blocker. Renewal is EUR72k ARR'"),
        umbrella_action=(R, "only under 'unclear': 'It may be a data issue or a real problem worth checking' - never enters today's list"),
        churn_action=(P, "#3, 'Daniel wants a clearer breakdown before Tuesday's board meeting. Start or assign the analysis'"),
        analytics_action=(P, "Wednesday correct; the readiness review is #4, below the churn analysis"),
        acme_resolved=(P, "'Acme confirmed they were stable and had processed the backlog'; 'no further customer follow-up needed'"),
        release_wednesday=(P, "'Analytics v2 release moved to Wednesday'"),
        contoso_blocked=(P, "'legal needs written confirmation... by 11:00 Monday. Noah flagged this as the only blocker'"),
        launch_email_julia=(P, "'Julia owns the launch email; no action needed from you there'"),
        pricing_confidential=(P, "'all proposed pricing is confidential until announced'; 'Do not share anything'"),
        contoso_first=(P, "#1 by priority"),
        umbrella_and_churn_high=(R, "churn actionable at #3; Umbrella appears only under 'unclear'"),
        no_false_priorities=(P, "the readiness review, Globex and the Acme close-out are #4, #5 and #6, all below the churn analysis"),
        umbrella_detected=(P, "'Umbrella metrics look concerning'"),
        umbrella_metrics=(P, "163 API errors, 1821ms p95, usage down 41% week-over-week"),
        churn_numbers=(P, "3.1% to 4.4%"),
        umbrella_error_rate=(F, "the three figures are given in isolation: no request volume, no rate, no reference to any other customer"),
        umbrella_unknown_cause=(P, "'No one mentioned this in Slack or email. It may be a data issue or a real problem worth checking'"),
        friday_conversion_unknown=(R, "'Could be noisy Friday traffic, but it hasn't been confirmed' - flagged, but no statement that the provided data cannot settle it"),
        churn_causality_unknown=(P, "'It's not established whether Pied Piper and Hooli fully explain the increase. More data is needed'"),
        _noise={},
        _pen=[],
    ),
    "qwen3.8-flash": dict(
        contoso_action=(P, "#1, 'deadline 11:00'; 'Contoso renewal is close but has a blocker'; 'notify Noah/Sarah immediately rather than guessing'"),
        umbrella_action=(P, "#2, 'Check whether anyone already knows about Umbrella's unusual metrics... If not, ask Laura/Marcus to investigate' - no cause claimed"),
        churn_action=(P, "#6, but 'Start the churn breakdown today' and tied to Tuesday's board meeting"),
        analytics_action=(P, "Wednesday correct, and the readiness task is questioned rather than performed ('Ask Sam whether it still needs you'); its placement is charged under no_false_priorities, not twice"),
        acme_resolved=(P, "'Acme P1 API incident was resolved'; 'The incident is resolved, and no further customer action is currently required'"),
        release_wednesday=(P, "'Analytics v2 release moved from Monday to Wednesday'"),
        contoso_blocked=(P, "'Contoso renewal is close but has a blocker'; 'The only stated blocker is the legal backup/deletion confirmation'"),
        launch_email_julia=(P, "'Julia explicitly took ownership of the launch email and said no action is needed from you'"),
        pricing_confidential=(P, "'reviewed but not finalized'; 'proposed numbers must not be shared'; 'Do not share proposed tiers with customers'"),
        contoso_first=(P, "#1 in the priority table"),
        umbrella_and_churn_high=(R, "Umbrella is well placed at #2, but the churn analysis is #6 of eight, below two task-cleanup items and the Initech reply"),
        no_false_priorities=(F, "two cleanup items outrank the churn analysis: the resolved Acme incident follow-up at #3 and the Analytics v2 task cleanup at #4, which closes the launch-email task Julia already owns"),
        umbrella_detected=(P, "'Umbrella metrics outlier'"),
        umbrella_metrics=(P, "163 API errors, 1,821 ms p95 latency, -41% usage"),
        churn_numbers=(P, "3.1% to 4.4%"),
        umbrella_error_rate=(F, "the three figures are given in isolation: no request volume, no rate, no reference to any other customer"),
        umbrella_unknown_cause=(P, "'no Slack/email context confirming whether this is a known issue or a new problem'"),
        friday_conversion_unknown=(R, "the Friday conversion question is never raised: the claim is not repeated, but the gap is not flagged"),
        churn_causality_unknown=(P, "'it is not confirmed whether they fully explain the increase'"),
        _noise={},
        _pen=[],
    ),
    "glm5.3-flash": dict(
        contoso_action=(P, "header banner 'Most urgent: Contoso legal confirmation due by 11:00 today' and #1: 'missing the deadline pushes signature to their next approval window'"),
        umbrella_action=(P, "#3, 'Umbrella anomaly - on nobody's radar... Investigate or assign', no cause claimed"),
        churn_action=(P, "#4, 'due tomorrow (board meeting Tuesday)'"),
        analytics_action=(P, "Wednesday correct; the readiness review appears only in section 4 as an open question"),
        acme_resolved=(P, "'Acme API incident (Thursday, resolved)'; 'Acme fully recovered and thanked the team; error rates at baseline since Thursday'"),
        release_wednesday=(P, "'Analytics v2 release moved Monday to Wednesday'"),
        contoso_blocked=(P, "'missing the deadline pushes signature to their next approval window'"),
        launch_email_julia=(P, "'Julia owns launch comms - she explicitly took the launch email off your plate'"),
        pricing_confidential=(P, "'numbers explicitly confidential until announced'; 'decline/defer politely, share nothing'"),
        contoso_first=(P, "#1 and the sole item in the header banner"),
        umbrella_and_churn_high=(P, "Umbrella #3 and churn #4 of six, both with concrete actions"),
        no_false_priorities=(P, "Globex and the stale-task closures are #5 and #6, below every critical item"),
        umbrella_detected=(P, "'Umbrella anomaly - on nobody's radar'"),
        umbrella_metrics=(P, "-41% in 7 days, 163 API errors, 1821ms p95, plus the EUR54k ARR"),
        churn_numbers=(P, "3.1% to 4.4%"),
        umbrella_error_rate=(R, "'1821ms (vs. ~300ms for everyone else)' quotes the peers' latency, but no request volume and no error rate"),
        umbrella_unknown_cause=(P, "'nothing anywhere explains the usage drop or degraded performance. Is anyone already looking at it?'"),
        friday_conversion_unknown=(P, "'Julia's Friday observation - real or Friday noise? No data provided' - names the gap in the provided material directly; also tagged 'unverified' in the recap"),
        churn_causality_unknown=(P, "'may not fully explain the increase'; 'do the two known cancellations fully explain the increase, or is something broader happening?'"),
        _noise={},
        _pen=[],
    ),
}

# run number -> the labels recorded for that run, by model.
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
    if not models:
        print("  no verdicts recorded yet - nothing written")
        return
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
