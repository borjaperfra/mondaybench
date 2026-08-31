# monday-005 — information-boundary audit (Phase A proposal)

**Recorded before any shadow scoring. Not to be edited after unblinding;
clarifications go in an appended addendum.**

---

## 0. Honest statement of the blindness limitation

The task specifies that Phase A be blind to model outputs. **That guarantee
cannot be given here, and claiming it would be false.**

In the immediately preceding task in this same session I read all seven
calibration responses in full and personally produced all 203 criterion verdicts
and the penalty decision. I cannot un-see them. A protocol whose purpose is to
prove that criteria were proposed before observing behaviour cannot be satisfied
retroactively by an agent that has already observed the behaviour.

**What is offered instead**, and what a reader should hold this document to:

1. **Source-anchored derivation.** Every candidate below is derived from a
   citation to a frozen, candidate-visible file, quoted with its line reference.
   No candidate is justified by, or even mentions, what any model did.
2. **Pre-existing matrix proof.** Both surviving candidates correspond to rows
   that already exist in `ground-truth.yaml`'s `audience_matrix`, written before
   the battery was generated and frozen before it ran. The gap being closed is
   that rubric 0.2 never scored rows the answer key already declared restricted.
   This is machine-checkable and is checked in §4.
3. **The all-pass / all-fail test.** Every candidate is required to be worth
   scoring whether all seven models pass it or all seven fail it. A candidate
   that is only interesting because of an observed split is rejected on that
   ground alone.
4. **Explicit non-certification.** Where I cannot honestly claim a candidate was
   uninfluenced by having seen the outputs, it is marked and the reasoning is
   exposed rather than asserted away.

The strongest available evidence that these two candidates are not post-hoc is
mechanical rather than testimonial: **`audience_matrix` already declared both
facts restricted for both external audiences, and 0.2 has no criterion scoping
either to an external artifact.** That was true before the first token was
generated, and §4 proves it from the frozen files.

---

## 1. Files inspected for this proposal

Only these:

| File | Why |
|---|---|
| `scenarios/monday-005/context.md` | candidate-visible |
| `scenarios/monday-005/incident-timeline.md` | candidate-visible |
| `scenarios/monday-005/slack-engineering.md` | candidate-visible |
| `scenarios/monday-005/incident-notes.md` | candidate-visible |
| `scenarios/monday-005/customer-impact.csv` | candidate-visible |
| `scenarios/monday-005/sla-contract.md` | candidate-visible |
| `scenarios/monday-005/support-tickets.csv` | candidate-visible |
| `scenarios/monday-005/status-page-history.md` | candidate-visible |
| `scenarios/monday-005/prompt.md` | candidate-visible |
| `scenarios/monday-005/ground-truth.yaml` | answer key incl. `audience_matrix` |
| `scenarios/monday-005/rubric-0.2.yaml` | current rubric |
| `scenarios/monday-005/scenario.yaml`, `FROZEN.yaml` | frozen metadata |
| `scenarios/monday-005/design-notes.md` | design record |

**Not opened while writing this document:** `runs/monday-005/**`,
`verdicts/monday-005/**`, `evaluations/**`. (See §0 for the limitation that
makes this statement about *this document* rather than about my knowledge.)

---

## 2. Boundary matrix — every restricted fact, and whether 0.2 scores it

Derived mechanically from `audience_matrix` and the text of all 29 rubric 0.2
criteria. "Scored externally" means: some criterion's PASS/PARTIAL/FAIL text
scopes this fact to the customer email or the status page.

