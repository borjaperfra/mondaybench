# MondayBench Overall — Overall v3.4 - DeepSeek V4.1 Flash measured on its current deployment

**Monday Score** is the arithmetic mean of a model's official score on each scenario listed below. Every scenario counts once. Latency, TTFA, tokens, cost and run stability are reported beside it and are never folded into it.

**Scenarios in this version:** `monday-001`, `monday-002`, `monday-003`, `monday-004`, `monday-005`

A model is ranked only if it has an official score on every one of them. Averaging over the scenarios a model happens to have completed would reward skipping the hard one.

A REVISION OF v3, NOT A NEW VERSION. Same five scenarios, same frozen prompts, same rubric versions, same arithmetic, same judge contract. Every incumbent Monday Score here is identical to its v3.3 score, and the re-stamp into suite v1.5 changed zero labels and zero scores across 151 evaluations.
WHAT CHANGED, AND WHY. DeepSeek V4.1 Flash now has ONE battery on this board instead of two, and it is a new one. The gateway serves this model under an id it shares with DeepSeek V4 Flash and replaced the deployment in place rather than publishing a second id, so the same request reaches different weights at different times. Measured on 2026-09-11, the same five prompts through the same endpoint produce reasoning volumes 1.3x to 2.5x the 2026-09-10 battery's at equal or better throughput - a change no amount of load explains. The 2026-09-10 battery therefore no longer describes what the id serves, and a board row is a claim about what a caller gets today.
WHAT IS NO LONGER CARRIED. Two batteries are not in this suite: the 2026-09-10 one and its reliability-prompt variant. Their runs, verdicts and v1.4 evaluations are untouched on disk and v1.4 still verifies; they are simply not members of v1.5. The reliability variant goes with them because its control no longer exists as a current measurement - a treated arm published without its untreated arm is a number with nothing to difference against. A later experiment against the current deployment found the same prompt worth +0.04 points under the judge who scored this board, which is not an effect.
THE ROW IS THE NATURAL CONFIGURATION. No reliability prompt, no reasoning_effort, the harness default system prompt, temperature 0 and the scenarios' own ceilings - the same configuration every other row on this board ran under.


| Rank | Model | Monday Score | #001 | #002 | #003 | #004 | #005 | Range | Stddev |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | GPT-6 Astra | **98.80** | 100.00 | 100.00 | 100.00 | 98.00 | 96.00 | 4.00 | 1.79 |
| 2 | Qwen 3.8 Flash | **95.07** | 92.50 | 94.83 | 94.50 | 96.50 | 97.00 | 4.50 | 1.79 |
| 3 | GLM 5.3 Flash | **94.93** | 98.00 | 87.33 | 92.83 | 98.00 | 98.50 | 11.17 | 4.84 |
| 4 | DeepSeek V4.1 Flash | **94.53** | 95.00 | 93.00 | 96.33 | 90.00 | 98.33 | 8.33 | 3.19 |
| 5 | GLM 5.3 | **93.73** | 97.50 | 87.67 | 94.83 | 91.67 | 97.00 | 9.83 | 4.10 |
| 6 | DeepSeek V4 Flash | **91.70** | 90.83 | 89.33 | 95.00 | 86.00 | 97.33 | 11.33 | 4.51 |
| 7 | MIMO v2.5 | **86.67** | 88.17 | 81.17 | 90.33 | 78.50 | 95.17 | 16.67 | 6.80 |
| 8 | GLM 5.2 | **86.50** | 84.33 | 91.17 | 87.33 | 71.17 | 98.50 | 27.33 | 10.08 |
| 9 | Qwen 3.6 | **68.77** | 82.83 | 70.17 | 65.50 | 46.00 | 79.33 | 36.83 | 14.49 |
| 10 | Gemma 4 | **63.00** | 70.67 | 54.17 | 65.33 | 35.17 | 89.67 | 54.50 | 20.17 |

`Range` and `Stddev` above measure how much a model's score moves **from one scenario to another** — how uneven it is across kinds of work. They are not run-to-run stability.

## Run stability

Spread between the three official runs **within** each scenario, averaged across scenarios. Published for observability; not part of the Monday Score.

| Model | Mean run range | Max run range | Mean run stddev |
|---|---:|---:|---:|
| GPT-6 Astra | 0.30 | 1.50 | 0.17 |
| DeepSeek V4.1 Flash | 4.30 | 10.50 | 2.44 |
| GLM 5.3 Flash | 6.00 | 19.00 | 3.31 |
| Qwen 3.8 Flash | 6.40 | 11.50 | 3.29 |
| DeepSeek V4 Flash | 6.80 | 13.50 | 3.53 |
| GLM 5.3 | 7.00 | 17.00 | 3.72 |
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

Generated 2026-09-11T20:40:20Z. Each scenario's own leaderboard, runs, verdicts and scoring rules are in this repository.
