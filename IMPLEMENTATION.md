# MondayBench v0.1 — Technical Specification

**Status:** Implementation-ready  
**Primary scenario:** `monday-001` — *Back to Work*  
**Language:** English  
**License:** Public / open benchmark  
**Goal:** Benchmark how useful an open model is at reconstructing a realistic work situation and deciding what matters now.

---

## 1. Product principle

MondayBench should answer one practical question:

> **Can this model handle your Monday?**

The benchmark must not optimize for academic reasoning puzzles. It evaluates a model on a realistic bundle of workplace information containing:

- Slack messages
- emails
- meeting notes
- a stale task list
- structured metrics
- changing decisions
- obsolete information
- incomplete evidence
- irrelevant noise

The model must reconstruct the current state of the world and produce a useful Monday briefing.

The first release contains one scenario, `monday-001`. The repository must be designed so additional scenarios can be added without changing the evaluator architecture.

---

# 2. Core design rules

1. **Everything is public.**
   - Scenario inputs
   - Prompt
   - Ground truth
   - Rubric
   - Raw model outputs
   - Judge outputs
   - Scoring code
   - Leaderboard

2. **Generation and evaluation are separate.**
   - Raw responses are immutable.
   - Changing the evaluator must not require re-running the benchmark models.

3. **The LLM judge does not invent the scoring rubric.**
   - The rubric is human-authored.
   - The judge only maps a response to predefined labels.

4. **Prefer auditable classifications over holistic scoring.**
   - Use `PASS`, `PARTIAL`, `FAIL`.
   - Never ask the judge: "score this answer from 0–100."

5. **A verbose answer must not automatically score better.**

6. **Unsupported certainty is a failure mode.**
   - Models should be rewarded for recognizing missing information.

7. **Stale information is intentionally present.**
   - The model must reconstruct the latest state, not simply extract high-priority keywords.

8. **The official score measures task quality only.**
   - Cost, latency, TTFT, output tokens, throughput and other economics are recorded separately.

---

# 3. Repository structure

```text
monday-bench/
├── README.md
├── LICENSE
├── pyproject.toml
├── .env.example
├── models.yaml
│
├── mondaybench/
│   ├── __init__.py
│   ├── cli.py
│   ├── config.py
│   ├── scenarios.py
│   ├── prompt_builder.py
│   ├── runner.py
│   ├── evaluator.py
│   ├── judge.py
│   ├── scoring.py
│   ├── leaderboard.py
│   ├── schemas.py
│   ├── pricing.py
│   └── providers/
│       ├── __init__.py
│       ├── base.py
│       └── openai_compatible.py
│
├── scenarios/
│   └── monday-001/
│       ├── scenario.yaml
│       ├── prompt.md
│       ├── slack.md
│       ├── emails.md
│       ├── meetings.md
│       ├── tasks.md
│       ├── metrics.csv
│       ├── ground-truth.yaml
│       └── rubric.yaml
│
├── runs/
│   └── monday-001/
│       └── <model-slug>/
│           ├── run-001.json
│           ├── run-002.json
│           └── run-003.json
│
├── evaluations/
│   └── evaluator-v0.1/
│       └── monday-001/
│           └── <model-slug>/
│               ├── run-001.json
│               ├── run-002.json
│               └── run-003.json
│
├── leaderboard/
│   ├── leaderboard.json
│   └── leaderboard.csv
│
└── tests/
    ├── test_prompt_builder.py
    ├── test_scoring.py
    ├── test_schemas.py
    └── fixtures/
```

---

# 4. Scenario metadata

Create `scenarios/monday-001/scenario.yaml`.

```yaml
id: monday-001
name: Back to Work
benchmark_version: "0.1"
language: en

context:
  current_time: "Monday 09:07"
  last_active: "Wednesday 17:30"
  company_type: "B2B SaaS"
  role: "Product/Growth lead"

sources:
  - slack.md
  - emails.md
  - meetings.md
  - tasks.md
  - metrics.csv

official_runs: 3
```

The source order is part of the benchmark specification and must remain fixed for a scenario version.

---

# 5. Prompt construction

`prompt.md` contains placeholders:

```markdown
# Monday #001 — Back to Work

It is Monday, 09:07.

You have been away from work since Wednesday at 17:30.

While you were away, your team continued working and you have accumulated Slack messages, emails, meeting notes, tasks, and company metrics.

Review all the information provided and prepare your Monday briefing.

Tell me:

1. What happened while I was away.
2. What requires my attention today, ordered by priority.
3. What is important to know but does not require action from me.
4. What is unclear or requires more information.

Be concise and practical.

Do not assume information that is not provided.

---

## Slack

{{SLACK}}

---

## Emails

{{EMAILS}}

---

## Meeting notes

{{MEETINGS}}

---

## Tasks

{{TASKS}}

---

## Company metrics

{{METRICS}}
```

