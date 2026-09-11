# Astra via Codex

Candidate: `gpt-6-astra`. Runtime: Codex CLI using the existing ChatGPT sign-in. Reasoning effort: **medium (highest available)**, as requested by the user. This is a Codex challenger, not an API-equivalent MondayBench run.

## Canonical reference versus runtime observation

| Setting | MondayBench v1.0 reference | Astra/Codex observation |
|---|---|---|
| System instruction | You are a helpful assistant. | Requested through `model_instructions_file`; separation from all Codex system/developer context is UNOBSERVABLE. |
| Temperature | 0 | UNOBSERVABLE |
| top_p | Omitted | UNOBSERVABLE |
| Caching | false | UNOBSERVABLE |
| Output ceiling, 001–003 | 32000 | UNOBSERVABLE |
| Output ceiling, 004 | 96000 | UNOBSERVABLE |
| Output ceiling, 005 | 131072 | UNOBSERVABLE |
| Reasoning effort | Model-specific standard mode | Explicit CLI configuration: medium |
| Model selection | Challenger-specific | Explicit CLI selection: gpt-6-astra; exact backend identity UNOBSERVABLE |

The earlier API preflight remains historical provenance. It verifies the canonical inputs and API harness behavior; it is not evidence that Codex exposes the same controls. The earlier endpoint blocker and declined launch are superseded by the user's Codex execution authorization.

## Candidate isolation and tools

Each candidate is a separate `codex exec --ephemeral` process, with neither resume nor fork, its own empty working directory, user configuration ignored, and project documentation limited to zero bytes. The exact frozen rendered input is passed on stdin without a wrapper or appended benchmark context. The controller loads only scenario templates and declared sources during generation, not rubric or ground truth.

The same developer instruction in every session prohibits tools, agents, file inspection, browsing and command execution. Configurable shell, app, plugin, browser, computer-use, multi-agent and memory features are disabled. The full backend tool inventory is UNOBSERVABLE: disabling known families does not establish that no tool exists anywhere in the runtime. Candidate tool use is independently checked from the returned Codex item events. Neither this document nor any other challenger artifact is supplied to the candidate.

Codex may inject environment and system/developer context. Therefore the benchmark system instruction is requested, but exact system-prompt equivalence is not claimed. The candidate has no inherited conversation or previous candidate response.

## Raw response and telemetry conventions

The preserved response is the final `agent_message.text` JSON string encoded directly as UTF-8. No newline is added, and no text is edited. The CLI's `--output-last-message` file is separately retained as execution evidence because its serialization can add a terminal newline. Every canonical response has a SHA-256, with the event-to-file equality checked after generation.

Codex session usage counters are preserved verbatim in `codex_usage`; these can include input, cached input, cache-write input, output and reasoning-output counters. They describe what Codex reports, not independently verified provider accounting. A zero reasoning-output counter is not used to infer absence of reasoning. Reasoning delivery, provider request/response IDs, finish reason, TTFT and TTFA remain UNOBSERVABLE. `codex_thread_id` is a session identifier, not a provider request ID. Host wall-clock latency includes Codex startup and any infrastructure retry.

Warnings about experimental skill-discovery suppression or PowerShell shell snapshots are operational runtime warnings, not candidate tool execution or failed model answers.

No response is selected by quality. Completed text is retained regardless of correctness. Qualification concerns canonical input, declared Astra/medium configuration, independent session, normal completion and absence of recorded tool use. Unobservable runtime controls are not qualification failures for this user-authorized route. Provider truncation remains UNOBSERVABLE; a normal Codex completion is reported separately.
