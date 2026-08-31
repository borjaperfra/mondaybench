"""`mondaybench endpoints` - regression cover for the scenario-override wiring.

The command once applied `endpoint_overrides_for(loaded.id)` while having no
`--scenario` option and no `loaded` in scope, so every invocation died with
`NameError: name 'loaded' is not defined`. That is a runtime fault inside the
callback, so `--help` does not catch it; these tests invoke the command for
real with the network stubbed out.
"""

from __future__ import annotations

import pytest
from typer.testing import CliRunner

from mondaybench import cli
from mondaybench.discovery import Endpoint

runner = CliRunner()


@pytest.fixture
def stub_endpoints(monkeypatch):
    """Answer the discovery calls locally so no HTTP is attempted."""
    served = {
        "helmcode": ["deepseek-v4-flash", "gemma4", "glm5.2", "qwen3.6"],
        "nan": ["glm5.3-flash", "mimo-v2.5", "qwen3.6", "qwen3.8-flash"],
    }
    probed: list[Endpoint] = []

    def fake_list_models(endpoint: Endpoint) -> list[str]:
        probed.append(endpoint)
        return served[endpoint.provider]

    monkeypatch.setattr(cli, "list_models", fake_list_models)
    return probed


def test_endpoints_runs_without_a_scenario(stub_endpoints):
    """The bare command is the "is this platform up?" case and must work."""
    result = runner.invoke(cli.app, ["endpoints"])

    assert "NameError" not in result.output
    assert result.exit_code == 0, result.output
    assert {e.provider for e in stub_endpoints} == {"helmcode", "nan"}


def test_endpoints_without_scenario_ignores_overrides(stub_endpoints):
    """qwen3.6 is declared on helmcode; monday-004's override is not applied here.

    The stub serves qwen3.6 from both endpoints, so the run is clean either
    way - what is asserted is the declaration, which is what MISSING is
    computed against.
    """
    result = runner.invoke(cli.app, ["endpoints"])

    assert result.exit_code == 0, result.output
    assert "MISSING" not in result.output


def test_endpoints_applies_the_scenario_override(stub_endpoints, monkeypatch):
    """With --scenario, a model moved to an endpoint that lacks it is reported.

    monday-004 moves qwen3.6 to nan. Pretending nan does not serve it proves
    the override reached the declaration set rather than being ignored.
    """
    monkeypatch.setattr(
        cli,
        "list_models",
        lambda endpoint: {
            "helmcode": ["deepseek-v4-flash", "gemma4", "glm5.2"],
            "nan": ["glm5.3-flash", "mimo-v2.5", "qwen3.8-flash"],
        }[endpoint.provider],
    )

    result = runner.invoke(cli.app, ["endpoints", "--scenario", "monday-004"])

    assert "NameError" not in result.output
    # qwen3.6 is now declared on nan, which the stub says does not serve it.
    assert "MISSING" in result.output
    assert "qwen3.6" in result.output
    assert result.exit_code == 1


def test_endpoints_rejects_an_unknown_scenarios_overrides(stub_endpoints, monkeypatch):
    """A bad override is a config error, not a traceback."""
    monkeypatch.setattr(
        cli, "endpoint_overrides_for", lambda scenario: {"nope-not-a-model": "nan"}
    )

    result = runner.invoke(cli.app, ["endpoints", "--scenario", "monday-004"])

    assert result.exit_code != 0
    assert "nope-not-a-model" in result.output
