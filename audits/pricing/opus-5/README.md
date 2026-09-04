# Claude Opus 5 Pricing Audit

## Executive summary

The 15 existing Claude Opus 5 runs cost **$0.2469 per MondayBench-equivalent
task** at Anthropic's public first-party list rates — **$246.91 per 1,000**,
**$24,690.82 per 100,000**, **$246,908.23 per 1,000,000** MondayBench-equivalent
tasks. Pricing identity is **EXACT** on a **FIRST_PARTY_LIST** basis with
**HIGH** confidence: the five rates were established two independent ways — read
off Anthropic's own pricing page, and solved algebraically from the
provider-reported meter — and the two agree exactly. Recomputing every run from
the published rates reproduces the provider's own Opus-only figure on **15 of 15
runs at 0.000000000% error**.

The headline trade-off is not the one the Fable 5.1 audit set up. **Claude Opus
5\* records a higher measured score than Claude Fable 5.1\* (97.07 against
94.90) at roughly half the cost ($246.91 against $456.27 per 1,000)** — it is
both better and cheaper on these measurements. Against the two official
top-band models the trade-off is the familiar one: **+2.00 points over Qwen 3.8
Flash at 15.9–19.6× the cost, and +2.14 points over GLM 5.3 Flash at 23.1× the
cost**, while being roughly 6× faster to first answer and using 2–3× fewer
output tokens.

Opus remains **PROVISIONAL**. The pricing audit does not change that.

| | Claude Opus 5\* |
|---|---|
| Monday Score | **97.07** (independently blind-rejudged) |
| Cost / 1k MondayBench-equivalent tasks | **$246.91** |
| Median TTFA | 41.3 s |
| Mean output tokens | 9,201 |
| Pricing basis | First-party list, EXACT, HIGH |
| Status | **PROVISIONAL** |

---

## Where this lives

The repo's canonical home for the **published** cost layer is
`analysis/cost-value/`, and it is untouched here: all three frozen pricing
snapshots remain byte-identical, and `publication-data.json`, `pareto.json` and
`cost-summary.json` were read and never written. Opus is provisional and
off-benchmark, so it does not belong in the published layer yet. This audit
therefore lives under `audits/pricing/opus-5/` and adds one **additive**
snapshot, `pricing-source.json`, which supersedes nothing.

---

## Pricing source

First-party vendor pricing page, retrieved 2026-09-02:
`https://platform.claude.com/docs/en/about-claude/pricing`

The Claude Opus 5 row, verbatim:

```
| Claude Opus 5 | $5 / MTok | $6.25 / MTok | $10 / MTok | $0.50 / MTok | $25 / MTok |
   Base input     5m writes    1h writes     Cache hits    Output
```

| Bucket | Rate | Multiplier |
|---|---:|---|
| Base input | **$5.00 / MTok** | — |
| Output | **$25.00 / MTok** | — |
| Cache read (hit) | **$0.50 / MTok** | 0.1× base input |
| Cache write, 1 hour | **$10.00 / MTok** | 2× base input |
| Cache write, 5 minute | $6.25 / MTok | 1.25× base input — **not used** |

**Opus 5 is not priced like Fable 5.1, and assuming it was would have doubled
the answer.** Fable 5.1 is $10/$50 with a cache-read *exception*: the page's
footnote reads *"Cache hits and refreshes on Claude Fable 5.1 and Claude Mythos
5.1 are priced at 0.025x the base input price. All other models use the standard
0.1x multiplier."* Opus 5 is not an exception, so its cache read is 0.1× —
$0.50/MTok, not $0.125/MTok.

### Two independent lines of evidence

**Line 1 — the vendor page**, above. Corroborated by the page's own worked
example, which prices Opus 5 cache reads as `40,000 × $5 × 0.1 / 1,000,000`.

**Line 2 — the solved meter.** The route reports `costUSD` at
`costBasis: "list"`. Solving it for the unknown rates, without reference to the
page:

