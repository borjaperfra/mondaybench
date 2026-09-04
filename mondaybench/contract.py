"""The judge contract: what a scenario's evaluation semantics actually are.

WHY THIS EXISTS. `judge.judge_prompt_fingerprint()` answers "did the repository
hold identical global schemas when these two evaluations were written?". That is
not the question a leaderboard needs. It needs "did these two evaluations use the
same scoring semantics APPLICABLE TO THIS SCENARIO?", and the two answers came
apart as soon as the suite grew:

`PENALTY_SCHEMA` embeds `PENALTY_TYPE_VALUES`, the shared penalty vocabulary.
That vocabulary gained types as scenarios were added - MAJOR_DATA_ERROR and
UNSUPPORTED_CAUSALITY with monday-004, CONFIDENTIALITY_BREACH with monday-005 -
so the fingerprint moved four times over the life of suite v1.0 and every model
judged after monday-005 is stamped differently from the incumbents on
monday-001..004, despite being judged against byte-identical rubrics. The full
diagnosis is in `audits/v1.1-migration/`.

WHAT THIS HASHES INSTEAD. A rendered contract containing only what applies to
one (scenario, rubric, evaluator) triple: the criteria in rubric order with
their definitions and points, the scenario's own penalties and their deductions,
its false actions, the ground-truth contract, the label semantics and the
tie-break rule, and the judge instruction texts - INCLUDING the external
`judge-prompt.md` and `penalty-judge-prompt.md` files that evaluators v0.2
onwards declare and that the legacy fingerprint never read.

WHAT THIS DELIBERATELY DOES NOT HASH. Timestamps, local paths, YAML comments,
and any criterion or penalty belonging to another scenario. Adding a monday-006
penalty type must leave monday-001..005 untouched; that is what makes a frozen
suite able to accept a new model at all.

THE GLOBAL ENUM IS REPLACED, NOT DROPPED. Dropping it would leave the
fingerprint blind to penalty semantics entirely - a change to monday-001's -5
hallucination deduction would not move the hash. `Rubric.penalties` is already
built per scenario by the loader, so the scenario's own penalty contract stays
hashed while the global union stops leaking in.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .config import EvaluatorConfig, judge_instruction_text, load_evaluator
from .judge import (
    CRITERION_SCHEMA,
    JUDGE_SYSTEM_PROMPT,
    NOISE_SCHEMA,
    PENALTY_SCHEMA,
)
from .prompt_builder import build_prompt
from .scenarios import Rubric, Scenario, load_scenario

# Bumped when the SHAPE of the contract object changes. A shape change moves
# every fingerprint, which is correct - it is a different claim - and is exactly
# why the version travels inside the hashed object.
CONTRACT_SCHEMA_VERSION = "1"

# The label vocabulary and the tie-break rule are semantics, not formatting, and
# they were previously buried inside a prompt template where no fingerprint
# could see them separately from the rest of the prose.
LABEL_SEMANTICS: dict[str, Any] = {
    "labels": ["PASS", "PARTIAL", "FAIL"],
    "tie_rule": "lower",
    "tie_rule_text": "If a response sits between two labels, choose the lower label.",
}


def canonical_json(obj: Any) -> str:
    """Stable serialisation. Key order, whitespace and unicode cannot move the hash."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def scenario_penalty_types(rubric: Rubric) -> list[str]:
    """The penalty types this scenario's rubric actually declares, sorted.

    A rubric names penalties in its own words; `scenarios.PENALTY_KEY_TO_TYPE`
    maps those onto the shared vocabulary, and `Rubric.penalties` is keyed by
    the shared type. So this is the scenario's operative set, not the union.
    """
    return sorted(rubric.penalties)


def scenario_penalty_schema(rubric: Rubric) -> dict[str, Any]:
    """`PENALTY_SCHEMA` with its enum narrowed to this scenario's penalties.

    On the API route the schema is sent as `response_format.json_schema`, so the
    enum is model-visible: with the global union, monday-001's judge is told it
    may return CONFIDENTIALITY_BREACH, a type monday-001's rubric does not
    define. It also disagreed with the prose - `evaluators/monday-004/
    penalty-judge-prompt.md` enumerates four types where the enum listed seven.
    """
    schema = json.loads(canonical_json(PENALTY_SCHEMA))
    schema["properties"]["violations"]["items"]["properties"]["type"]["enum"] = (
        scenario_penalty_types(rubric)
    )
    return schema


