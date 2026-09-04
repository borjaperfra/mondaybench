# Provisional model capability aggregation

Capability profiles for the two **PROVISIONAL, off-benchmark** models, computed
by the same canonical aggregation the seven published models use.

These artifacts do **not** make either model official. They live under
`audits/` and not in `analysis/capability-profiles-v0.2.json`, which is the
official seven built from official evaluations.

---

## Method

Nothing here reimplements the aggregation. `build-provisional-capabilities.py`
is an **adapter**: it turns two off-benchmark verdict sets into the same
`{scenario: {model: {criterion: (mean_earned, possible)}}}` shape that
`official_criterion_results` produces, and hands it to
**`mondaybench.capabilities.build_profiles`** — the canonical implementation,
unmodified.

The canonical definition, from `mondaybench/capabilities.py`:

```
capability = points earned on its criteria / points available on those criteria x 100
```

with the following rules, all taken from the existing code rather than restated:

* **Primary mappings only.** A criterion with a secondary tag contributes its
  points once, to its primary capability. 26 of the 119 mappings carry a
  secondary tag and none of them contributes points.
* **Each criterion is averaged across the model's three runs first**, then
  summed. This is what makes a capability profile reconcile with the scenario
  score: the scenario score is the mean of the run totals, and the mean of the
  totals equals the total of the means. Summing all runs and dividing by all
  possible would give a different, wrong answer.
* **Global penalties are excluded.** The calculator never reads them.
* **The noise dimension enters as a single pseudo-criterion**
  (`monday-001.noise_resistance`) carrying the dimension's own score, because
  the false-action deduction arithmetic belongs to the scoring module.
* **Rubric resolution matters.** The rubric used is the one each scenario's
  *official evaluator* declares, not `load_scenario`'s default — monday-001
  declares no `rubric_file`, so the default returns the superseded 0.1 rubric
  while the scenario is frozen against `rubric-0.2.yaml`.
* Status labels play no part in the arithmetic.

**Taxonomy v0.2**: 22 capabilities, 119 criterion mappings, 500 points across
all five scenarios. This is the taxonomy the published site artifact uses.

The canonical definition matches the expected one in the request, with one
addition worth stating: the per-criterion averaging across runs happens *before*
summation. That is the existing code's behaviour and it is what has been used.

---

## Reproduction check

Before publishing anything, the same builder was pointed at the official
evaluations and compared against the published artifact, field by field —
`percent`, `earned` (2 dp), `possible` and `criteria` count, for all 22
capabilities:

| Model | Capabilities | Exact match |
|---|---:|---|
| Qwen 3.8 Flash | 22 | **yes** |
| GLM 5.3 Flash | 22 | **yes** |
| DeepSeek V4 Flash | 22 | **yes** |
| MIMO v2.5 | 22 | **yes** |
| GLM 5.2 | 22 | **yes** |
| Qwen 3.6 | 22 | **yes** |
| Gemma 4 | 22 | **yes** |

**All seven reproduce exactly**, with zero builder warnings. The pipeline is the
published pipeline.

---

## Claude Fable 5.1\*

**Presentation score 94.90** · judge basis `ORIGINAL_RECORDED_JUDGE_POST_SCORING_AUDIT`

### Verdict source, and a wrinkle worth recording

The post-audit label set had to be assembled from three places, because the
Fable artifacts are internally inconsistent in a way that matters:

* `experiments/fable-5.1-full-mondaybench/five-scenario-summary.json` carries
  per-run `criteria` dicts holding **PRE-AUDIT** labels, while its `score`
  fields hold the **POST-AUDIT** scores. Rescoring the stored labels directly
  gives monday-001 = 98.50, not the audited 97.50.
* monday-002 has **no `criteria` key at all** — its verdicts live in
  `experiments/fable-5.1-date-sensitivity/verdicts.jsonl` and
  `verdicts-A2-A3.jsonl`, as that experiment's own header states.
  `B_NEUTRALIZED` is the date-neutralised run and is excluded.
