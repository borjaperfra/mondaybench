# MondayBench #003 "Blockers" — calibration v0.2, 2026-08-28

Scenario `monday-003` v0.2 · rubric 0.2 · evaluator `evaluator-opus5-v0.3-calibration-2`
· judge `claude-opus-5` · prompt `aaf788f309d955d2…`

Seven models, one attempt each. **Not official, not frozen.**

`RECOMMENDATION: REVISE BEFORE FREEZE`

The revision needed is small and specific, and the reason is not the one that
sank v0.1. v0.2 discriminates: the spread more than doubled, the constant point
mass fell below target, the field spread across fifty-one points, and penalties
fired for the first time. What it does not have is **headroom**. Two models
finished on exactly 100.0, and after deliberate scrutiny I could not fault
either answer. A scenario that cannot rank its two best candidates is not
finished, even when everything else about it works.

---

## Scores

| Model | Score | Base | Penalties | Valid / total attempts |
|---|---:|---:|---:|:--:|
| GLM 5.3 Flash | **100.0** | 100.0 | 0 | 1 / 1 |
| Qwen 3.8 Flash | **100.0** | 100.0 | 0 | 1 / 1 |
| MIMO v2.5 | **93.5** | 93.5 | 0 | 1 / 1 |
| GLM 5.2 | **88.0** | 88.0 | 0 | 1 / 1 |
| DeepSeek V4 Flash | **68.5** | 68.5 | 0 | 1 / 1 |
| Gemma 4 | **52.5** | 59.5 | −7.0 | 1 / 1 |
| Qwen 3.6 | **49.0** | 66.0 | −17.0 | 1 / 1 |

Spread **51.0** · median **88.0** · mean **78.8**.

### Attempts

Every model qualified on its first attempt. This is worth stating because v0.1
did not: Qwen 3.8 Flash needed three attempts there, two of them returning zero
reasoning tokens and being refused by the hardened guard. Nothing about that
defect was a model-quality signal then and its absence is not one now — it is a
serving property, recorded and moved past.

MIMO v2.5 again reported `reasoning_tokens: 0` while streaming a 137-second
thinking phase before its first answer token. The multi-signal detector caught
it through `explicit_reasoning_stream`, as designed, and the run qualified.

---

## Targets

| Signal | Target | v0.1 | v0.2 | |
|---|---|---:|---:|:--:|
| Top score | 82–90 (90–94 acceptable) | 100.0 ×3 | **100.0 ×2** | ✗ |
| Score spread | ≥ 25 | 20.0 | **51.0** | ✓ |
| Constant point mass | < 40 | 55.0 | **35.0** | ✓ |
| Universal-PASS criteria | fewer | 10 of 20 | **7 of 20** | ✓ |
| Penalties fired | some | 0 | **4, across 2 runs** | ✓ |
| Frontier disagreement | several criteria | none | **5 criteria** | ✓ |

Four of the six move decisively. The ceiling does not.

---

## v0.1 → v0.2 comparison

| | v0.1 | v0.2 |
|---|---:|---:|
| Best score | 100.0 | 100.0 |
| Models at 100 | 3 | 2 |
| Median | 98.5 | 88.0 |
| Mean | 93.8 | 78.8 |
| Lowest score | 80.0 | 49.0 |
| Spread | 20.0 | 51.0 |
| Constant point mass | 55.0 / 100 | 35.0 / 100 |
| Universal-PASS criteria | 10 of 20 | 7 of 20 |
| Penalties | 0 | 4 (−24 points) |

### Ranking

| v0.1 | | v0.2 | | Move |
|---|---:|---|---:|---|
| DeepSeek V4 Flash | 100.0 | GLM 5.3 Flash | 100.0 | — |
| GLM 5.3 Flash | 100.0 | Qwen 3.8 Flash | 100.0 | — |
| Qwen 3.8 Flash | 100.0 | MIMO v2.5 | 93.5 | +2 |
| GLM 5.2 | 98.5 | GLM 5.2 | 88.0 | — |
| MIMO v2.5 | 98.5 | DeepSeek V4 Flash | 68.5 | **−4** |
| Qwen 3.6 | 81.5 | Gemma 4 | 52.5 | +1 |
| Gemma 4 | 80.0 | Qwen 3.6 | 49.0 | −1 |

