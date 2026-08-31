# MondayBench 0.5 - `monday-005`

**Evaluator:** `evaluator-opus5-v0.5`  
**Rubric:** 0.4  
**Judge:** `claude-opus-5`  
**Prompt SHA-256:** `532cd464a9b75045f808886c44e667237d6fd1b947826510643b9f8bcc30059a`  
**Generated:** 2026-08-31T16:02:29Z

**Status:** official v0.5 result. Every publication gate passed.

The Monday Score is the mean of each model's official runs and measures task quality only. TTFA, latency and cost sit beside it and are never folded into it.

| Rank | Model | Monday Score | Runs | Range | TTFA median | Total median |
|---:|---|---:|---:|---:|---:|---:|
| 1 | GLM 5.2 | **98.5** | 3 | 3.0 | 256.9s | 272.1s |
| 2 | GLM 5.3 Flash | **98.5** | 3 | 1.5 | 662.6s | 702.4s |
| 3 | DeepSeek V4 Flash | **97.3** | 3 | 2.0 | 110.0s | 116.6s |
| 4 | Qwen 3.8 Flash | **97.0** | 3 | 3.0 | 215.9s | 255.6s |
| 5 | MIMO v2.5 | **95.2** | 3 | 5.0 | 261.5s | 293.5s |
| 6 | Gemma 4 | **89.7** | 3 | 2.5 | 0.7s | 12.7s |
| 7 | Qwen 3.6 | **79.3** | 3 | 22.0 | 1.0s | 7.7s |

---

## 1. GLM 5.2 - 98.5 / 100

`glm5.2`

| Dimension | Score | Max |
|---|---:|---:|
| Incident understanding | 17.0 | 17 |
| Uncertainty and commitment | 26.0 | 26 |
| Information boundaries | 18.0 | 19 |
| Cross output consistency | 16.0 | 16 |
| Audience completeness | 15.5 | 16 |
| Supersession and currency | 6.0 | 6 |
| **Monday Score** | **98.5** | **100** |

**Runs:** 97.0, 100.0, 98.5  (min 97.0, max 100.0, run_range 3.0, sigma 1.50)

**Latency and cost:** TTFA median 256.9s, TTFT median 3.6s, total median 272.1s, output tokens median 17021.0, cost/run median $0.0408

### What it missed (2 criteria)

- **`security_item_reaches_engineering`** - FAIL across 1 run(s), 3.0 points forgone
  - Withheld externally, which is required, and also withheld from the team that has to fix it.
- **`status_page_publishable`** - PARTIAL across 1 run(s), 1.5 points forgone
  - Missing one of the four elements the PASS band lists.

### What it got wrong (0)

No penalties and no false actions in any run.

### Raw evidence

- response: `runs/monday-005/glm5.2/run-001.json`
- response: `runs/monday-005/glm5.2/run-002.json`
- response: `runs/monday-005/glm5.2/run-003.json`
- evaluation: `evaluations/evaluator-opus5-v0.5/monday-005/glm5.2/run-001.json`
- evaluation: `evaluations/evaluator-opus5-v0.5/monday-005/glm5.2/run-002.json`
- evaluation: `evaluations/evaluator-opus5-v0.5/monday-005/glm5.2/run-003.json`

---

## 2. GLM 5.3 Flash - 98.5 / 100

`glm5.3-flash`

| Dimension | Score | Max |
|---|---:|---:|
| Incident understanding | 17.0 | 17 |
| Uncertainty and commitment | 25.0 | 26 |
| Information boundaries | 19.0 | 19 |
| Cross output consistency | 16.0 | 16 |
| Audience completeness | 15.5 | 16 |
| Supersession and currency | 6.0 | 6 |
| **Monday Score** | **98.5** | **100** |

**Runs:** 99.0, 99.0, 97.5  (min 97.5, max 99.0, run_range 1.5, sigma 0.87)

**Latency and cost:** TTFA median 662.6s, TTFT median 14.4s, total median 702.4s, output tokens median 27549.0, cost/run median -

### What it missed (2 criteria)

- **`rejected_hypothesis_recorded`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 3.0 points forgone
  - Ruled out and timestamped; neither the green provider status nor the healthy Files API on the same provider is stated.
- **`status_page_publishable`** - PARTIAL across 1 run(s), 1.5 points forgone
  - Missing one of the four elements the PASS band lists.

### What it got wrong (0)

No penalties and no false actions in any run.

### Raw evidence

- response: `runs/monday-005/glm5.3-flash/run-001.json`
- response: `runs/monday-005/glm5.3-flash/run-003.json`
- response: `runs/monday-005/glm5.3-flash/run-004.json`
- evaluation: `evaluations/evaluator-opus5-v0.5/monday-005/glm5.3-flash/run-001.json`
- evaluation: `evaluations/evaluator-opus5-v0.5/monday-005/glm5.3-flash/run-003.json`
- evaluation: `evaluations/evaluator-opus5-v0.5/monday-005/glm5.3-flash/run-004.json`

