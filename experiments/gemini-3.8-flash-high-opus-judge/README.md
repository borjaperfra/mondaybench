# Gemini 3.8 Flash (High) — blind re-judge, criterion by criterion

**2026-10-15. Off-board. The model stays PROVISIONAL.**

The fifteen Gemini 3.8 Flash (High) responses in
`gemini-3.8-mondaybench-challenger/` had a published score (88.37) but no
criterion-level labels anywhere, so the model could not enter the capability
profiles. This experiment re-judges all fifteen from the existing blind pack,
criterion by criterion, and replaces that score.

## Result

| Scenario | Rubric | Runs | Mean | Range | Sample sd |
|---|---|---|---:|---:|---:|
| monday-001 | 0.2 | 97.0 / 94.5 / 94.5 | 95.33 | 2.5 | 1.44 |
| monday-002 | 0.2 | 81.0 / 79.5 / 79.5 | 80.00 | 1.5 | 0.87 |
| monday-003 | 0.3 | 81.5 / 82.0 / 90.5 | 84.67 | 9.0 | 5.06 |
| monday-004 | 0.3 | 76.5 / 67.5 / 72.5 | 72.17 | 9.0 | 4.51 |
| monday-005 | 0.4 | 100.0 / 98.0 / 95.5 | 97.83 | 4.5 | 2.25 |
| **Monday Score** | | | **86.00** | | |

The earlier figure was 88.37 (97.0 / 81.0 / 85.33 / 78.5 / 100.0). Its labels
were never kept, so the two passes cannot be compared criterion by criterion.
Most of the gap is monday-004: this pass applies one `UNSUPPORTED_CAUSALITY`
penalty to each run, for stating why customers churned or contracted when the
answer key says "No file records why any customer churned. A stated reason is
invented." The earlier pass recorded that it applied no global penalties.

## Who judged, and how blind

- **Judge:** Claude Opus 5.5, in-session, one instance per scenario, five in
  parallel. **Not** the Claude Opus 5 that `evaluator-opus5-v0.x` pins and that
  labelled the board. Same protocol, same rubrics, a newer model — so this is
  not the board's judge, and the row stays provisional for that reason too.
- **Blind:** each judge read only `JUDGING.md`, the operative rules and its
  own scenario's sections A–D of `audits/blind-rejudge/opus-5-blind-rejudge.md`,
  and the anonymised candidates in the pack. They were forbidden the
  provenance map, every verdict, evaluation and leaderboard, and were not told
  any earlier score. The session that dispatched them knew the earlier 88.37.
- **Evidence:** every label carries specific evidence, PASS included — 353
  distinct evidence strings over 354 criterion labels.

## Files

| File | What |
|---|---|
| `JUDGING.md` | The brief every judge worked from |
| `blind-verdicts/<scenario>.blind.jsonl` | Labels as written, keyed by candidate id |
| `join-and-score.py` | Joins candidates to runs through the provenance map and scores with `mondaybench.scoring.build_breakdown` |
| `verdicts.jsonl` | The same labels keyed by run id |
| `scores.json` | Per-run scores, dimensions, penalties; scenario means; Monday Score |

`audits/capabilities/build-provisional-capabilities.py` builds the capability
profile from `verdicts.jsonl` with the canonical builder, and refuses to write
it unless every run reproduces `scores.json`.