The ranking is not a rescaling of v0.1. **DeepSeek V4 Flash falls from joint
first to fifth**, losing 31.5 points, and the model that displaces it at the top
of the second tier is MIMO. A benchmark version that only stretched the same
order would have told us nothing; this one reorders the field.

### Which changes created the discrimination

Measured against where the points actually moved:

**The contested engineer did most of the work.** `scarce_resource_allocation`
(10) and `marcus_reserved_for_sso` (6) together account for 18 of DeepSeek's
31.5-point fall and 16 of Gemma 4's. Nothing equivalent existed in v0.1, where
`marcus_bottleneck` was universal PASS at 7 points. In v0.2 the resource
dimension spans 25.0 to 7.0 across the field.

**The second dated commitment split the decision from the reading.** All seven
models found the Contoso permission defect and all seven dated it correctly —
`contoso_blocker_chain` and `contoso_compliance_is_urgent` are both universal
PASS. What separated them was what they did next. Finding a second blocker is
reading; deciding who fixes it is not.

**Hiding the pricing resolution in a checklist worked.** `pricing_dependency`
produced the battery's only outright FAIL from a strong model: GLM 5.2 read
Sarah's self-blocking plan, adopted it, and inverted the gate — "Pricing page
build gates packaging approval pack (screenshots needed)". Priya's line that
mockups are acceptable is never used. In v0.1 the same idea was handed over in
a five-line Slack exchange and six of seven models got it.

**Moving the Security approval to a single email had a smaller effect than
expected.** Five of seven still resolved it correctly. Gemma 4 reopened it as a
gate — the battery's PROHIBITED_ACTION penalty — and Qwen 3.6 saw both records
and refused to choose.

**Removing the leaks did not, on its own, make the chain hard.** `sso_chain`
stayed universal PASS after `work-items.csv` and `meetings.md` were stripped.
Seven of seven still reconstructed migration → patch → QA → rollout from the
Slack thread alone. That is a genuine finding: reconstructing a four-step chain
from one conversation is not a discriminating task for any of these models, and
the 8 points it carries are 8 points of floor.

---

## Criterion matrix

`P` = PASS · `~` = PARTIAL · `F` = FAIL

| # | Criterion | Pts | GLM 5.3 | Qwen 3.8 | MIMO | GLM 5.2 | DeepSeek | Gemma 4 | Qwen 3.6 | Const |
|---:|---|---:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| 1 | `sso_chain` | 8 | P | P | P | P | P | P | P | **YES** |
| 2 | `contoso_blocker_chain` | 6 | P | P | P | P | P | P | P | **YES** |
| 3 | `pricing_dependency` | 5 | P | P | ~ | **F** | ~ | P | ~ | — |
| 4 | `security_state_stale` | 3 | P | P | P | P | P | **F** | ~ | — |
| 5 | `board_dependency` | 3 | P | P | P | P | P | P | P | **YES** |
| 6 | `scarce_resource_allocation` | 10 | P | P | P | P | **F** | **F** | ~ | — |
| 7 | `marcus_reserved_for_sso` | 6 | P | P | P | ~ | ~ | ~ | ~ | — |
| 8 | `formatter_ownership` | 4 | P | P | P | P | P | P | P | **YES** |
| 9 | `elena_migration_fallback` | 5 | P | P | P | ~ | **F** | **F** | ~ | — |
| 10 | `monday_plan` | 7 | P | P | P | P | ~ | ~ | ~ | — |
| 11 | `concurrent_sso_and_contoso` | 7 | P | P | P | P | ~ | ~ | ~ | — |
| 12 | `pricing_board_parallel` | 6 | P | P | P | P | P | P | P | **YES** |
| 13 | `formatting_urgent_not_blocking` | 5 | P | P | ~ | P | ~ | ~ | ~ | — |
| 14 | `contoso_compliance_is_urgent` | 5 | P | P | P | P | P | P | P | **YES** |
| 15 | `stale_task_list_overridden` | 5 | P | P | P | P | P | ~ | ~ | — |
| 16 | `sso_state_reconstructed` | 4 | P | P | P | P | P | ~ | ~ | — |
| 17 | `onboarding_state_reconstructed` | 3 | P | P | P | P | P | P | P | **YES** |
| 18 | `contoso_state_separated` | 3 | P | P | ~ | ~ | ~ | ~ | ~ | — |
| 19 | `earliest_feasible_delivery` | 3 | P | P | P | P | P | **F** | **F** | — |
| 20 | `uncertainty_discipline` | 2 | P | P | P | P | P | ~ | ~ | — |

