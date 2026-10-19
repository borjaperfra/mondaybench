# Benchmarking a new model against the frozen suite

**Applies to:** MondayBench suite v1.14 — monday-001 … monday-005, 500 rubric
points, 15 incumbent models, current board Overall v3.6.

The suite is closed. This is how a sixteenth model gets a Monday Score **without
regenerating or rejudging a single incumbent run.**

**Publishing a model is a suite release.** `runs`, `verdicts`, `evaluations` and
`leaderboards` are `append_only` in the release manifest, and a scenario board is
a ranking — it cannot gain a row without changing. So the new evidence goes into
suite **v1.15**, the board becomes Overall **v3.7**, and every earlier release and
board stays byte-frozen. Below, `<N>` is the next suite version (1.15 today).

---

## Why this is possible at all

A model's Monday Score is the arithmetic mean of its own official scores, one
per scenario, and each scenario score is the mean of that model's own three
runs. **No term in the score depends on any other model.** Ranking is applied
after the fact; it does not feed back into any number.

So a challenger needs exactly:

| | Count |
|---|---:|
| Generations | **15** (5 scenarios × 3 runs) |
| Runs to judge | **15** |
| Criterion verdicts | **354** (19+20+21+27+31 criteria × 3) |
| Incumbent runs touched | **0** |
| Incumbent scores that move | **0** |

That last row is a claim the pipeline enforces rather than a promise: see step 6.

**The cost that is not in the table is judging.** MondayBench's judge is
*recorded* — verdicts are produced in-session and replayed with
`evaluate --verdicts`, never fetched from an API. 354 criterion verdicts is the
real budget item, and it is human-supervised time, not tokens.

---

## Before you start

**1. Register the model.** `models.yaml` is what decides which endpoint and
which model id a slug means; a run generated without an entry cannot be
qualified.

```bash
# Verify the id against the live endpoint FIRST. Provider docs are wrong often
# enough that this repo has a command for it.
uv run mondaybench endpoints --model <slug>
```

Placement rule: Helmcode by default, NaN only when a model is not on Helmcode.
Never copy a model id across endpoints — the same model is spelled differently
per platform.

**2. Confirm the suite verifies before you change anything.** If the tree is
already dirty you will not be able to tell your drift from someone else's.

```bash
uv run mondaybench verify-release --version 1.14 --strict
```

**3. Look at where you stand.** This is safe to run at any point and generates
nothing:

```bash
uv run mondaybench challenge --model <slug>
```

---

## The campaign

### Step 1 — generate, one scenario at a time

```bash
uv run mondaybench run --scenario monday-001 --model <slug> --runs 3
```

Do **not** pass `--all-models`. Do **not** pass `--overwrite`.

> **Check the endpoint's cache first.** Send one prompt twice; if the second
> comes back byte-identical in about a second, the endpoint is caching despite
> `caching: false` (NaN did on 2026-10-19). Set `generation.seed_per_run: true`
> in models.yaml so each run sends `seed: <run_number>`, and say so in the
> release note: a seeded battery is a different serving configuration.

> **Known sharp edge.** The plain `--runs N` branch schedules run numbers `1..N`
> and ignores archived run numbers. If this model has archived runs for the
> scenario, use `--reuse-valid-runs` so the schedule accounts for what is
> already reserved. For a genuinely new model this does not arise.

Repeat for monday-002 … monday-005.

### Step 2 — qualify

```bash
uv run mondaybench plan --scenario monday-001 --model <slug>
```

`qualify_run` rejects a run on any of: prompt-hash mismatch against the frozen
manifest, generation ceiling mismatch, wrong provider, reasoning-delivery
mismatch, or a response byte-identical to an earlier run (a cached duplicate is
not an independent sample). A rejected run is *replaced*, never edited — leave
the rejected file on disk and record why.

You need three qualifying runs per scenario before judging. `challenge` shows
the shortfall per scenario.

### Step 3 — judge

This is the step that cannot be automated in this repo: **there is no Anthropic
API key and no credits, so all judging happens in-session on the subscription.**

For each scenario, the judge produces one verdict per criterion per run against
that scenario's official evaluator — the one recorded in the published
leaderboard, not a fallback:

| Scenario | Evaluator | Rubric | Criteria |
|---|---|---|---:|
| monday-001 | `evaluator-opus5-v0.1` | `rubric-0.2.yaml` (0.2) | 19 |
| monday-002 | `evaluator-opus5-v0.2` | `rubric.yaml` (0.2) | 20 |
| monday-003 | `evaluator-opus5-v0.3` | `rubric.yaml` (0.3) | 21 |
| monday-004 | `evaluator-opus5-v0.4` | `rubric-0.3.yaml` (0.3) | 27 |
| monday-005 | `evaluator-opus5-v0.5` | `rubric-0.4.yaml` (0.4) | 31 |

Write the challenger's labels as a standalone
`verdicts/<scenario>/<slug>.verdicts.jsonl`. For monday-001 … monday-003 a
scenario generator (`verdicts/<scenario>/_generate.py`) can produce that file,
but **do not commit edits to a generator** — it is `append_only` evidence.
Revert the edit and keep only the `.jsonl` it produced.

Then replay, **writing straight into the next suite's subtree**:

```bash
uv run mondaybench evaluate --scenario monday-001 --model <slug> \
    --evaluator evaluator-opus5-v0.1 \
    --verdicts verdicts/monday-001/<slug>.verdicts.jsonl \
    --suite-version <N>
```

