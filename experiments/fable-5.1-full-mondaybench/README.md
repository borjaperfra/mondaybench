# OFF-BENCHMARK: Claude Fable 5.1 across all five published MondayBench scenarios

> **SUPERSEDED IN PART BY `AUDIT.md` (2026-09-02).** A scoring and calibration
> audit against the published `verdicts/` and the per-scenario
> `evaluators/*/judge-prompt.md` corrected ten verdicts. The provisional overall
> is **94.90**, not the 95.97 quoted below, and the claim that Fable had the
> highest provisional overall is withdrawn. Per-scenario corrected figures:
> 97.50 / 91.00 / 96.67 / 89.33 / 100.00. Read `AUDIT.md` first.

**Date:** 2026-09-02
**Status:** experiment. **OFF-BENCHMARK / CLAUDE CODE ROUTE. Not official, not a leaderboard entry, not eligible to become one.**
**Route:** `claude -p`, Claude Code CLI 2.1.258, OAuth subscription, `claude-fable-5-1`, effort `high`, adaptive thinking
**Judge:** `claude-opus-5`, recorded in-session. Each scenario scored against **its own** frozen rubric with `scoring.py` unmodified. No rubric was harmonised across scenarios.
**Generations this round:** 12 — three each for monday-001, -003, -004, -005. monday-002 reused from `experiments/fable-5.1-date-sensitivity/`, nothing re-run.

Artefacts: `raw/` (12 generations), `verdicts.jsonl` (309 rows), `five-scenario-summary.json`,
`METHODOLOGY.md`. Nothing was written to `runs/`, `verdicts/`, `evaluations/`,
`leaderboard/` or `models.yaml`.

---

## 1. The five scenarios, verified before generating

Every prompt was rebuilt from source and hashed against both `FROZEN.yaml` and
the pin in `overall-releases.yaml` (Overall v2). All five matched.

| Scenario | Title | Prompt SHA-256 | Rubric | Evaluator of record | Criteria | Runs | current_time | Prompt bytes |
|---|---|---|---|---|---|---|---|---|
| monday-001 | Back to Work | `ed4d7beb…a5e398` | 0.2 | `evaluator-opus5-v0.1` | 19 + noise ladder | 3 | Monday 09:07 | 11,664 |
| monday-002 | Moving Targets | `740e627c…0423a8` | 0.2 | `evaluator-opus5-v0.2` | 20 | 3 | 2026-09-14T09:07+02:00 | 8,786 |
| monday-003 | Blockers | `aaf788f3…4a103f` | 0.3 | `evaluator-opus5-v0.3` | 21 | 3 | 2026-09-21T09:10+02:00 | 13,009 |
| monday-004 | Numbers Don't Lie | `3a0cbb56…23ef99` | 0.3 | `evaluator-opus5-v0.4` | 27 | 3 | 2026-11-02T09:12+02:00 | 24,181 |
| monday-005 | Read the Room | `532cd464…30059a` | 0.4 | `evaluator-opus5-v0.5` | 31 | 3 | 2026-11-09T14:20Z | 19,102 |

monday-001 is the only scenario with a **noise-resistance ladder** (10 points,
6 named false actions, −2 each). Its official leaderboard also lives at
`leaderboard/leaderboard.json` rather than under `leaderboard/monday-001/`,
which predates the per-scenario directories. All seven published models have
official results on all five.

Config identity across all 12 new runs: served model `claude-fable-5-1`,
provider `firstParty`, effort `high` requested, `temperature` and `top_p`
unset and unobservable, route ceiling 64,000 output tokens, no tools,
`finish_reason` `end_turn`, `num_turns` 1, `is_error` false on every run. **No
run was invalid and none was replaced.**

---

## 2. Per-scenario results

