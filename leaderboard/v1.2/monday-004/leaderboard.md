# MondayBench 0.4 - `monday-004`

**Evaluator:** `evaluator-opus5-v0.4`  
**Rubric:** 0.3  
**Judge:** `claude-opus-5`  
**Prompt SHA-256:** `3a0cbb569ca4f711b8907177af9204cec267d26f35f732829df56b03ed23ef99`  
**Generated:** 2026-09-10T18:39:11Z

**Status:** official v0.4 result. Every publication gate passed.

The Monday Score is the mean of each model's official runs and measures task quality only. TTFA, latency and cost sit beside it and are never folded into it.

| Rank | Model | Monday Score | Runs | Range | TTFA median | Total median |
|---:|---|---:|---:|---:|---:|---:|
| 1 | GLM 5.3 Flash | **98.0** | 3 | 1.5 | 766.2s | 827.8s |
| 2 | Qwen 3.8 Flash | **96.5** | 3 | 3.0 | 394.1s | 468.0s |
| 3 | GLM 5.3 | **91.7** | 3 | 17.0 | 634.2s | 673.2s |
| 4 | DeepSeek V4 Flash | **86.0** | 3 | 10.5 | 164.6s | 174.4s |
| 5 | MIMO v2.5 | **78.5** | 3 | 25.5 | 368.6s | 483.6s |
| 6 | GLM 5.2 | **71.2** | 3 | 4.5 | 57.1s | 103.1s |
| 7 | DeepSeek V4.1 Flash | **63.7** | 3 | 34.0 | 85.8s | 101.1s |
| 8 | Qwen 3.6 | **46.0** | 3 | 2.5 | 72.6s | 102.4s |
| 9 | Gemma 4 | **35.2** | 3 | 19.0 | 0.8s | 15.3s |

---

## 1. GLM 5.3 Flash - 98.0 / 100

`glm5.3-flash`

| Dimension | Score | Max |
|---|---:|---:|
| Revenue reasoning | 20.0 | 20 |
| Customer health | 15.0 | 15 |
| Acquisition reasoning | 19.0 | 19 |
| Plan economics | 19.0 | 19 |
| Cross table data quality | 16.5 | 18 |
| Decision quality | 8.5 | 9 |
| **Monday Score** | **98.0** | **100** |

**Runs:** 98.5, 98.5, 97.0  (min 97.0, max 98.5, run_range 1.5, sigma 0.87)

**Latency and cost:** TTFA median 766.2s, TTFT median 2.5s, total median 827.8s, output tokens median 36248.0, cost/run median -

### What it missed (2 criteria)

- **`figures_carried_correctly`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 4.5 points forgone
  - Two small slips in supporting detail. Everything else checkable is exact, including the EUR 262.9k -> EUR 246.5k profit walk, the +5.8% cost growth, the MRR bridge, the EUR 216k expansion bookings itemised, the EUR 3.23M of ARR with open high-severity tickets, all eight funnel cells, the full new-logo table, all twelve plan figures, contribution per customer for all three plans, and the mid-market -EUR 42k walk.
- **`segment_recommendation`** - PARTIAL across 1 run(s), 1.5 points forgone
  - A reduction hedged with conditions, which is the PARTIAL band precisely. It names the missing input the PASS bar asks for and the budget stays inside SMB rather than leaving it, but leadership is still told to pause acquisition spend.

### What it got wrong (0)

No penalties and no false actions in any run.

### Raw evidence

- response: `runs/monday-004/glm5.3-flash/run-003.json`
- response: `runs/monday-004/glm5.3-flash/run-004.json`
- response: `runs/monday-004/glm5.3-flash/run-005.json`
- evaluation: `evaluations/v1.2/evaluator-opus5-v0.4/monday-004/glm5.3-flash/run-003.json`
- evaluation: `evaluations/v1.2/evaluator-opus5-v0.4/monday-004/glm5.3-flash/run-004.json`
- evaluation: `evaluations/v1.2/evaluator-opus5-v0.4/monday-004/glm5.3-flash/run-005.json`

---

## 2. Qwen 3.8 Flash - 96.5 / 100

`qwen3.8-flash`

| Dimension | Score | Max |
|---|---:|---:|
| Revenue reasoning | 20.0 | 20 |
| Customer health | 15.0 | 15 |
| Acquisition reasoning | 19.0 | 19 |
| Plan economics | 19.0 | 19 |
| Cross table data quality | 15.0 | 18 |
| Decision quality | 8.5 | 9 |
| **Monday Score** | **96.5** | **100** |

**Runs:** 96.5, 98.0, 95.0  (min 95.0, max 98.0, run_range 3.0, sigma 1.50)

**Latency and cost:** TTFA median 394.1s, TTFT median 3.3s, total median 468.0s, output tokens median 52295.0, cost/run median -

### What it missed (3 criteria)

- **`figures_carried_correctly`** - PARTIAL/PARTIAL across 2 run(s), 3.0 points forgone
  - One miscount. Everything else checkable is exact, and the response carries more arithmetic than any other in the battery: the ARR bridge reconciling to EUR 8,788,800 to the euro, four revenue bases, the segment ARR walk including the reconstructed EUR 1,704,000, both channel tables with totals, the full two-month plan economics with cost subtotals, the utilisation table computed from customer counts, all five over-allowance accounts with overage volumes, the Soylent four-metric table, and the 13 October rate-limit tickets itemised per account - the only response anywhere to get that count right.
- **`segment_recommendation`** - PARTIAL across 1 run(s), 1.5 points forgone
  - A reduction hedged with conditions, which is the PARTIAL band. It names the missing inputs the PASS bar asks for and keeps the budget inside SMB, but leadership is still told to pause acquisition spend rather than to investigate first.
- **`support_normalized`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 6.0 points forgone
  - It avoids the trap - Enterprise is called stable and Pro gets the focus - and it reads the segment view as well as the plan view, which is more care than most. But no rate against any denominator is computed, so the normalisation the criterion asks for is not performed.

### What it got wrong (0)

No penalties and no false actions in any run.

### Raw evidence

- response: `runs/monday-004/qwen3.8-flash/run-003.json`
- response: `runs/monday-004/qwen3.8-flash/run-004.json`
- response: `runs/monday-004/qwen3.8-flash/run-006.json`
- evaluation: `evaluations/v1.2/evaluator-opus5-v0.4/monday-004/qwen3.8-flash/run-003.json`
- evaluation: `evaluations/v1.2/evaluator-opus5-v0.4/monday-004/qwen3.8-flash/run-004.json`
- evaluation: `evaluations/v1.2/evaluator-opus5-v0.4/monday-004/qwen3.8-flash/run-006.json`

---

## 3. GLM 5.3 - 91.7 / 100

`glm5.3`

| Dimension | Score | Max |
|---|---:|---:|
| Revenue reasoning | 19.0 | 20 |
| Customer health | 14.2 | 15 |
| Acquisition reasoning | 19.0 | 19 |
| Plan economics | 17.3 | 19 |
| Cross table data quality | 13.7 | 18 |
| Decision quality | 8.5 | 9 |
| **Monday Score** | **91.7** | **100** |

