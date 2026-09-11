"""Sample provenance: an official run must not be a run the rubric was built on.

The rule is monday-003's and it is stated in every archive README. What did not
exist until monday-005 exposed it is an enforcement that survives the archiving
the rule itself demands.

check_calibration_overlap compared run_id between LIVE evaluations. Archive the
calibration battery and its evaluations leave evaluations/, so the comparison
has nothing to read and returns clean - including when a calibration response
has actually been promoted. Archiving also frees the run numbers, so the next
battery restarts at run-001 and the ids collide outright.

check_sample_provenance identifies a sample by its own immutable content
instead. These tests pin that behaviour, and case B pins the thing a naive fix
would get wrong: a shared run_id is not, by itself, evidence of anything.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from mondaybench.leaderboard import check_sample_provenance
from mondaybench.runner import archived_run_paths, read_run_record, sample_identity

REPO_ROOT = Path(__file__).resolve().parent.parent


def _record(run_id: str, response: str, request_id: str = "req-x") -> dict:
    return {
        "schema_version": "1",
        "scenario_id": "monday-999",
        "run_id": run_id,
        "run_number": int(run_id.split("__")[-1]),
        "model": {"slug": "m", "display_name": "M", "provider": "p", "model_id": "m"},
        "response": response,
        "provider_metadata": {"request_id": request_id},
    }


def _write(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record), encoding="utf-8")


CAL = ("archive", "monday-999-v0.1-calibration", "runs-monday-999", "m")


# --------------------------------------------------------------------------
# A. Archived overlap is detected
# --------------------------------------------------------------------------


def test_A_archived_calibration_sample_promoted_to_official_is_rejected(tmp_path):
    """The exact case the old guard could not see."""
    body = "## CEO BRIEFING\nthe calibration answer\n"
    _write(tmp_path.joinpath(*CAL, "run-001.json"), _record("monday-999__m__001", body, "req-cal"))
    # Promoted verbatim, and renumbered so run_id no longer matches.
    _write(tmp_path / "runs" / "monday-999" / "m" / "run-007.json",
           _record("monday-999__m__007", body, "req-cal"))

    problems = check_sample_provenance("monday-999", tmp_path)
    assert problems, "a promoted calibration sample must be rejected"
    assert "same sample" in problems[0]


# --------------------------------------------------------------------------
# B. Same run_id, different response is allowed
# --------------------------------------------------------------------------


def test_B_same_run_id_different_sample_is_allowed(tmp_path):
    """monday-005's real situation: ids collide because archiving freed them.

    A shared run_id proves nothing. If this test ever fails, someone has put
    run numbers back in the provenance path.
    """
    _write(tmp_path.joinpath(*CAL, "run-001.json"),
           _record("monday-999__m__001", "calibration answer", "req-cal"))
    _write(tmp_path / "runs" / "monday-999" / "m" / "run-001.json",
           _record("monday-999__m__001", "a genuinely different official answer", "req-off"))

    assert check_sample_provenance("monday-999", tmp_path) == []


# --------------------------------------------------------------------------
# C. Different run_id, identical sample is rejected
# --------------------------------------------------------------------------


def test_C_different_run_id_identical_sample_is_rejected(tmp_path):
    body = "identical bytes"
    _write(tmp_path.joinpath(*CAL, "run-001.json"), _record("monday-999__m__001", body, "req-cal"))
    _write(tmp_path / "runs" / "monday-999" / "m" / "run-004.json",
           _record("monday-999__m__004", body, "req-other"))

    problems = check_sample_provenance("monday-999", tmp_path)
    assert problems and "same sample" in problems[0]


def test_C2_shared_provider_request_id_is_rejected_even_if_text_differs(tmp_path):
    """One generation cannot be both development and official evidence."""
    _write(tmp_path.joinpath(*CAL, "run-001.json"),
           _record("monday-999__m__001", "text as first serialised", "req-shared"))
    _write(tmp_path / "runs" / "monday-999" / "m" / "run-004.json",
           _record("monday-999__m__004", "text after some re-serialisation", "req-shared"))

    problems = check_sample_provenance("monday-999", tmp_path)
    assert problems and "request id" in problems[0]


def test_C3_duplicate_inside_the_official_battery_is_rejected(tmp_path):
    """Two identical official runs are one sample; a mean over them is a lie."""
    body = "the same answer twice"
    _write(tmp_path / "runs" / "monday-999" / "m" / "run-001.json",
           _record("monday-999__m__001", body, "req-1"))
    _write(tmp_path / "runs" / "monday-999" / "m" / "run-002.json",
           _record("monday-999__m__002", body, "req-2"))

    problems = check_sample_provenance("monday-999", tmp_path)
    assert problems and "duplicates" in problems[0]


# --------------------------------------------------------------------------
# D + E. The real monday-005 battery
# --------------------------------------------------------------------------


def _official_monday_005_runs():
    """The runs that were actually judged, per model, three per model.

    Reading every file under runs/monday-005/ counts rejected attempts too, and
    pinning a total headcount made this test fail for any new model rather than
    for any real defect. The battery is defined by what earned an evaluation.
    """
    evaluated = REPO_ROOT / "evaluations" / "evaluator-opus5-v0.5" / "monday-005"
    paths = []
    for model_dir in sorted(p for p in evaluated.iterdir() if p.is_dir()):
        for evaluation in sorted(model_dir.glob("run-*.json")):
            run = REPO_ROOT / "runs" / "monday-005" / model_dir.name / evaluation.name
            assert run.is_file(), f"{evaluation} has no raw output at {run}"
            paths.append(run)
    return paths


def test_D_monday_005_official_has_zero_overlap_with_its_calibration_archive():
    archived = archived_run_paths("monday-005", REPO_ROOT)
    live = _official_monday_005_runs()
    assert len(archived) == 21, f"expected the archived calibration battery, found {len(archived)}"
    assert live, "no official monday-005 battery found"
    assert len(live) % 3 == 0, f"the battery is not three runs per model: {len(live)}"

    dev = {sample_identity(read_run_record(p))[0] for p in archived}
    off = [sample_identity(read_run_record(p))[0] for p in live]
    assert not (dev & set(off)), "an official monday-005 sample appears in the calibration archive"


def test_E_monday_005_official_samples_are_mutually_distinct():
    live = _official_monday_005_runs()
    ids = [sample_identity(read_run_record(p))[0] for p in live]
    assert len(ids) == len(set(ids)), "two official monday-005 samples are the same response"


def test_E2_every_monday_005_run_carries_a_provider_request_id():
    """Corroborating identity present on the real battery, both sides.

    A content hash alone cannot distinguish two samples that happen to produce
    identical text, so every run carries a second, independent identity. For an
    API route that is the provider's request id.

    A runtime that exposes no request id must still carry one: the rule is that
    corroborating identity exists, not that it came from an API. Such a run has
    to say so explicitly - `request_id` null AND the field listed among the
    values the runtime did not expose - and supply a session identity in its
    place. A run that is simply missing a request id, with no such record, still
    fails.
    """
    paths = sorted((REPO_ROOT / "runs" / "monday-005").glob("*/run-*.json")) + archived_run_paths(
        "monday-005", REPO_ROOT
    )
    missing = []
    for path in paths:
        record = read_run_record(path)
        if sample_identity(record)[1]:
            continue
        runtime = ((record.get("provider_metadata") or {}).get("raw_usage") or {}).get(
            "codex_runtime"
        ) or {}
        declared = "request_id" in (runtime.get("unobservable") or [])
        session = runtime.get("codex_thread_id")
        if not (declared and session):
            missing.append(path)
    assert not missing, f"runs without a request_id or a declared substitute: {missing[:3]}"


# --------------------------------------------------------------------------
# F. Historical scenarios remain valid
# --------------------------------------------------------------------------


@pytest.mark.parametrize("scenario", ["monday-001", "monday-002", "monday-003", "monday-004"])
def test_F_historical_scenarios_pass_the_new_guard_unchanged(scenario):
    """The guard must be additive. If a published scenario now fails, the guard
    is wrong - not the history."""
    assert check_sample_provenance(scenario, REPO_ROOT) == []


def test_F2_the_guard_finds_archived_material_for_every_scenario_that_has_it():
    """A guard that silently finds nothing to compare is the failure mode this
    whole exercise exists to remove."""
    counts = {
        s: len(archived_run_paths(s, REPO_ROOT))
        for s in ("monday-001", "monday-002", "monday-003", "monday-004", "monday-005")
    }
    assert counts["monday-005"] == 21
    assert sum(counts.values()) > 50, counts


def test_F3_identity_ignores_score_path_and_run_number():
    """Identity must be a property of the sample, not of where it is filed."""
    a = _record("monday-999__m__001", "same bytes", "req-1")
    b = _record("monday-999__m__099", "same bytes", "req-1")
    b["run_number"] = 99
    b["timestamp_utc"] = "2030-01-01T00:00:00Z"
    assert sample_identity(a) == sample_identity(b)
