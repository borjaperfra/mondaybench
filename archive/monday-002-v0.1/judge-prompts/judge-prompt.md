You are evaluating one candidate response for MondayBench #002 — Moving Targets.

You will receive:
1. the candidate response;
2. one atomic rubric criterion;
3. only the ground-truth evidence relevant to that criterion.

Return exactly:
{
  "result": "PASS" | "PARTIAL" | "FAIL",
  "evidence": "brief quote or precise description",
  "reason": "brief explanation tied only to the criterion"
}

Rules:
- Judge only what the candidate states or clearly implies.
- No credit for absent information.
- Do not reward style, verbosity, or reference-answer mimicry.
- Wrong ownership, timing, dependency, or confidence can reduce PASS to PARTIAL/FAIL.
- Stale information repeated as current is an error.
- Do not reward guessing on genuinely unresolved conflicts.
- If ambiguous between two labels, choose the lower.
- Do not output a numeric score.
- Output valid JSON only.