| Scenario | Run 1 | Run 2 | Run 3 | Mean | Median | Min | Max | Range | σ | Median TTFA | Mean thinking | Mean output | Total cost |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| monday-001 | 98.5 | 98.5 | 98.5 | **98.50** | 98.5 | 98.5 | 98.5 | 0.0 | 0.00 | 14.5 s | 723 | 2,443 | $0.4656 |
| monday-002 | 92.0 | 91.5 | 93.0 | **92.17** | 92.0 | 91.5 | 93.0 | 1.5 | 0.76 | 56.2 s | 4,046 | 7,134 | $1.1481 |
| monday-003 | 100.0 | 97.5 | 97.5 | **98.33** | 97.5 | 97.5 | 100.0 | 2.5 | 1.44 | 57.0 s | 3,968 | 6,912 | $1.1441 |
| monday-004 | 95.0 | 86.5 | 91.0 | **90.83** | 91.0 | 86.5 | 95.0 | 8.5 | 4.25 | 125.8 s | 10,235 | 17,406 | $2.8699 |
| monday-005 | 100.0 | 100.0 | 100.0 | **100.00** | 100.0 | 100.0 | 100.0 | 0.0 | 0.00 | 41.6 s | 2,844 | 7,094 | $1.2163 |

No penalty fired on any of the 15 runs. Two penalty candidates were recorded as
**dismissed** on monday-002 (A2, A3) for consistency with the frozen
evaluator's demonstrated standard; the reasons are in that experiment's
`verdicts.jsonl`.

### Dimension means

| Scenario | Dimensions |
|---|---|
| monday-001 | action_detection **25.0**/25 · state_reconstruction **25.0**/25 · prioritization **15.0**/15 · data_reasoning 13.5/15 · uncertainty **10.0**/10 · noise_resistance **10.0**/10 |
| monday-002 | state_reconstruction **15.0**/15 · temporal_supersession 14.17/15 · planning_dependencies 19.0/25 · decision_prioritization **20.0**/20 · cross_source_data_reasoning **15.0**/15 · uncertainty_epistemic 9.0/10 |
| monday-003 | critical_path_and_dependencies **21.0**/21 · resource_allocation **25.0**/25 · planning_and_parallelization **18.0**/18 · decision_quality **14.0**/14 · state_reconstruction **10.0**/10 · accuracy_and_uncertainty 10.33/12 |
| monday-004 | revenue_reasoning **20.0**/20 · customer_health 11.83/15 · acquisition_reasoning **19.0**/19 · plan_economics 15.67/19 · cross_table_data_quality 16.33/18 · decision_quality 8.0/9 |
| monday-005 | incident_understanding **17.0**/17 · uncertainty_and_commitment **26.0**/26 · information_boundaries **19.0**/19 · cross_output_consistency **16.0**/16 · audience_completeness **16.0**/16 · supersession_and_currency **6.0**/6 |

---

## 3. Provisional overall

Computed with the same arithmetic `mondaybench/overall.py` uses for the
published Overall v2 — the plain arithmetic mean of the five scenario scores,
each itself the plain mean of three runs, equal weight per scenario, nothing
else folded in.

| | |
|---|---:|
| **Provisional Monday Score** | **95.97** |
| monday-001 | 98.50 |
| monday-002 | 92.17 |
| monday-003 | 98.33 |
| monday-004 | 90.83 |
| monday-005 | 100.00 |
| across-scenario min / max | 90.83 / 100.00 |
| across-scenario range | 9.17 |
| across-scenario σ | 4.16 |
| within-scenario mean run range | 2.50 |
| within-scenario max run range | 8.50 (monday-004) |
| within-scenario mean run σ | 1.29 |

**Aggregate latency, 15 runs:** median TTFA **50.9 s**, median TTFT 5.2 s,
median total latency 85.9 s.
**Aggregate tokens, 15 runs:** mean output **8,198**, mean thinking **4,363**;
totals 122,968 output and 65,447 thinking.
**Aggregate cost, 15 runs:** **$6.8440** total, **$0.4563** mean per run, at
Anthropic first-party list pricing ($10/$50 per MTok, cache-write $12.50,
cache-read $0.25).

---

## 4. Comparison with the seven published models

**Fable 5.1 is OFF-BENCHMARK. No rank is assigned. The row is sorted by score
for readability only.**

