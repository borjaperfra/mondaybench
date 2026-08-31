"""The Overall leaderboard: one Monday Score across scenarios.

Two properties carry the whole thing, and both are easy to break by accident.

**Completeness.** Averaging over whichever scenarios a model happens to have
finished would reward not competing: a model that skipped the one it was worst
at would outrank one that took all four.

**Immutability.** A published Overall score must not move when a later scenario
is added. Overall v1 and Overall v2 are different claims about different sets of
scenarios, and both stay reproducible.

Everything else here guards the boundary between the score and the observability
numbers that sit beside it.
"""

from __future__ import annotations

import json
import statistics
from dataclasses import replace
from pathlib import Path

import pytest
import yaml

from mondaybench.overall import (
    AGGREGATION_ARITHMETIC_MEAN,
    ModelOverall,
    OverallError,
    OverallRelease,
    ScenarioPin,
    build_overall,
    check_score_recomputes,
    load_releases,
    validate_release,
    write_overall,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
PUBLISHED = ("monday-001", "monday-002", "monday-003")


# --------------------------------------------------------------------------
# Fixtures: a synthetic repository, so nothing here depends on live results
# --------------------------------------------------------------------------


def _leaderboard(scenario_id, models, *, official=True, status=None, sha="a" * 64, rubric="1.0"):
    return {
        "benchmark_version": "0.9",
        "scenario": scenario_id,
        "evaluator": f"evaluator-{scenario_id}",
        "generated_at": "2026-08-30T00:00:00Z",
        "scenario_status": status,
        "integrity_warning": None,
        "official": official,
        "frozen_prompt_sha256": sha,
        "rubric_version": rubric,
        "models": [
            {
                "rank": i,
                "model_slug": slug,
                "display_name": slug.upper(),
                "score": {
                    "mean": round(statistics.fmean(runs), 2),
                    "min": min(runs),
                    "max": max(runs),
                    "range": round(max(runs) - min(runs), 2),
                    "stddev": round(statistics.stdev(runs), 2) if len(runs) > 1 else 0.0,
                    "runs": len(runs),
                },
                "run_scores": runs,
            }
            for i, (slug, runs) in enumerate(models.items(), start=1)
        ],
    }


def _write(root: Path, scenario_id: str, payload: dict) -> None:
    directory = root / "leaderboard" if scenario_id == "monday-001" else root / "leaderboard" / scenario_id
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "leaderboard.json").write_text(json.dumps(payload), encoding="utf-8")


@pytest.fixture
def fake_repo(tmp_path):
    """Three scenarios, three models, one of which skipped a scenario."""
    _write(tmp_path, "monday-001", _leaderboard("monday-001", {
        "alpha": [90.0, 90.0, 90.0],
        "beta": [60.0, 70.0, 80.0],
        "gamma": [50.0, 50.0, 50.0],
    }))
    _write(tmp_path, "monday-002", _leaderboard("monday-002", {
        "alpha": [80.0, 80.0, 80.0],
        "beta": [70.0, 70.0, 70.0],
    }))
    _write(tmp_path, "monday-003", _leaderboard("monday-003", {
        "alpha": [70.0, 70.0, 70.0],
        "beta": [80.0, 80.0, 80.0],
        "gamma": [40.0, 40.0, 40.0],
    }))
    return tmp_path


def _release(version, ids, status="released"):
    return OverallRelease(
        version=version,
        scenarios=tuple(ScenarioPin(id=i) for i in ids),
        status=status,
    )


# --------------------------------------------------------------------------
# The definition
# --------------------------------------------------------------------------


def test_monday_score_is_the_arithmetic_mean_of_scenario_scores(fake_repo):
    _, ranked, _ = build_overall(_release(1, PUBLISHED), root=fake_repo)
    alpha = next(m for m in ranked if m.model_slug == "alpha")
    assert alpha.scenario_scores == {"monday-001": 90.0, "monday-002": 80.0, "monday-003": 70.0}
    assert alpha.monday_score == 80.0


def test_every_scenario_weighs_the_same(fake_repo):
    """No weighting. Swapping which scenario a model was good at changes nothing."""
    _, ranked, _ = build_overall(_release(1, PUBLISHED), root=fake_repo)
    alpha = next(m for m in ranked if m.model_slug == "alpha")
    beta = next(m for m in ranked if m.model_slug == "beta")
    # alpha 90/80/70, beta 70/70/80 -> means 80.0 and 73.33
    assert alpha.monday_score == 80.0
    assert beta.monday_score == round((70 + 70 + 80) / 3, 2)
    # Reversing alpha's scenario order must not move its score.
    reordered = ModelOverall(
        model_slug="alpha", display_name="ALPHA",
        scenario_scores={"monday-003": 70.0, "monday-002": 80.0, "monday-001": 90.0},
    )
    assert reordered.monday_score == alpha.monday_score


