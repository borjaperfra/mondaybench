# MondayBench v1.1 — implementation report

**Date:** 2026-09-03
**Strategy:** B — create-new re-stamp of recorded evaluations under a
scenario-specific judge contract.
**Model calls: 0. Judge calls: 0. Candidate regenerations: 0. Changed
historical labels: 0.**

v1.0 is byte-unchanged. Its suite digest is still
`c056b4b43d3caeb3b50394282b08ed281a5716fb1df68d1666abb950aa0b2a80`.

---

## 1. What was wrong

`judge_prompt_fingerprint()` hashed the built-in judge prompt templates and the
global verdict schemas. `PENALTY_SCHEMA` embeds `PENALTY_TYPE_VALUES`, the
shared penalty vocabulary, which grew as scenarios were added. The fingerprint
therefore moved four times over the life of suite v1.0, and every model judged
after monday-005 carried a stamp the monday-001..004 incumbents did not —
despite byte-identical rubrics.

The audit found two further defects, and the second is the more serious:

* **It hashed prompts nothing used.** All 121 official evaluations record
  `route=recorded`. `RecordedJudge` never constructs a provider or a prompt.
* **It did not hash the instructions that were in force.** Evaluators v0.2–v0.5
  each declare `prompt_file: judge-prompt.md` and
  `penalty_prompt_file: penalty-judge-prompt.md` under `evaluators/<scenario>/`.
  Neither the fingerprint nor `Judge` ever loaded them. Editing one changed the
  judge's instructions and moved no hash.
* **The enum and the prose disagreed.**
  `evaluators/monday-004/penalty-judge-prompt.md` enumerates four penalty types;
  `PENALTY_SCHEMA` offered all seven to every scenario.

---

## 2. What was built

### `mondaybench/contract.py`

`judge_contract(scenario, evaluator)` renders the evaluation semantics for one
(scenario, rubric, evaluator) triple; `judge_contract_fingerprint` is
`sha256(canonical_json(contract))[:16]` with
`sort_keys=True, separators=(',',':'), ensure_ascii=True`.

The contract carries: contract schema version, scenario id, scenario prompt
hash, evaluator id, judge model id, rubric version and file, ground-truth hash
and whether it is sliced per criterion, the judge instruction hashes **including
the external files**, label semantics and the tie rule, the scoring totals and
dimension maxima, every criterion **in rubric declaration order** with its
points, definitions and ground-truth paths, the noise dimension and its false
actions, **only the penalties the scenario's rubric declares**, and an output
contract whose penalty enum is scoped to those.

It carries no timestamp, no local path, no comment, and no criterion or penalty
belonging to another scenario.

Rendered fingerprints:

| Scenario | Contract | Penalties in scope | Excluded by scoping |
|---|---|---|---:|
| monday-001 | `60d8f16cacb11db3` | MAJOR_CONTRADICTION, MATERIAL_HALLUCINATION, PROHIBITED_ACTION | 4 |
| monday-002 | `d06759a2a96216cd` | + MAJOR_PLANNING_ERROR | 3 |
| monday-003 | `db0cb9aa9b9d8272` | + MAJOR_PLANNING_ERROR | 3 |
| monday-004 | `5ef5dc8dc34221ac` | MAJOR_DATA_ERROR, MATERIAL_HALLUCINATION, PROHIBITED_ACTION, UNSUPPORTED_CAUSALITY | 3 |
| monday-005 | `bca2e6b6c8487cb5` | CONFIDENTIALITY_BREACH, PROHIBITED_ACTION | 5 |

**The global enum was replaced, not dropped.** `Rubric.penalties` is already
built per scenario by the loader, so penalty semantics stay hashed — changing
monday-001's −5 hallucination deduction still moves its fingerprint (test B) —
while the global union stops leaking in (tests A and K).

### External judge prompts now load

`config.judge_instruction_path` / `judge_instruction_text` resolve them, and
`Judge` uses them: `criterion_prompt` and `penalty_prompt` gained an
`instructions` parameter that replaces the built-in header. A declared file that
is missing is an error, not a silent fallback.

**With `instructions` unset both render byte-identically**, so
`judge_prompt_fingerprint()` still returns `45998b3c03939498` and every stored
v1.0 fingerprint still describes its own evaluations. That is asserted as a test.

### Provenance fields, all optional

`JudgeRecord` gained `contract_fingerprint`, `contract_schema_version` and
`judge_session_id`; `Evaluation` gained `suite_version` and `migrated_from`.
Every v1.0 record still loads with all of them `None` (test P), and no legacy
field was removed.

