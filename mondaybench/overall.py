"""The Overall leaderboard: one Monday Score across scenarios.

    Monday Score = arithmetic mean of a model's official scenario scores.

No weighting. Every scenario in a release counts once. Nothing else is folded
in - not latency, TTFA, reasoning or completion tokens, cost, run stability,
serving qualification or the number of attempts it took to get a valid run.
Those are real and they are published, but beside the score and never inside it.
A composite that mixes quality with speed cannot be argued with, because no
reader can tell which half moved.

Two rules give the number its meaning.

**Completeness.** A model appears in the ranking only if it has an official
score for every scenario in the release. Averaging over the scenarios a model
happens to have finished rewards not competing: a model that skipped the one it
was worst at would outrank one that took all four. Incomplete models are
published in their own block with the missing scenario ids named.

**Immutability.** A release names its scenarios explicitly, so adding a fifth
scenario cannot move a number that was published when there were four. Overall
v1 and Overall v2 are different claims and both stay reproducible. The release
also pins each scenario's frozen prompt hash and rubric version, so a scenario
that is re-frozen or re-scored breaks the build loudly instead of quietly
changing history.
"""

from __future__ import annotations

import csv
import json
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import load_yaml, repo_root
from .leaderboard import leaderboard_dir

AGGREGATION_ARITHMETIC_MEAN = "arithmetic_mean"
SUPPORTED_AGGREGATIONS = (AGGREGATION_ARITHMETIC_MEAN,)

# A release that is still waiting on a scenario is `draft`: buildable as a
# preview, refused for publication. Only `released` reaches leaderboard/overall/.
STATUS_DRAFT = "draft"
STATUS_RELEASED = "released"


# CSV rows are terminated with LF, not the csv module's default CRLF, so a
# board written on Windows hashes the same as one written anywhere else.
LF = "\n"


class OverallError(Exception):
    """The Overall leaderboard cannot be built from what is on disk.

    Carries every blocker rather than the first, because a half-fixed release is
    worse than an unbuilt one: the second failure would otherwise arrive after
    someone had already convinced themselves the first was the whole problem.
    """

    def __init__(self, blockers: list[str]):
        self.blockers = blockers
        super().__init__("; ".join(blockers))


@dataclass(frozen=True)
class ScenarioPin:
    """One scenario in a release, with what its result must still hash to."""

    id: str
    prompt_sha256: str | None = None
    rubric_version: str | None = None


@dataclass(frozen=True)
class OverallRelease:
    version: int
    scenarios: tuple[ScenarioPin, ...]
    aggregation: str = AGGREGATION_ARITHMETIC_MEAN
    status: str = STATUS_DRAFT
    label: str | None = None
    note: str | None = None
    # Model-set revision within a fixed scenario set.
    #
    # An Overall release pins SCENARIOS, not models. Benchmarking a new model
    # against the frozen suite adds a row without touching any existing score -
    # each model's Monday Score is the mean of its own runs and cannot be moved
    # by another model appearing. But the published FILE changes, and
    # `overall-v2.json` is cited and hashed elsewhere.
    #
    # So the model set gets its own axis: v2 stays byte-frozen forever, and the
    # eight-model board is published as v2.1. Same scenarios, same arithmetic,
    # more competitors.
    revision: int = 0
    # Which SUITE release this Overall aggregates. None means v1.0, whose
    # scenario boards sit at their original paths. A later suite publishes its
    # boards under `leaderboard/v<version>/`, and an Overall that named the same
    # scenarios but read a different suite's boards would be a different claim
    # wearing the same number - so the version travels with the release.
    suite_version: str | None = None

    @property
    def scenario_ids(self) -> list[str]:
        return [s.id for s in self.scenarios]

    @property
    def key(self) -> tuple[int, int]:
        return (self.version, self.revision)

    @property
    def slug(self) -> str:
        """`2` -> "2"; `2` revision `1` -> "2.1". What the artifact is named."""
        return f"{self.version}" if not self.revision else f"{self.version}.{self.revision}"


