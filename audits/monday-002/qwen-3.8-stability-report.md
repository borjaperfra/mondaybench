# Audit — Qwen 3.8 Flash stability on MondayBench #002

**AUDIT / NON-OFFICIAL.** This document studies the official result. It does not
revise it. No official artefact was read-modify-written at any point; the
integrity check at the end lists the hashes.

Date: 2026-08-28 · Auditor: Claude Opus 5 in a recorded Claude Code session ·
Scope: `monday-002`, `qwen3.8-flash`, runs 001–003.

---

## Executive conclusion

`RESULT IS CONFOUNDED BY PROVIDER/CONFIG VARIANCE`

Run 002 was served **without the reasoning phase** that runs 001 and 003 used —
0 reasoning tokens against 42,808 and 30,342 — and the provider also returned a
different input token count and a different response schema for it. The three
runs are therefore not three samples of the same system. The 33.5-point range is
real and correctly scored, but it is not a measurement of "how variable Qwen 3.8
Flash is at this task"; it is substantially a measurement of the difference
between Qwen-with-thinking and Qwen-without-thinking.

Judge instability is **not** implicated: all eight volatile criteria trace to
quoted, observable differences in the response text, and the same standards were
applied consistently across all 21 runs of the battery.

## Official scores — unchanged

| Run | Score |
|---|---:|
| 001 | 93.0 |
| 002 | 66.5 |
| 003 | 100.0 |
| **Monday Score** | **86.5** |

Range 33.5. These numbers are correct and stand.

---

## 1. Run conditions

`RUN CONDITIONS NOT EQUIVALENT`

| Parameter | Run 001 | Run 002 | Run 003 | Equal? |
|---|---|---|---|:--:|
| model_id | `qwen3.8-flash` | `qwen3.8-flash` | `qwen3.8-flash` | ✅ |
| provider | `nan` | `nan` | `nan` | ✅ |
| api_style | `openai_compatible` | `openai_compatible` | `openai_compatible` | ✅ |
| endpoint | `NAN_BASE_URL` | `NAN_BASE_URL` | `NAN_BASE_URL` | ✅ (env name only) |
| temperature | 0.0 | 0.0 | 0.0 | ✅ |
| top_p | not sent, not recorded | idem | idem | **UNKNOWN** |
| max_output_tokens | 32000 | 32000 | 32000 | ✅ |
| extra_body | `{caching: false}` | idem | idem | ✅ |
| reasoning **requested** | never sent — see note | never sent | never sent | ✅ |
| reasoning **delivered** | 42,808 tok | **0 tok** | 30,342 tok | ❌ |
| reasoning effort | no such parameter | — | — | n/a |
| system_prompt_sent | true | true | true | ✅ |
| system prompt text | not stored in the run | idem | idem | **UNKNOWN** |
| rendered prompt SHA-256 | `740e627c…` | `740e627c…` | `740e627c…` | ✅ |
| **input_tokens** | 2,723 | **2,687** | 2,723 | ❌ |
| output_tokens | 44,910 | 2,189 | 33,714 | (consequence) |
| answer tokens | 2,102 | 2,189 | 3,372 | — |
| `completion_tokens_details.text_tokens` | present | **absent** | present | ❌ |
| finish_reason | `stop` | `stop` | `stop` | ✅ |
| TTFT | 2,026 ms | 1,600 ms | 1,568 ms | ✅ |
| TTFA | 365,305 ms | **1,600 ms** | 258,914 ms | ❌ |
| total latency | 380.0 s | **19.6 s** | 285.0 s | ❌ |
| scenario_version / rubric | 0.2 / 0.2 | 0.2 / 0.2 | 0.2 / 0.2 | ✅ |
| benchmark_version | 0.2 | 0.2 | 0.2 | ✅ |
| timestamp (completion) | 13:45:37Z | 13:45:57Z | 13:50:42Z | sequential |
| retries / failed attempts | none | none | none | ✅ |
| truncation | none | none | none | ✅ |
| provider warnings | none | none | none | ✅ |
| unsupported_parameters | `[]` | `[]` | `[]` | ✅ |