**Runs:** 95.0, 81.5, 98.5  (min 81.5, max 98.5, run_range 17.0, sigma 8.98)

**Latency and cost:** TTFA median 634.2s, TTFT median 4.6s, total median 673.2s, output tokens median 46592.0, cost/run median $0.0124

### What it missed (8 criteria)

- **`absolute_vs_scalable_economics`** - PARTIAL across 1 run(s), 2.5 points forgone
  - the contrast is drawn correctly - '87% of revenue, 79% of gross profit - but margin fell 2.7pp' against 'Pro is the margin leader (62.7%)' - and then the product recommendation leans on the absolute figure anyway: 'Plan focus (Product): Enterprise plan ... It carries 79% of gross profit'. That is the PARTIAL band's second clause word for word
- **`causal_boundary`** - PARTIAL/PARTIAL across 2 run(s), 3.0 points forgone
  - all three Soylent movements are present and correct - '-27%' usage, 'tickets went 3 to 8', and the EUR2.5k downgrade - and no mechanism is asserted or implied. What the PASS band also requires is the explicit statement that the data does not establish what caused what, and the response never makes it for Soylent; the epistemic caveat it does give is about channel attribution
- **`figures_carried_correctly`** - PARTIAL/FAIL/PARTIAL across 3 run(s), 6.0 points forgone
  - the great majority of a very large number of figures recompute exactly, including both revenue totals, the full MRR bridge, every churn base, all four channel yields and every plan margin. Three slips, none of which any recommendation rests on and none of which changes how the analysis reads once corrected: Pro rate-limit tickets given as '4 to 13' where September is 5; November's expansion uplift given as '+EUR19.5k/month' where EUR216k over twelve months is EUR18k; and 'all 35 rows' where customers.csv has 36. The ex-acme request growth of +9.3% against 8.8% is inside the rubric's own half-point tolerance and is not counted
- **`headline_vs_recurring_growth`** - PARTIAL across 1 run(s), 3.0 points forgone
  - the normalised figure is right and its treatment is stated - EUR746.1k to EUR757.7k, +1.6% - and the gap is correctly attributed to the annual invoice and the duplicate. But the headline it contrasts against is the DEDUPLICATED +9.6%; the raw invoice sum's ~+12.0% is never computed. EUR892.9k appears once, in the data-issues section, as a total rather than as a growth rate. That is the rubric's 'gives only one of the two figures'
- **`product_focus_supported`** - PARTIAL across 1 run(s), 2.5 points forgone
  - the Enterprise plan is chosen over Pro. The other-plan route is open in the rubric, but only when argued on cost-adjusted economics and at least two independent signals AND not resting on absolute revenue. Margin erosion and the open high-severity tickets are real signals; the case is nevertheless led by 'it carries 79% of gross profit' and closed by 'one enterprise churn (stark = EUR1.14M) would erase more ARR than a full quarter of new logos', both absolute-size arguments. Pro is named only as a secondary track
- **`segment_recommendation`** - PARTIAL across 1 run(s), 1.5 points forgone
  - SMB is not cut and the missing input is named ('Segment P&L cannot be built: costs are attributed by plan, and plans cut across segments'), but the recommendation is a reduction with conditions attached: 'freeze incremental SMB acquisition spend ... set a January checkpoint - cut only if SMB net revenue retention hasn't improved'
- **`segment_retention_quantified`** - PARTIAL across 1 run(s), 2.5 points forgone
  - SMB is correctly identified as worst and Enterprise as zero, but the middle is never quantified: no mid-market churn rate appears anywhere, so the three populations cannot be ranked from the figures given. The two framings are also mixed - '44% of the starter base' is plan, '4 of 12 September SMB logos' is segment - and that segment denominator is wrong (13 SMB accounts predate October, not 12). Neither error changes which population is worst, which is the PARTIAL band
- **`support_normalized`** - PARTIAL/PARTIAL across 2 run(s), 4.0 points forgone
  - support cost as a share of plan revenue is computed for STARTER only - '32% of revenue (EUR792/customer/month vs EUR2,462 ARPU)', both exact. Enterprise's support is discussed only as a margin movement and Pro's only as a month-on-month change; the raw ticket counts by plan never appear, so the conclusion that Enterprise is not the worst despite raising 35 of 74 October tickets is never reached. That is the rubric's 'computes a rate for one plan only'

### What it got wrong (0)

No penalties and no false actions in any run.

### Raw evidence

- response: `runs/monday-004/glm5.3/run-001.json`
- response: `runs/monday-004/glm5.3/run-002.json`
- response: `runs/monday-004/glm5.3/run-003.json`
- evaluation: `evaluations/v1.2/evaluator-opus5-v0.4/monday-004/glm5.3/run-001.json`
- evaluation: `evaluations/v1.2/evaluator-opus5-v0.4/monday-004/glm5.3/run-002.json`
- evaluation: `evaluations/v1.2/evaluator-opus5-v0.4/monday-004/glm5.3/run-003.json`

---

## 4. DeepSeek V4 Flash - 86.0 / 100

`deepseek-v4-flash`

| Dimension | Score | Max |
|---|---:|---:|
| Revenue reasoning | 19.0 | 20 |
| Customer health | 12.5 | 15 |
| Acquisition reasoning | 16.5 | 19 |
| Plan economics | 18.0 | 19 |
| Cross table data quality | 16.3 | 18 |
| Decision quality | 6.0 | 9 |
| **Monday Score** | **86.0** | **100** |

**Runs:** 91.0, 80.5, 86.5  (min 80.5, max 91.0, run_range 10.5, sigma 5.27)

**Latency and cost:** TTFA median 164.6s, TTFT median 2.1s, total median 174.4s, output tokens median 29942.0, cost/run median $0.0123

### What it missed (8 criteria)

- **`acquisition_recommendation`** - FAIL across 1 run(s), 3.0 points forgone
  - Refuses to increase spend, which is right, and then names the one channel the pack rules out - on the raw attributed revenue whose expansion contamination it had identified two sections earlier. Never having computed new-logo ARR by channel is what leaves it there.
- **`existing_customer_expansion_removed`** - PARTIAL/FAIL across 2 run(s), 7.5 points forgone
  - The correction is made for the channel it matters most for, then the ranking is redone on logo count rather than new-logo value - which is why content (3 logos, EUR 91.2k) is preferred to partner (2 logos, EUR 166.8k).
- **`figures_carried_correctly`** - PARTIAL/PARTIAL across 2 run(s), 3.0 points forgone
  - One figure error: '4 of 13 SMB customers' attaches the Starter plan's population to the SMB segment, which has 18, overstating segment churn as 30.8% against 22.2%. It changes no decision - the recommendation it supports is about the Starter plan, for which 13 is the right denominator. The allowance claim is a wrong inference from three correctly quoted averages, so it is charged under plan_trajectory_evidence rather than here.
- **`headline_vs_recurring_growth`** - PARTIAL across 1 run(s), 3.0 points forgone
  - Two bases, each labelled with exactly what it contains, and the gap between them shown. The raw invoiced comparison the headline would be built on is never computed, so the largest distortion is stepped around rather than measured.
