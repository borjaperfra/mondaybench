# MondayBench v1.1 — migration plan

**Status: PLAN ONLY. Nothing here has been executed.** No re-judge was run, no
model was called, no evaluation, run, verdict, leaderboard or release artifact
was written or changed.

---

## 1. Root cause, precisely

`mondaybench/judge.py::judge_prompt_fingerprint()` hashes seven things:

    JUDGE_SYSTEM_PROMPT
    criterion_prompt(<dummy criterion>, {}, "_")
    noise_prompt([], "_")
    penalty_prompt({}, "_", "_")
    CRITERION_SCHEMA
    NOISE_SCHEMA
    PENALTY_SCHEMA          <-- embeds list(PENALTY_TYPE_VALUES)

`PENALTY_TYPE_VALUES` is the shared penalty vocabulary in `schemas.py`. It grew
as scenarios were added — `MAJOR_DATA_ERROR` and `UNSUPPORTED_CAUSALITY` with
monday-004, `CONFIDENTIALITY_BREACH` with monday-005 — so the fingerprint moved
four times over the life of the suite:

| Fingerprint | Carried by |
|---|---|
| `2725f54f7f1dd9f6` | the 7 incumbents on monday-001 |
| `b10748f5636ba6a6` | the 7 incumbents on monday-002 and monday-003 |
| `26067608db5f7a2d` | the 7 incumbents on monday-004 |
| `45998b3c03939498` | the 7 incumbents on monday-005 — and anything judged today |

Every model judged today is stamped `45998b3c03939498` on all five scenarios, so
it can only ever join monday-005's board. **This is a property of the harness,
not of any model.**

### Two further defects the audit turned up

The fingerprint is wrong in the other direction as well, and the second finding
is arguably worse than the one that blocked GLM 5.3.

**(a) It hashes prompts that no published evaluation ever used.** Every one of
the 121 official evaluations across all five scenarios records `route=recorded`.
`RecordedJudge` serves labels from a file and never constructs a provider or a
prompt. The templates the fingerprint hashes belong to the API route, which has
produced nothing.

**(b) It does not hash the judge instructions that were actually in force.**
`evaluator-opus5-v0.2` through `v0.5` each declare

    judge:
      prompt_file: judge-prompt.md
      penalty_prompt_file: penalty-judge-prompt.md

resolved under `evaluators/<scenario>/`. Those eight files are the real,
scenario-specific judging instructions — and `judge_prompt_fingerprint()` never
reads them. Worse, `Judge` never reads them either: nothing in `judge.py`
touches `evaluator.prompt_file`. They are declared, shipped in the release
manifest as immutable content, referenced by `validate` and `publish`, used by
the recorded judge as the human-facing instructions, and invisible to the code.

Editing `evaluators/monday-003/judge-prompt.md` today would change the judge's
instructions and leave the fingerprint identical. Only the `immutable` policy on
the `evaluators` group stops that from mattering in practice.

**(c) The output schema and the prose disagree.** `PENALTY_SCHEMA`'s enum lists
all seven types for every scenario, while
`evaluators/monday-004/penalty-judge-prompt.md` opens by enumerating exactly
four: `MATERIAL_HALLUCINATION|PROHIBITED_ACTION|MAJOR_DATA_ERROR|UNSUPPORTED_CAUSALITY`.
On the API route the schema is sent as `response_format.json_schema`, so it is
model-visible: monday-001's judge would be told it may return
`CONFIDENTIALITY_BREACH`, a type monday-001's rubric does not define.

---

## 2. The proposed contract

Hash a **scenario-specific rendered judge contract**, not global repository
state. Full specification in `proposed-judge-contract.json`; one rendered
instance per scenario in `contract-monday-00X.json`.

    judge_contract_fingerprint(scenario, evaluator)
      = sha256(canonical_json(contract))[:16]

where `canonical_json` is `sort_keys=True, separators=(',',':'),
ensure_ascii=True`.

The contract carries, and only carries, what is applicable to that scenario:

* scenario id, scenario prompt sha256, evaluator id, rubric version and file;
* the ground truth hash and whether a `ground_truth_map` slices it;
* the judge instruction hashes — **including the external `judge-prompt.md` and
  `penalty-judge-prompt.md` when the evaluator declares them**;
* label semantics and the between-two-labels tie rule;
* every criterion in **rubric declaration order**, with its dimension, its three
  point values, its three definitions and its sorted ground-truth paths;
* the noise dimension and its false actions, or `null`;
* **only the penalties this scenario's rubric declares**, sorted by type;
* the output contract, with the penalty enum scoped to those same types.

