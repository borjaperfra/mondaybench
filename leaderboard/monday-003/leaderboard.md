# MondayBench 0.3 - `monday-003`

**Evaluator:** `evaluator-opus5-v0.3`  
**Rubric:** 0.3  
**Judge:** `claude-opus-5`  
**Prompt SHA-256:** `aaf788f309d955d2b427c86fe7d95d2bbf88575fde7306adcfd74b0ec4a4103f`  
**Generated:** 2026-08-28T20:57:26Z

**Status:** official v0.3 result. Every publication gate passed.

The Monday Score is the mean of each model's official runs and measures task quality only. TTFA, latency and cost sit beside it and are never folded into it.

| Rank | Model | Monday Score | Runs | Range | TTFA median | Total median |
|---:|---|---:|---:|---:|---:|---:|
| 1 | DeepSeek V4 Flash | **95.0** | 3 | 0.0 | 136.0s | 143.0s |
| 2 | Qwen 3.8 Flash | **94.5** | 3 | 11.5 | 309.3s | 327.2s |
| 3 | GLM 5.3 Flash | **92.8** | 3 | 19.0 | 120.8s | 145.9s |
| 4 | MIMO v2.5 | **90.3** | 3 | 11.5 | 139.1s | 167.8s |
| 5 | GLM 5.2 | **87.3** | 3 | 14.0 | 40.5s | 64.3s |
| 6 | Qwen 3.6 | **65.5** | 3 | 13.0 | 0.9s | 14.8s |
| 7 | Gemma 4 | **65.3** | 3 | 8.0 | 0.6s | 7.7s |

---

## 1. DeepSeek V4 Flash - 95.0 / 100

`deepseek-v4-flash`

| Dimension | Score | Max |
|---|---:|---:|
| Critical path and dependencies | 20.2 | 21 |
| Resource allocation | 20.8 | 25 |
| Planning and parallelization | 18.0 | 18 |
| Decision quality | 14.0 | 14 |
| State reconstruction | 10.0 | 10 |
| Accuracy and uncertainty | 12.0 | 12 |
| **Monday Score** | **95.0** | **100** |

**Runs:** 95.0, 95.0, 95.0  (min 95.0, max 95.0, run_range 0.0, sigma 0.00)

**Latency and cost:** TTFA median 136.0s, TTFT median 1.7s, total median 143.0s, output tokens median 21307.0, cost/run median $0.0080

### What it missed (2 criteria)

- **`elena_migration_fallback`** - PARTIAL/FAIL/FAIL across 3 run(s), 12.5 points forgone
  - 'Elena is out from Wednesday noon - the migration and backfill must happen before then. Our plan does this Monday' names the constraint and schedules around it, but the production-permission transfer and the Daniel fallback are absent
- **`pricing_dependency`** - PARTIAL across 1 run(s), 2.5 points forgone
  - has the mockup route - 'Use design mockups for the approval pack if available so she does not wait for live screenshots' - but never states that packaging approval gates the public page

### What it got wrong (0)

No penalties and no false actions in any run.

### Raw evidence

- response: `runs/monday-003/deepseek-v4-flash/run-001.json`
- response: `runs/monday-003/deepseek-v4-flash/run-002.json`
- response: `runs/monday-003/deepseek-v4-flash/run-003.json`
- evaluation: `evaluations/evaluator-opus5-v0.3/monday-003/deepseek-v4-flash/run-001.json`
- evaluation: `evaluations/evaluator-opus5-v0.3/monday-003/deepseek-v4-flash/run-002.json`
- evaluation: `evaluations/evaluator-opus5-v0.3/monday-003/deepseek-v4-flash/run-003.json`

---

## 2. Qwen 3.8 Flash - 94.5 / 100

`qwen3.8-flash`

| Dimension | Score | Max |
|---|---:|---:|
| Critical path and dependencies | 21.0 | 21 |
| Resource allocation | 20.7 | 25 |
| Planning and parallelization | 16.8 | 18 |
| Decision quality | 14.0 | 14 |
| State reconstruction | 10.0 | 10 |
| Accuracy and uncertainty | 12.0 | 12 |
| **Monday Score** | **94.5** | **100** |

