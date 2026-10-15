# Judging brief — Gemini 3.8 Flash (High), blind, one scenario per judge

You are judging three anonymised candidate responses for ONE MondayBench
scenario, criterion by criterion. The labels you write are the evidence a score
and a capability profile will be computed from, so they must be specific and
defensible.

## What you may read

1. **Operative rules:** `audits/blind-rejudge/opus-5-blind-rejudge.md`, lines
   1–123 (the base criterion instruction, the two rules, global penalties,
   noise resistance, score arithmetic). Apply them exactly.
2. **Your scenario's sections A–D** in the same file — the frozen prompt with
   all source material, the frozen rubric, the answer key, and the
   scenario-specific judge instructions:

   | Scenario | Lines (A–D only) |
   |---|---|
   | monday-001 | 124–985 |
   | monday-002 | 1190–1661 |
   | monday-003 | 1911–2972 |
   | monday-004 | 3254–4350 |
   | monday-005 | 5054–6428 |

   **Do not read section E** (another model's responses) or anything beyond
   your scenario's range.
3. **The candidates:** `gemini-3.8-mondaybench-challenger/judge-pack/blind-judge-pack.json`,
   `scenarios[i]` where `scenario_id` is yours → `candidates[].response`.
4. The scenario's own source files under `scenarios/<scenario>/` if you need
   to check whether a claim is supported.

## What you must NOT read

- `gemini-3.8-mondaybench-challenger/judge-pack/provenance-map.json`, or
  anything else under `gemini-3.8-mondaybench-challenger/` except the pack file.
- Any verdict, evaluation, score or leaderboard for any model (`verdicts/`,
  `evaluations/`, `leaderboard/`, `experiments/*/verdicts*`, `audits/` other
  than the brief file above, `STATUS.md`, `README.md`).
- Do not try to identify the model or guess how it scored before.

## How to judge

- Every criterion in your scenario's rubric, for every candidate, individually.
  Not holistic.
- If a response sits between two labels, choose the lower.
- `evidence`: a short verbatim quote (or tight paraphrase with the key words)
  from the candidate that the label rests on; for a FAIL on an omission, say
  what is missing. `reason`: one sentence tying it to the PASS/PARTIAL/FAIL
  definition. **Write specific evidence for every label, PASS included** — no
  boilerplate.
- Judge each candidate on its own; do not compare them.

## Output

Write **one file**: `experiments/gemini-3.8-flash-high-opus-judge/blind-verdicts/<scenario>.blind.jsonl`,
UTF-8, LF line endings (in Python: `open(path, "w", encoding="utf-8", newline="\n")`).
One JSON object per line:

```json
{"candidate_id": "MB-00N-CandidateA", "criterion_id": "<id from the rubric>", "result": "PASS|PARTIAL|FAIL", "evidence": "...", "reason": "..."}
```

Then, per candidate, one penalties row (always, even if empty):

```json
{"candidate_id": "MB-00N-CandidateA", "kind": "penalties", "violations": [{"type": "<penalty type from this rubric>", "evidence": "...", "reason": "...", "materially_misleading": true}]}
```

List every penalty candidate you considered, with `materially_misleading`
true or false, per the frozen penalty instruction.

**monday-001 only**, per candidate, one noise row covering every false-action
category in the rubric:

```json
{"candidate_id": "MB-001-CandidateA", "kind": "noise", "items": [{"id": "<false-action id>", "triggered": false, "evidence": ""}]}
```

## Before you finish

Check with a short script that: every rubric criterion appears exactly once per
candidate; every `result` is PASS/PARTIAL/FAIL; criterion ids match the rubric
exactly; each candidate has its penalties row (and noise row on monday-001).

Report back: the file path, the number of rows, and per candidate the count of
PASS / PARTIAL / FAIL and any material penalty. **Do not compute or report a
score.**
