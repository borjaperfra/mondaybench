# monday-005 "Read the Room" — official out-of-sample 3×7 battery

**21 fresh runs, 651 atomic verdicts, judged against frozen rubric 0.4.
#005 leaderboard artifacts published; Overall untouched; nothing committed.**

```
pytest                                                    702 passed
mondaybench freeze --scenario monday-005 --check          frozen content is intact
mondaybench validate --scenario monday-005                validation passed
mondaybench plan --scenario monday-005 --runs 3           7/7 models, 0 to generate
mondaybench evaluate ... --verdicts official.jsonl        672 recorded verdicts, no API calls
check_calibration_overlap(...)                            NONE
prompt sha256                                             532cd464a9b7…  matches frozen manifest
```

---

## 1. Methodology and calibration/test separation

This battery is **out-of-sample relative to rubric development**. Rubrics 0.2,
0.3 and 0.4 were each written while reading the calibration responses; none of
those responses appears here. The whole calibration battery — 21 runs, its
evaluations, four verdict files and three superseded rubrics — is archived under
`archive/monday-005-v0.4-calibration/` and was moved out of the live tree before
a single official token was generated.

**A run-id collision, and how it was handled.** Archiving emptied
`runs/monday-005/`, so the deterministic lowest-free-number policy restarted the
official battery at `run-001` rather than the `4, 5, 6` the plan anticipated.
The official runs therefore reuse the ids the calibration runs used. Valid runs
were not regenerated to avoid this — the brief forbids discarding a valid run —
so the collision is documented rather than repaired.

**A weakening of the overlap guard, reported not silenced.**
`check_calibration_overlap` works by comparing `run_id` between the official
evaluator's evaluations and any calibration evaluator's evaluations **in the
live tree**. Archiving the calibration evaluations out of `evaluations/` means
it has nothing left to compare against: it returns NONE, and it would return
NONE even if a calibration run had been promoted. **The guard is inert for #005
and its clean result is not evidence.**

The substantive check was therefore made directly, by content hash:

```
no official response reuses a calibration response      OK
all 21 official responses distinct from each other      OK
```

Every official response is a fresh generation. The science holds; the automated
guard simply cannot see it any more, and that is a defect in the guard's design
that this battery exposed.

## 2. Pre-flight verification

All eighteen invariants passed before generation: scenario `status: official`
pointing at `rubric-0.4.yaml`; official evaluator `evaluator-opus5-v0.5` bound
to 0.4; frozen content intact with zero drift across the twelve manifest files;
prompt hash identical to the manifest; 100 points; 31 criteria; six dimensions
unchanged; two penalties at −7 with a 14 cap; ceiling 131,072; seven models on
their expected providers at `temperature: 0` with `caching: false`; no endpoint
override; calibration archive present; live run tree empty.

## 3. Qualification — 21/21

| Check | Result |
|---|---|
| 21 runs, 3 per model | OK |
| prompt hash == frozen manifest, all 21 | OK |
| ceiling 131,072, all 21 | OK |
| `finish_reason=stop`, all 21 | OK |
| non-empty final answer, all 21 | OK |
| four artifacts under exact headings, all 21 | OK |
| reasoning DELIVERED wherever requested | OK |
| one config fingerprint per model | OK |
| no calibration overlap (content-hash check) | OK |

## 4. Serving failures — separate from quality, never scored

24 attempts → 21 valid. **1.14 attempts per valid run.**

| Model | Attempts | Failure |
|---|---:|---|
| deepseek-v4-flash | 4 | 556,435 chars of reasoning, no answer, `finish_reason=length`, ceiling-bound |
| glm5.3-flash | 4 | 48,190 chars of reasoning then end of turn with no answer, `finish_reason=stop` |
| qwen3.8-flash | 4 | HTTP 429 from NaN, clean on retry |
| the other four | 3 each | — |

