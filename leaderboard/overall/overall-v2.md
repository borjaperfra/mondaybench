# MondayBench Overall — Overall v2 — through Read the Room

**Monday Score** is the arithmetic mean of a model's official score on each scenario listed below. Every scenario counts once. Latency, TTFA, tokens, cost and run stability are reported beside it and are never folded into it.

**Scenarios in this version:** `monday-001`, `monday-002`, `monday-003`, `monday-004`, `monday-005`

A model is ranked only if it has an official score on every one of them. Averaging over the scenarios a model happens to have completed would reward skipping the hard one.

Adds monday-005 "Read the Room" to the four scenarios of Overall v1. All five are frozen, official and pinned below by prompt hash and rubric version; monday-005 is scored under rubric 0.4, the rubric its freeze covers.
Monday Score is the arithmetic mean of the five official scenario scores, equal weight per scenario. Each scenario score is itself the arithmetic mean of three valid official runs. Nothing else enters it: not latency, TTFA, cost, reasoning tokens, serving reliability, run range, standard deviation, penalty count or scenario wins. Across-scenario range and sigma are published beside the score and are descriptive only - and they measure variation across five different kinds of work, which is not the same quantity as run-to-run stability inside one scenario.
SERVING RELIABILITY IS EXCLUDED FROM THE SCORE AND REPORTED SEPARATELY. Three models needed a retry to complete the monday-005 battery - deepseek-v4-flash and glm5.3-flash each produced one reasoning-only generation with no answer, and qwen3.8-flash took one HTTP 429. None of those attempts is scored. mondaybench serving publishes attempts per valid run.
MONDAY-005 IS OUT-OF-SAMPLE. Its rubric was revised three times while reading a separate 21-run calibration battery, which is archived under archive/monday-005-v0.4-calibration/ and enters no official score. The official battery is 21 fresh runs generated after the freeze, and their independence is enforced mechanically by leaderboard.check_sample_provenance rather than asserted - 21 calibration samples against 21 official samples, zero overlap by response content and by provider request id.
CARRIED FORWARD FROM v1, because it is still true of the monday-004 component of every v2 average. Qwen 3.6's monday-004 runs were served by NaN, not Helmcode, under a per-scenario endpoint override - Helmcode was unreachable while that battery was generated. NaN serves qwen3.6 as a REASONING model and Helmcode does not, on a byte-identical request: roughly 6,000 reasoning tokens against zero. Measured afterwards, the regime moved the score by -1.8 points out of 100 and in both directions at criterion level, so this is a caveat about serving configuration and about latency, TTFA and token counts - which do differ materially - not a claim that the score is inflated. models.yaml carries the measurement.


| Rank | Model | Monday Score | #001 | #002 | #003 | #004 | #005 | Range | Stddev |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Qwen 3.8 Flash | **95.07** | 92.50 | 94.83 | 94.50 | 96.50 | 97.00 | 4.50 | 1.79 |
| 2 | GLM 5.3 Flash | **94.93** | 98.00 | 87.33 | 92.83 | 98.00 | 98.50 | 11.17 | 4.84 |
| 3 | DeepSeek V4 Flash | **91.70** | 90.83 | 89.33 | 95.00 | 86.00 | 97.33 | 11.33 | 4.51 |
| 4 | MIMO v2.5 | **86.67** | 88.17 | 81.17 | 90.33 | 78.50 | 95.17 | 16.67 | 6.80 |
| 5 | GLM 5.2 | **86.50** | 84.33 | 91.17 | 87.33 | 71.17 | 98.50 | 27.33 | 10.08 |
| 6 | Qwen 3.6 | **68.77** | 82.83 | 70.17 | 65.50 | 46.00 | 79.33 | 36.83 | 14.49 |
| 7 | Gemma 4 | **63.00** | 70.67 | 54.17 | 65.33 | 35.17 | 89.67 | 54.50 | 20.17 |

`Range` and `Stddev` above measure how much a model's score moves **from one scenario to another** — how uneven it is across kinds of work. They are not run-to-run stability.

## Run stability

Spread between the three official runs **within** each scenario, averaged across scenarios. Published for observability; not part of the Monday Score.

| Model | Mean run range | Max run range | Mean run stddev |
|---|---:|---:|---:|
| GLM 5.3 Flash | 6.00 | 19.00 | 3.31 |
| Qwen 3.8 Flash | 6.40 | 11.50 | 3.29 |
| DeepSeek V4 Flash | 6.80 | 13.50 | 3.53 |
| GLM 5.2 | 9.10 | 16.00 | 4.66 |
| Gemma 4 | 9.90 | 19.00 | 5.51 |
| Qwen 3.6 | 14.70 | 31.00 | 7.52 |
| MIMO v2.5 | 16.30 | 33.00 | 8.32 |

## Provenance

| Scenario | Prompt sha256 | Rubric | Evaluator |
|---|---|---|---|
| `monday-001` | `ed4d7beb1d7d` | 0.2 | `evaluator-opus5-v0.1` |
| `monday-002` | `740e627cbc74` | 0.2 | `evaluator-opus5-v0.2` |
| `monday-003` | `aaf788f309d9` | 0.3 | `evaluator-opus5-v0.3` |
| `monday-004` | `3a0cbb569ca4` | 0.3 | `evaluator-opus5-v0.4` |
| `monday-005` | `532cd464a9b7` | 0.4 | `evaluator-opus5-v0.5` |

Generated 2026-08-31T16:13:35Z. Each scenario's own leaderboard, runs, verdicts and scoring rules are in this repository.
