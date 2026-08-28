"""Generate raw model responses and write them as immutable benchmark evidence.

Everything in `runs/` is evidence. The runner refuses to overwrite an existing
run file unless explicitly told to, and never writes a run file for a failed
API call - a failed attempt is logged, not scored.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .config import ModelConfig, repo_root
from .pricing import compute_economics
from .prompt_builder import BuiltPrompt, build_prompt
from .providers import ProviderError, build_model_provider
from .scenarios import Scenario
from .schemas import (
    BenchmarkRun,
    RunGeneration,
    RunModel,
    RunPerformance,
    RunProviderMetadata,
    RunUsage,
)

MAX_ATTEMPTS = 3  # one call + two retries for transient failures
BACKOFF_SECONDS = (2.0, 6.0)


class RunExistsError(Exception):
    """An official run file already exists and --overwrite was not passed."""


@dataclass
class Attempt:
    run_number: int
    error: str
    transient: bool
    attempts: int


def runs_dir(scenario_id: str, model_slug: str, root: Path | None = None) -> Path:
    return (root or repo_root()) / "runs" / scenario_id / model_slug


def run_path(scenario_id: str, model_slug: str, run_number: int, root: Path | None = None) -> Path:
    return runs_dir(scenario_id, model_slug, root) / f"run-{run_number:03d}.json"


def make_run_id(scenario_id: str, model_slug: str, run_number: int) -> str:
    return f"{scenario_id}__{model_slug}__{run_number:03d}"


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def dry_run_report(scenario: Scenario, model: ModelConfig, prompt: BuiltPrompt) -> dict[str, object]:
    """Everything a dry run should show. Makes no API call."""
    return {
        "scenario": scenario.id,
        "model_slug": model.slug,
        "display_name": model.display_name,
        "provider": model.provider,
        "api_style": model.api_style,
        "model_id": model.model_id,
        "base_url_env": model.base_url_env,
        "prompt_sha256": prompt.sha256,
        "prompt_chars": len(prompt.text),
        "prompt_token_estimate": prompt.estimated_tokens(),
        "system_prompt": prompt.system_prompt,
        "temperature": model.temperature,
        "max_output_tokens": model.max_output_tokens,
        "reasoning_enabled": model.reasoning_enabled,
        "pricing_known": model.pricing.input_per_million_usd is not None,
    }


def execute_run(
    *,
    scenario: Scenario,
    model: ModelConfig,
    run_number: int,
    prompt: BuiltPrompt | None = None,
    overwrite: bool = False,
    root: Path | None = None,
) -> BenchmarkRun:
    """Generate one run and persist it. Raises on failure; writes nothing."""
    prompt = prompt or build_prompt(scenario)
    target = run_path(scenario.id, model.slug, run_number, root)
    if target.exists() and not overwrite:
        raise RunExistsError(
            f"{target} already exists - pass --overwrite to replace it "
            f"(published runs should never be overwritten)"
        )

    provider = build_model_provider(model)
    generation_config = {
        "temperature": model.temperature,
        "max_output_tokens": model.max_output_tokens,
        "extra_body": model.extra_body,
    }

    result = None
    last_error: ProviderError | None = None
    for attempt in range(MAX_ATTEMPTS):
        try:
            result = provider.generate(
                model_id=model.model_id,
                system_prompt=prompt.system_prompt,
                user_prompt=prompt.text,
                generation_config=generation_config,
            )
            break
        except ProviderError as exc:
            last_error = exc
            # Only transient network/5xx failures earn a retry. A response that
            # merely scores badly, or a truncated-but-valid response, does not.
            if not exc.transient or attempt == MAX_ATTEMPTS - 1:
                raise
            time.sleep(BACKOFF_SECONDS[min(attempt, len(BACKOFF_SECONDS) - 1)])

    if result is None:  # pragma: no cover - loop either breaks or raises
        raise last_error or ProviderError("generation failed with no error recorded")

    economics = compute_economics(
        model.pricing,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
        reasoning_tokens=result.reasoning_tokens,
    )

    run = BenchmarkRun(
        benchmark_version=scenario.benchmark_version,
        scenario_id=scenario.id,
        scenario_prompt_sha256=prompt.sha256,
        run_id=make_run_id(scenario.id, model.slug, run_number),
        run_number=run_number,
        model=RunModel(
            slug=model.slug,
            display_name=model.display_name,
            provider=model.provider,
            model_id=model.model_id,
        ),
        generation=RunGeneration(
            temperature=model.temperature,
            max_output_tokens=model.max_output_tokens,
            reasoning_enabled=model.reasoning_enabled,
            unsupported_parameters=result.unsupported_parameters,
            system_prompt_sent=result.system_prompt_sent,
        ),
        timestamp_utc=_now_utc(),
        usage=RunUsage(
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            reasoning_tokens=result.reasoning_tokens,
        ),
        performance=RunPerformance(
            ttft_ms=result.ttft_ms,
            ttfa_ms=result.ttfa_ms,
            total_latency_ms=result.total_latency_ms,
            tokens_per_second=result.tokens_per_second(),
        ),
        economics=economics,
        response=result.text,
        finish_reason=result.finish_reason,
        provider_metadata=RunProviderMetadata(
            request_id=result.provider_request_id,
            raw_usage=result.raw_usage,
        ),
    )

    write_run(run, root=root)
    return run


def write_run(run: BenchmarkRun, root: Path | None = None) -> Path:
    target = run_path(run.scenario_id, run.model.slug, run.run_number, root)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(run.model_dump(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return target


def log_failed_attempt(
    *,
    scenario_id: str,
    model_slug: str,
    run_number: int,
    error: str,
    kind: str = "error",
    root: Path | None = None,
) -> Path:
    """Record a failed API call without creating a valid benchmark run.

    `kind` is stored alongside the message so the log can be counted by failure
    class later. A model that ends its turn with an empty answer and one that
    ran out of budget mid-thought both leave "no answer" behind, and only the
    second is fixed by a bigger budget.
    """
    directory = runs_dir(scenario_id, model_slug, root)
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / "failed-attempts.jsonl"
    entry = {
        "timestamp_utc": _now_utc(),
        "run_number": run_number,
        "kind": kind,
        "error": error,
    }
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return target


def load_run(path: Path) -> BenchmarkRun:
    return BenchmarkRun.model_validate_json(path.read_text(encoding="utf-8"))


def find_runs(scenario_id: str, model_slug: str, root: Path | None = None) -> list[Path]:
    directory = runs_dir(scenario_id, model_slug, root)
    if not directory.is_dir():
        return []
    return sorted(directory.glob("run-*.json"))


def models_with_runs(scenario_id: str, root: Path | None = None) -> list[str]:
    directory = (root or repo_root()) / "runs" / scenario_id
    if not directory.is_dir():
        return []
    return sorted(p.name for p in directory.iterdir() if p.is_dir() and any(p.glob("run-*.json")))
