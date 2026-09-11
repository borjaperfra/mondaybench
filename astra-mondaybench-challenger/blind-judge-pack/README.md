# MondayBench v1.0 blind judge package

This package contains fifteen ungraded candidates. Each candidate directory is self-contained: exact input, exact response, frozen rubric, reference material, criterion packets, penalty instructions, weights and an unfilled verdict template.

Evaluate one candidate at a time. For each atomic criterion use its packet, which contains the applicable frozen definition and reference material. Judge meaning rather than exact wording; do not reward unstated facts or penalize style. When between labels choose the lower. Record PASS, PARTIAL or FAIL, response evidence and a criterion-specific reason for every criterion. Blank values are unfilled fields, not verdicts.

For penalties, read the candidate's penalty-instructions.md, frozen rubric, complete input and reference. The input is the authority on whether a statement is supported; the reference is not an exhaustive list of permissible facts. Use only penalty types defined for that scenario. Be conservative; omissions and weak answers are handled by atomic criteria. Record considered penalties with evidence, reason and materially_misleading=true/false; an explicit empty list is valid when none apply. Only materially misleading violations incur penalties. The semantics JSON contains the frozen type mappings, weights, cap and noise deduction rules.

For candidates with noise-instructions.md, classify every listed category explicitly. Do not default blank noise fields to false. Produce labels and evidence; deterministic point conversion is separate. Do not infer candidate identity, compare candidates, or use outside results. No judgments or scores are supplied here.

Criterion and penalty instruction files follow the frozen recorded-evaluator materials. Versioned scenario instructions are preserved for scenarios 002–005; scenario 001 uses the built-in instructions whose default rendering is unchanged from v1.0. Candidate references, weights and rubric definitions are frozen v1.0 artifacts. Criterion packets intentionally omit weights from the atomic judging prompt, while the accompanying rubric and semantics retain them for later deterministic conversion.
