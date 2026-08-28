# MondayBench #003 "Blockers" — calibration, 2026-08-28

Scenario `monday-003` v0.1 · rubric 0.1 · evaluator `evaluator-opus5-v0.3-calibration`
· judge `claude-opus-5` · prompt `efd837502f417466…`

Seven models, one attempt each. **Not official, not frozen.**

`RECOMMENDATION: REVISE BEFORE FREEZE`

---

## Executive summary

The scenario works — it tests what it set out to test, and the failures it does
produce are the right kind. It is also **too easy**. Three of seven models
scored a flat 100, and no model triggered a single penalty.

| Signal | Target | Measured | |
|---|---|---|:--:|
| Top score | 82–90 | **100.0** (×3) | ✗ |
| Score spread | ≥ 25 | **20.0** | ✗ |
| Constant point mass | < 40 | **55.0** | ✗ |
| Penalties fired | — | **0 of 7 runs** | ✗ |

Ten of twenty criteria returned PASS for all seven models, including
`critical_path_identified` — the ten-point criterion the whole scenario is built
around. Every model reconstructed the chain correctly on the first attempt.

---

## Scores

| Model | Score | Penalties | Qualification |
|---|---:|---:|---|
| DeepSeek V4 Flash | **100.0** | 0 | valid, reasoning delivered |
| GLM 5.3 Flash | **100.0** | 0 | valid, reasoning delivered |
| Qwen 3.8 Flash | **100.0** | 0 | valid on attempt 3 — see below |
| GLM 5.2 | **98.5** | 0 | valid, reasoning delivered |
| MIMO v2.5 | **98.5** | 0 | valid, reasoning delivered via stream |
| Qwen 3.6 | **81.5** | 0 | valid, reasoning not requested |
| Gemma 4 | **80.0** | 0 | valid, reasoning not requested |

Spread 80.0 – 100.0 = **20.0**.

### Qwen 3.8 Flash needed three attempts

Attempts 1 and 2 came back with **zero reasoning tokens** — 1,456 and 1,481
output tokens in 14.7s and 16.0s, with TTFA equal to TTFT. The hardened
qualification rule rejected both as `REASONING_NOT_DELIVERED` and they are
preserved at `runs/monday-003/qwen3.8-flash/run-00{1,2}.json`. Attempt 3
delivered 11,525 reasoning tokens in 121s and is the sample scored here.

This is the same provider defect found in monday-002, and it is worse than that
one occurrence suggested: **two of three attempts** on this scenario. The guard
added last session did its job twice without being asked.

---

## Dimension breakdown

| Dimension | Max | DeepSeek | GLM 5.3 | Qwen 3.8 | GLM 5.2 | MIMO | Qwen 3.6 | Gemma 4 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Critical path & dependencies | 30 | 30.0 | 30.0 | 30.0 | 30.0 | 30.0 | 26.0 | 26.0 |
| Resource allocation | 20 | 20.0 | 20.0 | 20.0 | 20.0 | 20.0 | 17.5 | 20.0 |
| Planning & parallelization | 20 | 20.0 | 20.0 | 20.0 | 20.0 | 20.0 | 20.0 | 13.5 |
| Replanning | 15 | 15.0 | 15.0 | 15.0 | 15.0 | 15.0 | 8.0 | 13.0 |
| State reconstruction | 10 | 10.0 | 10.0 | 10.0 | 8.5 | 8.5 | 5.0 | 6.5 |
| Earliest delivery & uncertainty | 5 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 1.0 |

Five of six dimensions are maxed by five of seven models.

---

## Criterion matrix

`P` = PASS · `~` = PARTIAL · `F` = FAIL