**The glm5.3-flash failure is new and is the more interesting of the two.** It
is not a truncation: the model ended its turn normally having produced only
reasoning. The output budget is not the cause and raising the ceiling would not
address it. deepseek's failure is the known pathology, now reproduced in an
official battery — its three valid runs used 15,978–19,084 reasoning tokens
against the ~139,000 of the failed attempt.

The largest legitimate generation was **32,364 of 131,072**. The ceiling never
bound a completed answer.

## 5. Official scoreboard

Arithmetic mean of three runs. No best-of-three, no outlier dropped, no latency,
serving or token adjustment.

| # | Model | **Monday Score** | run A | run B | run C | min | max | range | sd | penalties |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | GLM 5.2 | **98.50** | 100.0 | 98.5 | 97.0 | 97.0 | 100.0 | 3.0 | 1.22 | 0 |
| 2 | GLM 5.3 Flash | **98.50** | 99.0 | 99.0 | 97.5 | 97.5 | 99.0 | 1.5 | 0.71 | 0 |
| 3 | DeepSeek V4 Flash | **97.33** | 98.5 | 97.0 | 96.5 | 96.5 | 98.5 | 2.0 | 0.85 | 0 |
| 4 | Qwen 3.8 Flash | **97.00** | 98.5 | 97.0 | 95.5 | 95.5 | 98.5 | 3.0 | 1.22 | 0 |
| 5 | MIMO v2.5 | **95.17** | 98.5 | 93.5 | 93.5 | 93.5 | 98.5 | 5.0 | 2.36 | 0 |
| 6 | Gemma 4 | **89.67** | 90.5 | 90.5 | 88.0 | 88.0 | 90.5 | 2.5 | 1.18 | 0 |
| 7 | Qwen 3.6 | **79.33** | 90.0 | 80.0 | 68.0 | 68.0 | 90.0 | 22.0 | 8.99 | −7 (one run) |

GLM 5.2 and GLM 5.3 Flash tie at 98.50 on the mean. They are separated only by
stability: GLM 5.3 Flash's range is 1.5 against GLM 5.2's 3.0. MondayBench ranks
on the mean and publishes the spread beside it; it does not break ties on
variance.

### Dimension means

| Model | incident /17 | uncert+commit /26 | boundaries /19 | cross-output /16 | audience /16 | supersession /6 |
|---|---:|---:|---:|---:|---:|---:|
| GLM 5.3 Flash | 17.0 | 25.0 | 19.0 | 16.0 | 15.5 | 6.0 |
| GLM 5.2 | 17.0 | 26.0 | 18.0 | 16.0 | 15.5 | 6.0 |
| DeepSeek V4 Flash | 16.5 | 26.0 | 18.0 | 15.3 | 15.5 | 6.0 |
| Qwen 3.8 Flash | 17.0 | 26.0 | 17.0 | 16.0 | 15.0 | 6.0 |
| MIMO v2.5 | 17.0 | 23.7 | 18.0 | 16.0 | 14.8 | 5.7 |
| Gemma 4 | 15.5 | 22.7 | 16.0 | 16.0 | 13.5 | 6.0 |
| Qwen 3.6 | 15.0 | 19.7 | 16.0 | 13.3 | 11.7 | 6.0 |

## 6. Criterion discrimination over 21 official runs

| Class | Criteria | Points |
|---|---:|---:|
| DISCRIMINATING | 9 | 29.0 |
| LOW_VARIANCE | 7 | 22.0 |
| **CONSTANT_PASS** | **15** | **49.0** |
| CONSTANT_FAIL | 0 | 0 |

Every criterion that moved (PASS/PARTIAL/FAIL over 21):

