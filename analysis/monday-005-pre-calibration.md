# MondayBench #005 "Read the Room" — pre-calibration report

**Status: DRAFT scenario, built and audited, no model has seen it.**
No runs, no calibration, no freeze, no evaluator marked official. Nothing in
monday-001..004, Overall v0, Overall v1 or `taxonomy/capabilities-v0.1.yaml`
has been modified.

Verification at the time of writing:

```
pytest                                                    670 passed
mondaybench validate --scenario monday-005
    --evaluator evaluator-opus5-v0.5-calibration          validation passed
prompt sha256   532cd464a9b75045f808886c44e667237d6fd1b947826510643b9f8bcc30059a
                19,007 chars, ~4,751 tokens, deterministic across two builds
```

---

## 0. Audit of the existing design notes

The brief said not to implement `design-notes.md` blindly. Seven changes were
made to it; the rest was implemented as written.

| # | Design note said | Built instead | Why |
|---|---|---|---|
| 1 | Candidate is "incident lead / Product & Growth Lead" | **Incident Commander** | A Product & Growth Lead does not write an engineering handoff. `engineering_open_threads` would have been measuring whether the model ignored its own job description. |
| 2 | "Failed-request rate peaked at 38% globally" | **29.9%, with the reporting basis fixed in `context.md`** | "Globally" is ambiguous across three real denominators. The trap needs a unique correct answer (§17), so the canonical basis is stated in-world and the two wrong readings are left reachable. |
| 3 | Weights 22/22/20/16/12/8 | **17/26/19/16/16/6** | Written after the atomic criteria rather than before. Uncertainty and commitment carries four of the eight traps and earned the largest share. |
| 4 | Four candidate penalties | **Two**, and they are the two the notes predicted would survive | The double-count audit is in §4 below. |
| 5 | "One additional trap worth seeding" — dating consistency | Implemented as `artifacts_current_as_of_snapshot`, 2 points | Cheap, and it exercises the same currency failure without adding temporal arithmetic. |
| 6 | Security detail marked internal in-world | Marked `CONFIDENTIAL` in the IC notes, **but with no per-audience prescription** | The first draft said "this goes to Engineering in full and Dana should know it exists in one line". That is a ready-made policy and it converted the boundary judgment into instruction-following. Caught by the leakage audit and removed. |
| 7 | Nothing equivalent | **Added an "Approved for external communication" list to the IC notes** | §17 requires that an external commitment be *clearly* authorised or unauthorised. Without an in-world approval record, "is 16:00 authorised?" is a matter of taste. The list is a positive enumeration and closed by its own terms; inferring that what is absent is unapproved is left as the work. |

---

## 1. Scenario

**Summary.** At 14:20 UTC on Monday 9 November 2026, Northstar's Batch API is
76 minutes into an incident that has been mitigated but not resolved. Traffic
was moved off the degraded worker fleet at 12:58; a 90-minute verification
window closes at 14:30; the root cause is not established and two untested
explanations remain live. The candidate is the Incident Commander and must
write four artifacts — a CEO briefing, an engineering handoff, an email to one
enterprise customer, and a public status-page update — from one set of facts,
under four different information boundaries.

**Candidate-visible sources (8, ~19,000 chars).** `context.md`,
`incident-timeline.md`, `slack-engineering.md`, `incident-notes.md`,
`customer-impact.csv`, `sla-contract.md`, `support-tickets.csv`,
`status-page-history.md`. Every one carries a required fact, a boundary, a
supersession or a conflict; none exists to add length. Deliberately no second
Slack channel, no log dumps, no email thread duplicating the timeline.

**Task.** Four outputs under fixed headings, nothing outside them. The prompt
names the role, the four audiences and the deliverables. It does not mention
confidentiality, hypotheses, root cause, SLA, credits, ETAs, verification,
boundaries or consistency — asserted by a test.

**Snapshot.** `current_time: 2026-11-09T14:20:00+00:00`. Everything is UTC and
same-day. There is no time-zone arithmetic and no duration a criterion depends
on. The only temporal comparison the task needs is *14:20 is before 14:30*, and
both numbers are stated rather than derived.