`judge_session_id` is **null on every migrated record**. Which session produced
a recorded label was never captured, and a migration is not entitled to guess
it. **Contract equivalence is not session identity** — the contract says the
semantics were the same, not that one judge sat down once. It enters no
arithmetic.

### Versioned namespaces

`evaluations/v1.1/…` and `leaderboard/v1.1/<scenario>/`. v1.0's paths never
move, including monday-001's board at the `leaderboard/` root.
`write_evaluation` refuses to overwrite a versioned evaluation that already
exists, so the create-new guarantee is enforced rather than promised.

### Comparability key

`contract.comparability_key` prefers the contract fingerprint and falls back to
the legacy `rubric=…/judge=…` pair. A v1.0 board rebuilt today reaches exactly
the verdict it reached when published; the gate is not weakened (test Q).

The old remediation text — "re-evaluate every run with `--overwrite`" — was
removed. Following it would rewrite incumbent evidence in an `append_only`
group, which `docs/benchmarking-a-new-model.md` forbids twice.

### CLI

* `mondaybench migrate --to 1.1 [--dry-run]`
* `mondaybench leaderboard --suite-version 1.1`
* `mondaybench capabilities --suite-version 1.1`
* `mondaybench explain-judge-contract --scenario X [--compare Y] [--json]`

`explain-judge-contract --compare monday-001 monday-002` prints, among six
differing components, `penalties: +MAJOR_PLANNING_ERROR` — the sentence this
audit had to reconstruct by hand.

---

## 3. The migration

`mondaybench/migrate.py`. For every evaluation v1.0 holds: re-read the **same**
recorded verdict file, replay the **same** labels through the **same**
deterministic scoring code, write a **new** evaluation carrying the contract
fingerprint, then compare old and new field by field.

| | |
|---|---:|
| Evaluations migrated | **121** |
| Criterion labels changed | **0** |
| False-action judgments changed | **0** |
| Penalty verdicts changed | **0** |
| Awarded points changed | **0** |
| Run scores changed | **0** |
| Judge calls | **0** |
| Candidate regenerations | **0** |

### Fingerprint convergence

| Scenario | Legacy unique | v1.1 unique | Expected | Pass |
|---|---:|---:|---:|---|
| monday-001 | 2 | 1 | 1 | yes |
| monday-002 | 2 | 1 | 1 | yes |
| monday-003 | 2 | 1 | 1 | yes |
| monday-004 | 2 | 1 | 1 | yes |
| monday-005 | 1 | 1 | 1 | yes |

### Score invariance

Every incumbent, every run, every scenario mean, every overall: **delta 0.00**.

| Model | v1.0 | v1.1 | Δ |
|---|---:|---:|---:|
| Qwen 3.8 Flash | 95.07 | 95.07 | 0.00 |
| GLM 5.3 Flash | 94.93 | 94.93 | 0.00 |
| DeepSeek V4 Flash | 91.70 | 91.70 | 0.00 |
| MIMO v2.5 | 86.67 | 86.67 | 0.00 |
| GLM 5.2 | 86.50 | 86.50 | 0.00 |
| Qwen 3.6 | 68.77 | 68.77 | 0.00 |
| Gemma 4 | 63.00 | 63.00 | 0.00 |
| **GLM 5.3** | absent | **93.73** | new |

GLM 5.3's 93.73 was **recomputed from the preserved atomic verdicts**, not
carried across: 97.50 / 87.67 / 94.83 / 91.67 / 97.00, worst Monday 87.67,
scenario spread 9.83.

---

## 4. Publication

Five v1.1 scenario boards, eight models each, no `MIXED JUDGE VERSIONS` warning
on any of them. **Overall v3**, not a revision of v2 — `load_releases` would
have accepted `2.1` (same scenarios, same aggregation), but a revision adds
MODELS to a fixed scenario set, and v3 also reads a different suite's boards, so
`scenario_provenance` differs. A decimal point cannot carry that. v2 stays
byte-frozen.

Capability profiles regenerated from the v1.1 verdicts, both taxonomies. **Every
incumbent percentage is identical to v1.0** — checked, not assumed — and GLM 5.3
was added. Its profile matches the pre-migration audit's validation targets
exactly: `factual_accuracy` 64.6%, `temporal_reasoning` 78.6%, `planning` 80.0%,
`dependency_reasoning` 82.7%, and 100% on state reconstruction, supersession,
ownership, cross-source reconciliation and information boundaries.

Opus 5 and Fable 5.1 are **not** in any official v1.1 board, and a test asserts
it. Their generation route is not the official provider route; evaluation
comparability does not override generation eligibility.

---

## 5. Tests

**A–T: all pass. Full suite: 884 passed, 0 failed.**