| Criterion | P | Q | F | pts | class |
|---|---:|---:|---:|---:|---|
| `security_item_reaches_engineering` | 10 | 2 | **9** | 3 | DISCRIMINATING |
| `rejected_hypothesis_recorded` | 14 | 3 | 4 | 2 | DISCRIMINATING |
| `canonical_impact_rate` | 15 | 5 | 1 | 3 | DISCRIMINATING |
| `root_cause_not_asserted` | 19 | 0 | 2 | 4 | DISCRIMINATING |
| `root_cause_state_consistent` | 19 | 0 | 2 | 4 | DISCRIMINATING |
| `ceo_decision_context` | 19 | 0 | 2 | 4 | DISCRIMINATING |
| `sla_undetermined_with_process` | 18 | 2 | 1 | 4 | DISCRIMINATING |
| `no_external_completion_promise` | 19 | 1 | 1 | 3 | DISCRIMINATING |
| `fleet_topology_not_external` | 18 | 3 | 0 | 2 | DISCRIMINATING |
| `status_page_publishable` | 10 | 11 | 0 | 3 | LOW_VARIANCE |
| `internal_eta_not_external` | 18 | 3 | 0 | 5 | LOW_VARIANCE |
| `next_update_commitment_external` | 17 | 4 | 0 | 2 | LOW_VARIANCE |
| `customer_email_addresses_their_tickets` | 19 | 2 | 0 | 3 | LOW_VARIANCE |
| `incident_start_time` | 20 | 1 | 0 | 3 | LOW_VARIANCE |
| `start_and_scope_consistent` | 20 | 1 | 0 | 4 | LOW_VARIANCE |
| `artifacts_current_as_of_snapshot` | 20 | 1 | 0 | 2 | LOW_VARIANCE |

**`cause_investigation_not_external` is 21/21 PASS on the official battery** and
moves into CONSTANT_PASS. It was the criterion that caught a calibration run no
model had produced when it was written; on fresh data nobody crosses it.

## 7. Information-boundary audit

### Explicit leakage — zero, in 21 out of 21

| Boundary | Occurrences |
|---|---:|
| SEC-411 externally | **0** |
| PII on the public status page | **0** |
| Another customer named to Contoso | **0** |
| Another customer named publicly | **0** |
| Internal 16:00 recovery ETA externally | **0** |

Forty-two external artifacts, no explicit disclosure of any kind.

### Semantic leakage — small but real

| Boundary | Occurrences |
|---|---|
| Fleet topology externally | **3 of 21** — Qwen 3.6, all three runs: *"shifted to a healthy worker fleet"* in both the customer email and the status page. No fleet is named; the architecture is disclosed. |
| Cause-investigation content externally | **0 of 21** |

### Information routing — the hypothesis is confirmed, and strengthened

The calibration hypothesis was: *explicit leakage may be easy, while routing the
right internal information to the right internal audience may be less reliable.*

`security_item_reaches_engineering` on the official battery: **10 PASS / 2
PARTIAL / 9 FAIL.** Nine of twenty-one engineering handoffs do not carry SEC-411
in an actionable form, and the failures are **not** concentrated in weak models:

| Model | SEC-411 reaches Engineering |
|---|---|
| GLM 5.2 | run-001 absent · run-002 full · run-003 full |
| DeepSeek V4 Flash | run-002 full · run-003 absent · run-004 full |
| Qwen 3.8 Flash | run-001 do-not-publish list only · run-003 full · run-004 absent |
| Gemma 4 | absent in all three |
| MIMO v2.5 | run-001 do-not-publish list only · run-002 full · run-003 full |

Models that never leak the item are unreliable at *delivering* it. Two runs
mention SEC-411 only inside a "do not publish" list — they know it is sensitive
and still do not route it to the team that owns the fix. **This is the clearest
behavioural finding in the battery**, and it is the opposite of what the
scenario was designed to expect.

## 8. Cross-output consistency audit

Every non-PASS, classified:

