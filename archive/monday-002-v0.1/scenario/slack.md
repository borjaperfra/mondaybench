# Slack

## Thursday, September 10

### #enterprise-launch

09:12 — Maya (CEO)
> Reminder: do not launch Enterprise Controls without my explicit approval. I want to see the final security sign-off first.

09:16 — You
> Got it. I'll hold the launch until you approve.

10:03 — Sam (Release Manager)
> Current plan is still Monday at 15:00 if approvals land.

11:42 — Priya (Security)
> Security review is mostly complete. The only open item is the SSO session migration. We need to see the fix before sign-off.

14:08 — Marcus (Engineering)
> We reproduced the SSO migration problem. Existing enterprise sessions can be dropped during the migration. Working on it.

17:51 — Maya (CEO)
> Spoke with Priya. I'm comfortable proceeding once Security signs off. You do NOT need to come back to me for a separate approval after that.

17:54 — Sam
> Great. Updating my checklist: Security sign-off is the gate.

### #customer-zenith

13:24 — Laura (CS)
> Zenith is threatening to cancel unless we resolve the audit-log export issue. Their renewal is this month. Treating this as urgent.

13:31 — You
> I'll call them Monday if this isn't resolved before then.

### #random

16:20 — Daniel
> The new coffee machine is trying to bankrupt us one €2.40 espresso at a time.

16:24 — Julia
> Still cheaper than the place downstairs.

## Friday, September 11

### #enterprise-launch

09:18 — Marcus
> SSO migration fix is in staging now. Existing sessions survive in our tests.

10:06 — Priya
> Reviewed staging. The fix looks good. Security is happy with the implementation, conditional on the same build being deployed successfully to production and the post-deploy check passing.

10:11 — Sam
> So we're down to production deploy + verification. If those pass, I can open the rollout.

14:37 — Marcus
> Production deployment started.

15:04 — Marcus
> Deploy stopped. Migration step failed on one production shard. No customer impact because rollout hasn't opened.

15:07 — Priya
> Please don't treat staging sign-off as final production sign-off. Ping me after the production deployment succeeds and I'll run the verification.

15:12 — Sam
> Monday 15:00 is no longer something I'd promise externally. We can still launch Monday if the deploy and Security verification happen in time, but there is no confirmed launch time right now.

17:46 — Marcus
> I have a patch ready for the failed migration step. I have not redeployed it yet. I can take this first thing Monday.

### #customer-zenith

09:02 — Laura
> Good news: export fix went out last night and Zenith validated it this morning.

11:26 — Laura
> Renewal signed. 24 months, €96k ARR. No escalation needed. I'll handle the normal onboarding follow-up.

11:31 — You
> Perfect. I'll drop the Monday call then.

### #enterprise-pricing

08:44 — Daniel (Finance)
> Please ignore the pricing sheet I sent yesterday. Finance changed the minimum platform fee after the forecast review.

09:10 — Julia
> Is `enterprise-pricing-v4-final.xlsx` still the one Sales should use?

09:13 — Daniel
> No. Do not use any spreadsheet from this thread externally yet. Approved internal working numbers are now:
> Platform fee: €2,500/month
> Included seats: 40
> Additional seat: €55/month
> These are for internal planning only until the public pricing announcement.

13:40 — Sales Bot
> Reminder: `enterprise-pricing-v4-final.xlsx` is pinned in this channel.

13:44 — Daniel
> The pinned file is stale. My 09:13 message is the current source for internal working numbers.

### #launch-comms

09:32 — Julia
> I'll draft the Enterprise Controls customer announcement this morning.

10:20 — You
> I can send it once we have the launch green light.

11:48 — Julia
> Change of plan: Sarah will own the customer send so Product doesn't need to.

15:33 — Sarah
> I'm unexpectedly out Monday. Daniel, can you send the customer announcement once Sam confirms rollout is open?

15:36 — Daniel
> Yes, I'll own the send Monday. @you no action needed on the email.

### #orion

16:02 — Laura
> Orion says the new SCIM feature is enabled for them now. They tested adding a user and it worked.

16:04 — Sam
> That's odd. My rollout dashboard snapshot from 16:02 still shows Orion SCIM flag = OFF.

16:07 — Laura
> Could be dashboard lag, or I could be looking at a different org. I don't want to guess.

16:09 — Sam
> Agree. Let's verify the org ID and current flag state Monday before telling Orion anything else.

### #leadership

17:12 — Maya
> For tomorrow's board prep: I need a clean explanation of why enterprise expansion revenue is down this month.

17:18 — Daniel
> We know two large expansions slipped, but that's not enough to explain the whole gap. I'll send the account data.

17:25 — Maya
> Please have a first cut ready Monday afternoon so I can review it before Tuesday's board meeting.
