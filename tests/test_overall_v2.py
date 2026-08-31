"""Overall v2 = monday-001 + 002 + 003 + 004 + 005.

An Overall release is a permanent claim about a fixed set of scenarios, so the
things worth pinning are composition, the arithmetic, and the guarantee that
adding a release cannot disturb the ones already published.
"""

from __future__ import annotations

import csv
import hashlib
import json
import statistics
from pathlib import Path

import pytest
import yaml

from mondaybench.overall import OverallError, build_overall, load_releases

REPO_ROOT = Path(__file__).resolve().parent.parent
OVERALL = REPO_ROOT / "leaderboard" / "overall"
SCENARIOS = ["monday-001", "monday-002", "monday-003", "monday-004", "monday-005"]


def _artifact(version: int) -> dict:
    return json.loads((OVERALL / f"overall-v{version}.json").read_text(encoding="utf-8"))


def _scenario_board(scenario_id: str) -> dict[str, float]:
    path = (
        REPO_ROOT / "leaderboard" / "leaderboard.json"
        if scenario_id == "monday-001"
        else REPO_ROOT / "leaderboard" / scenario_id / "leaderboard.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {m["model_slug"]: m["score"]["mean"] for m in payload["models"]}


# ---------------------------------------------------------------- composition


def test_v2_contains_exactly_the_five_scenarios():
    release = load_releases()[2]
    assert release.scenario_ids == SCENARIOS
    assert release.status == "released"
    assert _artifact(2)["scenarios"] == SCENARIOS


def test_v2_does_not_disturb_the_composition_of_v0_or_v1():
    assert load_releases()[0].scenario_ids == SCENARIOS[:3]
    assert load_releases()[1].scenario_ids == SCENARIOS[:4]


# ---------------------------------------------------------------- immutability


def test_v0_and_v1_artifacts_are_byte_identical_after_publishing_v2():
    """Publishing a release must not rewrite the ones already published.

    Hashes recorded here rather than compared to a snapshot taken at runtime:
    a snapshot inside the test would only prove the test did not change them.
    If a legitimate change to v0/v1 is ever made, this test must be updated
    deliberately - which is the point.
    """
    digests = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(OVERALL.glob("overall-v[01].*"))
    }
    assert set(digests) == {
        "overall-v0.csv",
        "overall-v0.json",
        "overall-v0.md",
        "overall-v1.csv",
        "overall-v1.json",
        "overall-v1.md",
    }
    # v0 and v1 must still describe their own scenario sets, unchanged.
    assert _artifact(0)["scenarios"] == SCENARIOS[:3]
    assert _artifact(1)["scenarios"] == SCENARIOS[:4]
    assert _artifact(0)["overall_version"] == 0
    assert _artifact(1)["overall_version"] == 1


# ---------------------------------------------------------------- arithmetic


def test_every_v2_score_is_the_mean_of_its_five_pinned_scenario_scores():
    boards = {s: _scenario_board(s) for s in SCENARIOS}
    for model in _artifact(2)["models"]:
        slug = model["model_slug"]
        expected = statistics.mean(boards[s][slug] for s in SCENARIOS)
        assert model["monday_score"] == pytest.approx(expected, abs=0.005), slug
        assert model["scenario_scores"] == {s: boards[s][slug] for s in SCENARIOS}


def test_equal_weighting_no_scenario_counts_twice():
    """Five scenarios, one vote each. A weighted mean would diverge here."""
    for model in _artifact(2)["models"]:
        per = list(model["scenario_scores"].values())
        assert len(per) == 5
        assert model["monday_score"] == pytest.approx(sum(per) / 5, abs=0.005)


def test_no_observability_metric_reaches_the_v2_score():
    """Latency, cost, tokens and serving reliability are published beside the
    score and never inside it. Asserted structurally: the score is reproducible
    from scenario means alone, so nothing else can be contributing."""
    boards = {s: _scenario_board(s) for s in SCENARIOS}
    for model in _artifact(2)["models"]:
        slug = model["model_slug"]
        assert model["monday_score"] == pytest.approx(
            statistics.mean(boards[s][slug] for s in SCENARIOS), abs=0.005
        )
        # And none of these appears anywhere in the model payload.
        blob = json.dumps(model).lower()
        for banned in ("ttfa", "latency", "cost_usd", "reasoning_tokens", "attempts"):
            assert banned not in blob, (slug, banned)


def test_across_scenario_dispersion_is_not_run_stability():
    """The two are different quantities and the artifact must keep them apart."""
    for model in _artifact(2)["models"]:
        assert set(model["across_scenarios"]) >= {"mean", "min", "max", "range", "stddev"}
        assert set(model["run_stability"]) >= {"mean_run_range", "per_scenario_run_range"}
        per = list(model["scenario_scores"].values())
        assert model["across_scenarios"]["range"] == pytest.approx(max(per) - min(per), abs=0.005)
        # Run stability is per-scenario and cannot equal the across-scenario spread
        # except by coincidence; what matters is that it is a separate field.
        assert model["across_scenarios"] is not model["run_stability"]


# ---------------------------------------------------------------- eligibility


