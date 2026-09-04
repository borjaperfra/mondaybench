# Provider-public pricing fallback — OpenRouter

**Date:** 2026-09-02 · **Inferences run: zero.** No score, verdict, run or frozen
artefact touched. No first-party price replaced. No Value Score created.

**Provider snapshot:** `provider-pricing-snapshot-2026-09-02.yaml`
sha256 `6cb250f3dbbcf7043d63fa50f188184326388dd0e5f9132524cd9c4ebe503fac`
**First-party snapshot:** unchanged, sha256 `ec4dcc85…f389598`

**Result: one of three UNKNOWNs resolved.** MIMO v2.5 now carries an OpenRouter
route price. Qwen 3.6 and Gemma 4 stay UNKNOWN because no unique route could be
identified — the rule was applied rather than bent.

---

## 1. Two pricing classes, kept apart

| | FIRST_PARTY_LIST | PROVIDER_PUBLIC |
|---|---|---|
| what | the model vendor's own published rate | one third-party provider's public rate for one route |
| models | Fable 5.1, GLM 5.3 Flash, GLM 5.2, DeepSeek V4 Flash, Qwen 3.8 Flash | MIMO v2.5 |
| snapshot | `pricing-2026-09-02` | `provider-pricing-2026-09-02` |
| used in primary Pareto | **yes** | no |

Priority applied exactly as specified: FIRST_PARTY+EXACT → FIRST_PARTY+STRONG_MATCH
→ PROVIDER_PUBLIC+EXACT/STRONG_MATCH → UNKNOWN. **No model with a valid
first-party price was moved to a provider price**, and secondary provider prices
for those five were deliberately not computed — they cannot change the primary
analysis and publishing them alongside would invite exactly the substitution this
separation exists to prevent.

## 2. Identity check, per candidate

Evidence available for matching: the run `model_id`, and two facts recorded in
`models.yaml` — context length and declared reasoning capability.

### MIMO v2.5 → **EXACT** ✔

| | MondayBench | OpenRouter |
|---|---|---|
| model id | `mimo-v2.5` | `xiaomi/mimo-v2.5` — character-identical stem |
| context | 1M (models.yaml) | 1,050,000 |
| variants | one | one non-Pro route; `mimo-v2.5-pro` is a distinct SKU at ~3.7× |

Three independent signals agree and the only sibling is excluded by name and
price. **EXACT.**

### Qwen 3.6 → **AMBIGUOUS** ✘

Bare run id `qwen3.6`, no variant. Filtering OpenRouter by the recorded 256K
context leaves **three** candidates, and they are not close:

| Route | Input | Output | → $/1k on the MondayBench profile |
|---|---:|---:|---:|
| `qwen/qwen3.6-35b-a3b` | 0.05 | 0.70 | **2.47** |
| `qwen/qwen3.6-27b` | 0.60 | 3.60 | **14.21** |
| `qwen/qwen3.6-max-preview` | 1.027 | 6.162 | **23.95** |

A **9.7× spread**. `qwen3.6-flash` and `qwen3.6-plus` are excluded on context
(1M, not 256K). The second available signal points the other way and cannot
break the tie: every OpenRouter Qwen 3.6 route is a reasoning model while
`models.yaml` declares `reasoning: false` — but that is a statement about how
MondayBench configured the model, not about the model, and the NaN-served
monday-004 battery did return reasoning tokens. **Stays UNKNOWN.**

### Gemma 4 → **AMBIGUOUS** ✘

Bare run id `gemma4`. Both plausible routes match the recorded 256K context:

| Route | Params | Input | Output | → $/1k |
|---|---|---:|---:|---:|
| `google/gemma-4-26b-a4b-it` | 25.2B total / 3.8B active (sparse) | 0.042 | 0.22 | **0.44** |
| `google/gemma-4-31b-it` | 30.7B dense | 0.09 | 0.34 | **0.83** |

