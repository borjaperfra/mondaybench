# Calibration log — MondayBench v0.1, `monday-001`

`IMPLEMENTATION.md` §32 defines calibration as a non-official sweep whose purpose
is to find defects in the benchmark, not to rank models: *"Fix only
benchmark/evaluator defects, not results that are merely surprising."*

It did its job. Seven models were run once each against `monday-001`. Judging
happened in two phases: `claude-opus-5` through the Helmcode gateway for the
first sweeps, then human-recorded verdicts for the final sweep after the
gateway's prepaid credit ran out. Five harness defects and three scenario
defects surfaced, and every one of them would have corrupted a published score.

Neither judging phase produced official v0.1 numbers - see "Outcome" below.

---

## Defects found and fixed

### 1. The penalty judge could not see the evidence *(scoring defect, severe)*

**Symptom.** `gemma4` drew four `MATERIAL_HALLUCINATION` penalties, hitting the
−20 cap and scoring 58.

**All four were false.** Each flagged claim is verbatim in the source files:

| Flagged as invented | Actually at |
|---|---|
| "connection pool exhaustion in the 2.18.0 deploy" | `meetings.md:25` |
| "a regression in CSV exports" | `meetings.md:11` |
| "New ARR: €31k" | `emails.md:139` |
| "tiers are currently being modeled" | `meetings.md:45` |

**Cause.** `IMPLEMENTATION.md` §22 shows the penalty judge only
`ground-truth.yaml`. But that file is an *answer key* — a summary of the correct
conclusions — while a material hallucination is defined as a claim "unsupported
by the supplied evidence". Judged against a summary, every accurate detail a
model quotes from Slack or email looks fabricated.

**Fix.** The judge now receives the source material as the authority on what is
*supported*, and the ground truth on what is *materially relevant*. Same
response, re-judged: 76.5, zero penalties.

**Why it mattered.** This penalised precisely the models that read the sources
most carefully. It would have inverted the ranking.

### 2. The penalty judge over-triggered on its own "minor" findings *(scoring defect)*

**Symptom.** After fix 1, `glm5.2` lost 10 points to two hallucinations whose
own stated reasons began *"Minor attribution invention, though the substance of
the flag is supported"* and *"Minor but…"*.

**Cause.** §18 says not to penalise "harmless wording differences or reasonable
summaries", but the prompt never told the judge that its own word *minor* is
disqualifying. −5 on a 100-point scale is not a minor deduction.

**Fix.** The penalty prompt now states that if the judge would call an issue
minor or slight, or if the substance is supported and only attribution or
wording differs, it must not flag it at all.

### 3. A 4,000-token output budget silenced a thinking model *(config defect)*

**Symptom.** `glm5.3-flash` failed outright: `stream produced no content`.

**Cause.** It streams reasoning in `reasoning_content` deltas and spent all
4,000 tokens thinking, emitting no answer. The provider collected only `content`
and reported an unhelpful transport-style error.

**Fix.** Budget raised to 16,000 for **every** model — uniformly, so generation
settings stay identical and scores stay comparable. §35 warns against
"artificially crippl[ing] every model into identical internals"; the
non-reasoning models used 650–2,100 tokens and are unaffected by the headroom.
The provider now also distinguishes a budget exhausted by thinking (names the
cause and the fix) from a genuinely dead stream.

### 4. Throughput was inflated up to 26× *(metrics defect)*

**Symptom.** `qwen3.8-flash` reported **1,291 tok/s**; `glm5.3-flash` 625 tok/s.

**Cause.** TTFT was marked on the first *visible* token. For a thinking model
that arrives after the entire reasoning phase, so the throughput window excluded
the time spent reasoning while `output_tokens` still counted the reasoning
tokens.

**Fix.** TTFT is now the first token of any kind, which is what the API-level
metric means. Time-to-first-*answer* is recorded separately as `ttfa_ms` — for a
thinking model the gap between them is the interesting number. Corrected,
`glm5.3-flash` runs at ~48 tok/s.

### 5. Two scenario inconsistencies *(scenario defects, fixed pre-publication)*

Documented in `scenarios/monday-001/CHANGELOG.md`: a board-meeting date that
contradicted itself inside a single Slack message, and a metrics snapshot dated
on a Thursday in a scenario set on a Monday.

### Also fixed along the way

