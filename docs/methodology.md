# Methodology

## What MondayBench measures

One realistic task, scored on six axes at once. The model receives a weekend's
accumulation of workplace information and must produce a Monday briefing: what
happened, what needs attention today in priority order, what is informational,
and what is unclear.

The difficulty is not retrieval. The material contains decisions that were
reversed, work already reassigned to someone else, an incident already closed,
speculation with no supporting data, and ordinary chatter — mixed in with the
three things that genuinely need doing. A model that extracts urgent-sounding
keywords scores badly. A model that reconstructs the current state scores well.

## Why three runs

**Because one run does not represent a model.** This is not a theoretical
concern; it was measured during calibration.

`glm5.3-flash` was run twice on the same scenario at `temperature: 0`. On the
first run it reasoned about Umbrella's error *rate* explicitly — "163 API errors
(~0.17% error rate vs <0.01% for every other customer)" — a PASS on
`umbrella_error_rate`. On the second run, same model, same prompt, same settings,
it compared latencies across customers but never derived Umbrella's own rate — a
PARTIAL. One criterion, 1.5 points, flipped purely on run-to-run variance.

A single run would have reported that model as either capable or incapable of
rate reasoning, and either report would have been half wrong. Three runs with a
published `run_range` show the reader how much to trust the number.

Models are not deterministic even at `temperature: 0`, and thinking models are
less so. The official score is therefore the **plain mean of three runs**. The
worst run is not dropped, best-of-N is not used, and min, max, `run_range` and
standard deviation are published beside the mean so a lucky run is visible as
one.

## How the score is calculated

```
raw response
  → judge assigns PASS / PARTIAL / FAIL per criterion, with evidence
  → scoring.py converts labels to points (deterministic Python, no model)
  → dimensions sum to a base score out of 100
  → global penalties subtract, capped at −20, floored at 0
  → Monday Score = mean of the three runs
```

The judge is **never asked for a number**. It classifies 19 atomic criteria
against fixed definitions and returns the evidence in the response that
justifies each label. Every point is assigned by `mondaybench/scoring.py`, which
imports no provider and calls no model.

Two further judge calls run per response: one classifying six named false-action
categories, and one identifying material hallucinations, prohibited actions and
self-contradictions. For penalties the judge classifies each candidate with a
`materially_misleading` boolean rather than being asked to stay silent about what
it noticed; Python drops the ones marked false and keeps them visible under
`penalties.dismissed`. That design came from calibration, where the judge
returned penalties whose own stated reasons read "Not a violation-level issue on
its own" and still cost 5 points each.

| Dimension | Max |
|---|---:|
| Action detection | 25 |
| State reconstruction | 25 |
| Prioritization | 15 |
| Data reasoning | 15 |
| Uncertainty | 10 |
| Noise resistance | 10 |
| **Base** | **100** |

## Why TTFA and latency sit outside the score

The Monday Score measures task quality only. Speed and cost are recorded next to
it and never folded into it, because combining them would bury a judgement the
reader should make themselves.

The calibration data shows exactly why. `glm5.3-flash` scores highest — and takes
**about two minutes before it emits its first visible word**, because it spends
that budget thinking. `glm5.2` scores several points lower and starts answering
in about five seconds. Whether those points are worth two minutes of blank screen
depends entirely on the reader's situation, and no weighting we invented would be
honest about that.

So the leaderboard publishes both, separately:

- **TTFA** — time to first *answer* token: what a user actually waits.
- **TTFT** — time to first token of any kind, the API-level metric. For a
  thinking model, the gap between TTFT and TTFA *is* the thinking time.
- **Total latency** and **cost per run**, when the provider reports a price.

Medians, not means: with three runs one outlier drags a mean somewhere no run
actually was.

The only stability metric is `run_range = max_score − min_score`. There is
deliberately no "efficiency score" and no combined speed/quality number.

## The official evaluator

`evaluator-opus5-v0.1` pins the judge model (`claude-opus-5`), the provider route
(native Anthropic Messages API), the rubric (`rubric-0.2.yaml`), the generation
parameters and the expected output shape. Every evaluation records the exact
judge `model_id`, a `prompt_fingerprint` of the judge instructions, and the
`rubric_version`.

The model behind that id never changes. A different judge model, a different
route, or an edited judge prompt each require a new evaluator id, and the
leaderboard refuses to aggregate across any of them.

One caveat stated openly: Claude Opus 5 rejects `temperature`, so the requested
`temperature: 0` cannot take effect. The provider drops it and records
`"temperature"` in `judge.unsupported_parameters` on every evaluation. The judge
is therefore not bit-deterministic, which is why verdicts are stored as
artifacts — a published evaluation is reproducible as a *record*, and disputes
are settled by reading the stored evidence.

## Everything is public

Scenario inputs, the assembled prompt and its SHA-256, the ground truth, the
rubric, every raw model response, every judge label with its evidence and
reasoning, the scoring code, and the leaderboard. Any published number traces
back through the chain above, and every file it depends on is in this repository.

`scenarios/monday-001/FROZEN.yaml` records the SHA-256 of every canonical file.
`mondaybench validate` fails if any of them changes, and
`mondaybench leaderboard --official` refuses to publish against drifted content.

## Limitations of monday-001

- **One scenario.** A single task, however realistic, is not a general measure.
- **English only.**
- **Office knowledge work.** Nothing here tests engineering, clinical, legal or
  physical work.
- **An LLM judge** does the semantic classification. Human audit covered the
  calibration phase, and the judge's own reasoning is published for every label
  so a disputed call can be checked rather than trusted.
- **No headroom at the top.** Calibration found the scenario separates models
  well through the middle of the range but compresses at the ceiling. See
  `CALIBRATION.md`.
- **Noise resistance does not discriminate.** Every model in the calibration
  sweep scored 10/10. The false-action categories catch a failure mode these
  models simply do not have.
- **Not a measure of general intelligence.** It answers one question: can this
  model handle your Monday?

## Reproducing the official evaluation

```bash
# 1. Verify the published scenario has not drifted
mondaybench freeze --scenario monday-001 --check
mondaybench validate --scenario monday-001 --evaluator evaluator-opus5-v0.1

# 2. See what already counts as official and what is missing
mondaybench plan --scenario monday-001 --runs 3

# 3. Reach three official runs per model, generating only the shortfall
mondaybench run --scenario monday-001 \
    --models glm5.3-flash,glm5.2,mimo-v2.5,deepseek-v4-flash,qwen3.8-flash,qwen3.6,gemma4 \
    --runs 3 --reuse-valid-runs

# 4. Judge all 21 runs (needs ANTHROPIC_API_KEY)
mondaybench evaluate --scenario monday-001 \
    --models glm5.3-flash,glm5.2,mimo-v2.5,deepseek-v4-flash,qwen3.8-flash,qwen3.6,gemma4 \
    --evaluator evaluator-opus5-v0.1 --review

# 5. Publish, with every integrity gate enforced
mondaybench leaderboard --scenario monday-001 \
    --evaluator evaluator-opus5-v0.1 --official --runs 3
mondaybench results --scenario monday-001 --evaluator evaluator-opus5-v0.1
```

`--reuse-valid-runs` counts existing official runs, generates only the shortfall,
never reuses a run number, and rejects any stored run whose prompt hash, model
id, temperature, output budget or provider does not match the published
configuration — printing the reason for each rejection.

`--official` writes nothing unless every gate passes: three official runs per
model, one prompt hash, one rubric version, one judge model and prompt
fingerprint, no integrity warning, no missing evaluation, and scores that
re-derive correctly from their own dimensions and penalties.