@dataclass
class ModelOverall:
    model_slug: str
    display_name: str
    # scenario id -> official mean score for that scenario
    scenario_scores: dict[str, float] = field(default_factory=dict)
    missing: list[str] = field(default_factory=list)
    # Run-to-run spread inside each scenario. Reported, never scored, and
    # deliberately named so it cannot be mistaken for cross-scenario variance.
    run_ranges: dict[str, float] = field(default_factory=dict)
    run_stddevs: dict[str, float] = field(default_factory=dict)
    rank: int = 0

    @property
    def complete(self) -> bool:
        return not self.missing

    @property
    def monday_score(self) -> float:
        """The arithmetic mean of the scenario scores. Nothing else."""
        return round(statistics.fmean(self.scenario_scores.values()), 2)

    # --- variation ACROSS scenarios -----------------------------------------
    # How differently the model performs from one kind of work to another. A
    # model at 98/87/92 is not the same product as one at 92/92/93, and the mean
    # hides that. This is NOT run-to-run stability; see run_* below.
    @property
    def scenario_mean(self) -> float:
        return self.monday_score

    @property
    def scenario_min(self) -> float:
        return round(min(self.scenario_scores.values()), 2)

    @property
    def scenario_max(self) -> float:
        return round(max(self.scenario_scores.values()), 2)

    @property
    def scenario_range(self) -> float:
        return round(self.scenario_max - self.scenario_min, 2)

    @property
    def scenario_stddev(self) -> float:
        values = list(self.scenario_scores.values())
        return round(statistics.stdev(values), 2) if len(values) > 1 else 0.0

    # --- variation WITHIN a scenario, across its official runs ---------------
    @property
    def mean_run_range(self) -> float | None:
        return round(statistics.fmean(self.run_ranges.values()), 2) if self.run_ranges else None

    @property
    def max_run_range(self) -> float | None:
        return round(max(self.run_ranges.values()), 2) if self.run_ranges else None

    @property
    def mean_run_stddev(self) -> float | None:
        return round(statistics.fmean(self.run_stddevs.values()), 2) if self.run_stddevs else None


# --------------------------------------------------------------------------
# Release configuration
# --------------------------------------------------------------------------


def releases_path(root: Path | None = None) -> Path:
    return (root or repo_root()) / "overall-releases.yaml"


def load_releases(
    path: Path | None = None, root: Path | None = None
) -> dict[int | str, OverallRelease]:
    """Every declared Overall release.

    Keyed by version for a base release (`releases[2]`) and by its slug for a
    model-set revision (`releases["2.1"]`), so existing callers that index by
    integer keep working and a revision cannot shadow the release it extends.
    """
    path = path or releases_path(root)
    data = load_yaml(path) or {}
    out: dict[int | str, OverallRelease] = {}
    for raw in data.get("releases") or []:
        version = int(raw["overall_version"])
        revision = int(raw.get("revision", 0) or 0)
        key: int | str = version if not revision else f"{version}.{revision}"
        if key in out:
            raise OverallError([f"overall v{key} is declared twice"])
        scenarios = tuple(
            ScenarioPin(
                id=str(s["id"]) if isinstance(s, dict) else str(s),
                prompt_sha256=(s.get("prompt_sha256") if isinstance(s, dict) else None),
                rubric_version=(str(s["rubric_version"]) if isinstance(s, dict) and s.get("rubric_version") is not None else None),
            )
            for s in raw.get("scenarios") or []
        )
        out[key] = OverallRelease(
            version=version,
            revision=revision,
            scenarios=scenarios,
            aggregation=str(raw.get("aggregation", AGGREGATION_ARITHMETIC_MEAN)),
            suite_version=(str(raw["suite_version"]) if raw.get("suite_version") is not None
                           else None),
            status=str(raw.get("status", STATUS_DRAFT)),
            label=raw.get("label"),
            note=raw.get("note"),
        )

    # A revision must extend a real release and must not quietly change what it
    # extends: same scenarios, same aggregation, or it is a different claim
    # wearing a decimal point.
    for key, release in out.items():
        if not release.revision:
            continue
        base = out.get(release.version)
        if base is None:
            raise OverallError(
                [f"overall v{key} is a revision of v{release.version}, which is not declared"]
            )
        if release.scenario_ids != base.scenario_ids:
            raise OverallError(
                [
                    f"overall v{key} covers {release.scenario_ids} but v{release.version} "
                    f"covers {base.scenario_ids}. A revision adds MODELS to a fixed scenario "
                    f"set; changing the scenarios makes it a new version, not a revision."
                ]
            )
        if release.aggregation != base.aggregation:
            raise OverallError(
                [f"overall v{key} changes aggregation from v{release.version}"]
            )
    return out


