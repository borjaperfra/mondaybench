# monday-003 v0.1 — calibration draft, superseded 2026-08-28

The first calibration draft of Blockers, with its nine run attempts and their
seven evaluations. Kept whole and kept apart: v0.2 replaced the scenario, the
rubric and the evaluator at once, so **nothing here is comparable with a v0.2
result** and the two must never share a table.

## Why it was replaced

It saturated. Three of seven models scored a flat 100, no run triggered a single
penalty, and **10 of its 20 criteria returned PASS for all seven models** — 55.0
of the 100 points were constant. Every model reconstructed the dependency chain
on the first attempt, including `critical_path_identified`, the ten-point
criterion the whole scenario was built around.

| Model | Score |
|---|---:|
| DeepSeek V4 Flash | 100.0 |
| GLM 5.3 Flash | 100.0 |
| Qwen 3.8 Flash | 100.0 |
| GLM 5.2 | 98.5 |
| MIMO v2.5 | 98.5 |
| Qwen 3.6 | 81.5 |
| Gemma 4 | 80.0 |

Spread 20.0 against a target of ≥ 25. Best score 100.0 against a target of
82–90.

Three causes, diagnosed in `calibration-report.md`: `work-items.csv` stated the
dependencies in its `business_context` column, `meetings.md` restated the Slack
chain as a tidy ordered list, and the prompt named the three answer types
("circular, stale, or removable"). Underneath all three, the scenario had **no
competing chain and no contested resource** — identifying the critical path
required reading, not judgement.

## What is here

```
scenario/                                       the v0.1 scenario as it was run
RENDERED_PROMPT_SHA256.txt                      efd83750… — the assembly, not the template
evaluator-opus5-v0.3-calibration.yaml           the v0.1 spelling of that evaluator id
judge-prompts/                                  its judge and penalty prompts
runs-monday-003/                                9 attempts: 7 valid, 2 rejected
evaluations-evaluator-opus5-v0.3-calibration/   7 evaluations with per-criterion evidence
verdicts/                                       the recorded labels and their generator
test_monday_003.py                              the v0.1 guards, as they stood
calibration-report.md                           the report that produced the REVISE verdict
```

## Three traps for anyone reading this later

**The evaluator id is nearly reused.** v0.2 ships
`evaluator-opus5-v0.3-calibration-2` against rubric 0.2 — 20 criteria again and
100 points again, but not one criterion id in common, different weights, and
two of the six dimensions renamed. Neither the count nor the total identifies
which rubric produced a score; the rubric version does. There is a test
(`test_no_criterion_id_survives_from_v0_1`) that keeps the id sets disjoint.

**The verdicts are keyed by run id.** `monday-003__<model>__001` names the v0.1
run here *and* the v0.2 run in `runs/`. Serving these labels against v0.2 runs
would attach the wrong evidence to the wrong text, and against a rubric whose
criteria have different names it would simply fail. They are the audit trail for
the archived evaluations, and for nothing else.

**Two of the nine runs are rejected attempts, on purpose.**
`runs-monday-003/qwen3.8-flash/run-001.json` and `run-002.json` came back with
zero reasoning tokens from a reasoning-declared model and were refused by
`qualify_run` as `REASONING_NOT_DELIVERED`. Attempt 3 is the scored sample. They
are kept because a serving defect that is deleted cannot be counted later.

## What replaced it

`scenarios/monday-003/` at scenario 0.2, rendered prompt
`aaf788f309d955d2b427c86fe7d95d2bbf88575fde7306adcfd74b0ec4a4103f`, with its own
calibration report at `analysis/monday-003-calibration-v0.2.md`. The v0.1 report
sits beside it as `analysis/monday-003-calibration-v0.1.md` and is copied here as
`calibration-report.md`.

v0.2 kept the story and replaced the shape of the problem: the dependency leaks
came out of `work-items.csv` and `meetings.md`, a second dated commitment was
added that shares the same root dependency, and the engineer who owns the
critical work was given a substitutable task and a named substitute. Spread went
from 20.0 to 51.0 and the constant point mass from 55.0 to 35.0. Two models still
finished on 100.0, which is why v0.2 is not frozen either.