### Why this is a replacement, not a removal

The brief asked for the fix to be more than "drop `PENALTY_SCHEMA` from the
hash". It is. Dropping it would leave the fingerprint blind to the penalty
contract entirely — a change in monday-001's `-5` hallucination deduction would
not move the hash. The contract instead carries `rubric.penalties`, which the
loader already builds per scenario as `dict[str, PenaltyDefinition]`. Penalty
semantics stay hashed; the global union stops leaking in.

Rendered scenario penalty sets, from the real rubrics:

| Scenario | Penalties in the contract | Excluded by scoping |
|---|---|---|
| monday-001 | MAJOR_CONTRADICTION, MATERIAL_HALLUCINATION, PROHIBITED_ACTION | 4 |
| monday-002 | + MAJOR_PLANNING_ERROR | 3 |
| monday-003 | + MAJOR_PLANNING_ERROR | 3 |
| monday-004 | MAJOR_DATA_ERROR, MATERIAL_HALLUCINATION, PROHIBITED_ACTION, UNSUPPORTED_CAUSALITY | 3 |
| monday-005 | CONFIDENTIALITY_BREACH, PROHIBITED_ACTION | 5 |

### Output schema: scenario-specific (option A)

The brief asked both options to be weighed.

* **A — scenario-specific output schema.** The penalty enum carries the
  scenario's types only. Implementation is one dict copy with one key replaced;
  the schema is already built per call. It makes the enum agree with the prose
  instructions that already exist, and monday-001's judge stops being told about
  monday-005's vocabulary.
* **B — keep the global schema and accept that the model-visible contract
  changes with the repository.** Honest, but it means the judge prompt for a
  frozen scenario is not itself frozen, which is the property the whole release
  mechanism exists to provide.

**Recommendation: A.** It is cheap, it removes a real prose/schema
contradiction, and it is what makes TEST A and TEST K achievable at all.

### Three versions, three jobs

Today `rubric_version` and the fingerprint are welded together in one
comparability key: the leaderboard builds `f"rubric={v}/judge={fp}"`. That mixes
a human version number with a derived hash. Proposed separation:

| Concept | Owned by | Meaning | Changes when |
|---|---|---|---|
| `rubric_version` | the scenario | the human, logical version of the rubric | a person decides the rubric is a new revision |
| `evaluator_version` | the evaluator | the evaluation protocol: which prompts, which slicing, which judge model | the protocol changes |
| `judge_contract_fingerprint` | derived | the exact rendered semantics | any operative byte changes |

**An evaluator bump should not by itself invalidate comparability.** If a
protocol edit leaves the rendered contract identical, the fingerprint is
identical and the scores stay comparable — which is the correct answer and the
opposite of what happens today. The gate should therefore key on the fingerprint
alone; `rubric_version` is already inside the contract, so nothing is lost, and
the two versions become reported context rather than part of the key.

---

## 3. Historical dry run

`historical-dry-run.json`. No file was modified to produce it.

| Scenario | Current unique fingerprints | v1.1 unique contracts | Models | Evaluations | True semantic difference? |
|---|---:|---:|---:|---:|---|
| monday-001 | 2 | 1 | 8 | 24 | no |
| monday-002 | 2 | 1 | 8 | 25 | no |
| monday-003 | 2 | 1 | 8 | 24 | no |
| monday-004 | 2 | 1 | 8 | 24 | no |
| monday-005 | 1 | 1 | 8 | 24 | no |

121 evaluations examined. Every evaluation in a scenario was judged against a
single rubric version under a single evaluator, so **no scenario carries a
genuine semantic split**. The four two-fingerprint scenarios are recording
global repository drift and nothing else.

(monday-002 shows 25 because `qwen3.8-flash` has a fourth evaluation there — the
run that was judged and then rejected at qualification for delivering no
reasoning. It is evidence and stays; it is not a fourth official run.)

---

## 4. GLM 5.3

`glm5.3-compatibility.json`.

| Scenario | Compatible today | Compatible under v1.1 | Reason |
|---|---|---|---|
| monday-001 | NO | **COMPATIBLE** | same rubric 0.2, same evaluator, same criteria, same scenario penalties, same tie rule |
| monday-002 | NO | **COMPATIBLE** | same rubric 0.2 under evaluator-opus5-v0.2 |
| monday-003 | NO | **COMPATIBLE** | same rubric 0.3 under evaluator-opus5-v0.3 |
| monday-004 | NO | **COMPATIBLE** | same rubric 0.3 under evaluator-opus5-v0.4 |
| monday-005 | YES | **COMPATIBLE** | already shares today's fingerprint |

