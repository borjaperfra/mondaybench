"""The capability taxonomy: what kind of work is a model good at?

It is not a scoring system, and the tests that matter most are the ones that
keep it from becoming one by accident - it must not double-count, must not
reweight, must not touch a rubric, and must aggregate runs the same way the
scenario score does.
"""

from __future__ import annotations

import statistics
from pathlib import Path

import pytest

from mondaybench.capabilities import (
    TaxonomyError,
    build_profiles,
    coverage,
    load_taxonomy,
    official_criterion_results,
    rubric_points,
)
from mondaybench.scenarios import load_scenario

REPO_ROOT = Path(__file__).resolve().parent.parent

# scenario -> the rubric each is scored against, and its official evaluator.
RUBRICS = {
    "monday-001": "rubric-0.2.yaml",
    "monday-002": "rubric.yaml",
    "monday-003": "rubric.yaml",
    "monday-004": "rubric-0.3.yaml",
}
OFFICIAL_EVALUATORS = {
    "monday-001": "evaluator-opus5-v0.1",
    "monday-002": "evaluator-opus5-v0.2",
    "monday-003": "evaluator-opus5-v0.3",
}


@pytest.fixture(scope="module")
def taxonomy():
    return load_taxonomy()


@pytest.fixture(scope="module")
def points():
    return rubric_points(
        {sid: load_scenario(sid, rubric_file=rf).rubric for sid, rf in RUBRICS.items()}
    )


# --------------------------------------------------------------------------
# The mapping is complete and well formed
# --------------------------------------------------------------------------


def test_every_rubric_criterion_is_mapped(taxonomy, points):
    """A capability score computed over a partial mapping means nothing."""
    mapped = {m.key for m in taxonomy.mappings}
    assert set(points) - mapped == set()


def test_nothing_is_mapped_that_does_not_exist(taxonomy, points):
    """A stale mapping would silently contribute zero points forever."""
    mapped = {m.key for m in taxonomy.mappings}
    assert mapped - set(points) == set()


def test_all_four_scenarios_are_covered(taxonomy):
    assert set(taxonomy.scenarios) == set(RUBRICS)
    assert len(taxonomy.mappings) == 88  # 87 atomic criteria + the noise dimension


def test_every_capability_has_at_least_one_criterion(taxonomy, points):
    """A capability with no criteria is a claim the benchmark cannot support."""
    empty = [c.capability for c in coverage(taxonomy, points) if c.criterion_count == 0]
    assert empty == []


def test_the_loader_rejects_a_malformed_mapping(tmp_path):
    directory = tmp_path / "taxonomy"
    directory.mkdir()
    body = """
version: "9.9"
capabilities:
  alpha: {group: g, description: d}
criterion_mapping:
  monday-001.x: {primary: nope}
"""
    (directory / "capabilities-v9.9.yaml").write_text(body, encoding="utf-8")
    with pytest.raises(TaxonomyError, match="unknown primary"):
        load_taxonomy("9.9", root=tmp_path)

    body = body.replace("primary: nope", "primary: alpha, secondary: alpha")
    (directory / "capabilities-v9.9.yaml").write_text(
        body.replace("{primary: alpha, secondary: alpha}", "{primary: alpha, secondary: alpha}"),
        encoding="utf-8",
    )
    with pytest.raises(TaxonomyError, match="duplicates primary"):
        load_taxonomy("9.9", root=tmp_path)


# --------------------------------------------------------------------------
# The aggregation policy
# --------------------------------------------------------------------------


def test_scoring_uses_primary_mappings_only(taxonomy, points):
    """Secondary tags are metadata. Counting them would double the points."""
    with_secondary = [m for m in taxonomy.mappings if m.secondary]
    assert with_secondary, "the policy is only meaningful if secondaries exist"

    total_mapped = sum(c.points for c in coverage(taxonomy, points))
    assert total_mapped == pytest.approx(sum(points.values()))

    # If secondaries were counted, these criteria's points would appear twice.
    doubled = total_mapped + sum(points[m.key] for m in with_secondary)
    assert total_mapped < doubled


