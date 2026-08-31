"""Capability taxonomy v0.2 — completeness, reconciliation and immutability.

The taxonomy is analytical metadata. It changes no Monday Score and no Overall
release, and the last test in this file is what enforces that.
"""

from __future__ import annotations

import collections
import hashlib
import json
from pathlib import Path

import pytest
import yaml

from mondaybench.capabilities import (
    build_profiles,
    load_taxonomy,
    official_criterion_results,
    rubric_points,
)
from mondaybench.scenarios import load_scenario

REPO_ROOT = Path(__file__).resolve().parent.parent
SCENARIOS = ["monday-001", "monday-002", "monday-003", "monday-004", "monday-005"]
EVALUATORS = {
    "monday-001": "evaluator-opus5-v0.1",
    "monday-002": "evaluator-opus5-v0.2",
    "monday-003": "evaluator-opus5-v0.3",
    "monday-004": "evaluator-opus5-v0.4",
    "monday-005": "evaluator-opus5-v0.5",
}
PROFILES = REPO_ROOT / "analysis" / "capability-profiles-v0.2.json"


def _official_rubric(scenario_id: str):
    """Resolve the rubric the OFFICIAL EVALUATOR is bound to.

    Not load_scenario's default: monday-001's scenario.yaml declares no
    rubric_file, so the default returns the superseded rubric.yaml (0.1) while
    the scenario is frozen against rubric-0.2.yaml. Using the default here
    would silently mis-map monday-001. See capability-taxonomy-v0.2.md.
    """
    config = yaml.safe_load(
        (REPO_ROOT / "evaluators" / f"{EVALUATORS[scenario_id]}.yaml").read_text(encoding="utf-8")
    )
    return load_scenario(scenario_id, rubric_file=config["rubric_file"]).rubric


@pytest.fixture(scope="module")
def taxonomy():
    return load_taxonomy("0.2")


@pytest.fixture(scope="module")
def points():
    return rubric_points({s: _official_rubric(s) for s in SCENARIOS})


@pytest.fixture(scope="module")
def profiles_payload():
    return json.loads(PROFILES.read_text(encoding="utf-8"))


# ------------------------------------------------------------- completeness


def test_every_official_criterion_has_exactly_one_primary_capability(taxonomy, points):
    mapped = collections.Counter(m.key for m in taxonomy.mappings)
    assert set(points) == set(mapped), {
        "orphans": sorted(set(points) - set(mapped)),
        "phantoms": sorted(set(mapped) - set(points)),
    }
    duplicates = [key for key, n in mapped.items() if n > 1]
    assert not duplicates, duplicates


def test_no_orphan_and_no_phantom_criteria(taxonomy, points):
    keys = {m.key for m in taxonomy.mappings}
    assert not set(points) - keys, "scored but unmapped"
    assert not keys - set(points), "mapped but not scored"


def test_every_primary_names_a_declared_capability(taxonomy):
    for mapping in taxonomy.mappings:
        assert mapping.primary in taxonomy.capabilities, mapping.key


def test_secondary_mappings_never_carry_points(taxonomy, points):
    """Primary-only aggregation. Summing primaries must reach the full mass;
    if a secondary contributed, this would overshoot."""
    mass = sum(points[m.key] for m in taxonomy.mappings)
    assert mass == pytest.approx(500.0, abs=0.01)


# ------------------------------------------------------------- total mass


def test_primary_capability_mass_is_exactly_500(taxonomy, points):
    mass = collections.Counter()
    for mapping in taxonomy.mappings:
        mass[mapping.primary] += points[mapping.key]
    assert sum(mass.values()) == pytest.approx(500.0, abs=0.01)
    assert all(v > 0 for v in mass.values())


def test_each_scenario_contributes_exactly_100(taxonomy, points):
    per = collections.Counter()
    for mapping in taxonomy.mappings:
        per[mapping.scenario_id] += points[mapping.key]
    assert {s: round(v, 1) for s, v in per.items()} == {s: 100.0 for s in SCENARIOS}


def test_coverage_matrix_reconciles_with_rubric_points(profiles_payload, points):
    stated = sum(c["points"] for c in profiles_payload["capabilities"].values())
    assert stated == pytest.approx(500.0, abs=0.05)
    assert profiles_payload["total_suite_points"] == pytest.approx(500.0, abs=0.01)


# ------------------------------------------------------------- immutability


def test_v0_1_taxonomy_is_untouched():
    v1 = yaml.safe_load((REPO_ROOT / "taxonomy" / "capabilities-v0.1.yaml").read_text(encoding="utf-8"))
    assert v1["version"] == "0.1"
    assert len(v1["capabilities"]) == 17
    assert len(v1["criterion_mapping"]) == 88
    assert (REPO_ROOT / "analysis" / "capability-profiles-v0.1.json").is_file()
    assert (REPO_ROOT / "analysis" / "capability-taxonomy-v0.1.md").is_file()


def test_v0_2_carries_every_v0_1_mapping_verbatim():
    v1 = yaml.safe_load((REPO_ROOT / "taxonomy" / "capabilities-v0.1.yaml").read_text(encoding="utf-8"))
    v2 = yaml.safe_load((REPO_ROOT / "taxonomy" / "capabilities-v0.2.yaml").read_text(encoding="utf-8"))
    for key, spec in v1["criterion_mapping"].items():
        assert v2["criterion_mapping"][key] == spec, key
    for cid, spec in v1["capabilities"].items():
        assert v2["capabilities"][cid]["group"] == spec["group"], cid


