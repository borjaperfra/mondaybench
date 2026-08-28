# MondayBench 0.3-draft - `monday-003`

**Evaluator:** `evaluator-opus5-v0.3-calibration-3`  
**Rubric:** 0.3  
**Judge:** `claude-opus-5`  
**Prompt SHA-256:** `aaf788f309d955d2b427c86fe7d95d2bbf88575fde7306adcfd74b0ec4a4103f`  
**Generated:** 2026-08-28T19:08:14Z

> **NOT AN OFFICIAL RESULT.** This leaderboard was built without `--official`, so the publication gates were not enforced: run counts, prompt/rubric/judge consistency and scoring arithmetic are unverified. Do not cite these numbers as MondayBench v0.3-draft results.

The Monday Score is the mean of each model's official runs and measures task quality only. TTFA, latency and cost sit beside it and are never folded into it.

| Rank | Model | Monday Score | Runs | Range | TTFA median | Total median |
|---:|---|---:|---:|---:|---:|---:|
| 1 | GLM 5.3 Flash | **97.5** | 2 | 0.0 | 153.9s | 176.7s |
| 2 | Qwen 3.8 Flash | **96.8** | 2 | 6.5 | 335.0s | 358.7s |
| 3 | GLM 5.2 | **86.5** | 2 | 6.0 | 51.6s | 63.6s |
| 4 | MIMO v2.5 | **82.0** | 2 | 26.0 | 138.7s | 170.0s |
| 5 | DeepSeek V4 Flash | **76.8** | 2 | 13.5 | 32.6s | 36.7s |
| 6 | Gemma 4 | **54.5** | 2 | 3.0 | 0.7s | 6.7s |
| 7 | Qwen 3.6 | **41.5** | 2 | 3.0 | 1.2s | 17.4s |

---

## 1. GLM 5.3 Flash - 97.5 / 100

`glm5.3-flash`

| Dimension | Score | Max |
|---|---:|---:|
| Critical path and dependencies | 21.0 | 21 |
| Resource allocation | 25.0 | 25 |
| Planning and parallelization | 18.0 | 18 |
| Decision quality | 14.0 | 14 |
| State reconstruction | 10.0 | 10 |
| Accuracy and uncertainty | 9.5 | 12 |
| **Monday Score** | **97.5** | **100** |

**Runs:** 97.5, 97.5  (min 97.5, max 97.5, run_range 0.0, sigma 0.00)

**Latency and cost:** TTFA median 153.9s, TTFT median 5.7s, total median 176.7s, output tokens median 9815.5, cost/run median -

### What it missed (1 criteria)

- **`factual_plan_accuracy`** - PARTIAL/PARTIAL across 2 run(s), 5.0 points forgone
  - one substitution: 'Daniel can execute Wed AM, still ahead of the Wed 15:00 external milestone'. The billing migration's external deadline is Thursday 2026-09-24 15:00. Every other anchor it uses is correct, and the contingency conclusion survives the correction, so the plan is not materially altered

### What it got wrong (0)

No penalties and no false actions in any run.

### Raw evidence

- response: `runs/monday-003/glm5.3-flash/run-001.json`
- response: `runs/monday-003/glm5.3-flash/run-002.json`
- evaluation: `evaluations/evaluator-opus5-v0.3-calibration-3/monday-003/glm5.3-flash/run-001.json`
- evaluation: `evaluations/evaluator-opus5-v0.3-calibration-3/monday-003/glm5.3-flash/run-002.json`

---

## 2. Qwen 3.8 Flash - 96.8 / 100

`qwen3.8-flash`

| Dimension | Score | Max |
|---|---:|---:|
| Critical path and dependencies | 21.0 | 21 |
| Resource allocation | 23.5 | 25 |
| Planning and parallelization | 16.2 | 18 |
| Decision quality | 14.0 | 14 |
| State reconstruction | 10.0 | 10 |
| Accuracy and uncertainty | 12.0 | 12 |
| **Monday Score** | **96.8** | **100** |

**Runs:** 100.0, 93.5  (min 93.5, max 100.0, run_range 6.5, sigma 4.60)

**Latency and cost:** TTFA median 335.0s, TTFT median 3.1s, total median 358.7s, output tokens median 35127.0, cost/run median -

### What it missed (2 criteria)

