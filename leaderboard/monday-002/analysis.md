# MondayBench #002 — Moving Targets: official analysis

Scenario `monday-002` v0.2 · evaluator `evaluator-opus5-v0.2` · judge `claude-opus-5` · prompt `740e627cbc7413c3…`

Seven models, three official runs each (21 runs). Monday Score is the mean of the three. Quality, speed and cost are reported separately and never combined.

## Ranking

| # | Model | Monday Score | Runs | Min | Max | Range | Stddev |
|---:|---|---:|---|---:|---:|---:|---:|
| 1 | Qwen 3.8 Flash | **94.8** | 93.0 / 100.0 / 91.5 | 91.5 | 100.0 | 8.5 | 4.54 |
| 2 | GLM 5.2 | **91.2** | 90.5 / 87.5 / 95.5 | 87.5 | 95.5 | 8.0 | 4.04 |
| 3 | DeepSeek V4 Flash | **89.3** | 97.5 / 86.5 / 84.0 | 84.0 | 97.5 | 13.5 | 7.18 |
| 4 | GLM 5.3 Flash | **87.3** | 85.0 / 85.5 / 91.5 | 85.0 | 91.5 | 6.5 | 3.62 |
| 5 | MIMO v2.5 | **81.2** | 64.5 / 81.5 / 97.5 | 64.5 | 97.5 | 33.0 | 16.50 |
| 6 | Qwen 3.6 | **70.2** | 75.5 / 83.0 / 52.0 | 52.0 | 83.0 | 31.0 | 16.17 |
| 7 | Gemma 4 | **54.2** | 58.0 / 45.5 / 59.0 | 45.5 | 59.0 | 13.5 | 7.52 |

Spread 54.2 – 94.8 = **40.7 points**.

## Consistency

| Model | Range | Stddev |
|---|---:|---:|
| GLM 5.3 Flash | 6.5 | 3.62 |
| GLM 5.2 | 8.0 | 4.04 |
| Qwen 3.8 Flash | 8.5 | 4.54 |
| DeepSeek V4 Flash | 13.5 | 7.18 |
| Gemma 4 | 13.5 | 7.52 |
| Qwen 3.6 | 31.0 | 16.17 |
| MIMO v2.5 | 33.0 | 16.50 |

Most consistent: **GLM 5.3 Flash** (range 6.5). Least: **MIMO v2.5** (range 33.0).

## Constant criteria

**5 of 20 criteria return the same label in all 21 runs, worth 26.0 of 100 points.** 74.0 points discriminate.

| Reference | Constant point mass |
|---|---:|
| v0.1 calibration (4 models, 21 criteria) | 75.5 |
| v0.2 calibration (4 models, 20 criteria) | 37.0 |
| **v0.2 official (7 models, 20 criteria)** | **26.0** |

Constant across every run:

- `stale_external_actions` (5 pts) — always PASS
- `current_owners` (5 pts) — always PASS
- `pricing_authority` (5 pts) — always PASS
- `immediate_release_decision` (6 pts) — always PASS
- `orion_missing_evidence` (5 pts) — always PASS

Same modal label for every model, but not identical in every run (these move with run-to-run variance rather than with capability):

- `choose_option_b` (8 pts)
- `parallelize_work` (4 pts)
- `avoid_acme_false_positive` (4 pts)
- `causal_boundary` (3 pts)
- `no_unsupported_causality` (2 pts)

## Most discriminative criteria

Gap between the best and worst model's mean earned points on that criterion.

| Criterion | Points | Spread | Dimension |
|---|---:|---:|---|
| `launch_state` | 5 | 5.00 | state_reconstruction |
| `schedule_feasibility` | 6 | 4.00 | planning_dependencies |
| `option_b_sequence` | 7 | 3.50 | planning_dependencies |
| `executive_gate_superseded` | 5 | 3.33 | temporal_supersession |
| `expansion_fully_reconciled` | 6 | 3.00 | cross_source_data_reasoning |
| `customer_signal_integration` | 6 | 3.00 | cross_source_data_reasoning |
| `ownership_supersession` | 5 | 2.50 | temporal_supersession |
| `globex_priority` | 5 | 2.50 | decision_prioritization |

