# GLM 5.3 — the pricing-identity gate, and the decision that resolved it

> **Status: the block in this document was lifted on 2026-09-03 by a product
> decision, not by new evidence.** Sections 1–9 are preserved verbatim as
> provenance: they are the record of the original
> **$0.075 / $0.25 "first-party Z.AI"** assumption being examined and
> **rejected**. Nothing below them was rewritten to match the outcome. What
> changed is section 10: the two bases are now *both* published, each labelled,
> instead of one being chosen. The pricing identity is still **CONTESTED** and is
> published as such. See `audits/glm-5.3/cost-efficiency-publication.md`.

**Date:** 2026-09-03 · **Inferences run: zero.** No score, verdict, run,
evaluation, leaderboard or frozen artefact touched. No Value Score. No
Efficiency Score. *(At the time of writing, the website was unchanged; section 10
records what was later published and when.)*

**Snapshot added:** `pricing-snapshot-2026-09-03.yaml`
sha256 `9b1db0cb61b8b50e84221cc6d2ef4baad819fedaff73bac2ca2de24c2d92d81c`

**Previous snapshot preserved:** `pricing-snapshot-2026-09-02.yaml` still hashes
to `ec4dcc85…`, byte-identical to its recorded `.sha256`. No price in it moved.

---

## The finding, in one paragraph

GLM 5.3 was to be published at **$5.67 / 1k MondayBench-equivalent tasks** on a
**FIRST_PARTY / Z.AI** basis, from rates of $0.075 input / $0.25 output. Z.AI's
own pricing page lists **GLM-5.3 at $1.4 / $4.4**. The $0.075 / $0.25 figures
are not Z.AI's list price for this model — they are what the **Helmcode gateway
metered**, and they are *exactly* **GLM-5.3-Flash's promotional price**. On the
basis every other Z.AI row in the published table uses, GLM 5.3 costs
**$99.20 / 1k**, not $5.67. The two numbers differ by 17.5×, they cannot both be
right, and no client-side evidence settles which applies. **Nothing was
published.**

---

## 1. The method was validated before it was trusted

A normalized cost is a counterfactual: what this workload would have cost at the
vendor's list price. The reconstruction was therefore pointed at two models
whose $/1k is already published and gated, and required to reproduce them:

| Control | Published | Reconstructed | Δ |
|---|---:|---:|---:|
| GLM 5.2 | $39.50/1k | **$39.50/1k** | 0.00 |
| GLM 5.3 Flash | $10.71/1k | **$10.71/1k** | 0.00 |

Both exact. The first pass was *wrong* and the controls caught it: cache tokens
are not in `usage`, they are in
`provider_metadata.raw_usage.prompt_tokens_details.cached_tokens`. Reading only
`usage` charges every cached prompt token at full rate and overstated GLM 5.2 by
6.8%. Without the controls that error would have gone into a published number.

## 2. GLM 5.3 usage, from the run artifacts

15 official v1.1 runs, model id `glm5.3` on all 15, `finish_reason=stop` on all
15.

| | |
|---|---:|
| mean input tokens | 4,669.2 |
| mean output tokens | **21,298.6** |
| mean reasoning tokens | **19,288.1** |
| total cache-read tokens | 13,760 |
| total cache-write tokens | 0 |
| median TTFT | 2,108.4 ms = **2.108 s** |
| median TTFA | 253,260.4 ms = **253.26 s** |
| median total latency | 286,619.6 ms = **286.62 s** |

Matches the canonical figures. **Cache tokens do exist** on these runs — the
brief's "cache tokens if any" is answered yes, and they are billed at the cached
rate and removed from full-rate input.

## 3. Billing semantics

* **Reasoning is inside output.** `reasoning_tokens ≤ output_tokens` on all 15
  runs. Output is billed once; billing it once bills reasoning once.
  **Not double-counted.**
* **Reported cost exists here**, unusually: each scored run's `economics` block
  carries `input_cost_usd`, `output_cost_usd` and `total_cost_usd`. Solving them
  gives $0.075/M input (11 runs with no cached tokens) and $0.25/M output.
