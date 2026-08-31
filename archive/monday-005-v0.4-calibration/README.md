# monday-005 v0.4 — calibration, superseded by the freeze 2026-08-31

The calibration battery for "Read the Room", kept whole and kept apart from the
official battery that follows it.

**The scenario itself did not change when it was frozen.** Its candidate-visible
content — `prompt.md`, `context.md` and the seven sources — is byte-identical
throughout, and the rendered prompt hashes to
`532cd464a9b75045f808886c44e667237d6fd1b947826510643b9f8bcc30059a` here and in
the frozen scenario. What iterated four times was the rubric. That is why
`scenario_version` stays at 0.1 while `rubric_version` reads 0.4.

## Why these runs are not the official runs

Twenty-one runs live here, three per model. They were generated under the same
131,072-token safety ceiling and against the same prompt as the official battery
will be, and every one passes qualification. They are still not official
evidence, for the reason monday-003 and monday-004 recorded before them:

- **Rubrics 0.2, 0.3 and 0.4 were all written while reading these responses.**
  0.2 fixed two bands after reading seven of them. 0.3 repaired four more and
  added two criteria after judging those seven. 0.4 repaired three more after
  judging all twenty-one. A rubric fitted to a response cannot then be scored
  on that same response and published.
- They are the battery that produced the freeze recommendation, so they are the
  evidence *for* the decision, not evidence produced *under* it.

`leaderboard.check_calibration_overlap` enforces this: publishing refuses if any
run in an official battery was also scored by a calibration evaluator. Every run
here was scored by `evaluator-opus5-v0.5-calibration`.

The official battery is three new runs per model, generated after this freeze,
under `runs/monday-005/`. Same prompt, same models, same ceiling, no shared
samples.

## The one candidate boundary that was NOT fitted to these responses

Recorded because it is the strongest evidence in the archive that the audit
chain worked. `cause_investigation_not_external` was proposed in
`monday-005-boundary-audit-blind.md` from two quoted lines of frozen source
material, sealed by hash before any shadow scoring, and it passed every model
in the seven responses it was written from. It first caught a response in the
3×7 battery — qwen3.6 run-003, which did not exist when the criterion was
written. A criterion cannot be fitted to a response that does not yet exist.

## An honesty note about the blind protocol

`monday-005-boundary-audit-blind.md` §0 records that the Phase-A blindness
protocol could not be honoured: the agent writing it had already read all seven
responses in the preceding task. The compensating controls are stated there
rather than the guarantee being claimed. A reader auditing this archive should
weigh the boundary proposal accordingly.

## What is here

| | |
|---|---|
| `runs-monday-005/` | the twenty-one calibration runs, and both failed serving attempts |
| `evaluations-evaluator-opus5-v0.5-calibration/` | scored under rubric 0.3 |
| `verdicts/` | every verdict file: 0.2, the 0.3 shadow, the 3×7, and the 0.4 shadow |
| `rubric.yaml`, `rubric-0.2.yaml`, `rubric-0.3.yaml` | the superseded rubrics, unedited |
| the six analysis documents | pre-calibration, generation, 0.2 calibration, boundary audit, 0.3 shadow, 3×7 |

## Serving failures on record, which belong beside a score and never inside one

| Model | Attempt | What happened |
|---|---|---|
| deepseek-v4-flash | 1 of 3 | ~136,000 reasoning tokens, no answer, ceiling-bound. Two later attempts used 3,263 and 11,004 — a 40× spread at temperature 0 |
| qwen3.8-flash | 1 retry | HTTP 429 from NaN, clean on retry |

The largest legitimate generation in the battery was 36,687 tokens against a
131,072 ceiling. The ceiling never bound a completed answer and was not raised.
