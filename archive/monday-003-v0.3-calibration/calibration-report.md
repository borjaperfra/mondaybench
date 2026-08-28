# MondayBench #003 "Blockers" — calibration v0.3, 2026-08-28

Scenario `monday-003` v0.3 · rubric 0.3 · evaluator `evaluator-opus5-v0.3-calibration-3`
· judge `claude-opus-5` · prompt `aaf788f309d955d2…`

Seven models, two scored runs each: one fresh generation and one v0.2 response
rescored. **Not official, not frozen — yet.**

`RECOMMENDATION: FREEZE MONDAY-003 v0.3`

---

## What changed

**No candidate-visible source changed.** The rendered prompt still hashes to
`aaf788f309d955d2b427c86fe7d95d2bbf88575fde7306adcfd74b0ec4a4103f`, byte for
byte, and a test compares all seven candidate files against the archived v0.2
copies. v0.3 is a rubric revision, which is why the v0.2 responses could be
rescored rather than discarded.

Three rubric changes, one answer-key addition, one harness fix.

| | v0.2 | v0.3 |
|---|---:|---:|
| `sso_chain` | 8 | **4** |
| `pricing_board_parallel` | 6 | **4** |
| `contoso_compliance_is_urgent` | 5 | **4** |
| `factual_plan_accuracy` | — | **5** (new) |
| `uncertainty_discipline` | 2 | **4** |
| Criteria | 20 | 21 |
| Total | 100 | 100 |

**Where the points came from.** All seven freed points come from criteria that
returned *the same label for all seven models* in v0.2. A zero-variance
criterion contributes an identical number to every total, so cutting its weight
subtracts a constant and cannot reorder anything. That is the whole justification
and it is enforced by a test — `test_every_weight_that_went_down_had_zero_variance_in_v0_2`
reads the archived v0.2 evaluations and fails if a reduced criterion ever
discriminated. The arithmetic is checked too: freed 7, spent 7.

**`factual_plan_accuracy` (5).** Scored against a new `factual_anchors` block in
the answer key — every deadline, duration, owner, availability window and
commitment term that the sources state outright. Its scope boundary is written
into the key so it cannot charge the same mistake twice: a wrong *value* lands
here, a wrong *relationship* lands on the dependency criteria, a wrong *state* on
the state criteria. Omissions are not errors, and rounding the present moment
(09:00 for 09:10) is not a substitution.

**`contoso_state_separated` rewritten.** It now scores the operational
distinction — is it unambiguous that the format request is not what blocks the
contractual delivery, and that the permission defect is — and says explicitly
that demonstrating this through the plan counts in full, with no phrasing
required. It gained a FAIL band naming the three ways to get it wrong.

**`earliest_feasible_delivery` unchanged**, and the answer key still carries a
lower bound rather than a clock window. The criterion text now says outright
that a demonstrably earlier valid plan is equally correct.

**Answer-key addition.** One `recorded_gaps` entry: whether "the migration lands"
means the schema change alone or the schema change plus the backfill. The graph
is correct as written — Marcus names the migration, Elena describes the backfill
as a separate job — but the sources never say so outright, so a candidate that
*asks* is reading well and a candidate that *asserts* the extra link is scored
under `sso_chain`. Both happened in this battery.

---

## Fresh v0.3 scores

One new generation per model, under the identical candidate prompt. This is the
calibration result.

| Model | Score | Base | Penalties | Qualification | Valid / total attempts |
|---|---:|---:|---:|---|:--:|
| GLM 5.3 Flash | **97.5** | 97.5 | 0 | valid, reasoning delivered | 2 / 2 |
| Qwen 3.8 Flash | **93.5** | 93.5 | 0 | valid, reasoning delivered | 2 / 2 |
| DeepSeek V4 Flash | **83.5** | 83.5 | 0 | valid, reasoning delivered | 2 / **3** |
| GLM 5.2 | **83.5** | 83.5 | 0 | valid, reasoning delivered | 2 / 2 |
| MIMO v2.5 | **69.0** | 74.0 | −5.0 | valid, reasoning via stream | 2 / 2 |
| Gemma 4 | **56.0** | 63.0 | −7.0 | valid, reasoning not requested | 2 / 2 |
| Qwen 3.6 | **40.0** | 54.0 | −14.0 | valid, reasoning not requested | 2 / 2 |

Spread **57.5** · mean **74.7** · median **83.5** · best **97.5** · scores ≥ 95: **1**.

