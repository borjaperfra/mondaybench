# Opus 5 Inter-Judge Audit

## Executive summary

The 15 Claude Opus 5 responses were re-judged from scratch by an independent
judge (GPT-5.6 Sol) that was blind to the model's identity, to every original
label, to every original score and to the aggregate result. Both judges' labels
were then scored through the same harness code path, so any score difference can
only come from a label difference. **The original judge produced 97.10; the
independent blind judge produced 97.07 — a delta of −0.03.** The two judges
agreed on **343 of 354** criterion judgments (**96.89%**), with **zero
PASS↔FAIL disagreements**; Cohen's κ = 0.740, linear-weighted κ = 0.751,
quadratic-weighted κ = 0.770. Of the eleven disagreements, the original judge
was more generous on six and stricter on five, and the most conservative
reconciliation available — taking the **lower** of the two labels on every
disagreement — lands at **96.60**. On this evidence **material self-judge
inflation is NOT SUPPORTED**. This says nothing about the separate and still
unresolved problem: Opus was generated through Claude Code rather than
MondayBench's standard provider route, so the result **remains provisional and
off-benchmark**.

---

## Experimental design

The blind package (`audits/blind-rejudge/opus-5-blind-rejudge.md`, 412,144
chars) contained, per scenario: the frozen user prompt with its SHA-256, the
frozen rubric rendered from the parsed rubric object, the answer key, the
scenario-specific judge instructions, and the three responses verbatim.

What it deliberately did not contain: the model's identity, any original label
or score, the aggregate, telemetry, pricing, route metadata, the leaderboard, or
any comparison with another model. Two rubrics carry YAML comments naming other
models *and quoting their scores*; those comments were omitted, which is why the
rubrics were rendered from the parser rather than pasted as raw YAML.

Responses were relabelled **Candidate A / B / C** under a seeded permutation
chosen per scenario so that no scenario retained the identity order
`A=run1, B=run2, C=run3`:

| Scenario | A | B | C |
|---|---|---|---|
| monday-001 | run1 | run3 | run2 |
| monday-002 | run2 | run3 | run1 |
| monday-003 | run1 | run3 | run2 |
| monday-004 | run3 | run2 | run1 |
| monday-005 | run3 | run1 | run2 |

The mapping lived only in `opus-5-blind-rejudge-mapping.json` and was never
given to the second judge. **All comparative analysis in this audit is keyed on
`original_run_id`, never on the candidate letter.**

### Source integrity

* Frozen suite digest unchanged:
  `c056b4b43d3caeb3b50394282b08ed281a5716fb1df68d1666abb950aa0b2a80`
* Zero modified tracked files
* **15/15** responses in the blind package verified text-equivalent to the
  original raw responses that the first judge scored

### Validation of the second judge's artifact

Recomputed from the atomic rows rather than trusted. **Zero problems found:**
354 criterion rows, 18 false-action rows, 15 penalty rows, all criterion ids
valid against the right rubric, no duplicates, no omissions, all labels in
{PASS, PARTIAL, FAIL}, every `points_awarded` and `max_points` consistent with
the rubric, and all 15 candidate totals, all 5 scenario means and the overall
reproducing exactly from the rows.

---

## Aggregate result

| Scenario | Rubric | Original | Blind | Delta |
|---|---|---:|---:|---:|
| monday-001 | 0.2 | 98.50 | 98.50 | 0.00 |
| monday-002 | 0.2 | 99.00 | 98.00 | −1.00 |
| monday-003 | 0.3 | 98.33 | 98.33 | 0.00 |
| monday-004 | 0.3 | 89.67 | 90.83 | +1.16 |
| monday-005 | 0.4 | 100.00 | 99.67 | −0.33 |
| **OVERALL** | | **97.10** | **97.07** | **−0.03** |

Every figure in the table supplied with the second judge's artifact reproduced
exactly from the atomic rows. Nothing had to be forced or explained away.

Run level, keyed on the stable run id:

