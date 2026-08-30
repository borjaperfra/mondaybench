"""Capability profiles: what kind of work is a model good at?

Reads `taxonomy/capabilities-v0.1.yaml` and the official evaluations, and
answers a different question from the leaderboard. The leaderboard says how far
a model got. This says where it lost the points.

It is not a second scoring system. It changes no scenario score, reads no
rubric it could modify, and its output lives under `analysis/`.

**Aggregation.** A capability score is

    points earned on its criteria / points available on those criteria * 100

with each criterion's earned points averaged across the model's official runs
first - the same aggregation the scenario score uses. No best-of, no
cherry-picking, no reweighting between capabilities: the natural point mass of
the rubrics is the weighting, and it is reported so a reader can see it.

**Primary only.** A criterion with a secondary tag contributes its points once,
to the primary capability. Counting it in both would inflate the denominators
of whichever capabilities happen to share criteria and make two capability
scores silently dependent.
"""

from __future__ import annotations

import json
import statistics
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .config import load_yaml, repo_root


class TaxonomyError(Exception):
    pass


@dataclass(frozen=True)
class Capability:
    id: str
    group: str
    description: str


@dataclass(frozen=True)
class Mapping:
    scenario_id: str
    criterion_id: str
    primary: str
    secondary: str | None = None
    granularity: str = "criterion"

    @property
    def key(self) -> str:
        return f"{self.scenario_id}.{self.criterion_id}"


@dataclass
class Taxonomy:
    version: str
    capabilities: dict[str, Capability]
    mappings: list[Mapping]
    awkward_fits: list[dict[str, str]] = field(default_factory=list)

    def for_scenario(self, scenario_id: str) -> list[Mapping]:
        return [m for m in self.mappings if m.scenario_id == scenario_id]

    @property
    def scenarios(self) -> list[str]:
        seen: list[str] = []
        for m in self.mappings:
            if m.scenario_id not in seen:
                seen.append(m.scenario_id)
        return seen


def taxonomy_path(version: str = "0.1", root: Path | None = None) -> Path:
    return (root or repo_root()) / "taxonomy" / f"capabilities-v{version}.yaml"


def load_taxonomy(version: str = "0.1", root: Path | None = None) -> Taxonomy:
    data = load_yaml(taxonomy_path(version, root)) or {}
    capabilities = {
        cid: Capability(id=cid, group=str(body.get("group", "")), description=" ".join(str(body.get("description", "")).split()))
        for cid, body in (data.get("capabilities") or {}).items()
    }
    mappings: list[Mapping] = []
    for key, body in (data.get("criterion_mapping") or {}).items():
        scenario_id, _, criterion_id = key.partition(".")
        if not scenario_id or not criterion_id:
            raise TaxonomyError(f"criterion key {key!r} is not <scenario>.<criterion>")
        primary = body.get("primary")
        if primary not in capabilities:
            raise TaxonomyError(f"{key}: unknown primary capability {primary!r}")
        secondary = body.get("secondary")
        if secondary is not None and secondary not in capabilities:
            raise TaxonomyError(f"{key}: unknown secondary capability {secondary!r}")
        if secondary == primary:
            raise TaxonomyError(f"{key}: secondary duplicates primary")
        mappings.append(
            Mapping(
                scenario_id=scenario_id,
                criterion_id=criterion_id,
                primary=primary,
                secondary=secondary,
                granularity=str(body.get("granularity", "criterion")),
            )
        )
    keys = [m.key for m in mappings]
    if len(keys) != len(set(keys)):
        raise TaxonomyError("a criterion is mapped twice")
    return Taxonomy(
        version=str(data.get("version", version)),
        capabilities=capabilities,
        mappings=mappings,
        awkward_fits=list(data.get("awkward_fits") or []),
    )


# --------------------------------------------------------------------------
# Coverage: what the taxonomy says about the benchmark, before any model
# --------------------------------------------------------------------------


