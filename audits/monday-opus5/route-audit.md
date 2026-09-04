# Route audit: Claude Opus 5 against the frozen MondayBench suite

**Date:** 2026-09-02
**Requested model:** Claude Opus 5 (`claude-opus-5`)
**Scope:** all five frozen scenarios, 3 runs each
**Route status:** **OFFICIAL ROUTE UNAVAILABLE** → runs generated on the
Claude Code subscription route and classified
**PROVISIONAL / OFF-BENCHMARK / CLAUDE CODE ROUTE**

Raw evidence in this directory:

* `preflight-probes.json` — both gateways, through the harness's own adapter
* `prompt-verification.json` — all five frozen prompts, hashed three ways
* `prompt-<scenario>.txt` — the exact bytes sent
* `claude-code-wire-capture.json` — what the subscription route actually sends

---

## 1. The official route

MondayBench's official route is a direct streaming chat completion:

    mondaybench run → runner.py → build_model_provider()
                    → providers/openai_compatible.py → httpx → gateway

No tools, no repo context, no agent loop, no date injection, no auxiliary
calls. All seven published models were produced this way.

### `claude-opus-5` is on the allowlist, and it cannot be called

Enumerated live with `mondaybench endpoints`, then probed with a 16-token
completion through `OpenAICompatibleProvider` — the harness's own httpx client.

**Methodology note, carried over from the Fable 5.1 preflight and re-confirmed:**
a raw `urllib` probe of these endpoints returns Cloudflare `403 error code:
1010` for every model, including ones that work. That is client
fingerprinting, not model access, and it is not evidence. Probe through the
harness adapter or not at all.

    helmcode  claude-opus-5             500  credits_exhausted
              claude-opus-5-20260514    401  team_model_access_denied
              claude-opus-4-8           401  team_model_access_denied
              claude-opus-4-7           401  team_model_access_denied

    nan       claude-opus-5             401  auth_error

The 500 body is the decisive one, and it is explicit about the reason:

> Your organisation has no prepaid credit left. `claude-opus-5` is a
> third-party model billed per token from credits and is not covered by any
> subscription tier, so topping up is the only way to use it. Your own models
> and everything else your plan covers are unaffected.
> `type: credits_exhausted`

The 401 bodies enumerate the key's whole team allowlist, which is the useful
part — the server telling us what exists for us:

    ['qwen3.6', 'qwen3-embedding', 'kokoro', 'whisper', 'gemma4',
     'deepseek-v4-flash', 'rerank', 'claude-fable-5', 'claude-opus-5',
     'claude-sonnet-5', 'claude-haiku-4-5', 'gpt-5.6-sol', 'gpt-5.6-terra',
     'gpt-5.6-luna', 'gemini-3.6-flash', 'gemini-3.5-flash-lite', 'glm5.2']

Exactly one Opus id exists for this key: `claude-opus-5`. There is no dated
variant and no 4.x. So this is **not** a wrong-id problem — the same class of
finding as the `glm5.2` / `glm-5.2` note in `models.yaml`, where the allowlist
is authoritative over any doc page.

**This differs from the Fable 5.1 blockage and the difference matters.** Fable
5.1 was absent from the allowlist under all five spellings — the model was not
there. Opus 5 *is* there and is correctly named; what is missing is prepaid
credit. The gateway states plainly that plan-covered models are unaffected,
which is consistent with the header note in `models.yaml`: when the
organisation's credit ran out, only the third-party frontier models
(`claude-*`, `gpt-*`, `gemini-*`) failed.

### Route priority 1 — direct Anthropic API: closed by project rule

Verified, without printing any value: `ANTHROPIC_API_KEY`,
`ANTHROPIC_AUTH_TOKEN` and `ANTHROPIC_BASE_URL` are all unset.

This is not merely a missing key. `README.md` ("The judge"):

> **Do not set `ANTHROPIC_API_KEY` and do not spend Anthropic API credits on
> this project** — that is a hard project rule, not a preference.

So the direct API route is unavailable by policy, not by accident, and
`providers/anthropic_native.py` cannot be used to rescue this.

### Route priority 2 — any other direct completion route: none

Both configured endpoints were probed. Helmcode is credit-gated for this model;
NaN does not serve it to this key. There is no third endpoint.

### OpenCode — excluded, not tested

Already established for Fable 5.1: OpenCode 1.18.14 injects a large system
prompt, the current date, cwd/git/platform, skills/AGENTS, tools,
`tool_choice: auto` and auxiliary calls. It is not a valid MondayBench route
and was not probed again.

---

## 2. The Claude Code subscription route — what it actually sends

Hardened as far as the CLI allows:

    DISABLE_NON_ESSENTIAL_MODEL_CALLS=1 claude -p \
      --model claude-opus-5 \
      --system-prompt "You are a helpful assistant." \
      --tools "" --effort high \
      --output-format stream-json --include-partial-messages --verbose \
      --safe-mode --setting-sources "" --strict-mcp-config \
      --disable-slash-commands --no-session-persistence

Claude Code CLI 2.1.258, OAuth subscription auth, no `ANTHROPIC_API_KEY`.

Asked to echo everything it received byte for byte, the model returns:

### 2a. The system prompt is not the frozen bytes

    You are a Claude agent, built on Anthropic's Claude Agent SDK.You are a helpful assistant.

`--system-prompt` **prepends** rather than replaces. Every frozen scenario
declares the system prompt `"You are a helpful assistant."`, sha256
`75357d685f238b6afd7738be9786fdafde641eb6ca9a3be7471939715a68a4de`. What
reaches the model hashes to something else, so `system_prompt_sha256` cannot be
recorded truthfully as the frozen value.

### 2b. A `<system-reminder>` is injected into the user turn, carrying the real date

    <system-reminder>
    As you answer the user's questions, you can use the following context:
    # userEmail
    The user's email address is bperez@helmcode.com. ...
    # currentDate
    Today's date is 2026-09-02.
          IMPORTANT: this context may or may not be relevant to your tasks. ...
    </system-reminder>

The user turn is therefore not the frozen prompt bytes, and the injected
"today" contradicts every scenario's fictional clock. None of the seven
published models received anything like it. Measured effect on the runs
themselves is in `date-sensitivity.json`.

### 2c. The auxiliary Haiku call is NOT suppressed here

`DISABLE_NON_ESSENTIAL_MODEL_CALLS=1` is set, and `modelUsage` still contains a
`claude-haiku-4-5-20251001` line (960 input / 12 output tokens on the echo
probe). The Fable 5.1 audit recorded that this flag removed the auxiliary call;
on this route and this CLI build it does not.

It is a separate model on a separate call and does not enter the candidate's
context, so it does not change the response. It does mean the user's
"auxiliary model calls absent" check **fails**, and it means
`total_cost_usd` is not the candidate's cost. Each run record keeps the
per-model `modelUsage` breakdown so the `claude-opus-5` line can be read alone
in the later pricing audit.

### 2d. Recordable differences, none of them the reason this is off-benchmark

* `temperature` and `top_p` are neither settable nor observable. Note that
  `claude-opus-5` is already listed in
  `providers/anthropic_native.NO_TEMPERATURE_MODELS`, so the *official* adapter
  would also drop `temperature` and record it as unsupported. A null
  temperature is the honest record here, not a deviation.
* `--effort high` is sent and never echoed back: the canonical effort is
  requested and unverifiable.
* Route output ceiling is **64,000** tokens. monday-004 declares
  `safety_ceiling_tokens: 96000` and monday-005 declares `131072`, so those two
  scenarios cannot be run at their declared ceiling. Per-model ceilings already
  vary across the frozen battery, so this qualifies as a caveat *provided no
  run terminates on length* — checked per run via `stop_reason`.
* Context window reported as 1,000,000.
* No adapter exists in the harness for this transport. Generating through it
  would mean adding one, i.e. a harness change, so nothing under
  `mondaybench/` was touched and generation ran from a separate script.

---

## 3. Config equivalence

| Parameter | Official route | This route | Equivalent? |
|---|---|---|---|
| system prompt | frozen bytes, sha `75357d68…` | Agent SDK preamble prepended | **NO** |
| user prompt | frozen bytes only | frozen bytes + `<system-reminder>` | **NO** |
| temperature | `0` sent, dropped for claude-* by adapter | not settable, not observable | equal in effect |
| top_p | not sent | not settable | equal in effect |
| max output | 32,000 / 96,000 / 131,072 per scenario | 64,000 route ceiling | **NO** for 004, 005 |
| streaming | yes, TTFT measured | yes, TTFT/TTFA measured | yes |
| tools | absent | absent (`--tools ""`) | yes |
| tool_choice | absent | absent | yes |
| auxiliary calls | absent | **present** (`claude-haiku-4-5`) | **NO** |
| usage reporting | gateway usage block | route `usage` + `modelUsage` | richer, comparable |
| reasoning observability | provider counters | `thinking_tokens` | yes |

**Classification: `NON_EQUIVALENT`.**

Only `OFFICIAL_EQUIVALENT` may enter the official leaderboard, so these runs
may not. They are published, if at all, as a provisional off-benchmark result
with the route named.

---

## 4. A second, independent disqualifier: the candidate is the judge

This did not apply to Fable 5.1 and it applies here in full.

MondayBench's judge is **Claude Opus 5**, recorded rather than called
(`route: "recorded"` in every published evaluation; `evaluator-opus5-v0.1`
through `v0.5` all name `model_id: claude-opus-5`). The candidate under test is
`claude-opus-5`.

So the model grading the responses is the same model that produced them. The
instruction for this task was explicit — do not change the judge, and allow no
self-favouring adjustment — and that instruction has been followed: the frozen
judge prompts, rubrics and evaluator configs are used unchanged, and the
lower-label rule and the `factual_anchors` restriction were applied from the
first pass rather than discovered in audit.

But no amount of care inside the evaluation removes the structural fact. Even
on a hypothetical clean transport, an Opus 5 result judged by Opus 5 is not
comparable with seven models judged by a different model than produced them.
This is recorded here as a first-order caveat on the result, independent of the
route contamination, and it is the stronger of the two reasons the number must
not be read as a leaderboard entry.

---

## 5. Integrity

Nothing frozen was touched. Generation wrote only to
`experiments/opus-5-full-mondaybench/` and this audit directory. Verified
separately in `integrity.json`.
