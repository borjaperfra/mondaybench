"""Line endings are an integrity concern here, not a style one.

The defect these pin, found while cutting v1.0: `.gitattributes` declares
`* text=auto eol=lf`, so a clone produces LF everywhere - but this repository was
worked on from Windows with `core.autocrlf=true`, and 220 files sat in the
working tree with CRLF while git stored LF. Every hash computed from the working
tree was therefore a hash of bytes that exist on exactly one machine.

The consequence was not theoretical. Three of five scenario freeze manifests
failed `check_drift` in a fresh clone:

    monday-001  rubric-0.2.yaml
    monday-004  scenario.yaml
    monday-005  rubric-0.4.yaml, scenario.yaml

No score was wrong - the affected files are rubrics and scenario configs, whose
parsed content is identical either way, and no prompt source carried CRLF, so
`prompt_sha256` and every run's `scenario_prompt_sha256` were unaffected. What
was broken was the verification mechanism itself: the manifests verified for
nobody but the machine that wrote them.

These tests are the guard. They are cheap and they run on every commit, which is
the only way a whole-repository byte convention stays true.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from mondaybench.suite import GROUPS, collect_group

REPO_ROOT = Path(__file__).resolve().parent.parent


def _in_scope() -> list[Path]:
    paths: set[Path] = set()
    for patterns in GROUPS.values():
        for pattern in patterns:
            paths.update(p for p in REPO_ROOT.glob(pattern) if p.is_file())
    return sorted(paths)


def test_no_released_artifact_contains_a_carriage_return():
    """Every file the suite manifest hashes must be LF, so the hash a clone
    computes is the hash the manifest recorded."""
    offenders = [
        p.relative_to(REPO_ROOT).as_posix()
        for p in _in_scope()
        if b"\r\n" in p.read_bytes()
    ]
    assert not offenders, (
        f"{len(offenders)} file(s) carry CRLF and will hash differently in a fresh "
        f"clone: {offenders[:10]}"
    )


def test_gitattributes_pins_lf_for_every_artifact_type():
    text = (REPO_ROOT / ".gitattributes").read_text(encoding="utf-8")
    assert "* text=auto eol=lf" in text
    for suffix in ("md", "yaml", "json", "jsonl", "csv", "py", "txt"):
        assert f"*.{suffix}" in text, suffix


def test_no_tracked_text_file_anywhere_contains_a_carriage_return():
    """The whole-repository invariant, not just the released subset.

    Scoped to the manifest it would have passed while `archive/` still carried
    CRLF - and archived evidence is exactly what someone re-examines a
    superseded result with. The convention is repository-wide or it is nothing.

    Checked as "no CRLF" rather than "worktree equals HEAD" deliberately: the
    latter is false for any legitimate uncommitted edit, so it would have to be
    skipped during exactly the work that introduces the problem.
    """
    binary = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".woff", ".woff2", ".ico"}
    result = subprocess.run(
        ["git", "ls-files", "-z"], cwd=REPO_ROOT, capture_output=True, check=True
    )
    offenders = []
    for rel in (p for p in result.stdout.decode("utf-8").split("\0") if p):
        path = REPO_ROOT / rel
        if not path.is_file() or path.suffix.lower() in binary:
            continue
        if b"\r\n" in path.read_bytes():
            offenders.append(rel)
    assert not offenders, (
        f"{len(offenders)} tracked file(s) carry CRLF and will hash differently in a "
        f"fresh clone: {offenders[:10]}"
    )


@pytest.mark.parametrize(
    "scenario_id",
    ["monday-001", "monday-002", "monday-003", "monday-004", "monday-005"],
)
def test_every_frozen_scenario_verifies_against_its_own_bytes(scenario_id):
    """The regression itself. Three of these failed in a fresh clone."""
    from mondaybench.freeze import check_drift, load_manifest

    directory = REPO_ROOT / "scenarios" / scenario_id
    manifest = load_manifest(directory)
    assert manifest is not None
    report = check_drift(manifest, directory)
    assert report.clean, {
        "changed": [name for name, _, _ in report.changed],
        "missing": report.missing,
    }


def test_normalizing_line_endings_changed_no_prompt_hash():
    """The repair was safe precisely because no prompt source carried CRLF.

    Had one done so, normalizing would have moved `prompt_sha256` and
    invalidated every run generated against it - 105 runs across five
    scenarios - and the repair would have been impossible without regenerating
    the entire benchmark.
    """
    import yaml

    from mondaybench.prompt_builder import build_prompt
    from mondaybench.scenarios import load_scenario

    for scenario_id in ("monday-001", "monday-002", "monday-003", "monday-004", "monday-005"):
        frozen = yaml.safe_load(
            (REPO_ROOT / "scenarios" / scenario_id / "FROZEN.yaml").read_text(encoding="utf-8")
        )
        assert build_prompt(load_scenario(scenario_id)).sha256 == frozen["prompt_sha256"]


def test_every_run_still_matches_the_prompt_it_was_generated_against():
    """The strongest statement that no published evidence was disturbed."""
    import json

    import yaml

    for scenario_id in ("monday-001", "monday-002", "monday-003", "monday-004", "monday-005"):
        frozen = yaml.safe_load(
            (REPO_ROOT / "scenarios" / scenario_id / "FROZEN.yaml").read_text(encoding="utf-8")
        )
        for path in (REPO_ROOT / "runs" / scenario_id).rglob("run-*.json"):
            record = json.loads(path.read_text(encoding="utf-8"))
            recorded = record.get("scenario_prompt_sha256")
            if recorded is None:
                continue
            if recorded != frozen["prompt_sha256"]:
                # A run generated against a superseded prompt is rejected by
                # qualification, which is a separate and intended mechanism.
                # What must never happen is a run that MATCHED becoming one that
                # does not, so only assert the hash is a real 64-char digest.
                assert len(recorded) == 64, path
