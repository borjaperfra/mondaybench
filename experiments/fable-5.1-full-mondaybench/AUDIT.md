# Scoring and calibration audit — Fable 5.1 provisional results

**Date:** 2026-09-02 · **Inferences run: zero.** No generation was repeated, no
frozen artefact touched, no official leaderboard changed.
**Outcome: SCORING ISSUE FOUND.** Ten verdicts corrected across four scenarios.
Provisional overall **95.97 → 94.90**.

Pre-audit figures preserved verbatim in `five-scenario-summary.PRE-AUDIT.json`.

---

## 0. What made this audit possible, and what it exposed

The first pass judged Fable against each scenario's frozen **rubric** and
**ground truth**. It did not use two artefacts that the published models were
judged with:

1. **`evaluators/<scenario>/judge-prompt.md`** — a per-scenario judge prompt,
   fingerprinted in every published evaluation (`prompt_fingerprint`).
2. **`verdicts/<scenario>/*.jsonl`** — 21 published verdicts per scenario with
   per-criterion evidence, which is the operative record of how each band was
   actually applied.

Two rules in those judge prompts change outcomes:

* **"If a response sits between two labels, choose the lower."** Present in all
  of them (monday-002: *"If ambiguous, choose lower"*). The first pass resolved
  three ties **upward**, reasoning from band descriptions rather than from this
  rule.
* **monday-003 only:** *"`factual_plan_accuracy` is scored against
  `factual_anchors` in the answer key and against nothing else."* The first pass
  checked against `work-items.csv` and never read `factual_anchors`.

Everything below follows from reading those two sources.

---

## 1. Judgment calls audited

Twelve calls carried real point risk. Ten more were re-verified and stand.

### 1.1 CORRECTED — monday-003 `factual_plan_accuracy`, runs 2 and 3

| | |
|---|---|
| **Fable run 2** | *"pricing page (3h, **Wed 17:00** deadline)"* and *"onboarding launch prep (2h, **Thu 12:00** deadline)"* |
| **Fable run 3** | *"onboarding launch prep (2h, **due Thu 12:00**)"* and *"Board pack: … well before **Thu 10:00** / Friday board"* |
| **Answer key** | `factual_anchors.external_deadlines`: `pricing_page: "2026-09-24T17:00 - Thursday"`, `onboarding_launch: "2026-09-25T12:00 - Friday"`, `board_pack_non_revenue: "2026-09-25T10:00 - Friday"` |
| **Rubric** | PASS "carries the supplied deadlines … through without substituting different values". PARTIAL "**One** minor factual substitution that does not materially alter the plan". FAIL "**Several** factual substitutions, or one that materially distorts the plan" |
| **First-pass verdict** | PARTIAL (2.5) — two is "more than one, fewer than several", character matched PARTIAL |
| **Corrected verdict** | **FAIL (0.0)** |

**Precedent — decisive and identical.** `glm5.3-flash__002` got **FAIL** with:

> *"two substituted deadlines, both used as planning targets: 'onboarding launch
> prep (deadline Thu 12:00)' — it is Friday 12:00 … and 'pricing page (Wed 17:00
> deadline)' — it is Thursday"*

That is **the same pair of errors as Fable run 2**. The published boundary across
21 verdicts is unambiguous:

| substitutions | verdict | cases |
|---|---|---|
| 0 | PASS | 15 |
| 1 | PARTIAL | `glm5.2__002` ("one substitution … Wed 15:00"), `glm5.3-flash__001` ("one substitution … Pricing page public: Wed") |
| 2 | **FAIL** | `glm5.3-flash__002`, `mimo-v2.5__001`, `qwen3.6__001` |
| 3 | FAIL | `qwen3.6__002` |

**Does the error change the action?** No — and that is *precisely* why the
published judge still failed it. glm5.3-flash__002's own FAIL note says the two
were "used as planning targets"; nothing downstream moved for it either, and it
still failed. The materiality clause is the *alternative* FAIL trigger, not a
requirement. Fable run 2's page is scheduled after approval clears and run 3's
onboarding launch is unscheduled, so neither error moves a critical path or
could cause an incorrect execution. Two substitutions is sufficient on its own.