| Run | Original | Blind | Delta |
|---|---:|---:|---:|
| monday-001 run1 / run2 / run3 | 98.5 / 98.5 / 98.5 | 98.5 / 98.5 / 98.5 | 0 / 0 / 0 |
| monday-002 run1 / run2 / run3 | 100.0 / 97.0 / 100.0 | 99.0 / 96.0 / 99.0 | −1.0 / −1.0 / −1.0 |
| monday-003 run1 / run2 / run3 | 95.0 / 100.0 / 100.0 | 95.0 / 100.0 / 100.0 | 0 / 0 / 0 |
| monday-004 run1 / run2 / run3 | 85.0 / 89.5 / 94.5 | 86.5 / 90.0 / 96.0 | +1.5 / +0.5 / +1.5 |
| monday-005 run1 / run2 / run3 | 100.0 / 100.0 / 100.0 | 100.0 / 99.0 / 100.0 | 0 / −1.0 / 0 |

Mean run delta **−0.033**, median **0.00**, mean absolute **0.50**, max
absolute **1.5**. Pearson r **0.9897**, Spearman ρ **0.9537**. The two judges
rank the fifteen responses almost identically.

---

## Criterion-level agreement

354 judgments. **343 agreements (96.89%)**, 11 disagreements (3.11%).

| | blind PASS | blind PARTIAL | blind FAIL |
|---|---:|---:|---:|
| **original PASS** | 326 | 6 | 0 |
| **original PARTIAL** | 5 | 16 | 0 |
| **original FAIL** | 0 | 0 | 1 |

* Cohen's κ (unweighted) **0.7397**
* Linear-weighted κ **0.7508**
* Quadratic-weighted κ **0.7703** (ordinal FAIL < PARTIAL < PASS)
* Mean absolute point difference per criterion **0.0141**; median **0.0**
* **96.89%** of criteria differ by exactly zero points; **100%** differ by no
  more than the half-credit transition
* One-level disagreements **11** — PASS↔PARTIAL **11**, PARTIAL↔FAIL **0**
* **PASS↔FAIL disagreements: 0.** There is no case where one judge saw full
  credit and the other saw none.

### Reading the kappa honestly

κ = 0.74 alongside 96.89% agreement looks like a contradiction and is not. The
label marginals are extreme: 332 of 354 original labels are PASS. When one
category dominates, chance agreement is already high, so κ divides a small
observed-error term by a small expected-error term and becomes very sensitive to
a handful of cells. Two scenarios show the degenerate ends of this directly —
monday-001 and monday-003 have zero disagreements and κ = 1.0, while monday-005
has a single disagreement in 93 judgments and κ computes to **0.0** because
there is essentially no label variance for it to work with.

So κ here should be read as "the disagreements are not explained by chance
alone", not as a grade. The load-bearing numbers for this audit are the
agreement rate, the absence of any PASS↔FAIL disagreement, the directional
symmetry, and the size of the score movement.

---

## Where the judges disagreed

By scenario:

| Scenario | Criteria | Agreement | Disagreements | PASS↔FAIL | Delta |
|---|---:|---:|---:|---:|---:|
| monday-001 | 57 | 100.00% | 0 | 0 | 0.00 |
| monday-002 | 60 | 95.00% | 3 | 0 | −1.00 |
| monday-003 | 63 | 100.00% | 0 | 0 | 0.00 |
| monday-004 | 81 | 91.36% | 7 | 0 | +1.16 |
| monday-005 | 93 | 98.92% | 1 | 0 | −0.33 |

Two of the five scenarios are identical judgment-for-judgment. The disagreement
is concentrated in monday-004, which is also the scenario with the lowest score
and the most criteria.

By dimension, lowest agreement first:

| Scenario | Dimension | N | Agreement | Original % | Blind % | Points |
|---|---|---:|---:|---:|---:|---:|
| monday-002 | `uncertainty_epistemic` | 9 | 66.67% | 100.00 | 90.00 | −3.0 |
| monday-004 | `decision_quality` | 12 | 75.00% | 88.89 | 96.30 | +2.0 |
| monday-005 | `supersession_and_currency` | 6 | 83.33% | 100.00 | 94.44 | −1.0 |
| monday-004 | `cross_table_data_quality` | 15 | 86.67% | 78.70 | 84.26 | +3.0 |
| monday-004 | `plan_economics` | 15 | 93.33% | 90.35 | 85.96 | −2.5 |
| monday-004 | `acquisition_reasoning` | 15 | 93.33% | 93.86 | 95.61 | +1.0 |