No `INCOMPATIBLE`, no `UNKNOWN`.

### Naming during the transition

`EXCLUDED` reads as a verdict on the model. It is not one. Proposed internal
classification, to be carried in the audit and the migration record rather than
by changing any existing schema in this round:

    generation_eligibility     OFFICIAL_GENERATION
    evaluation_comparability   PENDING_V1_1_CONTRACT
    publication_eligibility    PENDING

* **Generation eligibility: valid.** Official provider route, frozen prompts,
  15/15 qualifying runs, reasoning DELIVERED on all 15, no truncation, 15
  distinct response hashes, prompt equivalence verified against the frozen
  bytes.
* **Evaluation comparability: pending.** Blocked by a harness-side stamp.
* **Publication eligibility: pending**, and downstream of the above.

### The 93.73

**93.73 is a valid current-evaluator measured score for GLM 5.3, pending a
uniform v1.1 re-stamp.** It is not invalid, not wrong and not discarded. Every
run of it was recomputed from the atomic criterion verdicts and matches the
stored evaluation. What it is not *yet* is officially comparable inside v1.0,
because the gate compares a fingerprint that describes repository state rather
than scenario semantics.

Under the recommended strategy the number does not move: the same recorded
labels are replayed, so the same score falls out.

---

## 5. Re-judge inventory

`rejudge-inventory.json`.

| Model | Scenarios | Run files on disk | Judged runs | Raw output available | Needs regeneration | Needs re-judge |
|---|---:|---:|---:|---|---|---|
| glm5.3-flash | 5 | 16 | 15 | yes | **no** | strategy-dependent |
| glm5.2 | 5 | 16 | 15 | yes | **no** | strategy-dependent |
| mimo-v2.5 | 5 | 17 | 15 | yes | **no** | strategy-dependent |
| deepseek-v4-flash | 5 | 17 | 15 | yes | **no** | strategy-dependent |
| qwen3.8-flash | 5 | 22 | 16 | yes | **no** | strategy-dependent |
| qwen3.6 | 5 | 16 | 15 | yes | **no** | strategy-dependent |
| gemma4 | 5 | 16 | 15 | yes | **no** | strategy-dependent |
| glm5.3 | 5 | 15 | 15 | yes | **no** | strategy-dependent |

**Total official judged responses: 121. Available: 121. Regeneration required:
0. Blockers: none.**

The gap between "on disk" and "judged" is rejected attempts — runs that never
earned an evaluation. They stay as evidence and must not acquire one now.

**Opus 5 and Fable 5.1 are out of scope.** Their generations did not come
through the official provider route; both are reachable only from the Claude
Code subscription, whose system prompt and injected context are not the frozen
ones (`audits/monday-002/fable-5.1-preflight.md`). Re-judging them under v1.1
would make their *evaluation* comparable while their *generation* still is not.
If comparability experiments are wanted later, judge them under the same v1.1
contract and publish them in a separate experimental namespace, never inside the
official board.

---

## 6. Cost

`estimated-rejudge-cost.json`.

| Option | Judge calls | Criterion verdicts | Cost |
|---|---:|---:|---:|
| Re-score only (replay recorded verdicts) | 0 | 0 | $0 |
| Full re-judge, recorded route | n/a | 2,852 (2,997 verdict records) | supervised session time |
| Full re-judge, API route | 2,997 | 2,852 | ~$53–106 — **and forbidden** |

The API line is a sizing exercise only. This project has no Anthropic API key
and no credits, and spending them is a hard rule violation rather than a cost
trade-off. There is also **no historical judge token data to calibrate against**:
`JudgeRecord` stores no token counts and every published evaluation used
`route=recorded`. The figures come from measured prompt material (source
material, ground truth and criterion definitions per scenario, mean response
length per scenario) and a stated 4 chars/token assumption.

For scale on the recorded route: the entire GLM 5.3 campaign produced 354
criterion verdicts for one model. A full re-judge is that work times eight.

---

## 7. Strategy comparison

### A — remove the global schemas from the fingerprint, keep current evaluations

| | |
|---|---|
| Methodological cleanliness | poor |
| Historical reproducibility | intact |
| Implementation complexity | low |
| Cost | zero |
| Risk | **it does not work** |
| Future-proofing | none |

