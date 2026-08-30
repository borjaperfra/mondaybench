# monday-004 rubric v0.2 — proposal and shadow rescore

**Proposed, not adopted. Nothing is frozen and no model was regenerated.**

- Rubric: `scenarios/monday-004/rubric-0.2.yaml` (new file; `rubric.yaml` v0.1 is
  untouched and still reproduces the calibration scores)
- Shadow evaluator: `evaluators/evaluator-opus5-v0.4-calibration-2.yaml`
- Shadow verdicts: `verdicts/monday-004/shadow-v0.2.jsonl`, built by
  `analysis/_monday_004_shadow_v02.py`
- Shadow evaluations: `evaluations/evaluator-opus5-v0.4-calibration-2/monday-004/`

**Candidate-visible files are byte-identical.** The rendered prompt still hashes
to `3a0cbb569ca4f711b8907177af9204cec267d26f35f732829df56b03ed23ef99` under both
rubrics — verified, not assumed. Nothing in `source_order` changed, so the six
qualifying v0.1 responses are valid evidence for v0.2 and the shadow rescore is a
rescore, not a re-run.

---

## What changed, and the variance that justifies it

Measured across the six qualifying v0.1 runs. `sd` is the population standard
deviation of the points awarded; a criterion with sd 0.00 gave every model the
same score and separated nothing.

| criterion | v0.1 | v0.2 | v0.1 labels | v0.1 sd | why |
|---|---:|---:|---|---:|---|
| `segment_churn_math` → `segment_retention_quantified` | 5 | 5 | `~ . ~ ~ ~ ~` | 0.93 | rewritten, see Part C |
| `contribution_calculated` | 6 | **4** | `+ + + + + +` | **0.00** | floor arithmetic, priced as a floor |
| `margin_calculated_or_correctly_compared` | 4 | **3** | `+ + + + + +` | **0.00** | one division on top of it |
| `enterprise_revenue_not_margin` | 4 | **removed** | `+ + + + + +` | **0.00** | noticing the contrast measured nothing |
| `absolute_vs_scalable_economics` | — | **5** | new | — | scores what follows from the contrast |
| `plan_trajectory_evidence` | — | **3** | new | — | unbundles evidence `product_focus_supported` absorbed |
| `product_focus_supported` | 6 | **5** | `~ + + ~ + +` | 1.41 | discriminates; one point moves out to avoid paying twice |
| `support_normalized` | 4 | 4 | `+ ~ + . . ~` | 1.63 | denominators clarified, no points move |
| `customer_id_alias_resolved` | 4 | 4 | `+ + + . . .` | 2.00 | never-attempted case named, no points move |

Everything in `revenue_reasoning`, `acquisition_reasoning` and
`decision_quality` is unchanged. Dimension totals: 20 / 15 / 20 / 20 / 15 / 10 =
100, as before. 26 criteria, up from 25.

Full label key: `+` PASS, `~` PARTIAL, `.` FAIL, in the order Qwen 3.8 Flash,
GLM 5.3 Flash, GLM 5.2, DeepSeek V4 Flash, Gemma 4, Qwen 3.6.

---

## Part C — `segment_retention_quantified`

**The problem.** v0.1's `segment_churn_math` asked for logo churn by segment.
Nobody passed it. Five of six runs scored PARTIAL and one FAILed, and the reason
was the same in four of the five: they computed something better. Qwen 3.8 Flash
produced ARR-weighted churn and per-segment NRR. GLM 5.3 Flash produced net ARR
movement per segment. Neither wrote "4 of 18". The criterion measured the
representation, not the reasoning, and cost each of them 2.5 points for
answering the business question with the metric that answers it.

**The rewrite.** PASS now requires the retention problem to be quantified
correctly and the populations ranked correctly, on **any** of:

- logo churn — SMB 4 of 18 (22.2%), Mid-market 1 of 10, Enterprise 0 of 8;
- ARR-weighted churn — SMB €123,600 on a base of about €602,400;
- gross or net revenue retention by segment.

