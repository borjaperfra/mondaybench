"""The LLM judge: classification only, never scoring.

Three judge calls per run:

1. one atomic call per rubric criterion (PASS / PARTIAL / FAIL + evidence),
2. one call covering every false-action category,
3. one call for global penalties.

The judge is never asked for a number. If its output cannot be parsed after one
repair attempt, the evaluation fails loudly rather than inventing a result.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

import yaml

from .config import EvaluatorConfig, judge_instruction_text
from .providers import ModelProvider, ProviderError, build_judge_provider
from .scenarios import Criterion, FalseAction
from .schemas import PENALTY_TYPE_VALUES, CriterionVerdict, NoiseVerdict, PenaltyVerdict

JUDGE_SYSTEM_PROMPT = (
    "You are a careful, literal evaluator. You classify against fixed "
    "definitions and return only the JSON object you are asked for."
)

CRITERION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "result": {"type": "string", "enum": ["PASS", "PARTIAL", "FAIL"]},
        "evidence": {"type": "string"},
        "reason": {"type": "string"},
    },
    "required": ["result", "evidence", "reason"],
    "additionalProperties": False,
}

NOISE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "triggered": {"type": "boolean"},
                    "evidence": {"type": "string"},
                },
                "required": ["id", "triggered", "evidence"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["items"],
    "additionalProperties": False,
}

PENALTY_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "violations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": list(PENALTY_TYPE_VALUES),
                    },
                    "evidence": {"type": "string"},
                    "reason": {"type": "string"},
                    "materially_misleading": {"type": "boolean"},
                },
                "required": ["type", "evidence", "reason", "materially_misleading"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["violations"],
    "additionalProperties": False,
}


class JudgeError(Exception):
    """The judge produced something that cannot be turned into a verdict."""


def judge_prompt_fingerprint() -> str:
    """A short hash of the judge prompt templates and verdict schemas.

    The evaluator id names the judge model, but two evaluations can share an id
    and still have been produced by different judge *instructions* - which is
    what happened when a calibration sweep was interrupted midway through a
    penalty-prompt change, leaving five evaluations from the old prompt beside
    two from the new one. Aggregating those in one ranking would be exactly the
    silent mixing the versioning rules exist to prevent, so the fingerprint
    travels with every evaluation and the leaderboard refuses to blend them.
    """
    import hashlib

    material = "\n".join(
        [
            JUDGE_SYSTEM_PROMPT,
            criterion_prompt(
                Criterion(
                    id="_",
                    dimension="_",
                    points_pass=0,
                    points_partial=0,
                    points_fail=0,
                    pass_definition="_",
                    partial_definition="_",
                    fail_definition="_",
                ),
                {},
                "_",
            ),
            noise_prompt([], "_"),
            penalty_prompt({}, "_", "_"),
            json.dumps(CRITERION_SCHEMA, sort_keys=True),
            json.dumps(NOISE_SCHEMA, sort_keys=True),
            json.dumps(PENALTY_SCHEMA, sort_keys=True),
        ]
    )
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]


# --------------------------------------------------------------------------
# JSON extraction
# --------------------------------------------------------------------------

FENCE_PATTERN = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)


def extract_json(text: str) -> dict[str, Any]:
    """Recover a JSON object from judge output.

    Handles the three things judges actually do: fence the JSON, wrap it in
    prose, or return it clean. Raises rather than guessing.
    """
    candidates: list[str] = []
    stripped = text.strip()
    if stripped:
        candidates.append(stripped)

    for match in FENCE_PATTERN.findall(text):
        if match.strip():
            candidates.append(match.strip())

    # Widest brace span, as a last resort for prose-wrapped JSON.
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end > start:
        candidates.append(text[start : end + 1])

    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed

    raise JudgeError(f"no JSON object found in judge output: {text[:300]!r}")


# --------------------------------------------------------------------------
# Prompts
# --------------------------------------------------------------------------


def format_ground_truth(excerpt: dict[str, Any]) -> str:
    if not excerpt:
        return "(no specific ground-truth facts apply to this criterion)"
    return yaml.safe_dump(excerpt, sort_keys=False, allow_unicode=True).strip()


# The built-in instruction header. Kept as a named constant so an external
# override replaces exactly this and nothing else - the data block below it is
# the same either way.
BUILTIN_CRITERION_INSTRUCTIONS = """You are evaluating a model response for MondayBench.

