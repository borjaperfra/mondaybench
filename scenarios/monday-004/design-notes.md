# monday-004 "Numbers Don't Lie" — design notes

**EVALUATOR AND AUDIT ONLY.** This file is not in `source_order`; no candidate
ever sees it. It records what the scenario is testing, which conclusion is
correct, which data supports it, and which mistake it is built to catch.

The order below is the order the scenario was built in, deliberately: ground
truth, then the derivations it requires, then the traps, then the rubric, then
the datasets, then the prompt. No CSV was written before the conclusion it has
to support existed on this page. The numbers quoted here are the ones
`tests/monday_004_derivations.py` recomputes from the published CSVs; if a
figure here and a figure in the data ever disagree, the test fails.

---

## 0. What this scenario is for

#001 asks what mattered over a weekend. #002 asks what is still true. #003 asks
what has to happen before what. All three are read-then-plan tasks over prose.

#004 asks a different question:

> Can the model make the right business decision from messy company data?

The material is seven tabular sources and one short context note. There is no
Slack, no email thread and no calendar. Nothing important is said in a sentence;
almost everything important has to be computed, and several of the computations
only mean something once two tables have been joined.

Three decisions are on the table, and each has an attractive wrong answer that a
naive reading of a single column supports.

---

## 1. Ground truth — the three decisions

### Decision 1 — the segment (Finance wants to cut SMB)

**Correct: do not cut SMB on this evidence. Flag it, size it, ask for what is
missing.**

| segment | customers | churned | logo churn | ARR lost |
|---|---:|---:|---:|---:|
| SMB | 18 | 4 | 22.2% | €123,600 |
| Mid-market | 10 | 1 | 10.0% | €180,000 |
| Enterprise | 8 | 0 | 0.0% | €0 |

SMB's churn rate is the worst in the company and the fact is real. It is also
four events out of eighteen, and those four events between them destroyed
**less ARR than the single Mid-market churn** (€123,600 against €180,000). SMB
is 6.6% of total ARR. Nothing in the pack gives acquisition cost, lifetime value
or retention by segment, and `plans.csv` reports economics by **plan**, not by
segment — and plan and segment do not align, so SMB's contribution margin is not
derivable from the pack at all.

Supported: name the churn, quantify the denominator and the ARR, ask for the
segment economics before deciding.
Not supported: exit or defund the segment.

### Decision 2 — the channel (Growth wants to double Paid Search)

**Correct: do not double Paid Search on attributed revenue.**

| channel | attributed revenue | of which new-logo | of which expansion |
|---|---:|---:|---:|
| paid_search | €274,800 | €64,800 | €210,000 |
| partner | €166,800 | €166,800 | €0 |
| content | €109,200 | €91,200 | €18,000 |
| outbound | €80,400 | €56,400 | €24,000 |

Paid Search leads raw attribution by 65%. **76.4% of its attributed revenue is
expansion on accounts that were already customers**, three of them since 2023 or
2024. On new-logo revenue it is third, behind Partner and Content.

The funnel points the same way: Paid Search took its lead volume from 520 to 900
(+73%) while its lead-to-trial conversion fell from 8.46% to 6.44%.

And no file in the pack contains channel spend. CAC, CAC payback and ROAS are
therefore not computable. Partner looks like the strongest new-logo channel on
what is here, but "best CAC" is a claim the pack cannot support.

### Decision 3 — the plan (Product wants a focus)

**Correct: Pro.**

| plan (October) | customers | revenue | contribution | margin | ARPU |
|---|---:|---:|---:|---:|---:|
| enterprise | 14 | €659,500 | €194,700 | 29.5% | €47,107 |
| pro | 9 | €66,200 | €41,500 | 62.7% | €7,356 |
| starter | 13 | €32,000 | €10,300 | 32.2% | €2,462 |

Enterprise is 87% of revenue and by far the highest revenue per customer, and it
is the **worst** of the three on contribution margin. Pro earns 62.7% on 8.7% of
the revenue, its usage grew 14.8% month over month against a flat Enterprise
book, three of its nine customers are already over their included request
volume, and its support load per customer is the highest in the company and
rising (2.38 → 3.11 tickets per customer).

That combination — healthy margin, real usage growth, a ceiling customers are
hitting, and friction that is visible but bounded — is the case for Pro. It is
not "Pro earns the most", because it does not.

---

## 2. Required derivations

Each row is a conclusion the data must force, the tables it needs, and the
mistake it is there to catch.