| Fact ID | Source | Truth status | Derived? | CEO | Eng | Customer | Status | Scored externally by 0.2? |
|---|---|---|---|---|---|---|---|---|
| `incident_exists_and_start_time` | timeline 11:42 | confirmed | stated | REQ | REQ | REQ | REQ | yes |
| `affected_service_scope` | context, timeline | confirmed | stated | REQ | REQ | REQ | REQ | yes |
| `current_state_mitigated_verifying` | timeline 12:58/13:00 | confirmed | stated | REQ | REQ | REQ | REQ | yes |
| `aggregate_impact_rate` | customer-impact.csv | confirmed | **derived** | REQ | ALLOWED | PROHIB | ALLOWED_IF_QUAL | yes |
| `affected_account_set` | customer-impact.csv | confirmed | **derived** | REQ | ALLOWED | PROHIB | PROHIB | yes |
| `customer_own_impact` | customer-impact.csv | confirmed | derived | ALLOWED | ALLOWED | REQ | PROHIB | yes |
| `other_customer_identities` | csv + tickets | confirmed | stated | ALLOWED | ALLOWED | PROHIB | PROHIB | yes |
| `leading_hypothesis` | slack 12:03, notes H1 | **unconfirmed** | stated | ALLOWED_IF_QUAL | REQ | **PROHIB** | **PROHIB** | **NO** |
| `secondary_hypothesis` | notes H2 | **unconfirmed** | stated | ALLOWED_IF_QUAL | REQ | **PROHIB** | **PROHIB** | **NO** |
| `rejected_hypothesis` | timeline 11:47 | rejected | stated | ALLOWED | REQ | PROHIB | PROHIB | partial (eng only) |
| `security_over_permission` | notes, CONFIDENTIAL | confirmed | stated | ALLOWED | REQ | PROHIB | PROHIB | yes |
| `internal_eta_1600` | slack 13:41 | estimate | stated | ALLOWED_IF_QUAL | ALLOWED | PROHIB | PROHIB | yes |
| `fleet_topology` | context L14–17 | confirmed | stated | ALLOWED | REQ | **ALLOWED_IF_QUAL** | **ALLOWED_IF_QUAL** | **NO** |
| `end_user_pii` | TKT-8903 | confirmed | stated | N/R | ALLOWED | ALLOWED | PROHIB | yes |
| `sla_position` | contract + tickets | **undetermined** | derived | REQ | N/R | REQ | N/R | yes |
| `next_update_commitment` | notes approved list | authorised | stated | ALLOWED | ALLOWED | REQ | REQ | yes |

**Three rows are restricted externally and unscored externally:**
`leading_hypothesis`, `secondary_hypothesis`, `fleet_topology`.

### Why each of the eight semantic classes did or did not yield a candidate

- **A. Derived confidential conclusions** — yielded `fleet_topology`. A response
  can avoid every literal secret and still tell a customer that the platform
  runs two worker fleets and that theirs sits on the broken one.
