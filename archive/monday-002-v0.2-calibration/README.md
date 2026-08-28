# monday-002 v0.2-draft — calibration, superseded by the official freeze 2026-08-28

The calibration sweep that qualified "Moving Targets" for official publication:
four models, one attempt each, `evaluator-opus5-v0.2-draft`, rubric 0.2-draft.

**These are not official results.** One run per model measures nothing about a
model; it measures the scenario. They must never appear in a leaderboard or be
averaged with the official three-run battery in `runs/monday-002/`.

| Model | Base | Penalty | Final |
|---|---:|---:|---:|
| DeepSeek V4 Flash | 92.0 | 0 | 92.0 |
| Qwen 3.8 Flash | 85.0 | 0 | 85.0 |
| GLM 5.3 Flash | 81.5 | 0 | 81.5 |
| Qwen 3.6 | 67.5 | −5 | 62.5 |

Spread 29.5 points; 8 of 20 criteria identical across all four models, worth
37.0 points. v0.1 had a 4.5-point spread and 75.5 constant points. That is what
the redesign bought, and why this draft was frozen rather than redesigned again.

## What is here

```
scenario/                                    the scenario as calibration ran it
evaluator-opus5-v0.2-draft.yaml              the draft evaluator
judge-prompts/                               its judge and penalty prompts
runs-monday-002/                             4 runs
evaluations-evaluator-opus5-v0.2-draft/      4 evaluations with per-criterion evidence
verdicts/                                    the recorded labels and their generator
```

## What the freeze changed, and nothing else

Everything the models actually read is byte-identical between this snapshot and
the official scenario. The rendered candidate prompt hashes to
`740e627cbc7413c321ede0d54000504de54821d34ff4677f82731b89600423a8` in both, so
the calibration responses were produced against exactly the official input.

1. `scenario.yaml`: `benchmark_version` and `scenario_version` `0.2-draft` → `0.2`,
   `status` `calibration` → `official`, `official_runs: 3` added.
2. `rubric.yaml`: `rubric_version` `0.2-draft` → `0.2`. No criterion, weight or
   definition changed.
3. `deployments.csv` deleted from the live scenario. It was a v0.1 leftover that
   was never in `source_order`, so no model ever saw it and no score depends on
   it. Kept here, and in `archive/monday-002-v0.1/scenario/`.
4. `penalty-judge-prompt.md` rewritten. The calibration version is preserved in
   `judge-prompts/` here; see below.

## The one substantive change: MAJOR_PLANNING_ERROR

Calibration exposed a gap. Three of four models chose release path A after
wrongly concluding that path B was infeasible. The draft prompt said to penalize
"impossible dependency schedules" and to be conservative — but their schedules
were entirely possible; only their reason for rejecting B was false. The prompt
did not say which way to read that, so the calibration labels took the
conservative reading and applied no penalty.

The official prompt settles it explicitly: MAJOR_PLANNING_ERROR applies to a
recommended plan that cannot be executed, not to wrongly rejecting a viable
alternative, which the planning criteria already price. Under both readings the
calibration ranking is identical, which is why the draft's scores stand as a
valid qualification of the scenario.

## Three traps for anyone reading this later

**Three run histories now share the id `monday-002`.** v0.1 calibration
(`archive/monday-002-v0.1/`), v0.2 calibration (here), and the official v0.2
battery (`runs/monday-002/`). Only the last is publishable.

**The evaluator id `evaluator-opus5-v0.2-draft` is reused across two rubrics.**
It scored the v0.1 draft *and* this one. The id alone does not identify what
produced a score; the rubric version does. Official results carry
`evaluator-opus5-v0.2`, which is a distinct file.

**The verdicts are keyed by run id.** `monday-002__<model>__001` names a run in
all three histories. Serving these labels against official runs would attach the
wrong evidence to the wrong text.