- **`concurrent_sso_and_contoso`** - PARTIAL across 1 run(s), 3.5 points forgone
  - Julia's export does run alongside Marcus's SSO work, but the two engineering items are serial through one person: the compatibility patch does not start until the permission patch is finished at 14:10
- **`marcus_reserved_for_sso`** - PARTIAL across 1 run(s), 3.0 points forgone
  - states the constraint exactly - 'Only realistic owner for SSO compatibility... Needs protection Monday afternoon' - and releases the 3-hour instrumentation hold, but then spends that protected afternoon on the substitutable Contoso patch, which is what moves the rollout from 14:00 to 16:40

### What it got wrong (0)

No penalties and no false actions in any run.

### Raw evidence

- response: `runs/monday-003/qwen3.8-flash/run-001.json`
- response: `runs/monday-003/qwen3.8-flash/run-002.json`
- evaluation: `evaluations/evaluator-opus5-v0.3-calibration-3/monday-003/qwen3.8-flash/run-001.json`
- evaluation: `evaluations/evaluator-opus5-v0.3-calibration-3/monday-003/qwen3.8-flash/run-002.json`

---

## 3. GLM 5.2 - 86.5 / 100

`glm5.2`

| Dimension | Score | Max |
|---|---:|---:|
| Critical path and dependencies | 17.2 | 21 |
| Resource allocation | 18.2 | 25 |
| Planning and parallelization | 16.2 | 18 |
| Decision quality | 14.0 | 14 |
| State reconstruction | 10.0 | 10 |
| Accuracy and uncertainty | 10.8 | 12 |
| **Monday Score** | **86.5** | **100** |

**Runs:** 89.5, 83.5  (min 83.5, max 89.5, run_range 6.0, sigma 4.24)

**Latency and cost:** TTFA median 51.6s, TTFT median 1.5s, total median 63.6s, output tokens median 8503.5, cost/run median $0.0210

### What it missed (6 criteria)

- **`concurrent_sso_and_contoso`** - PARTIAL across 1 run(s), 3.5 points forgone
  - the two chains are run one after the other through one person: 'after Elena's schema lands (~12:30): (a) contoso_permission_patch 2h, then (b) api_compatibility_patch'
- **`elena_migration_fallback`** - PARTIAL across 1 run(s), 2.5 points forgone
  - has the mechanics - 'Daniel needs the 30-min permission transfer and runbook walkthrough' - but frames it as something to do 'if it slips beyond Wednesday noon', when Elena is gone by then
- **`factual_plan_accuracy`** - PARTIAL across 1 run(s), 2.5 points forgone
  - one substitution: the delivery table reads 'Billing migration + backfill | Wed 15:00'. The stated external deadline is Thursday 2026-09-24 15:00. It changes nothing downstream - its own plan lands the migration Monday - so the plan is not materially altered
- **`marcus_reserved_for_sso`** - PARTIAL/PARTIAL across 2 run(s), 6.0 points forgone
  - frees him - 'release Marcus's 3h hold', 'These two stale items are... consuming Marcus's capacity' - and keeps him on the patch, but never states that the compatibility work has no substitute
- **`pricing_dependency`** - FAIL/PARTIAL across 2 run(s), 7.5 points forgone
  - inverts the gate and misses the shortcut: 'Pricing page build gates packaging approval pack (screenshots needed)', with the pack scheduled for Tuesday once the page exists; Priya's line that mockups are acceptable is never used
- **`scarce_resource_allocation`** - PARTIAL across 1 run(s), 5.0 points forgone
  - detects the contention and prices the substitute exactly - 'Daniel: available as backup for contoso_permission_patch (3.5h + 0.5h walkthrough with Marcus)' - then declines to use him and serialises both patches through Marcus, with no reason given for preferring that. The stated justification is only 'Contoso deadline is Tuesday 16:00, so this goes first'

### What it got wrong (0)

No penalties and no false actions in any run.

### Raw evidence

- response: `runs/monday-003/glm5.2/run-001.json`
- response: `runs/monday-003/glm5.2/run-002.json`
- evaluation: `evaluations/evaluator-opus5-v0.3-calibration-3/monday-003/glm5.2/run-001.json`
- evaluation: `evaluations/evaluator-opus5-v0.3-calibration-3/monday-003/glm5.2/run-002.json`

---

## 4. MIMO v2.5 - 82.0 / 100

`mimo-v2.5`

