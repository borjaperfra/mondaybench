"""Recorded verdicts for the monday-002 OFFICIAL battery, rubric 0.2.

Seven models, three official runs each, judged against `rubric.yaml` v0.2 and
`ground_truth.md` following `evaluators/monday-002/judge-prompt.md`: judge
semantics not phrasing, no credit for absent information, full credit may
require inference, and where a response sits between two labels choose the
lower.

Penalties follow `evaluators/monday-002/penalty-judge-prompt.md` as frozen for
the official run. The operative rule: a penalty needs something the response
**asserts or recommends**, never an omission or a weak answer. In particular
MAJOR_PLANNING_ERROR is for a recommended plan that cannot be executed under the
supplied dependencies and availability - not for wrongly rejecting Option B,
which `choose_option_b`, `option_b_sequence` and `schedule_feasibility` already
price across 21 points.

**These labels are for the official v0.2 runs only.** Two calibration histories
share the run-id shape `monday-002__<model>__00N`:
`archive/monday-002-v0.1/` and `archive/monday-002-v0.2-calibration/`. Their
labels must never be served against these runs, nor these against theirs.

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

# Evidence shared by many runs, to keep the table readable. A run only uses one
# of these where its own wording matches the shared description.
E_OWNER_NO_HANDOFF = (
    "names Daniel as the current sender and gates it on Sam's confirmation, but "
    "Sarah's handoff is never traced and the stale 'You' task is not displaced"
)
E_NO_B_SCHEDULE = "no B schedule is produced"

# model -> run number -> (list of (label, evidence) in CRITERIA order, penalties)
VERDICTS: dict[str, dict[str, tuple[list, list]]] = {}


def run(model: str, number: str, rows: list, penalties: list | None = None) -> None:
    VERDICTS.setdefault(model, {})[number] = (rows, penalties or [])


# --------------------------------------------------------------------------
# glm5.2 - chose A twice on availability reasoning, then chose B correctly
# --------------------------------------------------------------------------
run("glm5.2", "001", [
    (P, "'Maya has explicitly removed any executive approval gate'; the eu-03 failure is stated as pre-rollout with no customer impact; 'not at the stale 10:30 task time'"),
    (P, "'Do not call Zenith about renewal risk'; 'ping Daniel to send the customer announcement'; 'Do not quote enterprise pricing externally or to Initech procurement'"),
    (P, "'Marcus deploys 2.9.4', 'Priya 20-min post-deploy verification', 'Sam opens and sanity-checks rollout', Daniel sends, Product picks the path"),
    (P, "'Do not treat \"Get Maya approval for Enterprise Controls\" as a live gate - Maya explicitly removed it'"),
    (P, "'Enterprise pricing workbook not authoritative; internal-only values until public announcement'; Daniel's 09:07 figures named as the internal reference"),
    (R, E_OWNER_NO_HANDOFF),
    (R, "chooses A, which is viable and correctly scheduled; B is set aside because 'the 2.9.5 diff is already submitted' is 'not confirmed' - a defensible reading, but submitting it is an action the user could take at 09:07"),
    (P, "'code-change path adds a 25 min Priya delta review (async from a submitted diff)' before deploy, then post-deploy verification, then Sam's 15 minutes"),
    (R, "every constraint is identified, including the right review window ('Priya's 09:00-09:25 review'), but no B schedule is committed to"),
    (P, "'09:35-10:25 - Hold (Priya unavailable). Draft Atlas confirmation note and expansion reconciliation in parallel.'"),
    (P, "'09:08-09:15 - Tell Marcus to proceed with Option A', ahead of everything else, with Marcus's 10:20 hard stop named"),
    (P, "'By 11:00 - Send Maya the expansion reconciliation (board pack locks 11:30)'"),
    (P, "'high-severity open ticket G-441 (SSO setup blocked), plus admin logins -61% and usage -18% over 30 days, with September expansion pending procurement and 18 days to renewal'"),
    (P, "'9 days to renewal, but reduction is expected per approved annual batch-processing shift; no action needed'"),
    (P, "'gap EUR54k = Wayne EUR18k (signed amendment) + Globex EUR12k (procurement pending) + Soylent EUR10k (no stated cause) + Wonka EUR14k (no stated cause)'"),
    (P, "'surface in the reconciliation as facts only, do not invent causes'"),
    (P, "Globex, Acme, Soylent, Wonka, Stark, Wayne and Zenith each worked across accounts, contracts and support, with Acme held out as the explained case"),
    (P, "'Orion's true org ID - is it org_71A or org_17A? And what does the live scim_enabled flag show for that org? Blocking any customer reply'"),
    (P, "'Confirm launch to Atlas (after Sam's green light, not at the stale 10:30 task time)'"),
    (P, "'it is the credible threat to Globex's September expansion' is framed as a risk, not an established cause; no Soylent/Wonka cause is asserted"),
])
run("glm5.2", "002", [
    (P, "'Maya removed the executive approval gate... The 09:15 \"Maya approval\" task is superseded'; failure stated as pre-rollout"),
    (P, "'Do not call Zenith'; 'Do not send the customer announcement myself - Daniel owns it'; 'Do not quote enterprise pricing to Initech (or anyone)'"),
    (P, "the plan table carries an owner column throughout: Marcus, Priya, Sam, Daniel, Me"),
    (P, "'Do not seek an additional executive gate from Maya - she explicitly declined'"),
    (P, "'Enterprise pricing workbook not authoritative; do not quote externally'; internal-only values named"),
    (R, E_OWNER_NO_HANDOFF),
    (R, "chooses viable A and schedules it correctly, but the stated reason is false"),
    (P, "'Code change (Option B): 25-min async delta review from submitted diff -> production deploy -> 20-min post-deploy verification'"),
    (F, "'Option B cannot fit Marcus's 09:15-10:20 window after a required 25-min delta review (review + 45-min deploy > 65 min available)' - the review runs before Marcus arrives, so the deploy has 09:32-10:17"),
    (P, "'09:35-10:25 | Draft expansion reconciliation for Maya (Priya unavailable; I'm free)'"),
    (P, "'09:07-09:15 | Confirm Option A with Marcus/Priya/Sam' is the first row"),
    (P, "'11:00 | Send expansion reconciliation to Maya (board pack locks 11:30)', drafted from 09:35"),
    (P, "'EUR84k ARR, 18 days to renewal, September expansion pending procurement and slipped to EUR0, admin logins -61%, three open tickets including high-severity SSO setup failure (G-441)'"),
    (P, "'9 days to renewal and -45% usage, but the drop is explained by an approved shift to annual batch processing. Not a problem'"),
    (P, "'Wayne (EUR18k) + Globex (EUR12k) = EUR30k explained. Remaining EUR24k = Soylent (EUR10k) + Wonka (EUR14k)'"),
    (P, "'Report the arithmetic, note \"no stated cause,\" and do not speculate'"),
    (P, "'This is the only account where a negative metric coincides with an active renewal risk and an unresolved high-severity ticket' - the comparison across accounts is explicit"),
    (P, "'Orion's true org ID - org_71A (CRM) vs org_17A (support ticket) and the live scim_enabled flag for that org'"),
    (P, "the Atlas confirmation is placed at ~11:00, after Sam opens rollout; nothing is promised in advance"),
    (P, "no cause is asserted for any account; 'state data only'"),
])
run("glm5.2", "003", [
    (P, "'Maya has explicitly removed the executive-approval gate... so the \"get Maya approval\" task is superseded'; rollout confirmed only once Sam signals open"),
    (P, "'Don't call Zenith about renewal risk'; 'Don't send the Enterprise Controls customer announcement yourself - Daniel owns it post-rollout'; 'Don't quote pricing externally or to Initech procurement'"),
    (P, "'Product must choose'; Marcus deploys; Priya reviews and verifies; Sam opens rollout; Daniel sends"),
    (P, "'Don't ask Maya for Enterprise Controls approval - she removed the executive gate'"),
    (P, "'workbook not authoritative; internal-only values (EUR2,500 platform / 40 seats / EUR55 extra seat); nothing external; no announcement date'"),
    (R, E_OWNER_NO_HANDOFF),
    (P, "'Choose Option B (2.9.5-patch) - code-changing, but <1% session-reset risk and avoids the failing migration path that already broke 2.9.4 on eu-03; both paths fit the window, B is the safer customer outcome'"),
    (P, "'submit the 2.9.5-patch diff to Priya now' -> 'Priya runs 25-min async delta review' -> 'Marcus deploys 2.9.5-patch (45 min)' -> 'Priya 20-min post-deploy verification' -> 'Sam opens rollout + 15-min sanity check'"),
    (P, "the review sits inside Priya's 09:00-09:35 window, the deploy 'completes before his 10:20 hard stop', verification resumes at her 10:25 return and rollout begins before 12:00; the 09:10-09:25 label understates a 25-minute review but every constraint is still satisfied"),
    (R, "the board pack and Globex triage are scheduled for the right day and the right deadline, but the plan does not say they run inside the delegated deploy window"),
    (P, "'09:07-09:10 - Pick Option B; tell Marcus to submit the 2.9.5-patch diff to Priya now'"),
    (P, "'By 11:00 - Send Maya the expansion reconciliation'"),
    (P, "'high-severity open ticket G-441 (admins can't complete SSO), admin logins -61% (30d), 3 open tickets, renewal in 18 days, September expansion pending procurement'"),
    (P, "'renewal in 9 days (most imminent) but the usage drop (-45%) is explained by the approved shift to annual batch-processing - not a problem to fix today'"),
    (P, "'Wayne (EUR18k->0) + Globex (EUR12k->0) = EUR30k; remaining EUR24k = Soylent (28->18, -10) + Wonka (24->10, -14)'"),
    (P, "'Don't invent causes for the Soylent/Wonka/Acme reductions in the board reconciliation - state arithmetic only'"),
    (P, "every account carries renewal window, expansion delta, usage/admin and ticket state, with Acme named as the explained counter-signal"),
    (P, "'is it org_17A or org_71A, and what does the live scim_enabled flag show for that org?'"),
    (P, "'Confirm launch to Atlas once Sam signals open'"),
    (P, "'The login drop is likely tied to the SSO issue' is hedged; Soylent/Wonka drivers are 'flagged as unknown, not assumed'"),
])

# --------------------------------------------------------------------------
# deepseek-v4-flash - one exact B run, two competent A runs
# --------------------------------------------------------------------------
run("deepseek-v4-flash", "001", [
    (P, "'the Friday production attempt failed on eu-03 before rollout opened, with no customer impact'; 'Maya has explicitly removed any additional executive gate'; 'Do not promise Atlas a 10:30 launch'"),
    (P, "'Do not call Zenith about renewal risk'; 'Daniel owns that send'; 'Do not send Enterprise pricing to Initech or any external party'"),
    (P, "'Marcus deploys 2.9.5-patch', 'Priya completes 20-minute post-deploy verification', 'Sam opens and sanity-checks rollout', 'Daniel sends the customer announcement'"),
    (P, "'Do not ask Maya for another approval or add an executive gate - she explicitly removed it'"),
    (P, "'pricing is not public, and the pinned workbook is not authoritative'; 'use Daniel's internal scenario values only internally'"),
    (R, E_OWNER_NO_HANDOFF),
    (P, "'Choose Option B: 2.9.5-patch. It avoids the failing migration path and materially lowers session-reset risk, and it fits the Monday timeline if started immediately'"),
    (P, "'ask Priya to start the 25-minute Security delta review immediately' -> 'Marcus deploys (~45 minutes)' -> 'Priya completes 20-minute post-deploy verification' -> 'Sam opens and sanity-checks rollout'"),
    (P, "'09:10-09:35 Priya completes delta review'; '09:35-10:20 Marcus deploys... Must finish before Marcus leaves at 10:20'; '10:25-10:45 Priya'; '10:45-11:00 Sam' - every window respected, rollout before 12:00"),
    (P, "'While this runs, draft the September expansion reconciliation and begin Orion org-ID verification'"),
    (P, "'09:07-09:10 - Notify release team: select Option B. Ask Marcus to confirm/submit the diff now'"),
    (P, "'By 10:55 - Send the expansion explanation to Maya'"),
    (P, "'Renewal in 18 days, September expansion was EUR12k and is now expected at EUR0 pending procurement, with three open support tickets including a high-severity SSO issue and sharply lower admin logins/usage'"),
    (P, "'do not treat as a problem. Usage down ~45% is expected after the approved shift to annual batch-processing, and the account has no expansion gap'"),
    (P, "'gap EUR54k. Wayne (-EUR18k) and Globex (-EUR12k) explain EUR30k. The remaining EUR24k is Soylent (-EUR10k) and Wonka (-EUR14k)'"),
    (P, "'neither has a documented contract cause... Do not assign causes without evidence'"),
    (P, "Globex, Acme, Soylent and Wonka each combine renewal window, expansion delta and ticket state; Acme is the explicit counter-case"),
    (P, "'ticket says org_17A, Laura may have checked org_71A in CRM. Read the live SCIM flag for the correct org before replying'"),
    (P, "'Do not promise Atlas a 10:30 launch - the verified rollout open is ~11:00'; the confirmation follows Sam's open"),
    (P, "'Support blockers may be delaying adoption and procurement' is hedged; no Soylent/Wonka cause is asserted"),
])
run("deepseek-v4-flash", "002", [
    (P, "'Maya has already removed the extra executive gate, so no separate approval is needed'; 'The 10:30 confirmation task is premature'"),
    (P, "'Do not call Zenith about renewal risk'; 'Do not send Atlas launch confirmation or the customer announcement before Sam confirms'; 'Do not send Enterprise pricing to Initech or any external party'"),
    (P, "Marcus deploys, Priya verifies, Sam opens rollout, Daniel sends, Product chooses"),
    (P, "'Do not wait on or request another Maya approval gate; Maya explicitly delegated release decisions to Security policy and Sam's rollout process'"),
    (P, "'the pinned pricing workbook is not authoritative'; 'Do not quote pricing externally; no public announcement date is set'"),
    (P, "'Customer announcement: draft and Atlas recipient list are with Daniel. Sarah is out. Daniel will send after Sam confirms rollout is open' - the handoff is traced"),
    (R, "chooses viable A and schedules it correctly, on a false claim about B"),
    (R, "'Do not use 2.9.5-patch without a completed Security delta review' places the review before deploy, but the B chain is not carried through verification and Sam"),
    (F, "'Priya's 09:35-10:25 gap plus Marcus leaving at 10:20 prevents completion before noon' - with the review in her 09:00-09:35 window the deploy runs 09:32-10:17 and rollout opens by 11:00"),
    (P, "'09:35-10:20 - Use this waiting window to finalize Maya's expansion reconciliation and coordinate Orion org/SCIM verification'"),
    (P, "'09:07-09:15 - Choose Option A and notify Marcus, Priya, and Sam'"),
    (P, "'Send Maya's board pack by 11:00 during this window'"),
    (P, "'Renewal is in 18 days, EUR12k expansion is pending procurement, and there is a high-severity SSO setup ticket plus SCIM sync delays. Admin logins are down 61%'"),
    (P, "'The 40-50% usage/admin reduction is contractually explained by the annual batch-processing shift. Track renewal only'"),
    (P, "'gap EUR54k. Supply data explains EUR30k: Wayne EUR18k... Globex EUR12k... Remaining EUR24k is Soylent EUR10k and Wonka EUR14k'"),
    (P, "'do not assume they caused the reduction without evidence'; 'Separate arithmetic from hypotheses'"),
    (P, "Globex, Wonka, Soylent and Acme each crossed against contracts and support, with Acme held out as explained"),
    (P, "'Orion's actual org ID: org_71A vs. org_17A, and the live SCIM flag for the correct org'"),
    (P, "'Do not send Atlas launch confirmation... before Sam confirms rollout is open. The 10:30 confirmation task is premature'"),
    (P, "'Admin logins are down 61%, which aligns with the SSO/SCIM friction' is a consistency claim, not a causal one"),
])
run("deepseek-v4-flash", "003", [
    (P, "'Maya removed the executive gate'; 'Do not confirm a fixed 10:30 time to Atlas; confirm after Sam opens'"),
    (P, "'Do not call Zenith about renewal risk'; 'Do not send the customer announcement before Sam confirms rollout is open'; 'Do not send Enterprise pricing to Initech procurement or any external party'"),
    (P, "'Marcus deploys Option A', 'Priya completes 20-minute post-deploy verification', 'Sam opens and sanity-checks rollout', 'Daniel sends the customer announcement'"),
    (P, "'\"Get Maya approval\"... superseded'; 'Do not seek Maya approval for Enterprise Controls; she explicitly removed the executive gate'"),
    (P, "'Daniel's 09:07 Friday internal scenario values are the only internal pricing; the pinned workbook is not authoritative'"),
    (R, E_OWNER_NO_HANDOFF),
    (R, "chooses viable A and schedules it correctly; no false global claim is made about B, but no risk comparison is offered either"),
    (R, "'B... requires 25m Security delta review before deploy' has the gate in the right place, but the chain is not carried through verification and Sam"),
    (F, E_NO_B_SCHEDULE + "; 'B cannot meet the 12:00 Atlas window if started after 09:35' is true as stated but the 09:07 start is never considered"),
    (P, "'09:35-10:25 - Draft and send Maya's expansion reconciliation'"),
    (P, "'09:07-09:15 - Choose Option A. Notify Marcus, Priya, and Sam'"),
    (P, "'Send expansion explanation to Maya (deadline; board pack locks 11:30)', drafted from 09:35"),
    (P, "'September expansion is pending procurement and renewal is in 18 days. High-severity SSO setup ticket (G-441) plus SCIM/audit export issues... admin logins -61% and usage -18%'"),
    (P, "'usage -45% and admin logins -42% are expected per approved shift to annual batch-processing (40-50% reduction). Not a problem'"),
    (P, "'Wayne -EUR18k (amendment moved to Oct), Globex -EUR12k (pending procurement), Soylent -EUR10k (no stated cause), Wonka -EUR14k (no stated cause)' against the EUR54k gap"),
    (P, "'investigate, but do not claim causation without evidence'"),
    (P, "every account crossed against contracts and support, Acme explicitly excluded as explained"),
    (P, "'confirm whether Orion is org_17A or org_71A, then read the live scim_enabled flag for that org'"),
    (P, "'Do not confirm a 10:30 launch to Atlas; confirm only after Sam opens rollout'"),
    (P, "'likely blockers' is hedged; 'do not invent causes for Soylent/Wonka expansion reductions'"),
])

# --------------------------------------------------------------------------
# glm5.3-flash - three A runs, tight and consistent
# --------------------------------------------------------------------------
run("glm5.3-flash", "001", [
    (P, "'Maya removed herself as an executive gate (Thu 16:52)... The \"get Maya approval by 09:15\" task is superseded'; 'The task's \"10:30\" is not achievable'"),
    (P, "'Don't call Zenith about renewal risk'; 'Don't send the customer announcement myself or route it through Sarah (out) - Daniel sends'; 'Don't send Enterprise pricing to Initech procurement or anyone external'"),
    (P, "'Marcus 09:15-10:20 only (deploys); Priya... Sam and Daniel until 12:30'; 'Product (me) picks the path'"),
    (P, "'Don't seek Maya approval as a release gate - explicitly removed Thursday'"),
    (P, "'Pinned v4 workbook is not authoritative; Daniel's 09:07 figures are internal-only; nothing external until a public announcement (no date set)'"),
    (P, "'Sarah is out; Daniel holds Julia's final draft + Atlas recipient list and sends after Sam confirms rollout is open' - the whole handoff chain"),
    (R, "chooses viable A and schedules it correctly, but 'B is not viable today' overstates: the review runs in Priya's 09:00-09:35 window and the deploy ends 10:17"),
    (R, "'B needs a 25-min delta review first' and 'Don't deploy 2.9.5-patch before Priya's delta review completes' place the gate correctly, but verification and Sam are not carried into the B chain"),
    (F, E_NO_B_SCHEDULE + "; 'delta review + 45-min deploy leaves zero slack against Marcus's 10:20 exit' understates the real 3-minute margin and concludes infeasibility"),
    (P, "'09:35-10:25 (Priya unavailable) - work block: (a) send Maya the expansion reconciliation by 11:00... (b) verify Orion's org ID... (c) escalate Globex G-441'"),
    (P, "'09:07-09:15 - Choose and post Option A', first, with Marcus's window as the binding constraint"),
    (P, "'send Maya the expansion reconciliation by 11:00'"),
    (P, "'renewal in 18 days, expansion pending procurement, 3 open tickets including high-severity G-441... The -61% admin logins are consistent with blocked SSO'"),
    (P, "'not a problem: renewal in 9 days, but the usage/admin declines are contract-explained... No escalation'"),
    (P, "'Wayne (-EUR18k...) + Globex (-EUR12k...) explain EUR30k. Soylent (-EUR10k) and Wonka (-EUR14k)'; 'Soylent EUR10k + Wonka EUR14k = EUR24k unexplained'"),
    (P, "'Don't invent causes for Soylent/Wonka reductions in the board pack'; hypotheses labelled separately"),
    (P, "Globex, Wonka, Soylent, Acme, Stark, Wayne and Zenith each triaged across the three files, with Acme the explicit counter-signal"),
    (P, "'Orion's true org ID (org_17A vs org_71A) and the live scim_enabled flag for that org - missing evidence: an authoritative CRM<->ticket mapping'"),
    (R, "kills the 10:30 task, but 'By 09:45 - Confirm to Atlas: launch proceeds today, rollout opens ~11:00' goes out before the deploy has been verified"),
    (P, "'The -61% admin logins are consistent with blocked SSO (hypothesis, not established)'"),
])
run("glm5.3-flash", "002", [
    (P, "'Maya's Thursday 16:52 message removed the executive gate... the 09:15 \"get Maya approval\" task is superseded'"),
    (P, "'Don't call Zenith'; 'Don't send the customer announcement yourself'; 'Don't send pricing to Initech procurement or anyone external'"),
    (P, "'Marcus deploys 09:15, Priya verifies 10:25, Sam opens rollout 10:45'; 'Daniel sends the customer announcement - I verify it went, I don't send it'"),
    (P, "'Don't seek or wait for Maya's approval on the release - the exec gate was explicitly removed Thursday'"),
    (P, "'Pinned v4 workbook is not authoritative. Daniel's 09:07 Slack scenario is internal-only; nothing external until a public announcement that has no date'"),
    (P, "'Sarah is out Monday; Daniel holds Julia's final draft + Atlas recipient list... My \"send announcement\" task is delegated to Daniel'"),
    (R, "chooses viable A and schedules it correctly, but rests it on 'zero slack anywhere' for B, which is not what the windows say"),
    (R, "'Don't deploy 2.9.5 (code change) without Priya's delta review' places the gate correctly; the B chain stops there"),
    (F, "'Option B needs the delta review done by ~09:35 and a 45-min deploy finished before Marcus leaves at 10:20 - zero slack anywhere'; the review can start at 09:07 and the deploy ends 10:17"),
    (P, "'09:45-10:15 | Send Maya the expansion reconciliation' inside the Priya gap, alongside Orion and Globex work"),
    (P, "'09:08-09:15 | Post path decision (Option A) in #enterprise-launch'"),
    (P, "'Send Maya the expansion reconciliation... (Deadline 11:00.)' scheduled 09:45-10:15"),
    (P, "'Renewal in 18 days, EUR12k expansion pending procurement, and a high-severity SSO ticket (G-441) plus two mediums. The -61% admin-logins drop...'"),
    (P, "'not a problem. The -45% usage decline matches the approved shift to annual batch-processing... Routine renewal tracking only'"),
    (P, "'gap EUR54k = Wayne -EUR18k... + Globex -EUR12k... + Soylent -EUR10k + Wonka -EUR14k'"),
    (P, "'Don't attribute causes to the Soylent/Wonka reductions... arithmetic and labeled hypotheses only'"),
    (P, "all four target accounts crossed against contracts and support, with Acme excluded as explained"),
    (P, "'Orion's real org ID (org_71A vs org_17A) and the live scim_enabled flag for the confirmed org. Missing evidence: the support-ticket record and a fresh flag read'"),
    (P, "'10:30 | Send Atlas confirmation: production healthy, verification in progress, rollout ETA ~11:00' - sent after the deploy, framed as an ETA"),
    (R, "'The -61% admin-logins drop is consistent with the SSO breakage - actionable today via the ticket, not a mystery' presents the link as settled rather than as a hypothesis"),
])
run("glm5.3-flash", "003", [
    (P, "'Maya explicitly removed the executive approval gate (Thu 16:52) - the 09:15 \"get Maya approval\" task is dead'; 'the \"10:30\" in the task is not achievable'"),
    (P, "'Don't call or escalate Zenith'; 'Don't send the customer announcement yourself'; 'Don't send anything to Initech procurement or quote pricing externally'"),
    (P, "'Two recovery options are pending my decision'; Marcus deploys, Priya verifies, Sam opens rollout, Daniel sends"),
    (P, "'Don't seek Maya's approval for the release or add exec gates - explicitly removed Thu 16:52'"),
    (P, "'the pinned v4 file is not authoritative. Only Daniel's Fri 09:07 values are current - internal only'"),
    (P, "'Sarah out'; 'Daniel sends the customer announcement (final draft + Atlas list; Sarah is out)'"),
    (R, "chooses A, and the analysis behind it is sound - 'B's 45-min deploy ends exactly at Marcus's 10:20 hard stop with zero slack' is close to correct - but the <1% path is still traded away for the 8% one"),
    (P, "'B = 2.9.5-patch (45 min, <1% risk, code change -> 25-min delta review + 20-min verification)' plus 'Sam to stand by for 15-min rollout open after'"),
    (R, "the B analysis correctly shows it fits ('requires Priya to start a delta review by ~09:10'), but no verification or Sam timings are attached to it"),
    (P, "'09:35-10:25 (Priya unavailable) - parallel work' covering the board pack, Orion and Globex"),
    (P, "'09:07-09:15 - Choose and post path: Option A'"),
    (P, "'send to Maya by ~10:45 - arithmetic only'"),
    (P, "'Renewal in 18 days + high-sev ticket G-441 + admin logins -61% + EUR12k expansion pending procurement'"),
    (P, "'The -45% usage is the contracted, approved shift to annual batch-processing. Not a churn signal'"),
    (P, "'Gap = EUR54k... Wayne -EUR18k + Globex -EUR12k explain EUR30k. Remaining EUR24k = Soylent (-EUR10k) + Wonka (-EUR14k)'"),
    (P, "'Don't invent causes for the Soylent/Wonka reductions in the board pack'"),
    (P, "each account triaged across accounts, contracts and support with an explicit ranking rationale"),
    (P, "'need the support ticket record and a CRM/billing match, then the live flag for the confirmed org. No reply until then'"),
    (R, "rejects the 10:30 task, but '~09:45: Confirm to Atlas that migration is on this morning with rollout opening ~11:00' precedes any verification"),
    (P, "'(Don't assert the SSO bug caused the login drop - just close it before the renewal conversation.)'"),
])

# --------------------------------------------------------------------------
# qwen3.8-flash - the widest range in the battery: a 100 and a 66.5
# --------------------------------------------------------------------------
run("qwen3.8-flash", "001", [
    (P, "'Maya's approval gate is superseded by her instruction to follow Security policy and Sam's rollout process'; 'The task to confirm a 10:30 launch is superseded/infeasible'"),
    (P, "'Do not call Zenith about renewal risk'; 'Do not send the customer announcement before Sam confirms rollout is open; Daniel owns the send'; 'Do not send enterprise pricing to Initech, procurement, or customers'"),
    (P, "'Product chooses path; Marcus deploys; Priya verifies; Sam opens rollout'; Daniel holds the announcement"),
    (P, "'Do not seek Maya approval as a release gate; it is superseded'"),
    (P, "'The pinned workbook is not authoritative despite the Sales Ops pin. Daniel's Friday 09:07 internal scenario is internal only'"),
    (P, "'Daniel has the final draft and Atlas recipient list. He will send after Sam confirms rollout is open. Sarah is out Monday'"),
    (R, "chooses viable A and schedules it correctly; B is set aside because 'there is no evidence the 2.9.5 diff is already submitted', which the response itself files as a thing to verify rather than a settled constraint"),
    (P, "'requires a 25-minute Security delta review before production deploy'; 'Do not open Enterprise Controls rollout before Priya's required verification and Sam's sanity check'"),
    (R, "every constraint is named and the A sequence is exact, but no B schedule is committed - it is deferred to MUST VERIFY"),
    (P, "'09:35-10:20 - Draft expansion reconciliation for Maya' while the delegated chain runs"),
    (P, "'09:07 - Choose Option A. Send decision to #enterprise-launch and owners'"),
    (P, "'11:00 - Send board pack to Maya before the 11:30 lock', drafted from 09:35"),
    (P, "'EUR84k ARR, renewal in 18 days, EUR12k expansion pending procurement, 3 open tickets including high-severity SSO setup, SCIM delay, and audit export timeout; admin logins -61%'"),
    (P, "'Monitor only... usage/logins decline explained by approved annual batch-processing shift; no expansion change and no support issue'"),
    (P, "'gap EUR54k. Wayne -EUR18k... Globex -EUR12k... Remaining -EUR24k is Soylent -EUR10k and Wonka -EUR14k'; Acme explicitly excluded"),
    (P, "'with no stated cause in the supplied contract/account data'; 'Do not invent causes for Soylent or Wonka expansion reductions'"),
    (P, "nine accounts triaged across the three files, each with ARR, renewal window, expansion delta, usage and ticket state"),
    (P, "'Orion's authoritative org ID and live SCIM flag. Missing: mapping between org_71A and org_17A and current flag for the correct org'"),
    (P, "'Do not promise Atlas a 10:30 launch; current evidence supports 11:00'; the Atlas update is conditioned on 'If deploy is healthy'"),
    (P, "no cause is asserted for any account; Soylent/Wonka reductions are 'unexplained by supplied data'"),
])
run("qwen3.8-flash", "002", [
    (R, "the recovery state and Maya's removed gate are right, but '09:45 Atlas Confirmation: \"Migration confirmed for today. Rollout begins shortly\"' is sent 75 minutes before rollout can open"),
    (P, "'DO NOT call Zenith'; 'Daniel sends announcement once Sam confirms rollout is live'; 'DO NOT send pricing to Initech Procurement'"),
    (P, "Marcus deploys, Priya verifies, Sam opens rollout, Daniel sends, Product chooses"),
    (P, "'DO NOT ask Maya for approval on the release path. She explicitly stated: \"I'm not adding another executive gate\"'"),
    (F, "the authority is inverted: 'Internal scenario planning values are obsolete/incorrect. The pinned workbook (enterprise-pricing-v4-final.xlsx) is authoritative internally'. Daniel's email says the opposite - the pinned workbook is not authoritative and his 09:07 values are the internal reference"),
    (R, E_OWNER_NO_HANDOFF),
    (R, "chooses A, which is viable, and reaches the correct A timeline after a visible self-correction; the B rejection rests on 'too tight' rather than on the windows"),
    (P, "'Option B... Requires 25m async delta review + 20m post-deploy verification' before deploy, with Sam's 15 minutes after"),
    (F, "'25m delta review + 45m deploy + 20m verification = 90m... If started at 09:15, completion is ~10:45' - the review can start at 09:07, and the response never commits a B schedule"),
    (P, "'09:15-09:35 Deploy & Verify (Parallel)... Simultaneously: Draft Board Pack email'"),
    (P, "'09:07-09:15: Decision & Communication' is the first action"),
    (P, "'11:00: Board Pack Submission. Send expansion reconciliation to Maya', drafted from 09:15"),
    (R, "Globex is ranked fourth as 'Support Risk' with the action 'Monitor'; the 18-day renewal, usage -18% and admin logins -61% are all absent from the assessment"),
    (P, "'Do not count as revenue loss unless ARR changed; ARR is flat at EUR150k. Exclude from expansion gap calculation'"),
    (P, "'Subtotal Explained: EUR30k. Remaining Gap: EUR24k. Soylent... EUR10k. Wonka... EUR14k' against the EUR54k gap, with Acme excluded"),
    (P, "'No stated cause in contracts/support'; 'DO NOT invent causes for Soylent/Wonka revenue drops'"),
    (R, "Acme is crossed against its contract and Soylent/Wonka against contracts and support, but Globex is handled on ticket severity alone and no counter-signal comparison is drawn"),
    (P, "'Must verify which org ID corresponds to the customer complaining about SCIM'; 'Check CRM/Live Flag for correct Org ID'"),
    (F, "'Migration confirmed for today. Rollout begins shortly' is sent to the customer at 09:45 as a statement of fact, when the response's own timeline opens rollout at 10:45-11:00"),
    (P, "'high-severity SSO issue may impact future adoption' is hedged"),
], penalties=[(
    "MATERIAL_HALLUCINATION",
    "'Internal scenario planning values are obsolete/incorrect. The pinned workbook (enterprise-pricing-v4-final.xlsx) is authoritative internally'",
    "The source authority is stated backwards. Daniel's Friday email says 'Pinned workbook is not authoritative. Use my 09:07 Slack values internally only.' Acting on this would put the obsolete numbers into internal planning and discard the current ones - the judge prompt names wrong source authority as material.",
)])
run("qwen3.8-flash", "003", [
    (P, "'Maya explicitly said no additional executive approval gate'; 'The task \"confirm launch at 10:30 to Atlas\" is not supported by Security/rollout timing'"),
    (P, "'Do not call Zenith about renewal risk'; 'Do not send the Enterprise Controls customer announcement before Sam confirms rollout is open; Daniel owns that send'; 'Do not send enterprise pricing to Initech procurement or any customer'"),
    (P, "'Marcus: 09:15-10:20 only'; Priya reviews and verifies; 'Sam owns rollout opening'; 'Daniel sends'; 'Product chooses the path'"),
    (P, "'Do not ask Maya for Enterprise Controls approval; she explicitly said no additional executive gate'"),
    (P, "'The pinned enterprise-pricing-v4-final.xlsx is not authoritative. Only Daniel's internal scenario values are usable internally'"),
    (P, "'Sarah is out Monday. Daniel has the final customer announcement draft and Atlas recipient list. Daniel will send only after Sam confirms rollout is open'"),
    (P, "'Primary path: Option B - 2.9.5-patch, because it reduces session-reset risk from 8% to <1% and can still meet the 12:00 Atlas window if started immediately'"),
    (P, "'Submit the 2.9.5-patch diff to Priya for the 25-minute asynchronous delta review' -> 'Marcus production deploy: 09:32-10:17' -> 'Priya post-deploy verification 10:25-10:45' -> 'Sam rollout open/sanity-check 10:45-11:00'"),
    (P, "'Marcus production deploy: 09:32-10:17 if review finishes by 09:32, or 09:35-10:20 if it finishes at 09:35' - both variants fit Marcus's window, Priya's two windows, Sam's 15 minutes and the 12:00 deadline, with an explicit 09:10 fallback gate to A"),
    (P, "'10:00-10:45 - Send expansion explanation to Maya' runs while the delegated release chain executes"),
    (P, "'09:07 - Choose Enterprise Controls path'; '09:08 - Trigger release sequence. Submit the 2.9.5-patch diff to Priya'"),
    (P, "'Send by 10:45, before the 11:00 deadline'"),
    (P, "'Renewal in 18 days, September expansion pending procurement, 3 open tickets including high-severity SSO setup issue, SCIM delay, audit export timeout; admin logins down 61%'"),
    (P, "'Renewal in 9 days, but usage/admin decline is expected due approved annual batch-processing shift. Routine renewal readiness check only; do not escalate usage decline as a risk'"),
    (P, "'Wayne: EUR18k -> EUR0 = -EUR18k... Globex: EUR12k -> EUR0 = -EUR12k... Soylent: EUR28k -> EUR18k = -EUR10k... Wonka: EUR24k -> EUR10k = -EUR14k' against the EUR54k gap, Stark and Acme both accounted for"),
    (P, "'Separate facts from risk indicators; do not infer causes for Soylent/Wonka'"),
    (P, "the priorities table carries every account with renewal window, expansion delta, usage/admin and ticket state; Acme is the explicit counter-case and both Soylent and Wonka are worked"),
    (P, "'Confirm whether Orion is org_71A or org_17A. Read the live scim_enabled flag for the confirmed org. Do not reply to Orion until both are verified'"),
    (P, "'Do not confirm Enterprise Controls launch to Atlas at 10:30'; the 11:00 figure is given to Atlas as an expectation gated on the sequence holding"),
    (P, "'Do not assume usage decline alone caused the expansion slip'; 'connect ticket context to expansion reduction only if evidence supports it'"),
])

# run-004 replaces run-002, which the reasoning audit disqualified. run-002's
# labels stay below, unchanged, because its evaluation is still on disk and
# still auditable - it simply no longer counts as official evidence.
run("qwen3.8-flash", "004", [
    (P, "'A production attempt failed on shard eu-03 before rollout opened; no customer impact'; 'Maya approval is not required for launch'; 'The task to confirm a 10:30 launch to Atlas is stale/unsafe'"),
    (P, "'Do not call Zenith about renewal risk'; 'Do not send the customer announcement yourself. Daniel owns it'; 'Do not send Enterprise pricing to Initech or any procurement/customer'"),
    (P, "'Product must choose the recovery path'; Marcus deploys, Priya verifies, 'Sam opens/sanity-checks rollout', 'Daniel owns sending the customer announcement'"),
    (P, "'Do not seek Maya approval for Enterprise Controls launch. Maya explicitly rejected another executive gate'"),
    (P, "'The pinned enterprise-pricing-v4-final.xlsx is not authoritative. Daniel's 09:07 Slack values are internal scenario planning only'"),
    (P, "'Sarah is out Monday. Daniel has Julia's final draft and the Atlas recipient list. Daniel owns sending the customer announcement after Sam confirms rollout is open' - the handoff is traced"),
    (R, "chooses A, which is viable and correctly scheduled; B is set aside because a diff submitted before 09:15 'is not evidenced', which names the right unlocking condition but treats submitting it as outside the user's control"),
    (P, "'2.9.5-patch requires a 25-minute delta review before deploy'; 'Do not open rollout before Priya's required verification and Sam's sanity check'"),
    (R, "the B arithmetic is right for the anchor it picks - 'if Marcus submits the diff at his 09:15 start, review ends 09:40, then a 45-minute deploy would end 10:25' - and it identifies the crux ('B could only work if a diff is submitted before 09:15'), but no viable B schedule is committed"),
    (P, "'09:45-10:25 - Prepare and send Maya's expansion explanation' runs inside the wait for Priya's 10:25 return"),
    (P, "'09:07-09:10 - Choose Option A and notify owners' is the first action, with Marcus's window driving the sequence"),
    (P, "'Send by 10:50, before the 11:00 deadline'"),
    (P, "'Renewal in 18 days. September expansion is pending procurement. Admin logins down 61%, usage down 18%. Three open tickets, including high-severity SSO setup issue'"),
    (P, "'Renewal in 9 days... contract context explicitly says this is an approved shift to annual batch-processing... Do not treat the usage decline as churn risk by default'"),
    (P, "'Gap EUR54k = Wayne -EUR18k + Globex -EUR12k + Soylent -EUR10k + Wonka -EUR14k'"),
    (P, "'Soylent/Wonka: no stated cause; investigation needed'; 'Do not invent causes for Soylent or Wonka expansion reductions'"),
    (P, "eight accounts triaged across accounts, contracts and support, each with renewal window, expansion delta, usage/admin and ticket state; Acme is the explicit counter-case and both Soylent and Wonka are worked"),
    (P, "'Confirm which org ID is correct: org_71A vs org_17A. Read the live SCIM flag for the correct org. No customer status until verified'"),
    (R, "'Do not confirm Atlas launch at 10:30' is right, but '09:40-09:45 ... confirm to Atlas that rollout is scheduled to begin at 11:00' still goes out before Priya's verification, with the conditionality only implied by the preceding step"),
    (P, "'investigate whether onboarding performance is related to the decline, but treat the relationship as unconfirmed until verified'"),
])


# --------------------------------------------------------------------------
# mimo-v2.5 - the widest spread of quality within one model
# --------------------------------------------------------------------------
run("mimo-v2.5", "001", [
    (R, "the recovery state and Maya's removed gate are right, but '09:45 | Confirm to Atlas: Enterprise Controls launch is on for today... Migration target ~11:00' is sent before any verification"),
    (P, "'Call Zenith about renewal risk | Fully resolved'; 'Daniel sends customer announcement'; 'Send Enterprise pricing to Initech procurement | Daniel explicitly blocked'"),
    (P, "Marcus deploys, Priya verifies, Sam opens rollout, Daniel sends, 'Product (you) must choose the path'"),
    (P, "'Seek Maya's approval for Enterprise Controls | Maya explicitly refused an executive gate'"),
    (P, "'Daniel's 09:07 Slack values are the only current figures. The pinned enterprise-pricing-v4-final.xlsx is obsolete'"),
    (R, E_OWNER_NO_HANDOFF),
    (R, "chooses viable A; the rationale is 'fewer moving parts' and an accepted 8% risk rather than a comparison the evidence supports"),
    (F, "no B chain is given; the contingency - 'fall to Option B with a delta review Monday afternoon' - is offered for a moment when Marcus, the only deployer, has already left"),
    (F, E_NO_B_SCHEDULE),
    (P, "'09:15-09:35 | While deploy runs: finalise expansion reconciliation. Verify Orion correct org ID'"),
    (P, "'09:07 | Message Marcus: choose Option A' is the first line of the timeline"),
    (P, "'Before 11:00 | Send expansion explanation to Maya (deadline 11:00; board pack locks 11:30)'"),
    (R, "'3 open tickets, one high-severity (SSO blocker). September expansion (EUR12k) stalled in procurement. Renewal in 18 days' - the usage -18% and admin -61% signals are never brought in"),
    (P, "'No expansion expected. Usage decline (-45%) is expected and approved (batch-processing shift). Not a risk'"),
    (R, "Wayne EUR18k, Globex EUR12k, Soylent EUR10k and Wonka EUR14k all appear, and 'Together these are the entire EUR24k unexplained gap', but the four are never closed against the EUR54k"),
    (P, "'Data-sufficient to report the arithmetic. Insufficient to state cause - do not fabricate one'"),
    (P, "Globex, Soylent, Wonka, Stark and Acme each crossed against contracts and support, Acme explicitly not a risk"),
    (P, "'Check the support ticket for the org ID Orion actually provided. Pull the live SCIM flag for that org. Do not reply until both are confirmed'"),
    (F, "'09:45 | Confirm to Atlas: Enterprise Controls launch is on for today; admins should be standing by. Migration target ~11:00' - an unconditional external commitment made before the deploy is verified"),
    (P, "no cause is invented for the eu-03 failure, Orion, or any account"),
], penalties=[(
    "MAJOR_CONTRADICTION",
    "'09:35 | Deploy complete. No post-deploy verification needed (no code change from staging-verified build).' against '10:25-10:45 | Priya runs post-deploy verification (~20 min)'",
    "The timeline states that Security's post-deploy check is not required and then schedules it. Priya's policy is explicit that a verified build still needs a production post-deploy check, so the first statement is also wrong on the policy - a reader following the timeline in order would skip a mandatory gate.",
)])
run("mimo-v2.5", "002", [
    (P, "'Maya has declined adding an executive gate and directed the team to follow Priya's release policy and Sam's rollout process'; no launch time is promised in advance"),
    (P, "'Do not call Zenith about renewal risk'; 'Daniel sends customer announcement'; 'Do not send Enterprise pricing to Initech or any customer/procurement'"),
    (P, "the timeline carries a Who column: Marcus deploys, Priya verifies, Sam opens rollout, Daniel sends, Me decides"),
    (P, "'Do not seek Maya's approval for Enterprise Controls release. She explicitly declined an executive gate'"),
    (P, "'Internal-only numbers... The pinned v4-final workbook is obsolete per Daniel. Nothing goes to customers or procurement'"),
    (R, E_OWNER_NO_HANDOFF),
    (R, "chooses viable A and schedules it correctly, on a false reading of the windows"),
    (R, "'Option B requires a 25-minute delta review before deploy' then '45-min deploy... post-deploy verification' has the order right; Sam's step is not carried into the B chain"),
    (F, "'with Priya unavailable 09:35-10:25 and Marcus departing 10:20, the windows don't overlap enough to complete delta review -> 45-min deploy -> post-deploy verification before 12:00' - Priya is available 09:00-09:35, so the review runs 09:07-09:32"),
    (P, "'09:35-10:25 ... Use this window for board-pack expansion explanation draft and Globex support follow-up'"),
    (P, "'09:07-09:15 | Arrive. Confirm Option A with Marcus, Priya, Sam'"),
    (P, "'11:00 | Hard deadline: Send expansion explanation to Maya', drafted from 09:35"),
    (R, "'3 open tickets incl. high-severity SSO blocker (G-441)... Renewal in 18 days. Expansion EUR12k pending procurement' - correct and top-ranked, but the usage and admin-login collapse is not used"),
    (P, "'Usage decline (-45%) is within the planned 40-50% range from their batch-processing shift - this is not a problem'"),
    (P, "'gap EUR54k. Wayne (EUR18k->October by amendment) + Globex (EUR12k->pending procurement) = EUR30k. Remaining EUR24k = Soylent (EUR28k->EUR18k) + Wonka (EUR24k->EUR10k)'"),
    (P, "'Do not fabricate causal explanations for Soylent or Wonka usage drops'; 'no customer communication explaining the change'"),
    (P, "Globex, Acme, Soylent, Wonka, Stark and Wayne each crossed against contracts and support; Acme is the explicit counter-case"),
    (P, "'No one has read the live flag for the correct org... Any SCIM status communication to Orion would be wrong until this is resolved'"),
    (P, "'~11:00 | Rollout open... I send Atlas launch confirmation' - after Sam's open, with nothing promised earlier"),
    (P, "no cause is asserted; the Soylent/Wonka root causes are filed as open questions"),
])
run("mimo-v2.5", "003", [
    (P, "'Sam has blocked all further communication until the correct org ID is confirmed'; 'Cross off stale tasks: \"Get Maya approval\" (she explicitly declined an executive gate)'; rollout 'projected'"),
    (P, "'Do not call Zenith. Resolved Friday. Task is stale'; 'Daniel sends customer announcement once Sam confirms rollout open'; 'Do not send Enterprise pricing to Initech procurement'"),
    (P, "'Message Marcus... Message Priya... Message Sam'; Daniel sends; the user picks the path"),
    (P, "'Do not request or add an executive gate to Enterprise Controls. Maya said \"I'm not adding another executive gate\"'"),
    (P, "'The authoritative internal figures are Daniel's... The pinned workbook is not authoritative. No external quote, no announcement date'"),
    (R, E_OWNER_NO_HANDOFF),
    (P, "'Option A and Option B both reach rollout opening at approximately the same time (~11:00)... Option B has <1% session-reset risk versus 8% for Option A... No extra time cost'"),
    (P, "'Ask him to submit the diff to Priya immediately' -> 'Priya conducts 25-min Security delta review... Must complete before production deploy begins' -> 'Marcus deploys 2.9.5-patch (45 min)' -> 'Priya verifies production (20 min)' -> 'Sam opens rollout and sanity-checks (15 min)'"),
    (P, "'09:25-10:10 Production deploy... He leaves at 10:20; deploy finishes ~10:10'; verification 10:25-10:45 on her return; Sam 10:45-11:00; rollout an hour before the 12:00 cutoff"),
    (P, "'09:25-10:10 - Parallel: draft board pack (my work)... Send to Maya by ~10:30'"),
    (P, "'09:07-09:15 - Launch recovery. Message Marcus: confirm Option B. Ask him to submit the diff to Priya immediately'"),
    (P, "'Send to Maya by ~10:30'; 'Board pack to Maya (due 11:00)'"),
    (P, "'18 days to renewal, 3 open tickets including a high-severity SSO blocker (G-441). Admin logins down 61%... The EUR12k expansion is pending procurement'"),
    (P, "'Contract notes explicitly state an approved shift to batch processing with expected interactive usage reduction of 40-50%. The numbers match the explanation'"),
    (P, "a full account table with a delta column: 'Wayne + Globex = EUR30k (explained). Soylent + Wonka = EUR24k' against the EUR54k gap"),
    (P, "'Do not cite causal explanations for Soylent or Wonka expansion reductions... Present the numbers and flag the gap'"),
    (P, "every account crossed against accounts, contracts and support, with Acme's explanation checked against its own numbers"),
    (P, "'Which Orion org ID is correct, and what is the live SCIM flag for it?... This is prerequisite to any customer communication'"),
    (P, "'rollout projected to open ~11:00'; 'if verification fails, the 12:00 deadline puts migration to Thursday'"),
    (P, "'Could be a deal-stalling signal or could be seasonal' - hypotheses are labelled as such throughout"),
])

# --------------------------------------------------------------------------
# qwen3.6 - the least stable model in the battery
# --------------------------------------------------------------------------
run("qwen3.6", "001", [
    (P, "'Policy: Maya refuses executive gate; follow Security/Release policy'; recovery options open; no launch time promised externally"),
    (P, "'Do NOT call Zenith'; 'Notify Daniel: \"Rollout open. Please send customer announcement\"'; 'Do NOT send Enterprise Pricing to Initech Procurement'"),
    (P, "'Marcus deploys 2.9.4', 'Priya performs 20-minute verification', 'Sam opens rollout', Daniel sends, 'Choose Release Path' is the user's"),
    (P, "'Decline \"Get Maya Approval\": Maya already stated: \"Follow Security's release policy.\" No approval needed'"),
    (P, "'Workbook is obsolete. Daniel's Slack values (EUR2,500 platform / 40 seats / EUR55 extra) are internal only. No external quotes'"),
    (P, "'Sarah (author) is out Monday. Daniel is the single point of failure for comms'; 'Daniel holds final draft and recipient list'"),
    (R, "chooses A, which is viable, but calls it 'the only viable path' while its own contingency shows B is 'tight but possible'"),
    (R, "'Option B: Marcus deploy -> Priya 25m delta review (async) -> Priya 20m post-deploy verify -> Sam 15m rollout check' puts the delta review after the deploy"),
    (F, "'Monitor Post-Deploy Verify: Priya performs 20-minute verification (09:35-09:55)' - Priya is unavailable 09:35-10:25, so the recommended A schedule cannot run as written"),
    (P, "'10:00-11:00: Board Pack & Expansion Reconciliation' fills the wait, and Orion is checked 'while waiting for Priya'"),
    (P, "'09:07-09:15: Immediate Actions. 1. Choose Release Path', citing Marcus's limited window"),
    (P, "'10:00-11:00: Board Pack... Send to Maya: Email Maya with the arithmetic breakdown'"),
    (R, "'3 open tickets (High/Medium/Medium). SSO setup failure (G-441) is a blocker for admin operations. Expansion is pending procurement' - the 18-day renewal and the usage/admin figures are absent"),
    (P, "'Acme: EUR0 expected. Contract explains \"approved shift to annual batch-processing\"... This is a known structural change, not a slip'"),
    (P, "'Total Gap: EUR18k (Wayne) + EUR12k (Globex) + EUR10k (Soylent) + EUR14k (Wonka) = EUR54k. Matches gap'"),
    (P, "'Separate data (contract terms, usage stats) from hypotheses (none, per Maya's instruction)'"),
    (P, "Globex on tickets and procurement, Acme on its contract, Soylent and Wonka both carried in the priorities with their amounts and 'no stated cause'"),
    (P, "'Must verify which org is live and active for Orion before replying'; 'check live flag for org_71A and org_17A'"),
    (R, "no external promise is made, but the ~10:10 rollout figure is passed to Sam and Daniel with no conditionality, and the stale 10:30 Atlas task is never addressed"),
    (P, "'SSO setup failure (G-441) is a blocker for admin operations' restates the ticket text rather than inventing a link"),
], penalties=[(
    "MAJOR_PLANNING_ERROR",
    "'Monitor Post-Deploy Verify: Priya performs 20-minute verification (09:35-09:55)' and 'If verify finishes at 09:55, rollout opens ~10:10'",
    "calendars.csv and Priya's own email both put her out of contact 09:35-10:25. The recommended plan books her required verification inside that window and derives a rollout time from it, so the schedule the response tells the user to execute cannot run.",
)])
run("qwen3.6", "002", [
    (R, "the recovery state and both option timings are right, but Maya's removal of the executive gate never appears and the stale 09:15 approval task is left standing"),
    (P, "'Do NOT call Zenith'; 'Daniel sends the customer announcement (he has the draft/list)'; 'Do NOT send Enterprise pricing to Initech procurement'"),
    (P, "'Priya: 09:00-09:35... Marcus: 09:15-10:20 (Deployer). Sam: 09:00-12:30 (Rollout Owner)'; Daniel sends; the user chooses"),
    (R, "no approval is sought, but the supersession is never established and the stale task is not rejected"),
    (P, "'Daniel's internal numbers... are current. External workbook is obsolete. No external quotes'"),
    (R, E_OWNER_NO_HANDOFF),
    (R, "correctly shows both paths reach rollout at 11:00, then picks A for 'lower technical risk' - which inverts the only risk figures given, 8% against <1%"),
    (P, "'Option B: Delta Review (25m, async) -> Prod Deploy (45m) -> Post-deploy Verification (20m, Priya) -> Sam Sanity Check (15m)'"),
    (R, "the B walk-through respects Priya's gap and Sam's 15 minutes and lands rollout at 11:00, but starts Marcus's deploy at 09:15 without the delta review having completed"),
    (P, "'09:15-10:20 Execution & Monitoring... 6. Board Pack Draft: Prepare the expansion explanation for Maya'"),
    (P, "'09:07-09:15: Immediate Actions. 1. Choose Release Path'"),
    (P, "'Send the expansion explanation to Maya by 11:00. (Send early if ready)'"),
    (R, "'Globex: Medium. High severity support ticket (SSO setup). Expansion is pending procurement. No immediate revenue impact today' - ranked fifth, with the 18-day renewal and the usage/admin collapse omitted"),
    (P, "'Acme: Low. Shift to annual batch processing. Expected usage reduction. No expansion expected'"),
    (P, "'Total unexplained gap: EUR24k. Soylent (-10k) + Wonka (-14k) = -24k' on top of 'Wayne/Globex explain EUR30k'"),
    (P, "'State that Soylent and Wonka reductions have no stated contractual cause. Do not invent reasons'"),
    (P, "Globex, Acme, Soylent and Wonka each crossed against contracts and support, with Acme held out as explained"),
    (P, "'Must verify which org ID belongs to Orion and check its live flag before replying'"),
    (P, "'Notify Sam: Inform him that rollout is targeted to open at 11:00 Monday, pending successful verification' - conditional, and nothing goes to the customer"),
    (P, "'support issues could delay procurement' is hedged; no cause is asserted"),
])
run("qwen3.6", "003", [
    (F, "Maya's removal of the executive gate never appears; the stale 09:15 approval task is left standing; and '#leadership: \"Will confirm rollout open by 10:30\"' revives the stale launch time"),
    (P, "'Do NOT call Zenith'; 'Notify Daniel to send customer announcement'; 'Do NOT send Enterprise Pricing to Initech Procurement'"),
    (P, "'Marcus (Deployer)', 'Priya (Security)', 'Sam (Release Mgr)', Daniel sends, 'Product Lead (You) must choose the recovery path'"),
    (R, "no approval is sought, but the supersession is never established and Maya is messaged about the choice instead"),
    (P, "'Daniel's internal numbers (EUR2,500 platform / 40 seats / EUR55 extra) are authoritative. External workbook is obsolete'"),
    (R, E_OWNER_NO_HANDOFF),
    (R, "chooses A, which is viable, on 'faster, verified build, fits Marcus's window' - the 8% against <1% comparison it states in CURRENT STATE is never applied"),
    (P, "'Option B: Priya Delta Review (25m async) -> Prod Deploy (45m) -> Priya Post-Deploy Verification (20m) -> Sam Sanity Check (15m)'"),
    (F, "'Priya verifies 09:35-09:55 (after her break)' misreads calendars.csv - 09:35-10:25 is the break - and the whole A timeline, 'Rollout opens ~10:15. Feasible', is built on it"),
    (R, "'10:30-11:00 Board Pack Expansion Reconciliation' sits after the release rather than inside the delegated waiting window"),
    (P, "'09:07-09:15: Immediate Actions. 1. Choose Release Path'"),
    (P, "'Send to Maya: By 11:00'"),
    (R, "'High Risk. 3 open tickets... SSO setup failure (G-441) is a blocker for SCIM and audit logs. Expansion is pending procurement' - correctly elevated, but the 18-day renewal and the usage/admin figures are absent"),
    (R, "'Acme: Medium Risk. Structural shift to annual batch processing. Usage down 45%... Monitor for churn' - the explanation is noticed and then the account is still carried as a churn watch"),
    (R, "'Explained (EUR30k): Wayne EUR18k; Globex EUR12k' and 'Remaining Gap (EUR24k)' are right, but the response concludes 'exact arithmetic requires full account file review' and never closes Soylent EUR10k + Wonka EUR14k"),
    (R, "'Do NOT invent causes for the EUR24k expansion gap' is stated and then broken in the same section by 'attributed to Soylent and Wonka usage declines and Acme's structural shift'"),
    (P, "Globex, Soylent, Wonka and Acme each crossed against accounts, contracts and support"),
    (P, "'Need to confirm which Org ID (org_71A or org_17A) belongs to Orion and what the live flag is'"),
    (F, "'#leadership: \"Maya, selecting Option A... Will confirm rollout open by 10:30\"' - a commitment to a time the response's own impossible schedule produced"),
    (F, "'The remaining EUR24k gap is attributed to Soylent and Wonka usage declines and Acme's structural shift' asserts a cause Maya explicitly forbade inventing, and Acme's expansion is unchanged at zero"),
], penalties=[
    (
        "MAJOR_PLANNING_ERROR",
        "'Priya verifies 09:35-09:55 (after her break). Sam checks 09:55-10:10. Rollout opens ~10:15. Feasible.'",
        "Priya's break is 09:35-10:25, not before it. The recommended plan books her mandatory verification inside her stated unavailable window and then commits a rollout time to the CEO on that basis, so the plan the response tells the user to execute cannot run.",
    ),
    (
        "MATERIAL_HALLUCINATION",
        "'The remaining EUR24k gap is attributed to Soylent and Wonka usage declines and Acme's structural shift'",
        "No source establishes usage decline as the cause of either expansion reduction, and Acme's September expansion is unchanged at zero so it contributes nothing to the gap. Maya's brief specifically forbids supplying causes the data does not establish, and this goes into the board pack.",
    ),
])

# --------------------------------------------------------------------------
# gemma4 - the only model whose recommended schedules cannot be executed
# --------------------------------------------------------------------------
run("gemma4", "001", [
    (F, "Maya's removal of the executive gate never appears anywhere, and '09:30-09:45: Confirm the 10:30 launch window to Atlas' revives the stale launch time the sources supersede"),
    (P, "'Zenith: Low priority... move to normal cadence'; 'instruct Daniel to send the customer announcement'; 'DO NOT quote the new pricing workbook externally'"),
    (P, "'Marcus deploys 2.9.5-patch', 'Priya performs 25m delta review + 20m post-deploy verification', 'Sam performs 15m sanity check', 'instruct Daniel to send'"),
    (R, "no approval is sought, but the supersession is never established and the stale 09:15 task is left standing"),
    (P, "'use only Daniel's 09:07 internal scenario values for internal planning'; 'DO NOT use the pinned enterprise-pricing-v4-final.xlsx as an authoritative source'"),
    (R, E_OWNER_NO_HANDOFF),
    (R, "chooses B for the right reason - 'to minimize session reset risk for Atlas' - but never shows it viable, and the schedule it then writes is not"),
    (R, "'Marcus deploys 2.9.5-patch (45m). Priya performs 25m delta review (asynchronous) + 20m post-deploy verification' puts the mandatory pre-deploy review after the deploy, contradicting the 09:15 instruction to submit the diff first"),
    (F, "'10:30-11:30 Execution Sequence: Marcus deploys 2.9.5-patch (45m)' - Marcus's hard stop is 10:20, so the deploy the plan schedules has no deployer"),
    (P, "'09:45-10:25: Draft the expansion reconciliation for Maya' while the release runs"),
    (P, "'09:15-09:30: Select Option B... Submit the diff to Priya immediately'"),
    (P, "'10:25-11:00: Finalize and send expansion explanation to Maya (Deadline 11:00)'"),
    (R, "'Active contract (18 days to renewal) with high-severity SSO/SCIM support tickets and a pending EUR12k expansion' - three of the four signals, with usage -18% and admin -61% missing"),
    (P, "'Acme: Monitor. Usage reduction is expected due to their shift to annual batch-processing'"),
    (R, "'EUR30k of the gap is explained by Wayne and Globex. The remaining EUR24k is driven by account-level reductions (Soylent, Wonka, Acme)' - the split is right but Acme's expansion is unchanged at zero, so the EUR24k attribution never closes"),
    (P, "'DO NOT invent causal hypotheses for Soylent or Wonka's expansion reductions in the board pack'"),
    (R, "Globex and Acme are each crossed against two sources, but Soylent and Wonka never reach the customer priorities at all"),
    (P, "'Confirm if the customer is org_71A or org_17A to ensure the SCIM flag is read for the correct account'"),
    (F, "'09:30-09:45: Confirm the 10:30 launch window to Atlas (pending successful deployment/verification)' commits to a time the response's own timeline opens at 11:30-12:00"),
    (P, "no cause is asserted for any account or for the eu-03 failure"),
], penalties=[(
    "MAJOR_PLANNING_ERROR",
    "'10:30 - 11:30: Execution Sequence: Marcus deploys 2.9.5-patch (45m)'",
    "calendars.csv and Marcus's own email both put his hard stop at 10:20. The plan schedules his 45-minute deploy to start ten minutes after he leaves, so the release the response recommends cannot be executed at all.",
)])
run("gemma4", "002", [
    (F, "'09:30-09:45: Confirm Enterprise Controls launch path with Maya' re-adds the executive gate Maya explicitly removed on Thursday"),
    (P, "'Zenith: Low priority; contract is signed and issues resolved'; 'instruct Daniel to send the customer announcement'; 'DO NOT quote the pinned enterprise-pricing-v4-final.xlsx to Initech or any external party'"),
    (P, "'Coordinate with Marcus to initiate deployment', 'Priya... post-deploy verification', 'Sam performs 15m sanity check', 'instruct Daniel to send'"),
    (F, "'Confirm Enterprise Controls launch path with Maya' seeks exactly the approval Maya said she would not add"),
    (P, "'The pinned enterprise-pricing-v4-final.xlsx is not authoritative. Internal scenario planning is EUR2,500 platform / 40 seats / EUR55 extra seat'"),
    (R, E_OWNER_NO_HANDOFF),
    (R, "chooses B to minimise session-reset risk, but never establishes viability and the schedule that follows is not executable"),
    (R, "'Submit diff to Priya immediately for asynchronous delta review' is right, but the timeline then runs '09:45-10:15 Coordinate with Marcus to initiate deployment' before '10:15-10:45 Monitor Priya's delta review'"),
    (F, "a 45-minute deploy initiated at 09:45-10:15 cannot finish inside Marcus's window, which closes at 10:20"),
    (R, "the board pack is submitted at 11:00 as a discrete step rather than drafted inside the delegated deploy window"),
    (P, "'09:15-09:30: Select Option B... Submit diff to Priya immediately'"),
    (R, "'11:00: Submit expansion reconciliation to Maya' lands on the deadline itself, after the 10:45-11:00 rollout step, with no earlier draft"),
    (R, "'18 days to renewal and 3 open support tickets (including high-severity SSO issue) impacting the pending September expansion' - the usage and admin-login figures are absent, and the link to the expansion is asserted"),
    (P, "'Acme: High priority; 9 days to renewal. Monitor usage reduction following their shift to annual batch-processing' - the decline is attributed to the approved change, not to churn"),
    (R, "'Wayne/Globex EUR30k slip; Soylent/Wonka/Acme EUR24k reduction' - the EUR24k figure is right but Acme contributes nothing to it, so the attribution is unvalidated"),
    (P, "'DO NOT invent causal reasons for Soylent or Wonka's expansion reductions in the Board pack'"),
    (R, "Globex and Acme are crossed against two sources each; Soylent and Wonka never appear in the priorities"),
    (P, "'DO NOT send status updates to Orion until the Org ID and live SCIM flag are confirmed'"),
    (R, "no external launch time is promised, but no conditionality is attached to the ~11:00 sequence and the stale 10:30 Atlas task is never addressed"),
    (F, "'3 open support tickets (including high-severity SSO issue) impacting the pending September expansion' asserts a causal link between the tickets and the procurement delay that no source establishes"),
], penalties=[
    (
        "MAJOR_PLANNING_ERROR",
        "'09:45 - 10:15: Coordinate with Marcus to initiate deployment of Option B. (Marcus must start by 09:15 and leave by 10:20; deployment takes 45m).'",
        "The plan starts a 45-minute deploy at 09:45-10:15 while quoting, in the same line, that Marcus leaves at 10:20. The recommended release cannot complete under the availability the response itself cites.",
    ),
    (
        "MATERIAL_HALLUCINATION",
        "'3 open support tickets (including high-severity SSO issue) impacting the pending September expansion'",
        "contracts.csv states only that Globex's September expansion is pending procurement. Nothing links the support tickets to the procurement delay, and Maya's brief explicitly forbids supplying causes the data does not establish.",
    ),
])
run("gemma4", "003", [
    (F, "Maya's removal of the executive gate never appears, and 'Notify Atlas of the 10:30 launch target' revives the stale launch time"),
    (P, "'Zenith: Low priority. Contract is signed and issues are resolved'; 'instruct Daniel to send the customer announcement'; 'DO NOT use the pinned enterprise-pricing-v4-final.xlsx for any external quotes'"),
    (P, "'Marcus deploys Option B', 'Priya performs post-deploy verification', 'Sam performs rollout sanity check', 'instruct Daniel to send'"),
    (R, "no approval is sought, but the supersession is never established and the stale task is left standing"),
    (P, "'The pinned enterprise-pricing-v4-final.xlsx is obsolete. Internal scenario planning is EUR2,500 platform / 40 seats / EUR55 extra seat'"),
    (R, E_OWNER_NO_HANDOFF),
    (R, "chooses B to minimise session-reset risk, but the schedule that follows cannot run"),
    (P, "'Submit diff to Priya for asynchronous delta review immediately' at 09:15, then 'Marcus deploys Option B (45m) -> Priya post-deploy verification (20m) -> Sam rollout sanity check (15m)'"),
    (F, "'10:25 - 11:15: Deployment Sequence: Marcus deploys Option B (45m) -> Priya (20m) -> Sam (15m)' - Marcus is gone at 10:20, and 80 minutes of work is booked into a 50-minute slot"),
    (P, "'09:45-10:25: Draft and send the September expansion reconciliation to Maya... Verify Orion's correct Org ID'"),
    (P, "'09:15-09:30: Select Option B... Submit diff to Priya for asynchronous delta review immediately'"),
    (R, "the 09:45-10:25 draft-and-send is right, but the plan then schedules '11:15-11:30: Finalize expansion explanation for Maya (Deadline 11:00, but priority is the Board Pack lock at 11:30)', deliberately overrunning the 11:00 deadline"),
    (R, "'Active expansion pending procurement; has 3 open support tickets (including high-severity SSO issue)' - the 18-day renewal and the usage/admin figures are absent"),
    (P, "'Acme: Monitor. Expected usage reduction is planned due to their shift to annual batch-processing'"),
    (R, "'The remaining EUR24k gap is driven by Soylent (-EUR10k), Wonka (-EUR14k), and Acme' - the two figures are correct and sum to EUR24k, but Acme is included even though its expansion is unchanged at zero"),
    (P, "'DO NOT invent causal reasons for Soylent or Wonka's expansion reductions in the Board pack'"),
    (R, "Globex and Acme are crossed against two sources; Soylent and Wonka appear only as arithmetic, never as customer signals"),
    (P, "'Confirm if the correct account is org_17A or org_71A'; 'Confirm the live flag status for the verified Org ID'"),
    (F, "'Notify Atlas of the 10:30 launch target' at 09:30-09:45 - an unhedged external commitment to a time the response's own timeline opens at 11:30-12:00"),
    (P, "no cause is asserted for any account"),
], penalties=[(
    "MAJOR_PLANNING_ERROR",
    "'10:25 - 11:15: Deployment Sequence: Marcus deploys Option B (45m) -> Priya performs post-deploy verification (20m) -> Sam performs rollout sanity check (15m)'",
    "Marcus's hard stop is 10:20, so the deploy has no deployer, and the three steps total 80 minutes inside a 50-minute block. The release the response recommends is unexecutable on both counts.",
)])


def main() -> None:
    out_dir = Path(__file__).resolve().parent
    for model, runs in VERDICTS.items():
        lines: list[str] = []
        for run_number, (rows, penalties) in sorted(runs.items()):
            run_id = f"monday-002__{model}__{run_number}"
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
            # One `penalties` entry per run, always written. The recorded judge
            # refuses to default it: an absent entry is an unanswered question,
            # an empty list is the answer "no violations".
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
        print(f"wrote {path.name} ({len(runs)} runs, {len(lines)} lines)")


if __name__ == "__main__":
    main()
