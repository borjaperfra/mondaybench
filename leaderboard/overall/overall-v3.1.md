# MondayBench Overall — Overall v3.1 - DeepSeek V4.1 Flash added

**Monday Score** is the arithmetic mean of a model's official score on each scenario listed below. Every scenario counts once. Latency, TTFA, tokens, cost and run stability are reported beside it and are never folded into it.

**Scenarios in this version:** `monday-001`, `monday-002`, `monday-003`, `monday-004`, `monday-005`

A model is ranked only if it has an official score on every one of them. Averaging over the scenarios a model happens to have completed would reward skipping the hard one.

A REVISION OF v3, NOT A NEW VERSION. Same five scenarios, same frozen prompts, same rubric versions, same arithmetic, same judge contract. One model is added and nothing else moves: every incumbent Monday Score here is identical to its v3 score. v3 stays byte-frozen and remains the citable eight-model artifact.
WHY IT READS SUITE v1.2 AND NOT v1.1. The suite CONTENT is byte-identical to v1.1 - the same scenarios, rubrics, evaluators and taxonomy, all verified `immutable` against the v1.1 manifest. What v1.2 adds is evidence: fifteen runs, 354 criterion verdicts, fifteen evaluations and a ninth column on each scenario board. A scenario board is a ranking of N models, so it cannot gain a row without changing, and the v1.1 manifest hashes `leaderboard/**/*` as append_only. Writing the nine-model boards into v1.1 would therefore have stopped v1.1 verifying - so they are written to `leaderboard/v1.2/` and v1.1 keeps its eight-model boards byte-frozen. Nothing about the suite got harder or different; a release is how this repository records that more evidence exists.
WHY THE NEW MODEL HAS ITS OWN SLUG. Helmcode replaced the deployment behind the model id `deepseek-v4-flash` with V4.1 in place, so the id the harness calls is the same one the incumbent `deepseek-v4-flash` was generated against in August. The incumbent's fifteen runs are untouched and its Monday Score is identical to its v3 score; the challenger is a separate slug with its own fifteen generations and its own 354 criterion verdicts. Averaging the two into one row would put two different models behind one number, which is the failure a frozen suite exists to prevent.
WHAT A CLIENT COULD AND COULD NOT VERIFY. The version change is an operator statement, not something this repository proved: the gateway exposes no version field anywhere a client can read. What IS observable, and is recorded in models.yaml, is that the deployment behind that id changed - the request-id format moved from OpenRouter-style `gen-...` to `chatcmpl-...`, and `cost_details` stopped being returned. Neither says "4.1"; together they say "not the same deployment".
SPEED IS THE STANDOUT AND IT IS NOT IN THE SCORE. The challenger's median TTFA is between two and five times faster than the incumbent's on every one of the five scenarios. Latency has never been a term in a Monday Score and is not one here; it is published beside it.


| Rank | Model | Monday Score | #001 | #002 | #003 | #004 | #005 | Range | Stddev |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Qwen 3.8 Flash | **95.07** | 92.50 | 94.83 | 94.50 | 96.50 | 97.00 | 4.50 | 1.79 |
| 2 | GLM 5.3 Flash | **94.93** | 98.00 | 87.33 | 92.83 | 98.00 | 98.50 | 11.17 | 4.84 |
| 3 | GLM 5.3 | **93.73** | 97.50 | 87.67 | 94.83 | 91.67 | 97.00 | 9.83 | 4.10 |
| 4 | DeepSeek V4 Flash | **91.70** | 90.83 | 89.33 | 95.00 | 86.00 | 97.33 | 11.33 | 4.51 |
| 5 | MIMO v2.5 | **86.67** | 88.17 | 81.17 | 90.33 | 78.50 | 95.17 | 16.67 | 6.80 |
| 6 | GLM 5.2 | **86.50** | 84.33 | 91.17 | 87.33 | 71.17 | 98.50 | 27.33 | 10.08 |
| 7 | DeepSeek V4.1 Flash | **84.63** | 84.00 | 92.00 | 87.83 | 63.67 | 95.67 | 32.00 | 12.51 |
| 8 | Qwen 3.6 | **68.77** | 82.83 | 70.17 | 65.50 | 46.00 | 79.33 | 36.83 | 14.49 |
| 9 | Gemma 4 | **63.00** | 70.67 | 54.17 | 65.33 | 35.17 | 89.67 | 54.50 | 20.17 |

`Range` and `Stddev` above measure how much a model's score moves **from one scenario to another** — how uneven it is across kinds of work. They are not run-to-run stability.

## Run stability

Spread between the three official runs **within** each scenario, averaged across scenarios. Published for observability; not part of the Monday Score.

| Model | Mean run range | Max run range | Mean run stddev |
|---|---:|---:|---:|
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

Generated 2026-09-10T18:39:26Z. Each scenario's own leaderboard, runs, verdicts and scoring rules are in this repository.
