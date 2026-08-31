Evaluate one atomic criterion for MondayBench #005 v0.1 "Read the Room". Return JSON only: {"result":"PASS|PARTIAL|FAIL","evidence":"brief semantic evidence","reason":"criterion-specific reason"}.

The response contains four artifacts under fixed headings: CEO BRIEFING, ENGINEERING UPDATE, CUSTOMER EMAIL, STATUS PAGE UPDATE. Most criteria are scoped to one of them and say which. Some compare all four. Read the whole response before scoring any criterion, because a fact's correctness here depends on which artifact it is in.

**This is not a writing test.** Do not score tone, register, length, structure, formatting or professionalism, and do not reward fluency. A blunt four-line status update that says the right things beats a polished one that publishes an unapproved time. If a criterion tempts you toward "this reads well", you are scoring the wrong thing.

**Different detail is not contradiction.** This is the single most important instruction here and the easiest to get wrong. Two artifacts stating the same fact at different resolutions are consistent: "a subset of Batch API requests failed" on the status page and "29.9% of Batch API requests failed" in the CEO briefing are the same fact. A fact present in one artifact and absent from another is not a contradiction. Different framing for a technical and a non-technical reader is not a contradiction. The customer email using Contoso's own 36.3% while the CEO briefing uses the 29.9% aggregate is not a contradiction - those are two correct figures on two correct denominators for two different readers. Only an artifact asserting a factual or commitment STATE that another artifact denies is a contradiction.

**Absence is not denial.** Saying nothing about cause in the customer email while treating it as an open hypothesis in the engineering update is the correct pattern, not an inconsistency. Several criteria are satisfied precisely by a fact NOT appearing somewhere.

**But an artifact that was not produced does not earn the absence criteria.** If a criterion is scoped to an artifact the response did not write, or wrote so slightly that it is not the deliverable, score FAIL. A boundary is honoured by a document that exists and leaves the fact out, not by the absence of the document. A response cannot buy the confidentiality points by staying silent.

**Omission and error are different labels.** Where a criterion requires something and the response simply does not do it, that is PARTIAL. Where the response does it wrongly - asserts a cause that is not established, publishes a time nobody approved, tells the customer the wrong number - that is FAIL. Do not collapse the two.

**Wording is free; state is not.** Never require a phrase. "Root cause remains under investigation", "we have not confirmed the underlying cause", "the cause is still unconfirmed" and "leading hypothesis, untested" are all the same correct state. "The outage was caused by the connection-pool change", stated without qualification, is the wrong state however carefully it is written. Judge the state the reader would come away with.

**Numbers carry tolerance.** The aggregate impact figure passes anywhere from 28% to 32%, and "about 30%", "roughly a third" and the raw counts all pass. Per-account figures pass within 1%. What does not pass is a figure on the wrong denominator, because the reporting basis is stated in context.md.

Score only the criterion in front of you. This scenario deliberately lets one mistake surface in several places - publishing the internal estimate is both a boundary failure and a commitment failure, and each criterion prices its own consequence. Do not charge the same error twice inside one criterion, and do not credit a correct call here because the response got a different one right elsewhere.

If a response sits between two labels, choose the lower.
