# MondayBench v1.0

**Released:** 2026-08-31
**Scope:** monday-001 … monday-005 · 500 rubric points · 118 atomic criteria ·
7 models · 105 official runs
**Manifest:** `SUITE-FROZEN.yaml` · **file index:** `v1.0.files.json`

MondayBench asks one question: **can this model handle your Monday?** Not can it
answer a trivia question or pass a coding test — can it come back after four
days away, read a week of Slack, email, tickets, meeting notes and metrics, work
out what actually happened, and do something useful about it.

v1.0 closes the first five Mondays.

---

## The suite

| Scenario | Rubric | Criteria | What it measures |
|---|---|---:|---|
| monday-001 | `rubric-0.2.yaml` (0.2) | 19 | Reconstructing a week from five noisy sources |
| monday-002 | `rubric.yaml` (0.2) | 20 | Dependencies, supersession, what to stop promising |
| monday-003 | `rubric.yaml` (0.3) | 21 | Prioritisation and resource allocation under a hard limit |
| monday-004 | `rubric-0.3.yaml` (0.3) | 27 | Reconciling contradictory data, and what to tell leadership |
| monday-005 | `rubric-0.4.yaml` (0.4) | 31 | One incident, four audiences, four different right answers |

monday-001's atomic criteria sum to 90; the remaining 10 points are the
noise-resistance dimension, scored at dimension granularity. All five scenarios
contribute exactly 100.

## Overall v2 — the headline result

Monday Score is the arithmetic mean of a model's official score on all five
scenarios. Equal weight per scenario. Nothing else is folded in — not latency,
cost, tokens, run stability or serving reliability. Those are published beside
the score, never inside it.

| # | Model | Monday Score | Worst scenario |
|---:|---|---:|---|
| 1 | Qwen 3.8 Flash | **95.1** | monday-001 — 92.5 |
| 2 | GLM 5.3 Flash | 94.9 | monday-002 — 87.3 |
| 3 | DeepSeek V4 Flash | 91.7 | monday-004 — 86.0 |
| 4 | MIMO v2.5 | 86.7 | monday-004 — 78.5 |
| 5 | GLM 5.2 | 86.5 | monday-004 — 71.2 |
| 6 | Qwen 3.6 | 68.8 | monday-004 — 46.0 |
| 7 | Gemma 4 | 63.0 | monday-004 — 35.2 |

monday-004 is the hardest Monday for five of seven models, and the one that
separates the field: 35.2 to 98.0, a 62.8-point spread.

**The 0.2 between first and second is not a ranking.** The capability taxonomy
shows why: Qwen 3.8 Flash never drops below 71.4% on any capability; GLM 5.3
Flash has a higher ceiling and a 50.0% floor on `factual_accuracy`. Read
`analysis/capability-taxonomy-v0.2.md` before choosing between them.

**Serving caveat, which travels with the result.** qwen3.6's three official
monday-004 runs were served from NaN, not Helmcode, which was unreachable during
generation. NaN serves that model as a *reasoning* model and Helmcode does not,
on a byte-identical request. Same weights, different inference regime. Recorded
as a scenario-scoped override in `models.yaml` and stated in the Overall v1 and
v2 release notes.

## What ships alongside

| Artifact | What it is |
|---|---|
| `leaderboard/overall/overall-v{0,1,2}.*` | Three permanent Overall releases: 3, 4 and 5 scenarios |
| `taxonomy/capabilities-v0.2.yaml` | 22 capabilities, 119 mappings, 500 points |
| `analysis/capability-profiles-v0.2.json` | Per-model capability scores, coverage, discrimination |
| `analysis/capability-taxonomy-v0.2.md` | What each model is good and bad at, and what the suite still cannot measure |
| `docs/benchmarking-a-new-model.md` | How to score a new model without rerunning anything |

---

## Integrity repairs in this release

Two known defects were repaired. Neither moved a published number, and that is
asserted rather than claimed.