`prompt_builder.py` must:

1. Read `prompt.md`.
2. Read every scenario source as UTF-8.
3. Replace placeholders exactly.
4. Return the final prompt string.
5. Compute a SHA-256 hash of the final prompt.
6. Store that hash with every run.

No hidden system prompt should contain benchmark hints.

Recommended system message:

```text
You are a helpful assistant.
```

If a provider does not support system messages, omit it and record that fact in metadata.

---

# 6. Model configuration

Root file: `models.yaml`

Example:

```yaml
models:

  deepseek-v4-flash:
    display_name: "DeepSeek V4 Flash"
    provider: helmcode
    api_style: openai_compatible
    model_id: "deepseek-v4-flash"
    base_url_env: HELMCODE_BASE_URL
    api_key_env: HELMCODE_API_KEY

    generation:
      temperature: 0
      max_output_tokens: 4000

    capabilities:
      reasoning: false

    pricing:
      input_per_million_usd: null
      output_per_million_usd: null

  qwen-3.8-flash:
    display_name: "Qwen 3.8 Flash"
    provider: helmcode
    api_style: openai_compatible
    model_id: "qwen-3.8-flash"
    base_url_env: HELMCODE_BASE_URL
    api_key_env: HELMCODE_API_KEY

    generation:
      temperature: 0
      max_output_tokens: 4000

    capabilities:
      reasoning: false

    pricing:
      input_per_million_usd: null
      output_per_million_usd: null
```

Do not hardcode credentials.

`.env.example`:

```dotenv
HELMCODE_BASE_URL=
HELMCODE_API_KEY=

JUDGE_BASE_URL=
JUDGE_API_KEY=
JUDGE_MODEL=
```

---

# 7. Provider abstraction

Use one small interface.

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class GenerationResult:
    text: str
    input_tokens: int | None
    output_tokens: int | None
    reasoning_tokens: int | None
    ttft_ms: float | None
    total_latency_ms: float
    provider_request_id: str | None
    raw_usage: dict[str, Any]

class ModelProvider:
    def generate(
        self,
        *,
        model_id: str,
        system_prompt: str | None,
        user_prompt: str,
        generation_config: dict,
    ) -> GenerationResult:
        raise NotImplementedError
```

Implement OpenAI-compatible endpoints first.

Do not build separate provider classes unless an API actually requires different behavior.

---

# 8. Benchmark run schema

Every raw generation is immutable and stored as:

`runs/<scenario>/<model>/run-XXX.json`

Schema:

```json
{
  "schema_version": "1",
  "benchmark_version": "0.1",
  "scenario_id": "monday-001",
  "scenario_prompt_sha256": "...",

  "run_id": "monday-001__deepseek-v4-flash__001",
  "run_number": 1,

  "model": {
    "slug": "deepseek-v4-flash",
    "display_name": "DeepSeek V4 Flash",
    "provider": "helmcode",
    "model_id": "deepseek-v4-flash"
  },

  "generation": {
    "temperature": 0,
    "max_output_tokens": 4000,
    "reasoning_enabled": false
  },

  "timestamp_utc": "2026-08-27T14:00:00Z",

  "usage": {
    "input_tokens": 6231,
    "output_tokens": 721,
    "reasoning_tokens": null
  },

  "performance": {
    "ttft_ms": 312,
    "total_latency_ms": 4182,
    "tokens_per_second": 172.4
  },

  "economics": {
    "input_cost_usd": null,
    "output_cost_usd": null,
    "total_cost_usd": null
  },

  "response": "RAW MODEL RESPONSE HERE",

  "provider_metadata": {
    "request_id": null
  }
}
```

The runner must refuse to overwrite an existing run unless the user explicitly passes:

```bash
--overwrite
```

Official published runs should never be overwritten after publication.

---

# 9. CLI

Use Typer or argparse. Typer is preferred for ergonomics.

## List scenarios

```bash
mondaybench scenarios
```

Expected:

```text
monday-001    Back to Work
```

## List configured models

```bash
mondaybench models
```

## Run one model

```bash
mondaybench run \
  --scenario monday-001 \
  --model deepseek-v4-flash \
  --runs 3
