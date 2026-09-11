"""Generate the reliability-prompt battery: 5 scenarios x 3 independent runs.

Uses the canonical MondayBench path and nothing else - `load_scenario`,
`apply_endpoint_overrides`, `build_prompt`, `execute_run` - which is exactly what
`mondaybench run` calls. The one thing this script does that the CLI cannot is
pass `root`, so the runs land under this experiment directory instead of the
repository's `runs/` tree. Nothing here reaches a leaderboard.

Each call is a fresh single-turn request: one system message, one user message.
No conversation state carries between runs, no run sees another run's output, no
best-of-N, and the only retries are the harness's own transient-failure retries
(`MAX_ATTEMPTS` in runner.py). A weak answer is a result and is kept.

    uv run python experiments/deepseek-v4.1-flash-reliability-v1/generate-battery.py [--dry-run]
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from mondaybench.config import (  # noqa: E402
    apply_endpoint_overrides,
    endpoint_overrides_for,
    load_models,
)
from mondaybench.prompt_builder import build_prompt  # noqa: E402
from mondaybench.providers import ProviderError  # noqa: E402
from mondaybench.runner import (  # noqa: E402
    apply_system_prompt,
    dry_run_report,
    execute_run,
    log_failed_attempt,
)
from mondaybench.scenarios import load_scenario  # noqa: E402

MODEL = "deepseek-v4.1-flash-reliability-v1"
SCENARIOS = ["monday-001", "monday-002", "monday-003", "monday-004", "monday-005"]
RUNS_PER_SCENARIO = 3
ROOT = Path(__file__).resolve().parent


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%H:%M:%S")


def main() -> int:
    dry = "--dry-run" in sys.argv
    failures = 0

    for scenario_id in SCENARIOS:
        scenario = load_scenario(scenario_id)
        models = apply_endpoint_overrides(load_models(), endpoint_overrides_for(scenario_id))
        model = models[MODEL]
        prompt = build_prompt(scenario)

        if dry:
            report = dry_run_report(scenario, model, prompt)
            sent = apply_system_prompt(prompt, model).system_prompt
            print(f"===== {scenario_id} (dry run)")
            for key in ("model_id", "provider", "temperature", "max_output_tokens",
                        "ceiling_semantics", "reasoning_enabled", "prompt_sha256",
                        "prompt_chars"):
                print(f"  {key}: {report[key]}")
            print(f"  system_prompt_bytes: {len(sent.encode('utf-8'))}")
            print(f"  system_prompt_head: {sent.splitlines()[0]!r}")
            continue

        print(f"===== {scenario_id} {stamp()}", flush=True)
        for run_number in range(1, RUNS_PER_SCENARIO + 1):
            try:
                run = execute_run(
                    scenario=scenario,
                    model=model,
                    run_number=run_number,
                    prompt=prompt,
                    root=ROOT,
                )
            except ProviderError as exc:
                # Infrastructure failure: logged, not scored, not retried for
                # quality. The battery continues so one bad call does not cost
                # the runs that succeeded.
                failures += 1
                log_failed_attempt(
                    scenario_id=scenario_id,
                    model_slug=MODEL,
                    run_number=run_number,
                    error=str(exc),
                    kind="provider_error",
                    root=ROOT,
                )
                print(f"FAIL run {run_number}: {exc}", flush=True)
                continue
            print(
                f"ok   run {run_number}  {run.usage.output_tokens} out tok  "
                f"{run.performance.total_latency_ms:.1f} ms  {run.finish_reason}",
                flush=True,
            )
        print(f"----- {scenario_id} done {stamp()}", flush=True)

    print("DRY RUN DONE" if dry else f"GENERATION DONE ({failures} infrastructure failures)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
