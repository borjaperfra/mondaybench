# Provider-public pricing — v2: closing the last two UNKNOWNs

**Date:** 2026-09-02 · **Inferences run: zero.** No score, run, verdict or frozen
artefact touched. No first-party price replaced or reclassified. No Value Score.

| Snapshot | id | sha256 | status |
|---|---|---|---|
| first-party | `pricing-2026-09-02` | `ec4dcc85…f389598` | **unchanged** |
| provider v1 | `provider-pricing-2026-09-02` | `6cb250f3…e503fac` | **preserved** |
| **provider v2** | `provider-pricing-2026-09-02-v2` | **`3da1aa54ad4ecb6244802b3668471acbc6bdc12ed4de55d7201ae47df4d043f7`** | FROZEN |

**No pricing UNKNOWN remains in the public table.** All eight models now carry a
publishable figure — five first-party, three OpenRouter.

---

## 1. The two prices verified live — and both diverged from the quoted figures

Per instruction, **the values the source returned at verification time are the
ones stored**, with `retrieved_at` recorded. Both differed from the decision
text, so both divergences are documented rather than silently absorbed.

### Qwen 3.6 → `qwen/qwen3.6-27b`

| | Quoted in the decision | **Live, 2026-09-02** |
|---|---:|---:|
| input / 1M | $0.289 | **$0.30** |
| output / 1M | $2.40 | **$2.00** |
| cache read / 1M | — | **$0.03** |
| context | 262K | 262,144 ✓ |
| max output | — | 65,536 |
| → **$/1k tasks** | *$8.96* | **$7.70** |

**16% lower than the quoted pair would give.** Input is slightly higher, output
materially lower, and output dominates this model's cost.

### Gemma 4 → `google/gemma-4-26b-a4b-it`

| | Quoted in the decision | **Live, 2026-09-02** |
|---|---:|---:|
| input / 1M | $0.07 | **$0.042** |
| output / 1M | $0.34 | **$0.22** |
| context | 262K | 262,144 ✓ |
| max output | — | 32,768 |
| → **$/1k tasks** | *$0.72* | **$0.44** |

**39% lower than the quoted pair.** Note the quoted $0.07/$0.34 matches the
stale local models.dev catalogue entry, which the live page supersedes; and
$0.09/$0.34 belongs to the *other* candidate, `gemma-4-31b-it`. Re-verify before
publication if the pages move.

## 2. Identity — recorded in three separate fields, deliberately

The variant choice is a **publication decision**, not a discovery. I did not
re-attempt to infer the variant from the bare gateway id, and I have **not**
retroactively upgraded the run identity.

| | Qwen 3.6 | Gemma 4 | MIMO v2.5 |
|---|---|---|---|
| `benchmark_run_identity` | **AMBIGUOUS** | **AMBIGUOUS** | EXACT |
| `publication_pricing_ref` | **USER_CONFIRMED_REFERENCE** | **USER_CONFIRMED_REFERENCE** | DERIVED_FROM_RUN_IDENTITY |
| `provider_route_identity` | EXACT | EXACT | EXACT |

The claim being made:

> "To represent the cost of Qwen 3.6 / Gemma 4 we use this public OpenRouter
> variant as the reference."

The claim **not** being made:

> ~~"We have shown the run was served by OpenRouter on this variant."~~

MIMO v2.5 is different in kind: its route identity was *derived* from the run
(slug matches the run `model_id`, route context 1,050,000 matches the recorded
1M, only one non-Pro route exists), so it carries `HIGH` pricing confidence.
Qwen 3.6 and Gemma 4 carry **`MEDIUM`**, because the route is exact but the
run-to-route link is a choice.

**Consistency checks** — these do not establish identity, but the references are
at least not contradicted: both routes' 262,144 context matches the 256K
recorded in `models.yaml`, and both max-output ceilings (65,536 and 32,768)
cover the 32,000 the runs were generated under.

## 3. Billing components inspected

| Component | Qwen 3.6 (`qwen3.6-27b`) | Gemma 4 (`gemma-4-26b-a4b-it`) |
|---|---|---|
| input | **$0.30** published | **$0.042** published |
| output | **$2.00** published | **$0.22** published |
| cache read | **$0.03** published | not published |
| cache write | not published | not published |
| per-request | not published | not published |
| image / multimodal | not published (multimodal input supported) | not published (multimodal input supported) |
| reasoning | not published | not published |

**No unverifiable component actually applies to either workload**, so the
absences are not limitations in practice:

* **Qwen 3.6** — the runs record **zero cache-write** tokens, so the missing
  cache-write rate has a zero quantity. Reasoning tokens (**17,338** across 15
  runs) sit **inside** `output_tokens` (48,842), and no reasoning rate is
  published, so **no reasoning line is added** — `reasoning_tokens` is never
  summed onto `output_tokens`.
* **Gemma 4** — the runs record **zero cache-read, zero cache-write and zero
  reasoning** tokens (`gemma4` has no cache fields at all, 0/16 coverage — a
  non-caching deployment). The two published rates cover the entire workload.
* Neither model sent images in MondayBench, so the multimodal gap is moot.

Token basis, OpenAI-compatible semantics (`input_tokens` **inclusive** of cache,
`output_tokens` **includes** reasoning), 15 official runs each:

| | uncached input | cache read | cache write | output | reasoning |
|---|---:|---:|---:|---:|---:|
| qwen3.6 | 56,800 | 27,248 | 0 | 48,842 | 17,338 |
| gemma4 | 85,791 | 0 | 0 | 13,891 | 0 |
| mimo-v2.5 | 24,034 | 58,112 | 0 | 196,944 | 0 |

## 4. Recomputed provider-public cost

| Model | $/task | **$/1k** | $/100k | $/1M |
|---|---:|---:|---:|---:|
| **Gemma 4** | 0.000444 | **$0.44** | $44.39 | $443.95 |
| **MIMO v2.5** | 0.003325 | **$3.33** | $332.54 | $3,325.39 |
| **Qwen 3.6** | 0.007703 | **$7.70** | $770.28 | $7,702.76 |

Monday Scores unchanged: **Qwen 3.6 = 68.77**, **Gemma 4 = 63.00**.

## 5. Full publication table

| Model | Monday Score | Cost / 1k | Price basis | Pricing confidence | Run identity | Pricing reference |
|---|---:|---:|---|---|---|---|
| Qwen 3.8 Flash | 95.07 | $12.61 – $15.56 | First-party | MEDIUM | AMBIGUOUS (region) | FIRST_PARTY_LIST |
| GLM 5.3 Flash | 94.93 | **$10.71** | First-party | HIGH | STRONG_MATCH | FIRST_PARTY_LIST |
| Claude Fable 5.1\* | 94.90 | $456.27 | First-party | HIGH | EXACT | FIRST_PARTY_LIST |
| DeepSeek V4 Flash | 91.70 | $12.94 – $25.88 | First-party | HIGH | STRONG_MATCH | FIRST_PARTY_LIST |
| MIMO v2.5 | 86.67 | $3.33 | **OpenRouter** | HIGH | EXACT | DERIVED_FROM_RUN_IDENTITY |
| GLM 5.2 | 86.50 | $39.50 | First-party | HIGH | STRONG_MATCH | FIRST_PARTY_LIST |
| Qwen 3.6 | 68.77 | $7.70 | **OpenRouter** | MEDIUM | **AMBIGUOUS** | **USER_CONFIRMED_REFERENCE** |
| Gemma 4 | 63.00 | **$0.44** | **OpenRouter** | MEDIUM | **AMBIGUOUS** | **USER_CONFIRMED_REFERENCE** |

\* Provisional, OFF-BENCHMARK / CLAUDE CODE ROUTE, excluded from the official ranking.

**No cost figure may be shown without its Price basis.**

## 6. Pareto — primary unchanged, extended recomputed

### A. PRIMARY — FIRST_PARTY_LIST only · **unchanged**

| | Model | Score | $/1k |
|---|---|---:|---:|
| frontier | **GLM 5.3 Flash** | 94.93 | 10.71 |
| frontier | **Qwen 3.8 Flash** | 95.07 | 15.56 |
| dominated | DeepSeek V4 Flash | 91.70 | 25.88 |
| dominated | GLM 5.2 | 86.50 | 39.50 |
| dominated | Claude Fable 5.1\* | 94.90 | 456.27 |

### B. EXTENDED PROVIDER — all eight

> **MIXES COST CLASSES.** Vendor list prices compared against third-party route
> prices, two of which are owner-chosen references rather than resolved run
> identities. Indicative only; does not change the primary frontier.

