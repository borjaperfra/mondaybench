# MondayBench Overall — Overall v3.2 - GPT-6 Astra added

**Monday Score** is the arithmetic mean of a model's official score on each scenario listed below. Every scenario counts once. Latency, TTFA, tokens, cost and run stability are reported beside it and are never folded into it.

**Scenarios in this version:** `monday-001`, `monday-002`, `monday-003`, `monday-004`, `monday-005`

A model is ranked only if it has an official score on every one of them. Averaging over the scenarios a model happens to have completed would reward skipping the hard one.

A REVISION OF v3, NOT A NEW VERSION. Same five scenarios, same frozen prompts, same rubric versions, same arithmetic, same judge contract. One model is added and nothing else moves: every incumbent Monday Score here is identical to its v3.1 score, and the re-stamp into suite v1.3 changed zero labels and zero scores across 151 evaluations.
THE CHALLENGER DID NOT RUN THROUGH THIS HARNESS. GPT-6 Astra's fifteen responses were generated through the Codex CLI, because no authenticated Astra API route was available. The canonical scenario inputs are the frozen ones - every prompt sha256 matches this suite - and each candidate ran in its own ephemeral session with no carry-over and no recorded tool use. What the runtime does not expose is recorded as null, never as a number: temperature, top_p, caching, the output ceiling, the resolved model id, finish reason, request ids, TTFT, TTFA, reasoning tokens and every token count. Its reasoning effort was set to medium, the highest that runtime offers. All of this travels with the runs in `provider_metadata.codex_runtime`, and the challenger pack that produced them is preserved under `astra-mondaybench-challenger/`.
ONE QUALIFICATION RULE CHANGED, AND IT APPLIES TO EVERY MODEL. The safety ceiling check now compares only when a run records a ceiling. A run that records none is not a mismatch, it is a run whose ceiling was never observable, and refusing it would be rejecting evidence that is absent rather than evidence that is wrong - the same rule the reasoning check has always applied. No published run changes status: all 393 of them record an integer. THE COST: for a run with neither a ceiling nor a finish reason, nothing in this harness can independently rule out that the answer was truncated. For Astra that assurance rests on the Codex completion events - returncode 0, turn completed, final message present on all fifteen - which is the runtime's own word, recorded rather than verified here.
TELEMETRY IS ABSENT, NOT ZERO. Astra publishes no latency, no token counts and no cost. Those cells are empty for it in the same way they are empty for any model whose provider stopped returning cost details.


| Rank | Model | Monday Score | #001 | #002 | #003 | #004 | #005 | Range | Stddev |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | GPT-6 Astra | **98.80** | 100.00 | 100.00 | 100.00 | 98.00 | 96.00 | 4.00 | 1.79 |
| 2 | Qwen 3.8 Flash | **95.07** | 92.50 | 94.83 | 94.50 | 96.50 | 97.00 | 4.50 | 1.79 |
| 3 | GLM 5.3 Flash | **94.93** | 98.00 | 87.33 | 92.83 | 98.00 | 98.50 | 11.17 | 4.84 |
| 4 | GLM 5.3 | **93.73** | 97.50 | 87.67 | 94.83 | 91.67 | 97.00 | 9.83 | 4.10 |
| 5 | DeepSeek V4 Flash | **91.70** | 90.83 | 89.33 | 95.00 | 86.00 | 97.33 | 11.33 | 4.51 |
| 6 | MIMO v2.5 | **86.67** | 88.17 | 81.17 | 90.33 | 78.50 | 95.17 | 16.67 | 6.80 |
| 7 | GLM 5.2 | **86.50** | 84.33 | 91.17 | 87.33 | 71.17 | 98.50 | 27.33 | 10.08 |
| 8 | DeepSeek V4.1 Flash | **84.63** | 84.00 | 92.00 | 87.83 | 63.67 | 95.67 | 32.00 | 12.51 |
| 9 | Qwen 3.6 | **68.77** | 82.83 | 70.17 | 65.50 | 46.00 | 79.33 | 36.83 | 14.49 |
| 10 | Gemma 4 | **63.00** | 70.67 | 54.17 | 65.33 | 35.17 | 89.67 | 54.50 | 20.17 |

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

Generated 2026-09-11T11:37:43Z. Each scenario's own leaderboard, runs, verdicts and scoring rules are in this repository.
