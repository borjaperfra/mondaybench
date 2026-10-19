# Discarded: NaN cache hits under an ignored `caching: false` (2026-10-19)

First attempt at the `deepseek-v4.1-flash-1017` and `mimo-v2.6-flash` batteries,
generated 2026-10-19 from 09:20 UTC on NaN without a per-run seed.

NaN no longer honours `extra_body: {caching: false}` for these models. In every
scenario, run-002 and run-003 came back in under ~2 seconds, byte-identical in
`response` to run-001. Reproduced on a small prompt the same morning: three
identical requests returned the same response, with or without
`Cache-Control: no-cache`; a different `seed` in the body returned a fresh
generation each time.

The run-001 files are genuine generations, but they were made without a seed
and the replacement batteries are seeded (`generation.seed_per_run: true` in
models.yaml), so they are archived with their duplicates rather than mixed into
a seeded battery. The generation was also cut short (Claude Code stopped the
background job on low system memory) before mimo-v2.6-flash finished
monday-005. `failed-attempts.jsonl` holds MiMo's attempts that spent the
32,000-token ceiling on reasoning and returned no answer (monday-002 ×1,
monday-004 ×3).

Kept as evidence, and so that `archived_run_numbers` reserves these numbers:
the seeded batteries continue after the highest archived run number
(run-004 where run-001..003 are archived here).