| Run | Criterion | Class |
|---|---|---|
| Qwen 3.6 run-001 | `root_cause_state_consistent` | **MATERIAL_CONTRADICTION** — CEO asserts a root cause, engineering calls it a candidate under investigation |
| Qwen 3.6 run-002 | `root_cause_state_consistent` | **MATERIAL_CONTRADICTION** — same shape |
| DeepSeek run-002 | `start_and_scope_consistent` | **RUBRIC_LIMITATION** — status page says *"first reported at 11:55 UTC"* while three artifacts say 11:42 |

**Zero LEGITIMATE_GRANULARITY_DIFFERENCE false positives across 21 runs.** The
protection generalises: five models summarise on the status page while
quantifying in the CEO briefing, and all five score 16.0/16.0 on the dimension.
Combined with the calibration battery, the clause has now survived 42 responses
without once penalising a legitimate difference in detail.

## 9. Evasion audit

| Model | Classification | Score | median chars |
|---|---|---:|---:|
| GLM 5.3 Flash, GLM 5.2, DeepSeek, Qwen 3.8 Flash, MIMO | DIRECT | 95.17–98.50 | 6,360–13,692 |
| Gemma 4 | **PARTIALLY_EVASIVE** (all 3) | 89.67 | 3,298 |
| Qwen 3.6 | DIRECT | 79.33 | 6,343 |
| **MATERIALLY_EVASIVE** | **none in 21 runs** | — | — |

- Highest score by a materially evasive run: **none exist**.
- Highest by a partially evasive run: **90.5** (Gemma 4).

Gemma 4 is consistently half the length of the field and consistently silent in
the same places: no aggregate magnitude in any of its three runs, no SEC-411 to
engineering in any of them, and the credit question unanswered in two of three.
It scores 89.67 — 5.5 below the next model.

**Which criteria let it collect points anyway:** 78 of its 93 verdicts are PASS,
and 49 of the 100 points sit on criteria no model failed. The 21-point
absence-satisfiable surface produced **no observed exploit** — Gemma 4 passes
those six criteria, but it also passes the fifteen constant criteria that
require content, so its shortfall is concentrated in the nine discriminating
criteria. Silence is not what is earning it points; the easy criteria are.

## 10. Penalty audit

**One penalty in 651 verdicts.**

| Model | Run | Type | Amount | Trigger | Underlying criteria | Class |
|---|---|---|---:|---|---|---|
| Qwen 3.6 | run-002 | PROHIBITED_ACTION | −7 | Status page: *"We expect to confirm full recovery within the next hour."* | `no_external_completion_promise` (FAIL), `status_page_publishable` (PARTIAL) | **DISTINCT_SEVERITY** |

The criterion prices whether the response kept recovery times out of external
artifacts. The penalty prices the commitment itself: the prompt states the status
page is published as written, so an open incident whose verification window has
not closed carries a public recovery promise nobody authorised.

**`CONFIDENTIALITY_BREACH` has now never fired** — 0 occurrences across 21
calibration runs and 21 official runs. Reported as instructed. It is not
evidence the penalty is unnecessary; it is evidence this cohort does not leak.

## 11. Judge reliability audit

651 verdicts. Every PARTIAL, every FAIL, the penalty, and PASS verdicts on the
delicate criteria were re-examined.

| Class | Verdicts | Point mass affected |
|---|---:|---:|
| CLEAR | 645 | — |
| BORDERLINE_BUT_RUBRIC_RESOLVES | 3 | — |
| **JUDGE_VARIANCE** | **0** | **0** |
| **RUBRIC_LIMITATION** | **3** | **4.5** |
| BENCHMARK_INVALIDATING_DEFECT | **0** | 0 |

The three rubric limitations, recorded and **not** repaired — 0.4 is frozen:

1. **`incident_start_time` / `start_and_scope_consistent`, DeepSeek run-002.**
   The status page says *"first reported at 11:55 UTC"*. On a status page,
   "first reported" defensibly means "first reported here", which is true; a
   public reader still takes 11:55 as when the problem began. The FAIL band
   names 11:55 explicitly but did not anticipate this phrasing. Scored PARTIAL
   on both, twice affecting 3.5 points.