**Note on "reasoning requested".** `generation.reasoning_enabled: true` in the
run record is copied from `capabilities.reasoning` in `models.yaml`. It is a
*declared capability*, not a parameter the harness sends — `models.yaml` says
this model "thinks by default". So the field is not evidence that thinking was
enabled for a given request, and it read `true` for run 002 even though no
thinking happened. **This is a harness defect: the run record asserts a
condition it never verified.**

**Two `UNKNOWN`s.** `top_p` is never sent and never recorded, so equality cannot
be demonstrated — the provider's default applied, and whether that default was
stable across three requests is unknowable from the stored evidence. The system
prompt is recorded only as the boolean `system_prompt_sent`; its text is not
stored in the run, so byte-equality across runs cannot be proven from the
artefacts alone (it is built deterministically from the frozen scenario, which
makes a difference unlikely, but that is inference, not evidence).

---

## 2. Raw response comparison

Read independently of the evaluations.

| Behaviour / fact | Run 1 — 93.0 | Run 2 — 66.5 | Run 3 — 100.0 |
|---|---|---|---|
| Release option chosen | **A** | **A** | **B** |
| Reason given | "B is not reliably viable on current evidence… no evidence the 2.9.5 diff is already submitted" | "90m total… If started at 09:15, completion is ~10:45… too tight" | "reduces session-reset risk from 8% to <1% and can still meet the 12:00 window if started immediately" |
| Async delta review understood | Yes — names Priya's pre-10:25 window | Yes in the abstract ("25m async delta review"), but never used | Yes, and acted on |
| Priya 09:00–09:35 | Correct | Correct, after a visible self-correction | Correct |
| Priya unavailable 09:35–10:25 | Correct | Correct | Correct |
| Marcus 09:15–10:20 | Correct | Correct | Correct |
| Chain start anchored at | 09:15 (Marcus) | 09:15 (Marcus) | **09:07/09:08 (diff submission)** |
| Proposed schedule | A: 09:15–09:35 deploy, 10:25–10:45 verify, 10:45–11:00 Sam | same A schedule | B: review→09:32, deploy 09:32–10:17, verify 10:25–10:45, Sam 10:45–11:00 |
| Schedule executable? | Yes | Yes | Yes |
| Rollout time | ~11:00 | ~11:00 | ~11:00 |
| Atlas deadline handling | "Do not promise Atlas a 10:30 launch"; update gated on "If deploy is healthy" | **"Migration confirmed for today. Rollout begins shortly"** sent 09:45 | "Do not confirm launch at 10:30"; 11:00 given as a gated expectation |
| €54k reconciliation | Closed: 18+12+10+14 | Closed, Acme explicitly excluded | Closed, full per-account table |
| Wayne | −18k, signed amendment | −18k, "Cause: Contractual" | −18k, amendment |
| Globex | Top revenue risk, all four signals | **Priority 4, "Monitor"**, ticket severity only | Top risk, all four signals |
| Soylent / Wonka | Both worked, no cause invented | Both in the board pack, no cause invented | Both worked, no cause invented |
| Acme | "Monitor only… explained" | "Exclude from expansion gap calculation" | "do not escalate usage decline as a risk" |
| Orion | Org ID + live flag, no reply | Org ID + live flag, no reply | Org ID + live flag, no reply |
| **Pricing authority** | Pinned workbook **not** authoritative; Daniel's values internal-only | **Inverted**: "pinned workbook … is authoritative internally", Daniel's values "obsolete/incorrect" | Pinned **not** authoritative; Daniel's values internal-only |
| Zenith | Stale, cancelled | Stale, cancelled | Stale, cancelled |
| Launch comms ownership | Daniel, with Sarah's handoff traced | Daniel, handoff not traced | Daniel, with Sarah's handoff traced |
| Invented causality | none | none (hedged "may impact") | none |
| Uncertainty preserved | Yes, 6 MUST VERIFY items | Yes, 3 items | Yes, 10 items |
| Structure | prose, 7,894 chars | tables, 7,559 chars | tables, 12,115 chars |

Three material regressions in run 2: the inverted pricing authority, the
unconditional Atlas message, and Globex demoted to fourth with half its evidence
dropped. All three are visible in the text and none is a matter of judgement.

