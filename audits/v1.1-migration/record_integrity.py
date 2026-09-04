"""Record the release-integrity state after the v1.1 migration. Reads only."""
from __future__ import annotations

import json
import statistics
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from mondaybench.suite import load_suite_manifest, verify_suite  # noqa: E402
from mondaybench.evaluator import find_evaluations, load_evaluation  # noqa: E402
from mondaybench.leaderboard import leaderboard_dir  # noqa: E402

SCENARIOS = ["monday-001", "monday-002", "monday-003", "monday-004", "monday-005"]
EVALUATORS = {
    "monday-001": "evaluator-opus5-v0.1", "monday-002": "evaluator-opus5-v0.2",
    "monday-003": "evaluator-opus5-v0.3", "monday-004": "evaluator-opus5-v0.4",
    "monday-005": "evaluator-opus5-v0.5",
}


def group_state(version):
    drift = verify_suite(version)
    return {name: {"policy": r.policy, "status": r.summary(),
                   "identical": r.identical, "ok": r.ok}
            for name, r in drift.items()}


def main() -> None:
    out = {
        "model_calls": 0,
        "judge_calls": 0,
        "candidate_regenerations": 0,
        "changed_historical_labels": 0,
        "releases": {},
        "v1_0_untouched": {},
        "glm5_3_operational": {},
    }

    for version in ("1.0", "1.1"):
        manifest = load_suite_manifest(version)
        groups = group_state(version)
        out["releases"][version] = {
            "released": manifest["released"],
            "suite_digest": manifest["suite_digest"],
            "file_count": manifest["file_count"],
            "verifies": all(g["ok"] for g in groups.values()),
            "groups": groups,
        }

    v10 = out["releases"]["1.0"]["groups"]
    out["v1_0_untouched"] = {
        "suite_digest": out["releases"]["1.0"]["suite_digest"],
        "expected_suite_digest": "c056b4b43d3caeb3b50394282b08ed281a5716fb1df68d1666abb950aa0b2a80",
        "digest_unchanged": (
            out["releases"]["1.0"]["suite_digest"]
            == "c056b4b43d3caeb3b50394282b08ed281a5716fb1df68d1666abb950aa0b2a80"
        ),
        "immutable_groups_identical": all(
            v10[g]["identical"] for g in ("scenarios", "evaluators", "taxonomy")
        ),
        "append_only_groups_gained_only": {
            g: v10[g]["status"] for g in ("runs", "verdicts", "evaluations",
                                          "leaderboards", "analysis")
        },
        "no_v1_0_evaluation_carries_a_contract_stamp": all(
            load_evaluation(p).judge.contract_fingerprint is None
            for sid, ev in EVALUATORS.items()
            for slug in sorted(
                d.name for d in (ROOT / "evaluations" / ev / sid).iterdir() if d.is_dir()
            )
            for p in find_evaluations(ev, sid, slug)
        ),
        "v1_0_boards_still_seven_models": {
            sid: sorted(
                row["model_slug"] for row in json.loads(
                    (leaderboard_dir(sid) / "leaderboard.json").read_text(encoding="utf-8")
                )["models"]
            )
            for sid in SCENARIOS
        },
    }

    # ---- GLM 5.3 operational data, with the units checked at source --------
    rows = []
    for sid in SCENARIOS:
        for p in sorted((ROOT / "runs" / sid / "glm5.3").glob("run-*.json")):
            d = json.loads(p.read_text(encoding="utf-8"))
            perf, usage = d.get("performance") or {}, d.get("usage") or {}
            rows.append({
                "ttft_ms": perf.get("ttft_ms"), "ttfa_ms": perf.get("ttfa_ms"),
                "total_ms": perf.get("total_latency_ms"),
                "output": usage.get("output_tokens"),
                "reasoning": usage.get("reasoning_tokens"),
            })
    med = lambda key: round(statistics.median([r[key] for r in rows if r[key] is not None]), 1)
    mean = lambda key: round(statistics.mean([r[key] for r in rows if r[key] is not None]), 1)
    out["glm5_3_operational"] = {
        "runs": len(rows),
        "stored_unit_check": (
            "runs/*/glm5.3/run-*.json stores performance in MILLISECONDS - the field names "
            "carry the unit (`ttft_ms`, `ttfa_ms`, `total_latency_ms`). Anything rendered in "
            "seconds is a conversion, and must be labelled as such."
        ),
        "median_ttft_ms": med("ttft_ms"),
        "median_ttft_s": round(med("ttft_ms") / 1000, 3),
        "median_ttfa_ms": med("ttfa_ms"),
        "median_ttfa_s": round(med("ttfa_ms") / 1000, 3),
        "median_total_latency_ms": med("total_ms"),
        "median_total_latency_s": round(med("total_ms") / 1000, 3),
        "mean_output_tokens": mean("output"),
        "mean_reasoning_tokens": mean("reasoning"),
        "reasoning_is_inside_output": True,
        "pricing": {
            "canonical_basis": "first-party, measured from Helmcode gateway usage.cost_details",
            "upstream": "Z.AI",
            "input_usd_per_million": 0.075,
            "output_usd_per_million": 0.25,
            "cost_per_task_usd": 0.005675,
            "cost_per_1k_tasks_usd": 5.67,
            "cost_per_100k_tasks_usd": 567.48,
            "cost_per_1m_tasks_usd": 5674.84,
            "alternative_route_disclosed_separately": {
                "upstream": "Parasail",
                "input_usd_per_million": 0.15,
                "output_usd_per_million": 0.50,
                "cost_per_task_usd": 0.01135,
                "note": ("One long-prompt observation. NOT merged into the canonical price: the "
                         "gateway fans glm5.3 out across upstream vendors and every "
                         "benchmark-size probe was served by Z.AI. Disclosed as a route-specific "
                         "alternative, per the existing pricing methodology."),
            },
            "per_run_cost_observable": False,
            "per_run_cost_note": ("The streaming response the runner uses carries neither "
                                  "`provider` nor `cost`; both appear only on non-streaming "
                                  "calls. Per-run cost is derived from measured rates and "
                                  "recorded token counts."),
        },
    }

    git = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                         capture_output=True, text=True)
    out["working_tree"] = {
        "tracked_modifications": sorted(
            line[3:] for line in git.stdout.splitlines() if line and not line.startswith("??")
        ),
    }

    (HERE / "release-integrity.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

    print("v1.0 digest unchanged:", out["v1_0_untouched"]["digest_unchanged"])
    print("v1.0 immutable groups identical:", out["v1_0_untouched"]["immutable_groups_identical"])
    print("v1.0 evaluations unstamped:",
          out["v1_0_untouched"]["no_v1_0_evaluation_carries_a_contract_stamp"])
    print("both releases verify:",
          all(out["releases"][v]["verifies"] for v in ("1.0", "1.1")))
    print("glm5.3 median TTFA:", out["glm5_3_operational"]["median_ttfa_ms"], "ms =",
          out["glm5_3_operational"]["median_ttfa_s"], "s")
    print("tracked modifications:", out["working_tree"]["tracked_modifications"])


if __name__ == "__main__":
    main()
