# Final pricing integrity gate — first-party verification

**Date:** 2026-09-02 · **Inferences run: zero.** No score, verdict, run, frozen
artefact or leaderboard was touched. No Value Score created. Web unchanged.

**Snapshot frozen:** `pricing-snapshot-2026-09-02.yaml`
sha256 `ec4dcc8537bf4af5a8944f7cc15cda5b55f789826a535b8b665b0c256f389598`
(also in `pricing-snapshot-2026-09-02.sha256`)

**Source policy tightened:** every published price now comes from a vendor
pricing page or vendor API documentation. OpenRouter, models.dev, Artificial
Analysis, resellers and blogs were used only to *locate* those pages and justify
nothing. That change alone forced one downgrade.

---

## 1. Primary-source verification, per price

| Model | Source | Type | Result |
|---|---|---|---|
| claude-fable-5-1 | `platform.claude.com/docs/en/about-claude/pricing` | vendor pricing page | **all 5 rates confirmed** |
| glm5.3-flash | `docs.z.ai/guides/overview/pricing` | vendor pricing page | confirmed, already first-party |
| glm5.2 | `docs.z.ai/guides/overview/pricing` | vendor pricing page | **re-sourced, MEDIUM → HIGH** |
| deepseek-v4-flash | `api-docs.deepseek.com/quick_start/pricing` | vendor API docs | **re-sourced, MEDIUM → HIGH** |
| qwen3.8-flash | `alibabacloud.com/help/en/model-studio/model-pricing` | vendor pricing page | **HIGH → MEDIUM, point → range** |
| mimo-v2.5 | none found | — | stays UNKNOWN |
| qwen3.6 | SKU not resolvable | — | stays UNKNOWN |
| gemma4 | no first-party API price | — | stays UNKNOWN |

## 2. DeepSeek V4 Flash — resolved

From DeepSeek's own API documentation:

| | input (cache miss) | cache hit | output |
|---|---:|---:|---:|
| **off-peak** | 0.22 | 0.007 | 0.66 |
| **peak** | 0.44 | 0.014 | 1.32 |

* **Timezone: UTC.** Matches the runs' own `timestamp_utc`, so band assignment
  per run is unambiguous.
* **Windows: 01:00–04:00 and 06:00–10:00 UTC, Monday–Friday.** The weekday
  condition is **new** — the previous calculator applied the hours only.
* **SKU:** `deepseek-v4-flash`, character-identical to the run `model_id`. The
  page also lists `deepseek-v4-pro` and `deepseek-v4-flash-vision-exp`, neither
  a plausible match.
* **Effective date: none published.** The vendor states prices may change.

**(A) Can the runs be mapped unambiguously?** **Yes.** UTC timestamps against UTC
windows. Re-checked with the weekday condition: all three peak-window runs fell
on **Friday 2026-08-28**, so the assignment is unchanged at 3 peak / 12 off-peak.
The formula is now correct regardless.

**(B) Which price for the $/1k extrapolation?** **A range.** $/1k is a
forward-looking figure and the price genuinely depends on when the task runs, so
a single number would be false precision:

| basis | $/1k |
|---|---:|
| all off-peak | 12.94 |
| **as observed** (3 peak / 12 off-peak) | **13.67** |
| all peak | 25.88 |

**Published as $12.94–$25.88/1k**, with as-observed noted. Pareto placement uses
the **conservative (peak) end**, so the figure cannot flatter this model.

## 3. GLM 5.2 — first-party confirmed, upgraded

Z.AI's own pricing table lists **GLM-5.2** at input **$1.4**, output **$4.4**,
cached input **$0.26**, cache storage "Limited-time Free". Numbers unchanged from
the previous snapshot; **provenance upgraded MEDIUM → HIGH**.

* **Exactly GLM 5.2?** Yes — the row is labelled `GLM-5.2`.
* **Not another variant?** The neighbouring SKUs differ (GLM-5 at $1.0/$3.2,
  GLM-4.7 at $0.6/$2.2), so neither is a plausible match for a run id of
  `glm5.2`. **Robustness note:** GLM-5.1 carries the *identical* trio, so even a
  5.1/5.2 mix-up would not move the figure.
