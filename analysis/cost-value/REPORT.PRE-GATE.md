# MondayBench cost / value layer

**Date:** 2026-09-02 · **Pricing snapshot:** `pricing-2026-09-02`
**Scores:** POST-AUDIT throughout. Fable 5.1 is **94.90**; the pre-audit 95.97 is superseded and appears nowhere in this analysis.
**Inferences run: zero.** No frozen artefact, run, verdict, leaderboard or Monday Score was modified. **No Value Score was created.**

The question this layer answers: *among models with similar MondayBench quality,
which one is actually cheaper to run?*

---

## 1. Usage coverage

135 runs audited — 120 stored official runs plus the 15 audited Fable frozen
runs. Field presence, non-null count over runs:

| Model | runs | input | output | reasoning | cache read | cache write | TTFT | TTFA | **reported cost** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| qwen3.8-flash | 22 | 22 | 22 | 22 | 22 | **3** | 22 | 22 | **0** |
| deepseek-v4-flash | 17 | 17 | 17 | 17 | 17 | 17 | 17 | 17 | **17** |
| mimo-v2.5 | 17 | 17 | 17 | 17 | 17 | **0** | 17 | 17 | **0** |
| gemma4 | 16 | 16 | 16 | 16 | **0** | **0** | 16 | 16 | **0** |
| glm5.2 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | **16** |
| glm5.3-flash | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | **0** |
| qwen3.6 | 16 | 16 | 16 | 16 | 16 | **0** | 16 | 16 | **0** |
| claude-fable-5-1 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | **15** |

**Reported cost exists for only 3 of 8 models.** Token counts and latency are
complete for all eight; cache-write observability is partial. `qwen3.6` spans
two providers (`helmcode` and `nan`) because of the documented monday-004
endpoint override.

Costing uses the **102 official runs** resolved by the harness's own
`official.plan_model`, plus one documented exception: monday-004/`qwen3.6`,
whose published battery was NaN-served under a per-scenario override that
`qualify_run` rejects on provider. 15 official runs per model.

Artefact: `usage-coverage.json`.

## 2. Pricing coverage

**5 of 8 models priced. 3 UNKNOWN, deliberately not estimated.**

| Model | Input | Output | Cache read | Cache write | Confidence |
|---|---:|---:|---:|---:|---|
| claude-fable-5-1 | 10.00 | 50.00 | 0.25 | **20.00** (1h TTL) | HIGH |
| qwen3.8-flash | 0.15 | 0.47 | 0.016 | 0.20 | HIGH |
| glm5.3-flash | 0.15 | 0.50 | 0.03 | 0.00 | HIGH |
| glm5.2 | 1.40 | 4.40 | 0.26 | 0.00 | MEDIUM |
| deepseek-v4-flash | 0.22 / 0.44 | 0.66 / 1.32 | 0.007 / 0.014 | n/a | MEDIUM |
| mimo-v2.5 | UNKNOWN | UNKNOWN | — | — | UNKNOWN |
| qwen3.6 | UNKNOWN | UNKNOWN | — | — | UNKNOWN |
| gemma4 | UNKNOWN | UNKNOWN | — | — | UNKNOWN |

USD per 1M tokens. DeepSeek shows off-peak / peak. Sources, dates and the full
reasoning are in `pricing-snapshot-2026-09-02.yaml`.

**Why the three are UNKNOWN**, rather than filled with a plausible number:

* **mimo-v2.5** — candidates span ~8× on input: OpenRouter shows $0.119/$0.238;
  a search summary reports Xiaomi first-party at $0.14/$0.28 *and*, in the same
  breath, a permanent change to $1/$3 in May 2026. Unresolved.
* **qwen3.6** and **gemma4** — open-weight models with **no single first-party
  price**. Rates are per variant (Qwen3.6-35B-A3B ~$0.05/$0.70 vs Qwen3.6-Plus
  ~$0.325/$1.95; Gemma 4 31B ~$0.08/$0.34 vs 26B-A4B ~$0.06/$0.30) and the run
  records only carry the bare gateway id, so the served variant is unidentified.
  Two compounding unknowns.

Local reseller catalogues were **rejected as a price source**: the models.dev
snapshot shipped with OpenCode carries 2.5× spreads for nominally identical
models across hosts (`glm-5.3-flash` at $0.06 from one reseller, $0.15 from
another). Picking one would decide the cost ranking by fiat.