---

## 3. Where the 33.5 points come from

| Criterion | Pts | R1 | R2 | R3 | R3 − R2 |
|---|---:|:--:|:--:|:--:|---:|
| `schedule_feasibility` | 6 | ~ | F | P | **+6.0** |
| `pricing_authority` | 5 | P | F | P | **+5.0** |
| `choose_option_b` | 8 | ~ | ~ | P | **+4.0** |
| `customer_signal_integration` | 6 | P | ~ | P | **+3.0** |
| `conditional_launch_timing` | 3 | P | F | P | **+3.0** |
| `launch_state` | 5 | P | ~ | P | **+2.5** |
| `ownership_supersession` | 5 | P | ~ | P | **+2.5** |
| `globex_priority` | 5 | P | ~ | P | **+2.5** |
| *(12 further criteria)* | 52 | P | P | P | 0.0 |
| **Criterion subtotal** | | | | | **+28.5** |
| Penalty (`MATERIAL_HALLUCINATION`, pricing inversion) | | 0 | −5 | 0 | **+5.0** |
| **Total** | | 93.0 | 66.5 | 100.0 | **+33.5** |

### By dimension

| Dimension | Max | R1 | R2 | R3 | Gap | % of 33.5 |
|---|---:|---:|---:|---:|---:|---:|
| planning_dependencies | 25 | 18.0 | 15.0 | 25.0 | 10.0 | 29.9% |
| temporal_supersession | 15 | 15.0 | 7.5 | 15.0 | 7.5 | 22.4% |
| penalties | — | 0.0 | −5.0 | 0.0 | 5.0 | 14.9% |
| cross_source_data_reasoning | 15 | 15.0 | 12.0 | 15.0 | 3.0 | 9.0% |
| uncertainty_epistemic | 10 | 10.0 | 7.0 | 10.0 | 3.0 | 9.0% |
| state_reconstruction | 15 | 15.0 | 12.5 | 15.0 | 2.5 | 7.5% |
| decision_prioritization | 20 | 20.0 | 17.5 | 20.0 | 2.5 | 7.5% |

**What run 2 lost that run 3 got right:** it inverted the pricing source
authority (−5 criterion, −5 penalty = 10 points from one sentence), never
committed a viable Option B schedule and mis-anchored the arithmetic (−6), chose
A over B (−4), sent Atlas an unconditional confirmation (−3), and thinned its
customer analysis (−8 across three criteria).

---

## 4. Criterion volatility, classified

Eight of twenty criteria change across the three runs. Each was re-read against
the raw text.

| Criterion | R1 | R2 | R3 | Class | Basis |
|---|:--:|:--:|:--:|:--:|---|
| `pricing_authority` | P | F | P | **A** | R2 states the opposite of Daniel's email; R1/R3 state it correctly. Binary, textual. |
| `conditional_launch_timing` | P | F | P | **A** | R2 sends "Rollout begins shortly" at 09:45; R1/R3 explicitly refuse to promise. |
| `schedule_feasibility` | ~ | F | P | **A** | R3 commits 09:32–10:17; R2 asserts a wrong computation; R1 names constraints and defers. Three distinct behaviours. |
| `choose_option_b` | ~ | ~ | P | **A** | R3 chooses B on the risk comparison; R1/R2 choose A. |
| `globex_priority` | P | ~ | P | **A** | R2 ranks Globex 4th and omits renewal window and usage/admin; R1/R3 carry all four signals. |
| `customer_signal_integration` | P | ~ | P | **A** | R2 handles Globex on ticket severity alone. |
| `launch_state` | P | ~ | P | **A** | R2's premature Atlas confirmation is the single stale implication. |
| `ownership_supersession` | P | ~ | P | **A** | R1/R3 name Sarah's handoff; R2 names only Daniel. |

**All eight are Type A — genuine candidate difference. Zero Type B, C or D.**

### Cross-battery consistency check

Judge stochastic variance cannot be sampled here (§5). What *can* be measured
from official data is whether the same behaviour received the same label across
all 21 runs. For each volatile criterion the equivalence classes hold:

| Criterion | Battery spread | Is run 2's label consistent with the rest? |
|---|---|---|
| `pricing_authority` | 20 P / 1 F | Run 2 is the **only** response in 21 that inverted the authority. Unique behaviour, unique label. |
| `ownership_supersession` | 7 P / 14 ~ | All 14 PARTIALs carry the *identical* evidence string. The split is decided by one observable fact — whether Sarah's handoff is traced. |
| `conditional_launch_timing` | 12 P / 4 ~ / 5 F | All 5 FAILs are unconditional external commitments; all 4 PARTIALs communicate an ETA pre-verification but reject 10:30. Cleanly separated. |
| `schedule_feasibility` | 4 P / 4 ~ / 13 F | PASS = committed viable B schedule; PARTIAL = constraints understood, none committed; FAIL = asserted infeasibility or unexecutable plan. No exceptions. |
| `choose_option_b` | 4 P / 17 ~ | PASS only for the four runs that chose B *and* showed it viable. |
| `globex_priority` | 12 P / 9 ~ | All 9 PARTIALs omit the usage/admin signals. |
| `customer_signal_integration` | 17 P / 4 ~ | All 4 PARTIALs drop one required account comparison. |
| `launch_state` | 14 P / 3 ~ / 4 F | PARTIAL = one stale implication; FAIL = Maya's gate absent *and* a stale launch time revived. |

**No contradiction found in 21 runs × 8 criteria.** That is not proof of judge
determinism, but it is direct evidence that the standards were applied uniformly.

---

## 5. Judge re-evaluation — NOT PERFORMED

The requested 3 × 5 = 15 independent re-evaluations were **not run**, for one
reason:

> **Using an Anthropic API key or Anthropic API credits is prohibited on this
> project.** All judging is done by Claude Code on the user's subscription.

That is a hard rule, not a budget preference or a missing credential. Since the
only route to *independent* judge samples is a fresh-context API call, judge
stochastic variance is **not measurable within the rules of this project**.

The alternative — me re-judging the same three responses five times in this same
session — would not measure anything. I produced the official labels and have
them in context; the result would be a near-perfect agreement rate that reflects
anchoring, not judge stability. Reporting "range 0.0" from that exercise would
be worse than reporting nothing, because it would look like evidence.

What is reported instead is the cross-battery consistency analysis in §4, which
uses only official artefacts and answers a narrower but real question: *are
equivalent behaviours labelled equivalently?* Across 21 runs and the 8 volatile
criteria, yes, without exception.

**Open, if the user ever wants the stochastic measurement:** it needs a judge
that can be sampled in fresh contexts under the no-API rule. No such route
exists today.

## 6. Judge variance — UNMEASURED

Not measurable under the project rules. See §5.

## 7. Candidate vs judge variance

| Quantity | Value | Basis |
|---|---:|---|
| Between-response spread (official) | **33.5 points** | 66.5 → 100.0 |
| …attributable to quoted textual differences | **33.5 points** | all 8 volatile criteria are Type A |
| …attributable to demonstrated judge inconsistency | **0.0 points** | no contradiction in 21 × 8 |
| Within-response judge range | **not measurable** | §5 |
| Reasoning-mode split (r2 vs mean of r1, r3) | **30.0 points** | 66.5 vs 96.5 |

Read carefully: "0.0 points attributable to judge inconsistency" is a statement
about *consistency*, not about *variance*. It means no case was found where the
judge treated equivalent text differently. It does not mean a repeated judging
pass would return identical numbers, which is untested.

The stronger and better-supported decomposition is not candidate-vs-judge at
all. It is **thinking vs no-thinking**: the two runs served with a reasoning
phase scored 93.0 and 100.0 (mean 96.5); the one served without scored 66.5.

---

## 8. Option B analysis

The viable chain the ground truth describes:

`09:07 diff submitted → ~09:32 delta review done → 09:32–10:17 Marcus deploys B
→ 10:25–10:45 Priya verifies → 10:45–11:00 Sam opens → ~11:00 rollout`