| Model | 001 | 002 | 003 | 004 | 005 | Overall | across-σ | range |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **Fable 5.1\*** | 98.50 | 92.17 | 98.33 | 90.83 | 100.00 | **95.97** | 4.16 | 9.17 |
| Qwen 3.8 Flash | 92.50 | 94.83 | 94.50 | 96.50 | 97.00 | 95.07 | 1.79 | 4.50 |
| GLM 5.3 Flash | 98.00 | 87.33 | 92.83 | 98.00 | 98.50 | 94.93 | 4.84 | 11.17 |
| DeepSeek V4 Flash | 90.83 | 89.33 | 95.00 | 86.00 | 97.33 | 91.70 | 4.51 | 11.33 |
| MIMO v2.5 | 88.17 | 81.17 | 90.33 | 78.50 | 95.17 | 86.67 | 6.80 | 16.67 |
| GLM 5.2 | 84.33 | 91.17 | 87.33 | 71.17 | 98.50 | 86.50 | 10.08 | 27.33 |
| Qwen 3.6 | 82.83 | 70.17 | 65.50 | 46.00 | 79.33 | 68.77 | 14.49 | 36.83 |
| Gemma 4 | 70.67 | 54.17 | 65.33 | 35.17 | 89.67 | 63.00 | 20.17 | 54.50 |

\* Provisional. Fable 5.1 was run through Claude Code rather than MondayBench's
standard API route and is excluded from the official ranking.

### PROVISIONAL PLACEMENT — not an official rank

Applying the same Overall v2 arithmetic, 95.97 places **above Qwen 3.8 Flash's
95.07 by 0.90 points**. That gap is smaller than every relevant measure of
uncertainty in the comparison: Qwen 3.8 Flash's own across-scenario σ is 1.79,
its monday-002 run σ is 4.54, and Fable's monday-004 run range is 8.5. Read the
two as **indistinguishable at the top of the field**, not as an ordering. The
same holds against GLM 5.3 Flash at 94.93.

What is separable: Fable 5.1 is clear of DeepSeek V4 Flash (91.70) and
everything below it by more than any of those models' own spreads.

### Cost, latency and tokens against the comparable models

| Model | Overall | Cost/run (monday-002) | TTFA median (monday-002) | Output tokens median (monday-002) |
|---|---:|---:|---:|---:|
| Fable 5.1 (off-benchmark) | 95.97 | **$0.3827** | 56.2 s | 7,134 |
| Qwen 3.8 Flash | 95.07 | – (plan-covered) | 258.9 s | 33,714 |
| GLM 5.3 Flash | 94.93 | – (plan-covered) | 238.5 s | 12,394 |
| GLM 5.2 | 86.50 | $0.0165 | 67.0 s | 6,777 |
| DeepSeek V4 Flash | 91.70 | $0.0056 | 162.6 s | 14,863 |

**The cost bases are not compatible and must not be compared without saying so.**
The published figures are gateway `cost_details` on plan-covered inference;
Qwen 3.8 Flash and GLM 5.3 Flash carry no cost figure at all because their
responses expose no cost field, and `models.yaml` records nulls there rather
than claiming $0. Fable's figure is Anthropic first-party list pricing. Against
GLM 5.2 — the only close comparison with a real per-token figure on the same
scenario — Fable is roughly **23× more expensive per run** for an overall score
9.5 points higher; against DeepSeek V4 Flash, roughly **68×** for 4.3 points.

On latency and verbosity Fable compares well: 4.6× faster to first answer than
Qwen 3.8 Flash on monday-002 and 4.7× more concise, while scoring within noise
of it.

---

## 5. Model profile

### 5.1 Where it excels

**Incident communication under information boundaries (monday-005: 100.00,
σ 0).** All 31 criteria PASS in all three runs — the only clean sweep in this
experiment. It kept SEC-411 out of both external artifacts while routing it to
engineering with ticket, owner and separation; kept the 16:00 internal estimate
internal in all three runs; gave Contoso its own impact row rather than the
29.9% aggregate; and never let an external artifact touch the cause hypotheses.
It also handled the trap the rubric was rewritten twice to catch: the 2.1%
platform-wide denominator appears in two runs and is explicitly refused as the
headline both times.