```

## Run all configured models

```bash
mondaybench run \
  --scenario monday-001 \
  --all-models \
  --runs 3
```

## Dry run

```bash
mondaybench run \
  --scenario monday-001 \
  --model deepseek-v4-flash \
  --dry-run
```

Dry run prints:

- resolved model
- provider
- prompt hash
- prompt token estimate if available
- generation parameters

It must not call the API.

## Evaluate one model

```bash
mondaybench evaluate \
  --scenario monday-001 \
  --model deepseek-v4-flash \
  --evaluator evaluator-v0.1
```

## Evaluate all available runs

```bash
mondaybench evaluate \
  --scenario monday-001 \
  --all-models \
  --evaluator evaluator-v0.1
```

## Build leaderboard

```bash
mondaybench leaderboard \
  --scenario monday-001 \
  --evaluator evaluator-v0.1
```

## Full pipeline

```bash
mondaybench benchmark \
  --scenario monday-001 \
  --all-models \
  --runs 3 \
  --evaluator evaluator-v0.1
```

This command performs:

```text
validate scenario
→ run models
→ save raw generations
→ evaluate
→ calculate scores
→ build leaderboard
```

---

# 10. Evaluation philosophy

The judge must evaluate **atomic criteria**, not the entire answer holistically.

Allowed outputs:

```text
PASS
PARTIAL
FAIL
```

The judge must also return evidence from the response.

Never allow the judge to assign points.

Points are assigned deterministically by `scoring.py`.

---

# 11. Rubric format

Upgrade `rubric.yaml` so every criterion includes explicit PASS/PARTIAL/FAIL definitions.

Example:

```yaml
version: "0.1"

dimensions:

  action_detection:
    max_points: 25

    criteria:

      - id: contoso_action
        points:
          pass: 8
          partial: 4
          fail: 0

        pass_definition: >
          Clearly identifies resolving the Contoso data-retention
          question before 11:00 Monday as the highest-priority action.

        partial_definition: >
          Identifies Contoso as requiring action today but misses either
          the 11:00 deadline, the renewal-blocking nature of the issue,
          or fails to treat it as the top priority.

        fail_definition: >
          Does not identify the action, materially misunderstands it,
          or treats it as already resolved.

      - id: umbrella_action
        points:
          pass: 7
          partial: 3.5
          fail: 0

        pass_definition: >
          Identifies Umbrella's metrics as a serious unexplained anomaly
          that should be investigated today without claiming a cause.

        partial_definition: >
          Notices the anomaly but either under-prioritizes it or describes
          the need for investigation incompletely.

        fail_definition: >
          Misses Umbrella or presents an unsupported root cause as established.

      - id: churn_action
        points:
          pass: 6
          partial: 3
          fail: 0

        pass_definition: >
          Identifies that enterprise churn should be investigated or broken
          down today ahead of Tuesday's board meeting.

        partial_definition: >
          Notes churn as important but does not connect it to work required
          before the board meeting.

        fail_definition: >
          Misses the churn issue or claims the known cancellations fully
          explain the increase.

      - id: analytics_action
        points:
          pass: 4
          partial: 2
          fail: 0

        pass_definition: >
          Correctly treats Wednesday as the release date and any readiness
          check as lower priority than today's critical work.

        partial_definition: >
          Correctly understands Wednesday but gives disproportionate priority
          to the release.

        fail_definition: >
          Treats Analytics v2 as launching Monday or gives the user ownership
          of the launch email.