**Runs:** 95.0, 100.0, 88.5  (min 88.5, max 100.0, run_range 11.5, sigma 5.77)

**Latency and cost:** TTFA median 309.3s, TTFT median 6.8s, total median 327.2s, output tokens median 36111.0, cost/run median -

### What it missed (4 criteria)

- **`concurrent_sso_and_contoso`** - PARTIAL across 1 run(s), 3.5 points forgone
  - Julia's export does overlap Marcus's SSO work, but the two engineering items run one after the other through one person: permission patch 12:10-14:10, compatibility patch from 14:10
- **`elena_migration_fallback`** - FAIL across 1 run(s), 5.0 points forgone
  - Elena's Wednesday-noon departure, the production-permission transfer and the Daniel migration fallback appear nowhere - not in the plan, not in the blocker table, and not in ten numbered risks
- **`marcus_reserved_for_sso`** - PARTIAL across 1 run(s), 3.0 points forgone
  - states the ground - 'Only Marcus can do it' - and releases the instrumentation, but the capacity that frees goes to the substitutable Contoso patch, which moves the rollout from an achievable Tuesday afternoon to 16:40
- **`scarce_resource_allocation`** - PARTIAL across 1 run(s), 5.0 points forgone
  - detects the contention outright - 'Marcus is the only person who can do the SSO compatibility patch, and he is also fastest on the Contoso permission patch' - and resolves it by sequencing him through both, on a reason that covers the order rather than the ownership: 'This is the fastest path to the Tuesday 16:00 contractual export'. Daniel is held as the billing backup only, never considered for the permission patch, and the compatibility work is pushed to 14:10 as a result

### What it got wrong (0)

No penalties and no false actions in any run.

### Raw evidence

- response: `runs/monday-003/qwen3.8-flash/run-001.json`
- response: `runs/monday-003/qwen3.8-flash/run-002.json`
- response: `runs/monday-003/qwen3.8-flash/run-007.json`
- evaluation: `evaluations/evaluator-opus5-v0.3/monday-003/qwen3.8-flash/run-001.json`
- evaluation: `evaluations/evaluator-opus5-v0.3/monday-003/qwen3.8-flash/run-002.json`
- evaluation: `evaluations/evaluator-opus5-v0.3/monday-003/qwen3.8-flash/run-007.json`

---

## 3. GLM 5.3 Flash - 92.8 / 100

`glm5.3-flash`

| Dimension | Score | Max |
|---|---:|---:|
| Critical path and dependencies | 21.0 | 21 |
| Resource allocation | 22.3 | 25 |
| Planning and parallelization | 16.8 | 18 |
| Decision quality | 13.2 | 14 |
| State reconstruction | 10.0 | 10 |
| Accuracy and uncertainty | 9.5 | 12 |
| **Monday Score** | **92.8** | **100** |

**Runs:** 97.5, 81.0, 100.0  (min 81.0, max 100.0, run_range 19.0, sigma 10.32)

**Latency and cost:** TTFA median 120.8s, TTFT median 2.1s, total median 145.9s, output tokens median 7349.0, cost/run median -

### What it missed (5 criteria)

- **`concurrent_sso_and_contoso`** - PARTIAL across 1 run(s), 3.5 points forgone
  - 'permission patch 12:00-14:00, then compatibility patch 14:00-17:30 + Tue 13:00-13:30' - the two chains run one after the other through one person
- **`factual_plan_accuracy`** - PARTIAL/FAIL across 2 run(s), 7.5 points forgone
  - one substitution: 'Pricing page public: Wed (deadline Wed 17:00)'. The page is due Thursday 17:00. Everything else it uses is right, and the plan does not move on the correction
- **`formatting_urgent_not_blocking`** - PARTIAL across 1 run(s), 2.5 points forgone
  - keeps the formatter with Julia and off the dated chain - Chain A contains only the permission patch - but never characterises the format request as cosmetic or the export as working
