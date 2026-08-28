from __future__ import annotations

from pathlib import Path

import pytest

from mondaybench.config import load_evaluator
from mondaybench.scenarios import load_scenario

REPO_ROOT = Path(__file__).resolve().parent.parent
SCENARIO_ID = "monday-001"


@pytest.fixture(scope="session")
def scenario():
    return load_scenario(SCENARIO_ID)


@pytest.fixture(scope="session")
def rubric(scenario):
    return scenario.rubric


@pytest.fixture(scope="session")
def evaluator_config():
    return load_evaluator("evaluator-v0.1")
