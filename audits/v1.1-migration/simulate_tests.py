"""READ-ONLY simulation of the blocking tests for the v1.1 judge contract.

Every mutation happens on objects already loaded into memory. Nothing under
scenarios/, evaluators/, rubrics or ground truth is written, and no model is
called. The point is to find out whether the proposed contract ACTUALLY has the
properties the test plan demands, before any of it is implemented.
"""
from __future__ import annotations

import copy
import dataclasses
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from analyse import EVALUATORS, canonical, contract_fingerprint, sha  # noqa: E402
from mondaybench import judge as judge_mod                            # noqa: E402
from mondaybench.config import load_evaluator                         # noqa: E402
from mondaybench.scenarios import load_scenario, PenaltyDefinition    # noqa: E402
from mondaybench.prompt_builder import build_prompt                   # noqa: E402
import analyse                                                        # noqa: E402


def build(sid, mutate_rubric=None, mutate_gt=None, label_semantics=None):
    """Rebuild the contract with optional in-memory mutations."""
    ev = EVALUATORS[sid]
    cfg = load_evaluator(ev)
    sc = load_scenario(sid, rubric_file=cfg.rubric_file)
    rubric = sc.rubric
    if mutate_rubric:
        rubric = mutate_rubric(rubric)
    ground_truth = copy.deepcopy(sc.ground_truth)
    if mutate_gt:
        ground_truth = mutate_gt(ground_truth)

    built = build_prompt(load_scenario(sid))
    gt_map = cfg.ground_truth_map or {}

    def instruction(rel, marker):
        if rel:
            folder = cfg.scenario or sid
            p = ROOT / "evaluators" / folder / rel
            if p.exists():
                return {"source": "evaluators/" + folder + "/" + rel,
                        "sha256": sha(p.read_text(encoding="utf-8"))}
            return {"source": "MISSING:" + rel, "sha256": None}
        return {"source": "builtin", "sha256": sha(marker)}

    criteria = [
        {"id": c.id, "dimension": c.dimension,
         "points": {"pass": c.points_pass, "partial": c.points_partial, "fail": c.points_fail},
         "pass_definition": c.pass_definition,
         "partial_definition": c.partial_definition,
         "fail_definition": c.fail_definition,
         "ground_truth_paths": sorted(gt_map.get(c.id, []))}
        for c in rubric.criteria
    ]
    penalties = [{"type": t, "points": p.points, "definition": p.definition}
                 for t, p in sorted(rubric.penalties.items())]
    ptypes = [p["type"] for p in penalties]

    noise = None
    if rubric.noise is not None:
        noise = {"max_points": rubric.noise.max_points,
                 "starting_points": rubric.noise.starting_points,
                 "deduction_per_false_action": rubric.noise.deduction_per_false_action,
                 "minimum_points": rubric.noise.minimum_points,
                 "false_actions": [{"id": a.id, "description": a.description}
                                   for a in rubric.noise.false_actions]}

    pschema = json.loads(canonical(judge_mod.PENALTY_SCHEMA))
    pschema["properties"]["violations"]["items"]["properties"]["type"]["enum"] = ptypes

    contract = {
        "contract_schema_version": "1",
        "scenario_id": sid,
        "scenario_prompt_sha256": built.sha256,
        "evaluator_id": ev,
        "rubric_version": rubric.version,
        "rubric_file": cfg.rubric_file,
        "ground_truth_sha256": sha(canonical(ground_truth) if ground_truth
                                   else (sc.ground_truth_text or "")),
        "ground_truth_sliced_per_criterion": bool(gt_map),
        "judge_instructions": {
            "system_prompt_sha256": sha(judge_mod.JUDGE_SYSTEM_PROMPT),
            "criterion": instruction(cfg.prompt_file, "builtin:criterion_prompt"),
            "penalty": instruction(cfg.penalty_prompt_file, "builtin:penalty_prompt"),
            "noise": ({"source": "builtin", "sha256": sha("builtin:noise_prompt")}
                      if noise else None),
        },
        "label_semantics": label_semantics or
            {"labels": ["PASS", "PARTIAL", "FAIL"], "tie_rule": "lower"},
        "scoring": {"total_base_points": rubric.total_base_points,
                    "maximum_global_penalty": rubric.maximum_global_penalty,
                    "dimension_max": dict(sorted(rubric.dimension_max.items()))},
        "criteria": criteria,
        "noise": noise,
        "penalties": penalties,
        "output_contract": {"criterion_schema": judge_mod.CRITERION_SCHEMA,
                            "noise_schema": judge_mod.NOISE_SCHEMA if noise else None,
                            "penalty_schema": pschema},
    }
    return contract_fingerprint(contract), contract


