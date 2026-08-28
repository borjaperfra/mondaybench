from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from mondaybench.schemas import BenchmarkRun, Evaluation

FIXTURES = Path(__file__).parent / "fixtures"


def test_fixture_run_validates():
    run = BenchmarkRun.model_validate_json(
        (FIXTURES / "run-001.json").read_text(encoding="utf-8")
    )
    assert run.schema_version == "1"
    assert run.scenario_id == "monday-001"
    assert run.run_id == "monday-001__fixture-model__001"
    assert run.response
    assert len(run.scenario_prompt_sha256) == 64


def test_fixture_evaluation_validates():
    evaluation = Evaluation.model_validate_json(
        (FIXTURES / "evaluation-001.json").read_text(encoding="utf-8")
    )
    assert evaluation.evaluator_id == "evaluator-v0.1"
    assert evaluation.final_score == evaluation.base_score + evaluation.penalties.total
    assert set(evaluation.dimensions) == {
        "action_detection",
        "state_reconstruction",
        "prioritization",
        "data_reasoning",
        "uncertainty",
        "noise_resistance",
    }


def test_fixture_evaluation_dimension_totals_are_internally_consistent():
    evaluation = Evaluation.model_validate_json(
        (FIXTURES / "evaluation-001.json").read_text(encoding="utf-8")
    )
    assert sum(d.score for d in evaluation.dimensions.values()) == pytest.approx(
        evaluation.base_score
    )


def test_unknown_fields_are_rejected():
    payload = json.loads((FIXTURES / "run-001.json").read_text(encoding="utf-8"))
    payload["surprise"] = True
    with pytest.raises(ValidationError):
        BenchmarkRun.model_validate(payload)


def test_bad_label_is_rejected():
    payload = json.loads((FIXTURES / "evaluation-001.json").read_text(encoding="utf-8"))
    first = next(iter(payload["criteria"]))
    payload["criteria"][first]["result"] = "EXCELLENT"
    with pytest.raises(ValidationError):
        Evaluation.model_validate(payload)


def test_bad_penalty_type_is_rejected():
    payload = json.loads((FIXTURES / "evaluation-001.json").read_text(encoding="utf-8"))
    payload["penalties"]["items"] = [
        {"type": "BAD_VIBES", "points": -5, "evidence": "e", "reason": "r"}
    ]
    with pytest.raises(ValidationError):
        Evaluation.model_validate(payload)


def test_run_round_trips_through_json():
    original = BenchmarkRun.model_validate_json(
        (FIXTURES / "run-001.json").read_text(encoding="utf-8")
    )
    again = BenchmarkRun.model_validate(json.loads(json.dumps(original.model_dump())))
    assert again == original


def test_evaluation_round_trips_through_json():
    original = Evaluation.model_validate_json(
        (FIXTURES / "evaluation-001.json").read_text(encoding="utf-8")
    )
    again = Evaluation.model_validate(json.loads(json.dumps(original.model_dump())))
    assert again == original
