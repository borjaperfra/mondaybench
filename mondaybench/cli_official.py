"""CLI pieces for the official v0.1 battery: freezing, planning, publishing.

Kept out of `cli.py` because these are the commands that turn a working
repository into a published claim, and they deserve to be readable on their own.
"""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .config import ConfigError, load_evaluator, load_models, repo_root
from .freeze import build_manifest, check_drift, load_manifest, write_manifest
from .leaderboard import (
    build_leaderboard,
    check_scoring_arithmetic,
    leaderboard_dir,
    official_blockers,
    write_leaderboard,
)
from .official import OFFICIAL_RUNS, plan_battery
from .prompt_builder import build_prompt
from .scenarios import ScenarioError, load_scenario

console = Console()

OFFICIAL_EVALUATOR = "evaluator-opus5-v0.1"

# The official v0.1 battery, in no particular order - ranking comes from scores.
OFFICIAL_MODELS = [
    "glm5.3-flash",
    "glm5.2",
    "mimo-v2.5",
    "deepseek-v4-flash",
    "qwen3.8-flash",
    "qwen3.6",
    "gemma4",
]


def parse_model_list(value: str | None) -> list[str] | None:
    if not value:
        return None
    return [part.strip() for part in value.split(",") if part.strip()]


def _fail(message: str) -> None:
    console.print(f"[bold red]error[/bold red] {message}")
    raise typer.Exit(code=1)


# --------------------------------------------------------------------------
# freeze
# --------------------------------------------------------------------------


def cmd_freeze(scenario: str, evaluator: str, check_only: bool) -> None:
    """Record - or verify - the canonical content hashes of a scenario."""
    try:
        evaluator_cfg = load_evaluator(evaluator)
        loaded = load_scenario(scenario, rubric_file=evaluator_cfg.rubric_file)
    except (ScenarioError, ConfigError) as exc:
        _fail(str(exc))
        return

    prompt = build_prompt(loaded)
    # Filenames come from the scenario, not from monday-001's spelling of them:
    # monday-002 ships `ground_truth.md`, and hardcoding `ground-truth.yaml`
    # would silently leave the answer key out of the integrity manifest.
    names = [
        "scenario.yaml",
        loaded.prompt_file,
        loaded.ground_truth_file,
        evaluator_cfg.rubric_file,
        *loaded.sources,
    ]
    existing = load_manifest(loaded.directory)

    if check_only:
        if existing is None:
            _fail(f"{scenario} is not frozen: no FROZEN.yaml in {loaded.directory}")
            return
        drift = check_drift(existing, loaded.directory)
        console.print(f"[bold]frozen manifest[/bold] {existing.path_count} files")
        console.print(f"[bold]prompt[/bold]          {existing.prompt_sha256}")
        if existing.prompt_sha256 != prompt.sha256:
            console.print(
                f"[bold red]DRIFT[/bold red] assembled prompt is {prompt.sha256} "
                f"but the manifest records {existing.prompt_sha256}"
            )
        for name, expected, actual in drift.changed:
            console.print(
                f"[bold red]DRIFT[/bold red] {name}: {expected[:12]} -> {actual[:12]}"
            )
        for name in drift.missing:
            console.print(f"[bold red]MISSING[/bold red] {name}")
        for name in drift.unlisted:
            console.print(f"[yellow]note[/yellow] {name} is not covered by the manifest")
        if drift.clean and existing.prompt_sha256 == prompt.sha256:
            console.print("\n[bold green]frozen content is intact[/bold green]")
            return
        raise typer.Exit(code=1)

    if existing is not None:
        console.print(
            f"[yellow]note[/yellow] {scenario} is already frozen "
            f"(prompt {existing.prompt_sha256[:12]}); rewriting the manifest"
        )

    manifest = build_manifest(
        scenario_id=loaded.id,
        benchmark_version=loaded.benchmark_version,
        prompt_sha256=prompt.sha256,
        rubric_file=evaluator_cfg.rubric_file,
        rubric_version=loaded.rubric.version,
        directory=loaded.directory,
        names=names,
    )
    target = write_manifest(manifest, loaded.directory)
    console.print(f"froze {manifest.path_count} files -> {target}")
    console.print(f"prompt sha256 {manifest.prompt_sha256}")
    console.print(f"rubric        {manifest.rubric_file} (version {manifest.rubric_version})")


