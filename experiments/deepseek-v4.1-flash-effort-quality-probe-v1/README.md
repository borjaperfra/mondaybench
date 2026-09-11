# deepseek-v4.1-flash-effort-quality-probe-v1

Phase 1b of the `reasoning_effort` investigation. **Not a MondayBench run**, not
a battery, not a leaderboard entry, not judged by any LLM.

## The question

Does `reasoning_effort="high"` change **task quality** on an objective,
deterministic exercise that is hard enough that baseline is **not** saturated?

Phase 1a (`experiments/deepseek-v4.1-flash-effort-probe-v1/`) could not answer
this. Its instrument was saturated: 30/30 correct in both variants, every one of
the 60 responses byte-identical. Gate A there could not have fired whatever the
parameter does. That is the gap this phase exists to close.

What phase 1a did establish, and what carries over as a standing constraint:

- `high` is accepted (HTTP 200) and reasoning delivery was observed in 30/30 of
  both arms.
- No upward shift in reported compute under `high`; median reasoning tokens were
  973 baseline against 474 high, i.e. the opposite direction, and not a finding.
- `prompt_tokens` varied (72/98/151) for byte-identical input, and the group
  predicted reasoning tokens at least as well as the variant did. **So
  reasoning-token differences are not read as causal evidence about effort.**
  This phase re-checks that accounting and says so explicitly either way.
- `reasoning_effort="banana"` is accepted with HTTP 200 and produces
  non-reasoning, wrong output. Already documented; **not repeated here**, since
  nothing in this phase's question depends on it.

Primary metric this time: **success rate**. Not reasoning tokens.

## Phase A - five microtests, designed before any data

Synthetic problems written for this experiment. They borrow the *kind* of
difficulty MondayBench exposes, and none of its content: no scenario, prompt,
source file, ground truth, wording, name or number from MondayBench appears in
any of them.

| id | failure modes under test | answer type |
| --- | --- | --- |
| `mt-01-schedule` | dependency ordering, resource contention, availability windows, deadline feasibility | exact clock time |
| `mt-02-supersession` | supersession of stale instructions, temporal consistency, ownership, eligibility | option letter |
| `mt-03-plan-trap` | a plan that is locally plausible and globally impossible | option letter |
| `mt-04-supported-claim` | preserving uncertainty, refusing an unsupported causal claim | option letter |
| `mt-05-allocation` | constrained allocation under a budget, dependencies, exclusivity, tie-break | exact set of IDs |

Each holds 6 to 9 constraints simultaneously, needs no outside knowledge, no
tools, no style judgement, and has exactly one verifiable answer.

## Phase B - keys proved, then frozen

`verify_keys.py` establishes every answer key mechanically **before any API
call**, and writes `microtests/answer-keys.json` only if all five pass:

- `mt-01` and `mt-05` are solved by **exhaustive search**, which also proves the
  answer is unique - nothing finishes earlier, and no other approved set ties on
  the objective.
- `mt-03` checks each proposed plan against each written rule.
- `mt-02` applies the log's supersessions in order and then evaluates all four
  options, asserting that exactly one survives.
- `mt-04` checks the arithmetic (8.0% and 9.0%) and records why each other
  option is unsupported. That discrimination is a labelled design assertion
  about causal claims, not an arithmetic result.

A wrong key would not produce noise, it would produce a confident wrong
conclusion. Hence the machine proof.

Each prompt is frozen as bytes with its sha256 in `answer-keys.json`. **No
prompt was edited after seeing any response.**

## Phase B scoring - deterministic, no LLM

Every prompt demands a final `ANSWER:` line. `scorers.py` implements the rules,
all fixed in advance, with 26 self-tests:

- markdown decoration is stripped first, so `**ANSWER: D**` is an answer, not a
  parse failure;
- all `ANSWER:` lines are collected; disagreeing values are **UNPARSEABLE**
  rather than resolved by guessing;
- `choice` takes the value's leading option letter when it has one, so
  `ANSWER: D) None of A, B or C` scores D. Without that rule mt-02's *correct*
  option would fail to parse precisely because its text quotes other letters -
  a bias in favour of the wrong answers;