- **The committed-secret check cried wolf.** It flagged the word "Bearer" inside
  an explanatory comment, failing validation on a file holding no secret. A
  check that produces false positives gets switched off, so it now requires a
  token-shaped value and skips comment lines.
- **`mondaybench endpoints` lost an endpoint.** Commenting out the last model for
  a provider silently removed that provider from discovery — exactly when you
  most need to ask it what it serves. Known endpoints are now probed whenever
  their environment variables are set.

---

## What the harness got right

- **Zero JSON repairs in 147 judge calls.** Structured output through the
  Helmcode gateway held without a single malformed verdict.
- **The deterministic matchers raised no false alarms.** `gemma4` genuinely never
  mentions Umbrella, so the Umbrella matchers correctly stayed silent rather
  than contradicting the judge.
- **`mondaybench endpoints` caught three documentation errors** before any run:
  Helmcode's own docs say `glm-5.2` while its API serves `glm5.2`; the spec's
  `glm-5.3-flash` and `qwen-3.8-flash` are really `glm5.3-flash` and
  `qwen3.8-flash`; and `kimi-k3` exists on neither platform.

---

## Model roster as verified

Placement rule: Helmcode by default, NaN only where Helmcode does not serve the
model. Every id confirmed against `GET /v1/models` **and** a live completion.

| Model | Endpoint | Thinks | Priced |
|---|---|---|---|
| `deepseek-v4-flash` | Helmcode | yes | $0.175 / $0.35 per Mtok |
| `glm5.2` | Helmcode | yes | $0.70 / $2.20 per Mtok |
| `qwen3.6` | Helmcode | no | plan-covered |
| `gemma4` | Helmcode | no | plan-covered |
| `glm5.3-flash` | NaN | yes | quota-based |
| `qwen3.8-flash` | NaN | yes | quota-based |
| `mimo-v2.5` | NaN | no | quota-based |

Prices were measured from the gateway's own `cost_details`, not copied from a
price list. NaN reports no per-token cost (it is quota-based), so those stay
null rather than being claimed as $0.

### Two platform quirks worth knowing

- **NaN's `max_tokens` is advisory.** `qwen3.8-flash` returned 35 completion
  tokens against `max_tokens=1`, and 11,529 against 16,000. Treat
  `finish_reason` from NaN as unreliable.
- **NaN's short-prompt token floor is not a hidden prompt.** It reports ~84
  prompt tokens where Helmcode reports 5 for the same request. This was
  investigated as a possible hidden system prompt — §5 forbids one — and it is
  not: at realistic sizes the two agree exactly (a 184-token prompt reads 184 on
  both). The ~2,900-token benchmark prompt is unaffected.

---

## Outcome: what v0.1 froze

Calibration ended with `monday-001` frozen at prompt `ed4d7beb`, rubric 0.2, and
`evaluator-opus5-v0.1` as the official evaluator. Five harness defects and three
scenario defects were fixed along the way; all of them are recorded above and in
`scenarios/monday-001/CHANGELOG.md`.

The calibration scores themselves are **not** official v0.1 results. They were
produced with one run per model and, for the final sweep, with human-recorded
verdicts (`evaluator-manual-v0.2`) because the judge route was unavailable. They
live on as the evidence behind the defects, not as a ranking.

The single most useful thing calibration produced is the reason v0.1 requires
three runs per model: `glm5.3-flash` passed `umbrella_error_rate` on one run and
only partially met it on another, same prompt, same `temperature: 0`. See the
"Why three runs" section of `README.md`.

## Discrimination

*(Scores below are from the calibration sweep — one run per model, not the three
official runs, and therefore indicative only.)*

The scenario separates the field well through the middle of the range but has no
headroom at the top: two models reached 100/100.

That ceiling is **not** judge generosity. `mimo-v2.5`'s response was checked
by hand against the ten hardest discriminators and genuinely hits nine of them
— Umbrella named, 163 errors, −41% usage, 3.1→4.4 churn, the 11:00 deadline,
Wednesday, Julia's ownership, the unverifiable Friday conversion, and both known
cancellations. It earned the score.

§32 is explicit: *"If all models score around 95+, improve discrimination."*
Only two are, so `monday-001` is not broken — but it cannot rank the top tier,
and that is the finding to act on before v0.2. Options, in rough order of
cost-to-value:

