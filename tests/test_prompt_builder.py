from __future__ import annotations

import pytest

from mondaybench.prompt_builder import (
    PLACEHOLDER_PATTERN,
    build_prompt,
    placeholder_for,
    sha256_text,
)
from mondaybench.scenarios import ScenarioError, load_scenario


def test_placeholder_naming():
    assert placeholder_for("slack.md") == "{{SLACK}}"
    assert placeholder_for("metrics.csv") == "{{METRICS}}"
    assert placeholder_for("meeting-notes.md") == "{{MEETING_NOTES}}"


def test_all_placeholders_replaced(scenario):
    built = build_prompt(scenario)
    assert PLACEHOLDER_PATTERN.findall(built.text) == []
    assert "{{" not in built.text


def test_every_source_body_is_present(scenario):
    built = build_prompt(scenario)
    for source, body in scenario.source_text.items():
        # first non-empty line of each source must appear in the final prompt
        marker = next(line for line in body.splitlines() if line.strip())
        assert marker.strip() in built.text, f"{source} content missing"


def test_hash_is_deterministic(scenario):
    first = build_prompt(scenario)
    second = build_prompt(scenario)
    assert first.sha256 == second.sha256
    assert first.sha256 == sha256_text(first.text)
    assert len(first.sha256) == 64


def test_hash_changes_when_a_source_changes(scenario):
    import dataclasses

    baseline = build_prompt(scenario).sha256
    mutated_sources = dict(scenario.source_text)
    mutated_sources["slack.md"] += "\n\n**23:59 - Someone** extra line\n"
    mutated = dataclasses.replace(scenario, source_text=mutated_sources)
    assert build_prompt(mutated).sha256 != baseline


def test_source_ordering_is_taken_from_scenario_yaml(scenario):
    built = build_prompt(scenario)
    # The prompt's section order must follow scenario.yaml's declared order.
    positions = []
    for source in scenario.sources:
        body = scenario.source_text[source]
        marker = next(line for line in body.splitlines() if line.strip())
        positions.append(built.text.index(marker.strip()))
    assert positions == sorted(positions), "sources appear out of declared order"


def test_missing_placeholder_is_an_error(scenario):
    import dataclasses

    broken = dataclasses.replace(
        scenario, prompt_template=scenario.prompt_template.replace("{{SLACK}}", "")
    )
    # A template that names *some* sources but not all of them is rejected,
    # rather than falling back to appending: a half-substituted prompt would
    # still hash cleanly and still produce runs, silently missing a source.
    with pytest.raises(ScenarioError, match="none for"):
        build_prompt(broken)


def test_unresolved_placeholder_is_an_error(scenario):
    import dataclasses

    broken = dataclasses.replace(
        scenario, prompt_template=scenario.prompt_template + "\n{{MYSTERY}}\n"
    )
    with pytest.raises(ScenarioError, match="unresolved placeholders"):
        build_prompt(broken)


def test_sources_are_read_as_utf8(scenario):
    built = build_prompt(scenario)
    # The scenario uses non-ASCII characters (euro signs, emoji, en dashes).
    assert "€72k" in built.text  # EUR 72k
    built.text.encode("utf-8")  # must round-trip without error


def test_system_prompt_carries_no_benchmark_hints(scenario):
    built = build_prompt(scenario)
    lowered = built.system_prompt.lower()
    for hint in ("monday", "benchmark", "rubric", "contoso", "umbrella", "priorit"):
        assert hint not in lowered


def test_prompt_hash_is_stable_across_reloads():
    # A fresh load from disk must produce the same bytes and hash.
    first = build_prompt(load_scenario("monday-001"))
    second = build_prompt(load_scenario("monday-001"))
    assert first.text == second.text
    assert first.sha256 == second.sha256
