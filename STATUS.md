# MondayBench v0.1 — published 2026-08-28

v0.1 is done. `monday-001` has an official result: 7 models, 3 runs each, 21
runs, all judged, every publication gate passed. Everything below is verified,
not remembered.

## Verified state

```
pytest                                                     173 passed
mondaybench freeze --scenario monday-001 --check            frozen content is intact
mondaybench validate --scenario monday-001 \
    --evaluator evaluator-opus5-v0.1                        validation passed
official runs                                              21 / 21
judged under evaluator-opus5-v0.1 (rubric 0.2)             21 / 21
mondaybench leaderboard --official                         published, all gates passed
```

- **Scenario:** `monday-001`, frozen. Prompt SHA-256 `ed4d7beb1d7d1029c36eb8533e449027e0dc1a1047f8a38951a91781a0a5e398`.
  `FROZEN.yaml` covers 9 canonical files; `validate` fails on drift.
- **Rubric:** `rubric-0.2.yaml`, version 0.2. Untouched since freezing.
- **Official evaluator:** `evaluator-opus5-v0.1` — judge `claude-opus-5`, route
  `recorded` (interactive session, verdicts in `verdicts/*.jsonl`).
- **Generation:** `max_output_tokens: 32000`, `temperature: 0`, uniform across
  all seven models.
- 441 verdicts, zero API calls during scoring. Every run has a `.review.md`.
- All 21 runs share one prompt hash. No duplicate responses, none truncated,
  every `finish_reason` is `stop`.

## The official result

```
 #  model              Monday Score  runs  range  TTFA med  total med
 1  GLM 5.3 Flash              98.0     3    1.5    118.8s     132.4s
 2  Qwen 3.8 Flash             92.5     3    6.0     72.2s      92.0s
 3  DeepSeek V4 Flash          90.8     3    8.0     55.4s      63.3s
 4  MIMO v2.5                  88.2     3    6.5     42.4s      64.1s
 5  GLM 5.2                    84.3     3   16.0      2.7s       6.9s
 6  Qwen 3.6                   82.8     3    5.0      0.8s       6.2s
 7  Gemma 4                    70.7     3    6.5      0.6s       5.5s
```

Artifacts: `leaderboard/leaderboard.{json,csv,md}` and
`leaderboard/models/<slug>.json`. The banner reads *"official v0.1 result. Every
publication gate passed."*

Two penalties in the whole battery, both `MATERIAL_HALLUCINATION` (−5) and both
`qwen3.6`, runs 001 and 002: proposed Enterprise pricing described as
confidential *until Wednesday's review*, when the source says confidential until
approved **and** publicly announced. Run 003 of the same model states it
correctly, which is why the model is not uniformly penalised.

`GLM 5.2` carries a 16-point range across its three runs (75.0 / 87.0 / 91.0) —
by far the widest in the battery, and worth knowing before quoting its mean.

## What happened to the 16,000-token battery

An earlier 20-run battery at `max_output_tokens: 16000` was judged in full and
then retired. `deepseek-v4-flash` stopped being able to answer at that budget —
two consecutive attempts produced 69,501 and 70,207 characters of reasoning and
no answer — so the budget was raised to 32,000 **for all seven models**, not
just the one that needed it, and the whole battery was regenerated.
`official.qualify_run` rejected all 20 old runs automatically on
`max_output_tokens 16000 != configured 32000`.

It is preserved under `archive/budget-16000/` with its own README. Its verdicts
are keyed by run id and this battery reuses those ids for different responses —
**do not serve them against the current runs.**

## Things not to redo

- **Do not touch scenario content or rubric 0.2.** Both are frozen; `validate`
  and `--official` enforce it.
- **Do not delete anything under `archive/`.** It holds the superseded
  calibration runs (`prompt-e19d123c/`), the four gateway cache hits
  (`cache-hits/`), and the retired 16,000-token battery (`budget-16000/`) —
  all evidence behind documented defects.