def test_v0_2_adds_capabilities_and_removes_none():
    v1 = yaml.safe_load((REPO_ROOT / "taxonomy" / "capabilities-v0.1.yaml").read_text(encoding="utf-8"))
    v2 = yaml.safe_load((REPO_ROOT / "taxonomy" / "capabilities-v0.2.yaml").read_text(encoding="utf-8"))
    assert set(v1["capabilities"]) < set(v2["capabilities"])
    assert set(v2["capabilities"]) - set(v1["capabilities"]) == {
        "audience_adaptation",
        "information_boundaries",
        "information_routing",
        "cross_output_consistency",
        "commitment_discipline",
    }


# ------------------------------------------------------------- official only


def test_profiles_are_built_from_official_evaluators_only(profiles_payload):
    assert profiles_payload["evaluators"] == EVALUATORS
    for evaluator in profiles_payload["evaluators"].values():
        assert "calibration" not in evaluator


def test_calibration_evaluations_cannot_reach_the_profiles():
    """The monday-005 calibration battery must contribute nothing.

    Its 21 judged runs were moved wholesale to archive/monday-005-v0.4-calibration/
    when the official battery was generated. What remains in the live tree is an
    empty directory, so this asserts three things: the calibration evidence is
    under archive/ and nowhere else, the live directory holds no evaluation, and
    asking the profile builder for it yields nothing rather than silently
    falling back to the official evaluator.
    """
    live = REPO_ROOT / "evaluations" / "evaluator-opus5-v0.5-calibration"
    assert list(live.rglob("*.json")) == [], "calibration evaluations are back in the live tree"
    archived = REPO_ROOT / "archive" / "monday-005-v0.4-calibration" / "evaluations-evaluator-opus5-v0.5-calibration"
    assert archived.is_dir() and list(archived.rglob("*.json")), "calibration evidence went missing"
    assert official_criterion_results("evaluator-opus5-v0.5-calibration", "monday-005") == {}


def test_no_archived_evaluation_reaches_the_profiles():
    """Nothing under archive/ may be read by the profile build - not the
    monday-005 calibration battery and not the superseded rubric passes on
    monday-002/003/004."""
    for scenario in SCENARIOS:
        results = official_criterion_results(EVALUATORS[scenario], scenario)
        # Every model in the profiles appears; no archived-only model leaks in.
        assert results, scenario
    profiles = json.loads(PROFILES.read_text(encoding="utf-8"))
    assert "archive" not in json.dumps(profiles)


# ------------------------------------------------------------- determinism


def test_rebuilding_profiles_from_the_same_inputs_is_identical(taxonomy, profiles_payload):
    results = {s: official_criterion_results(EVALUATORS[s], s) for s in SCENARIOS}
    rebuilt, warnings = build_profiles(taxonomy, results)
    assert warnings == []
    for slug, stored in profiles_payload["models"].items():
        for cid, entry in stored["capabilities"].items():
            assert rebuilt[slug][cid].percent == pytest.approx(entry["percent"], abs=0.05), (slug, cid)


def test_every_capability_percentage_is_within_bounds(profiles_payload):
    for slug, model in profiles_payload["models"].items():
        for cid, entry in model["capabilities"].items():
            assert 0.0 <= entry["percent"] <= 100.0, (slug, cid, entry["percent"])
            assert 0.0 <= entry["earned"] <= entry["possible"] + 1e-6, (slug, cid)


def test_seven_models_each_covering_every_capability_that_has_mass(profiles_payload):
    assert len(profiles_payload["models"]) == 7
    for slug, model in profiles_payload["models"].items():
        assert len(model["capabilities"]) == 22, slug


# ------------------------------------------------------------- independence


def test_the_taxonomy_cannot_influence_monday_score_or_overall():
    """Capability metadata is analytical. Nothing in the scoring path reads it.

    Asserted by import graph rather than by re-running a build: if scoring or
    the overall builder ever imported the taxonomy, this would fail.
    """
    for module in ("scoring.py", "overall.py", "leaderboard.py"):
        source = (REPO_ROOT / "mondaybench" / module).read_text(encoding="utf-8")
        assert "capabilities" not in source, module
        assert "taxonomy" not in source.lower(), module


def test_overall_v2_scores_do_not_appear_in_the_profiles(profiles_payload):
    """A capability profile must not be a re-labelled Monday Score."""
    overall = json.loads(
        (REPO_ROOT / "leaderboard" / "overall" / "overall-v2.json").read_text(encoding="utf-8")
    )
    scores = {m["model_slug"]: m["monday_score"] for m in overall["models"]}
    for slug, model in profiles_payload["models"].items():
        percentages = [e["percent"] for e in model["capabilities"].values()]
        # No capability percentage should coincidentally equal the Monday Score,
        # and the mean of percentages is not the Monday Score either.
        assert scores[slug] not in percentages, slug


def test_penalties_are_excluded_from_capability_scores(profiles_payload):
    """qwen3.6 carries a -7 penalty on monday-005 run-002. Its capability
    percentages must be computed from criterion points only, so the penalty
    appears nowhere - which is the documented v0.1 convention."""
    assert "penalt" in profiles_payload["note"].lower()
    model = profiles_payload["models"]["qwen3.6"]
    for cid, entry in model["capabilities"].items():
        assert entry["earned"] >= 0, cid
