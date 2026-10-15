"""Benchmarking a new model against the frozen suite.

The guarantee under test is narrow and load-bearing: an eighth model can get a
Monday Score without a single incumbent number moving. That holds because no
term in a model's score depends on any other model - and this file is what turns
that from an argument into a check.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from mondaybench.challenge import (
    ChallengeError,
    draft_revision_block,
    incumbents,
    leaderboard_path,
    next_overall_revision,
    official_evaluator,
    status_for,
    suite_scenarios,
)
from mondaybench.overall import OverallError, OverallRelease, build_overall, load_releases

REPO_ROOT = Path(__file__).resolve().parent.parent
SCENARIOS = ["monday-001", "monday-002", "monday-003", "monday-004", "monday-005"]
INCUMBENTS = [
    "deepseek-v4-flash",
    "gemma4",
    "glm5.2",
    "glm5.3-flash",
    "mimo-v2.5",
    "qwen3.6",
    "qwen3.8-flash",
]


# ------------------------------------------------------------------ status


def test_the_suite_being_challenged_is_the_released_one():
    assert suite_scenarios("1.0") == SCENARIOS


def test_every_incumbent_reads_as_complete_and_eligible():
    for slug in INCUMBENTS:
        status = status_for(slug)
        assert status.eligible_for_overall, slug
        assert status.runs_needed == 0, slug
        assert status.judgements_remaining == 0, slug
        assert [s.stage for s in status.scenarios] == ["published"] * 5, slug


def test_an_unknown_model_needs_the_whole_battery_and_says_why():
    status = status_for("no-such-model-xyz")
    assert not status.eligible_for_overall
    assert status.runs_needed == 15
    assert status.judgements_remaining == 15
    # 19 + 20 + 21 + 27 + 31 criteria, three runs each.
    assert status.criteria_to_judge == 354
    assert any("models.yaml" in note for note in status.notes)


def test_the_campaign_estimate_counts_runs_that_do_not_exist_yet():
    """`judgements_needed` is what is actionable today; a plan needs the total.
    A fresh model has nothing on disk, so a disk-only count reads zero and the
    judging session looks free."""
    status = status_for("no-such-model-xyz")
    assert status.judgements_needed == 0
    assert status.judgements_remaining == 15


def test_incumbents_are_exactly_the_seven_published_models():
    assert incumbents(suite_version="1.0") == INCUMBENTS


def test_a_per_scenario_endpoint_override_is_honoured_when_qualifying():
    """qwen3.6's three official monday-004 runs came from NaN because Helmcode
    was unreachable, recorded as a scenario-scoped override in models.yaml.

    Qualifying against the unscoped registry rejects all three on
    "provider 'nan' != configured 'helmcode'" and reports a published incumbent
    as incomplete. The override is exactly the mechanism that stops an endpoint
    move from retroactively disqualifying frozen batteries, so a planner that
    ignores it is worse than no planner.
    """
    from mondaybench.config import endpoint_overrides_for

    assert endpoint_overrides_for("monday-004").get("qwen3.6") == "nan"
    assert endpoint_overrides_for("monday-001") == {}

    monday_004 = next(
        s for s in status_for("qwen3.6").scenarios if s.scenario_id == "monday-004"
    )
    assert monday_004.official == 3
    assert monday_004.stage == "published"


def test_the_override_does_not_leak_into_other_scenarios():
    """It is scoped for a reason: qwen3.6 has Helmcode-served official runs in
    monday-001, 002 and 003."""
    status = status_for("qwen3.6")
    for entry in status.scenarios:
        assert entry.official == 3, entry.scenario_id


# ------------------------------------------------------------------ evaluator


@pytest.mark.parametrize("scenario_id", SCENARIOS)
def test_the_official_evaluator_comes_from_the_published_board(scenario_id):
    board = json.loads(leaderboard_path(scenario_id).read_text(encoding="utf-8"))
    assert official_evaluator(scenario_id) == board["evaluator"]


def test_monday_001_resolves_without_relying_on_a_fallback_constant():
    """`evaluator-opus5-v0.1` declares no `scenario_id`, so `resolve_evaluator`
    finds nothing for monday-001 and the CLI falls through to a hardcoded
    constant. Reading the board instead needs no fallback."""
    from mondaybench.config import resolve_evaluator

    assert resolve_evaluator("monday-001", None, "") == ""
    assert official_evaluator("monday-001") == "evaluator-opus5-v0.1"


# ------------------------------------------------------------------ revisions


def test_the_next_revision_extends_the_latest_release():
    version, revision = next_overall_revision()
    # The invariant is that it extends the LATEST base release with the next
    # unused revision - not that the latest happens to be v2. Pinning the
    # number made this fail the moment a legitimate v3 was released.
    from mondaybench.overall import load_releases

    releases = load_releases()
    latest = max(k for k in releases if isinstance(k, int))
    used = {
        releases[k].revision
        for k in releases
        if getattr(releases[k], "version", None) == latest
    }
    assert version == latest
    assert revision == max(used) + 1


def test_a_revision_slug_names_the_artifact():
    base = load_releases()[2]
    assert base.slug == "2"
    revised = OverallRelease(
        version=base.version, revision=1, scenarios=base.scenarios,
        aggregation=base.aggregation, status=base.status,
    )
    assert revised.slug == "2.1"
    assert revised.key == (2, 1)


def test_base_releases_are_still_keyed_by_integer():
    """Existing callers index `load_releases()[2]`. A revision must not break
    that, and must not shadow the release it extends.

    The invariant is the KEY TYPE and the absence of shadowing, not how many
    releases exist. Pinning `{0, 1, 2}` made this fail the moment a fourth was
    released, which is a thing releases are supposed to be able to do.
    """
    releases = load_releases()
    # A BASE release is keyed by its integer; a REVISION is keyed by "V.R" and
    # must not take the key of the release it extends. Asserting that every key
    # is an integer said something stronger and different - that no revision
    # exists - which is a state releases are supposed to be able to leave.
    for key, release in releases.items():
        if release.revision:
            assert key == f"{release.version}.{release.revision}", key
            assert release.version in releases, (
                f"revision {key} shadows or replaces base v{release.version}"
            )
        else:
            assert isinstance(key, int), key
            assert release.version == key
    assert {0, 1, 2} <= {k for k in releases if isinstance(k, int)}


def test_a_revision_must_keep_the_scenario_set_of_what_it_extends(tmp_path):
    """A decimal point must not smuggle in a different claim."""
    source = yaml.safe_load((REPO_ROOT / "overall-releases.yaml").read_text(encoding="utf-8"))
    v2 = next(r for r in source["releases"] if r["overall_version"] == 2)
    bogus = dict(v2)
    bogus["revision"] = 1
    bogus["scenarios"] = v2["scenarios"][:3]
    path = tmp_path / "overall-releases.yaml"
    path.write_text(yaml.safe_dump({"releases": source["releases"] + [bogus]}), encoding="utf-8")

    with pytest.raises(OverallError) as exc:
        load_releases(path=path)
    assert "revision adds MODELS" in " ".join(exc.value.blockers)


def test_a_revision_of_a_release_that_does_not_exist_is_refused(tmp_path):
    source = yaml.safe_load((REPO_ROOT / "overall-releases.yaml").read_text(encoding="utf-8"))
    orphan = dict(next(r for r in source["releases"] if r["overall_version"] == 2))
    orphan["overall_version"] = 9
    orphan["revision"] = 1
    path = tmp_path / "overall-releases.yaml"
    path.write_text(yaml.safe_dump({"releases": source["releases"] + [orphan]}), encoding="utf-8")

    with pytest.raises(OverallError) as exc:
        load_releases(path=path)
    assert "not declared" in " ".join(exc.value.blockers)


def test_the_generated_revision_block_pins_the_same_scenarios_as_the_base():
    """Generated rather than hand-written: five prompt hashes retyped by hand is
    how a release ends up unreproducible."""
    block = yaml.safe_load(draft_revision_block("kimi-k3"))[0]
    releases = load_releases()
    # The block extends the LATEST base release. Deriving it keeps this test
    # about the pinning behaviour rather than about which release is newest.
    base = releases[max(k for k in releases if isinstance(k, int))]
    assert block["overall_version"] == base.version
    # The next unused revision of that base, not literally 1: once a revision
    # is published the generator has to offer the one after it.
    taken = {r.revision for r in releases.values() if r.version == base.version}
    assert block["revision"] == max(taken) + 1
    assert block["status"] == "draft"
    assert block["aggregation"] == base.aggregation
    assert [s["id"] for s in block["scenarios"]] == base.scenario_ids
    for pin, declared in zip(base.scenarios, block["scenarios"]):
        assert declared["prompt_sha256"] == pin.prompt_sha256
        assert str(declared["rubric_version"]) == str(pin.rubric_version)
    assert "kimi-k3" in block["note"]


def test_a_generated_revision_block_actually_loads(tmp_path):
    source = yaml.safe_load((REPO_ROOT / "overall-releases.yaml").read_text(encoding="utf-8"))
    block = yaml.safe_load(draft_revision_block("kimi-k3"))[0]
    path = tmp_path / "overall-releases.yaml"
    path.write_text(yaml.safe_dump({"releases": source["releases"] + [block]}), encoding="utf-8")

    releases = load_releases(path=path)
    # The block extends whatever the latest base release is, so derive the slug
    # rather than pinning "2.1".
    base = max(k for k in releases if isinstance(k, int))
    slug = f"{base}.1"
    assert slug in releases
    assert releases[slug].revision == 1
    assert releases[slug].scenario_ids == releases[base].scenario_ids


# ------------------------------------------------------- incumbents unmoved


def test_a_new_model_cannot_move_an_incumbent_score():
    """The structural argument, made concrete.

    Each incumbent's Monday Score is recomputed from the published per-scenario
    boards alone. If a challenger's presence could alter one, this arithmetic
    would stop reproducing - so pinning it here is what makes 'no incumbent is
    rerun' a checkable claim rather than an intention.
    """
    import statistics

    boards = {
        s: {
            m["model_slug"]: m["score"]["mean"]
            for m in json.loads(leaderboard_path(s).read_text(encoding="utf-8"))["models"]
        }
        for s in SCENARIOS
    }
    published = json.loads(
        (REPO_ROOT / "leaderboard" / "overall" / "overall-v2.json").read_text(encoding="utf-8")
    )
    for model in published["models"]:
        slug = model["model_slug"]
        assert model["monday_score"] == pytest.approx(
            statistics.mean(boards[s][slug] for s in SCENARIOS), abs=0.005
        ), slug


def test_overall_v2_still_builds_and_ranks_only_complete_models():
    _, ranked, incomplete = build_overall(load_releases()[2], require_released=True)
    assert [m.model_slug for m in ranked] and all(m.complete for m in ranked)
    assert incomplete == []


def test_the_runbook_exists_and_names_the_four_verification_gates():
    text = (REPO_ROOT / "docs" / "benchmarking-a-new-model.md").read_text(encoding="utf-8")
    for phrase in (
        "verify-release --version 1.7",
        "check_sample_provenance",
        "overall-v3.5.json",
        "challenge --model",
        "354",
    ):
        assert phrase in text, phrase


def test_the_runbook_rubric_table_matches_the_evaluators():
    """A runbook that names the wrong rubric is worse than none."""
    text = (REPO_ROOT / "docs" / "benchmarking-a-new-model.md").read_text(encoding="utf-8")
    for scenario_id in SCENARIOS:
        evaluator = official_evaluator(scenario_id)
        config = yaml.safe_load(
            (REPO_ROOT / "evaluators" / f"{evaluator}.yaml").read_text(encoding="utf-8")
        )
        row = next(line for line in text.splitlines() if line.startswith(f"| {scenario_id} "))
        assert f"`{evaluator}`" in row, scenario_id
        assert f"`{config['rubric_file']}`" in row, scenario_id


def test_an_unknown_suite_version_is_refused():
    with pytest.raises(ChallengeError):
        status_for("gemma4", suite_version="99.9")
