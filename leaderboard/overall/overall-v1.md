# MondayBench Overall — Overall v1 — through Numbers Don't Lie

**Monday Score** is the arithmetic mean of a model's official score on each scenario listed below. Every scenario counts once. Latency, TTFA, tokens, cost and run stability are reported beside it and are never folded into it.

**Scenarios in this version:** `monday-001`, `monday-002`, `monday-003`, `monday-004`

A model is ranked only if it has an official score on every one of them. Averaging over the scenarios a model happens to have completed would reward skipping the hard one.

Adds monday-004 "Numbers Don't Lie" to the three scenarios of Overall v0. All four are frozen, official and pinned below by prompt hash and rubric version; monday-004 is scored under rubric 0.3, the rubric its freeze covers.
CARRY THIS WHEREVER THE v1 NUMBER IS QUOTED. Qwen 3.6's monday-004 runs were served by NaN, not Helmcode, under a per-scenario endpoint override - Helmcode was unreachable while that battery was generated. NaN serves qwen3.6 as a REASONING model and Helmcode does not, on a byte-identical request: roughly 6,000 reasoning tokens against zero. So qwen3.6's v1 average blends one scenario produced under a different inference regime with three that were not. Measured afterwards, the regime moved the score by -1.8 points out of 100 and in both directions at criterion level, so this is a caveat about serving configuration and about latency, TTFA and token counts - which do differ materially - not a claim that the score is inflated. models.yaml carries the full measurement.
GLM 5.2's monday-004 run-005 was generated a day late: the Helmcode gateway returned HTTP 402 for that model on 2026-08-31 and then cleared with no change on this side. The run qualifies on every configuration check and the delay does not affect comparability; the record is in runs/monday-004/glm5.2/SERVING-INCIDENT.md.


| Rank | Model | Monday Score | #001 | #002 | #003 | #004 | Range | Stddev |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | Qwen 3.8 Flash | **94.58** | 92.50 | 94.83 | 94.50 | 96.50 | 4.00 | 1.64 |
| 2 | GLM 5.3 Flash | **94.04** | 98.00 | 87.33 | 92.83 | 98.00 | 10.67 | 5.09 |
| 3 | DeepSeek V4 Flash | **90.29** | 90.83 | 89.33 | 95.00 | 86.00 | 9.00 | 3.73 |
| 4 | MIMO v2.5 | **84.54** | 88.17 | 81.17 | 90.33 | 78.50 | 11.83 | 5.61 |
| 5 | GLM 5.2 | **83.50** | 84.33 | 91.17 | 87.33 | 71.17 | 20.00 | 8.68 |
| 6 | Qwen 3.6 | **66.12** | 82.83 | 70.17 | 65.50 | 46.00 | 36.83 | 15.28 |
| 7 | Gemma 4 | **56.34** | 70.67 | 54.17 | 65.33 | 35.17 | 35.50 | 15.70 |

`Range` and `Stddev` above measure how much a model's score moves **from one scenario to another** — how uneven it is across kinds of work. They are not run-to-run stability.

## Run stability

Spread between the three official runs **within** each scenario, averaged across scenarios. Published for observability; not part of the Monday Score.

| Model | Mean run range | Max run range | Mean run stddev |
|---|---:|---:|---:|
| GLM 5.3 Flash | 7.12 | 19.00 | 3.92 |
| Qwen 3.8 Flash | 7.25 | 11.50 | 3.73 |
| DeepSeek V4 Flash | 8.00 | 13.50 | 4.15 |
| GLM 5.2 | 10.62 | 16.00 | 5.46 |
| Gemma 4 | 11.75 | 19.00 | 6.53 |
| Qwen 3.6 | 12.88 | 31.00 | 6.64 |
| MIMO v2.5 | 19.12 | 33.00 | 9.68 |

## Provenance

| Scenario | Prompt sha256 | Rubric | Evaluator |
|---|---|---|---|
| `monday-001` | `ed4d7beb1d7d` | 0.2 | `evaluator-opus5-v0.1` |
| `monday-002` | `740e627cbc74` | 0.2 | `evaluator-opus5-v0.2` |
| `monday-003` | `aaf788f309d9` | 0.3 | `evaluator-opus5-v0.3` |
| `monday-004` | `3a0cbb569ca4` | 0.3 | `evaluator-opus5-v0.4` |

Generated 2026-08-31T08:23:31Z. Each scenario's own leaderboard, runs, verdicts and scoring rules are in this repository.
