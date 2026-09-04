# MondayBench v1.1 migration — audit and plan

**Date:** 2026-09-03
**Status:** PLANNING ONLY. No re-judge executed, no model called, no leaderboard
or website change, v1.0 untouched.

This directory answers one question: how should MondayBench stop conflating
"the repository changed" with "the judging semantics changed", so that a frozen
suite can accept an eighth model?

---

## The finding in one paragraph

`judge_prompt_fingerprint()` hashes the built-in judge prompt templates and the
global verdict schemas. `PENALTY_SCHEMA` embeds `PENALTY_TYPE_VALUES`, the
shared penalty vocabulary, which grew as scenarios were added. So the
fingerprint moved four times over the life of the suite and every model judged
today is stamped with the newest value on all five scenarios — which is why
GLM 5.3 can only join monday-005's board. The audit also found the fingerprint
is wrong in the opposite direction: it hashes prompts that **no published
evaluation ever used** (all 121 are `route=recorded`), and it does **not** hash
the scenario-specific `judge-prompt.md` and `penalty-judge-prompt.md` files that
four of the five evaluators actually declare — files that `Judge` never loads
either.

---

## Component table

`CURRENTLY HASHED?` · `MODEL-VISIBLE?` · `SCENARIO-SPECIFIC?` ·
`CAN CHANGE SEMANTICS?` · `SHOULD BE HASHED IN V1.1?`

Model-visible is judged on the API route, where the schema is sent as
`response_format.json_schema`. On the recorded route nothing is model-visible in
that sense, which is itself part of the finding.

| Component | Hashed today | Model-visible | Scenario-specific | Can change semantics | Hash in v1.1 |
|---|---|---|---|---|---|
| judge model id | **no** | n/a | no | **yes** | **yes** — via `evaluator_version`; a different judge model is a different evaluator |
| judge system prompt | yes | yes | no | yes | yes |
| built-in criterion prompt template | yes (dummy-rendered) | yes | no | yes | yes, as a hash |
| **external `judge-prompt.md`** | **no** | yes | **yes** | **yes** | **yes — the biggest gap** |
| **external `penalty-judge-prompt.md`** | **no** | yes | **yes** | **yes** | **yes** |
| PASS/PARTIAL/FAIL semantics | partly, inside the template | yes | no | yes | **yes, explicitly** |
| lower-label tie rule | partly, inside the template | yes | no | yes | **yes, explicitly** |
| criterion IDs | **no** | yes | yes | yes | **yes** |
| criterion definitions | **no** | yes | yes | yes | **yes** |
| criterion points / weights | **no** | no | yes | **yes** | **yes** — scoring semantics even when the judge never sees them |
| criterion dimension | **no** | yes | yes | yes | **yes** |
| criterion order | **no** | no (one call each) | yes | yes | **yes** — rubric order is what the recorded judge reads |
| ground-truth map (per criterion) | **no** | yes | yes | **yes** | **yes** — it decides what the judge may see |
| ground-truth content | **no** | yes | yes | **yes** | **yes**, as a hash |
| factual anchors (monday-003) | **no** | yes | yes | **yes** | **yes**, inside the ground-truth hash |
| penalty IDs | yes, **as the GLOBAL union** | yes | yes | yes | **yes, scenario-scoped** |
| penalty definitions | **no** | yes | yes | yes | **yes** |
| penalty deduction values | **no** | no | yes | **yes** | **yes** |
| penalty cap | **no** | no | yes | **yes** | **yes** |
| false-action rules | **no** (rendered with an empty list) | yes | yes | yes | **yes** |
| criterion output schema | yes | yes | no | yes | yes |
| noise output schema | yes | yes | no | yes | yes, when the scenario has a noise dimension |
| **global penalty enum** | **yes — THE ROOT CAUSE** | yes | **no** | no, for this scenario | **no — replaced by the scenario's penalty list** |
| output formatting instructions | yes, inside the template | yes | no | yes | yes |
| rubric version | no (used beside it in the gate key) | no | yes | yes | **yes** |
| evaluator version | no (used as the directory key) | no | yes | yes | **yes** |
| scenario ID | **no** | no | yes | no | **yes** — cheap disambiguation |
| scenario prompt hash | **no** | no | yes | **yes** | **yes** — a different question is a different contract |
| timestamps, paths, comments | no | no | n/a | no | **no** |

