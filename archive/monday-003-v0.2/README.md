# monday-003 v0.2 — calibration draft, superseded 2026-08-28

The second calibration of Blockers: the version that fixed the scenario. Kept
whole because v0.3 changed only the rubric, and because the design decisions
recorded here are the ones that made #003 discriminate.

## What it did

v0.1 saturated — three models on 100.0, spread 20.0, 10 of 20 criteria constant.
v0.2 stripped the dependency leaks out of `work-items.csv` and `meetings.md`,
added a second dated commitment (the Contoso Q3 compliance export, Tuesday 16:00
CET) that shares the same root dependency as the SSO chain, and gave the
engineer who owns the un-substitutable work a substitutable task and a named
substitute.

| | v0.1 | v0.2 |
|---|---:|---:|
| Best score | 100.0 ×3 | 100.0 ×2 |
| Median | 98.5 | 88.0 |
| Lowest | 80.0 | 49.0 |
| Spread | 20.0 | **51.0** |
| Constant point mass | 55.0 | **35.0** |
| Penalties | 0 | **4, across 2 runs** |

| Model | Score |
|---|---:|
| GLM 5.3 Flash | 100.0 |
| Qwen 3.8 Flash | 100.0 |
| MIMO v2.5 | 93.5 |
| GLM 5.2 | 88.0 |
| DeepSeek V4 Flash | 68.5 |
| Gemma 4 | 52.5 |
| Qwen 3.6 | 49.0 |

DeepSeek V4 Flash fell from joint first in v0.1 to fifth, losing 31.5 points,
almost all of it on the two resource-allocation criteria. That reordering is the
evidence that v0.2 measured something v0.1 did not.

## Why it was replaced

Not by a redesign. v0.2 met three of its four targets and the scenario itself is
carried into v0.3 **unchanged** — the rendered candidate prompt still hashes to
`aaf788f309d955d2b427c86fe7d95d2bbf88575fde7306adcfd74b0ec4a4103f`. What it
lacked was resolution at the top and one correct criterion:

- **Two models tied at exactly 100.0** with no criterion able to separate them,
  even though GLM 5.3 Flash wrote *"Wed 15:00"* for a Thursday 15:00 milestone
  inside its answer. v0.3 adds `factual_plan_accuracy` (5).
- **`contoso_state_separated` was wording-sensitive.** Five of seven scored
  PARTIAL for separating the two Contoso items correctly in their plans without
  writing a sentence equivalent to "the export runs". v0.3 rewrote it to score
  the operational distinction.
- **`sso_chain` never discriminated** — 7/7 PASS in both versions, with and
  without the leaks. v0.3 cut it from 8 points to 4.

## What is here

```
scenario/                                        the v0.2 scenario as it was run
RENDERED_PROMPT_SHA256.txt                       aaf788f3… - identical in v0.3
evaluator-opus5-v0.3-calibration-2.yaml          bound to scenario 0.2 / rubric 0.2
judge-prompts/                                   its judge and penalty prompts
runs-monday-003/                                 7 runs, all qualified first attempt
evaluations-evaluator-opus5-v0.3-calibration-2/  7 evaluations with per-criterion evidence
verdicts/                                        the recorded labels and their generator
test_monday_003.py                               the v0.2 guards, as they stood
calibration-report.md                            the report that produced the REVISE verdict
```

## Two traps for anyone reading this later

**The runs here are also live.** Because v0.3 changed no candidate-visible
source, these seven responses remain valid samples of the v0.3 prompt and are
still present as `runs/monday-003/<model>/run-001.json`, rescored under rubric
0.3. The copies here are the frozen v0.2 record; the live ones carry v0.3
evaluations. Neither set was edited.

**Nineteen of the twenty criterion ids survive into rubric 0.3, and two of them
changed meaning.** `contoso_state_separated` was rewritten and
`factual_plan_accuracy` was added, so replaying these verdict files against a
v0.3 evaluation would attach v0.2 semantics to a v0.3 criterion and silently
score the wrong thing. The rubric version, not the criterion id, is what
identifies a label.
