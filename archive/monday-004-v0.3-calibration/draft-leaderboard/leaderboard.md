# MondayBench 0.4 - `monday-004`

**Evaluator:** `evaluator-opus5-v0.4-calibration-3`  
**Rubric:** 0.3  
**Judge:** `claude-opus-5`  
**Prompt SHA-256:** `3a0cbb569ca4f711b8907177af9204cec267d26f35f732829df56b03ed23ef99`  
**Generated:** 2026-08-29T11:24:53Z

> **NOT AN OFFICIAL RESULT.** This leaderboard was built without `--official`, so the publication gates were not enforced: run counts, prompt/rubric/judge consistency and scoring arithmetic are unverified. Do not cite these numbers as MondayBench v0.4 results.

The Monday Score is the mean of each model's official runs and measures task quality only. TTFA, latency and cost sit beside it and are never folded into it.

| Rank | Model | Monday Score | Runs | Range | TTFA median | Total median |
|---:|---|---:|---:|---:|---:|---:|
| 1 | GLM 5.3 Flash | **98.5** | 1 | 0.0 | 552.1s | 627.6s |
| 2 | Qwen 3.8 Flash | **98.5** | 1 | 0.0 | 325.4s | 387.9s |
| 3 | MIMO v2.5 | **90.0** | 1 | 0.0 | 289.1s | 398.1s |
| 4 | DeepSeek V4 Flash | **87.0** | 1 | 0.0 | 109.1s | 117.8s |
| 5 | GLM 5.2 | **71.0** | 1 | 0.0 | 273.5s | 311.8s |
| 6 | Qwen 3.6 | **54.5** | 1 | 0.0 | 1.3s | 30.8s |
| 7 | Gemma 4 | **45.5** | 1 | 0.0 | 1.1s | 15.2s |

---

## 1. GLM 5.3 Flash - 98.5 / 100

`glm5.3-flash`

| Dimension | Score | Max |
|---|---:|---:|
| Revenue reasoning | 20.0 | 20 |
| Customer health | 15.0 | 15 |
| Acquisition reasoning | 19.0 | 19 |
| Plan economics | 19.0 | 19 |
| Cross table data quality | 16.5 | 18 |
| Decision quality | 9.0 | 9 |
| **Monday Score** | **98.5** | **100** |

**Runs:** 98.5  (min 98.5, max 98.5, run_range 0.0, sigma 0.00)

**Latency and cost:** TTFA median 552.1s, TTFT median 2.6s, total median 627.6s, output tokens median 29778.0, cost/run median -

### What it missed (1 criteria)

- **`figures_carried_correctly`** - PARTIAL across 1 run(s), 1.5 points forgone
  - Two off-by-small counts in supporting statistics, neither decision-changing. Everything else checkable is exact: 59 -> 74 tickets, unresolved 20 -> 24, api-error tickets 10 -> 12, blended margin 35.2% -> 32.5%, SMB new ARR EUR 247.2k, Mid-market -EUR 42k, duff-brewing EUR 162k renewing 5 Dec, wayne at 11.5% of ARR.

### What it got wrong (0)

No penalties and no false actions in any run.

### Raw evidence

- response: `runs/monday-004/glm5.3-flash/run-002.json`
- evaluation: `evaluations/evaluator-opus5-v0.4-calibration-3/monday-004/glm5.3-flash/run-002.json`

---

## 2. Qwen 3.8 Flash - 98.5 / 100

`qwen3.8-flash`

| Dimension | Score | Max |
|---|---:|---:|
| Revenue reasoning | 20.0 | 20 |
| Customer health | 15.0 | 15 |
| Acquisition reasoning | 19.0 | 19 |
| Plan economics | 19.0 | 19 |
| Cross table data quality | 16.5 | 18 |
| Decision quality | 9.0 | 9 |
| **Monday Score** | **98.5** | **100** |

**Runs:** 98.5  (min 98.5, max 98.5, run_range 0.0, sigma 0.00)

**Latency and cost:** TTFA median 325.4s, TTFT median 3.2s, total median 387.9s, output tokens median 46434.0, cost/run median -

### What it missed (1 criteria)

- **`figures_carried_correctly`** - PARTIAL across 1 run(s), 1.5 points forgone
  - One aggregate wrong by 0.9% and the derived rate by a full point, outside the stated tolerance. Everything else checkable is exact - the ARR bridge, GRR/NRR, all six contribution figures, the attribution split, all six ticket totals, the utilisation percentages and 'Enterprise requests excluding Acme +8.0%'. No decision rests on the token line.

### What it got wrong (0)

No penalties and no false actions in any run.

### Raw evidence

