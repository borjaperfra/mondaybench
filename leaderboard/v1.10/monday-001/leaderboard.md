# MondayBench 0.1 - `monday-001`

**Evaluator:** `evaluator-opus5-v0.1`  
**Rubric:** 0.2  
**Judge:** `claude-opus-5`  
**Prompt SHA-256:** `ed4d7beb1d7d1029c36eb8533e449027e0dc1a1047f8a38951a91781a0a5e398`  
**Generated:** 2026-10-15T17:41:05Z

**Status:** official v0.1 result. Every publication gate passed.

The Monday Score is the mean of each model's official runs and measures task quality only. TTFA, latency and cost sit beside it and are never folded into it.

| Rank | Model | Monday Score | Runs | Range | TTFA median | Total median |
|---:|---|---:|---:|---:|---:|---:|
| 1 | GPT-6 Astra | **100.0** | 3 | 0.0 | - | - |
| 2 | Claude Opus 5 | **98.5** | 3 | 0.0 | - | - |
| 3 | GLM 5.3 Flash | **98.0** | 3 | 1.5 | 118.8s | 132.4s |
| 4 | Claude Fable 5.1 | **97.5** | 3 | 1.5 | - | - |
| 5 | GLM 5.3 | **97.5** | 3 | 6.0 | 181.6s | 202.8s |
| 6 | Gemini 3.8 Flash (High) | **95.3** | 3 | 2.5 | - | - |
| 7 | DeepSeek V4.1 Flash | **95.0** | 3 | 6.0 | 39.3s | 44.1s |
| 8 | Qwen 3.8 Flash | **92.5** | 3 | 6.0 | 72.2s | 92.0s |
| 9 | DeepSeek V4 Flash | **90.8** | 3 | 8.0 | 55.4s | 63.3s |
| 10 | MIMO v2.5 | **88.2** | 3 | 6.5 | 42.4s | 64.1s |
| 11 | GLM 5.2 | **84.3** | 3 | 16.0 | 2.7s | 6.9s |
| 12 | Qwen 3.6 | **82.8** | 3 | 5.0 | 0.8s | 6.2s |
| 13 | Gemma 4 | **70.7** | 3 | 6.5 | 0.6s | 5.5s |

---

## 1. GPT-6 Astra - 100.0 / 100

`gpt-6-astra`

| Dimension | Score | Max |
|---|---:|---:|
| Action detection | 25.0 | 25 |
| State reconstruction | 25.0 | 25 |
| Prioritization | 15.0 | 15 |
| Data reasoning | 15.0 | 15 |
| Uncertainty | 10.0 | 10 |
| Noise resistance | 10.0 | 10 |
| **Monday Score** | **100.0** | **100** |

**Runs:** 100.0, 100.0, 100.0  (min 100.0, max 100.0, run_range 0.0, sigma 0.00)

**Latency and cost:** TTFA median -, TTFT median -, total median -, output tokens median -, cost/run median -

### What it missed (0 criteria)

Nothing: every criterion passed in every run.

### What it got wrong (0)

No penalties and no false actions in any run.

### Raw evidence

- response: `runs/monday-001/gpt-6-astra/run-001.json`
- response: `runs/monday-001/gpt-6-astra/run-002.json`
- response: `runs/monday-001/gpt-6-astra/run-003.json`
- evaluation: `evaluations/v1.10/evaluator-opus5-v0.1/monday-001/gpt-6-astra/run-001.json`
- evaluation: `evaluations/v1.10/evaluator-opus5-v0.1/monday-001/gpt-6-astra/run-002.json`
- evaluation: `evaluations/v1.10/evaluator-opus5-v0.1/monday-001/gpt-6-astra/run-003.json`

---

## 2. Claude Opus 5 - 98.5 / 100

`claude-opus-5`

| Dimension | Score | Max |
|---|---:|---:|
| Action detection | 25.0 | 25 |
| State reconstruction | 25.0 | 25 |
| Prioritization | 15.0 | 15 |
| Data reasoning | 13.5 | 15 |
| Uncertainty | 10.0 | 10 |
| Noise resistance | 10.0 | 10 |
| **Monday Score** | **98.5** | **100** |