```

Use the same explicit pattern for all criteria.

---

# 12. Official scoring dimensions

Monday #001 uses:

| Dimension | Max |
|---|---:|
| Action detection | 25 |
| State reconstruction | 25 |
| Prioritization | 15 |
| Data reasoning | 15 |
| Uncertainty | 10 |
| Noise resistance | 10 |
| **Base score** | **100** |

Additional global penalties can reduce the final score.

Final score:

```text
max(0, base_score - penalties)
```

Maximum total penalties:

```text
20 points
```

---

# 13. State reconstruction criteria

`25 points`, five criteria × 5.

### `acme_resolved`

PASS:
- Clearly states that the Acme incident is resolved/recovered.
- Does not frame it as an active operational problem.

PARTIAL:
- Mentions recovery but still suggests light monitoring/follow-up as if uncertainty remains.

FAIL:
- Treats Acme as an active incident or a Monday investigation priority.

### `release_wednesday`

PASS:
- States Analytics v2 is now scheduled for Wednesday.

PARTIAL:
- Implies a delay but does not identify Wednesday.

FAIL:
- Says it launches Monday.

### `contoso_blocked`

PASS:
- Correctly says renewal/signature can be delayed or blocked pending retention confirmation.

PARTIAL:
- Identifies an outstanding legal question but misses the signature/approval consequence.

FAIL:
- Treats renewal as fully done or commercially blocked for another reason.

### `launch_email_julia`

PASS:
- States Julia owns the launch email or that no action is required from the user.

PARTIAL:
- Does not assign it to the user but misses Julia's ownership.

FAIL:
- Tells the user to prepare/write the launch email.

### `pricing_confidential`

PASS:
- States proposed pricing is not final and must not be shared externally.

PARTIAL:
- States it is not final but does not recognize the sharing restriction.

FAIL:
- Recommends sending draft/new pricing to Initech.

---

# 14. Prioritization criteria

`15 points`.

### `contoso_first` — 6

PASS:
- Explicitly first/highest priority.

PARTIAL:
- Included among the highest-priority items but not clearly first.

FAIL:
- Under-prioritized, omitted, or presented as non-urgent.

### `umbrella_and_churn_high` — 5

PASS:
- Both are prominent actionable items for today after Contoso.

PARTIAL:
- Only one is appropriately prioritized or both appear but are buried.

FAIL:
- Neither receives meaningful attention.

### `no_false_priorities` — 4

PASS:
- No resolved/delegated/noise item is elevated over legitimate work.

PARTIAL:
- One unnecessary item receives moderate priority.

FAIL:
- Multiple stale/noise items appear as priorities.

---

# 15. Data reasoning criteria

`15 points`.

### `umbrella_detected` — 5

PASS:
- Identifies Umbrella as the customer with anomalous metrics.

PARTIAL:
- Notices poor metrics but does not clearly connect the anomaly to Umbrella.

FAIL:
- Misses it.

### `umbrella_metrics` — 4

PASS:
- Uses at least two relevant supporting signals correctly, such as:
  - 163 API errors
  - 1821ms p95 latency
  - -41% 7-day usage
  - relatively low request count compared with Stark

PARTIAL:
- Uses one correct signal.

FAIL:
- Gives incorrect numbers or no evidence.

### `churn_numbers` — 3

PASS:
- Correctly identifies 3.1% → 4.4%.

PARTIAL:
- Correctly states churn increased but omits the figures.

FAIL:
- Gives incorrect movement or says churn decreased.

### `no_friday_conversion_claim` — 3

PASS:
- Explicitly says Friday conversion cannot be established from provided metrics, if discussing it.

PARTIAL:
- Avoids making a claim but does not explicitly flag the lack of data.

FAIL:
- Claims Friday conversion fell based on supplied evidence.

---

# 16. Uncertainty criteria

`10 points`.

### `umbrella_unknown_cause` — 4

PASS:
- Explicitly distinguishes anomaly from root cause.

PARTIAL:
- Does not invent a cause but fails to express uncertainty.

FAIL:
- Claims a cause not supported by the material.

### `friday_conversion_unknown` — 3

PASS:
- Explicitly says it cannot be verified from the provided data.

PARTIAL:
- Does not repeat the conversion claim but does not flag uncertainty.

FAIL:
- Treats the Slack speculation as established fact.

### `churn_causality_unknown` — 3

PASS:
- States the two known cancellations may contribute but do not establish full causality.

PARTIAL:
- Mentions the cancellations without claiming they fully explain churn.

FAIL:
- Says Pied Piper and Hooli explain the increase.

---

# 17. Noise resistance

Start at `10`.

Deduct `2` for each false action, to minimum `0`.

False-action classes:

```yaml
noise_resistance:
  starting_points: 10
  deduction_per_false_action: 2
  minimum_points: 0

  false_actions:
    - id: lunch
      description: Treating the lunch discussion as relevant.

    - id: icon
      description: Re-opening or prioritizing the resolved icon discussion.

    - id: partner_sync
      description: Treating Friday's completed partner sync as upcoming.

    - id: launch_email
      description: Assigning the launch email to the user.

    - id: acme_active
      description: Treating Acme investigation as an active Monday task.

    - id: pricing_send
      description: Treating sending proposed Enterprise pricing as a valid task.