# --------------------------------------------------------------------------
# plan
# --------------------------------------------------------------------------


def cmd_plan(scenario: str, models_csv: str | None, runs: int, evaluator: str) -> None:
    """Show which stored runs count as official and what still has to be generated."""
    try:
        evaluator_cfg = load_evaluator(evaluator)
        loaded = load_scenario(scenario, rubric_file=evaluator_cfg.rubric_file)
        configured = load_models()
    except (ScenarioError, ConfigError) as exc:
        _fail(str(exc))
        return

    slugs = parse_model_list(models_csv) or OFFICIAL_MODELS
    unknown = [s for s in slugs if s not in configured]
    if unknown:
        _fail(f"unknown model(s): {', '.join(unknown)}")

    prompt = build_prompt(loaded)
    plans = plan_battery(
        scenario_id=loaded.id,
        model_slugs=slugs,
        models=configured,
        expected_prompt_sha256=prompt.sha256,
        target=runs,
    )

    table = Table(title=f"Official run plan - {loaded.id} (target {runs}/model)", box=None)
    table.add_column("model")
    table.add_column("official", justify="right")
    table.add_column("rejected", justify="right")
    table.add_column("to generate", justify="right")
    table.add_column("run numbers")
    total_new = 0
    for slug in slugs:
        plan = plans[slug]
        numbers = plan.next_run_numbers()
        total_new += len(numbers)
        table.add_row(
            slug,
            str(plan.have),
            str(len(plan.rejected)) if plan.rejected else "-",
            str(plan.missing),
            ", ".join(str(n) for n in numbers) or "-",
        )
    console.print(table)

    for slug in slugs:
        for verdict in plans[slug].rejected:
            console.print(
                f"[yellow]rejected[/yellow] {slug} {verdict.path.name}: "
                f"{'; '.join(verdict.reasons)}"
            )

    console.print(f"\n[bold]new inferences required: {total_new}[/bold]")
    console.print(f"prompt sha256 {prompt.sha256}")
    console.print(f"rubric        {evaluator_cfg.rubric_file} ({loaded.rubric.version})")


# --------------------------------------------------------------------------
# publish
# --------------------------------------------------------------------------