**Runs:** 98.5, 98.5, 98.5  (min 98.5, max 98.5, run_range 0.0, sigma 0.00)

**Latency and cost:** TTFA median -, TTFT median -, total median -, output tokens median 2952.0, cost/run median -

### What it missed (1 criteria)

- **`umbrella_error_rate`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 4.5 points forgone
  - Compares Umbrella's 163 errors with other accounts / says it is high relative to volume, but does not give Umbrella's 94,217 request denominator, an error rate, or the Stark high-traffic comparison; lower-label rule => PARTIAL.

### What it got wrong (0)

No penalties and no false actions in any run.

### Raw evidence

- response: `runs/monday-001/claude-opus-5/run-001.json`
- response: `runs/monday-001/claude-opus-5/run-002.json`
- response: `runs/monday-001/claude-opus-5/run-003.json`
- evaluation: `evaluations/v1.10/evaluator-opus5-v0.1/monday-001/claude-opus-5/run-001.json`
- evaluation: `evaluations/v1.10/evaluator-opus5-v0.1/monday-001/claude-opus-5/run-002.json`
- evaluation: `evaluations/v1.10/evaluator-opus5-v0.1/monday-001/claude-opus-5/run-003.json`

---

## 3. GLM 5.3 Flash - 98.0 / 100

`glm5.3-flash`

| Dimension | Score | Max |
|---|---:|---:|
| Action detection | 25.0 | 25 |
| State reconstruction | 25.0 | 25 |
| Prioritization | 15.0 | 15 |
| Data reasoning | 13.5 | 15 |
| Uncertainty | 9.5 | 10 |
| Noise resistance | 10.0 | 10 |
| **Monday Score** | **98.0** | **100** |

**Runs:** 98.5, 97.0, 98.5  (min 97.0, max 98.5, run_range 1.5, sigma 0.87)

**Latency and cost:** TTFA median 118.8s, TTFT median 6.2s, total median 132.4s, output tokens median 5603.0, cost/run median -

### What it missed (2 criteria)

- **`friday_conversion_unknown`** - PARTIAL across 1 run(s), 1.5 points forgone
  - 'Julia saw weak conversion Friday but suspects noisy traffic; no owner assigned' - flagged, but no statement that the provided data cannot settle it
- **`umbrella_error_rate`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 4.5 points forgone
  - '1821ms (vs ~300 for everyone else)' quotes the peers' latency and 'Stark/Contoso error rates negligible' reaches for the rate idea, but no request volume and no rate figure - the 163-against-94,217 reading is never made

### What it got wrong (0)

No penalties and no false actions in any run.

### Raw evidence

- response: `runs/monday-001/glm5.3-flash/run-001.json`
- response: `runs/monday-001/glm5.3-flash/run-002.json`
- response: `runs/monday-001/glm5.3-flash/run-003.json`
- evaluation: `evaluations/v1.10/evaluator-opus5-v0.1/monday-001/glm5.3-flash/run-001.json`
- evaluation: `evaluations/v1.10/evaluator-opus5-v0.1/monday-001/glm5.3-flash/run-002.json`
- evaluation: `evaluations/v1.10/evaluator-opus5-v0.1/monday-001/glm5.3-flash/run-003.json`

---

## 4. Claude Fable 5.1 - 97.5 / 100

`claude-fable-5-1`

| Dimension | Score | Max |
|---|---:|---:|
| Action detection | 25.0 | 25 |
| State reconstruction | 25.0 | 25 |
| Prioritization | 15.0 | 15 |
| Data reasoning | 13.5 | 15 |
| Uncertainty | 9.0 | 10 |
| Noise resistance | 10.0 | 10 |
| **Monday Score** | **97.5** | **100** |

**Runs:** 97.0, 98.5, 97.0  (min 97.0, max 98.5, run_range 1.5, sigma 0.87)

**Latency and cost:** TTFA median -, TTFT median -, total median -, output tokens median 2352.0, cost/run median -

### What it missed (2 criteria)

