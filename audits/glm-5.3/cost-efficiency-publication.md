# GLM 5.3 — Cost / Efficiency publication

**Date:** 2026-09-03 · **Model calls: 0. Judge calls: 0. No re-judge.** No score,
run, verdict, evaluation, rubric, scenario or evaluator was touched. v1.0 is
byte-unchanged and v1.1 needed no re-cut.

Published under the approved decision: **the vendor's list price where the view
is first-party, the observed route cost where the view allows provider pricing,
and never the two merged.**

---

## 1. Quality — unchanged

| | |
|---|---|
| Monday Score | **93.73** |
| Status | **OFFICIAL**, no provisional badge |
| Scenario means | 97.50 / 87.67 / 94.83 / 91.67 / 97.00 |

Nothing in this workstream touched it. Overall, capabilities, the scenario
boards and the top-performance-band logic are as they were.

## 2. Efficiency — published, and independent of the pricing question

| | |
|---|---:|
| median TTFA | **253.26 s** (stored `ttfa_ms` = 253,260.4) |
| median TTFT | 2.108 s |
| mean output | **21,298.6** tokens |
| mean reasoning | **19,288.1** tokens |
| cache read | 13,760 tokens |
| cache write | 0 |

Rendered as `253.3s · ~21.3k output`. Seconds, never milliseconds; converted
once, from the one field on the row that carries a unit in its name. No "steps"
anywhere — MondayBench is one streaming completion per task.

**Pricing identity does not gate this.** A contested price says nothing about a
latency or a token count, and the gate now says so explicitly rather than
collapsing everything into one PASS/FAIL.

## 3. Two bases, never merged

### First-party — Z.AI list

| | |
|---|---|
| Vendor / SKU | Z.AI · `GLM-5.3` |
| Input / output | $1.40 / $4.40 per million |
| Cached input | $0.26 per million |
| Source | `docs.z.ai/guides/overview/pricing`, the same page the 2026-09-02 snapshot cites for GLM-5.2 and GLM-5.3-Flash |
| Snapshot | `pricing-2026-09-03` |
| **Cost / task** | **$0.099205** |
| **Cost / 1k** | **$99.20** |
| Cost / 100k | $9,920.50 |
| Cost / 1M | $99,204.96 |
| Pricing identity | **CONTESTED** |

### Route — Helmcode, observed

| | |
|---|---|
| Route | Helmcode gateway, `glm5.3` |
| Basis | `GATEWAY_METERED` |
| Source | each scored run's own `economics` block, all 15 runs |
| **Cost / task** | **$0.005675** |
| **Cost / 1k** | **$5.67** |
| Cost / 100k | $567.49 |
| Cost / 1M | $5,674.87 |
| Pricing identity | `OBSERVED_ROUTE` |

**Ratio: 17.48×**, computed from the unrounded per-task costs (the rounded $/1k figures give 17.50, which is the same number reported to fewer digits). Not published as a range. `$5.67–$99.20` would be a category
error, and `$5.67–$11.24` would promote the Parasail observation to a second
primary figure. Parasail stays where it was: a counterfactual in the snapshot
and the audit, at roughly $11.24/1k for the same token usage.

All figures are labelled **MondayBench-equivalent tasks**, never production
workloads.

### What is deliberately not said

No discount, wholesale agreement, batching, quantization, subsidy or alternative
deployment is asserted or implied. A test greps the published row for exactly
those words. The gateway does not expose enough information to explain the
difference, and this workstream does not try to.

## 4. Pricing identity, kept out of the score

| | |
|---|---|
| Served model id | `glm5.3` on all 15 runs, never `glm5.3-flash` |
| **Generation identity** | sufficient for official eligibility — unchanged |
| **Pricing basis identity** | **CONTESTED** |

Contested because Z.AI's public GLM-5.3 price is $1.4/$4.4 while the Helmcode
meter reads $0.075/$0.25; `/model/info` and `/model_group/info` are unavailable;
and the scored runs are streaming, which carries no provider field. The two are
different questions and are recorded on different fields.

The CONTESTED label is a provenance qualification, not a benchmark failure, and
is presented as such: an ordinary basis badge with a tooltip, no alarm styling.

## 5. Pareto, recomputed from the canonical data

`A` dominates `B` iff `A.score ≥ B.score` and `A.cost ≤ B.cost`, with at least
one strict. Ranges enter at their conservative end. Nothing is hardcoded.

**Official first-party frontier — unchanged.**

| | |
|---|---|
| Before | GLM 5.3 Flash · Qwen 3.8 Flash |
| After | GLM 5.3 Flash · Qwen 3.8 Flash |
| GLM 5.3 | **DOMINATED**, by both |

At 93.73 for $99.20 it is beaten on both axes by GLM 5.3 Flash (94.93 for
$10.71) and by Qwen 3.8 Flash (95.07 for $15.56). It adds nothing to this
frontier, and the calculation agrees with the audit's expectation rather than
being forced to.

**Provider frontier — GLM 5.3 enters, displacing nobody.**

| | |
|---|---|
| Before | Gemma 4 · MIMO v2.5 · GLM 5.3 Flash · Qwen 3.8 Flash |
| After | Gemma 4 · MIMO v2.5 · **GLM 5.3** · GLM 5.3 Flash · Qwen 3.8 Flash |

At $5.67 nothing scoring ≥ 93.73 is cheaper, and it does not undercut MIMO
v2.5's $3.33 at a lower score, so it is added rather than swapped in.

