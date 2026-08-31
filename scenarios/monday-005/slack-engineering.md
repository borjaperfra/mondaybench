# #inc-batch-1109

Engineering incident channel. All times UTC, 2026-11-09.

---

**11:42 · Priya Sandoval**
Got the page. batch_api_5xx_rate on fleet-a. Looking.

**11:43 · Priya Sandoval**
502s on POST /v1/batch/jobs. Not a total outage, submissions are partially
getting through. fleet-b looks completely clean.

**11:44 · Marcus Oyelaran**
Confirmed, fleet-b is fine. So it is not the API gateway and it is not the
client SDK, both fleets sit behind the same gateway.

**11:47 · Priya Sandoval**
Checked the storage provider. Status page green, and Files API is healthy and
it goes through the same provider. Ruling that out.

**11:50 · Marcus Oyelaran**
Volume on fleet-a is way up. Looks like wonka kicked off a big scheduled job
around 11:38. We're at about 3x the morning average on that fleet.

**11:52 · Priya Sandoval**
Could just be load then?

**11:53 · Marcus Oyelaran**
Maybe, but fleet-a took more than this last Tuesday without breaking a sweat.
I don't want to hang it on volume alone.

**12:03 · Marcus Oyelaran**
Workers on fleet-a are all sat waiting on database connections. And r3 went out
at 11:31 this morning and dropped max pool size from 80 to 24 per worker. That
is a big drop and the timing is eleven minutes before the first page.

**12:04 · Priya Sandoval**
That feels like it.

**12:04 · Marcus Oyelaran**
It feels like it, yes. But r3 went to fleet-b as well and fleet-b is completely
happy, so the pool change on its own does not explain why only a is hurting.
It is a hypothesis, not a finding. We have not tested it.

**12:06 · Ruth Adeyemi**
I've put a second update on the status page off the back of Marcus' 12:03.

**12:09 · Marcus Oyelaran**
Ruth, that update says we have identified the cause. We have not. Please do not
put anything else out about cause until I say so.

**12:10 · Ruth Adeyemi**
Understood, my mistake. I will leave it until you give me something confirmed.
Anything that goes out from here I'll take from Tomas' approved list.

**12:31 · Marcus Oyelaran**
Proposal: do not roll back r3 yet. If we roll it back and things recover we
still won't know whether it was the pool setting or the load, and we lose the
state on fleet-a that we need to test it properly. Cut traffic to fleet-b
instead, that fixes customers now and keeps the evidence.

**12:33 · Priya Sandoval**
Agreed. Doing the cutover.

**12:58 · Priya Sandoval**
Cutover done. All batch traffic on fleet-b. fleet-a drained.

**12:59 · Priya Sandoval**
error rate is on the floor already. that's fixed 🎉

**13:01 · Marcus Oyelaran**
It is mitigated, not fixed. We have moved the traffic off the broken thing. We
still do not know what the broken thing is, and fleet-a is still broken, it is
just not serving anyone. Verification window is open until 14:30 and I am not
calling this resolved before then.

**13:04 · Priya Sandoval**
Fair, poor choice of words.

**13:26 · Marcus Oyelaran**
Holding at 0.3-0.4%. Looks good so far.

**13:41 · Marcus Oyelaran**
Rough internal guess for planning: if the window closes clean at 14:30 and the
re-drive finishes, I'd expect us to be fully wrapped up and fleet-a back in
rotation around 16:00. That is my own estimate for our planning, it is not
something to tell anyone outside this channel.

**13:52 · Priya Sandoval**
Re-drive of failed jobs is going. About 60% through the affected accounts. No
failures on the re-drive.

**14:12 · Priya Sandoval**
0.3%. 18 minutes left on the window.

**14:18 · Dana Whitfield**
I have a board call at 15:00. Someone give me the state of play before then —
what happened, who is hit, what I should say if it comes up.