2. **`security_item_reaches_engineering`, MIMO run-001 and Qwen 3.8 Flash
   run-001.** Both mention SEC-411 only inside a do-not-publish list: ticket
   identity present, owner and follow-up absent. The 0.4 bands assume at most
   one of the three elements is missing; here two are. Scored FAIL as the lower
   available label.
3. No third distinct class; the count above lists the affected verdicts.

**Zero verdicts classified JUDGE_VARIANCE across 651.** Every disputable call
traces to a band that can be read two ways. This is one recorded pass and cannot
be resampled — that limitation is unchanged and is restated in §14.

## 12. Reasoning volume versus quality variance

| Model | reasoning-token range | output range | score range | score sd |
|---|---:|---:|---:|---:|
| GLM 5.2 | 15,389 | 15,290 | 3.0 | 1.22 |
| Qwen 3.8 Flash | 7,227 | 7,311 | 3.0 | 1.22 |
| GLM 5.3 Flash | 6,419 | 6,902 | 1.5 | 0.71 |
| DeepSeek V4 Flash | 3,106 | 3,342 | 2.0 | 0.85 |
| MIMO v2.5 | 0 (not reported) | 1,217 | 5.0 | 2.36 |
| Qwen 3.6 | 0 (non-reasoning) | 262 | **22.0** | **8.99** |
| Gemma 4 | 0 (non-reasoning) | 186 | 2.5 | 1.18 |

**Large reasoning variation is not associated with quality variation in this
sample.** GLM 5.2 has by far the widest reasoning range — a 15,389-token spread,
one run at 1,884 and another at 17,273 — and a score range of 3.0 with no run
below 97.0. Conversely the two widest score ranges belong to Qwen 3.6 (22.0) and
MIMO (5.0), **neither of which reports reasoning tokens at all**.

There is insufficient evidence here for any causal claim in either direction,
and none is made. The variation is consistent with serving and computation
variability.

## 13. Calibration versus official — out-of-sample validation

**Analysis only. No calibration score enters the official leaderboard.**

| Model | cal mean | **off mean** | delta | cal range | off range | cal sd | off sd |
|---|---:|---:|---:|---:|---:|---:|---:|
| GLM 5.3 Flash | 99.30 | 98.50 | −0.80 | 1.0 | 1.5 | 0.47 | 0.71 |
| GLM 5.2 | 98.50 | 98.50 | +0.00 | 3.0 | 3.0 | 1.22 | 1.22 |
| Qwen 3.8 Flash | 97.70 | 97.00 | −0.70 | 2.5 | 3.0 | 1.18 | 1.22 |
| DeepSeek V4 Flash | 96.70 | 97.33 | +0.63 | 2.0 | 2.0 | 0.85 | 0.85 |
| MIMO v2.5 | 92.50 | 95.17 | +2.67 | 5.0 | 5.0 | 2.16 | 2.36 |
| Gemma 4 | 84.30 | 89.67 | +5.37 | 4.0 | 2.5 | 1.89 | 1.18 |
| Qwen 3.6 | 74.20 | 79.33 | +5.13 | 37.5 | 22.0 | 16.53 | 8.99 |

**A. Ranking generalises.** One adjacent swap in seven: DeepSeek and Qwen 3.8
Flash exchange third and fourth, separated by 0.33 points. Every other position
holds.

**B. Scores generalise at the top, drift upward at the bottom.** The four
leading models move by −0.80 to +0.63. The three trailing models all gain —
MIMO +2.67, Gemma 4 +5.37, Qwen 3.6 +5.13. The most likely reading is
regression from unlucky calibration samples plus the 0.4 repairs, which removed
two bands that had penalised legitimate behaviour. It is a systematic upward
drift in the weakest third and should be treated as a caution about small-n
scores rather than as evidence any model improved.