**A does not unblock anything.** The leaderboard reads a *stored* fingerprint;
changing the function does not change values already on disk, so monday-001
still shows `2725f54f` beside `45998b3c`. The only way A works is to stop
storing the fingerprint and derive it at read time from
(scenario, rubric, evaluator) — at which point every evaluation under one pair
trivially agrees and the gate can never fail. That destroys the exact capability
it was built for: catching a calibration sweep interrupted midway through a
prompt change. Rejected.

### B — scenario-specific contracts, migrate historical evaluations without re-judging

| | |
|---|---|
| Methodological cleanliness | good — the stamp finally describes what it claims to |
| Historical reproducibility | **fully intact**: v1.0 files are never touched |
| Implementation complexity | moderate |
| Cost | zero judge calls |
| Risk | low |
| Future-proofing | high — an eighth, ninth, tenth model can join |

"Migrate" here means **create-new, never mutate-old**: write fresh evaluation
files under a new evaluator id by replaying the existing recorded verdict files.
The labels do not change, so no score moves; what changes is that each new
evaluation carries a contract fingerprint that is correct.

Honest limitation: it re-stamps rather than re-derives. It fixes the fingerprint
defect and nothing else. Cross-session judging drift — which the fingerprint
never captured and still would not — stays exactly as it is in v1.0.

### C — scenario-specific contracts plus a uniform re-judge of every official output

| | |
|---|---|
| Methodological cleanliness | highest in principle |
| Historical reproducibility | intact if v1.0 is preserved, but v1.1 numbers differ from v1.0's |
| Implementation complexity | same as B, plus the judging campaign |
| Cost | 2,852 criterion verdicts of supervised session work |
| Risk | **high** |
| Future-proofing | same as B |

C is the only option that addresses something B does not: it would put every
model's labels under one judging pass. That is a real gain, because session
identity has never been recorded and no strategy can establish it
retroactively.

But three things weigh against it here:

1. **It changes what was not asked to change.** Every published incumbent number
   would be re-derived. A release whose numbers differ from v1.0's invites
   "which is right?", and the answer — "both, under different judging passes" —
   weakens both. B produces a v1.1 whose numbers are identical to v1.0's by
   construction, differing only in that the stamp is correct and an eighth model
   can join. That is a much cleaner claim.
2. **The cure has the disease.** `evaluator-opus5-v0.1` itself warns that
   "labelling 21 runs in sequence risks becoming stricter or looser part-way
   through". A uniform re-judge is 121 runs in sequence. It would trade several
   per-scenario judging windows for one very long one.
3. **Nothing suggests any label is wrong.** The audit found a defective metadata
   stamp. Re-deriving 2,852 judgments to fix a stamp is disproportionate.

**Recommended: B**, with C deferred rather than discarded — see below.

---

## 8. Cutting v1.1

### What it is

Same five frozen scenarios, same frozen prompts, same source files, same
rubrics, same candidate generations. **New evaluator protocol, new contract
fingerprint, new evaluation artifacts.** v1.0 stays exactly as published.

### What needs to exist

| Item | Needed? | Detail |
|---|---|---|
| New release manifest | **yes** | `releases/v1.1/SUITE-FROZEN.yaml` + `v1.1.files.json`. `verify-release --version` already takes a version, so both verify side by side with no code change. |
| New evaluator ids | **yes** | `evaluator-opus5-v1.1-00X`, one per scenario, each declaring the same rubric file and the same external prompts as its v0.x predecessor. New ids mean new directories, so `evaluations/` grows and nothing existing is touched. |
| New leaderboard namespace | **yes, and this is the one real gap** | `write_leaderboard` writes to `leaderboard/<scenario>/`, a single unversioned namespace. v1.1 must write to `leaderboard/v1.1/<scenario>/` so v1.0's boards stay byte-identical under the `append_only` policy. |
| New evaluation directories | automatic | keyed by evaluator id. |
| New verdict files | **no, under strategy B** | the existing recorded verdicts are replayed as-is. Under C, yes — a full new set. |
| New capabilities output | **yes** | `analysis/capability-profiles-v1.1-*.json`. Never reuse v1.0's. |
| New score summaries | **yes** | derived from the v1.1 evaluations. |
| New Overall release | **yes, a VERSION not a revision** | `load_releases` permits a revision only when the scenario set and aggregation match; both do here. But a revision "adds MODELS to a fixed scenario set", and v1.1 changes the *evaluator*, which appears in `scenario_provenance`. That makes it `overall-v3`, not `overall-v2.2`. |

### Ordered steps — none executed

1. Implement `judge_contract()` and `judge_contract_fingerprint()` in a new
   module (`mondaybench/contract.py`), leaving `judge_prompt_fingerprint()`
   untouched so v1.0 stays readable.