Every other dimension across all five scenarios is at 100%.

**The pattern that matters: the effects run in opposite directions and very
nearly cancel.** The blind judge was stricter by 6.5 points across three
dimensions and more generous by 6.0 points across three others. Net −0.5 points
over 354 judgments. This is not what one-sided grading looks like.

---

## Largest disagreements

All eleven, with both rationales and a response excerpt, are in
`disagreements.json` / `disagreements.csv`. The three clusters:

### 1. monday-002 `no_unsupported_causality` — all three runs, original PASS → blind PARTIAL (−1.0 each)

The responses say Globex's usage and admin-login decline is "consistent with
admins being blocked" and that fixing the high-severity SSO ticket would
"likely unlock" the stalled expansion — and they label that linkage a
hypothesis elsewhere. The original judge read this as a data-consistent
observation, not an invented cause. The blind judge read it as an unsupported
causal hypothesis.

**The rubric text leans toward the blind judge.** The PARTIAL band reads, in
full: *"Unsupported cause only as explicit hypothesis."* That band exists
precisely for a hedged causal claim, which is what the responses make.

### 2. monday-004 `segment_recommendation` and `causal_boundary` — four judgments, original PARTIAL → blind PASS (+1.5 each)

On `segment_recommendation` the original applied a precedent from the
benchmark's own published verdicts, where another model recommending an
acquisition-spend pause scored PARTIAL as "a reduction hedged with conditions".
**The blind judge could not see that precedent — it was excluded from the
package by design.** It read the PASS band on its own terms and found the
response declines to cut SMB and names the missing segment economics.

This is the clearest cost of blinding: the package removed bias, and it removed
calibration context with it. The blinding was correct, and this is what it
costs.

`causal_boundary` is an omission dispute. The PASS band asks the response to
treat Soylent's three simultaneous movements as a pattern **and** to state that
the data does not establish what caused what. The original required the second
clause and did not find it; the blind judge did not require it.

### 3. monday-004 `cac_payback_unavailable` ↔ `uncertainty_discipline` — the same feature, charged at different criteria

Run 1 correctly refuses to compute CAC payback, then produces an illustrative
payback range from an assumed €10,000 CAC. The original charged this at
`cac_payback_unavailable` (PARTIAL, −1.0) and passed `uncertainty_discipline`.
The blind judge did the reverse: passed `cac_payback_unavailable` and charged
`uncertainty_discipline` (PARTIAL, −1.0).

**Net effect on the run: zero.** Both judges saw the same flaw and priced it
identically; only the attribution differs. The `INSTRUCTION_COMPLIANCE`
category nets exactly 0.0 points for this reason.

### 4. monday-005 `artifacts_current_as_of_snapshot` — original PASS → blind PARTIAL (−1.0)

The response's status page is headed **14:25** against a **14:20** snapshot. The
PARTIAL band names this exact case verbatim: *"an artifact stamped a few minutes
ahead of the snapshot … a status page headed 14:25 whose content is accurate
belongs here, not with a page that publishes a state which does not exist."*

The original judge saw the 14:25 stamp during its own audit, reasoned it was a
plausible publication time for a document drafted at 14:20, and passed it. On
the rubric text as written, **that was a misapplication of a band the rubric had
already written for this situation.** This is the one disagreement where the
frozen text resolves the question outright, and it resolves against the original
judge.

### Category distribution

| Category | Count | Net points |
|---|---:|---:|
| `BORDERLINE_RUBRIC_INTERPRETATION` | 7 | −3.5 |
| `OMISSION_INTERPRETATION` | 2 | +3.0 |
| `INSTRUCTION_COMPLIANCE` | 2 | 0.0 |

