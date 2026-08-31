# MondayBench Overall v2 — release analysis

**Overall v2 = monday-001 + monday-002 + monday-003 + monday-004 + monday-005.**
Artifacts materialised and validated. v0 and v1 byte-identical. Nothing committed.

```
pytest                                                    725 passed
overall v2 pins vs published scenario boards              0 mismatches
check_sample_provenance, all five scenarios               0 blockers
overall-v0.* / overall-v1.*                               byte-identical after release
```

---

## 1. Release definition and frozen inputs

Equal weight, five scenarios, each pinned by prompt hash and rubric version in
`overall-releases.yaml` and reproduced in the artifact's `scenario_provenance`.

| Scenario | prompt sha256 | rubric | evaluator |
|---|---|---|---|
| monday-001 | `ed4d7beb…` | 0.2 | evaluator-opus5-v0.1 |
| monday-002 | `740e627c…` | 0.2 | evaluator-opus5-v0.2 |
| monday-003 | `aaf788f3…` | 0.3 | evaluator-opus5-v0.3 |
| monday-004 | `3a0cbb56…` | 0.3 | evaluator-opus5-v0.4 |
| monday-005 | `532cd464…` | 0.4 | evaluator-opus5-v0.5 |

## 2. Score formula

```
Monday Score(v2) = mean(#001, #002, #003, #004, #005)
scenario score   = mean of three valid official runs
```

Equal weight per scenario. Nothing else enters it — not latency, TTFA, cost,
reasoning tokens, serving reliability, run range, standard deviation, penalty
count or scenario wins. Verified structurally: every v2 score reproduces from
the five published scenario means alone, and no observability field appears
anywhere in a model's v2 payload.

## 3. Overall v2 scoreboard

| # | Model | **Monday Score** | #001 | #002 | #003 | #004 | #005 | min | max | range | sigma |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Qwen 3.8 Flash | **95.07** | 92.50 | 94.83 | 94.50 | 96.50 | 97.00 | 92.50 | 97.00 | **4.50** | **1.79** |
| 2 | GLM 5.3 Flash | **94.93** | 98.00 | 87.33 | 92.83 | 98.00 | 98.50 | 87.33 | 98.50 | 11.17 | 4.84 |
| 3 | DeepSeek V4 Flash | **91.70** | 90.83 | 89.33 | 95.00 | 86.00 | 97.33 | 86.00 | 97.33 | 11.33 | 4.51 |
| 4 | MIMO v2.5 | **86.67** | 88.17 | 81.17 | 90.33 | 78.50 | 95.17 | 78.50 | 95.17 | 16.67 | 6.80 |
| 5 | GLM 5.2 | **86.50** | 84.33 | 91.17 | 87.33 | 71.17 | 98.50 | 71.17 | 98.50 | 27.33 | 10.08 |
| 6 | Qwen 3.6 | **68.77** | 82.83 | 70.17 | 65.50 | 46.00 | 79.33 | 46.00 | 82.83 | 36.83 | 14.49 |
| 7 | Gemma 4 | **63.00** | 70.67 | 54.17 | 65.33 | 35.17 | 89.67 | 35.17 | 89.67 | **54.50** | **20.17** |

All seven models are eligible: each has an official score on all five
scenarios. `incomplete_models` is empty.

**Range and sigma here are variation ACROSS five different kinds of work.** They
are not run-to-run stability. The artifact keeps the two in separate fields
(`across_scenarios` and `run_stability`) and a test enforces the separation.

## 4. The key hypothesis — checked, and partly wrong

**A. Who leads?** Qwen 3.8 Flash, 95.07.

**B. Lead over #2?** **0.14 points** over GLM 5.3 Flash at 94.93. That is a
seventh of a point across five scenarios, each itself a mean of three runs.
**Treat the top two as inseparable on this evidence.** Nothing in this battery
justifies calling one better than the other.

**C. Has the leader changed from v1?** No. Qwen 3.8 Flash led v1 at 94.58.

**D. Rank changes v1 → v2?** **None.** All seven models hold position.

**E. How much does #005 move each score?** Every model gains, because #005 is
the highest-scoring scenario in the set for every model except Qwen 3.6:
+0.49 (Qwen 3.8 Flash) to +6.66 (Gemma 4). Full table in §5.

**F. Does Qwen 3.8 Flash lead despite zero outright scenario wins?**
**No — the premise is wrong.** It has **one outright win** (monday-002, 94.83).
What is true, and is the more interesting fact, is that it leads with the
*fewest* wins of the top two: one outright and zero ties against GLM 5.3
Flash's two outright and one tie. It leads on floor, not ceiling.

**G. Most consistent across scenarios?** Qwen 3.8 Flash, decisively: range
4.50 and sigma 1.79, against 11.17 / 4.84 for the next best. Its worst scenario
(92.50) is higher than four models' best.

**H. Most scenario-dependent?** Gemma 4 (range 54.50, sigma 20.17), then
Qwen 3.6 (36.83 / 14.49) and GLM 5.2 (27.33 / 10.08).

## 5. v1 → v2 deltas