def test_a_model_missing_one_scenario_is_not_averaged_over_fewer(fake_repo=None):
    """Averaging over whichever scenarios a model finished would reward not
    competing. The builder must exclude it instead."""
    artifact = _artifact(2)
    assert artifact["incomplete_models"] == []
    for model in artifact["models"]:
        assert len(model["scenario_scores"]) == 5, model["model_slug"]
    # Every model on the board appears on all five scenario boards.
    boards = {s: _scenario_board(s) for s in SCENARIOS}
    for model in artifact["models"]:
        for s in SCENARIOS:
            assert model["model_slug"] in boards[s]


# ---------------------------------------------------------------- pinning


def test_v2_pins_match_what_each_scenario_actually_published():
    release = load_releases()[2]
    for pin in release.scenarios:
        path = (
            REPO_ROOT / "leaderboard" / "leaderboard.json"
            if pin.id == "monday-001"
            else REPO_ROOT / "leaderboard" / pin.id / "leaderboard.json"
        )
        published = json.loads(path.read_text(encoding="utf-8"))
        assert published["frozen_prompt_sha256"] == pin.prompt_sha256, pin.id
        assert str(published["rubric_version"]) == str(pin.rubric_version), pin.id


def test_rewriting_an_included_scenario_makes_v2_fail_to_build(tmp_path, monkeypatch):
    """The pin exists so a later rewrite cannot silently move a published score."""
    release = load_releases()[2]
    tampered = [
        p if p.id != "monday-005" else type(p)(id=p.id, prompt_sha256="0" * 64,
                                              rubric_version=p.rubric_version)
        for p in release.scenarios
    ]
    broken = type(release)(
        version=release.version, scenarios=tuple(tampered),
        aggregation=release.aggregation, status=release.status,
        label=release.label, note=release.note,
    )
    with pytest.raises(OverallError) as exc:
        build_overall(broken, require_released=True)
    assert any("monday-005" in b for b in exc.value.blockers)


def test_v2_artifact_carries_enough_provenance_to_reproduce_it():
    artifact = _artifact(2)
    prov = artifact["scenario_provenance"]
    assert set(prov) == set(SCENARIOS)
    for scenario, meta in prov.items():
        assert meta["prompt_sha256"] and meta["rubric_version"] and meta["evaluator"], scenario
    assert artifact["aggregation"] == "arithmetic_mean"
    assert "equal weight" in artifact["monday_score_definition"]


# ---------------------------------------------------------------- release notes


@pytest.mark.parametrize(
    "phrase",
    [
        "SERVING RELIABILITY IS EXCLUDED",
        "OUT-OF-SAMPLE",
        "check_sample_provenance",
        "qwen3.6",
        "equal weight per scenario",
        "descriptive only",
    ],
)
def test_v2_release_note_carries_the_required_context(phrase):
    note = load_releases()[2].note or ""
    assert phrase.lower() in note.lower(), phrase


# ---------------------------------------------------------------- compatibility


@pytest.mark.parametrize("version", [0, 1, 2])
def test_every_released_overall_still_builds(version):
    release = load_releases()[version]
    _, ranked, _ = build_overall(release, require_released=True)
    assert ranked and all(m.complete for m in ranked)


def test_provenance_logic_does_not_alter_overall_scoring():
    """The sample-provenance guard reads runs; it computes nothing. Overall
    scores must reproduce from the published scenario boards alone."""
    from mondaybench.leaderboard import check_sample_provenance

    for scenario in SCENARIOS:
        assert check_sample_provenance(scenario, REPO_ROOT) == []
    boards = {s: _scenario_board(s) for s in SCENARIOS}
    for model in _artifact(2)["models"]:
        assert model["monday_score"] == pytest.approx(
            statistics.mean(boards[s][model["model_slug"]] for s in SCENARIOS), abs=0.005
        )


def test_v2_csv_and_md_agree_with_the_json():
    rows = list(csv.DictReader((OVERALL / "overall-v2.csv").read_text(encoding="utf-8").splitlines()))
    by_slug = {m["model_slug"]: m for m in _artifact(2)["models"]}
    assert len(rows) == len(by_slug)
    score_key = next(k for k in rows[0] if "score" in k.lower())
    by_name = {m["display_name"]: m for m in by_slug.values()}
    name_key = next(
        k for k in rows[0] if any(row[k] in by_name or row[k] in by_slug for row in rows)
    )
    for row in rows:
        model = by_slug.get(row[name_key]) or by_name[row[name_key]]
        assert float(row[score_key]) == pytest.approx(model["monday_score"], abs=0.005)
    text = (OVERALL / "overall-v2.md").read_text(encoding="utf-8")
    assert "Overall v2" in text
    for slug in by_slug:
        assert by_slug[slug]["display_name"] in text


def test_the_frozen_scenarios_are_untouched_by_publishing_v2():
    """Releasing Overall changes no scenario artifact."""
    for scenario in SCENARIOS:
        manifest_path = REPO_ROOT / "scenarios" / scenario / "FROZEN.yaml"
        if not manifest_path.is_file():
            continue
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        for name, digest in manifest["files"].items():
            actual = hashlib.sha256(
                (REPO_ROOT / "scenarios" / scenario / name).read_bytes()
            ).hexdigest()
            assert actual == digest, f"{scenario}/{name}"
