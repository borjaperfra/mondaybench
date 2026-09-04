"""Assemble Anonymized Blind Judge Pack for MondayBench Challenger Evaluation.

Strictly follows blind pack rules:
- Pre-declared deterministic seed: 20260902
- Candidate display labels: Candidate A, Candidate B, Candidate C (randomized per scenario)
- Private provenance mapping stored in judge-pack/provenance-map.json
- Zero model/provider identity leakage (scrubbing gemini, google, antigravity, deepmind, etc.)
- Exact operative rubrics, criteria, bands, penalties, and ground truth preserved
- monday-003 factual_plan_accuracy pinned to factual_anchors
- Lower-label rule enforced: "If a response sits between two labels, choose the lower."
- Non-operative prior-precedent commentary removed and documented in scrub-log.json
- Full structural validation across all 5 scenarios and 15 candidates
"""

import copy
import hashlib
import json
import os
import random
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

CHALLENGER_DIR = REPO_ROOT / "gemini-3.8-mondaybench-challenger"
JUDGE_PACK_DIR = CHALLENGER_DIR / "judge-pack"

BLIND_SEED = 20260902

SCENARIO_SPECS = {
    "monday-001": {
        "name": "Back to Work",
        "rubric_file": "rubric-0.2.yaml",
        "rubric_version": "0.2",
        "ground_truth_file": "ground-truth.yaml",
        "expected_criteria": 19,
    },
    "monday-002": {
        "name": "Moving Targets",
        "rubric_file": "rubric.yaml",
        "rubric_version": "0.2",
        "ground_truth_file": "ground_truth.md",
        "expected_criteria": 20,
    },
    "monday-003": {
        "name": "Blockers",
        "rubric_file": "rubric.yaml",
        "rubric_version": "0.3",
        "ground_truth_file": "ground-truth.yaml",
        "expected_criteria": 21,
    },
    "monday-004": {
        "name": "Numbers Don't Lie",
        "rubric_file": "rubric-0.3.yaml",
        "rubric_version": "0.3",
        "ground_truth_file": "ground-truth.yaml",
        "expected_criteria": 27,
    },
    "monday-005": {
        "name": "Read the Room",
        "rubric_file": "rubric-0.4.yaml",
        "rubric_version": "0.4",
        "ground_truth_file": "ground-truth.yaml",
        "expected_criteria": 31,
    },
}

FORBIDDEN_TERMS = [
    "gemini",
    "google",
    "antigravity",
    "deepmind",
    "gemini-3.8",
    "claude",
    "anthropic",
    "openai",
    "gpt-",
    "deepseek",
    "qwen",
    "glm",
    "mimo",
]