- **`plan_trajectory_evidence`** - FAIL across 1 run(s), 3.0 points forgone
  - True of the three plan averages and false of the customers: Stark 4.29M and Wayne 3.41M exceed the 3M enterprise allowance, and Wonka 1.02M, Aperture 705k and Vandelay 690k exceed Pro's 600k. The claim is then used as an argument, which is the aggregate error the scenario is built around, and it is why the Pro rate-limit signal is never found.
- **`segment_recommendation`** - PARTIAL/FAIL/PARTIAL across 3 run(s), 6.0 points forgone
  - It does not cut SMB, which is what this criterion forbids, and it gives SMB no next step either - the PARTIAL bar. What it does instead is recommend a reduction in a different segment on one month of movement in a ten-customer population driven by a single churn, having itself noted that segment-level costs are not in the pack. The rubric does not reach that, and it is frozen.
- **`segment_retention_quantified`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 7.5 points forgone
  - Quantifies segment movement on a stated basis and ranks the three, but the basis is net revenue movement rather than retention: SMB's four churns are offset by its five new logos, so no churn or retention rate is given for any segment.
- **`support_normalized`** - PARTIAL across 1 run(s), 2.0 points forgone
  - Correct counts and a real within-plan trajectory, but no rate against any denominator and no comparison across plans. It avoids the raw-count trap without doing the normalisation.

### What it got wrong (1)

- **PROHIBITED_ACTION** `PROHIBITED_ACTION` (-7.0)
  - Defunding part of SMB on a logo churn rate is the first action the pack rules out, and this states that the data supports it. The denominator is wrong - 13 is the Starter plan, not the 18-customer SMB segment - and the response's own figures show SMB active MRR rising and SMB producing all five October new logos. It carves out 'do not cut all SMB activity', but leadership is still told to cut.
  - evidence: 'Reduce investment in the SMB segment, specifically the Starter plan. The data supports this: 4 of 13 SMB customers churned in October ... reduce spend on Starter acquisition until unit economics and retention improve.'

### Raw evidence

- response: `runs/monday-004/deepseek-v4-flash/run-004.json`
- response: `runs/monday-004/deepseek-v4-flash/run-005.json`
- response: `runs/monday-004/deepseek-v4-flash/run-006.json`
- evaluation: `evaluations/v1.2/evaluator-opus5-v0.4/monday-004/deepseek-v4-flash/run-004.json`
- evaluation: `evaluations/v1.2/evaluator-opus5-v0.4/monday-004/deepseek-v4-flash/run-005.json`
- evaluation: `evaluations/v1.2/evaluator-opus5-v0.4/monday-004/deepseek-v4-flash/run-006.json`

---

## 5. MIMO v2.5 - 78.5 / 100

`mimo-v2.5`

| Dimension | Score | Max |
|---|---:|---:|
| Revenue reasoning | 18.0 | 20 |
| Customer health | 11.8 | 15 |
| Acquisition reasoning | 15.8 | 19 |
| Plan economics | 18.0 | 19 |
| Cross table data quality | 13.5 | 18 |
| Decision quality | 6.0 | 9 |
| **Monday Score** | **78.5** | **100** |

**Runs:** 80.0, 65.0, 90.5  (min 65.0, max 90.5, run_range 25.5, sigma 12.82)

**Latency and cost:** TTFA median 368.6s, TTFT median 2.3s, total median 483.6s, output tokens median 24247.0, cost/run median -

### What it missed (12 criteria)

- **`acme_false_positive_avoided`** - PARTIAL across 1 run(s), 2.0 points forgone
  - The account is never treated as a risk and revenue stability is noted, but neither the -45% figure nor the batch migration is stated in the analysis itself, so the connection the criterion asks for is left implicit and no second usage metric is offered.
- **`acquisition_recommendation`** - PARTIAL/PARTIAL across 2 run(s), 3.0 points forgone
  - Identifies content on the corrected new-logo basis and gates everything on the missing cost data, but stops short of a recommendation - which the criterion places at PARTIAL.
- **`conversion_rate_vs_absolute_volume`** - PARTIAL across 1 run(s), 2.0 points forgone
  - Rising volume against a falling rate is stated for paid search, but the table drops the trial counts, so the other half - that absolute conversions rose while the rate fell - is not shown.
- **`customer_id_alias_resolved`** - PARTIAL/PARTIAL across 2 run(s), 4.0 points forgone
  - Wayne's usage growth is right and requires the alias, but no figure is given for it and no aggregate in the response is reachable only with the join, so the evidence is thinner than run-004's exact enterprise request total.
- **`existing_customer_expansion_removed`** - FAIL across 1 run(s), 5.0 points forgone
  - Having seen that paid search's number is mostly expansion, it never recomputes the ranking on new-logo revenue, so the reversal never appears.
- **`figures_carried_correctly`** - FAIL/FAIL/PARTIAL across 3 run(s), 7.5 points forgone
  - Repeated incorrect figures across three sections, and one of them - the October total - is the headline the whole revenue section is built to interrogate. Its plan tables, MRR bridge, churn table, funnel and channel tables are all exact to the euro, which makes this a lapse in the summary tables rather than a misreading of the data.
- **`headline_vs_recurring_growth`** - PARTIAL/PARTIAL across 2 run(s), 6.0 points forgone
  - The structure is right - a raw basis and a normalised one, both labelled, with the gap attributed to the annual invoice and the new logos. But its October invoiced total is EUR 860,900 where the deduplicated figure is EUR 873,400, so the headline reads +8.0% instead of about +12% and falls outside the stated tolerance.
- **`plan_trajectory_evidence`** - PARTIAL/PARTIAL across 2 run(s), 3.0 points forgone
  - Utilisation is quantified for every plan and hedged correctly - 'approaching' rather than 'below' - so it avoids the aggregate FAIL. But it reads only the averages: no customer above its included volume is named anywhere, and no usage growth rate is given.
- **`raw_attribution_not_equivalent_new_business`** - PARTIAL across 1 run(s), 2.5 points forgone
  - The contamination is identified for Paid Search and the reasoning is right, but it is never quantified: neither the EUR 274,800 attributed total nor the EUR 210,000 of expansion appears, only the October column.
- **`segment_recommendation`** - FAIL/FAIL across 2 run(s), 6.0 points forgone
  - Recommends defunding starter acquisition. It is a careful version - it says outright that 'Abandoning SMB entirely would cut off the top of the funnel', preserves SMB Pro, and offers three alternatives - but leadership is still told to move acquisition spend away, and the pack contains no segment-level acquisition cost to justify it.
- **`segment_retention_quantified`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 7.5 points forgone
  - The Starter rate is correct and correctly labelled as a plan, and the segments are ranked on MRR movement. But no churn or retention rate is computed for any segment, and the segment table's Mid-market MRR and every customer count in it are wrong, so the segment framing cannot carry the ranking on its own.
