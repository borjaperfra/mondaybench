"""The `mondaybench` command line."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from . import BENCHMARK_VERSION
from .config import (
    ConfigError,
    apply_endpoint_overrides,
    endpoint_overrides_for,
    find_literal_credentials,
    load_evaluator,
    load_models,
    repo_root,
    resolve_evaluator,
)
from .cli_official import (
    OFFICIAL_EVALUATOR,
    OFFICIAL_MODELS,
    cmd_freeze,
    cmd_plan,
    cmd_publish,
    cmd_results,
    parse_model_list,
)
from .discovery import endpoints_from_models, list_models
from .freeze import check_drift, load_manifest
from .official import plan_battery
from .evaluator import evaluate_run, find_evaluations, load_evaluation, resolve_ground_truth
from .judge import Judge, JudgeError
from .recorded_judge import RecordedJudge, VerdictStore, build_worksheet
from .leaderboard import build_leaderboard, write_leaderboard
from .prompt_builder import PLACEHOLDER_PATTERN, build_prompt, placeholder_for
from .providers import ProviderError
from .runner import (
    RunExistsError,
    dry_run_report,
    execute_run,
    find_runs,
    load_run,
    log_failed_attempt,
    models_with_runs,
)
from .scenarios import NOISE_DIMENSION, ScenarioError, list_scenario_ids, load_scenario
from .evaluator import write_review

app = typer.Typer(
    add_completion=False,
    help="MondayBench - can this model handle your Monday?",
    no_args_is_help=True,
)
console = Console()

DEFAULT_EVALUATOR = "evaluator-v0.1"

EVALUATOR_HELP = (
    "Evaluator id. Defaults to the one that declares this scenario and is "
    "marked `status: official`."
)


def _evaluator_for(scenario: str, explicit: str | None, *, fallback: str) -> str:
    """Resolve `--evaluator`, failing loudly rather than silently guessing.

    Every command used to default to a fixed id belonging to monday-001, so
    running one against a later scenario reached for monday-001's rubric
    filename inside that scenario's directory. See `config.resolve_evaluator`.
    """
    try:
        return resolve_evaluator(scenario, explicit, fallback)
    except ConfigError as exc:
        _fail(str(exc))
        raise


# A terminal column has room for about six characters. Dimension ids are long
# and snake_cased, so take the initial of every word after the first and hang it
# off a truncated first word: `plan_economics` -> `plan:e`.
def _dimension_heading(key: str) -> str:
    head, *rest = key.split("_")
    if not rest:
        return head[:8]
    return head[:5] + ":" + "".join(word[0] for word in rest)


def _fail(message: str) -> None:
    console.print(f"[bold red]error[/bold red] {message}")
    raise typer.Exit(code=1)


def _resolve_model_slugs(
    model: str | None, all_models: bool, available: dict[str, Any]
) -> list[str]:
    if all_models and model:
        _fail("pass either --model or --all-models, not both")
    if all_models:
        return sorted(available)
    if not model:
        _fail("pass --model <slug> or --all-models")
    if model not in available:
        _fail(f"unknown model {model!r} (configured: {', '.join(sorted(available))})")
    return [model]  # type: ignore[list-item]


# --------------------------------------------------------------------------
# scenarios / models
# --------------------------------------------------------------------------


@app.command()
def scenarios() -> None:
    """List available scenarios."""
    ids = list_scenario_ids()
    if not ids:
        _fail("no scenarios found under scenarios/")
    for scenario_id in ids:
        scenario = load_scenario(scenario_id)
        console.print(f"{scenario.id}    {scenario.name}")


@app.command()
def models() -> None:
    """List configured models."""
    try:
        configured = apply_endpoint_overrides(load_models(), endpoint_overrides_for(loaded.id))
    except ConfigError as exc:
        _fail(str(exc))
        return

    table = Table(title="Configured models", box=None, pad_edge=False)
    table.add_column("slug")
    table.add_column("display name")
    table.add_column("provider")
    table.add_column("model id")
    table.add_column("temp", justify="right")
    table.add_column("max out", justify="right")
    table.add_column("reasoning")
    table.add_column("priced")
    for slug in sorted(configured):
        cfg = configured[slug]
        table.add_row(
            slug,
            cfg.display_name,
            cfg.provider,
            cfg.model_id,
            "-" if cfg.temperature is None else str(cfg.temperature),
            str(cfg.max_output_tokens),
            "yes" if cfg.reasoning_enabled else "no",
            "yes" if cfg.pricing.input_per_million_usd is not None else "no",
        )
    console.print(table)


@app.command()
def endpoints() -> None:
    """Ask each configured endpoint which models it actually serves.

    Use this to confirm a `model_id` before an official run, and to discover ids
    that are served but not yet documented.
    """
    try:
        configured = apply_endpoint_overrides(load_models(), endpoint_overrides_for(loaded.id))
    except ConfigError as exc:
        _fail(str(exc))
        return

    discovered = endpoints_from_models(configured)
    if not discovered:
        _fail("no OpenAI-compatible endpoints found in models.yaml")

    declared: dict[str, set[str]] = {}
    for cfg in configured.values():
        declared.setdefault(cfg.provider, set()).add(cfg.model_id)

    problems = 0
    for endpoint in discovered:
        console.print(f"\n[bold]{endpoint.provider}[/bold]  ({endpoint.base_url_env})")
        try:
            served = list_models(endpoint)
        except ConfigError as exc:
            problems += 1
            console.print(f"  [bold red]unavailable[/bold red] {exc}")
            continue

        served_set = set(served)
        for model_id in served:
            mark = "[green]*[/green]" if model_id in declared.get(endpoint.provider, set()) else " "
            console.print(f"  {mark} {model_id}")

        missing = sorted(declared.get(endpoint.provider, set()) - served_set)
        for model_id in missing:
            problems += 1
            console.print(
                f"  [bold red]MISSING[/bold red] models.yaml declares {model_id!r} "
                f"but this endpoint does not serve it"
            )

    console.print("\n[green]*[/green] = declared in models.yaml")
    if problems:
        raise typer.Exit(code=1)


@app.command()
def worksheet(
    scenario: str = typer.Option(..., "--scenario"),
    model: str = typer.Option(..., "--model"),
    evaluator: str = typer.Option(
        "evaluator-manual-v0.2", "--evaluator", help="Supplies the rubric to grade against"
    ),
    out: Path | None = typer.Option(None, "--out", help="Defaults to worksheets/<scenario>/"),
) -> None:
    """Write a manual verdict worksheet for every stored run of a model.

    Fill in the labels, then evaluate with `--evaluator evaluator-manual-v0.1
    --verdicts <file>`. No API calls, no credentials.
    """
    try:
        evaluator_cfg = load_evaluator(evaluator)
        loaded = load_scenario(scenario, rubric_file=evaluator_cfg.rubric_file)
    except (ScenarioError, ConfigError) as exc:
        _fail(str(exc))
        return

    run_paths = find_runs(loaded.id, model)
    if not run_paths:
        _fail(f"no runs found under runs/{loaded.id}/{model}/ - run the model first")

    directory = out or repo_root() / "worksheets" / loaded.id / model
    directory.mkdir(parents=True, exist_ok=True)

    for path in run_paths:
        raw = load_run(path)
        target = directory / f"{path.stem}.verdicts.jsonl"
        target.write_text(
            build_worksheet(loaded.rubric, raw.run_id, raw.response), encoding="utf-8", newline="\n"
        )
        console.print(f"wrote {target}")

    noise_note = (
        f"{len(loaded.rubric.noise.false_actions)} noise flags and "
        if loaded.rubric.noise is not None
        else ""
    )
    console.print(
        f"\n{len(run_paths)} worksheet(s). Each needs "
        f"{len(loaded.rubric.criteria)} criterion labels, "
        f"{noise_note}a penalties list."
    )


# --------------------------------------------------------------------------
# validate
# --------------------------------------------------------------------------


@app.command()
def validate(
    scenario: str = typer.Option(..., "--scenario", help="Scenario id, e.g. monday-001"),
    evaluator: str | None = typer.Option(None, "--evaluator", help=EVALUATOR_HELP),
) -> None:
    """Check a scenario, its rubric and the evaluator config for consistency."""
    evaluator = _evaluator_for(scenario, evaluator, fallback=DEFAULT_EVALUATOR)
    problems: list[str] = []
    warnings: list[str] = []

    # The evaluator names the rubric, so it has to be resolved first.
    evaluator_cfg = None
    rubric_file = "rubric.yaml"
    try:
        evaluator_cfg = load_evaluator(evaluator)
        rubric_file = evaluator_cfg.rubric_file
    except ConfigError as exc:
        problems.append(str(exc))

    try:
        loaded = load_scenario(scenario, rubric_file=rubric_file)
    except ScenarioError as exc:
        _fail(str(exc))
        return

    rubric = loaded.rubric

    # dimension maximums sum to the declared base total
    dimension_total = sum(rubric.dimension_max.values())
    if abs(dimension_total - rubric.total_base_points) > 1e-9:
        problems.append(
            f"dimension maximums sum to {dimension_total} "
            f"but total_base_points is {rubric.total_base_points}"
        )

    # every criterion id is unique
    seen: set[str] = set()
    for criterion in rubric.criteria:
        if criterion.id in seen:
            problems.append(f"duplicate criterion id {criterion.id!r}")
        seen.add(criterion.id)

    # per-dimension PASS points sum to that dimension's maximum
    for name, max_points in rubric.dimension_max.items():
        if name == NOISE_DIMENSION:
            continue
        criteria = rubric.criteria_for(name)
        if not criteria:
            problems.append(f"dimension {name!r} has no criteria")
            continue
        pass_total = sum(c.points_pass for c in criteria)
        if abs(pass_total - max_points) > 1e-9:
            problems.append(
                f"dimension {name!r}: PASS points sum to {pass_total}, max_points is {max_points}"
            )
        for criterion in criteria:
            if not (criterion.points_fail <= criterion.points_partial <= criterion.points_pass):
                problems.append(
                    f"criterion {criterion.id!r}: points are not ordered fail <= partial <= pass"
                )
            for label, text in (
                ("pass", criterion.pass_definition),
                ("partial", criterion.partial_definition),
                ("fail", criterion.fail_definition),
            ):
                if not text:
                    problems.append(f"criterion {criterion.id!r} has an empty {label}_definition")

    # noise dimension is internally coherent, where the rubric has one
    noise = rubric.noise
    if noise is not None:
        if noise.starting_points > noise.max_points:
            problems.append("noise_resistance starting_points exceeds max_points")
        if not noise.false_actions:
            problems.append("noise_resistance defines no false_actions")
        noise_ids = [a.id for a in noise.false_actions]
        if len(noise_ids) != len(set(noise_ids)):
            problems.append("duplicate false_action ids")
        for action in noise.false_actions:
            if not action.description:
                problems.append(f"false_action {action.id!r} has no description")

    # global penalties
    if not rubric.penalties:
        problems.append("rubric defines no global penalties")
    for ptype, definition in rubric.penalties.items():
        if definition.points >= 0:
            problems.append(f"penalty {ptype} should be negative, got {definition.points}")

    # prompt resolves cleanly
    prompt = None
    try:
        prompt = build_prompt(loaded)
    except ScenarioError as exc:
        problems.append(str(exc))

    # Placeholder coverage, but only for a template that uses placeholders at
    # all. A template with none is assembled by appending sources in declared
    # order, which `build_prompt` above has already exercised.
    uses_placeholders = bool(PLACEHOLDER_PATTERN.search(loaded.prompt_template))
    if uses_placeholders:
        for source in loaded.sources:
            token = placeholder_for(source)
            if token not in loaded.prompt_template:
                problems.append(
                    f"prompt template is missing placeholder {token} for source {source!r}"
                )

    # Every declared source exists and reaches the rendered prompt. Appending
    # mode has no placeholder to check, so the content itself is the check.
    if prompt is not None:
        for source in loaded.sources:
            body = loaded.source_text[source].strip()
            if body and body[:200] not in prompt.text:
                problems.append(f"source {source!r} does not appear in the rendered prompt")

    # The answer key must never reach the candidate. Checked on content, not on
    # trust: a distinctive line from the ground truth appearing in the prompt
    # would mean the scenario leaks its own solution.
    if prompt is not None and loaded.ground_truth_text:
        leaked = [
            line.strip()
            for line in loaded.ground_truth_text.splitlines()
            if len(line.strip()) > 40 and line.strip() in prompt.text
        ]
        if leaked:
            problems.append(
                f"ground truth leaks into the candidate prompt: {leaked[0][:60]!r}"
            )

    # evaluator config and its ground-truth map
    if evaluator_cfg is not None and not evaluator_cfg.ground_truth_map:
        warnings.append(
            f"evaluator {evaluator} declares no ground_truth_map, so every criterion is "
            f"judged against the whole answer key ({loaded.ground_truth_file}); per-criterion "
            f"slicing is the stronger setup where the scenario supports it"
        )
    if evaluator_cfg is not None and evaluator_cfg.ground_truth_map:
        mapped = set(evaluator_cfg.ground_truth_map)
        criterion_ids = {c.id for c in rubric.criteria}
        for missing in sorted(criterion_ids - mapped):
            problems.append(f"evaluator {evaluator}: ground_truth_map has no entry for {missing!r}")
        for extra in sorted(mapped - criterion_ids):
            problems.append(
                f"evaluator {evaluator}: ground_truth_map references unknown criterion {extra!r}"
            )
        for criterion_id, paths in evaluator_cfg.ground_truth_map.items():
            if not paths:
                problems.append(
                    f"evaluator {evaluator}: criterion {criterion_id!r} maps to no ground-truth keys"
                )
            try:
                resolve_ground_truth(loaded.ground_truth, paths)
            except KeyError as exc:
                problems.append(f"criterion {criterion_id!r}: {exc}")

    # An evaluator written for one scenario must not be pointed at another:
    # its rubric, judge prompts and ground-truth map all assume that scenario.
    if evaluator_cfg is not None and evaluator_cfg.scenario:
        if evaluator_cfg.scenario != loaded.id:
            problems.append(
                f"evaluator {evaluator} is written for scenario "
                f"{evaluator_cfg.scenario!r}, not {loaded.id!r}"
            )

    # Same for the scenario version. An evaluator written against v0.1 of a
    # scenario cannot score v0.2 of it: the criteria ask different questions
    # about different sources, even though the scenario id has not changed.
    if evaluator_cfg is not None and evaluator_cfg.scenario_version:
        declared_sv = str(loaded.scenario_version or "")
        if evaluator_cfg.scenario_version != declared_sv:
            problems.append(
                f"evaluator {evaluator} declares scenario_version "
                f"{evaluator_cfg.scenario_version!r} but scenario.yaml says {declared_sv!r}"
            )

    # A data file sitting in the scenario directory but missing from
    # source_order never reaches the model. Usually a leftover from an earlier
    # version; always worth naming, because a reader will assume every file in
    # the folder is part of the test.
    known_files = set(loaded.sources) | {
        "scenario.yaml",
        loaded.ground_truth_file,
        rubric_file,
        "rubric.yaml",
        loaded.prompt_file,
        "FROZEN.yaml",
    }
    for entry in sorted(loaded.directory.iterdir()):
        if not entry.is_file() or entry.name in known_files:
            continue
        if entry.suffix.lower() in (".md", ".txt"):
            continue  # notes shipped with the package, not candidate sources
        warnings.append(
            f"{entry.name} sits in the scenario directory but is not in source_order, "
            f"so the model never sees it"
        )

    # The evaluator records which rubric version it was written against. If the
    # rubric on disk has moved on, the scores would not mean what the evaluator
    # claims they mean.
    if evaluator_cfg is not None and evaluator_cfg.rubric_version:
        if evaluator_cfg.rubric_version != rubric.version:
            problems.append(
                f"evaluator {evaluator} declares rubric_version "
                f"{evaluator_cfg.rubric_version!r} but {rubric_file} is version "
                f"{rubric.version!r}"
            )

    # External judge prompts must exist where the evaluator says they are.
    if evaluator_cfg is not None:
        for label, name in (
            ("prompt_file", evaluator_cfg.prompt_file),
            ("penalty_prompt_file", evaluator_cfg.penalty_prompt_file),
        ):
            if not name:
                continue
            candidates = [
                repo_root() / "evaluators" / name,
                repo_root() / "evaluators" / loaded.id / name,
            ]
            if not any(c.exists() for c in candidates):
                problems.append(
                    f"evaluator {evaluator}: {label} {name!r} not found under evaluators/"
                )

    # a frozen scenario must not have drifted
    manifest = load_manifest(loaded.directory)
    if loaded.is_calibration:
        warnings.append(
            f"{scenario} is status=calibration: it cannot be published as an official "
            f"result until it is calibrated and frozen"
        )
    elif manifest is None:
        warnings.append(
            f"{scenario} is not frozen - run `mondaybench freeze --scenario {scenario}` "
            f"before publishing"
        )
    elif manifest is not None:
        drift = check_drift(manifest, loaded.directory)
        if prompt is not None and manifest.prompt_sha256 != prompt.sha256:
            problems.append(
                f"frozen prompt is {manifest.prompt_sha256[:12]} but the assembled prompt "
                f"is {prompt.sha256[:12]} - scenario content changed after freezing"
            )
        for name, expected, actual in drift.changed:
            problems.append(
                f"frozen file changed: {name} {expected[:12]} -> {actual[:12]}"
            )
        for name in drift.missing:
            problems.append(f"frozen file missing: {name}")
        for name in drift.unlisted:
            warnings.append(f"{name} is not covered by the freeze manifest")

    # models config parses
    try:
        configured = apply_endpoint_overrides(load_models(), endpoint_overrides_for(loaded.id))
        if len(configured) < 5:
            warnings.append(
                f"only {len(configured)} models configured; v0.1 expects at least 5"
            )
    except ConfigError as exc:
        problems.append(str(exc))

    # no secrets committed
    env_file = repo_root() / ".env"
    if env_file.exists():
        gitignore = repo_root() / ".gitignore"
        ignored = gitignore.exists() and ".env" in gitignore.read_text(encoding="utf-8")
        if not ignored:
            problems.append(".env exists but is not listed in .gitignore")
    scanned = [repo_root() / "models.yaml", *sorted((repo_root() / "evaluators").glob("*.yaml"))]
    for path in scanned:
        if not path.exists():
            continue
        for line_number, hit in find_literal_credentials(path.read_text(encoding="utf-8")):
            problems.append(
                f"{path.name}:{line_number} looks like a literal credential ({hit}) - "
                f"configs must name an environment variable, not hold the value"
            )

    # report
    console.print(f"[bold]scenario[/bold]  {loaded.id} - {loaded.name}")
    console.print(f"[bold]sources[/bold]   {', '.join(loaded.sources)}")
    console.print(
        f"[bold]rubric[/bold]    {rubric_file} (version {rubric.version})"
    )
    console.print(f"[bold]criteria[/bold]  {len(rubric.criteria)} across {len(rubric.dimension_max)} dimensions")
    if prompt is not None:
        console.print(f"[bold]prompt[/bold]    sha256 {prompt.sha256}")
        console.print(f"[bold]size[/bold]      {len(prompt.text)} chars (~{prompt.estimated_tokens()} tokens)")

    for warning in warnings:
        console.print(f"[yellow]warning[/yellow] {warning}")

    if problems:
        console.print()
        for problem in problems:
            console.print(f"[bold red]FAIL[/bold red] {problem}")
        raise typer.Exit(code=1)

    console.print()
    console.print("[bold green]validation passed[/bold green]")


# --------------------------------------------------------------------------
# run
# --------------------------------------------------------------------------


@app.command()
def run(
    scenario: str = typer.Option(..., "--scenario"),
    model: str | None = typer.Option(None, "--model"),
    models_csv: str | None = typer.Option(
        None, "--models", help="Comma-separated slugs, e.g. glm5.2,gemma4"
    ),
    all_models: bool = typer.Option(False, "--all-models"),
    runs: int = typer.Option(0, "--runs", help="Defaults to the scenario's official_runs"),
    reuse_valid_runs: bool = typer.Option(
        False,
        "--reuse-valid-runs",
        help="Count existing official runs and generate only the shortfall",
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Resolve everything, call nothing"),
    overwrite: bool = typer.Option(False, "--overwrite"),
) -> None:
    """Generate raw model responses and store them as immutable evidence."""
    try:
        loaded = load_scenario(scenario)
        configured = apply_endpoint_overrides(load_models(), endpoint_overrides_for(loaded.id))
    except (ScenarioError, ConfigError) as exc:
        _fail(str(exc))
        return

    explicit = parse_model_list(models_csv)
    if explicit:
        unknown = [s for s in explicit if s not in configured]
        if unknown:
            _fail(f"unknown model(s): {', '.join(unknown)}")
        if model or all_models:
            _fail("pass only one of --model, --models or --all-models")
        slugs = explicit
    else:
        slugs = _resolve_model_slugs(model, all_models, configured)

    prompt = build_prompt(loaded)
    total_runs = runs or loaded.official_runs

    # --reuse-valid-runs turns "generate N runs" into "reach N official runs".
    # Existing official runs are counted, only the shortfall is generated, and
    # run numbers already on disk are never reused - so nothing is overwritten
    # even when an existing run was rejected as unofficial.
    schedule: dict[str, list[int]] = {}
    if reuse_valid_runs:
        if overwrite:
            _fail("--reuse-valid-runs and --overwrite contradict each other")
        plans = plan_battery(
            scenario_id=loaded.id,
            model_slugs=slugs,
            models=configured,
            expected_prompt_sha256=prompt.sha256,
            target=total_runs,
            expected_max_output_tokens=loaded.safety_ceiling_tokens,
        )
        for slug in slugs:
            plan = plans[slug]
            schedule[slug] = plan.next_run_numbers()
            detail = f"{plan.have} official, {plan.missing} to generate"
            if plan.rejected:
                detail += f", {len(plan.rejected)} rejected"
            console.print(f"[bold]{slug}[/bold]  {detail}")
            for verdict in plan.rejected:
                console.print(
                    f"  [yellow]rejected[/yellow] {verdict.path.name}: "
                    f"{'; '.join(verdict.reasons)}"
                )
    else:
        schedule = {slug: list(range(1, total_runs + 1)) for slug in slugs}

    planned = sum(len(v) for v in schedule.values())

    if dry_run:
        for slug in slugs:
            report = dry_run_report(loaded, configured[slug], prompt)
            report["run_numbers_to_generate"] = schedule[slug]
            console.print_json(json.dumps(report))
        console.print(
            f"[yellow]dry run - no API calls were made "
            f"({planned} inference(s) would run)[/yellow]"
        )
        return

    if not planned:
        console.print("[green]nothing to generate: every model already has its official runs[/green]")
        return

    failures = 0
    for slug in slugs:
        cfg = configured[slug]
        for run_number in schedule[slug]:
            label = f"{slug} run {run_number} (target {total_runs})"
            try:
                result = execute_run(
                    scenario=loaded,
                    model=cfg,
                    run_number=run_number,
                    prompt=prompt,
                    overwrite=overwrite,
                )
            except RunExistsError as exc:
                console.print(f"[yellow]skip[/yellow] {label}: {exc}")
                continue
            except (ProviderError, ConfigError) as exc:
                failures += 1
                log_failed_attempt(
                    scenario_id=loaded.id,
                    model_slug=slug,
                    run_number=run_number,
                    error=str(exc),
                    kind=getattr(exc, "kind", "error"),
                )
                console.print(f"[bold red]fail[/bold red] {label}: {exc}")
                continue

            truncated = " [yellow](truncated: finish_reason=length)[/yellow]" if result.finish_reason == "length" else ""
            console.print(
                f"[green]ok[/green]   {label}  "
                f"{result.usage.output_tokens or '?'} out tok  "
                f"{result.performance.total_latency_ms} ms{truncated}"
            )

    if failures:
        raise typer.Exit(code=1)


# --------------------------------------------------------------------------
# evaluate
# --------------------------------------------------------------------------


@app.command()
def evaluate(
    scenario: str = typer.Option(..., "--scenario"),
    model: str | None = typer.Option(None, "--model"),
    models_csv: str | None = typer.Option(None, "--models", help="Comma-separated slugs"),
    all_models: bool = typer.Option(False, "--all-models"),
    evaluator: str | None = typer.Option(None, "--evaluator", help=EVALUATOR_HELP),
    verdicts: Path | None = typer.Option(
        None,
        "--verdicts",
        help="Score from a recorded verdict file instead of calling a judge model",
    ),
    review: bool = typer.Option(False, "--review", help="Also write a human-audit review file"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Re-evaluate runs already evaluated"),
) -> None:
    """Classify every stored run against the rubric and score it deterministically."""
    evaluator = _evaluator_for(scenario, evaluator, fallback=DEFAULT_EVALUATOR)
    try:
        evaluator_cfg = load_evaluator(evaluator)
        loaded = load_scenario(scenario, rubric_file=evaluator_cfg.rubric_file)
    except (ScenarioError, ConfigError) as exc:
        _fail(str(exc))
        return

    explicit = parse_model_list(models_csv)
    if sum(bool(x) for x in (explicit, model, all_models)) > 1:
        _fail("pass only one of --model, --models or --all-models")
    if explicit:
        slugs = explicit
    elif all_models:
        slugs = models_with_runs(loaded.id)
        if not slugs:
            _fail(f"no runs found under runs/{loaded.id}/ - run the models first")
    elif model:
        slugs = [model]
    else:
        _fail("pass --model <slug>, --models a,b,c or --all-models")
        return

    recorded = verdicts is not None
    try:
        if recorded:
            assert verdicts is not None
            judge = RecordedJudge(
                evaluator_cfg, VerdictStore.load(verdicts), source=verdicts.name
            )
        else:
            judge = Judge(evaluator_cfg)
    except (ConfigError, ProviderError, JudgeError) as exc:
        _fail(str(exc))
        return

    failures = 0
    for slug in slugs:
        run_paths = find_runs(loaded.id, slug)
        if not run_paths:
            console.print(f"[yellow]skip[/yellow] {slug}: no runs found")
            continue
        already = {p.name for p in find_evaluations(evaluator, loaded.id, slug)}
        for path in run_paths:
            if path.name in already and not overwrite:
                console.print(f"[yellow]skip[/yellow] {slug} {path.name}: already evaluated")
                continue
            raw = load_run(path)
            try:
                if recorded:
                    judge.bind(raw.run_id)  # type: ignore[attr-defined]
                evaluation = evaluate_run(
                    scenario=loaded, evaluator=evaluator_cfg, run=raw, judge=judge
                )
            except (JudgeError, KeyError) as exc:
                failures += 1
                console.print(f"[bold red]fail[/bold red] {slug} {path.name}: {exc}")
                continue

            if review:
                write_review(evaluation, raw.response, raw.run_number)

            flags = []
            if evaluation.penalties.items:
                flags.append(f"penalties {evaluation.penalties.total}")
            if evaluation.disagreements:
                flags.append(f"{len(evaluation.disagreements)} disagreement(s)")
            suffix = f"  [yellow]{', '.join(flags)}[/yellow]" if flags else ""
            console.print(
                f"[green]ok[/green]   {slug} {path.name}  "
                f"base {evaluation.base_score}  final {evaluation.final_score}{suffix}"
            )
            for disagreement in evaluation.disagreements:
                console.print(f"       [yellow]WARNING[/yellow] {disagreement.message}")

    if recorded:
        console.print(f"\nrecorded verdicts served: {judge.stats.calls} (no API calls)")
    else:
        console.print(
            f"\njudge calls: {judge.stats.calls}  json repairs: {judge.stats.repairs}  "
            f"judge tokens: {judge.stats.input_tokens} in / {judge.stats.output_tokens} out"
        )
    if judge.stats.unsupported_parameters:
        console.print(
            f"[yellow]note[/yellow] judge dropped unsupported parameters: "
            f"{', '.join(judge.stats.unsupported_parameters)}"
        )

    if failures:
        raise typer.Exit(code=1)


# --------------------------------------------------------------------------
# leaderboard
# --------------------------------------------------------------------------


@app.command()
def leaderboard(
    scenario: str = typer.Option(..., "--scenario"),
    evaluator: str | None = typer.Option(None, "--evaluator", help=EVALUATOR_HELP),
    official: bool = typer.Option(
        False, "--official", help="Enforce every publication gate; write nothing if any fails"
    ),
    models_csv: str | None = typer.Option(
        None, "--models", help="Official battery membership (with --official)"
    ),
    runs: int = typer.Option(3, "--runs", help="Official runs required per model"),
    calibration: bool = typer.Option(
        False,
        "--calibration",
        help="Rank a calibration draft into analysis/leaderboards/ instead of leaderboard/",
    ),
) -> None:
    """Aggregate evaluations into the published ranking."""
    evaluator = _evaluator_for(scenario, evaluator, fallback=DEFAULT_EVALUATOR)
    if official:
        cmd_publish(scenario, evaluator, models_csv, runs)
        return
    try:
        loaded = load_scenario(scenario)
    except ScenarioError as exc:
        _fail(str(exc))
        return

    # A calibration draft has one run per model against a rubric that is still
    # moving. Written into `leaderboard/` it is indistinguishable from a
    # published result, which is how monday-003 v0.2 briefly acquired one.
    if loaded.is_calibration and not calibration:
        _fail(
            f"{loaded.id} is status={loaded.status}: it has no publishable ranking. "
            "Use --calibration to write a draft ranking under analysis/leaderboards/, "
            "or freeze the scenario first."
        )
        return
    if calibration and not loaded.is_calibration:
        _fail(
            f"--calibration is only for scenarios with status: calibration; "
            f"{loaded.id} is status={loaded.status}"
        )
        return

    payload, summaries = build_leaderboard(
        scenario_id=loaded.id,
        evaluator_id=evaluator,
        benchmark_version=loaded.benchmark_version or BENCHMARK_VERSION,
        scenario_status=loaded.status,
        expected_max_output_tokens=loaded.safety_ceiling_tokens,
        endpoint_overrides=endpoint_overrides_for(loaded.id),
    )
    if not summaries:
        _fail(f"no evaluations found under evaluations/{evaluator}/{loaded.id}/")

    table = Table(title=f"MondayBench {loaded.id} ({evaluator})", box=None, pad_edge=False)
    table.add_column("#", justify="right")
    table.add_column("model")
    table.add_column("score", justify="right")
    table.add_column("range", justify="right")
    table.add_column("sigma", justify="right")
    # Dimension columns come from what was actually scored, not from a fixed
    # list. They used to be hardcoded to monday-001's six names, so every later
    # scenario printed a row of zeros under headings from a different rubric.
    dimension_keys = sorted({k for s in summaries for k in s.dimensions})
    for key in dimension_keys:
        table.add_column(_dimension_heading(key), justify="right")
    table.add_column("cost/run", justify="right")
    table.add_column("TTFA med", justify="right")
    table.add_column("total med", justify="right")

    for s in summaries:
        table.add_row(
            str(s.rank),
            s.display_name,
            f"{s.mean:.1f}",
            f"{s.minimum:.0f}-{s.maximum:.0f}",
            f"{s.stddev:.2f}",
            *(f"{s.dimensions.get(key, 0):.1f}" for key in dimension_keys),
            "-" if s.median_cost_usd is None else f"${s.median_cost_usd:.4f}",
            "-" if s.median_ttfa_ms is None else f"{s.median_ttfa_ms / 1000:.1f}s",
            "-"
            if s.median_total_latency_ms is None
            else f"{s.median_total_latency_ms / 1000:.1f}s",
        )
    console.print(table)

    if payload.get("integrity_warning"):
        console.print(f"\n[bold red]{payload['integrity_warning']}[/bold red]")

    for s in summaries:
        for warning in s.warnings:
            console.print(f"[yellow]warning[/yellow] {s.model_slug}: {warning}")

    try:
        json_path, csv_path, md_path = write_leaderboard(
            payload, summaries, calibration=calibration
        )
    except ValueError as exc:
        _fail(str(exc))
        return
    console.print("")
    if calibration:
        console.print(
            "[yellow]calibration draft - not an official result, not comparable with any "
            "published leaderboard[/yellow]"
        )
    for path in (json_path, csv_path, md_path):
        console.print(f"wrote {path.relative_to(repo_root())}")


@app.command()
def freeze(
    scenario: str = typer.Option(..., "--scenario"),
    evaluator: str | None = typer.Option(None, "--evaluator", help=EVALUATOR_HELP),
    check: bool = typer.Option(False, "--check", help="Verify the manifest instead of writing it"),
) -> None:
    """Freeze a scenario's canonical content, or verify a frozen one is intact."""
    cmd_freeze(scenario, _evaluator_for(scenario, evaluator, fallback=OFFICIAL_EVALUATOR), check)