```

A single sentence can trigger more than one false-action category only when it clearly contains distinct actions.

---

# 18. Global penalties

Penalties must be evaluated separately from normal criteria.

## Material hallucination

`-5 each`, subject to total global penalty cap.

Definition:

> A factual claim that is materially relevant to the briefing but unsupported by the supplied evidence.

Examples:

- inventing a Contoso legal approval
- inventing the cause of Umbrella's anomaly
- claiming a specific Friday conversion percentage

Do not penalize harmless wording differences or reasonable summaries.

## Prohibited action

`-10 each`

Definition:

> Recommending an action explicitly contradicted or prohibited by the current state.

Examples:

- send proposed Enterprise pricing to Initech
- write the launch email despite Julia taking ownership

## Major contradiction

`-5 each`

Example:

> "Acme is resolved" followed by "Your first priority is to investigate the active Acme outage."

Total global penalties are capped at 20 points.

---

# 19. Judge configuration

Create an evaluator config:

`evaluators/evaluator-v0.1.yaml`

```yaml
id: evaluator-v0.1

judge:
  provider: openai_compatible
  base_url_env: JUDGE_BASE_URL
  api_key_env: JUDGE_API_KEY
  model_env: JUDGE_MODEL

generation:
  temperature: 0
  max_output_tokens: 1000

behavior:
  evaluate_atomic_criteria: true
  require_evidence: true
```

The exact judge model used in an official evaluation must be stored in every evaluation JSON.

Do not silently change the judge model under the same evaluator version.

If the judge model changes, create `evaluator-v0.2`.

---

# 20. Atomic judge prompt

For each rubric criterion:

```text
You are evaluating a model response for MondayBench.

Your job is NOT to judge writing quality and NOT to assign a numeric score.

Evaluate only the criterion below.

SCENARIO GROUND TRUTH RELEVANT TO THIS CRITERION:
{relevant_ground_truth}

CRITERION:
{criterion}

PASS DEFINITION:
{pass_definition}

PARTIAL DEFINITION:
{partial_definition}

FAIL DEFINITION:
{fail_definition}

MODEL RESPONSE:
{model_response}

Return valid JSON only:

{
  "result": "PASS" | "PARTIAL" | "FAIL",
  "evidence": "short quote or concise description of the relevant part of the response",
  "reason": "one-sentence explanation"
}

Rules:

- Judge only what is present in the model response.
- Do not give credit for facts the response does not state or clearly imply.
- Do not penalize style, brevity, formatting, or wording.
- Do not require exact phrasing.
- If the response is ambiguous between two labels, choose the lower label.
```

The evaluator should pass only relevant ground-truth facts for that criterion, not the entire answer key when unnecessary.

---

# 21. Noise judge prompt

Evaluate all false-action categories in one call if desired:

```text
You are evaluating a MondayBench response for false or unnecessary actions.

For each category, determine whether the model presents it as something the user
should actively do now.

Do not mark an item if the model merely mentions it as completed, resolved,
delegated, historical, or non-actionable.

CATEGORIES:
{categories}

MODEL RESPONSE:
{response}

Return JSON only:

{
  "items": [
    {
      "id": "acme_active",
      "triggered": false,
      "evidence": null
    }
  ]
}
```

---

# 22. Penalty judge prompt

```text
You are checking a MondayBench response for serious factual failures.

Ground truth:
{ground_truth}

Model response:
{response}

Identify only clear cases of:

1. MATERIAL_HALLUCINATION
2. PROHIBITED_ACTION
3. MAJOR_CONTRADICTION

Be conservative. Do not penalize omissions, style, imprecision that is already
captured by the rubric, or reasonable paraphrases.

Return valid JSON only:

{
  "violations": [
    {
      "type": "MATERIAL_HALLUCINATION",
      "evidence": "...",
      "reason": "..."
    }
  ]
}
```

`scoring.py` converts violations to points.

---

# 23. Evaluation result schema

Store:

`evaluations/<evaluator>/<scenario>/<model>/run-XXX.json`

Example:

```json
{
  "schema_version": "1",
  "evaluator_id": "evaluator-v0.1",
  "scenario_id": "monday-001",
  "run_id": "monday-001__deepseek-v4-flash__001",

  "judge": {
    "provider": "...",
    "model_id": "...",
    "temperature": 0
  },

  "dimensions": {
    "action_detection": {
      "score": 21.5,
      "max_score": 25
    },
    "state_reconstruction": {
      "score": 25,
      "max_score": 25
    },
    "prioritization": {
      "score": 11,
      "max_score": 15
    },
    "data_reasoning": {
      "score": 15,
      "max_score": 15
    },
    "uncertainty": {
      "score": 8,
      "max_score": 10
    },
    "noise_resistance": {
      "score": 10,
      "max_score": 10
    }
  },

  "criteria": {
    "contoso_action": {
      "result": "PASS",
      "points_awarded": 8,
      "points_possible": 8,
      "evidence": "...",
      "reason": "..."
    }
  },

  "penalties": {
    "items": [
      {
        "type": "MATERIAL_HALLUCINATION",
        "points": -5,
        "evidence": "...",
        "reason": "..."
      }
    ],
    "total": -5
  },

  "base_score": 90.5,
  "final_score": 85.5
}
```

Scores may be fractional.

Public display can round to one decimal.

---

# 24. Aggregating runs

Official scenario score for a model:

```text
mean(final_score across official runs)
```

For 3 runs:

```text
scores = [91, 87, 89]
official_score = 89.0
```

Also calculate:

- minimum
- maximum
- range
- standard deviation

Example public representation:

```text
89.0 / 100
Runs: 87.0–91.0
σ: 1.63
```

Do not drop the worst run.

Do not use best-of-N.

---

# 25. Model-level leaderboard schema

`leaderboard/leaderboard.json`

```json
{
  "benchmark_version": "0.1",
  "scenario": "monday-001",
  "evaluator": "evaluator-v0.1",
  "generated_at": "...",

  "models": [
    {
      "rank": 1,
      "model_slug": "example-model",
      "display_name": "Example Model",

      "score": {
        "mean": 92.7,
        "min": 91,
        "max": 94,
        "stddev": 1.25,
        "runs": 3
      },

      "dimensions": {
        "action_detection": 23.3,
        "state_reconstruction": 24.7,
        "prioritization": 13.0,
        "data_reasoning": 14.7,
        "uncertainty": 9.0,
        "noise_resistance": 10.0
      },

      "performance": {
        "mean_total_latency_ms": 8450,
        "mean_ttft_ms": 410,
        "mean_output_tokens": 682
      },

      "economics": {
        "mean_cost_usd": 0.041
      }
    }
  ]
}
```

CSV should include a flat version of the same useful fields.

---

# 26. Cost calculation

When public prices are configured:

```python
input_cost = input_tokens / 1_000_000 * input_price
output_cost = output_tokens / 1_000_000 * output_price
total_cost = input_cost + output_cost
```

If reasoning tokens have separate pricing, support that field.

If price is unknown:

```json
"total_cost_usd": null
```

Never estimate silently.

Record pricing source/version manually in `models.yaml` or a future `pricing.yaml`.

Cost does **not** affect Monday Score.

---

# 27. Performance metrics

Where the API makes them available:

- `input_tokens`
- `output_tokens`
- `reasoning_tokens`
- `ttft_ms`
- `total_latency_ms`
- `tokens_per_second`

`tokens_per_second` should preferably describe generated output throughput:

```text
output_tokens / generation_duration_seconds
```

If streaming timestamps are unavailable, leave TTFT null.

Do not fabricate performance values.

---

# 28. Deterministic checks

For v0.1 the judge remains the primary semantic evaluator, but implement lightweight deterministic sanity checks.

Examples:

- detect if `11:00` appears near `Contoso`
- detect whether `3.1` and `4.4` appear
- detect `163`, `1821`, `-41` near `Umbrella`
- detect explicit `Wednesday`
- detect explicit `Julia`

These checks should **not directly replace semantic scoring yet**.

Use them as:

1. evaluator debugging information;
2. warnings when deterministic evidence strongly disagrees with the judge.

Example:

```text
WARNING:
judge marked umbrella_metrics = FAIL
but deterministic matcher found 163 and 1821 within Umbrella context.
```

This will help catch judge mistakes during calibration.

---

# 29. Validation

Implement:

```bash
mondaybench validate --scenario monday-001
```

Checks:

- all required files exist;
- YAML parses;
- rubric points sum correctly;
- dimension maximums sum to 100;
- every criterion ID is unique;
- every referenced ground-truth key exists;
- every placeholder in prompt is resolved;
- final prompt contains no unresolved `{{...}}`;
- scenario hash can be generated;
- models config parses;
- no secrets are committed.

Return non-zero exit code on validation failure.

---

# 30. Scenario versioning

A benchmark scenario must be immutable after official publication.

If scenario content changes materially:

```text
monday-001-v2
```

or bump benchmark version according to repository convention.

Do not change input text while continuing to publish scores under the old scenario identifier.

Prompt hash gives an additional integrity check.

---

# 31. Evaluation versioning

Evaluator changes are separate from scenario changes.

Examples:

```text
evaluator-v0.1
evaluator-v0.2
```

A new evaluator can re-score existing raw responses.

Leaderboard must always specify evaluator version.

Never combine scores generated by different evaluator versions in one official ranking.

---

# 32. Calibration phase

Before publishing MondayBench v0.1:

Run exactly one non-official generation from:

1. one strong frontier/open model;
2. one strong Flash/smaller model;
3. one clearly weaker or much smaller model.

Purpose:

- validate difficulty;
- inspect ambiguity;
- inspect whether the judge behaves sensibly;
- find accidental contradictions;
- find rubric criteria that are too easy or impossible;
- inspect verbosity;
- inspect score spread.

Do **not** tune the benchmark to force predetermined model rankings.

Useful heuristic only:

```text
strong model: roughly 90–97
good model: roughly 75–90
smaller model: roughly 50–80
```

This is not a target distribution.

If all models score around 95+, improve discrimination.

If all models fail badly, inspect whether the scenario or rubric is unnatural.

---

# 33. Manual evaluator audit

For the first official release, manually inspect every criterion label for the calibration runs.

After the benchmark is stable:

- judge does first-pass evaluation;
- human reviewer checks only suspicious / disputed cases;
- raw judge reasoning fields remain public.

Create optional flag:

```bash
--review
```

that generates a concise review file containing:

- non-PASS criteria;
- penalties;
- judge/deterministic disagreements;
- evidence excerpts.

Goal: evaluating a newly released model should require roughly 10 minutes of human review, not 30–60 minutes of manual grading.

---

# 34. Failure handling

If a model API errors:

Store an attempt metadata file separately or log it, but do not create a valid benchmark run.

Retry policy:

- maximum 2 API retries for transient network/5xx errors;
- exponential backoff;
- do not retry content responses because they score badly;
- do not retry a valid truncated response unless the provider itself reports an API failure.

If a model hits `max_output_tokens`, record:

```json
"finish_reason": "length"
```

and evaluate the response as returned.

Do not give it a free re-run unless the benchmark configuration itself was invalid.

---

# 35. Official execution protocol

Every official model is evaluated using:

- same scenario;
- same prompt;
- same source order;
- same number of runs;
- documented generation settings;
- same evaluator version;
- no hidden per-model prompt changes.

If a model requires API-specific parameters, document them in `models.yaml`.

The benchmark should aim for the best standard API experience, not artificially cripple every model into identical internals.

---

# 36. Reasoning policy

For v0.1:

> Use each model's standard/recommended API mode configured publicly in `models.yaml`.

Record:

```yaml
capabilities:
  reasoning: true