- **`marcus_reserved_for_sso`** - PARTIAL across 1 run(s), 3.0 points forgone
  - 'Release the instrumentation hold' and 'only Marcus knows the account-mapping branch', but the freed capacity goes to the Contoso patch at 12:00-14:00
- **`scarce_resource_allocation`** - PARTIAL across 1 run(s), 5.0 points forgone
  - detects it - 'Marcus is the shared resource across both chains' - and prices the substitute as a contingency: 'if Marcus slips, Daniel takes the permission patch (3.5h + 0.5h Marcus walkthrough)'. But the substitutable work stays with Marcus and the only reason offered is the ordering one, 'earlier external deadline'; why Marcus rather than Daniel is never argued, and the rollout moves out to 15:30-16:30

### What it got wrong (0)

No penalties and no false actions in any run.

### Raw evidence

- response: `runs/monday-003/glm5.3-flash/run-001.json`
- response: `runs/monday-003/glm5.3-flash/run-002.json`
- response: `runs/monday-003/glm5.3-flash/run-003.json`
- evaluation: `evaluations/evaluator-opus5-v0.3/monday-003/glm5.3-flash/run-001.json`
- evaluation: `evaluations/evaluator-opus5-v0.3/monday-003/glm5.3-flash/run-002.json`
- evaluation: `evaluations/evaluator-opus5-v0.3/monday-003/glm5.3-flash/run-003.json`

---

## 4. MIMO v2.5 - 90.3 / 100

`mimo-v2.5`

| Dimension | Score | Max |
|---|---:|---:|
| Critical path and dependencies | 18.5 | 21 |
| Resource allocation | 22.3 | 25 |
| Planning and parallelization | 16.8 | 18 |
| Decision quality | 12.3 | 14 |
| State reconstruction | 10.0 | 10 |
| Accuracy and uncertainty | 10.3 | 12 |
| **Monday Score** | **90.3** | **100** |

**Runs:** 92.5, 95.0, 83.5  (min 83.5, max 95.0, run_range 11.5, sigma 6.05)

**Latency and cost:** TTFA median 139.1s, TTFT median 3.0s, total median 167.8s, output tokens median 15785.0, cost/run median -

### What it missed (6 criteria)

- **`concurrent_sso_and_contoso`** - PARTIAL across 1 run(s), 3.5 points forgone
  - 'I am placing the Contoso permission patch first' - the two chains run through Marcus one after the other while Daniel is free
- **`factual_plan_accuracy`** - FAIL across 1 run(s), 5.0 points forgone
  - two substituted deadlines, both used to compute the buffers it reports: 'Billing schema migration | 3h | Wed 15:00' - the stated deadline is Thursday 15:00 - and 'Packaging page build | Wed EOD' with 'Pricing page live | Wed AM | Wed EOD', where the page is due Thursday 17:00
- **`formatting_urgent_not_blocking`** - PARTIAL/PARTIAL across 2 run(s), 5.0 points forgone
  - handles the formatter correctly - Julia, 2h, independent, 'Decouples the date fix from the permission fix' - but never states that the reported breakage is cosmetic or that the file imports
- **`marcus_reserved_for_sso`** - PARTIAL across 1 run(s), 3.0 points forgone
  - declares the instrumentation not launch-blocking but then schedules Marcus on it 09:15-12:15 as 'fill work', and hands him the substitutable Contoso patch as well
- **`pricing_dependency`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 7.5 points forgone
  - 'Page can't go public until approval clears, but build can start' gives the gate, but the plan is 'pricing page now -> approval pack' and the mockup route is never used
- **`scarce_resource_allocation`** - PARTIAL across 1 run(s), 5.0 points forgone
  - detects it - 'Marcus is the shared resource between the Contoso permission patch and the SSO compatibility patch' - and gives a reason for the order, 'its deadline has less float'. But Daniel is used only as the migration backup, never considered for the patch, and the ownership choice is never argued

### What it got wrong (0)

No penalties and no false actions in any run.

### Raw evidence