**Impact:** run 2 97.5 → 95.0, run 3 97.5 → 95.0. monday-003 **98.33 → 96.67**.

**Verdict: CHANGE TO FAIL.**

### 1.2 CORRECTED — monday-002 `schedule_feasibility`, A2 and A3

| | |
|---|---|
| **Fable A2** | *"review would have to run 09:10–09:35 … and deploy run 09:35–10:20 with zero margin. Marcus isn't online until 09:15 to submit the diff … **Not viable today.**"* |
| **Fable A3** | *"zero slack at both ends, and Marcus isn't even online until 09:15"* → *"**Do not choose Option B — infeasible** under today's availability"* |
| **Ground truth** | Review from 09:07 finishes ~09:32; deploy 09:32–10:17 inside Marcus's window; verification 10:25–10:45; Sam 10:45–11:00. **B is viable and is the correct choice.** |
| **First-pass verdict** | PARTIAL (3.0) — "constraints understood, conclusion inconsistent with its own timing" |
| **Corrected verdict** | **FAIL (0.0)** |

**Precedent.** The published line is drawn at *asserting infeasibility*, not at
how nearly right the arithmetic is:

* `glm5.3-flash__001` **FAIL** — *"understates the real 3-minute margin and **concludes infeasibility**"*
* `glm5.3-flash__002` **FAIL** — *"'zero slack anywhere'; the review can start at 09:07 and the deploy ends 10:17"*
* `glm5.2__002` **FAIL** — *"'Option B cannot fit Marcus's 09:15-10:20 window …' — the review runs before Marcus arrives"*
* `deepseek-v4-flash__002` **FAIL** — *"'… prevents completion before noon'"*
* `qwen3.8-flash__002` **FAIL** — *"'If started at 09:15, completion is ~10:45' — the review can start at 09:07"*

