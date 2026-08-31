# MondayBench capability taxonomy v0.2

**Date:** 2026-08-31
**Scope:** monday-001 … monday-005, 500 rubric points, 7 models, 105 official runs
**Status:** analysis release. **This changes no score.**

---

## What this is, and what it is not

Monday Score answers *how much of a Monday did this model get right?* It is a
single number per scenario and one arithmetic mean across five. It is the right
number for ranking and the wrong number for almost everything else, because it
cannot distinguish a model that is uniformly good from a model that is
excellent four times and unusable once.

This taxonomy answers a different question: **what kinds of practical work is
each model consistently good or bad at, and what is MondayBench still not
asking?**

It is built bottom-up from the 119 atomic criteria that the five official
rubrics actually score. No capability exists here because it sounded like a
good category; each one exists because at least one criterion measures it. That
constraint is what makes the coverage gaps in §5 real findings rather than
opinions — a gap is a place where the rubrics have nothing to say.

**Nothing in this release feeds back into scoring.** `mondaybench.scoring`,
`mondaybench.overall` and `mondaybench.leaderboard` do not import the taxonomy
module, and `tests/test_capabilities_v02.py::test_the_taxonomy_cannot_influence_monday_score_or_overall`
pins that. Overall v0, v1 and v2 reproduce byte-for-byte with this file present
or absent.

---

## Method

**Rubrics are resolved through each scenario's official evaluator, not through
the scenario default.** This matters and is not a formality — see Finding 2
in §7. The five bindings actually used:

| Scenario | Evaluator | Rubric file | Version | Criteria | Points |
|---|---|---|---|---:|---:|
| monday-001 | `evaluator-opus5-v0.1` | `rubric-0.2.yaml` | 0.2 | 19 | 90 + 10† |
| monday-002 | `evaluator-opus5-v0.2` | `rubric.yaml` | 0.2 | 20 | 100 |
| monday-003 | `evaluator-opus5-v0.3` | `rubric.yaml` | 0.3 | 21 | 100 |
| monday-004 | `evaluator-opus5-v0.4` | `rubric-0.3.yaml` | 0.3 | 27 | 100 |
| monday-005 | `evaluator-opus5-v0.5` | `rubric-0.4.yaml` | 0.4 | 31 | 100 |

† monday-001's atomic criteria sum to 90. The remaining 10 points are the
noise-resistance dimension, scored at dimension granularity rather than as
atomic criteria and mapped to `action_safety` with `granularity: dimension`.
All five scenarios contribute exactly 100.

A rubric's *filename* and its *version* are independent: monday-002 and
monday-003 both score against a file called `rubric.yaml`, at versions 0.2 and
0.3. Each evaluator's `rubric_file` matches its scenario's `FROZEN.yaml`
exactly, for all five.

**Aggregation, unchanged from v0.1.** Each criterion is mapped to exactly one
PRIMARY capability. Points count once, to the primary. A SECONDARY tag records
a real overlap and carries **zero** points — it is metadata, and §6 shows it
turning out to be a useful diagnostic in its own right. Each criterion is
averaged across a model's three official runs *before* summing, which is what
makes a capability profile reconcile with the scenario score instead of
approximating it.

**Penalties are excluded, unchanged from v0.1.** A scenario penalty is a global
deduction, not a criterion-level one; attributing one to a capability would
mean inventing an attribution. The consequence is stated rather than hidden:
qwen3.6 took a −7 `CONFIDENTIALITY_BREACH`-class deduction on monday-005
run-002, and that deduction appears in its Monday Score and **not** in its
capability profile. This is also the main reason `action_safety` reads 100% for
six of seven models.

**Official evaluations only.** The monday-005 calibration battery — 21 judged
runs against rubric 0.4's predecessors — lives under
`archive/monday-005-v0.4-calibration/` and contributes nothing. Pinned by
`test_calibration_evaluations_cannot_reach_the_profiles`.

---

## 1. What changed from v0.1

v0.2 is v0.1 **plus five capabilities and the monday-005 mapping**. Nothing in
v0.1 was renamed, merged, split, reweighted or remapped. All 88 historical
entries are carried verbatim — the artifact was generated from v0.1 rather than
retyped, and `test_v0_2_carries_every_v0_1_mapping_verbatim` compares them
entry by entry.

| | v0.1 | v0.2 |
|---|---|---|
| Capabilities | 17 | 22 |
| Criterion mappings | 88 | 119 |
| Points | 400 | 500 |
| Scenarios | 001–004 | 001–005 |

`taxonomy/capabilities-v0.1.yaml`, `analysis/capability-profiles-v0.1.json` and
`analysis/capability-taxonomy-v0.1.md` stay on disk unmodified as the immutable
historical snapshot.

### The five additions

Four of the five are exactly the gaps v0.1 named and could not measure:

| New capability | Points | v0.1 gap it closes |
|---|---|---|
| `audience_adaptation` | 17 | Gap 1 — communication to an audience, *completely absent* |
| `cross_output_consistency` | 16 | Gap 3 — *structurally impossible* with one output |
| `information_boundaries` | 13 | Gap 2 — one criterion, no discrimination |
| `commitment_discipline` | 10 | Gap 4 — adjacent but not covered |
| `information_routing` | 7 | *not from that list — see below* |

