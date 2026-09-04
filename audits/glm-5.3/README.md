# GLM 5.3 against MondayBench v1.0 — complete, and NOT eligible for the official Overall

**Date:** 2026-09-03
**Model:** GLM 5.3 (`glm5.3`), Helmcode, OpenAI-compatible route
**Suite:** v1.0, digest `c056b4b43d3caeb3b50394282b08ed281a5716fb1df68d1666abb950aa0b2a80`
**Outcome:** 15/15 official runs generated and judged. Measured Monday Score **93.73**.
**It is not published anywhere**, because the harness's own comparability gate
refuses four of the five scenario boards and the only remedy it offers is one
this project forbids.

---

## What was asked, and what happened

Run GLM 5.3 through the official MondayBench route — 5 scenarios, 3 independent
runs each, frozen prompts, frozen rubrics, the recorded Opus 5 judge — and
integrate it only if every gate passes.

Everything up to publication passed. Publication did not, and the reason is
structural rather than anything about this model.

---

## 1. Identity

The header of `models.yaml` said, of the ids a spec had guessed on 2026-08-27,
that "`glm-5.3`, `qwen-3.8-flash` and `kimi-k3` exist nowhere". That was true
then. It is now stale for one of them: Helmcode serves **`glm5.3`**.

| | |
|---|---|
| Display name | GLM 5.3 |
| Requested model id | `glm5.3` |
| Served model id | `glm5.3` — echoed on every SSE frame and on the non-streaming body |
| Gateway | `https://api.helmcode.com/v1` (`HELMCODE_BASE_URL`) |
| Provider adapter | `mondaybench.providers.openai_compatible.OpenAICompatibleProvider` |
| Upstream vendor | Z.AI on six probes; Parasail on one long-prompt probe |
| Reasoning | Yes, by default. Streams `reasoning_content` and reports `reasoning_tokens` |
| Reasoning mode / effort | UNOBSERVABLE — this gateway exposes no such parameter |
| Context window | UNOBSERVABLE from the client; not asserted |
| Max output tokens | 32,000 model default; the scenario's safety ceiling wins (32k / 96k / 131,072) |
| Temperature | Supported; 0 accepted, `unsupported_parameters` empty on all 15 runs |
| top_p | Accepted when probed; not pinned in `models.yaml`, so never sent |
| Pricing identity | First-party, from gateway `cost_details` — see below |

**This is not GLM 5.3 Flash.** `glm5.3-flash` is a separate `models.yaml` entry
served by NaN and stays there. No id was ambiguous: `mondaybench endpoints`
returns exactly one `glm5.3` on Helmcode.

**Identity confidence: high on the id, medium on the deployment.** A client
cannot see past the gateway — `/model/info` and `/model_group/info` return 404,
as the `models.yaml` header already records for `glm5.2`. The distinguishing
evidence available is that `glm5.3` and `glm5.2` produced different output on an
identical prompt at temperature 0.

**Not hardcoded.** `models.yaml` had no entry, so one was added — the only
configuration file this campaign touched. No prompt, rubric, ground truth,
scoring rule, incumbent run or incumbent verdict was modified.

## 2. Route

    mondaybench run
      -> runner.generate
      -> providers.build_model_provider()
      -> OpenAICompatibleProvider (httpx, streaming)
      -> Helmcode gateway
      -> glm5.3

No Claude Code, no OpenCode, no agent loop, no tools, one isolated completion
per run.

`wire-capture.json` records the exact body the adapter builds for each frozen
scenario, built and not sent. For all five: exactly two messages, the frozen
system prompt verbatim, a user message whose sha256 equals the published prompt
hash, no `tools` key, no history, no injected date, no cwd, no repo metadata.
The only non-standard body key is `caching: false`, which the `models.yaml`
header documents and which changes nothing the model sees.

**Route equivalence: EQUIVALENT.** No material prompt contamination.

## 3. Frozen release

