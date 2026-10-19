# MondayBench

**A practical benchmark for testing whether an AI model can reconstruct a messy workplace situation and decide what matters.**

One question:

> Can this model handle your Monday?

## Scenarios

**Five scenarios are published and official**, frozen together since suite
v1.0. The current release is **suite v1.13**
([`releases/v1.13/SUITE-FROZEN.yaml`](releases/v1.13/SUITE-FROZEN.yaml)):
fifteen models, 225 official runs, 5,310 criterion verdicts. Each scenario is
frozen independently and scored against its own rubric.

| # | Scenario | Rubric | What it tests | Leader | Spread | Results |
|---|---|---|---|---|---:|---|
| 001 | **Back to Work** | 0.2 | Reconstructing a state that changed while you were away | GPT-6 Astra — 100.0 | 29.3 | [`leaderboard/v1.13/monday-001/`](leaderboard/v1.13/monday-001/leaderboard.md) |
| 002 | **Moving Targets** | 0.2 | Release-path choice under hard scheduling, cross-source customer risk, arithmetic vs causality | GPT-6 Astra — 100.0 | 45.8 | [`leaderboard/v1.13/monday-002/`](leaderboard/v1.13/monday-002/leaderboard.md) |
| 003 | **Blockers** | 0.3 | Prioritisation and resource allocation against a hard limit | GPT-6 Astra — 100.0 | 34.7 | [`leaderboard/v1.13/monday-003/`](leaderboard/v1.13/monday-003/leaderboard.md) |
| 004 | **Numbers Don't Lie** | 0.3 | Reconciling contradictory data, and what leadership is told about it | GLM 5.3 Flash and GPT-6 Astra — 98.0 | 62.8 | [`leaderboard/v1.13/monday-004/`](leaderboard/v1.13/monday-004/leaderboard.md) |
| 005 | **Read the Room** | 0.4 | One incident, four audiences, four different right answers | Claude Fable 5.1 — 100.0 | 20.7 | [`leaderboard/v1.13/monday-005/`](leaderboard/v1.13/monday-005/leaderboard.md) |

`monday-004` is the scenario that separates the field — 62.8 points between
first and last, and the worst Monday for eleven of the fifteen models.

The scenario boards live under `leaderboard/v1.13/`. Earlier suites keep their
own boards (`leaderboard/v1.1/` to `v1.5/` and `v1.10/`; v1.6 to v1.9 carried
the v1.5 evidence unchanged, v1.11 and v1.12 the v1.10 evidence), and the
unversioned `leaderboard/<scenario>/` files are the v1.0 boards, all kept byte-frozen.

## Overall

A model's **Monday Score** is the arithmetic mean of its official score on every
scenario in a release. Equal weight per scenario; nothing else folded in.

**Current board: [Overall v3.6](leaderboard/overall/overall-v3.6.md)**, suite v1.13.

| # | Model | Monday Score | #001 | #002 | #003 | #004 | #005 |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | GPT-6 Astra | **98.80** | 100.0 | 100.0 | 100.0 | 98.0 | 96.0 |
| 2 | Claude Opus 5 | **97.07** | 98.5 | 98.0 | 98.3 | 90.8 | 99.7 |
| 3 | Qwen 3.8 Flash | **95.07** | 92.5 | 94.8 | 94.5 | 96.5 | 97.0 |
| 4 | GLM 5.3 Flash | **94.93** | 98.0 | 87.3 | 92.8 | 98.0 | 98.5 |
| 5 | Claude Fable 5.1 | **94.90** | 97.5 | 91.0 | 96.7 | 89.3 | 100.0 |
| 6 | DeepSeek V4.1 Flash | **94.53** | 95.0 | 93.0 | 96.3 | 90.0 | 98.3 |
| 7 | GLM 5.3 | **93.73** | 97.5 | 87.7 | 94.8 | 91.7 | 97.0 |
| 8 | DeepSeek V4 Flash | **91.70** | 90.8 | 89.3 | 95.0 | 86.0 | 97.3 |
| 9 | DeepSeek V4.1 Flash (1017) | **91.23** | 90.3 | 95.2 | 95.8 | 79.7 | 95.2 |
| 10 | MiMo v2.6 Flash | **87.87** | 82.7 | 83.7 | 93.2 | 80.3 | 99.5 |
| 11 | MIMO v2.5 | **86.67** | 88.2 | 81.2 | 90.3 | 78.5 | 95.2 |
| 12 | GLM 5.2 | **86.50** | 84.3 | 91.2 | 87.3 | 71.2 | 98.5 |
| 13 | Gemini 3.8 Flash (High) | **86.00** | 95.3 | 80.0 | 84.7 | 72.2 | 97.8 |
| 14 | Qwen 3.6 | **68.77** | 82.8 | 70.2 | 65.5 | 46.0 | 79.3 |
| 15 | Gemma 4 | **63.00** | 70.7 | 54.2 | 65.3 | 35.2 | 89.7 |