The fifth is the one finding in this release that came from the runs rather
than from the design. `information_routing` was not in the pre-calibration
proposal. It exists because monday-005 measured **suppression** and **delivery**
separately and they came apart:

- Across all 21 official runs, **no model disclosed any of the four
  confidential classes externally.** `information_boundaries` sits at 100% for
  six of seven models.
- The criterion asking whether *the same security item reached the engineering
  handoff* was among the most-failed in the scenario. `information_routing`
  runs 57.1 → 100.0.

Same information, same run, opposite results. Keeping "must not leave" and
"must arrive" in one capability would have averaged a solved problem against an
unsolved one. The split is a claim about what the benchmark **asks** — the
audience matrix carries REQUIRED cells for internal readers and PROHIBITED
cells for external ones, enforced by different criteria — not a claim about
which model failed.

### One candidate considered and rejected

`epistemic_state_management` — hypothesis vs confirmed cause, mitigated vs
resolved, verification underway — is a real distinction monday-005 tests
heavily (24 of its 100 points touch it). It is **not** a new capability because
v0.1 already absorbs it cleanly. `state_reconstruction` is defined as
determining the current state of a thing, with the failure mode of reporting a
state that was true earlier — that is precisely mitigated-vs-resolved.
`causal_discipline` is defined as refusing a causal claim the evidence does not
support — that is precisely hypothesis-vs-root-cause. Adding a sixth capability
here would have split two working ones rather than added anything, and would
have broken the v0.1-verbatim guarantee.

### The superseded proposal

`taxonomy/capabilities-v0.2-proposed.yaml` was written **before** monday-005 was
calibrated or run. It is kept, marked `status: superseded`, as the record of
what was predicted. It was adopted with exactly two changes, both caused by the
`information_routing` split:

| Criterion | Proposed primary | Adopted primary |
|---|---|---|
| `security_item_reaches_engineering` | `audience_adaptation` | `information_routing` |
| `hypotheses_carried_to_engineering` | `uncertainty_calibration` | `information_routing` |

Mass moved accordingly: `audience_adaptation` 20→17, `uncertainty_calibration`
8→4, `information_routing` 0→7. All 29 other monday-005 mappings were adopted
verbatim. `test_the_proposal_diverges_from_the_adopted_taxonomy_in_exactly_two_places`
pins the divergence, so a third silent move would fail the suite.

---

## 2. Coverage matrix

500 points, 119 criteria, 22 capabilities. Sorted by point mass.

| Capability | Pts | % suite | Crit | Scen | Scenarios | Sparsity |
|---|---:|---:|---:|---:|---|---|
| `quantitative_reasoning` | 66 | 13.2 | 16 | 4 | 001,002,004,005 | BROADLY_COVERED |
| `prioritization` | 60 | 12.0 | 11 | 3 | 001,002,003 | BROADLY_COVERED |
| `state_reconstruction` | 50 | 10.0 | 13 | 4 | 001,002,003,005 | BROADLY_COVERED |
| `planning` | 30 | 6.0 | 5 | 2 | 002,003 | MODERATELY_COVERED |
| `supersession` | 27 | 5.4 | 6 | 3 | 002,003,005 | MODERATELY_COVERED |
| `dependency_reasoning` | 25 | 5.0 | 5 | 2 | 002,003 | MODERATELY_COVERED |
| `action_safety` | 23 | 4.6 | 4 | 3 | 001,002,004 | MODERATELY_COVERED |
| `causal_discipline` | 23 | 4.6 | 8 | 4 | 001,002,004,005 | MODERATELY_COVERED |
| `uncertainty_calibration` | 23 | 4.6 | 7 | **5** | 001-005 | MODERATELY_COVERED |
| `business_judgment` | 21 | 4.2 | 6 | 1 | 004 | SINGLE_SCENARIO |
| `resource_allocation` | 21 | 4.2 | 3 | 1 | 003 | SINGLE_SCENARIO |
| `cross_source_reconciliation` | 18 | 3.6 | 4 | 2 | 002,004 | MODERATELY_COVERED |
| `audience_adaptation` | 17 | 3.4 | 5 | 1 | 005 | SINGLE_SCENARIO |
| `cross_output_consistency` | 16 | 3.2 | 4 | 1 | 005 | SINGLE_SCENARIO |
| `ownership_and_delegation` | 14 | 2.8 | 3 | 3 | 001,002,003 | SPARSE |
| `temporal_reasoning` | 14 | 2.8 | 3 | 2 | 002,003 | SPARSE |
| `information_boundaries` | 13 | 2.6 | 6 | 1 | 005 | SINGLE_SCENARIO |
| `commitment_discipline` | 10 | 2.0 | 3 | 1 | 005 | SINGLE_SCENARIO |
| `data_cleaning` | 10 | 2.0 | 2 | 1 | 004 | SINGLE_SCENARIO |
| `factual_accuracy` | 8 | 1.6 | 2 | 2 | 003,004 | SPARSE |
| `information_routing` | 7 | 1.4 | 2 | 1 | 005 | SINGLE_SCENARIO |
| `entity_resolution` | 4 | 0.8 | 1 | 1 | 004 | SINGLE_CRITERION |