Pass `--suite-version` from the first evaluation. Without it the evaluation
lands at the unversioned v1.0 path and has to be re-stamped later — and a
release cut between the two pins a path that stops existing. That is exactly
what left v1.3, v1.4 and v1.5 permanently non-verifying (see `STATUS.md`).

**Judge the challenger under the same rubric version as the incumbents.** If a
rubric is revised, that is a new scenario version and a new Overall version —
not a revision. Never rejudge incumbents to "match" a challenger.

### Step 4 — rebuild each scenario leaderboard

```bash
uv run mondaybench leaderboard --scenario monday-001 --official \
    --evaluator evaluator-opus5-v0.1 \
    --models <the fifteen incumbent slugs>,<slug> --suite-version <N>
```

Pass `--evaluator` explicitly for monday-001: `evaluator-opus5-v0.1` declares no
scenario, so resolution would fall through to a fallback. Pass `--models`
explicitly too: without it the command uses the hardcoded `OFFICIAL_MODELS` in
`cli_official.py`, which is the original seven.

This adds a row. It recomputes every row from the same stored evaluations,
so incumbent scores must come out identical — step 6 checks that they did.

### Step 5 — publish an Overall revision

Overall v3.6 is **byte-frozen forever**. A new model is published as the next
*revision* of the same scenario set, pinned to the new suite:

```
leaderboard/overall/
  overall-v3.6.json   15 models   frozen, still the citable artifact
  overall-v3.7.json   16 models   same 5 scenarios, same arithmetic, suite <N>
```

Get the block to append to `overall-releases.yaml`:

```bash
uv run mondaybench challenge --model <slug> --revision-block
```

It is generated rather than hand-written because the five scenario pins must
match the base release exactly, and retyping prompt hashes is how you end up
with a release nobody can reproduce. `load_releases` refuses a revision whose
scenario set or aggregation differs from the release it extends.

Flip `status: draft` → `released` only after step 6, then:

```bash
uv run mondaybench overall --version 3.6
```

### Step 6 — verify nothing moved

Four checks. Run all four.

```bash
# 1. Frozen content is untouched; evidence grew but was not rewritten.
uv run mondaybench verify-release --version 1.14
#    scenarios / evaluators / taxonomy -> must be "identical"
#    runs / verdicts / evaluations / leaderboards -> "N added" is expected

# 2. No incumbent evidence was reused, moved or duplicated.
uv run python -c "
from mondaybench.leaderboard import check_sample_provenance
for s in ['monday-001','monday-002','monday-003','monday-004','monday-005']:
    assert check_sample_provenance(s, None) == [], s
print('sample provenance clean')"

# 3. Every incumbent's Monday Score is unchanged.
uv run pytest tests/test_overall_v2.py tests/test_deepseek_v41_single_battery.py \
    tests/test_suite_release.py tests/test_latest_release_verifies.py -q

# 4. The full suite.
uv run pytest -q
```

Then, and only then, cut the release — **last**, after every evaluation is where
it will stay:

```bash
uv run mondaybench release --version <N>
uv run mondaybench verify-release --version <N> --strict
```

`tests/test_latest_release_verifies.py` fails if the newest release pins a path
that is not on disk or misses an evaluation that is.

Expect the tests that hardcode the incumbent count to need the new model added
(`test_capabilities`, `test_sample_provenance`, `test_cli_endpoints`). The test
that must stay green untouched are the ones in check 3, which pin incumbent scores.

If check 1 reports a **changed** or **missing** file under `runs`, `verdicts`,
`evaluations` or `leaderboards`, stop. Something overwrote incumbent evidence,
and the challenger's board is not trustworthy until you know what.

### Step 7 — analysis (optional)

The capability taxonomy is analytical metadata and feeds back into no score.
Rebuilding profiles with the new model in is a separate, additive act:
`analysis/capability-profiles-v0.2.json` gains a model; `taxonomy/capabilities-v0.2.yaml`
does not change, because the mapping is per-criterion, not per-model.

---

## What must never happen

| Never | Why |
|---|---|
| Regenerate an incumbent run | It is published evidence. A re-run is a different sample and silently changes a published score. |
| Rejudge an incumbent | Judge state is not reproducible across sessions. A mixed-vintage board is not one measurement. |
| Edit a scenario, rubric, ground truth or evaluator | Those are `immutable` in the release manifest. Changing one invalidates all five batteries, not just the challenger's. |
| Rewrite a published Overall board | It is cited and hashed. Publish the next revision. |
| Cut a release before every evaluation is in its final path | The manifest pins where things were, under `append_only`, and the release never verifies. |
| Edit a released manifest to make verification pass | Cut a new version instead. |
| Promote calibration runs to official | `check_calibration_overlap` and `check_sample_provenance` will refuse, and correctly. |
| Average a model over the scenarios it finished | Rewards not competing. A model ranks only with an official score on all five. |

---

## Estimating a campaign

```bash
uv run mondaybench challenge --model <slug>
```

reports `generations needed`, `runs to judge` and `criterion verdicts` for the
whole campaign — including runs that do not exist yet, which is what a plan
needs. For a model starting from zero against the suite that is **15 / 15 / 354**.

Generation cost varies by model and is reported per run in
`provider_metadata.cost_details` where the gateway supplies it. Cost never
affects the Monday Score and is published beside it.

---

## Serving reliability

Report it beside the score, never inside it. If the model is served
intermittently, or a run needed several attempts, that belongs in
`mondaybench serving` and in the release note — as qwen3.6's NaN caveat is
recorded for every Overall board since v1. A model that scores well but serves badly is a
different fact from a model that scores badly, and the score must not blur them.