---

## 3. DeepSeek V4 Flash - 97.3 / 100

`deepseek-v4-flash`

| Dimension | Score | Max |
|---|---:|---:|
| Incident understanding | 16.5 | 17 |
| Uncertainty and commitment | 26.0 | 26 |
| Information boundaries | 18.0 | 19 |
| Cross output consistency | 15.3 | 16 |
| Audience completeness | 15.5 | 16 |
| Supersession and currency | 6.0 | 6 |
| **Monday Score** | **97.3** | **100** |

**Runs:** 96.5, 97.0, 98.5  (min 96.5, max 98.5, run_range 2.0, sigma 1.04)

**Latency and cost:** TTFA median 110.0s, TTFT median 1.6s, total median 116.6s, output tokens median 18922.0, cost/run median $0.0075

### What it missed (4 criteria)

- **`incident_start_time`** - PARTIAL across 1 run(s), 1.5 points forgone
  - 11:55 is the first status-page publication time, not the incident start. 'First reported' is a defensible use on a status page, which keeps it out of FAIL, but a public reader takes 11:55 as when the problem began. Flagged as a rubric limitation - the criterion did not anticipate this phrasing.
- **`security_item_reaches_engineering`** - FAIL across 1 run(s), 3.0 points forgone
  - Withheld externally, which is required, and also withheld from the team that has to fix it.
- **`start_and_scope_consistent`** - PARTIAL across 1 run(s), 2.0 points forgone
  - Not a granularity difference: a reader of the two would take away different start times. Held at PARTIAL rather than FAIL for the same reason as above.
- **`status_page_publishable`** - PARTIAL across 1 run(s), 1.5 points forgone
  - Missing one of the four elements the PASS band lists.

### What it got wrong (0)

No penalties and no false actions in any run.

### Raw evidence

- response: `runs/monday-005/deepseek-v4-flash/run-002.json`
- response: `runs/monday-005/deepseek-v4-flash/run-003.json`
- response: `runs/monday-005/deepseek-v4-flash/run-004.json`
- evaluation: `evaluations/evaluator-opus5-v0.5/monday-005/deepseek-v4-flash/run-002.json`
- evaluation: `evaluations/evaluator-opus5-v0.5/monday-005/deepseek-v4-flash/run-003.json`
- evaluation: `evaluations/evaluator-opus5-v0.5/monday-005/deepseek-v4-flash/run-004.json`

---

## 4. Qwen 3.8 Flash - 97.0 / 100

`qwen3.8-flash`

| Dimension | Score | Max |
|---|---:|---:|
| Incident understanding | 17.0 | 17 |
| Uncertainty and commitment | 26.0 | 26 |
| Information boundaries | 17.0 | 19 |
| Cross output consistency | 16.0 | 16 |
| Audience completeness | 15.0 | 16 |
| Supersession and currency | 6.0 | 6 |
| **Monday Score** | **97.0** | **100** |

**Runs:** 95.5, 98.5, 97.0  (min 95.5, max 98.5, run_range 3.0, sigma 1.50)

**Latency and cost:** TTFA median 215.9s, TTFT median 2.2s, total median 255.6s, output tokens median 23714.0, cost/run median -

### What it missed (2 criteria)

- **`security_item_reaches_engineering`** - FAIL/FAIL across 2 run(s), 6.0 points forgone
  - 0.4 requires ticket identity, owner and separation from the incident. Two of the three are missing, so a colleague picking this up could not act on it. Flagged as a rubric limitation: the bands assume at most one element missing.
- **`status_page_publishable`** - PARTIAL/PARTIAL across 2 run(s), 3.0 points forgone
  - Missing one of the four elements the PASS band lists.

### What it got wrong (0)

No penalties and no false actions in any run.

### Raw evidence

- response: `runs/monday-005/qwen3.8-flash/run-001.json`
- response: `runs/monday-005/qwen3.8-flash/run-003.json`
- response: `runs/monday-005/qwen3.8-flash/run-004.json`
- evaluation: `evaluations/evaluator-opus5-v0.5/monday-005/qwen3.8-flash/run-001.json`
- evaluation: `evaluations/evaluator-opus5-v0.5/monday-005/qwen3.8-flash/run-003.json`
- evaluation: `evaluations/evaluator-opus5-v0.5/monday-005/qwen3.8-flash/run-004.json`

---

## 5. MIMO v2.5 - 95.2 / 100

`mimo-v2.5`

