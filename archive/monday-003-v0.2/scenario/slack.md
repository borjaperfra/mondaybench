# Slack

## Friday 16:42 — #enterprise-sso

Noah:
Atlas is still expecting Enterprise SSO this week. Wednesday EOD is the committed date.

Marcus:
The auth side is basically done, but I cannot finish the compatibility work until the billing schema migration lands. The current branch still assumes the old account mapping.

Elena:
Yep. The schema change is mine. Roughly three hours once I start.

Marcus:
After that I need about four focused hours for the compatibility patch.

Sam:
QA needs the completed compatibility patch before regression. Two hours should be enough if nothing surprising appears.

Marcus:
And production rollout itself is about an hour after QA gives us the green light.

Sam:
If Marcus ends up stretched this week, can anyone else pick up the compatibility work?

Elena:
That branch is Marcus's account-mapping rewrite. Nobody else has been inside it since the spike.

## Friday 17:06 — #onboarding

Julia:
The onboarding flow itself is ready.

Sam:
Do we still need Marcus's event instrumentation before launch?

Julia:
No. Existing analytics are enough for launch monitoring. The additional events can ship afterwards.

Marcus:
Noted. The tracker still has it down as a launch blocker, so I have three hours held for it.

## Friday 17:24 — #contoso

CEO:
URGENT — Contoso says the export is broken. Can we please get someone on this first thing Monday?

Noah:
Looking.

Julia:
I ran it. The export completes and the file is valid. What they are reacting to is the date format: `2026-09-21` where they expect `21/09/2026`.

Noah:
Does that break their import?

Julia:
No. They confirmed both formats import correctly. They want the European format for an internal demo Tuesday.

CEO:
Still, €110k ARR account, and the expansion is meant to sign this quarter. Please don't let it linger.

Julia:
I wrote that exporter last quarter. Changing the format string and the fixtures is about two hours.

## Monday 08:06 — #support-escalations

Rachel:
Contoso opened a ticket at 07:40. Two of their delegated administrators get `insufficient scope for tenant export` when they run the tenant data export. Their tenant owner account works.

Sam:
Reproduced on staging with a delegated-admin token. The tenant-scoped export permission check does not accept delegated admins at all.

Daniel:
I was in that permission model two weeks ago for the SCIM work, so I can take it. Realistically three and a half hours for me, plus about half an hour with Marcus first to walk the delegated-admin path.

Marcus:
Two hours if I do it. Either way it sits on the same account-mapping layer as Elena's schema change, so it can only go in after that lands.

Rachel:
Logged as `contoso_permission_patch` and assigned to Marcus, since it is his module. Reassign if that is wrong.

Rachel:
Once the permission check accepts delegated admins, producing and sending the file itself is about an hour of Julia's time. Same exporter.

## Monday 08:19 — #billing

Elena:
Reminder: I am out from Wednesday noon through Friday.

If the billing migration somehow slips, Daniel can take over, but I need about 30 minutes with him before I leave to transfer the production migration permissions and walk through the runbook.

Elena:
Also, once the schema change lands the reconciliation backfill runs for about ninety minutes. I kick it off; after that it is automated.

## Monday 08:29 — #enterprise-sso

Marcus:
Heads up on my week. I am in Atlas's pre-rollout technical session on Tuesday, 09:00 to 13:00 — Laura's IT team wants the walkthrough before they start on Thursday. I am heads-down either side of it.

## Monday 08:41 — #board

Sarah:
I have started the Friday board pack.

Most of it can be done independently, but I do not want to freeze the revenue charts until the billing migration and its backfill are complete. The current revenue pipeline still duplicates some expansion events.

Noah:
Makes sense. Work on everything else in parallel.

## Monday 08:52 — #pricing

Daniel:
Reminder that the new pricing page cannot go public until packaging approval clears. Priya's committee signs it off.

Sarah:
Understood. I will put the approval pack together as soon as the page is built and I can take the screenshots off it.
