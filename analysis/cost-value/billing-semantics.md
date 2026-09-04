# Billing semantics per provider

Every statement below was **established from the stored run data**, not assumed
from field names. The tests and their results are reproduced so they can be
re-run.

The headline finding: **`input_tokens` does not mean the same thing on the two
routes.** Applying one formula to both would misprice by three orders of
magnitude on the cached portion.

---

## 1. Tests run over all 120 official runs + 15 Fable runs

| Test | Result |
|---|---|
| `usage.input_tokens == provider_metadata.raw_usage.prompt_tokens` | **120/120** on the OpenAI-compatible routes |
| `cached_tokens > input_tokens` (would prove cache is a separate bucket) | **0/120** — cache is a *subset* of input |
| `reasoning_tokens > output_tokens` (would prove reasoning is billed separately) | **0/120** — reasoning is *inside* output |
| Fable: `input_tokens` vs cache buckets | `in=2, cache_write=4832` and `in=2, cache_read=3804` — input is **exclusive** of cache |

That last row is the important one. On a ~4,800-token prompt Fable reports
`input_tokens: 2`. The prompt is not 2 tokens; the other 4,830 are in
`cache_creation_input_tokens`. On the gateways, the same prompt would report
`input_tokens: 4832` with `cached_tokens` as a subset of it.

---

## 2. OpenAI-compatible routes — Helmcode and NaN

Models: `qwen3.8-flash`, `glm5.3-flash`, `glm5.2`, `deepseek-v4-flash`,
`mimo-v2.5`, `qwen3.6`, `gemma4`.

* **`input_tokens` is INCLUSIVE of cached input.** `prompt_tokens` is the whole
  prompt; `prompt_tokens_details.cached_tokens` is the part of it that hit cache.
  Uncached input must be derived by subtraction.
* **`output_tokens` is INCLUSIVE of reasoning tokens.**
  `completion_tokens_details.reasoning_tokens` is a subset. Never add the two.
* **Cache writes are mostly unobservable.** `cache_write_tokens` is present for
  `deepseek-v4-flash` (17/17), `glm5.2` (16/16), `glm5.3-flash` (16/16) and only
  **3 of 22** `qwen3.8-flash` runs; absent entirely for `mimo-v2.5`, `qwen3.6`,
  `gemma4`. Where absent it is treated as zero and the run is flagged
  `cache_write_unobservable` rather than estimated.
* **`gemma4` reports no cache field at all** (0/16), consistent with a
  non-caching deployment.

### Billing formula — OpenAI-compatible

```
uncached_input = input_tokens - (cached_tokens or 0)
cache_read     = cached_tokens or 0
cache_write    = cache_write_tokens or 0          # 0 when unobservable
billable_output = output_tokens                    # already includes reasoning

cost = uncached_input  / 1e6 * price.input
     + cache_read      / 1e6 * price.cache_read
     + cache_write     / 1e6 * price.cache_write
     + billable_output / 1e6 * price.output
```

**Reasoning token classification: (A) included inside billable
`output_tokens`.** No separate line. Confirmed two ways — arithmetically
(`reasoning ≤ output` in all 120 runs) and from pricing (none of the four
verified price lists publishes a reasoning-token rate).

---

## 3. Anthropic first-party — Claude Fable 5.1 via `claude -p`

* **`input_tokens` is EXCLUSIVE of cache.** The three prompt buckets —
  `input_tokens`, `cache_read_input_tokens`, `cache_creation_input_tokens` — are
  disjoint and sum to the whole prompt. **Do not subtract.**
* **`output_tokens` is INCLUSIVE of `thinking_tokens`**, verified the same way.
* Cache write is billed at a premium ($12.50/MTok, 1.25× input) and cache read
  at a deep discount ($0.25/MTok, 0.025× input).
* First run of each battery *writes* the cache; later runs *read* it. Within one
  scenario the per-run costs are therefore not directly comparable, which is why
  the report uses the scenario **mean across three runs**.

### Billing formula — Anthropic first-party

```
uncached_input = input_tokens                      # already excludes cache
cache_read     = cache_read_input_tokens
cache_write    = cache_creation_input_tokens
billable_output = output_tokens                    # already includes thinking

cost = uncached_input  / 1e6 * 10.00
     + cache_read      / 1e6 * 0.25
     + cache_write     / 1e6 * 12.50
     + billable_output / 1e6 * 50.00
```

**Reasoning token classification: (A) included inside billable
`output_tokens`.** Anthropic bills thinking tokens as output; the `claude-api`
reference states thinking "happens and is billed the same under every
setting". No separate line.

---

## 4. DeepSeek V4 Flash — the one time-of-day case

DeepSeek is the only model here whose list price varies by hour: peak
(01:00–04:00 and 06:00–10:00 UTC) is exactly double off-peak. The calculator
resolves the band from each run's `timestamp_utc` and records
`pricing_band: peak|off_peak` on every DeepSeek row.

This makes DeepSeek's normalized cost a function of *when the benchmark
happened*, which no other model's is. Treated as a stated caveat, not smoothed
into an average.

---

## 5. Reasoning-token classification summary

| Model | Classification | Basis |
|---|---|---|
| claude-fable-5-1 | **A** — inside billable output | `thinking ≤ output` in 15/15; Anthropic bills thinking as output |
| qwen3.8-flash | **A** — inside billable output | `reasoning ≤ output` in 22/22; no reasoning rate published |
| glm5.3-flash | **A** | `reasoning ≤ output` in 16/16; no reasoning rate published |
| glm5.2 | **A** | `reasoning ≤ output` in 16/16; no reasoning rate published |
| deepseek-v4-flash | **A** | `reasoning ≤ output` in 17/17; no reasoning rate published |
| mimo-v2.5 | **D** — not observable | `reasoning_tokens` is 0 in all 17 runs while the model demonstrably streams a thinking phase (see `mondaybench/reasoning.py`) |
| qwen3.6 | **A** where reported | non-zero in 3 runs only (the NaN-served monday-004 battery) |
| gemma4 | **C** — none produced | `reasoning_tokens` 0 in all 16 runs; non-reasoning model |

**No double-counting anywhere.** `output_tokens + reasoning_tokens` is never
computed for any model.

---

## 6. What this makes comparable, and what it does not

**Comparable:** normalized cost across the five priced models, because the token
counts are complete for them and each formula matches its route's semantics.

**Not comparable:**

* **Reported vs normalized cost.** Reported cost exists for only 3 of 8 models
  (`deepseek-v4-flash`, `glm5.2`, `claude-fable-5-1`) and reflects gateway
  deals, plans and quotas. It is used for validation only.
* **Cache behaviour across routes.** Fable's battery writes then reads a cache;
  the gateway models show mostly cache misses on a fresh prompt per scenario.
  A cache-heavy route looks cheaper per run on repeats, which is real but is an
  artefact of how the batteries were generated, not a property of the model.
* **`mimo-v2.5`, `qwen3.6`, `gemma4`.** No usable list price; excluded from
  normalized cost entirely.