Plan-level equivalents (Starter 4 of 13, Pro 1 of 9, Enterprise plan 0 of 14)
pass too, provided they are labelled as plan rather than segment. The framing
must be stated and used consistently, and the figures must support whatever the
response concludes from them.

**Double-counting, checked explicitly.** The four ideas that could have been
spread across criteria each live in exactly one place:

| idea | scored by | not scored by |
|---|---|---|
| SMB has 4 churned logos out of 18 | `segment_retention_quantified` | — |
| the ARR impact is not proportionate to the logo share | `sample_size_arr_context` | — |
| one Mid-market churn destroys more ARR than four SMB churns | `sample_size_arr_context` | — |
| the evidence does not justify exiting SMB | `segment_recommendation` | — |

`segment_retention_quantified` is deliberately scoped to the quantification and
says nothing about the disproportion or the decision. Nothing moved between
criteria; the boundary was already clean and is now stated in the rubric.

**Effect on the six runs.**

| model | v0.1 | v0.2 | why |
|---|---|---|---|
| Qwen 3.8 Flash | PARTIAL | **PASS** | ARR-weighted churn plus per-segment NRR, labelled and ranked |
| GLM 5.3 Flash | PARTIAL | **PASS** | churned ARR per segment plus net movement, labelled |
| GLM 5.2 | PARTIAL | PARTIAL | "4 of 14" is not a valid SMB denominator on any basis |
| DeepSeek V4 Flash | PARTIAL | PARTIAL | correct 20.5% ARR rate, but "4 of 4 churned were SMB" contradicts its own table |
| Gemma 4 | FAIL | FAIL | no churn figure at all; Starter counts labelled as SMB |
| Qwen 3.6 | PARTIAL | PARTIAL | SMB churn quantified in ARR, no rate, no ranking |

From 0 PASS to 2 PASS, and the two that now pass are the two that did the better
analysis. The three that stay at PARTIAL stay there for real errors, not for
choosing a different metric.

---

## Part D — plan economics

**What was measured, and what was not.** The dimension was 20 points and 14 of
them had zero variance:

```
contribution_calculated                  6   + + + + + +   sd 0.00
margin_calculated_or_correctly_compared  4   + + + + + +   sd 0.00
enterprise_revenue_not_margin            4   + + + + + +   sd 0.00
product_focus_supported                  6   ~ + + ~ + +   sd 1.41
```

Gemma 4 and Qwen 3.6 — the two models that could not read the revenue file at
all — both scored 20/20 here. That is the signal that the dimension was not
measuring business reasoning.

**Which parts are floor and which are reasoning.** `plans.csv` puts
`revenue_eur`, `infra_cost_eur` and `support_cost_eur` in one row. Contribution
is one subtraction and margin is one division. Both are prerequisites: you
cannot say anything about plan economics without them, and a model that gets
them wrong must lose something real. Neither is a skill this cohort lacks.

`enterprise_revenue_not_margin` looks like interpretation but behaved like a
floor: once a model had the two columns, noticing that the biggest plan has the
worst margin was automatic. All six noticed. Two then went on to recommend
Enterprise for product priority **because it is the biggest** — so noticing the
contrast and understanding what it is for turned out to be different things, and
only the first was scored.

**The arithmetic is not made harder.** No data file changed. The same
subtraction earns 4 instead of 6 and the same division earns 3 instead of 4, and
the 4 freed points plus the 4 released by removing `enterprise_revenue_not_margin`
fund two criteria that ask what the numbers are for:

**`absolute_vs_scalable_economics` (5)** — hold both halves and say which
question each answers. Enterprise leads on absolute contribution (€194,700
against €41,500) and on revenue per customer (€47,107 against €7,356), and is
the weakest on margin (29.5% against 62.7%). A question about where the revenue
is takes the first; a question about which economics scale takes the second. A
response that draws the contrast and then argues product priority from the
absolute figure gets PARTIAL.

