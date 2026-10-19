# NaN challengers 2026-10-19 — blind judge, criterion by criterion

**Off-board. Nothing here is published until a suite release (v1.13) takes it.**

Two models on NaN, generated and judged on 2026-10-19:

- `deepseek-v4.1-flash-1017` — NaN's `deepseek-v4-flash` id, which NaN's
  operator says now serves DeepSeek V4-Flash 4.1-1017. Stated, not observed:
  the endpoint names no version.
- `mimo-v2.6-flash` — MiMo v2.6 Flash. NaN no longer serves `mimo-v2.5`.

## Result

| Model | #001 | #002 | #003 | #004 | #005 | Monday Score |
|---|---:|---:|---:|---:|---:|---:|
| DeepSeek V4.1 Flash (1017) | 90.33 | 95.17 | 95.83 | 79.67 | 95.17 | **91.23** |
| MiMo v2.6 Flash | 82.67 | 83.67 | 93.17 | 80.33 | 99.50 | **87.87** |

Per-run scores, dimensions and penalties: `scores/<slug>.json`. Labels keyed by
run id: `verdicts/<slug>.jsonl`.

## How it was generated

- Same frozen prompts, temperature 0, 32,000-token ceiling as every board row.
- **Seeded.** NaN ignores `extra_body: {caching: false}` for both ids: identical
  bodies returned the stored response (run-002/003 byte-identical to run-001,
  under 2 s). Each run therefore sends `seed: <run_number>`
  (`generation.seed_per_run: true` in models.yaml), which busts the cache
  without touching the prompt. No board row was generated with a seed. The
  unseeded first attempt is in `archive/nan-unseeded-2026-10-19/`.
- **MiMo exhausts the ceiling on thinking.** monday-004: 6 of 6 morning attempts
  (09:51 and 12:06 UTC) spent 32,000 tokens reasoning and returned no answer;
  from 13:25 UTC, 3 of 3 answered. monday-002: 2 of 5 attempts failed the same
  way. Failures are in each scenario's `failed-attempts.jsonl`; the ceiling was
  not raised (decision, 2026-10-19). NaN treats the cap as advisory - two
  qualifying monday-004 runs report 33,500 and 40,053 output tokens with
  `finish_reason=stop`.
- Both batteries are on NaN, not Helmcode: latency, TTFA and token counts are
  properties of NaN.

## Who judged, and how blind

Claude Opus 5.5, in-session, one subagent per scenario per model (ten in all),
from `JUDGING.md`: the operative rules and the scenario's sections A–D of
`audits/blind-rejudge/opus-5-blind-rejudge.md`, plus one pack. One pack per
model under an opaque key (first 8 hex of sha256(slug)); the judges were
forbidden the provenance maps, runs, archive, models.yaml and every existing
verdict or score. **Not** the Claude Opus 5 that `evaluator-opus5-v0.x` pins and
that labelled most of the board — the same caveat as Gemini 3.8 Flash (High).

## Reproduce

```bash
uv run python experiments/nan-challengers-2026-10-19-opus-judge/build-pack.py <slug>
uv run python experiments/nan-challengers-2026-10-19-opus-judge/join-and-score.py <slug>
```