def test_capability_points_sum_to_the_rubric_points(taxonomy, points):
    """Every point in every rubric lands in exactly one capability."""
    by_capability = {c.capability: c.points for c in coverage(taxonomy, points)}
    assert sum(by_capability.values()) == pytest.approx(sum(points.values()))
    assert sum(points.values()) == 400.0


def test_no_capability_is_reweighted(taxonomy, points):
    """v0.1 uses the rubrics' natural point mass. No normalisation between
    capabilities, which would invent an importance ordering the benchmark does
    not support."""
    values = sorted(c.points for c in coverage(taxonomy, points))
    # Deliberately uneven: 4 points at one end, 63 at the other.
    assert values[0] == 4.0 and values[-1] == 63.0


# --------------------------------------------------------------------------
# Profiles
# --------------------------------------------------------------------------


@pytest.fixture(scope="module")
def official_results():
    return {sid: official_criterion_results(ev, sid) for sid, ev in OFFICIAL_EVALUATORS.items()}


def test_profiles_use_official_scenarios_only(taxonomy, official_results):
    """monday-004 is frozen but not official; nothing from it may enter."""
    profiles, warnings = build_profiles(taxonomy, official_results)
    assert warnings == []
    covered = {c for p in profiles.values() for c in p}
    # These three are measured only by monday-004, so they must be absent.
    assert covered.isdisjoint({"business_judgment", "data_cleaning", "entity_resolution"})


def test_every_model_gets_a_profile(taxonomy, official_results):
    """The invariant is coverage, not a headcount.

    This asserted `len(profiles) == 7` until v1.1, which made it fail for any
    eighth model - by construction, and for no methodological reason. What the
    test is actually for is that no model with official results is silently
    left without a profile, and that no percentage escapes its range.
    """
    profiles, _ = build_profiles(taxonomy, official_results)
    expected = {slug for results in official_results.values() for slug in results}
    assert set(profiles) == expected
    assert len(profiles) == len(set(profiles)), "a model slug is profiled twice"
    assert profiles, "no model was profiled at all"
    for model, profile in profiles.items():
        assert profile, model
        for score in profile.values():
            assert 0.0 <= score.percent <= 100.0, (model, score.capability)


def test_criteria_are_averaged_across_runs_not_cherry_picked(taxonomy):
    """The scenario score is the mean of the run totals. A capability score has
    to use the same runs the same way, or the two describe different batteries.
    """
    results = official_criterion_results("evaluator-opus5-v0.1", "monday-001")
    earned, possible = results["glm5.2"]["umbrella_error_rate"]
    # Read the three runs directly and confirm the mean, not the max.
    import json

    raw = [
        json.loads(p.read_text(encoding="utf-8"))["criteria"]["umbrella_error_rate"]
        for p in sorted(
            (REPO_ROOT / "evaluations" / "evaluator-opus5-v0.1" / "monday-001" / "glm5.2").glob("run-*.json")
        )
    ]
    awarded = [r["points_awarded"] for r in raw]
    assert len(awarded) == 3
    assert earned == pytest.approx(statistics.fmean(awarded))
    if len(set(awarded)) > 1:
        assert earned != max(awarded), "a mean, not a best-of"
    assert possible == raw[0]["points_possible"]


def test_a_capability_total_reconciles_with_the_criteria_beneath_it(taxonomy, official_results):
    profiles, _ = build_profiles(taxonomy, official_results)
    profile = profiles["qwen3.8-flash"]
    by_primary: dict[str, float] = {}
    for scenario_id, per_model in official_results.items():
        for criterion_id, (earned, _) in per_model["qwen3.8-flash"].items():
            mapping = next(
                m for m in taxonomy.mappings
                if m.scenario_id == scenario_id and m.criterion_id == criterion_id
            )
            by_primary[mapping.primary] = by_primary.get(mapping.primary, 0.0) + earned
    for capability, total in by_primary.items():
        assert profile[capability].earned == pytest.approx(total)


