# Contoso — Master Services Agreement, Schedule B (Service Levels)

Extract. Effective 2026-04-01. Northstar Technologies and Contoso Ltd.

## B.1 Covered services

This Schedule applies to the Core APIs: the Inference API, the Batch API and
the Files API. The Embeddings API is expressly excluded.

## B.2 Monthly Availability

**Monthly Availability** is calculated per calendar month as:

```
Monthly Availability = (Eligible Requests - Failed Requests) / Eligible Requests
```

**Eligible Requests** means all requests Customer makes to the Covered Services
in the calendar month, excluding:

- (a) requests during Scheduled Maintenance announced at least 48 hours ahead;
- (b) requests that failed as a result of Customer's own configuration,
  integration or client software, including retry behaviour that exceeds the
  documented rate limits;
- (c) requests rejected for exceeding Customer's contracted rate limits.

**Failed Requests** means Eligible Requests returning a `5xx` status.

## B.3 Service Level Commitment

Northstar commits to Monthly Availability of **99.9%** across the Covered
Services.

## B.4 Service Credits

Where Monthly Availability falls below the commitment, Customer is entitled on
request to a credit against the following month's fees:

| Monthly Availability | Credit |
|---|---|
| 99.0% or above, but below 99.9% | 10% |
| 95.0% or above, but below 99.0% | 25% |
| Below 95.0% | 50% |

## B.5 Determination and claims

Monthly Availability is determined by Northstar from its own service records
**after the end of the calendar month to which it relates.** Northstar shall
publish the figure within 10 business days of month end.

Customer must submit any credit claim within 30 days of that publication.
Credits are the sole and exclusive remedy for failure to meet the commitment.

## B.6 Disputed exclusions

Where Northstar excludes requests under B.2(b), it shall identify the excluded
volume and the basis for the exclusion in the published figure. Customer may
dispute an exclusion within the claim window.