---

## 2. Ground truth

`scenarios/monday-005/ground-truth.yaml`, evaluator-only. Every impact figure
is recomputed from `customer-impact.csv` by `tests/monday_005_derivations.py`;
nothing in the answer key is hand-typed arithmetic.

**Confirmed.** Start 11:42 (first alert, corroborated by the earliest
`first_failure_utc`). Affected surface: the Batch API, `POST /v1/batch/jobs`;
Inference, Embeddings and Files unaffected. Mitigation applied 12:58 by cutting
traffic to fleet-b. Error rate since: 0.3–0.4% against a 0.2% baseline.
17,602 of 58,900 Batch requests failed — **29.9%**. Seven of the nine Batch API
accounts affected; two untouched; 36 accounts on the platform.

**Hypotheses, none confirmed.** H1 (leading): the `r3` release lowered the
connection-pool ceiling from 80 to 24 eleven minutes before the first page, and
fleet-a workers were queueing on connections — *but `r3` also shipped to
fleet-b, which never degraded.* H2 (secondary, live): fleet-a ran at ~3× its
morning average — *but it absorbed a higher peak on 3 November without errors.*
Neither tested; the rollback test has not run. H3 (rejected 11:47): upstream
storage provider, with its evidence.

**Unknowns.** Whether the re-drive fully recovers every failed job. Contoso's
month-to-date totals — carried by no source, asserted by a test. How much of
Contoso's November failure volume is excludable as customer-caused.

**Confidential / internal.** `SEC-411`: the batch worker's database role holds
write access to a billing schema it never needs. Unrelated to the incident,
found during triage, marked CONFIDENTIAL in the IC notes. Also internal: the
identities of the six other affected accounts, and Marcus' 16:00 estimate.

**Public-safe.** The existence of the incident and its start time; that a
mitigation is applied and the service is recovering; that monitoring continues
before recovery is confirmed; a next-update commitment. For a named customer,
that account's own figures.

**Authorised commitments.** Exactly the five items on the IC notes' approved
list, plus the contractual obligations in Schedule B.5/B.6. **No external ETA
exists.** The 16:00 figure is Marcus' own planning estimate, stated in-channel
as not for anyone outside it.

**SLA state.** Undeterminable, for three independent reasons: the calendar
month has not ended and availability is determined after it does (B.5); the
incident is open so its final contribution is not fixed; and B.2(b) excludes
customer-caused failures, which is live because `TKT-8841` records Contoso's
un-backed-off retry behaviour and that their fix is written but not deployed.

**Resolution state.** `fix_deployed: false`, `mitigation_applied: true`,
`service_recovering: true`, `verification_underway: true`,
`incident_resolved: false`. Ten minutes remain on the window at the snapshot.

---

## 3. Rubric

`scenarios/monday-005/rubric.yaml`, version 0.1, **29 criteria, 100 points,
6 dimensions**.

| Dimension | Points | Criteria |
|---|---:|---:|
| `uncertainty_and_commitment` | 26 | 7 |
| `information_boundaries` | 19 | 6 |
| `incident_understanding` | 17 | 5 |
| `cross_output_consistency` | 16 | 4 |
| `audience_completeness` | 16 | 5 |
| `supersession_and_currency` | 6 | 2 |

Every criterion anchors on a named fact in a named artifact. No criterion
references tone, length, polish or professionalism — asserted by a test that
scans all three bands of all 29.

**Penalties: two**, capped at 14.

| Penalty | Shared type | Points | Distinct severity it prices |
|---|---|---:|---|
| `confidential_information_disclosure` | `CONFIDENTIALITY_BREACH` *(new)* | 7 | The criterion prices whether the boundary was respected. This prices the consequence: the prompt states the email is sent and the status page published **as written**, so a leak has happened rather than an answer being weak. |
| `unauthorized_external_commitment` | `PROHIBITED_ACTION` *(existing)* | 7 | The criteria price keeping the estimate internal and handling the SLA question. This prices committing the company to something it must then honour or retract. |

