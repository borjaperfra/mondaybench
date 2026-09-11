"""Map the blind verdicts onto the runs and score them, inside this directory.

    python scripts/evaluate-challenger.py

Two steps, in this order and no other:

1. `judge-verdicts/*.blind.jsonl` is keyed by `candidate_id`. The join to
   `run_id` is performed here, mechanically, from `private-provenance-map.json`.
   The labels were written before that map was opened and none was changed
   afterwards.
2. The runs are scored through the harness's recorded-verdict route with `root`
   pointed at this directory, so `verdicts/`, `evaluations/` and the scores stay
   inside the challenger pack. No API call is made.
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT.parents[0]
sys.path.insert(0, str(REPO))

from mondaybench.config import load_evaluator  # noqa: E402
from mondaybench.evaluator import evaluate_run  # noqa: E402
from mondaybench.recorded_judge import RecordedJudge, VerdictStore  # noqa: E402
from mondaybench.runner import run_path  # noqa: E402
from mondaybench.scenarios import load_scenario  # noqa: E402
from mondaybench.schemas import BenchmarkRun  # noqa: E402

SLUG = "gpt-6-astra"
EVALUATORS = {
    "monday-001": "evaluator-opus5-v0.1",
    "monday-002": "evaluator-opus5-v0.2",
    "monday-003": "evaluator-opus5-v0.3",
    "monday-004": "evaluator-opus5-v0.4",
    "monday-005": "evaluator-opus5-v0.5",
}


def candidate_to_run_id() -> dict[str, str]:
    prov = json.loads((ROOT / "private-provenance-map.json").read_text(encoding="utf-8"))
    mapping = {}
    for entry in prov["candidates"]:
        number = int(entry["run_id"].split("-")[-1])
        mapping[entry["candidate_id"]] = (
            f"{entry['scenario_id']}__{SLUG}__{number:03d}"
        )
    return mapping


def write_verdicts() -> None:
    mapping = candidate_to_run_id()
    out_dir = ROOT / "verdicts"
    out_dir.mkdir(exist_ok=True)
    for path in sorted((ROOT / "judge-verdicts").glob("*.blind.jsonl")):
        scenario = path.name.split(".")[0]
        target = out_dir / f"{scenario}.verdicts.jsonl"
        lines = [json.loads(line) for line in
                 path.read_text(encoding="utf-8").splitlines() if line.strip()]
        with target.open("w", encoding="utf-8") as fh:
            for row in lines:
                cid = row.pop("candidate_id")
                fh.write(json.dumps({"run_id": mapping[cid], **row},
                                    ensure_ascii=False) + "\n")
        print(f"  {target.name}: {len(lines)} records")


def main() -> int:
    print("candidate -> run_id join:")
    write_verdicts()
    print()

    summary: dict[str, list[float]] = {}
    for scenario_id, evaluator_id in EVALUATORS.items():
        evaluator = load_evaluator(evaluator_id)
        loaded = load_scenario(scenario_id, rubric_file=evaluator.rubric_file)
        scenario = loaded.scenario if hasattr(loaded, "scenario") else loaded
        store_path = ROOT / "verdicts" / f"{scenario_id}.verdicts.jsonl"
        judge = RecordedJudge(evaluator, VerdictStore.load(store_path),
                              source=store_path.name)
        scores = []
        for run_number in (1, 2, 3):
            run_file = run_path(scenario_id, SLUG, run_number, root=ROOT)
            run = BenchmarkRun.model_validate_json(run_file.read_text(encoding="utf-8"))
            judge.bind(run.run_id)
            evaluation = evaluate_run(scenario=scenario, evaluator=evaluator, run=run,
                                      judge=judge, root=ROOT, write=True)
            scores.append(evaluation.final_score)
            print(f"{scenario_id} run-{run_number:03d}  base {evaluation.base_score:>6}"
                  f"  final {evaluation.final_score:>6}")
        summary[scenario_id] = scores

    means = {s: statistics.fmean(v) for s, v in summary.items()}
    print("\nscenario means:")
    for s, m in means.items():
        print(f"  {s}  {summary[s]}  mean {m:.2f}")
    monday = statistics.fmean(means.values())
    print(f"\nMonday Score: {monday:.2f}")
    (ROOT / "scores-summary.json").write_text(
        json.dumps({"model": SLUG, "display_name": "GPT-6 Astra",
                    "judge": "session (claude-opus-5), recorded verdicts",
                    "per_scenario_runs": summary,
                    "scenario_means": {k: round(v, 2) for k, v in means.items()},
                    "monday_score": round(monday, 2)}, indent=2),
        encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
