"""What a suite release does and does not claim.

These encode the intended SEMANTIC boundary, not the current implementation: a
release pins everything an official score cannot be reproduced without, and
nothing else. Analytical and experimental work that no score depends on is
tracked so drift stays visible, but changing it is not a release failure.

Every test mutates a temporary copy of the tree. Nothing under the real
runs/, verdicts/, evaluations/, scenarios/ or releases/ is written.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from mondaybench.config import repo_root
from mondaybench.suite import (
    GROUP_EXCLUDES,
    GROUP_POLICY,
    GROUPS,
    collect_group,
    load_suite_index,
    load_suite_manifest,
    verify_suite,
)

REPO_ROOT = repo_root()
VERSION = "1.1"


def _group_of(relative_path: str) -> str | None:
    """Which release group claims this path, if any."""
    for name, patterns in GROUPS.items():
        files = collect_group(patterns, REPO_ROOT, GROUP_EXCLUDES.get(name, ()))
        if relative_path in files:
            return name
    return None


def _verifies(version: str = VERSION) -> bool:
    return all(report.ok for report in verify_suite(version).values())


# ---------------------------------------------------------------------------
# The boundary itself, asserted as policy rather than as a file list
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "group",
    ["scenarios", "evaluators", "taxonomy", "runs", "verdicts", "evaluations",
     "leaderboards", "analysis"],
)
def test_score_bearing_groups_are_protected(group):
    """Everything a published score is reproduced from is frozen or append-only."""
    assert GROUP_POLICY[group] in {"immutable", "append_only"}, group


@pytest.mark.parametrize("group", ["pricing", "docs"])
def test_non_score_bearing_groups_do_not_gate_a_release(group):
    """Pricing research and audit prose change without invalidating a score.

    Monday Score is quality only. The cost layer reads the same frozen runs and
    multiplies their token counts by a published price, so a vendor moving a
    rate changes no score - and must not break the quality release.
    """
    assert GROUP_POLICY[group] == "mutable", group


def test_pricing_is_its_own_group_not_part_of_analysis():
    """The architecture the separation exists to create: suite release +
    independently versioned pricing snapshot."""
    analysis = collect_group(GROUPS["analysis"], REPO_ROOT, GROUP_EXCLUDES.get("analysis", ()))
    pricing = collect_group(GROUPS["pricing"], REPO_ROOT, GROUP_EXCLUDES.get("pricing", ()))
    assert not any(p.startswith("analysis/cost-value/") for p in analysis)
    assert pricing, "the pricing group matched nothing"
    assert all(p.startswith("analysis/cost-value/") for p in pricing)
    # exactly one group may claim a file, or the digest depends on ordering
    assert not (set(analysis) & set(pricing))


def test_a_pricing_snapshot_carries_its_own_integrity_anchor():
    """Prices are pinned by their own hash, not by the suite digest."""
    snapshots = sorted((REPO_ROOT / "analysis" / "cost-value").glob("pricing-snapshot-*.yaml"))
    assert snapshots, "no pricing snapshot found"
    for snapshot in snapshots:
        companion = snapshot.with_suffix(".sha256")
        assert companion.is_file(), f"{snapshot.name} has no .sha256 beside it"


# ---------------------------------------------------------------------------
# A + B - editing non-score-bearing work must not break the release
# ---------------------------------------------------------------------------


def test_A_editing_an_experimental_audit_does_not_break_v1_1():
    candidates = sorted((REPO_ROOT / "audits" / "monday-opus5").rglob("*"))
    target = next((p for p in candidates if p.is_file()), None)
    if target is None:
        pytest.skip("no experimental Opus audit present in this tree")
    relative = target.relative_to(REPO_ROOT).as_posix()
    group = _group_of(relative)
    assert group == "docs", f"{relative} is in {group}, expected the mutable docs group"
    assert GROUP_POLICY[group] == "mutable"


def test_B_updating_cost_publication_data_does_not_break_v1_1():
    target = REPO_ROOT / "analysis" / "cost-value" / "publication-data.json"
    if not target.is_file():
        pytest.skip("cost publication data not present in this tree")
    relative = target.relative_to(REPO_ROOT).as_posix()
    group = _group_of(relative)
    assert group == "pricing", f"{relative} is in {group}, expected the pricing group"
    assert GROUP_POLICY[group] == "mutable"
    # and it is genuinely not in the frozen part of the release
    index = load_suite_index(VERSION)
    assert relative not in index.get("analysis", {})


def test_B_the_suite_digest_does_not_move_when_a_price_moves(tmp_path):
    """The architectural claim, checked rather than asserted.

    A price change alters the pricing group's digest and nothing else, so the
    quality release's own groups are untouched.
    """
    index = load_suite_index(VERSION)
    frozen_groups = [n for n, p in GROUP_POLICY.items() if p != "mutable"]
    before = {name: index[name] for name in frozen_groups if name in index}
    # A price edit cannot appear in any frozen group, by construction: no frozen
    # group claims a path under analysis/cost-value/.
    for name, files in before.items():
        assert not any(p.startswith("analysis/cost-value/") for p in files), name


# ---------------------------------------------------------------------------
# C + D + E - editing score-bearing content MUST break the release
# ---------------------------------------------------------------------------


def _copy_tree(tmp_path: Path) -> Path:
    """A minimal copy: the release manifest plus the groups under test."""
    root = tmp_path / "repo"
    root.mkdir()
    shutil.copytree(REPO_ROOT / "releases", root / "releases")
    for name in ("scenarios", "evaluators", "taxonomy", "evaluations", "analysis",
                 "runs", "verdicts", "leaderboard", "taxonomy"):
        source = REPO_ROOT / name
        if source.is_dir():
            shutil.copytree(source, root / name, dirs_exist_ok=True)
    return root


def _drift_ok(root: Path, group: str) -> bool:
    index = load_suite_index(VERSION, root)
    actual = collect_group(GROUPS[group], root, GROUP_EXCLUDES.get(group, ()))
    recorded = index[group]
    changed = [p for p, sha in recorded.items() if p in actual and actual[p] != sha]
    missing = [p for p in recorded if p not in actual]
    policy = GROUP_POLICY[group]
    if policy == "immutable":
        added = [p for p in actual if p not in recorded]
        return not (changed or missing or added)
    if policy == "append_only":
        return not (changed or missing)
    return True


def test_C_changing_a_frozen_scenario_breaks_v1_1(tmp_path):
    root = _copy_tree(tmp_path)
    target = root / "scenarios" / "monday-001" / "prompt.md"
    assert _drift_ok(root, "scenarios"), "the copy should verify before the edit"
    target.write_text(target.read_text(encoding="utf-8") + "\nAn extra line.\n",
                      encoding="utf-8", newline="\n")
    assert not _drift_ok(root, "scenarios")


def test_D_changing_a_frozen_rubric_breaks_v1_1(tmp_path):
    root = _copy_tree(tmp_path)
    target = root / "scenarios" / "monday-001" / "rubric-0.2.yaml"
    assert _drift_ok(root, "scenarios")
    target.write_text(target.read_text(encoding="utf-8").replace(
        "pass: 8", "pass: 9", 1), encoding="utf-8", newline="\n")
    assert not _drift_ok(root, "scenarios")


def test_D_changing_an_evaluator_judge_prompt_breaks_v1_1(tmp_path):
    """The judge contract is part of the release, and v1.1 hashes it for real."""
    root = _copy_tree(tmp_path)
    target = root / "evaluators" / "monday-003" / "judge-prompt.md"
    assert _drift_ok(root, "evaluators")
    target.write_text(target.read_text(encoding="utf-8") + "\nExtra instruction.\n",
                      encoding="utf-8", newline="\n")
    assert not _drift_ok(root, "evaluators")


def test_E_changing_a_v1_1_official_evaluation_breaks_v1_1(tmp_path):
    root = _copy_tree(tmp_path)
    target = (root / "evaluations" / "v1.1" / "evaluator-opus5-v0.1" / "monday-001"
              / "glm5.3" / "run-001.json")
    assert target.is_file(), "the v1.1 evaluation should be in the copied tree"
    assert _drift_ok(root, "evaluations")
    payload = json.loads(target.read_text(encoding="utf-8"))
    payload["final_score"] = 0.0
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    assert not _drift_ok(root, "evaluations")


def test_E_deleting_an_official_run_breaks_v1_1(tmp_path):
    root = _copy_tree(tmp_path)
    target = root / "runs" / "monday-001" / "glm5.3" / "run-001.json"
    assert _drift_ok(root, "runs")
    target.unlink()
    assert not _drift_ok(root, "runs")


# ---------------------------------------------------------------------------
# F - v1.0 is not disturbed by any of this
# ---------------------------------------------------------------------------


def test_F_v1_0_still_verifies_and_keeps_its_digest():
    manifest = load_suite_manifest("1.0")
    assert manifest["suite_digest"] == (
        "c056b4b43d3caeb3b50394282b08ed281a5716fb1df68d1666abb950aa0b2a80"
    )
    assert _verifies("1.0")


def test_F_a_release_makes_no_claim_about_a_group_it_never_declared():
    """v1.0 predates the pricing group and must not acquire an opinion about it."""
    index_10 = load_suite_index("1.0")
    assert "pricing" not in index_10
    assert "pricing" not in verify_suite("1.0")
    # ...while v1.1 does declare it
    assert "pricing" in load_suite_index(VERSION)


def test_both_releases_verify_side_by_side():
    assert _verifies("1.0")
    assert _verifies("1.1")
