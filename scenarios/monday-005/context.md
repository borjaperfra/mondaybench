# Northstar — operating context

Northstar sells an API platform. Customers call several separate API surfaces;
this pack concerns one of them, the **Batch API**, which accepts bulk job
submissions. The other surfaces (Inference, Embeddings, Files) are unrelated
services and are not part of this incident.

**All timestamps in every file below are UTC**, written as `HH:MM` on
2026-11-09 unless a date is given. There is no other time zone anywhere in this
pack.

## The Batch API

The Batch API runs on two independent worker fleets, **fleet-a** and
**fleet-b**. Every customer account is pinned to exactly one fleet and stays
there. Which fleet an account sits on is an internal deployment detail; it is
not a product tier and customers are not told about it.

## Who is who

| Name | Role |
|---|---|
| You | Incident Commander for this incident |
| Dana Whitfield | CEO |
| Marcus Oyelaran | Staff engineer, Batch API |
| Priya Sandoval | Engineer, on call |
| Tomas Lindqvist | Support lead |
| Ruth Adeyemi | Communications, owns the public status page |

## The files in this pack

| File | What it is |
|---|---|
| `incident-timeline.md` | The incident log, maintained by you, most recent entry last |
| `slack-engineering.md` | The `#inc-batch-1109` channel, verbatim |
| `incident-notes.md` | Your own running notes as Incident Commander |
| `customer-impact.csv` | Per-account Batch API traffic and failures during the incident window |
| `sla-contract.md` | The service-level section of one customer's contract |
| `support-tickets.csv` | Tickets that arrived today, from the support queue |
| `status-page-history.md` | What has already been published on the public status page |

## Column definitions

`customer-impact.csv` covers **only** the incident window, 11:42 to 12:58.

| Column | Meaning |
|---|---|
| `customer_id` | The account |
| `worker_fleet` | Which fleet the account is pinned to |
| `batch_requests_window` | Batch API requests this account made between 11:42 and 12:58 |
| `batch_failures_window` | How many of those returned an error |
| `first_failure_utc` | First failed request for this account, blank if none |
| `last_failure_utc` | Last failed request for this account, blank if none |

Accounts that do not appear in `customer-impact.csv` made no Batch API calls in
the window. Northstar has 36 customer accounts in total; 9 of them use the
Batch API.

**Platform-wide traffic for reference:** across all API surfaces, Northstar
served **842,000 requests** between 11:42 and 12:58. The Batch API's share of
that is whatever `customer-impact.csv` sums to.

**The headline impact figure for this incident** is failed Batch API requests
as a share of all Batch API requests in the window. Fleet membership is an
internal detail and is not a reporting basis.

`support-tickets.csv` columns are `ticket_id`, `opened_utc`, `customer_id`,
`channel`, `subject`, `body`.
