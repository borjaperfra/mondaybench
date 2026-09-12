"""The newest released suite must still verify against this tree.

`verify-release` has always been able to catch a deleted artefact. Nothing ran
it on a schedule, so the v1.5 manifest spent a day pinning 30 evaluation files
that were not on disk and the tree looked healthy the whole time: every board
built, every score was reproducible, and the only thing wrong was a claim nobody
re-checked.

This closes that gap. It is deliberately scoped to the NEWEST release, because
that is the one a reader is told to verify and the only one a repair can still
reach - an older manifest is frozen, and the honest answer for a defect in one
is a new version, not an edit.

Two historical releases are known not to verify and are named below rather than
skipped silently. Both list evaluations for `deepseek-v4.1-flash-probe` at the
unversioned path they were written to before being re-stamped; the files were
removed after the cut, and `Evaluation.timestamp_utc` means a regenerated file
cannot match a recorded hash. The battery is on no board, so no published number
depends on them.
"""
from __future__ import annotations

import json

import pytest

from mondaybench.config import repo_root
from mondaybench.suite import GROUP_POLICY, SuiteError, load_suite_index

# Releases that cannot be made to verify, with the reason. Every entry here is a
# permanent record of a defect, not a waiver: nothing may be added without the
# same kind of explanation, and the newest release may never appear.
KNOWN_BROKEN = {
    "1.3": "15 deepseek-v4.1-flash-probe evaluations removed after the cut",
    "1.4": "same 15, carried forward",
    "1.5": "the same 15, plus 15 pre-re-stamp paths for deepseek-v4.1-flash-rerun-v1",
}


def released_versions() -> list[str]:
    directory = repo_root() / "releases"
    versions = [p.name[1:] for p in directory.iterdir() if p.is_dir() and p.name.startswith("v")]
    return sorted(versions, key=lambda v: tuple(int(part) for part in v.split(".")))


def latest_version() -> str:
    return released_versions()[-1]


def test_the_newest_release_is_not_on_the_known_broken_list():
    """A repair is a new version, so the newest one can never be excused."""
    latest = latest_version()
    assert latest not in KNOWN_BROKEN, (
        f"suite v{latest} is the newest release and is listed as known-broken. "
        f"A manifest defect is repaired by cutting the next version, never by "
        f"adding the current one here."
    )


def test_every_file_the_newest_manifest_pins_exists():
    latest = latest_version()
    index = load_suite_index(latest)

    missing: list[str] = []
    for group, files in index.items():
        if GROUP_POLICY.get(group) == "mutable":
            continue
        for relative in files:
            if not (repo_root() / relative).exists():
                missing.append(f"{group}: {relative}")

    assert not missing, (
        f"suite v{latest} pins {len(missing)} file(s) that are not on disk, under a "
        f"policy that forbids removal: {missing[:10]}"
    )


@pytest.mark.parametrize("version", sorted(KNOWN_BROKEN))
def test_a_known_broken_release_is_still_broken_for_the_stated_reason(version: str):
    """If one of these starts verifying, the record above is wrong and must go.

    A stale exception is worse than no exception: it teaches a reader that a
    check is expected to fail when it no longer is.
    """
    try:
        index = load_suite_index(version)
    except SuiteError:
        pytest.skip(f"suite v{version} has no file index")
    missing = [
        relative
        for group, files in index.items()
        if GROUP_POLICY.get(group) != "mutable"
        for relative in files
        if not (repo_root() / relative).exists()
    ]
    assert missing, (
        f"suite v{version} now verifies; remove it from KNOWN_BROKEN - "
        f"the recorded reason was: {KNOWN_BROKEN[version]}"
    )


def test_the_newest_release_covers_every_evaluation_on_disk():
    """A cut taken mid-re-stamp is the other half of the v1.5 defect.

    The manifest listing a file that does not exist and the tree holding an
    evaluation the manifest never saw are the same mistake seen from opposite
    sides, and only one of them makes `verify-release` fail.
    """
    latest = latest_version()
    pinned = set(load_suite_index(latest)["evaluations"])

    on_disk = {
        path.relative_to(repo_root()).as_posix()
        for path in (repo_root() / "evaluations").rglob("*")
        if path.is_file()
    }
    unpinned = sorted(on_disk - pinned)
    assert not unpinned, (
        f"{len(unpinned)} evaluation file(s) exist but are in no released manifest, so "
        f"nothing verifies them: {unpinned[:10]}"
    )


def test_every_recorded_evaluation_sits_under_the_tree_its_suite_version_names():
    """An evaluation stamped `suite_version: 1.5` under `evaluations/v1.4/` is
    findable by neither the version it claims nor the one it is filed under."""
    offenders: list[str] = []
    for path in (repo_root() / "evaluations").rglob("run-*.json"):
        relative = path.relative_to(repo_root()).as_posix()
        segment = relative.split("/")[1]
        filed_under = segment[1:] if segment.startswith("v") and segment[1:2].isdigit() else None
        claimed = json.loads(path.read_text(encoding="utf-8")).get("suite_version")
        if filed_under != claimed:
            offenders.append(f"{relative}: filed under {filed_under}, claims {claimed}")
    assert not offenders, (
        f"{len(offenders)} evaluation(s) are filed under a suite version they do not "
        f"claim: {offenders[:10]}"
    )