**Triage and briefing (monday-001: 98.50, σ 0).** Perfect on action detection,
state reconstruction, prioritisation, uncertainty and the noise ladder in all
three runs. Zero of the six named false actions triggered in any run.

**Dependency and resource planning (monday-003: 98.33).** Full marks on the
critical path, resource allocation, parallelisation and decision quality in all
three runs, including the contested-engineer problem the scenario exists to
test — it moved the Contoso permission patch to Daniel with the walkthrough and
gave a reason, in all three runs.

### 5.2 Where it does worse

**Quantitative business analysis (monday-004: 90.83, σ 4.25, range 8.5).** This
is both its lowest mean and its least stable scenario. It is not the arithmetic
— revenue_reasoning and acquisition_reasoning are 20/20 and 19/19 in all three
runs, and every figure I could check against the pack was right. The losses are
in `customer_health` (11.83/15) and `plan_economics` (15.67/19).

**Multi-path scheduling under contention (monday-002: 92.17).**
`planning_dependencies` 19.0/25, driven by the Option A/B decision.

### 5.3 Errors that recur across benchmarks

1. **Population denominators.** monday-004, all three runs: churn rates computed
   on the surviving count rather than the population at risk — "5 of 31" (36 at
   risk), "4 of 9 starter" (13), "4 of 13 SMB" (18 in the segment), "four of the
   seven legacy Starter customers" (a denominator matching nothing in the pack).
   The ranking is right every time; the rate is inflated every time.
2. **Rejecting the harder-but-correct option as infeasible.** monday-002, and
   documented in the earlier experiment across three of four generations: the
   Option B chain is declared not viable on an unsupported premise. The same
   shape appears in monday-004's `absolute_vs_scalable_economics` and
   `product_focus_supported` — the analysis identifies Pro as the best
   economics, then hands engineering priority to Enterprise on absolute
   exposure.
3. **Deadline substitution on the Thursday/Friday axis.** monday-003 runs 2 and
   3: the pricing page's Thursday 17:00 deadline written as Wednesday, and the
   onboarding launch's Friday 12:00 as Thursday. Two per run, neither altering
   the plan. Run 1 carried every value through correctly.
4. **Hedged reductions where the rubric wants investigation.** monday-004
   `segment_recommendation` PARTIAL in two of three runs: it declines to cut SMB
   and then recommends freezing Starter acquisition spend anyway.

### 5.4 Errors appearing once only

`support_normalized` PARTIAL in monday-004 run 2 alone — the only run that gave
support rates on two different denominators without a cross-plan ranking. And
in the other direction, run 3 alone earned `no_churn_overreach` and
`segment_recommendation` at PASS. The rest of the variance is a criterion
flipping in two runs out of three, not one.

### 5.5 Hallucinated constraints — yes, one clear class

The clearest instance is not a hallucinated *fact* but a hallucinated
*constraint*: on monday-002, that Marcus must submit the 2.9.5 diff and is not
online until 09:15. No source establishes it — Priya states she reviews
"asynchronously from a submitted diff" and nothing ties submission to Marcus.
It appears in three of the four monday-002 generations and is load-bearing: it
is the reason Option B is rejected.

monday-004 run 3's "seven legacy Starter customers" is a milder case of the same
habit — a denominator asserted rather than derived.

Against that: across all 15 runs I checked names, figures, deadlines and
durations against the sources and found **no invented person, no invented
figure and no invented deadline**. The habit is inventing *constraints*, not
inventing data.

### 5.6 Conservative in planning and decision — yes, consistently

- monday-002: chose Option A over the ground truth's Option B in all three runs.
- monday-004: declined all three decisions as framed in all three runs, which
  the rubric rewards on two of them and penalises on the third.
- monday-005: refused to answer the SLA question, refused an external ETA,
  refused to name a cause externally — all correct, all rewarded.

The conservatism is a strength wherever the right answer is "don't commit yet"
and a liability wherever the right answer is "the harder path is viable, take
it".

### 5.7 State reconstruction — excellent

Perfect in every scenario that scores it separately: monday-001 25/25,
monday-002 15/15, monday-003 10/10, all runs. monday-005's
`incident_understanding` is 17/17 in all three runs.