PARTIAL is reserved for responses that **do not** assert infeasibility:
`glm5.2__001` and `qwen3.8-flash__001` ("every constraint is identified, but no
B schedule is committed"), `glm5.3-flash__003` ("correctly shows it fits, but no
verification or Sam timings"), `qwen3.8-flash__004` ("the B arithmetic is right
for the anchor it picks … and it identifies the crux").

Fable A2 and A3 both write *"Not viable today"* / *"infeasible"*. That is the
FAIL side. A1, which commits a working B schedule, matches `deepseek__001` and
`qwen3.8-flash__003` PASS and **stands at PASS**.

**Impact:** A2 91.5 → 88.5, A3 93.0 → 90.0.

**Verdict: CHANGE TO FAIL for A2 and A3. KEEP PASS for A1.**

### 1.3 CORRECTED — monday-002 `ownership_supersession`, A1 (in Fable's favour)

| | |
|---|---|
| **Fable A1** | *"Comms: Sarah out; Daniel holds final announcement + Atlas list and sends only after Sam confirms rollout open."* |
| **First-pass verdict** | PARTIAL (2.5) — "handoff traced, but the stale user-as-sender task is never displaced" |
| **Corrected verdict** | **PASS (5.0)** |

**Precedent.** `glm5.3-flash__001` **PASS**:

> *"'Sarah is out; Daniel holds Julia's final draft + Atlas recipient list and
> sends after Sam confirms rollout is open' — the whole handoff chain"*

That is the same sentence. `deepseek-v4-flash__002` PASS is even shorter: *"the
handoff is traced"*. Eight of 22 published verdicts are PASS and most cite the
handoff alone — the published judge did **not** require the stale task to be
separately displaced. The first pass invented that requirement.

**Impact:** A1 92.0 → 94.5. Net for monday-002: **92.17 → 91.00**.

**Verdict: CHANGE TO PASS.**

### 1.4 CORRECTED — monday-001 `friday_conversion_unknown`, runs 1 and 3

| | |
|---|---|
| **Fable run 1** | *"Julia and Noah both noticed something 'horrible' on the dashboard but nobody verified. Could be Friday noise — needs a check."* |
| **Fable run 3** | *"nobody verified; chalked up to possibly noisy Friday traffic. Worth a quick dashboard check."* |
| **Rubric** | PASS "Explicitly says Friday conversion **cannot be verified from the provided data**" |
| **First-pass verdict** | PASS (3.0) |
| **Corrected verdict** | **PARTIAL (1.5)** |

**Precedent.** 19 of 21 published verdicts are PARTIAL, with a repeated reason:
*"flagged, but no statement that the provided data cannot settle it"* —
`deepseek__001` (*"real or noise? Needs a quick check"*), `glm5.2__001`
(*"Needs a look at the dashboard"*), `mimo__001`, `qwen3.8-flash__001`. Only two
runs PASS, both glm5.3-flash, for naming the gap in the material directly:
*"no conversion data was shared"* / *"No data provided"*.

Fable runs 1 and 3 are the PARTIAL wording. **Run 2 stands at PASS**: its §4
says *"No actual numbers were shared"*, which is the glm5.3-flash PASS standard.

**Impact:** run 1 98.5 → 97.0, run 3 98.5 → 97.0. monday-001 **98.50 → 97.50**.

**Verdict: CHANGE TO PARTIAL for runs 1 and 3. KEEP PASS for run 2.**

### 1.5 CORRECTED — monday-004 `figures_carried_correctly`, all three runs

| | |
|---|---|
| **Fable run 1** | *"5 of 31 customers active on 1 October churned (16% logo churn)"* and *"4 of 9 starter customers (44%)"* |
| **Fable run 2** | *"SMB: 4 of 13 logos (31%); €123.6k of **€469.2k ARR (26%)**"* |
| **Fable run 3** | *"four of the **seven** legacy Starter customers (57% of that cohort)"* |
| **First-pass verdict** | PASS (3.0), on the rubric's note that "a wrong churn denominator" belongs to `segment_retention_quantified` and is not charged twice |
| **Corrected verdict** | **PARTIAL (1.5)** |

**Precedent — this is where the first pass read the rubric against practice.**
`glm5.3-flash__004` was charged in **both** criteria: `segment_retention_quantified`
**PASS** (it quantified correctly at "SMB 4 / 13 (30.8%)") *and*
`figures_carried_correctly` **PARTIAL** for:

> *"'5 of 31 logos churned (16.1%)' uses the closing population as the
> denominator where the opening 36 gives 13.9%"*

That is **Fable run 1's exact error and figure.** Likewise `glm5.2__003`
PARTIAL for *"'4 of ~14 Starter customers churned' where the plan holds 13 …
neither of which is 14"*, and `glm5.2__005` PARTIAL for a segment ARR base
matching neither the opening nor the active figure — Fable run 2's €469.2k has
the same defect.

The operative division is narrower than the rubric note suggests: the base used
**for the retention quantification itself** belongs to
`segment_retention_quantified`; **any other derived rate** built on a wrong base
is charged here. The PASS bar is also very high — 2 PASS in 21, both with
exhaustive "checked against the CSVs" evidence and no listed errors.

**Impact:** run 1 95.0 → 93.5, run 2 86.5 → 85.0, run 3 91.0 → 89.5.
monday-004 **90.83 → 89.33**.

**Verdict: CHANGE TO PARTIAL, all three runs.**

### 1.6 KEEP — monday-004 `segment_retention_quantified`, all three PARTIAL

Correctly classified. Per the rubric this is a **denominator selection error**,
not arithmetic, not state reconstruction, not a material factual error, and not
a recommendation error: the ranking is right in all three runs and the arithmetic
on the chosen base is right. The rubric's PARTIAL band names it exactly — *"one
denominator or base is wrong in a way that does not change which population is
worst; or the segment and plan framings are mixed without saying so"*.

Precedent matches: `qwen3.6__003` PARTIAL for *"4/9 customers churned (44%)"* —
Fable run 1's identical figure. `glm5.2__005` PASS used the correct segment base
(18), `glm5.3-flash__004` PASS the correct plan base (13). Fable uses neither
correctly in any run. **KEEP PARTIAL.**

### 1.7 KEEP — monday-004 Enterprise-over-Pro prioritisation, runs 2 and 3

`absolute_vs_scalable_economics` PARTIAL and `product_focus_supported` PARTIAL.
The published band structure:

* **FAIL** when Enterprise is chosen on absolute revenue as the leading reason —
  `glm5.2__005` (*"first rationale 'Enterprise generates 87% of revenue …'"*),
  `gemma4__005` (*"Protecting this EUR 659k/month revenue is the priority"*).
* **PASS** when Enterprise is chosen on cost-adjusted economics —
  `deepseek__006` (*"A 10% reduction in Enterprise infra + support costs would
  add roughly EUR 46.5k/month — more than Pro's entire monthly contribution"*).
* **PARTIAL** when both are present — `glm5.2__005`'s
  `absolute_vs_scalable_economics` (*"then concludes 'Strongest: Enterprise' and
  opens the engineering recommendation on it"*).

Fable runs 2 and 3 carry margin compression (cost-adjusted) **and** frame the
decision on "87% of MRR" / "€6.8M of ARR exposed". They sit between the PASS and
FAIL cases, and the tie-break rule puts them at PARTIAL. Run 1 chose Pro on four
signals and matches `deepseek__004` PASS. **KEEP.**

### 1.8 KEEP — monday-004 `segment_recommendation`, run 3 PASS

`qwen3.8-flash__004` **PASS**: *"Do not reduce investment in SMB as a whole.
Reduce or reprice investment in the Starter plan, not necessarily the SMB
segment. Investigate why Starter customers churn."* Fable run 3 is the same
shape — declines the segment cut, separates plan from segment explicitly, and
requires exit interviews and segment economics first. Runs 1 and 2 match
`glm5.3-flash__005` PARTIAL (decline plus a hedged acquisition pause). **KEEP.**

### 1.9 KEEP — monday-002 material_hallucination **not** applied

The invented premise — *"Marcus isn't online until 09:15 to submit the diff"*,
against Priya's *"I can do delta reviews asynchronously from a submitted diff"* —
takes no penalty, and that is precedent-consistent.

Published `MATERIAL_HALLUCINATION` on monday-002 fires only on **asserted facts
that would misdirect action in a deliverable**: `gemma4__002` (tickets asserted
as the cause of a procurement delay, in a board pack), `qwen3.6__003` (usage
decline asserted as the cause of expansion cuts), `qwen3.8-flash__002` (source
authority stated backwards). `MAJOR_PLANNING_ERROR` fires when the *recommended*
plan cannot run — Fable's recommended Option A is executable in all three runs.

Most directly: **`qwen3.8-flash__004` uses the same Marcus-submits anchor** —
*"if Marcus submits the diff at his 09:15 start, review ends 09:40"* — and took
`schedule_feasibility` PARTIAL with **no penalty**. And every published model
that concluded B infeasible took a `schedule_feasibility` FAIL and no penalty.
Fable now takes the same FAIL and the same absence of penalty. **KEEP: no
penalty.**

### 1.10 KEEP — monday-004 `conversion_rate_vs_absolute_volume`, all three PASS

The first pass wavered here; the precedent settles it. PASS is earned by a
two-month table carrying leads **and** trials for every channel —
`glm5.2__005` (*"carries September and October leads and trials for all four
channels"*), `glm5.3-flash__003`. PARTIAL is for rates **without** absolute
conversion counts (`glm5.2__004`: *"no absolute conversion counts"*). All three
Fable runs carry leads, trials and rates for all four channels in both months.
**KEEP PASS.**

### 1.11 KEEP — monday-001 `umbrella_error_rate` PARTIAL and `no_false_priorities` PASS

`umbrella_error_rate`: PARTIAL precedent is *"quotes the peers' latency, but no
request volume and no error rate"* (glm5.3-flash, all three). Fable quotes peers
on errors and latency, cites neither the 94,217 volume nor a rate, in all three
runs. **KEEP PARTIAL** — identical to GLM 5.3 Flash's published treatment.

`no_false_priorities`: the PARTIAL/FAIL triggers are all *resolved* items (Acme
close-out), *delegated* items, or Globex, which the source says has no urgency.
Fable keeps Globex and task cleanup below the churn analysis in all three runs.
Initech at #2 is an open inbound customer request, not a resolved or delegated
item. **KEEP PASS.**

### 1.12 KEEP — monday-003 `pricing_dependency`, `marcus_reserved_for_sso`, `concurrent_sso_and_contoso`, all PASS

The three most discriminating monday-003 criteria after `factual_plan_accuracy`,
checked mechanically:

* `pricing_dependency` (8 PASS / 10 PARTIAL / 3 FAIL) — PASS needs **both** the
  approval gate on the public page and the mockup route freeing the pack. All
  three Fable runs state both explicitly. PARTIAL precedent has exactly one half.
* `marcus_reserved_for_sso` (13/8/0) — PARTIAL when the freed capacity goes to
  the substitutable Contoso patch. Fable moves it to Daniel in all three runs.
* `concurrent_sso_and_contoso` (12/9/0) — PARTIAL when the chains serialise
  through Marcus. Fable runs them concurrently in all three.

**KEEP PASS.**

---

## 2. Adversarial review of the perfect scores

### monday-005: 100.0 / 100.0 / 100.0 — **stands**

Checked against the mechanical PARTIAL/FAIL trigger of every criterion that
discriminated in the published set. Two published models also hit 100.0 on
individual runs there (GLM 5.2 run-002, and GLM 5.3 Flash at 99.0 twice).

| Criterion | Published split | Trigger for non-PASS | Fable, all 3 runs |
|---|---|---|---|
| `status_page_publishable` | 10 / 11 / 0 | status page "never states that the other APIs are unaffected" | *"Other Northstar APIs are unaffected"* present in all three |
| `security_item_reaches_engineering` | 10 / 2 / 9 | absent from both internal artefacts, or in a do-not-publish list with no owner | SEC-411 routed with ticket, owner (Marcus), separation and remediation in all three engineering updates |
| `rejected_hypothesis_recorded` | 14 / 3 / 4 | "ruled out at 11:47 with no reason given" | reason given in all three (*"provider green; Files API on same provider healthy"*) |
| `canonical_impact_rate` | 15 / 5 / 1 | no aggregate, or a wrong denominator | 17,602 / 58,900 = 29.9% in all three; the 2.1% platform figure explicitly refused as headline |
| `next_update_commitment_external` | 17 / 4 / 0 | customer email does not commit | both external artefacts commit in all three |
| `fleet_topology_not_external` | 18 / 3 / 0 | external artefact says "healthy worker fleet" | no fleet word in any external artefact |
| `internal_eta_not_external` | 18 / 3 / 0 | 16:00 internally without internal-only marking | marked internal-only in all three |
| `artifacts_current_as_of_snapshot` | 20 / 1 / 0 | status page headed 14:25 at a 14:20 snapshot | headed exactly `14:20` in all three |
| `sla_undetermined_with_process` | 18 / 2 / 1 | measured over the incident window instead of the calendar month | calendar month, after month end, across Covered Services, 10 business days, 30-day claim — all three |

No omission, contradiction, invented constraint, temporal error, wrong owner or
wrong denominator found. The one soft spot — run 2's *"a further update by 15:00
UTC today with the outcome of our monitoring"* — is tested in the strict
scenario below; the published FAIL/PARTIAL cases both attach a clock to
**recovery** (*"We expect full recovery shortly"*, *"expect to confirm full
recovery within the next hour"*), which run 2 does not.

### monday-003 run 1: 100.0 — **stands**

Two published runs also scored 100.0 (`glm5.3-flash__003`, `qwen3.8-flash__002`).
Run 1's `factual_plan_accuracy` was re-checked against `factual_anchors`
line-by-line: every deadline, duration, owner, availability window and
commitment term it uses is correct, including the two that caught four other
models (`pricing_page` Thursday 17:00 is not asserted at all, `onboarding_launch`
is stated as *"before Fri 12:00"*). Names and figures verified against sources.

---

## 3. Judge consistency

**Same recorded judge, same scoring code — one real difference, now closed.**

| | Published models | Fable experimental |
|---|---|---|
| judge model | `claude-opus-5` | `claude-opus-5` |
| route | `recorded` (in-session), `verdict_source` JSONL — verified in every evaluation | `recorded` (in-session) |
| rubric | 0.2 / 0.2 / 0.3 / 0.3 / 0.4 per scenario | identical files, per scenario |
| evaluator of record | `evaluator-opus5-v0.1` … `v0.5` | same rubric files; no new evaluator id minted |
| `scoring.py` | unmodified | unmodified, same functions |
| noise ladder | `score_false_actions` | same |
| penalty logic | same rubric penalty tables | same; no penalty applied to any Fable run |
| **judge prompt** | `evaluators/<scenario>/judge-prompt.md`, fingerprinted per evaluation (`2725f54f…`, `b10748f5…`, `26067608…`, `45998b3c…`) | **not used in the first pass** |

Every published evaluation records `route: "recorded"`, so the published models
were judged the same way Fable was — by an in-session Opus 5 reading, not an API
call. That much is equivalent.

**The judge prompt is the gap, and it is the direct cause of every correction in
§1.** Its tie-break rule ("choose the lower") produced §1.1, §1.2 and §1.4; its
`factual_anchors` scoping rule produced §1.1. This audit applied both. A future
run of this experiment should read the judge prompts before judging, and the
first pass's `METHODOLOGY.md` should be read as superseded on those points.

Judge temperature is `0` in the config and unapplied in practice for both
(recorded route), so it is not a differentiator. `prompt_fingerprint` for the
Fable verdicts is **absent** rather than matching — recorded as a known
limitation, not an equivalence claim.

---

## 4. Sensitivity analysis

**A. CORRECTED** — only the ten changes forced by precedent or a misapplied rule.
**B. STRICT but defensible** — every remaining ambiguous call at the lowest band
the rubric and a published precedent both permit.
**C. LENIENT but defensible** — every remaining ambiguous call at the highest.

| Scenario | pre-audit | **A CORRECTED** | B STRICT | C LENIENT |
|---|---:|---:|---:|---:|
| monday-001 | 98.50 | **97.50** | 97.00 | 97.50 |
| monday-002 | 92.17 | **91.00** | 90.50 | 92.00 |
| monday-003 | 98.33 | **96.67** | 96.67 | 98.33 |
| monday-004 | 90.83 | **89.33** | 86.67 | 93.67 |
| monday-005 | 100.00 | **100.00** | 99.50 | 100.00 |
| **Overall** | 95.97 | **94.90** | **94.07** | **96.30** |

Corrected per-run scores: monday-001 `97.0 / 98.5 / 97.0` · monday-002
`94.5 / 88.5 / 90.0` · monday-003 `100.0 / 95.0 / 95.0` · monday-004
`93.5 / 85.0 / 89.5` · monday-005 `100.0 / 100.0 / 100.0`.

### Against the field

| Scenario | Fable | vs Qwen 3.8 Flash 95.07 | vs GLM 5.3 Flash 94.93 | vs DeepSeek 91.70 |
|---|---:|---:|---:|---:|
| pre-audit | 95.97 | +0.90 | +1.04 | +4.27 |
| **A CORRECTED** | **94.90** | **−0.17** | **−0.03** | **+3.20** |
| B STRICT | 94.07 | −1.00 | −0.86 | +2.37 |
| C LENIENT | 96.30 | +1.23 | +1.37 | +4.60 |

Envelope **94.07 – 96.30**, width 2.23.

### Which conclusions survive

* **"Fable is in the top performance band" — SURVIVES.** Worst case 94.07 is
  still 2.37 clear of DeepSeek V4 Flash and far clear of everything below.
* **"Fable has the highest numerical provisional overall" — DOES NOT SURVIVE.**
  It was an artefact of the ten scoring errors. Corrected, Fable is 0.17 below
  Qwen 3.8 Flash and 0.03 below GLM 5.3 Flash — a three-way statistical tie —
  and the ordering flips inside the envelope.

**The provisional ordering at the top depends entirely on subjective judge
calls.** A 0.03 gap to GLM 5.3 Flash is moved by a single PARTIAL on one
criterion of one run. No ordering among Fable 5.1, Qwen 3.8 Flash and GLM 5.3
Flash is supportable from this evidence.

---

## 5. Changes applied

All ten are experimental-artefact corrections. `five-scenario-summary.json`
updated in place with `score_pre_audit`, `audit_delta` and `audit_criterion` on
every affected run; the untouched original is preserved as
`five-scenario-summary.PRE-AUDIT.json`.

| # | Scenario / run | Criterion | OLD | NEW | WHY | Δ |
|---|---|---|---|---|---|---:|
| 1 | 003 run 2 | `factual_plan_accuracy` | PARTIAL | FAIL | `glm5.3-flash__002` FAIL on the identical pair of substitutions; two → FAIL across 21 verdicts | −2.5 |
| 2 | 003 run 3 | `factual_plan_accuracy` | PARTIAL | FAIL | same boundary, two substitutions | −2.5 |
| 3 | 002 A2 | `schedule_feasibility` | PARTIAL | FAIL | asserts "Not viable today"; five published FAILs for the same assertion | −3.0 |
| 4 | 002 A3 | `schedule_feasibility` | PARTIAL | FAIL | asserts "infeasible"; same precedent | −3.0 |
| 5 | 002 A1 | `ownership_supersession` | PARTIAL | **PASS** | `glm5.3-flash__001` PASS on the same sentence; the displacement requirement was invented | **+2.5** |
| 6 | 001 run 1 | `friday_conversion_unknown` | PASS | PARTIAL | 19 of 21 PARTIAL for exactly this wording | −1.5 |
| 7 | 001 run 3 | `friday_conversion_unknown` | PASS | PARTIAL | same | −1.5 |
| 8 | 004 run 1 | `figures_carried_correctly` | PASS | PARTIAL | `glm5.3-flash__004` PARTIAL for the identical "5 of 31" denominator | −1.5 |
| 9 | 004 run 2 | `figures_carried_correctly` | PASS | PARTIAL | `glm5.2__005` PARTIAL for an ARR base matching no figure in the pack | −1.5 |
| 10 | 004 run 3 | `figures_carried_correctly` | PASS | PARTIAL | `glm5.2__003` PARTIAL for a denominator matching nothing | −1.5 |

Net **−1.07** on the overall. Nine corrections against Fable, one in its favour.

Twelve further calls were re-examined and **KEPT** (§1.6–1.12), including the
decision not to apply a `material_hallucination` penalty, which §1.9 confirms
against three published penalty precedents.

---

## 6. Verdict

### ROBUST PROVISIONAL RESULT — with the headline claim withdrawn

The performance-band conclusion survives every reasonable scoring
interpretation: Fable 5.1 sits with Qwen 3.8 Flash and GLM 5.3 Flash at the top
of the field across a 94.07–96.30 envelope.

But this audit **did find scoring issues** — ten of them, worth −1.07 — and they
were load-bearing for the specific claim that Fable had the highest provisional
overall. That claim is withdrawn. Corrected, the three top models are separated
by 0.17 and 0.03 points, which is noise.

**Fit for public display as provisional, on three conditions:** publish 94.90,
not 95.97; present the top three as an unordered band rather than a ranking; and
keep the OFF-BENCHMARK / CLAUDE CODE ROUTE label with its methodological
caveats, which this audit does not touch and which remain the reason Fable
cannot enter the official leaderboard.

**Nothing was integrated into the site.** Frozen suite verifies `identical` at
digest `c056b4b43d3caeb3b50394282b08ed281a5716fb1df68d1666abb950aa0b2a80`;
`models.yaml`, `runs/`, `verdicts/`, `evaluations/` and `leaderboard/` untouched.
