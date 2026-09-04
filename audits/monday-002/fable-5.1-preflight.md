# Preflight: Claude Fable 5.1 against MondayBench #002 — BLOCKED

**Date:** 2026-09-02
**Requested model:** Claude Fable 5.1 (`claude-fable-5-1`)
**Scenario:** monday-002 "Moving Targets", frozen, rubric 0.2
**Outcome:** no route can carry the frozen conditions. Zero official runs
generated, zero leaderboard changes, nothing frozen touched.

Raw evidence, this directory:

* `fable-5.1-preflight-probes.json` — gateway route, first pass
* `fable-5.1-preflight-subscription-probes.json` — gateway re-verification and
  the subscription route

---

## What was asked

Add Claude Fable 5.1 to the monday-002 leaderboard under the frozen conditions:
same scenario, prompt, system prompt, rubric, evaluator, judge, qualification
rules, harness and 3 official runs. Resolve the real served model id first
rather than assuming Anthropic's official `claude-fable-5-1`.

Two routes exist. Neither works, for different reasons, and the second reason
is the more interesting one.

---

## Route 1 — the gateways. The model is not there.

`mondaybench endpoints`, then 1-token completions through the harness's own
adapter (`OpenAICompatibleProvider`, httpx). Re-verified live at
**2026-09-02T06:45:50Z**; unchanged from the first pass.

    helmcode  claude-fable-5-1             401  team_model_access_denied
              claude-fable-5.1             401  team_model_access_denied
              claude-fable-5-1-20260501    401  team_model_access_denied
              claude-fable-51              401  team_model_access_denied
              fable-5.1                    401  team_model_access_denied
              claude-fable-5               500  credits_exhausted

    nan       claude-fable-5-1             401  auth_error
              claude-fable-5               401  auth_error

The 401 body enumerates the key's whole team allowlist, which is the useful
part — the server telling us what exists for us. It contains `claude-fable-5`
and no 5.1 under any spelling. Same class of finding as the `glm5.2` /
`glm-5.2` note in `models.yaml`: the allowlist is authoritative over any doc
page.

`claude-fable-5` is on the allowlist and still returns:

    "Your organisation has no prepaid credit left. claude-fable-5 is a
     third-party model billed per token from credits and is not covered by any
     subscription tier, so topping up is the only way to use it."
     type: credits_exhausted

**A methodology note for whoever re-runs this.** A raw `urllib` probe of the
same endpoints returns Cloudflare `403 error code: 1010` for every model,
including ones that work. That is client fingerprinting, not model access, and
it is not evidence. Probe through the harness adapter or not at all.

---

## Route 2 — the subscription. The model is there; the conditions are not.

Fable 5.1 *is* reachable from the Claude Code subscription this project already
uses to run the recorded Opus 5 judge. That is genuinely new information, and it
is why this second pass exists. It does not get us an official run.

Hardened as far as the CLI allows:

    DISABLE_NON_ESSENTIAL_MODEL_CALLS=1 claude -p \
      --model claude-fable-5-1 \
      --system-prompt "You are a helpful assistant." \
      --tools "" --effort high --output-format json \
      --safe-mode --setting-sources "" --strict-mcp-config \
      --disable-slash-commands --no-session-persistence

That answers correctly (`17 * 23` gives `391`), and it is observable in ways the
gateway route is not — served model echoed as `claude-fable-5-1`, provider
`firstParty`, input/output/cache tokens, `thinking_tokens`, `stop_reason`, and
per-model `costUSD` at `costBasis: list`. Six integrity gates pass on this
route.

Three do not, and they are not cosmetic.

### 2a. The system prompt is not the frozen bytes

Asked to echo everything it received, the model returns:

    You are a Claude agent, built on Anthropic's Claude Agent SDK.You are a helpful assistant.

`--system-prompt` prepends rather than replaces. monday-002's frozen system
prompt is `"You are a helpful assistant."`, sha256
`75357d685f238b6afd7738be9786fdafde641eb6ca9a3be7471939715a68a4de`. What is
actually sent hashes to something else, so `system_prompt_sha256` cannot be
recorded truthfully as the frozen value.

### 2b. A `<system-reminder>` is injected into the user turn — carrying the wrong date

The same echo returns, inside the first user turn:

    <system-reminder>
    # userEmail
    The user's email address is bperez@helmcode.com. ...
    # currentDate
    Today's date is 2026-09-02.
    </system-reminder>

**This is the decisive finding.** monday-002 declares
`current_time: "2026-09-14T09:07:00+02:00"` — the scenario's fictional Monday.
The route injects a contradictory real date directly into the model's context.

monday-002 is a temporal-reasoning scenario. "Temporal supersession" is a
15-point dimension, and `schedule_feasibility`, `conditional_launch_timing` and
`launch_state` all turn on which facts have been superseded by when. Handing the
candidate a conflicting "today" attacks the exact dimension the scenario
measures. None of the seven published models received anything like it.

A fixed ~254 tokens of this residual context is present on every call
(261 input tokens for a 6-token system prompt plus a 1-token user turn).

### 2c. The escape hatch requires the one thing this project forbids

`--bare` / `CLAUDE_CODE_SIMPLE=1` is the mode that would strip all of the above.
It refuses OAuth by design:

    CLAUDE_CODE_SIMPLE=1 claude -p ...  ->  "Not logged in - Please run /login"

It requires `ANTHROPIC_API_KEY`, which is empty in `.env`, and spending
Anthropic API credit on this project is a hard rule (README, "The judge";
`.env.example` Option A) rather than a cost trade-off. So the contamination
cannot be removed on any route that reaches the model.