### 5.8 Supersession and temporal reasoning — strong, with a specific gap

monday-003 `stale_task_list_overridden` PASS in all three runs (five of five
stale entries corrected). monday-005 `supersession_and_currency` 6/6 in all
three. monday-001 `release_wednesday`, `launch_email_julia`,
`pricing_confidential` PASS throughout. monday-002 `temporal_supersession`
14.17/15.

The gap is not supersession, it is **feasibility arithmetic on a contested
calendar** — deriving whether a chain fits inside two people's availability
windows. That is where monday-002 loses its points and where monday-003's
deadline substitutions occur.

### 5.9 Cross-source reasoning — strong

monday-002 `cross_source_data_reasoning` 15/15 all runs. monday-004
`cross_table_data_quality` 16.33/18 with `customer_id_alias_resolved` and
`cross_table_customer_signal` PASS in all three — it resolved the
`wayne_ent` alias every time, which the rubric notes silently drops a €1.008M
account. monday-001 `data_reasoning` 13.5/15, the only shortfall being
`umbrella_error_rate`: all three runs compared Umbrella's raw error count with
other customers but none read it against its 94,217 request volume. GLM 5.3
Flash scored identically on that criterion.

### 5.10 Does monday-002's consistency hold elsewhere? Partly.

| Scenario | run σ | criteria stable across 3 runs |
|---|---:|---|
| monday-001 | 0.00 | 19/19 |
| monday-005 | 0.00 | 31/31 |
| monday-002 | 0.76 | 17/20 |
| monday-003 | 1.44 | 20/21 |
| monday-004 | 4.25 | 21/27 |

**108 of 118 criteria carry an identical label in all three runs.** Consistency
is very high on judgment and communication work and degrades sharply on the
quantitative scenario. Across-scenario σ of 4.16 is a different quantity and is
mid-field: lower than GLM 5.3 Flash (4.84) and DeepSeek (4.51), higher than
Qwen 3.8 Flash (1.79).

---

## 6. Claude Code `currentDate` contamination across all 15 runs

Observed only; no prompt was changed to test it.

| | count |
|---|---:|
| runs mentioning the runtime date (`2026-09-02` / "system date") | **3 of 15** |
| runs anchored on the scenario's own clock | **15 of 15** |
| runs where the runtime date altered a decision | **0 of 15** |
| runs where it was recognised as a conflict and correctly overridden | **3 of 3** |

The three: monday-002 A2, monday-004 run 1 and monday-004 run 2. In each case
the model named the conflict and resolved it toward the scenario:

* monday-002 A2 — *"(Note: system date shows 2026‑09‑02, but all evidence places today as Monday 14 Sep; I am acting on the evidence.)"*
* monday-004 run 1 — *"the pack describes October 2026 as complete while today's system date is 2 September 2026; the pack has been taken at face value"*
* monday-004 run 2 — *"the pack describes September and October 2026 as complete, but the system date is 2 September 2026. Confirm the pack's period labels before circulation."*

monday-004 run 3 raises a fourth, weaker version without naming the date:
*"the pack's dating should be reconciled with the review's calendar date."*

Both scenarios where it surfaced are the two whose own clock is furthest from
2026-09-02 (14 September and 2 November). It never surfaced on monday-001,
which has no calendar date at all, or on monday-005, whose snapshot is a
time-of-day.

**Practical impact of the known contamination on these 15 runs: none
measurable.** No run reasoned from the runtime date, and the three that saw it
handled it the way a careful analyst would. That is evidence the contamination
is *tolerable for this model on these scenarios* — it is not evidence the
contamination is harmless in general, and it does not make these runs official.

---

## 7. PROVISIONAL PERFORMANCE CONCLUSION

**Provisional overall: 95.97** across five scenarios (98.50 / 92.17 / 98.33 /
90.83 / 100.00), 15 runs, no penalties, no invalid runs.

**Where it falls:** at the top of the field, statistically level with Qwen 3.8
Flash (95.07) and GLM 5.3 Flash (94.93) — the 0.90 and 1.04 point gaps are
inside every relevant spread — and clear of DeepSeek V4 Flash (91.70) and below.