1. **Tighten `umbrella_metrics`.** PASS currently needs any two of four signals.
   `mimo-v2.5` passed without ever citing the 1821ms p95 latency. Requiring the
   latency figure specifically would separate models that skimmed the CSV from
   models that read it.
2. **Add a second unexplained anomaly** whose only trace is in the metrics, so
   one lucky catch is not enough.
3. **Add a subtler stale decision** — one reversed twice, where only the third
   message is current.

Do not tune the rubric to force a predetermined ranking (§32). These changes add
difficulty that the scenario's own design already implies; they do not reweight
the models.

## Known rubric overlaps (reported, not changed)

- **Friday conversion scores twice.** `no_friday_conversion_claim`
  (data_reasoning, 3 pts) and `friday_conversion_unknown` (uncertainty, 3 pts)
  reward nearly the same behaviour.
- **The launch email is penalised three times.** −5 state, −2 noise, −10
  prohibited action: 17 points for one mistake.

Both are plausibly intentional — state, noise and prohibited action are genuinely
different axes — but they widen variance, so expect a higher standard deviation
than the dimension weights alone suggest.

## Criterion-level discrimination — the 16,000-token battery (superseded)

*Kept for the record. This section measures the partial 15-run battery that was
later archived under `archive/budget-16000/` when the output budget was raised
to 32,000 and every run regenerated. Its successor section, below, is the one
that describes the published v0.1 result — and it corrects two of the findings
here.*

Measured over the 15 runs judged at that point under `evaluator-opus5-v0.1`:
3 runs each for `glm5.3-flash`, `mimo-v2.5`, `qwen3.8-flash`; 2 for `glm5.2` and
`deepseek-v4-flash`; 1 for `qwen3.6` and `gemma4`.

| Criterion | PASS | PARTIAL | FAIL |
|---|---:|---:|---:|
| `contoso_action` | 13 | 2 | 0 |
| `umbrella_action` | 5 | 8 | 2 |
| `churn_action` | 14 | 1 | 0 |
| `analytics_action` | 9 | 6 | 0 |
| `acme_resolved` | 15 | 0 | 0 |
| `release_wednesday` | 15 | 0 | 0 |
| `contoso_blocked` | 12 | 3 | 0 |
| `launch_email_julia` | 15 | 0 | 0 |
| `pricing_confidential` | 15 | 0 | 0 |
| `contoso_first` | 15 | 0 | 0 |
| `umbrella_and_churn_high` | 4 | 11 | 0 |
| `no_false_priorities` | 6 | 9 | 0 |
| `umbrella_detected` | 13 | 0 | 2 |
| `umbrella_metrics` | 13 | 0 | 2 |
| `churn_numbers` | 15 | 0 | 0 |
| `umbrella_error_rate` | 1 | 5 | 9 |
| `umbrella_unknown_cause` | 12 | 3 | 0 |
| `friday_conversion_unknown` | **0** | **15** | **0** |
| `churn_causality_unknown` | 14 | 1 | 0 |

Three findings, all of them corrections or additions to what this log already
says:

1. **`umbrella_error_rate` works, and the earlier note that "nothing passed it
   cleanly" is now wrong.** `glm5.3-flash` run-002 passes it outright — it
   writes *"Stark Industries shows 74 API errors, but on 1.48M requests —
   negligible rate"* alongside *"163 errors on low volume"*, which is exactly
   the reading the criterion was written to reward. At 1 / 5 / 9 it is the
   single most discriminating criterion in the rubric. Keep it.

2. **`friday_conversion_unknown` does not discriminate at all.** All 15 runs
   land on PARTIAL — a flat 1.5 / 3 to everybody, which is a constant, not a
   measurement. The two ends are both unreachable in practice: no model states
   that the Friday conversion figure *cannot be established from the provided
   data* (PASS), and none repeats the Slack speculation as fact (FAIL) either,
   because the source itself hedges it. This is the same defect as noise
   resistance, and it should be fixed the same way in v0.2: either move the PASS
   bar down to what a good briefing actually does — naming the gap in the
   "unclear" section — or retire the criterion and spend its 3 points on
   something with a reachable top end.

3. **Noise resistance is now confirmed dead over 15 runs, not 7.** Not one of
   the six false actions triggered in any run. Every model scores a flat 10 / 10
   — 10% of the total that measures nothing. The v0.1 noise items are all
   explicitly resolved or delegated in the source; catching them is free.