Sparsity is mechanical, applied in this order: `SINGLE_CRITERION` if one
criterion; `SINGLE_SCENARIO` if one scenario; `SPARSE` if under 15 points;
`MODERATELY_COVERED` under 40; `BROADLY_COVERED` otherwise.

**Nine of 22 capabilities rest on a single scenario or a single criterion** —
39 criteria, 88 points. Five of the nine are the monday-005 additions, which is
expected on the day a scenario lands and is exactly the condition v0.1 flagged
for `entity_resolution` and `data_cleaning`. That condition has not improved for
those two: they are still #004-only, one Monday's evidence, 14 points carrying a
lot of inference.

**Only `uncertainty_calibration` is measured by all five scenarios.** Its 23
points come from five independent Mondays, and it is correspondingly the one
capability ranking I would trust most.

**Point mass is not importance.** `prioritization` has 60 points because three
scenarios happen to ask about it. Capability scores compare *models*, never
capabilities against each other.

---

## 3. Discrimination: how much of the suite actually measures anything

Two independent measures, both mechanical.

### 3a. Classification by observed spread

`range = best model - worst model` on that capability, across the seven models.

> `NON_DISCRIMINATING` range = 0 · `LOW_DISCRIMINATION` range < 10 ·
> `MEDIUM_DISCRIMINATION` range < 30 · `HIGH_DISCRIMINATION` range >= 30

The rule is stated because v0.1 had none — it discussed non-discrimination
narratively, and a reader could not reproduce the judgment. The thresholds are a
choice, not a discovery: they are round numbers on a 0-100 scale, and two
capabilities sit close enough to a boundary that a five-point shift would move
them (`commitment_discipline` at 30.0, `uncertainty_calibration` at 34.1).

| Class | n | Capabilities (range) |
|---|---:|---|
| HIGH | 12 | `entity_resolution` 100.0 · `quantitative_reasoning` 70.2 · `data_cleaning` 70.0 · `temporal_reasoning` 54.8 · `factual_accuracy` 54.2 · `business_judgment` 45.2 · `information_routing` 42.9 · `causal_discipline` 42.0 · `supersession` 40.1 · `cross_source_reconciliation` 38.9 · `uncertainty_calibration` 34.1 · `commitment_discipline` 30.0 |
| MEDIUM | 7 | `dependency_reasoning` 27.3 · `prioritization` 26.7 · `planning` 26.1 · `audience_adaptation` 18.7 · `state_reconstruction` 17.3 · `cross_output_consistency` 16.7 · `resource_allocation` 15.9 |
| LOW | 2 | `information_boundaries` 7.7 · `action_safety` 6.5 |
| NON | 1 | `ownership_and_delegation` 0.0 |

`entity_resolution` heads the list with a perfect 100.0 range and is the least
trustworthy entry in the table: one criterion, four points, one scenario, and
the range is produced by two models scoring zero on it. Large spread on thin
evidence is not strong discrimination — it is a coin landing on its edge.

### 3b. Observed mass — the more useful measure

Spread can be manufactured by one outlier on one criterion, so each criterion is
also classified directly: **CONSTANT_PASS** if every model earned full marks on
it in every official run, **CONSTANT_FAIL** if none ever earned any,
**DISCRIMINATING** otherwise.

> **367.0 of 500 points discriminate (73.4%). 133.0 are constant-pass. Zero are
> constant-fail.**

Zero constant-fail deserves stating plainly: **no criterion in MondayBench is
failed by every model.** Nothing in the suite is currently out of the field's
reach. Whether that means the benchmark is well-calibrated or simply not yet
hard enough is the question §5 turns on.

Where the dead weight sits:

| Capability | Pts | Discriminating | Constant-pass | Dead |
|---|---:|---:|---:|---:|
| `ownership_and_delegation` | 14 | 0 | 14 | **100%** |
| `action_safety` | 23 | 3 | 20 | 87% |
| `information_boundaries` | 13 | 2 | 11 | 85% |
| `information_routing` | 7 | 3 | 4 | 57% |
| `state_reconstruction` | 50 | 22 | 28 | 56% |
| `cross_output_consistency` | 16 | 8 | 8 | 50% |
| `audience_adaptation` | 17 | 10 | 7 | 41% |
| `prioritization` | 60 | 44 | 16 | 27% |
| *(the other 14)* | | | | <= 24% |

`ownership_and_delegation` is 14 points that have never once separated two
models, across three scenarios and 105 runs. It is not a badly designed
capability; it is a solved one. Assigning who owns a task is something every
model in this field does correctly every time. **It should not carry points in
#006.**

`action_safety` and `information_boundaries` need a caveat pulling the other
way. Both look solved partly *because* penalties are excluded from this analysis
(§7, Finding 3): the qwen3.6 monday-005 breach that cost -7 on the Monday Score
is invisible here. The honest reading is that models reliably clear the
*criterion-level* bar and occasionally trip the *penalty-level* one, and this
profile only sees the first.

---

## 4. Model capability profiles

Percent of available points, official runs only, penalties excluded.