* `experiments/fable-5.1-full-mondaybench/AUDIT.md` §5 holds the authoritative
  **10 OLD → NEW corrections**, which the builder applies. Every correction
  asserts its OLD label first, so a wrong starting point fails loudly instead
  of being overwritten.

With the corrections applied, every run reproduces the summary's stored
post-audit score and the overall reproduces **94.90**. The old 95.97 pre-audit
figure is not used anywhere.

### Capability table

| Capability | % | Earned / Possible | Criteria | Scenarios |
|---|---:|---:|---:|---:|
| action_safety | 100.0 | 23.00 / 23.0 | 4 | 3 |
| audience_adaptation | 100.0 | 17.00 / 17.0 | 5 | 1 |
| commitment_discipline | 100.0 | 10.00 / 10.0 | 3 | 1 |
| cross_output_consistency | 100.0 | 16.00 / 16.0 | 4 | 1 |
| cross_source_reconciliation | 100.0 | 18.00 / 18.0 | 4 | 2 |
| data_cleaning | 100.0 | 10.00 / 10.0 | 2 | 1 |
| dependency_reasoning | 100.0 | 25.00 / 25.0 | 5 | 2 |
| entity_resolution | 100.0 | 4.00 / 4.0 | 1 | 1 |
| information_boundaries | 100.0 | 13.00 / 13.0 | 6 | 1 |
| information_routing | 100.0 | 7.00 / 7.0 | 2 | 1 |
| ownership_and_delegation | 100.0 | 14.00 / 14.0 | 3 | 3 |
| prioritization | 100.0 | 60.00 / 60.0 | 11 | 3 |
| resource_allocation | 100.0 | 21.00 / 21.0 | 3 | 1 |
| state_reconstruction | 100.0 | 50.00 / 50.0 | 13 | 4 |
| supersession | 100.0 | 27.00 / 27.0 | 6 | 3 |
| quantitative_reasoning | 92.9 | 61.33 / 66.0 | 16 | 4 |
| causal_discipline | 92.8 | 21.33 / 23.0 | 8 | 4 |
| uncertainty_calibration | 91.3 | 21.00 / 23.0 | 7 | 5 |
| planning | 86.7 | 26.00 / 30.0 | 5 | 2 |
| business_judgment | 79.4 | 16.67 / 21.0 | 6 | 1 |
| temporal_reasoning | 71.4 | 10.00 / 14.0 | 3 | 2 |
| **factual_accuracy** | **39.6** | 3.17 / 8.0 | 2 | 2 |

---

## Claude Opus 5\*

**Presentation score 97.07** · judge basis `INDEPENDENT_BLIND_REJUDGE`

### Verdict source

The breakdown comes from **the same verdict set that produced 97.07** — the
independent blind re-judge — not from the original judge. That was the binding
constraint: presentation score and capability breakdown must share one verdict
set.

* `audits/blind-rejudge/inter-judge/source/independent-blind-rejudge-gpt-5.6-sol.json`
  — 354 criterion verdicts, 18 false-action verdicts, 15 penalty rows
* `audits/blind-rejudge/opus-5-blind-rejudge-mapping.json` — resolves each
  blind Candidate letter back to its original run, so nothing is matched by
  position

The overall recomputes to **97.07** from those labels through the canonical
scoring path.

### Capability table