- **`friday_conversion_unknown`** - PARTIAL/PARTIAL across 2 run(s), 3.0 points forgone
  - POST-AUDIT CORRECTION PASS -> PARTIAL (experiments/fable-5.1-full-mondaybench/AUDIT.md section 5). Original reason: flagged as unverifiable from the data
- **`umbrella_error_rate`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 4.5 points forgone
  - compares with other customers without connecting the count to traffic volume

### What it got wrong (0)

No penalties and no false actions in any run.

### Raw evidence

- response: `runs/monday-001/claude-fable-5-1/run-001.json`
- response: `runs/monday-001/claude-fable-5-1/run-002.json`
- response: `runs/monday-001/claude-fable-5-1/run-003.json`
- evaluation: `evaluations/v1.10/evaluator-opus5-v0.1/monday-001/claude-fable-5-1/run-001.json`
- evaluation: `evaluations/v1.10/evaluator-opus5-v0.1/monday-001/claude-fable-5-1/run-002.json`
- evaluation: `evaluations/v1.10/evaluator-opus5-v0.1/monday-001/claude-fable-5-1/run-003.json`

---

## 5. GLM 5.3 - 97.5 / 100

`glm5.3`

| Dimension | Score | Max |
|---|---:|---:|
| Action detection | 23.8 | 25 |
| State reconstruction | 25.0 | 25 |
| Prioritization | 14.2 | 15 |
| Data reasoning | 14.5 | 15 |
| Uncertainty | 10.0 | 10 |
| Noise resistance | 10.0 | 10 |
| **Monday Score** | **97.5** | **100** |

**Runs:** 100.0, 94.0, 98.5  (min 94.0, max 100.0, run_range 6.0, sigma 3.12)

**Latency and cost:** TTFA median 181.6s, TTFT median 1.8s, total median 202.8s, output tokens median 6861.0, cost/run median $0.0019

### What it missed (3 criteria)

- **`umbrella_action`** - PARTIAL across 1 run(s), 3.5 points forgone
  - detected and actioned for today ('Raise with engineering/CS today'), no root cause claimed - but ranked #4, below a holding reply to Initech and below the churn analysis, so it is under-prioritised; between PASS and PARTIAL the rubric's tie-break takes the lower
- **`umbrella_and_churn_high`** - PARTIAL across 1 run(s), 2.5 points forgone
  - churn is appropriately placed at #3; Umbrella is at #4 behind a routine email reply, so only one of the two is properly prioritised
- **`umbrella_error_rate`** - PARTIAL across 1 run(s), 1.5 points forgone
  - compares Umbrella with the other accounts on latency ('every other account: 267-341 ms') and notes they look healthy, but never reads the 163 errors against Umbrella's 94,217 requests, gives no error rate, and does not note that Stark carries more raw errors on far higher traffic

### What it got wrong (0)

No penalties and no false actions in any run.

### Raw evidence

- response: `runs/monday-001/glm5.3/run-001.json`
- response: `runs/monday-001/glm5.3/run-002.json`
- response: `runs/monday-001/glm5.3/run-003.json`
- evaluation: `evaluations/v1.10/evaluator-opus5-v0.1/monday-001/glm5.3/run-001.json`
- evaluation: `evaluations/v1.10/evaluator-opus5-v0.1/monday-001/glm5.3/run-002.json`
- evaluation: `evaluations/v1.10/evaluator-opus5-v0.1/monday-001/glm5.3/run-003.json`

---

## 6. Gemini 3.8 Flash (High) - 95.3 / 100

`gemini-3-8-flash-high`

| Dimension | Score | Max |
|---|---:|---:|
| Action detection | 25.0 | 25 |
| State reconstruction | 25.0 | 25 |
| Prioritization | 13.3 | 15 |
| Data reasoning | 12.0 | 15 |
| Uncertainty | 10.0 | 10 |
| Noise resistance | 10.0 | 10 |
| **Monday Score** | **95.3** | **100** |

**Runs:** 97.0, 94.5, 94.5  (min 94.5, max 97.0, run_range 2.5, sigma 1.44)