| Dimension | Score | Max |
|---|---:|---:|
| Critical path and dependencies | 18.5 | 21 |
| Resource allocation | 18.5 | 25 |
| Planning and parallelization | 16.2 | 18 |
| Decision quality | 12.8 | 14 |
| State reconstruction | 10.0 | 10 |
| Accuracy and uncertainty | 8.5 | 12 |
| **Monday Score** | **82.0** | **100** |

**Runs:** 95.0, 69.0  (min 69.0, max 95.0, run_range 26.0, sigma 18.38)

**Latency and cost:** TTFA median 138.7s, TTFT median 2.0s, total median 170.0s, output tokens median 14599.0, cost/run median -

### What it missed (7 criteria)

- **`concurrent_sso_and_contoso`** - PARTIAL across 1 run(s), 3.5 points forgone
  - the two chains are serialised through one person: 'Marcus must do the Contoso patch first (Tuesday deadline) then immediately pivot to the SSO compatibility patch'
- **`factual_plan_accuracy`** - FAIL across 1 run(s), 5.0 points forgone
  - two substituted deadlines, both used to compute buffers it then reports: 'Billing schema migration | Mon 12:10 | Wed 15:00 | ~51h' - the stated deadline is Thursday 15:00 - and 'Pricing page | Mon ~12:10 | Wed EOD | ~29h', where the page is due Thursday 17:00
- **`formatting_urgent_not_blocking`** - PARTIAL across 1 run(s), 2.5 points forgone
  - handles it correctly - Julia, 2h, Monday morning, 'None' dependency - but never states that the reported breakage is cosmetic or that the file imports correctly
- **`marcus_reserved_for_sso`** - PARTIAL across 1 run(s), 3.0 points forgone
  - releases the instrumentation and states the no-substitute ground for the compatibility patch, but does not protect the capacity: Marcus is given 5.5 hours of afternoon coding and the SSO work is pushed into Tuesday behind the Contoso patch
- **`pricing_dependency`** - PARTIAL/PARTIAL across 2 run(s), 5.0 points forgone
  - gets the gate - 'Packaging approval: Tue afternoon (if submitted before 12:00)' ahead of 'Pricing page public: Tue EOD' - but treats the pack as blocked on the page ('packaging_approval_pack | Sarah | pricing_page done') and never finds the mockup route
- **`scarce_resource_allocation`** - FAIL across 1 run(s), 10.0 points forgone
  - denies the substitute exists: 'There is no other person who can own either patch - the account-mapping branch is Marcus's exclusively', and serialises both patches through him. Daniel's offer of 3.5 hours plus a half-hour walkthrough is in the sources and is never engaged
- **`uncertainty_discipline`** - PARTIAL across 1 run(s), 2.0 points forgone
  - nine risks, most of them substantive, but the plan rests on one unsupported claim it treats as fact - that nobody but Marcus can own either patch - and every allocation decision follows from it

### What it got wrong (1)

- **MATERIAL_HALLUCINATION** `MATERIAL_HALLUCINATION` (-5.0)
  - Daniel states in #support-escalations that he was in the permission model two weeks ago for the SCIM work, can take the Contoso patch, and needs three and a half hours plus half an hour with Marcus. The claim is material: it is the stated reason both patches are serialised through one engineer, which pushes the SSO rollout from Tuesday 14:00 to Tuesday 16:30.
  - evidence: 'There is no other person who can own either patch - the account-mapping branch is Marcus's exclusively.'

### Raw evidence

- response: `runs/monday-003/mimo-v2.5/run-001.json`
- response: `runs/monday-003/mimo-v2.5/run-002.json`
- evaluation: `evaluations/evaluator-opus5-v0.3-calibration-3/monday-003/mimo-v2.5/run-001.json`
- evaluation: `evaluations/evaluator-opus5-v0.3-calibration-3/monday-003/mimo-v2.5/run-002.json`

---

## 5. DeepSeek V4 Flash - 76.8 / 100

`deepseek-v4-flash`

| Dimension | Score | Max |
|---|---:|---:|
| Critical path and dependencies | 18.5 | 21 |
| Resource allocation | 12.0 | 25 |
| Planning and parallelization | 12.8 | 18 |
| Decision quality | 11.5 | 14 |
| State reconstruction | 10.0 | 10 |
| Accuracy and uncertainty | 12.0 | 12 |
| **Monday Score** | **76.8** | **100** |