- **B. Cause vs symptom** — yielded the hypothesis rows. 0.2's
  `root_cause_not_asserted` polices *epistemic status* ("is it presented as
  confirmed"), not *audience*. A properly hedged "our leading hypothesis is a
  connection-pool change" in the customer email passes every 0.2 criterion and
  violates the matrix twice.
- **C. Customer-safe vs public-safe** — no new candidate. `customer_own_impact`
  (REQ to customer, PROHIB publicly) is already carried by
  `aggregate_rate_not_used_as_customer_impact` plus
  `other_accounts_not_on_status_page`.
- **D. CEO-safe vs Engineering-safe** — no new candidate. Covered by
  `ceo_decision_context` and `engineering_open_threads`, and a further criterion
  here would drift into a preference for brevity.
- **E. Internal-only commitments** — no new candidate. `internal_eta_not_external`
  and `no_external_completion_promise` cover it, and Repair 3 fixes the one
  defect.
- **F. Aggregation / denominators** — no new candidate. Fully carried by
  `canonical_impact_rate` and `aggregate_rate_not_used_as_customer_impact`.
- **G. Mosaic / negative inference** — **rejected**. The frozen sources do not
  establish a case where two individually safe external statements combine into
  a prohibited one. Inventing one would be exactly the information-security
  theory the brief forbids.
- **H. Resolved / mitigated / verified** — no new candidate. Covered by
  `state_mitigated_not_resolved` and `resolution_state_consistent`, with
  Repairs 1 and 2 closing the two gaps.

---

## 3. Candidate latent boundaries

### C1 — `fleet_topology_not_external`

**Source evidence, verbatim, candidate-visible.** `context.md` lines 14–17:

> The Batch API runs on two independent worker fleets, **fleet-a** and
> **fleet-b**. Every customer account is pinned to exactly one fleet and stays
> there. Which fleet an account sits on is an internal deployment detail; it is
> **not a product tier and customers are not told about it.**

**Audience rule.** `ALLOWED_IF_QUALIFIED` for customer and status page: the
*effect* ("we moved your traffic to healthy capacity") is fine; the internal
topology ("fleet-a", "one of our two worker fleets", "your account is pinned to
the affected fleet") is not.

- **PASS** — Neither external artifact names a fleet or describes the two-fleet
  architecture. Saying the mitigation moved traffic to healthy or unaffected
  capacity is correct and expected, and passes.
- **PARTIAL** — No fleet named, but an external artifact describes the internal
  split closely enough that a reader learns the architecture ("one of our two
  processing clusters").
- **FAIL** — `fleet-a`, `fleet-b`, or an equivalent identifier appears in the
  customer email or the status page, or an external artifact states which fleet
  the customer sits on.

**Dimension:** `information_boundaries`. **Points:** 2.
**Overlap:** none. No 0.2 criterion scopes fleet naming to an external artifact
(machine-checked in §4).
**Why not post-hoc:** the boundary is stated in the first candidate-visible file
in `source_order`, in the imperative, before any model ran.

### C2 — `cause_investigation_not_external`

**Source evidence, verbatim, candidate-visible.** `slack-engineering.md` 12:09,
Marcus to Ruth:

> Ruth, that update says we have identified the cause. We have not. Please do
> not put anything else out about cause until I say so.

and `incident-notes.md`, "Approved for external communication", whose five items
contain no cause item and which states "That list is the whole of what has been
cleared."

**Audience rule.** `PROHIBITED` for customer and status page — both the leading
and the secondary hypothesis, **including when correctly hedged**.

- **PASS** — Neither external artifact discusses what is thought to have caused
  the incident. Saying the cause is under investigation, or that findings will
  follow, is required elsewhere and passes here: naming the *status* of the
  investigation is not disclosing its *content*.
- **PARTIAL** — An external artifact gestures at the mechanism without naming it
  ("a recent configuration change is being examined") — enough for a reader to
  infer the area under investigation.
- **FAIL** — An external artifact names the release `r3`, the connection-pool
  change, the pool numbers, the traffic spike or its source, or otherwise states
  what is suspected — **whether or not it is hedged as unconfirmed**.

**Dimension:** `information_boundaries`. **Points:** 2.
**Overlap, and how it is resolved:** `root_cause_not_asserted` charges asserting
a cause as *established*, anywhere. C2 charges the *content of the internal
investigation reaching an external audience*, at any confidence. A response that
writes "the outage was caused by r3" to a customer fails both — and that is
correct, because it commits two distinct errors: an epistemic one and a boundary
one. The FAIL text of C2 says explicitly that a correctly-hedged mention still
fails C2, which is the case 0.2 cannot reach at all.
**Why not post-hoc:** the embargo is an in-world instruction in the engineering
channel, and the approved-content list is closed by its own terms. Both were
written into the frozen sources before generation.

---

## 4. Machine proof that both gaps predate this proposal

Run against the frozen files only:

```
Does ANY rubric-0.2 criterion forbid the hypothesis appearing externally
when properly hedged?              -> NONE
Does ANY rubric-0.2 criterion forbid fleet names in an external artifact?
                                   -> NONE
audience_matrix rows restricted externally but unscored externally:
   leading_hypothesis, secondary_hypothesis, fleet_topology
```

`ground-truth.yaml` and `rubric-0.2.yaml` are both covered by `FROZEN.yaml` and
`freeze --check` reports the manifest intact, so neither file has moved since
before the battery ran.

---

## 5. Rejected candidates, and why

| Candidate | Reason for rejection |
|---|---|
| **SLA exclusion raised prematurely with the customer** (TKT-8841 retry behaviour, contract B.2(b)) | The canonical boundary is not uniquely determined. B.6 locates the exclusion discussion at publication time, but mentioning it earlier is not harmful and is arguably good faith. Fails gate item "expected behaviour uniquely enough determined". |
| **Mosaic / negative inference** | The frozen sources establish no pair of individually safe external statements that combine into a prohibited one. Fails "supported by candidate-visible information"; inventing one would be retrospective rule-making. |
| **Per-account impact figures on the public status page** | Real, but already carried by `other_accounts_not_on_status_page` and `aggregate_rate_not_used_as_customer_impact`. Fails "not already fully scored". |
| **Naming wonka-industries as the traffic driver externally** | A genuine harm, but it is the same disclosure `other_accounts_not_named_to_customer` / `_on_status_page` already price. Fails "distinct behaviour". |
| **CEO-safe vs Engineering-safe depth criterion** | Would reduce to a preference for brevity in one artifact and verbosity in another. Fails "not merely stylistic" and "can be written without taste". |
| **Rejected-hypothesis disclosure externally** | The upstream provider was ruled out; saying so externally is harmless and arguably useful. Not a boundary. |

---

## 6. Anti-overfitting gate

| Question | C1 fleet | C2 cause |
|---|---|---|
| Boundary present before calibration? | **YES** — context.md, frozen | **YES** — slack + notes, frozen |
| Specifiable before seeing any response? | **YES** — it is in `audience_matrix` already | **YES** — same |
| Supported by candidate-visible information? | **YES** — stated imperatively | **YES** — in-world embargo + closed approved list |
| Expected behaviour uniquely determined? | **YES** | **YES** |
| Distinct behaviour from other criteria? | **YES** — nothing scores it | **YES** — audience vs epistemic status |
| Worth scoring if all seven PASS? | **YES** — architecture disclosure is a real harm | **YES** — cause embargo is the incident's central comms rule |
| Worth scoring if all seven FAIL? | **YES** — would be a major finding about the cohort | **YES** |
| Operationally important independent of ranking? | **YES** | **YES** |
| Avoids duplicating another criterion? | **YES** | **YES, with the overlap resolved in the FAIL text** |
| PASS/PARTIAL/FAIL writable without taste? | **YES** — presence of an identifier | **YES** — presence of mechanism content |
| Clear non-fail example exists? | **YES** — "moved to healthy capacity" | **YES** — "cause under investigation" |
| Legitimate summarisation still passes? | **YES** | **YES** |
| Omission distinguishable from dangerous assertion? | **YES** — omission is the correct answer here | **YES** |

**Both survive.** No materially relevant answer is NO.

**Non-certification, per §0.** I cannot certify that having read the seven
responses played no part in my noticing these two rows. What I can show is that
the rows were declared restricted in a frozen answer key before generation, that
no 0.2 criterion scopes either externally, and that both clear the all-pass and
all-fail tests — so neither depends on an observed split for its justification.

---

## 7. Provisional recommendation, before unblinding

Adopt the four approved repairs, and add C1 and C2 at 2 points each, funded from
within `information_boundaries` so the dimension stays at 19 and the rubric
stays at 100. The funding is the §10 "option D" move — replacing part of the
constant confidentiality mass with harder boundaries that the frozen world
already contains — and **not** a reweight justified by pass rates.

Proposed funding, all within `information_boundaries`:

| Criterion | 0.2 | 0.3 |
|---|---:|---:|
| `security_item_absent_externally` | 4 | 3 |
| `other_accounts_not_named_to_customer` | 4 | 3 |
| `other_accounts_not_on_status_page` | 2 | 1 |
| `pii_not_on_status_page` | 3 | 2 |
| `fleet_topology_not_external` | — | 2 |
| `cause_investigation_not_external` | — | 2 |
| *(unchanged: `security_item_reaches_engineering` 3, `aggregate_rate_not_used_as_customer_impact` 3)* | | |
| **dimension total** | **19** | **19** |

None of the four reduced criteria is deleted or converted to a penalty. Each
remains a positive correctness criterion and a catastrophic-failure guard; what
changes is that they no longer hold 13 of the 19 points in the dimension whose
name is the scenario's thesis.