These caveats travel with this board, one for each row that did not run through
this harness's own adapter or was not labelled by its usual judge:

- **GPT-6 Astra was generated through the Codex CLI**, because no authenticated
  API route exists; the frozen prompts match by SHA-256, but temperature, token
  counts and finish reason are recorded as `null`, never as numbers.
- **Claude Opus 5 and Claude Fable 5.1 were generated through `claude -p`**
  (Claude Code CLI, OAuth subscription, effort high). The frozen prompt bytes
  were passed to the route, but the route prepends its own system-prompt
  preamble, injects the runtime date into the user turn, and applies its own
  64,000-token output ceiling; temperature is not settable. Opus 5's labels are
  **GPT-5.6 Sol**'s blind re-judge (the Opus 5 judge would be judging itself);
  Fable 5.1's are the board's **Claude Opus 5** judge after a ten-label audit.
- **Gemini 3.8 Flash (High) was generated through Antigravity**, which sends no
  system prompt and exposes no temperature, token usage, finish reason or served
  model id. Its labels are a blind re-judge by **Claude Opus 5.5**.
- **DeepSeek V4.1 Flash is scored from GPT-5.6 Sol's labels** (see *The judge*).
- **DeepSeek V4.1 Flash (1017) and MiMo v2.6 Flash were generated on NaN with a
  per-run `seed`**, because NaN ignored `caching: false` on 2026-10-19; no other
  row carries a seed. Their labels are a blind judgement by **Claude Opus 5.5**.
  The 1017 version is stated by NaN's operator; the endpoint names none.
- **Qwen 3.6's three monday-004 runs came from NaN, not Helmcode**, which was
  unreachable during generation; the override is recorded in `models.yaml`.

Every field a route did not expose is `null` in its run files, and each closed
row's route and judge is stated in its `models.yaml` entry.

| Overall | Scenarios | Leader | Artefacts |
|---|---|---|---|
| [v0](leaderboard/overall/overall-v0.md) | 001–003 | Qwen 3.8 Flash | frozen |
| [v1](leaderboard/overall/overall-v1.md) | 001–004 | Qwen 3.8 Flash | frozen |
| [v2](leaderboard/overall/overall-v2.md) | 001–005 | Qwen 3.8 Flash — 95.1 | frozen, suite v1.0 |
| [v3](leaderboard/overall/overall-v3.md) – [v3.3](leaderboard/overall/overall-v3.3.md) | 001–005 | see each board | frozen, suites v1.1–v1.4 |
| [v3.4](leaderboard/overall/overall-v3.4.md) | 001–005 | GPT-6 Astra — 98.80 | frozen, suites v1.5–v1.9 |
| [v3.5](leaderboard/overall/overall-v3.5.md) | 001–005 | GPT-6 Astra — 98.80 | frozen, suites v1.10–v1.12 |
| **[v3.6](leaderboard/overall/overall-v3.6.md)** | **001–005** | **GPT-6 Astra — 98.80** | **current, suite v1.13** |

Each release names its scenarios explicitly and pins their prompt hashes, so
adding a scenario later cannot move a number already published. v0, v1, v2 and
v3 are different claims about different scenario sets or suite versions, not
successive corrections of one. A model is ranked only if it has an official
score on *every* scenario in the release.

Adding a **model** to a fixed scenario set is a new suite release plus an
Overall revision — v3.6, v3.7 — and leaves every earlier board byte-frozen. See
[`docs/benchmarking-a-new-model.md`](docs/benchmarking-a-new-model.md) and
[`STATUS.md`](STATUS.md) for the release line.

## What each model is actually good at

Monday Score cannot say what *kind* of work a model handles well.
[`analysis/capability-taxonomy-v0.2.md`](analysis/capability-taxonomy-v0.2.md)
maps all 119 scored criteria onto 22 capabilities and reports coverage,
discrimination and what the suite still does not measure. It changes no score;
nothing in the scoring path reads it.

