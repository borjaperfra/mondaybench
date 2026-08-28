# MondayBench 0.2 - `monday-002`

**Evaluator:** `evaluator-opus5-v0.2`  
**Rubric:** 0.2  
**Judge:** `claude-opus-5`  
**Prompt SHA-256:** `740e627cbc7413c321ede0d54000504de54821d34ff4677f82731b89600423a8`  
**Generated:** 2026-08-28T14:13:01Z

**Status:** official v0.1 result. Every publication gate passed.

The Monday Score is the mean of each model's official runs and measures task quality only. TTFA, latency and cost sit beside it and are never folded into it.

| Rank | Model | Monday Score | Runs | Range | TTFA median | Total median |
|---:|---|---:|---:|---:|---:|---:|
| 1 | GLM 5.2 | **91.2** | 3 | 8.0 | 67.0s | 85.4s |
| 2 | DeepSeek V4 Flash | **89.3** | 3 | 13.5 | 162.6s | 178.8s |
| 3 | GLM 5.3 Flash | **87.3** | 3 | 6.5 | 238.5s | 316.6s |
| 4 | Qwen 3.8 Flash | **86.5** | 3 | 33.5 | 258.9s | 285.0s |
| 5 | MIMO v2.5 | **81.2** | 3 | 33.0 | 163.3s | 195.4s |
| 6 | Qwen 3.6 | **70.2** | 3 | 31.0 | 0.9s | 18.2s |
| 7 | Gemma 4 | **54.2** | 3 | 13.5 | 0.3s | 8.7s |

---

## 1. GLM 5.2 - 91.2 / 100

`glm5.2`

| Dimension | Score | Max |
|---|---:|---:|
| Action detection | 0.0 | 25 |
| State reconstruction | 15.0 | 25 |
| Prioritization | 0.0 | 15 |
| Data reasoning | 0.0 | 15 |
| Uncertainty | 0.0 | 10 |
| Noise resistance | 0.0 | 10 |
| **Monday Score** | **91.2** | **100** |

**Runs:** 90.5, 87.5, 95.5  (min 87.5, max 95.5, run_range 8.0, sigma 4.04)

**Latency and cost:** TTFA median 67.0s, TTFT median 1.0s, total median 85.4s, output tokens median 6777.0, cost/run median $0.0165

### What it missed (4 criteria)

- **`choose_option_b`** - PARTIAL/PARTIAL across 2 run(s), 8.0 points forgone
  - chooses A, which is viable and correctly scheduled; B is set aside because 'the 2.9.5 diff is already submitted' is 'not confirmed' - a defensible reading, but submitting it is an action the user could take at 09:07
- **`ownership_supersession`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 7.5 points forgone
  - names Daniel as the current sender and gates it on Sam's confirmation, but Sarah's handoff is never traced and the stale 'You' task is not displaced
- **`parallelize_work`** - PARTIAL across 1 run(s), 2.0 points forgone
  - the board pack and Globex triage are scheduled for the right day and the right deadline, but the plan does not say they run inside the delegated deploy window
