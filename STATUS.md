# MondayBench v1.0 — published 2026-08-31

Five scenarios, seven models, 105 official runs, all judged, every publication
gate passed. The suite is frozen and tagged `v1.0`. Everything below is
verified, not remembered.

## Verified state

```
pytest                                              835 passed
mondaybench verify-release --version 1.0 --strict   identical, 617 artefacts
freeze check, all five scenarios                    clean, in tree and in a fresh clone
official runs                                       105 / 105
criterion verdicts, all recorded                    2478
Overall v0 / v1 / v2                                all three still build
```

The suite digest is recorded in `releases/v1.0/SUITE-FROZEN.yaml` and nowhere
else. It must not be quoted in a file the manifest hashes — this one included —
or re-cutting the release changes the file that states the digest, which changes
the digest.

## The suite

| # | Scenario | Rubric | Criteria | Evaluator | Spread | Prompt sha256 |
|---|---|---|---:|---|---:|---|
| 001 | Back to Work | 0.2 | 19 | `evaluator-opus5-v0.1` | 27.3 | `ed4d7beb1d7d…` |
| 002 | Moving Targets | 0.2 | 20 | `evaluator-opus5-v0.2` | 40.7 | `740e627cbc74…` |
| 003 | Blockers | 0.3 | 21 | `evaluator-opus5-v0.3` | 29.7 | `aaf788f309d9…` |
| 004 | Numbers Don't Lie | 0.3 | 27 | `evaluator-opus5-v0.4` | 62.8 | `3a0cbb569ca4…` |
| 005 | Read the Room | 0.4 | 31 | `evaluator-opus5-v0.5` | 19.2 | `532cd464a9b7…` |

monday-001's atomic criteria sum to 90; the remaining 10 points are the
noise-resistance dimension, scored at dimension granularity. All five scenarios
contribute exactly 100.

## Overall v2

```
 #  model              Monday   001   002   003   004   005   range   sigma
 1  Qwen 3.8 Flash       95.1  92.5  94.8  94.5  96.5  97.0     4.5     1.8
 2  GLM 5.3 Flash        94.9  98.0  87.3  92.8  98.0  98.5    11.2     4.8
 3  DeepSeek V4 Flash    91.7  90.8  89.3  95.0  86.0  97.3    11.3     4.5
 4  MIMO v2.5            86.7  88.2  81.2  90.3  78.5  95.2    16.7     6.8
 5  GLM 5.2              86.5  84.3  91.2  87.3  71.2  98.5    27.3    10.1
 6  Qwen 3.6             68.8  82.8  70.2  65.5  46.0  79.3    36.8    14.5
 7  Gemma 4              63.0  70.7  54.2  65.3  35.2  89.7    54.5    20.2
```

Monday Score is the arithmetic mean of the five scenario scores, equal weight,
nothing else folded in. Range and sigma describe dispersion **across
scenarios** and are published beside the score, never inside it.

Overall v0 (three scenarios) and v1 (four) are untouched and still build. They
are different claims about different scenario sets, not superseded views of
this one.

**The 0.2 between first and second is not a ranking.** Qwen 3.8 Flash never
drops below 92.5 on any Monday; GLM 5.3 Flash wins four of five and loses 11
points on the second. See `analysis/capability-taxonomy-v0.2.md`.

**Serving caveat that travels with the result.** qwen3.6's three official
monday-004 runs came from NaN, not Helmcode, which was unreachable during
generation. NaN serves that model as a *reasoning* model and Helmcode does not,
on a byte-identical request. Recorded as a scenario-scoped override in
`models.yaml`.

## What v1.0 repaired

Three integrity defects. None moved a published score, and each is asserted
rather than claimed.

1. **A frozen scenario resolving to a superseded rubric.**
   `scenarios/monday-001/scenario.yaml` declares no `rubric_file`, so a default
   load returned `rubric.yaml` (0.1) while the scenario is frozen against
   `rubric-0.2.yaml`. Repaired in the resolver — `FROZEN.yaml` already recorded
   the right answer, so no frozen artefact was edited.
   `tests/test_rubric_resolution.py`.

