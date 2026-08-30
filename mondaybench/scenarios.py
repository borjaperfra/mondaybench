"""Scenario loading: metadata, sources, rubric and ground truth.

A scenario is a directory under `scenarios/`. Its source order is part of the
benchmark specification and comes from `scenario.yaml`, never from directory
listing order.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .config import ConfigError, load_yaml, repo_root


class ScenarioError(Exception):
    """Raised when a scenario is missing files or is internally inconsistent."""


# --------------------------------------------------------------------------
# Rubric
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Criterion:
    id: str
    dimension: str
    points_pass: float
    points_partial: float
    points_fail: float
    pass_definition: str
    partial_definition: str
    fail_definition: str

    def points_for(self, label: str) -> float:
        return {
            "PASS": self.points_pass,
            "PARTIAL": self.points_partial,
            "FAIL": self.points_fail,
        }[label]


@dataclass(frozen=True)
class FalseAction:
    id: str
    description: str


@dataclass(frozen=True)
class NoiseDimension:
    max_points: float
    starting_points: float
    deduction_per_false_action: float
    minimum_points: float
    false_actions: list[FalseAction]


@dataclass(frozen=True)
class PenaltyDefinition:
    type: str
    points: float
    definition: str


@dataclass(frozen=True)
class Rubric:
    version: str
    total_base_points: float
    maximum_global_penalty: float
    dimension_max: dict[str, float]
    criteria: list[Criterion]
    # Optional: a rubric may score noise as its own dimension (monday-001) or
    # fold the same risk into criteria and penalties (monday-002, where the
    # dangerous noise is stale-but-plausible information rather than a listed
    # set of false actions). `None` means the dimension does not exist, which is
    # different from existing and scoring zero.
    noise: NoiseDimension | None
    penalties: dict[str, PenaltyDefinition]

    @property
    def criteria_by_id(self) -> dict[str, Criterion]:
        return {c.id: c for c in self.criteria}

    def criteria_for(self, dimension: str) -> list[Criterion]:
        return [c for c in self.criteria if c.dimension == dimension]


# The rubric names penalty kinds in snake_case; the judge returns SCREAMING_CASE.
# A rubric may name a penalty in its own terms; the stored type stays one of the
# four shared ones so a penalty means the same thing across scenarios. Adding a
# near-duplicate type per scenario is how a shared vocabulary stops being one -
# the same mistake the leaderboard renderer made with dimensions.
PENALTY_KEY_TO_TYPE = {
    "material_hallucination": "MATERIAL_HALLUCINATION",
    "prohibited_action": "PROHIBITED_ACTION",
    # monday-003 widens the definition to cover wasted effort as well as
    # forbidden action, and weights it differently. Same class of failure:
    # the response tells the user to do something the evidence rules out.
    "prohibited_or_wasteful_action": "PROHIBITED_ACTION",
    "major_planning_error": "MAJOR_PLANNING_ERROR",
    # monday-003's name for the same thing monday-002 calls a planning error:
    # a recommended plan that cannot run under the stated dependencies.
    "critical_path_violation": "MAJOR_PLANNING_ERROR",
    "major_contradiction": "MAJOR_CONTRADICTION",
    # monday-004 is an analysis scenario, not a planning one. Its rubric names
    # three penalties of its own: a recommendation the data rules out (the same
    # failure PROHIBITED_ACTION already covers), a numeric or data mistake the
    # analysis then rests on, and a causal claim nothing in the data supports.
    "prohibited_business_action": "PROHIBITED_ACTION",
    "major_data_error": "MAJOR_DATA_ERROR",
    "unsupported_causality": "UNSUPPORTED_CAUSALITY",
}
NOISE_DIMENSION = "noise_resistance"


def _clean(text: Any) -> str:
    """Collapse a YAML folded block into a single tidy line."""
    return " ".join(str(text or "").split())


def _parse_criterion(name: str, raw: dict[str, Any]) -> Criterion:
    """One criterion, in either of the two rubric spellings.

    monday-001 writes the three point values as a mapping and the three label
    definitions as `*_definition` keys:

        points: {pass: 8, partial: 4, fail: 0}
        pass_definition: ...

    monday-002 writes a scalar `points` with an explicit `partial_points`, and
    puts the definitions under `pass` / `partial`:

        {id: ..., points: 8, partial_points: 4, pass: "...", partial: "..."}

    Both are accepted as written. Neither is rewritten on disk, because a
    rubric's bytes are what its published scores were derived from.
    """
    points = raw.get("points")

    if isinstance(points, dict):
        for key in ("pass", "partial", "fail"):
            if key not in points:
                raise ScenarioError(f"criterion {raw.get('id')!r} is missing points.{key}")
        return Criterion(
            id=raw["id"],
            dimension=name,
            points_pass=float(points["pass"]),
            points_partial=float(points["partial"]),
            points_fail=float(points["fail"]),
            pass_definition=_clean(raw.get("pass_definition")),
            partial_definition=_clean(raw.get("partial_definition")),
            fail_definition=_clean(raw.get("fail_definition")),
        )

    if points is None:
        raise ScenarioError(f"criterion {raw.get('id')!r} is missing points")

    # Scalar form. `partial_points` is explicit rather than assumed to be half:
    # a rubric is free to make PARTIAL worth something other than 50%, and
    # guessing here would silently change what a published score means.
    if "partial_points" not in raw:
        raise ScenarioError(
            f"criterion {raw.get('id')!r} gives a scalar points value but no "
            f"partial_points; PARTIAL must not be inferred"
        )
    return Criterion(
        id=raw["id"],
        dimension=name,
        points_pass=float(points),
        points_partial=float(raw["partial_points"]),
        points_fail=0.0,
        pass_definition=_clean(raw.get("pass")),
        partial_definition=_clean(raw.get("partial")),
        # The scalar form states no FAIL prose: FAIL is "neither of the above".
        fail_definition=_clean(raw.get("fail")) or "Neither the PASS nor the PARTIAL bar is met.",
    )


def _parse_penalties(data: dict[str, Any]) -> tuple[dict[str, PenaltyDefinition], float | None]:
    """Global penalties, in either spelling.

    monday-001 maps each penalty name to `{points: -5, definition: ...}` with
    the sign already negative. monday-002 lists `{id, points_each: 5}` with a
    positive magnitude plus a `max_penalty`. Both normalise to negative points
    here, so `scoring.py` never has to know which rubric it is reading.
    """
    raw = data.get("global_penalties") or {}
    penalties: dict[str, PenaltyDefinition] = {}

    if "types" in raw:
        for spec in raw.get("types") or []:
            ptype = PENALTY_KEY_TO_TYPE.get(spec.get("id"))
            if ptype is None:
                raise ScenarioError(f"unknown global penalty {spec.get('id')!r}")
            magnitude = abs(float(spec["points_each"]))
            penalties[ptype] = PenaltyDefinition(
                type=ptype, points=-magnitude, definition=_clean(spec.get("definition"))
            )
        cap = raw.get("max_penalty")
        return penalties, (float(cap) if cap is not None else None)

    for key, spec in raw.items():
        ptype = PENALTY_KEY_TO_TYPE.get(key)
        if ptype is None:
            raise ScenarioError(f"unknown global penalty {key!r}")
        penalties[ptype] = PenaltyDefinition(
            type=ptype,
            points=float(spec["points"]),
            definition=_clean(spec.get("definition")),
        )
    return penalties, None


def parse_rubric(data: dict[str, Any]) -> Rubric:
    dimensions = data.get("dimensions") or {}
    if not dimensions:
        raise ScenarioError("rubric has no dimensions")

    criteria: list[Criterion] = []
    dimension_max: dict[str, float] = {}
    noise: NoiseDimension | None = None

    for name, spec in dimensions.items():
        if not isinstance(spec, dict):
            raise ScenarioError(f"rubric dimension {name!r} is not a mapping")
        if "max_points" not in spec:
            raise ScenarioError(f"rubric dimension {name!r} is missing max_points")
        dimension_max[name] = float(spec["max_points"])

        if name == NOISE_DIMENSION:
            raw_actions = spec.get("false_actions") or []
            noise = NoiseDimension(
                max_points=float(spec["max_points"]),
                starting_points=float(spec.get("starting_points", spec["max_points"])),
                deduction_per_false_action=float(spec.get("deduction_per_false_action", 2)),
                minimum_points=float(spec.get("minimum_points", 0)),
                false_actions=[
                    FalseAction(id=a["id"], description=_clean(a.get("description")))
                    for a in raw_actions
                ],
            )
            continue

        for raw in spec.get("criteria") or []:
            criteria.append(_parse_criterion(name, raw))

    seen: set[str] = set()
    for criterion in criteria:
        if criterion.id in seen:
            raise ScenarioError(f"duplicate criterion id {criterion.id!r}")
        seen.add(criterion.id)

    penalties, penalty_cap = _parse_penalties(data)

    if penalty_cap is None:
        penalty_cap = float(data.get("maximum_global_penalty", 20))

    return Rubric(
        version=str(data.get("version") or data.get("rubric_version") or "0"),
        total_base_points=float(
            data.get("total_base_points")
            or data.get("total_points")
            or sum(dimension_max.values())
        ),
        maximum_global_penalty=penalty_cap,
        dimension_max=dimension_max,
        criteria=criteria,
        noise=noise,
        penalties=penalties,
    )


# --------------------------------------------------------------------------
# Scenario
# --------------------------------------------------------------------------

REQUIRED_FILES = ("scenario.yaml", "prompt.md", "rubric.yaml")

# A scenario that has not been calibrated and frozen cannot be published. The
# publication gate reads this, so marking a scenario `calibration` is enough to
# keep it out of an official leaderboard.
CALIBRATION_STATUS = "calibration"


@dataclass(frozen=True)
class Scenario:
    id: str
    name: str
    benchmark_version: str
    language: str
    context: dict[str, Any]
    sources: list[str]
    official_runs: int
    directory: Path
    rubric: Rubric
    # Structured answer key (monday-001's `ground-truth.yaml`). Empty when the
    # scenario ships its ground truth as prose.
    ground_truth: dict[str, Any]
    prompt_template: str
    source_text: dict[str, str] = field(default_factory=dict)
    # Raw answer-key text, whatever the format. Always populated; a Markdown
    # ground truth has no dotted paths to slice, so the judge is given all of it.
    ground_truth_text: str = ""
    ground_truth_file: str = "ground-truth.yaml"
    prompt_file: str = "prompt.md"
    # Distinct from `benchmark_version`: a scenario can be revised while the
    # benchmark version stands still, and an evaluator is written against one
    # specific revision of the content.
    scenario_version: str = ""
    status: str = "frozen"
    # Optional per-scenario generation ceiling, in tokens.
    #
    # Added for monday-004. `models.yaml` sets one `max_output_tokens` per model
    # and monday-001..003 were generated under it; changing that value would
    # make every run of those three fail `qualify_run` on
    # `max_output_tokens != configured`, so the published batteries would stop
    # verifying. A scenario therefore declares its own ceiling and the older
    # ones inherit the model default unchanged.
    #
    # This is a SAFETY CEILING, not a reasoning budget. See the token-budget
    # audit: the value does not equalise compute across models and is not
    # intended to.
    safety_ceiling_tokens: int | None = None

    @property
    def is_calibration(self) -> bool:
        return self.status == CALIBRATION_STATUS


def scenarios_dir() -> Path:
    return repo_root() / "scenarios"


def list_scenario_ids() -> list[str]:
    root = scenarios_dir()
    if not root.exists():
        return []
    return sorted(p.name for p in root.iterdir() if p.is_dir() and (p / "scenario.yaml").exists())


def load_scenario(
    scenario_id: str,
    directory: Path | None = None,
    rubric_file: str | None = None,
) -> Scenario:
    """Load a scenario, optionally with an alternative rubric.

    The prompt sources are scenario content: immutable and hashed. The rubric is
    scoring, which belongs to the evaluator - so an evaluator may name a
    different rubric file. That keeps a superseded rubric on disk and its scores
    reproducible, instead of overwriting it and losing the ability to reproduce
    anything scored under it.
    """
    directory = directory or scenarios_dir() / scenario_id
    if not directory.is_dir():
        raise ScenarioError(f"unknown scenario {scenario_id!r} (looked in {directory})")

    try:
        meta = load_yaml(directory / "scenario.yaml") or {}
    except ConfigError as exc:
        raise ScenarioError(str(exc)) from exc

    # A scenario names its own rubric and answer key. An evaluator may override
    # the rubric (that is what `rubric_file` is for); the answer key belongs to
    # the scenario and is never overridden.
    # The sentinel is None, not "rubric.yaml". It used to be the filename, which
    # made "no opinion" and "explicitly rubric.yaml" the same request: once
    # monday-004 pointed its scenario at rubric-0.3.yaml, the evaluator that
    # declares `rubric_file: rubric.yaml` - the one that reproduces the first
    # calibration - silently started scoring against 0.3 instead. A caller that
    # names a rubric now gets that rubric.
    scenario_rubric = meta.get("rubric_file", "rubric.yaml")
    rubric_name = rubric_file or scenario_rubric
    gt_name = meta.get("ground_truth_file", "ground-truth.yaml")

    required = tuple(f for f in REQUIRED_FILES if f != "rubric.yaml") + (rubric_name, gt_name)
    missing = [f for f in required if not (directory / f).exists()]
    if missing:
        raise ScenarioError(f"scenario {scenario_id!r} is missing: {', '.join(missing)}")

    try:
        raw_rubric = load_yaml(directory / rubric_name) or {}
    except ConfigError as exc:
        raise ScenarioError(str(exc)) from exc

    gt_path = directory / gt_name
    ground_truth_text = gt_path.read_text(encoding="utf-8")
    if gt_path.suffix in (".yaml", ".yml"):
        try:
            ground_truth = load_yaml(gt_path) or {}
        except ConfigError as exc:
            raise ScenarioError(str(exc)) from exc
    else:
        # Prose answer key: there is nothing to slice by dotted path, so the
        # structured view stays empty and the judge receives the whole text.
        ground_truth = {}

    declared_id = meta.get("id")
    if declared_id != scenario_id:
        raise ScenarioError(
            f"scenario.yaml declares id {declared_id!r} but lives in directory {scenario_id!r}"
        )

    # `sources` (monday-001) and `source_order` (monday-002) mean the same
    # thing: the order the model sees them in, which is part of the spec.
    sources = list(meta.get("sources") or meta.get("source_order") or [])
    if not sources:
        raise ScenarioError(f"scenario {scenario_id!r} declares no sources")

    source_text: dict[str, str] = {}
    for source in sources:
        path = directory / source
        if not path.exists():
            raise ScenarioError(f"scenario {scenario_id!r} references missing source {source!r}")
        source_text[source] = path.read_text(encoding="utf-8")

    prompt_file = meta.get("prompt_file", "prompt.md")
    prompt_path = directory / prompt_file
    if not prompt_path.exists():
        raise ScenarioError(f"scenario {scenario_id!r} is missing: {prompt_file}")

    return Scenario(
        id=scenario_id,
        name=meta.get("name") or meta.get("title") or scenario_id,
        benchmark_version=str(meta.get("benchmark_version", "0.1")),
        language=meta.get("language", "en"),
        context=meta.get("context") or {},
        sources=sources,
        official_runs=int(meta.get("official_runs", 3)),
        directory=directory,
        rubric=parse_rubric(raw_rubric),
        ground_truth=ground_truth,
        prompt_template=prompt_path.read_text(encoding="utf-8"),
        source_text=source_text,
        ground_truth_text=ground_truth_text,
        ground_truth_file=gt_name,
        prompt_file=prompt_file,
        scenario_version=str(meta.get("scenario_version", "")),
        status=str(meta.get("status", "frozen")),
        safety_ceiling_tokens=(
            int(ceiling) if (ceiling := (meta.get("generation") or {}).get("safety_ceiling_tokens")) else None
        ),
    )