**One promotional caveat that matters:** GLM 5.3 Flash had a live 50% discount
at snapshot time (to 2026-09-09). **List price is used.** At promotional rates
its every figure below halves — to $5.36/1k — which widens rather than narrows
its cost advantage.

## 3. Billing semantics

Established from the data, not from field names. Full tests in
`billing-semantics.md`. The headline: **`input_tokens` does not mean the same
thing on the two routes.**

| | OpenAI-compatible (Helmcode/NaN) | Anthropic first-party (Fable) |
|---|---|---|
| `input_tokens` | **INCLUSIVE** of cached input — subtract to get uncached | **EXCLUSIVE** of cache — three disjoint buckets |
| `output_tokens` | **INCLUDES** reasoning tokens | **INCLUDES** thinking tokens |
| evidence | `cached_tokens > input_tokens` in 0/120; `reasoning > output` in 0/120 | `input=2` against `cache_write=4832` on a 4.8k-token prompt |

On a ~4,800-token prompt Fable reports `input_tokens: 2`. Applying the gateway
formula to it would misprice the cached portion by three orders of magnitude.
Two separate formulas are therefore used.

**Reasoning tokens: category (A) — inside billable `output_tokens` — for every
priced model.** Confirmed arithmetically (`reasoning ≤ output` in all 120 runs)
*and* from pricing (no verified price list publishes a reasoning rate).
`output_tokens + reasoning_tokens` is never computed anywhere.
`mimo-v2.5` is category **(D) not observable** — zero reported while the model
demonstrably streams a thinking phase. `gemma4` is **(C) none produced**.

## 4. Validation: reported vs normalized

| Model | n | mean reported | mean normalized | ratio | mean % diff |
|---|---:|---:|---:|---:|---:|
| claude-fable-5-1 | 15 | 0.456266 | 0.456266 | **1.000** | **0.0%** |
| deepseek-v4-flash | 15 | 0.007216 | 0.013672 | 1.895 | +113.1% |
| glm5.2 | 15 | 0.021100 | 0.039504 | 1.872 | +85.0% |

**All three differences are explained, and the formula is validated. The audit
found and fixed one real pricing error along the way.**

* **Fable reconciles to 0.00% on all 15 runs** — the only model where the served
  route and the list-price vendor are the same, so this is a true end-to-end
  check of both the formula and the price. Getting there required a correction:
  solving the provider's own meter for the cache-write rate returns
  **$20.000/MTok exactly** on every cache-writing run, not the $12.50 standard
  5-minute rate first assumed. $20.00 is 2× input — the **1-hour TTL** write,
  which is what this session's cache uses. With $12.50 the formula under-read by
  3.7%; with $20.00 it reconciles to the cent. Using the 5-minute rate instead
  would cut Fable's normalized cost by ~6%.
* **DeepSeek 1.895×** is the gateway charging below list, not an error.
  Recomputing reported cost from the *same token counts* at Helmcode's measured
  rates reproduces it to within 1.6% (ratio 0.984), and list/gateway output
  price is 0.66/0.35 = 1.89× — matching the observed 1.895 almost exactly.
* **GLM 5.2 1.872×** likewise: Helmcode's measured rate is **exactly 50%** of
  Z.AI list on both input and output. The token accounting reproduces reported
  cost to within 7.8% at gateway rates, the residual being the cache-read line
  that `models.yaml` does not price.

This is the whole reason reported and normalized are kept apart: for two of
three models the gateway was materially cheaper than list.

Artefact: `validation-reported-vs-normalized.json`.

## 5. Full model table

| Model | Monday Score | Normalized $/task | $/1k tasks | Median TTFA | Output tokens | Reasoning tokens | Pricing confidence |
|---|---:|---:|---:|---:|---:|---:|---|
| Qwen 3.8 Flash | 95.07 | 0.0156 | 15.56 | 258.9 s | 31,687 | 27,411 | HIGH |
| GLM 5.3 Flash | 94.93 | **0.0107** | **10.71** | 278.2 s | 20,072 | 18,031 | HIGH |
| Claude Fable 5.1\* | 94.90 | 0.4563 | 456.27 | **50.9 s** | **8,198** | **4,363** | HIGH |
| DeepSeek V4 Flash | 91.70 | 0.0137 | 13.67 | 121.4 s | 18,225 | 16,525 | MEDIUM |
| MIMO v2.5 | 86.67 | UNKNOWN | UNKNOWN | 170.4 s | 13,130 | 0 (D) | UNKNOWN |
| GLM 5.2 | 86.50 | 0.0395 | 39.50 | 44.1 s | 8,114 | 5,917 | MEDIUM |
| Qwen 3.6 | 68.77 | UNKNOWN | UNKNOWN | 1.0 s | 3,256 | 1,156 | UNKNOWN |
| Gemma 4 | 63.00 | UNKNOWN | UNKNOWN | 0.6 s | 926 | 0 (C) | UNKNOWN |

