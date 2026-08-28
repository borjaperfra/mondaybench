"""Aggregate evaluations into a ranking.

Official score for a model is the plain mean of its official runs. No dropping
the worst run, no best-of-N. Range and standard deviation are published
alongside so a lucky run is visible as one.
"""

from __future__ import annotations

import csv
import json
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import repo_root
from .evaluator import find_evaluations, load_evaluation, models_with_evaluations
from .runner import find_runs, load_run
from .schemas import Evaluation


@dataclass
class ModelSummary:
    model_slug: str
    display_name: str
    runs: int
    mean: float
    minimum: float
    maximum: float
    stddev: float
    dimensions: dict[str, float]
    # Rubric declaration order for those dimensions. Deliberately not
    # serialized: it is a rendering concern, and adding a key to the payload
    # would rewrite leaderboards that are already published.
    # Medians, not means: with three runs a single slow or expensive outlier
    # drags a mean somewhere no run actually was.
    median_ttfa_ms: float | None
    median_total_latency_ms: float | None
    median_cost_usd: float | None
    median_ttft_ms: float | None
    median_output_tokens: float | None
    prompt_sha256: str
    # Per-dimension maximum, read from the rubric via the evaluations, so a
    # renderer never has to look a scenario's rubric up. Defaulted because
    # callers that only exercise the gates do not need it.
    dimension_max: dict[str, float] = field(default_factory=dict)
    # Rubric declaration order for the dimensions above. Deliberately not
    # serialized: it is a rendering concern, and adding a key to the payload
    # would rewrite leaderboards that are already published.
    dimension_order: list[str] = field(default_factory=list)
    run_scores: list[float] = field(default_factory=list)
    rubric_version: str | None = None
    judge_model_id: str | None = None
    rank: int = 0
    warnings: list[str] = field(default_factory=list)
    # Per-criterion detail, for the public breakdown. Kept off the score path.
    missed: list[dict[str, Any]] = field(default_factory=list)
    got_wrong: list[dict[str, Any]] = field(default_factory=list)
    run_paths: list[str] = field(default_factory=list)
    evaluation_paths: list[str] = field(default_factory=list)

    @property
    def score_range(self) -> float:
        """run_range - the simplest stability signal there is.

        Deliberately not combined with speed or cost into any composite: the
        Monday Score measures task quality only.
        """
        return round(self.maximum - self.minimum, 2)


def _mean_or_none(values: list[float]) -> float | None:
    present = [v for v in values if v is not None]
    if not present:
        return None
    return round(statistics.fmean(present), 2)


def _median_or_none(values: list[float]) -> float | None:
    present = [v for v in values if v is not None]
    if not present:
        return None
    return round(statistics.median(present), 4)