| Capability | Pts | Qwen3.8F | GLM5.3F | DSV4F | MIMO | GLM5.2 | Qwen3.6 | Gemma4 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `quantitative_reasoning` | 66 | 93.2 | 97.7 | 83.8 | 81.3 | 79.0 | 56.8 | **27.5** |
| `prioritization` | 60 | 93.1 | 98.6 | 92.2 | 80.6 | 85.8 | 79.4 | 71.9 |
| `state_reconstruction` | 50 | 98.8 | 100.0 | 99.0 | 97.7 | 100.0 | 91.3 | 82.7 |
| `planning` | 30 | 86.1 | 82.8 | 91.1 | 87.2 | 81.1 | 68.9 | 65.0 |
| `supersession` | 27 | 93.1 | 100.0 | 93.8 | 90.7 | 90.7 | 74.7 | 59.9 |
| `dependency_reasoning` | 25 | 100.0 | 90.7 | 87.3 | 76.0 | 87.3 | 72.7 | 74.7 |
| `action_safety` | 23 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 93.5 |
| `causal_discipline` | 23 | 100.0 | 94.2 | 100.0 | 97.1 | 89.9 | **58.0** | 72.5 |
| `uncertainty_calibration` | 23 | 88.6 | 93.5 | 93.5 | 89.1 | 93.5 | 78.3 | 59.4 |
| `business_judgment` | 21 | 97.6 | 97.6 | 85.7 | 85.7 | **61.9** | 52.4 | 59.5 |
| `resource_allocation` | 21 | 79.4 | 87.3 | 80.2 | 87.3 | 74.6 | 78.6 | 71.4 |
| `cross_source_reconciliation` | 18 | 95.8 | 100.0 | 100.0 | 96.3 | 100.0 | 81.5 | 61.1 |
| `audience_adaptation` | 17 | 94.1 | 97.1 | 97.1 | 97.1 | 97.1 | 78.4 | 85.3 |
| `cross_output_consistency` | 16 | 100.0 | 100.0 | 95.8 | 100.0 | 100.0 | 83.3 | 100.0 |
| `ownership_and_delegation` | 14 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 |
| `temporal_reasoning` | 14 | 78.6 | 64.3 | 71.4 | 71.4 | 71.4 | 46.4 | **23.8** |
| `information_boundaries` | 13 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 92.3 | 100.0 |
| `commitment_discipline` | 10 | 100.0 | 100.0 | 100.0 | 76.7 | 100.0 | 70.0 | 100.0 |
| `data_cleaning` | 10 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 66.7 | **30.0** |
| `factual_accuracy` | 8 | 87.5 | **50.0** | 87.5 | **47.9** | 64.6 | **33.3** | 68.8 |
| `information_routing` | 7 | 71.4 | 100.0 | 85.7 | 85.7 | 85.7 | 71.4 | 57.1 |
| `entity_resolution` | 4 | 100.0 | 100.0 | 100.0 | 66.7 | 66.7 | **0.0** | **0.0** |

Summary, with Monday Score (Overall v2) alongside:

| Model | Monday | Cap. mean | Cap. median | Best | **Worst** | Spread |
|---|---:|---:|---:|---:|---:|---:|
| Qwen 3.8 Flash | 95.1 | 93.5 | 96.7 | 100.0 | **71.4** | 28.6 |
| GLM 5.3 Flash | 94.9 | 93.4 | 99.3 | 100.0 | **50.0** | 50.0 |
| DeepSeek V4 Flash | 91.7 | 92.9 | 94.8 | 100.0 | **71.4** | 28.6 |
| MIMO v2.5 | 86.7 | 87.0 | 88.2 | 100.0 | **47.9** | 52.1 |
| GLM 5.2 | 86.5 | 87.7 | 90.3 | 100.0 | **61.9** | 38.1 |
| Qwen 3.6 | 68.8 | 69.7 | 73.7 | 100.0 | **0.0** | 100.0 |
| Gemma 4 | 63.0 | 66.5 | 70.1 | 100.0 | **0.0** | 100.0 |

Capability mean is an unweighted average over 22 capabilities and is **not** a
rival to Monday Score — it treats a 4-point capability and a 66-point one as
equals. It is shown only because the reordering it produces is itself
informative: **MIMO v2.5 and GLM 5.2 swap places.** MIMO wins on Monday Score by
0.2 and loses on capability mean by 0.7. Neither ordering is wrong; they answer
different questions. A 0.2-point gap on Monday Score was never a ranking.

---

## 5. What the profiles say

### The leaderboard's top two are not the same product

Qwen 3.8 Flash 95.1, GLM 5.3 Flash 94.9. On Monday Score they are
indistinguishable. On capability shape they are not remotely alike:

| | Qwen 3.8 Flash | GLM 5.3 Flash |
|---|---:|---:|
| Capability mean | 93.5 | 93.4 |
| Capability **median** | 96.7 | **99.3** |
| Worst capability | 71.4 (`information_routing`, 7 pts) | **50.0** (`factual_accuracy`, 8 pts) |
| Spread | 28.6 | **50.0** |
| Capabilities at 100% | 9 | **11** |
| Capabilities below 80% | 3 | 2 |

