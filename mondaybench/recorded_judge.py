"""A judge whose verdicts are read from a file instead of a model call.

Two uses:

1. **Manual audit.** IMPLEMENTATION.md s33 requires a human to inspect every
   criterion label for the calibration runs. This turns that audit into the
   artifact it should be: a reviewer fills in a worksheet, and the same
   deterministic scoring code produces the score.

2. **No judge credentials.** The scoring pipeline runs end to end with zero API
   spend, which makes calibration possible before committing to a judge model.

A recorded evaluation is a real evaluation - the labels came from a reviewer
rather than a model - but it is **not** interchangeable with a model-judged one.
It therefore carries its own evaluator id (`evaluator-manual-v0.1`), and the
spec's rule against mixing evaluator versions in one ranking does the rest.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import EvaluatorConfig
from .judge import Judge, JudgeCallStats, JudgeError
from .scenarios import Criterion, FalseAction, Rubric
from .schemas import PENALTY_TYPE_VALUES, CriterionVerdict, NoiseVerdict, PenaltyVerdict

VALID_LABELS = {"PASS", "PARTIAL", "FAIL"}


class VerdictStore:
    """Verdicts loaded from a JSONL file, indexed by run id."""

    def __init__(self) -> None:
        self.criteria: dict[tuple[str, str], dict[str, Any]] = {}
        self.noise: dict[str, list[dict[str, Any]]] = {}
        self.penalties: dict[str, list[dict[str, Any]]] = {}

    @classmethod
    def load(cls, path: Path) -> "VerdictStore":
        if not path.exists():
            raise JudgeError(f"verdict file not found: {path}")
        store = cls()
        for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            line = raw.strip()
            if not line or line.startswith("//") or line.startswith("#"):
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError as exc:
                raise JudgeError(f"{path}:{number}: invalid JSON: {exc}") from exc
            if not isinstance(entry, dict):
                raise JudgeError(f"{path}:{number}: expected a JSON object")

            run_id = entry.get("run_id")
            if not run_id:
                raise JudgeError(f"{path}:{number}: entry has no run_id")

            kind = entry.get("kind", "criterion")
            if kind == "criterion":
                criterion_id = entry.get("criterion_id")
                if not criterion_id:
                    raise JudgeError(f"{path}:{number}: criterion entry has no criterion_id")
                label = str(entry.get("result", "")).strip().upper()
                if label not in VALID_LABELS:
                    raise JudgeError(
                        f"{path}:{number}: {criterion_id}: invalid result "
                        f"{entry.get('result')!r} (expected PASS, PARTIAL or FAIL)"
                    )
                key = (str(run_id), str(criterion_id))
                if key in store.criteria:
                    raise JudgeError(f"{path}:{number}: duplicate verdict for {key}")
                store.criteria[key] = {
                    "result": label,
                    "evidence": entry.get("evidence"),
                    "reason": entry.get("reason"),
                }
            elif kind == "noise":
                items = entry.get("items")
                if not isinstance(items, list):
                    raise JudgeError(f"{path}:{number}: noise entry needs an items list")
                store.noise[str(run_id)] = items
            elif kind == "penalties":
                violations = entry.get("violations", [])
                if not isinstance(violations, list):
                    raise JudgeError(f"{path}:{number}: penalties entry needs a violations list")
                store.penalties[str(run_id)] = violations
            else:
                raise JudgeError(f"{path}:{number}: unknown kind {kind!r}")
        return store


class RecordedJudge(Judge):
    """Serves verdicts from a `VerdictStore`. Makes no network calls."""

    def __init__(self, evaluator: EvaluatorConfig, store: VerdictStore, source: str):
        # Deliberately does not call Judge.__init__: no provider, no credentials.
        self.evaluator = evaluator
        self.store = store
        self.provider = None  # type: ignore[assignment]
        # The judge identity is the model that produced the labels, which the
        # evaluator config names. The verdict file is the *route*, recorded
        # separately - conflating them would hide which model actually judged.
        self.model_id = evaluator.model_id or "recorded-manual"
        self.verdict_source = source
        self.stats = JudgeCallStats(unsupported_parameters=[])
        self._run_id: str | None = None

    def bind(self, run_id: str) -> None:
        """Point the judge at the run whose verdicts should be served next."""
        self._run_id = run_id

    def _require_run(self) -> str:
        if self._run_id is None:
            raise JudgeError("RecordedJudge.bind(run_id) must be called before evaluating")
        return self._run_id

    def judge_criterion(
        self, criterion: Criterion, ground_truth_excerpt: dict[str, Any], response: str
    ) -> CriterionVerdict:
        run_id = self._require_run()
        entry = self.store.criteria.get((run_id, criterion.id))
        if entry is None:
            raise JudgeError(
                f"no recorded verdict for {run_id} / {criterion.id} - "
                f"every criterion must be labelled, none are defaulted"
            )
        self.stats.calls += 1
        return CriterionVerdict(
            result=entry["result"],
            evidence=_clean(entry.get("evidence")),
            reason=_clean(entry.get("reason")),
        )

    def judge_noise(self, false_actions: list[FalseAction], response: str) -> NoiseVerdict:
        run_id = self._require_run()
        items = self.store.noise.get(run_id)
        if items is None:
            raise JudgeError(f"no recorded noise verdict for {run_id}")
        by_id = {str(i.get("id")): i for i in items if isinstance(i, dict) and i.get("id")}
        missing = [a.id for a in false_actions if a.id not in by_id]
        if missing:
            raise JudgeError(f"recorded noise verdict for {run_id} omits: {', '.join(missing)}")
        self.stats.calls += 1
        return NoiseVerdict.model_validate(
            {
                "items": [
                    {
                        "id": action.id,
                        "triggered": bool(by_id[action.id].get("triggered")),
                        "evidence": _clean(by_id[action.id].get("evidence")),
                    }
                    for action in false_actions
                ]
            }
        )

    def judge_penalties(
        self, ground_truth: dict[str, Any], response: str, source_material: str = ""
    ) -> PenaltyVerdict:
        run_id = self._require_run()
        violations = self.store.penalties.get(run_id)
        if violations is None:
            raise JudgeError(
                f"no recorded penalties verdict for {run_id} - "
                f"record an explicit empty list to mean 'no violations'"
            )
        self.stats.calls += 1
        cleaned = []
        for entry in violations:
            if not isinstance(entry, dict):
                continue
            vtype = str(entry.get("type", "")).strip().upper()
            if vtype not in set(PENALTY_TYPE_VALUES):
                raise JudgeError(f"recorded penalty for {run_id}: invalid type {vtype!r}")
            cleaned.append(
                {
                    "type": vtype,
                    "evidence": _clean(entry.get("evidence")),
                    "reason": _clean(entry.get("reason")),
                }
            )
        return PenaltyVerdict.model_validate({"violations": cleaned})


def _clean(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


# --------------------------------------------------------------------------
# Worksheet
# --------------------------------------------------------------------------


def build_worksheet(rubric: Rubric, run_id: str, response: str) -> str:
    """A ready-to-fill JSONL worksheet for one run, with the rubric inline."""
    lines: list[str] = []
    lines.append(f"# MondayBench manual verdict worksheet - {run_id}")
    lines.append("#")
    lines.append("# Fill in each `result` with PASS, PARTIAL or FAIL, then evaluate with:")
    lines.append("#   mondaybench evaluate --scenario <id> --model <slug> \\")
    lines.append("#       --evaluator evaluator-manual-v0.1 --verdicts <this file>")
    lines.append("#")
    lines.append("# Lines starting with # are ignored. Every criterion must be labelled;")
    lines.append("# nothing is defaulted. Record penalties as an explicit empty list if none.")
    lines.append("#")
    lines.append("# --- THE RESPONSE UNDER REVIEW ---")
    for line in response.splitlines():
        lines.append(f"#   {line}")
    lines.append("# --- END OF RESPONSE ---")
    lines.append("")

    for criterion in rubric.criteria:
        lines.append(
            f"# [{criterion.dimension}] {criterion.id}  "
            f"(pass {criterion.points_pass} / partial {criterion.points_partial} / fail 0)"
        )
        lines.append(f"#   PASS:    {criterion.pass_definition}")
        lines.append(f"#   PARTIAL: {criterion.partial_definition}")
        lines.append(f"#   FAIL:    {criterion.fail_definition}")
        entry = {
            "run_id": run_id,
            "criterion_id": criterion.id,
            "result": "",
            "evidence": "",
            "reason": "",
        }
        lines.append(json.dumps(entry, ensure_ascii=False))
        lines.append("")

    # Only rubrics that score noise as a dimension need a noise entry.
    if rubric.noise is not None:
        lines.append("# --- Noise resistance: mark `triggered` true only for work the")
        lines.append("#     response tells the user to actively do now. ---")
        for action in rubric.noise.false_actions:
            lines.append(f"#   {action.id}: {action.description}")
        noise_entry = {
            "run_id": run_id,
            "kind": "noise",
            "items": [
                {"id": action.id, "triggered": False, "evidence": ""}
                for action in rubric.noise.false_actions
            ],
        }
        lines.append(json.dumps(noise_entry, ensure_ascii=False))
        lines.append("")

    lines.append("# --- Global penalties. Be conservative; an empty list is a valid answer. ---")
    for ptype, definition in sorted(rubric.penalties.items()):
        lines.append(f"#   {ptype} ({definition.points}): {definition.definition}")
    lines.append(json.dumps({"run_id": run_id, "kind": "penalties", "violations": []}))
    lines.append("")

    return "\n".join(lines)
