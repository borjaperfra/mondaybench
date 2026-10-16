# GPT-6 Astra — estimated pricing

**Estimated $0.1368 per MondayBench-equivalent task, $136.83 per 1,000**, at
OpenAI's standard list rates ($10 input / $50 output per 1M tokens, verified on
OpenAI's own pricing page on 2026-10-16). Basis `ESTIMATED_LIST`, pricing
confidence `MEDIUM`, identity `STRONG_MATCH`. Reasoning tokens are **included**.

This is an estimate, not a meter reading: the 15 official runs went through
the Codex CLI, not an API route, so `usage.*` is null on every run and no bill
exists. It is written for the site's quality-vs-cost chart, at the owner's
request, and changes nothing under `analysis/cost-value/` or the leaderboard.

## Method

| Bucket | Source | Mean per task |
|---|---|---|
| Input | `o200k_base` count of system prompt + frozen scenario prompt, rebuilt with `mondaybench.prompt_builder` and hash-checked against every run | 4,532.6 |
| Output | The Codex session's own `output_tokens` counter (`provider_metadata.raw_usage.codex_runtime.codex_usage`) | 1,830.1 |
| of which reasoning | Codex `reasoning_output_tokens`, a subset of output, billed once | 359.5 |

- **Why these counters can be trusted this far.** An independent `o200k_base`
  count of each visible response equals Codex's `output_tokens -
  reasoning_output_tokens` to within 4–6 tokens on all 15 runs. So the
  tokenizer is right for this model, and reasoning is inside output, not on top
  of it.
- **Codex's own context is left out.** Codex adds a fixed block of harness
  instructions to every input (5,193 tokens per run by the counters). A
  MondayBench API call would not send it, so the headline does not price it.
- **No caching** is assumed. No input is over the 272K long-context threshold
  (the largest is 9,714), so the long-context rates never apply.
- **TTFA is null.** The route does not expose it.

## Sensitivity (summary.json `sensitivity`)

| Variant | Cost / 1k tasks |
|---|---|
| Headline: API-equivalent input, output with reasoning | **$136.83** |
| As metered by Codex (its harness context in, its cache hits at $1) | $186.00 |
| Visible answer only, reasoning left out | $118.57 |

## Per scenario

| Scenario | Cost / 1k | Input | Output (reasoning) |
|---|---|---|---|
| monday-001 | $61.60 | 2,715 | 689 (23) |
| monday-002 | $82.48 | 2,253 | 1,199 (76) |
| monday-003 | $96.01 | 3,218 | 1,277 (232) |
| monday-004 | $302.09 | 9,714 | 4,099 (1,159) |
| monday-005 | $141.98 | 4,763 | 1,887 (307) |

## Caveats

The counters are what Codex reports, not provider accounting; the served
model id is not observable; the run used Codex reasoning effort `medium`.
`analysis/cost-value/publication-data.json` still lists Astra under
`unknown_pricing_remaining` with "NO_TOKEN_COUNTS". That file is frozen and
was not edited. Its statement was true of `usage.*`, but the Codex counters
used here were on every run all along.

## Reproduce

```
pip install tiktoken          # not a project dependency
python audits/pricing/gpt-6-astra/calculate.py
```

The script recomputes `summary.json`, `run-costs.csv` and `scenario-costs.csv`
from the run artefacts and `pricing-source.json`. It produces the same bytes
on every run, and it stops if any run turns out to be metered or to fail its
prompt hash.