## Dimension leaders

| Dimension | Max | Leader | Score |
|---|---:|---|---:|
| cross_source_data_reasoning | 15 | Qwen 3.8 Flash, GLM 5.2, DeepSeek V4 Flash, GLM 5.3 Flash | 15.0 |
| decision_prioritization | 20 | Qwen 3.8 Flash, GLM 5.2, DeepSeek V4 Flash, GLM 5.3 Flash | 20.0 |
| planning_dependencies | 25 | Qwen 3.8 Flash | 20.3 |
| state_reconstruction | 15 | Qwen 3.8 Flash, GLM 5.2, DeepSeek V4 Flash, GLM 5.3 Flash | 15.0 |
| temporal_supersession | 15 | Qwen 3.8 Flash, GLM 5.3 Flash | 15.0 |
| uncertainty_epistemic | 10 | GLM 5.2, DeepSeek V4 Flash | 10.0 |

## Failure stories

Each entry is a rubric criterion a model missed, quoted from the recorded evaluation evidence. Nothing here is inferred beyond the labels.

### Picked the riskier release path

`choose_option_b` (8 pts) — 17 miss(es).

- **Qwen 3.8 Flash run 1** (PARTIAL): chooses viable A and schedules it correctly; B is set aside because 'there is no evidence the 2.9.5 diff is already submitted', which the response itself files as a thing to verify rather than a settled constraint
- **Qwen 3.8 Flash run 3** (PARTIAL): chooses A, which is viable and correctly scheduled; B is set aside because a diff submitted before 09:15 'is not evidenced', which names the right unlocking condition but treats submitting it as outside the user's control
- **GLM 5.2 run 1** (PARTIAL): chooses A, which is viable and correctly scheduled; B is set aside because 'the 2.9.5 diff is already submitted' is 'not confirmed' - a defensible reading, but submitting it is an action the user could take at 09:07
- **GLM 5.2 run 2** (PARTIAL): chooses viable A and schedules it correctly, but the stated reason is false
- **DeepSeek V4 Flash run 2** (PARTIAL): chooses viable A and schedules it correctly, on a false claim about B
- **DeepSeek V4 Flash run 3** (PARTIAL): chooses viable A and schedules it correctly; no false global claim is made about B, but no risk comparison is offered either
- …and 11 more; see `criterion-matrix.md`.

### Lost the asynchronous delta review

`schedule_feasibility` (6 pts) — 17 miss(es).