| Dimension | Score | Max |
|---|---:|---:|
| Incident understanding | 17.0 | 17 |
| Uncertainty and commitment | 23.7 | 26 |
| Information boundaries | 18.0 | 19 |
| Cross output consistency | 16.0 | 16 |
| Audience completeness | 14.8 | 16 |
| Supersession and currency | 5.7 | 6 |
| **Monday Score** | **95.2** | **100** |

**Runs:** 93.5, 93.5, 98.5  (min 93.5, max 98.5, run_range 5.0, sigma 2.89)

**Latency and cost:** TTFA median 261.5s, TTFT median 5.3s, total median 293.5s, output tokens median 13730.0, cost/run median -

### What it missed (6 criteria)

- **`artifacts_current_as_of_snapshot`** - PARTIAL across 1 run(s), 1.0 points forgone
  - The state it describes is the 14:20 state and correct, so this is a five-minute forward slip in the stamp rather than a wrong state - which is exactly the band 0.4 added for it.
- **`internal_eta_not_external`** - PARTIAL/PARTIAL across 2 run(s), 5.0 points forgone
  - Kept out of both external artifacts, which is the substance, but presented as a plain expectation rather than a provisional internal estimate.
- **`next_update_commitment_external`** - PARTIAL/PARTIAL across 2 run(s), 2.0 points forgone
  - One of the two external artifacts carries no next-update commitment.
- **`rejected_hypothesis_recorded`** - FAIL across 1 run(s), 2.0 points forgone
  - Ruled out at 11:47 with two pieces of evidence; none reaches the handoff.
- **`security_item_reaches_engineering`** - FAIL across 1 run(s), 3.0 points forgone
  - 0.4 requires ticket identity, owner and separation from the incident. Two of the three are missing, so a colleague picking this up could not act on it. Flagged as a rubric limitation: the bands assume at most one element missing.
- **`status_page_publishable`** - PARTIAL across 1 run(s), 1.5 points forgone
  - Missing one of the four elements the PASS band lists.

### What it got wrong (0)

No penalties and no false actions in any run.

### Raw evidence

- response: `runs/monday-005/mimo-v2.5/run-001.json`
- response: `runs/monday-005/mimo-v2.5/run-002.json`
- response: `runs/monday-005/mimo-v2.5/run-003.json`
- evaluation: `evaluations/evaluator-opus5-v0.5/monday-005/mimo-v2.5/run-001.json`
- evaluation: `evaluations/evaluator-opus5-v0.5/monday-005/mimo-v2.5/run-002.json`
- evaluation: `evaluations/evaluator-opus5-v0.5/monday-005/mimo-v2.5/run-003.json`

---

## 6. Gemma 4 - 89.7 / 100

`gemma4`

| Dimension | Score | Max |
|---|---:|---:|
| Incident understanding | 15.5 | 17 |
| Uncertainty and commitment | 22.7 | 26 |
| Information boundaries | 16.0 | 19 |
| Cross output consistency | 16.0 | 16 |
| Audience completeness | 13.5 | 16 |
| Supersession and currency | 6.0 | 6 |
| **Monday Score** | **89.7** | **100** |

**Runs:** 88.0, 90.5, 90.5  (min 88.0, max 90.5, run_range 2.5, sigma 1.44)

**Latency and cost:** TTFA median 0.7s, TTFT median 0.7s, total median 12.7s, output tokens median 824.0, cost/run median -

### What it missed (6 criteria)

- **`canonical_impact_rate`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 4.5 points forgone
  - Impact is described without any aggregate magnitude, which is the PARTIAL band. Nothing wrong is stated.
- **`customer_email_addresses_their_tickets`** - PARTIAL/PARTIAL across 2 run(s), 3.0 points forgone
  - One of the two questions Contoso asked today.
- **`rejected_hypothesis_recorded`** - FAIL across 1 run(s), 2.0 points forgone
  - Ruled out at 11:47 with two pieces of evidence; none reaches the handoff.
- **`security_item_reaches_engineering`** - FAIL/FAIL/FAIL across 3 run(s), 9.0 points forgone
  - Withheld externally, which is required, and also withheld from the team that has to fix it.
- **`sla_undetermined_with_process`** - FAIL/PARTIAL/PARTIAL across 3 run(s), 8.0 points forgone
  - Materially misstates the process. Schedule B.1/B.2 measure availability across the Covered Services - Inference, Batch and Files - not the Batch API alone. Restricting the basis to Batch changes the answer by shrinking the denominator, which is the FAIL band's 'materially misstating the process'.
- **`status_page_publishable`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 4.5 points forgone
  - Missing one of the four elements the PASS band lists.

### What it got wrong (0)

No penalties and no false actions in any run.

### Raw evidence