@app.command()
def plan(
    scenario: str = typer.Option(..., "--scenario"),
    models_csv: str | None = typer.Option(None, "--models"),
    runs: int = typer.Option(3, "--runs"),
    evaluator: str | None = typer.Option(None, "--evaluator", help=EVALUATOR_HELP),
) -> None:
    """Show which stored runs are official and how many inferences are still needed."""
    cmd_plan(
        scenario, models_csv, runs, _evaluator_for(scenario, evaluator, fallback=OFFICIAL_EVALUATOR)
    )


@app.command()
def results(
    scenario: str = typer.Option(..., "--scenario"),
    evaluator: str | None = typer.Option(None, "--evaluator", help=EVALUATOR_HELP),
) -> None:
    """Write one public JSON file per model under leaderboard/models/."""
    cmd_results(scenario, _evaluator_for(scenario, evaluator, fallback=OFFICIAL_EVALUATOR))


@app.command()
def overall(
    version: int = typer.Option(..., "--version", help="Overall release version from overall-releases.yaml"),
    preview: bool = typer.Option(
        False,
        "--preview",
        help="Write a clearly-labelled non-official preview to analysis/overall/ instead",
    ),
) -> None:
    """Aggregate official scenario leaderboards into one Monday Score."""
    from .overall import OverallError, build_overall, load_releases, write_overall

    try:
        releases = load_releases()
    except OverallError as exc:
        _fail(str(exc))
        return
    release = releases.get(version)
    if release is None:
        _fail(
            f"no overall release v{version}; declared: "
            + ", ".join(f"v{v}" for v in sorted(releases))
        )
        return

    try:
        payload, ranked, incomplete = build_overall(release, require_released=not preview)
    except OverallError as exc:
        console.print(f"[bold red]refusing to build[/bold red] {len(exc.blockers)} blocker(s):\n")
        for blocker in exc.blockers:
            console.print(f"  [red]-[/red] {blocker}")
        console.print(
            "\nNothing was written. An Overall score is a claim that these scenario results "
            "are comparable and complete; each blocker above says they are not."
        )
        raise typer.Exit(code=1)

    ids = release.scenario_ids
    table = Table(
        title=f"MondayBench Overall v{release.version}"
        + ("  [PREVIEW - NOT OFFICIAL]" if preview else ""),
        box=None,
    )
    table.add_column("#", justify="right")
    table.add_column("model")
    table.add_column("Monday Score", justify="right")
    for scenario_id in ids:
        table.add_column(scenario_id.replace("monday-", "#"), justify="right")
    table.add_column("range", justify="right")
    table.add_column("sigma", justify="right")
    for entry in ranked:
        table.add_row(
            str(entry.rank),
            entry.display_name,
            f"{entry.monday_score:.2f}",
            *(f"{entry.scenario_scores[s]:.1f}" for s in ids),
            f"{entry.scenario_range:.1f}",
            f"{entry.scenario_stddev:.2f}",
        )
    console.print(table)
    console.print(
        "\nrange/sigma above are variation ACROSS scenarios, not run-to-run stability."
    )
    for entry in incomplete:
        console.print(
            f"[yellow]not ranked[/yellow] {entry.display_name}: missing "
            + ", ".join(entry.missing)
        )

    json_path, csv_path, md_path = write_overall(
        payload, ranked, incomplete, release, preview=preview
    )
    console.print("")
    if preview:
        console.print(
            "[yellow]preview[/yellow] - not an official result, not comparable with a "
            "published Overall score"
        )
    for path in (json_path, csv_path, md_path):
        console.print(f"wrote {path.relative_to(repo_root())}")


