"""The recorded judge must be as strict as the model judge.

Its whole value is that a human-recorded evaluation is auditable, so a missing
or malformed label has to fail loudly rather than default to anything.
"""

from __future__ import annotations

import json

import pytest

from mondaybench.config import load_evaluator
from mondaybench.evaluator import evaluate_run
from mondaybench.judge import JudgeError
from mondaybench.recorded_judge import RecordedJudge, VerdictStore, build_worksheet

RUN_ID = "monday-001__fixture-model__001"


def _full_verdicts(rubric, label="PASS", *, triggered=(), violations=()):
    lines = [
        json.dumps(
            {
                "run_id": RUN_ID,
                "criterion_id": c.id,
                "result": label,
                "evidence": "quoted",
                "reason": "matches",
            }
        )
        for c in rubric.criteria
    ]
    lines.append(
        json.dumps(
            {
                "run_id": RUN_ID,
                "kind": "noise",
                "items": [
                    {"id": a.id, "triggered": a.id in triggered, "evidence": ""}
                    for a in rubric.noise.false_actions
                ],
            }
        )
    )
    lines.append(
        json.dumps({"run_id": RUN_ID, "kind": "penalties", "violations": list(violations)})
    )
    return "\n".join(lines) + "\n"


def _write(tmp_path, content):
    path = tmp_path / "verdicts.jsonl"
    path.write_text(content, encoding="utf-8")
    return path


@pytest.fixture
def manual_evaluator():
    return load_evaluator("evaluator-manual-v0.1")


# --------------------------------------------------------------------------
# store parsing
# --------------------------------------------------------------------------


def test_loads_a_complete_file(rubric, tmp_path):
    store = VerdictStore.load(_write(tmp_path, _full_verdicts(rubric)))
    assert len(store.criteria) == len(rubric.criteria)
    assert RUN_ID in store.noise
    assert store.penalties[RUN_ID] == []


def test_comments_and_blank_lines_are_ignored(rubric, tmp_path):
    content = "# a comment\n\n" + _full_verdicts(rubric) + "\n# trailing\n"
    store = VerdictStore.load(_write(tmp_path, content))
    assert len(store.criteria) == len(rubric.criteria)


def test_missing_file_raises(tmp_path):
    with pytest.raises(JudgeError, match="not found"):
        VerdictStore.load(tmp_path / "nope.jsonl")


def test_invalid_json_names_the_line(tmp_path):
    with pytest.raises(JudgeError, match=r":2: invalid JSON"):
        VerdictStore.load(_write(tmp_path, '{"run_id":"a","criterion_id":"b","result":"PASS"}\n{oops\n'))


def test_unfilled_worksheet_label_is_rejected(tmp_path):
    # An empty `result` is exactly what an unfinished worksheet looks like.
    content = json.dumps({"run_id": RUN_ID, "criterion_id": "contoso_action", "result": ""})
    with pytest.raises(JudgeError, match="invalid result"):
        VerdictStore.load(_write(tmp_path, content))


def test_bad_label_is_rejected(tmp_path):
    content = json.dumps(
        {"run_id": RUN_ID, "criterion_id": "contoso_action", "result": "GOOD ENOUGH"}
    )
    with pytest.raises(JudgeError, match="invalid result"):
        VerdictStore.load(_write(tmp_path, content))


def test_duplicate_verdict_is_rejected(tmp_path):
    entry = json.dumps({"run_id": RUN_ID, "criterion_id": "contoso_action", "result": "PASS"})
    with pytest.raises(JudgeError, match="duplicate verdict"):
        VerdictStore.load(_write(tmp_path, entry + "\n" + entry + "\n"))


def test_entry_without_run_id_is_rejected(tmp_path):
    with pytest.raises(JudgeError, match="no run_id"):
        VerdictStore.load(_write(tmp_path, json.dumps({"criterion_id": "x", "result": "PASS"})))


def test_unknown_kind_is_rejected(tmp_path):
    with pytest.raises(JudgeError, match="unknown kind"):
        VerdictStore.load(_write(tmp_path, json.dumps({"run_id": RUN_ID, "kind": "vibes"})))


def test_lowercase_label_is_normalized(rubric, tmp_path):
    store = VerdictStore.load(_write(tmp_path, _full_verdicts(rubric, "partial")))
    assert all(v["result"] == "PARTIAL" for v in store.criteria.values())


# --------------------------------------------------------------------------
# serving verdicts
# --------------------------------------------------------------------------


def test_unbound_judge_refuses_to_serve(rubric, tmp_path, manual_evaluator):
    store = VerdictStore.load(_write(tmp_path, _full_verdicts(rubric)))
    judge = RecordedJudge(manual_evaluator, store, source="verdicts.jsonl")
    with pytest.raises(JudgeError, match="bind"):
        judge.judge_criterion(rubric.criteria[0], {}, "response")


