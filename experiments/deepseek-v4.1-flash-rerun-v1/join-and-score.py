"""Open the provenance map, join the blind labels to runs, and score them.

Order matters and is enforced by the ordering of the two steps below. Every
label in `blind-verdicts/` was written from the pack alone and none was touched
after `private-provenance-map.json` was read; this script does the join
mechanically so that no judgement is exercised at the point the two are brought
together.

Scoring goes through the harness's recorded-verdict route, so the arithmetic is
the same one every published battery was scored with and no judge model is
called.
"""
from __future__ import annotations

import json
import statistics
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
sys.path.insert(0, str(REPO))

SLUG = "deepseek-v4.1-flash-rerun-v1"
# The evaluator is named rather than resolved. `evaluate` defaults to whichever
# evaluator declares the scenario and is marked official, which for monday-001
# is not evaluator-opus5-v0.1 and therefore not the rubric the published battery
# was scored against. Naming them keeps this battery on the same five rubrics.
EVALUATORS = {
    "monday-001": "evaluator-opus5-v0.1",
    "monday-002": "evaluator-opus5-v0.2",
    "monday-003": "evaluator-opus5-v0.3",
    "monday-004": "evaluator-opus5-v0.4",
    "monday-005": "evaluator-opus5-v0.5",
}
SCENARIOS = list(EVALUATORS)


def candidate_to_run_id() -> dict[str, str]:
    prov = json.loads((ROOT / "private-provenance-map.json").read_text(encoding="utf-8"))
    return {e["candidate_id"]: e["run_id"] for e in prov["candidates"]}


def write_verdicts() -> list[Path]:
    mapping = candidate_to_run_id()
    written = []
    for sid in SCENARIOS:
        src = ROOT / "blind-verdicts" / f"{sid}.blind.jsonl"
        dst = REPO / "verdicts" / sid / f"{SLUG}.verdicts.jsonl"
        dst.parent.mkdir(parents=True, exist_ok=True)
        rows = [json.loads(l) for l in src.read_text(encoding="utf-8").splitlines() if l.strip()]
        with dst.open("w", encoding="utf-8", newline="\n") as fh:
            for row in rows:
                cid = row.pop("candidate_id")
                fh.write(json.dumps({"run_id": mapping[cid], **row}, ensure_ascii=False) + "\n")
        print(f"  {sid}: {len(rows)} records -> {dst.relative_to(REPO).as_posix()}")
        written.append(dst)
    return written


def main() -> int:
    print("candidate -> run_id join:")
    write_verdicts()
    print()

    for sid in SCENARIOS:
        vf = (REPO / "verdicts" / sid / f"{SLUG}.verdicts.jsonl").as_posix()
        r = subprocess.run(
            [sys.executable, "-m", "mondaybench.cli", "evaluate",
             "--scenario", sid, "--model", SLUG, "--verdicts", vf,
             "--evaluator", EVALUATORS[sid], "--overwrite"],
            cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace")
        print(f"--- {sid} ---")
        print((r.stdout or "").strip()[-900:])
        if r.returncode != 0:
            print((r.stderr or "").strip()[-1500:])
            return r.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
