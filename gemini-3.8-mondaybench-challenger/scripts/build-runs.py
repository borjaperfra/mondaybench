"""Turn the Gemini 3.8 Flash (High) challenger pack into MondayBench run files.

    uv run python gemini-3.8-mondaybench-challenger/scripts/build-runs.py

Writes `runs/monday-00N/gemini-3-8-flash-high/run-00K.json` (suite v1.10) in the
harness's `BenchmarkRun` shape, through the harness's own writer
(`mondaybench.runner.write_run`, exclusive mode, LF). An existing run file is
left alone if byte-identical to what this script would write and is a hard
error otherwise. Reads this pack only; moves and edits nothing in it (its other
scripts hardcode its path).

Modelled on `astra-mondaybench-challenger/scripts/build-runs.py` (commit
4d51bda), and it follows the same rule: every value the route did not expose is
written as null, never as a number.

## The route

Antigravity Language Server `ide-2.4.5`, Connect-RPC `GetModelResponse`. The
request carries two fields - `prompt` and `model` (`MODEL_PLACEHOLDER_M318`) -
and the response carries one, the answer text (`audits/route-preflight.md`).

What that means for each field here:

* `scenario_prompt_sha256` - the battery verified all five assembled prompts
  against the frozen hashes before generating, and sent exactly that string as
  `prompt`. Re-checked here against the hash the harness assembles today.
* NO system prompt was sent: the RPC has no field for one, and the backend
  applies Google-side instructions that cannot be inspected. So
  `system_prompt_sent` is false and `system_prompt_sha256` is null.
* temperature, top_p, the served model id, token usage, reasoning tokens, TTFT
  and TTFA - not in the RPC schema; null.
* `max_output_tokens` / `safety_ceiling_tokens` - null. The IDE model registry
  lists 65,536, but it is not transmitted, and the backend applies its own.
* `finish_reason` - null. The pack's metadata says `stop`, but that value was
  computed by the generation script from a character-count heuristic
  (`len(response) >= 65536 * 4` -> "length", else "stop"); the route returns no
  finish reason. The heuristic and its result are kept in the runtime block.
* Latency is the host wall clock of one non-streaming RPC round trip; it is
  kept in the runtime block, not in `performance`, because it is not the
  adapter's streaming measurement.
* Reasoning was configured (registry `thinkingBudget: -1`, labelled High) but
  the route reports no reasoning signal, so the status is UNOBSERVABLE - which
  does not disqualify, by the harness's own rule.

`config_sha256` is the sha256 of `config/model-config.json`, the configuration
the pack froze before run 1 (the same value its generation-freeze-manifest
records).
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

PACK = Path(__file__).resolve().parent.parent
REPO = PACK.parent
sys.path.insert(0, str(REPO))

from mondaybench.prompt_builder import build_prompt  # noqa: E402
from mondaybench.runner import run_path, write_run  # noqa: E402
from mondaybench.scenarios import load_scenario  # noqa: E402
from mondaybench.schemas import (  # noqa: E402
    BenchmarkRun, RunEconomics, RunGeneration, RunModel, RunPerformance,
    RunProviderMetadata, RunReasoning, RunUsage,
)

SLUG = "gemini-3-8-flash-high"
DISPLAY = "Gemini 3.8 Flash (High)"
PROVIDER = "antigravity"
MODEL_ID = "gemini-3.8-flash-high"
SCENARIOS = ["monday-001", "monday-002", "monday-003", "monday-004", "monday-005"]
BENCHMARK_VERSION = "1.0"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build(scenario_id: str, run_number: int, expected_hash: str,
          config: dict, config_sha: str) -> BenchmarkRun:
    stem = f"run-{run_number:03d}"
    meta = json.loads((PACK / "metadata" / scenario_id / f"{stem}.json").read_text(encoding="utf-8"))
    response_bytes = (PACK / "responses" / scenario_id / f"{stem}.txt").read_bytes()
    raw_bytes = (PACK / "raw" / scenario_id / f"{stem}.json").read_bytes()
    raw = json.loads(raw_bytes.decode("utf-8"))
    response = response_bytes.decode("utf-8")

    problems = []
    if meta["scenario_id"] != scenario_id or meta["run_number"] != run_number:
        problems.append(f"metadata names {meta['scenario_id']} run {meta['run_number']}")
    if meta["prompt_sha256"] != expected_hash:
        problems.append(f"prompt {meta['prompt_sha256'][:12]} != frozen {expected_hash[:12]}")
    if sha256_bytes(response_bytes) != meta["response_sha256"]:
        problems.append("response file does not match its recorded sha256")
    if sha256_bytes(raw_bytes) != meta["raw_sha256"]:
        problems.append("raw envelope does not match its recorded sha256")
    if raw.get("response", "").encode("utf-8") != response_bytes:
        problems.append("response file differs from the raw envelope's response")
    if meta["status"] != "COMPLETED" or meta["error_status"] is not None:
        problems.append(f"status {meta['status']}")
    if problems:
        raise SystemExit(f"{scenario_id}/{stem}: " + "; ".join(problems))

    runtime_block = {
        "runtime": "Antigravity Language Server",
        "language_server_version": meta["language_server_version"],
        "rpc": "exa.language_server_pb.LanguageServerService/GetModelResponse",
        "request_fields": ["prompt", "model"],
        "requested_model_id": meta["requested_model_id"],
        "raw_model_identifier": meta["raw_model_identifier"],
        "served_model_id": None,
        "platform": meta["platform"],
        "model_provider": meta["provider"],
        "session_isolation": meta["session_isolation"],
        "route_equivalence_classification": config["route_equivalence_classification"],
        "system_prompt": "none sent: the RPC has no system-prompt field; backend-managed "
                         "Google instructions apply and cannot be inspected",
        "thinking_budget": config["thinking_budget"],
        "thinking_budget_label": config["thinking_budget_label"],
        "ide_registry_max_output_tokens": config["max_output_tokens"],
        "ide_registry_max_output_tokens_note": "registry value; not transmitted on the "
                                               "wire, the backend applies its own ceiling",
        "tool_status": config["tool_status"],
        "conversation_status": config["conversation_status"],
        "web_access_status": config["web_access_status"],
        "started_at": meta["started_at"],
        "finished_at": meta["finished_at"],
        "latency_ms_host_wall_clock": meta["latency_ms"],
        "latency_semantics": "host wall clock of one non-streaming RPC round trip",
        "pack_finish_reason": meta["finish_reason"],
        "pack_truncation_status": meta["truncation_status"],
        "pack_finish_reason_semantics": "computed by the generation script from a "
                                        "character-count heuristic (>= 65536*4 chars -> "
                                        "length), not returned by the route",
        "response_sha256": meta["response_sha256"],
        "raw_envelope_sha256": meta["raw_sha256"],
        "source_files": {
            "metadata": f"gemini-3.8-mondaybench-challenger/metadata/{scenario_id}/{stem}.json",
            "response": f"gemini-3.8-mondaybench-challenger/responses/{scenario_id}/{stem}.txt",
            "raw": f"gemini-3.8-mondaybench-challenger/raw/{scenario_id}/{stem}.json",
        },
        "pack_run_id": meta["run_id"],
        "unobservable": ["temperature", "top_p", "served_model_id", "system_prompt",
                         "max_output_tokens", "finish_reason", "request_id", "usage",
                         "reasoning_tokens", "TTFT", "TTFA"],
        "not_an_api_equivalent_run": True,
    }

    return BenchmarkRun(
        benchmark_version=BENCHMARK_VERSION,
        scenario_id=scenario_id,
        scenario_prompt_sha256=meta["prompt_sha256"],
        run_id=f"{scenario_id}__{SLUG}__{run_number:03d}",
        run_number=run_number,
        model=RunModel(slug=SLUG, display_name=DISPLAY, provider=PROVIDER, model_id=MODEL_ID),
        generation=RunGeneration(
            temperature=None,
            top_p=None,
            max_output_tokens=None,
            safety_ceiling_tokens=None,
            ceiling_semantics="unobservable: not transmitted on the route; the IDE "
                              "registry lists 65536 and the backend applies its own",
            reasoning_enabled=True,
            reasoning_requested=True,
            reasoning_effort=config["thinking_budget_label"],
            system_prompt_sent=False,
            system_prompt_sha256=None,
            extra_body={},
            config_sha256=config_sha,
        ),
        timestamp_utc=meta["started_at"],
        usage=RunUsage(),
        performance=RunPerformance(),
        economics=RunEconomics(),
        reasoning=RunReasoning(requested=True, status="UNOBSERVABLE"),
        response=response,
        finish_reason=None,
        provider_metadata=RunProviderMetadata(
            request_id=None,
            raw_usage={"antigravity_runtime": runtime_block},
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
    config_path = PACK / "config" / "model-config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config_sha = sha256_bytes(config_path.read_bytes())
    freeze = json.loads((PACK / "generation-freeze-manifest.json").read_text(encoding="utf-8"))
    if freeze["model_config_sha256"] != config_sha:
        raise SystemExit("model-config.json no longer matches the generation freeze manifest")

    for scenario_id in SCENARIOS:
        expected_hash = build_prompt(load_scenario(scenario_id)).sha256
        for run_number in (1, 2, 3):
            run = build(scenario_id, run_number, expected_hash, config, config_sha)
            state = write(run)
            print(f"  {run.run_id}  {len(run.response):>6} chars  {state}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