def test_missing_criterion_verdict_is_not_defaulted(rubric, tmp_path, manual_evaluator):
    content = "\n".join(
        line
        for line in _full_verdicts(rubric).splitlines()
        if '"contoso_action"' not in line
    )
    store = VerdictStore.load(_write(tmp_path, content))
    judge = RecordedJudge(manual_evaluator, store, source="verdicts.jsonl")
    judge.bind(RUN_ID)
    with pytest.raises(JudgeError, match="no recorded verdict"):
        judge.judge_criterion(rubric.criteria_by_id["contoso_action"], {}, "response")


def test_missing_penalties_entry_is_not_assumed_empty(rubric, tmp_path, manual_evaluator):
    content = "\n".join(
        line for line in _full_verdicts(rubric).splitlines() if '"penalties"' not in line
    )
    store = VerdictStore.load(_write(tmp_path, content))
    judge = RecordedJudge(manual_evaluator, store, source="verdicts.jsonl")
    judge.bind(RUN_ID)
    with pytest.raises(JudgeError, match="no recorded penalties"):
        judge.judge_penalties({}, "response")


def test_noise_entry_omitting_a_category_is_rejected(rubric, tmp_path, manual_evaluator):
    lines = _full_verdicts(rubric).splitlines()
    noise_index = next(i for i, line in enumerate(lines) if '"noise"' in line)
    payload = json.loads(lines[noise_index])
    payload["items"] = payload["items"][:-1]
    lines[noise_index] = json.dumps(payload)
    store = VerdictStore.load(_write(tmp_path, "\n".join(lines)))
    judge = RecordedJudge(manual_evaluator, store, source="verdicts.jsonl")
    judge.bind(RUN_ID)
    with pytest.raises(JudgeError, match="omits"):
        judge.judge_noise(rubric.noise.false_actions, "response")


# --------------------------------------------------------------------------
# end to end, no credentials
# --------------------------------------------------------------------------


def test_full_recorded_evaluation_scores(legacy_scenario, manual_evaluator, tmp_path, monkeypatch):
    from mondaybench import runner as runner_mod
    from tests.test_end_to_end import TEST_MODEL, FakeModelProvider

    monkeypatch.setattr(runner_mod, "build_model_provider", lambda model: FakeModelProvider())
    run = runner_mod.execute_run(
        scenario=legacy_scenario, model=TEST_MODEL, run_number=1, root=tmp_path
    )

    path = _write(
        tmp_path,
        _full_verdicts(
            legacy_scenario.rubric,
            "PASS",
            triggered=("lunch",),
            violations=[
                {"type": "MAJOR_CONTRADICTION", "evidence": "e", "reason": "r"},
            ],
        ),
    )
    judge = RecordedJudge(manual_evaluator, VerdictStore.load(path), source=path.name)
    judge.bind(run.run_id)

    evaluation = evaluate_run(
        scenario=legacy_scenario,
        evaluator=manual_evaluator,
        run=run,
        judge=judge,
        root=tmp_path,
    )
    # 100 base, minus 2 for one false action, minus 5 for the contradiction
    assert evaluation.base_score == 98
    assert evaluation.final_score == 93
    # The judge identity is the model that produced the labels; the verdict file
    # is the route. Conflating them would hide which model actually judged.
    assert evaluation.judge.model_id == manual_evaluator.model_id
    assert evaluation.judge.route == "recorded"
    assert evaluation.judge.verdict_source == path.name
    assert evaluation.evaluator_id == "evaluator-manual-v0.1"


# --------------------------------------------------------------------------
# worksheet
# --------------------------------------------------------------------------


def test_worksheet_covers_every_criterion_and_parses_once_filled(rubric):
    text = build_worksheet(rubric, RUN_ID, "a model response")
    for criterion in rubric.criteria:
        assert criterion.id in text
        assert criterion.pass_definition[:40] in text
    # Filling every empty result makes the worksheet a valid verdict file.
    filled = text.replace('"result": ""', '"result": "PASS"')
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "w.jsonl"
        path.write_text(filled, encoding="utf-8")
        store = VerdictStore.load(path)
    assert len(store.criteria) == len(rubric.criteria)
    assert RUN_ID in store.noise
    assert RUN_ID in store.penalties


def test_blank_worksheet_does_not_parse(rubric, tmp_path):
    text = build_worksheet(rubric, RUN_ID, "a model response")
    with pytest.raises(JudgeError, match="invalid result"):
        VerdictStore.load(_write(tmp_path, text))
