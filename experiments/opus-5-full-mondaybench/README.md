# Claude Opus 5 across all five MondayBench scenarios — PROVISIONAL, OFF-BENCHMARK

> **This is not a MondayBench result.** It is an off-benchmark experiment on a
> contaminated route, scored by a judge that is the same model as the
> candidate. It must not be read as, published as, or compared with the
> official leaderboard.

**Date:** 2026-09-02
**Model:** requested `claude-opus-5`, served `claude-opus-5`, provider
`firstParty`
**Route:** `claude -p` (Claude Code CLI 2.1.258), OAuth subscription, effort
high
**Classification:** **PROVISIONAL / OFF-BENCHMARK / CLAUDE CODE ROUTE**
**Provisional Monday Score:** **97.10**

---

## Why this is off-benchmark

The official route was tried first and does not work. `claude-opus-5` **is** on
the Helmcode allowlist — unlike Fable 5.1, which was absent under every
spelling — and it returns HTTP 500:

> Your organisation has no prepaid credit left. `claude-opus-5` is a
> third-party model billed per token from credits and is not covered by any
> subscription tier. `type: credits_exhausted`

The direct Anthropic API is closed by a hard project rule, not by a missing
key. NaN does not serve the model to this key. OpenCode is excluded on the
evidence gathered for Fable 5.1. Full detail, including the exact allowlist the
401 body enumerates, in `../../audits/monday-opus5/route-audit.md`.

The Claude Code route reaches the model but changes two things that cannot be
recorded truthfully as frozen:

* the frozen system prompt has the Agent SDK preamble **prepended** to it, so
  `system_prompt_sha256` is not `75357d68…`;
* a `<system-reminder>` is **injected into the user turn** carrying
  `Today's date is 2026-09-02`, so the user turn is not the frozen bytes.

The auxiliary `claude-haiku-4-5` call was also **not** suppressed by
`DISABLE_NON_ESSENTIAL_MODEL_CALLS=1` on this route, unlike on the Fable run.
Config equivalence: **`NON_EQUIVALENT`**.

## And a second disqualifier that has nothing to do with the route

**The judge is the candidate.** MondayBench's judge is `claude-opus-5`
(`evaluator-opus5-v0.1` … `v0.5`, `route: recorded`) and so is the model under
test. Averaging fifteen runs does not reduce a systematic effect. This did not
apply to Fable 5.1. See `AUDIT.md` §3.

---

## Results

| Scenario | Rubric | Runs | Mean | sd | Range |
|---|---|---|---|---|---|
| monday-001 | 0.2 | 98.5 / 98.5 / 98.5 | **98.50** | 0.00 | 0.0 |
| monday-002 | 0.2 | 100.0 / 97.0 / 100.0 | **99.00** | 1.73 | 3.0 |
| monday-003 | 0.3 | 95.0 / 100.0 / 100.0 | **98.33** | 2.89 | 5.0 |
| monday-004 | 0.3 | 85.0 / 89.5 / 94.5 | **89.67** | 4.75 | 9.5 |
| monday-005 | 0.4 | 100.0 / 100.0 / 100.0 | **100.00** | 0.00 | 0.0 |
| **OVERALL** | | | **97.10** | | |

Overall is the arithmetic mean of the five scenario means, matching
`overall-releases.yaml` Overall v2. With three runs per scenario at equal
weights it also equals the mean of all fifteen runs — verified: both are
**97.10**.

Variance: mean run sigma **1.87**, max run range **9.5** (monday-004),
across-scenario sigma **4.20**, range **10.33**. Standard error of the overall
mean **0.67**.

monday-004 is the weak scenario and the reason is legible rather than
mysterious: it is the one scenario that rewards exhaustive quantification, GLM
5.3 Flash scored 98.0 on it with a median 36,248 output tokens, and Opus wrote
23,925. The criteria it drops are the ones that ask for a specific figure it
did not compute. `AUDIT.md` §1 names each one.

## Efficiency (observed, not scored)

| | Opus 5 |
|---|---|
| median TTFA | 41.3 s |
| median TTFT | 3.2 s |
| median total latency | 90.5 s |
| mean output tokens | 9,201 |
| mean reasoning tokens | 4,837 |
| mean total input tokens | 6,784 |

Input tokens need care: Anthropic's `input_tokens` is **exclusive** of cached
tokens, so the total is `input_tokens + cache_creation + cache_read`. The raw
`input_tokens` field reads 2 on most runs.

No "steps" metric appears anywhere. MondayBench is one streaming completion per
task, not an agent loop.

## Date sensitivity

The route injects `Today's date is 2026-09-02`; every scenario has its own
fictional clock. Measured across all fifteen runs (`date-sensitivity.json`):