### 1. `load_scenario("monday-001")` returned a rubric the scenario is not frozen against

`scenarios/monday-001/scenario.yaml` declares no `rubric_file`, so the loader
fell back to the directory default `rubric.yaml` — **version 0.1, superseded** —
while `FROZEN.yaml` freezes the scenario against `rubric-0.2.yaml` and
`evaluator-opus5-v0.1` scores against `rubric-0.2.yaml`. Every other scenario
declares its rubric and resolved correctly, which is what kept this invisible
across four releases: an analysis looping over five scenarios got four right and
one silently wrong.

**Repaired in the resolver, not in the scenario.** `FROZEN.yaml` already
recorded the right answer, and across all five scenarios every evaluator's
`rubric_file` matches its manifest exactly. So resolution order is now: explicit
argument → `scenario.yaml` → `FROZEN.yaml` → directory default; and a scenario
whose `scenario.yaml` and `FROZEN.yaml` name *different* rubrics is refused
outright, because one of the two is wrong and the loader cannot know which.

**No frozen artifact was edited.** Editing `scenario.yaml` would have meant
mutating a hashed file and re-freezing a published scenario. `check_drift` is
clean for all five and is asserted to be.

The repair surfaced four 0.1-era evaluators (`evaluator-manual-v0.1`,
`evaluator-v0.1`, `evaluator-open-v0.1`, `evaluator-gateway-v0.1`) that reached
rubric 0.1 through the same implicit default. They now declare
`rubric_file: rubric.yaml` explicitly. None had produced a published evaluation.

*24 tests in `tests/test_rubric_resolution.py`, all failing on the pre-repair resolver.*

### 2. `capability-profiles-v0.1.json` was stale against its own taxonomy

It covers **monday-001…003 — 300 points, 14 capabilities**. The taxonomy it
claims to apply maps **88 criteria across monday-001…004 — 400 points, 17
capabilities**. It was generated before monday-004 was official and never
rebuilt, so `business_judgment`, `data_cleaning` and `entity_resolution` were
missing entirely and `quantitative_reasoning` was carrying 21 of its 63 points.

**Repaired additively.** The stale file is byte-identical to what was published —
it is the artifact the v0.1 report was written from, and rewriting it would move
numbers a reader may already have cited. Instead:

- `analysis/capability-profiles-v0.1.1.json` applies the *same, unmodified* v0.1
  taxonomy to all four of its scenarios, in v0.1's schema.
- `analysis/capability-taxonomy-v0.1.md` opens with an erratum naming the one
  finding that did not survive: **Gemma 4 "copies accurately and computes
  badly"** rested on a single 5-point criterion. With monday-004 included its
  `factual_accuracy` is 68.8, not 100. The computation half stands and got
  stronger — `quantitative_reasoning` 27.5% on 66 points.

The root cause — a profile build that silently used whichever scenarios happened
to be official — is now pinned for both published profile sets.

*12 tests in `tests/test_capability_profiles_v011.py`.*

### Also corrected

`analysis/capability-taxonomy-v0.2.md`'s Method table named the wrong rubric
files for monday-002 and monday-003 (both are `rubric.yaml`, at versions 0.2 and
0.3, which the table also had swapped). No computed number was affected — the
code resolved through the evaluator — but the table was wrong and is now
generated from the evaluators.

---

## Known, documented, not repaired

**`evaluator-opus5-v0.1` declares no `scenario_id`.** monday-001 predates the
convention, so `resolve_evaluator("monday-001", …)` finds nothing and the CLI
falls through to a hardcoded fallback constant. It works, but the binding is
implicit. Not repaired here because the evaluator is part of the evidence chain
for 21 published runs and a metadata-only edit still changes its content hash.
Anything needing the authoritative answer should read the evaluator recorded in
the published leaderboard, as `challenge.official_evaluator` does.
**Recommended for v1.1**, together with a re-freeze.

