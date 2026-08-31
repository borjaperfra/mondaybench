# glm5.2 — the 2026-08-31 gateway outage, and how it resolved

RESOLVED. glm5.2 has its three official monday-004 runs and the battery is
published. This file is the record of the outage that held it up, kept because
a serving interruption that gets deleted cannot be counted later.

| | |
|---|---|
| official runs | 3 — `run-003`, `run-004`, `run-005` |
| rejected | `run-001` — `max_output_tokens` 32000 != configured 96000 |
| blocked | 2026-08-30 → 2026-08-31, `run-005` could not be generated |
| resolved | 2026-08-31, no change on this side |

## What happened

`run-005` was attempted twice on 2026-08-31 and both attempts returned HTTP 402:

```
litellm.APIError: OpenrouterException -
  "This request requires more credits, or fewer max_tokens. You requested up
   to 96000 tokens, but can only afford 0."
  code 402, metadata.limit_source: "openrouter_credits"
```

Both failures are in `failed-attempts.jsonl`. No run file was written, so no
partial or invalid response could reach a score.

It then cleared on its own, with no configuration change in this repository, and
`run-005` generated normally: 30,104 output tokens, 23,421 of them reasoning,
`finish_reason: stop`, 326.3s.

## What was ruled out while it was down

| probe | result |
|---|---|
| `glm5.2` at `max_tokens` 96000 / 32000 / 8000 / **16** | 402 at every budget |
| `gemma4`, `qwen3.6`, `deepseek-v4-flash` (helmcode) | 200, answered normally |
| `glm-5.2` (the id Helmcode's docs use) | 401 `team_model_access_denied` |

- **Not the safety ceiling.** The affordable budget was *zero*, so a 16-token
  request failed exactly like a 96,000-token one. Lowering
  `generation.safety_ceiling_tokens` would have bought nothing and would have
  invalidated the two runs that already qualified.
- **Not Helmcode being down.** It served its other three models throughout.
- **Not a wrong model id, and not an access problem.** The 401 body for
  `glm-5.2` enumerates this key's team allowlist, and `glm5.2` is in it while
  `glm-5.2` is not. The id in `models.yaml` is the one this team is entitled to
  call, which is also why no id change was attempted.

## What is NOT established

Helmcode states that GLM is served from their own inference, not OpenRouter.
A client cannot see past the gateway to confirm or refute that: `/model/info`
and `/model_group/info` return 404 and the 402 carried no routing headers.

One observation, recorded as an observation and not a conclusion: on Helmcode,
`glm5.2` and `deepseek-v4-flash` return OpenRouter-style `gen-…` request ids and
are the two models here with per-token pricing, while the plan-covered `gemma4`
and `qwen3.6` return `chatcmpl-…`. `deepseek-v4-flash` never hit a 402.

## Consequence for the published result

None for comparability. `run-005` was generated under the same configuration as
every other monday-004 run — same prompt hash
`3a0cbb56`, same 96,000 ceiling, same provider `helmcode`, `temperature: 0`,
`caching: false` — and `qualify_run` accepts it on all of them. The only thing
the outage cost was a day.

`run-005` is the slowest of the three at 326.3s against the model's 103.1s
median, but that is NOT an after-effect of the outage and should not be read as
one. It tracks output volume, which for this model varies enormously:

| run | output tokens | reasoning | total |
|---|---:|---:|---:|
| run-001 (rejected, 2026-08-29, before the outage) | 30,288 | 25,652 | 237.3s |
| run-003 | 4,931 | 2,019 | 60.9s |
| run-004 | 8,697 | 4,915 | 103.1s |
| run-005 | 30,104 | 23,421 | 326.3s |

run-001 was generated two days before the outage and sits in the same place as
run-005 on both volume and latency. glm5.2 sometimes spends six times as many
tokens on this prompt as at other times, at a fixed `temperature: 0`, and that
spread - not the endpoint - is what the latency follows. It is also why the
model's TTFA and total are published as medians beside the score rather than
folded into it.
