"""Rubric resolution: a frozen scenario must score against the rubric it is frozen with.

The defect these pin: `scenarios/monday-001/scenario.yaml` declares no
`rubric_file`, so `load_scenario("monday-001")` fell back to the directory
default `rubric.yaml` - which is version 0.1 and superseded - while
`FROZEN.yaml` freezes the scenario against `rubric-0.2.yaml` and
`evaluator-opus5-v0.1` scores against `rubric-0.2.yaml`.

Every other scenario declared its rubric, so every other scenario resolved
correctly. That is what made it invisible: an analysis that looped over five
scenarios got four right and one silently wrong.

The repair reads the frozen manifest instead of guessing, so no frozen artifact
had to be edited to fix it.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from mondaybench.freeze import load_manifest
from mondaybench.scenarios import ScenarioError, load_scenario

REPO_ROOT = Path(__file__).resolve().parent.parent
SCENARIOS = ["monday-001", "monday-002", "monday-003", "monday-004", "monday-005"]
EVALUATORS = {
    "monday-001": "evaluator-opus5-v0.1",
    "monday-002": "evaluator-opus5-v0.2",
    "monday-003": "evaluator-opus5-v0.3",
    "monday-004": "evaluator-opus5-v0.4",
    "monday-005": "evaluator-opus5-v0.5",
}


def _evaluator_rubric(scenario_id: str) -> str:
    config = yaml.safe_load(
        (REPO_ROOT / "evaluators" / f"{EVALUATORS[scenario_id]}.yaml").read_text(encoding="utf-8")
    )
    return config["rubric_file"]


# --------------------------------------------------------------- the defect


def test_monday_001_default_load_returns_the_frozen_rubric_not_rubric_yaml():
    """The exact bug. Before the repair this returned rubric.yaml (0.1)."""
    loaded = load_scenario("monday-001")
    assert loaded.rubric_file == "rubric-0.2.yaml"
    assert str(loaded.rubric.version) == "0.2"


def test_monday_001_default_load_agrees_with_its_official_evaluator():
    """A default load and the scoring path must not disagree about the rubric."""
    default = load_scenario("monday-001")
    official = load_scenario("monday-001", rubric_file=_evaluator_rubric("monday-001"))
    assert default.rubric_file == official.rubric_file
    assert [c.id for c in default.rubric.criteria] == [c.id for c in official.rubric.criteria]


def test_the_superseded_rubric_is_still_on_disk_and_still_loadable():
    """The repair must not delete history. Scores produced under 0.1 stay
    reproducible by naming it explicitly."""
    superseded = load_scenario("monday-001", rubric_file="rubric.yaml")
    assert str(superseded.rubric.version) == "0.1"
    assert [c.id for c in superseded.rubric.criteria] != [
        c.id for c in load_scenario("monday-001").rubric.criteria
    ]


# --------------------------------------------------------------- every scenario


@pytest.mark.parametrize("scenario_id", SCENARIOS)
def test_default_load_matches_the_frozen_manifest(scenario_id):
    manifest = load_manifest(REPO_ROOT / "scenarios" / scenario_id)
    assert manifest is not None, f"{scenario_id} is not frozen"
    assert load_scenario(scenario_id).rubric_file == manifest.rubric_file


@pytest.mark.parametrize("scenario_id", SCENARIOS)
def test_default_load_matches_the_official_evaluator(scenario_id):
    """The property the capability taxonomy depends on: looping over scenarios
    with a plain load_scenario() now scores against the same rubric the
    evaluator does, for all five."""
    assert load_scenario(scenario_id).rubric_file == _evaluator_rubric(scenario_id)


@pytest.mark.parametrize("scenario_id", SCENARIOS)
def test_frozen_manifest_and_evaluator_agree(scenario_id):
    manifest = load_manifest(REPO_ROOT / "scenarios" / scenario_id)
    assert manifest.rubric_file == _evaluator_rubric(scenario_id)


# --------------------------------------------------------------- precedence


def test_an_explicit_rubric_file_still_wins():
    """An evaluator may deliberately score against a superseded rubric to
    reproduce an old calibration. The repair must not take that away."""
    assert load_scenario("monday-001", rubric_file="rubric.yaml").rubric_file == "rubric.yaml"
    assert load_scenario("monday-005", rubric_file="rubric-0.3.yaml").rubric_file == "rubric-0.3.yaml"


def test_scenario_yaml_wins_over_the_manifest_when_it_declares_one(tmp_path):
    """The manifest is a fallback for silence, not an override. Four of five
    scenarios declare a rubric and must keep resolving from their own file."""
    for scenario_id in ("monday-002", "monday-003", "monday-004", "monday-005"):
        meta = yaml.safe_load(
            (REPO_ROOT / "scenarios" / scenario_id / "scenario.yaml").read_text(encoding="utf-8")
        )
        assert "rubric_file" in meta
        assert load_scenario(scenario_id).rubric_file == meta["rubric_file"]


# --------------------------------------------------------------- the guard


def test_a_scenario_disagreeing_with_its_manifest_is_an_error(tmp_path):
    """The class of bug, not just the instance.

    A scenario.yaml that names one rubric while FROZEN.yaml freezes another is
    an integrity failure: one of the two is wrong and the loader cannot know
    which. It must refuse rather than pick.
    """
    directory = tmp_path / "monday-999"
    source = REPO_ROOT / "scenarios" / "monday-005"
    directory.mkdir()
    for path in source.iterdir():
        if path.is_file():
            (directory / path.name).write_bytes(path.read_bytes())

    meta = yaml.safe_load((directory / "scenario.yaml").read_text(encoding="utf-8"))
    meta["rubric_file"] = "rubric-0.3.yaml"  # manifest freezes rubric-0.4.yaml
    (directory / "scenario.yaml").write_text(yaml.safe_dump(meta), encoding="utf-8")

    with pytest.raises(ScenarioError) as exc:
        load_scenario("monday-999", directory=directory)
    message = str(exc.value)
    assert "rubric-0.3.yaml" in message and "rubric-0.4.yaml" in message
    assert "FROZEN.yaml" in message


def test_an_unfrozen_scenario_still_falls_back_to_rubric_yaml(tmp_path):
    """A scenario under development has no manifest. It must still load."""
    directory = tmp_path / "monday-998"
    source = REPO_ROOT / "scenarios" / "monday-003"
    directory.mkdir()
    for path in source.iterdir():
        if path.is_file() and path.name != "FROZEN.yaml":
            (directory / path.name).write_bytes(path.read_bytes())
    meta = yaml.safe_load((directory / "scenario.yaml").read_text(encoding="utf-8"))
    meta.pop("rubric_file", None)
    meta["id"] = "monday-998"
    (directory / "scenario.yaml").write_text(yaml.safe_dump(meta), encoding="utf-8")

    assert load_scenario("monday-998", directory=directory).rubric_file == "rubric.yaml"


# --------------------------------------------------------------- no score moved


def test_the_repair_moves_no_published_score():
    """The whole point of fixing this in the resolver rather than in the
    scenario: the scoring path already used the evaluator's rubric_file, so
    correcting the default cannot change any published number."""
    import json

    board = json.loads((REPO_ROOT / "leaderboard" / "leaderboard.json").read_text(encoding="utf-8"))
    assert board["rubric_version"] == "0.2"
    scores = {m["model_slug"]: m["score"]["mean"] for m in board["models"]}
    assert scores["glm5.3-flash"] == pytest.approx(98.0, abs=0.005)
    assert scores["gemma4"] == pytest.approx(70.67, abs=0.005)


def test_no_frozen_artifact_was_edited_to_achieve_the_repair():
    """monday-001's FROZEN.yaml already named the right rubric. The repair
    reads it; it does not rewrite it. Drift here means the repair was done the
    unsafe way."""
    from mondaybench.freeze import check_drift

    for scenario_id in SCENARIOS:
        directory = REPO_ROOT / "scenarios" / scenario_id
        manifest = load_manifest(directory)
        assert check_drift(manifest, directory).clean, scenario_id
