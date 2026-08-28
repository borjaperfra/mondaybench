# MondayBench

**A practical benchmark for testing whether an AI model can reconstruct a messy workplace situation and decide what matters.**

One question:

> Can this model handle your Monday?

## Scenarios

Two scenarios are published and official. Each is frozen independently, scored
against its own rubric, and comparable only within itself — there is no combined
"overall" score, and there will not be one until there are enough scenarios for
a weighting to mean something.

| # | Scenario | Version | What it tests | Leader | Results |
|---|---|---|---|---|---|
| 001 | **Back to Work** | 0.1 | Reconstructing a state that changed while you were away | GLM 5.3 Flash — 98.0 | [`leaderboard/`](leaderboard/leaderboard.md) |
| 002 | **Moving Targets** | 0.2 | Release-path choice under hard scheduling, cross-source customer risk, arithmetic vs causality | GLM 5.2 — 91.2 | [`leaderboard/monday-002/`](leaderboard/monday-002/leaderboard.md) |

`monday-002` ships two extra audit artefacts: a
[criterion matrix](leaderboard/monday-002/criterion-matrix.md) covering all 20
criteria across 7 models and 3 runs each, and an
[analysis report](leaderboard/monday-002/analysis.md) with the failure stories
behind the scores. It discriminates far harder than #001: the score spread is
37.0 points against 27.3, and only 21 of 100 points return the same label in
every one of its 21 runs.

`archive/` keeps every superseded battery — earlier prompt hashes, an earlier
output budget, and both calibration drafts of #002 — separated from the official
results and never mixed with them.

## Why it exists

Traditional benchmarks test isolated capabilities one at a time. MondayBench tests several everyday capabilities together, in one realistic task: read a weekend's worth of accumulated work information, work out what the current state of the world actually is, and say what to do about it this morning.

The hard part is not retrieval. It is that the material contains decisions that changed, work that has already been done by someone else, incidents that are already closed, speculation with no supporting data, and ordinary chatter — all mixed in with the three things that genuinely need attention today.

## What the model sees

`monday-001` — *Back to Work*. It is Monday 09:07; you have been away since Wednesday 17:30. The model receives, in this fixed order:

| Source | Contents |
|---|---|
| `slack.md` | Two days of messages across nine channels |
| `emails.md` | Seven emails, including one with a hard deadline |
| `meetings.md` | Notes from two Friday meetings |
| `tasks.md` | A task list exported Monday 08:55 — deliberately stale |
| `metrics.csv` | Per-customer API metrics with one unexplained anomaly |

Then one prompt asking for a Monday briefing in four parts: what happened, what needs attention today in priority order, what is informational only, and what is unclear.

## What is scored

100 base points across six dimensions, minus global penalties (capped at 20):

| Dimension | Max | Question it answers |
|---|---:|---|
| Action detection | 25 | Did it find the work that actually needs doing today? |
| State reconstruction | 25 | Does it know the *current* state, not the stale one? |
| Prioritization | 15 | Is the most urgent thing first? |
| Data reasoning | 15 | Did it read the metrics and cite them correctly? |
| Uncertainty | 10 | Does it separate what it observed from what it cannot know? |
| Noise resistance | 10 | Did it avoid inventing work that does not exist? |

Two design rules matter more than the weights:

- **A verbose answer must not score better.** Points come from named criteria, not from coverage.
- **Unsupported certainty is a failure mode.** A model that says "I cannot establish this from the provided data" scores better than one that guesses confidently.

### How scoring works

The LLM judge **never assigns a number**. For each of the 19 rubric criteria it returns one of `PASS` / `PARTIAL` / `FAIL`, plus the evidence in the response that justifies the label. Deterministic Python in `mondaybench/scoring.py` converts labels to points. The rubric is human-authored and public; the judge only maps a response onto it.

Two further judge calls run per response: one classifying six named false-action categories (noise resistance), and one identifying material hallucinations, prohibited actions, and self-contradictions (global penalties).

**One deliberate deviation from `IMPLEMENTATION.md` §22.** The spec shows the penalty judge only the ground truth. That is not answerable: a material hallucination is a claim "unsupported by the supplied evidence", and `ground-truth.yaml` is an answer key summarising the correct *conclusions*, not the evidence itself. Judged against it alone, every accurate detail a model quotes from Slack or email looks invented.