**Runs:** 70.0, 83.5  (min 70.0, max 83.5, run_range 13.5, sigma 9.55)

**Latency and cost:** TTFA median 32.6s, TTFT median 1.5s, total median 36.7s, output tokens median 6243.5, cost/run median $0.0028

### What it missed (7 criteria)

- **`concurrent_sso_and_contoso`** - PARTIAL/PARTIAL across 2 run(s), 7.0 points forgone
  - 'The permission patch and compatibility patch are sequential because both require Marcus' - the two chains are explicitly serialised through one person
- **`elena_migration_fallback`** - FAIL across 1 run(s), 5.0 points forgone
  - Elena's Wednesday departure, the production-permission transfer and the Daniel fallback appear nowhere in the plan or the risks
- **`formatting_urgent_not_blocking`** - PARTIAL/PARTIAL across 2 run(s), 5.0 points forgone
  - keeps the format fix with Julia and off the critical work, but never says it is cosmetic or that the customer confirmed the file imports
- **`marcus_reserved_for_sso`** - PARTIAL/PARTIAL across 2 run(s), 6.0 points forgone
  - releases the instrumentation - 'not a blocker, can be deprioritized' - but then spends his Monday afternoon on the Contoso patch and pushes the compatibility work into Tuesday
- **`monday_plan`** - PARTIAL across 1 run(s), 3.5 points forgone
  - starts with the migration and delegates Sarah's work in the morning, but loses the afternoon to the wrong engineer and double-books Julia at 15:00 for both the formatter and the compliance export
- **`pricing_dependency`** - PARTIAL/PARTIAL across 2 run(s), 5.0 points forgone
  - 'Packaging approval: Can be submitted with mockups, so no need to wait for live page' - the mockup route is there, but the response never states that approval gates the public page
- **`scarce_resource_allocation`** - FAIL/PARTIAL across 2 run(s), 15.0 points forgone
  - keeps the substitutable work on the contested engineer and rules the substitute out explicitly: '13:00 - Marcus starts contoso_permission_patch (2h)' and 'Daniel: available for support, but not needed on critical path', while Daniel's 3.5h offer sits unused in the sources

### What it got wrong (0)

No penalties and no false actions in any run.

### Raw evidence

- response: `runs/monday-003/deepseek-v4-flash/run-001.json`
- response: `runs/monday-003/deepseek-v4-flash/run-002.json`
- evaluation: `evaluations/evaluator-opus5-v0.3-calibration-3/monday-003/deepseek-v4-flash/run-001.json`
- evaluation: `evaluations/evaluator-opus5-v0.3-calibration-3/monday-003/deepseek-v4-flash/run-002.json`

---

## 6. Gemma 4 - 54.5 / 100

`gemma4`

| Dimension | Score | Max |
|---|---:|---:|
| Critical path and dependencies | 17.0 | 21 |
| Resource allocation | 9.5 | 25 |
| Planning and parallelization | 11.0 | 18 |
| Decision quality | 9.0 | 14 |
| State reconstruction | 8.0 | 10 |
| Accuracy and uncertainty | 7.0 | 12 |
| **Monday Score** | **54.5** | **100** |

**Runs:** 53.0, 56.0  (min 53.0, max 56.0, run_range 3.0, sigma 2.12)

**Latency and cost:** TTFA median 0.7s, TTFT median 0.7s, total median 6.7s, output tokens median 827.0, cost/run median -

### What it missed (12 criteria)

- **`concurrent_sso_and_contoso`** - PARTIAL/PARTIAL across 2 run(s), 7.0 points forgone
  - the format fix and the board work run in parallel, but the two engineering chains are effectively serialised through Marcus and the SSO patch is never scheduled
- **`earliest_feasible_delivery`** - FAIL/FAIL across 2 run(s), 6.0 points forgone
  - 'Enterprise SSO (Atlas): Wednesday EOD (Matches commitment)' - Tuesday 14:00 is reachable under its own dependency ordering, and no schedule is offered
- **`elena_migration_fallback`** - FAIL across 1 run(s), 5.0 points forgone
  - Elena's Wednesday departure, the permission transfer and the Daniel fallback are absent; the only Elena action is 'Ensure Elena starts the billing_schema_migration today'
- **`formatting_urgent_not_blocking`** - PARTIAL/PARTIAL across 2 run(s), 5.0 points forgone
  - the format work goes to Julia in parallel and displaces nothing, but the response never says the export is working or the request cosmetic