| # | conclusion | needs | catches |
|---|---|---|---|
| D1 | The +12.0% headline is not recurring growth | revenue.csv | summing an invoice column |
| D2 | SMB churn is real, small and not a decision | customers.csv | a percentage without a denominator |
| D3 | Acme's −45% usage is a workflow change, not churn risk | usage.csv + context.md + revenue.csv | a health metric read alone |
| D4 | Paid Search's lead is expansion, not new business | acquisition.csv | trusting an attribution total |
| D5 | Conversion rate fell while conversions rose | funnel.csv | reading one of the two |
| D6 | Enterprise has the highest ARPU and the worst margin | plans.csv | revenue per customer as economics |
| D7 | Pro deserves the product focus | plans + usage + support + customers | picking the biggest number |
| D8 | One October invoice is double-counted | revenue.csv | trusting the row count |
| D9 | Wayne Enterprises' usage is under another id | customers.csv + usage.csv | joining on the obvious key |
| D10 | Enterprise has the most tickets and not the worst rate | support.csv + plans.csv | a raw count as a rate |
| D11 | Soylent's three bad signals are not a causal chain | usage + support + revenue | inventing the mechanism |
| D12 | CAC payback cannot be computed | absence of spend anywhere | inventing the input |

### D1 — headline revenue growth is distorted (three levels)

```
raw September                      €797,100
raw October                        €892,900     +12.0%   <- the headline
October less the duplicate         €873,400     + 9.6%
recurring September                €746,100
recurring October                  €757,700     + 1.6%   <- the answer
```

Two things separate the first line from the last. Gringotts moved from a monthly
contract to an annual one and was invoiced **€120,000 on 2026-10-01** for twelve
months (`billing_period_months=12`); its recurring value is €10,000/month, so
€110,000 of the October total buys eleven months that have not happened yet.
And one October invoice appears twice (D8), worth another €19,500.

`context.md` states the accounting fact — an invoice is recorded at full value
in the month it is issued, and `billing_period_months` says how many months it
covers — and states no conclusion. The normalisation is the candidate's job.

Two normalisations are defensible and they do **not** agree, which the first
draft of the rubric missed. Subscriptions only gives +1.6%. Subscriptions plus
the one-off professional services gives **-4.2%**, because September carried
EUR 51,000 of services against October's EUR 5,700. Both refute the headline and
both pass, provided the candidate says which invoices are in its figure. The
rubric does not require the word "MRR".

Known partial leak, accepted with eyes open: `plans.csv` reports plan revenue on
a recurring basis, so summing it for both months also yields ~€746k → ~€758k.
Reaching the answer that way requires noticing that two tables disagree and then
finding out why, which is exactly the cross-table reasoning this scenario is
for. `annual_prepayment_normalized` is written so that only identifying the
annual invoice earns it; "plans.csv says flat" alone is PARTIAL.

### D2 — sample size and ARR, not percentages

Total ARR across all 36 rows is €9,092,400; active ARR is €8,788,800. SMB is
€602,400 of it. The four SMB churns are €123,600 — 1.4% of the book. Nakatomi,
one Mid-market logo, is €180,000 on its own.

Note that churn by **plan** and churn by **segment** are different numbers,
because plan and segment do not align: Starter is 4 of 13 (30.8%), Pro 1 of 9
(11.1%), Enterprise plan 0 of 14. Either framing is correct if labelled. Mixing
them — quoting the Starter rate as the SMB rate — is not.

### D3 — Acme is not churning

| | September | October | change |
|---|---:|---:|---:|
| requests | 4,200,000 | 2,310,000 | −45.0% |
| tokens (M) | 4,620.0 | 4,066.0 | −12.0% |
| active users | 240 | 232 | −3.3% |
| MRR | €78,000 | €78,000 | 0.0% |
| support tickets | 4 | 3 | −1 |

`context.md` states that Acme moved its reporting workload to two scheduled
batch runs per day in late September and that the implementation plan estimated
a 40–50% reduction in interactive request volume. It does not say the decline is
healthy. The data says the workload did not leave: tokens fell an eighth while
requests fell nearly half, which is what batching looks like, and seats, revenue
and tickets are all steady.

Treating Acme as a churn risk is a false positive. Treating the request decline
as *evidence of nothing at all* is also wrong — the correct move is to identify
it, explain it against the stated migration, and note that the account is
otherwise healthy.

### D4 / D5 — attribution and the funnel

Expansion rows carry `new_logo=false`, `expansion=true` and a
`first_customer_date` years before `campaign_start`. Three of Paid Search's four
expansion rows are Enterprise accounts that have been customers since 2023–2024.

```
             September            October
             leads  conv  rate    leads  conv  rate
paid_search    520    44  8.46%     900    58  6.44%
content        260    31 11.92%     330    34 10.30%
partner         60    15 25.00%      75    17 22.67%
outbound       160    10  6.25%     195    11  5.64%
total        1,000   100 10.00%   1,500   120  8.00%
```

Overall conversion fell 2.0 points while absolute conversions rose 20%. Both are
true and neither settles whether October was worse: that needs cost per lead or
lead quality, and the pack has neither.

### D6 / D7 — unit economics