`verify-release --version 1.0` verified before generation, and all five prompt
hashes were re-derived independently:

    monday-001  ed4d7beb1d7d1029c36eb8533e449027e0dc1a1047f8a38951a91781a0a5e398
    monday-002  740e627cbc7413c321ede0d54000504de54821d34ff4677f82731b89600423a8
    monday-003  aaf788f309d955d2b427c86fe7d95d2bbf88575fde7306adcfd74b0ec4a4103f
    monday-004  3a0cbb569ca4f711b8907177af9204cec267d26f35f732829df56b03ed23ef99
    monday-005  532cd464a9b75045f808886c44e667237d6fd1b947826510643b9f8bcc30059a

All five match. Suite digest matches. System prompt sha256
`75357d685f238b6afd7738be9786fdafde641eb6ca9a3be7471939715a68a4de` on every run.

## 4. Config freeze

`config-snapshot.json`, written before the first generation. Three
`config_sha256` values, one per safety-ceiling group — 32,000 for
monday-001..003, 96,000 for monday-004, 131,072 for monday-005 — which is the
scenarios' own configuration, not a per-model exception. No temperature or top_p
exception was needed. Unobservable fields are recorded as UNOBSERVABLE rather
than given an invented default.

## 5. Preflight

`preflight.json` and `preflight-probes.json`. Non-scored, on a synthetic prompt;
no frozen scenario prompt was used. Every check passes: HTTP 200, requested ==
served, streaming, finish reason, usage, reasoning observable, zero tool calls,
no auxiliary calls, no hidden routing to another model.

## 6-8. Runs

15 official runs, 3 per scenario. Every gate in `official.qualify_run` passes on
every run:

* correct scenario, correct prompt hash, correct config hash
* requested model `glm5.3`, provider `helmcode`, temperature 0, correct ceiling
* `finish_reason=stop` on all 15; no truncation; no empty output
* reasoning **DELIVERED** on all 15, from `explicit_reasoning_tokens`
* `unsupported_parameters` empty on all 15
* **15 distinct response hashes** — no duplicate, so no cached sample

**One replacement, and it replaced nothing.** The first attempt at
monday-004 run 3 failed provider-side: 18,147 characters of reasoning, then the
turn ended with no answer and `finish_reason=None`. Not a truncation — the
ceiling was 96,000 and the budget was not the cause. The runner classifies this
as `empty_final_answer`, treats it as non-transient, and **writes no run file**,
so there was no invalid run to replace and nothing was silently overwritten. The
attempt is recorded in `runs/monday-004/glm5.3/failed-attempts.jsonl` and the
third run was generated with `--reuse-valid-runs` under the identical config.
`mondaybench serving` counts it as an attempt: 16 attempts, 15 official.

## 9-10. Scores

Judged against the frozen rubric versions — 0.2 / 0.2 / 0.3 / 0.3 / 0.4 — with
the official evaluator for each scenario, applying the tie-break "if a response
sits between two labels, choose the lower". `factual_plan_accuracy` in
monday-003 was scored only against `factual_anchors`. No incumbent's labels or
scores were consulted to decide any label.

Every score below was **recomputed from the atomic criterion verdicts** by
`summaries.py` and matches the stored evaluation:

| Scenario | Runs | Mean | sd | Range |
|---|---|---:|---:|---:|
| monday-001 | 100.0 / 94.0 / 98.5 | **97.50** | 3.12 | 6.0 |
| monday-002 | 85.5 / 88.0 / 89.5 | **87.67** | 2.02 | 4.0 |
| monday-003 | 98.0 / 93.5 / 93.0 | **94.83** | 2.75 | 5.0 |
| monday-004 | 95.0 / 81.5 / 98.5 | **91.67** | 8.98 | 17.0 |
| monday-005 | 96.0 / 96.0 / 99.0 | **97.00** | 1.73 | 3.0 |

**Overall Monday Score: 93.73** — the equal-weight mean of the five scenario
means, not weighted by criterion count.