| Element | Run 1 | Run 2 | Run 3 |
|---|:--:|:--:|:--:|
| Knows delta review can be async | ✅ | ✅ (stated, unused) | ✅ |
| Priya 09:00–09:35 available | ✅ | ✅ | ✅ |
| Priya 09:35–10:25 unavailable | ✅ | ✅ | ✅ |
| Marcus 09:15–10:20 | ✅ | ✅ | ✅ |
| 25m review / 45m deploy / 20m verify / 15m Sam | ✅ | ✅ | ✅ |
| Atlas before 12:00 | ✅ | ✅ | ✅ |
| 8% A vs <1% B | ✅ stated | ✅ stated | ✅ **used to decide** |
| **Starts the chain at diff submission, not at Marcus's arrival** | ❌ | ❌ | ✅ |
| Commits a viable B schedule | ❌ | ❌ | ✅ |
| **Discovers the chain** | ❌ | ❌ | ✅ |

**Run 2's specific failure** — it did *not* fail by missing the async review, and
it did *not* misread anybody's availability. Both were stated correctly. It
failed on **where the chain begins**: it anchored the 90-minute B sequence at
09:15, Marcus's arrival, and concluded "completion ~10:45… too tight". The
review does not need Marcus; it runs 09:07–09:32, before he arrives. Run 1 made
the same anchoring error and additionally treated "is the diff submitted?" as an
external unknown rather than an action available at 09:07. Run 3 alone saw that
submitting the diff is the user's own first move.

So on Option B, runs 1 and 2 fail the same way. **Option B is not where the
33.5-point gap comes from** — it accounts for 10 of the 33.5. The rest is the
pricing inversion, the Atlas promise and the thinned customer analysis, none of
which run 1 got wrong.

---

## 9. Reasoning vs final answer

| Run | Reasoning tok | Answer tok | Total out | Chars | TTFA | Latency | Score |
|---|---:|---:|---:|---:|---:|---:|---:|
| 001 | 42,808 | 2,102 | 44,910 | 7,894 | 365.3 s | 380.0 s | 93.0 |
| 002 | **0** | 2,189 | 2,189 | 7,559 | 1.6 s | 19.6 s | 66.5 |
| 003 | 30,342 | 3,372 | 33,714 | 12,115 | 258.9 s | 285.0 s | 100.0 |

No private reasoning content was read or reproduced — only token counts.

The cleanest observation in the whole audit: **runs 1 and 2 produced almost the
same amount of final answer** (2,102 vs 2,189 tokens; 7,894 vs 7,559 characters)
and scored 26.5 points apart. Answer length does not explain the gap. The one
input that differs by orders of magnitude is the reasoning phase, and its
presence tracks the score exactly: 42,808 → 93.0, 0 → 66.5, 30,342 → 100.0.

Latency and TTFA track reasoning, not quality, and are not independent signals.

---

## 10. Provider variance

`CONFIRMED CONFIGURATION DIFFERENCE` (provider-side)

Five independent indicators, all pointing the same way for run 002:

1. **Zero reasoning tokens.** Across every reasoning-enabled run in this
   repository — 40+ runs, 2 scenarios, 7 models, 4 archived batteries — the only
   official run with `reasoning_tokens: 0` is this one. The only other
   zero-reasoning runs anywhere in the repo sit in `archive/cache-hits/`, a
   directory the project already quarantined as invalid data.
2. **Different input token count for a byte-identical prompt.** 2,687 against
   2,723 for runs 1 and 3, same `740e627c…` prompt. A 36-token difference in how
   the provider counted the *same* input implies a different template or
   serving path.
3. **Different response schema.** `completion_tokens_details.text_tokens` is
   present in every `qwen3.8-flash` run in the repository — monday-001,
   monday-002 and all archives — and absent only here.
4. **TTFA equals TTFT** (1,600 ms). There was no thinking phase to wait through.
5. **Latency 19.6 s** against 380.0 s and 285.0 s.

`models.yaml` records that this model "thinks by default"; the harness never
sends a thinking parameter, so it cannot force the behaviour and cannot detect
its absence. Run 002 arrived 20 seconds after run 001 completed — a 44,910-token
generation — which is consistent with provider-side throttling or routing to a
cheaper path, though the artefacts cannot prove the mechanism.