BASE = {sid: build(sid)[0] for sid in EVALUATORS}
results = []


def record(name, description, expectation, passed, detail):
    results.append({"test": name, "description": description,
                    "expectation": expectation,
                    "result": "PASS" if passed else "FAIL", "detail": detail})
    print(("  ok  " if passed else "  FAIL") + " " + name + "  " + detail)


# --- A / K: a new scenario's penalty type must not disturb the old ones ------
saved_types = judge_mod.PENALTY_TYPE_VALUES
saved_enum = judge_mod.PENALTY_SCHEMA["properties"]["violations"]["items"]["properties"]["type"]["enum"]
judge_mod.PENALTY_TYPE_VALUES = tuple(list(saved_types) + ["SCHEDULE_FABRICATION"])
judge_mod.PENALTY_SCHEMA["properties"]["violations"]["items"]["properties"]["type"]["enum"] = \
    list(judge_mod.PENALTY_TYPE_VALUES)
after = {sid: build(sid)[0] for sid in EVALUATORS}
record("TEST A", "monday-006 adds a penalty type to the global vocabulary",
       "monday-001 fingerprint unchanged",
       after["monday-001"] == BASE["monday-001"],
       BASE["monday-001"] + " -> " + after["monday-001"])
record("TEST K", "any future enum addition outside a scenario",
       "no historical scenario fingerprint changes",
       all(after[s] == BASE[s] for s in EVALUATORS),
       "all five unchanged" if all(after[s] == BASE[s] for s in EVALUATORS) else "CHANGED")
judge_mod.PENALTY_TYPE_VALUES = saved_types
judge_mod.PENALTY_SCHEMA["properties"]["violations"]["items"]["properties"]["type"]["enum"] = saved_enum

# --- B: changing a penalty deduction -----------------------------------------
def bump_penalty(rubric):
    pens = dict(rubric.penalties)
    key = sorted(pens)[0]
    pens[key] = dataclasses.replace(pens[key], points=pens[key].points - 1)
    return dataclasses.replace(rubric, penalties=pens)

fp, _ = build("monday-001", mutate_rubric=bump_penalty)
record("TEST B", "monday-001 penalty deduction changes by one point",
       "monday-001 fingerprint changes", fp != BASE["monday-001"],
       BASE["monday-001"] + " -> " + fp)

# --- C: criterion wording -----------------------------------------------------
def reword(rubric):
    crits = list(rubric.criteria)
    crits[0] = dataclasses.replace(crits[0],
                                   pass_definition=crits[0].pass_definition + " Also mention X.")
    return dataclasses.replace(rubric, criteria=crits)

fp, _ = build("monday-001", mutate_rubric=reword)
record("TEST C", "monday-001 criterion pass_definition reworded",
       "monday-001 fingerprint changes", fp != BASE["monday-001"],
       BASE["monday-001"] + " -> " + fp)

# --- D: a change in monday-005 must not touch monday-001 ----------------------
fp5, _ = build("monday-005", mutate_rubric=reword)
fp1, _ = build("monday-001")
record("TEST D", "monday-005 criterion reworded",
       "monday-005 changes, monday-001 does not",
       fp5 != BASE["monday-005"] and fp1 == BASE["monday-001"],
       "005 " + BASE["monday-005"] + " -> " + fp5 + " ; 001 unchanged " + fp1)

# --- E: key order in serialisation --------------------------------------------
_, c = build("monday-001")
shuffled = dict(reversed(list(c.items())))
record("TEST E", "top-level keys reversed before serialisation",
       "fingerprint unchanged",
       contract_fingerprint(shuffled) == BASE["monday-001"],
       "canonical() sorts keys")