* **Not reseller pricing?** No — vendor page.
* **No promotion** on GLM-5.2; the 50% discount on that page is GLM-5.3-Flash only.
* **Region/product match?** Z.AI publishes one global table with no regional
  variants.

**Identity STRONG_MATCH**, not EXACT: the runs went through Helmcode, not Z.AI
directly. Helmcode charged exactly 50% of this list price on both input and
output — which is why reported and normalized differ by 1.87×.

## 4. Identity gate

| Run model ID | → Provider | → Public SKU | → Pricing source | Identity | Publishable |
|---|---|---|---|---|---|
| `claude-fable-5-1` | Anthropic (first party) | Claude Fable 5.1 | platform.claude.com | **EXACT** | point |
| `glm5.3-flash` | Z.AI via NaN | GLM-5.3-Flash | docs.z.ai | **STRONG_MATCH** | point |
| `glm5.2` | Z.AI via Helmcode | GLM-5.2 | docs.z.ai | **STRONG_MATCH** | point |
| `deepseek-v4-flash` | DeepSeek via Helmcode | deepseek-v4-flash | api-docs.deepseek.com | **STRONG_MATCH** | **range** (time-of-day) |
| `qwen3.8-flash` | Alibaba via NaN | qwen3.8-flash | alibabacloud.com | **AMBIGUOUS** | **range** (region) |
| `mimo-v2.5` | Xiaomi via NaN | — | — | **UNKNOWN** | UNKNOWN |
| `qwen3.6` | via Helmcode/NaN | — | — | **UNKNOWN** | UNKNOWN |
| `gemma4` | via Helmcode | — | — | **UNKNOWN** | UNKNOWN |

Rule applied as specified: point figures only for EXACT or justified
STRONG_MATCH; AMBIGUOUS → range; UNKNOWN → UNKNOWN.

**Why Qwen 3.8 Flash is AMBIGUOUS.** The SKU name matches character-for-character
on Alibaba's own page, but two things the aggregator hid appear there:

1. **Pricing is regional.** Singapore (International) $0.15/$0.47; China
   (Beijing), Hong Kong, Frankfurt, US (Virginia) and Tokyo all $0.113/$0.382 —
   a **23% spread**. The runs went through the NaN gateway and nothing in the
   records identifies which region NaN uses, or whether NaN fronts Alibaba.
2. **Cache prices are not published.** Alibaba's context-cache page states the
   explicit-cache hit price for `qwen3.8-flash` "is not 10% of the standard input
   token price. For specific pricing, see the Model Studio console", and the same
   for the implicit cache; cache creation is given only as "typically 125% of the
   standard input token price". No first-party number exists.

**Materiality, measured rather than asserted:** cache lines are **0.14%** of this
model's total normalized cost (output alone is 95.7%), so the unpublished cache
rates are immaterial. The region is what matters: **$12.61–$15.56/1k**.

## 5. Fable cache write — confirmed at source

Anthropic's own pricing page, Claude Fable 5.1 row:

| Base input | 5m cache write | **1h cache write** | Cache hits & refreshes | Output |
|---|---|---|---|---|
| $10/MTok | $12.50/MTok | **$20/MTok** | $0.25/MTok | $50/MTok |

All five figures confirmed. The $0.25 read carries a footnote: cache hits on
Fable 5.1 and Mythos 5.1 are priced at **0.025× base input**, against the 0.1×
every other model uses — which is why $0.25 and not $1.00.

**1-hour semantics confirmed:** the prompt-caching table gives "1-hour cache
write | **2× base input price** | Cache valid for 1 hour", and notes it pays off
after two cache reads. $20.00 is published, not inferred.

**That this was the modality Claude Code used** is established independently from
the meter: solving provider-reported `costUSD` for the cache-write rate returns
**$20.000/MTok** on every cache-writing run (A1, monday-001 run 1, monday-004
run 1, agreeing to three decimals). The harness documents a 1-hour prompt-cache
TTL for this session.

**Finding preserved — the strongest validation in the set:** with these five
first-party rates, **normalized list cost = provider-reported cost on all 15
runs, 0.00% error**. Identity is EXACT because the served route and the
list-price vendor are the same party. Every other model's normalized cost is a
counterfactual; Fable's is simultaneously a list-price estimate and a real
invoice.