def summarize_model(
    *,
    scenario_id: str,
    evaluator_id: str,
    model_slug: str,
    root: Path | None = None,
) -> ModelSummary | None:
    """Collect one model's evaluations plus the run metadata they point at."""
    evaluation_paths = find_evaluations(evaluator_id, scenario_id, model_slug, root)
    if not evaluation_paths:
        return None

    evaluations: list[Evaluation] = [load_evaluation(p) for p in evaluation_paths]
    scores = [e.final_score for e in evaluations]

    run_by_id = {}
    run_path_by_id = {}
    for path in find_runs(scenario_id, model_slug, root):
        run = load_run(path)
        run_by_id[run.run_id] = run
        run_path_by_id[run.run_id] = path

    warnings: list[str] = []
    display_name = model_slug
    latencies: list[float] = []
    ttfts: list[float] = []
    ttfas: list[float] = []
    output_tokens: list[float] = []
    costs: list[float] = []
    prompt_hashes: set[str] = set()
    base = root or repo_root()

    def _rel(path: Path) -> str:
        try:
            return path.relative_to(base).as_posix()
        except ValueError:
            return path.as_posix()

    run_paths: list[str] = []
    evaluation_paths: list[str] = [_rel(p) for p in evaluation_paths]

    for evaluation in evaluations:
        prompt_hashes.add(evaluation.scenario_prompt_sha256)
        run = run_by_id.get(evaluation.run_id)
        if run is None:
            warnings.append(f"evaluation {evaluation.run_id} has no matching raw run file")
            continue
        display_name = run.model.display_name
        if run.performance.total_latency_ms is not None:
            latencies.append(run.performance.total_latency_ms)
        if run.performance.ttft_ms is not None:
            ttfts.append(run.performance.ttft_ms)
        if run.performance.ttfa_ms is not None:
            ttfas.append(run.performance.ttfa_ms)
        run_paths.append(_rel(run_path_by_id[evaluation.run_id]))
        if run.usage.output_tokens is not None:
            output_tokens.append(float(run.usage.output_tokens))
        if run.economics.total_cost_usd is not None:
            costs.append(run.economics.total_cost_usd)
        if run.finish_reason == "length":
            warnings.append(f"{run.run_id} hit max_output_tokens (finish_reason=length)")

    if len(prompt_hashes) > 1:
        warnings.append(
            "runs were generated against more than one prompt hash - not comparable: "
            + ", ".join(sorted(h[:12] for h in prompt_hashes))
        )

    fingerprints = {e.judge.prompt_fingerprint for e in evaluations}
    if len(fingerprints) > 1:
        warnings.append(
            "evaluations came from more than one judge prompt version - not comparable: "
            + ", ".join(sorted(str(f) for f in fingerprints))
            + " (re-evaluate all runs with --overwrite)"
        )

    # Cost is only meaningful when every run priced; a partial figure would lie.
    median_cost = _median_or_none(costs) if len(costs) == len(evaluations) else None

    # "What it missed": every criterion that was not a clean PASS in any run.
    # "What it got wrong": every scored penalty and every triggered false action.
    missed: list[dict[str, Any]] = []
    got_wrong: list[dict[str, Any]] = []
    for evaluation in evaluations:
        for criterion_id, result in evaluation.criteria.items():
            if result.result == "PASS":
                continue
            missed.append(
                {
                    "run_id": evaluation.run_id,
                    "criterion": criterion_id,
                    "result": result.result,
                    "points_awarded": result.points_awarded,
                    "points_possible": result.points_possible,
                    "reason": result.reason,
                    "evidence": result.evidence,
                }
            )
        for action_id, action in evaluation.false_actions.items():
            if not action.triggered:
                continue
            got_wrong.append(
                {
                    "run_id": evaluation.run_id,
                    "type": "FALSE_ACTION",
                    "id": action_id,
                    "points": action.points,
                    "reason": action.description,
                    "evidence": action.evidence,
                }
            )
        for item in evaluation.penalties.items:
            got_wrong.append(
                {
                    "run_id": evaluation.run_id,
                    "type": item.type,
                    "id": item.type,
                    "points": item.points,
                    "reason": item.reason,
                    "evidence": item.evidence,
                }
            )

    dimension_names = sorted({name for e in evaluations for name in e.dimensions})
    dimensions = {
        name: round(
            statistics.fmean(
                [e.dimensions[name].score for e in evaluations if name in e.dimensions]
            ),
            2,
        )
        for name in dimension_names
    }
    # The maxima come from the evaluations, which got them from the scenario's
    # own rubric. Nothing downstream should carry a list of dimension names: a
    # renderer that knows monday-001's six dimensions will print them for every
    # scenario forever, silently scoring the real ones as absent.
    dimension_max = {
        name: max(
            e.dimensions[name].max_score for e in evaluations if name in e.dimensions
        )
        for name in dimension_names
    }

    return ModelSummary(
        model_slug=model_slug,
        display_name=display_name,
        runs=len(scores),
        mean=round(statistics.fmean(scores), 2),
        minimum=round(min(scores), 2),
        maximum=round(max(scores), 2),
        stddev=round(statistics.stdev(scores), 2) if len(scores) > 1 else 0.0,
        dimensions=dimensions,
        dimension_max=dimension_max,
        median_ttfa_ms=_median_or_none(ttfas),
        median_total_latency_ms=_median_or_none(latencies),
        median_cost_usd=median_cost,
        median_ttft_ms=_median_or_none(ttfts),
        median_output_tokens=_median_or_none(output_tokens),
        prompt_sha256=sorted(prompt_hashes)[0] if prompt_hashes else "",
        run_scores=[round(s, 2) for s in scores],
        rubric_version=next((e.rubric_version for e in evaluations), None),
        judge_model_id=next((e.judge.model_id for e in evaluations), None),
        warnings=warnings,
        missed=missed,
        got_wrong=got_wrong,
        run_paths=run_paths,
        evaluation_paths=evaluation_paths,
    )