- **`support_normalized`** - PARTIAL across 1 run(s), 2.0 points forgone
  - Support is read at account level throughout and Enterprise is never called the worst on raw volume, but no rate against any denominator is computed for any plan or segment, so the normalisation the criterion asks for is not performed.

### What it got wrong (2)

- **PROHIBITED_ACTION** `PROHIBITED_ACTION` (-7.0)
  - Defunding SMB acquisition on a churn rate is the first action the pack rules out. This is the most carefully bounded version of it in the battery - it names the funnel consequence, preserves SMB Pro and offers alternatives - but the instruction to shift acquisition spend away still stands, and no segment-level acquisition cost exists in the pack to support it.
  - evidence: 'Decision 1: Reduce investment in one customer segment. Recommendation: Yes - reduce investment in SMB starter customers ... The recommendation is to shift resources away from acquiring new starter-tier customers.'
- **PROHIBITED_ACTION** `PROHIBITED_ACTION` (-7.0)
  - Cutting SMB investment on a churn rate is the first action the pack rules out, and this states it at the segment level rather than the plan level and adds a sunset option. Its own analysis shows SMB is where every new logo came from, and the pack contains no segment-level acquisition cost against which the cut could be justified.
  - evidence: 'Decision 1: Reduce investment in SMB - YES, proceed ... Pause or reduce paid acquisition targeting SMB/starter segments ... Evaluate whether the Starter plan should be sunset or restructured.'

### Raw evidence

- response: `runs/monday-004/mimo-v2.5/run-004.json`
- response: `runs/monday-004/mimo-v2.5/run-005.json`
- response: `runs/monday-004/mimo-v2.5/run-006.json`
- evaluation: `evaluations/v1.2/evaluator-opus5-v0.4/monday-004/mimo-v2.5/run-004.json`
- evaluation: `evaluations/v1.2/evaluator-opus5-v0.4/monday-004/mimo-v2.5/run-005.json`
- evaluation: `evaluations/v1.2/evaluator-opus5-v0.4/monday-004/mimo-v2.5/run-006.json`

---

## 6. GLM 5.2 - 71.2 / 100

`glm5.2`

| Dimension | Score | Max |
|---|---:|---:|
| Revenue reasoning | 17.0 | 20 |
| Customer health | 13.5 | 15 |
| Acquisition reasoning | 15.0 | 19 |
| Plan economics | 14.7 | 19 |
| Cross table data quality | 13.7 | 18 |
| Decision quality | 4.3 | 9 |
| **Monday Score** | **71.2** | **100** |

**Runs:** 68.5, 72.0, 73.0  (min 68.5, max 73.0, run_range 4.5, sigma 2.36)

**Latency and cost:** TTFA median 57.1s, TTFT median 1.6s, total median 103.1s, output tokens median 8697.0, cost/run median $0.0261

### What it missed (15 criteria)

- **`absolute_vs_scalable_economics`** - PARTIAL across 1 run(s), 2.5 points forgone
  - Presents both halves and draws the contrast explicitly, then argues the product decision from the absolute revenue figure anyway - the second clause of the PARTIAL band, and the confusion the criterion exists to catch. Gemma 4 run-005 was placed here for the same sequence.
- **`acquisition_recommendation`** - FAIL/PARTIAL across 2 run(s), 4.5 points forgone
  - The one channel the pack rules out, recommended on the raw attributed revenue whose expansion contamination the response had itself identified. Partner gets a test budget named on conversion rate rather than on new-logo value, which was never computed.
- **`causal_boundary`** - PARTIAL/PARTIAL across 2 run(s), 3.0 points forgone
  - Two of the three simultaneous movements, with no mechanism asserted. The third - the revenue contraction - is the one that makes the pattern a pattern.
- **`conversion_rate_vs_absolute_volume`** - PARTIAL across 1 run(s), 2.0 points forgone
  - The falling rate against rising volume is stated and correct. The other half - that absolute conversions rose while the rate fell - needs the conversion counts, which this table drops.
- **`customer_id_alias_resolved`** - PARTIAL/PARTIAL across 2 run(s), 4.0 points forgone
  - The FAIL clause applies only when no account-level join is attempted at all, and several are. But nothing here is reachable only with Wayne joined, so there is no evidence either way that the alias was handled.
- **`existing_customer_expansion_removed`** - FAIL/PARTIAL across 2 run(s), 7.5 points forgone
  - The ranking is never recomputed on new-logo revenue, so the reversal never appears.
- **`figures_carried_correctly`** - PARTIAL/FAIL/PARTIAL across 3 run(s), 6.0 points forgone
  - Two slips, both hedged or self-corrected in the next clause ('flat per customer'), and neither changes a decision. Everything else checkable is exact: the segment ARR table, the EUR 174k expansion, all eight funnel cells, the twelve plan figures, the utilisation percentages and the EUR 6.8M of Enterprise ARR.
- **`headline_vs_recurring_growth`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 9.0 points forgone
  - The normalised side passes as written - the criterion accepts 'roughly flat' - and the treatment is stated. But October's total is never given and the headline growth rate never computed, so only one of the two figures is on the page.
- **`no_churn_overreach`** - PARTIAL/PARTIAL across 2 run(s), 2.0 points forgone
  - Offers a cause the pack does not record. 'Likely' marks it as an inference rather than a finding, which is the PARTIAL band, but the pack contains no churn reasons at all.
- **`plan_trajectory_evidence`** - FAIL across 1 run(s), 3.0 points forgone
  - Three plan averages, all quoted correctly, and then a claim about the customers that the customers contradict: Stark 4.29M and Wayne 3.41M are over the 3M enterprise allowance, and Wonka 1.02M, Aperture 705k and Vandelay 690k are over Pro's 600k. The claim is used as an argument, which is the FAIL clause as written.
- **`product_focus_supported`** - PARTIAL/FAIL across 2 run(s), 7.5 points forgone
  - Two plans with no choice made between them, which is the PARTIAL band as written. The split is coherent - cost work to Enterprise, scaling work to Pro - and the Enterprise half is argued partly from its 79% share of gross profit, which is the absolute figure the rubric warns against leaning on.
- **`product_recommendation`** - PARTIAL across 1 run(s), 0.5 points forgone
  - Actionable and consistent with its own section 4, but two recommendations rather than the single one the criterion asks for.
- **`raw_attribution_not_equivalent_new_business`** - PARTIAL across 1 run(s), 2.5 points forgone
  - It identifies the expansions and quantifies them at EUR 174k, then argues they make paid search look better rather than that they are not new business. The correction is observed and not applied.
- **`segment_recommendation`** - FAIL/FAIL/FAIL across 3 run(s), 9.0 points forgone
  - Recommends defunding part of SMB on churn and plan economics. It is a careful version - the Starter margin and support load are computed correctly and the rest of SMB is untouched - but the pack contains no segment-level acquisition cost, and it never says so before acting.
- **`segment_retention_quantified`** - PARTIAL across 1 run(s), 2.5 points forgone
  - Company-level GRR and NRR are both computed and internally consistent, and the Starter rate is correctly labelled as a plan. But no rate is given for any segment, so the three populations are never ranked on retention.

### What it got wrong (3)