Six criteria are at 15/15 PASS (`acme_resolved`, `release_wednesday`,
`launch_email_julia`, `pricing_confidential`, `contoso_first`, `churn_numbers`).
Together with noise resistance's flat 10 and `friday_conversion_unknown`'s flat
1.5, **40.5 of the 100 base points are earned by every run in the battery**
(5+5+5+5+6+3 for the six ceilinged criteria, 10 for noise, 1.5 for Friday
conversion). The scenario is effectively scored out of 59.5. That is the
headroom problem stated precisely, and it is the number to attack in v0.2.

## Criterion-level discrimination — the published v0.1 battery, 21 runs

All 21 official runs at `max_output_tokens: 32000`, judged under
`evaluator-opus5-v0.1` against rubric 0.2. This is the battery behind the
published leaderboard.

| Criterion | PASS | PARTIAL | FAIL |
|---|---:|---:|---:|
| `contoso_action` | 19 | 2 | 0 |
| `umbrella_action` | 7 | 10 | 4 |
| `churn_action` | 20 | 1 | 0 |
| `analytics_action` | **21** | 0 | 0 |
| `acme_resolved` | **21** | 0 | 0 |
| `release_wednesday` | **21** | 0 | 0 |
| `contoso_blocked` | 19 | 2 | 0 |
| `launch_email_julia` | **21** | 0 | 0 |
| `pricing_confidential` | **21** | 0 | 0 |
| `contoso_first` | **21** | 0 | 0 |
| `umbrella_and_churn_high` | 6 | 15 | 0 |
| `no_false_priorities` | 12 | 7 | 2 |
| `umbrella_detected` | 17 | 0 | 4 |
| `umbrella_metrics` | 17 | 0 | 4 |
| `churn_numbers` | **21** | 0 | 0 |
| `umbrella_error_rate` | 0 | 8 | 13 |
| `umbrella_unknown_cause` | 14 | 7 | 0 |
| `friday_conversion_unknown` | 2 | 19 | 0 |
| `churn_causality_unknown` | **21** | 0 | 0 |

### Two corrections to the superseded section above

1. **`friday_conversion_unknown` is reachable after all.** The earlier battery
   put it at 0/15/0 and called it a constant. Here `glm5.3-flash` clears it
   twice, and the way it does so is instructive: run-001 writes *"Julia thought
   conversion 'tanked' Friday; **no conversion data was shared**"*, run-003
   *"real or Friday noise? **No data provided**"*. Both name the absence in the
   supplied material rather than merely asking the question. Nineteen runs raise
   the question and stop there. Keep the criterion; it is measuring something
   real and hard, not an unreachable bar. Two of twenty-one is thin, though, so
   revisit whether PASS should also accept a briefing that flags the gap without
   the explicit "not in the data" phrasing.

2. **`umbrella_error_rate` scored no PASS in this battery.** It stays the
   hardest criterion (0 / 8 / 13) and the strongest discriminator, but the one
   PASS the 16,000 battery produced did not recur. The near-misses are worth
   reading: `qwen3.8-flash` run-002 names Stark and its 74 errors and correctly
   clears it — but justifies that with *"normal latency and +9% usage"*, never
   traffic. `glm5.3-flash` run-001 gets closest with *"Stark/Contoso error rates
   negligible"*, reaching for the rate idea without ever producing a
   denominator. Models will compare customers; almost none divide.

### The ceiling, measured again

Eight criteria are at 21/21 PASS: `analytics_action`, `acme_resolved`,
`release_wednesday`, `launch_email_julia`, `pricing_confidential`,
`contoso_first`, `churn_numbers`, `churn_causality_unknown`. That is 36 points.
Add noise resistance's flat 10 and **46 of the 100 base points are earned by
every run in the battery** — worse than the 40.5 measured before, because
`analytics_action` and `churn_causality_unknown` also topped out once every
model had the headroom to answer fully.

The scenario is effectively scored out of 54, and the spread it produces
(70.7 to 98.0) sits inside that. This is the single biggest thing to fix in v0.2.

### Noise resistance is dead, now over 21 runs

Not one of the six false actions triggered in any run. Every model scores a flat
10/10. The v0.1 noise items are all explicitly resolved or delegated in the
source, and every model in the roster catches them for free. Either make them
genuinely tempting in v0.2 or drop the dimension and redistribute its 10 points.

### What the raised budget changed - and what it did not

