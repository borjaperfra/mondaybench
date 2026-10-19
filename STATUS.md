# MondayBench suite v1.13 — Overall v3.6, published 2026-10-19

Five scenarios, fifteen models, 225 official runs, all judged, one board. The
suite is released as `v1.13` and the board it carries is Overall v3.6. Everything
below was verified against this working tree, not remembered.

**v1.13 adds two NaN models as official rows.** DeepSeek V4.1 Flash (1017),
**91.23**, rank 9, and MiMo v2.6 Flash, **87.87**, rank 10, were generated on
NaN on 2026-10-19 and judged blind the same day by Claude Opus 5.5
(`experiments/nan-challengers-2026-10-19-opus-judge/`). NaN ignored
`caching: false` that day: runs 2-3 came back byte-identical to run 1. So each
run sends `seed: <run_number>` (`generation.seed_per_run`, new in the harness),
and the unseeded attempt is archived in `archive/nan-unseeded-2026-10-19/`.
The 196 v1.10 evaluations were re-stamped into v1.13 with zero scores changed,
and every incumbent row on all five scenario boards equals its v1.10 row.
`tests/test_v1_13_nan_challengers.py` pins both scores, the seeds, and that no
incumbent moved.

**v1.12 added estimated costs for GPT-6 Astra and Gemini 3.8 Flash (High).**
Neither route reports billing, so both were unpriced. On 2026-10-16 the owner
decided they should appear on the site's quality-vs-cost chart as labelled
estimates. `audits/pricing/gpt-6-astra/` and `audits/pricing/gemini-3.8-flash/`
price the fifteen existing runs of each at the vendor's verified API list rates
from tokens counted offline: Astra at **$136.83** per 1,000 tasks (Codex's own
output counter, reasoning included; MEDIUM), Gemini at **at least $12.06**
(visible answer only, o200k_base as a proxy tokenizer, thinking unrecorded;
LOW). No score, run, verdict or board changed; the new files are additive.

## Verified state

```
pytest                                             993 passed
verify-release --version 1.13 --strict             identical, 2,341 artefacts
verify-release --version 1.12                      verified within policy
freeze check, all five scenarios                   frozen content intact
official runs behind the v3.6 board                225 / 225
recorded evaluations, v1.13 subtree                226
criterion verdicts behind them                     5,330
```

**v1.10 puts three closed models on the board as official rows.** Claude Opus
5, Claude Fable 5.1 and Gemini 3.8 Flash (High) had been shown on the site as
provisional; on 2026-10-15 the owner decided they are official, and the only
distinction the site keeps is open versus closed weights. Nothing was generated
and nothing was judged for this release. The fifteen preserved responses of
each became run files byte for byte, through a build script kept beside each
source (the GPT-6 Astra pattern, commit 4d51bda), and the labels are the exact
sets that already reproduced the published scores:

| Model | Monday Score | Generated through | Labels by |
|---|---:|---|---|
| Claude Opus 5 | 97.07 | `claude -p`, Claude Code CLI 2.1.258 | GPT-5.6 Sol, independent blind re-judge |
| Claude Fable 5.1 | 94.90 | `claude -p`, Claude Code CLI 2.1.258 | the recorded Claude Opus 5 judge, after a ten-label audit |
| Gemini 3.8 Flash (High) | 86.00 | Antigravity Language Server, Connect-RPC | Claude Opus 5.5, blind re-judge |

All 45 per-run scores from `evaluate --suite-version 1.10` equal the ones
`audits/capabilities/build-provisional-capabilities.py` computes, and all three
Monday Scores reproduce exactly (`audits/capabilities/build-board-verdicts.py
--check`). The 151 v1.5 evaluations were re-stamped into the v1.10 subtree with
zero labels and zero scores changed, so **no incumbent number moved**:
`tests/test_v1_10_closed_models.py` pins the three new scores and every
incumbent row of v3.4 against v3.5.