This is not theoretical — it was caught in calibration. A single `gemma4` run drew four `MATERIAL_HALLUCINATION` penalties, capping at −20 and scoring 58. All four claims ("connection pool exhaustion in the 2.18.0 deploy", "a regression in CSV exports", "New ARR: €31k", "tiers are currently being modeled") are verbatim in the source files. With the sources supplied to the judge, the same response scores 76.5 with zero penalties. The penalty judge now receives both: the sources as the authority on what is *supported*, the ground truth on what is *materially relevant*.

Alongside the judge, deterministic text matchers check whether the response contains the evidence a criterion requires (`11:00` near Contoso, `3.1` and `4.4`, `163`/`1821`/`41` near Umbrella, `Wednesday`, `Julia`). These **never award or remove a point**. When the judge marks a criterion `FAIL` but the matcher plainly finds the evidence, the evaluation records a warning so a human can look. This is how judge mistakes get caught during calibration.

## Reproducibility

```bash
# Setup
uv venv --python 3.12
uv pip install -e ".[dev]"
cp .env.example .env   # then fill in endpoints and keys

# Check the scenario, rubric and evaluator config are internally consistent
mondaybench validate --scenario monday-001

# See exactly what a model will be sent, and its hash
mondaybench prompt --scenario monday-001 --hash-only

# List what is configured
mondaybench scenarios
mondaybench models

# Confirm every model id against the endpoint that actually serves it
mondaybench endpoints

# Resolve everything without calling an API
mondaybench run --scenario monday-001 --model glm5.2 --dry-run

# Reach three official runs per model, generating only the shortfall
mondaybench run --scenario monday-001     --models glm5.3-flash,glm5.2,mimo-v2.5,deepseek-v4-flash,qwen3.8-flash,qwen3.6,gemma4     --runs 3 --reuse-valid-runs

# Evaluate stored runs (does not re-run any model)
mondaybench evaluate --scenario monday-001 --model glm5.2 --evaluator evaluator-opus5-v0.1
mondaybench evaluate --scenario monday-001 --all-models --evaluator evaluator-opus5-v0.1 --review

# Build the ranking (--official enforces every publication gate)
mondaybench leaderboard --scenario monday-001 --evaluator evaluator-opus5-v0.1 --official

# All of the above in one command
mondaybench benchmark --scenario monday-001     --models glm5.3-flash,glm5.2,mimo-v2.5,deepseek-v4-flash,qwen3.8-flash,qwen3.6,gemma4     --runs 3 --reuse-valid-runs --evaluator evaluator-opus5-v0.1
```

`--review` writes a per-run audit file listing every non-`PASS` criterion, every triggered penalty, every judge/matcher disagreement, and the full raw response — so reviewing a newly released model is minutes of reading, not an hour of manual grading.

Run the tests with `pytest`.

## Transparency

Everything is public: scenario inputs, the assembled prompt and its SHA-256, ground truth, the rubric, every raw model response, every judge classification with its evidence, the scoring code, and the leaderboard.

Every published score traces back through a chain you can follow yourself:

```
raw response  ->  per-criterion label + evidence  ->  deterministic points  ->  mean of 3 runs
```

**Immutability.** `runs/` is benchmark evidence. The runner refuses to overwrite an existing run file without `--overwrite`, and never writes a run for a failed API call. Generation and evaluation are separate: a new evaluator can re-score existing responses without re-running any model.

**Versioning.** A published scenario is immutable; material changes to its content require a new scenario id. Evaluator changes are independent and carry their own version (`evaluator-v0.1`), including the exact judge model, which is recorded in every evaluation. Scores from different evaluator versions are never combined in one ranking.

**Aggregation.** A model's scenario score is the plain mean of its official runs. The worst run is not dropped and best-of-N is not used; minimum, maximum, range and standard deviation are published alongside the mean.

## The judge

> **Judging never uses the Anthropic API.** Every official label in this
> repository was produced by Claude Opus 5 reading each response against the
> rubric in a recorded Claude Code session, and written into
> `verdicts/<scenario>/<model>.verdicts.jsonl`. `mondaybench evaluate
> --verdicts` then scores those labels deterministically. **Do not set
> `ANTHROPIC_API_KEY` and do not spend Anthropic API credits on this project** -
> that is a hard project rule, not a preference. The `provider: anthropic` /
> `model_id: claude-opus-5` fields in the evaluator config record *which model
> reasoned about the responses*; they are not an instruction to call an API.