| Model | Overall v1 | Overall v2 | Delta | Rank v1 | Rank v2 | Rank delta |
|---|---:|---:|---:|---:|---:|---:|
| Qwen 3.8 Flash | 94.58 | 95.07 | +0.49 | 1 | 1 | 0 |
| GLM 5.3 Flash | 94.04 | 94.93 | +0.89 | 2 | 2 | 0 |
| DeepSeek V4 Flash | 90.29 | 91.70 | +1.41 | 3 | 3 | 0 |
| MIMO v2.5 | 84.54 | 86.67 | +2.13 | 4 | 4 | 0 |
| GLM 5.2 | 83.50 | 86.50 | +3.00 | 5 | 5 | 0 |
| Qwen 3.6 | 66.12 | 68.77 | +2.65 | 6 | 6 | 0 |
| Gemma 4 | 56.34 | 63.00 | +6.66 | 7 | 7 | 0 |

**Every model gains and nobody moves.** The gains are ordered almost perfectly
inversely to v1 rank, which is the arithmetic of adding a scenario on which the
weak models did unusually well: a model already averaging 94 gains little from a
97, while one averaging 56 gains a lot from an 89.67.

**The ordering is unchanged, but the gaps narrowed.** Qwen 3.8 Flash's lead over
GLM 5.3 Flash fell from 0.54 to 0.14. Sixth to seventh narrowed from 9.78 to
5.77.

### Qwen 3.8 Flash vs GLM 5.3 Flash

0.14 points apart, and they got there by opposite routes. GLM 5.3 Flash wins
three of five scenario comparisons and wins them clearly — 98.00 vs 92.50 on
#001, 98.00 vs 96.50 on #004, 98.50 vs 97.00 on #005. Qwen 3.8 Flash wins the
other two and wins one of them by a mile: **94.83 vs 87.33 on #002**, a 7.5-point
gap that is by itself larger than everything GLM 5.3 Flash gained across the
other four. GLM 5.3 Flash's #002 result is its own worst scenario by 5.5 points.

The honest summary: **one model has a higher ceiling and one has a higher floor,
and over five scenarios the floor wins by 0.14 points.** That margin is small
enough that a sixth scenario could reverse it.

### MIMO v2.5 vs GLM 5.2

