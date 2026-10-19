# MondayBench Overall — Overall v3.6 - DeepSeek V4.1 Flash (1017) and MiMo v2.6 Flash added

**Monday Score** is the arithmetic mean of a model's official score on each scenario listed below. Every scenario counts once. Latency, TTFA, tokens, cost and run stability are reported beside it and are never folded into it.

**Scenarios in this version:** `monday-001`, `monday-002`, `monday-003`, `monday-004`, `monday-005`

A model is ranked only if it has an official score on every one of them. Averaging over the scenarios a model happens to have completed would reward skipping the hard one.

A REVISION OF v3, NOT A NEW VERSION. Same five scenarios, same frozen prompts, same rubric versions, same arithmetic, same judge contract. Two rows are added and no incumbent score moves: the re-stamp of the 196 v1.10 evaluations into suite v1.13 changed zero scores, and every incumbent row on the five v1.13 scenario boards equals its v1.10 row.
WHAT IS ADDED. Two open-weights models served on NaN, generated through this harness on 2026-10-19 and judged the same day (experiments/nan-challengers-2026-10-19-opus-judge/).
DEEPSEEK V4.1 FLASH (1017), 91.23. NaN's `deepseek-v4-flash` id, which NaN's operator states now serves the 4.1-1017 version; the endpoint names no version, so the version is stated, not observed. A separate row from DeepSeek V4.1 Flash (94.53), which is the September deployment on Helmcode, labelled by GPT-5.6 Sol.
MIMO V2.6 FLASH, 87.87. NaN's `mimo-v2.6-flash`. NaN no longer serves MiMo v2.5, whose row stays as published.
HOW THEY WERE GENERATED. Same frozen prompts, temperature 0 and 32,000-token ceiling as every row, but with `seed: <run_number>` in the request body: NaN ignored `caching: false` that day and returned stored responses for identical bodies. No other row was generated with a seed. The unseeded attempt is archived (archive/nan-unseeded-2026-10-19/). MiMo v2.6 spent the whole ceiling reasoning and returned no answer on 6 of 6 monday-004 attempts before 13:00 UTC and on 2 of 5 monday-002 attempts; from 13:25 UTC monday-004 answered 3 of 3. The ceiling was not raised. Failed attempts are logged beside the runs. Both rows' latency, TTFA and token counts are properties of NaN, which is quota-priced, so neither row has a cost.
THE JUDGE CAVEAT TRAVELS WITH THE BOARD. Both new rows are labelled by Claude Opus 5.5 in a blind, criterion-by-criterion judgement (ten subagents, one per scenario per model, one-model packs under opaque keys), not by the Claude Opus 5 session judge. Of fifteen rows, ten are labelled by Claude Opus 5, two by GPT-5.6 Sol and three by Claude Opus 5.5.


| Rank | Model | Monday Score | #001 | #002 | #003 | #004 | #005 | Range | Stddev |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | GPT-6 Astra | **98.80** | 100.00 | 100.00 | 100.00 | 98.00 | 96.00 | 4.00 | 1.79 |
| 2 | Claude Opus 5 | **97.07** | 98.50 | 98.00 | 98.33 | 90.83 | 99.67 | 8.84 | 3.54 |
| 3 | Qwen 3.8 Flash | **95.07** | 92.50 | 94.83 | 94.50 | 96.50 | 97.00 | 4.50 | 1.79 |
| 4 | GLM 5.3 Flash | **94.93** | 98.00 | 87.33 | 92.83 | 98.00 | 98.50 | 11.17 | 4.84 |
| 5 | Claude Fable 5.1 | **94.90** | 97.50 | 91.00 | 96.67 | 89.33 | 100.00 | 10.67 | 4.53 |
| 6 | DeepSeek V4.1 Flash | **94.53** | 95.00 | 93.00 | 96.33 | 90.00 | 98.33 | 8.33 | 3.19 |
| 7 | GLM 5.3 | **93.73** | 97.50 | 87.67 | 94.83 | 91.67 | 97.00 | 9.83 | 4.10 |
| 8 | DeepSeek V4 Flash | **91.70** | 90.83 | 89.33 | 95.00 | 86.00 | 97.33 | 11.33 | 4.51 |
| 9 | DeepSeek V4.1 Flash (1017) | **91.23** | 90.33 | 95.17 | 95.83 | 79.67 | 95.17 | 16.16 | 6.83 |
| 10 | MiMo v2.6 Flash | **87.87** | 82.67 | 83.67 | 93.17 | 80.33 | 99.50 | 19.17 | 8.14 |
| 11 | MIMO v2.5 | **86.67** | 88.17 | 81.17 | 90.33 | 78.50 | 95.17 | 16.67 | 6.80 |
| 12 | GLM 5.2 | **86.50** | 84.33 | 91.17 | 87.33 | 71.17 | 98.50 | 27.33 | 10.08 |
| 13 | Gemini 3.8 Flash (High) | **86.00** | 95.33 | 80.00 | 84.67 | 72.17 | 97.83 | 25.66 | 10.68 |
| 14 | Qwen 3.6 | **68.77** | 82.83 | 70.17 | 65.50 | 46.00 | 79.33 | 36.83 | 14.49 |
| 15 | Gemma 4 | **63.00** | 70.67 | 54.17 | 65.33 | 35.17 | 89.67 | 54.50 | 20.17 |

`Range` and `Stddev` above measure how much a model's score moves **from one scenario to another** — how uneven it is across kinds of work. They are not run-to-run stability.

## Run stability

Spread between the three official runs **within** each scenario, averaged across scenarios. Published for observability; not part of the Monday Score.

| Model | Mean run range | Max run range | Mean run stddev |
|---|---:|---:|---:|
| GPT-6 Astra | 0.30 | 1.50 | 0.17 |
| Claude Opus 5 | 3.70 | 9.50 | 2.00 |
| Claude Fable 5.1 | 4.20 | 8.50 | 2.23 |
| DeepSeek V4.1 Flash | 4.30 | 10.50 | 2.44 |
| Gemini 3.8 Flash (High) | 5.30 | 9.00 | 2.83 |
| DeepSeek V4.1 Flash (1017) | 5.80 | 11.00 | 3.04 |
| GLM 5.3 Flash | 6.00 | 19.00 | 3.31 |
| MiMo v2.6 Flash | 6.30 | 10.50 | 3.41 |
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

Generated 2026-10-19T16:10:13Z. Each scenario's own leaderboard, runs, verdicts and scoring rules are in this repository.