### Dimension breakdown (fresh)

| Dimension | Max | GLM 5.3 | Qwen 3.8 | DeepSeek | GLM 5.2 | MIMO | Gemma 4 | Qwen 3.6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Critical path & dependencies | 21 | 21.0 | 21.0 | 18.5 | 18.5 | 18.5 | 16.0 | 8.0 |
| Resource allocation | 25 | 25.0 | 22.0 | 17.0 | 17.0 | 12.0 | 12.0 | 17.0 |
| Planning & parallelization | 18 | 18.0 | 14.5 | 14.5 | 14.5 | 14.5 | 11.0 | 9.0 |
| Decision quality | 14 | 14.0 | 14.0 | 11.5 | 14.0 | 14.0 | 9.0 | 9.0 |
| State reconstruction | 10 | 10.0 | 10.0 | 10.0 | 10.0 | 10.0 | 8.0 | 6.5 |
| Accuracy & uncertainty | 12 | 9.5 | 12.0 | 12.0 | 9.5 | 5.0 | 7.0 | 4.5 |

### Attempts

Thirteen of fourteen generations qualified first time. The exception is
**DeepSeek V4 Flash**, whose first attempt at run-002 returned 128,223 characters
of reasoning and no answer (`finish_reason=length`) — its entire output budget
consumed by thinking. The attempt is preserved in
`runs/monday-003/deepseek-v4-flash/failed-attempts.jsonl` and it was retried at
identical configuration. This is the same serving failure seen once during the
#002 battery and is not a model-quality signal.

MIMO v2.5 again reported `reasoning_tokens: 0` behind a ~140-second thinking
stream on both runs; the multi-signal detector qualified them through
`explicit_reasoning_stream`, as designed.

---

## v0.2 responses rescored under v0.3

The same seven responses the v0.2 rubric scored, re-judged under rubric 0.3.
Because the prompt did not move, this isolates **rubric effect** from
**candidate-run variance**.

| Model | v0.2 score | v0.3 shadow | Rubric effect | v0.3 fresh | Run variance |
|---|---:|---:|---:|---:|---:|
| Qwen 3.8 Flash | 100.0 | **100.0** | 0.0 | 93.5 | −6.5 |
| GLM 5.3 Flash | 100.0 | **97.5** | **−2.5** | 97.5 | 0.0 |
| MIMO v2.5 | 93.5 | **95.0** | +1.5 | 69.0 | **−26.0** |
| GLM 5.2 | 88.0 | **89.5** | +1.5 | 83.5 | −6.0 |
| DeepSeek V4 Flash | 68.5 | **70.0** | +1.5 | 83.5 | **+13.5** |
| Gemma 4 | 52.5 | **53.0** | +0.5 | 56.0 | +3.0 |
| Qwen 3.6 | 49.0 | **43.0** | −6.0 | 40.0 | −3.0 |

Shadow spread 57.0, constant point mass 28.0, scores ≥ 95: 3.

**The rubric effect is small and targeted.** Five of seven move by 1.5 points or
less — the net of the reweighting and the `contoso_state_separated` rewrite. The
two that move further are the two the changes were written for:

- **GLM 5.3 Flash −2.5**: the Wednesday-for-Thursday milestone that v0.2 could
  not see. This is the change that broke the 100–100 tie at the top.
- **Qwen 3.6 −6.0**: its invented Monday availability now fails
  `factual_plan_accuracy` as well as carrying its penalty.

**The run variance is much larger than the rubric effect** — mean |Δ| 8.3,
maximum 26.0 — which is the most important number in this report and is
discussed below.

### What the `contoso_state_separated` rewrite actually did

Same seven responses, same plans, judged under the two definitions:

| | v0.2 wording | v0.3 operational |
|---|---:|---:|
| PASS | 2 | **6** |
| PARTIAL | 5 | 1 |

Five models had been losing 1.5 points each for separating the two Contoso items
correctly in their plans without writing a sentence equivalent to "the export
runs". They now pass. The one remaining PARTIAL is Qwen 3.6, which opens with a
single "Unblock Contoso (Highest Business Risk)" block that assigns both fixes
under one contractual justification — a real ambiguity about which item threatens
Tuesday, not a phrasing gap.

---

## Discrimination

