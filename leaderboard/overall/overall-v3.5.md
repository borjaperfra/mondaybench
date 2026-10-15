# MondayBench Overall — Overall v3.5 - Claude Opus 5, Claude Fable 5.1 and Gemini 3.8 Flash added

**Monday Score** is the arithmetic mean of a model's official score on each scenario listed below. Every scenario counts once. Latency, TTFA, tokens, cost and run stability are reported beside it and are never folded into it.

**Scenarios in this version:** `monday-001`, `monday-002`, `monday-003`, `monday-004`, `monday-005`

A model is ranked only if it has an official score on every one of them. Averaging over the scenarios a model happens to have completed would reward skipping the hard one.

A REVISION OF v3, NOT A NEW VERSION. Same five scenarios, same frozen prompts, same rubric versions, same arithmetic, same judge contract. Three rows are added and no incumbent score moves: every incumbent Monday Score here is identical to its v3.4 score, and the re-stamp of the 151 v1.5 evaluations into suite v1.10 changed zero labels and zero scores.
WHAT IS ADDED. Three closed-weights models, published as OFFICIAL rows by the owner's decision of 2026-10-15. All three were measured on 2026-09-02 and had been shown on the site as provisional; nothing was regenerated and nothing was re-judged for this revision. Each enters the way GPT-6 Astra did in v3.2: the preserved responses become run files byte for byte, the bytes each battery passed to its route hash to the frozen prompt on all five scenarios, and every field the route does not expose is recorded as null, never as a number.
CLAUDE OPUS 5, 97.07. Generated through `claude -p` (Claude Code CLI 2.1.258, OAuth subscription, effort high), not through this harness. LABELLED BY GPT-5.6 Sol, an independent blind re-judge, and not by the Claude Opus 5 session judge that labelled the incumbents - that judge is the same model as the candidate, and scored this battery 97.10.
CLAUDE FABLE 5.1, 94.90. Generated through the same route at effort high. Its monday-002 runs are the three frozen arms of the date-sensitivity experiment; the date-neutralised arm is not in the battery. LABELLED BY the board's own recorded Claude Opus 5 judge, after a scoring audit that corrected ten labels (experiments/fable-5.1-full-mondaybench/AUDIT.md).
GEMINI 3.8 FLASH (HIGH), 86.00. Generated through the Antigravity Language Server (Connect-RPC GetModelResponse, thinking budget High), not through this harness. LABELLED BY Claude Opus 5.5 in a blind criterion by criterion re-judge, not by the Claude Opus 5 that labelled the incumbents. The 88.37 shown before had no criterion labels and is superseded.
WHAT THE ROUTES CHANGE. On `claude -p` the requested system prompt is preceded by the Agent SDK preamble, and a reminder carrying the user's identity and the runtime date (2026-09-02) is injected into the user turn, so the user turn as delivered is not the frozen bytes; temperature is not settable; and the route applies its own 64,000-token output ceiling, recorded on each run as route-reported. That is not the scenarios' configured ceiling, and it bound nothing: every Claude run ended end_turn, the largest at 24,674 output tokens. On Antigravity no system prompt is sent at all, and temperature, the served model id, token usage, finish reason and the output ceiling are unobservable.
THE JUDGE CAVEAT TRAVELS WITH THE BOARD. Of thirteen rows, ten are labelled by the Claude Opus 5 session judge, DeepSeek V4.1 Flash and Claude Opus 5 by GPT-5.6 Sol, and Gemini 3.8 Flash by Claude Opus 5.5. The two batteries that both judges have labelled on disk moved by 0.03 and 1.50 points of Monday Score and by up to 1.5 and 10.0 points on a single run, so a gap of that size between rows labelled by different judges is not established by this suite.
TELEMETRY IS ABSENT, NOT ZERO. None of the three publishes latency or cost: the Claude timings were measured around the CLI process and the route's cost is a list figure for a subscription call, and the Gemini route reports neither. Both are kept with each run's runtime record.


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
| 9 | MIMO v2.5 | **86.67** | 88.17 | 81.17 | 90.33 | 78.50 | 95.17 | 16.67 | 6.80 |
| 10 | GLM 5.2 | **86.50** | 84.33 | 91.17 | 87.33 | 71.17 | 98.50 | 27.33 | 10.08 |
| 11 | Gemini 3.8 Flash (High) | **86.00** | 95.33 | 80.00 | 84.67 | 72.17 | 97.83 | 25.66 | 10.68 |
| 12 | Qwen 3.6 | **68.77** | 82.83 | 70.17 | 65.50 | 46.00 | 79.33 | 36.83 | 14.49 |
| 13 | Gemma 4 | **63.00** | 70.67 | 54.17 | 65.33 | 35.17 | 89.67 | 54.50 | 20.17 |

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

Generated 2026-10-15T17:42:20Z. Each scenario's own leaderboard, runs, verdicts and scoring rules are in this repository.