\* Provisional. Fable 5.1 was run through Claude Code rather than MondayBench's
standard provider route and is excluded from the official ranking.

## 6. Cost per scenario

Mean normalized cost per run, USD:

| Model | 001 | 002 | 003 | 004 | 005 | min run | max run |
|---|---:|---:|---:|---:|---:|---:|---:|
| Qwen 3.8 Flash | 0.0043 | 0.0170 | 0.0180 | 0.0264 | 0.0121 | 0.0037 | 0.0294 |
| GLM 5.3 Flash | 0.0031 | 0.0064 | 0.0037 | 0.0254 | 0.0150 | 0.0024 | 0.0417 |
| Claude Fable 5.1\* | 0.1552 | 0.3827 | 0.3814 | 0.9566 | 0.4054 | 0.1188 | 1.0883 |
| DeepSeek V4 Flash | 0.0073 | 0.0112 | 0.0147 | 0.0221 | 0.0131 | 0.0061 | 0.0296 |
| GLM 5.2 | 0.0107 | 0.0298 | 0.0207 | 0.0714 | 0.0649 | 0.0089 | 0.1464 |

**The five scenarios are not the same workload and the spread is large.**
monday-004 (24 KB prompt) costs 6–8× monday-001 (11.7 KB) for every model. Any
single "cost per task" figure is an average over five genuinely different jobs —
so per-scenario figures are published beside it rather than behind it. Full
per-scenario scores, TTFA and token counts are in `cost-summary.json`.

## 7. Cost per 1,000 tasks — and how it is aggregated

**Aggregation chosen:** the arithmetic mean over the 15 official runs. With
exactly 3 runs in each of 5 scenarios this is *identical* to the mean of the
five per-scenario means, so there is no weighting ambiguity — equal weight per
scenario, which is exactly how `mondaybench/overall.py` weights Monday Score.
The cost metric therefore sits beside the quality metric on the same footing.

The alternative — total battery cost divided by 15 — is the same number here.
A third option, weighting scenarios by token volume, was rejected: it would let
monday-004 dominate and would no longer correspond to the Monday Score's
weighting.

| Model | $/1,000 MondayBench-equivalent tasks |
|---|---:|
| GLM 5.3 Flash | **10.71** |
| DeepSeek V4 Flash | 13.67 |
| Qwen 3.8 Flash | 15.56 |
| GLM 5.2 | 39.50 |
| Claude Fable 5.1\* | 456.27 |

## 8. Cost at scale

**MondayBench-equivalent tasks.** This is a linear extrapolation of the observed
workload — five business-analysis tasks with 11–24 KB prompts and 0.9k–33k token
answers. It is **not** a universal cost per request.

| Model | 1 task | 1k | 10k | 100k | 1M |
|---|---:|---:|---:|---:|---:|
| GLM 5.3 Flash | $0.0107 | $10.71 | $107 | $1,071 | $10,710 |
| DeepSeek V4 Flash | $0.0137 | $13.67 | $137 | $1,367 | $13,672 |
| Qwen 3.8 Flash | $0.0156 | $15.56 | $156 | $1,556 | $15,561 |
| GLM 5.2 | $0.0395 | $39.50 | $395 | $3,950 | $39,504 |
| Claude Fable 5.1\* | $0.4563 | $456.27 | $4,563 | $45,627 | $456,266 |

## 9. Mathematical Pareto frontier

Definition applied with **no statistical tolerance**: A dominates B iff
`A.score >= B.score` and `A.cost <= B.cost`, at least one strict.

**Frontier (2 models):**

| Model | Score | $/1k |
|---|---:|---:|
| GLM 5.3 Flash | 94.93 | 10.71 |
| Qwen 3.8 Flash | 95.07 | 15.56 |

**Dominated (3 models):**

