# OFF-BENCHMARK: Claude Fable 5.1, three frozen-prompt runs on monday-002

**Date:** 2026-09-02
**Status:** experiment. **OFF-BENCHMARK / CLAUDE CODE ROUTE. Not official, not a leaderboard entry, not eligible to become one.**
**Route:** `claude -p`, Claude Code CLI 2.1.258, OAuth subscription, `claude-fable-5-1`, effort `high`, adaptive thinking
**Rubric / evaluator / judge:** frozen monday-002 rubric 0.2, recorded Opus 5 judge, `scoring.py` unmodified
**Generations this round:** A2 and A3 only. A1 was preserved and re-used, not re-run. Run B is context only and is excluded from every aggregate.

Artefacts: `run-A-frozen.json` (A1), `run-A2-frozen.json`, `run-A3-frozen.json`,
`verdicts.jsonl` (A1, B), `verdicts-A2-A3.jsonl`, `frozen-3run-summary.json`.
Nothing in `runs/`, `verdicts/`, `evaluations/`, `leaderboard/` or `models.yaml`
was created or touched.

---

## 1. Input and configuration identity

All three runs sent a byte-identical user prompt, verified before generation:

    prompt file    740e627cbc7413c321ede0d54000504de54821d34ff4677f82731b89600423a8
    FROZEN.yaml    740e627cbc7413c321ede0d54000504de54821d34ff4677f82731b89600423a8
    A1 recorded    740e627cbc7413c321ede0d54000504de54821d34ff4677f82731b89600423a8

Every observable configuration field is identical across A1, A2, A3: requested
and served model `claude-fable-5-1`, provider `firstParty`, route, system prompt
requested, effort `high`, `temperature` unset, `top_p` unset, route ceiling
64,000 output tokens, no tools, `finish_reason` `end_turn`, `num_turns` 1,
`is_error` false, billed models, `costBasis` `list`. **No run is invalid.**

**One difference, recorded rather than ignored:** A1 *wrote* the prompt cache
(3,804 cache-write tokens, 0 cache-read); A2 and A3 *read* it (0 cache-write,
3,804 cache-read). Identical token count and identical content — the model saw
the same input. It affects cost only, and it makes A1 look ~13% more expensive
than A2/A3 for a shorter answer. Not a comparability problem for scores.

---

## 2. Per-run results

| | A1 | A2 | A3 |
|---|---:|---:|---:|
| **Total** | **92.0** | **91.5** | **93.0** |
| state_reconstruction /15 | 15.0 | 15.0 | 15.0 |
| temporal_supersession /15 | 12.5 | 15.0 | 15.0 |
| planning_dependencies /25 | 21.0 | 18.0 | 18.0 |
| decision_prioritization /20 | 20.0 | 20.0 | 20.0 |
| cross_source_data_reasoning /15 | 15.0 | 15.0 | 15.0 |
| uncertainty_epistemic /10 | 8.5 | 8.5 | 10.0 |
| penalties applied | none | none | none |
| penalty candidates dismissed | 0 | 1 | 1 |
| TTFT | 3.16 s | 6.59 s | 4.80 s |
| TTFA | 50.23 s | 60.66 s | 56.24 s |
| total latency | 84.6 s | 98.6 s | 93.2 s |
| input tokens (uncached) | 2 | 2 | 2 |
| cache-write tokens | 3,804 | 0 | 0 |
| cache-read tokens | 0 | 3,804 | 3,804 |
| output tokens | 6,739 | 7,436 | 7,226 |
| thinking tokens | 3,819 | 4,235 | 4,084 |
| cost | $0.41305 | $0.37277 | $0.36227 |
| finish reason | `end_turn` | `end_turn` | `end_turn` |

### Qualification

**All three: NOT OFFICIAL.** The reason is the route, not the run content — the
system prompt actually sent carries the Agent SDK preamble and an injected
`<system-reminder>`, and `temperature` / `top_p` are unsettable, so the frozen
generation conditions are not met. See
`audits/monday-002/fable-5.1-preflight.md`.