- UNPARSEABLE is always reported separately from INCORRECT.

## Phase C - calibration on baseline only

`reasoning_effort` is never sent during calibration. There is no flag for it and
the call site passes `effort=None` literally, so difficulty cannot be tuned
against the treatment.

Promotion rule, fixed in advance: 5/5 correct is treated as probably saturated,
0/5 or 1/5 as probably too hard, and 2-4/5 earns a top-up to 10 samples. Target
band 50-80%, acceptable band 40-85%. If nothing lands in the acceptable band the
experiment stops and says so - **no new candidate is invented after seeing
results.**

## Selection rule, applied before any `high` sample

1. baseline success rate closest to 65%
2. greater diversity of distinct wrong answers
3. shorter prompt
4. least ambiguous scorer

Recorded in `calibration-result.json`, together with the full ranking.

## Phase D - 20 baseline vs 20 high

New samples; no calibration sample is reused. Randomised, balanced, interleaved
order frozen in `phase-d-config.json` before the first call (seed 31415926).
Bootstrap seed 27182818. `preflight.json` proves `reasoning_effort` is the only
field that differs.

Independent samples: one request each, no conversation state, no best-of-N, no
quality retries. Infrastructure retries only, every attempt recorded.

## Statistics

Success rate is primary. Fisher's exact test (two-sided, exact hypergeometric),
percentile bootstrap for the difference with a recorded seed, Wilson intervals
per arm, odds ratio flagged as uninterpretable when a zero cell forces the
Haldane-Anscombe correction, and a jackknife that asks whether a difference
survives dropping any single sample. Nothing is trimmed.

## Decision gate

- **A**: success rate improves by >= 10 pp, and the effect is not carried by one
  extreme sample or by a parsing asymmetry.
- **B**: below 10 pp, but the exact test or the bootstrap CI suggests a signal
  worth more statistical power.
- Either way the run **stops** and reports. A larger sample is a recommendation,
  never something this phase executes.
- If the prompt-token confound reappears *and* predicts correctness, the outcome
  is STOP because no reasonable causal reading is available.

`reasoning_effort="max"` is outside this phase entirely and is not executed.

## Language discipline

Five things are kept separate: parameter acceptance, observed reasoning
delivery, reported compute, latency, and task quality. Claims are phrased as
observable behaviour. Nothing in this directory asserts anything about the
provider's backend, routing, scheduler or architecture - the data cannot see
those.

## Isolation

Nothing outside this directory is written. No `runs/`, `evaluations/`,
`verdicts/`, `leaderboards/`, `releases/`, no existing DeepSeek battery, not the
reliability experiment, and not phase 1a's directory. Nothing published, nothing
committed.

## Files

| path | what it is |
| --- | --- |
| `microtests/mt-*.txt` | the five frozen prompts, exact bytes |
| `microtests/answer-keys.json` | keys, hashes, and the proof behind each key |
| `verify_keys.py` | the key prover |
| `scorers.py` | deterministic scorers with self-tests |
| `probe_lib.py` | shared request/record machinery |
| `calibrate.py` | phase C, baseline only |
| `calibration-progress.json` | per-candidate calibration counts |
| `calibration-result.json` | the selection rule and the chosen instrument |
| `run_phase_d.py` | preflight, frozen order, execution |
| `analyze_phase_d.py` | statistics and the decision gate |
| `preflight.json` | the pre-call control check for phase D |
| `phase-d-config.json` | frozen order, seeds, request config |
| `raw/calibration.jsonl` | every calibration sample, full detail |
| `raw/phase-d.jsonl` | every phase-D sample, full detail |
| `analysis/phase-d-*` | CSV of observations, summary JSON, readable report |
| `manifest.json` | file inventory with hashes |

`raw/*.jsonl` keeps the full answer text, its sha256, the provider's whole usage
block, request id, finish reason and all timings. Per-event SSE payloads are not
kept: the harness adapter consumes the stream to produce those fields, and
reasoning *content* is never stored anywhere in this project.
