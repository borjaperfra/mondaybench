# deepseek-v4.1-flash-context-density-probe-v1

Phase 1c. **Not a MondayBench run.** No treatment is sent: `reasoning_effort` is
absent from every request in this phase. Nothing is published or committed.

## The hypothesis being instrumented

DeepSeek V4.1 Flash may solve constraint, dependency, supersession and
allocation problems reliably when they arrive **compact**, and lose reliability
when the same constraints are **dispersed** through a larger context.

Two readings to separate:

- **H1, reasoning deficit** - it cannot resolve the constraints.
- **H2, constraint persistence under context** - it resolves them locally, and
  loses reliability when it has to locate, reconcile and hold them across
  distance.

Phase 1b is evidence against H1: 24 of 24 scored responses correct across five
short microtests covering dependency ordering, supersession, ownership, global
plan feasibility, unsupported conclusions and constrained allocation. Compute
rose with difficulty; errors did not appear. (One allocation run spent its whole
32,000-token budget on reasoning and returned nothing. It is **not** used to
select anything in this phase.)

So this phase varies **context density**, not logical difficulty.

## One problem, three presentations

A single synthetic problem - a one-day platform cutover with seven pieces of
work - rendered at three densities. Not three puzzles: three presentations of
the same instance, with the same answer.

| level | bytes | anchors | anchor span | mean gap between anchors |
| --- | --- | --- | --- | --- |
| compact | 2,341 | 32/32 | 2,138 chars | 69 chars |
| medium | 10,105 | 32/32 | 8,481 chars | 274 chars |
| dense | 21,297 | 32/32 | 18,187 chars | 587 chars |

Answer, identical in all three: **16:00**.

### The logical problem

Seven tasks with fixed durations on a chain with one branch; three people with
availability windows; two tasks contending for one exclusive resource; one task
restricted to a named person by credential; three facts superseded by later
updates; one optional item that would consume the contended resource; one alarm
that a later note explains away; one open question that must stay open.

The reasoning is identical at every level. What changes is how far apart the
facts sit and how much plausible irrelevant material surrounds them - including
the distance between each stale fact and the update that supersedes it:

| superseded fact | compact | medium | dense |
| --- | --- | --- | --- |
| index rebuild owner | 758 chars | 4,127 | 12,500 |
| Nadia's availability | 970 | 4,560 | 10,290 |
| permissions sync ordering | 198 | 1,926 | 12,992 |
| rehearsal alarm | 56 | 1,674 | 8,518 |

### Provenance

Entirely new. No MondayBench scenario, prompt, source file, ground truth,
wording, name or number appears anywhere in it. The failure-mode *classes* are
reproduced; none of the content is.

## The answer is proved, not asserted

`solve_and_verify.py` searches exhaustively on a 15-minute grid - sound because
every duration and every window boundary is a whole multiple of 15 - scanning
completion limits upward, so the first feasible limit **is** the minimum. It
records a witness schedule and confirms nothing finishes 15 minutes earlier.

It also records what a model gets wrong by dropping exactly one constraint,
which makes the instrument's failure modes legible:

| constraint dropped | answer produced |
| --- | --- |
| the superseded ordering update | 15:45 |
| the resource exclusivity | 15:45 |
| the credential restriction | 15:45 |
| the stale owner used instead of the update | no feasible schedule |
| the stale availability window used instead of the update | 16:00 (not binding) |

The last row is worth stating plainly: one of the four supersessions does not
change the answer. It is still a fact that has to be reconciled, but a model
that misses it is not penalised. That is recorded in the audit rather than
hidden.

## Equivalence is a checked property, not a claim

`equivalence_audit.py` enforces two invariants and refuses to freeze the prompts
if either breaks:

1. **Every one of the 32 anchor sentences appears exactly once in every level,
   character for character.** No level is missing a relevant fact, has an extra
   one, or paraphrases one.
2. **Every occurrence of a protected term - the seven task names, the three
   people, the shared resource, the optional item, the word for the exercise -
   lies inside an anchor.** So no filler sentence in any level can state, imply,
   weaken or contradict a fact about the problem. Filler is structurally
   incapable of touching it.