- **`schedule_feasibility`** - PARTIAL/FAIL across 2 run(s), 9.0 points forgone
  - every constraint is identified, including the right review window ('Priya's 09:00-09:25 review'), but no B schedule is committed to

### What it got wrong (0)

No penalties and no false actions in any run.

### Raw evidence

- response: `runs/monday-002/glm5.2/run-001.json`
- response: `runs/monday-002/glm5.2/run-002.json`
- response: `runs/monday-002/glm5.2/run-003.json`
- evaluation: `evaluations/evaluator-opus5-v0.2/monday-002/glm5.2/run-001.json`
- evaluation: `evaluations/evaluator-opus5-v0.2/monday-002/glm5.2/run-002.json`
- evaluation: `evaluations/evaluator-opus5-v0.2/monday-002/glm5.2/run-003.json`

---

## 2. DeepSeek V4 Flash - 89.3 / 100

`deepseek-v4-flash`

| Dimension | Score | Max |
|---|---:|---:|
| Action detection | 0.0 | 25 |
| State reconstruction | 15.0 | 25 |
| Prioritization | 0.0 | 15 |
| Data reasoning | 0.0 | 15 |
| Uncertainty | 0.0 | 10 |
| Noise resistance | 0.0 | 10 |
| **Monday Score** | **89.3** | **100** |

**Runs:** 97.5, 86.5, 84.0  (min 84.0, max 97.5, run_range 13.5, sigma 7.18)

**Latency and cost:** TTFA median 162.6s, TTFT median 2.8s, total median 178.8s, output tokens median 14863.0, cost/run median $0.0056

### What it missed (4 criteria)

- **`choose_option_b`** - PARTIAL/PARTIAL across 2 run(s), 8.0 points forgone
  - chooses viable A and schedules it correctly, on a false claim about B
- **`option_b_sequence`** - PARTIAL/PARTIAL across 2 run(s), 7.0 points forgone
  - 'Do not use 2.9.5-patch without a completed Security delta review' places the review before deploy, but the B chain is not carried through verification and Sam
- **`ownership_supersession`** - PARTIAL/PARTIAL across 2 run(s), 5.0 points forgone
  - names Daniel as the current sender and gates it on Sam's confirmation, but Sarah's handoff is never traced and the stale 'You' task is not displaced
- **`schedule_feasibility`** - FAIL/FAIL across 2 run(s), 12.0 points forgone
  - 'Priya's 09:35-10:25 gap plus Marcus leaving at 10:20 prevents completion before noon' - with the review in her 09:00-09:35 window the deploy runs 09:32-10:17 and rollout opens by 11:00

### What it got wrong (0)

No penalties and no false actions in any run.

### Raw evidence

- response: `runs/monday-002/deepseek-v4-flash/run-001.json`
- response: `runs/monday-002/deepseek-v4-flash/run-002.json`
- response: `runs/monday-002/deepseek-v4-flash/run-003.json`
- evaluation: `evaluations/evaluator-opus5-v0.2/monday-002/deepseek-v4-flash/run-001.json`
- evaluation: `evaluations/evaluator-opus5-v0.2/monday-002/deepseek-v4-flash/run-002.json`
- evaluation: `evaluations/evaluator-opus5-v0.2/monday-002/deepseek-v4-flash/run-003.json`

---

## 3. GLM 5.3 Flash - 87.3 / 100

`glm5.3-flash`

| Dimension | Score | Max |
|---|---:|---:|
| Action detection | 0.0 | 25 |
| State reconstruction | 15.0 | 25 |
| Prioritization | 0.0 | 15 |
| Data reasoning | 0.0 | 15 |
| Uncertainty | 0.0 | 10 |
| Noise resistance | 0.0 | 10 |
| **Monday Score** | **87.3** | **100** |

**Runs:** 85.0, 85.5, 91.5  (min 85.0, max 91.5, run_range 6.5, sigma 3.62)

**Latency and cost:** TTFA median 238.5s, TTFT median 1.9s, total median 316.6s, output tokens median 12394.0, cost/run median -

### What it missed (5 criteria)

- **`choose_option_b`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 12.0 points forgone
  - chooses viable A and schedules it correctly, but 'B is not viable today' overstates: the review runs in Priya's 09:00-09:35 window and the deploy ends 10:17
- **`conditional_launch_timing`** - PARTIAL/PARTIAL across 2 run(s), 3.0 points forgone
  - kills the 10:30 task, but 'By 09:45 - Confirm to Atlas: launch proceeds today, rollout opens ~11:00' goes out before the deploy has been verified
- **`no_unsupported_causality`** - PARTIAL across 1 run(s), 1.0 points forgone
  - 'The -61% admin-logins drop is consistent with the SSO breakage - actionable today via the ticket, not a mystery' presents the link as settled rather than as a hypothesis
- **`option_b_sequence`** - PARTIAL/PARTIAL across 2 run(s), 7.0 points forgone
  - 'B needs a 25-min delta review first' and 'Don't deploy 2.9.5-patch before Priya's delta review completes' place the gate correctly, but verification and Sam are not carried into the B chain
- **`schedule_feasibility`** - FAIL/FAIL/PARTIAL across 3 run(s), 15.0 points forgone
  - no B schedule is produced; 'delta review + 45-min deploy leaves zero slack against Marcus's 10:20 exit' understates the real 3-minute margin and concludes infeasibility

### What it got wrong (0)

No penalties and no false actions in any run.

### Raw evidence

- response: `runs/monday-002/glm5.3-flash/run-001.json`
- response: `runs/monday-002/glm5.3-flash/run-002.json`
- response: `runs/monday-002/glm5.3-flash/run-003.json`
- evaluation: `evaluations/evaluator-opus5-v0.2/monday-002/glm5.3-flash/run-001.json`
- evaluation: `evaluations/evaluator-opus5-v0.2/monday-002/glm5.3-flash/run-002.json`
- evaluation: `evaluations/evaluator-opus5-v0.2/monday-002/glm5.3-flash/run-003.json`

---

## 4. Qwen 3.8 Flash - 86.5 / 100

`qwen3.8-flash`

| Dimension | Score | Max |
|---|---:|---:|
| Action detection | 0.0 | 25 |
| State reconstruction | 14.2 | 25 |
| Prioritization | 0.0 | 15 |
| Data reasoning | 0.0 | 15 |
| Uncertainty | 0.0 | 10 |
| Noise resistance | 0.0 | 10 |
| **Monday Score** | **86.5** | **100** |

**Runs:** 93.0, 66.5, 100.0  (min 66.5, max 100.0, run_range 33.5, sigma 17.67)

**Latency and cost:** TTFA median 258.9s, TTFT median 1.6s, total median 285.0s, output tokens median 33714.0, cost/run median -

### What it missed (8 criteria)

- **`choose_option_b`** - PARTIAL/PARTIAL across 2 run(s), 8.0 points forgone
  - chooses viable A and schedules it correctly; B is set aside because 'there is no evidence the 2.9.5 diff is already submitted', which the response itself files as a thing to verify rather than a settled constraint
- **`conditional_launch_timing`** - FAIL across 1 run(s), 3.0 points forgone
  - 'Migration confirmed for today. Rollout begins shortly' is sent to the customer at 09:45 as a statement of fact, when the response's own timeline opens rollout at 10:45-11:00
- **`customer_signal_integration`** - PARTIAL across 1 run(s), 3.0 points forgone
  - Acme is crossed against its contract and Soylent/Wonka against contracts and support, but Globex is handled on ticket severity alone and no counter-signal comparison is drawn
- **`globex_priority`** - PARTIAL across 1 run(s), 2.5 points forgone
  - Globex is ranked fourth as 'Support Risk' with the action 'Monitor'; the 18-day renewal, usage -18% and admin logins -61% are all absent from the assessment
- **`launch_state`** - PARTIAL across 1 run(s), 2.5 points forgone
  - the recovery state and Maya's removed gate are right, but '09:45 Atlas Confirmation: "Migration confirmed for today. Rollout begins shortly"' is sent 75 minutes before rollout can open
- **`ownership_supersession`** - PARTIAL across 1 run(s), 2.5 points forgone
  - names Daniel as the current sender and gates it on Sam's confirmation, but Sarah's handoff is never traced and the stale 'You' task is not displaced
- **`pricing_authority`** - FAIL across 1 run(s), 5.0 points forgone
  - the authority is inverted: 'Internal scenario planning values are obsolete/incorrect. The pinned workbook (enterprise-pricing-v4-final.xlsx) is authoritative internally'. Daniel's email says the opposite - the pinned workbook is not authoritative and his 09:07 values are the internal reference
- **`schedule_feasibility`** - PARTIAL/FAIL across 2 run(s), 9.0 points forgone
  - every constraint is named and the A sequence is exact, but no B schedule is committed - it is deferred to MUST VERIFY

### What it got wrong (1)

- **MATERIAL_HALLUCINATION** `MATERIAL_HALLUCINATION` (-5.0)
  - The source authority is stated backwards. Daniel's Friday email says 'Pinned workbook is not authoritative. Use my 09:07 Slack values internally only.' Acting on this would put the obsolete numbers into internal planning and discard the current ones - the judge prompt names wrong source authority as material.
  - evidence: 'Internal scenario planning values are obsolete/incorrect. The pinned workbook (enterprise-pricing-v4-final.xlsx) is authoritative internally'

### Raw evidence

- response: `runs/monday-002/qwen3.8-flash/run-001.json`
- response: `runs/monday-002/qwen3.8-flash/run-002.json`
- response: `runs/monday-002/qwen3.8-flash/run-003.json`
- evaluation: `evaluations/evaluator-opus5-v0.2/monday-002/qwen3.8-flash/run-001.json`
- evaluation: `evaluations/evaluator-opus5-v0.2/monday-002/qwen3.8-flash/run-002.json`
- evaluation: `evaluations/evaluator-opus5-v0.2/monday-002/qwen3.8-flash/run-003.json`

---

## 5. MIMO v2.5 - 81.2 / 100

`mimo-v2.5`

| Dimension | Score | Max |
|---|---:|---:|
| Action detection | 0.0 | 25 |
| State reconstruction | 14.2 | 25 |
| Prioritization | 0.0 | 15 |
| Data reasoning | 0.0 | 15 |
| Uncertainty | 0.0 | 10 |
| Noise resistance | 0.0 | 10 |
| **Monday Score** | **81.2** | **100** |

**Runs:** 64.5, 81.5, 97.5  (min 64.5, max 97.5, run_range 33.0, sigma 16.50)

**Latency and cost:** TTFA median 163.3s, TTFT median 1.8s, total median 195.4s, output tokens median 9510.0, cost/run median -

### What it missed (8 criteria)

- **`choose_option_b`** - PARTIAL/PARTIAL across 2 run(s), 8.0 points forgone
  - chooses viable A; the rationale is 'fewer moving parts' and an accepted 8% risk rather than a comparison the evidence supports
- **`conditional_launch_timing`** - FAIL across 1 run(s), 3.0 points forgone
  - '09:45 | Confirm to Atlas: Enterprise Controls launch is on for today; admins should be standing by. Migration target ~11:00' - an unconditional external commitment made before the deploy is verified
- **`expansion_fully_reconciled`** - PARTIAL across 1 run(s), 3.0 points forgone
  - Wayne EUR18k, Globex EUR12k, Soylent EUR10k and Wonka EUR14k all appear, and 'Together these are the entire EUR24k unexplained gap', but the four are never closed against the EUR54k
- **`globex_priority`** - PARTIAL/PARTIAL across 2 run(s), 5.0 points forgone
  - '3 open tickets, one high-severity (SSO blocker). September expansion (EUR12k) stalled in procurement. Renewal in 18 days' - the usage -18% and admin -61% signals are never brought in
- **`launch_state`** - PARTIAL across 1 run(s), 2.5 points forgone
  - the recovery state and Maya's removed gate are right, but '09:45 | Confirm to Atlas: Enterprise Controls launch is on for today... Migration target ~11:00' is sent before any verification
- **`option_b_sequence`** - FAIL/PARTIAL across 2 run(s), 10.5 points forgone
  - no B chain is given; the contingency - 'fall to Option B with a delta review Monday afternoon' - is offered for a moment when Marcus, the only deployer, has already left
- **`ownership_supersession`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 7.5 points forgone
  - names Daniel as the current sender and gates it on Sam's confirmation, but Sarah's handoff is never traced and the stale 'You' task is not displaced
- **`schedule_feasibility`** - FAIL/FAIL across 2 run(s), 12.0 points forgone
  - no B schedule is produced

### What it got wrong (1)

- **MAJOR_CONTRADICTION** `MAJOR_CONTRADICTION` (-5.0)
  - The timeline states that Security's post-deploy check is not required and then schedules it. Priya's policy is explicit that a verified build still needs a production post-deploy check, so the first statement is also wrong on the policy - a reader following the timeline in order would skip a mandatory gate.
  - evidence: '09:35 | Deploy complete. No post-deploy verification needed (no code change from staging-verified build).' against '10:25-10:45 | Priya runs post-deploy verification (~20 min)'

### Raw evidence

- response: `runs/monday-002/mimo-v2.5/run-001.json`
- response: `runs/monday-002/mimo-v2.5/run-002.json`
- response: `runs/monday-002/mimo-v2.5/run-003.json`
- evaluation: `evaluations/evaluator-opus5-v0.2/monday-002/mimo-v2.5/run-001.json`
- evaluation: `evaluations/evaluator-opus5-v0.2/monday-002/mimo-v2.5/run-002.json`
- evaluation: `evaluations/evaluator-opus5-v0.2/monday-002/mimo-v2.5/run-003.json`

---

## 6. Qwen 3.6 - 70.2 / 100

`qwen3.6`

| Dimension | Score | Max |
|---|---:|---:|
| Action detection | 0.0 | 25 |
| State reconstruction | 12.5 | 25 |
| Prioritization | 0.0 | 15 |
| Data reasoning | 0.0 | 15 |
| Uncertainty | 0.0 | 10 |
| Noise resistance | 0.0 | 10 |
| **Monday Score** | **70.2** | **100** |

**Runs:** 75.5, 83.0, 52.0  (min 52.0, max 83.0, run_range 31.0, sigma 16.17)

**Latency and cost:** TTFA median 0.9s, TTFT median 0.9s, total median 18.2s, output tokens median 2644.0, cost/run median -

### What it missed (13 criteria)

- **`avoid_acme_false_positive`** - PARTIAL across 1 run(s), 2.0 points forgone
  - 'Acme: Medium Risk. Structural shift to annual batch processing. Usage down 45%... Monitor for churn' - the explanation is noticed and then the account is still carried as a churn watch
- **`causal_boundary`** - PARTIAL across 1 run(s), 1.5 points forgone
  - 'Do NOT invent causes for the EUR24k expansion gap' is stated and then broken in the same section by 'attributed to Soylent and Wonka usage declines and Acme's structural shift'
- **`choose_option_b`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 12.0 points forgone
  - chooses A, which is viable, but calls it 'the only viable path' while its own contingency shows B is 'tight but possible'
- **`conditional_launch_timing`** - PARTIAL/FAIL across 2 run(s), 4.5 points forgone
  - no external promise is made, but the ~10:10 rollout figure is passed to Sam and Daniel with no conditionality, and the stale 10:30 Atlas task is never addressed
- **`executive_gate_superseded`** - PARTIAL/PARTIAL across 2 run(s), 5.0 points forgone
  - no approval is sought, but the supersession is never established and the stale task is not rejected
- **`expansion_fully_reconciled`** - PARTIAL across 1 run(s), 3.0 points forgone
  - 'Explained (EUR30k): Wayne EUR18k; Globex EUR12k' and 'Remaining Gap (EUR24k)' are right, but the response concludes 'exact arithmetic requires full account file review' and never closes Soylent EUR10k + Wonka EUR14k
- **`globex_priority`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 7.5 points forgone
  - '3 open tickets (High/Medium/Medium). SSO setup failure (G-441) is a blocker for admin operations. Expansion is pending procurement' - the 18-day renewal and the usage/admin figures are absent
- **`launch_state`** - PARTIAL/FAIL across 2 run(s), 7.5 points forgone
  - the recovery state and both option timings are right, but Maya's removal of the executive gate never appears and the stale 09:15 approval task is left standing
- **`no_unsupported_causality`** - FAIL across 1 run(s), 2.0 points forgone
  - 'The remaining EUR24k gap is attributed to Soylent and Wonka usage declines and Acme's structural shift' asserts a cause Maya explicitly forbade inventing, and Acme's expansion is unchanged at zero
- **`option_b_sequence`** - PARTIAL across 1 run(s), 3.5 points forgone
  - 'Option B: Marcus deploy -> Priya 25m delta review (async) -> Priya 20m post-deploy verify -> Sam 15m rollout check' puts the delta review after the deploy
- **`ownership_supersession`** - PARTIAL/PARTIAL across 2 run(s), 5.0 points forgone
  - names Daniel as the current sender and gates it on Sam's confirmation, but Sarah's handoff is never traced and the stale 'You' task is not displaced
- **`parallelize_work`** - PARTIAL across 1 run(s), 2.0 points forgone
  - '10:30-11:00 Board Pack Expansion Reconciliation' sits after the release rather than inside the delegated waiting window
- **`schedule_feasibility`** - FAIL/PARTIAL/FAIL across 3 run(s), 15.0 points forgone
  - 'Monitor Post-Deploy Verify: Priya performs 20-minute verification (09:35-09:55)' - Priya is unavailable 09:35-10:25, so the recommended A schedule cannot run as written

### What it got wrong (3)

- **MAJOR_PLANNING_ERROR** `MAJOR_PLANNING_ERROR` (-7.0)
  - calendars.csv and Priya's own email both put her out of contact 09:35-10:25. The recommended plan books her required verification inside that window and derives a rollout time from it, so the schedule the response tells the user to execute cannot run.
  - evidence: 'Monitor Post-Deploy Verify: Priya performs 20-minute verification (09:35-09:55)' and 'If verify finishes at 09:55, rollout opens ~10:10'
- **MAJOR_PLANNING_ERROR** `MAJOR_PLANNING_ERROR` (-7.0)
  - Priya's break is 09:35-10:25, not before it. The recommended plan books her mandatory verification inside her stated unavailable window and then commits a rollout time to the CEO on that basis, so the plan the response tells the user to execute cannot run.
  - evidence: 'Priya verifies 09:35-09:55 (after her break). Sam checks 09:55-10:10. Rollout opens ~10:15. Feasible.'
- **MATERIAL_HALLUCINATION** `MATERIAL_HALLUCINATION` (-5.0)
  - No source establishes usage decline as the cause of either expansion reduction, and Acme's September expansion is unchanged at zero so it contributes nothing to the gap. Maya's brief specifically forbids supplying causes the data does not establish, and this goes into the board pack.
  - evidence: 'The remaining EUR24k gap is attributed to Soylent and Wonka usage declines and Acme's structural shift'

### Raw evidence

- response: `runs/monday-002/qwen3.6/run-001.json`
- response: `runs/monday-002/qwen3.6/run-002.json`
- response: `runs/monday-002/qwen3.6/run-003.json`
- evaluation: `evaluations/evaluator-opus5-v0.2/monday-002/qwen3.6/run-001.json`
- evaluation: `evaluations/evaluator-opus5-v0.2/monday-002/qwen3.6/run-002.json`
- evaluation: `evaluations/evaluator-opus5-v0.2/monday-002/qwen3.6/run-003.json`

---

## 7. Gemma 4 - 54.2 / 100

`gemma4`

| Dimension | Score | Max |
|---|---:|---:|
| Action detection | 0.0 | 25 |
| State reconstruction | 10.0 | 25 |
| Prioritization | 0.0 | 15 |
| Data reasoning | 0.0 | 15 |
| Uncertainty | 0.0 | 10 |
| Noise resistance | 0.0 | 10 |
| **Monday Score** | **54.2** | **100** |

**Runs:** 58.0, 45.5, 59.0  (min 45.5, max 59.0, run_range 13.5, sigma 7.52)

**Latency and cost:** TTFA median 0.3s, TTFT median 0.3s, total median 8.7s, output tokens median 921.0, cost/run median -

### What it missed (13 criteria)

- **`choose_option_b`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 12.0 points forgone
  - chooses B for the right reason - 'to minimize session reset risk for Atlas' - but never shows it viable, and the schedule it then writes is not
- **`conditional_launch_timing`** - FAIL/PARTIAL/FAIL across 3 run(s), 7.5 points forgone
  - '09:30-09:45: Confirm the 10:30 launch window to Atlas (pending successful deployment/verification)' commits to a time the response's own timeline opens at 11:30-12:00
- **`customer_signal_integration`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 9.0 points forgone
  - Globex and Acme are each crossed against two sources, but Soylent and Wonka never reach the customer priorities at all
- **`executive_gate_superseded`** - PARTIAL/FAIL/PARTIAL across 3 run(s), 10.0 points forgone
  - no approval is sought, but the supersession is never established and the stale 09:15 task is left standing
- **`expansion_before_11`** - PARTIAL/PARTIAL across 2 run(s), 5.0 points forgone
  - '11:00: Submit expansion reconciliation to Maya' lands on the deadline itself, after the 10:45-11:00 rollout step, with no earlier draft
- **`expansion_fully_reconciled`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 9.0 points forgone
  - 'EUR30k of the gap is explained by Wayne and Globex. The remaining EUR24k is driven by account-level reductions (Soylent, Wonka, Acme)' - the split is right but Acme's expansion is unchanged at zero, so the EUR24k attribution never closes
- **`globex_priority`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 7.5 points forgone
  - 'Active contract (18 days to renewal) with high-severity SSO/SCIM support tickets and a pending EUR12k expansion' - three of the four signals, with usage -18% and admin -61% missing
- **`launch_state`** - FAIL/FAIL/FAIL across 3 run(s), 15.0 points forgone
  - Maya's removal of the executive gate never appears anywhere, and '09:30-09:45: Confirm the 10:30 launch window to Atlas' revives the stale launch time the sources supersede
- **`no_unsupported_causality`** - FAIL across 1 run(s), 2.0 points forgone
  - '3 open support tickets (including high-severity SSO issue) impacting the pending September expansion' asserts a causal link between the tickets and the procurement delay that no source establishes
- **`option_b_sequence`** - PARTIAL/PARTIAL across 2 run(s), 7.0 points forgone
  - 'Marcus deploys 2.9.5-patch (45m). Priya performs 25m delta review (asynchronous) + 20m post-deploy verification' puts the mandatory pre-deploy review after the deploy, contradicting the 09:15 instruction to submit the diff first
- **`ownership_supersession`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 7.5 points forgone
  - names Daniel as the current sender and gates it on Sam's confirmation, but Sarah's handoff is never traced and the stale 'You' task is not displaced
- **`parallelize_work`** - PARTIAL across 1 run(s), 2.0 points forgone
  - the board pack is submitted at 11:00 as a discrete step rather than drafted inside the delegated deploy window
- **`schedule_feasibility`** - FAIL/FAIL/FAIL across 3 run(s), 18.0 points forgone
  - '10:30-11:30 Execution Sequence: Marcus deploys 2.9.5-patch (45m)' - Marcus's hard stop is 10:20, so the deploy the plan schedules has no deployer

### What it got wrong (4)

- **MAJOR_PLANNING_ERROR** `MAJOR_PLANNING_ERROR` (-7.0)
  - calendars.csv and Marcus's own email both put his hard stop at 10:20. The plan schedules his 45-minute deploy to start ten minutes after he leaves, so the release the response recommends cannot be executed at all.
  - evidence: '10:30 - 11:30: Execution Sequence: Marcus deploys 2.9.5-patch (45m)'
- **MAJOR_PLANNING_ERROR** `MAJOR_PLANNING_ERROR` (-7.0)
  - The plan starts a 45-minute deploy at 09:45-10:15 while quoting, in the same line, that Marcus leaves at 10:20. The recommended release cannot complete under the availability the response itself cites.
  - evidence: '09:45 - 10:15: Coordinate with Marcus to initiate deployment of Option B. (Marcus must start by 09:15 and leave by 10:20; deployment takes 45m).'
- **MATERIAL_HALLUCINATION** `MATERIAL_HALLUCINATION` (-5.0)
  - contracts.csv states only that Globex's September expansion is pending procurement. Nothing links the support tickets to the procurement delay, and Maya's brief explicitly forbids supplying causes the data does not establish.
  - evidence: '3 open support tickets (including high-severity SSO issue) impacting the pending September expansion'
- **MAJOR_PLANNING_ERROR** `MAJOR_PLANNING_ERROR` (-7.0)
  - Marcus's hard stop is 10:20, so the deploy has no deployer, and the three steps total 80 minutes inside a 50-minute block. The release the response recommends is unexecutable on both counts.
  - evidence: '10:25 - 11:15: Deployment Sequence: Marcus deploys Option B (45m) -> Priya performs post-deploy verification (20m) -> Sam performs rollout sanity check (15m)'

### Raw evidence

- response: `runs/monday-002/gemma4/run-001.json`
- response: `runs/monday-002/gemma4/run-002.json`
- response: `runs/monday-002/gemma4/run-003.json`
- evaluation: `evaluations/evaluator-opus5-v0.2/monday-002/gemma4/run-001.json`
- evaluation: `evaluations/evaluator-opus5-v0.2/monday-002/gemma4/run-002.json`
- evaluation: `evaluations/evaluator-opus5-v0.2/monday-002/gemma4/run-003.json`

---

## Reproducing this

```bash
mondaybench validate --scenario monday-002 \
    --evaluator evaluator-opus5-v0.2
mondaybench leaderboard --scenario monday-002 \
    --evaluator evaluator-opus5-v0.2 --official
```

Every input, raw response, judge verdict and scoring rule is in this repository. See `README.md` for the methodology.