No harness check was changed to admit them. One test was:
`test_sample_provenance.py::test_E2` required every monday-005 run without a
provider request id to carry a Codex thread id. It now accepts the session id of
any declared runtime block (Opus 5's `claude -p` session ids qualify), and names
Fable 5.1 and Gemini 3.8 Flash as the two batteries whose route recorded no
per-call identity at all - an explicit, checked exception, not a silent one.

**v1.9 gave Gemini 3.8 Flash (High) its labels.** Its published 88.37 had no
criterion-level labels, so it could not enter the capability profiles. Its
fifteen responses were re-judged blind, criterion by criterion, by Claude Opus
5.5 (not the Opus 5 that labelled the incumbents): **86.00**, with labels,
scores and the brief in `experiments/gemini-3.8-flash-high-opus-judge/`. Most
of the 2.37-point drop is monday-004, where every run now carries an
`UNSUPPORTED_CAUSALITY` penalty for inventing why customers churned. v1.10 is
the release that puts that number on the board.

**v1.8 is documentation, not a measurement.** The README, `docs/methodology.md`
and `docs/benchmarking-a-new-model.md` were still written for v1.0 — seven
models, Overall v2 as current, a judge whose variance "cannot be estimated".
v1.8 brings them up to this board and to what the cross-judge checks actually
show (see *The judge* below). No run, label, evaluation or score changed.

**v1.6 and v1.7 are repairs, not new measurements.** No run was generated, no
response was re-judged, no score moved, and the board is the same Overall v3.4
that v1.5 published. v1.6 stopped the manifest pinning 30 evaluation paths that
do not exist — see *The v1.5 defect, repaired in v1.6 and v1.7* below. v1.7 is
the same tree with the release writer fixed: it was the last writer in the
harness not pinning LF, so on Windows it wrote the release manifest itself with
line endings this repository forbids. v1.5 remains published and remains
non-verifying; that is the honest record.

Each suite digest is recorded in that release's `releases/v<N>/SUITE-FROZEN.yaml`
and nowhere else. It must not be quoted in a file the manifest hashes — this one
included — or re-cutting the release changes the file that states the digest,
which changes the digest.

## The suite

| # | Scenario | Rubric | Criteria | Evaluator | Spread | Prompt sha256 |
|---|---|---|---:|---|---:|---|
| 001 | Back to Work | 0.2 | 19 | `evaluator-opus5-v0.1` | 27.3 | `ed4d7beb1d7d…` |
| 002 | Moving Targets | 0.2 | 20 | `evaluator-opus5-v0.2` | 40.7 | `740e627cbc74…` |
| 003 | Blockers | 0.3 | 21 | `evaluator-opus5-v0.3` | 29.7 | `aaf788f309d9…` |
| 004 | Numbers Don't Lie | 0.3 | 27 | `evaluator-opus5-v0.4` | 62.8 | `3a0cbb569ca4…` |
| 005 | Read the Room | 0.4 | 31 | `evaluator-opus5-v0.5` | 19.2 | `532cd464a9b7…` |

Unchanged since v1.0. monday-001's atomic criteria sum to 90; the remaining 10
points are the noise-resistance dimension, scored at dimension granularity. All
five scenarios contribute exactly 100. A model that clears all five records 354
criterion verdicts.

## Overall v3.6

```
 #  model                    Monday    001    002    003    004    005   range   sigma
 1  GPT-6 Astra               98.80  100.0  100.0  100.0   98.0   96.0    4.00    1.79
 2  Claude Opus 5             97.07   98.5   98.0   98.3   90.8   99.7    8.84    3.54
 3  Qwen 3.8 Flash            95.07   92.5   94.8   94.5   96.5   97.0    4.50    1.79
 4  GLM 5.3 Flash             94.93   98.0   87.3   92.8   98.0   98.5   11.17    4.84
 5  Claude Fable 5.1          94.90   97.5   91.0   96.7   89.3  100.0   10.67    4.53
 6  DeepSeek V4.1 Flash       94.53   95.0   93.0   96.3   90.0   98.3    8.33    3.19
 7  GLM 5.3                   93.73   97.5   87.7   94.8   91.7   97.0    9.83    4.10
 8  DeepSeek V4 Flash         91.70   90.8   89.3   95.0   86.0   97.3   11.33    4.51
 9  DeepSeek V4.1 Flash (1017)91.23   90.3   95.2   95.8   79.7   95.2   16.16    6.83
10  MiMo v2.6 Flash           87.87   82.7   83.7   93.2   80.3   99.5   19.17    8.14
11  MIMO v2.5                 86.67   88.2   81.2   90.3   78.5   95.2   16.67    6.80
12  GLM 5.2                   86.50   84.3   91.2   87.3   71.2   98.5   27.33   10.08
13  Gemini 3.8 Flash (High)   86.00   95.3   80.0   84.7   72.2   97.8   25.66   10.68
14  Qwen 3.6                  68.77   82.8   70.2   65.5   46.0   79.3   36.83   14.49
15  Gemma 4                   63.00   70.7   54.2   65.3   35.2   89.7   54.50   20.17
```

Monday Score is the arithmetic mean of the five scenario scores, equal weight,
nothing else folded in. Range and sigma describe dispersion **across
scenarios** and are published beside the score, never inside it. Run-to-run
stability is a separate table in `leaderboard/overall/overall-v3.6.md`.

Overall v0 (three scenarios), v1 (four), v2, and v3 through v3.5 are untouched
and stay byte-frozen. They are different claims about different scenario sets
and different suite versions, not superseded views of this one.

**Seven caveats travel with this board.**

- **DeepSeek V4.1 Flash is scored from a different judge's labels.** Its
  battery was judged blind twice: 93.03 by the Opus session judge that scored
  the other nine v3.4 rows (labels in
  `experiments/deepseek-v4.1-flash-rerun-v1/blind-verdicts/`), and 94.53 by
  GPT-5.6 Sol (labels in `verdicts/monday-00N/deepseek-v4.1-flash-rerun-v1.verdicts.jsonl`).
  The board publishes 94.53. Under the Opus labels the row would rank 7th,
  below GLM 5.3. Kept as published and declared, by decision on
  2026-10-15; on v3.4 the site bracketed positions 2–5 as one group whose order
  is not established.

- **GPT-6 Astra was generated through the Codex CLI**, because no authenticated
  Astra API route exists. The frozen prompts match by sha256 and each candidate
  ran in its own ephemeral session, but everything the runtime does not expose
  — temperature, top_p, caching, the output ceiling, the resolved model id,
  finish reason, every token count — is recorded as `null` and never as a
  number. For that row, non-truncation rests on the Codex completion events and
  not on this harness.
- **Claude Opus 5 and Claude Fable 5.1 were generated through `claude -p`**
  (Claude Code CLI 2.1.258, OAuth subscription, effort high), because
  `claude-opus-5` returned credits_exhausted through Helmcode, Fable 5.1 is on
  no allowlist, and the Anthropic API is closed by project rule. The bytes
  passed to the route match the frozen prompts by sha256, but the route
  prepends its Agent SDK preamble to the system prompt and injects the user's
  identity and the runtime date (2026-09-02) into the user turn, so the user
  turn as delivered is not the frozen bytes. Temperature is not settable. The
  route reports its own 64,000-token output ceiling, recorded on each run as
  `safety_ceiling_tokens` with that provenance; it is not the scenarios'
  configured ceiling, and it bound nothing - every run ended `end_turn`, the
  largest at 24,674 output tokens. `max_output_tokens`, temperature, top_p,
  request ids and latency are `null`; the host timings and the route's
  list-price cost stay in each run's runtime block.
- **The three new rows are labelled by three different judges.** Claude Opus 5
  by GPT-5.6 Sol (the Opus 5 session judge is the candidate, and gave 97.10);
  Claude Fable 5.1 by the recorded Opus 5 judge after the ten corrections in
  `experiments/fable-5.1-full-mondaybench/AUDIT.md`; Gemini 3.8 Flash by Claude
  Opus 5.5, not the Opus 5 that labelled the incumbents. Each `models.yaml`
  entry says which.
- **Gemini 3.8 Flash (High) was generated through Antigravity** (Language
  Server ide-2.4.5, Connect-RPC `GetModelResponse`, thinking budget High). The
  RPC carries the prompt and a model placeholder only: no system prompt is
  sent, and temperature, the served model id, token usage, finish reason and
  the output ceiling are unobservable and recorded as `null`. Its pack's
  `finish_reason: stop` came from a character-count heuristic, so it is not
  carried into the run.
- **DeepSeek V4.1 Flash (1017) and MiMo v2.6 Flash were generated on NaN with
  a per-run seed** and labelled blind by Claude Opus 5.5, not the Opus 5 that
  labelled ten rows. No other row carries a seed. The 1017 version is stated by
  NaN's operator; the endpoint names none, and the row is separate from
  DeepSeek V4.1 Flash (the September Helmcode deployment). MiMo v2.6 spent the
  whole 32,000-token ceiling reasoning with no answer on 6 of 6 monday-004
  attempts before 13:00 UTC and on 2 of 5 monday-002 attempts; from 13:25 UTC
  monday-004 answered 3 of 3. The ceiling was not raised; failed attempts are
  in each scenario's `failed-attempts.jsonl`. NaN is quota-priced, so neither
  row has a cost.
- **qwen3.6's three official monday-004 runs came from NaN, not Helmcode**,
  which was unreachable during generation. NaN serves that model as a
  *reasoning* model and Helmcode does not, on a byte-identical request.
  Recorded as a scenario-scoped override in `models.yaml`.

## The release line

| Suite | Released | Board | What it added |
|---|---|---|---|
| v1.0 | 2026-08-31 | Overall v2 | Seven models, the first frozen suite |
| v1.1 | 2026-09-03 | Overall v3 | The judge contract; GLM 5.3 |
| v1.2 | 2026-09-10 | Overall v3.1 | DeepSeek V4.1 Flash, first battery |
| v1.3 | 2026-09-11 | Overall v3.2 | GPT-6 Astra |
| v1.4 | 2026-09-11 | Overall v3.3 | The DeepSeek reliability-prompt row |
| v1.5 | 2026-09-11 | Overall v3.4 | DeepSeek re-measured; two batteries dropped |
| v1.6 | 2026-09-12 | Overall v3.4 | Manifest repair; no measurement changed |
| v1.7 | 2026-09-12 | Overall v3.4 | The release writer now writes LF |
| v1.8 | 2026-10-15 | Overall v3.4 | Documentation brought up to v1.7 |
| v1.9 | 2026-10-15 | Overall v3.4 | Gemini 3.8 Flash re-judged with criterion labels, and its capability profile |
| v1.10 | 2026-10-15 | Overall v3.5 | Claude Opus 5, Claude Fable 5.1 and Gemini 3.8 Flash as official rows |
| v1.11 | 2026-10-15 | Overall v3.5 | Cost artefacts and the new-model runbook brought up to v1.10; no measurement changed |
| v1.12 | 2026-10-16 | Overall v3.5 | Estimated costs for GPT-6 Astra and Gemini 3.8 Flash (High) |
| v1.13 | 2026-10-19 | Overall v3.6 | DeepSeek V4.1 Flash (1017) and MiMo v2.6 Flash, seeded on NaN |

**Why DeepSeek was re-measured.** The gateway serves V4.1 Flash under the same
id as V4 Flash and replaced the deployment in place rather than publishing a
second id, so the same request reached different weights on different days.
Measured on 2026-09-11, the five frozen prompts return 1.3x to 2.5x the
reasoning of the 2026-09-10 battery at equal or better throughput. The 09-10
battery therefore no longer describes what the id serves. It and its
reliability-prompt variant are not members of v1.5; their runs, verdicts and
v1.4 evaluations are untouched on disk.

**The reliability prompt is on no board.** Re-run against the current
deployment: +1.57 points under the Opus judge (labels in
`experiments/deepseek-v4.1-flash-rerun-guardrail-v1/claude-blind-verdicts/`),
+0.04 under GPT-5.6 Sol (whose guardrail labels are not in this repository),
p = 0.42 on a permutation test. What moves is the floor — worst run 87.5 against 80.5, sd
4.00 against 6.08 — which is what the prompt was written to do and is not what a
mean can show. It stays under `experiments/`.

## The v1.5 defect, repaired in v1.6 and v1.7

Found and repaired 2026-09-12. **Nothing behind a published score was ever
missing.** The v1.5 manifest listed 30 evaluation files that are not on disk,
and `evaluations` is `append_only`, so verification failed.

The 30 split into two unrelated cases.

1. **15 phantom paths for `deepseek-v4.1-flash-rerun-v1`.** The judge wrote
   these at the unversioned `evaluations/<evaluator>/<scenario>/<slug>/`
   default and they were re-stamped into `evaluations/v1.5/` afterwards — but
   the manifest was cut from the pre-re-stamp scan, so it records both
   locations. The 15 real files are present, identical, and also in the
   manifest. Nothing is lost; the manifest names a path that no longer exists.

2. **15 genuinely absent evaluations for `deepseek-v4.1-flash-probe`.** Same
   cause, one release earlier — they entered the v1.3 manifest at the
   unversioned path and were never written anywhere else. The probe's runs and
   verdicts survive, so its scores are reconstructible in substance but not
   byte-identically: `Evaluation.timestamp_utc` means a regenerated file cannot
   match a recorded hash. **This battery is on no board**, so no published
   number depends on it.

v1.3 and v1.4 carry case 2 as well and do not verify either. They stay that way:
a published manifest is not edited to make a check pass, which is what
`SUITE-FROZEN.yaml` says in its own header and why the digest exists.

**The repair is `v1.6`, cut 2026-09-12 from a correct scan**, and `v1.7` the
same day when the writer defect below turned up. 1,764 artefacts,
strict-identical. They carry the same scenarios, the same evidence and the same
Overall v3.4 board; the 952 evaluations they pin are the 982 v1.5 claimed minus
the 30 that were never there. Nothing was regenerated and no score moved.

**Four things now stop it recurring.**

- `evaluate --suite-version` writes a new battery straight into its suite
  subtree. The unversioned tree was the v1.0 default, and everything since has
  been re-stamped into place by `migrate` afterwards — which is what left a
  window where a release could be cut against paths the re-stamp abandons.
- `write_review` reads the suite version off the evaluation instead of taking it
  as an argument, so a review cannot land in a different tree from the
  evaluation it explains.
- `tests/test_latest_release_verifies.py` asserts the newest release still
  verifies, that it pins nothing absent, that it covers every evaluation on
  disk, and that no evaluation is filed under a version it does not claim. v1.3,
  v1.4 and v1.5 are named there as known-broken with their reason, and the test
  fails if one of them ever starts verifying — a stale exception teaches a
  reader that a check is expected to fail when it no longer is.
- `tests/test_harness_writes_lf.py` reads every `write_text` call in the package
  and fails on any that does not pin `newline="\n"`. `write_suite_manifest` was
  the only one left, which is why v1.5's two release files were CRLF in a
  working copy git stores as LF — and why `test_line_endings.py` could not catch
  it until those files were committed. A writer is checked where it is written,
  not where its output eventually lands.

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

**Defect 3 recurred and was repaired again on 2026-09-12.** 34 tracked files,
all written by the DeepSeek probe scripts under `experiments/`, carried CRLF in
the working tree while git stored LF. Nothing under a manifest group was
affected and the repair produced no diff — the index was already correct. The
test catches it because it reads bytes from disk, which is the only thing that
sees it.

## Known, documented, not repaired

- **15 `deepseek-v4.1-flash-probe` evaluations are gone and cannot come back.**
  Their runs and verdicts survive, so the scores are reconstructible in
  substance, but `Evaluation.timestamp_utc` means a regenerated file can never
  match the hash v1.3 recorded. That battery is on no board. v1.3, v1.4 and v1.5
  therefore stay non-verifying, permanently.
- **`evaluator-opus5-v0.1` declares no `scenario_id`**, so scenario-to-evaluator
  resolution for monday-001 falls through to a hardcoded fallback. Read the
  evaluator from the published leaderboard instead, as
  `challenge.official_evaluator` does. Recommended for v1.1 with a re-freeze and
  not done there; still open at v1.5, and the evaluator group is `immutable`, so
  it needs a new evaluator id rather than an edit.
- **`run --runs N` ignores archived run numbers.** `--reuse-valid-runs` handles
  it correctly.
- **Penalties are excluded from capability profiles.** A scenario penalty is a
  global deduction; attributing it to a capability would mean inventing the
  attribution. qwen3.6's −7 monday-005 breach shows in its Monday Score and not
  in its `information_boundaries` profile.
- **Capability profiles cover the v3.5 board, not the two v1.13 rows.**
  `analysis/capability-profiles-suite-v1.10-taxonomy-v0.2.json` profiles the
  thirteen v3.5 models; the three v1.10 rows reproduce the profiles in
  `audits/capabilities/` exactly, and the ten incumbents are identical to v1.5.
  DeepSeek V4.1 Flash (1017) and MiMo v2.6 Flash have criterion labels on disk
  but no profile yet - an additive step, not a score.

## Benchmarking a new model

A Monday Score is the mean of a model's own runs, so a challenger needs 15
generations and 354 criterion verdicts and moves no incumbent number. Because
`runs`, `verdicts`, `evaluations` and `leaderboards` are all `append_only`,
publishing one is a suite release: the new evidence has to be a member of a
version before a board can show it.

```
mondaybench challenge --model <slug>            # what exists, what qualifies, what is left
mondaybench evaluate --scenario <id> --model <slug> --suite-version 1.13
mondaybench verify-release --version 1.12       # frozen content intact, evidence may only grow
```

Pass `--suite-version` to `evaluate` from the first run of the battery. It is
the difference between evidence that is already where its release will look for
it and evidence that has to be moved afterwards.

Full runbook in `docs/benchmarking-a-new-model.md`. New models publish as
Overall **v3.6, v3.7, …** against a new suite version. Every earlier board stays
byte-frozen. A new suite needs the previous suite's evaluations re-stamped into
its subtree first (`mondaybench.migrate.migrate_scenario` with
`source_suite_version` set to the previous one; v1.10 re-stamped from v1.5),
because a scenario board reads only its own suite's evaluations.

## Things not to redo

- **Do not touch scenario content, any rubric, or any evaluator.** All are
  frozen; `verify-release` marks those groups `immutable`.
- **Do not regenerate or rejudge an incumbent.** Judge state is not reproducible
  across sessions, and a mixed-vintage board is not one measurement.
- **Do not edit a released manifest to make verification pass.** Cut a new
  version. `SUITE-FROZEN.yaml` says this in its own header, and the v1.5 defect
  above is the case it was written for.
- **Pass `--suite-version` when judging a new battery.** Without it the
  evaluations land at the v1.0 unversioned path, and a release cut before the
  re-stamp records a path that will not exist afterwards. This is what broke
  v1.3 through v1.5.
- **Do not cut a release between judging and re-stamping.** If a battery is
  still being moved, the manifest will pin where it used to be. Cut after
  `migrate`, never between.
- **Do not rewrite a published board.** They are cited and hashed. Publish a
  revision instead.
- **Do not delete anything under `archive/`.** It holds every superseded
  battery — the earlier prompt hashes, the gateway cache hits, the
  16,000-token budget, and the calibration drafts of #002 through #005 — all
  evidence behind documented defects.
- **Do not remove `extra_body: {caching: false}`** from any model. Without it,
  back-to-back identical prompts return a byte-identical cached response in ~1s
  and run 3 becomes a copy of run 2. Since 2026-10-19 NaN ignores the flag;
  NaN batteries need `generation.seed_per_run: true` as well.
- **`mondaybench results` writes files** and prints no summary. Run it only at
  publication time, or it overwrites the per-model cards.
- **Do not write files with CRLF.** `tests/test_line_endings.py` will fail, and
  it is right to. It has now caught this twice.
- **Do not re-run a battery to explain a bad result before checking the
  gateway.** Identical requests have returned 0/6 and 24/26 on the same day.

## The judge

Ten of the fifteen board rows are labelled by one judge: Claude Opus 5
reading each response in a recorded session. DeepSeek V4.1 Flash and Claude
Opus 5 are labelled by GPT-5.6 Sol, and Gemini 3.8 Flash (High), DeepSeek V4.1
Flash (1017) and MiMo v2.6 Flash by Claude Opus 5.5. Two cross-checks have criterion-level labels on disk:

| Battery | Opus judge | Second blind judge | Agreement | Largest run gap |
|---|---:|---:|---|---:|
| Claude Opus 5 (board row, scored 97.07) | 97.10 | 97.07 (GPT-5.6 Sol) | 343 / 354, κ 0.74 | 1.5 |
| DeepSeek V4.1 Flash (board row) | 93.03 | 94.53 (GPT-5.6 Sol) | 317 / 354 | 10.0 |

Two more pairs are stated without their second label set:
`overall-v3.3.md` gives 90.33 / 93.47 on the reliability-prompt battery, and the
guardrail figures above. Quote them as stated, not as checked.

**What this supports.** No evidence of self-judge inflation on the Opus battery.
On a board row the choice of judge moved the Monday Score by 1.50 and one run by
10.0, so positions 3–7 (1.34 points apart) are not ordered by this suite, and a
gap of that size between rows labelled by different judges is not established
either.

## What the suite does not measure

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

The v0.1 open item about **noise resistance not discriminating** was confirmed
at v1.0 suite scale — `ownership_and_delegation` had never separated two models
across three scenarios and 105 runs, and `action_safety` was 87%
constant-pass — and three more models have not changed it. #006 should not
spend points there.

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
