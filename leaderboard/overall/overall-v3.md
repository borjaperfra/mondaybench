# MondayBench Overall — Overall v3 — the v1.1 evaluator contract

**Monday Score** is the arithmetic mean of a model's official score on each scenario listed below. Every scenario counts once. Latency, TTFA, tokens, cost and run stability are reported beside it and are never folded into it.

**Scenarios in this version:** `monday-001`, `monday-002`, `monday-003`, `monday-004`, `monday-005`

A model is ranked only if it has an official score on every one of them. Averaging over the scenarios a model happens to have completed would reward skipping the hard one.

A NEW VERSION, NOT A REVISION OF v2, AND THE DISTINCTION IS THE POINT.
A revision adds MODELS to a fixed scenario set - that is what `revision` means here and what `load_releases` enforces. v3 keeps the same five scenarios, the same frozen prompts, the same rubric versions and the same arithmetic, and it does add a model. But it also reads a different suite's scenario boards: the v1.1 boards, built from evaluations carrying the scenario-specific judge contract fingerprint. `scenario_provenance` would therefore differ from v2's, and a decimal point cannot carry that.
WHAT v1.1 CHANGED, AND WHAT IT DID NOT. It changed how a judge contract is identified. `judge_prompt_fingerprint()` hashed global repository state, including the shared penalty vocabulary - which grew as scenarios were added, so a model judged after monday-005 could not share a board with incumbents judged before it, despite byte-identical rubrics. v1.1 hashes a scenario-specific rendered contract instead.
It changed NO candidate generation, NO rubric, NO ground truth and NO judgment. Every v1.1 evaluation replays the same recorded verdict file through the same deterministic scoring code; the migration gate proves, for all 121 migrated evaluations, that zero criterion labels, zero false-action judgments, zero penalty verdicts and zero scores moved. Every incumbent's Monday Score in v3 is identical to its v2 score.
This is a provenance and comparability fix. It is not a score correction, and nobody should read it as one.
GLM 5.3 is the first model published under the v1.1 contract. Its generation predates the migration and cleared every official gate at the time; what it could not clear was a fingerprint comparison that described the repository rather than the scenario.
v2 stays byte-frozen and remains the citable v1.0 artifact.


| Rank | Model | Monday Score | #001 | #002 | #003 | #004 | #005 | Range | Stddev |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Qwen 3.8 Flash | **95.07** | 92.50 | 94.83 | 94.50 | 96.50 | 97.00 | 4.50 | 1.79 |
| 2 | GLM 5.3 Flash | **94.93** | 98.00 | 87.33 | 92.83 | 98.00 | 98.50 | 11.17 | 4.84 |
| 3 | GLM 5.3 | **93.73** | 97.50 | 87.67 | 94.83 | 91.67 | 97.00 | 9.83 | 4.10 |
| 4 | DeepSeek V4 Flash | **91.70** | 90.83 | 89.33 | 95.00 | 86.00 | 97.33 | 11.33 | 4.51 |
| 5 | MIMO v2.5 | **86.67** | 88.17 | 81.17 | 90.33 | 78.50 | 95.17 | 16.67 | 6.80 |
| 6 | GLM 5.2 | **86.50** | 84.33 | 91.17 | 87.33 | 71.17 | 98.50 | 27.33 | 10.08 |
| 7 | Qwen 3.6 | **68.77** | 82.83 | 70.17 | 65.50 | 46.00 | 79.33 | 36.83 | 14.49 |
| 8 | Gemma 4 | **63.00** | 70.67 | 54.17 | 65.33 | 35.17 | 89.67 | 54.50 | 20.17 |

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

## Provenance

| Scenario | Prompt sha256 | Rubric | Evaluator |
|---|---|---|---|
| `monday-001` | `ed4d7beb1d7d` | 0.2 | `evaluator-opus5-v0.1` |
| `monday-002` | `740e627cbc74` | 0.2 | `evaluator-opus5-v0.2` |
| `monday-003` | `aaf788f309d9` | 0.3 | `evaluator-opus5-v0.3` |
| `monday-004` | `3a0cbb569ca4` | 0.3 | `evaluator-opus5-v0.4` |
| `monday-005` | `532cd464a9b7` | 0.4 | `evaluator-opus5-v0.5` |

Generated 2026-09-03T09:17:40Z. Each scenario's own leaderboard, runs, verdicts and scoring rules are in this repository.
