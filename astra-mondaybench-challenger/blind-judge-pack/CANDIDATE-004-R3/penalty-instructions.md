Return JSON only: {"penalties":[{"type":"MATERIAL_HALLUCINATION|PROHIBITED_ACTION|MAJOR_DATA_ERROR|UNSUPPORTED_CAUSALITY","evidence":"...","reason":"..."}]}

Be conservative. An empty list is a valid and common answer. Never penalize an omission, a weak answer, a partial credit, or style: the rubric criteria already price those, and penalizing them again is double punishment. A penalty needs something the response **asserts or recommends**.

**MATERIAL_HALLUCINATION** - states as established fact a figure or fact the pack does not contain, and the claim is material. Examples: any channel spend, CAC or payback figure, because no file records acquisition cost; a stated reason for why customers churned, because no file records one; reporting that Wayne Enterprises or Prestige Worldwide has no usage data when their usage is in the file under the identifier `customers.csv` supplies. Presenting the same idea as a hypothesis to be tested is correct behaviour, not a hallucination.

**PROHIBITED_ACTION** (this rubric calls it *prohibited business action*) - recommends an action the supplied data rules out. Examples: cutting, exiting or defunding SMB on the strength of the 22.2% logo churn rate; doubling or materially increasing Paid Search spend on raw attributed revenue; recommending action against Acme as a churn risk on a usage decline the pack explains; dropping a customer or a plan on the strength of a data artifact. Naming a course of action in order to reject it is exactly right and must never be penalized. The test is whether the response tells leadership to do it.

**MAJOR_DATA_ERROR** - a numeric or data mistake that the analysis then rests on. Examples: quoting an October revenue total that double counts the duplicated invoice and drawing a growth conclusion from it; treating the EUR 120,000 annual invoice as a monthly figure, or Gringotts as a EUR 120,000-a-month account; joining usage to billing on `customer_id` alone and then reporting the missing account as a finding; quoting a churn rate whose denominator is wrong in a way that changes which segment looks worst.

Do not apply it for arithmetic that is merely imprecise, for a rounding difference, or for a figure that is wrong but which nothing in the response depends on. The criteria price those. The bar is that a recommendation or a headline conclusion stands on the mistake.

**UNSUPPORTED_CAUSALITY** - asserts a material causal link the pack does not establish. The shape to watch for is Soylent: requests down, tickets up and MRR down in the same month, with the response stating that the support problems caused the contraction, or that the usage decline caused the tickets. Also: attributing revenue growth to a campaign, or churn to a product gap, as fact. Naming the pattern, or offering a mechanism explicitly as a hypothesis to investigate, is correct and must not be penalized.

If a candidate penalty does not clearly meet one of these bars, leave it out.