def cmd_publish(scenario: str, evaluator: str, models_csv: str | None, runs: int) -> None:
    """Build the official leaderboard, refusing to publish anything unsound."""
    try:
        evaluator_cfg = load_evaluator(evaluator)
        loaded = load_scenario(scenario, rubric_file=evaluator_cfg.rubric_file)
    except (ScenarioError, ConfigError) as exc:
        _fail(str(exc))
        return

    slugs = parse_model_list(models_csv) or OFFICIAL_MODELS
    prompt = build_prompt(loaded)

    blockers: list[str] = []

    # A scenario still in calibration has no business in an official ranking:
    # its rubric and ground truth are still being tuned against the very runs
    # that would be published. This is the first gate, before anything else, so
    # the refusal names the real reason rather than a downstream symptom.
    if loaded.is_calibration:
        blockers.append(
            f"{scenario} is status=calibration - calibrate and freeze it before publishing"
        )

    manifest = load_manifest(loaded.directory)
    if manifest is None:
        blockers.append(
            f"{scenario} is not frozen - run `mondaybench freeze --scenario {scenario}`"
        )
    else:
        drift = check_drift(manifest, loaded.directory)
        if manifest.prompt_sha256 != prompt.sha256:
            blockers.append(
                f"prompt drifted: manifest {manifest.prompt_sha256[:12]}, "
                f"assembled {prompt.sha256[:12]}"
            )
        for name, expected, actual in drift.changed:
            blockers.append(f"frozen file changed: {name} {expected[:12]} -> {actual[:12]}")
        for name in drift.missing:
            blockers.append(f"frozen file missing: {name}")

    payload, summaries = build_leaderboard(
        scenario_id=loaded.id,
        evaluator_id=evaluator,
        benchmark_version=loaded.benchmark_version,
        root=None,
    )
    blockers.extend(
        official_blockers(
            payload,
            summaries,
            expected_models=slugs,
            expected_prompt_sha256=prompt.sha256,
            expected_rubric_version=loaded.rubric.version,
            expected_evaluator_id=evaluator,
            required_runs=runs,
        )
    )
    blockers.extend(check_scoring_arithmetic(evaluator, loaded.id))

    if blockers:
        console.print(
            f"[bold red]refusing to publish[/bold red] {len(blockers)} blocker(s):\n"
        )
        for blocker in blockers:
            console.print(f"  [red]-[/red] {blocker}")
        console.print(
            "\nNothing was written. An official leaderboard is a claim that these "
            "numbers are comparable; each blocker above says they are not."
        )
        raise typer.Exit(code=1)

    payload["official"] = True
    payload["frozen_prompt_sha256"] = prompt.sha256
    payload["rubric_version"] = loaded.rubric.version
    json_path, csv_path, md_path = write_leaderboard(payload, summaries)

    table = Table(title=f"MondayBench {loaded.benchmark_version} - OFFICIAL", box=None)
    table.add_column("#", justify="right")
    table.add_column("model")
    table.add_column("Monday Score", justify="right")
    table.add_column("runs", justify="right")
    table.add_column("range", justify="right")
    table.add_column("TTFA med", justify="right")
    table.add_column("total med", justify="right")
    for s in summaries:
        table.add_row(
            str(s.rank),
            s.display_name,
            f"{s.mean:.1f}",
            str(s.runs),
            f"{s.score_range:.1f}",
            "-" if s.median_ttfa_ms is None else f"{s.median_ttfa_ms / 1000:.1f}s",
            "-"
            if s.median_total_latency_ms is None
            else f"{s.median_total_latency_ms / 1000:.1f}s",
        )
    console.print(table)
    for path in (json_path, csv_path, md_path):
        console.print(f"wrote {path.relative_to(repo_root())}")


def cmd_results(scenario: str, evaluator: str) -> None:
    """Write one JSON file per model with everything published about it."""
    try:
        evaluator_cfg = load_evaluator(evaluator)
        loaded = load_scenario(scenario, rubric_file=evaluator_cfg.rubric_file)
    except (ScenarioError, ConfigError) as exc:
        _fail(str(exc))
        return

    payload, summaries = build_leaderboard(
        scenario_id=loaded.id,
        evaluator_id=evaluator,
        benchmark_version=loaded.benchmark_version,
    )
    if not summaries:
        _fail(f"no evaluations found for {evaluator}")

    directory = leaderboard_dir(loaded.id) / "models"
    directory.mkdir(parents=True, exist_ok=True)
    by_slug = {entry["model_slug"]: entry for entry in payload["models"]}
    for summary in summaries:
        entry = dict(by_slug[summary.model_slug])
        entry["scenario"] = loaded.id
        entry["evaluator"] = evaluator
        entry["benchmark_version"] = loaded.benchmark_version
        target = directory / f"{summary.model_slug}.json"
        target.write_text(
            json.dumps(entry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n"
        )
        console.print(f"wrote {target.relative_to(repo_root())}")


__all__ = [
    "OFFICIAL_EVALUATOR",
    "OFFICIAL_MODELS",
    "OFFICIAL_RUNS",
    "cmd_freeze",
    "cmd_plan",
    "cmd_publish",
    "cmd_results",
    "parse_model_list",
]