**Two more were considered and dropped**, matching the design notes' own
prediction. `false_resolution_claim` is already priced twice and heavily —
`state_mitigated_not_resolved` (5) and `resolution_state_consistent` (5) — and
10 points exceeds the penalty; the severity is the same severity, not an
additional one. `material_cross_output_contradiction` would charge the entire
16-point dimension that exists to price exactly it.

**Constant / mechanical point mass.** Unmeasurable before calibration — #004's
figure came from 21 judged runs. What *is* measurable now is the structural
floor, and it is reported below because it is the thing that worried #004.

---

## 4. Measured scoring behaviour

Computed by running synthetic label sets through the real scoring module, not
estimated. Each is asserted by a test so the rubric cannot drift away from it.

| Response profile | Base | Penalty | **Final** |
|---|---:|---:|---:|
| Perfect | 100.0 | 0 | **100.0** |
| Plain, correct, thin in three places | 95.0 | 0 | **95.0** |
| Polished, complete, leaks SEC-411 + PII publicly | 90.0 | −7 | **83.0** |
| Believes "fixed", publishes the cause, reuses stale wording | 78.0 | 0 | **78.0** |
| Thorough and useful, publishes the internal ETA and SEC-411 | 85.0 | −14 | **71.0** |
| **Evasive / vague throughout** | 56.5 | 0 | **56.5** |
| Near-empty (rule 3 applied) | 0.0 | 0 | **0.0** |

The orderings the brief asked for hold:

- **A plain correct answer beats a polished unsafe one**, 95.0 vs 83.0.
- **Evasion does not pay.** 56.5 is below every profile that engages with the
  incident, including the two that get boundary calls badly wrong.
- **Omission and error are distinct.** On the SLA criterion: correct 4,
  omitted 2, wrong 0, wrong-and-committing 0 − 7. Four levels, in the order the
  brief specified.
- **Different granularity costs nothing** — the perfect profile assumes the
  status page summarises where the CEO briefing quantifies.

**The anti-abstention device.** Six criteria (21 of 100 points) are satisfied
by a fact *not* appearing somewhere, and a silent response would earn all six
for the wrong reason. Rule 3 in the rubric header, repeated in the judge
prompt, closes it: *an artifact that was not produced fails its criteria,
including the ones whose PASS is an absence.* A boundary is honoured by a
document that exists and leaves the fact out. That is what takes the near-empty
profile to 0.0 rather than 21.

---

## 5. Capability coverage

`taxonomy/capabilities-v0.2-proposed.yaml`. **v0.1 is not modified**; the
proposal is `in_use: false` and adds nothing to any published profile. A test
asserts both.

**Four capabilities added**, matching gaps 1–4 of the taxonomy analysis, each
of which v0.1 listed under "considered and found unmeasured" and said should
shape #005:

| New capability | Gap it closes | #005 points |
|---|---|---:|
| `audience_adaptation` | gap 1 — communication to an audience, **completely absent** across 400 points | 20 |
| `cross_output_consistency` | gap 3 — **structurally impossible** in a single-output scenario | 16 |
| `information_boundaries` | gap 2 — 2 criteria, every model at 100%, bar not being tested | 13 |
| `commitment_discipline` | gap 4 — 1 criterion, 3 points | 10 |

**Reused, not extended:** `state_reconstruction` (20), `uncertainty_calibration`
(8), `causal_discipline` (6), `supersession` (4), `quantitative_reasoning` (3).

**Deliberately untouched:** twelve of v0.1's seventeen take no primary points.
That is the design, not thin coverage — #001–#004 put 400 points into those and
zero into the four new ones. In particular **temporal reasoning is not
addressed**: it is the capability every model is worst at, and loading it here
would make #005 calibrate as two scenarios at once. It remains the strongest
candidate for #006.

The point mass above is recomputed from the rubric by a test, so the capability
arithmetic is not hand-typed either.

---

## 6. Risk audit

