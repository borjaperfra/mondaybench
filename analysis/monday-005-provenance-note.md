# Sample provenance in MondayBench — why run ids are not evidence

**Repository-level fix, found while running the monday-005 official battery.**

## The rule, and the gap

monday-003 stated the rule and every archive README since repeats it: a run the
rubric was developed against cannot be the evidence that rubric publishes.
`leaderboard.check_calibration_overlap` was written to enforce it.

It enforced it by comparing `run_id` between the official evaluator's
evaluations and a calibration evaluator's evaluations, both read from the live
tree. That has two failures, and monday-005 hit both at once.

**1. Archiving disables the check.** The rule tells you to archive the
calibration battery. Doing so moves its evaluations out of `evaluations/`, so
the comparison has nothing left to read and returns clean — and it would return
clean even if a calibration response had been promoted verbatim. A guard that
switches itself off when you follow the procedure it enforces is not a guard.

**2. `run_id` is a location, not a provenance fact.** Archiving also frees the
run numbers. monday-005's live tree was empty when the official battery ran, so
the deterministic lowest-free-number policy restarted at `run-001` and the
official ids collide exactly with the calibration ids. A comparison keyed on
`run_id` would now report a false positive on every model, for samples that are
genuinely independent.

So the clean result the guard gave for monday-005 was not evidence of anything.
The independence was established manually, by content hash. This note is about
making that mechanical.

## The identity

`runner.sample_identity(record) -> (content_sha256, request_id)`.

**Primary: `sha256` over the response text**, exactly as the provider returned
it. That is the artefact a rubric is developed against — when a criterion is
written while reading a response, those bytes are what it was fitted to.

**Corroborating: `provider_metadata.request_id`**, the provider's own
generation id. Audited across all 206 run files in the repository: present on
every one, and unique per distinct sample. The only repeats are seven
monday-003 samples filed in two archive directories at once, which is archival
duplication of one sample rather than two samples sharing an id.

It is corroborating rather than primary because the schema types it
`str | None`. A future provider that stops returning one must degrade the guard,
not silently disable it — which is the failure this whole exercise exists to
remove.

**Deliberately excluded**, because none of it is a property of the sample: the
score, any judge verdict, the evaluation path, leaderboard position, the run
number, the file location, the timestamp. Every one of those can change without
the sample changing, and several change precisely when a battery is archived.

The identity survives moving a run to archive, renumbering, directory changes
and evaluation changes.

## The check

`leaderboard.check_sample_provenance(scenario_id, root)`, called from
`check_calibration_overlap` so every existing publication path picks it up with
no call-site change.

It compares every live official run against **every archived run for that
scenario**, found under the same `archive/*/runs-<scenario>/` layout
`archived_run_numbers` already relies on. Archived material is development
material by convention — every archive README says so.

It also reports duplicates **inside** the official battery. Two official runs
with identical bytes are one sample, not two, and a mean over them is not a mean
over three observations.

Generic, not monday-005-specific: any scenario with an archive gets it.

## Tests

`tests/test_sample_provenance.py`, fourteen tests.

| Case | What it pins |
|---|---|
| A | An archived calibration sample promoted verbatim **and renumbered** is rejected. Verified to return clean under the old run_id check. |
| B | **Same `run_id`, different response is allowed.** monday-005's real situation. If this fails, someone has put run numbers back in the provenance path. |
| C | Different `run_id`, identical sample is rejected. |
| C2 | Shared provider request id is rejected even where the text differs. |
| C3 | Duplicates inside the official battery are rejected. |
| D | The real monday-005 battery: 21 archived vs 21 official, zero overlap. |
| E | All 21 official samples mutually distinct. |
| E2 | Every monday-005 run carries a request id, both sides. |
| F | monday-001 … monday-004 pass the new guard unchanged. |
| F2 | The guard actually finds archived material — a guard that silently finds nothing to compare is the failure mode being removed. |
| F3 | Identity ignores run number, timestamp and file location. |

`test_the_calibration_battery_is_archived_and_out_of_the_live_tree` in
`tests/test_monday_005.py` previously asserted that live run numbers were above
3. That assertion used the run number as a proxy for provenance and broke the
moment numbering restarted — it now compares content hashes. No test in the
repository treats a run id or its numeric suffix as evidence of provenance.

`runner.archived_run_numbers` and its test are unchanged and remain correct:
they exist to stop a *verdict file* replaying against the wrong text, which is
keying, not provenance. Run ids are preserved for display and navigation.

## Historical compatibility

Zero overlap and zero internal duplicates in every scenario:

| Scenario | live runs | archived runs | content overlap | request-id overlap | live duplicates |
|---|---:|---:|---:|---:|---:|
| monday-001 | 21 | 20 | 0 | 0 | 0 |
| monday-002 | 22 | 8 | 0 | 0 | 0 |
| monday-003 | 25 | 30 | 0 | 0 | 0 |
| monday-004 | 31 | 7 | 0 | 0 | 0 |
| monday-005 | 21 | 21 | 0 | 0 | 0 |

No historical data was rewritten. The guard is additive.

---

## A separate defect, reported and NOT fixed

Found while tracing why monday-005's numbering restarted. It is not a provenance
defect and fixing it is outside the scope of this change, so it is recorded
rather than applied.

**`archived_run_numbers` is honoured on only one of the two generation paths.**
In `cli.run`, the reservation reaches the schedule through `plan_battery` when
`--reuse-valid-runs` is passed. The plain path is:

```python
else:
    schedule = {slug: list(range(1, total_runs + 1)) for slug in slugs}
```

which numbers from 1 unconditionally and never consults the archive. monday-005's
official battery was generated with `--all-models --runs 3` and took that
branch, so it restarted at `run-001` over the archived calibration ids — the
exact collision `archived_run_numbers` exists to prevent, and which `plan` had
correctly predicted as `4, 5, 6` moments earlier.

The consequence is real but bounded: the archived calibration verdict files are
keyed by the same run ids as the official runs, so replaying one against the
other would score the wrong text without erroring. Nothing in the repository
does that today — the calibration verdicts live in
`archive/monday-005-v0.4-calibration/verdicts/` and the official battery is
served only from `verdicts/monday-005/official.jsonl` — and the new provenance
check makes a promoted sample detectable regardless.

The fix is to give both branches the same reservation. It is a few lines and it
touches no data. Not applied here because it was not the assigned change and the
official runs must not be renumbered.