`plans.csv` carries revenue, infrastructure cost and support cost. There is no
margin column and no contribution column; both have to be computed:

```
contribution = revenue_eur - infra_cost_eur - support_cost_eur
margin       = contribution / revenue_eur
```

October: enterprise €194,700 / 29.5%, pro €41,500 / 62.7%, starter €10,300 /
32.2%. September: enterprise €212,000 / 32.2%, pro €42,500 / 67.5%, starter
€8,400 / 34.9%.

Pro's contribution fell slightly while its revenue rose, because its support
cost rose faster — the friction is real and is part of the recommendation, not
an argument against it.

### D8 — the duplicate

`INV-2026-10-0208`, Soylent, €19,500, appears twice: once dated 2026-10-01 with
`source=stripe` and once dated 2026-10-02 with `source=billing_sync`. The
transaction id is the detector; nothing else in the row is unique. `context.md`
does not mention duplicates and no column is named to suggest one.

### D9 — the alias

Two customers' usage identifiers differ from their billing identifiers:

```
wayne-enterprises   -> wayne_ent      (Enterprise, €1,008,000 ARR)
prestige-worldwide  -> prestige_ww    (Mid-market, €114,000 ARR)
```

`customers.csv` carries `usage_account_id` and `context.md` names it as the
authoritative link. A join on `customer_id` alone silently drops Wayne, the
second largest account in the company, and a model that then reports Wayne as
having no usage has invented a fact — that is what the MAJOR_DATA_ERROR penalty
is scoped to.

### D10 — support burden

October: enterprise 35 tickets over 14 customers (2.50), pro 28 over 9 (3.11),
starter 11 over 13 (0.85). Enterprise raises the most tickets and has the second
best rate. Any defensible normalisation — per customer, per active user, per
million requests — moves Enterprise off the top; the criterion rewards
normalising at all, not one particular denominator.

### D11 — the correlation

Soylent, in the same month: requests −27.0%, support tickets 3 → 8, and MRR down
€2,500. Three facts, no mechanism. Nothing in the pack says why any of them
happened, and nothing links them. The correct handling is to flag the account
for investigation and to stop there. Asserting that the support problems caused
the contraction is the UNSUPPORTED_CAUSALITY penalty.

### D12 — the impossible metric

`context.md` records that the CFO has asked for CAC payback by channel. No file
contains marketing or sales spend of any kind. `plans.csv` has infrastructure
and support cost only, which is cost of service, not cost of acquisition.
Neither CAC nor payback is computable, and no assumption rescues it. Saying so
is the point; inventing a spend figure is a MATERIAL_HALLUCINATION.

---

## 3. Traps, and the wrong answer each one buys

| trap | the attractive wrong answer |
|---|---|
| headline sum | "Revenue is up 12% month over month." |
| duplicate row | any October total quoted as €892,900 |
| annual invoice | "October MRR is €892,900" / "Gringotts is a €120k/month account" |
| SMB churn % | "SMB churns at 22%, cut it." |
| Acme usage | "Acme is disengaging — €936k ARR at risk." |
| paid search attribution | "Paid Search returns €274,800, double the budget." |
| conversion rate | "October was a worse month." / "October was a better month." |
| ARPU | "Enterprise is our best plan." |
| ticket counts | "Enterprise has the worst support experience." |
| Wayne join | "Wayne Enterprises has no usage this period." |
| Soylent | "Support failures caused Soylent to contract." |
| CAC payback | any payback number at all |

A weak model should be able to produce a confident, well-formatted brief made
entirely of these. That is the design target: the failure mode is plausible, not
obviously broken.

---

## 4. What the rubric prices

25 atomic criteria over six dimensions, 100 points, penalty cap 25. The full
text is `rubric.yaml`; the shape is:

| dimension | points | criteria |
|---|---:|---:|
| A revenue reasoning | 20 | 4 |
| B customer health and churn | 15 | 4 |
| C acquisition reasoning | 20 | 5 |
| D plan economics | 20 | 4 |
| E cross-table and data quality | 15 | 4 |
| F decision quality and uncertainty | 10 | 4 |

No single criterion is worth more than 6, so one arithmetic slip cannot decide a
run. Numeric criteria carry an explicit tolerance: percentages ±0.5 points
unless the difference changes the decision, currency ±1%. Arithmetic that is
equivalent by another route passes; prose is never required to match.

## 5. Quality checks this design is meant to satisfy

1. No single table contains any of the three decisions.
2. D3, D7, D9, D10 and D11 all require at least two tables.
3. D1 requires cleaning (the duplicate) before the calculation means anything.
4. D1 reverses a headline: +12.0% becomes +1.6%.
5. D12 is requested and not answerable.
6. Every trap above is a defensible-looking recommendation.
7. Prose summarisation earns nothing: eighteen of the twenty-five criteria rest
   on a figure that is printed in no file and has to be computed.
