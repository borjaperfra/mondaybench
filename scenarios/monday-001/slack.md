# Slack messages

## Thursday

### #incidents

**08:42 — Laura Chen — Customer Success**
Acme is reporting a significant increase in API errors this morning. Their engineering lead says requests to `/v2/events` are intermittently returning 500s.

**08:44 — Marcus Webb — Engineering**
Looking now.

**08:47 — Laura Chen**
They're pretty unhappy. Marking this P1 until we understand what's happening.

**09:03 — Marcus Webb**
Confirmed. Error rate jumped after yesterday's 2.18.0 deploy. Investigating the event processing workers.

**09:31 — Marcus Webb**
Found it. One of the new worker configs is exhausting the connection pool under higher concurrency.

Rolling back that config now.

**09:48 — Marcus Webb**
Rollback complete. Error rates are returning to normal.

Keeping an eye on it for the next couple of hours.

**11:57 — Marcus Webb**
Acme has been stable for two hours. Error rate is back at baseline.

I'll write up the incident notes later today.

**12:04 — Laura Chen**
Thanks. I'll check with them directly.

### #product

**10:16 — Julia Santos — Product Marketing**
For the Analytics v2 launch email, are we still using the screenshot with the old dashboard navigation?

**10:24 — Sam Rivera — Product**
I think so, unless design has the new one ready before Friday.

**10:31 — Sam Rivera**
Release is still planned for Monday from our side.

**14:08 — Julia Santos**
I'm going to start drafting the launch email this afternoon. I'll share it tomorrow.

**16:43 — Sam Rivera**
QA found two regressions in saved reports. Neither is data-loss related, but one affects exports.

We'll decide tomorrow whether this changes Monday's release.

### #random

**12:21 — Daniel Foster**
Lunch order: Thai or pizza?

**12:22 — Julia Santos**
Thai.

**12:22 — Marcus Webb**
Pizza.

**12:24 — Daniel Foster**
Democracy has failed us again.

## Friday

### #sales

**08:51 — Noah Williams — Sales**
Contoso update: call went really well yesterday.

Commercial terms are basically agreed. I don't see anything major blocking the renewal now.

**09:17 — Noah Williams**
Legal still has a couple of details but nothing scary.

### #product

**09:36 — Sam Rivera**
QA update on Analytics v2:

The export regression is more annoying than we thought. Fix is straightforward, but we need another QA cycle.

I'm proposing Wednesday instead of Monday.

**09:41 — Julia Santos**
Works for marketing.

**09:43 — Daniel Foster — CEO**
I'd rather ship Wednesday cleanly than force Monday.

Wednesday it is.

**09:47 — Sam Rivera**
👍 I'll update the internal release plan.

**10:06 — Julia Santos**
In that case I'll take full ownership of the launch email. @You no need to do anything there — I'll have the draft ready before Tuesday.

### #design

**10:32 — Julia Santos**
Tiny thing: are we keeping the outlined "spark" icon for Analytics or moving to the filled version?

**10:37 — Sam Rivera**
I prefer filled.

**10:39 — Laura Chen**
Outlined is clearer IMO.

**10:44 — Julia Santos**
Here's the filled one at 16px. It looks a little muddy.

**10:48 — Marcus Webb**
+1 outlined.

**10:51 — Sam Rivera**
At 24px filled looks better though.

**10:56 — Julia Santos**
Most customers will see 16px in the sidebar.

**11:02 — Daniel Foster**
I have no idea why I'm reading this thread.

**11:03 — Julia Santos**
Important executive matters.

**11:07 — Sam Rivera**
😂

**11:14 — Julia Santos**
Let's just keep the existing outlined icon for this release.

**11:15 — Sam Rivera**
Fine by me.

### #leadership

**11:42 — Daniel Foster**
One thing for next week: I'm slightly concerned about enterprise churn.

The dashboard has it moving from 3.1% to 4.4%. Not catastrophic, but directionally I don't like it.

Would be good to understand what's driving that before the board meeting next week.

**11:51 — Noah Williams**
Two enterprise cancellations I know about were Pied Piper and Hooli.

Pied Piper consolidated vendors after their acquisition.

Hooli said adoption wasn't high enough across teams.

**11:55 — Daniel Foster**
Useful. Let's understand whether those explain the movement or whether there's something broader happening.

### #growth

**13:06 — Julia Santos**
Did conversion absolutely tank today or am I imagining things?

I checked the dashboard earlier and it looked horrible.

**13:12 — Noah Williams**
I noticed that too but only looked quickly.

**13:18 — Julia Santos**
Could just be noisy Friday traffic. Worth checking next week.

### #pricing

**14:03 — Daniel Foster**
Quick reminder from today's pricing discussion:

The new Enterprise tiers are still a proposal.

Please keep the numbers internal until we've finalized them and announced the change.

**14:06 — Noah Williams**
👍

**14:08 — Laura Chen**
Got it.

### #general

**15:04 — Daniel Foster**
Partner sync done. Nothing major from my side.

Main takeaway is they're still targeting the October integration.

**15:09 — Sam Rivera**
Same here.

**16:48 — Julia Santos**
Have a good weekend everyone 👋