- **PROHIBITED_ACTION** `PROHIBITED_ACTION` (-7.0)
  - Defunding part of SMB on a churn rate is the first action the pack rules out, and this is an unhedged instruction to stop acquiring. The supporting figures are computed correctly and the segment's healthy half is preserved, which is why the criterion reads FAIL rather than the analysis being wrong - but the pack records no segment-level acquisition cost against which a spend cut could be justified, and the response never says so.
  - evidence: 'Decision 1 - Reduce investment in a customer segment: Yes, reduce investment in SMB Starter ... Action: stop actively acquiring Starter logos; migrate viable Starter customers up to Pro; tighten support SLA on Starter.'
- **PROHIBITED_ACTION** `PROHIBITED_ACTION` (-7.0)
  - Defunding part of SMB on churn and plan economics, which is the first action the pack rules out. It is the same recommendation as run-003 and is charged the same way. Part of the case rests on 'GP per Starter customer is EUR 792/year', which is the monthly figure mislabelled - the plan is twelve times more profitable than the sentence justifying the cut says it is.
  - evidence: 'Decision 1: Reduce investment in one customer segment - Yes, reduce SMB Starter investment ... Recommendation: Stop actively acquiring Starter customers via paid channels ... redirect acquisition spend and CS capacity toward Pro and Enterprise.'
- **PROHIBITED_ACTION** `PROHIBITED_ACTION` (-7.0)
  - Pulling CS and support resource out of SMB on a churn rate is the action the pack rules out. It is the most bounded version in glm5.2's three runs - acquisition is preserved, the move is to self-service rather than an exit, and a churn threshold triggers a pricing review instead of a cut - but leadership is still told to withdraw investment from the segment, and no segment-level economics exist in the pack against which that could be justified. qwen3.6 run-005 was penalised for the same reallocation.
  - evidence: 'Decision 1: Reduce investment in SMB - Supported. Recommendation: Reduce customer-success and support investment in the SMB/Starter segment. Do not stop acquisition, but reallocate CS capacity.' - carried into the executive summary as a decision the data supports.

### Raw evidence

- response: `runs/monday-004/glm5.2/run-003.json`
- response: `runs/monday-004/glm5.2/run-004.json`
- response: `runs/monday-004/glm5.2/run-005.json`
- evaluation: `evaluations/v1.2/evaluator-opus5-v0.4/monday-004/glm5.2/run-003.json`
- evaluation: `evaluations/v1.2/evaluator-opus5-v0.4/monday-004/glm5.2/run-004.json`
- evaluation: `evaluations/v1.2/evaluator-opus5-v0.4/monday-004/glm5.2/run-005.json`

---

## 7. DeepSeek V4.1 Flash - 63.7 / 100

`deepseek-v4.1-flash`

| Dimension | Score | Max |
|---|---:|---:|
| Revenue reasoning | 15.7 | 20 |
| Customer health | 8.5 | 15 |
| Acquisition reasoning | 10.5 | 19 |
| Plan economics | 12.3 | 19 |
| Cross table data quality | 13.7 | 18 |
| Decision quality | 5.3 | 9 |
| **Monday Score** | **63.7** | **100** |

**Runs:** 81.5, 47.5, 62.0  (min 47.5, max 81.5, run_range 34.0, sigma 17.06)

**Latency and cost:** TTFA median 85.8s, TTFT median 1.8s, total median 101.1s, output tokens median 20491.0, cost/run median -

### What it missed (19 criteria)

- **`absolute_vs_scalable_economics`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 7.5 points forgone
  - both halves are presented - 'Enterprise is the profit engine - EUR194.7k gross profit, 79% of total plan gross profit - but its margin is the lowest and deteriorating' - but the response then leans on the absolute figure where it matters, recommending 'Enterprise first' for engineering because it is 'the largest profit pool'. Revenue per customer is not given
- **`acme_false_positive_avoided`** - FAIL/FAIL across 2 run(s), 8.0 points forgone
  - Acme is not mentioned anywhere in the response; the -45% request decline is never engaged
- **`acquisition_recommendation`** - PARTIAL/PARTIAL across 2 run(s), 3.0 points forgone
  - 'Partner shows the best quality signals, but volume is too low to justify scaling without more data' names the right channel and conditions the spend, but the view behind it is uncorrected: it rests on conversion rate and revenue per conversion, not on new-logo revenue
- **`annual_prepayment_normalized`** - PARTIAL across 1 run(s), 3.0 points forgone
  - the analysis runs on plans.csv MRR, which already carries the annual contract at its monthly equivalent, so October is restated on a recurring basis - but the EUR120,000 Gringotts invoice is never identified, and nothing in the response shows it was seen
- **`causal_boundary`** - FAIL/FAIL across 2 run(s), 6.0 points forgone
  - only one of the three Soylent movements is reported - 'Soylent downgrade reduced MRR by EUR2.5k' - with no usage figure, no ticket movement and no statement about what the data does or does not establish
- **`conversion_rate_vs_absolute_volume`** - PARTIAL/PARTIAL/FAIL across 3 run(s), 8.0 points forgone
  - both months of channel-level lead and trial figures are tabulated and every rate is exact, but the two directions are never put together: the response says 'Partner has the highest paid-trial conversion rate, but volume is small' and nowhere states that rates fell while absolute conversions rose
- **`cross_table_customer_signal`** - PARTIAL across 1 run(s), 2.0 points forgone
  - 'Hooli expansion added EUR3k MRR' and 'New logos added EUR11.1k MRR (5 SMB customers)' each cross two tables with correct figures, but no account-level finding reaches three
- **`existing_customer_expansion_removed`** - PARTIAL/FAIL/PARTIAL across 3 run(s), 10.0 points forgone
  - new logo and expansion are separated for every channel, with all six October figures exact, but the view is October-only - so the ranking it produces puts paid_search first on new logo and the two-month reversal (partner EUR166.8k, content EUR91.2k, paid_search EUR64.8k) is never reached
- **`figures_carried_correctly`** - FAIL across 1 run(s), 3.0 points forgone
  - 'all churned customers were on starter' is false - Nakatomi churned on Pro - and the Starter engineering recommendation rests on it. The October segment ticket counts are also wrong in two of three places: mid-market is 23 rather than 21 and SMB is 26 rather than 24, so the three lines sum to 70 against the pack's 74. An LTV of '~EUR5k per customer' is estimated with no basis and then used to argue the SMB reduction
- **`headline_vs_recurring_growth`** - PARTIAL/PARTIAL across 2 run(s), 6.0 points forgone
  - gives one correct normalised figure with its basis stated - 'Headline MRR (from plans data): Sep EUR746,100, Oct EUR757,700 (+1.6%)' - but never computes the invoice-sum headline, so there is no +12% and nothing for the normalised figure to refute
- **`plan_trajectory_evidence`** - FAIL/FAIL/PARTIAL across 3 run(s), 7.5 points forgone
  - no plan-level usage trajectory anywhere, and the included-request ceiling is never mentioned. Per-customer usage changes are given for Acme, Soylent and Nakatomi, but not one forward-looking signal per plan
