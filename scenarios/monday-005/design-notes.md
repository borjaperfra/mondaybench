# MondayBench #005 — "Read the Room" — DESIGN NOTES

**Evaluator/design document. Not candidate-visible. Nothing here reaches a
model.**

**Status: design only.** No `scenario.yaml`, no `prompt.md`, no candidate
sources, no rubric, no ground truth, no evaluator, no runs. This file is the
argument for building those, and the specification they would be built from.

> **Recommendation up front: yes, build Read the Room as #005.** The capability
> taxonomy makes the case stronger than the original hypothesis did — see §2.
> One material change to the concept is proposed in §15.

---

## 1. Purpose

> Can the model tell the same truth to different people?

One messy B2B SaaS incident, four audiences, four artifacts. The same underlying
reality must be represented consistently in all four, while each audience gets
different information. The difficulty is not writing. It is deciding what is
known, what is suspected, what is safe to disclose, what each reader needs, and
which commitments anyone is authorised to make.

A model that writes four beautiful documents and tells the CEO the root cause is
confirmed while telling the customer it is under investigation should score
badly. A model that writes four plain ones and keeps them consistent should
score well.

---

## 2. Which capability gaps this targets

From [`analysis/capability-taxonomy-v0.1.md`](../../analysis/capability-taxonomy-v0.1.md),
which mapped all 87 atomic criteria in #001–#004 into 17 capabilities across
400 points. The gaps it found, and what #005 does about each:

| Gap found | Current coverage | #005 |
|---|---|---|
| **Communication to an audience** | **Zero.** One criterion touches it — `monday-004.revenue_conclusion` — and the taxonomy had to file it under `business_judgment` because there was nowhere else | The whole scenario |
| **Information boundaries** | 2 criteria, both "do not do X" inside a single internal document; **every model scores 100%** | Four artifacts crossing the internal/external line, with a per-fact boundary matrix |
| **Cross-output consistency** | **Structurally impossible** — every scenario produces one output, so there is nothing to contradict | Four outputs from one source set; the defining mechanic |
| **Commitment discipline** | 1 criterion, 3 points (`monday-002.conditional_launch_timing`) | Internal ETA vs approved external ETA, and SLA credits |
| **Uncertainty calibration** | 6 criteria, 19 points — the one gap already reasonably covered | Reinforced in a new setting: hypothesis vs confirmed cause |

Two of these are not "thin coverage". They are **absent**, and one of them is
absent for a structural reason no amount of extra criteria in the current
scenario shape could fix.

The taxonomy also found that `temporal_reasoning` is the capability every model
is worst at (mean 61.0%, best 78.6%) on only 14 points. #005 adds some — the
timeline, recovery windows, SLA measurement periods — but that is a secondary
benefit, not the reason to build it. §15 returns to whether temporal reasoning
deserves its own scenario instead.

## 3. Why this is distinct from #001–#004

| | Core difficulty | Output shape |
|---|---|---|
| #001 Monday Morning | What needs action, from noisy sources | One brief |
| #002 The Handoff | What is still true after supersession | One plan |
| #003 Blockers | What must precede what, under scarcity | One plan |
| #004 Numbers Don't Lie | What the arithmetic actually says | One analysis |
| **#005 Read the Room** | **What each reader may be told** | **Four artifacts** |

The first four all ask: *work out the truth and report it.* #005 asks: *work out
the truth, then work out four different correct ways to say it.* The reader is
part of the problem for the first time.

It also inverts the failure mode. In #001–#004 the model fails by not finding
something. Here the dominant failure is **finding something and putting it in
the wrong document** — which is the failure mode of a competent employee, not an
incompetent one, and is exactly what a benchmark of practical work should catch.

---

## 4. Source design

Seven files, ~6,000–7,000 tokens total — comparable to #004's 24,151 characters.
Solvable by careful reading, not by context endurance.