- **`marcus_reserved_for_sso`** - PARTIAL/PARTIAL across 2 run(s), 6.0 points forgone
  - takes him off the instrumentation but does not protect the capacity: the SSO compatibility patch is never assigned a slot anywhere in the plan
- **`monday_plan`** - PARTIAL/PARTIAL across 2 run(s), 7.0 points forgone
  - no times and the wrong order - the Marcus pivot is action 1 and starting the migration is action 4, filed under MONITOR
- **`scarce_resource_allocation`** - FAIL/FAIL across 2 run(s), 20.0 points forgone
  - 'Instruct Marcus to pivot from onboarding instrumentation to the contoso_permission_patch' - the contested engineer is put on the one item that has a substitute, and Daniel appears only as a 30-minute consultation
- **`security_state_stale`** - FAIL/FAIL across 2 run(s), 6.0 points forgone
  - reopens the closed gate: 'Check status of the Security Review for SSO. This is a listed task blocker that must be cleared before Wednesday' and 'if it is not cleared by Tuesday, the SSO rollout is at risk'. Maya's Friday 16:48 approval is never read
- **`sso_chain`** - PARTIAL across 1 run(s), 2.0 points forgone
  - 'Path A (SSO): Elena (Billing Migration: 3h) -> Backfill (1.5h) -> Marcus (Compatibility Patch: 4h) -> QA (Regression: 2h) -> Marcus (Rollout: 1h)'. The four real steps are in order, but the backfill is inserted as a prerequisite of the compatibility patch; it gates only the board revenue charts, and the insertion adds 90 minutes to the path
- **`sso_state_reconstructed`** - PARTIAL/PARTIAL across 2 run(s), 4.0 points forgone
  - chain outstanding and Wednesday intact, but Security is reported as unknown when it is closed
- **`stale_task_list_overridden`** - PARTIAL/PARTIAL across 2 run(s), 5.0 points forgone
  - instrumentation and the pricing order are corrected; Security is re-raised as an open gate and the Contoso task is only partly updated
- **`uncertainty_discipline`** - PARTIAL/PARTIAL across 2 run(s), 4.0 points forgone
  - no inventions, and the resource risk is named accurately, but it reports a settled fact as unknown: 'The status of the outstanding security review is unknown'

### What it got wrong (2)

- **PROHIBITED_ACTION** `PROHIBITED_ACTION` (-7.0)
  - Directs work against a gate the sources close: Maya's Friday 16:48 email states the review is approved for the current scope and that re-review is required only for authentication-flow changes. The response makes clearing it a Wednesday precondition for the rollout.
  - evidence: 'UNBLOCK (Immediate): Check status of the Security Review for SSO. This is a listed task blocker that must be cleared before Wednesday.'
- **PROHIBITED_ACTION** `PROHIBITED_ACTION` (-7.0)
  - Maya's Friday 16:48 email closes the review for the current scope and exempts permission-check and configuration fixes from re-review. The response directs work against a gate that is shut, and its risk section makes clearing it a condition of the Wednesday rollout.
  - evidence: 'UNBLOCK (Product): Identify the owner of the Security Review for SSO and force a resolution today.'

### Raw evidence

- response: `runs/monday-003/gemma4/run-001.json`
- response: `runs/monday-003/gemma4/run-002.json`
- evaluation: `evaluations/evaluator-opus5-v0.3-calibration-3/monday-003/gemma4/run-001.json`
- evaluation: `evaluations/evaluator-opus5-v0.3-calibration-3/monday-003/gemma4/run-002.json`

---

## 7. Qwen 3.6 - 41.5 / 100

`qwen3.6`

| Dimension | Score | Max |
|---|---:|---:|
| Critical path and dependencies | 12.5 | 21 |
| Resource allocation | 15.8 | 25 |
| Planning and parallelization | 10.0 | 18 |
| Decision quality | 9.0 | 14 |
| State reconstruction | 6.5 | 10 |
| Accuracy and uncertainty | 3.2 | 12 |
| **Monday Score** | **41.5** | **100** |

**Runs:** 43.0, 40.0  (min 40.0, max 43.0, run_range 3.0, sigma 2.12)

**Latency and cost:** TTFA median 1.2s, TTFT median 1.2s, total median 17.4s, output tokens median 1966.5, cost/run median -

