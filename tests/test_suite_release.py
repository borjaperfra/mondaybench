"""The v1.0 suite release: manifest integrity, group policy, and the guarantee
that a new model can be benchmarked without disturbing the frozen suite.

A release manifest that only says "nothing changed" is useless the moment real
work resumes, and one that says nothing is worse. The property worth pinning is
the distinction: scenarios and evaluators may not move at all, evidence may only
grow, and the difference is enforced rather than documented.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import pytest
import yaml

from mondaybench.suite import (
    EXCLUDED_PARTS,
    FORBIDDEN_NAMES,
    GROUP_POLICY,
    GROUPS,
    SuiteError,
    build_suite_manifest,
    collect_group,
    group_digest,
    load_suite_index,
    load_suite_manifest,
    verify_suite,
    write_suite_manifest,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
VERSION = "1.0"
SCENARIOS = ["monday-001", "monday-002", "monday-003", "monday-004", "monday-005"]


DIRS = (
    "scenarios", "evaluators", "runs", "verdicts", "evaluations", "leaderboard",
    "taxonomy", "analysis", "docs", "audits", "mondaybench", "tools", "tests",
)
FILES = (
    "models.yaml", "overall-releases.yaml", "pyproject.toml", "uv.lock",
    ".env.example", "LICENSE",
)


def clone_repo(tmp_path: Path) -> Path:
    """A throwaway copy of the tree, so freeze/verify can be exercised for real
    without any chance of writing to the repository under test."""
    root = tmp_path / "repo"
    root.mkdir()
    for name in DIRS:
        source = REPO_ROOT / name
        if source.is_dir():
            shutil.copytree(
                source, root / name, ignore=shutil.ignore_patterns("__pycache__", "*.pyc")
            )
    for name in FILES:
        if (REPO_ROOT / name).is_file():
            shutil.copy2(REPO_ROOT / name, root / name)
    for path in REPO_ROOT.glob("*.md"):
        shutil.copy2(path, root / path.name)
    return root


@pytest.fixture(scope="module")
def manifest():
    loaded = load_suite_manifest(VERSION)
    assert loaded is not None, "suite v1.0 has not been frozen"
    return loaded


@pytest.fixture(scope="module")
def index():
    return load_suite_index(VERSION)


# ------------------------------------------------------------------ contents


def test_the_release_covers_all_five_scenarios_with_their_frozen_pins(manifest):
    assert [s["id"] for s in manifest["scenarios"]] == SCENARIOS
    for entry in manifest["scenarios"]:
        frozen = yaml.safe_load(
            (REPO_ROOT / "scenarios" / entry["id"] / "FROZEN.yaml").read_text(encoding="utf-8")
        )
        assert entry["prompt_sha256"] == frozen["prompt_sha256"], entry["id"]
        assert entry["rubric_file"] == frozen["rubric_file"], entry["id"]
        assert str(entry["rubric_version"]) == str(frozen["rubric_version"]), entry["id"]


def test_the_release_records_every_overall_release(manifest):
    versions = [r["version"] for r in manifest["overall_releases"]]
    assert versions == [0, 1, 2]
    for entry in manifest["overall_releases"]:
        assert entry["status"] == "released"
        assert entry["artifact_sha256"], entry["version"]


def test_every_group_is_populated_and_has_a_policy(manifest):
    assert set(manifest["groups"]) == set(GROUPS)
    for name, group in manifest["groups"].items():
        assert group["file_count"] > 0, name
        assert group["policy"] == GROUP_POLICY[name], name
        assert len(group["content_digest"]) == 64


def test_the_evidence_groups_carry_the_expected_volume(manifest):
    """A release that quietly dropped half the evaluations would still be
    internally consistent. The counts are the check on that."""
    groups = manifest["groups"]
    assert groups["scenarios"]["file_count"] == 75
    assert groups["runs"]["file_count"] == 133
    assert groups["verdicts"]["file_count"] == 26
    assert groups["evaluations"]["file_count"] == 212
    assert manifest["file_count"] == sum(g["file_count"] for g in groups.values())


def test_monday_001_verdicts_are_covered(index):
    """They live at `verdicts/*.jsonl`, not under a scenario directory, and a
    `verdicts/monday-*/` pattern silently missed all seven."""
    verdicts = index["verdicts"]
    for slug in (
        "deepseek-v4-flash",
        "gemma4",
        "glm5.2",
        "glm5.3-flash",
        "mimo-v2.5",
        "qwen3.6",
        "qwen3.8-flash",
    ):
        assert f"verdicts/{slug}.verdicts.jsonl" in verdicts, slug


# ------------------------------------------------------------------ secrets


def test_no_credentials_file_is_ever_hashed(index):
    """A manifest is published. A hash of `.env` confirms its exact contents to
    anyone who can guess them, so the file is excluded by name regardless of
    what a pattern matches."""
    assert ".env" in FORBIDDEN_NAMES
    for group, files in index.items():
        for path in files:
            assert Path(path).name != ".env", (group, path)
            assert not path.endswith("/.env"), (group, path)


def test_archive_is_excluded_deliberately(index):
    """Superseded calibration evidence is kept for re-examination and is not
    part of what the suite claims."""
    assert "archive" in EXCLUDED_PARTS
    for group, files in index.items():
        for path in files:
            assert not path.startswith("archive/"), (group, path)


# ------------------------------------------------------------------ digests


def test_the_manifest_digests_match_the_working_tree(manifest, index):
    for name, patterns in GROUPS.items():
        actual = collect_group(patterns, REPO_ROOT)
        assert actual == index[name], name
        assert group_digest(actual) == manifest["groups"][name]["content_digest"], name


def test_the_suite_digest_is_a_function_of_the_group_digests(manifest):
    expected = hashlib.sha256()
    for name in sorted(manifest["groups"]):
        expected.update(name.encode("utf-8"))
        expected.update(b"\0")
        expected.update(manifest["groups"][name]["content_digest"].encode("ascii"))
        expected.update(b"\n")
    assert manifest["suite_digest"] == expected.hexdigest()


def test_a_group_digest_is_order_independent_but_path_sensitive():
    files = {"a/x.json": "0" * 64, "b/y.json": "1" * 64}
    assert group_digest(files) == group_digest(dict(reversed(list(files.items()))))
    renamed = {"a/z.json": "0" * 64, "b/y.json": "1" * 64}
    assert group_digest(renamed) != group_digest(files), "a rename must be drift"


def test_the_working_tree_verifies_strictly():
    drift = verify_suite(VERSION)
    dirty = {name: r.summary() for name, r in drift.items() if not r.identical}
    assert not dirty, dirty


# ------------------------------------------------------------------ policy


def test_immutable_groups_are_the_ones_that_decide_a_score():
    assert GROUP_POLICY["scenarios"] == "immutable"
    assert GROUP_POLICY["evaluators"] == "immutable"
    assert GROUP_POLICY["taxonomy"] == "immutable"


def test_evidence_groups_are_append_only_not_immutable():
    """A new model must be able to add runs. It must not be able to alter one."""
    for group in ("runs", "verdicts", "evaluations", "leaderboards", "analysis"):
        assert GROUP_POLICY[group] == "append_only", group


def test_a_new_run_is_permitted_but_a_rewritten_one_is_not(tmp_path):
    """The exact property the release exists to enforce, exercised end to end
    against a throwaway copy of the tree rather than the real one."""
    root = clone_repo(tmp_path)
    built, idx = build_suite_manifest("test", root=root, status="released")
    write_suite_manifest(built, idx, root=root)
    assert all(r.identical for r in verify_suite("test", root).values())

    # Adding a challenger's run: permitted by policy, and visible as drift.
    new_run = root / "runs" / "monday-001" / "challenger-x"
    new_run.mkdir(parents=True)
    (new_run / "run-001.json").write_text('{"response": "hi"}', encoding="utf-8")
    drift = verify_suite("test", root)
    assert drift["runs"].added == ["runs/monday-001/challenger-x/run-001.json"]
    assert not drift["runs"].identical
    assert drift["runs"].ok, "adding a run must be allowed"

    # Rewriting an incumbent's run: refused.
    incumbent = next((root / "runs" / "monday-001" / "gemma4").glob("run-*.json"))
    incumbent.write_text('{"response": "tampered"}', encoding="utf-8")
    drift = verify_suite("test", root)
    assert not drift["runs"].ok, "rewriting an incumbent run must fail"
    assert any(incumbent.name in path for path, _, _ in drift["runs"].changed)

    # And touching a rubric fails whatever the policy of anything else says.
    (root / "scenarios" / "monday-003" / "rubric.yaml").write_text("broken", encoding="utf-8")
    drift = verify_suite("test", root)
    assert not drift["scenarios"].ok
    assert drift["scenarios"].missing == []


def test_a_deleted_evidence_file_is_a_failure_not_an_omission(tmp_path):
    root = clone_repo(tmp_path)
    built, idx = build_suite_manifest("test", root=root)
    write_suite_manifest(built, idx, root=root)

    (root / "verdicts" / "gemma4.verdicts.jsonl").unlink()
    drift = verify_suite("test", root)
    assert drift["verdicts"].missing == ["verdicts/gemma4.verdicts.jsonl"]
    assert not drift["verdicts"].ok


# ------------------------------------------------------------------ guards


def test_a_scenario_that_is_not_frozen_cannot_be_released(tmp_path):
    root = clone_repo(tmp_path)
    (root / "scenarios" / "monday-004" / "FROZEN.yaml").unlink()
    with pytest.raises(SuiteError) as exc:
        build_suite_manifest("test", root=root)
    assert "monday-004" in str(exc.value)


def test_an_empty_group_is_refused(tmp_path):
    """A pattern that stops matching is how a release silently loses a whole
    category of evidence."""
    with pytest.raises(SuiteError) as exc:
        build_suite_manifest("test", root=tmp_path)
    assert "matched no files" in str(exc.value)


def test_the_release_directory_does_not_hash_itself(index):
    for group, files in index.items():
        for path in files:
            assert not path.startswith("releases/"), (group, path)