def test_a_model_missing_a_scenario_is_not_ranked(fake_repo):
    """The rule that stops "skip the hard one" from being a winning strategy."""
    _, ranked, incomplete = build_overall(_release(1, PUBLISHED), root=fake_repo)
    assert [m.model_slug for m in ranked] == ["alpha", "beta"]
    assert [m.model_slug for m in incomplete] == ["gamma"]
    entry = incomplete[0]
    assert entry.missing == ["monday-002"]
    assert not entry.complete
    # gamma's mean over the two it did run would be 45.0. It must not appear.
    payload, _, _ = build_overall(_release(1, PUBLISHED), root=fake_repo)
    assert all(m["model_slug"] != "gamma" for m in payload["models"])
    assert "monday_score" not in payload["incomplete_models"][0]


def test_incomplete_models_name_what_they_are_missing(fake_repo):
    payload, _, _ = build_overall(_release(1, PUBLISHED), root=fake_repo)
    gamma = payload["incomplete_models"][0]
    assert gamma["missing_scenarios"] == ["monday-002"]
    assert gamma["scenario_scores"]["monday-002"] is None
    assert gamma["scenario_scores"]["monday-001"] == 50.0


# --------------------------------------------------------------------------
# Version immutability
# --------------------------------------------------------------------------


def test_adding_a_scenario_does_not_move_an_older_version(fake_repo):
    """The property the whole release mechanism exists for."""
    before, ranked_before, _ = build_overall(_release(1, PUBLISHED), root=fake_repo)

    _write(fake_repo, "monday-004", _leaderboard("monday-004", {
        "alpha": [10.0, 10.0, 10.0],
        "beta": [99.0, 99.0, 99.0],
    }))
    after, ranked_after, _ = build_overall(_release(1, PUBLISHED), root=fake_repo)
    assert [(m.model_slug, m.monday_score) for m in ranked_before] == [
        (m.model_slug, m.monday_score) for m in ranked_after
    ]
    assert before["models"] == after["models"]

    # v2 includes it, and reaches a different - and differently ordered - answer.
    _, ranked_v2, _ = build_overall(_release(2, (*PUBLISHED, "monday-004")), root=fake_repo)
    assert [m.model_slug for m in ranked_v2] == ["beta", "alpha"]
    assert next(m for m in ranked_v2 if m.model_slug == "alpha").monday_score == 62.5


def test_a_release_declares_exactly_which_scenarios_it_includes(fake_repo):
    payload, _, _ = build_overall(_release(1, PUBLISHED), root=fake_repo)
    assert payload["scenarios"] == list(PUBLISHED)
    assert payload["aggregation"] == AGGREGATION_ARITHMETIC_MEAN
    assert set(payload["scenario_provenance"]) == set(PUBLISHED)


def test_a_scenario_cannot_be_included_twice(fake_repo):
    """Duplication would silently double that scenario's weight."""
    doubled = _release(1, ("monday-001", "monday-002", "monday-001"))
    assert any("twice" in b for b in validate_release(doubled))
    with pytest.raises(OverallError, match="twice"):
        build_overall(doubled, root=fake_repo)


# --------------------------------------------------------------------------
# What must be rejected
# --------------------------------------------------------------------------


def test_a_non_official_leaderboard_is_rejected(fake_repo):
    _write(fake_repo, "monday-002", _leaderboard(
        "monday-002", {"alpha": [80.0]}, official=False))
    with pytest.raises(OverallError, match="not marked official"):
        build_overall(_release(1, PUBLISHED), root=fake_repo)


def test_a_calibration_leaderboard_is_rejected(fake_repo):
    """Calibration results are tuned against the runs they rank."""
    _write(fake_repo, "monday-002", _leaderboard(
        "monday-002", {"alpha": [80.0]}, official=True, status="calibration"))
    with pytest.raises(OverallError, match="calibration"):
        build_overall(_release(1, PUBLISHED), root=fake_repo)