* **The `provider` field does not.** The scored runs are streaming, and the
  streaming response carries neither `provider` nor `cost` at the message level.
  Which upstream served each scored run is not determinable.
* Normalized cost is reconstructed from token usage × published price, never
  from a field absent from the scored runs.

## 4. Why the identity fails

| Model | Z.AI list | Gateway metered | Ratio |
|---|---|---|---:|
| GLM 5.2 | $1.4 / $4.4 | $0.70 / $2.20 | **exactly 50%** |
| GLM 5.3 Flash | $0.15 / $0.50 | *(via NaN, no cost reported)* | — |
| **GLM 5.3** | **$1.4 / $4.4** | **$0.075 / $0.25** | **5.4%** |

The 2026-09-02 gate already documented that Helmcode charges exactly 50% of Z.AI
list for GLM 5.2. GLM 5.3's metered rate is not 50% of GLM-5.3's list — it is
**exactly 50% of GLM-5.3-*Flash*'s list**, and exactly Flash's live promotional
price.

Two readings, and the client cannot choose between them:

1. the route is not GLM-5.3-as-listed; or
2. the gateway prices this route on a basis unrelated to Z.AI list.

`/model/info` and `/model_group/info` return 404, so the gateway cannot be
inspected. What is **not** in doubt: the served id echoes `glm5.3` on every
frame, never `glm5.3-flash`, and the model's behaviour differs measurably from
Flash's — different scores on four of five scenarios, a different output-token
profile. **This is a question about which price applies, not about which model
answered, and no benchmark score is affected.**

## 5. What each basis implies

