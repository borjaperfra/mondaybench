# deepseek-v4.1-flash-reliability-v1

A controlled experiment, not a benchmark entry.

## The hypothesis

Can a general-purpose reliability system prompt improve DeepSeek V4.1 Flash's
consistency on MondayBench, **without giving it any benchmark-specific
information**?

## The design

Three batteries of the same model against the same five frozen scenarios:

| battery | where it lives | system prompt |
| --- | --- | --- |
| published | `runs/monday-00X/deepseek-v4.1-flash/` | harness default |
| second (variance probe) | `runs/monday-00X/deepseek-v4.1-flash-probe/` | harness default |
| **this one** | `experiments/deepseek-v4.1-flash-reliability-v1/runs/` | reliability prompt v1 |

Everything else is held constant: same provider, same `model_id`, same endpoint,
same temperature, same output ceilings, same `extra_body`, same prompt assembly,
same retry policy, same schema, same writer. `pre-generation-control-check.json`
is the machine-checked proof, produced **before** the first API call; it compares
every `ModelConfig` field that reaches the wire and refuses to pass on any
difference other than the declared one.

The published battery is untouched. Its Monday Score of 84.63 is unchanged and
this experiment is not on any board.

## The variable

`frozen-system-prompt.txt` — 2,321 bytes, LF, sha256
`eb136804970c72fa214521a341fdde95294393990fae0a5e86bd15614794653d`.

Frozen and hashed before the first call, unedited since. It is generic by
construction: it names no scenario, no rubric criterion, no reference answer, and
no failure from either previous battery. Everything in it is a way of *working* —
resolve newer over stale, respect ownership and dependencies, check the
arithmetic, keep a hypothesis a hypothesis, give each audience what that audience
should have. The model still has to find all of that in the scenario sources.

That distinction is the whole experiment. A prompt that said "choose Option B" or
"the aggregate is 29.9%" would raise the score and prove nothing; this one either
generalises or it does not.

## Generation was blind to evaluation

