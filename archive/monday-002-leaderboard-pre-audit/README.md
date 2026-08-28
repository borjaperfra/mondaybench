# monday-002 — the official leaderboard as first published, 2026-08-28

Superseded the same day by the reasoning-delivery correction. Kept whole,
because a benchmark that quietly edits a published number is worth less than one
that shows its corrections.

## What this version said

| # | Model | Monday Score | Runs |
|---:|---|---:|---|
| 1 | GLM 5.2 | 91.2 | 90.5 / 87.5 / 95.5 |
| 2 | DeepSeek V4 Flash | 89.3 | 97.5 / 86.5 / 84.0 |
| 3 | GLM 5.3 Flash | 87.3 | 85.0 / 85.5 / 91.5 |
| 4 | **Qwen 3.8 Flash** | **86.5** | **93.0 / 66.5 / 100.0** |
| 5 | MIMO v2.5 | 81.2 | 64.5 / 81.5 / 97.5 |
| 6 | Qwen 3.6 | 70.2 | 75.5 / 83.0 / 52.0 |
| 7 | Gemma 4 | 54.2 | 58.0 / 45.5 / 59.0 |

## Why it was superseded

`audits/monday-002/qwen-3.8-stability-report.md` found that Qwen 3.8 Flash's
66.5 run came back with **zero reasoning tokens**, against 42,808 and 30,342 for
its two sibling runs, in 19.6 seconds against 380 and 285, with a different
input token count for a byte-identical prompt. The provider served a
non-thinking path and the harness had no way to notice: it recorded
`reasoning_enabled: true` from a declared capability in `models.yaml` rather
than from anything in the response.

That run therefore did not belong to the same experimental regime as the other
two, and averaging the three measured a mixture of two systems.

The correction did **not** rescore anything. The run's raw output, its
evaluation and its 66.5 all stand exactly as generated; the run simply stopped
counting as official evidence, and a replacement was generated under the
qualification rules that now exist.

## Nothing here has been altered

These five files are byte-for-byte the artefacts that were published, including
their `generated_at` timestamps. The corrected versions live in
`leaderboard/monday-002/`.