**That contrast is the result of this workstream.** The same model, the same
score, dominated on one basis and on the frontier on the other. Neither number
is wrong; they answer different questions.

Provisional models — Claude Opus 5\*, Claude Fable 5.1\* — are on neither
frontier, and `frontier_without_provisional` is recorded and tested for both
views.

## 6. GLM 5.3 versus GLM 5.3 Flash

| | GLM 5.3 | GLM 5.3 Flash |
|---|---:|---:|
| Monday Score | 93.73 | 94.93 |
| First-party $/1k | 99.20 | 10.71 |

**Score delta −1.20. First-party cost ×9.26.**

The earlier story — "gives up ~1.2 points for roughly half the cost" — is
**not published**. Like-for-like it is inverted: GLM 5.3 is nine times more
expensive at list, not half. The only arithmetic that produced "half" compared
GLM 5.3's meter against Flash's list price.

The 1.20-point difference is **not** called statistically significant. It sits
inside the per-scenario run variance.

What the data does support, and what the row's note says: **model price and
route price can tell very different stories.** That is a statement about the two
bases, not an explanation of either.

## 7. What the page shows

There is no pricing toggle on the Cost view — one existed and was removed
because it hid four of eight models. The page's principle is "not a filter, a
label": everything is plotted, each figure carries the badge that says which
basis produced it.

GLM 5.3 is therefore drawn as **two points at the same score**, joined by a
faint rule: the first-party point at $99.20 and the route point at $5.67 in the
page's existing dashed marker for a non-first-party basis. A silent swap between
them would have been the removed toggle's mistake in miniature — a model jumping
horizontally with nothing on screen saying why.

The table row carries both figures, each with its own badge and tooltip:

* *First-party* — "Normalized using Z.AI's public GLM-5.3 list price."
* *Helmcode route* — "Observed metering for the Helmcode route used in the
  benchmark. The upstream commercial pricing basis could not be independently
  resolved."

Efficiency picks the model up from the same dataset and needed no change of its
own.

## 8. Gate

| Check | |
|---|---|
| quality provenance | PASS |
| usage reconstruction | PASS |
| efficiency | PASS |
| Z.AI public price source | PASS |
| first-party normalization | PASS |
| gateway-metered reconstruction | PASS |
| billing semantics | PASS |
| reasoning double-count | NONE |
| cache treatment | PASS |
| existing cost invariance | PASS |
| first-party Pareto | PASS |
| provider Pareto | PASS |
| pricing-basis UI | PASS |
| release v1.0 / v1.1 | PASS |
| tests | PASS — 933 |
| **pricing identity** | **CONTESTED, declared** |

CONTESTED was not converted to EXACT. Publication is valid because every cost
number states its own basis on the row, in the tooltip and in the artifact.

## 9. Method, validated before it was used

The reconstruction was required to reproduce two already-gated figures before it
was allowed near a new one:

| Control | Published | Reconstructed |
|---|---:|---:|
| GLM 5.2 | $39.50/1k | $39.50/1k |
| GLM 5.3 Flash | $10.71/1k | $10.71/1k |

Both exact. The first attempt was wrong and the controls caught it: cache tokens
live in `provider_metadata.raw_usage.prompt_tokens_details`, not in `usage`, and
reading only `usage` overstated GLM 5.2 by 6.8%.

Two further defects were found and fixed on the way:

* the site's capability adapter returned early whenever `capabilities` was an
  array — true of the v0.1 artifact and, since the v1.1 migration, of the
  suite-versioned one too. Every official model was rendering with no `status`
  field. `astro check` now reports 0 errors.
* the first-party Pareto pool was being built with an `isinstance(..., number)`
  test, which silently dropped the two models that publish a price *range* and
  moved a frontier that must not move. Caught by the invariance gate before
  anything was written.

## 10. Integrity

| | |
|---|---|
| v1.0 digest | `c056b4b4…` **unchanged** |
| v1.1 digest | `a4d6eb6e…` **unchanged, and not re-cut** |
| v1.1 scoring groups | scenarios, evaluators, taxonomy, runs, verdicts, evaluations, leaderboards, analysis — **all identical** |
| v1.1 pricing group | 2 changed, 6 added — **mutable, not a failure** |
| Existing published costs | all eight invariant, tested per model |
| Model calls / judge calls | 0 / 0 |

The last two rows are the point of the release-boundary work from the previous
task, demonstrated rather than asserted: publishing a price changed the pricing
group and left every scoring group byte-identical.

## 11. Artifacts

| File | |
|---|---|
| `analysis/cost-value/publication-data.json` | rebuilt reproducibly, GLM 5.3 added with both bases |
| `analysis/cost-value/pareto.json` | both frontiers recomputed, `frontier_without_provisional` added |
| `analysis/cost-value/pricing-snapshot-2026-09-03.yaml` + `.sha256` | `9b1db0cb…`, addendum inheriting `ec4dcc85…` unchanged |
| `analysis/cost-value/GLM-5.3-COST-FINDING.md` | the finding that rejected the original $0.075/$0.25 first-party assumption |
| `analysis/cost-value/_build_publication.py` | the reproducible builder, with the invariance gate |
| `analysis/cost-value/_glm53_cost.py`, `_glm53_gate.py` and their JSON | reconstruction and gate evidence |
| `tests/test_cost_publication.py` | 26 tests, A–L |
| `audits/glm-5.3/cost-efficiency-publication.md` | this |

The previous gate artifacts are kept. They are the provenance showing that the
original $0.075/$0.25 first-party assumption was examined and rejected.