* monday-001 run2 and run3 differ *only* in output tokens →
  `(0.0762255 − 0.0657005) / (2952 − 2531)` = **$25.000000/MTok output**
* monday-001 run2 is a cache-read run → **$0.500000/MTok**, exactly **0.1×** input
* monday-001 run1 is a cache-write run → **$10.000000/MTok**, exactly **2.0×** input

Verified across every run: worst-case error **0.000000000%** on all 15.

Two methods, one answer, including both canonical multipliers. That is why
identity is `EXACT` and confidence `HIGH` rather than asserted.

### Recorded but not applied

| Modifier | Published | Why not applied |
|---|---|---|
| Batch API | $2.50 / $12.50 per MTok (−50%) | `service_tier: standard` on all 15 runs; none was a batch request |
| Fast mode | $10 / $50 per MTok | `speed: standard`, route reports `fast_mode_state: off` |
| US data residency | 1.1× on all categories | `inference_geo: not_available` — the global default |
| Regional endpoints | +10% | These are first-party API calls (`provider: firstParty`), not a partner cloud |
| Subscription | n/a | A seat price is not a per-token rate and cannot be compared with one. Deliberately priced at public list so the figure is comparable with the rest of the benchmark |

---

## Billing semantics

**Input tokens are cache-EXCLUSIVE.** Anthropic reports `input_tokens`,
`cache_creation_input_tokens` and `cache_read_input_tokens` as three *disjoint*
buckets. On these runs `input_tokens` reads **2** on every run, because
essentially the whole prompt is either a cache write or a cache read. Each
bucket is charged at its own rate; `effective_prompt_tokens` (their sum, mean
6,784) is kept as a descriptive metric only and is never multiplied by a single
rate.

**Cache modality was observed, not inferred.** `usage.cache_creation` splits the
write into `ephemeral_1h_input_tokens` and `ephemeral_5m_input_tokens`. Across
all 15 runs every cache-creation token is **1-hour** and the 5-minute count is
zero, so $10.00/MTok applies and $6.25/MTok never does. Four runs create the
cache (run 1 of monday-001, -002, -003, -005); the other eleven read it.

**Reasoning tokens are already inside billable output, and adding them would be
double counting.** Proven two ways:

1. The pricing page defines no reasoning or thinking category anywhere. The only
   output category is "Output tokens".
2. The meter settles it. Charging `output_tokens` alone reproduces the reported
   Opus cost at **0.000000000%** on all 15 runs. Adding `thinking_tokens` on top
   would overstate monday-004 run 1 by **69.71%** — $1.0258 against a reported
   $0.6044.

So `reasoning_additional_cost = 0`, by demonstration rather than assumption.
`thinking_tokens` (mean 4,837/run, 52.6% of output) is a *subset* of
`output_tokens` (mean 9,201).

**The auxiliary Haiku call is excluded.** The route made a
`claude-haiku-4-5` call per run that `DISABLE_NON_ESSENTIAL_MODEL_CALLS=1` did
not suppress, so `total_cost_usd` covers Claude Code's overhead as well as the
generation. The normalized figure uses the `claude-opus-5` line and its token
buckets only. All three are reported so the exclusion is visible:

| Per task, mean | |
|---|---:|
| Route total | $0.252871 |
| **Opus only — the comparable figure** | **$0.246908** |
| Auxiliary Haiku | $0.005963 (2.36% of route cost) |

We are pricing the cost of the Opus generation, not the cost of running Claude
Code.

---

## Reported vs normalized

| Classification | Runs |
|---|---:|
| `EXACT_RECONCILIATION` (\|diff\| < 1e-6 %) | **15** |
| `ROUNDING_ONLY` (\|diff\| < 0.5 %) | 0 |
| `MATERIAL_DIFFERENCE` (≥ 0.5 %) | 0 |
| `UNAVAILABLE` | 0 |