def _instruction(evaluator: EvaluatorConfig, scenario_id: str, which: str,
                 builtin_marker: str) -> dict[str, Any]:
    """Hash the instruction actually in force: the external file, or the built-in."""
    text = judge_instruction_text(evaluator, scenario_id, which)
    if text is not None:
        return {"source": "external", "sha256": _sha(text)}
    return {"source": "builtin", "sha256": _sha(builtin_marker)}


def judge_contract(scenario: Scenario, evaluator: EvaluatorConfig) -> dict[str, Any]:
    """The rendered evaluation semantics for one (scenario, rubric, evaluator).

    `scenario` must already be loaded against `evaluator.rubric_file`, which is
    what `contract_for` does. Passing a scenario loaded against a different
    rubric would describe a contract nobody used.
    """
    rubric = scenario.rubric
    gt_map = evaluator.ground_truth_map or {}

    criteria = [
        {
            "id": c.id,
            "dimension": c.dimension,
            "points": {
                "pass": c.points_pass,
                "partial": c.points_partial,
                "fail": c.points_fail,
            },
            "pass_definition": c.pass_definition,
            "partial_definition": c.partial_definition,
            "fail_definition": c.fail_definition,
            # Which slice of the answer key this criterion's judge call may see.
            # Changing it changes what the judge is allowed to know, so it is
            # semantics rather than plumbing.
            "ground_truth_paths": sorted(gt_map.get(c.id, [])),
        }
        # RUBRIC DECLARATION ORDER, not sorted. It is the order the recorded
        # judge reads the rubric in, and reordering a rubric is a rubric edit
        # that should move the hash.
        for c in rubric.criteria
    ]

    noise: dict[str, Any] | None = None
    if rubric.noise is not None:
        noise = {
            "max_points": rubric.noise.max_points,
            "starting_points": rubric.noise.starting_points,
            "deduction_per_false_action": rubric.noise.deduction_per_false_action,
            "minimum_points": rubric.noise.minimum_points,
            "false_actions": [
                {"id": a.id, "description": a.description}
                for a in rubric.noise.false_actions
            ],
        }

    # The ground truth is hashed rather than embedded: it is large, and what
    # matters is that it did not change. monday-003's `factual_anchors` live
    # inside it, so editing them moves this hash and moves nothing else.
    ground_truth_sha = _sha(
        canonical_json(scenario.ground_truth)
        if scenario.ground_truth
        else (scenario.ground_truth_text or "")
    )

    return {
        "contract_schema_version": CONTRACT_SCHEMA_VERSION,
        "scenario_id": scenario.id,
        # A different question is a different contract, even under one rubric.
        "scenario_prompt_sha256": build_prompt(scenario).sha256,
        "evaluator_id": evaluator.id,
        "judge_model_id": evaluator.model_id,
        "rubric_version": rubric.version,
        "rubric_file": evaluator.rubric_file,
        "ground_truth_sha256": ground_truth_sha,
        "ground_truth_sliced_per_criterion": bool(gt_map),
        "judge_instructions": {
            "system_prompt_sha256": _sha(JUDGE_SYSTEM_PROMPT),
            "criterion": _instruction(evaluator, scenario.id, "criterion",
                                      "builtin:criterion_prompt"),
            "penalty": _instruction(evaluator, scenario.id, "penalty",
                                    "builtin:penalty_prompt"),
            "noise": ({"source": "builtin", "sha256": _sha("builtin:noise_prompt")}
                      if noise else None),
        },
        "label_semantics": LABEL_SEMANTICS,
        "scoring": {
            "total_base_points": rubric.total_base_points,
            "maximum_global_penalty": rubric.maximum_global_penalty,
            "dimension_max": dict(sorted(rubric.dimension_max.items())),
        },
        "criteria": criteria,
        "noise": noise,
        "penalties": [
            {"type": t, "points": rubric.penalties[t].points,
             "definition": rubric.penalties[t].definition}
            for t in scenario_penalty_types(rubric)
        ],
        "output_contract": {
            "criterion_schema": CRITERION_SCHEMA,
            "noise_schema": NOISE_SCHEMA if noise else None,
            "penalty_schema": scenario_penalty_schema(rubric),
        },
    }