@dataclass
class Coverage:
    capability: str
    group: str
    criteria: list[str]
    scenarios: list[str]
    points: float
    dimension_level: list[str] = field(default_factory=list)

    @property
    def criterion_count(self) -> int:
        return len(self.criteria)

    @property
    def sparse(self) -> bool:
        """One criterion, or confined to a single scenario.

        Either makes the capability score a measurement of one rubric author's
        phrasing as much as of the model.
        """
        return self.criterion_count <= 1 or len(self.scenarios) <= 1


def coverage(taxonomy: Taxonomy, points: dict[str, float]) -> list[Coverage]:
    """Per-capability coverage. `points` maps `<scenario>.<criterion>` to points."""
    out: dict[str, Coverage] = {
        cid: Coverage(capability=cid, group=cap.group, criteria=[], scenarios=[], points=0.0)
        for cid, cap in taxonomy.capabilities.items()
    }
    for mapping in taxonomy.mappings:
        entry = out[mapping.primary]
        entry.criteria.append(mapping.key)
        if mapping.scenario_id not in entry.scenarios:
            entry.scenarios.append(mapping.scenario_id)
        entry.points += points.get(mapping.key, 0.0)
        if mapping.granularity != "criterion":
            entry.dimension_level.append(mapping.key)
    return sorted(out.values(), key=lambda c: (-c.points, c.capability))


def rubric_points(scenario_rubrics: dict[str, Any]) -> dict[str, float]:
    """`<scenario>.<criterion>` -> PASS points, from the rubrics themselves."""
    out: dict[str, float] = {}
    for scenario_id, rubric in scenario_rubrics.items():
        for criterion in rubric.criteria:
            out[f"{scenario_id}.{criterion.id}"] = criterion.points_pass
        if rubric.noise is not None:
            out[f"{scenario_id}.noise_resistance"] = rubric.noise.max_points
    return out


# --------------------------------------------------------------------------
# Profiles: what the taxonomy says about a model
# --------------------------------------------------------------------------


@dataclass
class CapabilityScore:
    capability: str
    earned: float
    possible: float
    criteria: int

    @property
    def percent(self) -> float | None:
        return round(self.earned / self.possible * 100, 1) if self.possible else None