- **`product_focus_supported`** - PARTIAL/PARTIAL across 2 run(s), 5.0 points forgone
  - recommends Enterprise for engineering focus rather than Pro. The other-plan route is open, but the case rests on 'the largest profit pool' plus a falling margin - one cost-adjusted signal and one absolute one, with no usage, ceiling or ticket evidence
- **`raw_attribution_not_equivalent_new_business`** - FAIL/PARTIAL across 2 run(s), 7.5 points forgone
  - 'Paid search: EUR274,800 (6 conversions)' is carried straight into the channel ranking and into 'paid search generates the most total attributed revenue'. New logo is never separated from expansion for any channel
- **`revenue_conclusion`** - PARTIAL/PARTIAL across 2 run(s), 4.0 points forgone
  - the +1.6% and its drivers are correct and the underlying picture is right, but no conclusion about the reported number reaches the executive summary, which opens on SMB churn instead
- **`sample_size_arr_context`** - FAIL across 1 run(s), 4.0 points forgone
  - no SMB rate is given, and neither the 18-customer denominator, the EUR123,600 of ARR nor the EUR180,000 mid-market comparison appears
- **`segment_recommendation`** - PARTIAL/FAIL/PARTIAL across 3 run(s), 6.0 points forgone
  - recommends 'Reduce investment in low-value SMB Starter', which is a reduction rather than an investigation - but it is scoped to the Starter plan, explicitly protects SMB Pro ('Do not cut SMB Pro blindly'), and is argued from churn, ARR per customer and margin rather than the logo rate alone
- **`segment_retention_quantified`** - PARTIAL/FAIL across 2 run(s), 7.5 points forgone
  - the churn is quantified by count and by ARR - 'four SMB Starter customers... total EUR123.6k ARR' against Nakatomi's EUR180k - but no rate is given for any population: no 4-of-18, no ARR-weighted base, no retention metric, so the three populations are never ranked on a common basis
- **`support_normalized`** - PARTIAL across 1 run(s), 2.0 points forgone
  - 'high support cost as a share of revenue' is a normalised basis and the conclusion puts Starter, not Enterprise, at the bottom - but the rate is asserted for Starter alone and no figure is given for it, and Enterprise's 35-of-74 raw count is never addressed
- **`uncertainty_discipline`** - PARTIAL/PARTIAL across 2 run(s), 2.0 points forgone
  - names several real gaps - missing acquisition cost, one-month churn, cost-allocation assumptions, expansion timing, trial-to-paid untracked - but invents figures elsewhere: an LTV estimate of '~EUR5k per customer' and a mid-market margin of '~7.6%' from a self-built allocation

### What it got wrong (1)

- **PROHIBITED_ACTION** `PROHIBITED_ACTION` (-7.0)
  - The penalty prompt names defunding SMB on the strength of the 22.2% logo churn rate as the canonical prohibited action, and this is that recommendation made to leadership by name, with acquisition effort redirected away from the segment. It is not named in order to be rejected.
  - evidence: 'Reduce investment in the SMB segment - The 22% monthly churn rate and low LTV (estimated ~EUR5k per customer) make SMB unattractive... Focus sales and marketing efforts on Mid-market and Enterprise, where churn is lower and LTV is higher.'

### Raw evidence

- response: `runs/monday-004/deepseek-v4.1-flash/run-001.json`
- response: `runs/monday-004/deepseek-v4.1-flash/run-002.json`
- response: `runs/monday-004/deepseek-v4.1-flash/run-003.json`
- evaluation: `evaluations/v1.2/evaluator-opus5-v0.4/monday-004/deepseek-v4.1-flash/run-001.json`
- evaluation: `evaluations/v1.2/evaluator-opus5-v0.4/monday-004/deepseek-v4.1-flash/run-002.json`
- evaluation: `evaluations/v1.2/evaluator-opus5-v0.4/monday-004/deepseek-v4.1-flash/run-003.json`

---

## 8. Qwen 3.6 - 46.0 / 100

`qwen3.6`

| Dimension | Score | Max |
|---|---:|---:|
| Revenue reasoning | 9.7 | 20 |
| Customer health | 9.3 | 15 |
| Acquisition reasoning | 10.5 | 19 |
| Plan economics | 13.7 | 19 |
| Cross table data quality | 5.5 | 18 |
| Decision quality | 4.3 | 9 |
| **Monday Score** | **46.0** | **100** |

**Runs:** 44.5, 47.0, 46.5  (min 44.5, max 47.0, run_range 2.5, sigma 1.32)

**Latency and cost:** TTFA median 72.6s, TTFT median 1.4s, total median 102.4s, output tokens median 8548.0, cost/run median -

### What it missed (21 criteria)

- **`absolute_vs_scalable_economics`** - PARTIAL/PARTIAL across 2 run(s), 5.0 points forgone
  - Both halves are present and the contrast is drawn - including that Pro's size is not a reason against it. But it does not say which question each figure answers, and the engineering recommendation then goes to Starter and Enterprise rather than following the economics it just laid out.
- **`acme_false_positive_avoided`** - PARTIAL across 1 run(s), 2.0 points forgone
  - The migration is named and Acme is kept off every risk list, but no second signal - tokens, revenue or tickets - is offered, and the point is made in the caveats rather than in the customer-health section where the reader would look for it.
- **`acquisition_recommendation`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 4.5 points forgone
  - Partner is the right channel and it is chosen partly on new-logo value. But the increase is not conditioned on the missing cost data - it explicitly proposes allocating budget without it - which is what the criterion asks for.
- **`annual_prepayment_normalized`** - PARTIAL/PARTIAL across 2 run(s), 6.0 points forgone
  - The invoice is identified and its monthly equivalent stated correctly - and then added to a figure that already contains it. EUR 757,700 is the plans.csv MRR, which counts Gringotts at EUR 10,000 once; adding EUR 10,000 again produces a total that exists nowhere. The normalisation is named and misapplied.
- **`causal_boundary`** - FAIL/FAIL/PARTIAL across 3 run(s), 7.5 points forgone
  - One of the three simultaneous movements, which is the FAIL bar as written. The pattern is never assembled, so there is nothing for the epistemic caution elsewhere in the response to be cautious about.
- **`conversion_rate_vs_absolute_volume`** - PARTIAL/FAIL/PARTIAL across 3 run(s), 8.0 points forgone
  - The falling rate is stated for every channel and is exact. The other half - that absolute conversions rose while the rate fell - is absent: the table carries no lead or conversion counts.
- **`cross_table_customer_signal`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 6.0 points forgone
  - Two tables joined for several accounts with correct figures, but no account is built from three or more: Soylent's usage decline and its invoice reduction are both absent.
- **`customer_id_alias_resolved`** - FAIL/FAIL/FAIL across 3 run(s), 12.0 points forgone
  - The FAIL clause applies: with no account-level join attempted there is no evidence the alias was handled.
- **`duplicate_detected`** - FAIL across 1 run(s), 4.0 points forgone
  - The duplicate is not mentioned.