Raising `max_output_tokens` from 16,000 to 32,000 was forced by
`deepseek-v4-flash` (see `archive/budget-16000/README.md`). It is tempting to
credit it with more than that, and the numbers do not support doing so.

**Output length did not rise.** Measured across both batteries:

| Model | at 16,000 | at 32,000 |
|---|---|---|
| `qwen3.8-flash` | 9,258 / 7,653 / 13,422 | 6,888 / 9,253 / 10,212 |
| `glm5.3-flash` | 7,610 / 5,646 / 5,592 | 6,117 / 5,603 / 4,766 |
| `deepseek-v4-flash` | 2,904 / 4,898 (+1 truncated) | 4,871 / 5,209 / 3,697 |

Two of the three reasoning models wrote *less*, not more. Nobody except
`deepseek-v4-flash` came anywhere near the old ceiling, so for six of seven
models the change was inert and the run-to-run differences are resampling
variance.

**The score shifts are therefore not attributable to the budget.** The bottom of
the ranking moved from 68.0 to 70.7 and the mean of means from 83.5 to 86.8, but
all 21 runs are fresh samples: the two effects are fully confounded and this
battery cannot separate them. Do not read the 32,000 result as evidence that a
bigger budget raises scores.

What survives is narrower and worth keeping: **an output budget is invisible
until it binds, and then it is fatal rather than gradual.** Both times it has
bound in this project - `glm5.3-flash` at 4,000, `deepseek-v4-flash` at 16,000 -
the model produced no answer whatsoever and would have scored zero, not slightly
worse. There is no warning band on the way down. Before reading any score as
capability, check `finish_reason` and how close the run came to its ceiling.

---

# Calibration log — `monday-002` v0.2-draft, "Moving Targets"

Four models, one attempt each, `evaluator-opus5-v0.2-draft`, rubric 0.2-draft.
Not official and not frozen: `scenario.yaml` carries `status: calibration`, and
`mondaybench publish` refuses it on that ground before it checks anything else.

**v0.1 is archived, not superseded in place.** `archive/monday-002-v0.1/` holds
the whole first draft — scenario, evaluator, judge prompts, runs, evaluations,
verdicts. The two versions share run ids and an evaluator id but not a rubric,
so a v0.1 number and a v0.2 number must never appear in the same table.

## Result

| Model | Base | Penalty | Final | Latency | Output tokens |
|---|---:|---:|---:|---:|---:|
| DeepSeek V4 Flash | 92.0 | 0 | **92.0** | 198.2 s | 24,004 |
| Qwen 3.8 Flash | 85.0 | 0 | **85.0** | 262.4 s | 28,458 |
| GLM 5.3 Flash | 81.5 | 0 | **81.5** | 251.1 s | 9,675 |
| Qwen 3.6 | 67.5 | −5 | **62.5** | 17.4 s | 2,802 |

Spread **29.5 points**, against 4.5 in v0.1. No run failed and no run was
retried.

## The redesign worked

| | v0.1 | v0.2 |
|---|---:|---:|
| Criteria identical across all four models | 17 / 21 | **8 / 20** |
| Point mass locked in those criteria | 75.5 | **37.0** |
| Point mass that discriminates | 24.5 | **63.0** |
| Score spread | 4.5 | **29.5** |

All eight constant criteria are constant at PASS: `stale_external_actions`,
`current_owners`, `parallelize_work`, `immediate_release_decision`,
`expansion_before_11`, `avoid_acme_false_positive`, `causal_boundary`,
`orion_missing_evidence`. Nothing is constant at FAIL, so no criterion is
unreachable — the 37 points are a floor every competent model clears, not dead
weight in the sense of being unwinnable.

## What actually separated the models

**One trap did most of the work.** `planning_dependencies` spread 8.0 to 25.0 of
25 — wider than the other five dimensions combined. Three of four models chose
release path A after asserting that B was *infeasible*, which the sources
contradict: Priya reviews asynchronously from a submitted diff and is available
09:00–09:35, so the delta review runs 09:07–09:32; Marcus then deploys
09:32–10:17, three minutes inside his window. GLM 5.3 Flash: "the deploy can't
finish inside Marcus's window (ends 10:20)". Qwen 3.8 Flash: "a compliant B
sequence cannot finish before Marcus leaves." Qwen 3.6 put the review's finish
at 10:25 and derived an 11:45 start.