| Signal | v0.1 | v0.2 | v0.3 shadow | **v0.3 fresh** |
|---|---:|---:|---:|---:|
| Best score | 100.0 | 100.0 | 100.0 | **97.5** |
| Scores ≥ 95 | 5 | 2 | 3 | **1** |
| Median | 98.5 | 88.0 | 89.5 | **83.5** |
| Mean | 93.8 | 78.8 | 78.3 | **74.7** |
| Lowest | 80.0 | 49.0 | 43.0 | **40.0** |
| Spread | 20.0 | 51.0 | 57.0 | **57.5** |
| Constant point mass | 55.0 | 35.0 | 28.0 | **19.0** |
| Universal-PASS criteria | 10 / 20 | 7 / 20 | 7 / 21 | **5 / 21** |
| Penalties | 0 | 4 | 4 | **5, across 3 runs** |

Sixteen of twenty-one criteria discriminate in the fresh battery, carrying 81 of
the 100 points. Only five are constant: `board_dependency` (3),
`formatter_ownership` (4), `elena_migration_fallback` (5),
`contoso_compliance_is_urgent` (4) and `onboarding_state_reconstructed` (3).

### Criterion matrix (fresh)

`P` = PASS · `~` = PARTIAL · `F` = FAIL

| # | Criterion | Pts | GLM 5.3 | Qwen 3.8 | DeepSeek | GLM 5.2 | MIMO | Gemma 4 | Qwen 3.6 | Labels |
|---:|---|---:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| 1 | `sso_chain` | 4 | P | P | P | P | P | ~ | ~ | 2 |
| 2 | `contoso_blocker_chain` | 6 | P | P | P | P | P | P | ~ | 2 |
| 3 | `pricing_dependency` | 5 | P | P | ~ | ~ | ~ | P | **F** | 3 |
| 4 | `security_state_stale` | 3 | P | P | P | P | P | **F** | **F** | 2 |
| 5 | `board_dependency` | 3 | P | P | P | P | P | P | P | 1 |
| 6 | `scarce_resource_allocation` | 10 | P | P | ~ | ~ | **F** | **F** | ~ | 3 |
| 7 | `marcus_reserved_for_sso` | 6 | P | ~ | ~ | ~ | ~ | ~ | ~ | 2 |
| 8 | `formatter_ownership` | 4 | P | P | P | P | P | P | P | 1 |
| 9 | `elena_migration_fallback` | 5 | P | P | P | P | P | P | P | 1 |
| 10 | `monday_plan` | 7 | P | P | P | P | P | ~ | ~ | 2 |
| 11 | `concurrent_sso_and_contoso` | 7 | P | ~ | ~ | ~ | ~ | ~ | ~ | 2 |
| 12 | `pricing_board_parallel` | 4 | P | P | P | P | P | P | ~ | 2 |
| 13 | `formatting_urgent_not_blocking` | 5 | P | P | ~ | P | P | ~ | ~ | 2 |
| 14 | `contoso_compliance_is_urgent` | 4 | P | P | P | P | P | P | P | 1 |
| 15 | `stale_task_list_overridden` | 5 | P | P | P | P | P | ~ | ~ | 2 |
| 16 | `sso_state_reconstructed` | 4 | P | P | P | P | P | ~ | ~ | 2 |
| 17 | `onboarding_state_reconstructed` | 3 | P | P | P | P | P | P | P | 1 |
| 18 | `contoso_state_separated` | 3 | P | P | P | P | P | P | ~ | 2 |
| 19 | `factual_plan_accuracy` | 5 | ~ | P | P | ~ | **F** | P | ~ | 3 |
| 20 | `earliest_feasible_delivery` | 3 | P | P | P | P | P | **F** | **F** | 2 |
| 21 | `uncertainty_discipline` | 4 | P | P | P | P | ~ | ~ | ~ | 2 |

**`factual_plan_accuracy` earned its place.** Three distinct labels across the
field in both batteries, and it caught the same class of error in three different
models independently:

- **GLM 5.3 Flash (shadow)**: *"still ahead of the Wed 15:00 external
  milestone"* — the billing migration is due Thursday 15:00.
- **GLM 5.2 (fresh)**: *"Billing migration + backfill | Wed 15:00"* — the same
  anchor, the same day early, in a different model's delivery table.
- **MIMO v2.5 (fresh)**: two at once — *"Billing schema migration | Wed 15:00"*
  and *"Pricing page | Wed EOD"*, both used to compute the buffers it then
  reported. Two substitutions is the FAIL band.