| Basis | $/task | $/1k | $/100k | $/1M |
|---|---:|---:|---:|---:|
| FIRST_PARTY_LIST (Z.AI GLM-5.3) | 0.099205 | **99.20** | 9,920 | 99,205 |
| GATEWAY_METERED (the runs' own meter) | 0.005675 | **5.67** | 567 | 5,675 |
| *Parasail-rate counterfactual* | 0.011240 | *11.24* | *1,124* | *11,240* |

The Parasail line is what the observed Parasail rates would imply for the same
token usage. It is **not** merged with anything and is **not** offered as a
range: two pricing bases do not make a range, they make a category error.

## 6. Pareto, computed under each basis

`A` dominates `B` iff `A.score ≥ B.score` and `A.cost ≤ B.cost`, with at least
one strict. Range models are placed at their conservative (expensive) end, as
the 2026-09-02 gate specifies. Provisional models are excluded from the official
frontier.

**Official frontier before:** Qwen 3.8 Flash · GLM 5.3 Flash · MIMO v2.5 · Gemma 4

| Basis | Frontier after | GLM 5.3 on it? | Displaced |
|---|---|---|---|
| FIRST_PARTY_LIST | unchanged | **no** | none |
| GATEWAY_METERED | Qwen 3.8 Flash · GLM 5.3 Flash · **GLM 5.3** · MIMO v2.5 · Gemma 4 | **yes** | none |

**So the answer to "does GLM 5.3 become an important official Pareto point?" is:
it depends entirely on the basis, and the basis is exactly what is unresolved.**
On list it is dominated and adds nothing; on the meter it joins the frontier
between GLM 5.3 Flash and MIMO v2.5 without displacing anyone. Guessing would
have been a coin flip on the headline.

## 7. The two editorial claims — both fail

**"GLM 5.3 gives up ~1.2 points versus GLM 5.3 Flash while costing roughly half
as much."** Score delta is −1.20, correct. Cost:

* like-for-like (both first-party list): $99.20 vs $10.71 → GLM 5.3 costs
  **9.26× MORE**. The claim is not merely unsupported, it is **inverted**.
* mixed basis (GLM 5.3's meter vs Flash's list): 0.53×, "roughly half" — but
  that compares a discounted invoice against a public list price, which the
  gate forbids.

**"GLM 5.3 is one of the cheapest ways to get above 90 Monday Score."** On the
first-party basis the field above 90 is GLM 5.3 Flash $10.71, Qwen 3.8 Flash
$15.56, DeepSeek V4 Flash $25.88, GLM 5.3 $99.20. It would be the **most
expensive**, not one of the cheapest.

Neither is published. The 1.20-point score difference is not called significant
in any case: it sits inside the per-scenario run variance.

## 8. Gate

| Check | |
|---|---|
| GLM 5.3 usage reconstruction | **PASS** |
| method validated against published figures | **PASS** |
| billing semantics | **PASS** |
| reasoning double-count | **NONE** |
| pricing snapshot created | **PASS** |
| existing model cost invariance | **PASS** — no published figure moved |
| Pareto recomputation | **PASS** (computed under both bases) |
| **pricing identity** | **FAIL** |
| cost publication gate | **FAIL** |

Per the brief's own rule — if any gate fails, do not publish cost changes —
`publication-data.json` was not modified and the website Cost and Efficiency
tabs were not touched.

## 9. What would unblock it

Any one of these, in decreasing order of strength:

1. **A first-party price for the route.** If Helmcode publishes its own per-token
   price for `glm5.3`, that is a first-party price for the thing that actually
   ran, and the row becomes publishable at that basis with `identity: EXACT` —
   the same status Fable 5.1 has, and for the same reason.
2. **A gateway statement of the discount.** If Helmcode documents "50% of vendor
   list", the metered rate identifies the SKU and the contradiction resolves in
   favour of Flash-list, which would mean the route is not GLM-5.3-as-listed.
3. **Publish it on the metered basis in the provider view only**, beside MIMO,
   Qwen 3.6 and Gemma 4, which already sit on route prices — and leave the
   first-party view without a GLM 5.3 row. This is available today and is a
   product decision, not a data one, so it is not taken here.

Option 3 is the one to weigh: it is honest and already has precedent in this
table, but it puts a metered invoice in the same column as list prices, which is
what section 7 shows produces an inverted headline.

---

## 10. Resolution — 2026-09-03, by decision

Section 9 listed three ways out and noted that the third was **a product
decision, not a data one, so it is not taken here**. That decision was
subsequently taken, and it went further than option 3: rather than confining
GLM 5.3 to the provider view, **both bases are published, each labelled with the
basis that produced it, and never merged.**

| | First-party | Route |
|---|---|---|
| Basis | Z.AI list, `GLM-5.3`, $1.4 / $4.4 | Helmcode, `GATEWAY_METERED` |
| $/task | 0.099205 | 0.005675 |
| **$/1k** | **99.20** | **5.67** |
| $/100k | 9,920.50 | 567.49 |
| $/1M | 99,204.96 | 5,674.87 |
| Identity | `CONTESTED` | `OBSERVED_ROUTE` |

**Ratio 17.48×** (from unrounded per-task costs). Still not a range, for the reason section 5 gives.

### What this does and does not change

* **Section 4 stands.** The identity was never resolved. No evidence arrived;
  `/model/info` is still 404, the scored runs are still streaming and still
  carry no `provider`. `identity_confidence` publishes as **CONTESTED**, on the
  row and in the artifact.
* **Section 7 stands, and is honoured.** Neither editorial claim is published.
  The "roughly half the cost" line was the mixed-basis arithmetic this document
  rejected; like-for-like GLM 5.3 is **9.26× more expensive** than Flash, and
  that is what the published note reflects. The 1.20-point delta is still not
  called significant.
* **Section 6's dilemma is now the published result rather than a blocker.**
  Both frontiers ship: dominated on first-party, on the frontier on the route
  basis, displacing nobody on either. The dependency on basis is the finding,
  and the page shows it as two points at one score instead of resolving it by
  guess.
* **No commercial mechanism is asserted.** Section 4's two readings remain two
  readings. The brief for the publication task explicitly excluded inferring
  why the meter differs from list, and nothing here does.

### Why this is not a gate being talked past

The 2026-09-03 gate row `pricing identity` read **FAIL**, and a failing gate
blocked publication because a single figure would have had to claim a basis it
could not support. Publishing both figures removes that claim: neither is
presented as the other, and the contested one says so. The gate now reads
**CONTESTED, declared** — a different verdict on a different question, not the
same question re-answered.

**Quality is untouched by all of this.** Monday Score 93.73, OFFICIAL, no
provisional badge. The pricing question never reached it: which price applies is
not a question about which model answered.