def test_the_profile_reconciles_with_the_published_scenario_score(taxonomy):
    """Summing every capability's earned points for one scenario must give the
    model's base score on it - proof that the profile is a decomposition of the
    same result and not a parallel measurement."""
    import json

    results = official_criterion_results("evaluator-opus5-v0.3", "monday-003")
    profiles, _ = build_profiles(taxonomy, {"monday-003": results})
    for model, profile in profiles.items():
        earned = sum(s.earned for s in profile.values())
        evaluations = sorted(
            (REPO_ROOT / "evaluations" / "evaluator-opus5-v0.3" / "monday-003" / model).glob("run-*.json")
        )
        bases = [json.loads(p.read_text(encoding="utf-8"))["base_score"] for p in evaluations]
        assert earned == pytest.approx(statistics.fmean(bases), abs=0.01), model


# --------------------------------------------------------------------------
# Honesty about weakness
# --------------------------------------------------------------------------


def test_sparse_capabilities_are_detected_not_hidden(taxonomy, points):
    sparse = {c.capability for c in coverage(taxonomy, points) if c.sparse}
    assert "entity_resolution" in sparse  # one criterion, one scenario
    assert "data_cleaning" in sparse  # two criteria, one scenario
    # And the report has to name them.
    report = (REPO_ROOT / "analysis" / "capability-taxonomy-v0.1.md").read_text(encoding="utf-8")
    for capability in sparse:
        assert capability in report, capability


def test_the_dimension_level_entry_is_flagged(taxonomy, points):
    """monday-001's noise dimension is not an atomic criterion and must say so."""
    entry = next(c for c in coverage(taxonomy, points) if c.capability == "action_safety")
    assert entry.dimension_level == ["monday-001.noise_resistance"]
    mapping = next(m for m in taxonomy.mappings if m.criterion_id == "noise_resistance")
    assert mapping.granularity == "dimension"


def test_awkward_fits_are_recorded(taxonomy):
    assert len(taxonomy.awkward_fits) >= 3
    keys = {entry["criterion"] for entry in taxonomy.awkward_fits}
    # The one that motivates monday-005 must be among them.
    assert "monday-004.revenue_conclusion" in keys


def test_the_report_names_what_the_benchmark_does_not_measure():
    report = (REPO_ROOT / "analysis" / "capability-taxonomy-v0.1.md").read_text(encoding="utf-8")
    assert "WHAT MONDAYBENCH DOES NOT MEASURE YET" in report
    for gap in ("Communication to an audience", "Information boundaries", "Cross-output consistency"):
        assert gap in report, gap


# --------------------------------------------------------------------------
# It must not be able to change anything
# --------------------------------------------------------------------------


@pytest.mark.parametrize("scenario_id", sorted(RUBRICS))
def test_the_taxonomy_touches_no_scenario(scenario_id):
    from mondaybench.freeze import check_drift, load_manifest

    directory = REPO_ROOT / "scenarios" / scenario_id
    manifest = load_manifest(directory)
    assert manifest is not None, scenario_id
    drift = check_drift(manifest, directory)
    assert drift.clean, (scenario_id, drift.changed, drift.missing)


def test_the_taxonomy_lives_outside_the_scenario_directories():
    assert (REPO_ROOT / "taxonomy" / "capabilities-v0.1.yaml").is_file()
    for scenario_id in RUBRICS:
        assert not list((REPO_ROOT / "scenarios" / scenario_id).glob("*capabilit*"))


def test_the_calculator_only_reads(tmp_path, taxonomy):
    """Building a profile must create and modify nothing."""
    import inspect

    from mondaybench import capabilities as module

    source = inspect.getsource(module)
    for forbidden in ("write_text(", "mkdir(", "open(", "unlink("):
        assert forbidden not in source, forbidden