Mean Opus-only reported **$0.246908**; mean normalized **$0.246908**;
difference **$+0.000000000**. Worst single-run absolute difference
**0.000000000%**.

No price was adjusted to make this fit. The rates were solved from three runs
and then verified against all fifteen.

---

## Cost by scenario

| Scenario | Mean / task | Cost / 1k | Mean cache create | Mean cache read | Mean output | Mean reasoning |
|---|---:|---:|---:|---:|---:|---:|
| monday-001 | $0.0894 | $89.40 | 1,610 | 3,221 | 2,867 | 667 |
| monday-002 | $0.1803 | $180.31 | 1,268 | 2,535 | 6,654 | 3,285 |
| monday-003 | $0.1768 | $176.76 | 1,742 | 3,484 | 6,304 | 3,003 |
| monday-004 | **$0.5688** | **$568.81** | 0 | 12,629 | 22,499 | 14,631 |
| monday-005 | $0.2193 | $219.26 | 2,473 | 4,947 | 7,682 | 2,601 |

**monday-004 costs 6.4× monday-001** and is the single reason the overall mean
sits where it does. The driver is output, not prompt: 22,499 output tokens
against 2,867, of which 14,631 are reasoning.

Cost composition across all 15 runs:

| Bucket | Cost | Share |
|---|---:|---:|
| Output | $3.4505 | **93.16%** |
| Cache creation | $0.2128 | 5.74% |
| Cache read | $0.0402 | 1.09% |
| Uncached input | $0.0001 | 0.00% |
| **Total** | **$3.7036** | |

This is an **output-dominated** cost profile. The prompt side is 6.84% of the
bill, and caching saved $0.3620 against paying those reads as uncached input.

**One caveat on comparability.** In four scenarios run 1 pays the 1-hour cache
write and runs 2–3 pay reads. In monday-004 all three runs pay *reads* and none
pays a write, because the write was paid by a generation that was later
discarded (`GENERATION-INCIDENT.md` in the experiment directory). The
as-observed figure is faithful to what was metered, but it omits one
12,629-token write worth **$0.126290**. Reported rather than smoothed into the
mean. More generally, 11 of 15 runs benefit from a warm 1-hour cache because the
schedule is three repeats of five prompts; a cold single run of each task would
pay writes instead of reads and cost more. That is a property of the run
schedule, and it applies to the other models' published figures too.

---

## Top-model comparison

| Model | Monday Score | Cost / 1k | Median TTFA | Mean output tokens | Pricing basis | Status |
|---|---:|---:|---:|---:|---|---|
| **Claude Opus 5\*** | **97.07** | **$246.91** | **41.3 s** | 9,201 | First-party | **PROVISIONAL** |
| Qwen 3.8 Flash | 95.07 | $12.61–$15.56 | 258.9 s | 31,687 | First-party | official |
| GLM 5.3 Flash | 94.93 | $10.71 | 278.2 s | 20,072 | First-party | official |
| Claude Fable 5.1\* | 94.90 | $456.27 | 50.9 s | 8,198 | First-party | PROVISIONAL |

Comparator figures were read from `analysis/cost-value/publication-data.json`
and verified against the canonical values before use. Nothing was overwritten.

### Trade-offs

**vs Claude Fable 5.1\*** — better *and* cheaper
* Score **+2.17**
* Cost **0.54×** — **−$209.36** / 1k, **−$20,936** / 100k, **−$209,360** / 1M
* TTFA ratio 1.23× (Opus faster)
* Output tokens 0.89× (Fable slightly more concise)

**vs Qwen 3.8 Flash**
* Score **+2.00**
* Cost **15.87×–19.58×** — **+$231.35 to +$234.30** / 1k, **+$23,135 to
  +$23,430** / 100k, **+$231,350 to +$234,300** / 1M
* TTFA ratio 6.27× (Opus faster)
* Output tokens 3.44× (Opus more concise)