`monday-002` ships two extra audit artefacts: a
[criterion matrix](leaderboard/monday-002/criterion-matrix.md) covering all 20
criteria across 7 models and 3 runs each, and an
[analysis report](leaderboard/monday-002/analysis.md) with the failure stories
behind the scores. It discriminates far harder than #001: the score spread is
37.0 points against 27.3, and only 21 of 100 points return the same label in
every one of its 21 runs.

`archive/` keeps every superseded battery — earlier prompt hashes, an earlier
output budget, and the calibration drafts of #002 through #005 — separated from the official
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
> repository was produced in a recorded session - by Claude Opus 5 for ten of the
> fifteen board rows, by GPT-5.6 Sol for DeepSeek V4.1 Flash and Claude Opus 5,
> and by Claude Opus 5.5 for Gemini 3.8 Flash, DeepSeek V4.1 Flash (1017) and
> MiMo v2.6 Flash - and written into
> `verdicts/<scenario>/<model>.verdicts.jsonl`. `mondaybench evaluate
> --verdicts` then scores those labels deterministically. **Do not set
> `ANTHROPIC_API_KEY` and do not spend Anthropic API credits on this project** -
> that is a hard project rule, not a preference. The `provider: anthropic` /
> `model_id: claude-opus-5` fields in the evaluator config record *which model
> reasoned about the responses*; they are not an instruction to call an API.

Each scenario has its own official evaluator, `evaluator-opus5-v0.1` through
`evaluator-opus5-v0.5` for monday-001 through monday-005; since suite v1.1 a
per-scenario judge contract (`mondaybench/contract.py`) pins what each one may
change. The others below ship alongside them for calibration and for anyone
without an Anthropic key. They are never mixed in one ranking — that is what
evaluator versioning is for.

**How much the judge moves a score has been measured, not assumed.** Two
independent blind passes over the same 15 responses — same rubric, no access to
each other's labels — give:

| Battery | Monday Score, official judge / second blind judge | Record |
|---|---|---|
| Claude Opus 5 (on the board from v1.10) | 97.10 / **97.07** — 96.9% of criteria agree, κ 0.74, no PASS↔FAIL | [`audits/blind-rejudge/inter-judge/`](audits/blind-rejudge/inter-judge/README.md) |
| DeepSeek V4.1 Flash (on the board) | 93.03 / **94.53** — 317 of 354 criteria agree, largest single-run gap 10.0 | Opus labels in [`experiments/deepseek-v4.1-flash-rerun-v1/blind-verdicts/`](experiments/deepseek-v4.1-flash-rerun-v1/blind-verdicts/); GPT-5.6 Sol labels in `verdicts/monday-00N/deepseek-v4.1-flash-rerun-v1.verdicts.jsonl` |
| DeepSeek V4.1 Flash, reliability prompt (off-board) | 90.33 / 93.47 | stated in [`overall-v3.3.md`](leaderboard/overall/overall-v3.3.md); the second pass's labels are not published |

**Two board rows are scored from the second judge's labels**: DeepSeek V4.1
Flash (GPT-5.6 Sol, 94.53; the Opus judge gives 93.03) and Claude Opus 5
(GPT-5.6 Sol, 97.07; the Opus judge, the same model as the candidate, gives
97.10). Gemini 3.8 Flash (High), DeepSeek V4.1 Flash (1017) and MiMo v2.6 Flash are
scored from blind judgements by Claude Opus 5.5, with no second label set. Every other row is scored by the official Opus
judge. The aggregate can agree while individual runs do not:
on the Opus battery the largest single-run disagreement was 1.5 points, on the
DeepSeek one 10.0. Read the board with that in mind — gaps of one or two points
between adjacent models are not established by this suite.

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


## Reasoning: requested is not delivered

MondayBench keeps two separate facts about every run, and never lets one stand
in for the other:

- **`reasoning_requested`** - the regime the run was *supposed* to belong to,
  taken from the model's effective configuration. A statement of intent.
- **reasoning delivery evidence** - whether the model *actually* generated a
  thinking phase, taken only from the response.

Conflating them cost a published result. `monday-002/qwen3.8-flash/run-002`
scored 66.5 against 93.0 and 100.0 for the same model on the same prompt,
because the provider served a non-thinking path; the run record said
`reasoning_enabled: true` regardless, because that field was copied out of
`models.yaml`.