**Latency and cost:** TTFA median -, TTFT median -, total median -, output tokens median -, cost/run median -

### What it missed (2 criteria)

- **`umbrella_and_churn_high`** - PARTIAL/PARTIAL across 2 run(s), 5.0 points forgone
  - Only Umbrella is appropriately prioritised; churn ahead of the board meeting sits below a holding reply.
- **`umbrella_error_rate`** - FAIL/FAIL/FAIL across 3 run(s), 9.0 points forgone
  - The raw error count is presented as a critical signal with no reference to traffic.

### What it got wrong (0)

No penalties and no false actions in any run.

### Raw evidence

- response: `runs/monday-001/gemini-3-8-flash-high/run-001.json`
- response: `runs/monday-001/gemini-3-8-flash-high/run-002.json`
- response: `runs/monday-001/gemini-3-8-flash-high/run-003.json`
- evaluation: `evaluations/v1.10/evaluator-opus5-v0.1/monday-001/gemini-3-8-flash-high/run-001.json`
- evaluation: `evaluations/v1.10/evaluator-opus5-v0.1/monday-001/gemini-3-8-flash-high/run-002.json`
- evaluation: `evaluations/v1.10/evaluator-opus5-v0.1/monday-001/gemini-3-8-flash-high/run-003.json`

---

## 7. DeepSeek V4.1 Flash - 95.0 / 100

`deepseek-v4.1-flash-rerun-v1`

| Dimension | Score | Max |
|---|---:|---:|
| Action detection | 23.8 | 25 |
| State reconstruction | 25.0 | 25 |
| Prioritization | 14.2 | 15 |
| Data reasoning | 12.0 | 15 |
| Uncertainty | 10.0 | 10 |
| Noise resistance | 10.0 | 10 |
| **Monday Score** | **95.0** | **100** |

**Runs:** 91.0, 97.0, 97.0  (min 91.0, max 97.0, run_range 6.0, sigma 3.46)

**Latency and cost:** TTFA median 39.3s, TTFT median 1.8s, total median 44.1s, output tokens median 8154.0, cost/run median -

### What it missed (3 criteria)

- **`umbrella_action`** - PARTIAL across 1 run(s), 3.5 points forgone
  - The response recognizes the Umbrella anomaly but gives it weaker operational treatment than the PASS band requires.
- **`umbrella_and_churn_high`** - PARTIAL across 1 run(s), 2.5 points forgone
  - Only one of the two required high-priority investigations is consistently elevated.
- **`umbrella_error_rate`** - FAIL/FAIL/FAIL across 3 run(s), 9.0 points forgone
  - The frozen PASS/PARTIAL bands require traffic context; the error count alone is not an error-rate interpretation.

### What it got wrong (0)

No penalties and no false actions in any run.

### Raw evidence

- response: `runs/monday-001/deepseek-v4.1-flash-rerun-v1/run-001.json`
- response: `runs/monday-001/deepseek-v4.1-flash-rerun-v1/run-002.json`
- response: `runs/monday-001/deepseek-v4.1-flash-rerun-v1/run-003.json`
- evaluation: `evaluations/v1.10/evaluator-opus5-v0.1/monday-001/deepseek-v4.1-flash-rerun-v1/run-001.json`
- evaluation: `evaluations/v1.10/evaluator-opus5-v0.1/monday-001/deepseek-v4.1-flash-rerun-v1/run-002.json`
- evaluation: `evaluations/v1.10/evaluator-opus5-v0.1/monday-001/deepseek-v4.1-flash-rerun-v1/run-003.json`

---

## 8. Qwen 3.8 Flash - 92.5 / 100

`qwen3.8-flash`

| Dimension | Score | Max |
|---|---:|---:|
| Action detection | 25.0 | 25 |
| State reconstruction | 25.0 | 25 |
| Prioritization | 11.5 | 15 |
| Data reasoning | 12.5 | 15 |
| Uncertainty | 8.5 | 10 |
| Noise resistance | 10.0 | 10 |
| **Monday Score** | **92.5** | **100** |

**Runs:** 93.5, 95.0, 89.0  (min 89.0, max 95.0, run_range 6.0, sigma 3.12)