Each of the 15 requests carried exactly two messages: the frozen system prompt,
and the canonical assembled scenario prompt (`prompt.md` plus the files in
`scenario.yaml`'s `source_order`). Rubrics and ground truth are not in
`source_order` for any scenario, so they cannot reach generation through the
canonical path. No judge output, no prior verdict, no prior score, no prior
response, no leaderboard data, and none of the judge packs were in context.

No tools: the OpenAI-compatible provider sends no `tools` key and never has. No
browsing, no code execution, no retrieval, no calculator.

Runs are independent — one request each, no conversation state between them, no
best-of-N, no candidate selection. Retries fire only on transient provider
errors, never because an answer looked weak. A bad answer is a result and is
kept.

## What is here

| path | what it is |
| --- | --- |
| `frozen-system-prompt.txt` | the experimental variable, byte-exact |
| `system-prompt.sha256` | its hash |
| `pre-generation-control-check.json` | the control proof, written before generation |
| `config.json` | the exact configuration the battery ran under |
| `manifest.json` | per-run metadata and the integrity checks |
| `generate-battery.py` | the generation script — the canonical harness path |
| `runs/monday-00X/deepseek-v4.1-flash-reliability-v1/` | the 15 raw responses |
| `blind-judge-pack/` | 5 packs, 3 blinded candidates each, for an independent judge |
| `private-provenance-map.json` | **private** — candidate label → run, model, config |

Raw responses are stored exactly as returned: not cleaned, reformatted,
truncated, or corrected in any way. Each response's sha256 is in `manifest.json`
and in the blind pack.

## The blind pack

`blind-judge-pack/pack-monday-00X.json` carries the frozen prompt, every source
file in declared order, the frozen rubric with its bands, points, partial points
and penalty rules, the ground truth, and three candidates under shuffled neutral
labels. It names no model, no experiment, no treatment, no run number and no
prior score — `blind-judge-pack/scrub-log.json` records that check.

`private-provenance-map.json` is deliberately outside `blind-judge-pack/`. Do not
move it in.

## Judged 2026-09-11, and by whom

The 15 responses have now been scored. What was done, and what it is worth:

**The procedure.** Every candidate was judged from `blind-judge-pack/` alone,
scenario by scenario, against the frozen rubric bands and the ground truth in
the pack. The labels were written to `blind-verdicts/*.blind.jsonl` keyed by
`candidate_id`, and only then was `private-provenance-map.json` read — by a
script, to perform the `candidate_id -> run_id` join. No label was written or
changed after the mapping was known. `evaluate-battery.py` then scored the runs
through the harness's recorded-verdict route, with `root` pointed here, so
`verdicts/`, `evaluations/` and the scores all stay inside this directory.

**The judge was not independent, and this matters.** The section this replaces
asked for an independent judge. There is none available: judging on this project
is done in-session by Claude (Opus 5), the API route is prohibited, and the same
judge produced the recorded verdicts for the published battery and the variance
probe in earlier sessions. So the judge knew the treatment existed and what it
says. What blinding could still buy — and did — is that the judge did not know
which candidate was which run while labelling.

**The standard was deliberately held to the earlier batteries.** Before
labelling, the recorded verdicts of the published battery and the probe were
read for the same criteria, so that a PASS here means what a PASS meant there.
That keeps the three batteries comparable; it also means the three label sets
are not independent of one another.

**The result, and the caveat that travels with it.**

| battery | 001 | 002 | 003 | 004 | 005 | mean of scenario means |
| --- | --- | --- | --- | --- | --- | --- |
| published | 84.00 | 92.00 | 87.83 | 63.67 | 95.67 | 84.63 |
| variance probe | 96.00 | 93.50 | 93.67 | 69.33 | 93.33 | 89.17 |
| this battery | 88.50 | 91.50 | 88.83 | 85.67 | 97.17 | **90.33** |

**90.33 is not a Monday Score.** These runs carry a non-default system prompt,
so the number is not a leaderboard figure and nothing here goes on a board. It
is also worth reading next to the gap between the two *untreated* batteries:
they differ by 4.54 points on the same model, same config, same judge. That
spread is the yardstick any treatment effect has to beat, and against the probe
this battery is 1.16 points ahead of it.

The one place the difference is larger than that yardstick is **monday-004**:
63.67 and 69.33 untreated against 85.67 here. That is the scenario whose rubric
turns on the duplicate invoice, the annual-prepayment normalisation and the
new-logo attribution split.

### Consistency, which is what the prompt was actually for

The hypothesis was not a higher mean. It was that a general reliability prompt
would make the model *more consistent*. Run-to-run range inside each scenario,
which is the thing that hypothesis is about:

| battery | 001 | 002 | 003 | 004 | 005 | mean range |
| --- | --- | --- | --- | --- | --- | --- |
| published | 16.5 | 18.5 | 16.5 | 34.0 | 8.5 | 18.80 |
| variance probe | 1.5 | 10.5 | 7.0 | 29.0 | 14.0 | 12.40 |
| this battery | 8.0 | 11.0 | 17.0 | 12.0 | 3.0 | **10.20** |

The ordering goes the way the hypothesis predicted, and the clearest movement is
in the worst runs rather than the best: on monday-004 the low run is 47.5
published, 57.0 probed and 79.5 here, and the spread falls from 34.0 and 29.0 to
12.0. On monday-003 this battery is the *widest* of the three, so the effect is
not uniform.

With three runs per scenario the range is a fragile statistic, and the two
untreated batteries already differ from each other by 6.4 points of mean range.
Against the probe specifically this battery improves mean range by 2.2 points,
which that spread does not let anyone call an effect. monday-004 is the one
place where the movement is bigger than the noise between the untreated pair.

## The harness change behind this

`models.yaml` entries gained an optional `system_prompt_file`, applied in
`runner.apply_system_prompt`. It is inert for every model that does not set it,
and it moves only the system field — `scenario_prompt_sha256` still records the
frozen assembled user prompt, so a run under a different system prompt is still
traceable to the same scenario bytes. The difference is hashed into
`generation.system_prompt_sha256` and through it into `config_sha256`, where
qualification can see it. `harness` is a mutable group in the release policy, and
verdicts are recorded rather than recomputed, so no published score is affected.
