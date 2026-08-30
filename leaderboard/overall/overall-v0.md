# MondayBench Overall — Overall v0 — the three published scenarios

**Monday Score** is the arithmetic mean of a model's official score on each scenario listed below. Every scenario counts once. Latency, TTFA, tokens, cost and run stability are reported beside it and are never folded into it.

**Scenarios in this version:** `monday-001`, `monday-002`, `monday-003`

A model is ranked only if it has an official score on every one of them. Averaging over the scenarios a model happens to have completed would reward skipping the hard one.

The first Overall result. It covers the three scenarios that were published before monday-004 existed, so it is a complete and permanent claim about those three - not a partial view of a four-scenario benchmark. When monday-004 becomes official it enters as Overall v1, alongside this one rather than replacing it.


| Rank | Model | Monday Score | #001 | #002 | #003 | Range | Stddev |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | Qwen 3.8 Flash | **93.94** | 92.50 | 94.83 | 94.50 | 2.33 | 1.26 |
| 2 | GLM 5.3 Flash | **92.72** | 98.00 | 87.33 | 92.83 | 10.67 | 5.34 |
| 3 | DeepSeek V4 Flash | **91.72** | 90.83 | 89.33 | 95.00 | 5.67 | 2.94 |
| 4 | GLM 5.2 | **87.61** | 84.33 | 91.17 | 87.33 | 6.84 | 3.43 |
| 5 | MIMO v2.5 | **86.56** | 88.17 | 81.17 | 90.33 | 9.16 | 4.79 |
| 6 | Qwen 3.6 | **72.83** | 82.83 | 70.17 | 65.50 | 17.33 | 8.97 |
| 7 | Gemma 4 | **63.39** | 70.67 | 54.17 | 65.33 | 16.50 | 8.42 |

`Range` and `Stddev` above measure how much a model's score moves **from one scenario to another** — how uneven it is across kinds of work. They are not run-to-run stability.

## Run stability

Spread between the three official runs **within** each scenario, averaged across scenarios. Published for observability; not part of the Monday Score.

| Model | Mean run range | Max run range | Mean run stddev |
|---|---:|---:|---:|
| DeepSeek V4 Flash | 7.17 | 13.50 | 3.78 |
| Qwen 3.8 Flash | 8.67 | 11.50 | 4.48 |
| GLM 5.3 Flash | 9.00 | 19.00 | 4.94 |
| Gemma 4 | 9.33 | 13.50 | 5.14 |
| GLM 5.2 | 12.67 | 16.00 | 6.49 |
| Qwen 3.6 | 16.33 | 31.00 | 8.42 |
| MIMO v2.5 | 17.00 | 33.00 | 8.63 |

## Provenance

| Scenario | Prompt sha256 | Rubric | Evaluator |
|---|---|---|---|
| `monday-001` | `ed4d7beb1d7d` | 0.2 | `evaluator-opus5-v0.1` |
| `monday-002` | `740e627cbc74` | 0.2 | `evaluator-opus5-v0.2` |
| `monday-003` | `aaf788f309d9` | 0.3 | `evaluator-opus5-v0.3` |

Generated 2026-08-30T18:28:18Z. Each scenario's own leaderboard, runs, verdicts and scoring rules are in this repository.