| Model | Score | $/1k | Dominated by |
|---|---:|---:|---|
| DeepSeek V4 Flash | 91.70 | 13.67 | GLM 5.3 Flash |
| GLM 5.2 | 86.50 | 39.50 | Qwen 3.8 Flash, GLM 5.3 Flash, DeepSeek V4 Flash |
| Claude Fable 5.1\* | 94.90 | 456.27 | Qwen 3.8 Flash, GLM 5.3 Flash |

Excluded for want of pricing: MIMO v2.5, Qwen 3.6, Gemma 4.

Artefact: `pareto.json`.

## 10. Quality-uncertainty-aware interpretation

The mathematical frontier treats 0.03 points as a real difference. It is not.

**Why these three group.** Not from an invented threshold — from the observed
spread already published beside each score:

| Model | Score | mean run σ (within scenario) | across-scenario σ |
|---|---:|---:|---:|
| Qwen 3.8 Flash | 95.07 | 3.34 | 1.79 |
| GLM 5.3 Flash | 94.93 | 3.94 | 4.84 |
| Claude Fable 5.1\* | 94.90 | 1.53 | 4.16 |

The gaps inside this group are **0.03, 0.14 and 0.17 points**. The smallest
run-to-run σ in the group is 1.53 — ten times the largest gap. Fable's own audit
independently reached the same conclusion by a different route: its 94.07–96.30
strict/lenient envelope straddles all three models, and the ordering flips
inside it. **TOP PERFORMANCE BAND: Qwen 3.8 Flash, GLM 5.3 Flash, Claude Fable
5.1\* — unordered.**

Below the band, **DeepSeek V4 Flash at 91.70 is a genuinely separate tier** by
score, but the gap to the band (3.23–3.37) is itself close to the run σ of both
sides (3.34–3.94), so it is stated as *probably* resolved rather than certainly.
Everything from MIMO v2.5 (86.67) down is clearly separated.

### The finding

> **GLM 5.3 Flash costs 42.6× less than Claude Fable 5.1 while MondayBench does
> not resolve a meaningful quality difference between them** (94.93 vs 94.90,
> a 0.03-point gap against a 1.53-point noise floor).
>
> **Qwen 3.8 Flash costs 29.3× less than Claude Fable 5.1** on the same
> unresolved-quality basis (95.07 vs 94.90, 0.17 points).

### `NO MEASURED QUALITY ADVANTAGE FOR THE ADDITIONAL COST`

Applied to **Claude Fable 5.1\***: it is the most expensive model in the priced
set by a factor of 29–43 against the other two band members, and MondayBench
resolves no quality advantage for that premium.

This is **not** a statement that Fable is a worse model. Two things it measurably
does buy, which are not quality:

* **Latency** — 50.9 s median TTFA against 258.9 s and 278.2 s. **5.1–5.5×
  faster to first answer** than either band peer.
* **Token efficiency** — 8,198 output tokens per task against 20,072 and 31,687.
  **2.4–3.9× more concise**, with 4.1–6.3× fewer reasoning tokens.

Both are real, measured and outside the Monday Score. Whether they justify the
premium is a product decision this layer deliberately does not make.

### Incremental cost per score point

Computed **only** where the score gap exceeds both models' mean run σ.

| Pair | Δ score | Δ $/1k | Multiple | Verdict |
|---|---:|---:|---:|---|
| Qwen 3.8 F vs GLM 5.3 F | +0.14 | +4.85 | 1.45× | **QUALITY DIFFERENCE NOT RESOLVED** |
| GLM 5.3 F vs Fable 5.1\* | +0.03 | −445.56 | 0.02× | **QUALITY DIFFERENCE NOT RESOLVED** |
| Qwen 3.8 F vs Fable 5.1\* | +0.17 | −440.71 | 0.03× | **QUALITY DIFFERENCE NOT RESOLVED** |
| GLM 5.3 F vs DeepSeek V4 F | +3.23 | −2.96 | 0.78× | better **and** cheaper — no trade-off |
| Qwen 3.8 F vs DeepSeek V4 F | +3.37 | +1.89 | 1.14× | not resolved (gap ≈ σ) |
| Qwen 3.8 F vs GLM 5.2 | +8.57 | −23.94 | 0.39× | better **and** cheaper — no trade-off |
| GLM 5.3 F vs GLM 5.2 | +8.43 | −28.79 | 0.27× | better **and** cheaper — no trade-off |
| DeepSeek V4 F vs GLM 5.2 | +5.20 | −25.83 | 0.35× | better **and** cheaper — no trade-off |
| Fable 5.1\* vs GLM 5.2 | +8.40 | +416.77 | 11.55× | $49.62 per 1k per score point |

