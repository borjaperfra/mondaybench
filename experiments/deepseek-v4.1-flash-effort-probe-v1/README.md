# deepseek-v4.1-flash-effort-probe-v1

A controlled probe of a request parameter. **Not a MondayBench run**, not a
battery, not a leaderboard entry, and not scored by any judge.

## The question

Does `reasoning_effort` observably control inference effort or answer quality
for DeepSeek V4.1 Flash on the Helmcode route, or is the parameter accepted
while its effect stays indistinguishable from the model's natural variance?

## What came before this

A small sweep (19 calls, non-streaming, `tools/probe_reasoning_effort.py`)
established three things and settled none of them:

- `baseline`, `low`, `medium`, `high` and `max` all return HTTP 200 and come
  back with `reasoning_tokens`.
- The variance is enormous and there was no monotone baseline -> high -> max
  ladder. At `high`, two consecutive samples reported 13,997 and 354 reasoning
  tokens.
- `reasoning_effort="banana"` **also** returns HTTP 200, with no
  `reasoning_tokens` field at all, ~6 output tokens, sub-second latency and a
  wrong answer.

So **HTTP 200 is not evidence that `reasoning_effort` was applied.** That is why
this experiment has a sentinel and why it measures distributions rather than
sampling each level once.

## Design

| | |
| --- | --- |
| phase 1 | 30 samples `baseline` (field absent) vs 30 samples `reasoning_effort="high"` |
| assignment | randomised, balanced, **interleaved**, frozen in `probe-config.json` before the first call (seed 20260911) |
| prompt | one frozen prompt for every sample, `frozen-prompt.txt`, sha256 `672c55f3...ada7` |
| scoring | deterministic parser, no LLM judge (`scorer.py`) |
| independence | one request per sample, no conversation state, no best-of-N, no quality retries |
| retries | infrastructure failures only, every attempt recorded |
| `max` | **not executed.** Phase 2 needs explicit authorisation. |

The order was frozen before the first call and not touched afterwards.
Interleaving is the reason: 30 baseline calls followed by 30 high calls would
confound the variable with whatever the backend was doing at the time.

### The prompt

Recovered byte-exact from the earlier probe by **importing** its `PROMPT`
constant, not by retyping it, and cross-checked against the prompt recorded in
that probe's raw output. 223 bytes, no trailing newline.

The exercise has one objectively correct answer, which is what makes a success
rate computable without a judge: A (2h) from 09:00, then B (3h, waits for A),
then C (1h, cannot overlap B) — six hours of work, so **15:00**.

### The single variable

Everything that reaches the wire comes from `models.yaml`'s
`deepseek-v4.1-flash` entry, through the harness's own `ModelConfig` and its own
`OpenAICompatibleProvider`. `preflight.json` is the machine-checked proof,
written **before** the first call: it compares every field and passes only if
`reasoning_effort` is the sole difference.

Two departures from a benchmark run are declared in the preflight, and both are
held **identical across variants**, so neither can explain a baseline/high
difference:

1. **No system prompt.** The earlier probe sent none; this continues that
   comparison. A benchmark run would send "You are a helpful assistant."
2. **Streaming on.** The earlier probe was blocking, which is exactly why it
   could not observe reasoning stream events. Streaming is what makes
   `reasoning_stream_observed` measurable. Consequence: token counts here are
   not directly comparable with the earlier blocking probe's numbers.

## Distinctions this experiment refuses to blur

- `reasoning_tokens = 0` (the provider counted none) and
  `reasoning_tokens = null` (the provider did not report the field) are recorded
  as different values and never averaged together.
- `reasoning_stream_observed = false` means **reasoning delivery was not
  observed**. It is not evidence that the model did not reason — the project
  learned that from MIMO v2.5, which streams a thinking phase and then reports
  zero tokens.
- API acceptance, observed reasoning delivery, reported reasoning compute,
  latency and task quality are five separate questions and are answered
  separately.

## Statistics

Medians and quantiles, not means alone: the distribution is heavily skewed and a
mean summarises nothing. Percentile bootstrap (10,000 resamples, seed 424242)
for the difference in median reasoning tokens, median latency and success rate.
Cliff's delta with its own bootstrap CI as a rank statistic that extreme values
cannot move. Two-sided permutation tests with the same seed. **No outliers are
removed from any headline number**; a trimmed view exists only as a labelled
sensitivity check answering "is this shift one or two extreme values?".

## Decision gate (fixed before the data existed)

`high` is interesting enough to keep investigating if either holds:

- **A, quality**: success rate improves by >= 10 percentage points.
- **B, compute**: `median(high) > median(baseline)` **and**
  `p25(high) > p25(baseline)` **and** the shift survives the tail sensitivity
  check **and** Cliff's delta's 95% CI excludes zero.

If neither holds: stop, and the provisional conclusion is *"no observable
high-effort effect large enough to justify a MondayBench battery"*.

Either way the run stops after phase 1. `max` is not executed without explicit
authorisation, and `analyze.py` never executes it under any outcome.

## Sentinel

After the 60 valid calls, 5 calls with `reasoning_effort="banana"`, kept in a
separate file and excluded from every statistic. It is an infrastructure check:
does an unrecognised value still come back as 200 without observable reasoning?

It describes **observable behaviour only**. Nothing here establishes how the
provider routes a request internally, and the report does not claim to.

## Isolation

Nothing outside this directory is read for data or written to. No `runs/`, no
`evaluations/`, no `verdicts/`, no `leaderboards/`, no `releases/`, no existing
DeepSeek battery, and not the reliability experiment. Nothing is published,
nothing is added to a board, and nothing is committed.

## Files

| path | what it is |
| --- | --- |
| `README.md` | this file |
| `frozen-prompt.txt` | the exact bytes sent as the user message, every sample |
| `prompt.sha256` | its sha256 |
| `preflight.json` | the pre-call control check |
| `probe-config.json` | frozen assignment order, seeds, request config |
| `scorer.py` | the deterministic scorer, with self-tests |
| `run_probe.py` | preflight / execute / sentinel |
| `analyze.py` | statistics, distributions, decision gate |
| `raw/samples.jsonl` | one record per phase-1 sample, full detail |
| `raw/sentinel-banana.jsonl` | the 5 sentinel calls |
| `analysis/observations.csv` | the 60 individual observations |
| `analysis/summary.json` | every computed number |
| `analysis/report.md` | the readable report |
| `manifest.json` | file inventory with hashes |

### On "raw response"

`raw/samples.jsonl` keeps the complete final answer text, its sha256, the
provider's whole `usage` block, the request id, finish reason and all timings.
It does **not** keep the per-event SSE payloads: the harness adapter consumes
the stream to produce those fields, and reasoning *content* is deliberately
never stored anywhere in this project (`mondaybench/reasoning.py`). Reasoning is
recorded structurally — event counts and token counts.
