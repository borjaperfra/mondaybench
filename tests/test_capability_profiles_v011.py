"""The v0.1 profiles staleness repair.

`analysis/capability-profiles-v0.1.json` was generated before monday-004 was
official and covers three of the four scenarios its own taxonomy maps. The
repair does not rewrite it - it is the artifact the v0.1 report was published
from. Instead a v0.1.1 revision applies the SAME, UNMODIFIED v0.1 taxonomy to
all four, and the original carries an erratum pointing at it.

The root cause is a profile build that silently used whichever scenarios
happened to be official at the time. The last test here is the one that stops
that recurring.
"""

from __future__ import annotations

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
ANALYSIS = REPO_ROOT / "analysis"
EVALUATORS = {
    "monday-001": "evaluator-opus5-v0.1",
    "monday-002": "evaluator-opus5-v0.2",
    "monday-003": "evaluator-opus5-v0.3",
    "monday-004": "evaluator-opus5-v0.4",
}


@pytest.fixture(scope="module")
def original():
    return json.loads((ANALYSIS / "capability-profiles-v0.1.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def revised():
    return json.loads((ANALYSIS / "capability-profiles-v0.1.1.json").read_text(encoding="utf-8"))


# ------------------------------------------------------- the original is intact


def test_the_original_profiles_are_not_rewritten(original):
    """The stale file stays exactly as published. It is what the v0.1 report was
    written from; changing it would move numbers a reader has already cited."""
    assert original["scenarios"] == ["monday-001", "monday-002", "monday-003"]
    assert len(original["capabilities"]) == 14
    assert sum(c["points"] for c in original["capabilities"]) == 300.0
    assert "profiles_revision" not in original


def test_the_v0_1_taxonomy_itself_is_untouched():
    v1 = yaml.safe_load(
        (REPO_ROOT / "taxonomy" / "capabilities-v0.1.yaml").read_text(encoding="utf-8")
    )
    assert v1["version"] == "0.1"
    assert len(v1["criterion_mapping"]) == 88
    assert len(v1["capabilities"]) == 17


def test_the_stale_report_carries_an_erratum_naming_the_wrong_finding():
    text = (ANALYSIS / "capability-taxonomy-v0.1.md").read_text(encoding="utf-8")
    head = text[:3000]
    assert "ERRATUM" in head
    assert "capability-profiles-v0.1.1.json" in head
    # The specific claim that did not survive the extra evidence.
    assert "copies accurately" in head and "68.8" in head


# ------------------------------------------------------- the revision is correct


def test_the_revision_covers_every_scenario_the_v0_1_taxonomy_maps(revised):
    taxonomy = load_taxonomy("0.1")
    mapped = sorted({m.scenario_id for m in taxonomy.mappings})
    assert mapped == ["monday-001", "monday-002", "monday-003", "monday-004"]
    assert revised["scenarios"] == mapped


def test_the_revision_carries_the_full_400_points_and_17_capabilities(revised):
    assert len(revised["capabilities"]) == 17
    assert sum(c["points"] for c in revised["capabilities"]) == pytest.approx(400.0, abs=0.05)


def test_the_revision_restores_exactly_the_three_missing_capabilities(original, revised):
    before = {c["id"] for c in original["capabilities"]}
    after = {c["id"] for c in revised["capabilities"]}
    assert after - before == {"business_judgment", "data_cleaning", "entity_resolution"}
    assert not before - after, "the revision must not drop a capability"


def test_the_revision_uses_the_unmodified_v0_1_taxonomy(revised):
    """Not a quiet v0.2. Same version, same 17 capabilities, same descriptions."""
    assert revised["taxonomy_version"] == "0.1"
    taxonomy = load_taxonomy("0.1")
    assert {c["id"] for c in revised["capabilities"]} == set(taxonomy.capabilities)
    for entry in revised["capabilities"]:
        expected = " ".join(str(taxonomy.capabilities[entry["id"]].description).split())
        assert entry["description"] == expected, entry["id"]


def test_the_revision_reproduces_from_the_taxonomy_and_official_evaluations(revised):
    taxonomy = load_taxonomy("0.1")
    profiles, warnings = build_profiles(
        taxonomy, {s: official_criterion_results(e, s) for s, e in EVALUATORS.items()}
    )
    assert warnings == []
    for model in revised["models"]:
        for cid, entry in model["capabilities"].items():
            assert profiles[model["model_slug"]][cid].percent == pytest.approx(
                entry["percent"], abs=0.05
            ), (model["model_slug"], cid)


def test_the_revision_keeps_the_v0_1_schema(original, revised):
    """It must be a drop-in replacement, not a new format."""
    assert set(original) <= set(revised)
    assert isinstance(revised["capabilities"], list)
    assert isinstance(revised["models"], list)
    assert [m["model_slug"] for m in revised["models"]] == [
        m["model_slug"] for m in original["models"]
    ] or sorted(m["model_slug"] for m in revised["models"]) == sorted(
        m["model_slug"] for m in original["models"]
    )
    for model in revised["models"]:
        assert set(model) == {"model_slug", "display_name", "capabilities"}


def test_the_revision_explains_itself_in_the_artifact(revised):
    """A reader who opens the JSON without the report must learn why it exists."""
    why = revised["why_this_exists"]
    assert "monday-004" in why and "300" in why and "400" in why
    assert revised["supersedes"] == "analysis/capability-profiles-v0.1.json"


# ------------------------------------------------------- the root cause


def test_a_profile_build_covers_every_scenario_its_taxonomy_maps():
    """The generalised guard. The v0.1 defect was a build that silently used the
    scenarios that happened to be official rather than the ones the taxonomy
    maps. Any published profile set must cover all of them."""
    for version, path in (
        ("0.1", ANALYSIS / "capability-profiles-v0.1.1.json"),
        ("0.2", ANALYSIS / "capability-profiles-v0.2.json"),
    ):
        payload = json.loads(path.read_text(encoding="utf-8"))
        mapped = sorted({m.scenario_id for m in load_taxonomy(version).mappings})
        assert sorted(payload["scenarios"]) == mapped, path.name


def test_the_point_mass_of_a_profile_set_matches_its_taxonomy():
    """The arithmetic check that would have caught it: 300 published against a
    400-point taxonomy."""
    for version, path, scenarios, expected in (
        ("0.1", ANALYSIS / "capability-profiles-v0.1.1.json",
         ["monday-001", "monday-002", "monday-003", "monday-004"], 400.0),
        ("0.2", ANALYSIS / "capability-profiles-v0.2.json",
         ["monday-001", "monday-002", "monday-003", "monday-004", "monday-005"], 500.0),
    ):
        taxonomy = load_taxonomy(version)
        points = rubric_points({s: load_scenario(s).rubric for s in scenarios})
        assert sum(points[m.key] for m in taxonomy.mappings) == pytest.approx(expected, abs=0.05)

        payload = json.loads(path.read_text(encoding="utf-8"))
        entries = (
            payload["capabilities"]
            if isinstance(payload["capabilities"], list)
            else payload["capabilities"].values()
        )
        assert sum(c["points"] for c in entries) == pytest.approx(expected, abs=0.05), path.name