**In the priced set there is exactly one pair where paying more buys resolved
quality** — Fable over GLM 5.2, at $49.62 per 1,000 tasks per score point. Every
other cost increase either buys nothing measurable or is dominated outright.

Artefact: `incremental-cost.json`.

## 11. Quality vs latency

| Model | Score | Median TTFA | Output tokens |
|---|---:|---:|---:|
| Qwen 3.8 Flash | 95.07 | 258.9 s | 31,687 |
| GLM 5.3 Flash | 94.93 | 278.2 s | 20,072 |
| Claude Fable 5.1\* | 94.90 | **50.9 s** | **8,198** |
| DeepSeek V4 Flash | 91.70 | 121.4 s | 18,225 |
| MIMO v2.5 | 86.67 | 170.4 s | 13,130 |
| GLM 5.2 | 86.50 | 44.1 s | 8,114 |
| Qwen 3.6 | 68.77 | 1.0 s | 3,256 |
| Gemma 4 | 63.00 | 0.6 s | 926 |

* **Highest measured quality:** Qwen 3.8 Flash, 95.07 — inside the band, so not
  a resolved win.
* **Cheapest top-band:** GLM 5.3 Flash, $10.71/1k.
* **Fastest top-band:** Claude Fable 5.1\*, 50.9 s.
* **Most expensive top-band:** Claude Fable 5.1\*, $456.27/1k.
* **Lowest-token top-band:** Claude Fable 5.1\*, 8,198 output tokens.

Not combined with cost — kept as a separate dimension by design.
Note GLM 5.2 is faster than every band member at 44.1 s, but it scores 8.4
points lower, which *is* resolved. Qwen 3.6 and Gemma 4 answer in about a second
because they barely think — 1,156 and 0 reasoning tokens — and score 68.77 and
63.00.

Artefacts: `quality-vs-latency.json`, `quality-vs-cost.json`.

## 12. Top-band comparison

| | Qwen 3.8 Flash | GLM 5.3 Flash | Claude Fable 5.1\* |
|---|---:|---:|---:|
| Monday Score (POST-AUDIT) | 95.07 | 94.93 | 94.90 |
| mean run σ | 3.34 | 3.94 | 1.53 |
| across-scenario σ | 1.79 | 4.84 | 4.16 |
| Normalized $/task | 0.0156 | **0.0107** | 0.4563 |
| $/1k tasks | 15.56 | **10.71** | 456.27 |
| $/100k tasks | 1,556 | **1,071** | 45,627 |
| Cost multiple vs cheapest | 1.45× | **1.00×** | 42.6× |
| Median TTFA | 258.9 s | 278.2 s | **50.9 s** |
| Mean output tokens | 31,687 | 20,072 | **8,198** |
| Mean reasoning tokens | 27,411 | 18,031 | **4,363** |

**1. Is there a resolved quality difference?** No. 0.03–0.17 points against a
1.53-point minimum run σ. The Fable audit's own sensitivity envelope
(94.07–96.30) straddles all three and reverses their order.

**2. Cheapest?** GLM 5.3 Flash, $10.71/1k — and $5.36/1k at the promotional rate
live at snapshot time.

**3. How much more expensive?** GLM 5.3 Flash 1.00× · Qwen 3.8 Flash 1.45× ·
Fable 5.1\* **42.6×**. Fable is 29.3× Qwen.

**4. Fastest?** Fable 5.1\*, 50.9 s — 5.1× faster than Qwen, 5.5× than GLM 5.3 F.

**5. Fewest tokens?** Fable 5.1\*, 8,198 output — 2.4× fewer than GLM 5.3 Flash,
3.9× fewer than Qwen.

**6. Any evidence that paying more buys quality?** **No.** Within the band cost
spans 42.6× and score spans 0.17 points. The most expensive model has the
*lowest* score of the three — by an amount that is itself noise. Across the whole
priced set the correlation runs the wrong way: the two frontier models are the
two cheapest.

**7. On quality/cost alone?** **GLM 5.3 Flash.** Cheapest in the band,
statistically indistinguishable in quality, on the mathematical frontier.