def test_a_missing_scenario_leaderboard_is_rejected(fake_repo):
    with pytest.raises(OverallError, match="no published leaderboard"):
        build_overall(_release(1, (*PUBLISHED, "monday-009")), root=fake_repo)


def test_a_prompt_hash_mismatch_is_rejected(fake_repo):
    """A re-frozen scenario is a different measurement, not the same one."""
    release = OverallRelease(
        version=1,
        scenarios=(ScenarioPin(id="monday-001", prompt_sha256="b" * 64),),
        status="released",
    )
    with pytest.raises(OverallError, match="prompt hash"):
        build_overall(release, root=fake_repo)


def test_a_rubric_version_mismatch_is_rejected(fake_repo):
    release = OverallRelease(
        version=1,
        scenarios=(ScenarioPin(id="monday-001", rubric_version="9.9"),),
        status="released",
    )
    with pytest.raises(OverallError, match="rubric version"):
        build_overall(release, root=fake_repo)


def test_an_integrity_warning_is_rejected(fake_repo):
    payload = _leaderboard("monday-002", {"alpha": [80.0], "beta": [70.0]})
    payload["integrity_warning"] = "scores do not match their evaluations"
    _write(fake_repo, "monday-002", payload)
    with pytest.raises(OverallError, match="integrity warning"):
        build_overall(_release(1, PUBLISHED), root=fake_repo)


def test_a_score_that_does_not_recompute_is_rejected(fake_repo):
    """The published mean must be the mean of the published run scores."""
    payload = _leaderboard("monday-002", {"alpha": [80.0, 80.0, 80.0], "beta": [70.0]})
    payload["models"][0]["score"]["mean"] = 95.0
    _write(fake_repo, "monday-002", payload)
    with pytest.raises(OverallError, match="does not recompute"):
        build_overall(_release(1, PUBLISHED), root=fake_repo)


def test_recompute_check_tolerates_rounding_but_not_drift():
    row = {"model_slug": "x", "run_scores": [90.0, 91.0, 92.5], "score": {"mean": 91.17, "runs": 3}}
    assert check_score_recomputes("s", row) == []
    row["score"]["mean"] = 91.5
    assert check_score_recomputes("s", row)


def test_a_draft_release_cannot_be_released_or_written(fake_repo):
    draft = _release(1, PUBLISHED, status="draft")
    with pytest.raises(OverallError, match="status=draft"):
        build_overall(draft, root=fake_repo, require_released=True)
    # ...but is buildable as a preview, and refuses the official path on write.
    payload, ranked, incomplete = build_overall(draft, root=fake_repo, require_released=False)
    with pytest.raises(OverallError, match="cannot be written"):
        write_overall(payload, ranked, incomplete, draft, root=fake_repo, preview=False)
    json_path, _, md_path = write_overall(
        payload, ranked, incomplete, draft, root=fake_repo, preview=True
    )
    assert "analysis" in json_path.parts and "preview" in json_path.stem
    assert "PREVIEW — NOT AN OFFICIAL RESULT" in md_path.read_text(encoding="utf-8")


def test_every_blocker_is_reported_not_just_the_first(fake_repo):
    _write(fake_repo, "monday-002", _leaderboard("monday-002", {"alpha": [80.0]}, official=False))
    with pytest.raises(OverallError) as exc:
        build_overall(_release(1, (*PUBLISHED, "monday-009")), root=fake_repo)
    assert len(exc.value.blockers) >= 2


# --------------------------------------------------------------------------
# Cross-scenario variance vs run stability: two different things
# --------------------------------------------------------------------------


def test_cross_scenario_variance_is_not_run_stability(fake_repo):
    """A model can be rock-steady within scenarios and wildly uneven across them.

    beta scores 70/70/80 across scenarios but its monday-001 runs were 60/70/80.
    The two numbers must not be confused, and neither may touch the score.
    """
    _, ranked, _ = build_overall(_release(1, PUBLISHED), root=fake_repo)
    beta = next(m for m in ranked if m.model_slug == "beta")
    # Across scenarios: 70, 70, 80.
    assert beta.scenario_min == 70.0 and beta.scenario_max == 80.0
    assert beta.scenario_range == 10.0
    assert beta.scenario_stddev == round(statistics.stdev([70.0, 70.0, 80.0]), 2)
    # Within scenarios: monday-001's runs spread 20 points, the others zero.
    assert beta.run_ranges["monday-001"] == 20.0
    assert beta.max_run_range == 20.0
    assert beta.mean_run_range == round(20.0 / 3, 2)
    # The two are different numbers for this model.
    assert beta.max_run_range != beta.scenario_range


