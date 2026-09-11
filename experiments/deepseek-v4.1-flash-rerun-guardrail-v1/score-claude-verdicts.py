"""Score the treatment battery from my own blind labels, inside this directory.

The labels in `claude-blind-verdicts/` were set from the packs alone and the
provenance map was opened only to perform the join below, mechanically. Scoring
goes through the harness's recorded-verdict route with `root` pointed here, so
the arithmetic is the one every published battery uses and no API call is made -
and nothing lands in the repository's evaluations tree.

This is one judge's pass. It is not the blind judge's pass and does not replace
it; the point of running both is that they can be differenced.
"""
from __future__ import annotations

import json
import statistics
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

SLUG = "deepseek-v4.1-flash-rerun-guardrail-v1"
EVALUATORS = {
    "monday-001": "evaluator-opus5-v0.1", "monday-002": "evaluator-opus5-v0.2",
    "monday-003": "evaluator-opus5-v0.3", "monday-004": "evaluator-opus5-v0.4",
    "monday-005": "evaluator-opus5-v0.5",
}


def main() -> int:
    prov = json.loads((ROOT / "private-provenance-map.json").read_text(encoding="utf-8"))
    mapping = {e["candidate_id"]: e["run_id"] for e in prov["candidates"]}

    summary: dict[str, list[float]] = {}
    for scenario_id, evaluator_id in EVALUATORS.items():
        src = ROOT / "claude-blind-verdicts" / f"{scenario_id}.blind.jsonl"
        dst = ROOT / "claude-verdicts" / f"{scenario_id}.verdicts.jsonl"
        dst.parent.mkdir(parents=True, exist_ok=True)
        rows = [json.loads(l) for l in src.read_text(encoding="utf-8").splitlines() if l.strip()]
        with dst.open("w", encoding="utf-8", newline="\n") as fh:
            for r in rows:
                cid = r.pop("candidate_id")
                fh.write(json.dumps({"run_id": mapping[cid], **r}, ensure_ascii=False) + "\n")

        evaluator = load_evaluator(evaluator_id)
        loaded = load_scenario(scenario_id, rubric_file=evaluator.rubric_file)
        scenario = loaded.scenario if hasattr(loaded, "scenario") else loaded
        judge = RecordedJudge(evaluator, VerdictStore.load(dst), source=dst.name)

        scores = []
        for run_number in (1, 2, 3):
            run_file = run_path(scenario_id, SLUG, run_number, root=ROOT)
            run = BenchmarkRun.model_validate_json(run_file.read_text(encoding="utf-8"))
            judge.bind(run.run_id)
            ev = evaluate_run(scenario=scenario, evaluator=evaluator, run=run,
                              judge=judge, root=ROOT, write=True)
            scores.append(ev.final_score)
            print(f"{scenario_id} run-{run_number:03d}  base {ev.base_score:>6}  final {ev.final_score:>6}")
        summary[scenario_id] = scores

    means = {s: statistics.fmean(v) for s, v in summary.items()}
    monday = statistics.fmean(means.values())
    print("\nscenario means:")
    for s, m in means.items():
        print(f"  {s}  {summary[s]}  mean {m:.2f}")
    print(f"\nMonday Score (this judge): {monday:.2f}")

    (ROOT / "claude-scores-summary.json").write_bytes((json.dumps({
        "model_slug": SLUG,
        "judge": "session (claude-opus-5), blind labels frozen before the provenance map was opened",
        "note": "one judge's pass, run alongside an independent blind judge; not a replacement for it",
        "per_scenario_runs": summary,
        "scenario_means": {k: round(v, 2) for k, v in means.items()},
        "monday_score": round(monday, 2),
    }, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