**Constant: 7 of 20 criteria, 35.0 of 100 points.** 65 points discriminate,
against 45 in v0.1.

---

## Dimensions

| Dimension | Max | GLM 5.3 | Qwen 3.8 | MIMO | GLM 5.2 | DeepSeek | Gemma 4 | Qwen 3.6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Critical path & dependencies | 25 | 25.0 | 25.0 | 22.5 | 20.0 | 22.5 | 22.0 | 21.0 |
| Resource allocation | 25 | 25.0 | 25.0 | 25.0 | 19.5 | **7.0** | **7.0** | 14.5 |
| Planning & parallelization | 20 | 20.0 | 20.0 | 20.0 | 20.0 | 13.0 | 13.0 | 13.0 |
| Decision quality | 15 | 15.0 | 15.0 | 12.5 | 15.0 | 12.5 | 10.0 | 10.0 |
| State reconstruction | 10 | 10.0 | 10.0 | 8.5 | 8.5 | 8.5 | 6.5 | 6.5 |
| Timing & uncertainty | 5 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 1.0 | 1.0 |

Resource allocation is the dimension that separates the field: 25.0 down to 7.0.
Reweighting it from 20 to 25 points and moving the dependency dimension from 30
to 25 was the single most productive change in the revision.

---

## The specific findings the brief asked for

**SSO chain.** Seven of seven. Removing the two leaks did not make it hard.

**Contoso: real blocker versus formatting noise.** Seven of seven found the
delegated-admin permission defect, dated it to Tuesday 16:00, and kept the
date-format request off that chain. The trap I expected — over-generalising
Peter's *"This isn't blocking production"* to the whole account — caught nobody.
Every model read Anja's Monday email as a separate matter.

Where they diverged was the *characterisation*. Only GLM 5.3 and Qwen 3.8 say in
so many words that the original report was cosmetic and the export runs; the
other five separate the two items in their plans without ever stating the state.
Qwen 3.8 was the most explicit: *"Contoso broken export is one issue — It is two
issues"*.

**Marcus versus Daniel.** This is the criterion that worked.

- Four models reassigned the permission patch to Daniel with a reason. GLM 5.3:
  *"Daniel knows the model from SCIM; Marcus is the bottleneck and the
  compatibility patch cannot move off him"*.
- **DeepSeek V4 Flash kept Marcus on both** and ruled the substitute out
  explicitly — *"Daniel: available for support, but not needed on critical
  path"* — while noting in its own risk section that Marcus is stretched and
  nobody else knows the branch. It saw the contention and drew the opposite
  conclusion.
- **Gemma 4 went further**: *"Instruct Marcus to pivot from onboarding
  instrumentation to the contoso_permission_patch"*, and then never scheduled
  the SSO compatibility patch at all.
- Qwen 3.6 made the right assignment but justified it as workstream separation
  rather than substitutability, and then contradicted itself by listing the
  Contoso fix among Marcus's load in its risk section.

**Pricing path.** GLM 5.2's FAIL, described above. MIMO and DeepSeek each got
half. Gemma 4 — the second-weakest model in the battery — got it cleanly:
*"mockups are acceptable per Priya"* plus *"Pricing Page launch is blocked by
Priya's committee approval"*. Criterion 3 is the only one where the ranking
inverts, which is a good sign that it is measuring something independent.