**8. On quality/latency alone?** **Claude Fable 5.1\*.** 5× faster to first
answer at indistinguishable quality — if the 42.6× cost is acceptable. If it is
not, DeepSeek V4 Flash at 121.4 s and $13.67/1k is the next best latency for the
money, at a probably-resolved 3.2-point quality cost.

## 13. Missing and UNKNOWN

| Item | Status | Effect |
|---|---|---|
| mimo-v2.5 list price | UNKNOWN — 8× conflict between sources | excluded from all cost figures |
| qwen3.6 list price | UNKNOWN — open weights, variant unidentified | excluded |
| gemma4 list price | UNKNOWN — open weights, variant unidentified | excluded |
| reported cost, 5 of 8 models | absent (quota/plan routes report none) | validation limited to 3 models |
| cache_write, qwen3.8-flash | present in 3 of 22 runs | treated as 0; flagged `cache_write_unobservable` |
| cache_write, mimo/qwen3.6/gemma4 | absent | treated as 0 |
| cache fields, gemma4 | absent entirely | non-caching deployment |
| deepseek peak windows | MEDIUM confidence, third-party citing official docs | 3 of 15 runs priced at peak |
| glm5.2 list price | MEDIUM — search summary, corroborated by 3 catalogue entries | — |

None of these touches the top-band conclusion: all three band members are priced
at HIGH confidence with complete token coverage.

## 14. Caveats

1. **Reported ≠ normalized, and the gap is large.** For DeepSeek and GLM 5.2 the
   gateway charged 47–53% of list. Normalized cost answers "what would this cost
   at list price", not "what did MondayBench pay".
2. **Fable's cost is the only one where route and price vendor coincide**, so it
   is the only figure that is simultaneously a list-price estimate and a real
   invoice. The other four are counterfactuals.
3. **Cache asymmetry is a real artefact.** Fable's battery writes the prompt
   cache on run 1 and reads it on runs 2–3, at a 1-hour TTL. The gateway models
   mostly show cache misses on a fresh prompt per scenario. A cache-friendly
   route looks cheaper on repeats; the scenario mean over three runs absorbs
   this, but it is not a like-for-like caching comparison.
4. **"MondayBench-equivalent task" is not a universal request.** Prompts are
   11–24 KB and answers 0.9k–33k tokens. The scale table is a linear
   extrapolation of that specific shape.
5. **Scenario workloads differ by 6–8× in cost.** The single per-task figure is
   an equal-weight average over five different jobs.
6. **GLM 5.3 Flash's promotional 50% discount** was live at snapshot time. List
   is used; the promotion would halve its already-lowest figure.
7. **DeepSeek's normalized cost depends on the hour the benchmark ran** — the
   only model here with time-of-day pricing. 12 of 15 runs fell off-peak.
8. **Fable remains OFF-BENCHMARK / CLAUDE CODE ROUTE.** Every methodological
   caveat in `experiments/fable-5.1-full-mondaybench/README.md` and `AUDIT.md`
   still applies: Agent SDK system-prompt injection, runtime `currentDate`
   injection, no `temperature`/`top_p` control. Its score is provisional and it
   cannot enter the official leaderboard.
9. **Monday Score is unchanged and still means quality only.** No composite,
   weighted or efficiency score was created.

---

## Conclusions

**1. Can we compare costs homogeneously across all models?** **No.** Five of
eight have usable list pricing; three do not. And even among the five, one route
reports cache exclusively and four inclusively, one has time-of-day pricing, and
cache-write observability is partial. The comparison is valid for the five
priced models with the stated formulas — and it is valid for the whole top band,
which is what the question needed.

**2. Which models have incomplete pricing or usage?** Pricing UNKNOWN:
**MIMO v2.5, Qwen 3.6, Gemma 4**. Usage gaps: `qwen3.8-flash` cache-write in 19
of 22 runs, `gemma4` no cache fields at all, reported cost absent for 5 of 8.

**3. What is the top performance band?** **Qwen 3.8 Flash (95.07), GLM 5.3 Flash
(94.93), Claude Fable 5.1\* (94.90)** — unordered. Gaps of 0.03–0.17 against a
minimum run σ of 1.53.

**4. Cheapest in the band?** **GLM 5.3 Flash**, $10.71 per 1,000 tasks.

**5. Fastest in the band?** **Claude Fable 5.1\***, 50.9 s median TTFA.