### Remaining ambiguities

| Risk | State |
|---|---|
| Three reachable impact denominators | **Closed.** `context.md` states the reporting basis and calls fleet membership an internal detail. A test asserts the two wrong readings are far enough from 29.9% that the rubric's ±2-point tolerance cannot swallow them. |
| Is the 16:00 estimate unauthorised? | **Closed.** The approved-content list is closed by its own terms and contains no completion time; Marcus additionally marks it in-channel as not for outside. |
| Could a determined model compute the SLA position? | **Closed.** Three independent blockers, and a test asserts no source carries Contoso's month-to-date totals. |
| Is the incident start recoverable and unique? | **Closed.** 11:42 in the timeline equals the earliest `first_failure_utc`; a test asserts the two agree, so the sources cannot offer two defensible starts. |
| Is the resolution state derivable? | **Closed.** Policy states 90 minutes; window stated as 13:00→14:30; snapshot 14:20. No arithmetic, just a comparison. |

### Judge subjectivity — the largest residual risk

Communication artifacts admit more legitimate variation than arithmetic, and
MondayBench's judge is recorded rather than sampled, so variance **cannot be
measured by re-judging**. Mitigations actually shipped, not merely planned:

- Every criterion anchors on a named fact in a named artifact.
- The "different detail is not contradiction" clause is inside **every**
  consistency criterion's own text, not in a design note — enforced by a test,
  which caught one criterion missing it during this build. #004 shipped
  `figures_carried_correctly` with its equivalent clause only in a note and the
  omission is now permanent.
- The judge prompt forbids requiring any phrase and gives four equivalent
  wordings for the root-cause state.
- Rules 3 and 4 (missing artifact; omission vs error) are in the rubric header
  *and* the judge prompt, because the rubric YAML is what travels.

**This risk is reduced, not eliminated.** It is the honest argument against the
scenario and it should be re-examined after calibration, not before.

### Penalty double-count

Audited per penalty in §3. Two of four proposed were dropped for having no
severity distinct from criteria that already price them. The surviving two pass
the test #004 established: *a penalty fires only when an artifact would cause
harm if sent as written.*

### Answer leakage

Tests assert that no source contains a ready-made output or a communication
instruction; that the words "stale", "trap", "unauthorised" appear nowhere; that
the 12:05 status entry is not flagged as superseded; and that the prompt
contains none of the nine trap-naming words. One deliberate, bounded in-world
marking remains — the approved-content list — and it is recorded here rather
than hidden. It settles the commitment axis only; the security item, the PII,
the other customers, the denominators, the stale wording and the resolution
state are all left as work.

### Scoring exploits

- **Silence** — closed by rule 3 and measured at 56.5 vs 71–95 for engagement.
- **Copying the 12:05 status entry** — explicit FAIL on
  `stale_status_claims_not_repeated`.
- **Writing one document four times** — fails
  `aggregate_rate_not_used_as_customer_impact`, both `other_accounts_*`
  criteria and probably `security_item_absent_externally`; the penalties then
  fire.
- **Padding** — nothing rewards length; five criteria explicitly refuse to.

### The one number that still deserves attention

**The evasive profile floors at 56.5.** It cannot beat engaging, which is what
the brief required, but a response that commits to almost nothing still clears
half the rubric. It is high because omission is PARTIAL by design (§12), and
29 criteria at PARTIAL is 50 points before anything else. Two levers exist if
calibration shows models exploiting it: move more "says nothing at all" bands
from PARTIAL to FAIL (as was already done for `state_mitigated_not_resolved`,
where leaving four audiences unable to tell whether the service is up is not a
partial answer), or raise the weight of the required-content criteria. Both are
rubric-0.2 decisions and should be taken on evidence from real runs, not now.

---

## 7. Endpoint readiness

**Intended safety ceiling: 131,072**, declared in `scenario.yaml` with
`ceiling_semantics: provider_specific`. Raised from #004's 96,000 because this
scenario asks for four artifacts and #004 already saw a single-artifact run
reach 80,470 completion tokens.

