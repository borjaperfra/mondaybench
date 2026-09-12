"""Every file this harness writes must be LF, on any platform.

`tests/test_line_endings.py` catches CRLF that is already in the tree. It cannot
catch a writer that produces CRLF until something that writer produced has been
committed - which is how `write_suite_manifest` stayed wrong through six
releases on a Windows machine: the two files it writes were the last in the
harness not pinning `newline="\\n"`, and they are the files that state what the
release contains.

This checks the writers themselves, so the next one written on a Windows box
fails here rather than in a manifest somebody else verifies.
"""
from __future__ import annotations

import ast

import pytest

from mondaybench.config import repo_root

PACKAGE = repo_root() / "mondaybench"


def write_text_calls():
    """Every `<something>.write_text(...)` in the package, with its location."""
    for path in sorted(PACKAGE.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "write_text"
            ):
                yield path.relative_to(repo_root()).as_posix(), node


def test_every_write_text_in_the_harness_pins_lf():
    offenders = [
        f"{relative}:{node.lineno}"
        for relative, node in write_text_calls()
        if not any(
            keyword.arg == "newline"
            and isinstance(keyword.value, ast.Constant)
            and keyword.value.value == "\n"
            for keyword in node.keywords
        )
    ]
    assert not offenders, (
        f"{len(offenders)} write_text call(s) do not pin newline=\"\\n\" and will write "
        f"CRLF on Windows: {offenders}"
    )


def test_the_suite_manifest_writer_round_trips_as_lf(tmp_path):
    """The specific writer that was wrong, checked by what it puts on disk."""
    from mondaybench.suite import build_suite_manifest, write_suite_manifest

    manifest, index = build_suite_manifest(
        "0.0-test", status="draft", released="2026-09-12"
    )
    manifest_path, index_path = write_suite_manifest(manifest, index, root=tmp_path)
    for written in (manifest_path, index_path):
        assert b"\r\n" not in written.read_bytes(), f"{written.name} was written with CRLF"


@pytest.mark.parametrize("suffix", [".yaml", ".json"])
def test_every_released_manifest_on_disk_is_lf(suffix: str):
    for path in (repo_root() / "releases").rglob(f"*{suffix}"):
        assert b"\r\n" not in path.read_bytes(), f"{path} carries CRLF"