Only a **1.9× spread**, so a range was tempting. Declined anyway: the rule admits
only EXACT or STRONG_MATCH, and two architecturally distinct variants with no
disambiguating evidence is neither. Nothing in the run records, `models.yaml` or
Helmcode's `/v1/models` listing names a size. Recorded for transparency,
**not published. Stays UNKNOWN.**

## 3. MIMO v2.5 — the resolved case

| | |
|---|---|
| OpenRouter model ID | **`xiaomi/mimo-v2.5`** |
| identity confidence | **EXACT** |
| input | **$0.119** / 1M |
| output | **$0.238** / 1M |
| cache read | **$0.00255** / 1M |
| cache write | not published for this route |
| reasoning | no separate rate; billable output is `output_tokens` alone |
| context | 1,050,000 |
| retrieved | 2026-09-02, `openrouter.ai/xiaomi/mimo-v2.5` |
| **$/1k tasks** | **$3.33** |

**Cost at scale:** $0.003325 per task · **$3.33 / 1k** · $332.54 / 100k ·
$3,325.39 / 1M MondayBench-equivalent tasks.

**Billing semantics respected.** MIMO ran on an OpenAI-compatible gateway, where
`input_tokens` is inclusive of cached tokens, so uncached input is derived by
subtraction (24,034 uncached, 58,112 cache-read, 196,944 output across 15 runs).
`reasoning_tokens` is 0 on all MIMO runs — classification **(D) not observable**;
the model demonstrably streams a thinking phase but the counter reports nothing.
OpenRouter publishes no reasoning rate, so **no reasoning line is added and no
double-counting is possible**.

**Routing limitation, as required.** This route is served by **five upstream
providers** — GMICloud, DeepInfra, Xiaomi, StreamLake, NovitaAI — whose
individual prices differ. OpenRouter publishes **one consolidated route price**,
described on the page as reflecting the average price customers actually pay,
accounting for caching and provider discounts. Per the brief, a single published
route price is usable as PROVIDER_PUBLIC even when the backend varies. The
caveat that must travel with the figure: **this is a blended route price, not a
fixed contractual rate**, and a request pinned to a specific backend could cost
more or less.

**Xiaomi's first-party rate remains UNKNOWN.** The earlier conflict ($0.14/$0.28
in a catalogue entry vs a claimed permanent move to $1/$3 in May 2026) is not
resolved by this and is not claimed to be. The two were not reconciled as though
they were the same product. Note the live page also supersedes the stale
catalogue figure of $0.14/$0.28.

## 4. Publication table

| Model | Monday Score | Cost / 1k | Price basis | Pricing confidence | Identity |
|---|---:|---:|---|---|---|
| Qwen 3.8 Flash | 95.07 | $12.61 – $15.56 | First-party | MEDIUM | AMBIGUOUS (region) |
| GLM 5.3 Flash | 94.93 | **$10.71** | First-party | HIGH | STRONG_MATCH |
| Claude Fable 5.1\* | 94.90 | $456.27 | First-party | HIGH | EXACT |
| DeepSeek V4 Flash | 91.70 | $12.94 – $25.88 | First-party | HIGH | STRONG_MATCH |
| MIMO v2.5 | 86.67 | **$3.33** | **OpenRouter** | HIGH | EXACT |
| GLM 5.2 | 86.50 | $39.50 | First-party | HIGH | STRONG_MATCH |
| Qwen 3.6 | 68.77 | UNKNOWN | Unknown | UNKNOWN | AMBIGUOUS |
| Gemma 4 | 63.00 | UNKNOWN | Unknown | UNKNOWN | AMBIGUOUS |

\* Provisional, OFF-BENCHMARK / CLAUDE CODE ROUTE, excluded from the official
ranking.

**No cost figure may ever be shown without its Price basis.**

## 5. Two Pareto analyses

