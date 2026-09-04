# What suite v1.1 claims — release boundary audit and correction

**Date:** 2026-09-03 · Read-only audit, then one scoped change to the release
boundary. No score, run, verdict, evaluation, rubric, scenario or evaluator was
touched, and v1.0 is byte-unchanged.

---

## 1. The question

Should editing an experimental Opus audit, or refreshing public pricing
analysis, invalidate MondayBench suite v1.1?

**No** — unless that artifact is required to reproduce official scoring. A
release digest is a claim about *what a published score was computed from*. If
it also pins research that no score depends on, the claim stops being falsifiable
in a useful way: it starts failing for reasons that say nothing about the
benchmark.

## 2. What the audit actually found

The migration report had flagged five directories. Four of them were **not a
problem**, and saying so is the first correction:

| Directory | Group | Policy | Breaks v1.1 if edited? |
|---|---|---|---|
| `audits/blind-rejudge/` (15 files) | docs | mutable | **no** |
| `audits/capabilities/` (5) | docs | mutable | **no** |
| `audits/monday-opus5/` (9) | docs | mutable | **no** |
| `audits/pricing/` (7) | docs | mutable | **no** |
| `audits/glm-5.3/` (23), `audits/v1.1-migration/` (23) | docs | mutable | **no** |
| **`analysis/cost-value/` (28)** | **analysis** | **append_only** | **YES** |

`docs` covers `audits/**/*` and is `mutable`: drift is reported and is never a
failure. Everything under `audits/` was always safe. The migration report was
wrong about that and has been corrected in place rather than quietly edited.

**Exactly one directory was the real problem.** `analysis/cost-value/` is
pricing research — provider price pages, snapshots, Pareto workings, publication
data. It fell under `analysis/**/*`, which is `append_only`, so editing a
published price would have broken the *quality* release.

## 3. The principled boundary

Derived from the repo's own semantics rather than from a list handed down.

**FROZEN BENCHMARK CORE — everything an official score cannot be reproduced
without.** Each group already carries its own rationale in `suite.py`:

| Group | Policy | Why it is core |
|---|---|---|
| `scenarios` | immutable | the questions, source fixtures, rubrics, ground truth |
| `evaluators` | immutable | evaluator configs and the external judge prompts — the judge contract |
| `taxonomy` | immutable | the capability mapping, read by a published artifact |
| `runs` | append_only | the candidate generations a score was computed from |
| `verdicts` | append_only | the recorded judge output a score was replayed from |
| `evaluations` | append_only | the scored evaluations |
| `leaderboards` | append_only | what was published |
| `config` | mutable | `models.yaml` and `overall-releases.yaml` decide what a slug and a release mean |
| `analysis` | append_only | calibration records, capability profiles, serving qualification — each tied to a published decision |
| `harness`, `tests` | mutable | the code, and the tests that enforce every claim above |

**DERIVED / ANALYTICAL — tracked so drift stays visible, but not a gate.**

| Group | Policy | Why it is not core |
|---|---|---|
| `docs` (incl. `audits/**`) | mutable | prose about the benchmark; no score reads it |
| **`pricing`** (`analysis/cost-value/**`) | **mutable** | **new** — see below |

The line is not "is it interesting" or "is it finished". It is: **does a
published Monday Score change if this file changes?** For a price the answer is
no, by construction — Monday Score is quality only, and the cost layer reads the
same frozen runs and multiplies their token counts by a published price.

## 4. The change

```python
GROUPS["pricing"]           = ("analysis/cost-value/**/*",)
GROUP_POLICY["pricing"]     = "mutable"
GROUP_EXCLUDES["analysis"]  = ("analysis/cost-value/",)
```

`GROUP_EXCLUDES` is new: a group may hand a subtree to a group with a different
policy, and exactly one group claims any file — two would hash it twice and make
the suite digest depend on an ordering nobody chose.

`verify_suite` also gained one rule: **a release makes no claim about a group it
never declared.** v1.0 predates `pricing`, so `pricing` does not appear in v1.0's
report at all. Without this, adding any future group would have retroactively
broken every older manifest.

**Pricing is still pinned — by its own anchor.** Each snapshot is immutable,
versioned by date, and carries its own `.sha256` beside it. That is the
architecture the brief asked to confirm:

    MondayBench suite release v1.1   +   pricing snapshot <date>/<sha256>

rather than a suite digest that moves whenever a vendor moves a price. The repo
already had the snapshot half; what was missing was keeping the two apart in the
manifest.

## 5. Digests

| | |
|---|---|
| v1.1 before | `4e5ec2f368a83b9048f3389ff9d5bcfcb68cd2c01d08e3734d022f3cc60f6052` |
| v1.1 after | `a4d6eb6eb143f1d975e15362642c256b36abbf3824f2edbeb0f5c1327c319a22` |
| reason | 28 pricing files moved from `analysis` (append_only) to `pricing` (mutable); `GROUP_EXCLUDES` and the undeclared-group rule added |
| v1.0 | `c056b4b43d3caeb3b50394282b08ed281a5716fb1df68d1666abb950aa0b2a80` — **unchanged** |

**Cut once, and it held.** After the re-cut, a new pricing snapshot
(`pricing-snapshot-2026-09-03.yaml` + `.sha256`) and a finding document were
added, and `verify-release --version 1.1` still reports every scoring group as
`identical` — the additions land in `pricing`, `4 added`, which is not a
failure. That is the demonstration that the scope is now correct: the manifest
did not need re-cutting to accommodate them, which under the old scope it would
have.

## 6. Tests

`tests/test_release_boundary.py`, 23 tests, all passing. They encode the
semantic boundary rather than the current file list:

* **A** editing an experimental Opus audit does not break v1.1 — asserted as
  "that path is in a `mutable` group", not "that file hashes to X".
* **B** updating cost publication data does not break v1.1, and no frozen group
  claims any path under `analysis/cost-value/`.
* **C** changing a frozen scenario prompt **does** break it.
* **D** changing a frozen rubric **does**, and so does changing an evaluator's
  external `judge-prompt.md` — which under v1.0's fingerprint moved nothing.
* **E** changing a v1.1 official evaluation **does**, and so does deleting an
  official run.
* **F** v1.0 still verifies, keeps its digest, and makes no claim about the
  `pricing` group it never declared.

Plus the policy invariants: every score-bearing group is `immutable` or
`append_only`; `pricing` and `docs` are `mutable`; every pricing snapshot has a
`.sha256` beside it; and no file is claimed by two groups.

C, D and E mutate a temporary copy of the tree. Nothing real is written.

## 7. What was deliberately not changed

* **`analysis` stays `append_only`.** What remains in it — the monday-003/004/005
  calibration records, the boundary audit and its sha256, the token-budget audit,
  the capability profiles, serving qualification — are each tied to a published
  decision. A capability profile is read by the website; a calibration record is
  the justification for a rubric version. Those must not move.
* **Nothing was excluded from the manifest outright.** `pricing` is still hashed
  and still reported; only its policy changed. Excluding it would have removed
  the drift signal along with the false failure.
* **`config` stays `mutable`**, as before: `models.yaml` gains a row when a model
  is onboarded.