def build_leaderboard(
    *,
    scenario_id: str,
    evaluator_id: str,
    benchmark_version: str,
    root: Path | None = None,
) -> tuple[dict[str, Any], list[ModelSummary]]:
    summaries: list[ModelSummary] = []
    for model_slug in models_with_evaluations(evaluator_id, scenario_id, root):
        summary = summarize_model(
            scenario_id=scenario_id,
            evaluator_id=evaluator_id,
            model_slug=model_slug,
            root=root,
        )
        if summary is not None:
            summaries.append(summary)

    summaries.sort(key=lambda s: (-s.mean, s.model_slug))
    order = rubric_dimension_order(scenario_id, evaluator_id)
    for index, summary in enumerate(summaries, start=1):
        summary.rank = index
        summary.dimension_order = order

    # A ranking that blends judge prompt versions across models is not a ranking.
    # Detected here, across models, because a single model can be internally
    # consistent while the field as a whole is not.
    all_fingerprints: set[str] = set()
    for model_slug in models_with_evaluations(evaluator_id, scenario_id, root):
        for path in find_evaluations(evaluator_id, scenario_id, model_slug, root):
            evaluation = load_evaluation(path)
            # Rubric version and judge instructions both change what a score
            # means, so they form one comparability key.
            all_fingerprints.add(
                f"rubric={evaluation.rubric_version}/"
                f"judge={evaluation.judge.prompt_fingerprint}"
            )
    cross_model_warning = (
        f"MIXED JUDGE VERSIONS across models ({len(all_fingerprints)} distinct): "
        + ", ".join(sorted(all_fingerprints))
        + " - this ranking is not valid; re-evaluate every run with --overwrite"
        if len(all_fingerprints) > 1
        else None
    )

    payload = {
        "benchmark_version": benchmark_version,
        "scenario": scenario_id,
        "evaluator": evaluator_id,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "integrity_warning": cross_model_warning,
        "models": [
            {
                "rank": s.rank,
                "model_slug": s.model_slug,
                "display_name": s.display_name,
                # The Monday Score. Task quality only - no speed, no cost.
                "score": {
                    "mean": s.mean,
                    "min": s.minimum,
                    "max": s.maximum,
                    "range": s.score_range,
                    "stddev": s.stddev,
                    "runs": s.runs,
                },
                "run_scores": s.run_scores,
                "dimensions": s.dimensions,
                # Recorded alongside the score and never folded into it.
                "performance": {
                    "median_ttfa_ms": s.median_ttfa_ms,
                    "median_ttft_ms": s.median_ttft_ms,
                    "median_total_latency_ms": s.median_total_latency_ms,
                    "median_output_tokens": s.median_output_tokens,
                },
                "economics": {"median_cost_usd": s.median_cost_usd},
                "provenance": {
                    "scenario_prompt_sha256": s.prompt_sha256,
                    "rubric_version": s.rubric_version,
                    "judge_model_id": s.judge_model_id,
                    "runs": s.run_paths,
                    "evaluations": s.evaluation_paths,
                },
                "missed": s.missed,
                "got_wrong": s.got_wrong,
                "warnings": s.warnings,
            }
            for s in summaries
        ],
    }
    return payload, summaries


def dimension_columns(summaries: "list[ModelSummary]") -> list[str]:
    """The dimension names this scenario scores, in the rubric's own order.

    Derived per scenario rather than declared here, so a new scenario with new
    dimensions publishes correctly without touching this module. The rubric's
    declaration order wins where it is known; otherwise the fallback is heaviest
    first, then alphabetically, which at least is stable.
    """
    names: dict[str, float] = {}
    for s in summaries:
        for name, maximum in s.dimension_max.items():
            names[name] = max(names.get(name, 0.0), maximum)
    declared = [n for n in (summaries[0].dimension_order if summaries else []) if n in names]
    rest = sorted((n for n in names if n not in declared), key=lambda n: (-names[n], n))
    return declared + rest


def rubric_dimension_order(scenario_id: str, evaluator_id: str) -> list[str]:
    """Dimension names in the order the scenario's rubric declares them.

    Returns an empty list when the scenario cannot be loaded - tests build
    summaries from fixtures with no scenario on disk, and a missing order is a
    rendering nicety, not a correctness problem.
    """
    try:
        from .config import ConfigError, load_evaluator
        from .scenarios import ScenarioError, load_scenario

        evaluator = load_evaluator(evaluator_id)
        scenario = load_scenario(scenario_id, rubric_file=evaluator.rubric_file)
        return list(scenario.rubric.dimension_max)
    except (ConfigError, ScenarioError, OSError, KeyError):
        return []