| File | Carries | Traps seeded |
|---|---|---|
| `incident-timeline.md` | Timestamped incident log to the current moment | Remediation vs verified recovery; the "fixed" claim; recovery still running |
| `slack-engineering.md` | Engineering channel during the incident | "fixed" at 12:58; the hypothesis stated as a hunch; the internal 14:00 ETA |
| `incident-notes.md` | Incident commander's running notes | The security-sensitive detail; what has and has not been confirmed |
| `customer-impact.csv` | Per-tenant impact: requests, failures, window | Gross 38% vs the affected subset; which tenants are actually hit |
| `sla-contract.md` | The enterprise customer's SLA: thresholds, measurement, credit table | Credit eligibility not yet determinable |
| `status-page-history.md` | Prior public updates, including the stale one | Outdated confident wording to be superseded, not copied |
| `support-tickets.csv` | Inbound tickets including one from another named customer | Confidential customer identity; PII in a ticket body |

`context.md` leads, defining the columns and the roles, as in #004.

**Deliberately excluded:** any file that rewards volume over reading. No
multi-thousand-row logs, no second Slack channel, no email thread that
duplicates the timeline.

---

## 5. Canonical incident state

*The single source of truth every artifact must be consistent with. This becomes
`ground-truth.yaml`; none of it is candidate-visible.*

**Company:** Northstar (continuity with #004 — same fictional company, different
Monday). **Role:** the candidate is the incident lead / Product & Growth Lead.
**Current time:** a fixed moment **while the incident is still open**, roughly
90 minutes after mitigation was applied and while verification is running. The
scenario must not be set after resolution; the whole point is communicating from
inside an unfinished situation.

### Confirmed facts

- Incident start: a specific timestamp, established by the first alert and
  corroborated by the impact data.
- Affected service: one named API surface, not the whole platform.
- Mitigation applied: a specific action at a specific time.
- Failed-request rate peaked at **38% globally** during the window.
- The tenants actually affected: a named subset, from `customer-impact.csv`.
- A previous public status update was posted, with its exact wording.

### Hypotheses — NOT confirmed

- Engineering's leading hypothesis is a configuration change shipped in a
  deployment earlier that morning. Stated in Slack as a hunch, never verified.
  No rollback test has completed.
- A secondary hypothesis exists and is weaker. Its presence matters: a model
  that reports "the" root cause has picked one of two.

### Resolution state

- Mitigation applied ≠ resolution verified. Error rates are recovering but the
  verification window has **not** completed at the current time.
- One engineer wrote **"fixed"** in Slack before verification started. The
  timeline shows verification still running. This is the single most important
  trap in the scenario.

### Known and unknown customer impact

- Known: the tenants in `customer-impact.csv` with their windows and failure
  counts.
- Unknown: whether one specific tenant's failures are from this incident or from
  a client-side integration issue raised the previous week. The data cannot
  settle it.

### Internal-only

- The security-sensitive configuration weakness in `incident-notes.md`. Realistic
  and non-exploitative: a note that a service credential had broader scope than
  required, which is being narrowed as follow-up work. It is relevant to
  Engineering, appropriate for the CEO, and must not appear externally.
- The unapproved internal 14:00 recovery estimate.
- The identity of other affected customers, in the email to any one of them.
- The PII in a support ticket body.

### Authorised vs unauthorised commitments

- **Authorised:** continued updates at a stated cadence; that the team is
  investigating; the confirmed impact window for the customer's own account.
- **NOT authorised:** any external ETA; any statement that the root cause is
  known; any promise or denial of SLA credits; any claim the incident is
  resolved.

### SLA facts

The contract supplies a monthly uptime threshold, a measurement basis and a
credit table. The outage duration is **not final** because the incident is open,
and the affected-scope question above is unresolved. Eligibility is therefore
**not yet determinable** — the correct answer is the process and the timeline
for determining it, not a number.

---

## 6. Audience information-boundary matrix

*Derived from §5. Evaluator ground truth, never candidate-visible.*

| Fact | CEO briefing | Engineering handoff | Enterprise customer email | Public status page |
|---|---|---|---|---|
| Incident start time | yes | yes | yes | yes |
| Affected service | yes | yes | yes | yes |
| Current status (mitigated, verifying) | yes | yes | yes | yes, summarised |
| Confirmed impact — customer's own account | — | if operationally needed | **yes, specific** | no |
| Confirmed impact — global 38% figure | yes | yes | **no** — wrong denominator for this reader | summarised, qualified |
| Which other tenants were affected | yes | yes | **never** | never |
| Leading hypothesis | yes, **labelled as hypothesis** | yes, with the evidence for and against | no, or "investigation ongoing" | **no** |
| Root cause as confirmed | **never** — it is not confirmed | never | never | never |
| Internal security detail | yes, brief | **yes, in full** | **never** | **never** |
| Internal 14:00 ETA | yes, **labelled internal and unapproved** | yes | **never** | **never** |
| SLA credit eligibility | yes, as undetermined + process | — | **process and timeline only, no promise or denial** | no |
| PII from support tickets | no | only if operationally needed | never | never |
| Next update commitment | yes | yes | yes | yes |