- response: `runs/monday-003/mimo-v2.5/run-001.json`
- response: `runs/monday-003/mimo-v2.5/run-002.json`
- response: `runs/monday-003/mimo-v2.5/run-003.json`
- evaluation: `evaluations/evaluator-opus5-v0.3/monday-003/mimo-v2.5/run-001.json`
- evaluation: `evaluations/evaluator-opus5-v0.3/monday-003/mimo-v2.5/run-002.json`
- evaluation: `evaluations/evaluator-opus5-v0.3/monday-003/mimo-v2.5/run-003.json`

---

## 5. GLM 5.2 - 87.3 / 100

`glm5.2`

| Dimension | Score | Max |
|---|---:|---:|
| Critical path and dependencies | 17.8 | 21 |
| Resource allocation | 19.7 | 25 |
| Planning and parallelization | 15.7 | 18 |
| Decision quality | 14.0 | 14 |
| State reconstruction | 10.0 | 10 |
| Accuracy and uncertainty | 10.2 | 12 |
| **Monday Score** | **87.3** | **100** |

**Runs:** 86.0, 95.0, 81.0  (min 81.0, max 95.0, run_range 14.0, sigma 7.09)

**Latency and cost:** TTFA median 40.5s, TTFT median 1.9s, total median 64.3s, output tokens median 4420.0, cost/run median $0.0120

### What it missed (7 criteria)

- **`concurrent_sso_and_contoso`** - PARTIAL/PARTIAL across 2 run(s), 7.0 points forgone
  - '12:30-14:30: contoso_permission_patch (2h)... 14:30-17:30: begin API compatibility patch' - the two chains are serialised through one person
- **`earliest_feasible_delivery`** - FAIL across 1 run(s), 3.0 points forgone
  - 'SSO production rollout: Wed 09:00-10:00 (Tue evening too tight given Marcus's 13:00 start; Wed morning is clean)' and 'Enterprise SSO delivered: Wed ~10:00'. Tuesday 14:00 is reachable; the answer key does not credit Wednesday presented as the earliest when Tuesday is available. The Wednesday is a consequence of its own allocation, which is priced separately
- **`factual_plan_accuracy`** - PARTIAL across 1 run(s), 2.5 points forgone
  - one substitution: the delivery table reads 'Billing migration + backfill | Wed 15:00'. The stated external deadline is Thursday 2026-09-24 15:00. Its own plan lands the migration Monday, so nothing downstream moves
- **`marcus_reserved_for_sso`** - PARTIAL/PARTIAL across 2 run(s), 6.0 points forgone
  - 'Marcus's 3h held capacity is released to SSO' and 'Nobody else knows the account-mapping branch', but the freed capacity then goes to the Contoso patch and pushes the compatibility work into Tuesday
- **`pricing_dependency`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 7.5 points forgone
  - 'pricing_page public | packaging committee approval' gives the gate, but the pack is scheduled for 'Tuesday morning' after the page is built and Priya's mockup line is never used
- **`scarce_resource_allocation`** - PARTIAL/PARTIAL across 2 run(s), 10.0 points forgone
  - recognises the contention - 'Marcus is the single point of failure for SSO compat patch, contoso_permission_patch, and SSO rollout' - but never engages the substitute for the substitutable item: Daniel appears only as the migration backup, and the stated reason is 'his module, fastest path' rather than a comparison
- **`sso_chain`** - PARTIAL across 1 run(s), 2.0 points forgone
  - the four SSO steps are in order, but the chain is written as 'billing_schema_migration -> billing_backfill -> api_compatibility_patch -> ...', inserting the backfill as a prerequisite of the patch. The dependency table below it says the patch is blocked by the migration alone, so the response contradicts itself on the point

### What it got wrong (0)

No penalties and no false actions in any run.

### Raw evidence

- response: `runs/monday-003/glm5.2/run-001.json`
- response: `runs/monday-003/glm5.2/run-002.json`
- response: `runs/monday-003/glm5.2/run-003.json`
- evaluation: `evaluations/evaluator-opus5-v0.3/monday-003/glm5.2/run-001.json`
- evaluation: `evaluations/evaluator-opus5-v0.3/monday-003/glm5.2/run-002.json`
- evaluation: `evaluations/evaluator-opus5-v0.3/monday-003/glm5.2/run-003.json`