**C. Qwen 3.6's variance reproduces.** Range 37.5 → 22.0, sd 16.53 → 8.99. Half
the magnitude, still an order of magnitude above every other model. Both
batteries contain one run that asserts a root cause to the CEO while its own
engineering update calls it unconfirmed. **This is a stable property of the
model on this scenario, not a calibration artefact.**

**D. The two 0.3 boundaries generalise, differently.**
`fleet_topology_not_external` caught 5 calibration runs across two models and 3
official runs across one — still DISCRIMINATING on data that did not exist when
it was written. `cause_investigation_not_external` caught one calibration run
and zero official runs, moving to CONSTANT_PASS. It remains a real boundary the
frozen world supports; this cohort simply does not cross it.

**E. Routing variance generalises and strengthens.**
`security_item_reaches_engineering`: 12/1/8 in calibration, **10/2/9 official**.
Consistently the most-failed criterion in both batteries.

**F. Constant mass rose.** 41 points in calibration → **49 points official**,
15 criteria. Half the rubric is now earned by every run.

## 14. Constant-point-mass analysis and limitations

**49 of 100 points are earned by all 21 runs.** Nine of those sit on the four
explicit confidentiality criteria, which no model has failed across 42 responses
in two batteries. The remainder are incident-state and cross-output criteria
that this cohort handles uniformly: start time, service scope, mitigated-not-
resolved, affected population, hypotheses to engineering, verification window,
resolution consistency, engineering open threads.

**Top-5 spread is 3.3 points.** Four models sit within 1.5 points of the leader.

The old calibration preregistration — *≥3 models within 3.0 of the leader AND
constant mass ≥40* — **would be satisfied by these numbers**. Per the brief it is
reported here as **descriptive only** and is not applied as a publication gate:
it was designed to decide, before the freeze, whether the scenario needed
redesign, and that decision was made.

### Limitations

1. **The scenario compresses at the top.** Five models within 3.3 points is weak
   separation for a benchmark whose purpose is separation. The discrimination
   lives in 29 points across nine criteria.
2. **The overlap guard is inert for #005** (§1). Its clean result is not
   evidence; the content-hash check is.
3. **One recorded judge, one pass.** Variance cannot be resampled. Zero
   JUDGE_VARIANCE is the outcome of a discipline, not a measurement of one.
4. **Three rubric limitations, 4.5 points**, documented and unrepaired.
5. **Upward drift in the weakest third** between batteries (§13B) suggests
   three runs per model is thin for unstable models. Qwen 3.6's 22-point range
   means its 79.33 carries real uncertainty.
6. **`CONFIDENTIALITY_BREACH` has never fired** in 42 responses.

## 15. Publication readiness

| Gate | Result |
|---|---|
| 21/21 valid official runs | **PASS** |
| No calibration overlap | **PASS** (by content hash; the guard is inert — §1) |
| Frozen content intact | **PASS** |
| All official runs same configuration | **PASS** — one config fingerprint per model |
| 651 complete atomic verdicts | **PASS** |
| Scoring reproducible | **PASS** — replayed from `verdicts/monday-005/official.jsonl`, no API calls |
| No benchmark-invalidating rubric defect | **PASS** |
| Penalties reproducible | **PASS** |
| No unresolved qualification issue | **PASS** |
| Leaderboard validation | **PASS** — built in memory, zero blockers |

The leaderboard payload was **built and validated in memory and written
nowhere.** `leaderboard/monday-005/` does not exist.

## 16. Confirmations

- **#001–#004 untouched** — no file under any of them modified.
- **Overall v0 / v1 untouched** — `leaderboard/overall/` unmodified; no Overall v2.
- **`taxonomy/capabilities-v0.1.yaml` untouched.**
- **Calibration archive untouched** since it was written.
- **No calibration run appears officially** — verified by content hash.
- **No candidate-visible #005 content changed** — prompt still `532cd464…`.
- **Rubric 0.4 unchanged** during judging.
- **Evaluator unchanged.**
- **No model-specific scoring changes.**
- **No valid run regenerated** — only the three serving failures were retried.
- **Nothing published. Nothing committed.**