def validate_release(release: OverallRelease) -> list[str]:
    """Problems with the release declaration itself, before any data is read."""
    blockers: list[str] = []
    if not release.scenarios:
        blockers.append(f"overall v{release.version} includes no scenarios")
    if release.aggregation not in SUPPORTED_AGGREGATIONS:
        blockers.append(
            f"overall v{release.version} declares aggregation {release.aggregation!r}; "
            f"supported: {', '.join(SUPPORTED_AGGREGATIONS)}"
        )
    seen: set[str] = set()
    for pin in release.scenarios:
        if pin.id in seen:
            blockers.append(
                f"overall v{release.version} includes {pin.id} twice, which would weight it double"
            )
        seen.add(pin.id)
    if release.status not in (STATUS_DRAFT, STATUS_RELEASED):
        blockers.append(f"overall v{release.version} has unknown status {release.status!r}")
    return blockers


# --------------------------------------------------------------------------
# Reading the per-scenario results
# --------------------------------------------------------------------------


def load_scenario_leaderboard(
    scenario_id: str, root: Path | None = None, suite_version: str | None = None
) -> dict[str, Any] | None:
    """The published leaderboard payload for one scenario, or None if absent.

    Reads the canonical JSON, never the Markdown: the Markdown is a rendering
    and parsing it would make the Overall score depend on a presentation choice.
    """
    path = leaderboard_dir(scenario_id, root, suite_version) / "leaderboard.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def check_scenario_payload(pin: ScenarioPin, payload: dict[str, Any] | None) -> list[str]:
    """Whether one scenario's published result may enter an Overall score."""
    blockers: list[str] = []
    if payload is None:
        blockers.append(
            f"{pin.id}: no published leaderboard - it must be official before it can be included"
        )
        return blockers

    if not payload.get("official"):
        blockers.append(
            f"{pin.id}: leaderboard is not marked official, so it has not passed the "
            f"publication gates"
        )
    if payload.get("scenario_status") == "calibration":
        blockers.append(
            f"{pin.id}: leaderboard is a calibration draft; calibration results are tuned "
            f"against the runs they rank and are never aggregated"
        )
    if payload.get("integrity_warning"):
        blockers.append(f"{pin.id}: integrity warning - {payload['integrity_warning']}")
    if payload.get("scenario") != pin.id:
        blockers.append(
            f"{pin.id}: leaderboard declares scenario {payload.get('scenario')!r}"
        )

    # Version pins. A scenario that was re-frozen or re-scored is a different
    # measurement; silently absorbing it would rewrite a published Overall.
    if pin.prompt_sha256 and payload.get("frozen_prompt_sha256") != pin.prompt_sha256:
        blockers.append(
            f"{pin.id}: prompt hash {str(payload.get('frozen_prompt_sha256'))[:12]} does not "
            f"match the {pin.prompt_sha256[:12]} this release was built on"
        )
    if pin.rubric_version and str(payload.get("rubric_version")) != pin.rubric_version:
        blockers.append(
            f"{pin.id}: rubric version {payload.get('rubric_version')!r} does not match the "
            f"{pin.rubric_version!r} this release was built on"
        )
    return blockers


def check_score_recomputes(scenario_id: str, row: dict[str, Any]) -> list[str]:
    """The published mean must be the mean of the published run scores.

    Cheap insurance against a leaderboard whose headline drifted from the runs
    beneath it - the Overall score would inherit the error and spread it across
    every scenario.
    """
    score = row.get("score") or {}
    runs = row.get("run_scores") or []
    slug = row.get("model_slug")
    if not runs:
        return [f"{scenario_id}/{slug}: no run scores, so the mean cannot be verified"]
    if len(runs) != score.get("runs"):
        return [
            f"{scenario_id}/{slug}: {score.get('runs')} runs claimed but {len(runs)} scores present"
        ]
    expected = round(statistics.fmean(runs), 2)
    if abs(expected - float(score.get("mean", 0))) > 0.011:
        return [
            f"{scenario_id}/{slug}: published mean {score.get('mean')} does not recompute from "
            f"its run scores {runs} (expected {expected})"
        ]
    return []