### Three signals, most direct first

| Evidence | Source |
|---|---|
| `explicit_reasoning_tokens` | the provider counted them in `usage` |
| `explicit_reasoning_stream` | the adapter saw `reasoning_content` / `reasoning` deltas and recorded how many. Structural only - no reasoning content is ever stored |
| `derived_pre_answer_stream` | reconstructed from a run's own TTFT/TTFA, for runs written before the adapter counted stream events |

The evidence kind travels with the verdict, so a reconstructed classification is
never mistaken for something the adapter asserted at the time.

### `reasoning_tokens == 0` does not mean "no reasoning"

**Some providers stream a thinking phase and then report zero reasoning tokens.**
MIMO v2.5 does exactly that: 16-24 seconds of pre-answer stream on monday-001
and 139-162 seconds on monday-002, with `usage.reasoning_tokens: 0` every time.
Trusting the counter alone had it recorded as a non-reasoning model through two
official batteries.

The derived signal is not "the response was slow". `ttft_ms` is set by the first
non-empty reasoning delta **or** the first non-empty content delta and by
nothing else - role-only deltas, `usage` events and `id` events never touch it -
while `ttfa_ms` is set only by the first content delta. A gap between them is
structural proof that reasoning deltas arrived first. A conservative 1-second
threshold still applies: across all 43 official runs the gap is either exactly
0.0 ms or at least 16,500 ms, so the threshold sits in an empty band four orders
of magnitude wide and absorbs rounding rather than tuning a result.

### The four states

| State | Meaning |
|---|---|
| `DELIVERED` | any of the three signals establishes a thinking phase |
| `NOT_DELIVERED` | reasoning was requested and its absence was *positively observed* - a reported zero, or an explicitly empty stream |
| `NOT_REQUESTED` | the configuration does not expect reasoning, and none was seen |
| `UNOBSERVABLE` | reasoning was requested and the provider exposes no reliable signal either way |

Only `NOT_DELIVERED` disqualifies a run. `UNOBSERVABLE` never does: refusing a
run because a provider is quiet about its telemetry would invent the evidence
this rule exists to demand. Delivery is settled before the request flag is
consulted, so a model that demonstrably thought is `DELIVERED` whether or not
the configuration expected it.

## Limitations

Suite v1.13, five scenarios, fifteen models. The full list is in
[`docs/methodology.md`](docs/methodology.md#limitations); the ones that matter
most when reading the board:

- **The top of the board is compressed.** Eight models sit between 91.7 and 98.8,
  GPT-6 Astra scores 100 on three scenarios, and none of the suite's 500 points
  is failed by every model — so the suite carries no evidence about where the
  frontier is.
- **Three judges on one board.** Ten rows are labelled by Claude Opus 5, two by
  GPT-5.6 Sol and one by Claude Opus 5.5 (see *The judge*). Where both label
  sets are on disk, two judges differ by 0.03 and 1.50 points on a Monday Score
  and by up to 10.0 on a single run.
- **Three runs per scenario.** A scenario score rests on three samples, and some
  models move by more than 15 points between runs of the same prompt.
- **Single-turn.** Every scenario is one prompt and one response.
- **English only**, and **office knowledge work** only.
- **Cost, latency and throughput are measured but excluded from the score.**
- **Every input is public**, so future models may have seen it in training.
  There is no held-out set.
- **Not a measure of general intelligence.**

## Layout

```
scenarios/monday-00N/   canonical inputs, rubric, ground truth, FROZEN.yaml
evaluators/             judge configuration, versioned and immutable
verdicts/               recorded judge labels, one file per scenario and model
mondaybench/            the implementation
runs/                   raw model responses (immutable evidence)
evaluations/            scored evaluations, versioned by suite
leaderboard/            scenario boards (v1.13/ is current) and overall/ boards
releases/               one frozen manifest per suite version
taxonomy/, analysis/    capability taxonomy and profiles
audits/, experiments/   cross-judge audits and off-board experiments
archive/                every superseded battery; never deleted
tests/                  offline test suite (no credentials needed)
STATUS.md               where the suite stands, and the release line
```

## License

MIT. The scenario, rubric and ground truth are published as an open benchmark.

The full methodology — why three runs, how a score is computed, the official
evaluator, generation limits and reproduction — is in
[`docs/methodology.md`](docs/methodology.md).