* **2 of 15** runs mention the runtime date — monday-004 runs 1 and 3, both in
  the header byline only ("prepared 2 Sep 2026 (data through Oct 2026)").
* **15 of 15** anchored their own scenario clock correctly.
* **Exactly one derived figure was altered by it.** monday-004 run 1 puts
  Wayne's 30 November renewal "90 days out" and flags "€1.17M of ARR renewing
  in the next 95 days". From the injected 2026-09-02 that is 89 days; from the
  data pack's end of October it is 30. Run 3, on the same scenario, says "29
  days out" — anchored to the data.
* **No decision changed.** Both runs escalate the Wayne renewal as an immediate
  action; the wrong window makes it look *less* urgent, not more. The error is
  priced by `figures_carried_correctly`, which run 1 already takes PARTIAL on,
  and it is cited there by name.

The prompt was not modified to hide the date. The point was to measure the
route's real effect, and its real effect is one wrong renewal window in fifteen
runs.

## Opus 5 vs Fable 5.1

Both on the same contaminated route, so the route confound cancels between
them. The self-judging confound does **not** cancel.

| | Opus 5 | Fable 5.1 |
|---|---|---|
| Monday Score | 97.10 | 94.90 |
| monday-001 / 002 / 003 / 004 / 005 | 98.50 / 99.00 / 98.33 / 89.67 / 100.00 | 97.50 / 91.00 / 96.67 / 89.33 / 100.00 |
| median TTFA | 41.3 s | 50.9 s |
| median TTFT | 3.2 s | 5.2 s |
| median total latency | 90.5 s | 93.2 s |
| mean output tokens | 9,201 | 8,198 |
| mean reasoning tokens | 4,837 | 4,363 |
| mean total input tokens | 6,784 | 6,785 |

Multiples: Opus reaches its first answer token in **0.81×** Fable's time
(**1.24× faster**) and its first stream token in **0.61×** (**1.63× faster**),
while generating **1.12×** the output tokens and **1.11×** the reasoning
tokens.

Reasoning comparability: **comparable**, and this is the only like-for-like
reasoning comparison in the repository. Both are `claude-*` models on the
identical transport, both report `thinking_tokens` from
`usage.output_tokens_details` with the same semantics, and reasoning sits
inside billable output tokens for both.

The whole difference is monday-002 (+8.00). On the other four scenarios the two
models are within 1.7 points, and identical on monday-005.

## Top performance band

Gaps: **+2.03** vs Qwen 3.8 Flash (95.07), **+2.17** vs GLM 5.3 Flash (94.93),
**+2.20** vs Fable 5.1 (94.90). All three exceed the 1.53-point noise
reference.

**Can MondayBench resolve a significant difference? NO.** Not primarily on the
statistics — though Opus's own mean run sigma of 1.87 is itself larger than
that 1.53 reference, with a 9.5-point run range on one scenario. The binding
reasons are the two systematic confounds: the candidate was judged by itself,
and it ran on a different route with a different system prompt. Neither is
reduced by averaging and both plausibly favour Opus.

So Opus 5 **joins the top performance band**. It is not stated as beating Qwen
3.8 Flash, GLM 5.3 Flash or Fable 5.1.

## Pricing

**Not computed in this phase, by instruction.** `served_model` is recorded on
every run so the later audit can map run → served model → first-party SKU →
public price. Every pricing snapshot was verified byte-identical
(`integrity.json`).

## Files

```
raw/monday-00N-runM.json      15 raw runs, full usage/timing/route metadata
verdicts-monday-00N.jsonl     per-criterion labels, evidence and reasons
five-scenario-summary.json    POST-AUDIT (authoritative)
five-scenario-summary.PRE-AUDIT.json   identical - no verdict changed
comparison.json               top band and Fable, with the variance analysis
date-sensitivity.json         per-run runtime-date audit
integrity.json                suite digest and untouched-artifact checks
scores.json                   flat per-run scores
AUDIT.md                      the scoring audit and its precedents
GENERATION-INCIDENT.md        duplicate generation of monday-004 run 1
../../audits/monday-opus5/    preflight, route audit, wire capture
```

## Integrity

Frozen suite digest **unchanged**:
`c056b4b43d3caeb3b50394282b08ed281a5716fb1df68d1666abb950aa0b2a80`.
`mondaybench verify-release --version 1.0` reports `scenarios`, `evaluators`,
`runs`, `verdicts`, `evaluations`, `leaderboards`, `config`, `taxonomy`,
`harness` and `tests` all **identical**. Zero modified tracked files. Nothing
published, no pricing recomputed, no website change.