- response: `runs/monday-004/qwen3.8-flash/run-002.json`
- evaluation: `evaluations/evaluator-opus5-v0.4-calibration-3/monday-004/qwen3.8-flash/run-002.json`

---

## 3. MIMO v2.5 - 90.0 / 100

`mimo-v2.5`

| Dimension | Score | Max |
|---|---:|---:|
| Revenue reasoning | 17.0 | 20 |
| Customer health | 12.5 | 15 |
| Acquisition reasoning | 19.0 | 19 |
| Plan economics | 19.0 | 19 |
| Cross table data quality | 15.0 | 18 |
| Decision quality | 7.5 | 9 |
| **Monday Score** | **90.0** | **100** |

**Runs:** 90.0  (min 90.0, max 90.0, run_range 0.0, sigma 0.00)

**Latency and cost:** TTFA median 289.1s, TTFT median 1.9s, total median 398.1s, output tokens median 28597.0, cost/run median -

### What it missed (4 criteria)

- **`acquisition_recommendation`** - PARTIAL across 1 run(s), 1.5 points forgone
  - Identifies Partner's efficiency and refuses paid search, but the content increase it does recommend is not itself conditioned on the missing cost data, which it raises only in a separate section.
- **`figures_carried_correctly`** - FAIL across 1 run(s), 3.0 points forgone
  - Four incorrect figures in four different sections, which is the FAIL band's 'repeated incorrect figures across different parts'. None is decision-changing on its own and the Pro figures that carry the recommendation are exact, but the errors are not confined to one lapse.
- **`headline_vs_recurring_growth`** - PARTIAL across 1 run(s), 3.0 points forgone
  - The normalised figure and both distortions are right, and the EUR 110,000 effect is quantified, but the raw comparison the headline would be built on is never computed, so the size of the gap is never shown.
- **`segment_retention_quantified`** - PARTIAL across 1 run(s), 2.5 points forgone
  - Populations and losses are correct and correctly placed, but no churn or retention rate is computed on any basis, so the segments are never ranked on retention.

### What it got wrong (0)

No penalties and no false actions in any run.

### Raw evidence

- response: `runs/monday-004/mimo-v2.5/run-003.json`
- evaluation: `evaluations/evaluator-opus5-v0.4-calibration-3/monday-004/mimo-v2.5/run-003.json`

---

## 4. DeepSeek V4 Flash - 87.0 / 100

`deepseek-v4-flash`

| Dimension | Score | Max |
|---|---:|---:|
| Revenue reasoning | 20.0 | 20 |
| Customer health | 14.0 | 15 |
| Acquisition reasoning | 19.0 | 19 |
| Plan economics | 19.0 | 19 |
| Cross table data quality | 16.0 | 18 |
| Decision quality | 6.0 | 9 |
| **Monday Score** | **87.0** | **100** |

**Runs:** 87.0  (min 87.0, max 87.0, run_range 0.0, sigma 0.00)

**Latency and cost:** TTFA median 109.1s, TTFT median 2.4s, total median 117.8s, output tokens median 24579.0, cost/run median $0.0104

### What it missed (3 criteria)

- **`no_churn_overreach`** - PARTIAL across 1 run(s), 1.0 points forgone
  - Offers a cause and immediately labels it unprovable. That is the PARTIAL band rather than the PASS bar, which asks that no cause be claimed.
- **`segment_recommendation`** - FAIL across 1 run(s), 3.0 points forgone
  - Recommends the reduction. Its own figures show SMB adding EUR 133.2k of new ARR against EUR 123.6k churned - net positive, not 'treading water' - and it never states that the segment economics needed to justify a reduction are absent from the pack.
- **`support_normalized`** - PARTIAL across 1 run(s), 2.0 points forgone
  - Correct counts and a within-plan trend, but no rate against any denominator and no comparison across plans. It avoids the raw-count trap without doing the normalisation the criterion asks for.

### What it got wrong (1)

- **PROHIBITED_ACTION** `PROHIBITED_ACTION` (-7.0)
  - Recommends reducing SMB acquisition spend on the churn rate, which is the action the pack rules out. Its own figures show SMB new logos adding EUR 133.2k against EUR 123.6k churned - net positive, not 'barely offset' - and the pack contains no segment-level cost data with which to justify a reduction. Naming the option in order to reject it would have been correct; this tells leadership to do it.
  - evidence: 'Reduce incremental investment in SMB. The data supports reducing new SMB acquisition spend until retention improves. SMB had ~20.5% ARR churn in one month' - the first of its three recommendations to leadership.

### Raw evidence

