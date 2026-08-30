# MondayBench capability taxonomy v0.1

**Not a scoring system.** No scenario score, rubric or published result changes
because of anything here. The taxonomy answers a different question from the
leaderboard: the leaderboard says how far a model got, this says where it lost
the points.

- Mapping: [`taxonomy/capabilities-v0.1.yaml`](../taxonomy/capabilities-v0.1.yaml)
- Calculator: `mondaybench/capabilities.py`
- Built from all 87 atomic criteria in monday-001, 002, 003 and monday-004
  rubric 0.3, plus monday-001's noise dimension — 88 mapped entries, 400 points
- Model profiles use **official results only**, which today means #001–#003

## Method

Derived bottom-up. I read every criterion's PASS definition and grouped by the
behaviour it actually tests, then checked the candidate structure against what
was left over — rather than starting from a generic taxonomy and forcing 87
criteria into it. Three of the candidate capability names survived contact
with the criteria unchanged; three were merged; one group turned out to be
almost entirely absent from the benchmark, which is the most useful finding
here.

**Aggregation.** A capability score is `points earned / points available × 100`
over its criteria, with each criterion's earned points averaged across the
model's three official runs *before* summing — the same aggregation the
scenario score uses. No best-of-three, no reweighting between capabilities: the
natural point mass of the rubrics is the weighting, and it is published below so
a reader can see how uneven it is.

**Primary only.** Twenty-one criteria carry a secondary tag. Those points count
once, toward the primary. Counting them twice would make two capability scores
silently dependent on the same criterion and inflate whichever denominators
happened to overlap. The secondary tag is metadata that records the overlap.

---

## 1. The taxonomy

Seventeen capabilities in three groups.

### Information handling

| Capability | What it tests |
|---|---|
| `state_reconstruction` | The current state of a thing, from evidence that is scattered and partly out of date |
| `supersession` | A later source overrides an earlier one, and both are present |
| `cross_source_reconciliation` | One finding no single source supports — or refusing one a single source appears to support |
| `data_cleaning` | Artifacts in the data itself: duplicates, values on a non-comparable basis |
| `entity_resolution` | Joining records whose identifiers differ between files |
| `factual_accuracy` | Carrying supplied values through without corrupting them |

### Reasoning

| Capability | What it tests |
|---|---|
| `quantitative_reasoning` | The right figure on the right basis: denominators, distributions, like-for-like |
| `temporal_reasoning` | Dates, durations, deadlines, availability windows |
| `dependency_reasoning` | What must precede what, and which chain sets the date |
| `causal_discipline` | Reporting the pattern while refusing the mechanism |
| `uncertainty_calibration` | Naming what cannot be determined, and what would settle it |

### Execution and judgment

| Capability | What it tests |
|---|---|
| `prioritization` | What needs action now, in what order, without displacement by closed or cosmetic items |
| `planning` | A sequence that actually runs |
| `resource_allocation` | Contention for a scarce person or window |
| `ownership_and_delegation` | Who currently owns the work, and who should |
| `business_judgment` | Turning an analysis into a decision, on the metric the decision depends on |
| `action_safety` | Declining actions the evidence rules out |

### What was merged, and why

- **`action_identification` → `prioritization`.** monday-001 splits "which items
  need action today" (25 points) from "which comes first" (15 points). Across
  the eight criteria involved the two are not separable: `contoso_action` and
  `contoso_first` are the same judgment written twice. Kept as one capability,
  flagged for revisiting if a later scenario genuinely separates them.
- **`constraint_reasoning` → `resource_allocation` and `planning`.** Every
  constraint in the set is a person or a window being scarce — Marcus, Elena's
  Wednesday departure, the 11:00 deadline — and is already scored as allocation
  or as schedule feasibility.
- **`delegation` → `ownership_and_delegation`.** Four criteria ask who owns a
  piece of work; none asks whether to delegate separately from to whom.

### Criteria the taxonomy fits least well

Recorded rather than hidden — a taxonomy with a clean home for everything is
usually concealing a stretch. Five are listed in the mapping file. The one that
matters:

> **`monday-004.revenue_conclusion`** is filed under `business_judgment`, but
> what it measures is whether the conclusion reached the reader instead of
> staying in the workings. That is executive communication, and MondayBench has
> no capability for it because nothing else measures it.

---

## 2. Coverage

All 400 mapped points, across the four scenarios.