def leaderboard_dir(scenario_id: str | None, root: Path | None = None) -> Path:
    """Where a scenario's published leaderboard lives.

    monday-001 was published when the repository held one scenario, straight
    into `leaderboard/`. Those files are the public v0.1 result and cannot move,
    so that path stays its own. Every scenario after it gets
    `leaderboard/<scenario_id>/`, which is what keeps a second publication from
    overwriting the first.
    """
    base = (root or repo_root()) / "leaderboard"
    if scenario_id in (None, "", "monday-001"):
        return base
    return base / scenario_id


def write_leaderboard(
    payload: dict[str, Any], summaries: list[ModelSummary], root: Path | None = None
) -> tuple[Path, Path, Path]:
    directory = leaderboard_dir(payload.get("scenario"), root)
    directory.mkdir(parents=True, exist_ok=True)

    json_path = directory / "leaderboard.json"
    json_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    csv_path = directory / "leaderboard.csv"
    csv_dimensions = dimension_columns(summaries)
    columns = [
        "rank",
        "model_slug",
        "display_name",
        "monday_score",
        "score_min",
        "score_max",
        "run_range",
        "score_stddev",
        "runs",
        *csv_dimensions,
        "median_ttfa_ms",
        "median_ttft_ms",
        "median_total_latency_ms",
        "median_output_tokens",
        "median_cost_usd",
        "rubric_version",
        "judge_model_id",
        "scenario_prompt_sha256",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for s in summaries:
            row: dict[str, Any] = {
                "rank": s.rank,
                "model_slug": s.model_slug,
                "display_name": s.display_name,
                "monday_score": s.mean,
                "score_min": s.minimum,
                "score_max": s.maximum,
                "run_range": s.score_range,
                "score_stddev": s.stddev,
                "runs": s.runs,
                "median_ttfa_ms": s.median_ttfa_ms,
                "median_ttft_ms": s.median_ttft_ms,
                "median_total_latency_ms": s.median_total_latency_ms,
                "median_output_tokens": s.median_output_tokens,
                "median_cost_usd": s.median_cost_usd,
                "rubric_version": s.rubric_version,
                "judge_model_id": s.judge_model_id,
                "scenario_prompt_sha256": s.prompt_sha256,
            }
            for name in csv_dimensions:
                row[name] = s.dimensions.get(name)
            writer.writerow(row)

    md_path = directory / "leaderboard.md"
    md_path.write_text(render_markdown(payload, summaries), encoding="utf-8")

    return json_path, csv_path, md_path


# --------------------------------------------------------------------------
# Public markdown
# --------------------------------------------------------------------------

def dimension_label(name: str) -> str:
    """`some_long_dimension` -> `Some long dimension`.

    No scenario's dimension names appear anywhere in this module, by design.
    """
    return name.replace("_", " ").capitalize()


def _ms(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{value / 1000:.1f}s"


def _usd(value: float | None) -> str:
    if value is None:
        return "-"
    return f"${value:.4f}"


def render_markdown(payload: dict[str, Any], summaries: list[ModelSummary]) -> str:
    lines: list[str] = []
    scenario = payload.get("scenario", "")
    lines.append(f"# MondayBench {payload.get('benchmark_version', '')} - `{scenario}`")
    lines.append("")
    lines.append(f"**Evaluator:** `{payload.get('evaluator', '')}`  ")
    if summaries:
        lines.append(f"**Rubric:** {summaries[0].rubric_version}  ")
        lines.append(f"**Judge:** `{summaries[0].judge_model_id}`  ")
        lines.append(f"**Prompt SHA-256:** `{summaries[0].prompt_sha256}`  ")
    lines.append(f"**Generated:** {payload.get('generated_at', '')}")
    lines.append("")
    # The version comes from the scenario, not from a literal. monday-001
    # declares 0.1 and monday-002 declares 0.2; hardcoding either one mislabels
    # the other.
    version = payload.get("benchmark_version", "")
    if payload.get("official"):
        lines.append(
            f"**Status:** official v{version} result. Every publication gate passed."
            if version
            else "**Status:** official. Every publication gate passed."
        )
    else:
        lines.append(
            "> **NOT AN OFFICIAL RESULT.** This leaderboard was built without "
            "`--official`, so the publication gates were not enforced: run counts, "
            "prompt/rubric/judge consistency and scoring arithmetic are unverified. "
            f"Do not cite these numbers as MondayBench v{version} results."
        )
    lines.append("")
    if payload.get("integrity_warning"):
        lines.append(f"> **INTEGRITY WARNING** {payload['integrity_warning']}")
        lines.append("")

    lines.append(
        "The Monday Score is the mean of each model's official runs and measures task "
        "quality only. TTFA, latency and cost sit beside it and are never folded into it."
    )
    lines.append("")

    lines.append("| Rank | Model | Monday Score | Runs | Range | TTFA median | Total median |")
    lines.append("|---:|---|---:|---:|---:|---:|---:|")
    for s in summaries:
        lines.append(
            f"| {s.rank} | {s.display_name} | **{s.mean:.1f}** | {s.runs} | "
            f"{s.score_range:.1f} | {_ms(s.median_ttfa_ms)} | {_ms(s.median_total_latency_ms)} |"
        )
    lines.append("")
    lines.append("---")
    lines.append("")

    for s in summaries:
        lines.append(f"## {s.rank}. {s.display_name} - {s.mean:.1f} / 100")
        lines.append("")
        lines.append(f"`{s.model_slug}`")
        lines.append("")
        lines.append("| Dimension | Score | Max |")
        lines.append("|---|---:|---:|")
        for key in dimension_columns([s]):
            lines.append(
                f"| {dimension_label(key)} | {s.dimensions[key]:.1f} "
                f"| {s.dimension_max[key]:g} |"
            )
        lines.append(f"| **Monday Score** | **{s.mean:.1f}** | **100** |")
        lines.append("")
        run_list = ", ".join(f"{score:.1f}" for score in s.run_scores)
        lines.append(
            f"**Runs:** {run_list}  (min {s.minimum:.1f}, max {s.maximum:.1f}, "
            f"run_range {s.score_range:.1f}, sigma {s.stddev:.2f})"
        )
        lines.append("")
        lines.append(
            f"**Latency and cost:** TTFA median {_ms(s.median_ttfa_ms)}, "
            f"TTFT median {_ms(s.median_ttft_ms)}, total median "
            f"{_ms(s.median_total_latency_ms)}, output tokens median "
            f"{s.median_output_tokens if s.median_output_tokens is not None else '-'}, "
            f"cost/run median {_usd(s.median_cost_usd)}"
        )
        lines.append("")

        # What it missed - grouped by criterion so a repeated miss reads as one.
        by_criterion: dict[str, list[dict[str, Any]]] = {}
        for entry in s.missed:
            by_criterion.setdefault(entry["criterion"], []).append(entry)
        lines.append(f"### What it missed ({len(by_criterion)} criteria)")
        lines.append("")
        if not by_criterion:
            lines.append("Nothing: every criterion passed in every run.")
        for criterion_id, entries in sorted(by_criterion.items()):
            labels = "/".join(e["result"] for e in entries)
            lost = sum(e["points_possible"] - e["points_awarded"] for e in entries)
            lines.append(
                f"- **`{criterion_id}`** - {labels} across {len(entries)} run(s), "
                f"{lost:.1f} points forgone"
            )
            reason = next((e["reason"] for e in entries if e.get("reason")), None)
            if reason:
                lines.append(f"  - {reason}")
        lines.append("")

        lines.append(f"### What it got wrong ({len(s.got_wrong)})")
        lines.append("")
        if not s.got_wrong:
            lines.append("No penalties and no false actions in any run.")
        for entry in s.got_wrong:
            lines.append(f"- **{entry['type']}** `{entry['id']}` ({entry['points']})")
            if entry.get("reason"):
                lines.append(f"  - {entry['reason']}")
            if entry.get("evidence"):
                lines.append(f"  - evidence: {entry['evidence']}")
        lines.append("")

        lines.append("### Raw evidence")
        lines.append("")
        for path in s.run_paths:
            lines.append(f"- response: `{path}`")
        for path in s.evaluation_paths:
            lines.append(f"- evaluation: `{path}`")
        lines.append("")
        lines.append("---")
        lines.append("")

    lines.append("## Reproducing this")
    lines.append("")
    lines.append("```bash")
    lines.append(f"mondaybench validate --scenario {scenario} \\")
    lines.append(f"    --evaluator {payload.get('evaluator', '')}")
    lines.append(f"mondaybench leaderboard --scenario {scenario} \\")
    lines.append(f"    --evaluator {payload.get('evaluator', '')} --official")
    lines.append("```")
    lines.append("")
    lines.append(
        "Every input, raw response, judge verdict and scoring rule is in this "
        "repository. See `README.md` for the methodology."
    )
    lines.append("")
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Official gate
# --------------------------------------------------------------------------


def official_blockers(
    payload: dict[str, Any],
    summaries: list[ModelSummary],
    *,
    expected_models: list[str],
    expected_prompt_sha256: str,
    expected_rubric_version: str,
    expected_evaluator_id: str,
    required_runs: int = 3,
) -> list[str]:
    """Reasons an official leaderboard must not be published.

    Every check answers one question: could a reader be misled into comparing
    numbers that were not produced under the same conditions? A published
    ranking is a claim about comparability, so these are hard failures rather
    than warnings.
    """
    blockers: list[str] = []
    by_slug = {s.model_slug: s for s in summaries}

    for slug in expected_models:
        summary = by_slug.get(slug)
        if summary is None:
            blockers.append(f"{slug}: no evaluations found")
            continue
        if summary.runs < required_runs:
            blockers.append(
                f"{slug}: {summary.runs} official run(s), {required_runs} required"
            )
        if len(summary.run_scores) != summary.runs:
            blockers.append(
                f"{slug}: {summary.runs} runs but {len(summary.run_scores)} scores - "
                f"an evaluation is missing"
            )

    extra = sorted(set(by_slug) - set(expected_models))
    if extra:
        blockers.append(
            f"evaluations present for models outside the official battery: {', '.join(extra)}"
        )

    if payload.get("integrity_warning"):
        blockers.append(f"integrity warning: {payload['integrity_warning']}")

    prompt_hashes = {s.prompt_sha256 for s in summaries}
    if len(prompt_hashes) > 1:
        blockers.append(
            "runs span multiple prompt hashes: "
            + ", ".join(sorted(h[:12] for h in prompt_hashes))
        )
    elif prompt_hashes and expected_prompt_sha256 not in prompt_hashes:
        blockers.append(
            f"runs were generated against {sorted(prompt_hashes)[0][:12]}, "
            f"published scenario is {expected_prompt_sha256[:12]}"
        )

    rubrics = {s.rubric_version for s in summaries}
    if len(rubrics) > 1:
        blockers.append(
            "evaluations span multiple rubric versions: "
            + ", ".join(sorted(str(r) for r in rubrics))
        )
    elif rubrics and expected_rubric_version not in {str(r) for r in rubrics}:
        blockers.append(
            f"evaluations used rubric {sorted(str(r) for r in rubrics)[0]}, "
            f"official evaluator pins {expected_rubric_version}"
        )

    judges = {s.judge_model_id for s in summaries}
    if len(judges) > 1:
        blockers.append(
            "evaluations span multiple judge models: "
            + ", ".join(sorted(str(j) for j in judges))
        )

    if payload.get("evaluator") != expected_evaluator_id:
        blockers.append(
            f"leaderboard was built for evaluator {payload.get('evaluator')!r}, "
            f"expected {expected_evaluator_id!r}"
        )

    for summary in summaries:
        for warning in summary.warnings:
            blockers.append(f"{summary.model_slug}: {warning}")

    return blockers


def check_scoring_arithmetic(
    evaluator_id: str, scenario_id: str, root: Path | None = None
) -> list[str]:
    """Re-derive every published score from its own parts.

    Cheap insurance against a scoring bug reaching a public number: dimensions
    must sum to base, base plus penalties must equal final, and final must never
    be negative.
    """
    problems: list[str] = []
    for model_slug in models_with_evaluations(evaluator_id, scenario_id, root):
        for path in find_evaluations(evaluator_id, scenario_id, model_slug, root):
            evaluation = load_evaluation(path)
            dimension_total = sum(d.score for d in evaluation.dimensions.values())
            if abs(dimension_total - evaluation.base_score) > 0.01:
                problems.append(
                    f"{evaluation.run_id}: dimensions sum to {dimension_total} "
                    f"but base_score is {evaluation.base_score}"
                )
            expected_final = max(0.0, evaluation.base_score + evaluation.penalties.total)
            if abs(expected_final - evaluation.final_score) > 0.01:
                problems.append(
                    f"{evaluation.run_id}: base {evaluation.base_score} + penalties "
                    f"{evaluation.penalties.total} != final {evaluation.final_score}"
                )
            if evaluation.final_score < 0:
                problems.append(f"{evaluation.run_id}: final_score is negative")
            for criterion_id, result in evaluation.criteria.items():
                if result.points_awarded > result.points_possible:
                    problems.append(
                        f"{evaluation.run_id}: {criterion_id} awarded "
                        f"{result.points_awarded} of {result.points_possible}"
                    )
    return problems