Classification is descriptive and does not decide which judge was correct.
Where the frozen rubric text does settle the question, that is recorded in
`disagreement-classification.json` under `_rubric_text_notes` rather than folded
into the category.

---

## False actions and penalties

**False actions** (monday-001 only, 6 categories × 3 runs = 18 rows):
**18/18 agreement, 100%.** Both judges triggered zero false actions. Score
effect: 0 points.

**Penalties** (15 rows): **15/15 presence agreement.** Both judges assessed
**zero counted penalty points**. The second judge listed two candidates and
marked both `materially_misleading: false`:

* monday-001 run2 — an aggressive Umbrella risk inference, dismissed as "not a
  fabricated source fact or asserted root cause; criterion-level uncertainty
  handling is sufficient".
* monday-004 run1 — the "90 days out" Wayne renewal slip, dismissed because "it
  is captured by `figures_carried_correctly` and does not rise to the heavy
  major-data-error penalty".

**No double counting in either direction.** The second candidate is worth
noting: the blind judge independently found the one date-arithmetic error the
generation route introduced, and independently reasoned that it was already
priced at criterion level and must not be charged twice. That is the frozen
rule applied correctly by a judge that had never seen the rule applied.

---

## Conservative sensitivity

Four readings of the same 354 judgments. **C and D are stress tests, not
scores.**

| | Overall | monday-004 |
|---|---:|---:|
| **A** original judge | **97.10** | 89.67 |
| **B** independent blind judge | **97.07** | 90.83 |
| **C** per-criterion mean of both judges | **97.08** | 90.25 |
| **D** lower label on every disagreement | **96.60** | 88.50 |

**Max spread across A/B/C/D: 0.50 points.**

D is the point of the exercise: take the stricter of the two judges on all
eleven disagreements, with no offsetting, and the overall falls by half a point.

---

## Does the result survive an independent judge?

**Yes, on the judging axis.**

* Overall delta **−0.03** (−0.031% relative). The blind judge came out
  *slightly lower*, not higher.
* Directional symmetry: the original awarded more points on **6** criteria, the
  blind judge on **5**, and they were identical on **343**. Net **−0.50** points
  across 354 judgments.
* Run scores: original higher on 4, blind higher on 3, identical on 8.
* Zero PASS↔FAIL disagreements.
* Under the harshest available reconciliation the overall is **96.60**.

A judge systematically favouring its own model family should be more generous
than an independent judge *consistently*. It was not: it was more generous on
some dimensions, stricter on others, and the two effects nearly cancel.

**Self-judge bias assessment: NOT SUPPORTED.**

This verdict follows a decision rule fixed before the numbers were inspected
(recorded in `summary.json` under `self_judge_bias_inputs.decision_rule`):
`NOT SUPPORTED` requires |overall delta| ≤ 0.5, a directional ratio between
0.5× and 2.0×, and zero PASS↔FAIL disagreements. Observed: 0.03, 1.2×, 0.

**The limitation, stated plainly.** N = 15 responses and 354 judgments against
*one* independent judge. This cannot establish the absence of a small effect. It
bounds the size: every reconciliation here sits inside a 0.50-point band. A
second independent judge would narrow that; one cannot.

---

## What this does NOT validate

**The generation route is still non-equivalent, and this audit does not touch
it.**

Opus 5 was generated through Claude Code, not MondayBench's standard provider
route. On that route the Agent SDK preamble is prepended to the frozen system
prompt, a `<system-reminder>` carrying a real-world date is injected into the
user turn, and the auxiliary Haiku call was not suppressed. Config equivalence
was classified `NON_EQUIVALENT`, and the audit found the injected date altering
one derived figure in one run.

An independent re-judge addresses **who graded the answers**. It cannot address
**how the answers were produced**. These are orthogonal:

| Axis | Status after this audit |
|---|---|
| **Judge validity** | Independent blind re-judge reproduces the result within 0.03 points; self-judge inflation not supported |
| **Generation validity** | Unchanged. `PROVISIONAL / OFF-BENCHMARK`, non-equivalent route |