| | Model | Score | $/1k | Basis |
|---|---|---:|---:|---|
| frontier | **Gemma 4** | 63.00 | **0.44** | OpenRouter |
| frontier | **MIMO v2.5** | 86.67 | 3.33 | OpenRouter |
| frontier | **GLM 5.3 Flash** | 94.93 | 10.71 | First-party |
| frontier | **Qwen 3.8 Flash** | 95.07 | 15.56 | First-party |
| dominated | Qwen 3.6 | 68.77 | 7.70 | OpenRouter — by MIMO v2.5 |
| dominated | DeepSeek V4 Flash | 91.70 | 25.88 | First-party |
| dominated | GLM 5.2 | 86.50 | 39.50 | First-party |
| dominated | Claude Fable 5.1\* | 94.90 | 456.27 | First-party |

**Frontier membership is not a ranking.** Gemma 4 is on the frontier *because it
is the cheapest*, and it is the **lowest-scoring model in the field** at 63.00 —
23.4 points below GLM 5.3 Flash and 31.9 below Qwen 3.8 Flash, gaps far beyond
any noise floor. "On the frontier" means only that nothing is both better and
cheaper.

**The one new domination is decisive.** **Qwen 3.6 is dominated by MIMO v2.5** —
MIMO scores **17.90 points higher** (86.67 vs 68.77) at **2.3× less cost** ($3.33
vs $7.70). Unlike the marginal cases elsewhere in this analysis, that quality gap
is well beyond run variance and is genuinely resolved. On these figures Qwen 3.6
has no economic case against MIMO v2.5.

## 7. Mandatory methodology caveat for Qwen 3.6 and Gemma 4

Verbatim text to carry wherever their cost figures appear:

> **Pricing reference chosen explicitly for publication.** The original gateway
> run id did not identify a commercial variant, so the benchmark run identity
> remains AMBIGUOUS; this OpenRouter route is a public reference for cost, not
> evidence of how the run was served.

Plus the class-level tooltip already in use:

> **OpenRouter** — "Public OpenRouter price for this model route. This is
> provider-specific pricing, not a canonical model list price."

Both are stored in `publication-data.json` as `provider_reference_caveat` and
`price_basis_labels`.

## 8. Does any Cost / Value conclusion change?

**Primary analysis: nothing.** First-party frontier, the top band, the cheapest
top-band model and the Fable conclusion are all identical:

* **TOP PERFORMANCE BAND / UNORDERED** — Qwen 3.8 Flash 95.07, GLM 5.3 Flash
  94.93, Claude Fable 5.1\* 94.90.
* **GLM 5.3 Flash cheapest in band**, $10.71/1k.
* **Fable 5.1\* fastest**, 50.9 s median TTFA.
* **`NO MEASURED QUALITY ADVANTAGE FOR THE ADDITIONAL COST`** for Fable, at
  42.6× GLM 5.3 Flash and 29.3–36.2× Qwen 3.8 Flash.

**Extended analysis: two changes worth publishing, neither affecting the band.**

1. **The cost floor of the field is now measured: $0.44/1k** (Gemma 4). The full
   field spans **$0.44 to $456.27 per 1,000 tasks — a factor of 1,037** — while
   Monday Score spans 63.00 to 95.07. That range is the headline economic fact
   of the whole layer and it was not quantifiable while three models were UNKNOWN.
2. **Qwen 3.6 is decisively dominated by MIMO v2.5** (+17.90 points, 2.3× cheaper).

One thing that has **not** changed and should not be over-read: Gemma 4 being
cheapest does not make it a recommendation. At 63.00 it is 31.9 points below the
top of the field on a 100-point quality scale.

---

**Artefacts.** New: `provider-pricing-snapshot-2026-09-02-v2.yaml` + `.sha256`,
`PROVIDER-PRICING-V2.md`. Updated: `publication-data.json` (all eight priced;
adds `benchmark_run_identity`, `publication_pricing_ref`,
`provider_route_identity`, per-scale provider costs, `provider_reference_caveat`,
`unknown_pricing_remaining: []`), `pareto.json` (dual, extended recomputed).
Preserved: `provider-pricing-snapshot-2026-09-02.yaml` + `.sha256` (v1),
`PROVIDER-PRICING.V1.md`, `publication-data.PROVIDER-V1.json`,
`publication-data.FIRST-PARTY-ONLY.json`.
**Untouched:** first-party snapshot and hash, `GATE.md`, `REPORT.md`,
`billing-semantics.md`, `cost-summary.json`, `normalized-costs.jsonl`,
`quality-vs-latency.json`.

Nothing integrated into the web. Leaderboard, Monday Score, runs and verdicts
untouched.
