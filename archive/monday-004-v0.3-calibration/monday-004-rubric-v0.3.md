# monday-004 rubric v0.3 — the figure-accuracy criterion, and the second shadow rescore

**Proposed. Nothing frozen, nothing published.** v0.3 is v0.2 plus one criterion
and three repricings. `rubric.yaml` (0.1) and `rubric-0.2.yaml` are both intact
and still reproduce the scores derived from them.

- Rubric: `scenarios/monday-004/rubric-0.3.yaml` — 27 criteria, 100 points
- Evaluator: `evaluators/evaluator-opus5-v0.4-calibration-3.yaml`
- Shadow verdicts: `verdicts/monday-004/shadow-v0.3.jsonl`
- Candidate prompt unchanged: `3a0cbb569ca4f711b8907177af9204cec267d26f35f732829df56b03ed23ef99`,
  verified under all three rubrics

---

## Why

The v0.2 shadow rescore gave Qwen 3.8 Flash 100.0. Its answer cites three
figures that are not in the pack and reports a Pro token trajectory that its own
correct request trajectory contradicts. No criterion in v0.1 or v0.2 asks whether
the figures a response quotes are the figures in the data — so in a benchmark
whose subject is quantitative business analysis, quantitative accuracy was the
one thing unscored.

monday-003 hit this and closed it with `factual_plan_accuracy` in its rubric 0.3,
after GLM 5.3 Flash wrote "Wed 15:00" for a Thursday milestone inside an answer
that scored 100.0. This is the same criterion for this scenario.

## What moved, and its measured variance

| criterion | v0.2 | v0.3 | v0.1 labels | v0.2 labels | v0.1 sd | v0.2 sd |
|---|---:|---:|---|---|---:|---:|
| `figures_carried_correctly` | — | **3** | new | new | — | — |
| `cac_payback_unavailable` | 3 | **2** | `+ + + + + +` | `+ + + + + +` | 0.00 | 0.00 |
| `contribution_calculated` | 4 | **3** | `+ + + + + +` | `+ + + + + +` | 0.00 | 0.00 |
| `product_recommendation` | 2 | **1** | `+ + + + + +` | `+ + + + + +` | 0.00 | 0.00 |

All three funders scored 6/6 PASS under both rubrics: they are the only places
in v0.2 where points could come from without removing something that separates
models. Two more criteria are also zero-variance in v0.2 —
`margin_calculated_or_correctly_compared` (3) and `uncertainty_discipline` (2) —
and were left alone: the first is already repriced once and the second is the
"knowing when the data runs out" skill the scenario exists to measure.

Dimension totals move to 20 / 15 / 19 / 19 / 18 / 9 and still sum to 100.

## The criterion

Scoped narrowly, and explicitly not a requirement to reproduce the answer key:

- only figures the candidate **uses** are scored; an omission is never an error;
- reasonable rounding and a differently-stated basis both pass;
- an error another criterion already prices is **not** charged again.

The last point does real work here. Wrong joins stay with
`customer_id_alias_resolved`, missed duplicates with `duplicate_detected`,
unnormalised annual invoices with `annual_prepayment_normalized`, wrong churn
denominators with `segment_retention_quantified`, and misread plan averages with
`plan_trajectory_evidence`. Two of the six runs pass this criterion precisely
because their only figure errors are already priced elsewhere.

## Second shadow rescore

Same six responses. No model regenerated. 162 verdict entries carried from the
v0.2 shadow unchanged — a reprice moves no label — and six
`figures_carried_correctly` labels judged fresh.

| model | v0.1 | v0.2 | v0.3 | Δ v0.2→v0.3 | `figures_carried_correctly` |
|---|---:|---:|---:|---:|---|
| Qwen 3.8 Flash | 97.5 | 100.0 | **98.5** | −1.5 | PARTIAL |
| GLM 5.3 Flash | 92.5 | 95.0 | **93.5** | −1.5 | PARTIAL |
| GLM 5.2 | 86.0 | 86.0 | **86.0** | 0.0 | PASS |
| DeepSeek V4 Flash | 79.0 | 74.0 | **74.0** | 0.0 | PASS |
| Gemma 4 | 42.0 | 40.5 | **37.5** | −3.0 | FAIL |
| Qwen 3.6 | 38.5 | 39.0 | **37.5** | −1.5 | PARTIAL |

Penalties unchanged: GLM 5.2 −7, Qwen 3.6 −7 and −5.