| model | label | |
|---|---|---|
| Qwen 3.8 Flash | PASS | routes product to margin, revenue-protection to Enterprise |
| GLM 5.3 Flash | **PARTIAL** | "Pro is the margin engine", then focuses Enterprise "defending 87% of MRR" |
| GLM 5.2 | PASS | |
| DeepSeek V4 Flash | **PARTIAL** | "lowest margin", then "deserves the most attention... generates the majority of revenue" |
| Gemma 4 | PASS | "While Enterprise brings the most revenue, the Pro plan has superior unit economics" |
| Qwen 3.6 | PASS | |

**`plan_trajectory_evidence` (3)** — quantify a forward-looking usage signal:
Pro requests up ~14.8% against a flat Enterprise book, or the customers already
above their included volume (three of nine on Pro against a 600,000 allowance).
Reading the distribution rather than the plan average is the point.

| model | label | |
|---|---|---|
| Qwen 3.8 Flash | PASS | +14.8% and the three accounts named |
| GLM 5.3 Flash | PASS | wonka 1.02M, aperture 705k, vandelay 690k |
| GLM 5.2 | PASS | separates the accounts above the line from those below |
| DeepSeek V4 Flash | **FAIL** | "All plans are below included request volumes" — true of the averages, false of five customers |
| Gemma 4 | PARTIAL | names the ceiling, no figure |
| Qwen 3.6 | PARTIAL | "healthy usage growth", never computed |

This is the criterion that finally prices DeepSeek's aggregate error. v0.1
charged it nowhere: it was the one place the scenario's own thesis — that
averages hide the customers — went unmeasured.

**Dimension variance, before and after.**

| | v0.1 | v0.2 |
|---|---|---|
| zero-variance points in the dimension | 14 of 20 | **7 of 20** |
| scores across the six runs | 20, 17, 20, 17, 20, 20 | 20, 15, 20, 12, 18.5, 18.5 |
| range | 3.0 | **8.0** |

---

## Part E — shadow rescore

Six qualifying v0.1 responses, rescored under rubric 0.2. **No model was
regenerated.** Of the 156 criterion labels, 136 were carried across unchanged
(same criterion, same wording, same response) and 20 were re-judged or newly
judged; every one of the 20 is listed with its reasoning in
`analysis/_monday_004_shadow_v02.py`.

| model | v0.1 base | v0.1 final | v0.2 base | v0.2 final | delta |
|---|---:|---:|---:|---:|---:|
| Qwen 3.8 Flash | 97.5 | 97.5 | 100.0 | **100.0** | **+2.5** |
| GLM 5.3 Flash | 92.5 | 92.5 | 95.0 | **95.0** | **+2.5** |
| GLM 5.2 | 93.0 | 86.0 | 93.0 | **86.0** | 0.0 |
| DeepSeek V4 Flash | 79.0 | 79.0 | 74.0 | **74.0** | **−5.0** |
| Gemma 4 | 42.0 | 42.0 | 40.5 | **40.5** | −1.5 |
| Qwen 3.6 | 50.5 | 38.5 | 51.0 | **39.0** | +0.5 |

**Dimension changes.** Only two dimensions move at all.

| model | customer health | plan economics | cross-table |
|---|---|---|---|
| Qwen 3.8 Flash | 12.5 → **15.0** | 20.0 → 20.0 | 15.0 → 15.0 |
| GLM 5.3 Flash | 12.5 → **15.0** | 17.0 → **15.0** | 13.0 → **15.0** |
| GLM 5.2 | 12.5 → 12.5 | 20.0 → 20.0 | 13.5 → 13.5 |
| DeepSeek V4 Flash | 12.5 → 12.5 | 17.0 → **12.0** | 5.5 → 5.5 |
| Gemma 4 | 4.0 → 4.0 | 20.0 → **18.5** | 3.5 → 3.5 |
| Qwen 3.6 | 6.5 → 6.5 | 20.0 → **18.5** | 4.0 → **6.0** |

**Penalties: unchanged.** GLM 5.2 −7 (PROHIBITED_ACTION), Qwen 3.6 −7 + −5. The
penalty scale and definitions are identical in v0.2 and no new penalty fires.