---

## 6. Qwen 3.6 - 65.5 / 100

`qwen3.6`

| Dimension | Score | Max |
|---|---:|---:|
| Critical path and dependencies | 14.3 | 21 |
| Resource allocation | 20.5 | 25 |
| Planning and parallelization | 13.3 | 18 |
| Decision quality | 9.0 | 14 |
| State reconstruction | 8.2 | 10 |
| Accuracy and uncertainty | 4.2 | 12 |
| **Monday Score** | **65.5** | **100** |

**Runs:** 64.5, 59.5, 72.5  (min 59.5, max 72.5, run_range 13.0, sigma 6.56)

**Latency and cost:** TTFA median 0.9s, TTFT median 0.9s, total median 14.8s, output tokens median 1872.0, cost/run median -

### What it missed (14 criteria)

- **`board_dependency`** - FAIL/PARTIAL across 2 run(s), 4.5 points forgone
  - the backfill appears nowhere; the board revenue dependency is not raised at all
- **`concurrent_sso_and_contoso`** - PARTIAL/PARTIAL across 2 run(s), 7.0 points forgone
  - Daniel and Julia do work the Contoso chain while SSO waits, but the SSO patch is deferred to 'Tue PM/Wed AM' rather than run alongside
- **`earliest_feasible_delivery`** - FAIL/FAIL/PARTIAL across 3 run(s), 7.5 points forgone
  - 'Enterprise SSO (Atlas): Monday EOD... Rollout at 18:00+.' Ten hours of dependent work cannot fit into Monday from 09:10, and the fallback offered, 'Tuesday morning', is a window in which the rollout owner is in the Atlas session
- **`elena_migration_fallback`** - PARTIAL/FAIL across 2 run(s), 7.5 points forgone
  - 'She is available until 12:00 Wednesday, but doing it Monday clears the path' names the constraint, but the production-permission transfer and the Daniel fallback are missing
- **`factual_plan_accuracy`** - FAIL/FAIL across 2 run(s), 10.0 points forgone
  - two substitutions. 'Marcus still needs 2h to walk Daniel through the delegated-admin path' - the walkthrough is 30 minutes, as the same response says twice elsewhere. And the delivery arithmetic runs QA to 18:00 on a Monday when the QA window closes at 17:30
- **`formatting_urgent_not_blocking`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 7.5 points forgone
  - 'Independent of backend permission fixes. Can be done Monday' keeps it off the committed work, but the response never characterises it as a preference against a working export
- **`marcus_reserved_for_sso`** - PARTIAL/PARTIAL across 2 run(s), 6.0 points forgone
  - keeps Marcus on the SSO work and cites 'Marcus's specific code ownership', but never releases the three hours he is holding for the instrumentation
- **`monday_plan`** - PARTIAL/PARTIAL across 2 run(s), 7.0 points forgone
  - the handoff sequencing contradicts itself - Daniel is told to work 13:00-17:30 while the Marcus walkthrough is described as 'likely sequential' after the four-hour patch
- **`onboarding_state_reconstructed`** - PARTIAL across 1 run(s), 1.5 points forgone
  - 'The task list says Marcus owns onboarding launch support. Julia owns the flow' gets the ownership move, but the instrumentation status is never stated
- **`pricing_dependency`** - FAIL/PARTIAL/FAIL across 3 run(s), 12.5 points forgone
  - 'Packaging Approval Pack (Sarah): 1.5 hours. Independent.' Neither half is addressed: no gate on the public page and no use of the mockup allowance
- **`security_state_stale`** - PARTIAL/PARTIAL across 2 run(s), 3.0 points forgone
  - 'Assume approved... but Noah/Product must confirm with Maya if there is any ambiguity', and the risk section still asks whether the patch touches the auth flow
- **`sso_state_reconstructed`** - PARTIAL/PARTIAL across 2 run(s), 4.0 points forgone
  - the chain and the Wednesday commitment are right; Security is left unresolved
