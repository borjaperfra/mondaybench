"""Write the harness verdict files for the two NaN challengers of 2026-10-19.

    uv run python experiments/nan-challengers-2026-10-19-opus-judge/build-board-verdicts.py           # write
    uv run python experiments/nan-challengers-2026-10-19-opus-judge/build-board-verdicts.py --check   # compare

The labels are NOT re-derived here: they are `verdicts/<slug>.jsonl`, which
`join-and-score.py` built from the blind labels through the provenance map.
This script only reshapes them into `verdicts/<scenario>/<slug>.verdicts.jsonl`,
one criterion row per rubric criterion in rubric order, a noise row where the
rubric scores noise, and a penalties row per run.

Penalty candidates the judge recorded with `materially_misleading: false` go
under `dismissed`, as in audits/capabilities/build-board-verdicts.py: the
canonical scorer charges nothing for them, and the recorded-verdict route does
not read the flag, so listing them under `violations` would deduct.

`--check` reads the evaluations `mondaybench evaluate --suite-version 1.13`
wrote and compares every run's final score, and every Monday Score, with
`scores/<slug>.json`.
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))

from mondaybench.config import load_yaml                     # noqa: E402
from mondaybench.scenarios import load_scenario              # noqa: E402

SCEN = ["monday-001", "monday-002", "monday-003", "monday-004", "monday-005"]
EVALUATORS = {f"monday-00{i}": f"evaluator-opus5-v0.{i}" for i in range(1, 6)}
MODELS = ["deepseek-v4.1-flash-1017", "mimo-v2.6-flash"]
SUITE = "1.13"


def official_rubric(sid):
    cfg = load_yaml(ROOT / "evaluators" / f"{EVALUATORS[sid]}.yaml")
    return load_scenario(sid, rubric_file=cfg["rubric_file"]).rubric


def split_penalties(violations: list[dict]) -> tuple[list[dict], list[dict]]:
    deducting, dismissed = [], []
    for v in violations:
        entry = {"type": str(v["type"]).upper(), "evidence": v.get("evidence"),
                 "reason": v.get("reason")}
        if v.get("materially_misleading", True):
            deducting.append(entry)
        else:
            dismissed.append({**entry, "materially_misleading": False,
                              "note": "recorded by the judge as not materially misleading; "
                                      "the canonical scorer charges nothing for it"})
    return deducting, dismissed


def render(sid: str, rows: list[dict], rubric) -> str:
    by_run: dict[str, dict] = {}
    for r in rows:
        if not r["run_id"].startswith(sid + "__"):
            continue
        e = by_run.setdefault(r["run_id"], {"criteria": {}, "noise": None, "penalties": None})
        if r.get("kind") == "noise":
            e["noise"] = r["items"]
        elif r.get("kind") == "penalties":
            e["penalties"] = r.get("violations") or []
        else:
            e["criteria"][r["criterion_id"]] = r
    assert len(by_run) == 3, (sid, sorted(by_run))
    lines: list[str] = []
    for run_id in sorted(by_run):
        e = by_run[run_id]
        assert set(e["criteria"]) == {c.id for c in rubric.criteria}, (run_id, "criteria")
        assert e["penalties"] is not None, (run_id, "no penalties row")
        for c in rubric.criteria:
            r = e["criteria"][c.id]
            lines.append(json.dumps({"run_id": run_id, "criterion_id": c.id, "result": r["result"],
                                     "evidence": r["evidence"], "reason": r["reason"]},
                                    ensure_ascii=False))
        if rubric.noise is not None:
            assert e["noise"] is not None, (run_id, "no noise row")
            assert {i["id"] for i in e["noise"]} == {f.id for f in rubric.noise.false_actions}
            lines.append(json.dumps({"run_id": run_id, "kind": "noise", "items": e["noise"]},
                                    ensure_ascii=False))
        violations, dismissed = split_penalties(e["penalties"])
        lines.append(json.dumps({"run_id": run_id, "kind": "penalties",
                                 "violations": violations, "dismissed": dismissed},
                                ensure_ascii=False))
    return "\n".join(lines) + "\n"


def main() -> int:
    if "--check" not in sys.argv[1:]:
        for slug in MODELS:
            rows = [json.loads(l) for l in (HERE / "verdicts" / f"{slug}.jsonl")
                    .read_text(encoding="utf-8").splitlines() if l.strip()]
            for sid in SCEN:
                target = ROOT / "verdicts" / sid / f"{slug}.verdicts.jsonl"
                text = render(sid, rows, official_rubric(sid))
                if target.exists() and target.read_text(encoding="utf-8") != text:
                    raise SystemExit(f"{target} exists and differs - refusing to overwrite")
                target.write_text(text, encoding="utf-8", newline="\n")
                print(f"  {target.relative_to(ROOT).as_posix()}  {len(text.splitlines())} rows")
        return 0

    from mondaybench.evaluator import evaluation_path, load_evaluation
    failures = 0
    for slug in MODELS:
        want = json.loads((HERE / "scores" / f"{slug}.json").read_text(encoding="utf-8"))
        means = []
        for sid in SCEN:
            scores = []
            for run_id, run in sorted(want["scenarios"][sid]["runs"].items()):
                n = int(run_id.rsplit("__", 1)[1])
                got = load_evaluation(evaluation_path(EVALUATORS[sid], sid, slug, n, None, SUITE)).final_score
                ok = abs(got - run["final_score"]) < 1e-9
                failures += not ok
                scores.append(got)
                print(f"  {slug:26} {sid} run-{n:03d}  harness {got:>6}  join {run['final_score']:>6}"
                      f"  {'ok' if ok else 'MISMATCH'}")
            means.append(statistics.mean(scores))
        monday = statistics.mean(means)
        ok = abs(monday - want["monday_score"]) < 1e-9
        failures += not ok
        print(f"  {slug:26} Monday Score {monday:.2f}  join {want['monday_score']:.2f}"
              f"  {'ok' if ok else 'MISMATCH'}\n")
    if failures:
        raise SystemExit(f"{failures} mismatch(es)")
    print("every run and every Monday Score reproduces")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