| # | Criterion | Pts | DeepSeek | GLM 5.3 | Qwen 3.8 | GLM 5.2 | MIMO | Qwen 3.6 | Gemma 4 | Const |
|---:|---|---:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| 1 | `critical_path_identified` | 10 | P | P | P | P | P | P | P | **YES** |
| 2 | `marcus_bottleneck` | 7 | P | P | P | P | P | P | P | **YES** |
| 3 | `instrumentation_nonblocking` | 5 | P | P | P | P | P | P | P | **YES** |
| 4 | `security_not_blocking` | 4 | P | P | P | P | P | F | F | — |
| 5 | `hard_dependency_order` | 4 | P | P | P | P | P | P | P | **YES** |
| 6 | `contoso_delegated` | 6 | P | P | P | P | P | P | P | **YES** |
| 7 | `elena_risk_managed` | 5 | P | P | P | P | P | P | P | **YES** |
| 8 | `pricing_owner_and_mockups` | 5 | P | P | P | P | P | ~ | P | — |
| 9 | `board_work_owned_correctly` | 4 | P | P | P | P | P | P | P | **YES** |
| 10 | `monday_sequence` | 7 | P | P | P | P | P | P | ~ | — |
| 11 | `parallel_work` | 7 | P | P | P | P | P | P | P | **YES** |
| 12 | `board_pack_partial_parallelization` | 6 | P | P | P | P | P | P | ~ | — |
| 13 | `urgent_vs_critical` | 6 | P | P | P | P | P | P | P | **YES** |
| 14 | `pricing_cycle_detected_and_broken` | 5 | P | P | P | P | P | F | P | — |
| 15 | `stale_tasks_overridden` | 4 | P | P | P | P | P | ~ | ~ | — |
| 16 | `sso_current_state` | 4 | P | P | P | P | P | ~ | ~ | — |
| 17 | `contoso_current_state` | 3 | P | P | P | ~ | P | ~ | ~ | — |
| 18 | `onboarding_current_state` | 3 | P | P | P | P | ~ | ~ | P | — |
| 19 | `earliest_delivery` | 4 | P | P | P | P | P | P | F | — |
| 20 | `no_invented_blockers` | 1 | P | P | P | P | P | P | P | **YES** |

**Constant: 10 of 20 criteria, 55.0 of 100 points.** 45 points discriminate.

Every constant criterion is constant at PASS. Nothing is unreachable — the
problem is the opposite.

---

## Critical failures

The findings the brief asked to be reported specifically:

| Question | Answer |
|---|---|
| Who reconstructs the full critical path? | **All seven.** |
| Who identifies the Marcus bottleneck? | **All seven.** |
| Who lets Contoso hijack priority? | **Nobody.** All seven delegated it to Julia and kept it off the chain. |
| Who keeps instrumentation as a blocker? | **Nobody.** All seven released Marcus's three hours. |
| Who detects the pricing cycle? | Six of seven. Qwen 3.6 wrote a section headed "Circular/Stale Dependency" — about the *onboarding* task, never noticing the pricing loop. |
| Who breaks it with mockups? | The same six. |
| Who gets Tuesday delivery? | Six of seven. Gemma 4 answered "Wednesday EOD", reasoning that "the path is easily cleared before Wednesday" without ever asking whether Tuesday was reachable. |
| Who violates a dependency? | **Nobody.** |
| Who mishandles Elena/Daniel? | **Nobody.** All seven understood Daniel is a fallback needing the 30-minute permission transfer first. |
| Who freezes board revenue too early? | **Nobody.** |

Only two things separated the bottom two models from the rest:

- **`security_not_blocking`** — Qwen 3.6 and Gemma 4 never mention Security at
  all. The stale "unblock Security review" task is neither used nor rejected,
  and Maya's Friday approval never enters the reconstruction. This is the single
  most discriminating criterion in the scenario, and it is worth four points.
- **Gemma 4's Wednesday answer** on `earliest_delivery`.

---

## Why it is too easy

Three causes, in order of size.

**1. `work-items.csv` states the dependencies in a data column.** The
`business_context` field reads *"Required before Enterprise SSO regression"* and
*"Required before Enterprise SSO production rollout"*. The chain the model is
supposed to reconstruct from conversation is sitting in a spreadsheet column,
pre-labelled. This alone probably explains why `critical_path_identified` scored
7/7.

**2. `meetings.md` restates the chain as a tidy ordered list.** Slack has it as
five people talking across a thread; the meeting notes then summarise it into
four clean bullets in dependency order. The second copy removes the
reconstruction work that the first copy creates.

