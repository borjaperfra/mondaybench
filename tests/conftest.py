from __future__ import annotations

from pathlib import Path

import pytest

from mondaybench.config import load_evaluator
from mondaybench.scenarios import load_scenario

REPO_ROOT = Path(__file__).resolve().parent.parent
SCENARIO_ID = "monday-001"


@pytest.fixture(scope="session")
def scenario():
    """monday-001 as production loads it: the rubric it is FROZEN against (0.2).

    Before the resolver repair this silently returned rubric.yaml (0.1),
    because scenario.yaml declares no `rubric_file`. See
    tests/test_rubric_resolution.py.
    """
    return load_scenario(SCENARIO_ID)


@pytest.fixture(scope="session")
def legacy_scenario():
    """monday-001 under the SUPERSEDED 0.1 rubric.

    The `-v0.1` evaluators (manual, plain, open, gateway) were written against
    monday-001 rubric 0.1 and their `ground_truth_map` is keyed to 0.1's
    criterion ids. They now declare `rubric_file: rubric.yaml` explicitly, and a
    test that pairs one with a scenario has to load the same rubric or the
    evaluator correctly refuses the mismatch.
    """
    return load_scenario(SCENARIO_ID, rubric_file="rubric.yaml")


@pytest.fixture(scope="session")
def rubric(scenario):
    return scenario.rubric


@pytest.fixture(scope="session")
def evaluator_config():
    return load_evaluator("evaluator-v0.1")
