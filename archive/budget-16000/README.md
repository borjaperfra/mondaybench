# The 16,000-token battery — superseded 2026-08-28

Twenty runs of `monday-001`, all judged under `evaluator-opus5-v0.1` against
rubric 0.2, generated with `max_output_tokens: 16000` for every model.

## Why it is here and not in `runs/`

`deepseek-v4-flash` stopped being able to answer this prompt at that budget. Two
consecutive attempts on 2026-08-28 produced 69,501 and 70,207 characters of
reasoning and no answer at all (`finish_reason=length`), while its run-001 and
run-002 had completed comfortably at the same budget the day before, using 2,904
and 4,898 output tokens.

`IMPLEMENTATION.md` §34 forbids a free re-run unless the configuration itself was
invalid, so the budget was raised — for **all seven models**, to 32,000, rather
than for the one model that needed it. Per-model tuning to rescue one model is
exactly what a benchmark must not do.

`official.qualify_run` then rejected all twenty runs on
`max_output_tokens 16000 != configured 32000`. That rejection is the mechanism
working as designed: a mixed-budget ranking is not a ranking. The battery was
regenerated from scratch.

## What is here

```
runs-monday-001/      20 runs, 7 models (deepseek-v4-flash has 2, the rest 3)
evaluations/          evaluator-opus5-v0.1 (20), evaluator-manual-v0.2 (7),
                      evaluator-manual-v0.1 (7)
verdicts/             the verdict files and the _generate.py that produced them
```

## Do not reuse the verdicts

`verdicts/*.verdicts.jsonl` here are keyed by run id — `monday-001__<model>__001`
and so on — and the regenerated battery **reuses those same run ids for
different responses**. Serving these labels against the new runs would silently
attach the wrong evidence to the wrong text. They are kept as the audit trail for
the archived evaluations, and for nothing else.

## Scores it recorded

Mean final score under `evaluator-opus5-v0.1`, for reference only. Not
comparable with anything produced at 32,000.

| Model | n | mean |
|---|---:|---:|
| `glm5.3-flash` | 3 | 97.5 |
| `glm5.2` | 3 | 90.8 |
| `deepseek-v4-flash` | 2 | 87.5 |
| `qwen3.8-flash` | 3 | 84.7 |
| `mimo-v2.5` | 3 | 84.3 |
| `qwen3.6` | 3 | 72.0 |
| `gemma4` | 3 | 68.0 |
