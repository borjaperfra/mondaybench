# MondayBench Overall — Overall v3.3 - DeepSeek V4.1 Flash reliability prompt added

**Monday Score** is the arithmetic mean of a model's official score on each scenario listed below. Every scenario counts once. Latency, TTFA, tokens, cost and run stability are reported beside it and are never folded into it.

**Scenarios in this version:** `monday-001`, `monday-002`, `monday-003`, `monday-004`, `monday-005`

A model is ranked only if it has an official score on every one of them. Averaging over the scenarios a model happens to have completed would reward skipping the hard one.

A REVISION OF v3, NOT A NEW VERSION. Same five scenarios, same frozen prompts, same rubric versions, same arithmetic, same judge contract. One row is added and nothing else moves: every incumbent Monday Score here is identical to its v3.2 score, and the re-stamp into suite v1.4 changed zero labels and zero scores across 166 evaluations.
WHAT THE NEW ROW IS. The same model as DeepSeek V4.1 Flash, run against the same five frozen scenarios through the same endpoint, the same model id, the same temperature, the same ceilings and the same retry policy. ONE thing differs: a general reliability system prompt replaces the harness default. It is a separate slug and a separate row because a Monday Score is the mean of a model's own runs, and averaging a treated battery into an untreated one would put two different configurations behind one number. The prompt is generic by construction - it names no scenario, no rubric criterion, no reference answer and no prior failure - and is published byte-exact with its sha256 alongside the machine-checked control proof that was written before generation.
WHAT THE COMPARISON SHOWS, AND WHAT IT DOES NOT. Read against the incumbent the treated battery is 5.70 points higher; read against the same model's untreated variance probe it is 1.16 higher. Those two untreated batteries differ from each other by 4.54 points, which is the yardstick any treatment effect has to beat, so the difference in the MEAN is not distinguishable from this model's own run-to-run variation. What does move is the floor: the worst run of the treated battery is 79.5 against 47.5 and 57.0 untreated, and mean run-to-run range falls from 18.80 and 12.40 to 10.20. The effect is concentrated in monday-004 and is not uniform - on monday-003 the treated battery is the widest of the three.
JUDGE VARIANCE IS THE SAME SIZE AS THE EFFECT. These fifteen responses were judged twice, independently, from the same blind pack: 90.33 and 93.47, a 3.14-point spread on the same runs. The published figure is the one produced by the same judge as every other row on this board, because a row scored by a different judge would sit above the board for that reason alone. The second pass is recorded in the experiment directory.


| Rank | Model | Monday Score | #001 | #002 | #003 | #004 | #005 | Range | Stddev |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | GPT-6 Astra | **98.80** | 100.00 | 100.00 | 100.00 | 98.00 | 96.00 | 4.00 | 1.79 |
| 2 | Qwen 3.8 Flash | **95.07** | 92.50 | 94.83 | 94.50 | 96.50 | 97.00 | 4.50 | 1.79 |
| 3 | GLM 5.3 Flash | **94.93** | 98.00 | 87.33 | 92.83 | 98.00 | 98.50 | 11.17 | 4.84 |
| 4 | GLM 5.3 | **93.73** | 97.50 | 87.67 | 94.83 | 91.67 | 97.00 | 9.83 | 4.10 |
| 5 | DeepSeek V4 Flash | **91.70** | 90.83 | 89.33 | 95.00 | 86.00 | 97.33 | 11.33 | 4.51 |
| 6 | DeepSeek V4.1 Flash (reliability prompt v1) | **90.33** | 88.50 | 91.50 | 88.83 | 85.67 | 97.17 | 11.50 | 4.34 |
| 7 | MIMO v2.5 | **86.67** | 88.17 | 81.17 | 90.33 | 78.50 | 95.17 | 16.67 | 6.80 |
| 8 | GLM 5.2 | **86.50** | 84.33 | 91.17 | 87.33 | 71.17 | 98.50 | 27.33 | 10.08 |
| 9 | DeepSeek V4.1 Flash | **84.63** | 84.00 | 92.00 | 87.83 | 63.67 | 95.67 | 32.00 | 12.51 |
| 10 | Qwen 3.6 | **68.77** | 82.83 | 70.17 | 65.50 | 46.00 | 79.33 | 36.83 | 14.49 |
| 11 | Gemma 4 | **63.00** | 70.67 | 54.17 | 65.33 | 35.17 | 89.67 | 54.50 | 20.17 |

`Range` and `Stddev` above measure how much a model's score moves **from one scenario to another** — how uneven it is across kinds of work. They are not run-to-run stability.

## Run stability

Spread between the three official runs **within** each scenario, averaged across scenarios. Published for observability; not part of the Monday Score.

| Model | Mean run range | Max run range | Mean run stddev |
|---|---:|---:|---:|
| GPT-6 Astra | 0.30 | 1.50 | 0.17 |
| GLM 5.3 Flash | 6.00 | 19.00 | 3.31 |
| Qwen 3.8 Flash | 6.40 | 11.50 | 3.29 |
| DeepSeek V4 Flash | 6.80 | 13.50 | 3.53 |
| GLM 5.3 | 7.00 | 17.00 | 3.72 |
| GLM 5.2 | 9.10 | 16.00 | 4.66 |
| Gemma 4 | 9.90 | 19.00 | 5.51 |
| DeepSeek V4.1 Flash (reliability prompt v1) | 10.20 | 17.00 | 5.23 |
| Qwen 3.6 | 14.70 | 31.00 | 7.52 |
| MIMO v2.5 | 16.30 | 33.00 | 8.32 |
| DeepSeek V4.1 Flash | 18.80 | 34.00 | 9.79 |

## Provenance

| Scenario | Prompt sha256 | Rubric | Evaluator |
|---|---|---|---|
| `monday-001` | `ed4d7beb1d7d` | 0.2 | `evaluator-opus5-v0.1` |
| `monday-002` | `740e627cbc74` | 0.2 | `evaluator-opus5-v0.2` |
| `monday-003` | `aaf788f309d9` | 0.3 | `evaluator-opus5-v0.3` |
| `monday-004` | `3a0cbb569ca4` | 0.3 | `evaluator-opus5-v0.4` |
| `monday-005` | `532cd464a9b7` | 0.4 | `evaluator-opus5-v0.5` |

Generated 2026-09-11T12:05:47Z. Each scenario's own leaderboard, runs, verdicts and scoring rules are in this repository.