Worth recording precisely, because it is a gap rather than a formality:
`official.py:qualify_run` was **not executed** on these artefacts — they are not
`BenchmarkRun` records and building them would mean writing into `runs/`. Read
against its gates by inspection, they would clear every one it actually checks:
prompt hash matches, response non-empty, `generation_ceiling_status` NON_BINDING
(`end_turn`, 6.7k–7.4k against a 64,000 ceiling), `unsupported_parameters`
empty, reasoning DELIVERED on positive thinking tokens. The gates it would fail
are ones the function has no way to test, because it assumes its own provider
produced the run. **The frozen qualification logic cannot detect this
contamination.** That is an argument for keeping these runs out by hand, not an
argument that they are admissible.

---

## 3. Aggregates over A1 + A2 + A3

Run B is not included in any figure below.

| Statistic | Value |
|---|---:|
| n | 3 |
| **mean** | **92.17** |
| median | 92.0 |
| min | 91.5 |
| max | 93.0 |
| range | **1.5** |
| stddev (sample) | **0.76** |
| median TTFA | 56.24 s |
| median TTFT | 4.80 s |
| mean thinking tokens | 4,046 |
| mean output tokens | 7,134 |
| mean cost / run | $0.382697 |
| **total cost, 3 runs** | **$1.148092** |

Dimension means: state_reconstruction **15.00**, temporal_supersession
**14.17**, planning_dependencies **19.00**, decision_prioritization **20.00**,
cross_source_data_reasoning **15.00**, uncertainty_epistemic **9.00**.

---

## 4. Variability analysis

**17 of 20 criteria carry an identical label in all three runs.** That is where
the 0.76 stddev comes from.

| Criterion | A1 | A2 | A3 | points |
|---|---|---|---|---|
| `ownership_supersession` | PARTIAL | PASS | PASS | 2.5 / 5.0 / 5.0 |
| `schedule_feasibility` | PASS | PARTIAL | PARTIAL | 6.0 / 3.0 / 3.0 |
| `conditional_launch_timing` | PARTIAL | PARTIAL | PASS | 1.5 / 1.5 / 3.0 |

Stable at PASS in all three: `launch_state`, `stale_external_actions`,
`current_owners`, `executive_gate_superseded`, `pricing_authority`,
`option_b_sequence`, `parallelize_work`, `immediate_release_decision`,
`expansion_before_11`, `globex_priority`, `avoid_acme_false_positive`,
`expansion_fully_reconciled`, `causal_boundary`, `customer_signal_integration`,
`orion_missing_evidence`, `no_unsupported_causality`. Stable at PARTIAL in all
three: `choose_option_b`.

### 4.1 What all three agree on

Option A (2.9.4 retry with shard precheck). Deploy inside Marcus's 09:15–10:20
window, Priya's post-deploy verification at 10:25–10:45, Sam opens rollout
10:45–11:00, Atlas begins ~11:00 inside the before-12:00 deadline, Daniel sends
only on Sam's confirmation. No Maya gate. Zenith closed. Pinned pricing workbook
non-authoritative, internal only, nothing to Initech. Orion held pending the
org-ID/live-flag pair. €54k = 18+12+10+14 closed in all three. Globex first on
evidence; Acme dismissed as an explained false positive; Wonka and Soylent as
unexplained secondaries. Reconciliation to Maya before 11:00 in all three.

### 4.2 What changed between runs

Only the three criteria above, and each turns on one sentence:

* `ownership_supersession` — whether the response says the user is *not* the
  sender. A2 *"(Daniel sends, not me)"* and A3 *"Do not send the customer
  announcement myself"* displace the stale task. A1 only names the owner:
  *"Don't send the customer announcement before Sam's confirmation (Daniel owns
  the send)."*
* `conditional_launch_timing` — whether the ~11:00 figure is hedged when it goes
  to Atlas. A3 alone adds *"targeted to begin ~11:00 … confirmation to follow"*.
  A1 *"reset Atlas expectation … migration starts ~11:00–11:15"* and A2
  *"rollout expected to begin ~11:00"* both send a time before Priya's 10:25
  verification with conditionality only implied.
* `schedule_feasibility` — see 4.5. **A1 is the outlier here, in the model's
  favour.**

### 4.3 Do all three read `current_time` correctly?