# --------------------------------------------------------------------------
# Building
# --------------------------------------------------------------------------


def build_overall(
    release: OverallRelease, root: Path | None = None, *, require_released: bool = False
) -> tuple[dict[str, Any], list[ModelOverall], list[ModelOverall]]:
    """Aggregate one release. Returns (payload, ranked, incomplete).

    Raises OverallError with every blocker rather than producing a number that
    would have to be retracted.
    """
    blockers = validate_release(release)
    if require_released and release.status != STATUS_RELEASED:
        blockers.append(
            f"overall v{release.version} is status={release.status}, not {STATUS_RELEASED}. "
            f"Marking a release is a deliberate act, separate from publishing the scenarios "
            f"it names - so this is not something the build infers from their state"
        )

    payloads: dict[str, dict[str, Any]] = {}
    for pin in release.scenarios:
        payload = load_scenario_leaderboard(pin.id, root, release.suite_version)
        problems = check_scenario_payload(pin, payload)
        blockers.extend(problems)
        if payload is not None and not problems:
            payloads[pin.id] = payload

    if blockers:
        raise OverallError(blockers)

    models: dict[str, ModelOverall] = {}
    display: dict[str, str] = {}
    for scenario_id, payload in payloads.items():
        for row in payload.get("models") or []:
            slug = row["model_slug"]
            blockers.extend(check_score_recomputes(scenario_id, row))
            entry = models.setdefault(slug, ModelOverall(model_slug=slug, display_name=slug))
            entry.scenario_scores[scenario_id] = float(row["score"]["mean"])
            entry.run_ranges[scenario_id] = float(row["score"].get("range", 0.0))
            entry.run_stddevs[scenario_id] = float(row["score"].get("stddev", 0.0))
            display[slug] = row.get("display_name") or slug

    for slug, entry in models.items():
        entry.display_name = display.get(slug, slug)
        entry.missing = [s for s in release.scenario_ids if s not in entry.scenario_scores]

    if blockers:
        raise OverallError(blockers)

    complete = [m for m in models.values() if m.complete]
    incomplete = [m for m in models.values() if not m.complete]

    # Deterministic order: score descending, then slug, so two models that tie
    # rank the same way on every rebuild. Ties share a rank rather than being
    # separated by an arbitrary tiebreak the score does not support.
    complete.sort(key=lambda m: (-m.monday_score, m.model_slug))
    previous: float | None = None
    previous_rank = 0
    for position, entry in enumerate(complete, start=1):
        if previous is not None and abs(entry.monday_score - previous) < 1e-9:
            entry.rank = previous_rank
        else:
            entry.rank = position
            previous_rank = position
        previous = entry.monday_score
    incomplete.sort(key=lambda m: m.model_slug)

    payload = {
        "overall_version": release.version,
        # Emitted only for an actual model-set revision, so the payloads of
        # v0/v1/v2 stay byte-reproducible from this code.
        **({"overall_revision": release.revision, "overall_slug": release.slug}
           if release.revision else {}),
        # Emitted only when the release names one, so v0/v1/v2 stay
        # byte-reproducible from this code.
        **({"suite_version": release.suite_version} if release.suite_version else {}),
        "label": release.label,
        "status": release.status,
        "aggregation": release.aggregation,
        "scenarios": release.scenario_ids,
        "scenario_provenance": {
            pin.id: {
                "prompt_sha256": payloads[pin.id].get("frozen_prompt_sha256"),
                "rubric_version": payloads[pin.id].get("rubric_version"),
                "evaluator": payloads[pin.id].get("evaluator"),
                "generated_at": payloads[pin.id].get("generated_at"),
            }
            for pin in release.scenarios
        },
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "monday_score_definition": (
            "arithmetic mean of the model's official score on each scenario listed above; "
            "equal weight per scenario; excludes latency, TTFA, tokens, cost and run stability"
        ),
        "models": [_serialize(m, release) for m in complete],
        "incomplete_models": [_serialize(m, release) for m in incomplete],
    }
    if release.note:
        payload["note"] = release.note
    return payload, complete, incomplete