### A. PRIMARY — FIRST_PARTY_LIST only (**unchanged**)

| | Model | Score | $/1k |
|---|---|---:|---:|
| frontier | **GLM 5.3 Flash** | 94.93 | 10.71 |
| frontier | **Qwen 3.8 Flash** | 95.07 | 15.56 |
| dominated | DeepSeek V4 Flash | 91.70 | 25.88 |
| dominated | GLM 5.2 | 86.50 | 39.50 |
| dominated | Claude Fable 5.1\* | 94.90 | 456.27 |

Excluded for want of a first-party price: MIMO v2.5, Qwen 3.6, Gemma 4.
This remains the methodologically clean analysis and is **identical to before**.

### B. EXTENDED PROVIDER — first-party + provider-public

> **MIXES COST CLASSES.** Vendor list prices are compared against one reseller's
> blended route price. These are different commercial products; the comparison
> is indicative only and does not change the primary frontier.

| | Model | Score | $/1k | Basis |
|---|---|---:|---:|---|
| frontier | **MIMO v2.5** | 86.67 | **3.33** | OpenRouter |
| frontier | **GLM 5.3 Flash** | 94.93 | 10.71 | First-party |
| frontier | **Qwen 3.8 Flash** | 95.07 | 15.56 | First-party |
| dominated | DeepSeek V4 Flash | 91.70 | 25.88 | First-party |
| dominated | GLM 5.2 | 86.50 | 39.50 | First-party |
| dominated | Claude Fable 5.1\* | 94.90 | 456.27 | First-party |

MIMO adds a new cheap corner. Two consequences, both stated carefully:

* **GLM 5.2 is now dominated by four models instead of three** — MIMO v2.5 scores
  0.17 higher (86.67 vs 86.50) at 11.9× less cost. Note the 0.17-point edge is
  itself noise, so the honest reading is "same quality, far cheaper", not "better".
* **MIMO v2.5 vs GLM 5.3 Flash is a real alternative trade-off**: 3.2× cheaper
  for 8.26 points less. **But that gap is not clearly resolved** — MIMO's own
  mean run σ is 8.32, the highest in the set, so 8.26 sits right at its noise
  floor. Treat it as "probably worse, materially cheaper", not a settled tier
  difference.

## 6. Top performance band — unchanged

Nothing here touches it. **Qwen 3.8 Flash 95.07 · GLM 5.3 Flash 94.93 · Claude
Fable 5.1\* 94.90 — TOP PERFORMANCE BAND, UNORDERED**, on first-party pricing:

* **GLM 5.3 Flash cheapest** in the band, $10.71/1k.
* **Fable 5.1\* fastest**, 50.9 s median TTFA.
* **`NO MEASURED QUALITY ADVANTAGE FOR THE ADDITIONAL COST`** for Fable, at
  42.6× GLM 5.3 Flash and 29.3–36.2× Qwen 3.8 Flash.

OpenRouter did not replace any band member's price and none of these figures moved.

## 7. Does anything economic change materially?

**In the primary analysis: no.** The first-party frontier, the band, the cheapest
top-band model and the Fable conclusion are all identical.

**In the extended analysis: one genuinely new data point.** MIMO v2.5 at
**$3.33/1k** is the cheapest measured cost in the whole set — 3.2× below GLM 5.3
Flash — and it establishes that the cost floor of the field is well under $10/1k.
That is worth publishing, with three qualifications: it is a provider price not a
list price, it is a blended route price across five backends, and MIMO's quality
gap to the band is not cleanly resolved against its own high run variance.

It does **not** displace GLM 5.3 Flash as the value answer for the top band,
because MIMO is not in the top band.

## 8. Recommended web labels

Three labels, short and unambiguous:

| Label | Tooltip |
|---|---|
| **First-party** | "Published list price from the model/API vendor." |
| **OpenRouter** | "Public OpenRouter price for this model route. This is provider-specific pricing, not a canonical model list price." |
| **Unknown** | "No sufficiently identified price source." |