- response: `runs/monday-004/deepseek-v4-flash/run-003.json`
- evaluation: `evaluations/evaluator-opus5-v0.4-calibration-3/monday-004/deepseek-v4-flash/run-003.json`

---

## 5. GLM 5.2 - 71.0 / 100

`glm5.2`

| Dimension | Score | Max |
|---|---:|---:|
| Revenue reasoning | 17.0 | 20 |
| Customer health | 12.5 | 15 |
| Acquisition reasoning | 15.0 | 19 |
| Plan economics | 11.0 | 19 |
| Cross table data quality | 16.5 | 18 |
| Decision quality | 6.0 | 9 |
| **Monday Score** | **71.0** | **100** |

**Runs:** 71.0  (min 71.0, max 71.0, run_range 0.0, sigma 0.00)

**Latency and cost:** TTFA median 273.5s, TTFT median 1.7s, total median 311.8s, output tokens median 43200.0, cost/run median $0.1020

### What it missed (8 criteria)

- **`absolute_vs_scalable_economics`** - PARTIAL across 1 run(s), 2.5 points forgone
  - Both halves are present and correct, and then the product decision is argued from the absolute figure - the first bullet of its own justification. The margin erosion is a real second reason, which keeps this off FAIL.
- **`conversion_rate_vs_absolute_volume`** - FAIL across 1 run(s), 4.0 points forgone
  - Combining the two months erases the movement entirely: neither the falling conversion rate nor the rising absolute conversions is reported, and the pack's central funnel observation is never made.
- **`figures_carried_correctly`** - PARTIAL across 1 run(s), 1.5 points forgone
  - Two slips, neither decision-changing. Everything else checkable is exact, including 44% of the September starter base, EUR 94,800 of replacement ARR, EUR 218.4k of SMB pro ARR, enterprise support cost rising EUR 9k on +2 tickets, and every figure in the funnel and attribution tables.
- **`headline_vs_recurring_growth`** - PARTIAL across 1 run(s), 3.0 points forgone
  - The normalised figure is right and the distortions are all identified, but the raw invoiced comparison - EUR 797.1k against EUR 892.9k - is never computed, so the +12% the pack would otherwise report is never set against the +1.6%.
- **`plan_trajectory_evidence`** - FAIL across 1 run(s), 3.0 points forgone
  - True of the three plan averages it tabulates and false of the customers: Stark 4.29M and Wayne 3.41M exceed the 3M enterprise allowance, and Wonka 1.02M, Aperture 705k and Vandelay 690k exceed the 600k Pro allowance. The claim is then used as an argument, which is the aggregate error the scenario is built around.
- **`product_focus_supported`** - PARTIAL across 1 run(s), 2.5 points forgone
  - A plan other than Pro is allowed only when the case does not rest on absolute revenue; the first reason offered is that Enterprise is the largest base. The margin erosion and the support cost per customer are genuine independent signals, so PARTIAL rather than FAIL.
- **`segment_recommendation`** - FAIL across 1 run(s), 3.0 points forgone
  - Recommends the reduction. It is the best-argued version of this answer in the battery - it separates SMB/pro from SMB/starter explicitly, computes the Starter economics correctly and preserves the rest of the segment - but it still recommends a cut, and it never states that segment-level economics are absent from the pack.
- **`segment_retention_quantified`** - PARTIAL across 1 run(s), 2.5 points forgone
  - The Starter plan rate is correct and correctly labelled (4 of 9), and churned ARR is placed by segment, but no rate is given for the other plans or for any segment, so the populations are never ranked on retention.

### What it got wrong (1)

- **PROHIBITED_ACTION** `PROHIBITED_ACTION` (-7.0)
  - Recommends defunding part of the SMB segment on Starter-plan economics and a churn count. The best-argued version of this answer in the battery - it separates SMB/pro from SMB/starter, computes the Starter economics correctly and preserves the rest of the segment - but the pack has no segment-level economics, and it never says so before acting.
  - evidence: 'Decision 1 - Finance: reduce investment in SMB, specifically SMB/starter ... Action: Reduce paid acquisition targeting SMB/starter.'

### Raw evidence

- response: `runs/monday-004/glm5.2/run-002.json`
- evaluation: `evaluations/evaluator-opus5-v0.4-calibration-3/monday-004/glm5.2/run-002.json`

---

## 6. Qwen 3.6 - 54.5 / 100

`qwen3.6`

| Dimension | Score | Max |
|---|---:|---:|
| Revenue reasoning | 5.0 | 20 |
| Customer health | 10.5 | 15 |
| Acquisition reasoning | 14.0 | 19 |
| Plan economics | 12.5 | 19 |
| Cross table data quality | 5.5 | 18 |
| Decision quality | 7.0 | 9 |
| **Monday Score** | **54.5** | **100** |