That three models slipped on the same Thursday deadline is itself a finding. The
date is in `work-items.csv` and nowhere else; the models that quote it appear to
be reconstructing it from the surrounding Wednesday commitments rather than
reading the column.

---

## Qualitative audit of every candidate scoring ≥ 95

Required by the brief, and the outcome that decides the freeze. A legitimate high
score is allowed; a high score propped up by a rubric blind spot is not.

### GLM 5.3 Flash — 97.5 (fresh run-002) — supported

- **Factual errors: one, and it is exactly the 2.5 points it lost.** The pricing
  contingency reads *"submission slips to Tue 12:00 → approval Wed AM → page
  still public by Wed 17:00 but buffer nearly gone."* The page is due **Thursday**
  17:00, so publishing Wednesday leaves a full day. No date is misquoted — the
  error is only visible in the assessment — which makes this **the closest call
  in the battery**. Graded PARTIAL under the judge prompt's "choose the lower"
  rule, and disclosed here so the line is inspectable.
- **Missed dependencies: none.** All four chains reconstructed, plus a
  distinction neither the answer key nor any other model drew — *"Daniel: can
  develop the permission patch before the migration lands; it only goes in
  after."*
- **Inefficient allocations: none.** It sequences Julia's formatter *after* the
  compliance file is sent — *"same exporter, don't risk it"* — which is better
  than the canonical plan.
- **Unsupported assumptions: none.** It names the one it stands on: whether
  "migration lands" includes the backfill.
- **Timing errors: one immaterial internal slip.** §2 has the permission patch
  landing ~14:30 and Julia taking an hour; §5 reports the export at ~16:30 rather
  than ~15:30. Same day, same conclusion.
- **Ownership errors: none. Uncertainty failures: none.** It identifies the only
  thing that could genuinely threaten Wednesday — an auth-flow change surfacing
  in Tuesday's Atlas session triggering Maya's re-review clause.

### Qwen 3.8 Flash — 100.0 (shadow run-001) — genuinely flawless

Re-audited under the new `factual_anchors`, specifically looking for a
substitution. There is none: the four SSO durations, Daniel at 3.5 hours plus a
half-hour handoff, the 90-minute backfill, Marcus unavailable until Tuesday
13:00, Elena's Wednesday-noon cutoff, Tuesday 16:00 CET, Friday 12:00 — all
carried through intact. The step table gives earliest-start and earliest-finish
per step and lands exactly on the lower bound. Every stale item corrected, both
chains reconstructed, the substitution priced against its alternative, and a risk
section that flags the assumption its own timing rests on.

**This answer has no defect I can find, and I looked for one deliberately.** Its
100.0 is a legitimate 100.0.

### MIMO v2.5 — 95.0 (shadow run-001) — supported

Loses 2.5 on `pricing_dependency` — it treats the approval pack as blocked on the
finished page and never finds Priya's mockup line — and 1.5 on
`contoso_state_separated` under the old wording (6.5 points would have been 5.0
under the v0.3 definition, which is why its shadow rose). Both are real gaps, not
rubric artefacts. One small over-commit: Marcus is given 3 hours of
instrumentation plus a 30-minute walkthrough inside a 3-hour morning window.

**No fresh run reached 95.** The single ≥95 in the fresh battery is GLM 5.3's
97.5, audited above.

---

## Run variance is now the dominant term

Mean |Δ| between the two runs is **8.3 points**; the rubric change moved five of
seven models by 1.5 or less. Three cases are worth stating plainly, because they
matter more for how #003 should be *used* than anything in the rubric.

**MIMO v2.5: 95.0 → 69.0.** Not noise. In run-001 it wrote *"Key decision:
Reassign contoso_permission_patch from Marcus to Daniel"*. In run-002 it wrote
*"There is no other person who can own either patch — the account-mapping branch
is Marcus's exclusively"*, which Daniel's own message contradicts, and every
allocation followed from it. Same prompt, opposite conclusion, and the second one
earned a MATERIAL_HALLUCINATION.

**DeepSeek V4 Flash: 70.0 → 83.5.** Also not noise. Run-001 never mentioned
Elena's Wednesday departure at all; run-002 handles it correctly. Run-001 ruled
Daniel out flatly; run-002 at least engages him and gives a reason, wrong though
it is.