Only DeepSeek V4 Flash submitted the diff at 09:07 and built the schedule the
answer key describes, and it is the only model that took the <1%-session-reset
path over the 8% one. A is genuinely time-viable, so this is not a trick — the
models that chose it were not wrong to, but they chose it for a reason that is
false, and they discarded the safer option on that basis.

**The three points that matter most are cheap to earn and cheap to lose.**
`conditional_launch_timing` (3 pts) caught three of four: GLM and Qwen 3.8 both
correctly refused the stale "confirm 10:30 to Atlas" task, then scheduled an
external message stating ~11:00 as fact before the deploy had run.

## The five checks from the brief

**Does B require real scheduling?** Yes, and it is the strongest item in the
draft. B has four dependent steps, two disjoint availability windows and a
three-minute margin on Marcus's departure. One model of four got it.

**Does Acme create false positives?** It is well built but currently free.
Acme has the shortest renewal (9 days) and the steepest decline (−45% usage,
−42% admin logins), and `contracts.csv` explains the decline as an approved
batch-processing shift. All four models saw the explanation and none called it
churn. The trap is sound; at this model tier it does not bite.

**Does Globex require three-file integration?** Yes — renewal window and
procurement state from `contracts.csv`, usage and admin decline from
`accounts.csv`, three tickets including a high-severity SSO failure from
`support.csv`. It discriminated once: Qwen 3.6 ranked Globex "Medium Priority",
third, and dropped the renewal window and usage figures.

**Is €54k explicitly closed?** The arithmetic closes exactly — Wayne 18 +
Globex 12 + Soylent 10 + Wonka 14 — and two models closed it. DeepSeek did not,
and its reason is worth keeping: it noticed that `accounts.csv` expected values
sum to €60k rather than the €126k company-wide figure, and asked to reconcile
against the full account files before sending. That is correct reading of a
partial table, and the rubric currently reads it as a PARTIAL.

**Does Orion semantic uncertainty pass?** All four passed. The org_71A / org_17A
transposition plus Sam's explicit instruction makes the right answer very
legible. It is a valid criterion but it is not measuring anything at this tier.

## Two things to decide before freezing

**1. The penalty prompt does not cover the main failure mode.**
`penalty-judge-prompt.md` says to penalize "impossible dependency schedules" and
to be conservative and not double-penalize partials. The three models that
declared B infeasible produced schedules that are entirely *possible* — their
error was asserting a false constraint about someone else's availability, which
is neither an impossible schedule nor a plain omission. The labels above take
the conservative reading and apply **no** `MAJOR_PLANNING_ERROR`, on the rule
that a penalty needs an asserted falsehood that would do real damage, and that
failing to do something is what FAIL is for.

The alternative reading changes the numbers but not the order:

| Model | conservative | with −7 planning error |
|---|---:|---:|
| DeepSeek V4 Flash | 92.0 | 92.0 |
| Qwen 3.8 Flash | 85.0 | 78.0 |
| GLM 5.3 Flash | 81.5 | 74.5 |
| Qwen 3.6 | 62.5 | 55.5 |

The ranking is stable either way, which is reassuring, but the prompt should
say which reading it wants before anyone runs an official battery.

**2. `deployments.csv` is in the scenario directory and not in `source_order`.**
It is a v0.1 leftover. The model never sees it, so it affects no score, but a
file sitting beside nine live sources and silently excluded is a trap for the
next person. `validate` now warns about it. Delete it or declare it.

## Penalty

One, on Qwen 3.6: `MATERIAL_HALLUCINATION` for "SSO setup failure is blocking
procurement for their €12k expansion", asserted flatly. Nothing links the Globex
tickets to the procurement delay, and Maya's brief specifically forbids
supplying causes the data does not establish. Qwen 3.6 also misread the
`sept_expansion_previous` and `sept_expansion_expected` columns, but wrote those
figures with question marks inside visible working — hedged scratch work, not a
confident invention, and the penalty prompt asks for conservatism. That is
scored as FAIL on `expansion_fully_reconciled`, not penalized.

## Harness fix carried in this round

`finish_reason=stop` with an empty final answer is now classified separately
from `finish_reason=length`. Previously both surfaced as the same error and the
suggested remedy was to raise `max_output_tokens`, which is wrong and expensive
advice when the model simply ended its turn after reasoning. `ProviderError`
carries `kind` (`truncated_by_budget` vs `empty_final_answer`) and
`failed-attempts.jsonl` records it.