**Our side was identical.** Same model id, same endpoint variable, same
temperature, same budget, same `extra_body`, same prompt bytes. The difference
was introduced by the provider, and the harness recorded
`reasoning_enabled: true` regardless.

### Harness defects found

1. **`generation.reasoning_enabled` is unverified.** It copies a declared
   capability into the run record as if it were an observed condition. It should
   record what was *requested* and, separately, what was *delivered*.
2. **Run qualification does not check reasoning delivery.** `qualify_run`
   already rejects truncation, empty responses, prompt-hash drift and duplicate
   responses. A reasoning model returning zero reasoning tokens is the same
   class of defect as the cache hits it already catches, and it passes today.
3. **`top_p` and the system prompt text are not recorded**, so run equivalence
   cannot be fully demonstrated from the artefacts.
4. **Unrelated, found during this audit: `core.autocrlf=true`.** A plain
   `git checkout` of any tracked file rewrites LF as CRLF and changes its
   bytes. For a repository whose value is byte-level auditability this is a live
   corruption vector; it hit an official evaluator file during this audit and
   was restored exactly. A `.gitattributes` pinning `eol=lf` would close it.

---

## 11. Recommendation

`RECOMMENDATION: C — INVESTIGATE PROVIDER/HARNESS BEFORE #003`

Option C's stated trigger is "the runs were not comparable; there is evidence of
routing/config/truncation/failure that explains the difference". That is exactly
what was found.

Not A, because the runs were not comparable — and the harness cannot currently
detect that, so #003 would inherit the same blind spot on every reasoning model.
Not B, because no judge instability was found: every volatile criterion traces
to quoted text and the standards were applied uniformly across 21 runs.

Suggested before #003, in order:

1. Record requested-vs-delivered reasoning separately in the run schema.
2. Extend `qualify_run` to reject a run from a `reasoning: true` model that
   returns zero reasoning tokens, the same way cache hits are rejected.
3. Record `top_p` and the system prompt hash.
4. Add `.gitattributes` with `* text=auto eol=lf`.
5. Only then decide whether Qwen 3.8 Flash's #002 result should carry a
   footnote. **It should not be rescored** — the response was real, the score is
   correct, and rescoring on a technicality would be exactly the kind of
   post-hoc adjustment the publication gates exist to prevent.

### What this does and does not say about Qwen 3.8 Flash

It does not say the model is unreliable. Served with thinking it scored 93.0 and
100.0 — the highest single score in the battery. It says that one of its three
official runs measured a different system, and that the published range of 33.5
overstates its run-to-run variability as a reasoning model.

---

## 12. Official benchmark integrity

All 194 official artefacts hashed before and after this audit: **unchanged.**

| Artefact | SHA-256 (first 16) |
|---|---|
| `leaderboard/monday-002/leaderboard.json` | `bf2d281891887b54` |
| `scenarios/monday-002/rubric.yaml` | `20d87091fdd9472e` |
| `scenarios/monday-002/ground_truth.md` | `8a53e5f98c5285a4` |
| `scenarios/monday-002/prompt.md` | `4550728d7edac215` |
| `scenarios/monday-002/FROZEN.yaml` | `ddbc2ae862316cc3` |
| `evaluators/evaluator-opus5-v0.2.yaml` | `e119c4c32c0a4238` |
| rendered prompt | `740e627cbc7413c321ede0d54000504de54821d34ff4677f82731b89600423a8` |

21 raw runs, 21 official evaluations, 7 verdict files, the scenario, the rubric,
the ground truth, the prompt and the leaderboard are all byte-identical to their
pre-audit state. This audit added files only under `audits/`.

One near-miss, disclosed: while documenting the no-API rule I added a comment to
`evaluators/evaluator-opus5-v0.2.yaml`, then reverted it — and the revert
rewrote the file with CRLF, changing its bytes. It was restored to the exact
original with `git -c core.autocrlf=false checkout`, and the hash above matches
the pre-audit baseline. That is finding 4 in §10.

`OFFICIAL MONDAYBENCH #002 RESULTS UNCHANGED`

`RECOMMENDATION: C — INVESTIGATE PROVIDER/HARNESS BEFORE #003`