Yes, in substance. All three run the whole morning off 09:07 with Friday behind
them, Thursday as the slip target, and every relative figure right — Globex
renewal 18 days, Acme 9 days, Wonka 31, Soylent 44.

A1 states *"CURRENT STATE (Mon 14 Sep, 09:07)"*. A2 states *"(Mon 14 Sep,
09:07)"*. **A3 never writes the calendar date at all** — its header is
*"Monday 09:07 — Return-to-work brief"*. A3 is not wrong, it simply never
commits the date to paper; nothing in it is inconsistent with 14 September.

### 4.4 Does the real date appear? — the most interesting result here

| | mentions `2026-09-02` |
|---|---|
| A1 | no |
| **A2** | **yes, once, explicitly** |
| A3 | no |

A2, in its own words:

> *(Note: system date shows 2026‑09‑02, but all evidence places today as Monday
> 14 Sep; I am acting on the evidence.)*

This is the first direct proof that the injected `currentDate` **does reach the
model** — the previous experiment could only show it never surfaced. Fable 5.1
saw the conflict, named it, and resolved it the right way. A2 also scored 91.5,
the lowest of the three, but it lost its points on `schedule_feasibility` and
`conditional_launch_timing`, neither of which has anything to do with the date.

No run reasons *from* 2026-09-02. No date-derived error appears anywhere in
three runs.

### 4.5 Does Run B's `schedule_feasibility` error reappear? — yes, and this
### revises the previous conclusion

**Yes. A2 and A3 both declare Option B infeasible.** So across all four
generations produced in this experiment, three conclude B is not viable and only
A1 does not:

| Run | Option B verdict | criterion |
|---|---|---|
| A1 | tight but real; commits review 09:10–09:35 then deploy 09:35–10:20 | PASS 6.0 |
| A2 | *"Not viable today"* — after writing windows that do fit | PARTIAL 3.0 |
| A3 | *"infeasible under today's availability"* | PARTIAL 3.0 |
| B *(context only)* | *"finishes at 10:30 at the earliest"* — wrong time, no schedule | FAIL 0.0 |

The ground truth: a 25-minute delta review from 09:07 finishes ~09:32, the
45-minute deploy runs 09:32–10:17 inside Marcus's window, verification
10:25–10:45, Sam 10:45–11:00. B is viable and is the correct choice.

**This corrects the previous experiment's framing.** That report treated B's
`schedule_feasibility` FAIL as possibly a treatment effect of the date-neutralising
instruction. With A2 and A3 in hand it is clearly not: concluding "Option B is
infeasible" is Fable 5.1's **default behaviour on this scenario**, and A1 was
the lucky draw. The date instruction did not cause it.

What varies is only *how* wrong the reasoning is. A1 built a correct B schedule
and kept it. A2 built the correct windows — *"review would have to run
09:10–09:35 … and deploy run 09:35–10:20"* — and then rejected them. A3 stated
the correct constraints — *"a 25-min delta review to finish by 09:35 … so that a
45-min deploy can finish by 10:20"* — and concluded the opposite of what they
imply. B alone got the arithmetic itself wrong.

All three of A2, A3 and B lean on the same unsupported premise: that Marcus must
submit the diff and is not online until 09:15. No source establishes it — Priya
says she reviews *"asynchronously from a submitted diff"* and nothing ties
submission to Marcus. Logged as a **dismissed** `material_hallucination` on A2
and A3, for consistency with the frozen evaluator's demonstrated standard:
`deepseek-v4-flash` made the same class of error on this scenario and was graded
`schedule_feasibility` FAIL with no penalty. The error is already priced through
the criterion.

### 4.6 Systematic vs stochastic

**Systematic — present in every run, and where the points actually go:**

* Chooses Option A over B. `choose_option_b` PARTIAL 3/3, **4.0 points forgone
  every single run** — the largest recurring loss.
* Rejects B as infeasible or near-infeasible (2/3 frozen runs, 3/4 counting B),
  on the unsupported Marcus-submits premise.
* Communicates a rollout time to Atlas before the Security chain finishes
  (2/3 frozen runs).

Together these are why `planning_dependencies` (19.00/25) and
`uncertainty_epistemic` (9.00/10) are the only two dimensions off maximum.