## 6. Qwen and GLM 5.3 Flash — SKU, cache, reasoning, promotions

| | Qwen 3.8 Flash | GLM 5.3 Flash |
|---|---|---|
| exact SKU | `qwen3.8-flash` on Alibaba's page | `GLM-5.3-Flash` on Z.AI's page |
| list input / output | 0.113–0.15 / 0.382–0.47 (regional) | 0.15 / 0.50 |
| cache read | **not published by vendor** | 0.03 |
| cache write | **not published** ("typically 125% of input") | 0.00 (storage free) |
| context tiering | none (flat to 1M) | none published |
| reasoning in output | **yes** — `reasoning ≤ output` in 22/22 runs, no reasoning rate published | **yes** — 16/16, no reasoning rate published |
| promotion | none | **50% off, ends 2026-09-09 24:00 UTC+8** |

**Promotion handling as required.** GLM 5.3 Flash's promotional trio
($0.075/$0.25/$0.015) is stored in a separate `promotion:` block with its end
date and source, and is **never** used for the headline. The main table uses
**list** and therefore stays valid after 2026-09-09. Recorded secondary figure:
**promo $5.36/1k** against **list $10.71/1k** — the promotion *widens* its cost
advantage, so using list is also the conservative choice.

## 7. Snapshot changes — OLD / NEW / SOURCE / WHY

| # | Model | Field | OLD | NEW | Source | Why |
|---|---|---|---|---|---|---|
| 1 | claude-fable-5-1 | source | claude-api skill + models.dev | platform.claude.com pricing page | vendor | first-party policy; all 5 rates confirmed, **no number changed** |
| 2 | claude-fable-5-1 | cache_write_5m | (absent) | 12.50 recorded alongside 20.00 | vendor | both TTLs now published in the snapshot |
| 3 | glm5.3-flash | promotion block | prose note | structured `promotion:` with end date + source | vendor | list/promo separation |
| 4 | glm5.2 | pricing_confidence | MEDIUM | **HIGH** | docs.z.ai | re-sourced to vendor page; **numbers unchanged** |
| 5 | deepseek-v4-flash | pricing_confidence | MEDIUM | **HIGH** | api-docs.deepseek.com | re-sourced to vendor API docs; **numbers unchanged** |
| 6 | deepseek-v4-flash | peak window | hours only | hours **+ Monday–Friday** | vendor | new constraint; band assignment unchanged (all 3 peak runs were a Friday) |
| 7 | deepseek-v4-flash | published cost | point $13.67/1k | **range $12.94–$25.88/1k** | — | price is time-of-day dependent; range is the honest form |
| 8 | qwen3.8-flash | pricing_confidence | HIGH | **MEDIUM** | alibabacloud.com | prior figure was OpenRouter, now disallowed |
| 9 | qwen3.8-flash | identity_confidence | (implicit exact) | **AMBIGUOUS** | alibabacloud.com | pricing is regional; serving region not determinable |
| 10 | qwen3.8-flash | published cost | point $15.56/1k | **range $12.61–$15.56/1k** | — | AMBIGUOUS identity → range, per the gate rule |
| 11 | qwen3.8-flash | cache_read / cache_write | 0.016 / 0.20 (OpenRouter) | **UNPUBLISHED** (placeholder retained, flagged) | alibabacloud.com | vendor explicitly does not publish; immaterial at 0.14% of cost |

**No quality figure changed. No score, verdict or run was touched.**

## 8. Recomputed with verified prices

| Model | Score | $/1k tasks (LIST) | Kind | Pricing | Identity |
|---|---:|---:|---|---|---|
| Qwen 3.8 Flash | 95.07 | **12.61 – 15.56** | RANGE | MEDIUM | AMBIGUOUS |
| GLM 5.3 Flash | 94.93 | **10.71** | POINT | HIGH | STRONG_MATCH |
| Claude Fable 5.1\* | 94.90 | **456.27** | POINT | HIGH | EXACT |
| DeepSeek V4 Flash | 91.70 | **12.94 – 25.88** | RANGE | HIGH | STRONG_MATCH |
| MIMO v2.5 | 86.67 | UNKNOWN | — | UNKNOWN | UNKNOWN |
| GLM 5.2 | 86.50 | **39.50** | POINT | HIGH | STRONG_MATCH |
| Qwen 3.6 | 68.77 | UNKNOWN | — | UNKNOWN | UNKNOWN |
| Gemma 4 | 63.00 | UNKNOWN | — | UNKNOWN | UNKNOWN |