**6. Lowest token consumption in the band?** **Claude Fable 5.1\***, 8,198
output tokens per task and 4,363 reasoning tokens.

**7. Best quality/cost on the data, without a composite score?** **GLM 5.3
Flash** — on the mathematical frontier, cheapest in the band, quality
indistinguishable from the two models above it.

**8. Best quality/latency?** **Claude Fable 5.1\*** — 5× faster to first answer
at unresolved-equal quality. On latency-per-dollar instead, DeepSeek V4 Flash.

**9. Does Fable buy measured quality for the extra cost?** **No.** `NO MEASURED
QUALITY ADVANTAGE FOR THE ADDITIONAL COST`. It buys measured *latency* (5×) and
measured *token efficiency* (2.4–3.9×) — neither of which is quality, and both
of which are outside the Monday Score.

**10. What does choosing Fable cost?**

| vs | multiple | 1k tasks | 100k tasks | 1M tasks |
|---|---:|---:|---:|---:|
| GLM 5.3 Flash | 42.6× | +$445.56 | +$44,556 | +$445,560 |
| Qwen 3.8 Flash | 29.3× | +$440.71 | +$44,071 | +$440,710 |

**11. Which models are mathematically dominated?** **DeepSeek V4 Flash** (by GLM
5.3 Flash), **GLM 5.2** (by three), **Claude Fable 5.1\*** (by both frontier
models). Frontier: GLM 5.3 Flash and Qwen 3.8 Flash.

**12. What changes when quality uncertainty is taken into account?** The
frontier's *shape* survives — the two cheapest models are still the ones to
beat — but two readings change. Fable's domination becomes "dominated on a
0.03-point difference that MondayBench cannot resolve", which is a statement
about the benchmark's resolution rather than about the model. And Qwen 3.8
Flash's position on the frontier is no longer a quality win over GLM 5.3 Flash;
it is 1.45× the cost for a gap of 0.14 points. Under uncertainty the frontier
collapses toward **one practical answer in the band: GLM 5.3 Flash**, with Fable
as the choice if 5× latency and 2.4× fewer tokens are worth 42.6× the price.

**13. Three visualisations for the web.**

1. **Quality vs cost, log-x scatter.** Monday Score on y (85–100), $/1k tasks on
   a log x-axis, a shaded horizontal band covering the three top-band models to
   show the unresolved zone, the Pareto frontier as a step line, UNKNOWN-pricing
   models listed beside the plot rather than plotted at zero. The log axis is
   essential — 10.71 to 456.27 is 42× and would otherwise flatten everything.
2. **Cost-at-scale line chart.** $/task × volume from 1 to 1M on log-log, one
   line per priced model. This is where 42.6× becomes $445k and where the
   decision actually gets made.
3. **Three-dimension small-multiples for the top band.** Three side-by-side bar
   charts — score with its σ as an error bar, $/1k on a log scale, median TTFA —
   over the same three models. Keeping them separate is the point: it shows the
   score bars overlapping while the cost bars do not.

---

**Artefacts** in `analysis/cost-value/`: `pricing-snapshot-2026-09-02.yaml`,
`billing-semantics.md`, `usage-coverage.json`, `normalized-costs.jsonl`,
`validation-reported-vs-normalized.json`, `cost-summary.json`,
`quality-vs-cost.json`, `quality-vs-latency.json`, `pareto.json`,
`incremental-cost.json`, `REPORT.md`.

Nothing was integrated into the site. Monday Score, the official leaderboard and
every frozen artefact are untouched.

**Sources for pricing** (read 2026-09-02): [openrouter.ai/qwen/qwen3.8-flash](https://openrouter.ai/qwen/qwen3.8-flash) ·
[docs.z.ai/guides/overview/pricing](https://docs.z.ai/guides/overview/pricing) ·
[devtk.ai/en/models/deepseek-v4-flash](https://devtk.ai/en/models/deepseek-v4-flash/) ·
[openrouter.ai/xiaomi/mimo-v2.5](https://openrouter.ai/xiaomi/mimo-v2.5) ·
[openrouter.ai/z-ai/glm-5.2](https://openrouter.ai/z-ai/glm-5.2) ·
[alibabacloud.com Model Studio pricing](https://www.alibabacloud.com/help/en/model-studio/model-pricing) ·
[openrouter.ai/google/gemma-4-31b-it](https://openrouter.ai/google/gemma-4-31b-it)
