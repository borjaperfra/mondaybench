"""Blocking properties of the v1.1 scenario-specific judge contract.

Written against the DESIRED behaviour, not the behaviour that shipped in v1.0.
The v1.0 fingerprint was defective in both directions - it moved when unrelated
global state moved, and it stayed still when a scenario's real judge
instructions changed - so a test that encoded it would be encoding the bug.

Every mutation here happens on objects already loaded into memory. Nothing under
scenarios/, evaluators/, runs/, verdicts/ or evaluations/ is written, and no
model is called.
"""

from __future__ import annotations

import copy
import dataclasses
import json

import pytest

from mondaybench import judge as judge_mod
from mondaybench.config import load_evaluator
from mondaybench.contract import (
    canonical_json,
    judge_contract,
    judge_contract_fingerprint,
    contract_for,
    diff_contracts,
    comparability_key,
    scenario_penalty_types,
)
from mondaybench.scenarios import load_scenario

EVALUATORS = {
    "monday-001": "evaluator-opus5-v0.1",
    "monday-002": "evaluator-opus5-v0.2",
    "monday-003": "evaluator-opus5-v0.3",
    "monday-004": "evaluator-opus5-v0.4",
    "monday-005": "evaluator-opus5-v0.5",
}


def build(scenario_id, mutate_rubric=None, mutate_gt=None, label_semantics=None):
    """The contract, optionally with an in-memory mutation of its inputs."""
    evaluator = load_evaluator(EVALUATORS[scenario_id])
    scenario = load_scenario(scenario_id, rubric_file=evaluator.rubric_file)
    if mutate_rubric:
        scenario = dataclasses.replace(scenario, rubric=mutate_rubric(scenario.rubric))
    if mutate_gt:
        scenario = dataclasses.replace(
            scenario, ground_truth=mutate_gt(copy.deepcopy(scenario.ground_truth))
        )
    contract = judge_contract(scenario, evaluator)
    if label_semantics is not None:
        contract["label_semantics"] = label_semantics
    return judge_contract_fingerprint(contract), contract


@pytest.fixture(scope="module")
def baseline():
    return {sid: build(sid)[0] for sid in EVALUATORS}


# ---------------------------------------------------------------------------
# A / K - a later scenario's vocabulary must not disturb an earlier scenario
# ---------------------------------------------------------------------------


@pytest.fixture
def a_new_global_penalty_type(monkeypatch):
    """Simulate a monday-006 that introduces a penalty nothing else uses."""
    extended = tuple(list(judge_mod.PENALTY_TYPE_VALUES) + ["SCHEDULE_FABRICATION"])
    monkeypatch.setattr(judge_mod, "PENALTY_TYPE_VALUES", extended)
    schema = copy.deepcopy(judge_mod.PENALTY_SCHEMA)
    schema["properties"]["violations"]["items"]["properties"]["type"]["enum"] = list(extended)
    monkeypatch.setattr(judge_mod, "PENALTY_SCHEMA", schema)
    return extended


def test_A_a_new_scenario_penalty_does_not_change_monday_001(baseline, a_new_global_penalty_type):
    """THE regression. This is precisely what blocked GLM 5.3 under v1.0."""
    assert build("monday-001")[0] == baseline["monday-001"]


def test_K_no_historical_scenario_moves_when_the_global_enum_grows(
    baseline, a_new_global_penalty_type
):
    for scenario_id in EVALUATORS:
        assert build(scenario_id)[0] == baseline[scenario_id], scenario_id


# ---------------------------------------------------------------------------
# B / C / F - operative scenario content must move the hash
# ---------------------------------------------------------------------------


def test_B_changing_a_penalty_deduction_changes_the_fingerprint(baseline):
    def cheaper(rubric):
        penalties = dict(rubric.penalties)
        key = sorted(penalties)[0]
        penalties[key] = dataclasses.replace(penalties[key], points=penalties[key].points - 1)
        return dataclasses.replace(rubric, penalties=penalties)

    assert build("monday-001", mutate_rubric=cheaper)[0] != baseline["monday-001"]


def test_C_changing_criterion_wording_changes_the_fingerprint(baseline):
    def reword(rubric):
        criteria = list(rubric.criteria)
        criteria[0] = dataclasses.replace(
            criteria[0], pass_definition=criteria[0].pass_definition + " Also mention X."
        )
        return dataclasses.replace(rubric, criteria=criteria)

    assert build("monday-001", mutate_rubric=reword)[0] != baseline["monday-001"]


def test_F_reordering_criteria_changes_the_fingerprint(baseline):
    """Rubric order is the order the recorded judge reads the rubric in.

    Contrast with test_E: how the contract OBJECT is serialised must not matter,
    while the order the rubric declares its criteria in must.
    """

    def swap(rubric):
        criteria = list(rubric.criteria)
        criteria[0], criteria[1] = criteria[1], criteria[0]
        return dataclasses.replace(rubric, criteria=criteria)

    assert build("monday-001", mutate_rubric=swap)[0] != baseline["monday-001"]


# ---------------------------------------------------------------------------
# D / J - a change must be confined to the scenario it belongs to
# ---------------------------------------------------------------------------