Worst Monday: **monday-002 (87.67)**. Best: **monday-001 (97.50)**.
Scenario spread: **9.83**. That spread is variation across five *different
tasks* and is not an estimate of judge noise; this benchmark's judge is
recorded, so judge variance cannot be sampled independently at all.

The one wide run-range is monday-004 at 17.0 points. It is a real difference
between the answers, not noise: run 2 argued the product-priority decision from
absolute contribution and carried an ARR bridge whose stated direction
contradicted its own components, while run 3 did neither.

## 11. Capabilities

`capabilities-summary.json`, plus the full payloads for both taxonomy versions.
Computed with `mondaybench/capabilities.py` — the canonical implementation —
so the semantics are the repo's: points awarded over points available, counting
only criteria whose PRIMARY mapping is that capability, penalties excluded.
Nothing is recomputed in a frontend.

**Audit only. No official artifact was written**, and none should be:
`mondaybench capabilities` profiles models from official scenario leaderboards,
and GLM 5.3 is on none.

## 12. Cost and efficiency

`pricing-summary.json`. Pricing is first-party verifiable, measured from the
gateway's own `usage.cost_details`, not from a price list.

Two rates were observed, because the gateway fans `glm5.3` out across upstream
vendors:

| Upstream | Input $/M | Output $/M | Observations |
|---|---:|---:|---|
| Z.AI | 0.075 | 0.25 | 6, including every probe at benchmark prompt size |
| Parasail | 0.15 | 0.50 | 1, on a long prompt |

The served model id was `glm5.3` on both, so this is an upstream-vendor
difference, not a different model. A third observation is worth recording: an
immediately repeated prompt was billed at an effective input rate of
$0.016/M despite `extra_body: {caching: false}`.

**Per-run cost is not observable.** The streaming response the runner uses
carries neither `provider` nor `cost`; both appear only on non-streaming calls.
The figures below are therefore derived from measured rates and recorded token
counts, not read from the run files.

Across the 15 runs: mean input 4,669 tokens, mean output 21,299, mean reasoning
19,288. Reasoning tokens are **inside** `completion_tokens` and are not added
again.

| | Z.AI rate | Parasail upper bound |
|---|---:|---:|
| cost / task | $0.005675 | $0.011350 |
| cost / 1k tasks | $5.67 | $11.35 |
| cost / 100k tasks | $567.48 | — |
| cost / 1M tasks | $5,674.84 | — |

One completion per task. MondayBench is not an agent benchmark and there are no
steps to multiply.

Efficiency: median TTFT **2,108 ms**, median TTFA **253,260 ms**, median total
latency **286,620 ms**. TTFA and total latency are dominated by reasoning; the
model spends 91% of its output budget thinking. One outlier is worth naming:
monday-005 run 1 took 2,231 seconds end to end, roughly three times the next
slowest run of that scenario.

## 13. Eligibility: EXCLUDED from the official Overall

Nine of the eleven eligibility conditions pass. Two do not, and they are the
same fact seen twice.

| Condition | |
|---|---|
| Standard MondayBench provider route | PASS |
| Frozen prompts | PASS |
| Matching config across official runs | PASS |
| Valid model identity | PASS |
| No material prompt contamination | PASS |
| No reasoning delivery failure | PASS — DELIVERED on all 15 |
| Run-count gate | PASS — 3/3 on all five |
| Release verification gates | PASS |
| Scoring artifacts valid | PASS |
| **Scenario leaderboards publishable** | **FAIL on monday-001..004** |
| **Overall revision publishable** | **FAIL — needs all five** |

### The blocker

`mondaybench leaderboard --official` refuses monday-001 through monday-004:

    integrity warning: MIXED JUDGE VERSIONS across models (2 distinct):
    rubric=0.2/judge=2725f54f7f1dd9f6, rubric=0.2/judge=45998b3c03939498
    - this ranking is not valid; re-evaluate every run with --overwrite

