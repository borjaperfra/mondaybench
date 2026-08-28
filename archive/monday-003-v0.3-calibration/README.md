# monday-003 v0.3 — calibration, superseded by the freeze 2026-08-28

The third and final calibration of Blockers, and the one that produced the FREEZE
recommendation. Kept whole and kept apart from the official battery that follows
it.

**The scenario itself did not change when it was frozen.** v0.3 was a rubric
revision on top of v0.2's sources, and the freeze added nothing but
`status: official`, a `FROZEN.yaml` manifest and an evaluator id without
`-calibration`. The rendered candidate prompt is the same in all three places:
`aaf788f309d955d2b427c86fe7d95d2bbf88575fde7306adcfd74b0ec4a4103f`.

## Why these runs are not the official runs

Fourteen scored runs live here — two per model. Neither set was promoted:

- **run-001** is the v0.2 response, rescored under rubric 0.3. Rubric 0.3 was
  designed while reading those responses, so they cannot also be the evidence it
  publishes.
- **run-002** is a fresh generation, and clean, but it was still part of the
  battery that decided the freeze.

The official battery is three new runs per model generated *after* the freeze,
under `runs/monday-003/`. Same prompt, same models, no shared samples.

## What it found

| Model | Fresh v0.3 | Shadow (v0.2 response rescored) |
|---|---:|---:|
| GLM 5.3 Flash | 97.5 | 97.5 |
| Qwen 3.8 Flash | 93.5 | 100.0 |
| DeepSeek V4 Flash | 83.5 | 70.0 |
| GLM 5.2 | 83.5 | 89.5 |
| MIMO v2.5 | 69.0 | 95.0 |
| Gemma 4 | 56.0 | 53.0 |
| Qwen 3.6 | 40.0 | 43.0 |

Fresh spread 57.5, constant point mass 19.0, 16 of 21 criteria discriminating,
five penalties across three runs. All seven freeze conditions met.

The finding that mattered most was not about the rubric: **run-to-run variance
(mean 8.3 points, maximum 26.0) is several times larger than the rubric change
itself (±1.5 for five of seven models).** MIMO v2.5 reassigned the contested
patch in one run and denied the substitute existed in the other. That is why the
official battery is three runs and why `run_range` belongs on the leaderboard.

## What is here

```
scenario/                                        the v0.3 scenario as calibrated
RENDERED_PROMPT_SHA256.txt                       aaf788f3… - identical before and after the freeze
evaluator-opus5-v0.3-calibration-3.yaml          bound to scenario 0.3 / rubric 0.3
judge-prompts/                                   its judge and penalty prompts
runs-monday-003/                                 14 runs plus one preserved DeepSeek failure
evaluations-evaluator-opus5-v0.3-calibration-3/  14 evaluations with per-criterion evidence
verdicts/                                        the recorded labels and their generator
draft-leaderboard/                               the --calibration ranking, never published
test_monday_003.py                               the calibration-era guards
calibration-report.md                            the report that produced the FREEZE recommendation
```

## Traps

**The criterion ids are the official ones.** Rubric 0.3 here and rubric 0.3 in
`scenarios/monday-003/` are the same file. These verdicts would therefore replay
cleanly against official runs and produce a plausible-looking wrong answer, since
they are keyed by run id and `monday-003__<model>__001` now names a different
response. Serve official runs only from `verdicts/monday-003/`.

**`draft-leaderboard/` is a two-run mean across the shadow and fresh runs.** Its
`Range` column is the run-variance figure, not a stability estimate, and it
carries the "NOT AN OFFICIAL RESULT" banner. It is here as the record of what the
`--calibration` gate produced.