def test_run_stability_is_serialized_under_its_own_name(fake_repo):
    payload, _, _ = build_overall(_release(1, PUBLISHED), root=fake_repo)
    row = next(m for m in payload["models"] if m["model_slug"] == "beta")
    assert set(row["across_scenarios"]) == {"mean", "min", "max", "range", "stddev"}
    assert set(row["run_stability"]) == {
        "mean_run_range", "max_run_range", "mean_run_stddev", "per_scenario_run_range"
    }
    # And nothing from either block leaks into the score.
    assert row["monday_score"] == row["across_scenarios"]["mean"]


def test_no_observability_metric_reaches_the_monday_score(fake_repo):
    """Latency, tokens and cost must not be able to move the number.

    Asserted structurally: the score is computed from `scenario_scores` alone,
    so a leaderboard carrying wild performance figures scores identically.
    """
    base, ranked_base, _ = build_overall(_release(1, PUBLISHED), root=fake_repo)
    payload = _leaderboard("monday-002", {"alpha": [80.0, 80.0, 80.0], "beta": [70.0, 70.0, 70.0]})
    for row in payload["models"]:
        row["performance"] = {"median_ttfa_ms": 999_999.0, "median_total_latency_ms": 999_999.0}
        row["economics"] = {"median_cost_usd": 42.0}
    _write(fake_repo, "monday-002", payload)
    after, ranked_after, _ = build_overall(_release(1, PUBLISHED), root=fake_repo)
    assert [(m.model_slug, m.monday_score) for m in ranked_base] == [
        (m.model_slug, m.monday_score) for m in ranked_after
    ]


# --------------------------------------------------------------------------
# Determinism
# --------------------------------------------------------------------------


def test_rank_order_is_deterministic_and_ties_share_a_rank(fake_repo):
    _write(fake_repo, "monday-001", _leaderboard("monday-001", {"a": [80.0], "b": [80.0], "c": [90.0]}))
    _write(fake_repo, "monday-002", _leaderboard("monday-002", {"a": [80.0], "b": [80.0], "c": [90.0]}))
    _write(fake_repo, "monday-003", _leaderboard("monday-003", {"a": [80.0], "b": [80.0], "c": [90.0]}))
    first, ranked, _ = build_overall(_release(1, PUBLISHED), root=fake_repo)
    assert [(m.model_slug, m.rank) for m in ranked] == [("c", 1), ("a", 2), ("b", 2)]
    second, _, _ = build_overall(_release(1, PUBLISHED), root=fake_repo)
    assert first["models"] == second["models"]


# --------------------------------------------------------------------------
# The repository's own release file
# --------------------------------------------------------------------------


def test_the_declared_releases_are_internally_valid():
    for version, release in load_releases().items():
        assert validate_release(release) == [], version
        assert release.aggregation == AGGREGATION_ARITHMETIC_MEAN


def test_overall_v0_covers_exactly_the_published_scenarios():
    release = load_releases()[0]
    assert release.status == "released"
    assert release.scenario_ids == list(PUBLISHED)
    for pin in release.scenarios:
        assert pin.prompt_sha256 and pin.rubric_version, pin.id


def test_overall_v1_is_released_and_names_monday_004():
    """v1 was released on 2026-08-31, once monday-004's battery was published."""
    release = load_releases()[1]
    assert release.status == "released"
    assert release.scenario_ids == ["monday-001", "monday-002", "monday-003", "monday-004"]
    for pin in release.scenarios:
        assert pin.prompt_sha256 and pin.rubric_version, pin.id

    _, ranked, _ = build_overall(release, require_released=True)
    assert ranked, "a released v1 must build"
    assert all(m.complete for m in ranked)


def test_overall_v1_carries_the_serving_caveat_it_is_required_to_carry():
    """models.yaml says the release note has to carry this, so it is tested.

    qwen3.6's monday-004 runs came from NaN under a per-scenario endpoint
    override, and NaN serves that model as a reasoning model where Helmcode does
    not. A v1 average that hides this is the failure mode; the note is where it
    is prevented.
    """
    note = load_releases()[1].note or ""
    assert "qwen3.6" in note.lower()
    assert "nan" in note.lower()
    for term in ("reasoning", "override", "latency"):
        assert term in note.lower(), term


