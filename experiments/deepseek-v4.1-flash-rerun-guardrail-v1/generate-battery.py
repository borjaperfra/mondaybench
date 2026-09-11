"""Generate the treatment battery: 5 scenarios x 3 independent runs.

The path is the canonical one and nothing else - `load_scenario`,
`apply_endpoint_overrides`, `build_prompt`, `execute_run` - which is what
`mondaybench run` calls and what the control battery went through. The single
thing this script does that the CLI cannot is pass `root`, so the runs land under
this experiment directory rather than the repository's `runs/` tree; no official
artifact is touched.

`apply_system_prompt` inside `execute_run` swaps the harness default for the
frozen guardrail because the slug declares `system_prompt_file`. That is the one
variable. Everything else - endpoint, model id, temperature, ceilings, caching
flag, absence of reasoning_effort, absence of tools, streaming, retry semantics -
is resolved from the same configuration the control used and was checked field by
field before this script was allowed to run.

Each call is a fresh single-turn request: one system message, one user message.
No conversation state carries between runs, no run sees another run's output, no
best-of-N, and the only retries are the harness's own transient-failure retries.
A weak answer is a result and is kept.

    python experiments/deepseek-v4.1-flash-rerun-guardrail-v1/generate-battery.py [--dry-run] [scenario ...]
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
sys.path.insert(0, str(REPO))

from mondaybench.config import (  # noqa: E402
    apply_endpoint_overrides, endpoint_overrides_for, load_models)
from mondaybench.prompt_builder import build_prompt  # noqa: E402
from mondaybench.providers import ProviderError  # noqa: E402
from mondaybench.runner import (  # noqa: E402
    apply_system_prompt, dry_run_report, execute_run, log_failed_attempt)
from mondaybench.scenarios import load_scenario  # noqa: E402

MODEL = "deepseek-v4.1-flash-rerun-guardrail-v1"
ALL_SCENARIOS = ["monday-001", "monday-002", "monday-003", "monday-004", "monday-005"]
RUNS_PER_SCENARIO = 3
EXPECTED_SYSTEM_SHA = "eb136804970c72fa214521a341fdde95294393990fae0a5e86bd15614794653d"


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%H:%M:%S")


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    scenarios = args or ALL_SCENARIOS
    dry = "--dry-run" in sys.argv
    failures, retries_log = 0, []

    # Refuse to proceed before the control check has run and said so.
    check = ROOT / "pre-generation-control-check.json"
    if not check.exists():
        print("STOP: pre-generation-control-check.json is absent")
        return 2
    verdict = json.loads(check.read_text(encoding="utf-8"))["verdict"]
    if verdict != "PROCEED":
        print(f"STOP: control check verdict is {verdict}")
        return 2

    for scenario_id in scenarios:
        scenario = load_scenario(scenario_id)
        models = apply_endpoint_overrides(load_models(), endpoint_overrides_for(scenario_id))
        model = models[MODEL]
        prompt = build_prompt(scenario)
        sent = apply_system_prompt(prompt, model)

        import hashlib
        sha = hashlib.sha256(sent.system_prompt.encode("utf-8")).hexdigest()
        if sha != EXPECTED_SYSTEM_SHA:
            print(f"STOP: {scenario_id} system prompt sha {sha} != expected")
            return 2

        if dry:
            report = dry_run_report(scenario, model, prompt)
            print(f"===== {scenario_id} (dry run)")
            for key in ("model_id", "provider", "temperature", "max_output_tokens",
                        "ceiling_semantics", "reasoning_enabled", "prompt_sha256"):
                print(f"  {key}: {report[key]}")
            print(f"  system_prompt_sha256: {sha}")
            print(f"  system_prompt_bytes: {len(sent.system_prompt.encode('utf-8'))}")
            continue

        print(f"===== {scenario_id} {stamp()}  ceiling={scenario.safety_ceiling_tokens}", flush=True)
        for run_number in range(1, RUNS_PER_SCENARIO + 1):
            try:
                run = execute_run(scenario=scenario, model=model,
                                  run_number=run_number, prompt=prompt, root=ROOT)
            except ProviderError as exc:
                failures += 1
                log_failed_attempt(scenario_id=scenario_id, model_slug=MODEL,
                                   run_number=run_number, error=str(exc),
                                   kind="provider_error", root=ROOT)
                retries_log.append({"scenario_id": scenario_id, "run_number": run_number,
                                    "kind": "provider_error", "error": str(exc)[:400]})
                print(f"FAIL run {run_number}: {str(exc)[:200]}", flush=True)
                continue
            print(f"ok   run {run_number}  reas={run.reasoning.tokens} "
                  f"out={run.usage.output_tokens}  "
                  f"{run.performance.total_latency_ms/1000:.0f}s  {run.finish_reason}",
                  flush=True)
        print(f"----- {scenario_id} done {stamp()}", flush=True)

    if not dry:
        path = ROOT / "infrastructure-failures.json"
        existing = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
        path.write_bytes((json.dumps(existing + retries_log, indent=2,
                                     ensure_ascii=False) + "\n").encode("utf-8"))
    print("DRY RUN DONE" if dry else f"GENERATION DONE ({failures} infrastructure failures)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