| | v0.1 | v0.2 | v0.3 |
|---|---:|---:|---:|
| spread | 59.0 | 61.0 | **61.0** |
| mean | 72.6 | 72.4 | **71.2** |
| median | 82.5 | 80.0 | **80.0** |
| constant point mass | 21 | 14 | **11** |
| discriminating criteria | 19/25 | 21/26 | **22/27** |
| scores ≥ 95 | 1 | 2 | **1** |

The criterion discriminates immediately — PASS, PARTIAL and FAIL all appear
across six runs — and constant mass falls again.

### The verdicts, one by one

**Qwen 3.8 Flash — PARTIAL.** Pro September tokens given as 2,725.5M against
2,425.5M; Pro active users as 338 and 364 against 288 and 331. The wrong
September token value produces a "+2.1%" Pro token trajectory that reads against
the "+14.8%" request trajectory the same response states correctly two lines
above. Nothing rests on any of them: the Pro recommendation is carried by the
request growth, the margin and the three accounts over their included volume,
all exact.

Graded PARTIAL, and the alternative is worth stating because it is defensible:
the FAIL band names "repeated incorrect figures", and three is repeated. PARTIAL
was chosen because the three are one lapse in one sub-table rather than errors
spread through the analysis, and because the divergence is not a stated
self-contradiction — a falling tokens-per-request ratio is a real phenomenon in
this very pack, which is what Acme's whole trap turns on. Under the stricter
reading Qwen 3.8 Flash scores 97.0 rather than 98.5.

**GLM 5.3 Flash — PARTIAL.** "Enterprise has 8 of 14 customers with high-severity
api_errors or performance tickets in October" — the count is 7. Its own list
names nakatomi, which is on the pro plan. Everything else checkable is exact:
support volume 59 → 74, unresolved backlog 20 → 24, api-error tickets 10 → 12,
blended margin 35.2% → 32.5%, SMB new ARR €247.2k, Mid-market −€42k.

**GLM 5.2 — PASS.** Its only figure error, "SMB churned 4 of 14 … 28.6% MoM
churn", is already priced at PARTIAL under `segment_retention_quantified`.

**DeepSeek V4 Flash — PASS.** Both its errors are already priced: "4 of 4 churned
customers were SMB Starter" under `segment_retention_quantified`, and "All plans
are below included request volumes" under `plan_trajectory_evidence`, where it
is the FAIL.

**Gemma 4 — FAIL.** "September Total Revenue: €673,100 … October Total Revenue:
€754,400". Neither is any total in the pack on any basis — the raw sums are
€797,100 and €892,900, the deduplicated October is €873,400, the recurring pair
is €746,100 and €757,700 — and the executive summary's "high-growth revenue"
rests on them. This is not the error the revenue criteria price: those price the
failure to normalise, and a response can fail to normalise and still sum
correctly, which is exactly what DeepSeek did.

**Qwen 3.6 — PARTIAL.** "September Subscription Revenue: €646,100 … October
€657,700", contradicted three paragraphs later by its own correct €746,100 and
€757,700 from plans.csv, never reconciled. Held at PARTIAL rather than FAIL
because `revenue_conclusion` already cited this contradiction as part of why it
sits at PARTIAL there.

## Every score ≥ 95, audited

One: **Qwen 3.8 Flash at 98.5.**

I checked every figure in the response that the pack can verify. Exact: raw and
deduplicated revenue totals; all five growth bases including both accepted
normalisations; the €8,953.2k → €8,788.8k ARR walk; GRR 96.7% and NRR 98.2%;
segment MRR and active MRR; the full attributed-revenue split by channel and
month; the funnel; all six contribution figures and margins; contribution per
customer; tickets per active customer and per €100k MRR by segment; plan
utilisation at 63.0% / 73.6% / 42.2%; enterprise-plan tokens 29,194M → 30,605M;
enterprise segment requests 22.00M → 21.59M, tokens 24,200M → 25,275M, users
+6.1%; mid-market 6.68M → 7.26M; SMB 2.36M → 2.66M.

Wrong: the three Pro-plan usage figures above, and nothing else.

**Is it a perfect answer? No — and it no longer scores as one.** It gets every
decision and every trap right, it is the best of the seven by a clear margin, and
it contains three figures that are not in the data. 98.5 is the honest number:
full credit for the analysis, a half-credit deduction for the arithmetic that
carries none of it. The failure was not manufactured to create headroom — it was
found by checking the response against the CSVs, and it is documented to the
digit.
