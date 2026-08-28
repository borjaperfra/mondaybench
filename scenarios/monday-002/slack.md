# Slack
## Thursday, September 10
### #enterprise-launch
09:08 — Maya (CEO)
> I don't want Enterprise Controls opened broadly without Security being comfortable with the migration. If we change the build after their review, follow Priya's release policy.
09:41 — Sam (Release Manager)
> Atlas's migration window is Monday morning. If rollout hasn't begun by 12:00 Monday, their admins aren't available again until Thursday.
11:18 — Priya (Security)
> Release policy: exact build already verified in staging = production post-deploy check only. A code-changing patch after staging verification = 25-minute Security delta review before production deploy, then 20-minute post-deploy verification. I can do delta reviews asynchronously from a submitted diff.
16:52 — Maya
> I'm not adding another executive gate. Follow Security's release policy and Sam's rollout process.
### #customer-atlas
10:27 — Laura (CS)
> Atlas renewal is signed. Missing Monday's migration window doesn't threaten renewal, but pushes migration to Thursday and creates executive noise.
### #pricing
15:06 — Daniel (Finance)
> The pricing workbook is still being revised. Don't quote it externally.

## Friday, September 11
### #enterprise-launch
08:51 — Marcus
> Staging build 2.9.4 passed the session-preservation test.
09:37 — Priya
> 2.9.4 staging verification complete.
13:46 — Marcus
> Production attempt with 2.9.4 failed on shard eu-03 before rollout opened. No customer impact.
14:18 — Marcus
> I have two safe recovery approaches for Monday; details are in release-options. One changes code, one doesn't.
14:26 — Priya
> If the chosen recovery changes code from 2.9.4, I need the delta review before production.
15:03 — Sam
> After production is healthy and Priya completes required verification, I need 15 minutes to open and sanity-check rollout.
### #launch-comms
09:21 — Julia
> Sarah has the customer announcement draft.
11:44 — Sarah
> I'm out Monday. Daniel — forwarding you Julia's final draft and Atlas recipient list.
11:51 — Daniel
> Received both. I'll watch Sam's rollout channel Monday.
### #customer-zenith
08:42 — Laura
> Zenith validated the audit-log export fix.
10:58 — Finance Bot
> Contract countersigned: Zenith — 24 months — €96k ARR.
12:13 — Laura
> Moving Zenith back to normal CS cadence.
### #pricing
08:35 — Daniel
> Yesterday's workbook numbers are obsolete.
09:07 — Daniel
> Internal scenario planning: €2,500 platform / 40 seats / €55 extra seat. Still not external.
13:32 — Sales Bot
> enterprise-pricing-v4-final.xlsx pinned by Sales Ops.
### #orion
15:58 — Laura
> Orion admin says SCIM provisioning worked.
16:00 — Rollout Bot
> Orion / org_71A / scim_enabled=false
16:03 — Laura
> Their support ticket lists org_17A. I may have looked at the wrong account in CRM.
16:05 — Sam
> Don't send another status until we confirm which org ID is theirs and read the live flag for that org.
### #leadership
16:32 — Maya
> I need the expansion explanation before 11:00 Monday. Board pack locks 11:30.
16:36 — Daniel
> The two slipped expansions are only part of it. Account files have the rest.
16:41 — Maya
> Keep it to actual arithmetic. If a customer's reduction has no stated cause, don't invent one.