- **`stale_task_list_overridden`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 7.5 points forgone
  - the Contoso ticket is split into its two real items, but Security is left as something to confirm, the instrumentation is not addressed, and the pricing entry is untouched
- **`uncertainty_discipline`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 6.0 points forgone
  - the risk section is otherwise sound, but the plan rests on an invented two-hour walkthrough that the same response contradicts

### What it got wrong (2)

- **MATERIAL_HALLUCINATION** `MATERIAL_HALLUCINATION` (-5.0)
  - Anja's Monday 07:52 email states that only the tenant owner account can produce the export and that she is on leave until October. The response offers that account as the fallback for a contractual Tuesday 16:00 delivery without the fact that removes it, and additionally attributes Rachel's line to Julia.
  - evidence: 'If the permission patch isn't done by Monday EOD, Julia can still generate the file using the tenant owner account (as per her earlier note: "Their tenant owner account works").'
- **MAJOR_PLANNING_ERROR** `MAJOR_PLANNING_ERROR` (-7.0)
  - The permission patch is scheduled to start at 10:00 and finish at 13:30, overlapping the schema migration it depends on. Marcus states in #support-escalations that the patch sits on the same account-mapping layer and can only go in after the migration lands; this run never records that dependency.
  - evidence: 'Contoso Sync: Daniel needs 3.5h. If Marcus syncs with Daniel at 09:30, Daniel can work 10:00-13:30. This works.' against 'Elena finishes migration ~12:30-13:30. Marcus can start patch ~13:30.'

### Raw evidence

- response: `runs/monday-003/qwen3.6/run-001.json`
- response: `runs/monday-003/qwen3.6/run-002.json`
- response: `runs/monday-003/qwen3.6/run-003.json`
- evaluation: `evaluations/evaluator-opus5-v0.3/monday-003/qwen3.6/run-001.json`
- evaluation: `evaluations/evaluator-opus5-v0.3/monday-003/qwen3.6/run-002.json`
- evaluation: `evaluations/evaluator-opus5-v0.3/monday-003/qwen3.6/run-003.json`

---

## 7. Gemma 4 - 65.3 / 100

`gemma4`

| Dimension | Score | Max |
|---|---:|---:|
| Critical path and dependencies | 14.5 | 21 |
| Resource allocation | 19.0 | 25 |
| Planning and parallelization | 12.2 | 18 |
| Decision quality | 9.3 | 14 |
| State reconstruction | 8.0 | 10 |
| Accuracy and uncertainty | 7.0 | 12 |
| **Monday Score** | **65.3** | **100** |

**Runs:** 70.0, 64.0, 62.0  (min 62.0, max 70.0, run_range 8.0, sigma 4.16)

**Latency and cost:** TTFA median 0.6s, TTFT median 0.6s, total median 7.7s, output tokens median 878.0, cost/run median -

### What it missed (13 criteria)

- **`concurrent_sso_and_contoso`** - PARTIAL/PARTIAL across 2 run(s), 7.0 points forgone
  - Marcus is given the permission patch and then the compatibility patch, so the two chains run one after the other
- **`contoso_compliance_is_urgent`** - PARTIAL/PARTIAL across 2 run(s), 4.0 points forgone
  - 'ensure Contoso's Tuesday deadline is met' and 'Contoso Compliance Export: Tuesday afternoon' - the commitment is named but left undated, and its own estimate could fall after 16:00
- **`earliest_feasible_delivery`** - FAIL/FAIL/FAIL across 3 run(s), 9.0 points forgone
  - 'Enterprise SSO (Atlas): Wednesday EOD (Meeting the commitment, provided Marcus has the 4 hours for the patch and 2 hours for QA/Rollout after Elena lands the migration).' Tuesday 14:00 is reachable under its own ordering, and no schedule is offered
- **`formatting_urgent_not_blocking`** - PARTIAL across 1 run(s), 2.5 points forgone
  - the fix goes to Julia in parallel and displaces nothing, but 'low-complexity task for a high-value account' stops short of saying the export works or the request is cosmetic