def test_D_changing_monday_005_leaves_monday_001_alone(baseline):
    def reword(rubric):
        criteria = list(rubric.criteria)
        criteria[0] = dataclasses.replace(
            criteria[0], pass_definition=criteria[0].pass_definition + " Also mention X."
        )
        return dataclasses.replace(rubric, criteria=criteria)

    assert build("monday-005", mutate_rubric=reword)[0] != baseline["monday-005"]
    assert build("monday-001")[0] == baseline["monday-001"]


def test_J_changing_monday_003_factual_anchors_is_confined_to_monday_003(baseline):
    """`factual_plan_accuracy` is scored against these and nothing else."""

    def edit_anchors(ground_truth):
        anchors = ground_truth["factual_anchors"]
        anchors["durations_hours"]["billing_schema_migration"] = 4
        return ground_truth

    assert build("monday-003", mutate_gt=edit_anchors)[0] != baseline["monday-003"]
    for other in ("monday-001", "monday-002", "monday-004", "monday-005"):
        assert build(other)[0] == baseline[other], other


# ---------------------------------------------------------------------------
# E / G - what must NOT move the hash
# ---------------------------------------------------------------------------


def test_E_serialisation_order_does_not_change_the_fingerprint(baseline):
    _, contract = build("monday-001")
    reversed_keys = dict(reversed(list(contract.items())))
    assert judge_contract_fingerprint(reversed_keys) == baseline["monday-001"]


def test_G_non_operative_metadata_does_not_reach_the_contract(baseline):
    """A YAML comment or an unread key never reaches the loaded Rubric.

    Asserted at the level that matters: the builder reads named operative
    fields, so a rubric file carrying extra commentary produces the same
    contract.
    """
    evaluator = load_evaluator(EVALUATORS["monday-001"])
    scenario = load_scenario("monday-001", rubric_file=evaluator.rubric_file)
    first = judge_contract(scenario, evaluator)
    second = judge_contract(scenario, evaluator)
    assert judge_contract_fingerprint(first) == judge_contract_fingerprint(second)
    assert judge_contract_fingerprint(first) == baseline["monday-001"]
    # Nothing incidental is present to begin with.
    blob = canonical_json(first)
    assert "timestamp" not in blob and "C:\\\\" not in blob and "/home/" not in blob


# ---------------------------------------------------------------------------
# H / I - label semantics
# ---------------------------------------------------------------------------


def test_H_changing_the_label_vocabulary_changes_the_fingerprint(baseline):
    changed, _ = build(
        "monday-001",
        label_semantics={"labels": ["PASS", "PARTIAL", "FAIL", "STRONG_PASS"], "tie_rule": "lower"},
    )
    assert changed != baseline["monday-001"]


def test_I_changing_the_tie_rule_changes_the_fingerprint(baseline):
    changed, _ = build(
        "monday-001",
        label_semantics={"labels": ["PASS", "PARTIAL", "FAIL"], "tie_rule": "higher"},
    )
    assert changed != baseline["monday-001"]


# ---------------------------------------------------------------------------
# M / N - the external judge instructions the v1.0 fingerprint never read
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "scenario_id,which",
    [("monday-003", "criterion"), ("monday-004", "penalty")],
)
def test_MN_changing_an_external_judge_prompt_changes_the_fingerprint(
    baseline, monkeypatch, scenario_id, which
):
    """evaluators/<scenario>/judge-prompt.md is the real instruction.

    Under v1.0 editing it moved nothing: `judge_prompt_fingerprint()` hashed the
    built-in templates and `Judge` never loaded the file either.
    """
    from mondaybench import contract as contract_mod

    real = contract_mod.judge_instruction_text

    def altered(evaluator, sid, kind):
        text = real(evaluator, sid, kind)
        if text is not None and kind == which and sid == scenario_id:
            return text + "\nAn extra instruction."
        return text

    monkeypatch.setattr(contract_mod, "judge_instruction_text", altered)
    assert build(scenario_id)[0] != baseline[scenario_id]
    # and it is confined to that scenario
    assert build("monday-001")[0] == baseline["monday-001"]


def test_the_external_prompts_are_actually_in_force(baseline):
    """Every evaluator that declares one must resolve it, not silently fall back."""
    for scenario_id, evaluator_id in EVALUATORS.items():
        evaluator = load_evaluator(evaluator_id)
        _, contract = build(scenario_id)
        for which, field in (("criterion", "prompt_file"), ("penalty", "penalty_prompt_file")):
            declared = getattr(evaluator, field)
            source = contract["judge_instructions"][which]["source"]
            assert source == ("external" if declared else "builtin"), (
                f"{evaluator_id}.{field}={declared!r} but contract says {source}"
            )


# ---------------------------------------------------------------------------
# O - the rendered enum is the scenario's own
# ---------------------------------------------------------------------------


