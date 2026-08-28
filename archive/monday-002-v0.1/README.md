# monday-002 v0.1 — calibration draft, superseded 2026-08-28

The first calibration draft of Moving Targets, with its four calibration runs
and their evaluations. Kept whole and kept apart: v0.2 replaced the scenario,
the rubric and the evaluator at once, so **nothing here is comparable with a
v0.2 result** and the two must never share a table.

## Why it was replaced

It saturated. Four models scored 91.0 to 95.5, and **17 of its 21 criteria
returned the same label for all four** — 75.5 of the 100 points were constant.
A mid-tier model (Qwen 3.6, 92.5) finished ahead of the #001 leader
(GLM 5.3 Flash, 91.0), which is measurement noise rather than a ranking.

| Model | Score |
|---|---:|
| Qwen 3.8 Flash | 95.5 |
| DeepSeek V4 Flash | 95.0 |
| Qwen 3.6 | 92.5 |
| GLM 5.3 Flash | 91.0 |

Two penalties in the battery, both `MATERIAL_HALLUCINATION` on Qwen 3.6, for
describing proposed pricing as confidential *until Wednesday's review* when the
source says confidential until approved **and** publicly announced.

## What is here

```
scenario/                                   the v0.1 scenario as it was run
evaluator-opus5-v0.2-draft.yaml             the v0.1 spelling of that evaluator id
judge-prompts/                              its judge and penalty prompts
runs-monday-002/                            4 runs, plus deepseek's failed attempt
evaluations-evaluator-opus5-v0.2-draft/     4 evaluations with per-criterion evidence
verdicts/                                   the recorded labels and their generator
```

## Two traps for anyone reading this later

**The evaluator id is reused.** v0.2 ships an `evaluator-opus5-v0.2-draft.yaml`
too, against a different rubric (0.2-draft, 20 criteria) and a different
scenario version. The id alone does not identify which one produced a score;
the rubric version does.

**The verdicts are keyed by run id.** `monday-002__<model>__001` means the v0.1
run here and the v0.2 run in `runs/`. Serving these labels against v0.2 runs
would attach the wrong evidence to the wrong text, and against a rubric whose
criteria have different names it would simply fail. They are the audit trail
for the archived evaluations, and for nothing else.
