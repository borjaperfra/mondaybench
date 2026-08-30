# mimo-v2.5 — every attempt is INVALIDATED (truncated)

`qualify_run` rejects both on **finish_reason=length: output was truncated by
the token budget**. The files are kept, not deleted: a budget defect that gets
deleted cannot be counted later. Neither contributes to any published statistic,
and MIMO v2.5 therefore has **no qualifying run for monday-004**.

| | run-001 | run-002 |
|---|---:|---:|
| output tokens | **32,000** | **32,000** |
| reasoning tokens reported | 0 | 0 |
| answer characters | 9,182 | 16,655 |
| finish_reason | **length** | **length** |
| qualifies | no | no |

Three generation attempts were made in total and only two files exist. Two
retries were launched concurrently, both computed `run-002` as the next free run
number, and the later one overwrote the earlier at 11:51:06. Both were truncated
at 32,000, so the conclusion is unaffected, but one attempt's bytes are gone and
that is recorded here rather than left to be inferred from a timestamp. The
run-002 on disk is the later generation. Concurrent retries against one model
are the cause; they should be run one at a time.

## What actually ran out

run-001's answer is 9,182 characters — roughly 2,300 tokens — and stops
mid-sentence inside the per-customer economics table of section 4b. run-002 got
further, to 16,655 characters, and still stopped short of the recommendations.
In neither case is the rest of the 32,000 in the answer, and neither reports any
reasoning tokens. `models.yaml` already records that this provider's reasoning
accounting is unreliable for this model:

> Corrected 2026-08-28. This was `false`, and the provider reports [...] the
> provider just does not count it.

So the most likely reading is that MIMO reasons inside the same envelope, is not
billed for it as reasoning, and hits the ceiling before finishing. That is a
budget problem rather than a quality problem: the truncated text is a strong
analysis. run-001 finds the duplicated invoice, builds a correct MRR bridge to
EUR 732,400, resolves Wayne Enterprises through the alias, spots that the
churned SMB accounts all declined 34–37% before leaving, and states plainly that
CAC payback cannot be computed.

## Why the budget was not simply raised

`max_output_tokens: 32000` is set per model in `models.yaml` and is shared with
monday-001, monday-002 and monday-003. Raising it would make every official run
of all three frozen scenarios fail `qualify_run` on
`max_output_tokens != configured`, because those runs were generated at 32,000.
The published batteries would stop verifying.

The budget therefore cannot be raised for monday-004 alone with the harness as
it stands. `analysis/monday-004-calibration.md` records this as one of the three
blocking findings, together with the related and worse one: qwen3.8-flash was
served **58,956** output tokens against the same configured 32,000 ceiling, so
the battery was not run under one budget at all.