Three categories, kept apart as the brief asked:

* **scoring semantics** — rubric, penalties, ground truth, label rules. Mostly
  unhashed today. All of it must be hashed.
* **serialization / transport semantics** — JSON schemas, output formatting.
  Hashed today, correctly, but must be scenario-scoped where the payload is.
* **irrelevant global repository state** — the penalty union, and any future
  scenario's vocabulary. Hashed today. Must not be.

---

## Results

**Historical dry run** (`historical-dry-run.json`) — 121 evaluations, no file
modified:

| Scenario | Current unique fingerprints | v1.1 unique contracts | Models | True semantic difference |
|---|---:|---:|---:|---|
| monday-001 | 2 | 1 | 8 | no |
| monday-002 | 2 | 1 | 8 | no |
| monday-003 | 2 | 1 | 8 | no |
| monday-004 | 2 | 1 | 8 | no |
| monday-005 | 1 | 1 | 8 | no |

**GLM 5.3** (`glm5.3-compatibility.json`) — COMPATIBLE on all five under v1.1;
no INCOMPATIBLE, no UNKNOWN. Generation eligibility valid; 93.73 is a valid
current-evaluator measured score pending a uniform v1.1 re-stamp, and it does
not move under the recommended strategy.

**Test simulation** (`test-simulation.json`) — 12/12 of the mandated properties
hold against the proposed design, verified by mutation rather than asserted.

**Inventory** (`rejudge-inventory.json`) — 121 official judged responses, all
raw outputs available, **regeneration required: 0**, no blockers.

**Recommendation: GO for v1.1, strategy B** — scenario-specific contract
fingerprints with a create-new re-score that replays the existing recorded
verdicts. Zero judge calls, zero score movement, v1.0 preserved byte-for-byte.
Strategy C (uniform re-judge) is deferred to the next release that changes a
rubric, when the work is required anyway. Reasoning in `migration-plan.md` §7.

---

## Files

| File | What it is |
|---|---|
| `README.md` | this: the finding, the component table, the results |
| `migration-plan.md` | root cause, contract design, strategy comparison, the v1.1 cut, website plan, tool design |
| `test-plan.md` | the blocking tests, the simulation results, the tests that must be rewritten |
| `current-fingerprint-audit.json` | exactly what feeds the fingerprint today, and what does not |
| `proposed-judge-contract.json` | the contract specification and its ordering rules |
| `contract-monday-00{1..5}.json` | the rendered contract for each scenario |
| `historical-dry-run.json` | current vs proposed fingerprints over every existing evaluation |
| `glm5.3-compatibility.json` | per-scenario compatibility, and the proposed interim classification |
| `rejudge-inventory.json` | what exists, what would be re-judged, what is out of scope |
| `estimated-rejudge-cost.json` | the three options costed, with the assumptions stated |
| `test-simulation.json` | the 12 simulated tests and their fingerprint transitions |
| `analyse.py` | READ-ONLY: builds the contracts, replays both fingerprints |
| `simulate_tests.py` | READ-ONLY: mutates loaded objects in memory and re-hashes |
| `inventory.py` | READ-ONLY: counts responses and estimates cost |
| `compatibility.py` | READ-ONLY: the GLM 5.3 question |
| `emit_docs.py` | READ-ONLY: derives the remaining JSON artifacts |

Every script reads the repo and writes only into this directory.

---

## Integrity

`git status` outside this directory shows only `models.yaml`, which is the GLM 5.3
registry entry from the previous campaign and predates this audit. No core code
was modified. `verify-release --version 1.0` still verifies and the suite digest
is unchanged.