**Stochastic — one sentence's presence or absence:**

* Saying "not me" about the announcement (`ownership_supersession`).
* Adding "confirmation to follow" to the ~11:00 figure
  (`conditional_launch_timing`).
* Whether the correct B schedule survives to the plan (`schedule_feasibility`
  PASS vs PARTIAL).
* Whether the system date is mentioned at all (A2 only) — cosmetic, no score
  effect.

**Was A1's 92.0 representative? Yes.** It sits 0.17 below the three-run mean.
But it was representative *by luck rather than by consistency*: A1 gained 3.0
on `schedule_feasibility` that A2 and A3 did not, and gave back 2.5 on
`ownership_supersession` that they did not. The two errors nearly cancelled.

---

## 5. Descriptive comparison with the official board

**Fable 5.1 is OFF-BENCHMARK / CLAUDE CODE ROUTE. No rank is assigned or
implied.** The official column is means of three runs generated through
MondayBench's own provider under the frozen conditions; the Fable column is
three runs through a contaminated harness with no sampling control. The two are
not comparable, and the table below is a sighting.

| | Model | Mean | Range | σ | TTFA med | Output tok | Cost/run |
|---|---|---:|---:|---:|---:|---:|---:|
| 1 | Qwen 3.8 Flash | 94.83 | 8.5 | 4.54 | 258.9 s | 33,714 | – |
| — | *Fable 5.1 — off-benchmark* | *92.17* | *1.5* | *0.76* | *56.2 s* | *7,134* | *$0.3827* |
| 2 | GLM 5.2 | 91.17 | 8.0 | 4.04 | 67.0 s | 6,777 | $0.0165 |
| 3 | DeepSeek V4 Flash | 89.33 | 13.5 | 7.18 | 162.6 s | 14,863 | $0.0056 |
| 4 | GLM 5.3 Flash | 87.33 | 6.5 | 3.62 | 238.5 s | 12,394 | – |
| 5 | MIMO v2.5 | 81.17 | 33.0 | 16.50 | 163.3 s | 9,510 | – |
| 6 | Qwen 3.6 | 70.17 | 31.0 | 16.17 | 0.9 s | 2,644 | – |
| 7 | Gemma 4 | 54.17 | 13.5 | 7.52 | 0.3 s | 921 | – |

**Score.** The provisional mean of 92.17 **falls between GLM 5.2 (91.17) and
Qwen 3.8 Flash (94.83)**. The 1.00-point gap over GLM 5.2 is far inside GLM
5.2's own three-run spread (σ 4.04, range 8.0) and cannot be called a
difference. The 2.66-point gap to Qwen 3.8 Flash is likewise inside that model's
spread (σ 4.54, range 8.5). On this evidence Fable 5.1 sits in the same
performance band as the top three and is **not separated from any of them**.

**Variance.** σ 0.76 over a 1.5-point range is the tightest of anything measured
on this scenario — the next tightest is GLM 5.3 Flash at 3.62, and MIMO v2.5
reaches 16.50. Two caveats: n=3 is a weak variance estimate, and the official
runs were generated with `temperature: 0.0` while this route cannot set it at
all, so the comparison is not like-for-like in the direction that would normally
*widen* Fable's spread, not narrow it.

**Latency.** Median TTFA 56.2 s is faster than GLM 5.2 (67.0 s) and roughly
4.6× faster than Qwen 3.8 Flash (258.9 s), despite ~4,046 thinking tokens per
run. Fable spends its thinking budget quickly.

**Tokens.** 7,134 output tokens per run is close to GLM 5.2's 6,777 and 4.7×
more concise than Qwen 3.8 Flash's 33,714, for a mean 2.66 points lower.

**Cost.** $0.3827 per run against GLM 5.2's $0.0165 — roughly **23×** — and
against DeepSeek V4 Flash's $0.0056, roughly **68×**, for no established score
advantage over either. Read that gap with care: the official figures are gateway
`cost_details` on plan-covered inference, while Fable's is Anthropic first-party
list pricing ($10/$50 per MTok, cache-write $12.50, cache-read $0.25). Different
billing bases, as `models.yaml`'s header warns. The order of magnitude survives
the caveat; the exact multiple does not.

