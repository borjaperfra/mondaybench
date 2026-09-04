# Methodology notes — Fable 5.1 five-scenario off-benchmark experiment

Companion to `README.md`. What was done, in what order, and every judgment call
a reader might want to check.

## Generation

One script, `fable_gen.py`, unchanged from the monday-002 experiment except for
a Windows launcher path. It runs:

    DISABLE_NON_ESSENTIAL_MODEL_CALLS=1 claude -p \
      --model claude-fable-5-1 \
      --system-prompt "You are a helpful assistant." \
      --tools "" --effort high \
      --output-format stream-json --include-partial-messages --verbose \
      --safe-mode --setting-sources "" --strict-mcp-config \
      --disable-slash-commands --no-session-persistence

TTFT is taken from the first `content_block_delta` of any kind and TTFA from the
first `text_delta`, which is the definition `providers/base.py` documents. The
gap between them is the adaptive thinking phase.

`DISABLE_NON_ESSENTIAL_MODEL_CALLS=1` suppresses the auxiliary
`claude-haiku-4-5` call the CLI otherwise makes. The reported cost is the
`claude-fable-5-1` line from `modelUsage` only.

## Prompt verification

Each prompt was rebuilt with `mondaybench.prompt_builder.build_prompt`, written
to disk, re-hashed from the bytes on disk, and compared against **both**
`scenarios/<id>/FROZEN.yaml` and the `prompt_sha256` pin in
`overall-releases.yaml`. All five matched all three ways before any generation
ran. Had one mismatched, that scenario would have been skipped.

## Judging

Each scenario was judged against its own frozen rubric file — 0.2, 0.2, 0.3,
0.3, 0.4 respectively — with no harmonisation between them. Scores come from
`mondaybench.scoring.score_criteria`, `score_false_actions` and `aggregate`,
unmodified. monday-001's noise ladder was scored through `score_false_actions`
rather than by hand.

Every criterion in every run carries a label, an evidence quote and a reason in
`verdicts.jsonl`. `score_criteria` raises on a missing criterion, so no label
was defaulted.

### Calibration check

Before trusting my own labels I compared them against the frozen evaluator's
demonstrated standard on the published results. On monday-001, GLM 5.3 Flash's
official dimensions are `action_detection 25.0, state_reconstruction 25.0,
prioritization 15.0, data_reasoning 13.5, uncertainty 9.5, noise_resistance
10.0` for a 98.0 mean, including a `data_reasoning` shortfall of exactly the
1.5 points that `umbrella_error_rate` PARTIAL costs. Fable's three runs landed
on the same 13.5 for the same reason. That is not proof of calibration but it is
the closest available check, and it is the reason I did not treat 98.5 as
implausibly high.

### Judgment calls a reader may disagree with

Recorded because they move points.

1. **monday-003 `factual_plan_accuracy`, runs 2 and 3: PARTIAL, not FAIL.**
   Each run makes **two** deadline substitutions on the Thursday/Friday axis.
   The PARTIAL band names "one minor factual substitution"; the FAIL band names
   "several ... or one that materially distorts the plan". Two is more than one
   and fewer than several, and neither substitution alters the plan. I took
   PARTIAL because the band's *character* test (minor, non-material) matches and
   only the count pulls the other way. FAIL would put both runs at 95.0 and
   monday-003 at 96.67.

2. **monday-004 `no_churn_overreach`: PARTIAL for runs 1-2, PASS for run 3.**
   All three float reliability as a candidate cause. Only run 3 states that
   nothing establishes cause *and* names the counter-evidence ("the other two
   churners contradict it"). Runs 1-2 offer a labelled hypothesis, which is the
   PARTIAL band verbatim.

3. **monday-004 `segment_recommendation`: PARTIAL for runs 1-2, PASS for run 3.**
   All three decline to cut SMB and then constrain Starter spend. Run 3 alone
   separates plan from segment explicitly ("6 Mid-market on Enterprise plan, 4
   SMB on Pro"), notes SMB customers on Pro are healthy, and requires exit
   interviews and segment economics before any segment call — so its reduction
   is a plan decision, not a hedged segment cut.

4. **monday-004 `absolute_vs_scalable_economics` and `product_focus_supported`:
   PARTIAL for runs 2-3.** Both runs put Enterprise ahead of Pro for engineering
   after their own analysis names Pro the better economics, framing it on "87%
   of MRR" and "€6.8M of ARR exposed". The rubric allows another plan to win
   only if the case does not rest on absolute revenue. Run 1 chose Pro and
   passes both.

5. **monday-004 `figures_carried_correctly`: PASS in all three runs**, despite
   the churn-denominator errors. The rubric states explicitly that an error
   another criterion prices is not charged here and names "a wrong churn
   denominator to `segment_retention_quantified`" as an example. Charging it
   twice would be the double-count that criterion was written to avoid.

6. **monday-005 `commitment_state_consistent`: PASS in run 2** although its
   status page promises the next update at 14:45 and its customer email at
   15:00. Those are next-*communication* times to different audiences, not
   completion commitments, and the criterion is scoped to whether a completion
   commitment exists.

7. **No penalty fired anywhere.** The candidates I considered and rejected:
   monday-004's churn denominators (priced by `segment_retention_quantified`,
   and not a `major_data_error` in the penalty's sense of an artifact that
   would cause harm as written), and monday-003's deadline substitutions
   (`factual_plan_accuracy` prices them, and the rubric confines the penalty
   overlap to that criterion's FAIL band, which I did not reach).

## What was reused rather than re-run

monday-002's three scores were read out of
`experiments/fable-5.1-date-sensitivity/frozen-3run-summary.json` — the
structured artefact, not retyped values — and its usage, latency and cost blocks
came from the same file. Run B, the date-neutralized generation, is excluded
from every aggregate in this experiment by construction: `score_all.py` never
loads it.

## Aggregation

`five-scenario-summary.json` computes the provisional overall as
`round(statistics.fmean(scenario_scores), 2)`, which is what
`mondaybench/overall.py:ModelOverall.monday_score` does, over scenario scores
that are themselves `round(statistics.fmean(runs), 2)` as
`overall.check_score_recomputes` requires. Across-scenario range and σ use the
same definitions as the `scenario_*` properties on that class. No weighting, no
latency, no cost, no stability enters the score.

I did not call `build_overall()` itself, because it reads published
`leaderboard/<scenario>/leaderboard.json` payloads and validates them against
the release pins — and writing those payloads for Fable is exactly what this
experiment must not do. The arithmetic is reproduced; the publication path is
not touched.

## Cost accounting

Route-reported `costUSD` per run at `costBasis: list`. Cross-checked once
against the price list in the monday-002 experiment: 277 input + 3 output tokens
returned $0.00292, exactly `277/1e6*10 + 3/1e6*50`.

Note the cache asymmetry across runs of the same scenario: the first run of each
battery writes the prompt cache at $12.50/MTok and later runs read it at
$0.25/MTok. It changes cost only, not what the model saw, and it means the
per-run costs inside one scenario are not directly comparable.

## Spend

12 new generations: **$6.844 minus monday-002's $1.148 = $5.696**, plus the
$1.148 already spent on monday-002 in the earlier experiment. None of it is
charged to the benchmark.
