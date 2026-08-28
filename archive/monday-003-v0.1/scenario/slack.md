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

## Friday 16:51 — #security

Maya:
Security review for Enterprise SSO is complete. Approved.

Noah:
Great. So no more Security gate?

Maya:
Correct, unless the implementation scope materially changes.

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
I checked it. Export succeeds. The issue is date formatting:
`2026-09-21` instead of `21/09/2026`.

Noah:
Does that break their import?

Julia:
No. They confirmed both formats import correctly. They want the European format for an internal demo Tuesday.

CEO:
Still, €110k ARR account. Please don't let it linger.

Julia:
Formatter is in my area. About two hours.

## Monday 08:34 — #billing

Elena:
Reminder: I'm out from Wednesday noon through Friday.

If the billing migration somehow slips, Daniel can take over, but I need about 30 minutes with him before I leave to transfer the prod migration permissions and walk through the runbook.

## Monday 08:41 — #board

Sarah:
I've started the Friday board pack.

Most of it can be done independently, but I don't want to freeze the revenue charts until the billing migration/backfill is complete. The current revenue pipeline still duplicates some expansion events.

Noah:
Makes sense. Work on everything else in parallel.

## Monday 08:52 — #pricing

Daniel:
We still need packaging approval before the new pricing page can go public.

Sarah:
Approval needs screenshots of the updated pricing page, doesn't it?

Daniel:
It needs screenshots showing the proposed packaging, yes.

Sarah:
Which is what the new page is supposed to be.

Daniel:
Mock screenshots are fine for internal approval. They don't need to come from the production page.