**Dimension profile.**

| Dimension | Fable 5.1 | Qwen 3.8 F | GLM 5.2 | DeepSeek V4 F |
|---|---:|---:|---:|---:|
| state_reconstruction | **15.00** | 15.00 | 15.00 | 15.00 |
| temporal_supersession | 14.17 | **15.00** | 12.50 | 13.33 |
| planning_dependencies | 19.00 | **20.33** | 18.67 | 16.00 |
| decision_prioritization | **20.00** | 20.00 | 20.00 | 20.00 |
| cross_source_data_reasoning | **15.00** | 15.00 | 15.00 | 15.00 |
| uncertainty_epistemic | 9.00 | 9.50 | **10.00** | **10.00** |

---

## PROVISIONAL PERFORMANCE CONCLUSION

1. **Provisional monday-002 mean: 92.17** over three frozen-prompt runs
   (92.0 / 91.5 / 93.0).
2. **Variability: very low** — range 1.5, σ 0.76, with 17 of 20 criteria
   identical across all three runs. The lowest measured on this scenario, though
   n=3 is a weak estimate.
3. **In the top band: yes.** Above GLM 5.3 Flash and everything below it by more
   than any plausible noise, and level with the top three.
4. **Closest to GLM 5.2** by score (+1.00) and by dimension shape, though better
   than GLM 5.2 on temporal supersession and worse on uncertainty. It is *not*
   separated from GLM 5.2, DeepSeek V4 Flash or Qwen 3.8 Flash by more than
   their own run-to-run spreads, so no ordering between Fable and any of those
   three is supported.
5. **No evidence the Claude Code `currentDate` altered the result.** Stronger
   than last time, in both directions: A2 proves the date *reaches* the model,
   and all three runs resolve it correctly against the scenario evidence. No run
   reasons from 2026-09-02, and the one run that mentioned it lost its points on
   two criteria unrelated to dates.
6. **Strengths:** perfect and stable on `state_reconstruction` (15.00),
   `decision_prioritization` (20.00) and `cross_source_data_reasoning` (15.00) —
   nine criteria at PASS in every run, including the full €54k reconciliation,
   the Acme false positive, Globex on four signals, the Orion refusal and the
   causal boundary. `temporal_supersession` 14.17 beats GLM 5.2 and DeepSeek.
7. **Principal weakness: `planning_dependencies`, 19.00/25 — specifically the
   Option A/B decision.** It chose A in all three runs (4.0 forgone each time)
   and in two of three additionally argued B was infeasible, using a constraint
   no source supports. This is systematic, not noise, and it is the single
   change that would move the score most.
8. **Cost and latency against performance:** fast to first answer (56.2 s median
   TTFA, faster than GLM 5.2) and concise (7,134 output tokens), but roughly 23×
   GLM 5.2's cost per run for a score difference that the variance does not
   support. On this scenario Fable 5.1 buys consistency, not accuracy — its
   distinguishing property is a 0.76 σ, not a higher mean.

## METHODOLOGICAL STATUS

**These three runs are NOT official and cannot become official.** Fable 5.1 was
served through **Claude Code**, not through MondayBench's own provider path.
Consequences, all documented in
`audits/monday-002/fable-5.1-preflight.md`:

* The system prompt actually sent is not the frozen
  `"You are a helpful assistant."` — an Agent SDK preamble is prepended and
  cannot be removed on any route that reaches this model.
* A `<system-reminder>` is injected into the user turn. A2 quotes it back, so
  this is now observed rather than inferred.
* `temperature` and `top_p` are neither settable nor observable, so there is no
  single `config_sha256` for the battery.
* No adapter exists in the harness for this transport, and none was added.

The official monday-002 result stands at seven models. `models.yaml`,
`runs/`, `verdicts/`, `evaluations/` and `leaderboard/` are untouched; frozen
suite digest `c056b4b43d3caeb3b50394282b08ed281a5716fb1df68d1666abb950aa0b2a80`
verifies `identical`. Admitting Fable to the board still requires the gateway
route: `claude-fable-5-1` on the Helmcode team allowlist **and** prepaid credit
restored. Nothing in this experiment changes that.