| Capability | % | Earned / Possible | Criteria | Scenarios |
|---|---:|---:|---:|---:|
| action_safety | 100.0 | 23.00 / 23.0 | 4 | 3 |
| audience_adaptation | 100.0 | 17.00 / 17.0 | 5 | 1 |
| commitment_discipline | 100.0 | 10.00 / 10.0 | 3 | 1 |
| cross_output_consistency | 100.0 | 16.00 / 16.0 | 4 | 1 |
| cross_source_reconciliation | 100.0 | 18.00 / 18.0 | 4 | 2 |
| data_cleaning | 100.0 | 10.00 / 10.0 | 2 | 1 |
| dependency_reasoning | 100.0 | 25.00 / 25.0 | 5 | 2 |
| entity_resolution | 100.0 | 4.00 / 4.0 | 1 | 1 |
| information_boundaries | 100.0 | 13.00 / 13.0 | 6 | 1 |
| information_routing | 100.0 | 7.00 / 7.0 | 2 | 1 |
| ownership_and_delegation | 100.0 | 14.00 / 14.0 | 3 | 3 |
| planning | 100.0 | 30.00 / 30.0 | 5 | 2 |
| prioritization | 100.0 | 60.00 / 60.0 | 11 | 3 |
| resource_allocation | 100.0 | 21.00 / 21.0 | 3 | 1 |
| supersession | 100.0 | 27.00 / 27.0 | 6 | 3 |
| state_reconstruction | 99.3 | 49.67 / 50.0 | 13 | 4 |
| uncertainty_calibration | 98.6 | 22.67 / 23.0 | 7 | 5 |
| causal_discipline | 95.7 | 22.00 / 23.0 | 8 | 4 |
| temporal_reasoning | 92.9 | 13.00 / 14.0 | 3 | 2 |
| business_judgment | 92.1 | 19.33 / 21.0 | 6 | 1 |
| quantitative_reasoning | 89.1 | 58.83 / 66.0 | 16 | 4 |
| **factual_accuracy** | **60.4** | 4.83 / 8.0 | 2 | 2 |

---

## What the two profiles say

Both models are at 100% on fifteen of twenty-two capabilities, so the profile
is defined by where they are not.

**Both lose most on `factual_accuracy`** — Fable 39.6%, Opus 60.4%. It is the
thinnest capability in the taxonomy at 8 points over 2 criteria
(`monday-003.factual_plan_accuracy` and `monday-004.figures_carried_correctly`),
and both are criteria that price carrying a supplied figure through unchanged.
Read it as a two-criterion signal, not a broad claim.

**Opus is ahead on every capability where they differ**, and the gaps are
concentrated in the same places: factual_accuracy (+20.8), temporal_reasoning
(+21.5), planning (+13.3), business_judgment (+12.7), uncertainty_calibration
(+7.3). Fable is ahead on nothing — consistent with 97.07 against 94.90 on the
same five scenarios.

A useful consistency check falls out of this. Summed across all 22 capabilities,
Fable earns 474.50 / 500 = **94.90%** and Opus 485.33 / 500 = **97.07%** —
exactly their presentation scores. That identity holds only for models carrying
zero counted penalties, which both do; of the published seven only GLM 5.3 Flash
also ties exactly, and the rest diverge by precisely their penalty mass. It is
a direct confirmation that penalties are excluded as the convention says.

---

## Caveat

Both models remain **provisional** because generation did not use the standard
MondayBench provider route: they were generated through Claude Code, which
prepends an Agent SDK preamble to the frozen system prompt and injects a
`<system-reminder>` into the user turn. Neither this aggregation, nor the
independent blind re-judge behind Opus's 97.07, changes that. The capability
percentages describe the responses that were actually produced; they say nothing
about whether the serving conditions were equivalent to the seven published
models.

---

## Files

```
build-provisional-capabilities.py   the adapter; calls the canonical builder
claude-opus-5.json                  22 capabilities, PROVISIONAL / OFF_BENCHMARK
claude-fable-5-1.json               22 capabilities, PROVISIONAL / OFF_BENCHMARK
comparison.json                     all nine models side by side, status-tagged
```

Reproduce with:

```
python audits/capabilities/build-provisional-capabilities.py
```

The script exits non-zero if either model fails to reproduce its presentation
score, if any published model fails to reproduce exactly, if the canonical
builder warns about an unmapped criterion, or if a percentage falls outside
[0, 100].

## Site consumption

`scripts/sync-mondaybench.mjs` in the site repo reads these two artifacts in
`readProvisionalCapabilities()` and merges them into `capabilities.data.ts`
alongside the official seven, carrying `status`, `presentation_score` and
`judge_basis` through as presentation metadata. **No percentage is computed at
build time or in the browser.** The components read `.percent`, sort, and draw a
bar; they never touch points, weights, penalties, verdicts or criterion
mappings.
