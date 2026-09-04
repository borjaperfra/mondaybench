# Scoring audit — Claude Opus 5, five scenarios, 15 runs

**Date:** 2026-09-02
**Outcome:** **no verdict changed.** `five-scenario-summary.PRE-AUDIT.json` and
`five-scenario-summary.json` are byte-identical, and both carry
**97.10**.

That is not because the audit was skipped. It is because the two corrections
that the Fable 5.1 audit had to make retrospectively were applied here from the
first pass, by instruction:

1. **The lower-label rule** — every per-scenario judge prompt ends with "If a
   response sits between two labels, choose the lower" (monday-002 words it "If
   ambiguous, choose lower"). All four judge prompts were read before any
   response was.
2. **`factual_plan_accuracy` is scored against `factual_anchors` and nothing
   else** — monday-003's judge prompt says so explicitly. The anchors were
   loaded and the criterion was scored against them alone.

Every criterion whose label discriminated between runs was calibrated against
the frozen judge's own published verdicts before the label was assigned, rather
than after. That is what this document records.

---

## 1. Calibration against precedent, criterion by criterion

The rule applied throughout: **same class of error, same verdict severity.**

### monday-001 — `umbrella_error_rate`

The frozen judge gave glm5.3-flash **PARTIAL on all three runs** for reading
Umbrella's 163 errors against other customers' raw counts without connecting
them to its 94,217 request volume. All three Opus runs do exactly that — "vs.
single digits for most accounts", "highest of any account by far relative to
volume", "an order of magnitude worse than every other account" — and none
gives an error rate, cites 94,217 alongside 163, or notes Stark Industries'
higher raw count on far higher traffic. **PARTIAL ×3.**

Cross-check: replaying glm5.3-flash's published verdicts through the same
scoring path reproduces its published **98.0** exactly, which is what
established that this scoring model is calibrated before any Opus label was set.

### monday-003 — `factual_plan_accuracy`

The precedent is unusually precise here.

| Precedent | Substitutions | Label |
|---|---|---|
| glm5.3-flash run 001 | one (pricing page Wed for Thu 17:00) | PARTIAL |
| glm5.2 run 002 | one (billing migration Wed for Thu 15:00) | PARTIAL |
| **glm5.3-flash run 002** | **two — onboarding Thu for Fri 12:00, pricing Wed for Thu 17:00** | **FAIL** |
| mimo-v2.5 run 001 | two | FAIL |
| qwen3.6 runs 001/002 | two / three | FAIL |

Opus run 1 makes **the identical pair** glm5.3-flash run 002 made: "pricing_page
(3h) this afternoon (deadline Wed 17:00)" against a Thursday anchor, and
"Onboarding launch: Tuesday (deadline Thu 12:00)" against a Friday anchor. Runs
2 and 3 carry both correctly. So **FAIL / PASS / PASS**, which is the precedent
applied rather than a fresh judgement.

Note what was *not* charged here: run 1's derived end-times drift by up to half
an hour (Daniel 12:30–16:30 for a 3.5h task). Those are arithmetic on derived
values, not substitutions of supplied anchors, and monday-003's judge prompt
narrows this criterion to the supplied deadlines, durations, owners,
availability windows and commitments. Charging them here would have been
double-pricing.

### monday-004 — the strict criteria

This is the scenario where Opus scores lowest (89.67) and the calibration
matters most, because GLM 5.3 Flash scored **98.0** here on 36,248 median
output tokens against Opus's 23,925. The gap is real and it is not a scoring
artefact:

* **`segment_retention_quantified`** — all eight published PASS verdicts
  computed *a rate for every population on one consistent labelled basis*
  ("logo churn and ARR churn for all three segments on the canonical
  denominators"). The published PARTIALs are for ranking on revenue movement
  instead of retention, or using the Starter plan's 13 as the SMB denominator.
  All three Opus runs quantify churned ARR across the segments and rank them
  correctly, and run 2 gives one segment logo rate (4 of 13, the correct
  opening-cohort SMB denominator), but none carries a per-segment rate through
  for all three. **PARTIAL ×3.**
* **`cac_payback_unavailable`** — gemma4 run 004 stated the refusal and the
  missing input correctly, then computed a proxy, and the frozen judge's reason
  says that proxy is "which the criterion places at PARTIAL". Opus run 1 does
  the same shape: "a hard stop, not a caveat", then payback of 0.7 / 2.2 / 12.6
  months from an assumed EUR 10,000 CAC. **PARTIAL** for run 1, PASS for runs
  2 and 3, which compute nothing.
* **`figures_carried_correctly`** — 2 of 21 published runs reached PASS. GLM 5.3
  Flash took PARTIAL for "two small slips" on an otherwise exact response.
  Each Opus run has at least one checkable slip (run 1 a 59% share that does
  not reconcile and EUR 4.05 quoted in two different units; run 2 Enterprise
  usage at +5–10% when the segment is −1.86%, plus 77% and 87% given for the
  same quantity; run 3 rate-limit tickets as 6→13 when support.csv holds 5→13).
  **PARTIAL ×3.**
* **`segment_recommendation`** — glm5.3-flash took PARTIAL because "the budget
  stays inside SMB rather than leaving it, but leadership is still told to pause
  acquisition spend". Runs 2 and 3 do exactly that ("stop paid acquisition into
  it", "freeze new starter acquisition for 60 days") → **PARTIAL**. Run 1's
  Starter action is "stop routing new logos into Starter by default" — a
  routing and packaging change, not a spend cut → **PASS**. That distinction is
  the reason the three runs differ here, and it is checkable in the text.

### monday-002 and monday-005 — the perfect scores, checked adversarially

Five of the fifteen runs score 100.0. Each was re-examined specifically because
a perfect score is where leniency would hide.

**monday-002 (runs 1 and 3).** The published top is 94.8, and the whole field
lost points in the same two places. `choose_option_b`: every published model
that took PARTIAL chose Option A, several on a false claim about B's diff being
unsubmitted. All three Opus runs choose B, on viability plus the materially
lower stated risk (8% → <1%), which is both halves of the PASS bar.
`ownership_supersession`: the published PARTIALs read "names Daniel as the
current sender and gates it on Sam's confirmation, but Sarah's handoff is never
traced and the stale 'You' task is not displaced" — all three Opus runs trace
Sarah → Daniel *and* displace the user's task ("I do not send it").
`conditional_launch_timing`: the published PARTIAL was for telling Atlas
rollout "is scheduled to begin at 11:00" with conditionality only implied by a
preceding step; Opus states the conditionality in the same sentence ("rollout
opening ~11:00, will confirm on Sam's go").

The one criterion that separates run 2 from runs 1 and 3 is
`schedule_feasibility`, and it is a two-minute arithmetic fact rather than a
matter of taste. Priya's only pre-10:25 window ends at 09:35 and the delta
review takes 25 minutes:

| run | review slot | fits? |
|---|---|---|
| 1 | 09:10–09:35 | yes, exactly 25 minutes |
| 2 | **09:12–09:35** | **no — 23 minutes for a 25-minute review; a 25m review from 09:12 ends 09:37** |
| 3 | ~09:10–09:35, with the constraint derived explicitly | yes |

Run 2's downstream chain is correct, so this is "timing incomplete/slightly
inconsistent" — the PARTIAL band — and the lower-label rule settles it against
PASS. **PASS / PARTIAL / PASS.**

**monday-005 (all three runs).** The published top is 98.5, shared by GLM 5.2
and GLM 5.3 Flash, and each lost its 1.5 points on criteria these runs satisfy:

* glm5.2 — `security_item_reaches_engineering` FAIL in one run ("withheld
  externally, which is required, and also withheld from the team that has to
  fix it") and `status_page_publishable` PARTIAL in one run. Every Opus run
  routes SEC-411 with all three required elements (ticket identity, owner
  Marcus, explicitly separate from this incident) and every Opus status page
  carries all four PASS elements.
* glm5.3-flash — `rejected_hypothesis_recorded` PARTIAL in **all three** runs:
  "neither the green provider status nor the healthy Files API on the same
  provider is stated." Every Opus run states both: "ruled out at 11:47 —
  provider status green, Files API on the same provider healthy."

Nine of the 21 published runs failed `security_item_reaches_engineering`
outright. Opus passing it in all three is the single largest reason it clears
the published top here.

Every boundary criterion was additionally checked **mechanically** rather than
by reading: across all three runs the customer email and status page contain no
occurrence of "fleet", no SEC-411, no release name, no connection-pool detail
and no other customer's name, and each email carries Contoso's own 9,400 /
3,410 figures with the 29.9% aggregate absent.

The closest call in monday-005 is run 3's `internal_eta_not_external`. Marcus's
internal estimate is ~16:00, and run 3's external artifacts do contain "16:00" —
but as the *next update* time ("a further update by 16:00 UTC today whether or
not the position has changed"), which is a different semantic object from a
recovery time and is the one forward-looking commitment the rubric authorises.
The criterion directs the judge to "the semantic object of any time, not the
digits", and the engineering update states "no restoration estimate" and that
"the ~16:00 figure in the channel is an internal planning guess and stays
there". Recorded as PASS, and recorded here as the judgement a reader is most
likely to want to check.

---

## 2. The boundaries the audit was asked to re-examine

| Item | Finding |
|---|---|
| PASS / PARTIAL / FAIL boundaries | Every discriminating label anchored to a published precedent, tabulated above. |
| Lower-label rule | Applied from the first pass. It is what decides monday-002 run 2 (`schedule_feasibility`) and several monday-004 criteria. |
| Factual anchors | monday-003's `factual_plan_accuracy` scored against `factual_anchors` only; derived-time arithmetic deliberately not charged here. |
| Schedule feasibility | Checked minute by minute against `calendars.csv` and `emails.md` for all three monday-002 runs. |
| Ownership / supersession | Sarah → Daniel traced and the stale "You" task displaced in all three monday-002 runs; monday-003's five stale task-list items all overridden. |
| Unknown conversions | monday-004 `cac_payback_unavailable`: run 1 computed a number from an assumed input after refusing correctly, which is the PARTIAL band per precedent. |
| Carried figures | monday-004 `figures_carried_correctly` PARTIAL ×3, with the specific slip named per run. Every figure quoted in this audit was recomputed from the candidate-visible CSVs. |
| Scenario-specific rubric semantics | Each scenario judged against its own frozen rubric (0.2 / 0.2 / 0.3 / 0.3 / 0.4) with no harmonisation between them; rubric file read from each scenario's own `FROZEN.yaml` rather than hardcoded. |

---

## 3. The confound this audit cannot fix

**MondayBench's judge is `claude-opus-5`. The candidate is `claude-opus-5`.**

Everything above is about applying the frozen rubric consistently, and it was.
None of it addresses the structural problem: the model grading the responses is
the model that produced them. Averaging over fifteen runs does not reduce a
systematic effect, and no calibration against other models' verdicts detects
one that applies only to this candidate.

This did not apply to Fable 5.1 and it applies here in full. It is the stronger
of the two reasons this result is not a leaderboard entry — stronger than the
route contamination, which at least cancels in the Opus-versus-Fable comparison.

The honest position: 97.10 is what the frozen rubric yields when applied to
these fifteen responses with the precedents above. It is not a measurement that
can be set beside the seven models the same judge scored without having written
their answers.
