# Northstar — Monday business review pack

Northstar sells an AI inference platform to businesses. This is the data pack
behind this morning's business review. It covers September and October 2026.
Both months are complete.

## What leadership wants to decide this week

- Finance is asking whether to reduce investment in one customer segment.
- Growth is asking whether to increase spend on one acquisition channel.
- Product is asking which plan should get the next quarter's engineering focus.
- The CFO has separately asked for CAC payback by acquisition channel.

## How to read the files

**customers.csv** — one row per customer, current as of this morning.
`usage_account_id` is the identifier the usage pipeline writes for that customer
and is the authoritative link between billing records and usage records.
`arr_eur` is the annualised value of the customer's current contract.

**revenue.csv** — one row per invoice, recorded at its full value in the month
it is dated. Subscriptions are invoiced in advance for the period they cover:
`billing_period_months` is the number of months an invoice covers, and is 0 for
invoices that do not cover a period. October's invoices were issued between the
1st and the 3rd. `source` is the system the record was loaded from.

**usage.csv** — one row per usage account per month. `requests` counts API calls
and `tokens_m` counts tokens processed, in millions. `usage_change_pct` is the
change in requests against the previous month, where there is one.

**plans.csv** — one row per plan per month. `revenue_eur` is monthly recurring
revenue on that plan, with annual contracts counted at their monthly equivalent.
`infra_cost_eur` and `support_cost_eur` are the infrastructure and support costs
directly attributable to the plan; `support_cost_eur` includes the fully loaded
cost of the customer-success staff assigned to it. `included_requests_per_customer`
is the request volume included in the plan price; usage beyond it is billed
separately at renewal.

**acquisition.csv** — one row per lead that converted. `attributed_revenue_eur`
is the annualised contract value the marketing platform credited to the channel
at the point of conversion. Expansion bookings take effect from the following
billing cycle.

**funnel.csv** — marketing leads by channel and month, and the number of those
leads that reached a paid trial in the same month. Trial-to-paid conversion runs
on a longer cycle and is not tracked in this pack.

**support.csv** — one row per support ticket raised in the month.

## Operational notes

- Acme moved its reporting workload from interactive API calls to two scheduled
  batch runs per day in late September. The implementation plan estimated a
  40–50% reduction in interactive request volume.