2. **Capability profiles stale against their own taxonomy.**
   `capability-profiles-v0.1.json` covers three scenarios; the taxonomy it
   applies maps four. Repaired additively as
   `capability-profiles-v0.1.1.json`; the original is byte-identical and the
   v0.1 report now carries an erratum.
   `tests/test_capability_profiles_v011.py`.

3. **A CRLF working tree against an LF repository.** 220 files carried CRLF
   while git stored LF, so three of five freeze manifests failed in a fresh
   clone. `git diff` cannot show this — it normalises both sides. No prompt
   source was affected, so no `prompt_sha256` moved and no run was invalidated.
   `tests/test_line_endings.py`.

## Known, documented, not repaired

- **`evaluator-opus5-v0.1` declares no `scenario_id`**, so scenario-to-evaluator
  resolution for monday-001 falls through to a hardcoded fallback. Read the
  evaluator from the published leaderboard instead, as
  `challenge.official_evaluator` does. Recommended for v1.1 with a re-freeze.
- **`run --runs N` ignores archived run numbers.** `--reuse-valid-runs` handles
  it correctly.
- **Penalties are excluded from capability profiles.** A scenario penalty is a
  global deduction; attributing it to a capability would mean inventing the
  attribution. qwen3.6's −7 monday-005 breach shows in its Monday Score and not
  in its `information_boundaries` profile.

## Benchmarking a new model

A Monday Score is the mean of a model's own runs, so a challenger needs 15
generations and 354 criterion verdicts and moves no incumbent number.

```
mondaybench challenge --model <slug>       # what exists, what qualifies, what is left
mondaybench verify-release --version 1.0   # frozen content intact, evidence may only grow
```

Full runbook in `docs/benchmarking-a-new-model.md`. New models publish as
Overall **v2.1, v2.2, …** — same five scenarios, one more competitor. `v2` stays
byte-frozen.

## Things not to redo

- **Do not touch scenario content, any rubric, or any evaluator.** All are
  frozen; `verify-release` marks those groups `immutable`.
- **Do not regenerate or rejudge an incumbent.** Judge state is not reproducible
  across sessions, and a mixed-vintage board is not one measurement.
- **Do not rewrite `overall-v2.json`.** It is cited and hashed. Publish a
  revision instead.
- **Do not delete anything under `archive/`.** It holds every superseded
  battery — the earlier prompt hashes, the gateway cache hits, the
  16,000-token budget, and the calibration drafts of #002 through #005 — all
  evidence behind documented defects.
- **Do not remove `extra_body: {caching: false}`** from any model. Without it,
  back-to-back identical prompts return a byte-identical cached response in ~1s
  and run 3 becomes a copy of run 2.
- **`mondaybench results` writes files** and prints no summary. Run it only at
  publication time, or it overwrites the per-model cards.
- **Do not write files with CRLF.** `tests/test_line_endings.py` will fail, and
  it is right to.

## What v1.0 does not measure

Ranked in `analysis/capability-taxonomy-v0.2.md`:

1. **Temporal reasoning under a moving clock.** The field's worst capability
   (mean 61.0) and the only one whose shadow mass exceeds its primary mass — 22
   points depend on getting time right while scoring something else, against 14
   that score it directly.
2. **Multi-turn correction.** All five scenarios are one prompt and one
   response. Structural; no rubric change closes it.
3. **Entity resolution and data cleaning beyond one Monday.** Still #004-only.
4. **A criterion the field actually fails.** Zero of 500 points are
   constant-fail, so there is no evidence about where the frontier is.

`RECOMMEND #006` — temporal reasoning under a moving clock, delivered
multi-turn. Gaps 1 and 2 compose rather than compete. Not started.

The v0.1 open item about **noise resistance not discriminating** is now
confirmed at suite scale: `ownership_and_delegation` has never separated two
models across three scenarios and 105 runs, and `action_safety` is 87%
constant-pass. #006 should not spend points there.

---

# Historical — monday-001 under v0.1

Kept because it is the evidence behind documented defects, not because it is
current. The result it describes is superseded by the board above.

## The v0.1 result

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

Generation was `max_output_tokens: 32000`, `temperature: 0`, uniform across all
seven models. 441 verdicts, zero API calls during scoring; every run has a
`.review.md`.

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

## monday-001 labelling conventions

Recorded so a re-judge or a dispute can be held to the same line. Each was
derived from the rubric text and applied to every one of the 21 runs.

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