**3. The prompt asks for the answers by name.** Section 4 says *"including
circular, stale, or removable dependencies"*, which tells the model that a
circular dependency, a stale blocker and a removable dependency all exist and
should be hunted for. That was specified in the brief, and it is defensible as
an output format — but combined with (1) and (2) it leaves very little to find.

Beyond the leaks, the scenario has **no competition for the critical path**. The
SSO chain is the only multi-step dependency chain and the only dated external
commitment. There is nothing plausible for a model to mistake for it, so
identifying it correctly requires no judgement — only reading.

---

## Judge quality

No criterion looked wording-sensitive. Every label rested on a quotable
sentence, and the two FAILs (`security_not_blocking`, `pricing_cycle`) were
absences rather than interpretations — the word "Security" does not appear in
either response.

One criterion is **defective as written**, and it did not bite only by luck:

**`earliest_delivery`** accepts "Tuesday, around 12:00–13:30". Qwen 3.8 Flash
found a legitimately faster plan — QA starts Monday 16:10 the moment the patch
lands, finishes Tuesday morning, rollout by ~10:40 — which respects every
duration, every dependency and QA's stated Monday availability. It is a better
answer than the canonical one and falls **outside** the accept window. It was
graded PASS because marking a superior plan down would be perverse, but the
criterion should be rewritten to test dependency-respect rather than a clock
range.

---

## Ambiguities found

**1. `availability.csv` is incomplete, and silence is doing work.** Julia and
Sarah are listed for Monday only; QA for Monday and Tuesday. Sarah owns work due
Thursday and Friday. Absent rows are meant to read as "not recorded", but a
model could reasonably read them as "unavailable" and conclude the pricing page
cannot ship. No model did — but that is luck, not design.

**2. The work-item deadlines are internally inconsistent.** `api_compatibility_patch`,
`sso_regression` and `sso_production_rollout` all carry `2026-09-23T17:00`.
GLM 5.3 Flash spotted it: *"impossible sequentially (would finish ~20:00)"*. They
are meant to be the shared commitment date, not per-step deadlines, and nothing
says so.

**3. Backfill has no owner, duration or work item.** The board revenue section
depends on "migration/backfill", and five of seven models raised this as their
top unknown — correctly. It is a genuine gap in the scenario rather than a
designed one.

---

## Minimum changes required before freeze

Ordered by expected effect. Nothing here has been applied.

1. **Strip the dependency statements from `work-items.csv`.** Make
   `business_context` commercial only — *"Enterprise customer delivery"* is
   fine, *"Required before Enterprise SSO regression"* is the answer.
2. **Delete the SSO bullet list from `meetings.md`.** Keep the Slack thread as
   the single source of the chain. Optionally keep one meeting line that
   confirms the Wednesday commitment without re-deriving the order.
3. **Soften prompt section 4** to "BLOCKERS & DEPENDENCIES — what is really
   blocking, and what only appears to be", removing the enumeration of the three
   answer types.
4. **Add a competing chain.** A second workstream with an earlier deadline and a
   shorter dependency path — something that *looks* like the critical path until
   you count the hours — would make criterion 1 measure judgement instead of
   reading.
5. **Contest the bottleneck.** Have something genuinely pull at Marcus, with
   Julia's ownership of the Contoso fix requiring inference rather than being
   stated by Julia herself.
6. **Rewrite `earliest_delivery`** to score dependency-respect and a stated
   schedule, not a time window.
7. **Complete `availability.csv`** through Friday for everyone who has work due
   after Wednesday.
8. **Fix or explain the three identical Wednesday deadlines.**

Items 1–3 are removals and would take an hour. My expectation is that they alone
move the ceiling into the 88–94 band; items 4 and 5 are what would bring it to
the 82–90 target and give the penalty scale something to catch.

I have not applied any of them.

---

## Integrity

monday-001 and monday-002 are untouched: their frozen manifests still verify and
no run, evaluation, verdict or leaderboard of either was read-modify-written.
#003 is additive.

`RECOMMENDATION: REVISE BEFORE FREEZE`
