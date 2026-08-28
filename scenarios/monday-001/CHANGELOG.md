# monday-001 — change log

A scenario is immutable **after official publication**. `monday-001` has not
been published: no official runs or scores exist yet, so the fixes below were
applied in place rather than as `monday-001-v2`. Any change made after the
first official publication requires a new scenario id instead.

The prompt SHA-256 is the integrity check. Runs generated against an earlier
hash are not comparable with runs generated after these fixes, and the
leaderboard flags a model whose runs span more than one hash.

---

## 2026-08-27 — pre-publication consistency fixes

Prompt SHA-256 before: `ac0149fb737a310b3bc4d3bcfede12ba1f800ba25ce91e720dab3780ef2beddd`
Prompt SHA-256 after:  `e19d123cd105469f62338604b0c8102f57f57793f344b22f11e4ee738a995c1b`

### 1. `slack.md` — board meeting date contradicted itself

**Was:** Friday 11:42, Daniel Foster, `#leadership`:

> One thing for **next week**: I'm slightly concerned about enterprise churn.
> [...] Would be good to understand what's driving that before the board
> meeting **tomorrow**.

**Problem.** The message contradicts itself inside four lines: it opens with
"next week" and closes with "tomorrow", and tomorrow from Friday is Saturday.
Meanwhile `meetings.md` (written 18 minutes later, Friday 12:00) and
`ground-truth.yaml` both put the board meeting on **Tuesday**, and the rubric's
`churn_action` PASS definition requires connecting churn work to "Tuesday's
board meeting".

A model reading Slack carefully would have computed Saturday and could lose
points for being precise about a defect in the source material.

**Now:** "...before the board meeting **next week**."

**Why this fix and not the alternatives.** Rewriting the Slack line to say
"Tuesday" explicitly would have removed the contradiction but also removed the
work: the model would no longer need to reconcile a vague Slack reference
against the authoritative meeting note. "Next week" keeps the meeting note as
the only place the exact day appears, so `churn_action` still requires reading
both sources — it just no longer punishes a model for doing so correctly.

### 2. `metrics.csv` — snapshot dated on a Thursday

**Was:** all seven rows dated `2026-08-27`, which is a Thursday.

**Problem.** The scenario is set on a Monday at 09:07, and `tasks.md` is stamped
"Exported: Monday 08:55". A metrics snapshot dated Thursday invites a model to
raise a data-freshness question that neither `ground-truth.yaml` nor the rubric
accounts for — an unscored distraction rather than a designed one.

**Now:** all rows dated `2026-08-31`, the Monday.

No metric values were changed. Umbrella's anomaly (163 API errors, 1821ms p95,
-41% 7-day usage on 94,217 requests) is untouched, as is Stark Industries'
higher raw error count on much higher traffic.

---

## 2026-08-27 (later) — the user was present for the events they missed

Prompt SHA-256 before: `e19d123cd105469f62338604b0c8102f57f57793f344b22f11e4ee738a995c1b`
Prompt SHA-256 after:  `ed4d7beb1d7d1029c36eb8533e449027e0dc1a1047f8a38951a91781a0a5e398`

**Found by a benchmarked model, not by the author.** `glm5.3-flash` raised it
unprompted in its "unclear" section:

> the Slack log shows messages from you Thursday and Friday despite your absence
> since Wednesday 17:30

It was right, and none of the other six models mentioned it.

**Problem.** The scenario's premise is that you have been away since Wednesday
17:30. `slack.md` showed "You" posting three times after that:

| Where | When | Message |
|---|---|---|
| `#product` | Thursday 10:20 | "I think so, unless design has the new one ready before Friday." |
| `#sales` | Friday 09:02 | "Great. Let me know if you need anything from me." |
| `#product` | Friday 10:08 | "Perfect, thanks." |

The third is the damaging one. Julia writes *"I'll take full ownership of the
launch email. @You no need to do anything there"* and **the user replies
"Perfect, thanks."** — acknowledging in the transcript the very fact the model is
supposed to reconstruct. `launch_email_julia` is worth 5 points plus a
false-action category plus a prohibited-action penalty, and the scenario handed
the answer over as something the user had already agreed to.

**Now.**

- Thursday 10:20 is reattributed to **Sam Rivera at 10:24**, who already speaks
  in that thread at 10:31. Julia's question still gets answered, so the stale
  "Release is still planned for Monday" context that Friday later overrides is
  preserved intact.
- Friday 09:02 is **removed**, and Noah's 09:17 reply loses its now-dangling
  "Will do." opener. His substantive line — "Legal still has a couple of details
  but nothing scary" — is untouched, because it is the soft signal that Friday
  16:18 escalates into the hard 11:00 deadline.
- Friday 10:08 is **removed**. Julia's 10:06 message stands alone.

**What deliberately stays.** The `@You` mention in Julia's 10:06 message. It is
addressed *to* the user and is how the user learns the email was reassigned; it
does not imply the user was present or that they responded.

No other source file was touched. Every rubric-bearing fact was checked to
survive the edit: the Monday-release stale context, Julia's ownership, the
Wednesday decision, 3.1%→4.4%, Pied Piper and Hooli, the board meeting, and the
pricing confidentiality instruction.

**Consequence.** The prompt hash changed, so the seven calibration runs
generated against `e19d123c` are no longer comparable and must be regenerated.

---

## Known rubric overlaps (reported, not changed)

These are scoring-design observations, not scenario defects. They are recorded
here so calibration is not surprised by them:

- **Friday conversion is scored twice.** `no_friday_conversion_claim`
  (data_reasoning, 3 pts) and `friday_conversion_unknown` (uncertainty, 3 pts)
  reward nearly the same behaviour, so one insight is worth 6 points.
- **The launch email is penalised three times.** Telling the user to write it
  triggers `launch_email_julia` = FAIL (-5), the `launch_email` false action
  (-2), and a `PROHIBITED_ACTION` global penalty (-10): 17 points for a single
  mistake.

Both are plausibly intentional — state, noise and prohibited action are
genuinely different axes — but they widen score variance, so expect a higher
standard deviation than the dimension weights alone suggest.