Eight count-based assertions were rewritten as invariants rather than bumped
from 7 to 8 — the list is in `contract-tests.json`. The most consequential:
`test_the_manifest_digests_match_the_working_tree` demanded byte-identity for
every non-mutable group, which contradicted the `append_only` policy it claimed
to verify; it now asserts byte-identity for `immutable` groups, and a new test
asserts the append-only invariant separately.

`tests/test_overall_v2.py` is unchanged and green.

Two harness bugs were fixed along the way, both real:

* **CSV files were written with CRLF.** `csv.writer` defaults to `\r\n`, and the
  v1.0 boards read as LF only because `.gitattributes` normalises them on
  checkout — which does nothing for a file not yet committed. Both writers now
  pin an LF terminator. Without this, every v1.1 board would have hashed
  differently in a fresh clone.
* **41 pre-existing artifacts under `analysis/` and `audits/` carried CRLF.**
  Untracked work from earlier sessions; normalised to LF, content otherwise
  byte-identical. They are now inside v1.1's manifest, so leaving them would
  have shipped a release that fails its own integrity test.

---

## 6. Integrity

| | |
|---|---|
| v1.0 suite digest | `c056b4b4…` — **unchanged** |
| v1.1 suite digest | `4e5ec2f368a83b9048f3389ff9d5bcfcb68cd2c01d08e3734d022f3cc60f6052` |
| `verify-release --version 1.0` | passes |
| `verify-release --version 1.1` | passes |
| v1.0 scenarios / evaluators / taxonomy | identical |
| v1.0 runs / verdicts / evaluations / leaderboards / analysis | additions only |
| v1.0 evaluations carrying a contract stamp | none |
| v1.0 boards | still seven models each |

Tracked modifications are confined to the harness, the tests and two registries
(`models.yaml`, `overall-releases.yaml`). No run, verdict, evaluation,
leaderboard, scenario, rubric, ground truth or release artifact of v1.0 was
edited.

---

## 7. Release scope — CORRECTED 2026-09-03

**This section was wrong when first written and is corrected here rather than
quietly edited away.**

It claimed that `audits/blind-rejudge/`, `audits/capabilities/`,
`audits/monday-opus5/`, `audits/pricing/` and the `gemini-3.8` material were
pinned in a way that would break `verify-release --version 1.1` if edited. They
are not. Everything under `audits/` belongs to the **`docs`** group, whose
policy is **`mutable`**: drift is reported and is never a failure. Editing an
experimental Opus audit has never been able to break a release.

The claim was right about exactly one directory. `analysis/cost-value/` — 28
files of pricing research, none of it required to reproduce any score — fell
under `analysis/**/*`, which is `append_only`, so editing a published price
*would* have broken the quality release.

**Fixed on 2026-09-03** by giving pricing its own group:

    GROUPS["pricing"]      = ("analysis/cost-value/**/*",)
    GROUP_POLICY["pricing"] = "mutable"
    GROUP_EXCLUDES["analysis"] = ("analysis/cost-value/",)

Pricing keeps its own integrity anchor — each snapshot is immutable, versioned
by date, and carries its own `.sha256` — so the architecture is *suite release +
independently versioned pricing snapshot*, and the suite digest no longer moves
when a vendor moves a price. The full audit is in `release-scope-audit.json` and
the reasoning in `release-scope-decision.md`.

v1.1's digest changed once for this, from `4e5ec2f3…` to `a4d6eb6e…`, and is now
stable: a new pricing snapshot was added afterwards and every scoring group
still reads `identical`.

---

## 8. Artifacts

| File | What it is |
|---|---|
| `implementation-report.md` | this |
| `score-invariance.json` | per-model, per-run, per-scenario, overall — old against new |
| `fingerprint-migration.json` | legacy vs v1.1 fingerprint counts per scenario |
| `contract-tests.json` | A–T results, the full-suite summary, and every rewritten assertion |
| `release-integrity.json` | both manifests, group states, the v1.0 untouched proof, GLM 5.3's operational data with its units |
| `README.md`, `migration-plan.md`, `test-plan.md` | the pre-implementation audit |
| `current-fingerprint-audit.json`, `proposed-judge-contract.json`, `contract-monday-00X.json`, `historical-dry-run.json`, `glm5.3-compatibility.json`, `rejudge-inventory.json`, `estimated-rejudge-cost.json`, `test-simulation.json` | the audit's evidence |
| `analyse.py`, `simulate_tests.py`, `inventory.py`, `compatibility.py`, `emit_docs.py`, `run_migration.py`, `record_tests.py`, `record_integrity.py` | the scripts that produced all of it |