**Qwen 3.8 Flash: 100.0 → 93.5, by changing its mind.** Run-001 reassigned the
permission patch to Daniel. Run-002 deliberately kept it with Marcus — *"he is
also the fastest owner"* — armed Daniel as a triggered fallback, and justified
the choice twice, including on merge risk: *"If Daniel takes permission instead,
parallel work may create merge/dependency risk."* Both commitments are still met.
That earned a PASS on `scarce_resource_allocation`, because the criterion
explicitly allows an equivalent allocation with a reason, and a PARTIAL on
`marcus_reserved_for_sso`, because the protected capacity went to the
substitutable item and moved the rollout from 14:00 to 16:40.

**Consequence for the leaderboard: three official runs per model is the floor,
not a formality.** On this scenario a single run can miss by 26 points. That is a
property of the models on a decision task with a defensible fork in it, not a
defect in the scenario — but #003 must never be published from fewer than its
three runs, and `run_range` will be wide and should be read.

---

## Penalties

Five penalties across three runs in the fresh battery, none against the top two.

| Model | Penalty | For |
|---|---|---|
| MIMO v2.5 | MATERIAL_HALLUCINATION −5 | *"There is no other person who can own either patch"* — Daniel states otherwise, and the claim drives the whole allocation |
| Gemma 4 | PROHIBITED_ACTION −7 | *"Identify the owner of the Security Review for SSO and force a resolution today"* — the review is closed |
| Qwen 3.6 | PROHIBITED_ACTION −7 | Makes the closed review the first hour of the day and step 1 of its critical path |
| Qwen 3.6 | MAJOR_PLANNING_ERROR −7 | Schedules Daniel's permission patch 12:00–15:00 against a migration it depends on running 13:00–16:00 |

Behaviour is correct in both directions. Nothing fired for a slower-but-valid
allocation: DeepSeek, GLM 5.2 and Qwen 3.8 all kept Marcus on both engineering
items and all lost rubric points and no penalty, exactly as the answer key
prescribes (*"feasible, materially worse, and avoidable"*). Nothing fired for an
omission. And the penalty scale now reaches a mid-tier model for a genuine
fabrication rather than only punishing the bottom of the field.

---

## Evaluator quality

**The known wording sensitivity is fixed and the fix is measured** — 2 PASS to
6 PASS on the same seven responses, with the one remaining PARTIAL earned on
substance.

**One thing to watch, not a blocker.** `scarce_resource_allocation` (10),
`marcus_reserved_for_sso` (6) and `concurrent_sso_and_contoso` (7) are 23 points
that all move with the same decision, and in the fresh battery only GLM 5.3
passes all three while five models sit at PARTIAL on two of them. They do measure
different things — did you resolve the contention, did you protect the
un-substitutable work, did the chains run in parallel — and Qwen 3.8 splits them
(PASS, PARTIAL, PARTIAL), which is the evidence they are not one criterion in
three costumes. But they are correlated by construction, because they are all
downstream of the scenario's central decision. That is the scenario working as
designed; it is recorded here so nobody later reads 23 points as three
independent signals.

**No criterion is now decided by phrasing.** Every label in this battery rests on
a quotable recommendation, a scheduled time, or an absence.

---

## Scenario ambiguity

One, recorded and resolved in the answer key rather than in the sources:
whether "the migration lands" means the schema change alone or the schema change
plus the backfill. Marcus names the migration; Elena describes the backfill as a
separate ninety-minute job that follows. The graph is correct as written, and the
battery shows the ambiguity is doing the right work — GLM 5.3 raises it as an
open question and is not marked down, Gemma 4 asserts the extra link and loses
half of `sso_chain` for it.

Nothing else surfaced across fourteen responses.

---

## Leaderboard calibration gate

The harness gap found during v0.2 — a plain `mondaybench leaderboard --scenario
monday-003` wrote a calibration ranking into `leaderboard/monday-003/`, beside
the published results — is closed.

- **Normal `leaderboard` now refuses a `status: calibration` scenario** with a
  clear error naming the two ways forward.
- **`--calibration` writes to `analysis/leaderboards/<scenario>/`** and never
  under `leaderboard/`, with a "not an official result" banner on the console.
- The guard is also in `write_leaderboard` itself, keyed off `scenario_status` in
  the payload, so a caller that forgets the flag still cannot reach the official
  tree.
- **`--official` / `publish` behaviour for #001 and #002 is unchanged.**

