"""`--evaluator` must be resolved from the scenario, not from a fixed default.

Every publishing command defaulted to `evaluator-opus5-v0.1`, which belongs to
monday-001 and names `rubric-0.2.yaml`. So `freeze --scenario monday-002 --check`
looked for `scenarios/monday-002/rubric-0.2.yaml`, did not find it, and reported
"scenario 'monday-002' is missing: rubric-0.2.yaml" - a scary message about a
perfectly intact frozen scenario.

The quiet failure was worse than the loud one. A scenario that happened to ship
a file of that name would have been frozen, planned or published against the
wrong rubric without a word.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from mondaybench.config import ConfigError, evaluators_for_scenario, resolve_evaluator

REPO_ROOT = Path(__file__).resolve().parent.parent
EVALUATORS = REPO_ROOT / "evaluators"
FALLBACK = "evaluator-opus5-v0.1"


def _write(tmp_path: Path, name: str, body: dict) -> None:
    directory = tmp_path / "evaluators"
    directory.mkdir(exist_ok=True)
    (directory / f"{name}.yaml").write_text(yaml.safe_dump(body), encoding="utf-8")


# --------------------------------------------------------------------------
# The repository as it stands
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "scenario_id,expected",
    [
        ("monday-002", "evaluator-opus5-v0.2"),
        ("monday-003", "evaluator-opus5-v0.3"),
    ],
)
def test_a_scenario_resolves_to_its_own_official_evaluator(scenario_id, expected):
    assert resolve_evaluator(scenario_id, None, FALLBACK) == expected


def test_the_resolved_evaluator_names_a_rubric_the_scenario_actually_ships():
    """The bug, stated as a property: the rubric has to exist where it is looked for."""
    for scenario_id in ("monday-001", "monday-002", "monday-003"):
        evaluator_id = resolve_evaluator(scenario_id, None, FALLBACK)
        rubric = yaml.safe_load(
            (EVALUATORS / f"{evaluator_id}.yaml").read_text(encoding="utf-8")
        ).get("rubric_file", "rubric.yaml")
        assert (REPO_ROOT / "scenarios" / scenario_id / rubric).exists(), (
            scenario_id,
            evaluator_id,
            rubric,
        )


def test_monday_001_keeps_the_old_fallback():
    """Its evaluators predate the `scenario` field. Nothing about them may change."""
    assert evaluators_for_scenario("monday-001") == {
        "official": [],
        "calibration": [],
        "other": [],
    }
    assert resolve_evaluator("monday-001", None, FALLBACK) == FALLBACK


def test_an_explicit_evaluator_always_wins():
    assert resolve_evaluator("monday-002", "evaluator-manual-v0.1", FALLBACK) == (
        "evaluator-manual-v0.1"
    )


# --------------------------------------------------------------------------
# The shapes that must fail rather than guess
# --------------------------------------------------------------------------


def test_calibration_evaluators_never_resolve_on_their_own(tmp_path, monkeypatch):
    """A draft evaluator must never be picked up by a publishing command."""
    _write(tmp_path, "draft-a", {"id": "draft-a", "scenario": "monday-999", "status": "calibration"})
    found = evaluators_for_scenario("monday-999", root=tmp_path)
    assert found["calibration"] == ["draft-a"]
    monkeypatch.setattr("mondaybench.config.repo_root", lambda: tmp_path)
    with pytest.raises(ConfigError) as exc:
        resolve_evaluator("monday-999", None, FALLBACK)
    assert "no evaluator marked" in str(exc.value)


def test_two_official_evaluators_are_an_error_not_a_coin_flip(tmp_path, monkeypatch):
    _write(tmp_path, "off-a", {"id": "off-a", "scenario": "monday-999", "status": "official"})
    _write(tmp_path, "off-b", {"id": "off-b", "scenario": "monday-999", "status": "official"})
    monkeypatch.setattr("mondaybench.config.repo_root", lambda: tmp_path)
    with pytest.raises(ConfigError) as exc:
        resolve_evaluator("monday-999", None, FALLBACK)
    assert "2 official evaluators" in str(exc.value)


def test_an_unknown_scenario_falls_back_rather_than_raising(tmp_path, monkeypatch):
    monkeypatch.setattr("mondaybench.config.repo_root", lambda: tmp_path)
    assert resolve_evaluator("monday-999", None, FALLBACK) == FALLBACK


# --------------------------------------------------------------------------
# No command may reintroduce a scenario-blind default
# --------------------------------------------------------------------------


def test_no_command_defaults_to_a_literal_evaluator_id():
    import inspect

    from mondaybench import cli

    source = inspect.getsource(cli)
    for marker in ("typer.Option(OFFICIAL_EVALUATOR", "typer.Option(DEFAULT_EVALUATOR"):
        assert marker not in source, f"a command still defaults to {marker}"


def test_every_command_taking_evaluator_resolves_it():
    import inspect

    from mondaybench import cli

    for name in ("validate", "evaluate", "leaderboard", "freeze", "plan", "results", "benchmark"):
        source = inspect.getsource(getattr(cli, name))
        assert "--evaluator" in source, name
        assert "_evaluator_for(" in source, f"{name} does not resolve --evaluator"


# --------------------------------------------------------------------------
# The same shape of bug: a per-scenario value some call sites thread and
# others forget
# --------------------------------------------------------------------------


def test_every_battery_call_site_threads_the_scenario_ceiling():
    """A missing `expected_max_output_tokens` inverts qualification silently.

    `plan_battery` and `build_leaderboard` fall back to the model default when
    the scenario ceiling is not passed. On monday-004 that turned the comparison
    inside out: the 96,000-token official runs were rejected as
    "!= configured 32000" and the superseded pre-policy runs were counted as
    official. `plan` and `publish` both did it, so `--official` would have
    published the wrong battery without a single warning.
    """
    import ast

    for module in ("mondaybench/cli.py", "mondaybench/cli_official.py"):
        tree = ast.parse((REPO_ROOT / module).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
                continue
            if node.func.id not in ("plan_battery", "build_leaderboard"):
                continue
            keywords = {kw.arg for kw in node.keywords}
            assert "expected_max_output_tokens" in keywords, (
                f"{module}:{node.lineno} calls {node.func.id}() without "
                "expected_max_output_tokens"
            )


# --------------------------------------------------------------------------
# A run the rubric was tuned on must not become the evidence it publishes
# --------------------------------------------------------------------------


def _fake_evaluation(root: Path, evaluator: str, scenario: str, model: str, run: int) -> None:
    directory = root / "evaluations" / evaluator / scenario / model
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"run-{run:03d}.json").write_text(
        __import__("json").dumps(
            {
                "schema_version": "1",
                "evaluator_id": evaluator,
                "benchmark_version": "0.4",
                "scenario_id": scenario,
                "run_id": f"{scenario}__{model}__{run:03d}",
                "model_slug": model,
                "scenario_prompt_sha256": "0" * 64,
                "timestamp_utc": "2026-11-02T00:00:00Z",
                "judge": {"provider": "anthropic", "model_id": "claude-opus-5", "temperature": 0},
                "dimensions": {},
                "criteria": {},
                "false_actions": {},
                "penalties": {},
                "base_score": 90.0,
                "final_score": 90.0,
            }
        ),
        encoding="utf-8",
    )


def test_a_calibration_run_cannot_be_published_as_official(tmp_path, monkeypatch):
    """The gate that would have caught `run --reuse-valid-runs` on a fresh freeze.

    Qualification cannot see this: a calibration run was generated under exactly
    the published conditions. What disqualifies it is that a draft evaluator also
    scored it, which is a fact about the evaluations tree, not about the run.
    """
    from mondaybench.leaderboard import check_calibration_overlap

    _write(tmp_path, "off", {"id": "off", "scenario": "monday-999", "status": "official"})
    _write(tmp_path, "cal", {"id": "cal", "scenario": "monday-999", "status": "calibration"})
    monkeypatch.setattr("mondaybench.config.repo_root", lambda: tmp_path)

    # run-002 was the calibration sample; run-003 is fresh after the freeze.
    _fake_evaluation(tmp_path, "cal", "monday-999", "glm5.2", 2)
    _fake_evaluation(tmp_path, "off", "monday-999", "glm5.2", 3)
    assert check_calibration_overlap("off", "monday-999", root=tmp_path) == []

    # Now promote the calibration run into the official battery.
    _fake_evaluation(tmp_path, "off", "monday-999", "glm5.2", 2)
    problems = check_calibration_overlap("off", "monday-999", root=tmp_path)
    assert len(problems) == 1
    assert "monday-999__glm5.2__002" in problems[0]
    assert "cal" in problems[0]


def test_publish_runs_the_calibration_overlap_gate():
    import inspect

    from mondaybench import cli_official

    source = inspect.getsource(cli_official.cmd_publish)
    assert "check_calibration_overlap(" in source


# --------------------------------------------------------------------------
# Per-scenario endpoint overrides
# --------------------------------------------------------------------------
#
# A model's endpoint is part of its serving configuration, so qualification
# rejects a run whose provider differs from the configured one. Moving a model
# in models.yaml therefore disqualifies every run already published under the
# old endpoint - qwen3.6 alone has three official runs in each of monday-001,
# 002 and 003. The override scopes an endpoint change to one scenario.


def test_overrides_swap_the_endpoint_and_its_credentials(tmp_path, monkeypatch):
    """Provider, base_url_env and api_key_env must move together."""
    from mondaybench.config import apply_endpoint_overrides, load_models

    models = load_models()
    assert models["qwen3.6"].provider == "helmcode"
    moved = apply_endpoint_overrides(models, {"qwen3.6": "nan"})
    assert moved["qwen3.6"].provider == "nan"
    assert moved["qwen3.6"].base_url_env == models["glm5.3-flash"].base_url_env
    assert moved["qwen3.6"].api_key_env == models["glm5.3-flash"].api_key_env
    # Everything else about the model is untouched, including its id.
    assert moved["qwen3.6"].model_id == models["qwen3.6"].model_id
    assert moved["qwen3.6"].max_output_tokens == models["qwen3.6"].max_output_tokens
    # And no other model moved.
    assert moved["gemma4"].provider == models["gemma4"].provider


def test_an_empty_override_map_returns_the_models_unchanged():
    from mondaybench.config import apply_endpoint_overrides, load_models

    models = load_models()
    assert apply_endpoint_overrides(models, {}) is models


def test_an_unknown_model_or_endpoint_is_an_error():
    from mondaybench.config import apply_endpoint_overrides, load_models

    models = load_models()
    with pytest.raises(ConfigError, match="unknown model"):
        apply_endpoint_overrides(models, {"nope": "nan"})
    with pytest.raises(ConfigError, match="unknown endpoint"):
        apply_endpoint_overrides(models, {"qwen3.6": "nowhere"})


def test_endpoint_overrides_live_outside_the_frozen_scenario():
    """scenario.yaml is covered by FROZEN.yaml; a serving detail must not be."""
    import yaml as _yaml

    from mondaybench.config import endpoint_overrides_for

    for scenario_id in ("monday-001", "monday-002", "monday-003", "monday-004"):
        raw = _yaml.safe_load(
            (REPO_ROOT / "scenarios" / scenario_id / "scenario.yaml").read_text(encoding="utf-8")
        )
        generation = raw.get("generation") or {}
        assert "endpoint_overrides" not in generation, scenario_id
    # The map is read from models.yaml, and is currently empty for every
    # scenario - see the note there about qwen3.6.
    assert endpoint_overrides_for("monday-004") == {}


def test_published_scenarios_declare_no_override():
    """A frozen battery's endpoints must never move under it."""
    from mondaybench.config import endpoint_overrides_for

    for scenario_id in ("monday-001", "monday-002", "monday-003"):
        assert endpoint_overrides_for(scenario_id) == {}


