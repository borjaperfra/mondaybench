# MondayBench judge pack — one model, two batteries, #001–#005

Thirty runs of the same model against the same five frozen scenarios: the fifteen
that produced its published Monday Score, and fifteen more generated afterwards
under identical prompts and settings.

## What this is for

The published score came out low enough to be worth checking. Re-running the whole
battery moved it by more than four points without a single scenario, prompt or
setting changing — so either the published fifteen drew badly, or the judging moved
between the two batteries, or both.

One judge labelled all thirty runs, in a single session, having judged the
published battery before the second one. That is the condition under which
anchoring is hardest to rule out from the inside. This pack is an independent
second reading, not a review of the first. **The first labels are not in any pack.**

## The three sets

| set | what it holds | use it for |
| --- | --- | --- |
| `official/` | the 15 runs behind the published score, 3 per scenario | scoring the published battery on its own terms |
| `probe/` | the 15 runs of the second battery, 3 per scenario | scoring the second battery on its own terms |
| `combined/` | the same 30 runs, **6 per scenario, both batteries shuffled together** | telling the two apart — or failing to |

`combined/` is the one that answers the question. In `official/` and `probe/` the
judge knows every response in front of them came from the same batch, and that is
itself a signal. In `combined/` they cannot tell which battery a response came
from, so a score gap that survives is a gap in the responses rather than in the
reading of them. If only one set gets judged, judge `combined/`.

`official/` on its own is the narrower ask: score the fifteen runs behind the
published number and see whether they land where they landed the first time.

## Files

| file | for the second judge? |
| --- | --- |
| `official/pack-monday-00X.json` | yes — 5 packs, 3 candidates each |
| `probe/pack-monday-00X.json` | yes — 5 packs, 3 candidates each |
| `combined/pack-monday-00X.json` | yes — 5 packs, 6 candidates each |
| `provenance-map.json` | **no** — label → run identity, battery, model, timings |
| `held-back-verdicts.json` | **no** — the first-pass labels and scores |

Hand over the pack files only. Open the other two after the second judge's labels
are recorded.

## Sizes

| scenario | name | criteria | candidates in `combined/` |
| --- | --- | --- | --- |
| monday-001 | Back to Work | 19 + 6 noise items | 6 |
| monday-002 | Moving Targets | 20 | 6 |
| monday-003 | Blockers | 21 | 6 |
| monday-004 | Numbers Don't Lie | 27 | 6 |
| monday-005 | Read the Room | 31 | 6 |

## What is in a pack

- `scenario.prompt_text` — the frozen prompt. `scenario.scenario_prompt_sha256` is
  the hash of the assembled prompt (prompt plus sources, in `source_order`) that
  every run record carries and that `releases/v1.2/SUITE-FROZEN.yaml` publishes —
  check the pack against the frozen release with it. `prompt_file_sha256` is the
  hash of `prompt.md` alone.
- `scenario.sources` — every source file the model was given, in the order it was
  given them. This is the whole world: a candidate claim is supported only if one
  of these files supports it.
- `scenario.rubric` — the frozen rubric, with each criterion's `points`,
  `partial_points`, and its PASS and PARTIAL bands.
- `scenario.ground_truth` — the reference answer.
- `candidates` — responses under `Candidate A…F`, shuffled. The labels carry no
  order, no battery, no length ranking and no quality ranking.
- `expected_output.criteria_ids` — every criterion id to return a label for.
- `evaluation_protocol` — the labelling rules.

Nothing in a pack names the model, the battery, the run number, or any score.

## What to send back

For each candidate, one label — `PASS`, `PARTIAL` or `FAIL` — for **every**
criterion id in `expected_output.criteria_ids`, each with a verbatim quotation from
that candidate's own text, plus any global penalties.

monday-001 additionally scores noise resistance: for each id in
`expected_output.false_actions.ids`, say whether the candidate triggered it. That
dimension starts at its maximum and deducts per trigger.

Score = sum of `points` (PASS) and `partial_points` (PARTIAL), minus penalties,
floored at zero.

## Rules that matter

- Judge each candidate on its own. Do not rank the candidates against each other,
  and do not let a strong candidate raise the bar for the next one.
- If a response sits between two bands, take the lower one.
- Length is not quality. Across these batteries the shortest response of six scored
  highest on its scenario, and one of the longest scored below the median on
  another.
- Read the PASS band before the PARTIAL band, and quote the candidate rather than
  paraphrasing — the quotation is what makes the label checkable afterwards.

## Note on the earlier build

An earlier version of this directory held two packs at the top level,
`pack-monday-002.json` and `pack-monday-005.json`, covering the second battery
only. Those are now `probe/pack-monday-002.json` and `probe/pack-monday-005.json`,
with the **same candidate labels and the same response hashes** — labels already
recorded against them stay valid.
