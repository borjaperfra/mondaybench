"""Deterministic prompt assembly.

The final prompt is the benchmark's unit of comparability, so it is built one
way only: read `prompt.md`, substitute each source's placeholder in the order
declared by `scenario.yaml`, hash the result. The hash travels with every run
and every evaluation so any published score can be traced to the exact bytes
the model saw.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

from .scenarios import Scenario, ScenarioError

# `slack.md` -> `{{SLACK}}`
PLACEHOLDER_PATTERN = re.compile(r"\{\{([A-Z0-9_]+)\}\}")

SYSTEM_PROMPT = "You are a helpful assistant."


def placeholder_for(source: str) -> str:
    """Map a source filename to its placeholder token."""
    stem = source.rsplit(".", 1)[0]
    return "{{" + re.sub(r"[^A-Z0-9]+", "_", stem.upper()).strip("_") + "}}"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class BuiltPrompt:
    text: str
    sha256: str
    system_prompt: str

    def estimated_tokens(self) -> int:
        """Rough character-based estimate. Only for dry-run display.

        Never recorded as a usage figure - real token counts come from the
        provider.
        """
        return len(self.text) // 4


def section_title(source: str) -> str:
    """`deployments.csv` -> `Deployments`. The heading a source is filed under."""
    stem = source.rsplit(".", 1)[0]
    return re.sub(r"[^0-9A-Za-z]+", " ", stem).strip().title()


def _append_sources(scenario: Scenario) -> str:
    """Assemble a prompt whose template declares no placeholders.

    monday-002's `prompt.md` is instructions only: it names the sources in prose
    and expects them beneath. Rather than edit that file to carry placeholders -
    its bytes are pinned by `PROMPT_FILE_SHA256.txt` - each source is appended
    under its own heading, in the order `scenario.yaml` declares.

    The separator and heading shape are fixed here on purpose. They are part of
    what the model reads, so they belong to the rendered-prompt hash and must
    not vary between runs or machines.
    """
    parts = [scenario.prompt_template.rstrip()]
    for source in scenario.sources:
        body = scenario.source_text[source].strip()
        parts.append(f"---\n\n## {section_title(source)}\n\n{body}")
    return "\n\n".join(parts) + "\n"


def build_prompt(scenario: Scenario) -> BuiltPrompt:
    """Render the exact bytes a model is given.

    Two assembly modes, chosen by what the template contains rather than by
    scenario id:

    * **substitution** — the template carries a `{{SOURCE}}` placeholder per
      declared source (monday-001). Every source must have one, and no
      placeholder may survive.
    * **append** — the template carries no placeholders at all (monday-002).
      Sources are appended in declared order under their own headings.

    A template that carries *some* placeholders but not one per source is
    rejected rather than half-substituted: a prompt missing a source silently
    would still hash cleanly and still produce runs.
    """
    template = scenario.prompt_template
    declared = [placeholder_for(s) for s in scenario.sources]
    present = [t for t in declared if t in template]
    any_placeholder = bool(PLACEHOLDER_PATTERN.search(template))

    if not any_placeholder:
        text = _append_sources(scenario)
        return BuiltPrompt(text=text, sha256=sha256_text(text), system_prompt=SYSTEM_PROMPT)

    if len(present) != len(declared):
        missing = [t for t in declared if t not in template]
        raise ScenarioError(
            f"scenario {scenario.id!r}: prompt template has placeholders but none for "
            f"{', '.join(missing)}; a template either names every source or none of them"
        )

    text = template
    for source in scenario.sources:
        body = scenario.source_text[source].strip()
        # `str.replace` (not a regex) so source content containing backslashes
        # or group references is inserted verbatim.
        text = text.replace(placeholder_for(source), body)

    leftover = PLACEHOLDER_PATTERN.findall(text)
    if leftover:
        raise ScenarioError(
            f"scenario {scenario.id!r}: unresolved placeholders after substitution: "
            f"{', '.join(sorted(set(leftover)))}"
        )

    return BuiltPrompt(text=text, sha256=sha256_text(text), system_prompt=SYSTEM_PROMPT)