| Capability | Group | Criteria | Points | Scenarios | |
|---|---|---:|---:|---|---|
| `quantitative_reasoning` | reasoning | 15 | 63 | #001 #002 #004 | |
| `prioritization` | execution | 11 | 60 | #001 #002 #003 | |
| `planning` | execution | 5 | 30 | #002 #003 | |
| `state_reconstruction` | information | 7 | 30 | #001 #002 #003 | |
| `dependency_reasoning` | reasoning | 5 | 25 | #002 #003 | |
| `action_safety` | execution | 4 | 23 | #001 #002 #004 | |
| `supersession` | information | 5 | 23 | #002 #003 | |
| `business_judgment` | execution | 6 | 21 | #004 | **sparse — one scenario** |
| `resource_allocation` | execution | 3 | 21 | #003 | **sparse — one scenario** |
| `uncertainty_calibration` | reasoning | 6 | 19 | #001 #002 #003 #004 | |
| `cross_source_reconciliation` | information | 4 | 18 | #002 #004 | |
| `causal_discipline` | reasoning | 6 | 17 | #001 #002 #004 | |
| `ownership_and_delegation` | execution | 3 | 14 | #001 #002 #003 | |
| `temporal_reasoning` | reasoning | 3 | 14 | #002 #003 | |
| `data_cleaning` | information | 2 | 10 | #004 | **sparse — one scenario** |
| `factual_accuracy` | information | 2 | 8 | #003 #004 | |
| `entity_resolution` | information | 1 | 4 | #004 | **sparse — one criterion** |

Every rubric criterion is mapped; nothing in the mapping is absent from a
rubric. Both directions are asserted in the tests.

### Sparse capabilities

Four, and they need different responses.

**`entity_resolution` — one criterion, 4 points, one scenario.** The weakest
entry in the taxonomy. It exists because `customer_id_alias_resolved` measures
something no other criterion touches, and because the trap it guards is real —
a naive join silently drops a €1M account. But one criterion measures one
rubric author's phrasing as much as it measures the model. It should either
recur in a later scenario or be folded into `cross_source_reconciliation`.

**`data_cleaning` — two criteria, one scenario.** Both from #004, and both
about the same pack. It is a genuine capability with a real failure mode; it
just has not been asked twice.

**`business_judgment` and `resource_allocation` — several criteria each, but
confined to one scenario.** Less alarming: within their scenario each has
enough criteria to be more than a single judgment. But a model's score on them
is a score on one Monday, not on the capability.

### Non-discriminating capabilities

Two capabilities score **100% for every model** in the official set:

- `action_safety` (20 points across #001–#002)
- `ownership_and_delegation` (14 points across #001–#003)

Every model declines the prohibited action and identifies the current owner.
Thirty-four points of rubric mass currently separate nobody. That is not a
reason to remove them — a benchmark needs criteria that catch a catastrophic
failure even when nobody commits it — but it does mean these capabilities are
reported without evidence of difficulty, and #004 will change that: three of
its five penalty-triggering runs recommended a prohibited action.

---

## 3. Model capability profiles

**Official scenarios only: #001–#003.** monday-004 is frozen but its official
battery is incomplete, so nothing from it enters these numbers. Three
capabilities therefore have **no official coverage at all** yet:
`business_judgment`, `data_cleaning` and `entity_resolution` — all three are
measured only by #004.

| Model | temporal | factual | quant | resource | planning | uncert | superseds | dependency | prioritiz | causal | state | cross-src | action | ownership |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DeepSeek V4 Flash | 71.4 | 100.0 | 85.7 | 80.2 | 91.1 | 90.0 | 92.8 | 87.3 | 92.2 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 |
| Qwen 3.8 Flash | 78.6 | 100.0 | 88.1 | 79.4 | 86.1 | 82.5 | 91.8 | 100.0 | 93.1 | 100.0 | 97.9 | 92.5 | 100.0 | 100.0 |
| GLM 5.3 Flash | 64.3 | 50.0 | 92.9 | 87.3 | 82.8 | 90.0 | 100.0 | 90.7 | 98.6 | 97.2 | 100.0 | 100.0 | 100.0 | 100.0 |
| MIMO v2.5 | 71.4 | 66.7 | 85.7 | 87.3 | 87.2 | 83.3 | 89.1 | 76.0 | 80.6 | 100.0 | 97.2 | 100.0 | 100.0 | 100.0 |
| GLM 5.2 | 71.4 | 83.3 | 76.2 | 74.6 | 81.1 | 90.0 | 89.1 | 87.3 | 85.8 | 94.4 | 100.0 | 100.0 | 100.0 | 100.0 |
| Qwen 3.6 | 46.4 | 33.3 | 81.0 | 78.6 | 68.9 | 66.7 | 70.3 | 72.7 | 79.4 | 73.6 | 85.6 | 93.3 | 100.0 | 100.0 |
| Gemma 4 | 23.8 | 100.0 | 28.6 | 71.4 | 65.0 | 60.0 | 52.9 | 74.7 | 71.9 | 77.8 | 71.1 | 70.0 | 100.0 | 100.0 |

Points available per capability in the official set are uneven and small in
places — `factual_accuracy` is a single 5-point criterion, `cross_source_
reconciliation` is 10 points. Read the sparse rows as directional.

### What the profiles say

**Temporal reasoning is the benchmark's hardest capability, for everyone.**
Mean 61.0%, and the best model in the set reaches 78.6%. Every other capability
has at least one model at or near 100%. Three criteria and 14 points is thin
evidence, but the pattern is consistent across all seven models, which is
harder to explain as noise than as difficulty.

**Factual accuracy separates models more than anything else and does it on one
criterion.** 33.3% to 100.0%, a 66.7-point spread from `factual_plan_accuracy`
alone. GLM 5.3 Flash — second overall on Monday Score — sits at 50%. This is
the profile's sharpest signal and its most fragile: #004's
`figures_carried_correctly` will roughly double the evidence, and the
calibration battery suggests it will confirm the split rather than close it.

**Gemma 4's profile is not a weaker version of the others; it is a different
shape.** 28.6% on quantitative reasoning and 23.8% on temporal against 100% on
factual accuracy and 71.9% on prioritization. It copies accurately and computes
badly. The Monday Score of 63.4 does not say that; the profile does.

**Rank order is not capability order.** Qwen 3.8 Flash leads Overall v0 but is
fourth on resource allocation. GLM 5.3 Flash is second overall and last but one
on factual accuracy. DeepSeek V4 Flash is third overall and first or joint-first
on six of fourteen capabilities.

---

## 4. Limitations

**Multi-run aggregation.** Per-criterion `points_awarded` is preserved per run,
so averaging each criterion across the three official runs before summing is
exact, and it reconciles with the scenario mean by construction. No precision is
faked.

**The noise dimension enters at dimension granularity.** monday-001 scores noise
resistance as a 10-point dimension with six named false actions rather than as
atomic criteria. It is included in `action_safety` because excluding a real
10-point measurement of exactly that capability would understate its coverage
by a third, and it is flagged `granularity: dimension` in the mapping so no
reader mistakes it for an atomic criterion. Its per-run false-action flags are
recorded, but the deduction arithmetic that turns them into a dimension score
belongs to the scoring module, so the dimension score is used as given.

**Point mass is not a difficulty measure.** `prioritization` has 60 points
because three scenarios happen to ask about it, not because it is four times as
important as `supersession`. Capability scores are comparable across models,
not across capabilities.

**Penalties are excluded.** Scenario penalties are global deductions, not
criterion-level, so they cannot be attributed to a capability without inventing
an attribution. A model that recommended a prohibited action loses points on
the scenario score but not on its `action_safety` profile — which is exactly
why `action_safety` reads 100% for everyone. Flagged rather than fixed.

---

# WHAT MONDAYBENCH DOES NOT MEASURE YET

The taxonomy's most useful output. Six gaps, ordered by how badly they matter.

### 1. Communication to an audience — completely absent

Nothing in 400 points measures whether a model can say the right thing to a
particular reader. Every scenario asks for one artifact, addressed to one
implicit audience (the user), scored on whether it contains the right
conclusions. The single criterion that touches it —
`monday-004.revenue_conclusion`, asking whether the finding "is carried into
what leadership is told rather than left in the workings" — had to be filed
under `business_judgment` because there was nowhere else for it.

This is the largest hole in the benchmark. Every one of these models is
deployed to write to people.

### 2. Information boundaries — one criterion, no discrimination

`monday-001.pricing_confidential` (5 points) asks the model to state that
proposed pricing must not be shared externally, and
`monday-002.stale_external_actions` asks it not to send an email. Both are
scored as things not to do inside a single internal document. Nothing asks the
model to produce an external artifact and *decide what belongs in it*. Every
model scores 100%, which tells us the current bar is trivially clearing.

### 3. Cross-output consistency — structurally impossible today

Every scenario produces one output, so there is nothing to be consistent with.
The failure mode where a model tells one reader one thing and another reader
something incompatible cannot occur, and therefore cannot be measured.

### 4. Commitment discipline — adjacent but not covered

`monday-002.conditional_launch_timing` ("rollout estimate conditional and not
promised externally") is the closest thing, at 3 points. There is no measurement
of whether a model distinguishes an internal estimate from an authorised
external promise — which is the specific way real incident communications go
wrong.

### 5. Temporal reasoning — measured, weak, and thin

14 points across two scenarios, and the capability every model is worst at. The
combination of "hardest" and "least measured" is the wrong way round.

### 6. Entity resolution and data cleaning — real, one scenario each

Both are #004-only. They will look better once #004 is official but they will
still rest on a single Monday.

---

## Reproducing

```bash
uv run python -c "
from mondaybench.capabilities import *
t = load_taxonomy()
res = {s: official_criterion_results(e, s) for s, e in {
    'monday-001': 'evaluator-opus5-v0.1',
    'monday-002': 'evaluator-opus5-v0.2',
    'monday-003': 'evaluator-opus5-v0.3'}.items()}
profiles, warnings = build_profiles(t, res)
"
```

Once monday-004 is official, adding `'monday-004': 'evaluator-opus5-v0.4'` to
that map extends every profile and gives `business_judgment`, `data_cleaning`
and `entity_resolution` their first official coverage.