### What it missed (17 criteria)

- **`concurrent_sso_and_contoso`** - PARTIAL/PARTIAL across 2 run(s), 7.0 points forgone
  - both chains do move - Daniel and Julia on Contoso while SSO proceeds - but the SSO sequencing collapses into overlapping Monday-afternoon slots
- **`contoso_blocker_chain`** - PARTIAL across 1 run(s), 3.0 points forgone
  - 'Secondary Critical Path: Contoso Compliance Export' gets the permission fix and the file generation in order, but then couples the formatter to the delivery: 'Date Format Fix (Julia) is independent but must be combined with the permission fix for the final file'
- **`contoso_state_separated`** - PARTIAL/PARTIAL across 2 run(s), 3.0 points forgone
  - rescored under the 0.3 definition and still short of it: the two items get different owners and only the export carries the contractual date, but the plan opens with a single '09:00-10:30: Unblock Contoso (Highest Business Risk)' block that assigns both fixes under one 'contractual deadline' justification, leaving which one threatens Tuesday ambiguous at the point of decision
- **`earliest_feasible_delivery`** - FAIL/FAIL across 2 run(s), 6.0 points forgone
  - 'Earliest Realistic Completion: Wednesday Morning (if Monday slips) or Tuesday EOD (if Monday goes perfectly)' - hedged onto Wednesday, and the Tuesday variant rests on a Monday schedule in which the compatibility patch and the migration run at the same time
- **`elena_migration_fallback`** - PARTIAL across 1 run(s), 2.5 points forgone
  - has the transfer and the fallback but misdates the window: 'schedule a 30-min slot for Tuesday morning before her 12:00 cutoff' - the cutoff is Wednesday 12:00
- **`factual_plan_accuracy`** - FAIL/PARTIAL across 2 run(s), 7.5 points forgone
  - two substitutions, one of them load-bearing. 'Marcus is unavailable Monday 09:00-13:00 (Atlas session)' contradicts availability.csv and Marcus's own message, and the whole Monday plan is built on it; 'a 30-min slot for Tuesday morning before her 12:00 cutoff' moves Elena's Wednesday-noon departure to Tuesday
- **`formatting_urgent_not_blocking`** - PARTIAL/PARTIAL across 2 run(s), 5.0 points forgone
  - 'Contoso Date Format (Julia): Can start immediately today. Independent of SSO' - kept off the committed work, but never characterised as a preference against a working export
- **`marcus_reserved_for_sso`** - PARTIAL/PARTIAL across 2 run(s), 6.0 points forgone
  - names the constraint - 'Marcus's unique code ownership' - and defers the instrumentation, but spends the analysis considering whether to delay the migration to keep Marcus free 'for Contoso support if needed'
- **`monday_plan`** - PARTIAL/PARTIAL across 2 run(s), 7.0 points forgone
  - the morning is spent deliberating rather than starting: the migration is pushed to 13:00 after an explicit reversal, and the reasoning for the delay rests on a Monday absence that does not exist
- **`pricing_board_parallel`** - PARTIAL across 1 run(s), 2.0 points forgone
  - Sarah gets the board non-revenue work, but the entire pricing workstream is missing from the parallel plan
- **`pricing_dependency`** - PARTIAL/FAIL across 2 run(s), 7.5 points forgone
  - 'Prepare the submission pack (margin, structure, mockups)' and 'Pricing Page Public Launch: Blocked by Packaging Approval' - but it also directs 'Ensure it is built so she can take screenshots for Priya's committee', keeping the page-first order it just contradicted
- **`scarce_resource_allocation`** - PARTIAL/PARTIAL across 2 run(s), 10.0 points forgone
  - makes the right assignment - 'Assign Daniel to fix the delegated admin permission check (3.5 hours)... Daniel needs 30 mins with Marcus' - but justifies it only as workstream separation, and then contradicts it in the risks by listing 'Contoso Permission Fix (2h)' among Marcus's load
- **`security_state_stale`** - PARTIAL/FAIL across 2 run(s), 4.5 points forgone
  - sees both records and refuses to resolve them: 'This is a contradiction. Unknown: Is the security review actually closed in the system? If not, it may block the SSO rollout checklist. Action: Verify with Noah or Maya'