**Statistics.**

| | v0.1 | v0.2 |
|---|---:|---:|
| spread | 59.0 | **61.0** |
| mean | 72.6 | 72.4 |
| median | 82.5 | 80.0 |
| constant point mass | 21 / 100 | **14 / 100** |
| discriminating criteria | 19 / 25 | **21 / 26** |
| scores ≥ 95 | 1 | **2** |

Every headline moves the right way: more spread, a third less constant mass, two
more criteria doing work. The middle of the table separates — DeepSeek falls 5
points on two real errors that v0.1 could not see, and the gap between it and
GLM 5.2 widens from 7.0 to 12.0.

---

## The 100.0, audited

Qwen 3.8 Flash reaches 100.0 under v0.2: 26 of 26 criteria at PASS, no
penalties. The question is whether that is a perfect answer or a blind rubric.

**It is not a perfect answer.** Three figures in it are wrong.

I checked every number in the response that the answer key can verify — raw and
deduplicated revenue totals, all growth bases, the €8,953.2k → €8,788.8k ARR
walk, GRR 96.7% and NRR 98.2%, segment MRR and active MRR, the full attributed
revenue split by channel and by month, the funnel, all six contribution figures
and margins, per-customer contribution, tickets per active customer and per
€100k MRR by segment, plan utilisation percentages, and enterprise-plan token
totals of 29,194M → 30,605M. Almost all of it is exact. Three things are not,
all inside the Pro plan's usage block:

| figure | stated | actual |
|---|---:|---:|
| Pro September tokens | 2,725.5M | **2,425.5M** |
| Pro September active users | 338 | **288** |
| Pro October active users | 364 | **331** |

And one consequence: it reports **"Pro tokens: +2.1%"** two lines below its own
correct **"Pro requests: 3.465M → 3.977M = +14.8%"**. Those two cannot both be
true of the same plan over the same period, and the response never notices.

**Why no criterion catches it.** Because nothing in v0.1 or v0.2 scores whether
the figures a response quotes are the figures in the data. `plan_trajectory_evidence`
asks for *at least one* correct quantified signal and it supplied two.
`contribution_calculated` and `margin_calculated_or_correctly_compared` cover the
plan P&L, which is exact. The wrong numbers sit in a sub-table no criterion
reaches, and no conclusion rests on them — which is precisely why they survive.

monday-003 met this and solved it. Its rubric 0.3 added `factual_plan_accuracy`
after GLM 5.3 Flash wrote "Wed 15:00" for a Thursday milestone inside an answer
that scored 100.0. **monday-004 has no equivalent criterion, and this is the same
failure in the same place in the scoring.**

**Proposed, and deliberately NOT applied:**

```yaml
- id: figures_carried_correctly
  points: 3
  partial_points: 1.5
  pass: >
    Every figure the response quotes from the pack, or derives from it, matches
    the data within the stated tolerance, and the response does not contradict
    itself on any figure it states twice.
  partial: >
    One incorrect figure that no conclusion rests on, or one internal
    inconsistency between two figures the response itself states.
  fail: >
    Several incorrect figures, or one that a stated conclusion depends on.
```

Funded from the three criteria that still have zero variance in v0.2 —
`cac_payback_unavailable` (3, 6/6 PASS), `product_recommendation` (2, 6/6) and
`uncertainty_discipline` (2, 6/6) — one point each.

I have not applied it, for two reasons. It is outside the two changes this
revision was scoped to; and applying it would manufacture exactly the sub-100
result the brief warned against inventing. Under it, Qwen 3.8 Flash would score
PARTIAL (one wrong figure block, one self-contradiction) and land at 98.5.
That is a decision about what #004 should measure, and it is yours.

**The honest summary:** Qwen 3.8 Flash's answer is the best of the seven by a
clear margin, it gets every decision and every trap right, and it is not
perfect. The 100.0 is the rubric's blind spot, not the model's achievement.