Therefore: Opus 5 does **not** become official, does **not** enter the official
leaderboard, and does **not** lose the PROVISIONAL label. Nothing here says
"Opus wins MondayBench", and nothing here repairs the generation harness
contamination.

---

## Top-band comparison

Blind overall **97.07** against the published band:

| Model | Score | Blind − them |
|---|---:|---:|
| Qwen 3.8 Flash | 95.07 | **+2.00** |
| GLM 5.3 Flash | 94.93 | **+2.14** |
| Claude Fable 5.1* | 94.90 | **+2.17** |

All three gaps exceed the benchmark's minimum observed run sigma of **1.53**.
But that reference is the *smallest* sigma in the band, and it is not the right
yardstick on its own:

* Opus's own within-scenario run sigmas are **0.00 / 1.73 / 2.89 / 4.75 / 0.00**
  (original) and **0.00 / 1.73 / 2.89 / 4.80 / 0.58** (blind).
* **Pooled within-scenario run SD: 2.604** (original), **2.635** (blind) — both
  *larger* than every gap above.
* Standard error of the blind overall: **0.68**, putting the gaps at 2.9–3.2 SE
  *if the comparators had zero variance*, which they do not.

Scenario spread is deliberately not used as a proxy for run variance anywhere in
this audit; the sigmas above are within-scenario across three runs.

**Verdict: measured above the existing top band, and clearly separated enough to
be interesting — but not resolved.** The gap survives the noise-floor reference
and the conservative reconciliation D (96.60 is still above 95.07), yet it is
smaller than the candidate's own pooled run-to-run variability, the comparators'
variance is unmodelled, and the generation route makes the comparison
non-equivalent regardless of the statistics.

---

## Publication recommendation

**Can be said:**

* The result was independently re-judged blind and moved by 0.03 points.
* Judges agreed on 96.89% of 354 atomic criterion judgments with no PASS↔FAIL
  disagreement.
* There is no evidence of material self-judge inflation in this experiment.
* Under the most conservative reconciliation the score is 96.60.
* The score measures above the current top band, and the separation is not
  statistically resolved.

**Must not be said:**

* That Opus 5 is official, verified, validated, or the leader.
* That the blind re-judge fixes or offsets the generation-route problem.
* That the difference from Qwen 3.8 Flash, GLM 5.3 Flash or Fable 5.1 is
  statistically established.
* Anything that drops or softens PROVISIONAL.

### Proposed copy

Long form:

> Claude Opus 5 scored **97.07** under an independent blind re-judge, against
> **97.10** under MondayBench's original judge. The two judges agreed on 96.89%
> of 354 atomic criterion judgments, with no PASS↔FAIL disagreement, and the
> 0.03-point difference provides no evidence of material self-judge inflation in
> this experiment. Taking the stricter of the two judges on every disagreement
> gives 96.60. The result remains **provisional** because Opus was generated
> through Claude Code rather than MondayBench's standard provider route — an
> independent re-judge addresses who graded the answers, not how they were
> produced.

Tooltip:

> Independently blind-rejudged. Score changed by 0.03 points. Generation route
> remains provisional.

Badges:

> `INDEPENDENTLY RE-JUDGED` alongside `PROVISIONAL`

Not `VERIFIED`, `VALIDATED` or `OFFICIAL` — each would imply an equivalence
this experiment does not establish.

---

## Files

```
reconcile.py                        regenerates every number here from source
summary.json                        the full machine-readable result
criterion-comparison.csv            354 rows, both judges side by side
run-comparison.csv                  15 rows keyed on original_run_id
dimension-comparison.csv            per scenario x dimension
disagreements.json / .csv           all 11, with rationales and excerpts
disagreement-classification.json    hand-assigned categories + rubric-text notes
false-action-comparison.csv         18 rows
penalty-comparison.csv              15 rows
source/                             the second judge's artifacts as received
```

Reproduce with:

```
python audits/blind-rejudge/inter-judge/reconcile.py
```

Both judges are scored through `mondaybench.scoring.build_breakdown`, so a score
difference can only come from a label difference and never from the arithmetic.
