"""Turn the Claude Opus 5 battery into MondayBench run files (suite v1.10).

    uv run python experiments/opus-5-full-mondaybench/build-runs.py

Writes `runs/monday-00N/claude-opus-5/run-00K.json` in the harness's
`BenchmarkRun` shape, from the fifteen raw generations in `raw/`, through the
harness's own writer (`mondaybench.runner.write_run`, exclusive mode, LF). A run
file that already exists is left alone if it is byte-identical to what this
script would write, and is a hard error otherwise - nothing is ever overwritten.

Modelled on `astra-mondaybench-challenger/scripts/build-runs.py` (commit
4d51bda), and it follows the same rule:

## Every value the route did not expose is written as null, never as a number

The battery ran through `claude -p` (Claude Code CLI 2.1.258, OAuth
subscription, effort high), not through this harness's provider adapter. What
that route does NOT expose, and is therefore null here:

* temperature and top_p - not settable on the route (and Opus 5 rejects
  temperature through the API as well);
* `max_output_tokens`, the value that reaches the wire as `max_tokens` - the
  battery never set one and the wire was not captured per run;
* the exact system prompt bytes as sent - the route PREPENDS the Agent SDK
  preamble to the requested "You are a helpful assistant.", so
  `system_prompt_sha256` is not the frozen 75357d68... and is not claimed;
* a provider request id, and per-run TTFT / TTFA / total latency in the
  harness's sense (see below).

What IS recorded, and where:

* `scenario_prompt_sha256` - the hash the generation script recorded for the
  bytes it passed to the route. It is checked here against the frozen hash
  the harness assembles today, and the script refuses to write on a mismatch.
  THE USER TURN AS DELIVERED WAS NOT THOSE BYTES: the route injects a
  `<system-reminder>` carrying the user's identity and `Today's date is
  2026-09-02` into the user turn (audits/monday-opus5/route-audit.md and
  claude-code-wire-capture.json). That is recorded on every run.
* `generation.safety_ceiling_tokens = 64000` - the output ceiling the route
  REPORTS for this model (`modelUsage.maxOutputTokens`). It was not set by this
  battery and it is not the scenario's configured ceiling (32,000 for
  monday-001..003, 96,000 for monday-004, 131,072 for monday-005). Recorded
  under the field that says what it is, with `ceiling_semantics` saying whose
  number it is; `max_output_tokens` stays null because nothing was observed on
  the wire.
* `usage` - the Anthropic `usage` block the route passes through. Anthropic's
  `input_tokens` EXCLUDES cached tokens, so `usage.input_tokens` here is
  input + cache_creation + cache_read (the split is kept in the runtime block).
  `output_tokens` includes thinking; `reasoning_tokens` is
  `usage.output_tokens_details.thinking_tokens`.
* `finish_reason` - the route's `stop_reason` (`end_turn` on all fifteen).
* Timings live in the runtime block, not in `performance`: they were measured
  on the host around the `claude -p` process (TTFT/TTFA from stream-json
  deltas), and the CLI's own `route_ttft_ms` differs from the host-measured one
  by more than a second. Neither is the adapter's measurement, so neither is
  published as one.
* Cost is not published: the route reports a list-price figure for a
  subscription call, which is not a price this battery paid. It stays in the
  runtime block.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))

from mondaybench.prompt_builder import build_prompt  # noqa: E402
from mondaybench.runner import run_path, write_run  # noqa: E402
from mondaybench.scenarios import load_scenario  # noqa: E402
from mondaybench.schemas import (  # noqa: E402
    BenchmarkRun, RunEconomics, RunGeneration, RunModel, RunPerformance,
    RunProviderMetadata, RunReasoning, RunUsage,
)

SLUG = "claude-opus-5"
DISPLAY = "Claude Opus 5"
PROVIDER = "claude-code"
MODEL_ID = "claude-opus-5"
SCENARIOS = ["monday-001", "monday-002", "monday-003", "monday-004", "monday-005"]
BENCHMARK_VERSION = "1.0"
CLI_VERSION = "2.1.258"
ROUTE_CEILING_SEMANTICS = (
    "route-reported, not configured by this battery: Claude Code reports "
    "maxOutputTokens 64000 for claude-opus-5 (modelUsage). The battery set no "
    "ceiling and the wire max_tokens was not captured, so max_output_tokens is "
    "null. This is NOT the scenario's configured ceiling (32000 for "
    "monday-001..003, 96000 for monday-004, 131072 for monday-005)."
)
USER_TURN_NOTE = (
    "NOT the frozen bytes as delivered: the route injects a <system-reminder> "
    "carrying the user's identity and 'Today's date is 2026-09-02' into the user "
    "turn. The frozen prompt bytes were what the battery passed to the route "
    "(sha256 recorded in scenario_prompt_sha256). See "
    "audits/monday-opus5/route-audit.md and claude-code-wire-capture.json."
)


def frozen_hashes() -> dict[str, str]:
    return {sid: build_prompt(load_scenario(sid)).sha256 for sid in SCENARIOS}


def config_fingerprint(raw: dict) -> str:
    """sha256 over the route configuration this raw file records.

    Everything that shapes the generation and is recorded identically for every
    run of the battery; nothing per-run (timestamps, session ids, usage).
    """
    shape = {
        "route": raw["route"],
        "cli_version": CLI_VERSION,
        "requested_model": raw["requested_model"],
        "system_prompt_requested": raw["system_prompt"],
        "cli_flags": raw["cli_flags"],
        "env": raw["env"],
        "route_max_output_tokens": raw["max_output_tokens"],
    }
    return hashlib.sha256(
        json.dumps(shape, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def build(scenario_id: str, run_number: int, expected_hash: str) -> BenchmarkRun:
    source = HERE / "raw" / f"{scenario_id}-run{run_number}.json"
    raw = json.loads(source.read_text(encoding="utf-8"))

    if raw["scenario"] != scenario_id or raw["run"] != run_number:
        raise SystemExit(f"{source}: records {raw['scenario']} run {raw['run']}")
    if raw["prompt_sha256"] != expected_hash:
        raise SystemExit(
            f"{source}: prompt {raw['prompt_sha256'][:12]} != frozen {expected_hash[:12]}"
        )
    if raw["served_model"] != MODEL_ID or raw["is_error"] or raw["num_turns"] != 1:
        raise SystemExit(f"{source}: served {raw['served_model']}, is_error {raw['is_error']}")

    usage = raw["usage"]
    thinking = (usage.get("output_tokens_details") or {}).get("thinking_tokens")
    total_input = (usage["input_tokens"] + usage["cache_creation_input_tokens"]
                   + usage["cache_read_input_tokens"])

    runtime_block = {
        "runtime": "Claude Code CLI",
        "cli_version": CLI_VERSION,
        "route": raw["route"],
        "route_classification_at_generation": raw["route_classification"],
        "cli_flags": raw["cli_flags"],
        "env": raw["env"],
        "requested_model_id": raw["requested_model"],
        "served_model_id": raw["served_model"],
        "served_model_provider": raw["provider"],
        "reasoning_effort": "high",
        "system_prompt_requested": raw["system_prompt"],
        "system_prompt_requested_sha256": raw["system_prompt_sha256"],
        "system_prompt_as_sent": raw["system_prompt_as_sent_note"],
        "user_turn_as_delivered": USER_TURN_NOTE,
        "temperature_note": raw["temperature_note"],
        "route_max_output_tokens": raw["max_output_tokens"],
        "route_context_window": raw["context_window"],
        "anthropic_usage": usage,
        "input_tokens_semantics": "usage.input_tokens above is EXCLUSIVE of cache; "
                                  "the run's usage.input_tokens is input + "
                                  "cache_creation + cache_read",
        "model_usage_all": raw["model_usage_all"],
        "auxiliary_models": raw["auxiliary_models"],
        "stop_reason": raw["stop_reason"],
        "terminal_reason": raw["terminal_reason"],
        "subtype": raw["subtype"],
        "is_error": raw["is_error"],
        "num_turns": raw["num_turns"],
        "session_id": raw["session_id"],
        "subagent_stats": raw["subagent_stats"],
        "timing_host_measured_ms": {
            "ttft": raw["ttft_ms"], "ttfa": raw["ttfa_ms"], "total": raw["latency_ms"],
        },
        "timing_route_reported_ms": {
            "ttft": raw["route_ttft_ms"], "ttfa": raw["route_ttfa_ms"],
            "duration_api": raw["duration_api_ms"],
        },
        "timing_semantics": "host wall clock around the claude -p process, TTFT/TTFA "
                            "from stream-json deltas; not the harness adapter's "
                            "measurement, so not published in `performance`",
        "cost_usd_route_reported": raw["cost_usd_route_reported"],
        "total_cost_usd_including_auxiliary": raw["total_cost_usd_including_auxiliary"],
        "cost_basis": raw["cost_basis"],
        "cost_note": "list-price figure the route reports for a subscription call; "
                     "not a price this battery paid, so `economics` is empty",
        "source_file": source.relative_to(REPO).as_posix(),
        "unobservable": ["temperature", "top_p", "max_output_tokens (wire)",
                         "system_prompt bytes as sent", "request_id"],
        "not_an_api_equivalent_run": True,
    }
    if scenario_id == "monday-004" and run_number == 1:
        runtime_block["generation_incident"] = (
            "This slot was generated twice by two concurrent processes; the later "
            "write survives and neither generation had been read or judged when it "
            "did. See experiments/opus-5-full-mondaybench/GENERATION-INCIDENT.md."
        )

    return BenchmarkRun(
        benchmark_version=BENCHMARK_VERSION,
        scenario_id=scenario_id,
        scenario_prompt_sha256=raw["prompt_sha256"],
        run_id=f"{scenario_id}__{SLUG}__{run_number:03d}",
        run_number=run_number,
        model=RunModel(slug=SLUG, display_name=DISPLAY, provider=PROVIDER, model_id=MODEL_ID),
        generation=RunGeneration(
            temperature=None,
            top_p=None,
            max_output_tokens=None,
            safety_ceiling_tokens=raw["max_output_tokens"],
            ceiling_semantics=ROUTE_CEILING_SEMANTICS,
            reasoning_enabled=True,
            reasoning_requested=True,
            reasoning_effort="high",
            system_prompt_sent=True,
            system_prompt_sha256=None,
            extra_body={},
            config_sha256=config_fingerprint(raw),
        ),
        timestamp_utc=raw["generated_at_utc"],
        usage=RunUsage(input_tokens=total_input, output_tokens=usage["output_tokens"],
                       reasoning_tokens=thinking),
        performance=RunPerformance(),
        economics=RunEconomics(),
        reasoning=RunReasoning(
            requested=True,
            status="DELIVERED" if thinking else "UNOBSERVABLE",
            tokens=thinking,
            evidence="explicit_reasoning_tokens" if thinking else None,
        ),
        response=raw["response_text"],
        finish_reason=raw["finish_reason"],
        provider_metadata=RunProviderMetadata(
            request_id=None,
            raw_usage={"claude_code_runtime": runtime_block},
        ),
    )


def write(run: BenchmarkRun) -> str:
    target = run_path(run.scenario_id, run.model.slug, run.run_number)
    if target.exists():
        expected = json.dumps(run.model_dump(), indent=2, ensure_ascii=False) + "\n"
        if target.read_text(encoding="utf-8") != expected:
            raise SystemExit(f"{target} exists and differs - refusing to overwrite")
        return "unchanged"
    write_run(run, exclusive=True)
    return "written"


def main() -> int:
    hashes = frozen_hashes()
    for scenario_id in SCENARIOS:
        for run_number in (1, 2, 3):
            run = build(scenario_id, run_number, hashes[scenario_id])
            raw_text = json.loads(
                (HERE / "raw" / f"{scenario_id}-run{run_number}.json").read_text(encoding="utf-8")
            )["response_text"]
            assert run.response.encode("utf-8") == raw_text.encode("utf-8")
            state = write(run)
            print(f"  {run.run_id}  {len(run.response):>6} chars  "
                  f"out={run.usage.output_tokens}  think={run.usage.reasoning_tokens}  {state}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