GLM 5.3 Flash has the higher ceiling — a 99.3 median and eleven perfect
capabilities against Qwen's nine — and the lower floor. Qwen 3.8 Flash never
drops below 71.4 on anything. **This is the floor-versus-peak trade-off, and the
data supports it.** If the deployment tolerates an occasional bad output in
exchange for more excellent ones, GLM 5.3 Flash is the better pick. If a single
bad output is expensive — which describes most of the work these scenarios
imitate — Qwen 3.8 Flash is, and the 0.2-point Monday Score gap understates by
how much.

GLM 5.3 Flash's specific hole is worth naming: **`factual_accuracy` 50.0 on 8
points.** It is the second-best model in the suite at getting the *reasoning*
right and roughly a coin-flip at carrying a *number* through unchanged.

### v0.1's sharpest prediction was correct, and its most quotable finding was wrong

v0.1 predicted that #004's `figures_carried_correctly` would "confirm the split
rather than close it" on `factual_accuracy`. With #004 official, the capability
has doubled from 5 points to 8 and the split held: 33.3 to 87.5, with GLM 5.3
Flash still at 50.0. **Confirmed.**

v0.1 also said Gemma 4 "copies accurately and computes badly" — 100% on
`factual_accuracy` against 28.6% on `quantitative_reasoning`. That story does
not survive the extra evidence. Gemma 4's `factual_accuracy` is now **68.8**,
because the 100% rested on a single 5-point criterion from monday-003 and
monday-004's second criterion went badly. The computation half stands
unchanged — `quantitative_reasoning` 27.5 on **66 points**, the largest single
weakness anywhere in this table. The accurate-copier half was an artifact of
five points of evidence.

That is the strongest argument in this document for treating SPARSE and
SINGLE_CRITERION capabilities as provisional. It is also why v0.1 is kept
unmodified rather than corrected: the correction belongs here, where the
evidence that produced it is.

### Qwen 3.6 and Gemma 4 fail differently

Both sit far below the field (68.8 and 63.0) and both have a 100.0 spread, both
courtesy of `entity_resolution` at zero. Underneath, they are unlike:

- **Qwen 3.6** collapses on *discipline*: `causal_discipline` 58.0 (worst in the
  field, 23 points), `factual_accuracy` 33.3, `commitment_discipline` 70.0,
  `cross_output_consistency` 83.3, and it is the only model to breach an
  information boundary at all (92.3, plus the -7 penalty this profile excludes).
  It is a model that reaches for a conclusion and then overstates it.
- **Gemma 4** collapses on *quantity and time*: `quantitative_reasoning` 27.5,
  `temporal_reasoning` 23.8, `data_cleaning` 30.0 — while scoring 100.0 on
  `commitment_discipline`, 100.0 on `cross_output_consistency` and 100.0 on
  `information_boundaries`. It is careful about what it says and unreliable
  about what it counts.

Practically: Gemma 4 is safer to let write to a customer than Qwen 3.6, and
neither should be shown a spreadsheet. Monday Score puts them 5.8 points apart
and says none of that.

### GLM 5.2 and MIMO v2.5: the same score, opposite risk profiles

86.5 and 86.7 — a 0.2 gap, the same near-tie as the top two, and again the
shapes diverge. GLM 5.2's worst capability is `business_judgment` at 61.9, and
that is **21 points wide across six criteria**. MIMO's worst is
`factual_accuracy` at 47.9, **8 points across two criteria in two scenarios**.
MIMO's number is lower and rests on a quarter of the evidence. GLM 5.2's
weakness is the better-established of the two and the more consequential:
`business_judgment` is what monday-004 asks about end-to-end, and 61.9 on it
means the model does the analysis and then draws the wrong conclusion from it.

### Rank order is still not capability order

DeepSeek V4 Flash is third on Monday Score and joint-first or outright first on
**12 of 22 capabilities** — exactly as many as Qwen 3.8 Flash, which leads the
board. And it is the **sole** leader on `planning` (91.1), ahead of both models
above it. Anyone choosing a model for work that is mostly *planning under
constraints* should be reading this table, not the leaderboard.

The count that does track the leaderboard is GLM 5.3 Flash's: first or joint-first
on 17 of 22, sole leader on 4. Its 94.9 is not built on breadth failing to show
up in the ranking — it is built on one 50.0 dragging an otherwise dominant profile
down, which is the §5 floor argument from the other direction.

---

## 6. Did the boundary/routing split earn its place?

The split was proposed on design grounds and could have been wishful. The
evidence is unambiguous:

| | `information_boundaries` | `information_routing` |
|---|---|---|
| Points | 13 (6 criteria) | 7 (2 criteria) |
| Range | **7.7** | **42.9** |
| Class | LOW_DISCRIMINATION | HIGH_DISCRIMINATION |
| Models at 100% | 6 of 7 | 1 of 7 |
| Discriminating mass | 2 of 13 (15%) | 3 of 7 (43%) |

Suppressing confidential material is, for this field, a solved problem: across
21 official monday-005 runs no model put the security item, another customer's
identity, personal data, fleet topology or the cause investigation into an
external artifact. Making sure the *same* item reaches the engineer who needs it
is not solved: `security_item_reaches_engineering` is among the most-failed
criteria in the scenario, and Gemma 4 sits at 57.1 on the capability.