- **Qwen 3.8 Flash run 1** (PARTIAL): every constraint is named and the A sequence is exact, but no B schedule is committed - it is deferred to MUST VERIFY
- **Qwen 3.8 Flash run 3** (PARTIAL): the B arithmetic is right for the anchor it picks - 'if Marcus submits the diff at his 09:15 start, review ends 09:40, then a 45-minute deploy would end 10:25' - and it identifies the crux ('B could only work if a diff is submitted before 09:15'), but no viable B schedule is committed
- **GLM 5.2 run 1** (PARTIAL): every constraint is identified, including the right review window ('Priya's 09:00-09:25 review'), but no B schedule is committed to
- **GLM 5.2 run 2** (FAIL): 'Option B cannot fit Marcus's 09:15-10:20 window after a required 25-min delta review (review + 45-min deploy > 65 min available)' - the review runs before Marcus arrives, so the deploy has 09:32-10:17
- **DeepSeek V4 Flash run 2** (FAIL): 'Priya's 09:35-10:25 gap plus Marcus leaving at 10:20 prevents completion before noon' - with the review in her 09:00-09:35 window the deploy runs 09:32-10:17 and rollout opens by 11:00
- **DeepSeek V4 Flash run 3** (FAIL): no B schedule is produced; 'B cannot meet the 12:00 Atlas window if started after 09:35' is true as stated but the 09:07 start is never considered
- …and 11 more; see `criterion-matrix.md`.

### Broke the release dependency chain

`option_b_sequence` (7 pts) — 9 miss(es).

- **DeepSeek V4 Flash run 2** (PARTIAL): 'Do not use 2.9.5-patch without a completed Security delta review' places the review before deploy, but the B chain is not carried through verification and Sam
- **DeepSeek V4 Flash run 3** (PARTIAL): 'B... requires 25m Security delta review before deploy' has the gate in the right place, but the chain is not carried through verification and Sam
- **GLM 5.3 Flash run 1** (PARTIAL): 'B needs a 25-min delta review first' and 'Don't deploy 2.9.5-patch before Priya's delta review completes' place the gate correctly, but verification and Sam are not carried into the B chain
- **GLM 5.3 Flash run 2** (PARTIAL): 'Don't deploy 2.9.5 (code change) without Priya's delta review' places the gate correctly; the B chain stops there
- **MIMO v2.5 run 1** (FAIL): no B chain is given; the contingency - 'fall to Option B with a delta review Monday afternoon' - is offered for a moment when Marcus, the only deployer, has already left
- **MIMO v2.5 run 2** (PARTIAL): 'Option B requires a 25-minute delta review before deploy' then '45-min deploy... post-deploy verification' has the order right; Sam's step is not carried into the B chain
- …and 3 more; see `criterion-matrix.md`.

### Left the €54k gap open

`expansion_fully_reconciled` (6 pts) — 5 miss(es).

- **MIMO v2.5 run 1** (PARTIAL): Wayne EUR18k, Globex EUR12k, Soylent EUR10k and Wonka EUR14k all appear, and 'Together these are the entire EUR24k unexplained gap', but the four are never closed against the EUR54k
- **Qwen 3.6 run 3** (PARTIAL): 'Explained (EUR30k): Wayne EUR18k; Globex EUR12k' and 'Remaining Gap (EUR24k)' are right, but the response concludes 'exact arithmetic requires full account file review' and never closes Soylent EUR10k + Wonka EUR14k
- **Gemma 4 run 1** (PARTIAL): 'EUR30k of the gap is explained by Wayne and Globex. The remaining EUR24k is driven by account-level reductions (Soylent, Wonka, Acme)' - the split is right but Acme's expansion is unchanged at zero, so the EUR24k attribution never closes
- **Gemma 4 run 2** (PARTIAL): 'Wayne/Globex EUR30k slip; Soylent/Wonka/Acme EUR24k reduction' - the EUR24k figure is right but Acme contributes nothing to it, so the attribution is unvalidated
- **Gemma 4 run 3** (PARTIAL): 'The remaining EUR24k gap is driven by Soylent (-EUR10k), Wonka (-EUR14k), and Acme' - the two figures are correct and sum to EUR24k, but Acme is included even though its expansion is unchanged at zero

### Read Acme's explained decline as churn

`avoid_acme_false_positive` (4 pts) — 1 miss(es).

- **Qwen 3.6 run 3** (PARTIAL): 'Acme: Medium Risk. Structural shift to annual batch processing. Usage down 45%... Monitor for churn' - the explanation is noticed and then the account is still carried as a churn watch

### Invented a cause the sources do not establish

`no_unsupported_causality` (2 pts) — 3 miss(es).

- **GLM 5.3 Flash run 2** (PARTIAL): 'The -61% admin-logins drop is consistent with the SSO breakage - actionable today via the ticket, not a mystery' presents the link as settled rather than as a hypothesis
- **Qwen 3.6 run 3** (FAIL): 'The remaining EUR24k gap is attributed to Soylent and Wonka usage declines and Acme's structural shift' asserts a cause Maya explicitly forbade inventing, and Acme's expansion is unchanged at zero
- **Gemma 4 run 2** (FAIL): '3 open support tickets (including high-severity SSO issue) impacting the pending September expansion' asserts a causal link between the tickets and the procurement delay that no source establishes

### Settled Orion without the evidence to settle it

`orion_missing_evidence` — no model missed this.

### Turned an estimate into an external promise

`conditional_launch_timing` (3 pts) — 9 miss(es).

- **Qwen 3.8 Flash run 3** (PARTIAL): 'Do not confirm Atlas launch at 10:30' is right, but '09:40-09:45 ... confirm to Atlas that rollout is scheduled to begin at 11:00' still goes out before Priya's verification, with the conditionality only implied by the preceding step
- **GLM 5.3 Flash run 1** (PARTIAL): kills the 10:30 task, but 'By 09:45 - Confirm to Atlas: launch proceeds today, rollout opens ~11:00' goes out before the deploy has been verified
- **GLM 5.3 Flash run 3** (PARTIAL): rejects the 10:30 task, but '~09:45: Confirm to Atlas that migration is on this morning with rollout opening ~11:00' precedes any verification
- **MIMO v2.5 run 1** (FAIL): '09:45 | Confirm to Atlas: Enterprise Controls launch is on for today; admins should be standing by. Migration target ~11:00' - an unconditional external commitment made before the deploy is verified
- **Qwen 3.6 run 1** (PARTIAL): no external promise is made, but the ~10:10 rollout figure is passed to Sam and Daniel with no conditionality, and the stale 10:30 Atlas task is never addressed
- **Qwen 3.6 run 3** (FAIL): '#leadership: "Maya, selecting Option A... Will confirm rollout open by 10:30"' - a commitment to a time the response's own impossible schedule produced
- …and 3 more; see `criterion-matrix.md`.

## Penalties

| Model | Run | Type | Points | Evidence |
|---|---:|---|---:|---|
| MIMO v2.5 | 1 | MAJOR_CONTRADICTION | -5 | '09:35 \| Deploy complete. No post-deploy verification needed (no code change from staging-verified build).' against '10:25-10:45 \| Priya runs post-deploy verification (~20 min)' |
| Qwen 3.6 | 1 | MAJOR_PLANNING_ERROR | -7 | 'Monitor Post-Deploy Verify: Priya performs 20-minute verification (09:35-09:55)' and 'If verify finishes at 09:55, rollout opens ~10:10' |
| Qwen 3.6 | 3 | MAJOR_PLANNING_ERROR | -7 | 'Priya verifies 09:35-09:55 (after her break). Sam checks 09:55-10:10. Rollout opens ~10:15. Feasible.' |
| Qwen 3.6 | 3 | MATERIAL_HALLUCINATION | -5 | 'The remaining EUR24k gap is attributed to Soylent and Wonka usage declines and Acme's structural shift' |
| Gemma 4 | 1 | MAJOR_PLANNING_ERROR | -7 | '10:30 - 11:30: Execution Sequence: Marcus deploys 2.9.5-patch (45m)' |
| Gemma 4 | 2 | MAJOR_PLANNING_ERROR | -7 | '09:45 - 10:15: Coordinate with Marcus to initiate deployment of Option B. (Marcus must start by 09:15 and leave by 10:20; deployment takes 45m).' |
| Gemma 4 | 2 | MATERIAL_HALLUCINATION | -5 | '3 open support tickets (including high-severity SSO issue) impacting the pending September expansion' |
| Gemma 4 | 3 | MAJOR_PLANNING_ERROR | -7 | '10:25 - 11:15: Deployment Sequence: Marcus deploys Option B (45m) -> Priya performs post-deploy verification (20m) -> Sam performs rollout sanity check (15m)' |

## Speed and cost

Reported separately from quality. No combined efficiency score exists, by design.

| Model | TTFA median | Total latency median | Output tokens median | Cost median |
|---|---:|---:|---:|---:|
| Qwen 3.8 Flash | 258.9s | 285.0s | 33714 | - |
| GLM 5.2 | 67.0s | 85.4s | 6777 | $0.0165 |
| DeepSeek V4 Flash | 162.6s | 178.8s | 14863 | $0.0056 |
| GLM 5.3 Flash | 238.5s | 316.6s | 12394 | - |
| MIMO v2.5 | 163.3s | 195.4s | 9510 | - |
| Qwen 3.6 | 0.9s | 18.2s | 2644 | - |
| Gemma 4 | 0.3s | 8.7s | 921 | - |

## Not yet: an Overall Monday Score

Two scenarios is not a benchmark suite. #001 and #002 measure overlapping but different things, and averaging two numbers would imply a weighting nobody has argued for. The per-scenario results are published in a shape that can be aggregated later; no aggregate is published now.