**Board partial dependency.** Seven of seven named the backfill, not just the
migration. Defining the backfill as a work item with an owner and a duration
removed the ambiguity v0.1 had and removed the discrimination with it.

**Earliest feasible delivery.** Five of seven answered Tuesday 14:00 or
equivalent — the lower bound. The bound held: it is pinned by Marcus's Tuesday
morning, not by arithmetic, so compressing the earlier steps cannot beat it and
nobody tried. Gemma 4 answered *"Wednesday EOD (Matches commitment)"* without
testing whether Tuesday was reachable; Qwen 3.6 hedged between Tuesday EOD and
Wednesday on top of a schedule that starts the patch before the migration.

DeepSeek answered Tuesday 17:30 — three and a half hours later than the bound —
and earned the point, because that is genuinely the earliest its own plan
supports and its plan is internally valid. The lateness is a consequence of the
allocation, and the allocation is priced at criterion 6. Rewriting this
criterion away from a clock window is the change that made that possible; the
v0.1 version would have had to hand a PASS to a plan that beat it and a FAIL to
a plan that was merely slower for a stated reason.

---

## Penalties

Four penalties, both fired against the bottom two models, none against the top
five. This is the first #003 battery to produce any.

**Gemma 4 — PROHIBITED_ACTION (−7).** *"UNBLOCK (Immediate): Check status of the
Security Review for SSO. This is a listed task blocker that must be cleared
before Wednesday."* Maya's Friday 16:48 email closes the review. The response
directs work against a gate that is shut and makes clearing it a precondition
for the rollout.

**Qwen 3.6 — MATERIAL_HALLUCINATION (−5).** *"Marcus is unavailable Monday
09:00–13:00 (Atlas session) and Tuesday 09:00–13:00 (Atlas session)."* There is
one session and it is on Tuesday. `availability.csv` shows him 09:00–17:30 on
Monday. The invented Monday absence is asserted as fact and is the reason the
response spends its morning deciding whether to delay the migration.

**Qwen 3.6 — MAJOR_PLANNING_ERROR (−7).** It directs Elena to start the
three-hour migration at Monday 13:00 and, in the same plan, has Marcus run the
four-hour compatibility patch from 13:00 — *"13:00–17:00 is 4.5 hours, enough
for 4h work + handoff"*. Marcus's own Friday message is that he cannot finish
that work until the migration lands.

**Qwen 3.6 — MAJOR_CONTRADICTION (−5).** *"Direct Elena to start Migration
Monday 13:00"* against *"Since we are pushing migration to Tuesday, the revenue
charts are blocked until Wednesday"*, with the whole board-pack section built on
the Tuesday version. Both instructions stand and a reader cannot tell which to
follow.

No penalty was applied for a slower-but-valid allocation. Keeping Marcus on both
engineering items is recorded in the answer key as *feasible, materially worse,
and avoidable*, and the penalty prompt says so explicitly, so DeepSeek's
allocation cost it 18 rubric points and nothing else. That separation is
deliberate: penalties are for what a response gets wrong, not for what it gets
suboptimal.

---

## Judge quality

Two notes, both about criteria rather than responses.

**`contoso_state_separated` may be too strict.** Five of seven scored PARTIAL,
and in every case for the same reason: the model separates the two Contoso items
correctly in its plan but never writes the sentence "the export runs". The
criterion asks for a state, and a state has to be stated — but a criterion that
five of seven fail on a wording rather than a reading is worth watching. It is
worth 3 points, so the exposure is small.

**One factual error went unpriced.** GLM 5.3 Flash writes *"still ahead of the
Wed 15:00 external milestone"* in a contingency clause; the billing migration's
external deadline is Thursday 15:00. The error changes no recommendation — the
true date is later, so the conclusion holds a fortiori — and it is therefore not
a material hallucination. But it is a plain misreading of supplied data inside a
response that scored 100.0, and no criterion in the rubric catches it. See the
first recommended change below.

Every other label rested on a quotable sentence. The three FAILs on criteria 4,
6 and 19 were absences and assertions rather than interpretations.