def _serialize(entry: ModelOverall, release: OverallRelease) -> dict[str, Any]:
    row: dict[str, Any] = {
        "model_slug": entry.model_slug,
        "display_name": entry.display_name,
        "scenario_scores": {s: entry.scenario_scores.get(s) for s in release.scenario_ids},
    }
    if entry.complete:
        row["rank"] = entry.rank
        row["monday_score"] = entry.monday_score
        # Variation across scenarios - how uneven the model is across kinds of
        # work. Named `across_scenarios` so it cannot be read as run stability.
        row["across_scenarios"] = {
            "mean": entry.scenario_mean,
            "min": entry.scenario_min,
            "max": entry.scenario_max,
            "range": entry.scenario_range,
            "stddev": entry.scenario_stddev,
        }
        # Variation between the official runs inside each scenario. Observability
        # only: never part of the Monday Score.
        row["run_stability"] = {
            "mean_run_range": entry.mean_run_range,
            "max_run_range": entry.max_run_range,
            "mean_run_stddev": entry.mean_run_stddev,
            "per_scenario_run_range": dict(entry.run_ranges),
        }
    else:
        row["missing_scenarios"] = entry.missing
    return row


# --------------------------------------------------------------------------
# Writing
# --------------------------------------------------------------------------


def overall_dir(root: Path | None = None, *, preview: bool = False) -> Path:
    base = root or repo_root()
    return base / "analysis" / "overall" if preview else base / "leaderboard" / "overall"


def write_overall(
    payload: dict[str, Any],
    ranked: list[ModelOverall],
    incomplete: list[ModelOverall],
    release: OverallRelease,
    root: Path | None = None,
    *,
    preview: bool = False,
) -> tuple[Path, Path, Path]:
    if not preview and release.status != STATUS_RELEASED:
        raise OverallError(
            [
                f"overall v{release.version} is status={release.status} and cannot be written to "
                f"leaderboard/overall/. Build it as a preview instead."
            ]
        )
    directory = overall_dir(root, preview=preview)
    directory.mkdir(parents=True, exist_ok=True)
    stem = f"overall-v{release.slug}" + ("-preview" if preview else "")

    json_path = directory / f"{stem}.json"
    json_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n"
    )

    csv_path = directory / f"{stem}.csv"
    # newline="" stops the file object translating; the explicit LF line
    # terminator stops csv.writer emitting its default CRLF. Both are needed:
    # without the second, a CSV written on Windows carries CRLF, hashes
    # differently from the same file written on Linux, and trips the
    # repository's own released-artifact invariant. The v1.0 CSVs read as LF
    # only because .gitattributes normalises them on checkout, which does
    # nothing for a file that has not been committed yet.
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator=LF)
        header = ["Rank", "Model", "Monday Score"]
        header += [s.replace("monday-", "#") for s in release.scenario_ids]
        header += ["Scenario mean", "Scenario min", "Scenario max", "Scenario range",
                   "Scenario stddev", "Mean run range", "Max run range", "Mean run stddev"]
        writer.writerow(header)
        for entry in ranked:
            writer.writerow(
                [entry.rank, entry.display_name, f"{entry.monday_score:.2f}"]
                + [f"{entry.scenario_scores[s]:.2f}" for s in release.scenario_ids]
                + [
                    f"{entry.scenario_mean:.2f}", f"{entry.scenario_min:.2f}",
                    f"{entry.scenario_max:.2f}", f"{entry.scenario_range:.2f}",
                    f"{entry.scenario_stddev:.2f}",
                    "" if entry.mean_run_range is None else f"{entry.mean_run_range:.2f}",
                    "" if entry.max_run_range is None else f"{entry.max_run_range:.2f}",
                    "" if entry.mean_run_stddev is None else f"{entry.mean_run_stddev:.2f}",
                ]
            )

    md_path = directory / f"{stem}.md"
    md_path.write_text(render_markdown(payload, ranked, incomplete, release), encoding="utf-8", newline="\n")
    return json_path, csv_path, md_path


