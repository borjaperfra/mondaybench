"""Suite-level release manifests.

A scenario freeze (`freeze.py`) protects one scenario's content. This protects a
whole published *suite*: the scenarios, the evaluators that scored them, the
evidence those scores were computed from, the boards, and the analysis released
alongside. `mondaybench verify-release` fails when any of it drifts.

WHY TWO FILES. `SUITE-FROZEN.yaml` is the release definition and is meant to be
read: five scenarios with their prompt hashes, the evaluator bound to each, the
Overall releases included, and one `content_digest` per group. `<version>.files.json`
is the per-file index behind those digests - a few hundred entries, machine
territory. The digest is what a human checks; the index is what says which file
moved.

WHAT A GROUP DIGEST IS. sha256 over `"<relative path>\\0<file sha256>\\n"` for
every file in the group, sorted by path. Sorted, so it does not depend on
filesystem order; path-inclusive, so a rename is drift; NUL-separated, so no
path can forge an entry boundary.

WHAT IS DELIBERATELY NOT COVERED. `archive/` holds superseded evidence -
calibration batteries, pre-audit boards - which is kept precisely so it can be
re-examined, and is not part of what the suite claims. Excluding it is a
statement, not an oversight: nothing under `archive/` contributed to a published
score.

CODE IS PINNED, SEPARATELY AND FOR A DIFFERENT REASON. The `harness` group
covers `mondaybench/**/*.py`. A change there does not invalidate a recorded
score - the verdicts are recorded, not recomputed - but it does invalidate the
claim that this tree reproduces them. The two are different claims and the
manifest keeps them apart.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Iterable

import yaml

from .config import repo_root

MANIFEST_NAME = "SUITE-FROZEN.yaml"
RELEASES_DIR = "releases"


class SuiteError(Exception):
    """Raised when a suite release cannot be built or does not verify."""


# The groups a release covers, each a list of glob patterns relative to the repo
# root. Order is presentation order in the manifest.
GROUPS: dict[str, tuple[str, ...]] = {
    # What the models were asked, and the answer keys and rubrics that scored it.
    "scenarios": ("scenarios/**/*",),
    # How they were judged: evaluator configs and judge prompts.
    "evaluators": ("evaluators/**/*",),
    # The evidence. Raw generations, plus the failed-attempt logs and the
    # INVALIDATED / REJECTED / SERVING-INCIDENT notes that record what was
    # thrown away and why - which is as much a part of the integrity record as
    # what was kept.
    "runs": ("runs/**/*",),
    # Recorded judge output. Deliberately a whole-directory glob: monday-001's
    # verdicts sit at `verdicts/*.jsonl` rather than under a scenario folder,
    # and a `verdicts/monday-*/` pattern silently missed all seven of them.
    "verdicts": ("verdicts/**/*",),
    # Scored evaluations and their human-readable reviews.
    "evaluations": ("evaluations/**/*",),
    # What was published.
    "leaderboards": ("leaderboard/**/*",),
    # Registries that decide what a slug means and what a release contains,
    # plus the pinned dependency set. `.env` is NEVER included - see
    # FORBIDDEN_NAMES.
    "config": (
        "models.yaml",
        "overall-releases.yaml",
        "pyproject.toml",
        "uv.lock",
        ".env.example",
        "LICENSE",
    ),
    # Analysis released alongside, including the derivation scripts.
    "taxonomy": ("taxonomy/*.yaml",),
    "analysis": ("analysis/**/*",),
    # Pricing research, kept OUT of `analysis` on purpose - see GROUP_POLICY.
    "pricing": ("analysis/cost-value/**/*",),
    "docs": ("docs/**/*", "audits/**/*", "*.md"),
    # The code that produced all of the above.
    "harness": ("mondaybench/**/*.py", "tools/**/*.py"),
    # The tests are part of the release, not an accessory to it: every integrity
    # claim this manifest makes is enforced by one of them, and a release whose
    # tests can be quietly weakened is not frozen.
    "tests": ("tests/**/*.py", "tests/**/*.json"),
}

# Paths a group must NOT claim, even though its own patterns match them.
#
# A file belongs to exactly one group, because two groups claiming it would
# hash it twice and make the suite digest depend on an ordering nobody chose.
# `analysis/**/*` would otherwise swallow the pricing subtree, and those two
# things have opposite integrity requirements: a calibration record must never
# change, while a price is a fact about the world that vendors move.
GROUP_EXCLUDES: dict[str, tuple[str, ...]] = {
    "analysis": ("analysis/cost-value/",),
}


# What each group is allowed to do after the release is cut.
#
# This is the distinction that makes a suite release usable rather than merely
# strict. Benchmarking a NEW model against the frozen suite necessarily writes
# new runs, new verdicts, new evaluations and a new board - and must not alter a
# single byte of the scenarios, rubrics or evaluators, or of any existing
# model's evidence. A single "did anything change?" check cannot tell those two
# apart, so it would either forbid the legitimate case or wave through the
# illegitimate one.
#
#   immutable   nothing may change, and nothing may be added
#   append_only existing files are frozen; new files are expected
#   mutable     tracked so drift is visible, but change is not a failure
GROUP_POLICY: dict[str, str] = {
    "scenarios": "immutable",
    "evaluators": "immutable",
    "taxonomy": "immutable",
    "runs": "append_only",
    "verdicts": "append_only",
    "evaluations": "append_only",
    "leaderboards": "append_only",
    "analysis": "append_only",
    # MUTABLE, and this is the whole point of separating it.
    #
    # No official MondayBench score depends on a price. Monday Score is quality
    # only; the cost layer reads the same frozen runs and multiplies their token
    # counts by a published price. Pinning that research append_only made a
    # vendor changing a rate - or this repository re-sourcing one - break the
    # QUALITY release, which is a claim the release was never trying to make.
    #
    # Pricing has its own integrity anchor and does not need this one: each
    # snapshot is immutable, versioned by date, and carries its own sha256
    # beside it (`pricing-snapshot-<date>.yaml` + `.sha256`). That is the
    # architecture - suite release + pricing snapshot, pinned separately - and
    # it is why the suite digest must not move when a price does.
    #
    # Tracked rather than excluded: drift is still reported, it just is not a
    # failure, exactly as for `docs` and `harness`.
    "pricing": "mutable",
    # models.yaml gains a row when a model is onboarded; overall-releases.yaml
    # gains a revision. Both are registries, and a registry that cannot grow is
    # a registry that cannot describe a new model.
    "config": "mutable",
    "docs": "mutable",
    "harness": "mutable",
    "tests": "mutable",
}

EXCLUDED_PARTS = (
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "archive",
    ".venv",
    ".git",
    RELEASES_DIR,
)

# Never hashed, never listed, whatever a pattern says. A manifest is a published
# artifact; a credentials file has no business being fingerprinted in one, and
# the presence of a hash is itself a small leak (it confirms the file's exact
# contents to anyone who can guess them).
FORBIDDEN_NAMES = (".env",)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _excluded(relative: Path) -> bool:
    if relative.name in FORBIDDEN_NAMES:
        return True
    return any(part in EXCLUDED_PARTS for part in relative.parts)


def collect_group(
    patterns: Iterable[str], root: Path, excludes: Iterable[str] = ()
) -> dict[str, str]:
    """Hash every file matching any pattern, keyed by POSIX-relative path.

    `excludes` are path prefixes this group does not claim, so a broad pattern
    can hand a subtree to a group with a different policy without either group
    hashing it twice.
    """
    prefixes = tuple(excludes)
    found: dict[str, str] = {}
    for pattern in patterns:
        for path in root.glob(pattern):
            if not path.is_file():
                continue
            relative = path.relative_to(root)
            if _excluded(relative):
                continue
            posix = relative.as_posix()
            if any(posix.startswith(prefix) for prefix in prefixes):
                continue
            found[posix] = file_sha256(path)
    return dict(sorted(found.items()))


def group_digest(files: dict[str, str]) -> str:
    """Order-independent digest over a group's (path, hash) pairs."""
    digest = hashlib.sha256()
    for path, sha in sorted(files.items()):
        digest.update(path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(sha.encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


@dataclass(frozen=True)
class SuiteManifest:
    version: str
    released: str
    status: str
    scenarios: list[dict[str, Any]]
    overall_releases: list[dict[str, Any]]
    groups: dict[str, dict[str, Any]]
    notes: dict[str, Any] = field(default_factory=dict)

    @property
    def file_count(self) -> int:
        return sum(g["file_count"] for g in self.groups.values())

    @property
    def suite_digest(self) -> str:
        """One hash over every group digest. The whole release in 64 characters."""
        digest = hashlib.sha256()
        for name in sorted(self.groups):
            digest.update(name.encode("utf-8"))
            digest.update(b"\0")
            digest.update(self.groups[name]["content_digest"].encode("ascii"))
            digest.update(b"\n")
        return digest.hexdigest()


@dataclass(frozen=True)
class SuiteDrift:
    group: str
    policy: str
    changed: list[tuple[str, str, str]]
    missing: list[str]
    added: list[str]

    @property
    def identical(self) -> bool:
        """Byte-for-byte the tree that was released."""
        return not (self.changed or self.missing or self.added)

    @property
    def ok(self) -> bool:
        """Within what this group's policy permits."""
        if self.policy == "mutable":
            return True
        if self.policy == "append_only":
            # An added file is fine; a rewritten or vanished one is not.
            return not (self.changed or self.missing)
        return self.identical

    def summary(self) -> str:
        if self.identical:
            return "identical"
        parts = []
        if self.changed:
            parts.append(f"{len(self.changed)} changed")
        if self.missing:
            parts.append(f"{len(self.missing)} missing")
        if self.added:
            parts.append(f"{len(self.added)} added")
        return ", ".join(parts)


def release_dir(version: str, root: Path | None = None) -> Path:
    return (root or repo_root()) / RELEASES_DIR / f"v{version}"


def _scenario_entries(root: Path) -> list[dict[str, Any]]:
    from .freeze import load_manifest
    from .scenarios import list_scenario_ids, load_scenario

    entries: list[dict[str, Any]] = []
    for scenario_id in list_scenario_ids():
        directory = root / "scenarios" / scenario_id
        manifest = load_manifest(directory)
        if manifest is None:
            raise SuiteError(
                f"{scenario_id} has no FROZEN.yaml: an unfrozen scenario cannot be released"
            )
        loaded = load_scenario(scenario_id)
        if loaded.rubric_file != manifest.rubric_file:
            raise SuiteError(
                f"{scenario_id} resolves rubric {loaded.rubric_file!r} but is frozen "
                f"against {manifest.rubric_file!r}"
            )
        entries.append(
            {
                "id": scenario_id,
                "name": loaded.name,
                "prompt_sha256": manifest.prompt_sha256,
                "rubric_file": manifest.rubric_file,
                "rubric_version": manifest.rubric_version,
                "criteria": len(loaded.rubric.criteria),
                "official_runs": loaded.official_runs,
                "frozen_manifest_sha256": file_sha256(directory / "FROZEN.yaml"),
            }
        )
    return entries


def _overall_entries(root: Path) -> list[dict[str, Any]]:
    from .overall import load_releases

    entries: list[dict[str, Any]] = []
    for version, release in sorted(load_releases().items()):
        artifact = root / "leaderboard" / "overall" / f"overall-v{version}.json"
        entries.append(
            {
                "version": version,
                "status": release.status,
                "scenarios": list(release.scenario_ids),
                "aggregation": release.aggregation,
                "artifact_sha256": file_sha256(artifact) if artifact.is_file() else None,
            }
        )
    return entries


def build_suite_manifest(
    version: str,
    *,
    root: Path | None = None,
    status: str = "released",
    released: str | None = None,
    notes: dict[str, Any] | None = None,
) -> tuple[SuiteManifest, dict[str, dict[str, str]]]:
    """Build a manifest and the per-file index behind it."""
    root = root or repo_root()
    index: dict[str, dict[str, str]] = {}
    groups: dict[str, dict[str, Any]] = {}

    for name, patterns in GROUPS.items():
        files = collect_group(patterns, root, GROUP_EXCLUDES.get(name, ()))
        if not files:
            raise SuiteError(f"release group {name!r} matched no files - refusing to freeze it")
        index[name] = files
        groups[name] = {
            "file_count": len(files),
            "content_digest": group_digest(files),
            "policy": GROUP_POLICY.get(name, "immutable"),
            "patterns": list(patterns),
        }

    manifest = SuiteManifest(
        version=version,
        released=released or date.today().isoformat(),
        status=status,
        scenarios=_scenario_entries(root),
        overall_releases=_overall_entries(root),
        groups=groups,
        notes=notes or {},
    )
    return manifest, index


HEADER = """\
# MondayBench suite release manifest.
#
# Every hash here is checked by `mondaybench verify-release`. A published suite
# is immutable: if a file under one of these groups changes, is removed, or is
# added, verification fails. That is the point.
#
# `content_digest` is sha256 over "<path>\\0<file sha256>\\n" for every file in
# the group, sorted by path. The per-file hashes behind it are in the companion
# `.files.json`, which is what tells you WHICH file moved.
#
# `suite_digest` is one hash over every group digest: the whole release in 64
# characters.
#
# NOT COVERED: `archive/` (superseded evidence, kept for re-examination, and no
# part of it contributed to a published score) and the test suite.
#
# The `harness` group covers the code. A change there does not invalidate a
# recorded score - verdicts are recorded, not recomputed - but it does
# invalidate the claim that this tree reproduces them.
#
# To change a released suite, publish a new version. Do not edit this manifest
# to make a change pass.
"""


def write_suite_manifest(
    manifest: SuiteManifest, index: dict[str, dict[str, str]], *, root: Path | None = None
) -> tuple[Path, Path]:
    directory = release_dir(manifest.version, root)
    directory.mkdir(parents=True, exist_ok=True)

    payload = {
        "suite_version": manifest.version,
        "released": manifest.released,
        "status": manifest.status,
        "suite_digest": manifest.suite_digest,
        "file_count": manifest.file_count,
        "scenarios": manifest.scenarios,
        "overall_releases": manifest.overall_releases,
        "groups": manifest.groups,
    }
    if manifest.notes:
        payload["notes"] = manifest.notes

    manifest_path = directory / MANIFEST_NAME
    manifest_path.write_text(
        HEADER + yaml.safe_dump(payload, sort_keys=False, allow_unicode=True, width=100),
        encoding="utf-8",
    )

    index_path = directory / f"v{manifest.version}.files.json"
    index_path.write_text(
        json.dumps({"suite_version": manifest.version, "files": index}, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest_path, index_path


def load_suite_manifest(version: str, root: Path | None = None) -> dict[str, Any] | None:
    path = release_dir(version, root) / MANIFEST_NAME
    if not path.is_file():
        return None
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_suite_index(version: str, root: Path | None = None) -> dict[str, dict[str, str]]:
    path = release_dir(version, root) / f"v{version}.files.json"
    if not path.is_file():
        raise SuiteError(f"no file index for suite v{version} (looked in {path})")
    return json.loads(path.read_text(encoding="utf-8"))["files"]


def verify_suite(version: str, root: Path | None = None) -> dict[str, SuiteDrift]:
    """Compare the working tree against a published suite manifest."""
    root = root or repo_root()
    manifest = load_suite_manifest(version, root)
    if manifest is None:
        raise SuiteError(f"no manifest for suite v{version}")
    index = load_suite_index(version, root)

    drift: dict[str, SuiteDrift] = {}
    for name, patterns in GROUPS.items():
        if name not in index:
            # A release that did not declare this group makes no claim about it.
            # Groups are added over time - `pricing` was split out of `analysis`
            # after v1.0 - and an older manifest must not start failing, or even
            # reporting, because a later release drew a new boundary.
            continue
        recorded = index[name]
        actual = collect_group(patterns, root, GROUP_EXCLUDES.get(name, ()))
        changed = [
            (path, sha, actual[path])
            for path, sha in recorded.items()
            if path in actual and actual[path] != sha
        ]
        drift[name] = SuiteDrift(
            group=name,
            policy=GROUP_POLICY.get(name, "immutable"),
            changed=changed,
            missing=sorted(set(recorded) - set(actual)),
            added=sorted(set(actual) - set(recorded)),
        )
    return drift