**Runs:** 54.5  (min 54.5, max 54.5, run_range 0.0, sigma 0.00)

**Latency and cost:** TTFA median 1.3s, TTFT median 1.3s, total median 30.8s, output tokens median 3659.0, cost/run median -

### What it missed (18 criteria)

- **`absolute_vs_scalable_economics`** - PARTIAL across 1 run(s), 2.5 points forgone
  - Both halves are held and correctly stated, and then the product decision goes to Enterprise on the strength of its being the profit driver.
- **`annual_prepayment_normalized`** - FAIL across 1 run(s), 6.0 points forgone
  - Reaches a recurring figure without ever identifying or normalising the annual invoice.
- **`causal_boundary`** - PARTIAL across 1 run(s), 1.5 points forgone
  - Offers a mechanism as a suggestion rather than asserting it, but the ticket spike is absent and the epistemic limit is never stated for this account.
- **`cross_table_customer_signal`** - PARTIAL across 1 run(s), 2.0 points forgone
  - Two tables joined at account level with correct figures, but the plan is wrong and the support signal is missing, so the three-table picture is never assembled.
- **`customer_id_alias_resolved`** - FAIL across 1 run(s), 4.0 points forgone
  - No account-level join between billing and usage was attempted, so the alias is neither resolved nor noticed.
- **`duplicate_detected`** - FAIL across 1 run(s), 4.0 points forgone
  - The duplicate is not mentioned.
- **`existing_customer_expansion_removed`** - PARTIAL across 1 run(s), 2.5 points forgone
  - The split is done per channel but never carried through to a new-logo ranking, so the reversal against the raw table is never shown.
- **`figures_carried_correctly`** - FAIL across 1 run(s), 3.0 points forgone
  - Four incorrect figures in four different sections, one of which - the 89% profit share - is used to argue against reducing Enterprise investment.
- **`headline_vs_recurring_growth`** - PARTIAL across 1 run(s), 3.0 points forgone
  - The normalised figure is right and correctly labelled, but the raw invoiced comparison it should be set against is never computed.
- **`plan_trajectory_evidence`** - PARTIAL across 1 run(s), 1.5 points forgone
  - Utilisation is quantified per plan from the averages and hedged with 'most', which keeps it off the FAIL clause, but the accounts above their allowance are never identified and no usage growth rate is computed.
- **`product_focus_supported`** - PARTIAL across 1 run(s), 2.5 points forgone
  - Two different answers in one response, and the Enterprise case is argued from its being the revenue and profit driver rather than from cost-adjusted economics.
- **`product_recommendation`** - PARTIAL across 1 run(s), 0.5 points forgone
  - A recommendation is made but it is not single and it contradicts its own section 4 conclusion that Pro is the most efficient.
- **`raw_attribution_not_equivalent_new_business`** - PARTIAL across 1 run(s), 2.5 points forgone
  - Separates the expansions and names them, but never states the EUR 274.8k attributed total or what share of it is not new business.
- **`revenue_conclusion`** - PARTIAL across 1 run(s), 2.0 points forgone
  - Right direction and a real driver, but the reported number leadership would otherwise quote is never confronted.
- **`sample_size_arr_context`** - PARTIAL across 1 run(s), 2.0 points forgone
  - The churned ARR is itemised, but SMB's own base is never given and the comparison drawn is Enterprise's share of profit rather than what the SMB churn actually cost.
- **`segment_recommendation`** - PARTIAL across 1 run(s), 1.5 points forgone
  - It does not recommend cutting SMB, which keeps it off FAIL, but it answers the segment question about Enterprise instead, offers no next step for SMB, and floats sunsetting Starter as one of three options.
- **`segment_retention_quantified`** - PARTIAL across 1 run(s), 2.5 points forgone
  - A rate is computed and SMB is correctly identified as worst, but the numerator counts a Mid-market churn inside SMB and contradicts the table three paragraphs above it.
- **`support_normalized`** - PARTIAL across 1 run(s), 2.0 points forgone
  - One plan normalised against revenue, with no comparison across plans.

### What it got wrong (0)

No penalties and no false actions in any run.

### Raw evidence

- response: `runs/monday-004/qwen3.6/run-002.json`
- evaluation: `evaluations/evaluator-opus5-v0.4-calibration-3/monday-004/qwen3.6/run-002.json`

---

## 7. Gemma 4 - 45.5 / 100

`gemma4`