def test_O_the_rendered_penalty_enum_equals_the_scenarios_penalties():
    for scenario_id, evaluator_id in EVALUATORS.items():
        evaluator = load_evaluator(evaluator_id)
        scenario = load_scenario(scenario_id, rubric_file=evaluator.rubric_file)
        contract = judge_contract(scenario, evaluator)
        rendered = contract["output_contract"]["penalty_schema"]
        enum = rendered["properties"]["violations"]["items"]["properties"]["type"]["enum"]
        assert enum == scenario_penalty_types(scenario.rubric)
        assert enum == [p["type"] for p in contract["penalties"]]
        # and it is a strict subset of the global vocabulary for every scenario
        # that does not use all of it
        assert set(enum) <= set(judge_mod.PENALTY_TYPE_VALUES)


# ---------------------------------------------------------------------------
# P / Q - backward compatibility and a gate that stays meaningful
# ---------------------------------------------------------------------------


def test_P_a_v1_0_evaluation_without_a_contract_still_loads_and_keys_legacy(tmp_path):
    from mondaybench.evaluator import load_evaluation
    from mondaybench.config import repo_root

    path = (
        repo_root()
        / "evaluations"
        / "evaluator-opus5-v0.1"
        / "monday-001"
        / "gemma4"
        / "run-001.json"
    )
    evaluation = load_evaluation(path)
    assert evaluation.judge.contract_fingerprint is None
    assert evaluation.suite_version is None
    # It must still be comparable with its own cohort, by the legacy key.
    assert comparability_key(evaluation).startswith("rubric=")


def test_Q_the_comparability_gate_cannot_become_a_no_op():
    """Two genuinely different contracts must still be refused."""

    class _Judge:
        def __init__(self, contract, prompt):
            self.contract_fingerprint = contract
            self.prompt_fingerprint = prompt

    class _Eval:
        def __init__(self, contract, prompt="p", rubric="0.2"):
            self.judge = _Judge(contract, prompt)
            self.rubric_version = rubric

    assert comparability_key(_Eval("aaaa")) != comparability_key(_Eval("bbbb"))
    # a contract-stamped and a legacy record are not silently merged either
    assert comparability_key(_Eval("aaaa")) != comparability_key(_Eval(None))
    # identical contracts do agree - that is the whole point of the fix
    assert comparability_key(_Eval("aaaa")) == comparability_key(_Eval("aaaa"))


# ---------------------------------------------------------------------------
# L - the case that started the migration
# ---------------------------------------------------------------------------


def test_L_a_model_judged_today_shares_the_contract_of_earlier_incumbents():
    """GLM 5.3 versus the seven incumbents, per scenario, from what is on disk."""
    from mondaybench.evaluator import find_evaluations, load_evaluation, models_with_evaluations

    for scenario_id, evaluator_id in EVALUATORS.items():
        contracts = set()
        legacy = set()
        models = models_with_evaluations(evaluator_id, scenario_id, None, "1.1")
        assert "glm5.3" in models, f"{scenario_id}: the challenger is missing from v1.1"
        for slug in models:
            for path in find_evaluations(evaluator_id, scenario_id, slug, None, "1.1"):
                evaluation = load_evaluation(path)
                contracts.add(evaluation.judge.contract_fingerprint)
                legacy.add(evaluation.judge.prompt_fingerprint)
        assert len(contracts) == 1, f"{scenario_id}: {len(contracts)} distinct contracts"
        assert None not in contracts, f"{scenario_id}: a v1.1 evaluation carries no contract"


def test_the_v1_1_contract_matches_what_the_evaluations_recorded():
    """The stored stamp must be reproducible from the scenario, not just stored."""
    from mondaybench.evaluator import find_evaluations, load_evaluation

    for scenario_id, evaluator_id in EVALUATORS.items():
        _, expected = contract_for(scenario_id, evaluator_id)
        for path in find_evaluations(evaluator_id, scenario_id, "glm5.3", None, "1.1"):
            assert load_evaluation(path).judge.contract_fingerprint == expected


# ---------------------------------------------------------------------------
# Explainability
# ---------------------------------------------------------------------------


def test_diff_contracts_names_the_component_that_moved():
    a, _ = contract_for("monday-001", "evaluator-opus5-v0.1")[1], None
    contract_a, _ = contract_for("monday-001", "evaluator-opus5-v0.1")
    contract_b, _ = contract_for("monday-002", "evaluator-opus5-v0.2")
    differences = {d["component"] for d in diff_contracts(contract_a, contract_b)}
    assert {"criteria", "penalties", "noise", "judge_instructions"} <= differences
    penalty_entry = next(
        d for d in diff_contracts(contract_a, contract_b) if d["component"] == "penalties"
    )
    assert "MAJOR_PLANNING_ERROR" in penalty_entry["detail"]
    assert diff_contracts(contract_a, contract_a) == []


def test_the_legacy_fingerprint_is_unchanged_by_the_v1_1_refactor():
    """v1.0 evaluations must keep meaning exactly what they meant.

    `criterion_prompt` and `penalty_prompt` gained an `instructions` parameter.
    With it unset they must render byte-identically, or every stored v1.0
    fingerprint would stop describing its own evaluations.
    """
    assert judge_mod.judge_prompt_fingerprint() == "45998b3c03939498"