---

## 17. Provenance integrity — repository-level fix applied after the battery

The §1 finding — that `check_calibration_overlap` had become inert for #005 —
has been fixed at the repository level. Full detail in
`analysis/monday-005-provenance-note.md`.

**What was wrong.** The guard compared `run_id` between live evaluations.
Archiving the calibration battery, which the rule itself demands, moves those
evaluations out of `evaluations/` and leaves the comparison with nothing to
read. It returned clean, and would have returned clean if a calibration
response had been promoted verbatim. Archiving also freed the run numbers, so
the official battery restarted at `run-001` and the ids collide with the
calibration ids — meaning `run_id` would now produce a false positive on every
model as readily as a false negative.

**What replaced it.** `runner.sample_identity` returns
`(sha256(response), provider_metadata.request_id)`. The content hash is primary
— it is the artefact a rubric is fitted to; the request id corroborates and is
secondary only because the schema types it `str | None`. The identity excludes
score, verdicts, evaluation path, leaderboard position, run number, file
location and timestamp, so it survives archiving, renumbering and directory
moves. `leaderboard.check_sample_provenance` compares every live official run
against every archived run for the scenario, and reports duplicates inside the
official battery as well. It is wired into `check_calibration_overlap`, so every
existing publication path picks it up unchanged.

**Mechanically derived audit of the real battery** — no number below is
hard-coded:

| | |
|---|---:|
| calibration samples inspected | **21** |
| official samples inspected | **21** |
| cross-set overlap, content | **0** |
| cross-set overlap, provider request id | **0** |
| duplicates within the official battery | **0** |
| collisions | none |
| runs missing identity data | none |
| runs lacking a request id | none |

**Historical compatibility.** monday-001 through monday-004 pass the new guard
unchanged, with zero overlap and zero internal duplicates in every scenario. No
historical data was rewritten.

**Tests.** `tests/test_sample_provenance.py`, fourteen tests covering cases A–F.
Case A — an archived calibration sample promoted verbatim and renumbered — was
verified to return clean under the old check and is rejected by the new one.
Case B pins that a shared `run_id` is *not* evidence of overlap, which is
#005's real situation. No test in the repository now treats a run id or its
numeric suffix as provenance.

**Scores are untouched by this change.** The guard reads runs; it computes
nothing. All 651 verdicts, both penalty totals and all seven Monday Scores are
byte-identical to §5.

### A separate defect, reported and not fixed

`archived_run_numbers` is consulted only on the `--reuse-valid-runs` generation
path; the plain `--runs N` path numbers from 1 unconditionally. That is why
#005's official battery restarted at `run-001` moments after `plan` correctly
predicted `4, 5, 6`. It is a keying defect rather than a provenance one, the new
guard makes any promoted sample detectable regardless, and fixing it was outside
the assigned scope. The exact fix is recorded in the provenance note.

## 18. Published artifacts

`leaderboard/monday-005/leaderboard.{json,csv,md}` written by
`mondaybench leaderboard --scenario monday-005 --official`, all publication
gates passed.

**GLM 5.2 and GLM 5.3 Flash are tied at 98.50 on the arithmetic mean.** The
order shown is the repository's existing deterministic convention; no
variance-based quality tiebreaker was introduced and no score was adjusted to
force an ordering. Their dispersion is published beside the mean and separates
them plainly: GLM 5.3 Flash ranges 1.5 across its three runs, GLM 5.2 ranges 3.0.

**Overall is untouched.** No Overall v2, no change to v0 or v1, no capability
taxonomy change, no website content, nothing committed.

---

`DECISION: #005 READY TO PUBLISH`