| Dimension | Score | Max |
|---|---:|---:|
| Revenue reasoning | 11.0 | 20 |
| Customer health | 6.5 | 15 |
| Acquisition reasoning | 7.0 | 19 |
| Plan economics | 8.5 | 19 |
| Cross table data quality | 7.0 | 18 |
| Decision quality | 5.5 | 9 |
| **Monday Score** | **45.5** | **100** |

**Runs:** 45.5  (min 45.5, max 45.5, run_range 0.0, sigma 0.00)

**Latency and cost:** TTFA median 1.1s, TTFT median 1.1s, total median 15.2s, output tokens median 1442.0, cost/run median -

### What it missed (19 criteria)

- **`absolute_vs_scalable_economics`** - FAIL across 1 run(s), 5.0 points forgone
  - The summary states the opposite of its own analysis and gets the direction wrong: Enterprise has the worst margin of the three. Absolute contribution and margin are never distinguished.
- **`acme_false_positive_avoided`** - PARTIAL across 1 run(s), 2.0 points forgone
  - The migration and the token figure are both there and correct, but the executive summary still books the decline as declining segment health.
- **`acquisition_recommendation`** - PARTIAL across 1 run(s), 1.5 points forgone
  - Names Partner as the efficiency lever and conditions the spend, but reaches it through conversion rate alone because the new-logo correction is never made.
- **`causal_boundary`** - FAIL across 1 run(s), 3.0 points forgone
  - None of the three simultaneous movements is reported, so the pattern is never seen.
- **`conversion_rate_vs_absolute_volume`** - PARTIAL across 1 run(s), 2.0 points forgone
  - Both figures are on the page but the movement is never read: neither the falling rate nor the rising absolute conversions is stated.
- **`cross_table_customer_signal`** - PARTIAL across 1 run(s), 2.0 points forgone
  - Usage and context joined for one account, but no third table and no account built from customers, usage and support together.
- **`customer_id_alias_resolved`** - FAIL across 1 run(s), 4.0 points forgone
  - The alias is neither resolved nor noticed.
- **`duplicate_detected`** - FAIL across 1 run(s), 4.0 points forgone
  - The duplicate is not mentioned.
- **`existing_customer_expansion_removed`** - FAIL across 1 run(s), 5.0 points forgone
  - The split is never made.
- **`headline_vs_recurring_growth`** - PARTIAL across 1 run(s), 3.0 points forgone
  - Establishes that the headline overstates and names the cause, but gives no figure on either side, so the size of the distortion is never shown.
- **`plan_trajectory_evidence`** - FAIL across 1 run(s), 3.0 points forgone
  - Neither growth nor the included-volume distribution is examined.
- **`product_focus_supported`** - PARTIAL across 1 run(s), 2.5 points forgone
  - Recommends Pro on margin alone and then offers an alternative without choosing between them.
- **`product_recommendation`** - PARTIAL across 1 run(s), 0.5 points forgone
  - Two recommendations rather than one, and both sit against an executive summary that names Enterprise as the most efficient plan.
- **`raw_attribution_not_equivalent_new_business`** - FAIL across 1 run(s), 5.0 points forgone
  - No adjustment is attempted because the attribution data is never opened.
- **`revenue_conclusion`** - PARTIAL across 1 run(s), 2.0 points forgone
  - The right conclusion, carried into the summary, with nothing quantified behind it.
- **`sample_size_arr_context`** - FAIL across 1 run(s), 4.0 points forgone
  - None of the three contexts the criterion asks for is present.
- **`segment_recommendation`** - PARTIAL across 1 run(s), 1.5 points forgone
  - It does not recommend cutting SMB, which keeps it off FAIL, but it answers the segment question about Enterprise and leaves SMB without a next step or a statement of what is missing.
- **`segment_retention_quantified`** - PARTIAL across 1 run(s), 2.5 points forgone
  - The churned logos are placed in the right segments, but no rate is computed on any basis and the segments are never ranked.
- **`support_normalized`** - PARTIAL across 1 run(s), 2.0 points forgone
  - One plan normalised against revenue, with no comparison across plans.

### What it got wrong (0)

No penalties and no false actions in any run.

### Raw evidence

- response: `runs/monday-004/gemma4/run-002.json`
- evaluation: `evaluations/evaluator-opus5-v0.4-calibration-3/monday-004/gemma4/run-002.json`

---

## Reproducing this

```bash
mondaybench validate --scenario monday-004 \
    --evaluator evaluator-opus5-v0.4-calibration-3
mondaybench leaderboard --scenario monday-004 \
    --evaluator evaluator-opus5-v0.4-calibration-3 --official
```

Every input, raw response, judge verdict and scoring rule is in this repository. See `README.md` for the methodology.