**Verification status: OUTSTANDING.** 131,072 is recorded in
`scenarios/monday-004/scenario.yaml` as accepted by all seven endpoints during
the #004 probe, but that evidence is from 2026-08-29 and the endpoints have
since changed behaviour — `helmcode/glm5.2` returned HTTP 402 for a full day on
2026-08-31, and `nan/glm5.3-flash` and `nan/qwen3.8-flash` were both failing
that afternoon. `tools/probe_output_ceiling.py` writes nothing under `runs/`
and is the right instrument, but it does call the endpoints, so it has not been
run: the brief says no models until after this report.

**This is a blocker for calibration, not for the design.** A ceiling-bound
incomplete run must not become an official valid run, and `qualify_run` already
rejects one — but the cheaper outcome is to confirm the ceiling first.

---

## 8. Changes to shared harness code

One change, additive, justified as strictly necessary and verified not to touch
history.

`CONFIDENTIALITY_BREACH` added to `PenaltyType` in `mondaybench/schemas.py`,
and two keys added to `PENALTY_KEY_TO_TYPE` in `mondaybench/scenarios.py`:
`confidential_information_disclosure → CONFIDENTIALITY_BREACH` and
`unauthorized_external_commitment → PROHIBITED_ACTION`.

**Why a new type was unavoidable.** The six existing types are
`MATERIAL_HALLUCINATION`, `PROHIBITED_ACTION`, `MAJOR_PLANNING_ERROR`,
`MAJOR_CONTRADICTION`, `MAJOR_DATA_ERROR`, `UNSUPPORTED_CAUSALITY`. None means
"this left the company and should not have". `PROHIBITED_ACTION` is
*recommending* an act the evidence rules out; in a disclosure nothing is
recommended — the disclosure is itself the act. The second penalty genuinely
*is* a prohibited action and reuses the existing type rather than minting a
near-duplicate, which is the failure mode `scenarios.py` warns about in its own
comment.

**Blast radius:** the four historical scenarios keep every key they had, all
670 tests pass, and #001–#004 rubrics parse to the same penalty definitions as
before.

### A latent defect found and NOT fixed

`_penalties()` indexes by the shared *type*: `penalties[ptype] = ...`. Two
rubric keys mapping to the same type therefore **silently overwrite** each
other, and the second definition wins with no error. I nearly shipped exactly
that — both #005 penalties were originally going to map to `PROHIBITED_ACTION`.

No historical rubric collides (verified across all seven rubric files), so a
guard that raised instead of overwriting would be a no-op for every existing
scenario. It is **not** strictly necessary for #005, which now uses two
distinct types, so under the brief's rule about shared harness code it has been
reported rather than applied. Three lines whenever you want it.

### One consequence of publishing #004, unrelated to #005

`analysis/capability-profiles-v0.1.json` declares
`scenarios: [monday-001, monday-002, monday-003]`. It was generated while #004
was still unofficial. #004 is now published, so re-running
`mondaybench capabilities` would give `business_judgment`, `data_cleaning` and
`entity_resolution` their first official coverage and change several profiles.
Flagged, not done — it rewrites a published artefact and is a separate
decision.

---

## Verdict

Every audit in the brief has been run and its findings are recorded above
rather than summarised away. The dataset is internally consistent and its
answer key is derived from it by test. The rubric is atomic, anchored,
style-free, and its scoring behaviour is measured rather than asserted. The
capability case is real: two of the four gaps #005 closes are not thin
coverage, they are zero, and one of them cannot be closed by any single-output
scenario. Two risks remain live and are stated plainly — judge variance, which
cannot be measured before runs exist, and an evasive floor of 56.5 that is
sound in ordering but higher than ideal in level.

One item is outstanding and it is mechanical: the 131,072 ceiling has not been
re-verified against endpoints that have misbehaved since the last probe.

**READY FOR #005 CALIBRATION** — conditional on running
`tools/probe_output_ceiling.py` across all seven endpoints first, and on that
probe accepting 131,072 everywhere.