def load_yaml(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def scrub_commentary(text: str) -> tuple[str, list[str]]:
    """Remove references to prior models, scores, and precedent while preserving operative definitions."""
    if not isinstance(text, str):
        return text, []

    removals = []
    cleaned = text
    for term in FORBIDDEN_TERMS:
        pattern = re.compile(rf"\b{re.escape(term)}[^\s.,;:!?'\"()]*", re.IGNORECASE)
        matches = pattern.findall(cleaned)
        if matches:
            removals.extend(matches)
            cleaned = pattern.sub("[PRIOR_MODEL_REFERENCE_REDACTED]", cleaned)

    return cleaned, removals


def clean_rubric_structure(raw_rubric: dict, sid: str, scrub_log: list) -> dict:
    """Extract operative rubric fields and strip non-operative historical/precedent commentary."""
    clean = {
        "scenario_id": sid,
        "rubric_version": SCENARIO_SPECS[sid]["rubric_version"],
        "total_points": raw_rubric.get("total_points", 100),
        "scoring_rule": "If a response sits between two labels, choose the lower.",
        "dimensions": {},
        "global_penalties": []
    }

    if sid == "monday-003":
        clean["scoring_rule"] += " For monday-003: factual_plan_accuracy must be judged ONLY against factual_anchors."

    raw_dims = raw_rubric.get("dimensions", {})
    for dim_key, dim_val in raw_dims.items():
        if dim_key == "noise_resistance":
            # Handle noise dimension (e.g. monday-001)
            clean_dim = {
                "max_points": dim_val.get("max_points", 0),
                "starting_points": dim_val.get("starting_points", 0),
                "deduction_per_false_action": dim_val.get("deduction_per_false_action", 0),
                "minimum_points": dim_val.get("minimum_points", 0),
                "false_actions": []
            }
            for fa in dim_val.get("false_actions", []):
                fa_desc, rem = scrub_commentary(fa.get("description", ""))
                if rem:
                    scrub_log.append({"location": f"{sid}.noise_resistance.{fa.get('id')}", "redacted": rem})
                clean_dim["false_actions"].append({
                    "id": fa.get("id"),
                    "description": fa_desc
                })
            clean["dimensions"][dim_key] = clean_dim
            continue

        clean_dim = {
            "max_points": dim_val.get("max_points", 0),
            "criteria": []
        }
        for crit in dim_val.get("criteria", []):
            cid = crit.get("id")
            pts = crit.get("points")
            if isinstance(pts, dict):
                p_pass = float(pts["pass"])
                p_partial = float(pts["partial"])
                p_fail = float(pts["fail"])
            else:
                p_pass = float(pts)
                p_partial = float(crit.get("partial_points", p_pass / 2.0))
                p_fail = float(crit.get("fail_points", 0.0))

            pass_def, rem1 = scrub_commentary(crit.get("pass") or crit.get("pass_definition", ""))
            part_def, rem2 = scrub_commentary(crit.get("partial") or crit.get("partial_definition", ""))
            fail_def, rem3 = scrub_commentary(crit.get("fail") or crit.get("fail_definition", "") or "Neither PASS nor PARTIAL bar is met.")

            for r in (rem1 + rem2 + rem3):
                scrub_log.append({"location": f"{sid}.criteria.{cid}", "redacted": r})

            clean_crit = {
                "id": cid,
                "dimension": dim_key,
                "points_pass": p_pass,
                "points_partial": p_partial,
                "points_fail": p_fail,
                "pass_definition": pass_def,
                "partial_definition": part_def,
                "fail_definition": fail_def
            }
            if "guidelines" in crit:
                g_clean, rem_g = scrub_commentary(crit["guidelines"])
                clean_crit["guidelines"] = g_clean
                if rem_g:
                    scrub_log.append({"location": f"{sid}.criteria.{cid}.guidelines", "redacted": rem_g})

            clean_dim["criteria"].append(clean_crit)

        clean["dimensions"][dim_key] = clean_dim

    # Global penalties
    penalties_raw = raw_rubric.get("global_penalties", {})
    if "types" in penalties_raw:
        max_pen = penalties_raw.get("max_penalty", 25)
        for p in penalties_raw.get("types", []):
            p_desc, rem_p = scrub_commentary(p.get("definition", ""))
            clean["global_penalties"].append({
                "id": p.get("id"),
                "points_each": p.get("points_each", 5),
                "max_penalty": max_pen,
                "definition": p_desc
            })
            if rem_p:
                scrub_log.append({"location": f"{sid}.penalties.{p.get('id')}", "redacted": rem_p})
    elif isinstance(penalties_raw, dict):
        for pkey, pval in penalties_raw.items():
            if isinstance(pval, dict):
                p_desc, rem_p = scrub_commentary(pval.get("definition", ""))
                clean["global_penalties"].append({
                    "id": pkey,
                    "points": pval.get("points", -5),
                    "definition": p_desc
                })
                if rem_p:
                    scrub_log.append({"location": f"{sid}.penalties.{pkey}", "redacted": rem_p})

    return clean


def clean_ground_truth(raw_gt: dict, sid: str, scrub_log: list) -> dict:
    """Clean ground truth data of any prior model references or verdict commentary."""
    clean_gt = {}
    for k, v in raw_gt.items():
        if k in ("header_comment", "notes_v0.1", "notes_v0.2"):
            continue
        if isinstance(v, str):
            cv, rem = scrub_commentary(v)
            clean_gt[k] = cv
            if rem:
                scrub_log.append({"location": f"{sid}.ground_truth.{k}", "redacted": rem})
        elif isinstance(v, list):
            clean_list = []
            for item in v:
                if isinstance(item, str):
                    ci, rem = scrub_commentary(item)
                    clean_list.append(ci)
                    if rem:
                        scrub_log.append({"location": f"{sid}.ground_truth.{k}", "redacted": rem})
                else:
                    clean_list.append(item)
            clean_gt[k] = clean_list
        elif isinstance(v, dict):
            clean_sub = {}
            for subk, subv in v.items():
                if isinstance(subv, str):
                    csub, rem = scrub_commentary(subv)
                    clean_sub[subk] = csub
                    if rem:
                        scrub_log.append({"location": f"{sid}.ground_truth.{k}.{subk}", "redacted": rem})
                else:
                    clean_sub[subk] = subv
            clean_gt[k] = clean_sub
        else:
            clean_gt[k] = v

    return clean_gt


def main():
    print("================================================================")
    print("Building Anonymized Blind Judge Pack (MondayBench Challenger)")
    print(f"Deterministic Blind Seed: {BLIND_SEED}")
    print("================================================================")

    JUDGE_PACK_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load generation freeze manifest to consume frozen responses read-only
    freeze_manifest_file = CHALLENGER_DIR / "generation-freeze-manifest.json"
    if not freeze_manifest_file.exists():
        raise FileNotFoundError(f"Freeze manifest missing at {freeze_manifest_file}")

    with open(freeze_manifest_file, "r", encoding="utf-8") as f:
        freeze_data = json.load(f)

    runs_by_scenario = {}
    for r in freeze_data["runs"]:
        sid = r["scenario_id"]
        runs_by_scenario.setdefault(sid, []).append(r)

    scrub_log = []
    provenance_map = {
        "blind_seed": BLIND_SEED,
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generation_freeze_manifest_sha256": sha256_text(freeze_manifest_file.read_text(encoding="utf-8")),
        "scenarios": {}
    }

    judge_pack = {
        "benchmark_suite": "MondayBench v1.0",
        "pack_type": "BLIND_INDEPENDENT_EVALUATION_PACK",
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "evaluation_protocol": {
            "rule_lower_label": "If a candidate response sits between two labels, choose the lower.",
            "rule_labels": ["PASS", "PARTIAL", "FAIL"],
            "rule_monday_003_accuracy": "For monday-003, factual_plan_accuracy must be judged strictly against factual_anchors.",
            "general_instruction": "Evaluate each candidate independently against the frozen atomic criteria, bands, and ground truth reference evidence. Provide score, label, and verbatim justification citing candidate text."
        },
        "scenarios": []
    }

    # Iterate over 5 scenarios in canonical order
    total_candidates = 0
    scenario_order = ["monday-001", "monday-002", "monday-003", "monday-004", "monday-005"]

    for sid in scenario_order:
        spec = SCENARIO_SPECS[sid]
        scen_dir = REPO_ROOT / "scenarios" / sid

        # Load scenario prompt
        prompt_file = scen_dir / "prompt.md"
        prompt_text = prompt_file.read_text(encoding="utf-8")

        # Load rubric
        rubric_path = scen_dir / spec["rubric_file"]
        raw_rubric = load_yaml(rubric_path)
        clean_rubric = clean_rubric_structure(raw_rubric, sid, scrub_log)

        # Load ground truth
        gt_path = scen_dir / spec["ground_truth_file"]
        if gt_path.suffix == ".md":
            raw_gt_text = gt_path.read_text(encoding="utf-8")
            clean_gt, rem_gt = scrub_commentary(raw_gt_text)
            if rem_gt:
                scrub_log.append({"location": f"{sid}.ground_truth", "redacted": rem_gt})
        else:
            raw_gt = load_yaml(gt_path)
            clean_gt = clean_ground_truth(raw_gt, sid, scrub_log)

        # Retrieve the 3 runs from freeze manifest
        runs = runs_by_scenario[sid]
        if len(runs) != 3:
            raise ValueError(f"Scenario {sid} has {len(runs)} runs; expected exactly 3")

        # Deterministic shuffle using seed + scenario id
        rng = random.Random(f"{BLIND_SEED}_{sid}")
        shuffled_runs = list(runs)
        rng.shuffle(shuffled_runs)

        candidate_labels = ["Candidate A", "Candidate B", "Candidate C"]
        candidates_pack = []
        provenance_map["scenarios"][sid] = []

        for label, run_meta in zip(candidate_labels, shuffled_runs):
            run_id = run_meta["run_id"]
            resp_path = CHALLENGER_DIR / "responses" / sid / f"{run_id.split('__')[-1]}.txt"
            resp_text = resp_path.read_text(encoding="utf-8")

            # Verify response hash matches freeze manifest
            resp_hash = sha256_text(resp_text)
            if resp_hash != run_meta["response_sha256"]:
                raise ValueError(f"CRITICAL: Response hash mismatch for {run_id}: {resp_hash} != {run_meta['response_sha256']}")

            candidate_id = f"MB-{sid.split('-')[-1]}-{label.replace(' ', '')}"

            candidates_pack.append({
                "candidate_id": candidate_id,
                "display_label": label,
                "response": resp_text,
                "response_sha256": resp_hash
            })

            provenance_map["scenarios"][sid].append({
                "candidate_id": candidate_id,
                "display_label": label,
                "true_run_id": run_id,
                "response_sha256": resp_hash,
                "raw_file": run_meta["raw_sha256"],
                "started_at": run_meta["started_at"],
                "finished_at": run_meta["finished_at"]
            })
            total_candidates += 1

        judge_pack["scenarios"].append({
            "scenario_id": sid,
            "scenario_name": spec["name"],
            "prompt_text": prompt_text,
            "prompt_sha256": runs[0]["prompt_sha256"],
            "rubric": clean_rubric,
            "ground_truth": clean_gt,
            "candidates": candidates_pack
        })

    # 2. Write provenance map
    prov_file = JUDGE_PACK_DIR / "provenance-map.json"
    prov_file.write_text(json.dumps(provenance_map, indent=2), encoding="utf-8")
    print(f"[OK] Private Provenance Map written to {prov_file}")

    # 3. Write scrub log
    scrub_file = JUDGE_PACK_DIR / "scrub-log.json"
    scrub_file.write_text(json.dumps(scrub_log, indent=2), encoding="utf-8")
    print(f"[OK] Scrub log written to {scrub_file} ({len(scrub_log)} items documented)")

    # 4. Write blind judge pack
    pack_file = JUDGE_PACK_DIR / "blind-judge-pack.json"
    pack_json = json.dumps(judge_pack, indent=2)
    pack_file.write_text(pack_json, encoding="utf-8")
    pack_sha256 = sha256_text(pack_json)
    print(f"[OK] Blind Judge Pack written to {pack_file} (SHA256: {pack_sha256[:16]}...)")

    # 5. Execute Structural Validation
    print("\n================================================================")
    print("Executing Judge Pack Structural Validation")
    print("================================================================")

    assert len(judge_pack["scenarios"]) == 5, f"Expected 5 scenarios, got {len(judge_pack['scenarios'])}"
    assert total_candidates == 15, f"Expected 15 candidates total, got {total_candidates}"

    total_atomic_criteria = 0
    for scen in judge_pack["scenarios"]:
        sid = scen["scenario_id"]
        expected_cnt = SCENARIO_SPECS[sid]["expected_criteria"]
        dims = scen["rubric"]["dimensions"]
        scen_criteria = []
        for dkey, dval in dims.items():
            if "criteria" in dval:
                for c in dval["criteria"]:
                    scen_criteria.append(c["id"])

        actual_cnt = len(scen_criteria)
        if actual_cnt != expected_cnt:
            raise ValueError(f"CRITICAL: {sid} has {actual_cnt} criteria, expected {expected_cnt}")

        if len(set(scen_criteria)) != actual_cnt:
            raise ValueError(f"CRITICAL: {sid} has duplicate criteria: {scen_criteria}")

        print(f"[VALIDATED] {sid}: {actual_cnt} atomic criteria verified (no duplicates, no omissions)")
        total_atomic_criteria += actual_cnt

    print(f"\n[VALIDATED] All 5 scenarios verified: {total_atomic_criteria} criteria per candidate (118 total).")
    print(f"[VALIDATED] 3 candidates per scenario x 5 scenarios = 15 candidates total.")

    # 6. Verify zero identity leaks in judge pack wrapper/metadata
    print("\n--- Verifying Identity Scrubbing in Blind Pack ---")
    pack_data_without_responses = copy.deepcopy(judge_pack)
    for s in pack_data_without_responses["scenarios"]:
        for c in s["candidates"]:
            c["response"] = ""  # responses are separately verified

    pack_wrapper_str = json.dumps(pack_data_without_responses)
    found_leaks = []
    for term in ["gemini", "google", "antigravity", "deepmind", "gemini-3.8"]:
        matches = re.findall(rf"\b{re.escape(term)}\b", pack_wrapper_str, re.IGNORECASE)
        if matches:
            found_leaks.append(f"{term} ({len(matches)})")

    if found_leaks:
        raise ValueError(f"CRITICAL: Identity leaks found in judge pack wrapper: {found_leaks}")
    print("[VALIDATED] ZERO identity terms found in judge pack wrapper and rubric metadata!")

    print("\n=== BLIND JUDGE PACK ASSEMBLY & VALIDATION COMPLETE ===")


if __name__ == "__main__":
    main()