**Latency and cost:** TTFA median 72.2s, TTFT median 2.1s, total median 92.0s, output tokens median 9253.0, cost/run median -

### What it missed (4 criteria)

- **`friday_conversion_unknown`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 4.5 points forgone
  - 'The team suspected noisy traffic, but it has not been investigated' - flagged, but no statement that the provided data cannot settle it
- **`no_false_priorities`** - PARTIAL/PARTIAL/FAIL across 3 run(s), 8.0 points forgone
  - the resolved Acme incident close-out is #3, above the churn analysis
- **`umbrella_and_churn_high`** - PARTIAL across 1 run(s), 2.5 points forgone
  - Umbrella is well placed at #2, but the churn analysis is #6 of eight, below two task-cleanup items and the Initech reply
- **`umbrella_error_rate`** - FAIL/PARTIAL/FAIL across 3 run(s), 7.5 points forgone
  - the three figures are given in isolation: no request volume, no rate, no reference to any other customer

### What it got wrong (0)

No penalties and no false actions in any run.

### Raw evidence

- response: `runs/monday-001/qwen3.8-flash/run-001.json`
- response: `runs/monday-001/qwen3.8-flash/run-002.json`
- response: `runs/monday-001/qwen3.8-flash/run-003.json`
- evaluation: `evaluations/v1.10/evaluator-opus5-v0.1/monday-001/qwen3.8-flash/run-001.json`
- evaluation: `evaluations/v1.10/evaluator-opus5-v0.1/monday-001/qwen3.8-flash/run-002.json`
- evaluation: `evaluations/v1.10/evaluator-opus5-v0.1/monday-001/qwen3.8-flash/run-003.json`

---

## 9. DeepSeek V4 Flash - 90.8 / 100

`deepseek-v4-flash`

| Dimension | Score | Max |
|---|---:|---:|
| Action detection | 22.7 | 25 |
| State reconstruction | 25.0 | 25 |
| Prioritization | 12.7 | 15 |
| Data reasoning | 12.0 | 15 |
| Uncertainty | 8.5 | 10 |
| Noise resistance | 10.0 | 10 |
| **Monday Score** | **90.8** | **100** |

**Runs:** 95.5, 87.5, 89.5  (min 87.5, max 95.5, run_range 8.0, sigma 4.16)

**Latency and cost:** TTFA median 55.4s, TTFT median 1.4s, total median 63.3s, output tokens median 4871.0, cost/run median $0.0022

### What it missed (5 criteria)

- **`friday_conversion_unknown`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 4.5 points forgone
  - 'possibly noise, not yet investigated'; 'real or noise? Needs a quick check' - flagged, but no statement that the provided data cannot settle it
- **`no_false_priorities`** - PARTIAL across 1 run(s), 2.0 points forgone
  - the #3 task-cleanup bundle, which closes the resolved Acme task, is ranked above the churn analysis
- **`umbrella_action`** - PARTIAL/PARTIAL across 2 run(s), 7.0 points forgone
  - only under 'unclear': 'Umbrella metrics look anomalous... Needs an explanation' - never enters today's list
- **`umbrella_and_churn_high`** - PARTIAL/PARTIAL across 2 run(s), 5.0 points forgone
  - churn actionable at #4; Umbrella appears only under 'unclear'
- **`umbrella_error_rate`** - FAIL/FAIL/FAIL across 3 run(s), 9.0 points forgone
  - the three figures are given in isolation: no request volume, no rate, no reference to any other customer

### What it got wrong (0)

No penalties and no false actions in any run.

### Raw evidence

- response: `runs/monday-001/deepseek-v4-flash/run-001.json`
- response: `runs/monday-001/deepseek-v4-flash/run-002.json`
- response: `runs/monday-001/deepseek-v4-flash/run-003.json`
- evaluation: `evaluations/v1.10/evaluator-opus5-v0.1/monday-001/deepseek-v4-flash/run-001.json`
- evaluation: `evaluations/v1.10/evaluator-opus5-v0.1/monday-001/deepseek-v4-flash/run-002.json`
- evaluation: `evaluations/v1.10/evaluator-opus5-v0.1/monday-001/deepseek-v4-flash/run-003.json`

