"""Content freezing for a published scenario.

A published scenario is immutable. Saying so in a README is not a mechanism, so
this module records the SHA-256 of every canonical file in a `FROZEN.yaml`
manifest and lets `validate` fail when any of them drifts.

The prompt hash already protects the *assembled* prompt. This protects the parts
that never reach the prompt but still decide a score: `ground-truth.yaml`, the
rubric, and `scenario.yaml` itself.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

import yaml

from .config import ConfigError, load_yaml

MANIFEST_NAME = "FROZEN.yaml"


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass(frozen=True)
class FreezeManifest:
    scenario_id: str
    benchmark_version: str
    prompt_sha256: str
    rubric_file: str
    rubric_version: str
    files: dict[str, str]

    @property
    def path_count(self) -> int:
        return len(self.files)


@dataclass(frozen=True)
class DriftReport:
    changed: list[tuple[str, str, str]]  # (name, expected, actual)
    missing: list[str]
    unlisted: list[str]

    @property
    def clean(self) -> bool:
        return not (self.changed or self.missing)


def build_manifest(
    *,
    scenario_id: str,
    benchmark_version: str,
    prompt_sha256: str,
    rubric_file: str,
    rubric_version: str,
    directory: Path,
    names: list[str],
) -> FreezeManifest:
    files = {}
    for name in sorted(names):
        path = directory / name
        if not path.exists():
            raise ConfigError(f"cannot freeze missing file: {path}")
        files[name] = file_sha256(path)
    return FreezeManifest(
        scenario_id=scenario_id,
        benchmark_version=benchmark_version,
        prompt_sha256=prompt_sha256,
        rubric_file=rubric_file,
        rubric_version=rubric_version,
        files=files,
    )


def write_manifest(manifest: FreezeManifest, directory: Path) -> Path:
    payload = {
        "scenario_id": manifest.scenario_id,
        "benchmark_version": manifest.benchmark_version,
        "frozen": True,
        "prompt_sha256": manifest.prompt_sha256,
        "rubric_file": manifest.rubric_file,
        "rubric_version": manifest.rubric_version,
        "files": manifest.files,
    }
    header = (
        "# Canonical content of this scenario, frozen for publication.\n"
        "#\n"
        "# Every hash below is checked by `mondaybench validate`. If a file changes,\n"
        "# validation fails - which is the point: a published scenario is immutable,\n"
        "# and scores are only comparable against the bytes recorded here.\n"
        "#\n"
        "# To change scenario content after publication, create a new scenario id.\n"
        "# Do not edit this manifest to make a change pass.\n"
        "#\n"
        "# `prompt_sha256` covers the assembled prompt; the per-file hashes also cover\n"
        "# ground-truth.yaml and the rubric, which never reach the prompt but do decide\n"
        "# the score.\n"
    )
    target = directory / MANIFEST_NAME
    target.write_text(
        header + yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8", newline="\n"
    )
    return target


def load_manifest(directory: Path) -> FreezeManifest | None:
    path = directory / MANIFEST_NAME
    if not path.exists():
        return None
    data = load_yaml(path) or {}
    return FreezeManifest(
        scenario_id=str(data.get("scenario_id", "")),
        benchmark_version=str(data.get("benchmark_version", "")),
        prompt_sha256=str(data.get("prompt_sha256", "")),
        rubric_file=str(data.get("rubric_file", "rubric.yaml")),
        rubric_version=str(data.get("rubric_version", "")),
        files={str(k): str(v) for k, v in (data.get("files") or {}).items()},
    )


def check_drift(manifest: FreezeManifest, directory: Path) -> DriftReport:
    changed: list[tuple[str, str, str]] = []
    missing: list[str] = []
    for name, expected in manifest.files.items():
        path = directory / name
        if not path.exists():
            missing.append(name)
            continue
        actual = file_sha256(path)
        if actual != expected:
            changed.append((name, expected, actual))

    # Files present in the scenario directory that the manifest does not cover.
    # Reported, not failed: a README or CHANGELOG alongside canonical content is
    # fine, and freezing them would block documenting the freeze itself.
    ignore = {MANIFEST_NAME, "CHANGELOG.md", "README.md"}
    unlisted = sorted(
        p.name
        for p in directory.iterdir()
        if p.is_file() and p.name not in manifest.files and p.name not in ignore
    )
    return DriftReport(changed=changed, missing=missing, unlisted=unlisted)
