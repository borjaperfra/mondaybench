"""The leaderboard must not write a draft where a published result lives.

Two accidents, one shape. During the monday-003 v0.2 sweep a plain
`mondaybench leaderboard --scenario monday-003` wrote a calibration ranking into
`leaderboard/monday-003/`, beside the official results, where nothing about the
file says it was one run per model against a rubric still being edited. Minutes
later a plain `leaderboard --scenario monday-001` overwrote the *published* v0.1
leaderboard with a non-official rebuild carrying a "NOT AN OFFICIAL RESULT"
banner - same numbers, wrong status.

Both are now refusals. `--official` still overwrites, because that is the
command whose whole job is to publish.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from mondaybench.leaderboard import (
    ModelSummary,
    calibration_leaderboard_dir,
    leaderboard_dir,
    write_leaderboard,
)
from mondaybench.scenarios import load_scenario

REPO_ROOT = Path(__file__).resolve().parent.parent


def summary(slug: str = "glm5.2", mean: float = 90.0) -> ModelSummary:
    return ModelSummary(
        model_slug=slug,
        display_name=slug,
        runs=1,
        mean=mean,
        minimum=mean,
        maximum=mean,
        stddev=0.0,
        dimensions={"resource_allocation": mean},
        median_ttfa_ms=None,
        median_total_latency_ms=None,
        median_cost_usd=None,
        median_ttft_ms=None,
        median_output_tokens=None,
        prompt_sha256="0" * 64,
        rubric_version="0.3",
        judge_model_id="claude-opus-5",
        rank=1,
        run_scores=[mean],
    )


def payload(status: str | None, official: bool = False, scenario: str = "monday-003") -> dict:
    return {
        "benchmark_version": "0.3-draft",
        "scenario": scenario,
        "evaluator": "evaluator-opus5-v0.3-calibration-3",
        "generated_at": "2026-08-28T00:00:00Z",
        "scenario_status": status,
        "official": official,
        "integrity_warning": None,
        "models": [],
    }


# --------------------------------------------------------------------------
# The calibration gate
# --------------------------------------------------------------------------


def test_a_calibration_ranking_is_refused_by_default(tmp_path):
    with pytest.raises(ValueError, match="status=calibration"):
        write_leaderboard(payload("calibration"), [summary()], root=tmp_path)
    assert not (tmp_path / "leaderboard").exists()


def test_a_calibration_ranking_lands_under_analysis_when_asked(tmp_path):
    paths = write_leaderboard(
        payload("calibration"), [summary()], root=tmp_path, calibration=True
    )
    for path in paths:
        assert path.is_file()
        assert (tmp_path / "analysis" / "leaderboards" / "monday-003") == path.parent
        assert "leaderboard" not in path.relative_to(tmp_path).parts[:1]
    assert not (tmp_path / "leaderboard").exists()


def test_the_calibration_directory_is_never_under_the_official_tree(tmp_path):
    official = leaderboard_dir("monday-003", tmp_path)
    draft = calibration_leaderboard_dir("monday-003", tmp_path)
    assert official.parts[-2:] == ("leaderboard", "monday-003")
    assert draft.parts[-3:] == ("analysis", "leaderboards", "monday-003")
    assert (tmp_path / "leaderboard") not in draft.parents


def test_a_frozen_scenario_still_writes_where_it_always_did(tmp_path):
    paths = write_leaderboard(payload("frozen", scenario="monday-002"), [summary()], root=tmp_path)
    assert paths[0].parent == tmp_path / "leaderboard" / "monday-002"


def test_monday_001_keeps_its_bare_directory(tmp_path):
    paths = write_leaderboard(payload("frozen", scenario="monday-001"), [summary()], root=tmp_path)
    assert paths[0].parent == tmp_path / "leaderboard"


# --------------------------------------------------------------------------
# The downgrade gate
# --------------------------------------------------------------------------


def _publish(tmp_path, scenario="monday-001"):
    paths = write_leaderboard(payload("frozen", official=True, scenario=scenario), [summary()], root=tmp_path)
    return paths[0]


def test_a_published_leaderboard_is_not_overwritten_by_a_plain_rebuild(tmp_path):
    published = _publish(tmp_path)
    before = published.read_bytes()
    with pytest.raises(ValueError, match="published official leaderboard"):
        write_leaderboard(
            payload("frozen", official=False, scenario="monday-001"),
            [summary(mean=1.0)],
            root=tmp_path,
        )
    assert published.read_bytes() == before


def test_publishing_over_a_published_leaderboard_is_still_allowed(tmp_path):
    _publish(tmp_path)
    paths = write_leaderboard(
        payload("frozen", official=True, scenario="monday-001"),
        [summary(mean=91.0)],
        root=tmp_path,
    )
    written = json.loads(paths[0].read_text(encoding="utf-8"))
    assert written["official"] is True
    assert written["models"] == []


def test_a_plain_rebuild_is_fine_where_nothing_official_exists(tmp_path):
    paths = write_leaderboard(
        payload("frozen", official=False, scenario="monday-002"), [summary()], root=tmp_path
    )
    assert paths[0].is_file()


# --------------------------------------------------------------------------
# The real repository
# --------------------------------------------------------------------------


def test_no_scenario_in_the_repository_is_left_in_calibration():
    """All three are frozen. The gate is kept for the next one."""
    for scenario_id in ("monday-001", "monday-002", "monday-003"):
        assert load_scenario(scenario_id).is_calibration is False, scenario_id


def test_no_draft_ranking_sits_in_the_published_tree():
    """The file this whole module exists because of."""
    for path in (REPO_ROOT / "leaderboard").rglob("leaderboard.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data.get("official") is True, path


def test_every_published_leaderboard_declares_itself_official():
    published = sorted((REPO_ROOT / "leaderboard").rglob("leaderboard.json"))
    scenarios = set()
    for path in published:
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data.get("official") is True, path
        scenarios.add(data["scenario"])
    assert scenarios == {"monday-001", "monday-002", "monday-003", "monday-004", "monday-005"}