**`run --runs N` ignores archived run numbers.** The plain branch schedules
`1..N` regardless of what is reserved in `archive/`. `--reuse-valid-runs`
handles it correctly. Sharp edge, not a defect in any published result.

**Penalties are excluded from capability profiles.** A scenario penalty is a
global deduction, not a criterion-level one, so attributing it to a capability
would mean inventing an attribution. The consequence is stated rather than
hidden: qwen3.6's −7 monday-005 deduction — a PROHIBITED_ACTION for promising a
recovery time nobody authorised on the public status page — appears in its
Monday Score and in no capability profile at all.

---

## The manifest

`SUITE-FROZEN.yaml` records a `content_digest` per group and one `suite_digest`
over all of them. `v1.0.files.json` holds the per-file hashes behind those
digests. The digest is what a human checks; the index is what says which file
moved.

```bash
uv run mondaybench verify-release --version 1.0            # policy check
uv run mondaybench verify-release --version 1.0 --strict   # byte-identical
```

**Group policy** is the part that makes this usable rather than merely strict:

| Policy | Groups | Meaning |
|---|---|---|
| `immutable` | scenarios, evaluators, taxonomy | Nothing may change, nothing may be added |
| `append_only` | runs, verdicts, evaluations, leaderboards, analysis | Existing files frozen; new files expected |
| `mutable` | config, docs, harness, tests | Tracked so drift is visible; change is not a failure |

Benchmarking a new model necessarily writes new runs, verdicts, evaluations and
a board, and must not alter one byte of the scenarios or of any incumbent's
evidence. A single "did anything change?" check cannot tell those apart — it
would either forbid the legitimate case or wave through the illegitimate one.

**Deliberately not covered:** `archive/` (superseded calibration evidence, kept
for re-examination; nothing in it contributed to a published score) and `.env`,
which is excluded by name — a manifest is published, and a hash confirms a
file's exact contents to anyone who can guess them.

---

## Reproducibility, stated honestly

**The judge is recorded, not called.** There is no Anthropic API key and no
credits on this project; every verdict was produced in-session and replayed with
`evaluate --verdicts`. Scores reproduce exactly from the stored verdicts. What
*cannot* be done from these artifacts is sample judge variance independently —
re-judging would be a new measurement, not a reproduction, and no claim here
should be read as controlling for it.

**Three official runs per model per scenario.** Each criterion is averaged
across runs before summing, which is exact and reconciles with the scenario mean
by construction. Three is few; per-criterion run variance is preserved in the
evaluation records.

**The harness is pinned separately from the data.** A change under `mondaybench/`
does not invalidate a recorded score — verdicts are recorded, not recomputed —
but it does invalidate the claim that this tree reproduces them. Different
claims, kept apart.

---

## What v1.0 does not measure

From `analysis/capability-taxonomy-v0.2.md`, which ranks these:

1. **Temporal reasoning under a moving clock.** The field's worst capability
   (mean 61.0) and the only one whose *shadow* mass exceeds its primary mass:
   22 points of criteria depend on getting time right while scoring something
   else, against 14 that score it directly.
2. **Multi-turn correction.** All five scenarios are one prompt and one
   response. Nothing measures what happens when the requester says "that's not
   what I meant". Structural — no rubric change closes it.
3. **Entity resolution and data cleaning beyond one Monday.** Still #004-only.
4. **A criterion the field actually fails.** Zero of 500 points are
   constant-fail. Nothing in the suite is out of reach, so there is no evidence
   about where the frontier is.

The taxonomy recommends **#006: temporal reasoning under a moving clock,
delivered multi-turn** — gaps 1 and 2 compose rather than compete.

## Next

- **v1.1** — the `evaluator-opus5-v0.1` scenario binding, with a re-freeze.
- **v2.0** — monday-006, and the multi-turn harness work it needs, which must be
  scoped and confirmed as not affecting #001–#005 before any scenario content is
  written.
- **Overall v2.1, v2.2, …** — new models against this frozen suite. See
  `docs/benchmarking-a-new-model.md`.