Had these stayed merged, the combined capability would have read ~92% with a
range near 12 — MEDIUM at best, and the actual finding, that models are much
better at withholding than at delivering, would have been averaged out of
existence. **The split is validated.**

The mirror-image caveat from §3b applies: `information_boundaries` looks solved
because criteria measure it and the penalty does not enter here. Six models at
100% and one −7 penalty is a different picture from six models at 100%.

---

## 7. Findings documented, not fixed

Both are real defects in the repository. Neither is corrected here, because
correcting them would modify historical artifacts the release is required to
leave alone.

### Finding 1 — `analysis/capability-profiles-v0.1.json` is stale relative to its own taxonomy

`taxonomy/capabilities-v0.1.yaml` maps **88 criteria across monday-001…004, 400
points, 17 capabilities**. The profiles JSON published alongside it covers
**monday-001…003, 300 points, 14 capabilities**. It was generated before
monday-004 was official — its own report says so, predicting what
`figures_carried_correctly` "will" do — and was never rebuilt after #004 was
published.

The three missing capabilities are exactly the monday-004-only ones:
`business_judgment`, `data_cleaning`, `entity_resolution`.

**Impact:** the v0.1 artifact set is internally inconsistent, and anyone reading
`capability-profiles-v0.1.json` as "the v0.1 taxonomy applied to the suite" gets
a 300-point answer to a 400-point question. This is how the Gemma 4
accurate-copier claim in §5 came to be published.

**REPAIRED on 2026-08-31, in the v1.0 close.** Not by rewriting the file —
that would silently move numbers a reader may already have cited — but by
publishing the corrected revision alongside it:

- `analysis/capability-profiles-v0.1.1.json` applies the *same, unmodified* v0.1
  taxonomy to all four of its scenarios: 400 points, 17 capabilities, v0.1's
  schema so it is a drop-in replacement.
- `analysis/capability-profiles-v0.1.json` is byte-identical to what was
  published, and `tests/test_capability_profiles_v011.py` keeps it that way.
- `analysis/capability-taxonomy-v0.1.md` now opens with an erratum naming the
  one finding that did not survive the extra evidence — the Gemma 4
  accurate-copier claim.

The rebuild shows the staleness was material, not cosmetic:
`quantitative_reasoning` was carrying **21 of its 63 points**, and Gemma 4's
`factual_accuracy` falls **31.2 points** once monday-004 is included.

The root cause — a profile build that silently used whichever scenarios happened
to be official rather than the ones the taxonomy maps — is now pinned by
`test_a_profile_build_covers_every_scenario_its_taxonomy_maps` and
`test_the_point_mass_of_a_profile_set_matches_its_taxonomy`, which check both
published profile sets.

### Finding 2 — `load_scenario("monday-001")` returns a rubric the scenario is not frozen against

`scenarios/monday-001/scenario.yaml` declares no `rubric_file`. `load_scenario`
therefore defaults to `rubric.yaml`, which is **version 0.1 and superseded**,
while `FROZEN.yaml` freezes the scenario against `rubric-0.2.yaml` and
`evaluator-opus5-v0.1` scores against `rubric-0.2.yaml`.

Any analysis that calls `load_scenario("monday-001")` without an explicit
`rubric_file` silently reads the wrong criteria for monday-001 — different
criterion ids, different points — and every other scenario reads correctly,
which makes it the hardest kind of bug to notice.

**Impact on this release: none.** Every rubric here was already resolved through
the official evaluator's declared `rubric_file` (see Method), so no number in
this report was ever computed from the wrong criteria. Since the repair, a plain
`load_scenario(scenario_id)` returns the same rubric for all five scenarios, and
that equivalence is asserted rather than assumed.

**REPAIRED on 2026-08-31, in the v1.0 close — and by a better route than the
one proposed here.** Editing `scenario.yaml` would have meant mutating a frozen,
hashed artifact and re-freezing a published scenario. That turned out to be
unnecessary: **`FROZEN.yaml` already recorded `rubric_file: rubric-0.2.yaml`**,
and across all five scenarios every evaluator's `rubric_file` matches its
manifest exactly. The manifest was already the truth; only the resolver was not
reading it.

`load_scenario` now resolves in this order — explicit argument, `scenario.yaml`,
`FROZEN.yaml`, directory default — and **refuses** when `scenario.yaml` and
`FROZEN.yaml` name different rubrics, since one of the two is then wrong and the
loader cannot know which. No frozen artifact was edited; `check_drift` is clean
for all five scenarios and is asserted to be.

The repair also surfaced four 0.1-era evaluators (`evaluator-manual-v0.1`,
`evaluator-v0.1`, `evaluator-open-v0.1`, `evaluator-gateway-v0.1`) that were
relying on the old implicit default to reach rubric 0.1. They now declare
`rubric_file: rubric.yaml` explicitly. None had produced a published evaluation.

24 regression tests in `tests/test_rubric_resolution.py`, all of which fail on
the pre-repair resolver.

### Finding 3 — the penalty exclusion, restated