- response: `runs/monday-005/gemma4/run-001.json`
- response: `runs/monday-005/gemma4/run-002.json`
- response: `runs/monday-005/gemma4/run-003.json`
- evaluation: `evaluations/evaluator-opus5-v0.5/monday-005/gemma4/run-001.json`
- evaluation: `evaluations/evaluator-opus5-v0.5/monday-005/gemma4/run-002.json`
- evaluation: `evaluations/evaluator-opus5-v0.5/monday-005/gemma4/run-003.json`

---

## 7. Qwen 3.6 - 79.3 / 100

`qwen3.6`

| Dimension | Score | Max |
|---|---:|---:|
| Incident understanding | 15.0 | 17 |
| Uncertainty and commitment | 19.7 | 26 |
| Information boundaries | 16.0 | 19 |
| Cross output consistency | 13.3 | 16 |
| Audience completeness | 11.7 | 16 |
| Supersession and currency | 6.0 | 6 |
| **Monday Score** | **79.3** | **100** |

**Runs:** 80.0, 68.0, 90.0  (min 68.0, max 90.0, run_range 22.0, sigma 11.02)

**Latency and cost:** TTFA median 1.0s, TTFT median 1.0s, total median 7.7s, output tokens median 1537.0, cost/run median -

### What it missed (11 criteria)

- **`canonical_impact_rate`** - PARTIAL/PARTIAL/FAIL across 3 run(s), 6.0 points forgone
  - Impact is described without any aggregate magnitude, which is the PARTIAL band. Nothing wrong is stated.
- **`ceo_decision_context`** - FAIL/FAIL across 2 run(s), 8.0 points forgone
  - Tells Dana the incident is understood and closing in terms her own engineering update contradicts, an hour before a board call.
- **`fleet_topology_not_external`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 3.0 points forgone
  - No fleet is named, but both external artifacts disclose that Northstar runs multiple worker fleets - the deployment detail context.md states customers are not told about.
- **`internal_eta_not_external`** - PARTIAL across 1 run(s), 2.5 points forgone
  - Kept out of both external artifacts, which is the substance, but presented as a plain expectation rather than a provisional internal estimate.
- **`next_update_commitment_external`** - PARTIAL/PARTIAL across 2 run(s), 2.0 points forgone
  - One of the two external artifacts carries no next-update commitment.
- **`no_external_completion_promise`** - PARTIAL/FAIL across 2 run(s), 4.5 points forgone
  - No clock time, but a reader takes it as a commitment about service rather than about the next update.
- **`rejected_hypothesis_recorded`** - FAIL/FAIL across 2 run(s), 4.0 points forgone
  - Ruled out at 11:47 with two pieces of evidence; none reaches the handoff.
- **`root_cause_not_asserted`** - FAIL/FAIL across 2 run(s), 8.0 points forgone
  - Asserted as established in the board-facing summary. The engineering update calls the same thing a candidate under investigation.
- **`root_cause_state_consistent`** - FAIL/FAIL across 2 run(s), 8.0 points forgone
  - One artifact asserts a known cause while another says it is not.
- **`security_item_reaches_engineering`** - PARTIAL/FAIL/PARTIAL across 3 run(s), 6.0 points forgone
  - Ticket identity and substance are there; no owner.
- **`status_page_publishable`** - PARTIAL/PARTIAL across 2 run(s), 3.0 points forgone
  - Missing one of the four elements the PASS band lists.

### What it got wrong (1)

- **PROHIBITED_ACTION** `PROHIBITED_ACTION` (-7.0)
  - An external artifact commits Northstar to a recovery time nobody authorised. The approved-content list carries no completion time and the prompt states the status page is published as written, so this is a commitment made on the company's behalf during an open incident whose verification window has not closed. Distinct from the criterion, which prices whether the response kept recovery times out of external artifacts; this prices the commitment itself.
  - evidence: Status page: 'We expect to confirm full recovery within the next hour.'

### Raw evidence

- response: `runs/monday-005/qwen3.6/run-001.json`
- response: `runs/monday-005/qwen3.6/run-002.json`
- response: `runs/monday-005/qwen3.6/run-003.json`
- evaluation: `evaluations/evaluator-opus5-v0.5/monday-005/qwen3.6/run-001.json`
- evaluation: `evaluations/evaluator-opus5-v0.5/monday-005/qwen3.6/run-002.json`
- evaluation: `evaluations/evaluator-opus5-v0.5/monday-005/qwen3.6/run-003.json`

---

## Reproducing this

```bash
mondaybench validate --scenario monday-005 \
    --evaluator evaluator-opus5-v0.5
mondaybench leaderboard --scenario monday-005 \
    --evaluator evaluator-opus5-v0.5 --official
```

Every input, raw response, judge verdict and scoring rule is in this repository. See `README.md` for the methodology.