def test_the_abandoned_qwen36_nan_runs_do_not_qualify():
    """Kept as evidence of the endpoint finding; never counted as official.

    NaN serves qwen3.6 as a reasoning model and Helmcode does not, so a
    monday-004 score from NaN would not be comparable with the same model's
    monday-001..003 scores. With no override declared these fail on provider,
    which is the outcome we want and did not have to hand-maintain.
    """
    from mondaybench.config import apply_endpoint_overrides, endpoint_overrides_for, load_models
    from mondaybench.official import plan_model
    from mondaybench.prompt_builder import build_prompt
    from mondaybench.scenarios import load_scenario

    scenario = load_scenario("monday-004")
    models = apply_endpoint_overrides(load_models(), endpoint_overrides_for("monday-004"))
    plan = plan_model(
        scenario_id="monday-004",
        model_slug="qwen3.6",
        model=models.get("qwen3.6"),
        expected_prompt_sha256=build_prompt(scenario).sha256,
        expected_max_output_tokens=scenario.safety_ceiling_tokens,
    )
    rejected = {v.run_number: v.reasons for v in plan.rejected}
    for number in (3, 4, 5):
        assert number in rejected, number
        assert any("provider 'nan'" in r for r in rejected[number]), rejected[number]


def test_qwen36_reasons_on_nan_and_not_on_helmcode():
    """The measurement behind the decision, so it cannot quietly rot."""
    import json as _json

    def usage(number):
        # run-002 is the Helmcode calibration run, archived with its battery;
        # 003-005 are the abandoned NaN runs, still under runs/.
        for base in (
            REPO_ROOT / "runs" / "monday-004" / "qwen3.6",
            REPO_ROOT / "archive" / "monday-004-v0.3-calibration" / "runs-monday-004" / "qwen3.6",
        ):
            path = base / f"run-{number:03d}.json"
            if path.is_file():
                payload = _json.loads(path.read_text(encoding="utf-8"))
                return payload["model"]["provider"], payload["usage"], payload["reasoning"]
        raise AssertionError(f"qwen3.6 run-{number:03d} is missing from both trees")

    provider, helmcode_usage, _ = usage(2)
    assert provider == "helmcode"
    assert not helmcode_usage["reasoning_tokens"]

    for number in (3, 4, 5):
        provider, nan_usage, reasoning = usage(number)
        assert provider == "nan"
        # Same request, `reasoning_requested: false`, and it reasons anyway.
        assert reasoning["requested"] is False
        assert reasoning["status"] == "DELIVERED"
        assert nan_usage["reasoning_tokens"] > 5_000
        assert nan_usage["output_tokens"] > 2 * helmcode_usage["output_tokens"]


