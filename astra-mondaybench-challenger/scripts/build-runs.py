"""Turn the Codex challenger pack into MondayBench run files.

    python scripts/build-runs.py

Writes `runs/monday-00X/gpt-6-astra/run-00N.json` under this challenger
directory, in the harness's `BenchmarkRun` shape, from the responses and
per-run metadata the pack already carries.

## The rule this script follows

Every value the Codex runtime did not expose is written as **null**, never as a
number. `generation-summary.json` records temperature, top_p, caching, the
output ceiling, the model id, finish reason, request ids, TTFT, TTFA and
reasoning tokens as UNOBSERVABLE for all fifteen runs, so none of them appear
here as a figure. A zero would be a measurement; null is the absence of one.

What IS observable is carried through and kept together in
`provider_metadata.raw_usage` under `codex_runtime`: the runtime, the requested
model id, the configured reasoning effort, the Codex session usage counters as
Codex reported them, the thread id, host wall-clock latency with its semantics,
retries and the recorded tool-event count. These are Codex's own numbers, not
independently verified provider accounting, and the field says so.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT.parents[0]
sys.path.insert(0, str(REPO))

from mondaybench.schemas import (  # noqa: E402
    BenchmarkRun, RunEconomics, RunGeneration, RunModel, RunPerformance,
    RunProviderMetadata, RunReasoning, RunUsage,
)

SLUG = "gpt-6-astra"
DISPLAY = "GPT-6 Astra"
SCENARIOS = ["monday-001", "monday-002", "monday-003", "monday-004", "monday-005"]
BENCHMARK_VERSION = "1.0"


def unobservable(value):
    """UNOBSERVABLE and any string sentinel become None. Numbers pass through."""
    if isinstance(value, str):
        return None
    return value


def build(scenario_id: str, run_number: int) -> BenchmarkRun:
    meta = json.loads(
        (ROOT / "metadata" / scenario_id / f"run-{run_number:03d}.json")
        .read_text(encoding="utf-8")
    )
    response = (ROOT / "responses" / scenario_id / f"run-{run_number:03d}.txt") \
        .read_text(encoding="utf-8")

    codex_usage = meta.get("codex_usage") or {}
    runtime_block = {
        "runtime": meta.get("runtime"),
        "requested_model_id": meta.get("requested_model_id"),
        "resolved_model_id": unobservable(meta.get("model_id")),
        "reasoning_effort": meta.get("reasoning_effort"),
        "reasoning_effort_note": meta.get("reasoning_effort_note"),
        "codex_thread_id": meta.get("codex_thread_id"),
        "codex_usage": codex_usage,
        "codex_usage_note": "counters as Codex reported them, not independently "
                            "verified provider accounting",
        "latency_ms_host_wall_clock": meta.get("latency_ms"),
        "latency_semantics": meta.get("latency_semantics"),
        "retries": meta.get("retries"),
        "tools_used_by_candidate": meta.get("tools_used_by_candidate"),
        "tools_available_to_runtime": meta.get("tools_available_to_runtime"),
        "system_prompt_equivalence": meta.get("system_prompt_equivalence"),
        "qualification": meta.get("qualification"),
        "unobservable": [
            key for key in ("temperature", "top_p", "caching", "max_output_tokens",
                            "model_id", "finish_reason", "request_id", "response_id",
                            "TTFT", "TTFA", "reasoning_tokens",
                            "reasoning_delivery_state", "provider_truncation")
            if isinstance(meta.get(key), str) and meta[key].startswith("UNOBSERVABLE")
        ],
        "not_an_api_equivalent_run": True,
    }

    return BenchmarkRun(
        benchmark_version=BENCHMARK_VERSION,
        scenario_id=scenario_id,
        scenario_prompt_sha256=meta["scenario_prompt_sha256"],
        run_id=f"{scenario_id}__{SLUG}__{run_number:03d}",
        run_number=run_number,
        model=RunModel(slug=SLUG, display_name=DISPLAY, provider="codex",
                       model_id=meta.get("requested_model_id", SLUG)),
        generation=RunGeneration(
            temperature=unobservable(meta.get("temperature")),
            top_p=unobservable(meta.get("top_p")),
            max_output_tokens=unobservable(meta.get("max_output_tokens")),
            safety_ceiling_tokens=None,
            ceiling_semantics="unobservable: the runtime does not expose an "
                              "output ceiling",
            reasoning_enabled=True,
            reasoning_requested=True,
            reasoning_effort=meta.get("reasoning_effort"),
            system_prompt_sent=True,
            system_prompt_sha256=None,
            extra_body={},
            config_sha256=meta.get("config_sha256"),
        ),
        timestamp_utc=meta["timestamp"],
        usage=RunUsage(input_tokens=None, output_tokens=None, reasoning_tokens=None),
        performance=RunPerformance(ttft_ms=None, ttfa_ms=None,
                                   total_latency_ms=None, tokens_per_second=None),
        economics=RunEconomics(),
        reasoning=RunReasoning(
            requested=True,
            # The runtime reports no reasoning signal at all, which is exactly
            # what UNOBSERVABLE is for: an unreported signal is never read as
            # an absence of reasoning.
            status="UNOBSERVABLE",
            tokens=None,
            stream_observed=None,
            stream_event_count=None,
        ),
        response=response,
        finish_reason=unobservable(meta.get("finish_reason")),
        provider_metadata=RunProviderMetadata(
            request_id=unobservable(meta.get("request_id")),
            raw_usage={"codex_runtime": runtime_block},
        ),
    )


def main() -> int:
    written = 0
    for scenario_id in SCENARIOS:
        for run_number in (1, 2, 3):
            run = build(scenario_id, run_number)
            target = ROOT / "runs" / scenario_id / SLUG / f"run-{run_number:03d}.json"
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("wb") as fh:
                fh.write(run.model_dump_json(indent=2).encode("utf-8"))
            written += 1
            print(f"  {target.relative_to(ROOT).as_posix()}  "
                  f"{len(run.response)} chars  ceiling={run.generation.max_output_tokens}"
                  f"  temp={run.generation.temperature}")
    print(f"\nwrote {written} run files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
