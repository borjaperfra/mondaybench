# monday-002 — criterion matrix (evaluator-opus5-v0.2, rubric 0.2)

Every criterion, every model, all three official runs. `P` = PASS, `~` = PARTIAL, `F` = FAIL.

## A. Summary — the shape of each model's three runs

| # | Criterion | Points | Qwen 3.8 Flash | GLM 5.2 | DeepSeek V4 Flash | GLM 5.3 Flash | MIMO v2.5 | Qwen 3.6 | Gemma 4 |
|---:|---|---:|---|---|---|---|---|---|---|
| 1 | `launch_state` | 5 | 3P | 3P | 3P | 3P | 2P + 1~ | 1P + 1~ + 1F | 3F |
| 2 | `stale_external_actions` | 5 | 3P | 3P | 3P | 3P | 3P | 3P | 3P |
| 3 | `current_owners` | 5 | 3P | 3P | 3P | 3P | 3P | 3P | 3P |
| 4 | `executive_gate_superseded` | 5 | 3P | 3P | 3P | 3P | 3P | 1P + 2~ | 2~ + 1F |
| 5 | `pricing_authority` | 5 | 3P | 3P | 3P | 3P | 3P | 3P | 3P |
| 6 | `ownership_supersession` | 5 | 3P | 3~ | 1P + 2~ | 3P | 3~ | 1P + 2~ | 3~ |
| 7 | `choose_option_b` | 8 | 1P + 2~ | 1P + 2~ | 1P + 2~ | 3~ | 1P + 2~ | 3~ | 3~ |
| 8 | `option_b_sequence` | 7 | 3P | 3P | 1P + 2~ | 1P + 2~ | 1P + 1~ + 1F | 2P + 1~ | 1P + 2~ |
| 9 | `schedule_feasibility` | 6 | 1P + 2~ | 1P + 1~ + 1F | 1P + 2F | 1~ + 2F | 1P + 2F | 1~ + 2F | 3F |
| 10 | `parallelize_work` | 4 | 3P | 2P + 1~ | 3P | 3P | 3P | 2P + 1~ | 2P + 1~ |
| 11 | `immediate_release_decision` | 6 | 3P | 3P | 3P | 3P | 3P | 3P | 3P |
| 12 | `expansion_before_11` | 5 | 3P | 3P | 3P | 3P | 3P | 3P | 1P + 2~ |
| 13 | `globex_priority` | 5 | 3P | 3P | 3P | 3P | 1P + 2~ | 3~ | 3~ |
| 14 | `avoid_acme_false_positive` | 4 | 3P | 3P | 3P | 3P | 3P | 2P + 1~ | 3P |
| 15 | `expansion_fully_reconciled` | 6 | 3P | 3P | 3P | 3P | 2P + 1~ | 2P + 1~ | 3~ |
| 16 | `causal_boundary` | 3 | 3P | 3P | 3P | 3P | 3P | 2P + 1~ | 3P |
| 17 | `customer_signal_integration` | 6 | 3P | 3P | 3P | 3P | 3P | 3P | 3~ |
| 18 | `orion_missing_evidence` | 5 | 3P | 3P | 3P | 3P | 3P | 3P | 3P |
| 19 | `conditional_launch_timing` | 3 | 2P + 1~ | 3P | 3P | 1P + 2~ | 2P + 1F | 1P + 1~ + 1F | 1~ + 2F |
| 20 | `no_unsupported_causality` | 2 | 3P | 3P | 3P | 2P + 1~ | 3P | 2P + 1F | 2P + 1F |

## B. Full per-run matrix

| # | Criterion | Points | Qwen 3.8 Flash r1 | Qwen 3.8 Flash r2 | Qwen 3.8 Flash r3 | GLM 5.2 r1 | GLM 5.2 r2 | GLM 5.2 r3 | DeepSeek V4 Flash r1 | DeepSeek V4 Flash r2 | DeepSeek V4 Flash r3 | GLM 5.3 Flash r1 | GLM 5.3 Flash r2 | GLM 5.3 Flash r3 | MIMO v2.5 r1 | MIMO v2.5 r2 | MIMO v2.5 r3 | Qwen 3.6 r1 | Qwen 3.6 r2 | Qwen 3.6 r3 | Gemma 4 r1 | Gemma 4 r2 | Gemma 4 r3 |
|---:|---|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `launch_state` | 5 | P | P | P | P | P | P | P | P | P | P | P | P | ~ | P | P | P | ~ | F | F | F | F |
| 2 | `stale_external_actions` | 5 | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P |
| 3 | `current_owners` | 5 | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P |
| 4 | `executive_gate_superseded` | 5 | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | ~ | ~ | ~ | F | ~ |
| 5 | `pricing_authority` | 5 | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P |
| 6 | `ownership_supersession` | 5 | P | P | P | ~ | ~ | ~ | ~ | P | ~ | P | P | P | ~ | ~ | ~ | P | ~ | ~ | ~ | ~ | ~ |
| 7 | `choose_option_b` | 8 | ~ | P | ~ | ~ | ~ | P | P | ~ | ~ | ~ | ~ | ~ | ~ | ~ | P | ~ | ~ | ~ | ~ | ~ | ~ |
| 8 | `option_b_sequence` | 7 | P | P | P | P | P | P | P | ~ | ~ | ~ | ~ | P | F | ~ | P | ~ | P | P | ~ | ~ | P |
| 9 | `schedule_feasibility` | 6 | ~ | P | ~ | ~ | F | P | P | F | F | F | F | ~ | F | F | P | F | ~ | F | F | F | F |
| 10 | `parallelize_work` | 4 | P | P | P | P | P | ~ | P | P | P | P | P | P | P | P | P | P | P | ~ | P | ~ | P |
| 11 | `immediate_release_decision` | 6 | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P |
| 12 | `expansion_before_11` | 5 | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | ~ | ~ |
| 13 | `globex_priority` | 5 | P | P | P | P | P | P | P | P | P | P | P | P | ~ | ~ | P | ~ | ~ | ~ | ~ | ~ | ~ |
| 14 | `avoid_acme_false_positive` | 4 | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | ~ | P | P | P |
| 15 | `expansion_fully_reconciled` | 6 | P | P | P | P | P | P | P | P | P | P | P | P | ~ | P | P | P | P | ~ | ~ | ~ | ~ |
| 16 | `causal_boundary` | 3 | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | ~ | P | P | P |
| 17 | `customer_signal_integration` | 6 | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | ~ | ~ | ~ |
| 18 | `orion_missing_evidence` | 5 | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P | P |
| 19 | `conditional_launch_timing` | 3 | P | P | ~ | P | P | P | P | P | P | ~ | P | ~ | F | P | P | ~ | P | F | F | ~ | F |
| 20 | `no_unsupported_causality` | 2 | P | P | P | P | P | P | P | P | P | P | ~ | P | P | P | P | P | P | F | P | F | P |