`evaluator-opus5-v0.1` is the **official** evaluator for v0.1. The others ship
alongside it for calibration and for anyone without an Anthropic key. They are
never mixed in one ranking — that is what evaluator versioning is for.

Measured judge cost, not estimated: one seven-model sweep is roughly **465k input
and 35k output tokens**, or about 21 judge calls per run.

| Evaluator | Judge | Cost | Trade-off |
|---|---|---|---|
| **`evaluator-opus5-v0.1`** | **`claude-opus-5`, recorded session** | **no API spend** | **Official. Labels recorded with their evidence and replayed deterministically** |
| `evaluator-gateway-v0.2` | `claude-opus-5` via an OpenAI-compatible gateway | Billed from gateway credits | Same model, but `temperature` is rejected and `effort` is unavailable |
| `evaluator-open-v0.1` | Any OpenAI-compatible model (`JUDGE_MODEL`) | Zero marginal cost on your own infra | No closed model judging open ones; weaker label consistency |
| `evaluator-manual-v0.1` | Verdicts recorded in a worksheet | No credentials at all | Labels come from a reviewer, so they are not machine-reproducible |

All three feed the same deterministic scoring code, so a score is comparable *within* an evaluator and never across.

Two honest caveats about `evaluator-v0.1`, both recorded in every evaluation file:

- **`temperature` is not applied.** The config asks for `temperature: 0`, but Claude Opus 5 rejects the parameter outright. The provider drops it and records `"temperature"` in `judge.unsupported_parameters` rather than pretending the setting took effect.
- **The judge is therefore not bit-deterministic.** Re-running it on the same responses can shift a score slightly. This is why judge outputs are stored as artifacts: a published evaluation is reproducible as a *record*, and disputes are settled by reading the stored evidence rather than by re-rolling. `evaluator-open-v0.1` does accept `temperature: 0`, so determinism is actually reachable there.

Changing a judge model means creating the next version — never editing a published evaluator file.

### Manual and calibration judging

`IMPLEMENTATION.md` §33 requires a human to inspect every criterion label for the calibration runs. `evaluator-manual-v0.1` turns that audit into an artifact:

```bash
mondaybench worksheet --scenario monday-001 --model gemma4
# fill in the labels in worksheets/monday-001/gemma4/run-001.verdicts.jsonl
mondaybench evaluate --scenario monday-001 --model gemma4 \
    --evaluator evaluator-manual-v0.1 \
    --verdicts worksheets/monday-001/gemma4/run-001.verdicts.jsonl
```

The worksheet embeds the response under review and each criterion's three definitions inline, so grading needs no second window. It is as strict as the model judge: an unfilled label, a missing criterion, an omitted noise category, or an absent penalties list all fail loudly. Nothing is defaulted.

## Confirming model ids

Model ids drift and documentation lags — the ids in the original spec (`glm-5.3`, `qwen-3.8-flash`, `kimi-k3`) are served by neither endpoint, and the same model is spelled `glm-5.2` on Helmcode but `glm5.2` on NaN. Before an official run:

```bash
mondaybench endpoints
```

This queries `GET /v1/models` on every configured endpoint, marks the ids `models.yaml` declares, and exits non-zero if a declared id is not actually served. A wrong id fails the call rather than quietly scoring badly, but finding out before the run is cheaper.

## Limitations

MondayBench v0.1:

- is **one scenario**;
- is **English-only**;
- reflects office / knowledge-work tasks, not engineering, clinical, legal or physical work;
- uses an **LLM judge** for semantic classification, with human audit for the first official release;
- measures cost, latency and throughput but **excludes them from the score**;
- should **not** be treated as a measurement of general intelligence.

## Layout

```
scenarios/monday-001/   canonical benchmark inputs, rubric, ground truth
evaluators/             judge configuration, versioned
mondaybench/            the implementation
runs/                   raw model responses (immutable evidence)
evaluations/            judge classifications + deterministic scores
leaderboard/            leaderboard.json and leaderboard.csv
tests/                  offline test suite (no credentials needed)
IMPLEMENTATION.md       the full v0.1 specification
```

## License

MIT. The scenario, rubric and ground truth are published as an open benchmark.

---

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

# 4. Replay the recorded judge labels (no API key, no credits)
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