```

and generation-specific reasoning controls if applicable.

Do not compare a reasoning-enabled run and a non-reasoning run under the same model slug.

Use distinct variants if necessary:

```text
model-x
model-x-thinking
```

This enables future categories such as:

- MondayBench Standard
- MondayBench Fast

but do not create these categories in v0.1.

---

# 37. Public model page data

The output format should support eventually rendering:

```text
DeepSeek V4 Flash

MONDAY SCORE
89.0 / 100

Actions          23 / 25
State            22 / 25
Prioritization   13 / 15
Data             15 / 15
Uncertainty       8 / 10
Noise             8 / 10

Runs: 87–91
Cost/run: $0.018
Latency: 4.2s
```

Also derive:

### What it missed

Every criterion graded `PARTIAL` or `FAIL`.

### What it got wrong

Every triggered penalty or false action.

### Full answer

Raw response exactly as generated.

Do not generate marketing conclusions inside the evaluator. Those belong to presentation logic.

---

# 38. README minimum

README should explain:

## What MondayBench is

> A practical benchmark for testing whether an AI model can reconstruct a messy workplace situation and decide what matters.

## Why it exists

Traditional benchmarks often test isolated capabilities. MondayBench tests multiple everyday capabilities together in one realistic task.

## What the model sees

- Slack
- Email
- Meetings
- Tasks
- Metrics

## What is scored

- action detection
- state reconstruction
- prioritization
- data reasoning
- uncertainty
- noise resistance

## Reproducibility

Include exact CLI commands.

## Transparency

State clearly that prompts, raw outputs, evaluator decisions and scoring logic are public.

## Limitations

MondayBench #001:

- is one scenario;
- is English-only;
- reflects office/knowledge-work tasks;
- uses an LLM judge for semantic classification;
- should not be treated as general intelligence measurement.

---

# 39. Testing

At minimum:

## `test_scoring.py`

Test:

- PASS/PARTIAL/FAIL mapping;
- fractional points;
- penalty cap;
- final score cannot fall below zero;
- dimension totals;
- noise deductions.

## `test_prompt_builder.py`

Test:

- all placeholders replaced;
- deterministic prompt hash;
- source ordering;
- UTF-8.

## `test_schemas.py`

Validate fixture run and evaluation JSON.

## Judge parsing

Test malformed outputs:

- markdown fences around JSON;
- invalid enum;
- missing fields;
- extra text.

Implement one JSON repair/retry attempt for judge-format failures.

Never silently invent missing results.

---

# 40. Implementation milestones

## Milestone 1 — Core repository

Deliver:

- project structure
- config loader
- scenario loader
- prompt builder
- schema models
- CLI skeleton
- validation

Acceptance:

```bash
mondaybench validate --scenario monday-001
```

passes.

---

## Milestone 2 — Model runner

Deliver:

- OpenAI-compatible provider
- single-model execution
- all-model execution
- immutable raw run files
- token/latency metadata
- prompt hashes

Acceptance:

```bash
mondaybench run --scenario monday-001 --model <model> --runs 1
```

creates a valid run JSON.

---

## Milestone 3 — Evaluator

Deliver:

- rubric parser
- atomic criterion judge
- noise judge
- penalty judge
- deterministic sanity checks
- evaluation JSON

Acceptance:

```bash
mondaybench evaluate --scenario monday-001 --model <model>
```

creates an auditable evaluation.

---

## Milestone 4 — Scoring and leaderboard

Deliver:

- score aggregation
- run statistics
- leaderboard JSON
- leaderboard CSV
- terminal leaderboard

Acceptance:

```bash
mondaybench leaderboard --scenario monday-001
```

prints and writes ranking.

---

## Milestone 5 — Calibration

Run:

- 3 model tiers
- one run each

Manually inspect:

- model outputs;
- all judge decisions;
- deterministic disagreements;
- penalty decisions;
- score spread.

Fix only benchmark/evaluator defects, not results that are merely surprising.

---

## Milestone 6 — Official v0.1

Run selected models 3× each.

Suggested initial battery:

- DeepSeek V4 Flash
- Qwen 3.8 Flash
- GLM 5.3 Flash
- GLM 5.3
- Kimi K3

For every model publish:

- three raw runs;
- three evaluations;
- aggregate score;
- score range;
- per-dimension score;
- cost if known;
- latency if measurable.

---

# 41. Claude Code implementation brief

The following can be used as the implementation instruction.

---

## Build request

Build `monday-bench` v0.1 according to this specification.

Prioritize:

1. simplicity;
2. reproducibility;
3. auditable outputs;
4. clean schemas;
5. easy addition of future scenarios and models.

Do not build:

- a web frontend;
- a database;
- authentication;
- a hosted service;
- RAG;
- tool-calling;
- agent loops;
- hidden prompts;
- complex abstractions for providers we do not yet use.

Use Python 3.12+.

Preferred dependencies:

- `typer`
- `pydantic`
- `pyyaml`
- `httpx`
- official OpenAI SDK only if it materially simplifies OpenAI-compatible calls
- `rich` for CLI output if useful
- `pytest`

Keep the provider abstraction minimal.

Treat all files in `runs/` as immutable benchmark evidence.

The evaluator must never directly assign a 0–100 score using an LLM.

The evaluator classifies explicit rubric criteria as `PASS`, `PARTIAL`, or `FAIL`, and deterministic Python code converts those labels into points.

Implement the project in milestones and ensure tests pass after each milestone.

Before completing:

```bash
pytest
mondaybench validate --scenario monday-001
```

must pass.

Document exact commands for:

```bash
mondaybench run
mondaybench evaluate
mondaybench leaderboard
mondaybench benchmark
```

Do not change scenario content or scoring definitions unless required to fix a clear internal inconsistency. If one is found, report it explicitly.

---

# 42. Definition of done for MondayBench v0.1

v0.1 is complete when:

- `monday-001` is versioned and validated;
- at least 5 models can be configured;
- each model can be run 3× from one CLI command;
- raw responses are stored immutably;
- all rubric criteria are evaluated atomically;
- evidence is stored for every judge classification;
- global penalties are auditable;
- evaluator version is stored;
- model score is the mean of the 3 runs;
- run range and standard deviation are generated;
- leaderboard JSON and CSV are created;
- cost/latency metadata is included when available;
- every public score can be traced back to raw output → criterion decisions → deterministic score.

The benchmark is successful if a reader can answer both:

> **Which model scored better?**

and:

> **Why did it score better?**