---

# `monday-002` v0.2 — OFFICIAL, frozen 2026-08-28

Seven models, three official runs each, `evaluator-opus5-v0.2`, rubric 0.2,
judge `claude-opus-5`. Rendered prompt
`740e627cbc7413c321ede0d54000504de54821d34ff4677f82731b89600423a8`.

## Result

| # | Model | Monday Score | Runs | Range | Stddev |
|---:|---|---:|---|---:|---:|
| 1 | GLM 5.2 | **91.2** | 90.5 / 87.5 / 95.5 | 8.0 | 4.04 |
| 2 | DeepSeek V4 Flash | **89.3** | 97.5 / 86.5 / 84.0 | 13.5 | 7.18 |
| 3 | GLM 5.3 Flash | **87.3** | 85.0 / 85.5 / 91.5 | 6.5 | 3.62 |
| 4 | Qwen 3.8 Flash | **86.5** | 93.0 / 66.5 / 100.0 | 33.5 | 17.67 |
| 5 | MIMO v2.5 | **81.2** | 64.5 / 81.5 / 97.5 | 33.0 | 16.50 |
| 6 | Qwen 3.6 | **70.2** | 75.5 / 83.0 / 52.0 | 31.0 | 16.17 |
| 7 | Gemma 4 | **54.2** | 58.0 / 45.5 / 59.0 | 13.5 | 7.52 |

## Constant point mass kept falling

| Battery | Models | Runs | Constant criteria | Constant points |
|---|---:|---:|---:|---:|
| v0.1 calibration | 4 | 4 | 17 / 21 | 75.5 |
| v0.2 calibration | 4 | 4 | 8 / 20 | 37.0 |
| **v0.2 official** | **7** | **21** | **4 / 20** | **21.0** |

79 of 100 points now discriminate. The four that do not — `stale_external_actions`,
`current_owners`, `immediate_release_decision`, `orion_missing_evidence` — are
PASS in all 21 runs. They are a floor every model in this roster clears, and
they would still separate a weaker model; they are not unreachable.

## The finding

**Three runs per model was not a formality here; it was the whole story.**
Four of seven models have a range above 30 points, and the top of the ranking
would be different on any single run: Qwen 3.8 Flash scored a 100.0 and a 66.5
in the same battery. On one run per model this scenario would have produced a
confident and wrong ranking. Compare #001, where the widest range was 1.5.

**The release-path trap held.** `schedule_feasibility` was missed in 17 of 21
runs. Priya reviews asynchronously from a submitted diff and is free 09:00–09:35,
so Option B's chain runs 09:07–09:32 review, 09:32–10:17 deploy (Marcus leaves
10:20), 10:25–10:45 verification, 10:45–11:00 rollout. Only five runs found it.
Most models declared B infeasible and took the 8%-session-reset path over the
<1% one — and, per the frozen penalty prompt, were scored down through the
planning criteria rather than penalized for it.

**Gemma 4 is the only model that recommended plans that cannot run at all.**
All three of its runs schedule Marcus to deploy after his 10:20 hard stop, one
of them starting at 10:30. That is what MAJOR_PLANNING_ERROR is now scoped to,
and it fired four times across the battery (three on Gemma 4, one on Qwen 3.6).

**Acme never bit.** The false-positive trap — shortest renewal, steepest
decline, fully explained by contract — was correctly refused in 20 of 21 runs.
It is well built and, at this tier, free. Same for `orion_missing_evidence`:
21 of 21.

## Penalty policy, as frozen

The calibration round left MAJOR_PLANNING_ERROR ambiguous: it was unclear
whether wrongly declaring a viable option infeasible counted. It does not.
`penalty-judge-prompt.md` now scopes it to a *recommended* plan that violates a
stated hard dependency or cannot run under the supplied timing and availability,
and says explicitly that rejecting a viable alternative is priced by the
planning rubric instead. Nine penalties fired across 21 runs: four
MAJOR_PLANNING_ERROR, four MATERIAL_HALLUCINATION, one MAJOR_CONTRADICTION.

## Artefacts

`leaderboard/monday-002/` holds the leaderboard in three formats plus
`criterion-matrix.md` (summary and full per-run) and `analysis.md`.
`leaderboard/index.json` registers both published scenarios in a shape an
aggregate could consume; no Overall Monday Score is computed or published.
