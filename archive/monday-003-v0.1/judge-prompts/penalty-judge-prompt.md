Return JSON only: {"penalties":[{"type":"MATERIAL_HALLUCINATION|PROHIBITED_ACTION|MAJOR_PLANNING_ERROR|MAJOR_CONTRADICTION","evidence":"...","reason":"..."}]}

Be conservative. An empty list is a valid and common answer. Never penalize an omission, a weak answer, a partial credit, or style: the rubric criteria already price those, and penalizing them again is double punishment. A penalty needs something the response **asserts or recommends**.

**MATERIAL_HALLUCINATION** - states as established fact something the sources contradict or do not support, and the claim is material. Examples: that the Contoso import is broken; that Security has not approved; that Daniel already holds the production migration permissions; a customer deadline nobody supplied. Presenting the same idea as a hypothesis or an open question is correct behaviour, not a hallucination.

**PROHIBITED_ACTION** (this rubric calls it *prohibited or wasteful action*) - tells the user to actually do something the evidence rules out or makes pointless. Examples: putting Marcus on the Contoso formatter when Julia owns it; reopening Security as a required gate; requiring instrumentation before the onboarding launch. Listing a stale task under what not to do is exactly right and must never be penalized. The test is whether the response directs the work to happen.

**MAJOR_PLANNING_ERROR** (this rubric calls it *critical path violation*) - the recommended plan breaks a hard dependency, or makes an otherwise achievable committed deadline impossible. Examples: QA regression before the compatibility patch completes; rollout before QA passes; spending Marcus's Monday on instrumentation in a way that pushes Enterprise SSO past Wednesday.

Do not apply it merely because the candidate did not find the fastest plan. A slower plan that still respects every dependency and still meets Wednesday is a rubric matter, not a penalty.

**MAJOR_CONTRADICTION** - directs two incompatible actions, or asserts and denies the same material fact, in a way a reader could not resolve. A visible self-correction that lands on one clear answer is not a contradiction.

If a candidate penalty does not clearly meet one of these bars, leave it out.