### 2d. Also true, and less severe than the above

* `temperature` and `top_p` are neither settable nor observable. For the Claude
  family the harness already documents that `temperature` is rejected outright
  (`providers/anthropic_native.py`, `NO_TEMPERATURE_MODELS` — which already
  lists `claude-fable-5`), so a null temperature would be the honest record
  rather than a violation. Not a blocker on its own.
* `--effort high` is sent but never echoed back, so the canonical effort is
  requested and unverifiable.
* The route ceiling is 64,000 output tokens against the model's 128,000 API
  maximum. Per-model ceilings already vary across the frozen battery (32,000 for
  qwen3.6, 96,000 for glm5.2), so this alone would qualify.
* An auxiliary `claude-haiku-4-5` call rides along by default and shows up in
  `total_cost_usd`. `DISABLE_NON_ESSENTIAL_MODEL_CALLS=1` removes it.
* No adapter exists in the harness for this transport. Generating a run through
  it would mean adding one — a harness change.

**Do not read 2d as the reason this is blocked.** Every item there is either
already normal in the frozen battery or recordable as a caveat. 2a and 2b are
what stop it.

---

## Integrity gates

| Gate | Route 1 (gateway) | Route 2 (subscription) |
|---|---|---|
| model reachable | **FAIL** 401 / credits | PASS |
| same scenario hash | n/a | PASS |
| same prompt hash | n/a | **FAIL** system-reminder injected into the user turn |
| same system prompt | n/a | **FAIL** Agent SDK preamble prepended |
| same rubric 0.2 | n/a | PASS |
| same evaluator `evaluator-opus5-v0.2` | n/a | PASS |
| same judge (recorded Opus 5) | n/a | PASS |
| same qualification logic | n/a | PASS |
| same harness | n/a | **FAIL** no adapter; agentic CLI, not a streaming completion |
| exactly 3 valid runs | **FAIL** 0 | **FAIL** 0 |
| single `config_sha256` | n/a | **FAIL** temperature/top_p neither sent nor observable |
| non-empty outputs | n/a | PASS |
| valid usage | n/a | PASS |
| `finish_reason` recorded | n/a | PASS |
| real model/provider verified | **FAIL** | PASS `claude-fable-5-1`, firstParty |
| reasoning observability | n/a | PASS `thinking_tokens`, adaptive |

Publication gate: **not met.** No result published.

---

## Reasoning / thinking, for the record

Classified against `mondaybench/reasoning.py`. Fable 5.1's thinking is
always-on and adaptive; there is no flag to set, so `reasoning_requested` would
come from `capabilities.reasoning` exactly as it does for every
OpenAI-compatible model in the battery.

Delivery *is* observable on route 2, by signal 1 —
`explicit_reasoning_tokens`, read off
`usage.output_tokens_details.thinking_tokens`. Observed 152 on the echo probe
and 0 on trivial arithmetic. Zero on an easy question is adaptive thinking
working as designed, not `NOT_DELIVERED`; the module's own MIMO v2.5 note covers
why a single counter reading is not a verdict.

No reasoning tokens were invented anywhere. The gateway route produced no
reasoning evidence at all because it produced no completions.

---

## Pricing, verified rather than quoted

$10.00 / 1M input, $50.00 / 1M output (`claude-api` skill, Current Models;
1M context, 128K max output, effort default `high`).

Cross-checked against the route's own accounting: 277 input + 3 output gives
`277/1e6*10 + 3/1e6*50 = 0.00292`, exactly the `costUSD` returned. The price
list and the meter agree.

**Projected cost of the 3 runs that were not generated,** from the observed
prompt size (2,164 estimated input tokens) and the battery's output range
(2.6k–33.7k tokens/run): roughly **$0.15–$1.70 per run**, so **$0.45–$5.10** for
three. Judging is recorded in-session as always and adds no API spend.

**Preflight spend, which is not charged to the benchmark:** about $0.0095 on the
CLI probes, plus one 35,221-token subagent probe. The gateway probes cost
nothing — every one was refused.

---

## What was NOT done, deliberately

* **No run was generated through route 2.** It would carry a conflicting date
  into a temporal-reasoning scenario. That is not a slightly-off run, it is
  evidence about a different question.
* **`claude-fable-5` was not substituted for 5.1.** Different models. A row
  labelled 5.1 carrying 5's weights is a misattribution nothing downstream could
  detect. It is also credit-blocked.
* **No entry was added to `models.yaml`.** A registration needs a `model_id`
  verified live against a route that can actually serve the frozen conditions.
* **No `runs/monday-002/…` directory was created.** An empty model directory
  misreports a campaign as started.
* **No adapter was added to the harness**, and nothing frozen was
  read-modified. `verify-release --version 1.0` reports every group `identical`;
  suite digest
  `c056b4b43d3caeb3b50394282b08ed281a5716fb1df68d1666abb950aa0b2a80`.

---

## What would unblock it

1. **Helmcode adds `claude-fable-5-1` to the team allowlist** *and* **prepaid
   credit is topped up.** Both, or neither buys anything: with credit but no
   allowlist entry the 401 stands, with the entry but no credit the 500 does.
   This is the only path that reaches the frozen conditions, because it is the
   only path where we control the system prompt and the request bytes.
2. **A CLI/SDK mode that keeps subscription auth and injects nothing.** Today
   `--bare` is that mode and it refuses OAuth. If that ever changes, route 2
   clears 2a and 2b, and the remaining 2d items become recordable caveats.

Nothing on our side is misconfigured. Re-run this preflight after either
change; `endpoints` must list the id and a 1-token completion must return 200
with the served model echoed before any official run is generated.
