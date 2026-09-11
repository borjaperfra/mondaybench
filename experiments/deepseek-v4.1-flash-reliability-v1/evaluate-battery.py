"""Score the reliability battery from the recorded verdicts, inside this directory.

    python evaluate-battery.py

The counterpart to `generate-battery.py`: it passes `root=ROOT`, so the
evaluations land under this experiment directory and the repository's
`evaluations/` tree is untouched. Nothing here reaches a leaderboard.

No API calls. The judge route is `RecordedJudge`, served from the verdict files
under `verdicts/`, which were produced by judging the blind pack candidate by
candidate and then applying the provenance map. The evaluator config names the
model that produced the labels; the verdict file is recorded as the route.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
sys.path.insert(0, str(REPO))

from mondaybench.config import load_evaluator  # noqa: E402
from mondaybench.evaluator import evaluate_run  # noqa: E402
from mondaybench.recorded_judge import RecordedJudge, VerdictStore  # noqa: E402
from mondaybench.runner import run_path  # noqa: E402
from mondaybench.scenarios import load_scenario  # noqa: E402
from mondaybench.schemas import BenchmarkRun  # noqa: E402

MODEL = "deepseek-v4.1-flash-reliability-v1"
EVALUATORS = {
    "monday-001": "evaluator-opus5-v0.1",
    "monday-002": "evaluator-opus5-v0.2",
    "monday-003": "evaluator-opus5-v0.3",
    "monday-004": "evaluator-opus5-v0.4",
    "monday-005": "evaluator-opus5-v0.5",
}


def verdict_file(scenario_id: str) -> Path:
    """Inside this directory, like everything else this experiment produces."""
    return ROOT / "verdicts" / f"{scenario_id}.verdicts.jsonl"


def main() -> int:
    summary: dict[str, list[float]] = {}
    for scenario_id, evaluator_id in EVALUATORS.items():
        evaluator = load_evaluator(evaluator_id)
        loaded = load_scenario(scenario_id, rubric_file=evaluator.rubric_file)
        scenario = loaded.scenario if hasattr(loaded, "scenario") else loaded
        path = verdict_file(scenario_id)
        store = VerdictStore.load(path)
        judge = RecordedJudge(evaluator, store, source=path.name)

        scores = []
        for run_number in (1, 2, 3):
            run_file = run_path(scenario_id, MODEL, run_number, root=ROOT)
            run = BenchmarkRun.model_validate_json(run_file.read_text(encoding="utf-8"))
            judge.bind(run.run_id)
            evaluation = evaluate_run(
                scenario=scenario,
                evaluator=evaluator,
                run=run,
                judge=judge,
                root=ROOT,
                write=True,
            )
            scores.append(evaluation.final_score)
            print(f"{scenario_id} run-{run_number:03d}  base {evaluation.base_score:>6}  "
                  f"final {evaluation.final_score:>6}  "
                  f"penalties {getattr(evaluation.penalties, 'total', evaluation.penalties)}")
        summary[scenario_id] = scores

    print("\nper-scenario means (this battery only, not a Monday Score):")
    means = []
    for scenario_id, scores in summary.items():
        mean = sum(scores) / len(scores)
        means.append(mean)
        print(f"  {scenario_id}  {scores}  mean {mean:.2f}")
    print(f"\nmean of the five scenario means: {sum(means) / len(means):.2f}")
    (ROOT / "scores-summary.json").write_text(
        json.dumps({"model": MODEL, "per_scenario": summary,
                    "scenario_means": {k: sum(v) / len(v) for k, v in summary.items()},
                    "mean_of_scenario_means": sum(means) / len(means),
                    "note": "recorded-verdict route; a prompt-treated battery, not a "
                            "Monday Score"}, indent=2),
        encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
