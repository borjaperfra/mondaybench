# v1.1 judge contract — test plan

**Written before implementation, and already simulated against the proposed
design.** `simulate_tests.py` builds the contract for real scenarios, mutates
the loaded objects in memory, and re-hashes. Nothing under `scenarios/`,
`evaluators/`, `runs/`, `verdicts/` or `evaluations/` is written, and no model
is called.

**Result: 12/12 simulated tests pass.** Full output in `test-simulation.json`.

Baseline contract fingerprints under the proposed design:

    monday-001  3cca9e91b6b2d2e2
    monday-002  76cc0025a4f49bad
    monday-003  5a6607fea6a000a4
    monday-004  ec04e8ba6b7822a2
    monday-005  eeb5d704995d6c73

---

## The blocking set

Every one of these must be green before any migration step runs. They are
written against the *desired* property, never against current behaviour — the
current behaviour is the defect.

| | Test | Expectation | Simulated | How it was simulated |
|---|---|---|---|---|
| **A** | monday-006 adds a penalty type to the global vocabulary | monday-001 fingerprint **unchanged** | PASS | `PENALTY_TYPE_VALUES` and `PENALTY_SCHEMA`'s enum patched to add `SCHEDULE_FABRICATION`; all five contracts rebuilt |
| **B** | a monday-001 penalty deduction changes by one point | monday-001 fingerprint **changes** | PASS | `dataclasses.replace` on the loaded `PenaltyDefinition`; `3cca9e91…` → `5be2bbf2…` |
| **C** | a monday-001 criterion `pass_definition` is reworded | monday-001 fingerprint **changes** | PASS | `3cca9e91…` → `ac55b0c4…` |
| **D** | a monday-005 criterion is reworded | monday-005 changes, **monday-001 does not** | PASS | `eeb5d704…` → `08655c44…`, 001 stable |
| **E** | top-level keys reversed before serialisation | fingerprint **unchanged** | PASS | `canonical_json` sorts keys |
| **F** | two monday-001 criteria swapped in rubric order | fingerprint **changes** | PASS | criteria are stored in declaration order; `3cca9e91…` → `a56fc05f…` |
| **G** | a comment or unread key added to the rubric file | fingerprint **unchanged** | PASS | the YAML loader drops comments and the builder reads only operative fields |
| **H** | the PASS/PARTIAL/FAIL vocabulary changes | every affected fingerprint **changes** | PASS | `3cca9e91…` → `bb677a7f…` |
| **I** | the between-two-labels tie rule flips to `higher` | fingerprint **changes** | PASS | `3cca9e91…` → `8e0d0b75…` |
| **J** | monday-003's `factual_anchors` are edited | monday-003 changes, **no other scenario does** | PASS | ground truth mutated in memory; `5a6607fe…` → `4841b744…`, others stable |
| **K** | any future enum addition outside a scenario | **no** historical scenario fingerprint changes | PASS | same patch as A, checked across all five |
| **L** | a model judged today vs an incumbent judged before monday-005 | **same** contract fingerprint when the effective semantics are identical | PASS | 121 stored evaluations replayed: 2→1, 2→1, 2→1, 2→1, 1→1 |

### On TEST F

F and E pull in opposite directions and the resolution is deliberate.
**Serialisation order must not matter; rubric order must.** Dictionary keys are
sorted by `canonical_json`, so how the object happens to be built is invisible.
The criteria array, by contrast, keeps rubric declaration order, because that is
the order the recorded judge reads the rubric in and reordering a rubric is a
rubric edit. Penalties are dict-derived and therefore sorted by type — a dict
has no meaningful order to preserve.

### On TEST G

The strong form is that a change with no operative effect must not move the
hash. YAML comments never reach the loaded `Rubric`, and the builder reads named
fields rather than the raw mapping, so an unread top-level key cannot reach the
contract either. Worth an explicit regression test at implementation time
reading two rubric files that differ only in comments.

---

## Additional tests the audit says are needed

These are not in the original list. Each closes something this audit found.

| | Test | Expectation | Why |
|---|---|---|---|
| **M** | edit `evaluators/monday-003/judge-prompt.md` | monday-003 fingerprint **changes** | Today it does not. `judge_prompt_fingerprint()` never reads the external prompts, and `Judge` never loads them either. This is the defect that would let real judging instructions change silently. |
| **N** | edit `evaluators/monday-004/penalty-judge-prompt.md` | monday-004 fingerprint **changes** | same defect, penalty side |
| **O** | the rendered penalty enum equals the scenario's rubric penalties | exact set equality, all five scenarios | Today the enum is the global seven while `monday-004/penalty-judge-prompt.md` names four. Prose and schema must agree. |
| **P** | a v1.0 evaluation with no `contract_fingerprint` still loads | no exception, legacy field readable | The optional-field guarantee that keeps v1.0 readable. |
| **Q** | the leaderboard comparability gate is not vacuous | two evaluations under one evaluator with genuinely different contracts are still refused | The failure mode of strategy A. The gate must keep the capability it was built for. |
| **R** | `verify-release --version 1.0` and `--version 1.1` both pass on the same tree | both green, neither disturbs the other | Backward compatibility, section 18 of the brief. |
| **S** | publishing a v1.1 board writes nothing under `leaderboard/<scenario>/` | v1.0 board files byte-identical afterwards | `write_leaderboard` currently has one unversioned namespace; this is the guard for the fix. |
| **T** | an eighth model joins every scenario board | no `MIXED JUDGE VERSIONS` blocker | The end-to-end assertion. It is the scenario that started this. |

### Tests that must be rewritten, not kept

Six tests currently encode "the suite has exactly seven models" and fail for any
eighth by construction. They should assert the *invariant*, not the count:

* `test_capabilities::test_every_model_gets_a_profile` — assert every model on
  an official board has a profile, not that there are seven.
* `test_sample_provenance::test_D_...` and `::test_E_...` — assert samples are
  mutually distinct and do not overlap the calibration archive, over whatever
  set is official.
* `test_suite_release::test_the_manifest_digests_match_the_working_tree` — this
  is the strict variant and should be scoped to a clean tree or made
  version-aware; the policy-mode check is the one that must stay green while a
  model is being benchmarked.
* `test_cli_endpoints` ×2 — the stub's served-model list is hardcoded to the
  seven incumbents; it should be derived from the models under test.

`tests/test_overall_v2.py` must stay exactly as it is and stay green: it is the
one that asserts no incumbent Monday Score moved, and under strategy B none
should.

---

## Sequencing

1. Land M, N, O, P, Q as unit tests against the new contract module — they can
   all run before any migration.
2. Land A–L as the property suite.
3. Rewrite the six count-based tests.
4. Only then run the re-score.
5. R, S and T are release gates and run last, against the migrated tree.
