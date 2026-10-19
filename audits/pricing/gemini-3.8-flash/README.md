# Gemini 3.8 Flash (High) — estimated minimum pricing

**At least $0.0121 per MondayBench-equivalent task, $12.06 per 1,000**, at the
Gemini API standard rates in force today ($0.75 input / $3.75 output per 1M
tokens through 2026-12-31). At the rates from 2027-01-01 ($1.50 / $7.50) the
same tokens cost **$24.11 per 1,000**. Both rates were verified on Google's own
pricing page on 2026-10-16. Basis `ESTIMATED_LIST_LOWER_BOUND`, pricing
confidence `LOW`, identity `STRONG_MATCH`.

This is a **lower bound**. The 15 official runs went through the Antigravity
Language Server, which reports no token usage of any kind. Only the text could
be counted, and the model's thinking cannot be seen. Google bills thinking as
output ("Output price (including thinking tokens)"), and these runs used
thinking budget High. Written for the site's quality-vs-cost chart at the
owner's request; nothing under `analysis/cost-value/` or the leaderboard
changes.

## Method

| Bucket | Source | Mean per task |
|---|---|---|
| Input | `o200k_base` count of the frozen scenario prompt (no system prompt is sent on this route), rebuilt and hash-checked against every run | 4,526.6 |
| Output | `o200k_base` count of the visible response | 2,310.0 |
| Thinking | **not recorded**, `reasoning_tokens: null` | — |

- **Proxy tokenizer.** Google publishes no offline Gemini tokenizer, so this
  uses the same `o200k_base` count as the GPT-6 Astra estimate. Real Gemini
  counts will differ, and the direction of the error is not known.
- **Uncounted input.** Any instructions Google adds on its side are not
  visible, so they are not counted. That also pushes the estimate down.
- **No caching** is assumed. **TTFA is null**: the route returns one
  non-streaming response.
- **Cost of the missing thinking:** every 1,000 thinking tokens per task adds
  $3.75 per 1,000 tasks ($7.50 after 2026). The number of thinking tokens per
  task is not known.

## Per scenario

| Scenario | Cost / 1k | Post-intro / 1k | Input | Visible output |
|---|---|---|---|---|
| monday-001 | $5.72 | $11.44 | 2,709 | 984 |
| monday-002 | $9.34 | $18.68 | 2,247 | 2,041 |
| monday-003 | $8.27 | $16.54 | 3,212 | 1,563 |
| monday-004 | $23.80 | $47.60 | 9,708 | 4,406 |
| monday-005 | $13.15 | $26.31 | 4,757 | 2,556 |

## Note for the site

The sync computes `mean_reasoning_tokens` as `r.reasoning_tokens ?? 0`, so this
row will read 0 reasoning tokens where the truth is "not recorded".

## Reproduce

```
pip install tiktoken          # not a project dependency
python audits/pricing/gemini-3.8-flash/calculate.py
```

The script recomputes `summary.json`, `run-costs.csv` and `scenario-costs.csv`
from the run artefacts and `pricing-source.json`. It produces the same bytes
on every run, and it stops if any run turns out to be metered, carries a system
prompt, or fails its prompt or response hash.