`judge_prompt_fingerprint()` hashes the judge prompt templates **and the verdict
JSON schemas**. `PENALTY_SCHEMA` embeds `PENALTY_TYPE_VALUES`, the shared
penalty vocabulary in `schemas.py` — and that vocabulary grew as scenarios were
added: `MAJOR_DATA_ERROR` and `UNSUPPORTED_CAUSALITY` with monday-004,
`CONFIDENTIALITY_BREACH` with monday-005. So the fingerprint changed four times
over the life of the suite:

| Fingerprint | Carried by |
|---|---|
| `2725f54f7f1dd9f6` | the 7 incumbents on monday-001 |
| `b10748f5636ba6a6` | the 7 incumbents on monday-002 and monday-003 |
| `26067608db5f7a2d` | the 7 incumbents on monday-004 |
| `45998b3c03939498` | the 7 incumbents on monday-005 — and everything judged today |

**This is not about GLM 5.3.** Any model judged today is stamped
`45998b3c03939498` on every scenario, so it can only ever join monday-005's
board. The frozen suite v1.0 cannot currently accept the eighth model that
`docs/benchmarking-a-new-model.md` describes, for four of its five scenarios.

It is also spurious as a comparability signal *on this route*. The recorded
judge never builds a prompt — `RecordedJudge` serves labels from a file and
constructs no provider — so the fingerprint records the state of code that had
no part in producing any of these labels.

### Why it was not worked around

The remedy the error names, `--overwrite` every run, would rewrite 7 incumbents
× 4 scenarios of evaluation files. Their scores would not move — replaying the
same recorded verdicts yields identical numbers — but the files would change,
and:

* the campaign brief forbids touching prior runs and prior verdicts;
* `docs/benchmarking-a-new-model.md` forbids it twice, in step 3 ("Never rejudge
  incumbents to 'match' a challenger") and in step 6 ("If check 1 reports a
  **changed** ... file under ... `evaluations`, stop");
* `evaluations` is `append_only` in the release manifest, so the suite would
  stop verifying.

Changing the integrity rule instead would be changing a scoring rule. Rebuilding
the harness at four historical commits so the challenger's stamp matches each
scenario's incumbents would manufacture agreement rather than establish it.

**monday-005 did publish** — its incumbents share today's fingerprint — placing
GLM 5.3 fourth at 97.0. That board was then **reverted to its committed state**.
A model on one official scenario board and absent from the other four is a
half-integrated result, and it would have fed a one-scenario capability profile.
The evidence stays on disk; only the published ranking was rolled back.

## 14. Where it would have landed

Measured, not published. Against the current board:

| Model | Monday Score | vs GLM 5.3 |
|---|---:|---:|
| Claude Opus 5 (provisional) | 97.07 | +3.34 |
| Qwen 3.8 Flash | 95.07 | +1.34 |
| GLM 5.3 Flash | 94.93 | +1.20 |
| Claude Fable 5.1 (provisional) | 94.90 | +1.17 |
| **GLM 5.3 (measured, unpublished)** | **93.73** | — |
| DeepSeek V4 Flash | 91.70 | −2.03 |
| Gemini 3.8 Flash High (provisional) | 88.37 | −5.36 |
| MIMO v2.5 | 86.67 | −7.06 |
| GLM 5.2 | 86.50 | −7.23 |
| Qwen 3.6 | 68.77 | −24.96 |
| Gemma 4 | 63.00 | −30.73 |

The comparison that will be asked for is GLM 5.3 against GLM 5.3 Flash: **93.73
against 94.93, a 1.20-point gap in Flash's favour.** That is not a result. Each
figure is a mean of three runs whose per-scenario standard deviations run from
1.7 to 9.0 points; a gap of 1.2 is inside that. GLM 5.3 is ahead of Flash on
monday-002 (87.67 against 87.33) and behind on monday-001, 003, 004 and 005.
Nothing here establishes that the larger model is better or worse than the Flash
one on this benchmark, and the honest summary is that they are close.

The gap to GLM 5.2 (+7.23) is a different matter — that one is wide relative to
run variance.

## 15. Website

**Not updated. Correct outcome, not an oversight.** GLM 5.3 is not OFFICIAL, so
it belongs on no leaderboard, no scenario view, no capability view, no cost or
efficiency view. `helmcode-site` was not touched.

## 16. Integrity

`verify-release --version 1.0`:

| group | policy | status |
|---|---|---|
| scenarios | immutable | **identical** |
| evaluators | immutable | **identical** |
| taxonomy | immutable | **identical** |
| leaderboards | append_only | **identical** |
| harness | mutable | **identical** |
| tests | mutable | **identical** |
| runs | append_only | 16 added |
| verdicts | append_only | 5 added |
| evaluations | append_only | 15 added |
| config | mutable | 1 changed (`models.yaml`) |

Suite digest unchanged. `check_sample_provenance` clean on all five scenarios.
`tests/test_overall_v2.py` — the 23 tests that assert every incumbent's Monday
Score is what it was — all pass. No incumbent run, verdict, evaluation or
leaderboard file changed. No pricing snapshot changed. No unrelated tracked file
was touched.

`pytest -q`: **830 passed, 7 failed.** None indicates corrupted evidence:

* `test_line_endings::test_no_released_artifact_contains_a_carriage_return` —
  **pre-existing**, 54 untracked files under `analysis/cost-value/` dated
  2026-09-02, before this campaign. (A second line-ending failure *was* caused
  here — `models.yaml` was rewritten with CRLF — and has been corrected.)
* `test_capabilities::test_every_model_gets_a_profile` (8 != 7),
  `test_sample_provenance` D and E (24 != 21),
  `test_suite_release::test_the_manifest_digests_match_the_working_tree`
  (16 added files), and `test_cli_endpoints` ×2 (the stub's served list has no
  `glm5.3`) — all six are "the suite has exactly seven models" assertions that
  any eighth model trips by construction, the same structural issue as the
  fingerprint.

## 17. Artifacts

    audits/glm-5.3/
      README.md                        this file
      preflight.json                   preflight verdict, identity, route equivalence
      preflight-probes.json            raw probe output
      wire-capture.json                the exact request body per frozen scenario
      routing-probes.json              upstream fan-out at benchmark prompt size
      pricing-probes.json              per-token rates from cost_details
      config-snapshot.json             the config freeze, written before run 1
      run-summary.json                 all 15 runs with every qualification field
      score-summary.json               scores recomputed from the atomic verdicts
      capabilities-summary.json        capability breakdown (audit only)
      capabilities-summary-v0.1.json   full payload, taxonomy 0.1
      capabilities-summary-v0.2.json   full payload, taxonomy 0.2
      pricing-summary.json             cost and efficiency
      preflight_probe.py               \
      make_config_snapshot.py           |
      wire_capture.py                   > the scripts that produced the above
      verdicts_build.py                 |
      v_monday_002..005.py              |
      summaries.py                      |
      capabilities_audit.py            /

    runs/monday-00{1..5}/glm5.3/        15 runs + one failed-attempts.jsonl
    verdicts/glm5.3.verdicts.jsonl                      monday-001
    verdicts/monday-00{2..5}/glm5.3.verdicts.jsonl      the rest
    evaluations/evaluator-opus5-v0.{1..5}/monday-00{1..5}/glm5.3/   15 evaluations
    models.yaml                         one new entry

All in the repo's canonical locations. No parallel structure was invented.

## What would unblock this

Not a decision for this campaign, but the options are worth writing down:

1. **Exclude the verdict schemas from `judge_prompt_fingerprint()`**, or version
   the fingerprint per scenario so a later scenario's penalty type cannot
   retroactively change an earlier scenario's judge identity. This is a harness
   change and would need its own justification and tests.
2. **Accept that v1.0 is closed to new models on monday-001..004** and cut a
   v1.1 whose incumbents are re-stamped in one deliberate, documented pass —
   which does rewrite evaluation files, but as an announced release action
   rather than as a side effect of adding a challenger.

Either way the 15 runs and 354 verdicts here stand: they are valid evidence
generated under the published conditions, and they are what a future publication
would use.
