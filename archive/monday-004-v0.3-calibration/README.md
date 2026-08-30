# monday-004 v0.3 — calibration, superseded by the freeze 2026-08-30

The calibration batteries for "Numbers Don't Lie", kept whole and kept apart from
the official battery that follows them.

**The scenario itself did not change when it was frozen.** Its candidate-visible
content — `prompt.md`, `context.md` and the seven CSVs — is byte-identical
throughout, and the rendered prompt hashes to
`3a0cbb569ca4f711b8907177af9204cec267d26f35f732829df56b03ed23ef99` here and in
the frozen scenario. What iterated three times was the rubric. That is why
`scenario_version` stays at 0.1 while `rubric_version` reads 0.3.

## Why these runs are not the official runs

Seven runs live here, one per model. They were generated under the same 96,000-
token safety ceiling and against the same prompt as the official battery, and
every one of them passes qualification. They are still not official evidence:

- **Rubric 0.3 was written while reading them.** `figures_carried_correctly` was
  added because one of these responses reached 100.0 under the v0.2 shadow and
  the rubric had no way to see the three figures it had invented. A criterion
  fitted to a response cannot then be scored on that same response and published.
- They are the battery that produced the `FREEZE MONDAY-004` recommendation, so
  they are the evidence *for* the decision, not evidence produced *under* it.

The official battery is three new runs per model generated after the freeze,
under `runs/monday-004/`. Same prompt, same models, same ceiling, no shared
samples.

`leaderboard.check_calibration_overlap` now enforces this: publishing refuses if
any run in an official battery was also scored by a calibration evaluator. It
exists because nothing enforced it, and `run --reuse-valid-runs` happily counted
a calibration run toward the official three.

## What is here

| | |
|---|---|
| `runs-monday-004/` | the seven calibration runs |
| `evaluations-evaluator-opus5-v0.4-calibration/` | scored under rubric 0.1 |
| `evaluations-evaluator-opus5-v0.4-calibration-2/` | the v0.2 shadow rescore |
| `evaluations-evaluator-opus5-v0.4-calibration-3/` | scored under rubric 0.3 |
| `verdicts/` | the recorded judge verdicts for all of the above |
| `draft-leaderboard/` | the calibration ranking, never published |
| `monday-004-calibration.md` | the rubric-0.3 calibration report |
| `monday-004-calibration-v0.1.md` | the first battery, which returned REVISE |
| `monday-004-rubric-v0.2.md`, `-v0.3.md` | what each rubric revision moved, and why |

The three calibration evaluator configs stay under `evaluators/`, each still
bound to the rubric it was written for, so any of these scores can be
reproduced.

## What it found

| Model | rubric 0.1 | v0.2 shadow | rubric 0.3 |
|---|---:|---:|---:|
| Qwen 3.8 Flash | 97.5 | 100.0 | 98.5 |
| GLM 5.3 Flash | 92.5 | 95.0 | 98.5 |
| DeepSeek V4 Flash | 79.0 | 74.0 | 94.0 |
| MIMO v2.5 | — | — | 90.0 |
| GLM 5.2 | 86.0 | 86.0 | 78.0 |
| Qwen 3.6 | 38.5 | 39.0 | 54.5 |
| Gemma 4 | 42.0 | 40.5 | 45.5 |

The 0.1 and shadow columns cover six models: MIMO could not finish the scenario
under the 32,000-token limit those batteries ran under, which is what prompted
the safety-ceiling policy in `docs/methodology.md`.