---

## 10. MIMO v2.5 - 88.2 / 100

`mimo-v2.5`

| Dimension | Score | Max |
|---|---:|---:|
| Action detection | 20.5 | 25 |
| State reconstruction | 25.0 | 25 |
| Prioritization | 11.2 | 15 |
| Data reasoning | 13.0 | 15 |
| Uncertainty | 8.5 | 10 |
| Noise resistance | 10.0 | 10 |
| **Monday Score** | **88.2** | **100** |

**Runs:** 91.0, 89.0, 84.5  (min 84.5, max 91.0, run_range 6.5, sigma 3.33)

**Latency and cost:** TTFA median 42.4s, TTFT median 24.3s, total median 64.1s, output tokens median 2150.0, cost/run median -

### What it missed (6 criteria)

- **`churn_action`** - PARTIAL across 1 run(s), 3.0 points forgone
  - the board deadline is stated ('Need a fuller breakdown for Tuesday's board meeting'), but the analysis never enters the action table - it is filed under 'no action required from you' as 'Analysis task is yours for Tuesday'
- **`friday_conversion_unknown`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 4.5 points forgone
  - 'flagged as potentially noisy Friday traffic. Worth revisiting next week' - not repeated as fact, but no data-gap statement
- **`no_false_priorities`** - PARTIAL/PARTIAL across 2 run(s), 4.0 points forgone
  - Globex, which the source says has no urgency, is #4, above the Umbrella investigation
- **`umbrella_action`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 10.5 points forgone
  - only under 'Unclear': 'Worth investigating - is there an active issue, or was this just a quiet week?' - never enters today's list
- **`umbrella_and_churn_high`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 7.5 points forgone
  - churn actionable in today's list; Umbrella appears only under 'Unclear'
- **`umbrella_error_rate`** - PARTIAL/PARTIAL/FAIL across 3 run(s), 6.0 points forgone
  - 'roughly 6x higher than any other customer' positions Umbrella against the rest of the table, but on latency only - no request volume and no error rate

### What it got wrong (0)

No penalties and no false actions in any run.

### Raw evidence

- response: `runs/monday-001/mimo-v2.5/run-001.json`
- response: `runs/monday-001/mimo-v2.5/run-002.json`
- response: `runs/monday-001/mimo-v2.5/run-003.json`
- evaluation: `evaluations/v1.10/evaluator-opus5-v0.1/monday-001/mimo-v2.5/run-001.json`
- evaluation: `evaluations/v1.10/evaluator-opus5-v0.1/monday-001/mimo-v2.5/run-002.json`
- evaluation: `evaluations/v1.10/evaluator-opus5-v0.1/monday-001/mimo-v2.5/run-003.json`

---

## 11. GLM 5.2 - 84.3 / 100

`glm5.2`

| Dimension | Score | Max |
|---|---:|---:|
| Action detection | 20.3 | 25 |
| State reconstruction | 25.0 | 25 |
| Prioritization | 11.2 | 15 |
| Data reasoning | 10.0 | 15 |
| Uncertainty | 7.8 | 10 |
| Noise resistance | 10.0 | 10 |
| **Monday Score** | **84.3** | **100** |

**Runs:** 87.0, 75.0, 91.0  (min 75.0, max 91.0, run_range 16.0, sigma 8.33)

**Latency and cost:** TTFA median 2.7s, TTFT median 1.3s, total median 6.9s, output tokens median 1241.0, cost/run median $0.0047

### What it missed (8 criteria)

- **`friday_conversion_unknown`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 4.5 points forgone
  - 'Is it noise or a real signal? Needs a look at the dashboard' - uncertainty flagged, but no statement that the provided data cannot settle it
- **`no_false_priorities`** - FAIL across 1 run(s), 4.0 points forgone
  - two false priorities outrank the Umbrella investigation: the resolved Acme task close-out at #4 and Globex at #5, which the source says has no urgency
- **`umbrella_action`** - PARTIAL/FAIL/PARTIAL across 3 run(s), 14.0 points forgone
  - in today's list but last of six and in the lowest band, below the Acme close-out and Globex: strong substance ('may indicate a serious issue or at-risk account'), badly under-prioritized
- **`umbrella_and_churn_high`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 7.5 points forgone
  - churn well placed at #3, but the Umbrella investigation is buried at #6
- **`umbrella_detected`** - FAIL across 1 run(s), 5.0 points forgone
  - the anomaly is missed entirely - the only customer row it reads is Initech's, and it reads it correctly as healthy
- **`umbrella_error_rate`** - PARTIAL/FAIL/PARTIAL across 3 run(s), 6.0 points forgone
  - '1,821 ms vs. ~300 ms baseline' and 'p95 latency 6x higher than peers' quote the other customers' values, but no request volume and no error rate
- **`umbrella_metrics`** - FAIL across 1 run(s), 4.0 points forgone
  - no Umbrella figures
- **`umbrella_unknown_cause`** - PARTIAL across 1 run(s), 2.0 points forgone
  - invents no cause, but expresses no uncertainty either - Umbrella is absent

### What it got wrong (0)

No penalties and no false actions in any run.

### Raw evidence

- response: `runs/monday-001/glm5.2/run-001.json`
- response: `runs/monday-001/glm5.2/run-002.json`
- response: `runs/monday-001/glm5.2/run-003.json`
- evaluation: `evaluations/v1.10/evaluator-opus5-v0.1/monday-001/glm5.2/run-001.json`
- evaluation: `evaluations/v1.10/evaluator-opus5-v0.1/monday-001/glm5.2/run-002.json`
- evaluation: `evaluations/v1.10/evaluator-opus5-v0.1/monday-001/glm5.2/run-003.json`

---

## 12. Qwen 3.6 - 82.8 / 100

`qwen3.6`

| Dimension | Score | Max |
|---|---:|---:|
| Action detection | 21.5 | 25 |
| State reconstruction | 25.0 | 25 |
| Prioritization | 11.2 | 15 |
| Data reasoning | 12.0 | 15 |
| Uncertainty | 6.5 | 10 |
| Noise resistance | 10.0 | 10 |
| **Monday Score** | **82.8** | **100** |

**Runs:** 82.5, 80.5, 85.5  (min 80.5, max 85.5, run_range 5.0, sigma 2.52)

**Latency and cost:** TTFA median 0.8s, TTFT median 0.8s, total median 6.2s, output tokens median 1036.0, cost/run median -

### What it missed (6 criteria)

- **`friday_conversion_unknown`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 4.5 points forgone
  - the Friday conversion question is never raised: the claim is not repeated, but the gap is not flagged
- **`no_false_priorities`** - PARTIAL/PARTIAL across 2 run(s), 4.0 points forgone
  - Globex, which the source says has no urgency, is #2 High, above the churn analysis
- **`umbrella_action`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 10.5 points forgone
  - under 'does not require action': 'a potential churn risk, though not explicitly flagged as urgent... Worth keeping in mind' - noticed, but not work for today
- **`umbrella_and_churn_high`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 7.5 points forgone
  - churn actionable at #2 HIGH; Umbrella filed under 'does not require action'
- **`umbrella_error_rate`** - FAIL/FAIL/FAIL across 3 run(s), 9.0 points forgone
  - the 163 errors are never mentioned; no volume, no rate, no other customer's figures
- **`umbrella_unknown_cause`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 6.0 points forgone
  - no cause asserted as established, but no uncertainty expressed either, and Umbrella is absent from section 4

### What it got wrong (2)

- **MATERIAL_HALLUCINATION** `MATERIAL_HALLUCINATION` (-5.0)
  - The source says pricing stays confidential until approved AND publicly announced; Wednesday is only the next review, and no announcement is scheduled at all. The error is written into the reply the user is told to send Initech, so it leaves the company.
  - evidence: Strictly confidential until Wednesday's review / state that new tiers are under review and will be announced publicly soon
- **MATERIAL_HALLUCINATION** `MATERIAL_HALLUCINATION` (-5.0)
  - The source says pricing stays confidential until approved AND publicly announced; Wednesday is only the next review. A reader could conclude the tiers may be shared after Wednesday.
  - evidence: Strictly confidential until Wednesday's review / state that pricing is under review and will be communicated officially soon

### Raw evidence

- response: `runs/monday-001/qwen3.6/run-001.json`
- response: `runs/monday-001/qwen3.6/run-002.json`
- response: `runs/monday-001/qwen3.6/run-003.json`
- evaluation: `evaluations/v1.10/evaluator-opus5-v0.1/monday-001/qwen3.6/run-001.json`
- evaluation: `evaluations/v1.10/evaluator-opus5-v0.1/monday-001/qwen3.6/run-002.json`
- evaluation: `evaluations/v1.10/evaluator-opus5-v0.1/monday-001/qwen3.6/run-003.json`

---

## 13. Gemma 4 - 70.7 / 100

`gemma4`

| Dimension | Score | Max |
|---|---:|---:|
| Action detection | 15.3 | 25 |
| State reconstruction | 23.3 | 25 |
| Prioritization | 12.5 | 15 |
| Data reasoning | 3.0 | 15 |
| Uncertainty | 6.5 | 10 |
| Noise resistance | 10.0 | 10 |
| **Monday Score** | **70.7** | **100** |

**Runs:** 68.5, 68.5, 75.0  (min 68.5, max 75.0, run_range 6.5, sigma 3.75)

**Latency and cost:** TTFA median 0.6s, TTFT median 0.6s, total median 5.5s, output tokens median 605.0, cost/run median -

### What it missed (9 criteria)

- **`contoso_action`** - PARTIAL/PARTIAL across 2 run(s), 8.0 points forgone
  - first item under High with the 11:00 deadline, but 'ready to renew pending a single legal clarification' states sequence, not jeopardy: nothing says what happens if 11:00 is missed
- **`contoso_blocked`** - PARTIAL/PARTIAL across 2 run(s), 5.0 points forgone
  - 'pending a single legal clarification' - identifies the question, misses the signature or approval consequence
- **`friday_conversion_unknown`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 4.5 points forgone
  - 'currently unconfirmed if this was a data anomaly or a trend' - uncertainty noted, data gap not flagged
- **`umbrella_action`** - FAIL/FAIL/FAIL across 3 run(s), 21.0 points forgone
  - Umbrella never mentioned; the metrics file is not used at all
- **`umbrella_and_churn_high`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 7.5 points forgone
  - churn is a High item; Umbrella is entirely absent
- **`umbrella_detected`** - FAIL/FAIL/FAIL across 3 run(s), 15.0 points forgone
  - anomaly missed
- **`umbrella_error_rate`** - FAIL/FAIL/FAIL across 3 run(s), 9.0 points forgone
  - no metrics reasoning of any kind
- **`umbrella_metrics`** - FAIL/FAIL/FAIL across 3 run(s), 12.0 points forgone
  - no supporting figures at all
- **`umbrella_unknown_cause`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 6.0 points forgone
  - invents no cause, but expresses no uncertainty either - Umbrella is absent

### What it got wrong (0)

No penalties and no false actions in any run.

### Raw evidence

- response: `runs/monday-001/gemma4/run-001.json`
- response: `runs/monday-001/gemma4/run-002.json`
- response: `runs/monday-001/gemma4/run-003.json`
- evaluation: `evaluations/v1.10/evaluator-opus5-v0.1/monday-001/gemma4/run-001.json`
- evaluation: `evaluations/v1.10/evaluator-opus5-v0.1/monday-001/gemma4/run-002.json`
- evaluation: `evaluations/v1.10/evaluator-opus5-v0.1/monday-001/gemma4/run-003.json`

---

## Reproducing this

```bash
mondaybench validate --scenario monday-001 \
    --evaluator evaluator-opus5-v0.1
mondaybench leaderboard --scenario monday-001 \
    --evaluator evaluator-opus5-v0.1 --official
```

Every input, raw response, judge verdict and scoring rule is in this repository. See `README.md` for the methodology.