def judge_contract_fingerprint(contract: dict[str, Any]) -> str:
    """sha256 over the canonical contract, truncated to 16 hex characters."""
    return _sha(canonical_json(contract))[:16]


def contract_for(scenario_id: str, evaluator_id: str) -> tuple[dict[str, Any], str]:
    """Load what a scenario/evaluator pair means, and fingerprint it."""
    evaluator = load_evaluator(evaluator_id)
    scenario = load_scenario(scenario_id, rubric_file=evaluator.rubric_file)
    contract = judge_contract(scenario, evaluator)
    return contract, judge_contract_fingerprint(contract)


# --------------------------------------------------------------------------
# Explainability
#
# Opaque 16-character hashes are what turned a one-line defect into a full
# audit. `diff_contracts` is the reusable half of `explain-judge-contract`: it
# names the component that moved instead of leaving a reader to bisect it.
# --------------------------------------------------------------------------

# Compared as wholes rather than recursed into. A criteria array diff is
# reported as "criteria differ (19 vs 20, 0 shared ids)", which is the useful
# sentence; a per-key walk of 31 criteria is not.
_TOP_LEVEL = (
    "contract_schema_version", "scenario_id", "scenario_prompt_sha256",
    "evaluator_id", "judge_model_id", "rubric_version", "rubric_file",
    "ground_truth_sha256", "ground_truth_sliced_per_criterion",
    "judge_instructions", "label_semantics", "scoring", "criteria", "noise",
    "penalties", "output_contract",
)


def _summarise(component: str, value: Any) -> str:
    if component == "criteria":
        return f"{len(value)} criteria"
    if component == "penalties":
        return ", ".join(p["type"] for p in value) or "none"
    if component == "noise":
        return "absent" if value is None else f"{len(value['false_actions'])} false actions"
    if component == "judge_instructions":
        parts = []
        for key in ("criterion", "penalty"):
            block = value.get(key)
            if block:
                parts.append(f"{key}={block['source']}:{(block['sha256'] or '-')[:12]}")
        return " ".join(parts)
    if isinstance(value, dict):
        return canonical_json(value)[:80]
    return str(value)


def diff_contracts(a: dict[str, Any], b: dict[str, Any]) -> list[dict[str, str]]:
    """Which components of two contracts differ, and how."""
    out: list[dict[str, str]] = []
    for component in _TOP_LEVEL:
        left, right = a.get(component), b.get(component)
        if canonical_json(left) == canonical_json(right):
            continue
        entry = {
            "component": component,
            "left": _summarise(component, left),
            "right": _summarise(component, right),
        }
        if component == "criteria":
            ids_a = {c["id"] for c in left or []}
            ids_b = {c["id"] for c in right or []}
            shared = len(ids_a & ids_b)
            entry["detail"] = (
                f"{len(ids_a)} vs {len(ids_b)} criteria, {shared} shared ids"
                + (f", order or content changed for {shared} shared" if shared else "")
            )
        if component == "penalties":
            types_a = {p["type"] for p in left or []}
            types_b = {p["type"] for p in right or []}
            added = sorted(types_b - types_a)
            removed = sorted(types_a - types_b)
            bits = []
            if added:
                bits.append("+" + ",".join(added))
            if removed:
                bits.append("-" + ",".join(removed))
            if not bits:
                bits.append("same types, different points or definitions")
            entry["detail"] = " ".join(bits)
        out.append(entry)
    return out


def comparability_key(evaluation: Any) -> str:
    """The key a ranking may aggregate across. One per distinct judge contract.

    Prefers the contract fingerprint. Falls back to the legacy pair for v1.0
    evaluations, which carry no contract field and must keep behaving exactly as
    they did - a v1.0 board rebuilt today must reach the same verdict it reached
    when it was published.
    """
    contract = getattr(evaluation.judge, "contract_fingerprint", None)
    if contract:
        return f"contract={contract}"
    return (
        f"rubric={evaluation.rubric_version}/"
        f"judge={evaluation.judge.prompt_fingerprint}"
    )