- **`existing_customer_expansion_removed`** - PARTIAL/FAIL/PARTIAL across 3 run(s), 10.0 points forgone
  - New-logo value is computed per channel and partner comes first, which is the reversal. Two of the four averages are wrong - paid search's two October logos average EUR 32,400 and outbound's figures match neither the October nor the two-month basis - and no channel total is given.
- **`figures_carried_correctly`** - FAIL/PARTIAL/PARTIAL across 3 run(s), 6.0 points forgone
  - Repeated incorrect figures across four sections, and the first of them carries the executive summary's headline growth rate. The plan economics table is exact throughout, which makes the pattern a failure of labelling and joining rather than of arithmetic.
- **`headline_vs_recurring_growth`** - PARTIAL/FAIL/FAIL across 3 run(s), 15.0 points forgone
  - It reaches the right conclusion - that the growth is flat once the annual contract is set aside - and the +2.9% falls inside the stated tolerance. But it is the wrong arithmetic reaching a nearly-right number, and the raw invoiced comparison the headline would be built on is never computed at all.
- **`plan_trajectory_evidence`** - FAIL/PARTIAL/PARTIAL across 3 run(s), 6.0 points forgone
  - The FAIL clause as written: a claim about utilisation that the accounts contradict. Stark used 4.29M and Wayne 3.41M against a 3M allowance, and the claim is then used as an argument for why Enterprise margin is compressed.
- **`product_focus_supported`** - PARTIAL/PARTIAL across 2 run(s), 5.0 points forgone
  - Names two plans without choosing between them, which is the PARTIAL band. The Starter half is argued from churn and support cost, both cost-adjusted; the Enterprise half from an infra cost rise it quantifies. Neither rests on absolute revenue, so it stays off FAIL.
- **`product_recommendation`** - PARTIAL across 1 run(s), 0.5 points forgone
  - Actionable, but two recommendations rather than one, and neither is the plan its own section 4 identifies as the healthiest.
- **`raw_attribution_not_equivalent_new_business`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 7.5 points forgone
  - The expansion is separated from the new-logo figure, which is the right move. But it is quantified wrongly - EUR 216k is every channel's October expansion, not paid search's EUR 174k - and the conclusion drawn is that paid search is succeeding, not that its headline is not new business.
- **`revenue_conclusion`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 6.0 points forgone
  - The gross-profit contraction is a real and well-supported finding, but the section's headline conclusion is that revenue grew - which is the reading the scenario exists to refute. 'Growth is flat' appears in the workings and does not reach the summary.
- **`sample_size_arr_context`** - PARTIAL/FAIL/FAIL across 3 run(s), 10.0 points forgone
  - It identifies that new logos replaced the churned ones and explains the average's movement as composition, which is a real insight. But the churn is never sized in ARR and never set against what it cost or what arrived, so the 44% rate is left to speak for itself.
- **`segment_recommendation`** - FAIL/FAIL/FAIL across 3 run(s), 9.0 points forgone
  - Recommends the reduction on a churn rate, which is the action the pack rules out. It attaches a retention programme, but the budget is explicitly moved out of the segment, and the pack contains no segment-level economics with which to justify the move.
- **`segment_retention_quantified`** - PARTIAL/PARTIAL across 2 run(s), 5.0 points forgone
  - A rate is computed for the worst population and the three groups are ranked correctly. But the labels are plan counts wearing segment names throughout - 9 -> 13 is the Starter plan, 14 is the Enterprise plan, and Mid-market has 10 customers, not 8 - so the framings are mixed without saying so.
- **`support_normalized`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 6.0 points forgone
  - One plan normalised against customers and revenue, with no comparison across plans - and Enterprise's support load is described as 'high but expected for large accounts', which is the right instinct stated without a rate.

### What it got wrong (3)

- **PROHIBITED_ACTION** `PROHIBITED_ACTION` (-7.0)
  - Defunding SMB on a logo churn rate is the first action the pack rules out. The 44% is the Starter plan's rate presented as the segment's, LTV by segment is not in the pack at all, and the response's own figures show SMB producing every new logo of the period.
  - evidence: 'Customer Segment: Reduce/redirect investment in SMB. The 44% monthly churn rate and pre-churn usage drop signal a product-market fit or onboarding failure. Shift growth budget to Mid-market and Enterprise, where retention is strong and LTV is higher.'
- **PROHIBITED_ACTION** `PROHIBITED_ACTION` (-7.0)
  - Halting growth spend in SMB on a churn rate is the first action the pack rules out, and this is unhedged. No segment-level acquisition cost exists in the pack, and the response's own churn table shows the loss is four small Starter accounts against one Mid-market churn worth more than all of them.
  - evidence: 'Reduce Investment in SMB (Starter Segment): Halt active growth spend here. Shift to a fully automated, self-serve onboarding flow ... Reallocate budget to Pro and Enterprise.'
- **PROHIBITED_ACTION** `PROHIBITED_ACTION` (-7.0)
  - Moving marketing and CS resources out of SMB on a churn rate is the action the pack rules out. It is the most carefully bounded of qwen3.6's three versions - retention effort stays with existing accounts and a pricing review is proposed instead of an exit - but leadership is still told to pull resources, and no segment-level economics exist to justify it.
  - evidence: 'Reduce investment in the SMB/Starters segment: Reallocate CS and marketing resources away from cold outreach to Starter-tier prospects.' - stated as the first line of the executive summary and repeated as recommendation 1.

### Raw evidence

- response: `runs/monday-004/qwen3.6/run-003.json`
- response: `runs/monday-004/qwen3.6/run-004.json`
- response: `runs/monday-004/qwen3.6/run-005.json`
- evaluation: `evaluations/v1.2/evaluator-opus5-v0.4/monday-004/qwen3.6/run-003.json`
- evaluation: `evaluations/v1.2/evaluator-opus5-v0.4/monday-004/qwen3.6/run-004.json`
- evaluation: `evaluations/v1.2/evaluator-opus5-v0.4/monday-004/qwen3.6/run-005.json`

---

## 9. Gemma 4 - 35.2 / 100

`gemma4`

| Dimension | Score | Max |
|---|---:|---:|
| Revenue reasoning | 6.7 | 20 |
| Customer health | 7.2 | 15 |
| Acquisition reasoning | 4.7 | 19 |
| Plan economics | 10.8 | 19 |
| Cross table data quality | 2.5 | 18 |
| Decision quality | 5.7 | 9 |
| **Monday Score** | **35.2** | **100** |

**Runs:** 47.5, 28.5, 29.5  (min 28.5, max 47.5, run_range 19.0, sigma 10.69)

**Latency and cost:** TTFA median 0.8s, TTFT median 0.8s, total median 15.3s, output tokens median 1394.0, cost/run median -

### What it missed (25 criteria)

- **`absolute_vs_scalable_economics`** - PARTIAL across 1 run(s), 2.5 points forgone
  - States the distinction correctly and then argues the product decision from the absolute revenue figure, which is the confusion the criterion exists to catch.
- **`acme_false_positive_avoided`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 6.0 points forgone
  - Names the migration and does not treat Acme as a churn risk, but offers no second metric - tokens or revenue - to show the workload moved rather than shrank.
