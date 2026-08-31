# Incident log — INC-2026-1109-01

Maintained by the Incident Commander. All times UTC, 2026-11-09.
Most recent entry last.

**11:31** — Release `batch-api@2026.11.09-r3` finishes rolling out. It goes to
both worker fleets. The changeset is small: three dependency bumps and one
change to the batch worker's database connection-pool settings (max pool size
lowered from 80 to 24 per worker).

**11:38** — Batch submission volume on fleet-a begins climbing. By 11:50 it is
running at roughly three times the morning's average, driven mainly by
wonka-industries starting a large scheduled job.

**11:42** — First alert. `batch_api_5xx_rate` crosses its page threshold on
fleet-a. Errors are `502` responses on `POST /v1/batch/jobs`. Priya
acknowledges the page. **This is the incident start time.**

**11:44** — Confirmed the errors are confined to fleet-a. fleet-b is serving
normally with no elevated error rate.

**11:47** — Checked the upstream object-storage provider Northstar uses for
batch payloads. Their status page shows no incident, and the Files API, which
uses the same provider, is healthy throughout. Upstream provider ruled out.

**11:55** — First public status-page update published. See
`status-page-history.md`.

**12:03** — Marcus notes that fleet-a workers are queueing on database
connections and that `batch-api@2026.11.09-r3` lowered the pool ceiling this
morning. Correlation noted. Not tested.

**12:05** — Second public status-page update published, drafted by Ruth from
the 12:03 message. See `status-page-history.md`.

**12:31** — Decision: do not roll back `r3` yet. Rolling back would remove the
evidence needed to test whether the pool change is actually responsible, and
the same release is running on fleet-b without harm. Mitigate by moving traffic
instead.

**12:58** — **Mitigation applied.** All Batch API traffic cut over to fleet-b.
fleet-a drained and held out of rotation. Error rate on `POST /v1/batch/jobs`
falls to 0.4% within two minutes. Baseline for this endpoint is 0.2%.

Note on figures: the only impact numbers for this incident are the per-account
rows in `customer-impact.csv`. No aggregate impact figure is recorded anywhere
in this log, deliberately — aggregate impact is computed from that file.

**13:00** — **Verification window opened. It closes at 14:30.** Northstar's
incident policy requires 90 minutes of continuous normal error rate on the
affected endpoint before an incident may be declared resolved. Nothing about
the incident is called resolved before that window closes clean.

**13:20** — Error rate holding at 0.3–0.4%. Queue depth on fleet-b normal. No
customer reports of new failures since the cutover.

**13:52** — Backlog of jobs that failed during the window is being re-driven
for affected accounts. Roughly 60% re-driven so far. No failures on re-drive.

**14:12** — Error rate 0.3%. Verification window still open, 18 minutes
remaining.

**14:20** — *Current time. Incident is OPEN: mitigated, verification in
progress, root cause not established.*

## Still open at 14:20

- Root cause not established. Two candidate explanations remain live and
  neither has been tested (see `incident-notes.md`).
- The `r3` rollback test has not been run.
- fleet-a is still out of rotation and has not been returned to service.
- The re-drive of failed jobs is not finished.
- Whether the incident is resolved cannot be stated until 14:30 at the earliest.