Display rules:

1. **Never show a cost without its basis label.** A bare "$3.33" beside "$10.71"
   implies they are the same kind of number; they are not.
2. **Style the labels differently** — First-party solid, OpenRouter outlined or
   muted, Unknown grey. A reader should see the class before reading the figure.
3. **Default the cost chart to first-party only**, with an explicit "include
   provider prices" toggle that surfaces the mixing warning when enabled. The
   primary frontier must be what loads by default.
4. **Render ranges as ranges** — Qwen 3.8 Flash and DeepSeek V4 Flash are
   intervals, not points.
5. **Keep Unknown rows visible** with the score and latency populated. Removing
   them would hide that a third of the field has no usable price.
6. **Show both snapshot ids** wherever figures appear: `pricing-2026-09-02` and
   `provider-pricing-2026-09-02`, with their hashes available on hover or in a
   methodology footer.

---

## Answers

**1. Which UNKNOWNs did OpenRouter resolve?** One of three — **MIMO v2.5**.
Qwen 3.6 and Gemma 4 remain UNKNOWN.

**2. Exact OpenRouter model ID?** **`xiaomi/mimo-v2.5`**.

**3. Identity confidence?** **EXACT** — slug matches the run `model_id`, the
route's 1,050,000-token context matches the recorded 1M, and the only sibling
(`mimo-v2.5-pro`) is excluded by name and by a ~3.7× price difference.

**4. Input/output pricing?** **$0.119 / $0.238** per 1M, cache read
**$0.00255**; no cache-write and no reasoning rate published.

**5. Calculated $/1k?** **$3.33** per 1,000 MondayBench-equivalent tasks
($0.003325/task; $332.54/100k; $3,325.39/1M).

**6. Which remain UNKNOWN?** **Qwen 3.6** (3 candidate routes at the matching
context, 9.7× spread) and **Gemma 4** (2 candidate routes, 1.9× spread, different
architectures). Neither reaches EXACT or STRONG_MATCH.

**7. Primary Pareto?** **GLM 5.3 Flash ($10.71) and Qwen 3.8 Flash ($15.56)** —
first-party only, unchanged.

**8. Extended provider Pareto?** **MIMO v2.5 ($3.33), GLM 5.3 Flash ($10.71),
Qwen 3.8 Flash ($15.56)** — mixes cost classes, indicative only.

**9. Does any economic finding change materially?** Not in the primary analysis.
In the extended view, MIMO v2.5 becomes the cheapest measured model in the field
and pushes GLM 5.2 into deeper domination — same score, 11.9× less cost. The
top-band conclusions are untouched.

**10. How to show first-party vs OpenRouter on the web?** Three labelled classes
(First-party / OpenRouter / Unknown), never a figure without its label, visually
distinct styling, first-party-only as the default chart with an opt-in toggle for
provider prices, ranges rendered as ranges, Unknown rows kept visible, and both
snapshot ids shown in the methodology footer.

---

**Artefacts.** New: `provider-pricing-snapshot-2026-09-02.yaml` + `.sha256`,
`PROVIDER-PRICING.md`. Updated: `publication-data.json` (now carries
`pricing_class`, `price_basis`, `normalized_first_party_cost_per_1k`,
`provider_public_cost_per_1k`, and per-snapshot attribution), `pareto.json` (now
dual: `primary` and `extended_provider`). Preserved:
`publication-data.FIRST-PARTY-ONLY.json`, `pareto.PRE-GATE.json`.
**Unchanged:** the first-party snapshot and its hash, `GATE.md`, `REPORT.md`,
`billing-semantics.md`, `usage-coverage.json`, `normalized-costs.jsonl`,
`cost-summary.json`, `quality-vs-latency.json`.

Nothing integrated into the web. Leaderboard, Monday Score, runs and verdicts
untouched.