Secondary: GLM 5.3 Flash promo **$5.36/1k** to 2026-09-09. DeepSeek as-observed
**$13.67/1k**.

**Cheapest top-band: GLM 5.3 Flash, $10.71/1k** — cheaper than *both ends* of
Qwen's range, so the conclusion does not depend on the region question.

**Cost multiples for Fable (list):**

| vs | multiple | +$/1k | +$/100k | +$/1M |
|---|---:|---:|---:|---:|
| GLM 5.3 Flash | **42.6×** | +445.56 | +44,556 | +445,555 |
| Qwen 3.8 Flash | **29.3–36.2×** | +440.71 to +443.65 | +44,071 to +44,365 | +440,705 to +443,653 |

**Pareto frontier, conservative end of every range:** **GLM 5.3 Flash** and
**Qwen 3.8 Flash**. Dominated: DeepSeek V4 Flash, GLM 5.2, Claude Fable 5.1\*.
**Invariant** — the frontier is identical at the optimistic end of every range.

## 9. Top band — unchanged

**No quality data error found.** The band stands as
**TOP PERFORMANCE BAND / UNORDERED**: Qwen 3.8 Flash 95.07, GLM 5.3 Flash 94.93,
Claude Fable 5.1\* 94.90 — gaps of 0.03–0.17 points against a minimum run σ of
1.53, and the Fable audit's 94.07–96.30 envelope straddles all three.

## 10. Result statement — does the data still support it?

> "MondayBench cannot resolve a meaningful quality difference between Qwen 3.8
> Flash, GLM 5.3 Flash and Claude Fable 5.1. Their costs, however, are
> dramatically different."

**SUPPORTED, and more strongly than before.** Quality gaps 0.03–0.17 against a
1.53 noise floor; cost now spans **$10.71 to $456.27 per 1,000 tasks** on
first-party list prices — a 42.6× spread. Moving Qwen to a range does not soften
it: even Qwen's cheapest end ($12.61) is 36× below Fable.

> "Fable 5.1 buys substantially lower latency and fewer generated tokens, but no
> measured quality advantage on MondayBench."

**SUPPORTED.** Median TTFA 50.9 s against 258.9 s and 278.2 s — **5.1–5.5×
faster**. Mean output 8,198 tokens against 20,072 and 31,687 — **2.4–3.9× fewer**,
with 4.1–6.3× fewer reasoning tokens. And it is the *lowest*-scoring of the three
by an amount that is itself noise, so no quality advantage is measured. Nothing
in the gate changed either figure — latency and token counts do not depend on
pricing.

---

## Publication recommendation

# PRICING DATA READY FOR PUBLICATION

With the mandatory caveats in §12 below.

**1. Which prices are HIGH / exact?**
**Claude Fable 5.1** (HIGH, identity **EXACT** — all five rates from Anthropic's
own page, and reported = normalized at 0.00% on 15 runs), **GLM 5.3 Flash**
(HIGH, STRONG_MATCH), **GLM 5.2** (HIGH, STRONG_MATCH), **DeepSeek V4 Flash**
(HIGH, STRONG_MATCH — but published as a range because the price is
time-of-day dependent).

**2. Which remain MEDIUM?**
**Qwen 3.8 Flash** only — downgraded from HIGH at this gate. The rates are
first-party but regional, and the serving region is not determinable.

**3. Which remain UNKNOWN?** **MIMO v2.5, Qwen 3.6, Gemma 4.** All three kept as
UNKNOWN and none dropped from the tables.

**4. Did any figure change?** **No price value changed. Two presentations did:**
Qwen 3.8 Flash from a point ($15.56) to a range ($12.61–$15.56), and DeepSeek V4
Flash from a point ($13.67) to a range ($12.94–$25.88). Two confidences rose
(GLM 5.2, DeepSeek) and one fell (Qwen 3.8 Flash). Full OLD/NEW in §7.