def official_criterion_results(
    evaluator_id: str, scenario_id: str, root: Path | None = None
) -> dict[str, dict[str, tuple[float, float]]]:
    """model -> criterion -> (mean earned across official runs, points possible).

    Averaging each criterion across the model's runs before summing is what
    makes a capability profile reconcile with the scenario score: the scenario
    score is the mean of the run totals, and the mean of the totals equals the
    total of the means.

    The noise dimension has no atomic criteria, so it enters as a single
    pseudo-criterion carrying the dimension's own score. That is the safest
    reproducible treatment available: the underlying false-action flags are
    recorded per run, but the deduction arithmetic that turns them into a
    dimension score belongs to the scoring module, not here.
    """
    base = (root or repo_root()) / "evaluations" / evaluator_id / scenario_id
    out: dict[str, dict[str, list[tuple[float, float]]]] = {}
    if not base.is_dir():
        return {}
    for model_dir in sorted(p for p in base.iterdir() if p.is_dir()):
        per_criterion: dict[str, list[tuple[float, float]]] = {}
        for path in sorted(model_dir.glob("run-*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            for criterion_id, result in payload["criteria"].items():
                per_criterion.setdefault(criterion_id, []).append(
                    (float(result["points_awarded"]), float(result["points_possible"]))
                )
            noise = (payload.get("dimensions") or {}).get("noise_resistance")
            if noise:
                per_criterion.setdefault("noise_resistance", []).append(
                    (float(noise["score"]), float(noise["max_score"]))
                )
        out[model_dir.name] = per_criterion
    return {
        model: {
            criterion: (
                round(statistics.fmean(a for a, _ in samples), 4),
                samples[0][1],
            )
            for criterion, samples in per_criterion.items()
        }
        for model, per_criterion in out.items()
    }


def build_profiles(
    taxonomy: Taxonomy,
    results_by_scenario: dict[str, dict[str, dict[str, tuple[float, float]]]],
) -> tuple[dict[str, dict[str, CapabilityScore]], list[str]]:
    """model -> capability -> score, plus any warnings raised while building."""
    warnings: list[str] = []
    mapped: dict[str, Mapping] = {m.key: m for m in taxonomy.mappings}

    models: set[str] = set()
    for per_model in results_by_scenario.values():
        models.update(per_model)

    profiles: dict[str, dict[str, CapabilityScore]] = {}
    for model in sorted(models):
        buckets: dict[str, CapabilityScore] = {
            cid: CapabilityScore(capability=cid, earned=0.0, possible=0.0, criteria=0)
            for cid in taxonomy.capabilities
        }
        for scenario_id, per_model in results_by_scenario.items():
            results = per_model.get(model)
            if results is None:
                continue
            for criterion_id, (earned, possible) in results.items():
                mapping = mapped.get(f"{scenario_id}.{criterion_id}")
                if mapping is None:
                    warnings.append(
                        f"{scenario_id}.{criterion_id} is scored but not in the taxonomy"
                    )
                    continue
                bucket = buckets[mapping.primary]
                bucket.earned += earned
                bucket.possible += possible
                bucket.criteria += 1
        profiles[model] = {cid: b for cid, b in buckets.items() if b.possible}
    return profiles, sorted(set(warnings))


# --------------------------------------------------------------------------
# Publication
# --------------------------------------------------------------------------
#
# The calculator above only reads. Writing lives here, in one function, so the
# "this cannot modify anything" property of the calculator stays checkable.


def profiles_payload(
    taxonomy: Taxonomy,
    results_by_scenario: dict[str, dict[str, dict[str, tuple[float, float]]]],
    points: dict[str, float],
    display_names: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Everything a reader needs to check a capability profile, as JSON.

    Carries the coverage beside the scores on purpose. A capability measured by
    one criterion in one scenario is a different kind of claim from one measured
    by fifteen across three, and a profile that hides which is which invites
    exactly the over-reading it should prevent.
    """
    profiles, warnings = build_profiles(taxonomy, results_by_scenario)
    display_names = display_names or {}
    scenarios = sorted(results_by_scenario)
    covered = sorted({c for p in profiles.values() for c in p})

    # Coverage restricted to the scenarios that actually contributed, which is
    # not the same as the taxonomy's full coverage: monday-004 is mapped but not
    # yet official.
    official_points = {
        key: value
        for key, value in points.items()
        if key.split(".", 1)[0] in results_by_scenario
    }
    scoped = [c for c in coverage(taxonomy, official_points) if c.capability in covered]

    return {
        "taxonomy_version": taxonomy.version,
        "scenarios": scenarios,
        "note": (
            "Capability scores are points earned divided by points available on the "
            "criteria mapped to that capability, with each criterion averaged across the "
            "model's official runs first - the same aggregation the scenario score uses. "
            "Scoring uses primary mappings only, so no criterion's points are counted "
            "twice. Scores are comparable across models, not across capabilities: the "
            "weighting is the rubrics' own point mass, not a claim about importance."
        ),
        "capabilities": [
            {
                "id": entry.capability,
                "group": taxonomy.capabilities[entry.capability].group,
                "description": taxonomy.capabilities[entry.capability].description,
                "criteria": entry.criterion_count,
                "points": entry.points,
                "scenarios": entry.scenarios,
                "sparse": entry.sparse,
            }
            for entry in scoped
        ],
        "models": [
            {
                "model_slug": slug,
                "display_name": display_names.get(slug, slug),
                "capabilities": {
                    cid: {
                        "percent": score.percent,
                        "earned": round(score.earned, 2),
                        "possible": score.possible,
                    }
                    for cid, score in sorted(profile.items())
                },
            }
            for slug, profile in sorted(profiles.items())
        ],
        "warnings": warnings,
    }