**vs GLM 5.3 Flash**
* Score **+2.14**
* Cost **23.05×** — **+$236.20** / 1k, **+$23,620** / 100k, **+$236,200** / 1M
* TTFA ratio 6.74× (Opus faster)
* Output tokens 2.18× (Opus more concise)

No score-per-dollar, no value score, no efficiency score. Quality, cost, speed
and output length are four separate readings and stay that way.

---

## Experimental Pareto

**The official frontiers are unchanged and were not recomputed.** Reproduced
from `analysis/cost-value/pareto.json`:

* Official **primary** (first-party priced only): `glm5.3-flash`, `qwen3.8-flash`
* Official **extended** (also admits provider-public prices): `gemma4`,
  `mimo-v2.5`, `glm5.3-flash`, `qwen3.8-flash`

Experimentally, adding provisional Opus on each basis:

* First-party basis + Opus: **Qwen 3.8 Flash, GLM 5.3 Flash, Claude Opus 5\***
* Extended basis + Opus: Qwen 3.8 Flash, GLM 5.3 Flash, MIMO v2.5, Gemma 4,
  **Claude Opus 5\***

Opus would sit on the frontier, and **Claude Fable 5.1\* would leave it** —
Opus beats it on measured score and undercuts it on cost, which is domination
under the frozen definition (*A dominates B iff A.score ≥ B.score AND A.cost ≤
B.cost, with at least one strict*).

**Experimental only.** These frontiers contain a provisional, off-benchmark
result. They must not replace, modify or be shown beside the official frontiers.
Being on a frontier is not a ranking and not a recommendation.

---

## What Opus buys

Read off the four measurements, without inventing a composite:

**Against the cheap top-band models (Qwen, GLM 5.3)** the pattern is *higher
measured quality, much higher cost, much lower latency, far fewer output
tokens*. Two points of score cost 16–23× more per task. Whether that is worth
it depends entirely on whether two points of measured quality matters for the
workload — and MondayBench cannot resolve a two-point gap in the first place
(see the inter-judge audit's variance analysis). What is *not* ambiguous is the
speed and concision: roughly 6× faster to first answer and 2–3× fewer output
tokens.

**Against Fable 5.1** the pattern is different and worth stating plainly:
*higher measured quality, lower cost, lower latency, marginally more verbose*.
On these measurements Opus is simply the better of the two Claude results, and
the Fable audit's framing — a large quality premium paid for speed — does not
transfer. Opus 5 lists at half Fable 5.1's per-token price while scoring higher
here.

**The cost profile is output-dominated** (93.16%), so anything that shortens
responses moves the bill almost one-for-one, and prompt caching — which saved
$0.36 across these runs — is close to noise by comparison. monday-004 shows this
directly: it is the most expensive scenario by 6.4× purely because it generates
the most tokens.

Framing note: Opus **records the highest measured score in this experiment**.
That is not the same as winning MondayBench, and it is not an official result.

---

## Methodological caveat

Opus 5 remains **PROVISIONAL** because generation used Claude Code rather than
MondayBench's standard provider route: the Agent SDK preamble is prepended to
the frozen system prompt and a `<system-reminder>` is injected into the user
turn, which makes the served conditions non-equivalent to the seven published
models. The score used here (97.07) is the independent blind re-judge result,
which addresses judge validity only. Neither that re-judge nor this pricing
audit changes the generation-route status.

---

## Files

```
calculate.py          recomputes every figure from raw usage + pricing-source.json
pricing-source.json   the additive rate card, identity, billing semantics, evidence
summary.json          full machine-readable result
run-costs.csv         15 rows, per-bucket cost and reconciliation
scenario-costs.csv    5 rows
top-comparison.csv    the four-model table
```

Reproduce with:

```
python audits/pricing/opus-5/calculate.py
```

No normalized cost is hardcoded. The script exits non-zero if any run's served
model is not `claude-opus-5`, if the cache-creation split does not reconcile, or
if any run carries a billing modifier that would change the rate card.