def test_a_draft_release_refuses_to_build_however_published_its_scenarios_are():
    """Draft is a decision, not a state derived from the scenarios.

    Every scenario v1 names is published and official, so nothing about their
    state could justify refusing. A draft copy of it must still refuse, and
    must refuse for the right reason - otherwise `status` is decorative and the
    "second, separate act" the file describes is not actually enforced.
    """
    draft = replace(load_releases()[1], status="draft")

    with pytest.raises(OverallError) as exc:
        build_overall(draft, require_released=True)

    assert any("status=draft" in b for b in exc.value.blockers)
    # It must not refuse for a reason that is no longer true of these scenarios.
    assert not any("not published yet" in b for b in exc.value.blockers)


def test_the_published_overall_v0_matches_the_live_scenario_results():
    """The published file must recompute from the scenario leaderboards it cites."""
    published = json.loads(
        (REPO_ROOT / "leaderboard" / "overall" / "overall-v0.json").read_text(encoding="utf-8")
    )
    _, ranked, _ = build_overall(load_releases()[0])
    assert [m["model_slug"] for m in published["models"]] == [m.model_slug for m in ranked]
    for row, entry in zip(published["models"], ranked):
        assert row["monday_score"] == entry.monday_score
        assert row["monday_score"] == round(
            statistics.fmean(row["scenario_scores"].values()), 2
        )


@pytest.mark.parametrize("scenario_id", PUBLISHED)
def test_the_frozen_scenarios_are_untouched_by_any_of_this(scenario_id):
    """Overall is a read-only consumer. It must never write into a scenario."""
    from mondaybench.freeze import check_drift, load_manifest

    directory = REPO_ROOT / "scenarios" / scenario_id
    manifest = load_manifest(directory)
    assert manifest is not None
    drift = check_drift(manifest, directory)
    assert drift.clean, (scenario_id, drift.changed, drift.missing)


def test_overall_writes_only_under_its_own_directories(tmp_path, fake_repo):
    """No path in the writer may reach a scenario or a per-scenario leaderboard.

    Asserted behaviourally rather than by reading the source: the module does
    mention "scenarios", but only as a YAML key in the release file.
    """
    payload, ranked, incomplete = build_overall(_release(1, PUBLISHED), root=fake_repo)
    before = {p for p in fake_repo.rglob("*") if p.is_file()}
    write_overall(payload, ranked, incomplete, _release(1, PUBLISHED), root=fake_repo)
    created = {p for p in fake_repo.rglob("*") if p.is_file()} - before
    assert created
    for path in created:
        assert path.parent == fake_repo / "leaderboard" / "overall", path


def test_the_release_file_is_the_only_place_scenarios_are_listed():
    """No hardcoded scenario list in the builder - releases are data, not code."""
    import inspect

    from mondaybench import overall as module

    source = inspect.getsource(module)
    for scenario_id in (*PUBLISHED, "monday-004"):
        assert scenario_id not in source, scenario_id


def test_release_file_pins_match_what_each_scenario_actually_published():
    """A pin that has silently drifted would make the guard useless."""
    raw = yaml.safe_load((REPO_ROOT / "overall-releases.yaml").read_text(encoding="utf-8"))
    for release in raw["releases"]:
        for pin in release["scenarios"]:
            if pin["id"] == "monday-004":
                continue  # not published yet; pinned from its freeze manifest
            directory = (
                REPO_ROOT / "leaderboard"
                if pin["id"] == "monday-001"
                else REPO_ROOT / "leaderboard" / pin["id"]
            )
            payload = json.loads((directory / "leaderboard.json").read_text(encoding="utf-8"))
            assert payload["frozen_prompt_sha256"] == pin["prompt_sha256"], pin["id"]
            assert payload["rubric_version"] == pin["rubric_version"], pin["id"]


def test_monday_004_pin_matches_its_freeze_manifest():
    """v1 pins monday-004 from the freeze, so publication cannot change the target."""
    manifest = yaml.safe_load(
        (REPO_ROOT / "scenarios" / "monday-004" / "FROZEN.yaml").read_text(encoding="utf-8")
    )
    raw = yaml.safe_load((REPO_ROOT / "overall-releases.yaml").read_text(encoding="utf-8"))
    pin = next(
        p for r in raw["releases"] if r["overall_version"] == 1
        for p in r["scenarios"] if p["id"] == "monday-004"
    )
    assert pin["prompt_sha256"] == manifest["prompt_sha256"]
    assert pin["rubric_version"] == manifest["rubric_version"]
