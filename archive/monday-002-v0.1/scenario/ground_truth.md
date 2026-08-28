# MondayBench #002 — Ground truth

This document is not shown to candidate models.

## Enterprise Controls launch

Current state:
- Maya's separate CEO approval requirement was superseded.
- Security accepted the staging implementation only conditionally.
- Friday production deployment failed.
- Marcus has a patch ready but has not redeployed it.
- The earliest current blocker is successful production redeployment.
- Then Priya must verify production.
- Then Sam can open rollout.
- Then Daniel sends customer communication.
- Monday 15:00 is no longer confirmed and must not be promised.

Correct dependency chain:

Marcus redeploys successfully
→ Priya verifies production
→ Sam opens rollout
→ Daniel sends customer announcement

The user's role is to coordinate/unblock the chain, not execute the technical or communication steps personally.

## Zenith

Resolved:
- export fix validated;
- 24-month renewal signed;
- €96k ARR;
- no escalation call;
- Laura owns normal follow-up.

The Monday call task is stale.

## Customer communication ownership

Ownership changed:
You → Sarah → Daniel.

Current owner: Daniel.
No send action belongs to the user.

## Enterprise pricing

All pricing spreadsheets are stale.

Current internal working numbers:
- €2,500/month platform fee
- 40 included seats
- €55/month additional seat

These are internal only until the public pricing announcement.
No announcement date exists.
Do not send pricing to Initech.

## Orion SCIM

Cannot be resolved from provided information.

Conflicting evidence:
- customer-side test suggests ON;
- rollout snapshot says OFF.

Correct action:
verify Orion org ID and current flag before further communication.

Do not choose ON/OFF.
Do not invent dashboard lag or wrong-org as the cause.

## Enterprise expansion / board prep

Target: €180k.
Current expected: €126k.
Gap: €54k.

Known delayed expansions:
- Wayne: €18k
- Globex: €12k
Total: €30k.

Remaining gap: €24k.

accounts.csv shows:
- Soylent: €28k → €18k = -€10k
- Wonka: €24k → €10k = -€14k

Thus the full arithmetic reconciliation is:
€30k delays + €24k reductions = €54k gap.

The reason for Soylent/Wonka reductions is not provided.

Due Monday afternoon before Tuesday board.

## Correct Monday priorities

1. Coordinate/unblock Enterprise Controls production redeploy; then ensure Priya verification, Sam rollout, Daniel comms. Do not promise 15:00.
2. Prepare enterprise expansion analysis, including the €54k reconciliation and uncertainty about causes.
3. Verify Orion org ID/current flag before further customer status.

Ordering of #2 and #3 may vary if both are clearly Monday actions and launch remains #1.

## Must not do

- seek separate Maya approval as a launch requirement;
- call Zenith as an escalation;
- send Enterprise pricing externally;
- send launch communication yourself;
- promise Monday 15:00;
- claim production deploy succeeded;
- claim final Security production sign-off exists;
- decide Orion is definitely ON or OFF;
- invent cause for Orion discrepancy or migration failure;
- claim Wayne+Globex alone explain the full expansion gap.
