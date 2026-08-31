# Why monday-005 was frozen before calibration, not after

#001-#004 were all frozen at the end: calibrate, settle the rubric, then pin
the bytes. #005 was frozen first, on 2026-08-31, before a single run existed.

**The reason.** A calibration battery is only interpretable if every run
answered the same prompt. Freezing first makes that a property of the
repository rather than of nobody having touched a source file midway. The
prompt hash `532cd464...` is now pinned, and `validate` fails if any of the
eight candidate-visible files moves by a byte.

**The cost, stated rather than discovered later.** `FROZEN.yaml` also pins
`rubric.yaml` at version 0.1 and pins `scenario.yaml`, which names it. So:

- a rubric change during calibration is no longer a silent edit. It requires
  either a deliberate re-freeze, or #004's pattern of adding a NEW versioned
  file (`rubric-0.2.yaml`) and re-freezing against it. Both are auditable acts
  and neither is an accident, which is the point.
- `rubric.yaml` at 0.1 will survive on disk as the calibration record whatever
  happens next, the same way monday-004 kept its `rubric.yaml` (0.1) and
  `rubric-0.2.yaml` after freezing against 0.3.

**What frozen does NOT mean here.** `scenario.yaml` still says
`status: draft`. There is no official evaluator, no official battery, no
leaderboard and no entry in any Overall release. Frozen means the bytes are
pinned; published is a separate act that has not happened.

---

# Re-freeze: rubric 0.1 -> rubric 0.2

**2026-08-31, after the 7x1 calibration battery was generated and before any
response was judged.**

## Why

Two judge-facing semantic ambiguities were discovered by reading the seven
responses, before any of them was scored:

1. **Conditional SLA quantification vs current applicability.** The 0.1 FAIL
   band for `sla_undetermined_with_process` read "promised, denied, or
   quantified". Reproducing the Schedule B.4 credit table *conditionally* is a
   correct explanation of the contract and necessarily contains percentages, so
   the band could have failed a right answer. 0.2 draws the line where it
   belongs: a quantified conditional contract explanation passes, a quantified
   claim of current applicability fails.

2. **External update-time commitment vs recovery-time commitment.** 0.1 did not
   separate a commitment about the NEXT COMMUNICATION from a commitment about
   SERVICE RECOVERY. 14:30 - the verification window's close - appears in all
   seven responses, and whether "we expect to confirm recovery by 14:30" in an
   external artifact was the authorised thing or the prohibited thing was left
   to the judge unaided. 0.2 makes the semantic object of the time the test,
   and states that hedging verbs do not launder a recovery ETA.

**This is not model-specific tuning.** Neither correction was made because a
particular model scored a particular way - no score existed when they were
written. Neither makes a criterion harder or easier; each replaces a boundary
that could be read two ways with one that cannot. A diff audit asserts that the
criterion ids, count, point values, dimensions, weights, penalties, penalty
amounts and total are identical between 0.1 and 0.2, and that exactly three
criterion texts changed - the two the corrections name, one of which spans two
criteria.

## What did NOT change

The candidate prompt, all eight sources, and `ground-truth.yaml` are
byte-identical. The prompt still hashes to `532cd464...`. **No model was
regenerated because of the rubric change**, and none needed to be: generation
inputs did not move, so the seven responses answer exactly the bytes 0.2 scores
them against.

`rubric.yaml` (0.1) stays on disk unedited as the artifact generation ran
under, the same way monday-004 kept `rubric.yaml` and `rubric-0.2.yaml` after
freezing against 0.3.

## Order of events, for the record

1. Scenario frozen against rubric 0.1. `frozen content is intact`.
2. 7x1 calibration battery generated. 6/7 first attempt; deepseek-v4-flash
   needed 2 (see the serving incident record).
3. Responses read, not scored. Two ambiguities found.
4. rubric-0.2.yaml written from 0.1 by textual substitution; diff audited.
5. Deliberate re-freeze against 0.2. No regeneration.
6. Judging begins against 0.2.

---

# Re-freeze: rubric 0.2 -> rubric 0.3

**2026-08-31, after the 7x1 battery was judged under 0.2 and before the 3x7
battery was generated.**

## Why

Two kinds of change, both rubric-only.

**Four semantic repairs**, every one of them found by actually judging the
seven responses against 0.2 and hitting a band that could be read two ways.
All four were classified RUBRIC_AMBIGUITY in the 0.2 calibration report and all
four are now closed:

1. `artifacts_current_as_of_snapshot` — FAIL covered only a state that WAS true
   earlier. It now covers a state that is not true YET.
2. `status_page_publishable` — the unpublishable-material list omitted a false
   resolution claim, the most damaging thing that page can carry during an open
   incident.
3. `internal_eta_not_external` — 0.2 penalised OMITTING the internal estimate.
   A model must not have to repeat internal-only information to prove it knows
   the information is internal.
4. `security_item_reaches_engineering` — measured restatement of technical
   detail rather than whether the handoff is actionable.

**Two information boundaries the frozen world already contained.** Both
correspond to `audience_matrix` rows declared restricted for both external
audiences before the battery ran, which no 0.2 criterion scoped to an external
artifact:

- `fleet_topology_not_external` — `context.md` L14-17 states the fleet split is
  an internal deployment detail and that "customers are not told about it".
- `cause_investigation_not_external` — Slack 12:09, "do not put anything else
  out about cause until I say so", plus an approved-content list carrying no
  cause item and stating it is "the whole of what has been cleared".

Proposal, derivation and the anti-overfitting gate are in
`analysis/monday-005-boundary-audit-blind.md`, sealed at
sha256 `25162cdaa6184e8d58885175d35fd89dcac73eea46fd31de8de92161b45b01b1`
before any shadow scoring. That document also records, in its own §0, that the
blindness protocol it was written under could not be honoured: the agent had
already read all seven responses in the previous task. The compensating
controls are stated there rather than the guarantee being claimed.

## What did NOT change

The candidate prompt, all eight sources and `ground-truth.yaml` are
byte-identical. The prompt still hashes to `532cd464...`. Total stays 100, the
six dimensions and their weights are unchanged, both penalties and the 14-point
cap are unchanged, and the 131,072 ceiling is unchanged. 29 -> 31 criteria; the
two additions are funded from within `information_boundaries`, which stays at
19.

**No model response was regenerated for 0.2 or for 0.3.** The seven 7x1
responses were re-scored, not re-produced.

## Order of events

1. Frozen against 0.1. 7x1 generated.
2. Re-frozen against 0.2 (two corrections). 7x1 judged: 203 verdicts, 4 flagged
   RUBRIC_AMBIGUITY, 0 JUDGE_VARIANCE.
3. Boundary audit; Phase-A proposal sealed by hash; 0.3 built; all seven
   shadow-scored against it without regeneration.
4. **Re-frozen against 0.3, here.**
5. 3x7 battery generated against 0.3. rubric.yaml and rubric-0.2.yaml stay on
   disk unedited as the record of stages 1 and 2.