**0.17 points apart** — the closest pair on the board, and also not a meaningful
difference. They are near-mirror images: GLM 5.2 has both the higher single
score (98.50 on #005) and the lower one (71.17 on #004); MIMO is flatter
(range 16.67 vs 27.33). GLM 5.2 gained more from #005 (+3.00 vs +2.13) and still
did not pass MIMO.

### Qwen 3.6 and Gemma 4

Both gain (+2.65, +6.66) and both stay put. Gemma 4's +6.66 is the largest
movement on the board and comes entirely from one scenario: 89.67 on #005
against a v1 average of 56.34. **Its range is now 54.50 points** — from 35.17 on
#004 to 89.67 on #005 — which is over half the scale, and the single most
scenario-dependent profile in the benchmark.

Qwen 3.6 is the only model for which #005 is *not* its best scenario (79.33
against 82.83 on #001).

## 6. Scenario winners

| Scenario | Winner(s) | Score |
|---|---|---:|
| monday-001 | GLM 5.3 Flash | 98.00 |
| monday-002 | Qwen 3.8 Flash | 94.83 |
| monday-003 | DeepSeek V4 Flash | 95.00 |
| monday-004 | GLM 5.3 Flash | 98.00 |
| monday-005 | **GLM 5.2 and GLM 5.3 Flash (tie)** | 98.50 |

| Model | outright wins | tied wins | top-2 finishes | best | worst |
|---|---:|---:|---:|---|---|
| Qwen 3.8 Flash | **1** | 0 | **4** | #005 97.00 | #001 92.50 |
| GLM 5.3 Flash | 2 | 1 | 3 | #005 98.50 | #002 87.33 |
| DeepSeek V4 Flash | 1 | 0 | 1 | #005 97.33 | #004 86.00 |
| MIMO v2.5 | 0 | 0 | 0 | #005 95.17 | #004 78.50 |
| GLM 5.2 | 0 | 1 | 2 | #005 98.50 | #004 71.17 |
| Qwen 3.6 | 0 | 0 | 0 | #001 82.83 | #004 46.00 |
| Gemma 4 | 0 | 0 | 0 | #005 89.67 | #004 35.17 |

**Overall rewards broad competence across work types, not the number of scenario
wins**, and this release is a clean illustration. The leader has one outright win
and no ties; the model directly behind it has two outright wins and a share of a
third. What separates them is that Qwen 3.8 Flash finished top-2 in **four of
five** scenarios and never dropped below 92.50, while GLM 5.3 Flash gave back
7.5 points on the one Monday it found hard.

The narrative is *not* that the winner never wins — it wins once, and that
qualification matters. It is that the winner never loses badly.

## 7. Consistency across scenarios

| Model | mean | range | sigma | largest drop below own mean |
|---|---:|---:|---:|---|
| Qwen 3.8 Flash | 95.07 | 4.50 | 1.79 | #001, −2.57 |
| DeepSeek V4 Flash | 91.70 | 11.33 | 4.51 | #004, −5.70 |
| GLM 5.3 Flash | 94.93 | 11.17 | 4.84 | #002, −7.60 |
| MIMO v2.5 | 86.67 | 16.67 | 6.80 | #004, −8.17 |
| GLM 5.2 | 86.50 | 27.33 | 10.08 | #004, −15.33 |
| Qwen 3.6 | 68.77 | 36.83 | 14.49 | #004, −22.77 |
| Gemma 4 | 63.00 | 54.50 | 20.17 | #004, −27.83 |

- **Most consistent:** Qwen 3.8 Flash, by a factor of 2.5 on range.
- **Least consistent:** Gemma 4, whose spread exceeds half the scale.
- **Largest single drop:** Gemma 4 on #004, −27.83 below its own mean.
- **Largest single gain:** Gemma 4 on #005, +26.67 above its own mean.

**monday-004 is the worst scenario for five of seven models** — the quantitative
analysis Monday remains the hardest work type in the benchmark, and #005 is the
easiest for six of seven.

**This is cross-scenario capability consistency, not sampling stability.** The
two are reported in separate fields and are genuinely different: Qwen 3.8 Flash
has the tightest across-scenario spread (4.50) while carrying a mean run range
of 6.40 and a worst-scenario run range of 11.50 on #003. A model can be steady
across kinds of work and variable between repeats of the same work.

## 8. What #005 changes

| | |
|---|---|
| Benefits most | **Gemma 4, +6.66** |
| Benefits least | **Qwen 3.8 Flash, +0.49** |
| Ordering change | **None.** Zero rank movements |
| Effect on the consistency story | **Reinforces it.** Qwen 3.8 Flash's range tightens from 4.0 (v1) to 4.50 (v2) while every other model's widens |

**Does audience and information-routing competence reveal a weakness invisible in
v1?** Not at the Overall level — nobody moved. But the scenario-level finding is
worth carrying: `security_item_reaches_engineering` was the most-failed criterion
of #005 at 10 PASS / 2 PARTIAL / 9 FAIL, and the failures were spread across
strong models, not concentrated in weak ones. Models that never leaked a
confidential item externally (0 of 21 across four explicit classes) were
unreliable at *delivering* it to the internal audience that owns the fix. That
is a within-scenario finding about routing, and it does not survive into an
Overall average — which is a limitation of averaging, not evidence against it.

No causal claim about model properties is made from any of this.

## 9. Methodological caveats carried into the release

- Serving reliability is excluded from Monday Score and reported separately;
  three models needed one retry each to complete #005.
- Each scenario score is the arithmetic mean of three valid official runs.
- #005's official battery is out-of-sample relative to rubric development; its
  calibration battery is archived and enters no official score, and the
  independence is enforced by `check_sample_provenance`, not asserted.
- Qwen 3.6's monday-004 runs were served by NaN under a per-scenario endpoint
  override, a different inference regime from its other scenarios. Measured
  effect: −1.8 points out of 100, running both ways at criterion level.
- Overall uses equal scenario weighting.
- Across-scenario dispersion is descriptive and never enters the score.

## 10. Tests and validation

`tests/test_overall_v2.py`, 23 tests: composition, v0/v1 immutability, the
arithmetic, equal weighting, the exclusion of every observability metric, the
across-scenario vs run-stability separation, eligibility, pin matching, a
tampered-pin build failure, artifact provenance, release-note content, CSV/MD
agreement with the JSON, and that publishing v2 touches no frozen scenario file.

Full suite: **725 passed.**

One existing assertion was updated rather than deleted:
`test_the_scenario_is_frozen_and_official` previously asserted Overall held only
v0 and v1. That was correct when written — publishing a *scenario* must not
update Overall — and it now asserts the same intent against a three-release
directory, plus that v0 and v1 still describe their own scenario sets.

## 11. Files changed

Added: `leaderboard/overall/overall-v2.{json,csv,md}`,
`tests/test_overall_v2.py`, this report.
Modified: `overall-releases.yaml` (v2 definition appended; v0 and v1 blocks
untouched), `tests/test_monday_005.py` (the assertion above).

**Not touched:** any scenario score, rubric, run, evaluation, verdict file,
frozen manifest, `leaderboard/overall/overall-v0.*`,
`leaderboard/overall/overall-v1.*`, `taxonomy/capabilities-v0.1.yaml`, capability
profiles, criterion mappings. Nothing committed.

## 12. Recommendation

The release validates. Composition is exactly the five scenarios, every pin
matches what each scenario actually published, v0 and v1 are byte-identical, all
seven models are eligible on all five, and every score reproduces as the
arithmetic mean of its five pinned inputs.

Two things a reader should be told plainly rather than left to infer:

1. **The top two are 0.14 points apart** and should be read as tied on this
   evidence. So should MIMO v2.5 and GLM 5.2 at 0.17.
2. **The expected narrative was wrong in one detail.** Qwen 3.8 Flash does lead
   without leading on wins, but it is not winless — it takes monday-002
   outright, and by the largest margin any model achieves on any scenario in the
   set.

---

`DECISION: OVERALL V2 READY FOR HUMAN REVIEW`
