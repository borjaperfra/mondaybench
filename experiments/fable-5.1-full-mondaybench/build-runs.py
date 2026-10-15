"""Turn the Claude Fable 5.1 battery into MondayBench run files (suite v1.10).

    uv run python experiments/fable-5.1-full-mondaybench/build-runs.py

Writes `runs/monday-00N/claude-fable-5-1/run-00K.json` in the harness's
`BenchmarkRun` shape through the harness's own writer
(`mondaybench.runner.write_run`, exclusive mode, LF). An existing run file is
left alone if byte-identical to what this script would write and is a hard error
otherwise - nothing is ever overwritten.

## Where the fifteen responses come from

* monday-001, 003, 004, 005: `raw/monday-00N-runK.json` in this directory.
* monday-002: the three FROZEN arms of `../fable-5.1-date-sensitivity/`:
  `run-A-frozen.json` -> run 1, `run-A2-frozen.json` -> run 2,
  `run-A3-frozen.json` -> run 3 (that is also their generation order).
  `run-B-neutralized.json` is NOT part of the battery: it was sent a different
  prompt (149 bytes prepended, sha256 31e9a9d2...) and is never read here.

A SOURCE DEFECT, recorded rather than repaired: every file in `raw/` carries
`scenario_id: "monday-002"` whatever scenario it holds. The scenario is taken
from the file name and is cross-checked against the file's own `label`,
`prompt_file` and `prompt_sha256`, which all agree with the name; the script
refuses to write if any of them disagree.

## The rule this script follows (as Astra's build-runs.py, commit 4d51bda)

Every value the route did not expose is written as null, never as a number.
The battery ran through `claude -p` (Claude Code CLI 2.1.258, OAuth
subscription, effort high, adaptive thinking), not this harness's adapter:

* temperature and top_p - not settable on the route; null.
* `max_output_tokens` (the wire `max_tokens`) - never set by the battery and
  not captured; null. The route REPORTS a 64,000-token output ceiling for this
  model (`generation.route_max_output_tokens`), which is recorded as
  `safety_ceiling_tokens` with `ceiling_semantics` saying whose number it is and
  that it is not the scenario's configured ceiling.
* the system prompt bytes as sent - the route prepends the Agent SDK preamble
  to the requested "You are a helpful assistant."; `system_prompt_sha256` null.
* the user turn as delivered - the route injects a `<system-reminder>` with the
  user's identity and `Today's date is 2026-09-02`. `scenario_prompt_sha256` is
  the hash of the bytes the battery passed to the route, checked here against
  the frozen hash; the injection is recorded on every run.
* no provider request id; timings and the route-reported list-price cost are
  kept in the runtime block, not in `performance` / `economics`, because they
  are host measurements around the CLI process and a list figure for a
  subscription call, not the adapter's measurements or a price paid.

`usage.input_tokens` is input + cache_creation + cache_read (Anthropic's
`input_tokens` excludes cache); `reasoning_tokens` is the route's
`thinking_tokens`.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
DATE_SENSITIVITY = REPO / "experiments" / "fable-5.1-date-sensitivity"
sys.path.insert(0, str(REPO))

from mondaybench.prompt_builder import build_prompt  # noqa: E402
from mondaybench.runner import run_path, write_run  # noqa: E402
from mondaybench.scenarios import load_scenario  # noqa: E402
from mondaybench.schemas import (  # noqa: E402
    BenchmarkRun, RunEconomics, RunGeneration, RunModel, RunPerformance,
    RunProviderMetadata, RunReasoning, RunUsage,
)

SLUG = "claude-fable-5-1"
DISPLAY = "Claude Fable 5.1"
PROVIDER = "claude-code"
MODEL_ID = "claude-fable-5-1"
SCENARIOS = ["monday-001", "monday-002", "monday-003", "monday-004", "monday-005"]
BENCHMARK_VERSION = "1.0"
CLI_VERSION = "2.1.258"

# monday-002's three frozen arms, in generation order. B_NEUTRALIZED is absent
# on purpose.
MONDAY_002 = {
    1: ("run-A-frozen.json", "RUN_A_FROZEN"),
    2: ("run-A2-frozen.json", "RUN_A2_FROZEN"),
    3: ("run-A3-frozen.json", "RUN_A3_FROZEN"),
}
CEILING_SEMANTICS = (
    "route-reported, not configured by this battery: Claude Code reports a "
    "64000-token output ceiling for claude-fable-5-1. The battery set no ceiling "
    "and the wire max_tokens was not captured, so max_output_tokens is null. This "
    "is NOT the scenario's configured ceiling (32000 for monday-001..003, 96000 "
    "for monday-004, 131072 for monday-005)."
)
USER_TURN_NOTE = (
    "NOT the frozen bytes as delivered: the route injects a <system-reminder> "
    "carrying the user's identity and 'Today's date is 2026-09-02' into the user "
    "turn. The frozen prompt bytes were what the battery passed to the route "
    "(sha256 recorded in scenario_prompt_sha256). See "
    "audits/monday-002/fable-5.1-preflight.md."
)
SYSTEM_PROMPT_NOTE = (
    "NOT the frozen bytes: the route prepends the Agent SDK preamble to the "
    "requested system prompt."
)


def source_for(scenario_id: str, run_number: int) -> tuple[Path, str]:
    if scenario_id == "monday-002":
        name, label = MONDAY_002[run_number]
        return DATE_SENSITIVITY / name, label
    return (HERE / "raw" / f"{scenario_id}-run{run_number}.json",
            f"M{scenario_id[-3:]}_RUN{run_number}")


def config_fingerprint(raw: dict) -> str:
    """sha256 over the route configuration the raw file records - identical for
    every run of the battery, nothing per-run."""
    shape = {
        "route": raw["route"],
        "requested_model": raw["model"]["requested"],
        "generation": raw["generation"],
    }
    return hashlib.sha256(
        json.dumps(shape, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def build(scenario_id: str, run_number: int, expected_hash: str) -> BenchmarkRun:
    source, label = source_for(scenario_id, run_number)
    raw = json.loads(source.read_text(encoding="utf-8"))

    problems = []
    if raw["label"] != label:
        problems.append(f"label {raw['label']} != {label}")
    if raw["prompt_sha256"] != expected_hash:
        problems.append(f"prompt {raw['prompt_sha256'][:12]} != frozen {expected_hash[:12]}")
    expected_prompt_file = ("monday002_frozen.txt" if scenario_id == "monday-002"
                            else f"{scenario_id}.txt")
    if raw["prompt_file"] != expected_prompt_file:
        problems.append(f"prompt_file {raw['prompt_file']}")
    if raw["model"]["served"] != MODEL_ID or raw["is_error"] or raw["num_turns"] != 1:
        problems.append(f"served {raw['model']['served']}, is_error {raw['is_error']}")
    if problems:
        raise SystemExit(f"{source}: " + "; ".join(problems))

    usage = raw["usage"]
    thinking = usage.get("thinking_tokens")
    total_input = (usage["input_tokens"] + usage["cache_creation_input_tokens"]
                   + usage["cache_read_input_tokens"])

    runtime_block = {
        "runtime": "Claude Code CLI",
        "cli_version": CLI_VERSION,
        "route": raw["route"],
        "cli_invocation": "documented in experiments/fable-5.1-full-mondaybench/"
                          "METHODOLOGY.md (not recorded per run)",
        "requested_model_id": raw["model"]["requested"],
        "served_model_id": raw["model"]["served"],
        "served_model_provider": raw["model"]["provider"],
        "generation_as_recorded": raw["generation"],
        "reasoning_effort": raw["generation"]["effort_requested"],
        "system_prompt_as_sent": SYSTEM_PROMPT_NOTE,
        "user_turn_as_delivered": USER_TURN_NOTE,
        "route_max_output_tokens": raw["generation"]["route_max_output_tokens"],
        "usage_as_recorded": usage,
        "input_tokens_semantics": "usage_as_recorded.input_tokens is EXCLUSIVE of "
                                  "cache; the run's usage.input_tokens is input + "
                                  "cache_creation + cache_read",
        "finish_reason": raw["finish_reason"],
        "is_error": raw["is_error"],
        "num_turns": raw["num_turns"],
        "timing_host_measured_ms": raw["performance"],
        "timing_semantics": "host wall clock around the claude -p process, TTFT/TTFA "
                            "from stream-json deltas; not the harness adapter's "
                            "measurement, so not published in `performance`",
        "economics_as_recorded": raw["economics"],
        "cost_note": "list-price figure the route reports for a subscription call; "
                     "not a price this battery paid, so `economics` is empty",
        "source_file": source.relative_to(REPO).as_posix(),
        "source_label": raw["label"],
        "unobservable": ["temperature", "top_p", "max_output_tokens (wire)",
                         "system_prompt bytes as sent", "request_id"],
        "not_an_api_equivalent_run": True,
    }
    if raw.get("scenario_id") != scenario_id:
        runtime_block["source_scenario_id_field"] = (
            f"the source file records scenario_id {raw.get('scenario_id')!r}; its label, "
            f"prompt_file and prompt_sha256 all say {scenario_id}, which is used"
        )
    if scenario_id == "monday-002":
        runtime_block["battery_note"] = (
            "a frozen arm of experiments/fable-5.1-date-sensitivity/; the "
            "date-neutralised arm B_NEUTRALIZED is not part of this battery"
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
            safety_ceiling_tokens=raw["generation"]["route_max_output_tokens"],
            ceiling_semantics=CEILING_SEMANTICS,
            reasoning_enabled=True,
            reasoning_requested=True,
            reasoning_effort=raw["generation"]["effort_requested"],
            system_prompt_sent=True,
            system_prompt_sha256=None,
            extra_body={},
            config_sha256=config_fingerprint(raw),
        ),
        timestamp_utc=raw["timestamp_utc"],
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
        response=raw["response"],
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
    for scenario_id in SCENARIOS:
        expected_hash = build_prompt(load_scenario(scenario_id)).sha256
        for run_number in (1, 2, 3):
            run = build(scenario_id, run_number, expected_hash)
            source, _ = source_for(scenario_id, run_number)
            original = json.loads(source.read_text(encoding="utf-8"))["response"]
            assert run.response.encode("utf-8") == original.encode("utf-8")
            state = write(run)
            print(f"  {run.run_id}  {len(run.response):>6} chars  "
                  f"out={run.usage.output_tokens}  think={run.usage.reasoning_tokens}  "
                  f"<- {source.relative_to(REPO).as_posix()}  {state}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
