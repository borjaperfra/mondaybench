"""Generate raw model responses and write them as immutable benchmark evidence.

Everything in `runs/` is evidence. The runner refuses to overwrite an existing
run file unless explicitly told to, and never writes a run file for a failed
API call - a failed attempt is logged, not scored.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path

from .config import ModelConfig, repo_root
from .pricing import compute_economics
from .prompt_builder import BuiltPrompt, build_prompt
from .providers import ProviderError, build_model_provider
from .scenarios import Scenario
from . import reasoning
from .schemas import (
    BenchmarkRun,
    RunGeneration,
    RunModel,
    RunPerformance,
    RunProviderMetadata,
    RunReasoning,
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


# What the provider is actually sent as `max_tokens`, and what MondayBench calls
# it internally from monday-004 onwards.
#
# A SAFETY CEILING, not a reasoning budget. The token-budget audit established
# that the same configured value is honoured as reasoning+answer by some
# provider/model pairs, ignored by another and never tested by the rest, so it
# cannot equalise compute and is not meant to. It exists to stop a runaway
# generation, and it is set high enough that a normal successful answer never
# reaches it.
CEILING_SEMANTICS = "provider_specific"


def effective_ceiling(scenario: Scenario, model: ModelConfig) -> int:
    """The scenario's own ceiling if it declares one, else the model default.

    monday-001..003 declare none and keep the 32,000 they were generated under,
    so their runs go on qualifying against `models.yaml` unchanged.
    """
    return scenario.safety_ceiling_tokens or model.max_output_tokens


def apply_system_prompt(prompt: BuiltPrompt, model: ModelConfig) -> BuiltPrompt:
    """Swap in a model's own system prompt, leaving the user prompt untouched.

    `build_prompt` renders one prompt for a whole battery, and the CLI builds it
    once for every model in that battery, so a per-model system prompt cannot be
    chosen there. It is applied here, where the model is known.

    Only the system field moves. `prompt.sha256` is the hash of the assembled
    USER prompt and is what `scenario_prompt_sha256` records, so a run generated
    under a different system prompt still carries the frozen scenario hash - it
    is the same scenario, read under different instructions. The system prompt
    is hashed separately into `generation.system_prompt_sha256`, and through it
    into `config_sha256`, which is where the difference belongs and where
    qualification can see it.
    """
    if model.system_prompt is None:
        return prompt
    return replace(prompt, system_prompt=model.system_prompt)


def dry_run_report(scenario: Scenario, model: ModelConfig, prompt: BuiltPrompt) -> dict[str, object]:
    """Everything a dry run should show. Makes no API call."""
    prompt = apply_system_prompt(prompt, model)
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
        "max_output_tokens": effective_ceiling(scenario, model),
        "safety_ceiling_tokens": effective_ceiling(scenario, model),
        "ceiling_semantics": CEILING_SEMANTICS,
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
    prompt = apply_system_prompt(prompt, model)
    target = run_path(scenario.id, model.slug, run_number, root)
    if target.exists() and not overwrite:
        raise RunExistsError(
            f"{target} already exists - pass --overwrite to replace it "
            f"(published runs should never be overwritten)"
        )

    provider = build_model_provider(model)
    ceiling = effective_ceiling(scenario, model)
    # The body actually sent. A per-run seed is the only thing that can differ
    # between runs of one model, and it is recorded in the run's extra_body.
    wire_extra_body = dict(model.extra_body)
    if model.seed_per_run:
        wire_extra_body["seed"] = run_number
    generation_config = {
        "temperature": model.temperature,
        "max_output_tokens": ceiling,
        "extra_body": wire_extra_body,
    }
    # Only sent when a model pins it, so adding the field changes nothing on the
    # wire for existing configs and keeps a replacement run comparable with the
    # runs it joins.
    if model.top_p is not None:
        generation_config["top_p"] = model.top_p

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

    # Effective configuration, recorded so a later audit does not have to
    # reconstruct it. `reasoning_requested` is the regime this run is supposed
    # to belong to; whether the provider honoured it is decided from the
    # response, further down.
    reasoning_requested = reasoning.requested_from_config(model.capabilities, model.extra_body)
    system_hash = reasoning.system_prompt_sha256(prompt.system_prompt)
    config_hash = reasoning.generation_config_sha256(
        provider=model.provider,
        model_id=model.model_id,
        temperature=model.temperature,
        top_p=model.top_p,
        max_output_tokens=ceiling,
        reasoning_requested=reasoning_requested,
        reasoning_mode=None,
        reasoning_effort=None,
        # Hashed from the model's configuration, not the wire body, so a per-run
        # seed does not split one battery into three fingerprints; the marker
        # still separates a seeded battery from an unseeded one.
        extra_body=({**model.extra_body, "seed_per_run": True}
                    if model.seed_per_run else model.extra_body),
        system_prompt_hash=system_hash,
    )

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
            top_p=model.top_p,
            max_output_tokens=ceiling,
            safety_ceiling_tokens=ceiling,
            ceiling_semantics=CEILING_SEMANTICS,
            reasoning_enabled=model.reasoning_enabled,
            reasoning_requested=reasoning_requested,
            reasoning_mode=None,
            reasoning_effort=None,
            unsupported_parameters=result.unsupported_parameters,
            system_prompt_sent=result.system_prompt_sent,
            system_prompt_sha256=system_hash,
            extra_body=wire_extra_body,
            config_sha256=config_hash,
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

    # Observed, not configured. The stream evidence is attached first so
    # classify() can use it, then the verdict is written back alongside.
    observed = RunReasoning(
        requested=reasoning_requested,
        status="UNOBSERVABLE",
        tokens=result.reasoning_tokens,
        stream_observed=result.reasoning_stream_observed,
        stream_event_count=result.reasoning_stream_event_count,
    )
    status, tokens, evidence = reasoning.classify_detailed(
        run.model_copy(update={"reasoning": observed})
    )
    run = run.model_copy(
        update={
            "reasoning": observed.model_copy(
                update={"status": status, "tokens": tokens, "evidence": evidence}
            )
        }
    )

    # Exclusive unless the caller explicitly asked to overwrite: reaching here
    # otherwise means we intend to create a file that did not exist at the
    # start of generation, and it must still not exist now.
    write_run(run, root=root, exclusive=not overwrite)
    return run


def write_run(run: BenchmarkRun, root: Path | None = None, *, exclusive: bool = False) -> Path:
    """Persist a run. With `exclusive`, refuse to clobber an existing file.

    `execute_run` checks for an existing file before calling the provider, and
    generation then takes minutes. Two concurrent batteries covering the same
    model both pass that check and both write, and the second silently replaces
    the first - which happened once on monday-004/mimo-v2.5, and the second time
    was caught only because the writes happened to land in a safe order.

    The check belongs at the write, not at the start. Mode "x" is
    O_CREAT|O_EXCL: the filesystem decides the race, not two Python processes.
    """
    target = run_path(run.scenario_id, run.model.slug, run.run_number, root)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(run.model_dump(), indent=2, ensure_ascii=False) + "\n"
    if exclusive:
        try:
            with open(target, "x", encoding="utf-8", newline="\n") as handle:
                handle.write(payload)
        except FileExistsError as exc:
            raise RunExistsError(
                f"{target} appeared while this run was generating - another battery is "
                f"covering the same model. Nothing was overwritten; re-plan and retry."
            ) from exc
        return target
    target.write_text(payload, encoding="utf-8", newline="\n")
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
    with target.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return target


def load_run(path: Path) -> BenchmarkRun:
    return BenchmarkRun.model_validate_json(path.read_text(encoding="utf-8"))


def find_runs(scenario_id: str, model_slug: str, root: Path | None = None) -> list[Path]:
    directory = runs_dir(scenario_id, model_slug, root)
    if not directory.is_dir():
        return []
    return sorted(directory.glob("run-*.json"))


def archived_run_numbers(
    scenario_id: str, model_slug: str, root: Path | None = None
) -> set[int]:
    """Run numbers already used by archived batteries, which must never recur.

    A run id is `<scenario>__<model>__<NNN>`, and recorded verdicts are keyed by
    it. Archiving a calibration battery frees its numbers on disk, so the next
    generation would reuse them - and then the archived verdict file would
    replay against a different response without erroring, scoring the wrong
    text. monday-003's archive README flags exactly this trap; nothing stopped
    it from happening.
    """
    base = (root or repo_root()) / "archive"
    if not base.is_dir():
        return set()
    taken: set[int] = set()
    for path in base.glob(f"*/runs-{scenario_id}/{model_slug}/run-*.json"):
        try:
            taken.add(int(path.stem.split("-")[-1]))
        except ValueError:
            continue
    return taken


SAMPLE_IDENTITY_FIELDS = ("response", "provider_metadata.request_id")


def sample_identity(record: dict[str, Any]) -> tuple[str, str | None]:
    """The immutable identity of one generated sample.

    Returns `(content_sha256, request_id)`.

    WHY THIS AND NOT `run_id`. A run id is `<scenario>__<model>__<NNN>`, which is
    a *location*, not a provenance fact. Archiving a battery frees its numbers,
    the next generation reuses them, and two entirely different samples then
    carry the same id - which is exactly what happened to monday-005, whose
    official battery restarted at run-001 over the calibration battery's ids.
    An identity that collides on the thing it is meant to distinguish is not an
    identity.

    WHAT IS HASHED, and why only this. `content_sha256` is sha256 over the
    response text exactly as the provider returned it. That is the artefact a
    rubric is developed against: when a criterion is written while reading a
    response, it is those bytes the criterion was fitted to. `request_id` is the
    provider's own generation id, carried alongside as a corroborating identity.

    Deliberately NOT part of the identity, because none of it is a property of
    the sample: the score, any judge verdict, the evaluation path, leaderboard
    position, the run number, the file location, or the timestamp. All of those
    can change without the sample changing, and some change precisely when a
    battery is archived.

    `request_id` is typed `str | None` in the schema, so it is corroborating
    rather than primary - a provider that stops returning one must not silently
    disable the guard. Verified across all 206 run files in the repository:
    present on every one, and unique per distinct sample. The only repeats are
    seven monday-003 samples filed in two archive directories at once, which is
    archival duplication of one sample rather than two samples sharing an id.
    """
    body = record.get("response")
    if not isinstance(body, str):
        raise ValueError("run record has no response text to identify")
    content = hashlib.sha256(body.encode("utf-8")).hexdigest()
    request_id = (record.get("provider_metadata") or {}).get("request_id")
    return content, request_id


def archived_run_paths(scenario_id: str, root: Path | None = None) -> list[Path]:
    """Every archived run file for a scenario, whatever archive holds it.

    Same layout `archived_run_numbers` relies on: `archive/*/runs-<scenario>/`.
    Archived material is development material by convention - every archive
    README in this repository says so - so anything here is a sample the rubric
    may have been written against.
    """
    base = (root or repo_root()) / "archive"
    if not base.is_dir():
        return []
    return sorted(base.glob(f"*/runs-{scenario_id}/*/run-*.json"))


def read_run_record(path: Path) -> dict[str, Any]:
    """Raw run JSON. Deliberately not validated: an archived run written under
    an older schema must still be identifiable, or archiving would erase
    provenance rather than preserve it."""
    return json.loads(path.read_text(encoding="utf-8"))


def models_with_runs(scenario_id: str, root: Path | None = None) -> list[str]:
    directory = (root or repo_root()) / "runs" / scenario_id
    if not directory.is_dir():
        return []
    return sorted(p.name for p in directory.iterdir() if p.is_dir() and any(p.glob("run-*.json")))