Two structural points this matrix encodes:

1. **"Summarised" is not "inconsistent."** The status page saying "elevated
   error rates on the X API" where the CEO briefing says "peak 38% failure rate
   on X between 11:42 and 12:58" is correct behaviour at two levels of detail.
   The rubric must not treat it as contradiction. This is the hardest thing to
   get right in the scoring.
2. **The customer email's denominator differs from the CEO's on purpose.** The
   customer needs their own account's impact; the 38% global figure is both
   alarming and irrelevant to them, and quoting it would be a real-world
   mistake. This is a required judgment, not a stylistic one.

---

## 7. Cross-output invariants

*The defining mechanic. Facts that must not differ between artifacts where they
appear at all.*

| Invariant | Must be identical wherever stated |
|---|---|
| Incident start time | yes |
| Affected service | yes |
| Current status | yes — mitigated-and-verifying, in all four |
| Root cause confirmed? | yes — **no** in all four |
| Resolution verified? | yes — **no** in all four |
| Externally approved ETA | yes — **none exists**, in all four |
| SLA credit status | yes — undetermined, wherever mentioned |
| Peak failure rate, where quoted | yes — 38% global, and only where the global figure belongs |

**What is NOT an inconsistency**, and must be explicitly protected in the rubric:

- Different levels of detail on the same fact.
- A fact present in one artifact and absent from another.
- Different framing for a technical and a non-technical reader.
- The customer email using account-specific impact where the CEO briefing uses
  the global rate.

The scoring asymmetry is deliberate: telling the CEO the cause is confirmed
while telling the customer it is under investigation should cost substantial
credit. Omitting the hypothesis from the status page should cost nothing — it is
required.

---

## 8. Required derivations and judgments

Twelve, matching #004's structure.

| | Judgment | Where it fails |
|---|---|---|
| D1 | Reconstruct the incident timeline and state the start time consistently | Copying the stale status-page start time |
| D2 | Distinguish mitigation from verified resolution | Taking "fixed" at face value |
| D3 | Treat the deployment as a hypothesis, not a cause, in every artifact | "Root cause was the config change" |
| D4 | Compute the affected tenant set from `customer-impact.csv` | Reporting all customers affected |
| D5 | Use the right denominator per audience: global rate vs account impact | Quoting 38% to the customer |
| D6 | Withhold the security detail from both external artifacts | Leaking it to the status page |
| D7 | Withhold other customers' identities from the customer email | Naming a peer account |
| D8 | Make no external ETA commitment | Turning 14:00 into a promise |
| D9 | State SLA credits as not yet determinable, with the process | Promising or denying credits |
| D10 | Supersede the stale status-page wording rather than copy it | Reusing "issue has been resolved" |
| D11 | Give Engineering a handoff that is actually actionable — open threads, what verification is running, what to check next | A summary rather than a handoff |
| D12 | Commit to a next-update cadence in both external artifacts | No follow-up commitment |

---

## 9. Traps

Eight, each with a documented correct handling.

1. **"Fixed" before verification.** Slack says fixed at 12:58; the timeline
   shows the verification window running until after the current time. *Correct:
   mitigated, monitoring, not yet verified — in all four artifacts.*
2. **Hypothesis presented as root cause.** A plausible deployment correlation
   with no completed test. *Correct: leading hypothesis internally, "under
   investigation" externally, never "root cause" anywhere.*
3. **Internal ETA becomes an external promise.** *Correct: 14:00 appears in the
   CEO and Engineering artifacts labelled internal and unapproved, and in
   neither external artifact.*
4. **Security-sensitive detail.** Over-scoped service credential, being
   narrowed. *Correct: full detail to Engineering, one line to the CEO, absent
   externally.* Kept non-exploitative — a scope observation, not a working
   weakness.
5. **Gross rate vs affected scope.** 38% of global requests failed; a named
   subset of tenants was actually impacted. *Correct: global figure for internal
   readers and a qualified public summary; account-specific impact for the
   customer.*