**Strong benchmarks:** monday-005 (100.00, perfect on all 31 criteria in all
three runs), monday-001 (98.50), monday-003 (98.33).
**Weak benchmarks:** monday-004 (90.83) and monday-002 (92.17).

**Consistency:** very high within scenarios — 108 of 118 criteria identical
across runs, run σ of 0.00 on two scenarios — but concentrated: monday-004's
run σ of 4.25 is an order of magnitude above monday-001's and monday-005's.
Across-scenario σ 4.16, mid-field.

**Principal error pattern:** it discounts the harder correct option and
substitutes an unstated constraint to justify doing so — Option B declared
infeasible on a diff-submission constraint no source contains; engineering
priority handed to Enterprise on absolute exposure after its own analysis names
Pro as the better economics. Paired with a systematic denominator habit on
monday-004: churn rates computed on survivors rather than the population at
risk, in all three runs.

**Latency:** median TTFA 50.9 s across 15 runs, faster to first answer than
GLM 5.2 and 4.6× faster than Qwen 3.8 Flash on the shared scenario, with
~4,363 thinking tokens per run.

**Cost against performance:** $0.4563 per run, $6.8440 for the 15 runs. Roughly
23× GLM 5.2 and 68× DeepSeek V4 Flash per run on incompatible billing bases.
For a score that the variance cannot separate from two plan-covered models, the
cost is the least favourable thing about this result.

**Closest existing profile:** by overall score, **Qwen 3.8 Flash** (+0.90). By
*shape*, nothing matches: Qwen 3.8 Flash is flat across all five (σ 1.79) while
Fable swings 9.17 points. GLM 5.3 Flash's shape is nearest — peaking on
monday-005 and monday-001, dipping on monday-002 — but it inverts on monday-004,
where it scores 98.00 and Fable 90.83. **Fable 5.1's profile is closest to GLM
5.3 Flash with monday-004 reversed:** the same judgment-and-communication
strength, the opposite quantitative result.

## 8. METHODOLOGICAL STATUS

**These 15 runs are NOT an official result and cannot become one.**

* **Claude Code route ≠ MondayBench direct provider route.** Every official run
  in this repository was produced by `mondaybench run` →
  `mondaybench/runner.py` → `mondaybench/providers/openai_compatible.py` →
  httpx to the gateway. These 15 were produced by `claude -p`. No adapter for
  that transport exists in the harness and none was added.
* **Agent SDK system-prompt injection.** The frozen system prompt
  `"You are a helpful assistant."` (sha256 `75357d68…68a4de`) is prefixed by
  `"You are a Claude agent, built on Anthropic's Claude Agent SDK."` and cannot
  be removed on any route that reaches this model.
* **Runtime `currentDate` injection.** A `<system-reminder>` carrying
  `Today's date is 2026-09-02` is injected into the first user turn. Three of
  these 15 runs quote it back, so this is observed, not inferred. Its measured
  effect here was nil — that is a finding about tolerance, not a licence.
* **`temperature` and `top_p` are not equivalent.** The official runs were
  generated with `temperature: 0.0`; this route can neither set nor observe
  either parameter, so there is no single `config_sha256` for any of these
  batteries.
* **The frozen qualification logic cannot detect any of this.** As recorded in
  the monday-002 experiment, `official.py:qualify_run` checks only what its own
  provider can produce and would clear every gate it actually tests. These runs
  are excluded by hand, not by machine.

**Fable 5.1 cannot enter the official leaderboard until the battery is
regenerated through a compatible route** — `claude-fable-5-1` on the Helmcode
team allowlist **and** prepaid credit restored, per
`audits/monday-002/fable-5.1-preflight.md`. A 95.97 provisional does not change
that, and a good experimental result is exactly the circumstance in which these
limitations are most likely to be quietly dropped.

The official Overall v2 stands at seven models, unchanged. `models.yaml`,
`runs/`, `verdicts/`, `evaluations/` and `leaderboard/` are untouched; the
frozen suite verifies `identical` at digest
`c056b4b43d3caeb3b50394282b08ed281a5716fb1df68d1666abb950aa0b2a80`.