---

## Why the ceiling was not reached

Not because the scenario is easy. The bottom of the field is at 49.0, a strong
model is at 68.5, and thirteen of twenty criteria discriminate. The ceiling was
reached because two models solved the scenario completely, and I could not find
a defect in either after looking for one specifically.

Qwen 3.8 Flash spent 34,001 reasoning tokens and returned a step table with
earliest-start and earliest-finish per step, the exact lower bound, both chains,
the substitution priced against its alternative, every stale item corrected, and
a risk section that flags the assumption its own timing rests on — *"Migration
lands is assumed to mean schema migration complete, not backfill complete"*.
GLM 5.3 Flash returned a comparable answer in a third of the tokens and asked
the sharpest question in the battery: whether section 8.3 requires Contoso's
delegated admins to run the export themselves, or whether Northstar sending the
file discharges the obligation. Neither answer has anything left to withhold
points for.

That is a rubric problem, not a scenario problem. The rubric prices twenty
things a good answer does and nothing that only an excellent answer does.

---

## Minimum changes required before freeze

Short list. The structure of v0.2 is right and should not be rebuilt.

1. **Price factual accuracy against the supplied data.** Add a criterion — or
   widen `uncertainty_discipline` and raise its weight — that fails a response
   for misstating a date, duration or owner that the sources give explicitly.
   This is the change that separates the two leaders today: GLM 5.3's
   Wednesday-for-Thursday slip would cost it, Qwen 3.8's answer has no
   equivalent. It creates headroom honestly, by asking for something a perfect
   answer already does, rather than by making the scenario harder.

2. **Contest a second resource.** Julia currently holds the formatter (2h), the
   compliance export (1h) and the onboarding launch (2h) against a Friday
   deadline, and her week is trivially satisfiable, so no model has to think
   about it. Tightening her load — or giving the compliance export a second
   possible owner at a stated cost — adds a second allocation judgement without
   adding calendar arithmetic. One contested decision is a coin flip between
   the top models; two is a measurement.

3. **Reclaim the 8 points on `sso_chain`.** Seven of seven reconstruct it, in
   both versions, with and without the leaks. Either cut its weight to 4–5 and
   move the difference into the allocation dimension, or make the chain itself
   contestable — a step whose necessity is disputed between two people, so that
   reconstructing it requires deciding whom to believe.

Optional, lower value:

4. Consider whether `contoso_state_separated` should reward the separation as
   demonstrated in the plan rather than as stated in prose (see Judge quality).
5. `board_dependency` and `contoso_compliance_is_urgent` are now universal
   PASS and could be merged into their neighbouring criteria to free weight.

I have applied none of them.

**The counter-argument, stated plainly:** freezing v0.2 as it stands is
defensible. Three of the four quantitative targets are met, the spread is
51 points, the ranking reorders the field, penalties fire where they should, and
the only failure is that two models tied at the top of a scenario they both
solved. If the purpose of #003 is to separate strong planning from weak
planning, it already does that better than #001 or #002. If the purpose is to
rank frontier models against each other, it does not yet, and change 1 is the
cheapest way to fix that. That is the user's call, not mine.

---

## Integrity

monday-001 and monday-002 are untouched: their frozen manifests still verify and
no run, evaluation, verdict or leaderboard of either was read, modified or
written.

The whole v0.1 calibration is preserved at `archive/monday-003-v0.1/` — scenario,
prompt hash, evaluator, judge prompts, nine run attempts including the two
rejected ones, seven evaluations, seven verdict files, the v0.1 test suite and
the v0.1 report. Nothing there was deleted or overwritten. v0.2 reproduces
independently from `scenarios/monday-003/` at prompt
`aaf788f309d955d2b427c86fe7d95d2bbf88575fde7306adcfd74b0ec4a4103f`, and no v0.1
criterion id survives into rubric 0.2, so the archived verdicts cannot silently
replay against v0.2 runs.

`publish` refuses monday-003 while it is `status: calibration`.

`RECOMMENDATION: REVISE BEFORE FREEZE`