Your job is NOT to judge writing quality and NOT to assign a numeric score.

Evaluate only the criterion below."""


def criterion_prompt(
    criterion: Criterion,
    ground_truth_excerpt: dict[str, Any],
    response: str,
    instructions: str | None = None,
) -> str:
    """The criterion judge prompt.

    `instructions` replaces the built-in header with the evaluator's own
    `judge-prompt.md` when it declares one. Passing None reproduces the previous
    output byte for byte, which is what keeps the legacy
    `judge_prompt_fingerprint()` value stable for v1.0 evaluations.
    """
    header = (instructions.strip() if instructions else BUILTIN_CRITERION_INSTRUCTIONS)
    return f"""{header}

SCENARIO GROUND TRUTH RELEVANT TO THIS CRITERION:
{format_ground_truth(ground_truth_excerpt)}

CRITERION:
{criterion.id} (dimension: {criterion.dimension})

PASS DEFINITION:
{criterion.pass_definition}

PARTIAL DEFINITION:
{criterion.partial_definition}

FAIL DEFINITION:
{criterion.fail_definition}

MODEL RESPONSE:
{response}

Return valid JSON only:

{{
  "result": "PASS" | "PARTIAL" | "FAIL",
  "evidence": "short quote or concise description of the relevant part of the response",
  "reason": "one-sentence explanation"
}}

Rules:

- Judge only what is present in the model response.
- Do not give credit for facts the response does not state or clearly imply.
- Do not penalize style, brevity, formatting, or wording.
- Do not require exact phrasing.
- If the response is ambiguous between two labels, choose the lower label."""


def noise_prompt(false_actions: list[FalseAction], response: str) -> str:
    categories = "\n".join(f"- {a.id}: {a.description}" for a in false_actions)
    return f"""You are evaluating a MondayBench response for false or unnecessary actions.

For each category, determine whether the model presents it as something the user
should actively do now.

Do not mark an item if the model merely mentions it as completed, resolved,
delegated, historical, or non-actionable.

CATEGORIES:
{categories}

MODEL RESPONSE:
{response}

Return JSON only, with one entry for every category listed above:

{{
  "items": [
    {{
      "id": "acme_active",
      "triggered": false,
      "evidence": ""
    }}
  ]
}}"""


def penalty_prompt(
    ground_truth: dict[str, Any],
    source_material: str,
    response: str,
    instructions: str | None = None,
) -> str:
    """Penalty prompt.

    `instructions`, when given, replaces the built-in header with the
    evaluator's own `penalty-judge-prompt.md`. Those files enumerate the
    scenario's own penalty types - monday-004's names four where the global enum
    listed seven - so honouring them is what makes the prose and the schema
    agree. Passing None reproduces the previous output byte for byte.

    IMPLEMENTATION.md s22 shows only the ground truth here. That is not
    answerable: MATERIAL_HALLUCINATION is defined as a claim "unsupported by the
    supplied evidence", and `ground-truth.yaml` is an answer key summarising the
    correct conclusions - not the evidence. Judged against it alone, every
    accurate detail a model quotes from Slack or email reads as invented.
    Calibration produced four such false positives in a single run, capping the
    penalty at -20 for a response that had fabricated nothing.

    So the judge gets both: the source material is the authority on whether a
    claim is supported, the ground truth on whether it is materially relevant.
    """
    header = (
        instructions.strip() if instructions
        else "You are checking a MondayBench response for serious factual failures."
    )
    return f"""{header}

SOURCE MATERIAL THE MODEL WAS GIVEN. This is the authority on what is
supported. Any claim traceable to this material is NOT a hallucination, even if
it is a detail the ground-truth summary below does not repeat:

{source_material}

GROUND TRUTH (the correct conclusions, for judging what is materially relevant -
not an exhaustive list of permitted facts):
{format_ground_truth(ground_truth)}

Model response:
{response}

Identify only clear cases of:

1. MATERIAL_HALLUCINATION - a factual claim materially relevant to the briefing
   that the SOURCE MATERIAL above does not support. Before flagging one, look
   for it in the source material; quoting or paraphrasing a detail found there
   is never a hallucination.
