"""Loaders for `models.yaml` and `evaluators/*.yaml`, plus env resolution.

Credentials are never stored in config files - configs name the *environment
variable* that holds them, and this module resolves those names at call time.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, replace, field
from pathlib import Path
from typing import Any

import yaml


class ConfigError(Exception):
    """Raised when a config file is missing, unparseable or internally invalid."""


def repo_root() -> Path:
    """The benchmark repository root (the directory holding `models.yaml`)."""
    return Path(__file__).resolve().parent.parent


def load_yaml(path: Path) -> Any:
    if not path.exists():
        raise ConfigError(f"missing file: {path}")
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConfigError(f"invalid YAML in {path}: {exc}") from exc


def _load_dotenv(root: Path) -> None:
    """Minimal .env reader.

    Avoids a python-dotenv dependency for a five-line job. Existing environment
    variables always win, so an exported key is never silently overridden.
    """
    env_file = root / ".env"
    if not env_file.exists():
        return
    for raw in env_file.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("\"").strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


_dotenv_loaded = False


def resolve_env(var_name: str | None, *, required: bool = True) -> str | None:
    """Read `var_name` from the environment, loading `.env` once on first use."""
    global _dotenv_loaded
    if not _dotenv_loaded:
        _load_dotenv(repo_root())
        _dotenv_loaded = True
    if var_name is None:
        return None
    value = os.environ.get(var_name)
    if not value and required:
        raise ConfigError(
            f"environment variable {var_name} is not set "
            f"(copy .env.example to .env and fill it in)"
        )
    return value or None


# --------------------------------------------------------------------------
# models.yaml
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Pricing:
    input_per_million_usd: float | None = None
    output_per_million_usd: float | None = None
    reasoning_per_million_usd: float | None = None
    source: str | None = None


@dataclass(frozen=True)
class ModelConfig:
    slug: str
    display_name: str
    provider: str
    api_style: str
    model_id: str
    base_url_env: str | None
    api_key_env: str | None
    temperature: float | None
    max_output_tokens: int | None
    reasoning_enabled: bool
    # Not sent unless a model pins it. None means "not sent, provider default
    # applied" - recorded as such so an audit can tell that apart from a value
    # we chose. Pin it in models.yaml under `generation.top_p`.
    top_p: float | None = None
    # The raw capability block, so reasoning intent can be derived without this
    # module having to know every provider's spelling of "thinking".
    capabilities: dict[str, Any] = field(default_factory=dict)
    pricing: Pricing = field(default_factory=Pricing)
    extra_body: dict[str, Any] = field(default_factory=dict)
    notes: str | None = None
    # Replaces the harness default system prompt for this model only. None means
    # "use the default", which is every model that does not set it, so adding
    # the field changes nothing on the wire for an existing config.
    #
    # Loaded from a file rather than inline YAML on purpose: a system prompt is
    # an experimental variable and has to be byte-exact, and YAML block scalars
    # rewrite trailing whitespace and line endings. The file's bytes are the
    # prompt, and its sha256 travels with every run in
    # `generation.system_prompt_sha256`.
    system_prompt: str | None = None
    system_prompt_file: str | None = None

    def base_url(self) -> str | None:
        return resolve_env(self.base_url_env, required=self.api_style == "openai_compatible")

    def api_key(self) -> str | None:
        return resolve_env(self.api_key_env, required=True)


SUPPORTED_API_STYLES = {"openai_compatible", "anthropic"}


def _parse_pricing(raw: dict[str, Any] | None) -> Pricing:
    raw = raw or {}
    return Pricing(
        input_per_million_usd=raw.get("input_per_million_usd"),
        output_per_million_usd=raw.get("output_per_million_usd"),
        reasoning_per_million_usd=raw.get("reasoning_per_million_usd"),
        source=raw.get("source"),
    )


def load_models(path: Path | None = None) -> dict[str, ModelConfig]:
    path = path or repo_root() / "models.yaml"
    data = load_yaml(path) or {}
    raw_models = data.get("models")
    if not isinstance(raw_models, dict) or not raw_models:
        raise ConfigError(f"{path} defines no models")

    models: dict[str, ModelConfig] = {}
    for slug, cfg in raw_models.items():
        if not isinstance(cfg, dict):
            raise ConfigError(f"model {slug!r} is not a mapping")
        api_style = cfg.get("api_style", "openai_compatible")
        if api_style not in SUPPORTED_API_STYLES:
            raise ConfigError(
                f"model {slug!r} uses unsupported api_style {api_style!r} "
                f"(supported: {sorted(SUPPORTED_API_STYLES)})"
            )
        generation = cfg.get("generation") or {}
        if "max_output_tokens" not in generation:
            raise ConfigError(f"model {slug!r} is missing generation.max_output_tokens")
        # An explicit null is allowed and means "this runtime exposes no output
        # ceiling", which is different from a ceiling of zero. It must still be
        # written out deliberately: the key is required, only its value may be
        # null. A model configured this way cannot be used to generate runs.
        capabilities = cfg.get("capabilities") or {}
        system_prompt_file = cfg.get("system_prompt_file")
        system_prompt = None
        if system_prompt_file is not None:
            prompt_path = (path.parent / str(system_prompt_file)).resolve()
            if not prompt_path.is_file():
                raise ConfigError(
                    f"model {slug!r}: system_prompt_file {system_prompt_file!r} not found "
                    f"at {prompt_path}"
                )
            # Read as bytes and decode, so nothing normalises line endings on the
            # way in. What is on disk is what the model is sent.
            system_prompt = prompt_path.read_bytes().decode("utf-8")
        models[slug] = ModelConfig(
            slug=slug,
            display_name=cfg.get("display_name", slug),
            provider=cfg.get("provider", "unknown"),
            api_style=api_style,
            model_id=cfg.get("model_id", slug),
            base_url_env=cfg.get("base_url_env"),
            api_key_env=cfg.get("api_key_env"),
            temperature=generation.get("temperature"),
            top_p=generation.get("top_p"),
            max_output_tokens=(int(generation["max_output_tokens"])
                               if generation["max_output_tokens"] is not None else None),
            reasoning_enabled=bool(capabilities.get("reasoning", False)),
            capabilities=dict(capabilities),
            pricing=_parse_pricing(cfg.get("pricing")),
            extra_body=cfg.get("extra_body") or {},
            notes=cfg.get("notes"),
            system_prompt=system_prompt,
            system_prompt_file=str(system_prompt_file) if system_prompt_file else None,
        )
    return models


# --------------------------------------------------------------------------
# evaluators/<id>.yaml
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class EvaluatorConfig:
    id: str
    provider: str
    api_style: str
    model_id: str | None
    model_env: str | None
    base_url_env: str | None
    api_key_env: str | None
    temperature: float | None
    effort: str | None
    max_output_tokens: int
    require_evidence: bool
    # Which ground-truth facts each criterion's judge call may see. Empty means
    # the scenario ships no dotted paths to slice (a prose answer key), and the
    # judge is given the whole thing.
    ground_truth_map: dict[str, list[str]]
    # Which rubric this evaluator scores against. A rubric change alters what a
    # score means, so it is versioned with the evaluator rather than overwritten.
    rubric_file: str = "rubric.yaml"
    # The scenario this evaluator was written for, when it is scenario-specific.
    # `validate` refuses to pair it with any other scenario rather than scoring
    # one scenario's responses against another's rubric.
    scenario: str | None = None
    # The rubric version the evaluator was written against. Checked at load
    # against the rubric actually on disk.
    rubric_version: str | None = None
    # The scenario revision it was written against, checked the same way.
    scenario_version: str | None = None
    # External judge prompts, relative to `evaluators/`. When absent the judge
    # uses the prompts built into `judge.py`.
    prompt_file: str | None = None
    penalty_prompt_file: str | None = None

    def resolved_model_id(self) -> str:
        if self.model_id:
            return self.model_id
        value = resolve_env(self.model_env, required=True)
        assert value is not None  # resolve_env raises when required and unset
        return value

    def base_url(self) -> str | None:
        return resolve_env(self.base_url_env, required=self.api_style == "openai_compatible")

    def api_key(self) -> str | None:
        return resolve_env(self.api_key_env, required=True)


# Which evaluator field names each external judge instruction file.
JUDGE_INSTRUCTION_FIELDS = {"criterion": "prompt_file", "penalty": "penalty_prompt_file"}


def judge_instruction_path(
    evaluator: EvaluatorConfig, scenario_id: str, which: str
) -> Path | None:
    """Where an evaluator's external judge instruction lives, if it declares one.

    Resolved under `evaluators/<scenario>/`, using the evaluator's own declared
    scenario when it has one. Returns None when the evaluator uses the built-in
    templates in `judge.py`.
    """
    field = JUDGE_INSTRUCTION_FIELDS.get(which)
    if field is None:
        raise ConfigError(f"unknown judge instruction {which!r}")
    relative = getattr(evaluator, field, None)
    if not relative:
        return None
    folder = evaluator.scenario or scenario_id
    return repo_root() / "evaluators" / folder / relative


def judge_instruction_text(
    evaluator: EvaluatorConfig, scenario_id: str, which: str
) -> str | None:
    """The external judge instruction text, or None when there is no override.

    A declared file that does not exist is an error, not a silent fallback to
    the built-in template: the evaluator is asserting that its judging was done
    under those instructions, and scoring against different ones would be a
    different evaluator.
    """
    path = judge_instruction_path(evaluator, scenario_id, which)
    if path is None:
        return None
    if not path.exists():
        raise ConfigError(
            f"evaluator {evaluator.id} declares {which} prompt {path.name!r} "
            f"but {path} does not exist"
        )
    return path.read_text(encoding="utf-8")


def load_evaluator(evaluator_id: str, path: Path | None = None) -> EvaluatorConfig:
    path = path or repo_root() / "evaluators" / f"{evaluator_id}.yaml"
    data = load_yaml(path) or {}
    declared = data.get("id")
    if declared and declared != evaluator_id:
        raise ConfigError(f"{path} declares id {declared!r} but was loaded as {evaluator_id!r}")

    judge = data.get("judge") or {}
    api_style = judge.get("api_style", judge.get("provider", "openai_compatible"))
    if api_style not in SUPPORTED_API_STYLES:
        raise ConfigError(f"evaluator {evaluator_id}: unsupported judge api_style {api_style!r}")
    if not judge.get("model_id") and not judge.get("model_env"):
        raise ConfigError(
            f"evaluator {evaluator_id}: judge needs either model_id or model_env "
            f"so the exact judge model can be recorded"
        )

    generation = data.get("generation") or {}
    behavior = data.get("behavior") or {}
    gt_map = data.get("ground_truth_map") or {}
    if not isinstance(gt_map, dict):
        raise ConfigError(f"evaluator {evaluator_id}: ground_truth_map must be a mapping")

    # Generation parameters may sit under `generation:` (monday-001's
    # evaluators) or inline on `judge:` (monday-002's draft). `generation` wins
    # where both are given, so the more specific block is never shadowed.
    def _gen(key: str) -> Any:
        return generation[key] if key in generation else judge.get(key)

    return EvaluatorConfig(
        id=evaluator_id,
        provider=judge.get("provider", api_style),
        api_style=api_style,
        model_id=judge.get("model_id"),
        model_env=judge.get("model_env"),
        base_url_env=judge.get("base_url_env"),
        api_key_env=judge.get("api_key_env"),
        temperature=_gen("temperature"),
        effort=_gen("effort"),
        # Explicit None check, not `or`: the recorded evaluators declare 0 on
        # purpose ("no generation parameters apply") and `or` would silently
        # turn that into a budget.
        max_output_tokens=int(
            _gen("max_output_tokens") if _gen("max_output_tokens") is not None else 4000
        ),
        require_evidence=bool(behavior.get("require_evidence", True)),
        ground_truth_map={k: list(v or []) for k, v in gt_map.items()},
        rubric_file=data.get("rubric_file", "rubric.yaml"),
        scenario=data.get("scenario"),
        rubric_version=(
            str(data["rubric_version"]) if data.get("rubric_version") is not None else None
        ),
        scenario_version=(
            str(data["scenario_version"]) if data.get("scenario_version") is not None else None
        ),
        prompt_file=judge.get("prompt_file"),
        penalty_prompt_file=judge.get("penalty_prompt_file"),
    )


# --------------------------------------------------------------------------
# Per-scenario endpoint overrides
# --------------------------------------------------------------------------


def endpoint_env_names(models: dict[str, ModelConfig]) -> dict[str, tuple[str | None, str | None]]:
    """Endpoint name -> (base_url_env, api_key_env), learned from models.yaml.

    Derived rather than declared, so there is no second list of endpoints to
    keep in step with the first.
    """
    found: dict[str, tuple[str | None, str | None]] = {}
    for cfg in models.values():
        found.setdefault(cfg.provider, (cfg.base_url_env, cfg.api_key_env))
    return found


def endpoint_overrides_for(scenario_id: str, path: Path | None = None) -> dict[str, str]:
    """Per-scenario endpoint overrides, read from models.yaml.

    Deliberately NOT in scenario.yaml. That file is covered by FROZEN.yaml, so
    putting a serving detail there would mean a published scenario's content
    hash changed every time an endpoint moved - and the manifest exists to make
    exactly that impossible. Which endpoint serves a model is configuration, and
    configuration lives in models.yaml.
    """
    path = path or repo_root() / "models.yaml"
    data = load_yaml(path) or {}
    scoped = (data.get("scenario_endpoint_overrides") or {}).get(scenario_id) or {}
    return {str(slug): str(endpoint) for slug, endpoint in scoped.items()}


def apply_endpoint_overrides(
    models: dict[str, ModelConfig], overrides: dict[str, str]
) -> dict[str, ModelConfig]:
    """Serve some models from a different endpoint, for one scenario only.

    A model's endpoint is part of its serving configuration, and qualification
    rejects a run whose provider differs from the configured one. So moving a
    model in models.yaml does not just change future runs - it retroactively
    disqualifies every run already published under the old endpoint. qwen3.6 has
    three official runs in each of monday-001, 002 and 003, all served by
    helmcode; editing that one line would have broken three frozen batteries.

    This scopes the change to the scenario that needs it. monday-001..003
    declare no overrides and are untouched.

    The cost is real and must be reported, not buried: a model served from a
    different endpoint is not strictly comparable with its own results on other
    scenarios. Latency and TTFA especially are properties of the endpoint.
    """
    if not overrides:
        return models
    env = endpoint_env_names(models)
    out = dict(models)
    for slug, endpoint in overrides.items():
        cfg = out.get(slug)
        if cfg is None:
            raise ConfigError(f"endpoint override names unknown model {slug!r}")
        if endpoint not in env:
            raise ConfigError(
                f"endpoint override for {slug!r} names unknown endpoint {endpoint!r}; "
                f"models.yaml knows {', '.join(sorted(env))}"
            )
        base_url_env, api_key_env = env[endpoint]
        out[slug] = replace(
            cfg, provider=endpoint, base_url_env=base_url_env, api_key_env=api_key_env
        )
    return out


# --------------------------------------------------------------------------
# Which evaluator belongs to which scenario
# --------------------------------------------------------------------------


def evaluators_for_scenario(scenario_id: str, root: Path | None = None) -> dict[str, list[str]]:
    """Evaluator ids that declare `scenario: <scenario_id>`, grouped by status.

    Returns {"official": [...], "calibration": [...], "other": [...]}, each
    sorted. An evaluator that declares no scenario belongs to none of them:
    monday-001's evaluators predate the field and are matched by neither.
    """
    directory = (root or repo_root()) / "evaluators"
    found: dict[str, list[str]] = {"official": [], "calibration": [], "other": []}
    if not directory.is_dir():
        return found
    for path in sorted(directory.glob("*.yaml")):
        data = load_yaml(path) or {}
        if data.get("scenario") != scenario_id:
            continue
        status = str(data.get("status") or "other")
        found.setdefault(status, []).append(data.get("id") or path.stem)
    return found


def resolve_evaluator(scenario_id: str, explicit: str | None, fallback: str) -> str:
    """The evaluator to use for a scenario when the caller named none.

    The commands that publish used to default to a fixed evaluator id, which is
    monday-001's. Running `freeze --scenario monday-002 --check` therefore tried
    to hash monday-001's `rubric-0.2.yaml` inside monday-002's directory and
    failed with "scenario is missing: rubric-0.2.yaml" - a confusing message for
    a scenario that is perfectly intact. Worse, a scenario that *did* happen to
    ship a file of that name would have been checked against the wrong rubric
    without complaining at all.

    So: an explicit `--evaluator` always wins, and otherwise the evaluator is
    the one that declares this scenario and is marked official. Ambiguity is an
    error rather than a guess. Scenarios whose evaluators predate the `scenario`
    field keep the old fallback, which is what monday-001 relies on.
    """
    if explicit:
        return explicit

    found = evaluators_for_scenario(scenario_id)
    official = found.get("official") or []
    if len(official) == 1:
        return official[0]
    if len(official) > 1:
        raise ConfigError(
            f"{scenario_id} has {len(official)} official evaluators "
            f"({', '.join(official)}); name one with --evaluator"
        )

    others = sorted(
        name for status, names in found.items() if status != "official" for name in names
    )
    if others:
        raise ConfigError(
            f"{scenario_id} has no evaluator marked `status: official` - only "
            f"{', '.join(others)}. Name one with --evaluator, or promote one."
        )
    return fallback


# --------------------------------------------------------------------------
# Committed-secret scanning
# --------------------------------------------------------------------------

import re as _re

# A credential *value*, not a prose mention of one. The first version of this
# check flagged the word "Bearer" inside an explanatory comment, so it now
# requires an actual token-shaped string and skips comment lines.
_CREDENTIAL_PATTERNS: tuple[tuple[str, "_re.Pattern[str]"], ...] = (
    ("sk- prefixed key", _re.compile(r"\bsk-[A-Za-z0-9_\-]{16,}")),
    ("bearer token", _re.compile(r"\bBearer\s+[A-Za-z0-9_\-\.]{16,}")),
    # `api_key: <value>` assigns a literal; `api_key_env: NAME` is correct usage.
    ("inline api_key value", _re.compile(r"^\s*api_key\s*:\s*[\"']?\S{8,}")),
)


def find_literal_credentials(text: str) -> list[tuple[int, str]]:
    """Return (line number, description) for lines that hold a credential value.

    Comment lines are skipped: documenting that an endpoint expects a bearer
    token is not the same as committing one.
    """
    findings: list[tuple[int, str]] = []
    for number, line in enumerate(text.splitlines(), start=1):
        if line.lstrip().startswith("#"):
            continue
        for label, pattern in _CREDENTIAL_PATTERNS:
            if pattern.search(line):
                findings.append((number, label))
                break
    return findings