Carried from v0.1 unchanged and repeated because it materially shapes §3b:
capability profiles exclude scenario penalties. `action_safety` (100% for six of
seven) and `information_boundaries` (100% for six of seven) are the two
capabilities most distorted by this. Flagged, not fixed — attributing a global
deduction to a capability would mean inventing the attribution.

---

## 8. What MondayBench still does not measure

v0.1 listed six gaps. Here is where each stands after #005, followed by three
that are new.

| # | v0.1 gap | Status after #005 |
|---|---|---|
| 1 | Communication to an audience | **CLOSED.** `audience_adaptation`, 17 pts, 5 criteria, MEDIUM discrimination |
| 2 | Information boundaries | **CLOSED, and the bar is still low.** 13 pts but 85% constant-pass; LOW discrimination |
| 3 | Cross-output consistency | **CLOSED.** 16 pts, 4 criteria, MEDIUM discrimination |
| 4 | Commitment discipline | **CLOSED.** 10 pts, 3 criteria, HIGH discrimination |
| 5 | Temporal reasoning | **OPEN, unchanged.** Still 14 pts, still 2 scenarios, still the field's worst capability |
| 6 | Entity resolution / data cleaning | **OPEN, unchanged.** Still #004-only, 4 and 10 pts |

Four of six closed in one scenario. Two untouched — and #005 was designed to
close the first four, so this is the design working, not luck.

### The shadow-mass diagnostic

A capability's SECONDARY tags carry no points but do record where a criterion
*also* measures something. Comparing shadow mass to primary mass shows which
capabilities the benchmark keeps invoking without ever scoring directly:

| Capability | Primary pts | Shadow pts | Ratio |
|---|---:|---:|---:|
| **`temporal_reasoning`** | **14** | **22** | **1.57** |
| `causal_discipline` | 23 | 26 | 1.13 |
| `factual_accuracy` | 8 | 7 | 0.88 |
| `information_boundaries` | 13 | 11 | 0.85 |
| `uncertainty_calibration` | 23 | 17 | 0.74 |
| `commitment_discipline` | 10 | 7 | 0.70 |
| *(16 others)* | | | <= 0.65 |

`temporal_reasoning` is the **only** capability in the suite whose shadow mass
exceeds its primary mass. Twenty-two points of criteria depend on getting time
right while scoring something else, against fourteen points that score it
directly. The benchmark leans on it constantly and tests it barely.

### New gaps, visible only now

**7. Nothing is out of reach.** Zero of 500 points are constant-fail. Every
criterion in MondayBench has been passed by at least one model in at least one
run. A benchmark whose hardest question is answerable by the field has a ceiling
problem coming, even if it has not arrived: the top two are at 95.1 and 94.9,
and 133 points are already dead weight.

**8. Multi-turn work is entirely absent.** All five scenarios are single-turn:
one prompt, one response, judged. Nothing measures what happens when the
requester replies "that's not what I meant", when new information arrives
mid-task, or when the model must ask a question before it can proceed.
Realistically, more of a knowledge worker's Monday is spent in that mode than in
the one MondayBench measures. This is a larger hole than anything in the v0.1
list and it is structural — no rubric change closes it.

**9. `ownership_and_delegation` is measured and settled.** 14 points, three
scenarios, 105 runs, zero discrimination ever. It is now a coverage cost rather
than a coverage gap.

---

## 9. Ranked gaps, and the #006 recommendation

Ranked by *value of the information a scenario would add*, which is discriminating
power expected times the cost of getting it wrong in real work:

**1. Temporal reasoning under a moving clock.** Worst capability in the field
(mean 61.0), thinnest primary coverage relative to how much the suite depends on
it (shadow ratio 1.57), and consistent across all seven models over two
scenarios — hard to explain as noise. It has been the top open gap since v0.1
and #005 did not touch it. Every model in this set is deployed against calendars,
deadlines and SLAs.

**2. Multi-turn correction and clarification.** The largest structural hole.
Currently unmeasurable at any point value.

**3. Entity resolution and data cleaning at more than one Monday.** 14 points on
one scenario, and `entity_resolution` produces the widest spread in the whole
table (100.0) off a single 4-point criterion. Either the capability is genuinely
bimodal or the criterion is fragile, and one scenario cannot tell us which.

**4. A criterion the field actually fails.** Not a capability — a calibration
target. With zero constant-fail points, the suite has no evidence about where
the frontier is.

**5. Raising the information-boundaries bar.** 85% constant-pass. The capability
exists but the questions are too easy.

**6. Retiring `ownership_and_delegation` points.** Housekeeping, not a gap.

### Recommendation

> ## RECOMMEND #006

**Subject: temporal reasoning under a moving clock, delivered as a multi-turn
scenario.**

The argument, briefly. Gaps 1 and 2 are the two that matter and they compose
naturally rather than competing: a scenario where the clock moves *between
turns* — a deadline slips, a meeting is rescheduled mid-conversation, the
requester corrects a date you already reasoned from — tests temporal reasoning
and multi-turn correction with the same material. Neither is reachable by
editing an existing rubric; both need a new Monday. And temporal reasoning is
the rare case where the benchmark already knows the answer will be
discriminating: mean 61.0 with a 54.8 range on only 14 points.

Design constraints this analysis implies, which are inputs to the #006 design
and not a design:

- **Do not re-measure the solved.** `ownership_and_delegation` (0% discriminating
  across 105 runs) and the easy end of `action_safety` and
  `information_boundaries` (87% and 85% constant-pass) should carry few points
  or none. That frees roughly 30 points of a 100-point budget.
- **Aim at least a few points above the field.** #006 is the place to
  deliberately include criteria the current top model is expected to fail. The
  suite currently has none, and without them the leaderboard will compress.
- **Temporal reasoning should be the primary, not the shadow.** The 1.57 ratio
  is the specific defect to correct: at least 25 points scoring time directly.
- **Multi-turn requires harness work before scenario work.** Every existing
  scenario is one prompt and one response; runner, evaluator and freeze
  manifest all assume that. That work must be scoped and confirmed as not
  affecting #001-#005 before #006 content is written — the same rule that
  governed #005.

**What would change this recommendation:** if the multi-turn harness work is
larger than a scenario's worth of effort, split it — do a single-turn temporal
scenario for #006 and hold multi-turn for #007. Gap 1 is worth a Monday on its
own.

---

## 10. Limitations of this release

**This is not a scoring system and must not become one.** Capability mean is
shown in §4 with an explicit warning; it is an unweighted average across
capabilities of wildly different mass and it is not a model ranking.

**Capability scores compare models, not capabilities.** `prioritization` at 60
points and `entity_resolution` at 4 are not comparable quantities. Reading down
a column is valid; reading across the "Pts" column as importance is not.

**Discrimination thresholds are a choice.** Stated in §3a so they can be
disagreed with. The observed-mass measure in §3b is threshold-free and should be
preferred where the two disagree.

**Seven models is a small field.** A "range" is a max-minus-min over seven
points. `NON_DISCRIMINATING` means "did not separate these seven", not "cannot
separate models".

**Three official runs per model per scenario.** Each criterion is averaged over
three runs before summing, which is exact and reconciles with the scenario mean
by construction, but three is few. Per-criterion run variance is preserved in
the evaluation records for anyone who wants it.

**The judge is recorded, not sampled.** Every verdict in this analysis was
produced in-session and replayed. Judge variance cannot be estimated from these
artifacts, and no claim here should be read as controlling for it.

**Penalties excluded** — see §7, Finding 3.

**The five new capabilities rest on one Monday.** `audience_adaptation`,
`information_boundaries`, `information_routing`, `cross_output_consistency` and
`commitment_discipline` are all SINGLE_SCENARIO. The Gemma 4 correction in §5 is
a live demonstration of what single-scenario evidence is worth. Treat all five
as provisional until a second scenario touches them.

---

## Reproducing

```bash
uv run python - <<'PY'
import yaml, json
from pathlib import Path
from mondaybench.scenarios import load_scenario
from mondaybench.capabilities import (
    load_taxonomy, rubric_points, official_criterion_results, build_profiles)

EV = {"monday-001": "evaluator-opus5-v0.1", "monday-002": "evaluator-opus5-v0.2",
      "monday-003": "evaluator-opus5-v0.3", "monday-004": "evaluator-opus5-v0.4",
      "monday-005": "evaluator-opus5-v0.5"}

# Resolve each rubric through the evaluator, NOT through the scenario default.
# monday-001 declares no rubric_file and would otherwise load the superseded
# rubric.yaml (0.1). See Finding 2.
rubrics = {}
for s, e in EV.items():
    rf = yaml.safe_load(Path(f"evaluators/{e}.yaml").read_text(encoding="utf-8"))["rubric_file"]
    rubrics[s] = load_scenario(s, rubric_file=rf).rubric

tx = load_taxonomy("0.2")
pts = rubric_points(rubrics)
assert round(sum(pts.values()), 1) == 500.0

profiles, warnings = build_profiles(
    tx, {s: official_criterion_results(EV[s], s) for s in EV})
assert not warnings
# CapabilityScore(capability='quantitative_reasoning', earned=18.1667,
#                 possible=66.0, criteria=16)  ->  27.5%
print(profiles["gemma4"]["quantitative_reasoning"])
PY
```

```bash
uv run pytest tests/test_capabilities_v02.py tests/test_monday_005.py -q
```

---

## Artifacts

| Path | What it is |
|---|---|
| `taxonomy/capabilities-v0.2.yaml` | 22 capabilities, 119 mappings, 500 pts. v0.1's 88 entries verbatim |
| `analysis/capability-profiles-v0.2.json` | Per-model, per-capability earned/possible/percent + coverage, sparsity, discrimination, observed mass |
| `analysis/capability-taxonomy-v0.2.md` | This report |
| `tests/test_capabilities_v02.py` | 19 tests: completeness, mass, immutability, official-only, determinism, independence |
| `taxonomy/capabilities-v0.1.yaml` | Unmodified. Historical snapshot |
| `analysis/capability-profiles-v0.1.json` | Unmodified. **Stale — see Finding 1** |
| `taxonomy/capabilities-v0.2-proposed.yaml` | Unmodified below its header. Marked `superseded`; kept as the pre-calibration record |

Nothing under `scenarios/`, `evaluations/`, `runs/`, `leaderboard/` or
`overall-releases.yaml` was touched.