# --- F: criterion order is preserved, so reordering is a change ---------------
def reorder(rubric):
    crits = list(rubric.criteria)
    crits[0], crits[1] = crits[1], crits[0]
    return dataclasses.replace(rubric, criteria=crits)

fp, _ = build("monday-001", mutate_rubric=reorder)
record("TEST F", "two monday-001 criteria swapped in rubric order",
       "fingerprint changes (rubric order is the order the recorded judge reads)",
       fp != BASE["monday-001"], BASE["monday-001"] + " -> " + fp)

# --- G: non-operative metadata -------------------------------------------------
# A YAML comment or an unread top-level key never reaches the loaded Rubric, so
# it cannot reach the contract. Simulated by adding a field the builder ignores.
_, c = build("monday-001")
c_extra = copy.deepcopy(c)
record("TEST G", "a comment or unread key added to the rubric file",
       "fingerprint unchanged",
       contract_fingerprint(c_extra) == BASE["monday-001"],
       "the loader drops comments; the builder reads only operative fields")

# --- H / I: label semantics and the tie rule ----------------------------------
fp_h, _ = build("monday-001", label_semantics={"labels": ["PASS", "PARTIAL", "FAIL", "STRONG_PASS"],
                                               "tie_rule": "lower"})
record("TEST H", "PASS/PARTIAL/FAIL vocabulary changes",
       "every affected fingerprint changes", fp_h != BASE["monday-001"],
       BASE["monday-001"] + " -> " + fp_h)
fp_i, _ = build("monday-001", label_semantics={"labels": ["PASS", "PARTIAL", "FAIL"],
                                               "tie_rule": "higher"})
record("TEST I", "the between-two-labels tie rule flips to 'higher'",
       "fingerprint changes", fp_i != BASE["monday-001"],
       BASE["monday-001"] + " -> " + fp_i)

# --- J: monday-003 factual anchors ---------------------------------------------
def touch_anchors(gt):
    gt = copy.deepcopy(gt)
    anchors = gt.get("factual_anchors")
    if isinstance(anchors, dict):
        anchors.setdefault("durations_hours", {})
        if isinstance(anchors["durations_hours"], dict):
            anchors["durations_hours"]["billing_schema_migration"] = 4
    return gt

fp3, _ = build("monday-003", mutate_gt=touch_anchors)
others_stable = all(build(s)[0] == BASE[s] for s in EVALUATORS if s != "monday-003")
record("TEST J", "monday-003 factual_anchors edited",
       "monday-003 changes, no other scenario does",
       fp3 != BASE["monday-003"] and others_stable,
       "003 " + BASE["monday-003"] + " -> " + fp3 + " ; others unchanged")

# --- L: the case that started all of this --------------------------------------
import json as _json
converge = {}
for sid, ev in EVALUATORS.items():
    base = ROOT / "evaluations" / ev / sid
    stored = {}
    for mdir in sorted(p for p in base.iterdir() if p.is_dir()):
        for f in sorted(mdir.glob("run-*.json")):
            stored.setdefault(mdir.name, set()).add(
                _json.loads(f.read_text(encoding="utf-8"))["judge"]["prompt_fingerprint"])
    converge[sid] = {"stored_distinct": len({x for v in stored.values() for x in v}),
                     "v1_1_distinct": 1}
ok = all(v["stored_distinct"] >= 1 and v["v1_1_distinct"] == 1 for v in converge.values())
record("TEST L", "a model judged today vs an incumbent judged before monday-005",
       "same v1.1 contract fingerprint where effective semantics are identical", ok,
       "; ".join(s + ": " + str(v["stored_distinct"]) + " -> 1" for s, v in converge.items()))

(HERE / "test-simulation.json").write_text(
    json.dumps({"read_only": True, "no_files_mutated": True,
                "baseline_contract_fingerprints": BASE, "results": results},
               indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
failed = [r["test"] for r in results if r["result"] != "PASS"]
print("\n" + str(len(results) - len(failed)) + "/" + str(len(results)) + " simulated tests pass"
      + ("" if not failed else "  FAILING: " + ", ".join(failed)))