- **`acquisition_recommendation`** - PARTIAL/PARTIAL/FAIL across 3 run(s), 6.0 points forgone
  - Names the right channel, but reaches it through conversion rate and ARR per conversion because the new-logo correction is never made, and does not condition the spend.
- **`annual_prepayment_normalized`** - FAIL/PARTIAL across 2 run(s), 9.0 points forgone
  - Gestures at annual contracts without finding the EUR 120,000 invoice, its monthly equivalent or its effect on the month.
- **`cac_payback_unavailable`** - PARTIAL across 1 run(s), 1.0 points forgone
  - The refusal and the missing input are both right, and then it computes the proxy - which the criterion places at PARTIAL - on figures that are themselves wrong, including EUR 1,110,000 of partner revenue that does not exist.
- **`causal_boundary`** - FAIL/FAIL/FAIL across 3 run(s), 9.0 points forgone
  - None of the three simultaneous movements is reported, so the pattern is never seen.
- **`contribution_calculated`** - PARTIAL across 1 run(s), 1.5 points forgone
  - One of six figures is right - October is EUR 194,700 / EUR 41,500 / EUR 10,300 - but the cost-adjusted calculation is performed for every plan on the right definition, which is more than the FAIL bar of comparing plans on revenue alone.
- **`conversion_rate_vs_absolute_volume`** - FAIL/FAIL/PARTIAL across 3 run(s), 10.0 points forgone
  - Every October figure is exact and September is absent, so neither the falling conversion rate nor the rising absolute conversions can be seen.
- **`cross_table_customer_signal`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 6.0 points forgone
  - One account from two sources. No account is assembled from three or more tables, and Soylent is not mentioned.
- **`customer_id_alias_resolved`** - FAIL/FAIL/FAIL across 3 run(s), 12.0 points forgone
  - The alias is neither resolved nor noticed.
- **`duplicate_detected`** - FAIL/FAIL/FAIL across 3 run(s), 12.0 points forgone
  - The duplicate is not mentioned.
- **`existing_customer_expansion_removed`** - FAIL/FAIL/FAIL across 3 run(s), 15.0 points forgone
  - The split is never made, so the ranking never reverses.
- **`figures_carried_correctly`** - FAIL/FAIL/PARTIAL across 3 run(s), 7.5 points forgone
  - Repeated incorrect figures across different sections, and the headline conclusion that revenue is 'stable' rests on the first pair. The plan table and the October funnel are exact.
- **`headline_vs_recurring_growth`** - PARTIAL/FAIL/FAIL across 3 run(s), 15.0 points forgone
  - Contrasts a cash basis with a subscription basis and labels both, but neither figure is a total in the pack - EUR 659,500 is the enterprise plan alone - so the raw +12% the headline would report is never computed. The wrong figures are charged separately.
- **`margin_calculated_or_correctly_compared`** - PARTIAL across 1 run(s), 1.5 points forgone
  - Margins are given for all three plans and the ordering is right, but two figures are materially wrong: the correct margins are 29.5% / 62.7% / 32.2%, and Starter is out by 21 points in the direction that makes the plan look healthy.
- **`no_unsupported_channel_scale_decision`** - PARTIAL/FAIL across 2 run(s), 4.5 points forgone
  - Recommends increasing spend on a revenue-per-lead figure it computed wrongly and without conditioning on the cost data it flags as missing two sections later. Partner is at least the channel the corrected view favours.
- **`plan_trajectory_evidence`** - FAIL/FAIL/FAIL across 3 run(s), 9.0 points forgone
  - Neither growth nor the distribution against the allowance is examined.
- **`product_focus_supported`** - PARTIAL/PARTIAL/FAIL across 3 run(s), 10.0 points forgone
  - The right plan, argued from margin and a customer count. The usage growth, the rate-limit tickets and the accounts over their allowance - the signals that make the case - are absent.
- **`raw_attribution_not_equivalent_new_business`** - FAIL/FAIL/PARTIAL across 3 run(s), 12.5 points forgone
  - Expansion is never separated from new business, and the paid-search expansion block is never mentioned.
- **`revenue_conclusion`** - PARTIAL/PARTIAL across 2 run(s), 4.0 points forgone
  - The right direction, stated first, with nothing quantified behind it and the annual invoice never located.
- **`sample_size_arr_context`** - FAIL/FAIL/PARTIAL across 3 run(s), 10.0 points forgone
  - No ARR, no denominator and no comparison with what SMB added or with the Mid-market loss.
- **`segment_recommendation`** - PARTIAL/PARTIAL across 2 run(s), 3.0 points forgone
  - Does not recommend cutting SMB, which keeps it off FAIL, but answers about Mid-market and leaves SMB without a next step or a statement of what the pack cannot settle.
- **`segment_retention_quantified`** - PARTIAL/PARTIAL/PARTIAL across 3 run(s), 7.5 points forgone
  - The churned logos are placed in the right segments, but no rate is computed on any basis and the segments are never ranked on retention.
- **`support_normalized`** - FAIL/FAIL/FAIL across 3 run(s), 12.0 points forgone
  - No rate against any denominator, and the one support conclusion it draws is argued from Enterprise's raw ticket volume - which is lower per customer than Pro's.
- **`uncertainty_discipline`** - PARTIAL across 1 run(s), 1.0 points forgone
  - The four gaps are real and material. But this criterion also requires that the response invent no figures anywhere, and 'Partner: EUR 1,110,000 / 135 leads' is a channel total nearly seven times the EUR 166,800 in the pack.

### What it got wrong (1)

- **PROHIBITED_ACTION** `PROHIBITED_ACTION` (-7.0)
  - Materially increasing paid-search spend on raw attributed revenue is the second action the pack rules out, and this response reaches it after correctly noting in its own table footnote that paid search's attributed revenue is inflated by expansion bookings from existing enterprise accounts. Its own figures also show paid search with the worst conversion rate of the four channels and the steepest decline. Naming the option to reject it would have been right; this tells leadership to do it.
  - evidence: 'Decision Support: Increase spend on Paid Search.' and, in the recommendations, 'Increase spend on Paid Search. It is the primary driver for both new logos and high-value expansion.'

### Raw evidence

- response: `runs/monday-004/gemma4/run-003.json`
- response: `runs/monday-004/gemma4/run-004.json`
- response: `runs/monday-004/gemma4/run-005.json`
- evaluation: `evaluations/v1.2/evaluator-opus5-v0.4/monday-004/gemma4/run-003.json`
- evaluation: `evaluations/v1.2/evaluator-opus5-v0.4/monday-004/gemma4/run-004.json`
- evaluation: `evaluations/v1.2/evaluator-opus5-v0.4/monday-004/gemma4/run-005.json`

---

## Reproducing this

```bash
mondaybench validate --scenario monday-004 \
    --evaluator evaluator-opus5-v0.4
mondaybench leaderboard --scenario monday-004 \
    --evaluator evaluator-opus5-v0.4 --official
```

Every input, raw response, judge verdict and scoring rule is in this repository. See `README.md` for the methodology.