**A second gap of the same family, found and closed while testing this one.**
Running plain `leaderboard --scenario monday-001` (without `--official`) silently
overwrote the *published* v0.1 leaderboard with a non-official rebuild — same
scores, but the "official v0.1 result" banner replaced by "NOT AN OFFICIAL
RESULT". I did this by accident, restored the file from git, and added a refusal:
a non-official build will not overwrite a leaderboard whose payload says
`official: true`. `--official` still overwrites, because publishing is its job.
This goes slightly beyond the brief; it protects #001/#002 publication rather
than altering it, and it is reported here rather than left silent.

Eleven regression tests in `tests/test_leaderboard_calibration_gate.py`.

The gate's own output now sits at `analysis/leaderboards/monday-003/`, carrying
the "NOT AN OFFICIAL RESULT" banner. It is a two-run mean over the shadow and the
fresh run together, so its `Range` column is the run-variance figure discussed
above (26.0 for MIMO, 13.5 for DeepSeek) rather than a stability estimate. Read
the fresh table in this report for the calibration result.

---

## Freeze decision

Against the seven conditions in the brief:

| Condition | Required | Measured | |
|---|---|---|:--:|
| Spread | ≥ 25 | **57.5** | ✓ |
| Constant point mass | < 40 | **19.0** | ✓ |
| Evaluator wording sensitivity | none obvious | the one known case fixed and measured; nothing new | ✓ |
| Penalties | behave correctly | 5 across 3 runs, all on asserted content, none for slower-but-valid plans | ✓ |
| Scenario ambiguity | no material ambiguity | one, documented in the answer key, behaving as intended | ✓ |
| Discriminating criteria | several important ones | **16 of 21**, carrying 81 points | ✓ |
| Top scores ≥ 95 | supported by excellent answers | one fresh (97.5, audited, one real slip); the shadow 100.0 is faultless | ✓ |

All seven met.

The one number that would have failed the v0.2 target — a best score above 90 —
is no longer a hard gate, and on the evidence it should not be: the answers at
the top are the reason for the scores at the top. Qwen 3.8's 100.0 in the shadow
battery is the strongest single response across three calibrations of this
scenario and I could not fault it. GLM 5.3's 97.5 is a near-perfect plan with one
genuine, disclosed slip, now visible because v0.3 added the criterion that sees
it.

`RECOMMENDATION: FREEZE MONDAY-003 v0.3`

Freezing means: `freeze --scenario monday-003`, `status: official`, an official
evaluator id without `-calibration`, three official runs per model, and
publication through `--official`. **None of that has been done** — the brief asks
for the calibration review first, and `publish` still refuses monday-003.

One thing to carry into the freeze: **three runs is a floor, not a formality**
on this scenario. Publish `run_range` prominently.

---

## Integrity

**No candidate-visible source changed between v0.2 and v0.3.** Prompt SHA-256
`aaf788f309d955d2b427c86fe7d95d2bbf88575fde7306adcfd74b0ec4a4103f` in both, and
a test byte-compares all seven files against the v0.2 archive.

**monday-001 and monday-002 are untouched.** Frozen manifests verify; both
published leaderboards still declare `official: true` and are now protected
against accidental downgrade.

**All three #003 calibrations are preserved and separately reproducible:**

| | `archive/monday-003-v0.1/` | `archive/monday-003-v0.2/` | live |
|---|---|---|---|
| Scenario | 0.1 | 0.2 | 0.3 |
| Rubric | 0.1 | 0.2 | 0.3 |
| Prompt | `efd83750…` | `aaf788f3…` | `aaf788f3…` |
| Evaluator | `…-calibration` | `…-calibration-2` | `…-calibration-3` |
| Runs | 9 (7 valid, 2 rejected) | 7 | 14 + 1 preserved failure |
| Report | `analysis/…-v0.1.md` | `analysis/…-v0.2.md` | `analysis/…-v0.3.md` |

No v0.1 criterion id survives into rubric 0.3, so those verdicts cannot replay.
The v0.2 ids mostly do survive, and two of them changed meaning — that is stated
in both the archive README and the verdict generator, and the rubric version, not
the criterion id, is what identifies a label.

The v0.2 runs are still live as `run-001`, because the prompt did not move and
they remain valid samples of it; the archive holds the frozen v0.2 copies and
their v0.2 evaluations. Neither set was edited.

**403 tests pass.** `publish` refuses monday-003 while it is a calibration draft.

`RECOMMENDATION: FREEZE MONDAY-003 v0.3`