- **`marcus_reserved_for_sso`** - PARTIAL across 1 run(s), 3.0 points forgone
  - takes him off the instrumentation but hands him the substitutable Contoso work, so the capacity freed does not go to the work only he can do
- **`monday_plan`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 10.5 points forgone
  - five ordered instructions but no clock times, and the reassignment is action 1 while starting the migration is action 4
- **`pricing_dependency`** - FAIL/PARTIAL/PARTIAL across 3 run(s), 10.0 points forgone
  - pricing appears only as 'Ensure she is working on the pricing_page and packaging_approval_pack to hit the 12:00 committee cutoff tomorrow'. No approval gate on the public page, and no use of the mockup allowance
- **`scarce_resource_allocation`** - FAIL/PARTIAL across 2 run(s), 15.0 points forgone
  - 'Direct Marcus to stop working on onboarding instrumentation and prioritize the contoso_permission_patch' - the contested engineer keeps the one item that has a substitute, and Daniel does not appear anywhere in the plan
- **`security_state_stale`** - FAIL/PARTIAL/FAIL across 3 run(s), 7.5 points forgone
  - reopens the closed gate: 'Check the status of the Security Review mentioned in Friday's notes. If it is still outstanding, I must escalate/resolve it to prevent a late-week stall', with the risk section reporting the status as unknown
- **`sso_chain`** - PARTIAL across 1 run(s), 2.0 points forgone
  - the four SSO steps are in order, but the chain reads 'Elena: Billing schema migration (3h) -> Elena: Reconciliation backfill (1.5h) -> Marcus: Contoso permission patch AND SSO compatibility patch -> QA -> Marcus rollout', and the blocker list repeats it: 'SSO Compatibility Patch: Blocked by Elena's schema migration and backfill'. The backfill gates the board revenue charts, not the patch, and the insertion adds 90 minutes to the path
- **`sso_state_reconstructed`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 6.0 points forgone
  - chain outstanding and Wednesday intact, but Security is reported as unknown when it is closed
- **`stale_task_list_overridden`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 7.5 points forgone
  - the instrumentation is cleared and the Contoso ticket split, but Security is re-raised as an open gate and the pricing entry is untouched
- **`uncertainty_discipline`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 6.0 points forgone
  - the resource risk is named accurately, but a settled fact is filed as unknown: 'The status of the outstanding security review for SSO is unknown'

### What it got wrong (2)

- **PROHIBITED_ACTION** `PROHIBITED_ACTION` (-7.0)
  - Maya's Friday 16:48 email closes the review for the current scope and exempts permission-check and configuration fixes from re-review. The response directs work against a gate that is shut and, in the risks, makes clearing it a condition of the rollout.
  - evidence: 'Unblock SSO (Immediate): Check the status of the Security Review mentioned in Friday's notes. If it is still outstanding, I must escalate/resolve it to prevent a late-week stall.'
- **PROHIBITED_ACTION** `PROHIBITED_ACTION` (-7.0)
  - Maya's Friday 16:48 email closes the review for the current scope. The response directs work against a gate that is shut and reports its status as unknown in the risks, spending product time on a precondition that has already been met.
  - evidence: 'Unblock SSO (Immediate): Check the status of the Security Review on the release checklist. If it is still outstanding, I must resolve this to prevent a late-week stall.'

### Raw evidence

- response: `runs/monday-003/gemma4/run-001.json`
- response: `runs/monday-003/gemma4/run-002.json`
- response: `runs/monday-003/gemma4/run-003.json`
- evaluation: `evaluations/evaluator-opus5-v0.3/monday-003/gemma4/run-001.json`
- evaluation: `evaluations/evaluator-opus5-v0.3/monday-003/gemma4/run-002.json`
- evaluation: `evaluations/evaluator-opus5-v0.3/monday-003/gemma4/run-003.json`

---

## Reproducing this

```bash
mondaybench validate --scenario monday-003 \
    --evaluator evaluator-opus5-v0.3
mondaybench leaderboard --scenario monday-003 \
    --evaluator evaluator-opus5-v0.3 --official
```

Every input, raw response, judge verdict and scoring rule is in this repository. See `README.md` for the methodology.