- **Do not remove `extra_body: {caching: false}`** from any model. Without it,
  back-to-back identical prompts return a byte-identical cached response in
  ~1s, and run 3 becomes a copy of run 2.
- **`mondaybench results` writes files** and prints no summary. Run it only at
  publication time, or it overwrites the per-model cards.
- Changing `max_output_tokens` again invalidates the whole battery. That is the
  gate working, not a bug.

## Labelling conventions used for all 21 runs

Recorded so a re-judge, a v0.2 battery, or a dispute can be held to the same
line. Each was derived from the rubric text and applied to every run.

- **`umbrella_error_rate`.** PASS needs the error count read against traffic: a
  rate, the 94,217 denominator beside the 163 errors, or the point that Stark
  carries more raw errors on far higher traffic while staying healthy. PARTIAL
  needs an explicit statement about the *other* customers — naming one, quoting
  their values, or ranking Umbrella among them — or a reference to Umbrella's own
  low request volume. A bare outlier adjective ("anomalous", "concerning",
  "stands out") is FAIL: it asserts noticeability, not a reading of the data.
- **`no_false_priorities`.** A false priority is an item the source marks
  resolved, delegated, completed, or explicitly non-urgent — the Acme close-out,
  Globex — ranked above legitimate critical work. One such item → PARTIAL, two or
  more → FAIL. A live inbound request that is merely over-ranked (the Initech
  holding reply) is **not** a false priority: over-ranking real work is already
  priced into `analytics_action` and `umbrella_and_churn_high`, and the rubric
  warns against charging one mistake twice.
- **`contoso_action` / `contoso_blocked`.** PASS needs the renewal put in
  jeopardy, not merely sequenced behind the question: "the only blocker on a
  €72k ARR renewal", "€72k ARR at stake", "signature slips to their next
  approval window", "critical for a €72k ARR renewal". "Pending one legal
  clarification", or the value with no consequence, is PARTIAL.
- **`friday_conversion_unknown`.** PASS requires naming the gap in the supplied
  material — "no conversion data was shared", "No data provided". Asking "real
  or noise?" under an "unclear" heading is PARTIAL. Two of 21 runs cleared it.
- **Placement is charged once.** Where a single bundled action item carries both
  a stale task and a release-readiness question, it is scored under
  `no_false_priorities`, not also under `analytics_action`.
- **Peer-range slips are not penalties.** Several runs quote an approximate
  floor for the peer p95 band; the point being made — Umbrella at 1821ms is a
  huge outlier — is correct. Recorded in the criterion evidence. The rubric says
  to be conservative and not to penalise harmless slips.

## Open items for v0.2

Detail in the two criterion-level sections at the end of `CALIBRATION.md`.

- **The ceiling is the main problem.** Eight criteria scored 21/21 PASS; with
  noise resistance's flat 10, **46 of the 100 base points are earned by every
  run**. The scenario is effectively scored out of 54.
- **Noise resistance does not discriminate** — no false action triggered in any
  of the 21 runs, in either battery. Make the items genuinely tempting or drop
  the dimension and redistribute its 10 points.
- **`umbrella_error_rate` is the strongest criterion** (0 PASS / 8 PARTIAL /
  13 FAIL). Models will compare customers; almost none divide. Keep it and build
  more like it.
- **`friday_conversion_unknown` is nearly a constant** (2 / 19 / 0). Reachable,
  but consider whether PASS should also accept flagging the gap without the
  explicit "not in the data" phrasing.
- **The judge-developer overlap is unresolved and inherent to
  `evaluator-opus5-v0.1`.** The same session that built the harness produced the
  labels. Every verdict ships with its evidence, which is the mitigation, not a
  claim that none was needed. An independent re-judge of the same 21 runs would
  be the single most valuable thing to do next.
- `IMPLEMENTATION.md` §22 deviation (penalty judge sees the sources) is
  documented in `README.md` and was proven necessary during calibration.