# --------------------------------------------------------------------------
# benchmark (full pipeline)
# --------------------------------------------------------------------------


@app.command()
def benchmark(
    ctx: typer.Context,
    scenario: str = typer.Option(..., "--scenario"),
    model: str | None = typer.Option(None, "--model"),
    models_csv: str | None = typer.Option(None, "--models", help="Comma-separated slugs"),
    all_models: bool = typer.Option(False, "--all-models"),
    runs: int = typer.Option(0, "--runs"),
    reuse_valid_runs: bool = typer.Option(
        False, "--reuse-valid-runs", help="Reach --runs official runs, generating only the shortfall"
    ),
    evaluator: str | None = typer.Option(None, "--evaluator", help=EVALUATOR_HELP),
    review: bool = typer.Option(False, "--review"),
    official: bool = typer.Option(False, "--official", help="Enforce the publication gates"),
    overwrite: bool = typer.Option(False, "--overwrite"),
) -> None:
    """validate -> run -> evaluate -> leaderboard, in one command."""
    evaluator = _evaluator_for(scenario, evaluator, fallback=DEFAULT_EVALUATOR)
    console.rule("[bold]validate")
    ctx.invoke(validate, scenario=scenario, evaluator=evaluator)

    console.rule("[bold]run")
    ctx.invoke(
        run,
        scenario=scenario,
        model=model,
        models_csv=models_csv,
        all_models=all_models,
        runs=runs,
        reuse_valid_runs=reuse_valid_runs,
        dry_run=False,
        overwrite=overwrite,
    )

    console.rule("[bold]evaluate")
    ctx.invoke(
        evaluate,
        scenario=scenario,
        model=model,
        models_csv=models_csv,
        all_models=all_models,
        evaluator=evaluator,
        review=review,
        overwrite=overwrite,
    )

    console.rule("[bold]leaderboard")
    ctx.invoke(
        leaderboard,
        scenario=scenario,
        evaluator=evaluator,
        official=official,
        models_csv=models_csv,
        runs=runs or 3,
    )


# --------------------------------------------------------------------------
# prompt (utility: see exactly what a model is sent)
# --------------------------------------------------------------------------


@app.command()
def prompt(
    scenario: str = typer.Option(..., "--scenario"),
    out: Path | None = typer.Option(None, "--out", help="Write the prompt to a file"),
    hash_only: bool = typer.Option(False, "--hash-only"),
) -> None:
    """Print the exact assembled prompt, or just its hash."""
    try:
        loaded = load_scenario(scenario)
    except ScenarioError as exc:
        _fail(str(exc))
        return
    built = build_prompt(loaded)
    if hash_only:
        console.print(built.sha256)
        return
    if out:
        out.write_text(built.text, encoding="utf-8", newline="\n")
        console.print(f"wrote {out} (sha256 {built.sha256})")
        return
    print(built.text)


if __name__ == "__main__":  # pragma: no cover
    app()