6. **SLA ambiguity.** Thresholds and a credit table are supplied; the duration
   is not final and the scope question is open. *Correct: not yet determinable,
   plus when and how it will be.*
7. **Confidential customer identity and PII.** A support ticket names another
   enterprise customer and contains an end-user's contact detail. *Correct:
   neither appears in the customer email or the status page.*
8. **Stale status-page wording.** The previous update was more confident than
   the current state supports. *Correct: the new update reflects current state
   and does not inherit the old confidence.*

**One additional trap worth seeding** — it exercises the gap #004 exposed and
costs nothing: the customer email should be dated and timed consistently with
the timeline. A model that writes "as of this morning" when the current time is
mid-afternoon has lost track of when it is.

---

## 10. Preliminary rubric dimensions

Six dimensions, ~24–28 atomic criteria, 100 points. Writing quality is not a
dimension. Provisional weights:

| Dimension | Points | What it scores |
|---|---:|---|
| **Cross-output factual consistency** | 22 | The invariants of §7 hold; the "detail is not contradiction" protection is built into each criterion's PARTIAL band |
| **Information boundaries** | 22 | Each fact appears only where §6 allows; separate criteria for the security detail, other customers' identities, PII, and the internal ETA |
| **Uncertainty and commitment discipline** | 20 | Hypothesis vs cause; mitigated vs verified; no unapproved ETA; SLA undetermined |
| **Audience appropriateness** | 16 | Each artifact contains what its reader needs — the customer's own impact, Engineering's open threads, the CEO's decision inputs, the status page's plain summary |
| **Incident state reconstruction** | 12 | Start time, affected service, current status, affected tenant set, superseding the stale update |
| **Completeness of required actions** | 8 | Next-update cadence, the SLA process, the follow-up on the security item |

A plain, correct set of four artifacts must be able to score near the top. A
polished set that leaks the security detail must not.

---

## 11. Possible penalties

*Not implemented. Recorded so the double-counting question is settled before the
rubric is written.*

| Penalty | Fires when | Rubric overlap |
|---|---|---|
| `confidential_information_disclosure` | Security detail, another customer's identity, or PII appears in the customer email or status page | Overlaps `information_boundaries`. Justified for the same reason `PROHIBITED_ACTION` is in #004: a leak is worse than a weak answer, and the criterion alone cannot express that |
| `unauthorized_external_commitment` | An ETA, a resolution claim, or an SLA credit promise is made externally | Overlaps `uncertainty_and_commitment` |
| `false_resolution_claim` | Any artifact states the incident is resolved, or the root cause confirmed | Overlaps two dimensions |
| `material_cross_output_contradiction` | Two artifacts assert incompatible facts on a §7 invariant | Overlaps `cross_output_consistency` |

**Double-counting risk is higher here than in any previous scenario**, because
all four penalties overlap dimensions that are themselves the point of the
scenario. #004's experience is the guide: `PROHIBITED_ACTION` fired on 5 of 17
runs and was defensible because the criterion priced a weak answer while the
penalty priced an actionable instruction. The same test should be applied here —
**a penalty fires only when an artifact would cause harm if sent as written**,
not when a criterion is merely unmet. Expect to ship with two of the four, not
all four; `false_resolution_claim` and `material_cross_output_contradiction` are
the strongest candidates to fold into criteria instead.

---

## 12. Ambiguity audit

Risks identified before any file is written.

| Risk | Mitigation |
|---|---|
| **"Summarised" read as inconsistent** | The largest scoring risk. Every consistency criterion must carry an explicit "different level of detail is not a contradiction" clause in its PASS text, not just in design notes. #004's `figures_carried_correctly` shipped without its "not charged twice" clause and the omission is now permanent — the same mistake must not repeat |
| **Style leaking into scoring** | No criterion may reference tone, length or polish. The judge prompt should say plainly that a plain correct message beats a polished leaky one |
| **Four artifacts, unclear boundaries** | The prompt must state the four required outputs and their audiences explicitly. The difficulty is what goes in them, not guessing what they are |
| **"Confidential" underspecified** | `incident-notes.md` should mark the security item as internal in-world — an incident commander would. The judgment being tested is honouring a boundary under pressure, not inferring one from nothing |
| **SLA arithmetic becoming the point** | The contract must make eligibility genuinely undeterminable, not merely hard. If a determined model can compute it, the criterion is measuring arithmetic and belongs in #004 |
| **Length inflation** | Four artifacts invite very long answers. Reasoning-model runs on #004 already reached 80,470 completion tokens against a 96,000 ceiling. **#005 must be generated at 131,072** — see §14 |