2. PROHIBITED_ACTION - recommending an action explicitly contradicted or
   prohibited by the current state.
3. MAJOR_CONTRADICTION - the response materially contradicts itself about the
   current state of an important issue.

Be conservative. Do not penalize omissions, style, imprecision that is already
captured by the rubric, or reasonable paraphrases. An empty list is the correct
answer for a response with no clear violations.

These penalties are heavy (-5 to -10 each, against a 100-point scale), so they
are reserved for failures that would actually mislead the reader.

For every candidate you list, set `materially_misleading`:

- `true`  - a reader acting on this response would be materially misled.
- `false` - you noticed it, but it does not rise to a violation: the substance
  is supported and only the attribution, timing or wording differs; it is a
  reasonable paraphrase or compression; or you would describe it as minor.

Do not soften a real violation by marking it false, and do not omit a candidate
you considered - listing it with `false` is the correct way to record that you
looked and decided it did not count. Only `true` entries cost points.

Guidance for the boundary:

- A detail present in the source material but attributed to a slightly wrong
  person, team or time is NOT materially misleading.
- Compressing or paraphrasing the source is NOT a hallucination.
- Stating a confidentiality or deadline condition wrongly in a way that would
  change what the reader does IS materially misleading.

Return valid JSON only:

{{
  "violations": [
    {{
      "type": "MATERIAL_HALLUCINATION",
      "evidence": "...",
      "reason": "..."
    }}
  ]
}}"""


# --------------------------------------------------------------------------
# Judge
# --------------------------------------------------------------------------

REPAIR_INSTRUCTION = (
    "Your previous reply was not valid JSON matching the requested shape. "
    "Return only the JSON object, with no prose, no explanation and no code fences."
)


@dataclass
class JudgeCallStats:
    calls: int = 0
    repairs: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    unsupported_parameters: list[str] | None = None


class Judge:
    """Wraps one judge model and the evaluator's generation settings."""

    def __init__(
        self,
        evaluator: EvaluatorConfig,
        provider: ModelProvider | None = None,
        scenario_id: str | None = None,
        rubric: Any | None = None,
    ):
        self.evaluator = evaluator
        self.provider = provider or build_judge_provider(evaluator)
        self.model_id = evaluator.resolved_model_id()
        self.stats = JudgeCallStats(unsupported_parameters=[])
        # An evaluator may override the built-in templates with scenario-specific
        # files under `evaluators/<scenario>/`. Every evaluator from v0.2 onwards
        # declares both, and until v1.1 nothing loaded them: the recorded judge
        # read them, the code did not. Knowing the scenario is what lets the
        # override be resolved at all.
        self.scenario_id = scenario_id
        # Carried so the penalty enum can be narrowed to the penalties this
        # scenario's rubric actually declares.
        self.rubric = rubric

    def _generation_config(self, schema: dict[str, Any]) -> dict[str, Any]:
        return {
            "temperature": self.evaluator.temperature,
            "effort": self.evaluator.effort,
            "max_output_tokens": self.evaluator.max_output_tokens,
            "response_json_schema": schema,
        }

    def _instruction_override(self, which: str) -> str | None:
        """The evaluator's external judge instruction for this scenario, if any."""
        scenario_id = getattr(self, "scenario_id", None)
        evaluator = getattr(self, "evaluator", None)
        if scenario_id is None or evaluator is None:
            return None
        return judge_instruction_text(evaluator, scenario_id, which)

    def _penalty_schema(self) -> dict[str, Any]:
        """The penalty schema, narrowed to this scenario's penalties when known.

        On the API route the schema reaches the model as
        `response_format.json_schema`, so a global enum tells monday-001's judge
        it may return a type monday-001's rubric does not define. Falls back to
        the global schema when the rubric is not known, which is what a caller
        constructing a bare Judge gets.
        """
        rubric = getattr(self, "rubric", None)
        if rubric is None or not getattr(rubric, "penalties", None):
            return PENALTY_SCHEMA
        schema = json.loads(json.dumps(PENALTY_SCHEMA, sort_keys=True))
        schema["properties"]["violations"]["items"]["properties"]["type"]["enum"] = sorted(
            rubric.penalties
        )
        return schema

    def _ask(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        """One judge call, with a single JSON-repair retry."""
        config = self._generation_config(schema)
        attempts = [prompt, f"{prompt}\n\n{REPAIR_INSTRUCTION}"]
        last_error: Exception | None = None

        for index, attempt_prompt in enumerate(attempts):
            try:
                result = self.provider.generate(
                    model_id=self.model_id,
                    system_prompt=JUDGE_SYSTEM_PROMPT,
                    user_prompt=attempt_prompt,
                    generation_config=config,
                )
            except ProviderError as exc:
                raise JudgeError(f"judge call failed: {exc}") from exc

            self.stats.calls += 1
            self.stats.input_tokens += result.input_tokens or 0
            self.stats.output_tokens += result.output_tokens or 0
            for param in result.unsupported_parameters:
                assert self.stats.unsupported_parameters is not None
                if param not in self.stats.unsupported_parameters:
                    self.stats.unsupported_parameters.append(param)

            try:
                return extract_json(result.text)
            except JudgeError as exc:
                last_error = exc
                if index == 0:
                    self.stats.repairs += 1

        raise JudgeError(f"judge output unusable after one repair attempt: {last_error}")

    def judge_criterion(
        self, criterion: Criterion, ground_truth_excerpt: dict[str, Any], response: str
    ) -> CriterionVerdict:
        override = self._instruction_override("criterion")
        prompt = criterion_prompt(criterion, ground_truth_excerpt, response, instructions=override)
        raw = self._ask(prompt, CRITERION_SCHEMA)
        result = str(raw.get("result", "")).strip().upper()
        if result not in {"PASS", "PARTIAL", "FAIL"}:
            raise JudgeError(
                f"criterion {criterion.id!r}: judge returned invalid label {raw.get('result')!r}"
            )
        return CriterionVerdict(
            result=result,  # type: ignore[arg-type]
            evidence=_text_or_none(raw.get("evidence")),
            reason=_text_or_none(raw.get("reason")),
        )

    def judge_noise(self, false_actions: list[FalseAction], response: str) -> NoiseVerdict:
        raw = self._ask(noise_prompt(false_actions, response), NOISE_SCHEMA)
        items = raw.get("items")
        if not isinstance(items, list):
            raise JudgeError("noise judge returned no items list")

        by_id = {
            str(item.get("id")): item for item in items if isinstance(item, dict) and item.get("id")
        }
        missing = [a.id for a in false_actions if a.id not in by_id]
        if missing:
            raise JudgeError(f"noise judge omitted categories: {', '.join(missing)}")

        return NoiseVerdict.model_validate(
            {
                "items": [
                    {
                        "id": action.id,
                        "triggered": bool(by_id[action.id].get("triggered")),
                        "evidence": _text_or_none(by_id[action.id].get("evidence")),
                    }
                    for action in false_actions
                ]
            }
        )

    def judge_penalties(
        self, ground_truth: dict[str, Any], response: str, source_material: str = ""
    ) -> PenaltyVerdict:
        override = self._instruction_override("penalty")
        raw = self._ask(
            penalty_prompt(ground_truth, source_material, response, instructions=override),
            self._penalty_schema(),
        )
        violations = raw.get("violations")
        if violations is None:
            violations = []
        if not isinstance(violations, list):
            raise JudgeError("penalty judge returned a non-list violations field")

        cleaned = []
        for entry in violations:
            if not isinstance(entry, dict):
                continue
            vtype = str(entry.get("type", "")).strip().upper()
            if vtype not in set(PENALTY_TYPE_VALUES):
                raise JudgeError(f"penalty judge returned invalid type {entry.get('type')!r}")
            cleaned.append(
                {
                    "type": vtype,
                    "evidence": _text_or_none(entry.get("evidence")),
                    "reason": _text_or_none(entry.get("reason")),
                    # Absent means the judge did not classify it; default to
                    # scoring it rather than silently discarding a violation.
                    "materially_misleading": bool(entry.get("materially_misleading", True)),
                }
            )
        return PenaltyVerdict.model_validate({"violations": cleaned})


def _text_or_none(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