def test_archived_run_numbers_are_never_reused():
    """A reused number would give a new response an archived run's id.

    Recorded verdicts are keyed by run id, so an archived verdict file would
    replay against the wrong text and score it without erroring. monday-003's
    archive README names this trap; nothing prevented it until now.
    """
    from mondaybench.config import load_models
    from mondaybench.official import plan_model
    from mondaybench.prompt_builder import build_prompt
    from mondaybench.runner import archived_run_numbers
    from mondaybench.scenarios import load_scenario

    archived = archived_run_numbers("monday-004", "qwen3.8-flash")
    assert archived, "the calibration battery was archived; its numbers must be known"

    scenario = load_scenario("monday-004")
    plan = plan_model(
        scenario_id="monday-004",
        model_slug="qwen3.8-flash",
        model=load_models().get("qwen3.8-flash"),
        expected_prompt_sha256=build_prompt(scenario).sha256,
        expected_max_output_tokens=scenario.safety_ceiling_tokens,
        target=3,
    )
    assert plan.reserved == archived
    assert not (set(plan.next_run_numbers()) & archived)
    on_disk = {v.run_number for v in (*plan.official, *plan.rejected)}
    assert not (set(plan.next_run_numbers()) & on_disk)


def test_the_calibration_battery_is_out_of_the_official_tree():
    """Archived, so `run --reuse-valid-runs` cannot promote it by accident."""
    archive = REPO_ROOT / "archive" / "monday-004-v0.3-calibration"
    assert (archive / "README.md").is_file()
    assert (archive / "runs-monday-004").is_dir()
    assert len(list((archive / "runs-monday-004").glob("*/run-*.json"))) == 7
    # And no calibration evaluator still has live evaluations for the scenario.
    for name in ("evaluator-opus5-v0.4-calibration",
                 "evaluator-opus5-v0.4-calibration-2",
                 "evaluator-opus5-v0.4-calibration-3"):
        assert not (REPO_ROOT / "evaluations" / name / "monday-004").exists(), name


def test_a_run_write_will_not_clobber_a_file_that_appeared_meanwhile(tmp_path):
    """The pre-flight existence check cannot close this race on its own.

    `execute_run` checks before calling the provider; generation then takes
    minutes. Two batteries covering the same model both pass that check and both
    write. It happened once on monday-004/mimo-v2.5, and the second time only
    the ordering saved it. The write itself has to be exclusive.
    """
    import json as _json

    from mondaybench.runner import RunExistsError, run_path, write_run
    from tests.test_official import make_run

    run = make_run(run_number=1)
    first = write_run(run, root=tmp_path, exclusive=True)
    assert first == run_path(run.scenario_id, run.model.slug, 1, tmp_path)
    assert _json.loads(first.read_text(encoding="utf-8"))["run_number"] == 1

    # A second battery finishes generating the same run number.
    with pytest.raises(RunExistsError, match="appeared while this run was generating"):
        write_run(run, root=tmp_path, exclusive=True)
    # ...and the original is untouched.
    assert _json.loads(first.read_text(encoding="utf-8"))["run_number"] == 1

    # `--overwrite` still overwrites, deliberately.
    write_run(run, root=tmp_path, exclusive=False)