2. Add `contract_fingerprint` to `JudgeRecord` as an optional field. Optional
   matters: every v1.0 evaluation must keep loading unchanged.
3. Make the judge use `evaluator.prompt_file` / `penalty_prompt_file` when
   declared — closing defect (b) — and scope the penalty enum per scenario,
   closing defect (c).
4. Change the leaderboard's comparability key from
   `rubric={v}/judge={prompt_fingerprint}` to the contract fingerprint, falling
   back to the legacy field when an evaluation predates it.
5. Add `--suite-version` to `leaderboard`, writing versioned boards under
   `leaderboard/v<version>/`.
6. Land the blocking tests (`test-plan.md`) **before** any migration runs.
7. Create the v1.1 evaluator configs.
8. Re-score: replay every existing recorded verdict file under the v1.1
   evaluator ids, producing 121 new evaluations. Zero model calls.
9. Publish the five v1.1 scenario boards and `overall-v3`.
10. Rebuild capabilities from the v1.1 verdicts.
11. Cut `releases/v1.1/`.
12. Verify both releases side by side.

### When C becomes the right answer

Defer C to the next release that changes a rubric. A rubric revision forces a
re-judge anyway; that is the moment to make the labels uniform, and it costs
nothing extra because the work is already required. Doing it now would mean
paying the full price to fix a metadata field.

Independently of the strategy chosen: **add a `judge_session_id` to
`JudgeRecord`**. Session identity is the thing that actually matters for a
recorded judge, it has never been recorded, and no fingerprint design can
recover it retroactively. Recording it from v1.1 onward is cheap and makes a
future C-style decision evidence-based instead of speculative.

---

## 9. Website — design only, nothing implemented

`helmcode-site` was not touched.

`scripts/sync-mondaybench.mjs` reads harness artefacts from `../monday-bench`
and generates `src/data/mondaybench/*.data.ts`; editorial copy lives in sibling
files without `.data`, so regenerating cannot overwrite a translation.

**Recommendation: yes, v1.1 becomes canonical latest and v1.0 is archived.** A
board whose comparability stamp is known to be wrong should not be the one on
the front page.

Minimum data migration:

1. Teach the sync script which suite version to read, defaulting to latest
   released, and have it emit `*.data.ts` from the versioned leaderboard path.
2. Keep the v1.0 payloads as generated data under an archive key rather than
   deleting them.
3. Serve `/mondaybench` from v1.1 and add `/mondaybench/v1.0` as the archived
   board, with a line on each pointing at the other.
4. Since B moves no number, the visible change is one added model and a
   provenance line — not a re-ranking. Worth saying so on the page.
5. `node scripts/sync-mondaybench.mjs --check` stays the guard against stale
   numbers.

---

## 10. Explainability tool — interface design

Opaque hashes are what made this take an audit to diagnose. Proposed, not built:

    mondaybench explain-judge-contract --scenario monday-001 [--evaluator ID]

        scenario            monday-001
        evaluator           evaluator-opus5-v0.1
        rubric              rubric-0.2.yaml  version 0.2
        contract            3cca9e91b6b2d2e2
        legacy fingerprint  2725f54f7f1dd9f6  (judge_prompt_fingerprint, v1.0)

        components
          scenario_prompt_sha256    ed4d7beb...
          ground_truth_sha256       9f2c...
          judge_instructions        builtin (this evaluator declares no prompt_file)
          label_semantics           PASS/PARTIAL/FAIL, tie_rule=lower
          criteria                  19, in rubric order
          noise                     6 false actions
          penalties                 3  MAJOR_CONTRADICTION, MATERIAL_HALLUCINATION,
                                       PROHIBITED_ACTION
          output_contract           penalty enum scoped to those 3

    mondaybench explain-judge-contract --compare monday-001 monday-002

        differs in 6 of 14 components:
          rubric_file           rubric-0.2.yaml -> rubric.yaml
          criteria              19 -> 20  (0 shared ids)
          penalties             +MAJOR_PLANNING_ERROR
          noise                 present -> absent
          judge_instructions    builtin -> evaluators/monday-002/judge-prompt.md
          ground_truth_sha256   differs

    mondaybench explain-judge-contract --evaluation evaluations/.../run-001.json

        resolves the contract that evaluation was produced under and diffs it
        against the current one, naming the first component that moved.

The `--compare` form is the one that matters: it turns "these two hashes differ"
into "they differ because the penalty vocabulary is bigger", which is the
sentence this audit had to reconstruct by hand.