Verdict: **CLEAN**, 0 violations at all three levels.

An asymmetry the audit caught before any API call: in the first draft of
`medium` the note explaining the rehearsal alarm appeared *before* the alarm,
where the other two levels had it after. It changed no answer, but it was a
presentation difference beyond density, so it was fixed and the prompts were
re-frozen.

## Scoring

Deterministic, no LLM judge, 23 self-tests. The rules are phase 1b's, unchanged,
so the phases stay comparable: decoration stripped, all `ANSWER:` lines
collected, disagreeing values are UNPARSEABLE rather than resolved by guessing.

Four outcomes, and they are never merged:

- **CORRECT**
- **INCORRECT** - answered, wrongly
- **UNPARSEABLE** - no single readable answer
- **BUDGET_EXHAUSTED** - `finish_reason=length`, or the provider closed after
  spending the whole budget on reasoning. Counted as a **failure** in the
  success rate, reported in its own column, and never folded into INCORRECT.

Infrastructure failures are excluded from the denominator and reported
separately: they say nothing about the model.

## Baseline calibration

15 samples, 5 per level, in a randomised balanced **interleaved** order frozen
before the first call (seed 16003112). Configuration is the baseline of the two
previous probes, unchanged. Independent samples: one request each, no
conversation state, no best-of-N, no quality retries, infrastructure retries
only with every attempt recorded.

## What is primary, and what reasoning tokens are not

Task success is the metric. Reasoning tokens, latency and prompt tokens are
description. Phase 1a established on this route that reported compute moves
non-monotonically and that input accounting can vary for byte-identical input,
so **more reasoning tokens are not read as better reasoning** and no causal
claim is drawn from them. The prompt-token check is repeated because it has
fired before.

## Decision gate, fixed in advance

- **Case 1** - compact below 80%: STOP. The instrument raised logical difficulty
  instead of isolating density, so degradation cannot be attributed to density.
- **Case 2** - compact 100% and medium or dense in 20-80%: candidate. Extend
  **only that level** to 10 baseline runs and re-check it stays in 30-85%.
- **Case 3** - all three at 100%: STOP, saturated. No harder instrument is
  designed automatically.
- **Case 4** - failures are only BUDGET_EXHAUSTED: STOP. Whether that measures
  context reliability or output-budget behaviour is a human decision.

`reasoning_effort="high"` is **not** executed in this phase under any outcome,
and `max` is outside it entirely. baseline-versus-high is phase 1d and needs
explicit authorisation.

## Isolation

Nothing outside this directory is written. No `runs/`, `evaluations/`,
`verdicts/`, `leaderboards/`, `releases/`, no DeepSeek battery, not the
reliability experiment, and neither of the two earlier probe directories.

## Files

| path | what it is |
| --- | --- |
| `README.md` | this file |
| `solve_and_verify.py` | exhaustive solver, uniqueness proof, drop-one diagnostics |
| `answer-key.json` | the answer, the witness schedule, the proof metadata |
| `anchors.py` | the 32 shared sentences and the protected-term list |
| `equivalence_audit.py` | the two invariants, dispersion measurement |
| `equivalence-audit.json` | the audit result, constraint map, offsets per level |
| `prompts/compact.txt` `medium.txt` `dense.txt` | the three frozen prompts |
| `prompts/hashes.json` | their sha256, written only on a CLEAN audit |
| `scorer.py` | deterministic scorer and the four outcomes, with self-tests |
| `run_baseline_density.py` | preflight, frozen order, baseline execution |
| `preflight.json` | the pre-call control check |
| `experiment-config.json` | frozen order, seed, outcome classes, request config |
| `raw/baseline-density.jsonl` | every sample, full detail |
| `analyze_density.py` | the curve, the deltas, the decision gate |
| `analysis/density-summary.json` | every computed number |
| `analysis/density-report.md` | the readable report |
| `analysis/density-observations.csv` | the individual observations |
| `manifest.json` | file inventory with hashes |
