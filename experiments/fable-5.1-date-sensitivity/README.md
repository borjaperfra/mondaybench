# OFF-BENCHMARK: does Claude Code's date contamination move Fable 5.1 on monday-002?

**Date:** 2026-09-02
**Status:** experiment. **Not official. Not a leaderboard entry. Not eligible to become one.**
**Route:** `claude -p`, Claude Code CLI 2.1.258, OAuth subscription, `claude-fable-5-1`
**Rubric / evaluator / judge:** frozen monday-002 rubric 0.2, recorded Opus 5 judge, `scoring.py` unmodified
**Generations:** exactly two, one per arm. No retries, no best-of.

Artefacts here: `run-A-frozen.json`, `run-B-neutralized.json`, `verdicts.jsonl`,
`scores.json`. Nothing in `runs/`, `verdicts/`, `evaluations/` or `leaderboard/`
was created or touched.

---

## The two arms

| | RUN A | RUN B |
|---|---|---|
| user content | the frozen monday-002 prompt, byte-identical | 149 bytes prepended, then the frozen prompt byte-identical |
| prompt sha256 | `740e627c…423a8` — matches `FROZEN.yaml` | `31e9a9d2…a98d1` |
| prepended line | — | *"For this scenario, current_time in the scenario is authoritative. Ignore any runtime, environment, system, or reminder date that conflicts with it."* |

Both arms carry the full Claude Code contamination documented in
`audits/monday-002/fable-5.1-preflight.md`: the Agent SDK system-prompt preamble
and the injected `<system-reminder>` stating `Today's date is 2026-09-02`, against
a scenario whose `current_time` is `2026-09-14T09:07:00+02:00`. Only the date is
addressed in B; nothing else was mitigated, by design.

---

## Result

| | RUN A (frozen) | RUN B (date-neutralized) | Δ (B − A) |
|---|---:|---:|---:|
| **Total** | **92.0** | **88.5** | **−3.5** |
| state_reconstruction | 15.0 / 15 | 15.0 / 15 | 0.00 |
| temporal_supersession | 12.5 / 15 | 15.0 / 15 | **+2.50** |
| planning_dependencies | 21.0 / 25 | 15.0 / 25 | **−6.00** |
| decision_prioritization | 20.0 / 20 | 20.0 / 20 | 0.00 |
| cross_source_data_reasoning | 15.0 / 15 | 15.0 / 15 | 0.00 |
| uncertainty_epistemic | 8.5 / 10 | 8.5 / 10 | 0.00 |
| penalties | none | none (one candidate dismissed) | — |

**Exactly two of twenty criteria differ.** Every other criterion carries the same
label in both arms.

| Criterion | A | B | Δ |
|---|---|---|---:|
| `ownership_supersession` | PARTIAL 2.5 | **PASS 5.0** | +2.5 |
| `schedule_feasibility` | **PASS 6.0** | FAIL 0.0 | −6.0 |

The four temporal criteria the experiment was aimed at:

| Criterion | A | B |
|---|---|---|
| `temporal_supersession` (dimension) | 12.5 | 15.0 |
| `schedule_feasibility` | PASS | FAIL |
| `conditional_launch_timing` | PARTIAL | PARTIAL |
| `launch_state` | PASS | PASS |

---

## The date did not leak into either answer

Scanned both responses for the real date. **Zero occurrences of `2026-09-02`,
`Sep 02`, `2 September`, or any 2026-0[1-8] date in either arm.** Both anchor
themselves on the scenario clock in their first line:

* A — `# 1. CURRENT STATE (Mon 14 Sep, 09:07)`
* B — `# Monday 14 Sept, 09:07 — Enterprise Controls / Atlas week`

So the answers to the two questions that actually matter are both negative:

* **Did the conflicting `currentDate` produce a visible error in A?** No. Not one.
* **Did B's instruction fix an error in A?** No — there was nothing to fix.
  B instead introduced a *new* temporal error that A did not have.

## What actually differed

**Both arms make the same primary decision and the same plan.** Option A
(2.9.4 + shard precheck), deploy 09:15–09:35, Priya's post-deploy verification
10:25–10:45, Sam opens rollout 10:45–11:00, Atlas starts ~11:00 inside the
before-12:00 window, Daniel sends only on Sam's confirmation, reconciliation to
Maya before 11:00, Globex escalated, Orion held pending org ID. Same customer
ranking, same do-not list, same €54k reconciliation.

The two divergences:

1. **`schedule_feasibility` — A is right and B is wrong.** A treats Option B as
   tight but real and commits a schedule for it: delta review 09:10–09:35, then
   *"Marcus deploys B 09:35–10:20 (only if delta review completed)"*. That fits
   Priya's 09:00–09:35 window, Marcus's 10:20 stop and the 12:00 deadline, and it
   is close to the ground truth (review ~09:32, deploy 09:32–10:17).
   B instead declares B dead: *"the 25-min delta review cannot complete before
   Priya goes offline at 09:35 … finishes at 10:30 at the earliest, and Marcus
   (sole deployer) leaves at 10:20, so the 45-min deploy has no one to run it."*
   A 25-minute review from 09:07 finishes ~09:32, inside Priya's window. B also
   leans on *"Marcus can't even submit the diff before 09:15"*, a constraint no
   source establishes — Priya says she reviews *"asynchronously from a submitted
   diff"* and nothing ties submission to Marcus.