---

## 13. Answer-leakage audit

| Check | Design response |
|---|---|
| No source states the correct boundary | The matrix in §6 is evaluator-only. Sources carry facts and in-world markings, never instructions about what to disclose |
| No source states "this is a hypothesis, not a cause" in those words | Slack carries the hunch in natural engineering register; the timeline shows no completed test. The candidate must infer it |
| No source says "do not promise an ETA" | The absence of approval is inferable from who said what to whom, not stated |
| The stale status update is not labelled stale | It carries its own earlier timestamp. Noticing it is superseded is the work |
| The affected tenant set is not pre-computed | `customer-impact.csv` carries per-tenant rows; the subset must be derived |
| SLA ineligibility is not stated | The contract gives rules; the incomplete inputs make the answer undeterminable |
| The prompt does not enumerate the traps | It names four artifacts and four audiences, nothing more |

---

## 14. Calibration risks

| Risk | Note |
|---|---|
| **Judge variance is higher here than in #004** | Communication artifacts admit more legitimate variation than arithmetic. Every criterion needs a concrete anchor — a named fact in a named artifact — not a quality judgment. This is the single biggest threat to the scenario |
| **Four artifacts × 27 criteria is a long judging pass** | #004's judging was already the slow step. Consider fewer criteria with clearer anchors rather than more |
| **Generation ceiling** | Start at **131,072**, already verified accepted on all seven endpoints. #004's 96,000 left only 1.19× headroom after one battery, and a ceiling cannot be raised mid-scenario without disqualifying it |
| **The rubric text is the contract** | Ship every scoring nuance *in the rubric YAML*, not in a design note. #004 proved the design note does not travel |
| **Ceiling on scores** | If four artifacts are individually easy, strong models may cluster at 95+. The consistency and boundary criteria are what should separate them; if calibration shows they do not, the incident is not messy enough |

---

## 15. Recommendation

**Build Read the Room as #005.** The taxonomy strengthened the case rather than
merely confirming it: communication to an audience and cross-output consistency
are not thin in MondayBench, they are **absent**, and cross-output consistency
cannot be added to any single-output scenario at all. That makes #005
structurally necessary rather than merely desirable.

**Two changes to the concept, both from the taxonomy:**

1. **Promote information boundaries from a supporting capability to a
   co-headline one.** The original concept treats confidentiality as one trap
   among several. The taxonomy shows the current coverage is two criteria on
   which every model scores 100% — the bar is not being tested at all. The
   boundary matrix, not the writing, should carry the most points alongside
   consistency. The rubric weights in §10 reflect this.

2. **Do not try to fix temporal reasoning here.** It is the capability every
   model is worst at (mean 61.0%) on the thinnest evidence (14 points), and it
   is tempting to load #005 with timeline arithmetic. Resist it: a scenario that
   tries to be both a communication test and a temporal-reasoning test will
   calibrate as neither. #005 should carry only the temporal reasoning the
   incident naturally needs. **Temporal reasoning is the strongest candidate for
   #006** and deserves its own scenario.

**The one honest argument against #005** is that judge variance on communication
artifacts is genuinely higher than on arithmetic, and MondayBench's judge is
recorded rather than sampled — so variance cannot be measured by re-judging.
That is a real limitation and it does not disqualify the scenario, but it does
mean every criterion must anchor on a named fact in a named artifact. A rubric
of the form "the CEO briefing is appropriately concise" would be unscoreable and
must not be written.

### What happens next

1. **Finish monday-004.** Nothing here proceeds until its official battery is
   complete and published. #005 must not compete for attention with a scenario
   that is four runs from done.
2. Publish Overall v1 once #004 is official — the release is already declared
   and pinned in `overall-releases.yaml`, awaiting only a status flip.
3. Extend the capability profiles with #004, which gives `business_judgment`,
   `data_cleaning` and `entity_resolution` their first official coverage and may
   change the sparse-capability picture.
4. Then build #005 from this document, sources first, ground truth second,
   rubric third — the order that worked for #004.
