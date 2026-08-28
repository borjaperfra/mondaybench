"""Regenerate the schema fixtures.

Run from the repository root:

    python tests/fixtures/generate.py

Uses the fake providers from `tests/test_end_to_end.py`, so the fixtures are
always shaped exactly like real artifacts without needing credentials.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "tests"))

from mondaybench import runner as runner_mod  # noqa: E402
from mondaybench.config import load_evaluator  # noqa: E402
from mondaybench.evaluator import evaluate_run  # noqa: E402
from mondaybench.judge import Judge  # noqa: E402
from mondaybench.scenarios import load_scenario  # noqa: E402
from test_end_to_end import (  # noqa: E402
    TEST_MODEL,
    FakeJudgeProvider,
    FakeModelProvider,
    _evaluator,
)

OUT = Path(__file__).parent


def main() -> None:
    scenario = load_scenario("monday-001")
    evaluator = _evaluator(load_evaluator("evaluator-v0.1").ground_truth_map)

    runner_mod.build_model_provider = lambda model: FakeModelProvider()

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        run = runner_mod.execute_run(
            scenario=scenario, model=TEST_MODEL, run_number=1, root=root
        )
        # One PARTIAL and one penalty, so the fixture exercises fractional
        # points and the penalty path rather than a trivial all-PASS shape.
        judge = Judge(evaluator, provider=_MixedJudge())
        evaluation = evaluate_run(
            scenario=scenario, evaluator=evaluator, run=run, judge=judge, root=root
        )

    (OUT / "run-001.json").write_text(
        json.dumps(run.model_dump(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (OUT / "evaluation-001.json").write_text(
        json.dumps(evaluation.model_dump(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"wrote fixtures to {OUT}")
    print(f"base {evaluation.base_score} final {evaluation.final_score}")


class _MixedJudge(FakeJudgeProvider):
    """PASS everything except one PARTIAL, trigger one false action, one penalty."""

    def __init__(self) -> None:
        super().__init__("PASS")
        self.seen: set[str] = set()

    def generate(self, *, model_id, system_prompt, user_prompt, generation_config):
        from mondaybench.providers.base import GenerationResult

        if "false or unnecessary actions" in user_prompt:
            ids = [
                line.split(":")[0].removeprefix("- ").strip()
                for line in user_prompt.splitlines()
                if line.startswith("- ") and ":" in line
            ]
            payload = {
                "items": [
                    {
                        "id": i,
                        "triggered": i == "partner_sync",
                        "evidence": "lists the partner sync as upcoming"
                        if i == "partner_sync"
                        else "",
                    }
                    for i in ids
                ]
            }
        elif "serious factual failures" in user_prompt:
            payload = {
                "violations": [
                    {
                        "type": "MATERIAL_HALLUCINATION",
                        "evidence": "conversion fell 12% on Friday",
                        "reason": "no conversion figure exists in the provided metrics",
                    }
                ]
            }
        elif "umbrella_metrics" in user_prompt:
            payload = {
                "result": "PARTIAL",
                "evidence": "cites 163 API errors",
                "reason": "uses one supporting signal rather than two",
            }
        else:
            payload = {
                "result": "PASS",
                "evidence": "quoted from the response",
                "reason": "matches the PASS definition",
            }
        return GenerationResult(
            text=json.dumps(payload), input_tokens=800, output_tokens=40, total_latency_ms=900.0
        )


if __name__ == "__main__":
    main()