**5. Cheapest top-band on LIST price?** **GLM 5.3 Flash, $10.71/1,000 tasks** —
cheaper than both ends of Qwen's range, so this does not rest on the region
question. (Promo $5.36 to 2026-09-09; not used for the headline.)

**6. Fastest top-band?** **Claude Fable 5.1\***, median TTFA **50.9 s**.

**7. How much more expensive is Fable than Qwen?** **29.3× to 36.2×**, depending
on Qwen's region.

**8. How much more expensive is Fable than GLM 5.3 Flash?** **42.6×**.

**9. What difference per 1k / 100k / 1M tasks?**
vs GLM 5.3 Flash **+$445.56 / +$44,556 / +$445,555**.
vs Qwen 3.8 Flash **+$440.71–443.65 / +$44,071–44,365 / +$440,705–443,653**.

**10. Pareto frontier?** **GLM 5.3 Flash and Qwen 3.8 Flash**, invariant across
both ends of every range. Dominated: DeepSeek V4 Flash, GLM 5.2, Claude Fable
5.1\*.

**11. Which conclusions are robust to publish?**

* The top band is unordered — Qwen 3.8 Flash, GLM 5.3 Flash, Claude Fable 5.1\*.
* GLM 5.3 Flash is the cheapest top-band model on list price.
* Fable 5.1 costs 29–43× the other two band members with no measured quality
  advantage: `NO MEASURED QUALITY ADVANTAGE FOR THE ADDITIONAL COST`.
* Fable 5.1 is 5.1–5.5× faster to first answer and 2.4–3.9× more concise.
* The Pareto frontier is GLM 5.3 Flash and Qwen 3.8 Flash.
* In the whole priced set, exactly one pair exists where paying more buys
  resolved quality (Fable over GLM 5.2).
* Monday Score still means quality only; no composite score exists.

**12. Caveats that must appear on the web:**

1. **Fable 5.1 is provisional and OFF-BENCHMARK / CLAUDE CODE ROUTE**, excluded
   from the official ranking. Score 94.90, never 95.97.
2. **The top three are an unordered band.** Do not render them as ranks 1-2-3.
3. **Cost is normalized list price, not what MondayBench paid.** For DeepSeek and
   GLM 5.2 the gateway charged ~50% of list.
4. **Qwen 3.8 Flash and DeepSeek V4 Flash are ranges, not points** — regional and
   time-of-day pricing respectively. Render as ranges.
5. **GLM 5.3 Flash's headline uses list price**; a 50% promotion ran to
   2026-09-09 and must be labelled as promotional if shown.
6. **MIMO v2.5, Qwen 3.6 and Gemma 4 have UNKNOWN pricing** and must be shown as
   UNKNOWN, not omitted and not zero.
7. **"MondayBench-equivalent task"** — 11–24 KB prompts, 0.9k–33k token answers.
   Not a universal per-request cost. Scale figures are linear extrapolations.
8. **Scenario workloads differ by 6–8× in cost**; the per-task figure is an
   equal-weight average over five different jobs.
9. **Latency and token counts are not folded into any score**, and no Value Score
   exists.
10. **Pricing snapshot** `pricing-2026-09-02`, sha256 `ec4dcc85…f389598`. Prices
    change; the snapshot id should be shown wherever the figures are.

---

**Artefacts.** Frozen: `pricing-snapshot-2026-09-02.yaml` +
`.sha256`. Publication-ready: `publication-data.json`. Regenerated:
`cost-summary.json`, `quality-vs-cost.json`, `pareto.json`,
`verified-list-costs.json`. Unchanged (pricing-independent):
`quality-vs-latency.json`, `usage-coverage.json`, `normalized-costs.jsonl`,
`billing-semantics.md`, `validation-reported-vs-normalized.json`,
`incremental-cost.json`. Superseded copies preserved:
`REPORT.PRE-GATE.md`, `cost-summary.PRE-GATE.json`, `pareto.PRE-GATE.json`,
`quality-vs-cost.PRE-GATE.json`.

Nothing was integrated into the web. Monday Score, verdicts, runs, the official
leaderboard and every frozen artefact are untouched.