2. **`ownership_supersession` — B is right and A is thinner.** Both trace the
   handoff (*"Sarah is out; Daniel holds Julia's final draft + Atlas recipient
   list"*). Only B explicitly displaces the stale user-as-sender task:
   *"Do not send the customer announcement myself — Daniel owns it."* A only says
   *"Don't send the customer announcement before Sam's confirmation (Daniel owns
   the send)"*, which names the owner without rejecting the stale assignment.

The two deltas point in **opposite directions**. That is the shape of sampling
noise, not of a treatment effect.

### Penalty candidate, dismissed

B's *"Marcus can't even submit the diff before 09:15"* is an unsupported
constraint doing load-bearing work in a release-decision rationale, which is a
`material_hallucination` candidate. It is **dismissed** and recorded as such in
`verdicts.jsonl`, for consistency with the frozen evaluator's demonstrated
standard on this exact scenario: `deepseek-v4-flash` made the same class of
wrong-feasibility derivation (*"Priya's 09:35-10:25 gap plus Marcus leaving at
10:20 prevents completion before noon"*) and was graded `schedule_feasibility`
FAIL with no penalty. Applying a penalty here but not there would make the
comparison less honest, not more, and the error is already priced at −6.0.

---

## Verdict against the stated thresholds

The −3.5 total sits in the **WEAK / UNCERTAIN** band by magnitude
(> 2 and ≤ 5). But the diagnostic's NOT VIABLE clause is triggered on content,
not magnitude: *any difference that changes supersession, launch timing,
feasibility or a main decision.* Both differing criteria are in that set —
`ownership_supersession` is a supersession criterion and `schedule_feasibility`
is a feasibility criterion.

### **NOT VIABLE**

Read carefully, though, because the label describes the *experiment*, not the
model. It is NOT VIABLE in the sense that **1+1 does not isolate a date effect**:

* The date never reached either answer, so there was no effect to isolate.
* The two criteria that moved, moved in opposite directions and are unrelated to
  the date — one is about who sends a customer email, the other about arithmetic
  on Priya's calendar window.
* Sampling cannot be separated from treatment at n=1 per arm, and this route
  cannot set `temperature`. Run-to-run spread on this scenario reaches 33.0
  points for MIMO v2.5 and 31.0 for Qwen 3.6 across three official runs; a
  3.5-point gap between two single samples is well inside that.

The defensible conclusion is narrower than the question asked: **on this evidence
the injected date did not visibly change Fable 5.1's temporal reasoning on
monday-002, and the mitigation bought nothing.** That does not license adding
Fable to the leaderboard — the preflight blockers in
`audits/monday-002/fable-5.1-preflight.md` are unchanged, and this experiment
had no power to test them.

---

## Cost and observability

| | RUN A | RUN B |
|---|---:|---:|
| served model | `claude-fable-5-1`, firstParty | `claude-fable-5-1`, firstParty |
| uncached input tokens | 2 | 2 |
| cache-write input tokens | 3,804 | 3,852 |
| output tokens | 6,739 | 7,649 |
| thinking tokens | 3,819 | 4,195 |
| TTFT | 3.16 s | 5.00 s |
| **TTFA** | **50.23 s** | **58.26 s** |
| total latency | 84.6 s | 98.6 s |
| finish reason | `end_turn` | `end_turn` |
| route-reported cost | **$0.41305** | **$0.45951** |

**Total experiment spend: $0.87256** at list pricing ($10/$50 per MTok,
cache-write $12.50). Route ceiling 64,000 output tokens; neither run approached
it. Cost is recorded beside the scores and never folded into them.

TTFA is a real measurement here, not an estimate: the run harness reads the
`stream-json` event stream and takes TTFT from the first delta of any kind and
TTFA from the first `text_delta`, which is the same definition
`providers/base.py` documents. The ~47 s and ~53 s gaps between them are the
adaptive thinking phase, corroborated by the non-zero `thinking_tokens`.

`temperature` and `top_p` remain unsettable and unobservable on this route,
which is the main reason the two samples cannot be separated from noise.

---

## Descriptive position against the official board

**Both Fable figures are OFF-BENCHMARK / CLAUDE CODE ROUTE.** They were
generated through a contaminated harness with a different system prompt, no
sampling control and two samples instead of three. They are **not ranked**, and
no ordinal position is implied or available.

| | Model | Monday Score | Runs |
|---|---|---:|---:|
| — | *Fable 5.1 — RUN A, off-benchmark / Claude Code route* | *92.0* | *1* |
| — | *Fable 5.1 — RUN B, off-benchmark / Claude Code route* | *88.5* | *1* |
| 1 | Qwen 3.8 Flash | 94.8 | 3 |
| 2 | GLM 5.2 | 91.2 | 3 |
| 3 | DeepSeek V4 Flash | 89.3 | 3 |
| 4 | GLM 5.3 Flash | 87.3 | 3 |
| 5 | MIMO v2.5 | 81.2 | 3 |
| 6 | Qwen 3.6 | 70.2 | 3 |
| 7 | Gemma 4 | 54.2 | 3 |

Descriptively: both Fable samples land in the same band as the top three
published models, and neither is separated from GLM 5.2 (91.2) or DeepSeek V4
Flash (89.3) by more than the run-to-run spread those models show across three
runs. The published figures are means of three official runs under the frozen
conditions; these are single samples under a different harness. The two columns
are not comparable and the table above is a sighting, not a ranking.

One substantive observation that is comparable, because it is about content
rather than score: both Fable arms chose **Option A**, as did five of the seven
published models. `choose_option_b` is PARTIAL in both arms for the same reason
it is PARTIAL across most of the board — the ground truth wants B, chosen because
it is viable and materially lower risk. Only run A came close to demonstrating
that viability, and it still chose A.