- **`sso_chain`** - PARTIAL across 1 run(s), 2.0 points forgone
  - the SSO steps are in order - migration, compatibility patch, QA regression, production rollout - but the chain is headed by a step that does not exist: '1. Monday AM: Product unblocks Security Review (Prerequisite for SSO)'
- **`sso_state_reconstructed`** - PARTIAL/PARTIAL across 2 run(s), 4.0 points forgone
  - the chain and the Wednesday commitment are right; Security is left unresolved
- **`stale_task_list_overridden`** - PARTIAL/PARTIAL across 2 run(s), 5.0 points forgone
  - defers the instrumentation and moves launch support to Julia, but leaves Security open and keeps the page-before-approval order
- **`uncertainty_discipline`** - PARTIAL/PARTIAL across 2 run(s), 4.0 points forgone
  - the risk section is otherwise honest, but the plan is built on an availability constraint the response invented and then treated as fact

### What it got wrong (5)

- **MATERIAL_HALLUCINATION** `MATERIAL_HALLUCINATION` (-5.0)
  - The Atlas pre-rollout session is Tuesday only, in both Marcus's Monday 08:29 message and availability.csv, which shows him available 09:00-17:30 on Monday. The invented Monday absence is asserted as fact and drives the decision to push the migration to 13:00.
  - evidence: 'Constraint: Marcus is unavailable Monday 09:00-13:00 (Atlas session) and Tuesday 09:00-13:00 (Atlas session).'
- **MAJOR_PLANNING_ERROR** `MAJOR_PLANNING_ERROR` (-7.0)
  - The recommended plan starts the compatibility patch at the same moment as the three-hour migration it depends on. Marcus's own Friday statement is that he cannot finish the compatibility work until the migration lands.
  - evidence: 'Direct Elena to start Migration Monday 13:00' together with 'if Elena starts migration Mon 13:00, Marcus patches Mon PM' and 'Marcus can do the patch Monday afternoon (13:00-17:00 is 4.5 hours, enough for 4h work + handoff)'.
- **MAJOR_CONTRADICTION** `MAJOR_CONTRADICTION` (-5.0)
  - Both the Monday start and the Tuesday start are directed in the same response, and the downstream board-pack plan is built on the Tuesday one. A reader cannot tell which instruction to follow.
  - evidence: 'Direct Elena to start Migration Monday 13:00' against 'Since we are pushing migration to Tuesday, the revenue charts are blocked until Wednesday' and 'If migration lands Tuesday, backfill runs Tuesday PM, charts ready Wednesday'.
- **PROHIBITED_ACTION** `PROHIBITED_ACTION` (-7.0)
  - Maya's Friday 16:48 email closes the review for the current scope. The response makes clearing it the first hour of the day and the first step of its critical path, spending the morning on a gate that is already open.
  - evidence: '09:10 - 10:00: Unblock Security Review (SSO). Contact Maya (Security) immediately... Get written confirmation or a quick Slack approval to remove the outstanding status. Why: This is a hard blocker for the SSO release checklist.'
- **MAJOR_PLANNING_ERROR** `MAJOR_PLANNING_ERROR` (-7.0)
  - The permission patch is scheduled to start, finish and be handed to Julia before the schema migration it depends on has landed. Marcus states in #support-escalations that the patch sits on the same account-mapping layer and can only go in after the migration.
  - evidence: 'Daniel: contoso_permission_patch (2.5 hrs effective). Starts after Marcus handoff (~12:00)' and 'If Daniel finishes patch by 15:00 Monday, Julia can fix format and generate by 17:00 Monday', against 'Elena: billing_schema_migration (3 hrs). Starts ~13:00 Monday'.

### Raw evidence

- response: `runs/monday-003/qwen3.6/run-001.json`
- response: `runs/monday-003/qwen3.6/run-002.json`
- evaluation: `evaluations/evaluator-opus5-v0.3-calibration-3/monday-003/qwen3.6/run-001.json`
- evaluation: `evaluations/evaluator-opus5-v0.3-calibration-3/monday-003/qwen3.6/run-002.json`

---

## Reproducing this

```bash
mondaybench validate --scenario monday-003 \
    --evaluator evaluator-opus5-v0.3-calibration-3
mondaybench leaderboard --scenario monday-003 \
    --evaluator evaluator-opus5-v0.3-calibration-3 --official
```

Every input, raw response, judge verdict and scoring rule is in this repository. See `README.md` for the methodology.