def render_markdown(
    payload: dict[str, Any],
    ranked: list[ModelOverall],
    incomplete: list[ModelOverall],
    release: OverallRelease,
) -> str:
    ids = release.scenario_ids
    lines: list[str] = []
    title = release.label or f"Overall v{release.version}"
    lines.append(f"# MondayBench Overall — {title}")
    lines.append("")
    if payload.get("status") != STATUS_RELEASED:
        lines.append(
            f"> **PREVIEW — NOT AN OFFICIAL RESULT.** This release is `status: "
            f"{payload.get('status')}`. It is built from the scenarios below for analysis only "
            f"and must not be quoted as a MondayBench Overall score."
        )
        lines.append("")
    lines.append(
        f"**Monday Score** is the arithmetic mean of a model's official score on each scenario "
        f"listed below. Every scenario counts once. Latency, TTFA, tokens, cost and run stability "
        f"are reported beside it and are never folded into it."
    )
    lines.append("")
    lines.append(f"**Scenarios in this version:** {', '.join(f'`{s}`' for s in ids)}")
    lines.append("")
    lines.append(
        "A model is ranked only if it has an official score on every one of them. Averaging over "
        "the scenarios a model happens to have completed would reward skipping the hard one."
    )
    lines.append("")
    if release.note:
        lines.append(f"{release.note}")
        lines.append("")

    header = ["Rank", "Model", "Monday Score"] + [s.replace("monday-", "#") for s in ids] + ["Range", "Stddev"]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("|---:|---|---:|" + "---:|" * (len(ids) + 2))
    for entry in ranked:
        cells = [str(entry.rank), entry.display_name, f"**{entry.monday_score:.2f}**"]
        cells += [f"{entry.scenario_scores[s]:.2f}" for s in ids]
        cells += [f"{entry.scenario_range:.2f}", f"{entry.scenario_stddev:.2f}"]
        lines.append("| " + " | ".join(cells) + " |")
    lines.append("")
    lines.append(
        "`Range` and `Stddev` above measure how much a model's score moves **from one scenario to "
        "another** — how uneven it is across kinds of work. They are not run-to-run stability."
    )
    lines.append("")

    if any(e.mean_run_range is not None for e in ranked):
        lines.append("## Run stability")
        lines.append("")
        lines.append(
            "Spread between the three official runs **within** each scenario, averaged across "
            "scenarios. Published for observability; not part of the Monday Score."
        )
        lines.append("")
        lines.append("| Model | Mean run range | Max run range | Mean run stddev |")
        lines.append("|---|---:|---:|---:|")
        for entry in sorted(ranked, key=lambda m: (m.mean_run_range or 0.0)):
            lines.append(
                f"| {entry.display_name} | {entry.mean_run_range:.2f} | "
                f"{entry.max_run_range:.2f} | {entry.mean_run_stddev:.2f} |"
            )
        lines.append("")

    if incomplete:
        lines.append("## Not ranked — incomplete")
        lines.append("")
        lines.append(
            "These models have an official score on some but not all of the scenarios in this "
            "version, so no Monday Score is computed for them."
        )
        lines.append("")
        lines.append("| Model | Has | Missing |")
        lines.append("|---|---|---|")
        for entry in incomplete:
            has = ", ".join(f"`{s}`" for s in ids if s in entry.scenario_scores) or "—"
            lines.append(f"| {entry.display_name} | {has} | " + ", ".join(f"`{s}`" for s in entry.missing) + " |")
        lines.append("")

    lines.append("## Provenance")
    lines.append("")
    lines.append("| Scenario | Prompt sha256 | Rubric | Evaluator |")
    lines.append("|---|---|---|---|")
    for scenario_id in ids:
        prov = payload["scenario_provenance"][scenario_id]
        sha = (prov.get("prompt_sha256") or "")[:12]
        lines.append(
            f"| `{scenario_id}` | `{sha}` | {prov.get('rubric_version')} | "
            f"`{prov.get('evaluator')}` |"
        )
    lines.append("")
    lines.append(
        f"Generated {payload['generated_at']}. Each scenario's own leaderboard, runs, verdicts "
        f"and scoring rules are in this repository."
    )
    lines.append("")
    return "\n".join(lines)
