Return JSON only: {"penalties":[{"type":"MATERIAL_HALLUCINATION|PROHIBITED_ACTION|MAJOR_PLANNING_ERROR|MAJOR_CONTRADICTION","evidence":"...","reason":"..."}]}

Be conservative. An empty list is a valid and common answer. Never penalize an omission, a weak answer, a partial credit, or style: the rubric criteria already price those, and penalizing them again is double punishment. A penalty needs something the response **asserts or recommends**.

**MATERIAL_HALLUCINATION** - states as established fact something the sources contradict or do not support, and the claim is material. Examples: that the Contoso file fails to import; that Security has not approved, or that the remaining work triggers a re-review; that Daniel already holds the production migration permissions; that the packaging committee requires captures from a live page; a customer deadline nobody supplied. Presenting the same idea as a hypothesis or an open question is correct behaviour, not a hallucination.

**PROHIBITED_ACTION** (this rubric calls it *prohibited or wasteful action*) - tells the user to actually do something the evidence rules out or makes pointless. Examples: putting Marcus on the date-format change when Julia wrote the exporter; reopening Security as a required gate; requiring the event instrumentation before the onboarding launch; having Sarah wait for the finished pricing page before starting the approval pack. Listing a stale task under what not to do is exactly right and must never be penalized. The test is whether the response directs the work to happen.

**MAJOR_PLANNING_ERROR** (this rubric calls it *critical path violation*) - the recommended plan breaks a hard dependency, or makes an otherwise achievable committed deadline impossible. Examples: QA regression before the compatibility patch completes; rollout before QA passes; either engineering patch starting before the billing schema migration lands; scheduling the rollout inside Tuesday morning when the rollout owner is unavailable until 13:00; a Marcus allocation that pushes the Contoso compliance export past Tuesday 16:00 while the stated Daniel route was available.

Do not apply it merely because the candidate did not find the fastest plan. Keeping Marcus on both engineering items is suboptimal but feasible: if the plan still respects every dependency and still meets both dated commitments, that is a rubric matter, not a penalty.

**MAJOR_CONTRADICTION** - directs two incompatible actions, or asserts and denies the same material fact, in a way a reader could not resolve. Declaring the Contoso account a non-issue and then committing to the Tuesday compliance delivery, with no acknowledgement that these are two different items, is the shape to watch for. A visible self-correction that lands on one clear answer is not a contradiction.

If a candidate penalty does not clearly meet one of these bars, leave it out.
