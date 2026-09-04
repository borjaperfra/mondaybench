"""READ-ONLY audit of what suite v1.1's integrity digest actually covers.

Answers one question: if someone edits an experimental audit or refreshes a
pricing analysis, does MondayBench v1.1 stop verifying - and should it?

Writes only release-scope-audit.json in this directory. Calls no model.
"""
from __future__ import annotations

import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from mondaybench.suite import GROUP_POLICY, load_suite_index  # noqa: E402

# What a released score cannot be reproduced without. Derived from the repo's
# own semantics rather than asserted: each entry names the claim it supports.
CORE_RATIONALE = {
    "scenarios": "the questions, their source fixtures, the rubrics and the ground truth",
    "evaluators": "the evaluator configs and the external judge prompts - the judge contract",
    "taxonomy": "the capability mapping, which is versioned and read by a published artifact",
    "runs": "the candidate generations a score was computed from",
    "verdicts": "the recorded judge output a score was replayed from",
    "evaluations": "the scored evaluations themselves",
    "leaderboards": "what was published",
    "config": "models.yaml and overall-releases.yaml decide what a slug and a release mean",
    "harness": "the code that produced all of it",
    "tests": "every integrity claim the manifest makes is enforced by one of these",
}
# Groups whose membership is worth questioning file by file.
MIXED = {"analysis", "docs"}


def tracked() -> set[str]:
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True)
    return {line.strip() for line in out.stdout.splitlines() if line.strip()}


def main() -> None:
    index = load_suite_index("1.1")
    index_10 = load_suite_index("1.0")
    is_tracked = tracked()

    report: dict = {
        "read_only": True,
        "question": ("Which files does suite v1.1's digest cover, and is each of them required "
                     "to reproduce an official MondayBench score?"),
        "groups": {},
        "analysis_breakdown": {},
        "docs_breakdown": {},
    }

    for group, files in index.items():
        report["groups"][group] = {
            "policy": GROUP_POLICY[group],
            "files": len(files),
            "in_v1_0_manifest": len(index_10.get(group, {})),
            "role": CORE_RATIONALE.get(group, "MIXED - see the per-file breakdown"),
        }

    # ---- what is actually inside analysis/ and docs/ -----------------------
    for group in MIXED:
        buckets: dict[str, dict] = defaultdict(
            lambda: {"files": 0, "tracked": 0, "untracked": 0, "in_v1_0": 0, "examples": []}
        )
        for path in sorted(index.get(group, {})):
            # first two path segments identify the workstream
            parts = path.split("/")
            key = "/".join(parts[:2]) if len(parts) > 1 else parts[0]
            b = buckets[key]
            b["files"] += 1
            b["tracked" if path in is_tracked else "untracked"] += 1
            if path in index_10.get(group, {}):
                b["in_v1_0"] += 1
            if len(b["examples"]) < 3:
                b["examples"].append(path)
        report[f"{group}_breakdown"] = {
            k: v for k, v in sorted(buckets.items(), key=lambda kv: -kv[1]["files"])
        }

    # ---- the specific directories the migration report flagged -------------
    flagged = [
        "analysis/cost-value", "audits/blind-rejudge", "audits/capabilities",
        "audits/monday-opus5", "audits/pricing", "audits/glm-5.3",
        "audits/v1.1-migration", "audits/monday-002",
    ]
    detail = {}
    for prefix in flagged:
        group = "analysis" if prefix.startswith("analysis/") else "docs"
        covered = sorted(p for p in index.get(group, {}) if p.startswith(prefix + "/"))
        detail[prefix] = {
            "group": group,
            "policy": GROUP_POLICY[group],
            "files_in_v1_1_digest": len(covered),
            "files_in_v1_0_digest": sum(
                1 for p in covered if p in index_10.get(group, {})
            ),
            "tracked_in_git": sum(1 for p in covered if p in is_tracked),
            "untracked_in_git": sum(1 for p in covered if p not in is_tracked),
            "editing_one_breaks_v1_1": GROUP_POLICY[group] == "append_only" and bool(covered),
            "required_to_reproduce_a_score": False,
        }
    report["flagged_directories"] = detail

    report["finding"] = {
        "analysis_policy": GROUP_POLICY["analysis"],
        "docs_policy": GROUP_POLICY["docs"],
        "why_it_matters": (
            "`analysis` is append_only: every file it pins must stay byte-identical. "
            "`docs` is mutable: editing one is reported and is not a failure. So an edit "
            "under audits/ never breaks a release, but an edit under analysis/ does - "
            "including to pricing research that no official score depends on."
        ),
        "analysis_files_required_by_a_published_artifact": [
            p for p in index.get("analysis", {})
            if p.startswith("analysis/capability-profiles")
            or p == "analysis/serving-qualification.json"
        ],
    }

    (HERE / "release-scope-audit.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8", newline="\n")

    print("group            policy        v1.1  v1.0  role")
    for group, g in report["groups"].items():
        print(f"{group:<16} {g['policy']:<12} {g['files']:>5} {g['in_v1_0_manifest']:>5}  "
              f"{g['role'][:52]}")
    print("\nanalysis/ breakdown:")
    for key, b in report["analysis_breakdown"].items():
        print(f"  {key:<38} {b['files']:>4} files  tracked {b['tracked']:>3}  "
              f"untracked {b['untracked']:>3}  in v1.0 {b['in_v1_0']:>3}")
    print("\nflagged directories:")
    for prefix, d in detail.items():
        print(f"  {prefix:<28} {d['group']:<9} {d['policy']:<12} "
              f"v1.1 {d['files_in_v1_1_digest']:>3}  v1.0 {d['files_in_v1_0_digest']:>3}  "
              f"breaks-v1.1-if-edited {d['editing_one_breaks_v1_1']}")


if __name__ == "__main__":
    main()
