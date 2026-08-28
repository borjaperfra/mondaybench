"""Guards for the monday-002 official freeze.

Each test here corresponds to a way the #002 publication could quietly go wrong:
an orphan source file, a prompt hash that drifts, a calibration run leaking into
an official battery, a penalty prompt that starts double-punishing, or a
provider failure that produces misleading advice. They are written against the
real repository content rather than fixtures where the point is that the
*shipped* artefact says the right thing.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import httpx
import pytest

from mondaybench.config import load_evaluator
from mondaybench.leaderboard import ModelSummary, official_blockers
from mondaybench.prompt_builder import build_prompt
from mondaybench.providers.base import ProviderError
from mondaybench.scenarios import load_scenario

REPO_ROOT = Path(__file__).resolve().parent.parent
SCENARIO_DIR = REPO_ROOT / "scenarios" / "monday-002"

OFFICIAL_PROMPT_SHA256 = "740e627cbc7413c321ede0d54000504de54821d34ff4677f82731b89600423a8"
OFFICIAL_SOURCE_ORDER = [
    "slack.md",
    "emails.md",
    "meetings.md",
    "tasks.md",
    "release-options.csv",
    "calendars.csv",
    "accounts.csv",
    "contracts.csv",
    "support.csv",
]


@pytest.fixture(scope="module")
def m2():
    return load_scenario("monday-002")


# --------------------------------------------------------------------------
# 1. Orphan source detection
# --------------------------------------------------------------------------


def test_no_data_file_sits_in_the_scenario_directory_unused(m2):
    """A csv beside nine live sources that the model never sees is a trap.

    `deployments.csv` was exactly that - a v0.1 leftover carried into the v0.2
    package and never added to `source_order`. It is deleted; this fails if any
    equivalent file reappears.
    """
    declared = set(m2.sources) | {
        "scenario.yaml",
        m2.ground_truth_file,
        m2.prompt_file,
        "rubric.yaml",
        "FROZEN.yaml",
    }
    orphans = [
        entry.name
        for entry in SCENARIO_DIR.iterdir()
        if entry.is_file()
        and entry.name not in declared
        # .md/.txt are notes shipped with the package, not candidate sources.
        and entry.suffix.lower() not in (".md", ".txt")
    ]
    assert orphans == [], f"unused data files in the scenario directory: {orphans}"


def test_deployments_csv_is_gone_but_preserved_in_the_archive():
    assert not (SCENARIO_DIR / "deployments.csv").exists()
    # Deleting evidence is not the same as retiring it from the test.
    assert (
        REPO_ROOT / "archive" / "monday-002-v0.1" / "scenario" / "deployments.csv"
    ).exists()


# --------------------------------------------------------------------------
# 2. Rendered prompt hash consistency
# --------------------------------------------------------------------------


def test_source_order_is_exactly_the_official_nine(m2):
    assert m2.sources == OFFICIAL_SOURCE_ORDER


def test_rendered_prompt_hash_is_the_published_one(m2):
    """The hash covers the assembled candidate prompt, not just prompt.md."""
    built = build_prompt(m2)
    assert built.sha256 == OFFICIAL_PROMPT_SHA256
    assert hashlib.sha256(built.text.encode("utf-8")).hexdigest() == OFFICIAL_PROMPT_SHA256
    # And it is genuinely the assembly, not the template alone.
    template = (SCENARIO_DIR / m2.prompt_file).read_bytes()
    assert hashlib.sha256(template).hexdigest() != OFFICIAL_PROMPT_SHA256


def test_every_source_reaches_the_rendered_prompt(m2):
    text = build_prompt(m2).text
    for name in m2.sources:
        body = (SCENARIO_DIR / name).read_text(encoding="utf-8").strip()
        first_line = body.splitlines()[0]
        assert first_line in text, f"{name} does not appear in the rendered prompt"


def test_the_frozen_manifest_agrees_with_the_rendered_prompt(m2):
    manifest = (SCENARIO_DIR / "FROZEN.yaml").read_text(encoding="utf-8")
    assert f"prompt_sha256: {OFFICIAL_PROMPT_SHA256}" in manifest


def test_every_official_run_used_the_published_prompt_hash():
    """Runs generated against different inputs are not comparable."""
    runs = sorted((REPO_ROOT / "runs" / "monday-002").rglob("run-*.json"))
    if not runs:
        pytest.skip("no official runs generated yet")
    for path in runs:
        run = json.loads(path.read_text(encoding="utf-8"))
        assert run["scenario_prompt_sha256"] == OFFICIAL_PROMPT_SHA256, path


# --------------------------------------------------------------------------
# 3. Calibration vs official isolation
# --------------------------------------------------------------------------


def test_calibration_histories_live_outside_the_official_trees():
    """Three run histories share the id monday-002. Only one is publishable."""
    for name in ("monday-002-v0.1", "monday-002-v0.2-calibration"):
        assert (REPO_ROOT / "archive" / name).is_dir(), f"{name} archive is missing"

    # The draft evaluator must not be loadable as a live evaluator any more:
    # its id is reused across two different rubrics.
    assert not (REPO_ROOT / "evaluators" / "evaluator-opus5-v0.2-draft.yaml").exists()

    # No calibration evaluation may sit in the live evaluations tree.
    live = REPO_ROOT / "evaluations"
    assert not (live / "evaluator-opus5-v0.2-draft").exists()


def test_publishing_002_cannot_overwrite_the_001_leaderboard(tmp_path):
    """#001 was published into `leaderboard/` when it was the only scenario.

    A second scenario writing `leaderboard/leaderboard.json` would silently
    destroy the public v0.1 result, so every scenario after the first gets its
    own directory.
    """
    from mondaybench.leaderboard import leaderboard_dir

    first = leaderboard_dir("monday-001", tmp_path)
    second = leaderboard_dir("monday-002", tmp_path)
    assert first != second
    assert second == tmp_path / "leaderboard" / "monday-002"
    for name in ("leaderboard.json", "leaderboard.csv", "leaderboard.md"):
        assert first / name != second / name


def test_the_official_evaluator_is_a_distinct_file_from_the_draft():
    cfg = load_evaluator("evaluator-opus5-v0.2")
    assert cfg.id == "evaluator-opus5-v0.2"
    assert cfg.scenario == "monday-002"
    assert cfg.rubric_version == "0.2"
    assert cfg.scenario_version == "0.2"
    assert cfg.model_id == "claude-opus-5"
    assert cfg.temperature == 0
    assert cfg.require_evidence is True


def test_the_scenario_is_official_and_pins_three_runs(m2):
    assert m2.status == "official"
    assert m2.is_calibration is False
    assert m2.scenario_version == "0.2"
    assert m2.rubric.version == "0.2"
    assert m2.official_runs == 3
    # The -draft suffix must be gone everywhere it was load-bearing.
    assert "draft" not in m2.benchmark_version
    assert "draft" not in m2.rubric.version


def test_rubric_still_totals_100_across_20_criteria(m2):
    assert len(m2.rubric.criteria) == 20
    assert m2.rubric.total_base_points == 100
    assert sum(m2.rubric.dimension_max.values()) == 100


# --------------------------------------------------------------------------
# 4. The "exactly three official runs" gate
# --------------------------------------------------------------------------


def _summary(slug: str, runs: int, scores: list[float]) -> ModelSummary:
    mean = sum(scores) / len(scores) if scores else 0.0
    return ModelSummary(
        model_slug=slug,
        display_name=slug,
        runs=runs,
        mean=mean,
        minimum=min(scores) if scores else 0.0,
        maximum=max(scores) if scores else 0.0,
        stddev=0.0,
        dimensions={},
        median_ttfa_ms=None,
        median_total_latency_ms=None,
        median_cost_usd=None,
        median_ttft_ms=None,
        median_output_tokens=None,
        prompt_sha256=OFFICIAL_PROMPT_SHA256,
        run_scores=scores,
        rubric_version="0.2",
        judge_model_id="claude-opus-5",
    )


def _payload() -> dict:
    return {"evaluator": "evaluator-opus5-v0.2", "integrity_warning": None}


def _blockers(summaries: list[ModelSummary]) -> list[str]:
    return official_blockers(
        _payload(),
        summaries,
        expected_models=[s.model_slug for s in summaries],
        expected_prompt_sha256=OFFICIAL_PROMPT_SHA256,
        expected_rubric_version="0.2",
        expected_evaluator_id="evaluator-opus5-v0.2",
        required_runs=3,
    )


def test_three_runs_with_three_scores_passes_the_count_gate():
    assert _blockers([_summary("glm5.2", 3, [80.0, 82.0, 84.0])]) == []


def test_two_runs_blocks_publication():
    blockers = _blockers([_summary("glm5.2", 2, [80.0, 82.0])])
    assert any("2 official run(s), 3 required" in b for b in blockers)


def test_a_missing_evaluation_blocks_even_when_the_run_count_is_right():
    blockers = _blockers([_summary("glm5.2", 3, [80.0, 82.0])])
    assert any("an evaluation is missing" in b for b in blockers)


def test_a_run_generated_against_another_prompt_blocks_publication():
    summary = _summary("glm5.2", 3, [80.0, 82.0, 84.0])
    summary.prompt_sha256 = "a" * 64
    blockers = _blockers([summary])
    assert any("published scenario is" in b for b in blockers)


def test_a_draft_rubric_evaluation_blocks_publication():
    summary = _summary("glm5.2", 3, [80.0, 82.0, 84.0])
    summary.rubric_version = "0.2-draft"
    blockers = _blockers([summary])
    assert any("official evaluator pins 0.2" in b for b in blockers)


# --------------------------------------------------------------------------
# 5 & 6. What the penalty prompt must say
#
# The judge for this scenario is a recorded Opus 5 session reading these
# instructions, so the shipped prompt text *is* the implementation. Testing it
# is the only regression guard available, and it is a real one: the calibration
# round showed the draft wording was ambiguous on exactly this point.
# --------------------------------------------------------------------------


@pytest.fixture(scope="module")
def penalty_prompt() -> str:
    raw = (
        REPO_ROOT / "evaluators" / "monday-002" / "penalty-judge-prompt.md"
    ).read_text(encoding="utf-8")
    # Collapsed to one line: the prompt is hard-wrapped prose, and a test that
    # breaks when a sentence rewraps is testing the wrong thing.
    return " ".join(raw.split())


def test_major_planning_error_is_scoped_to_unexecutable_plans(penalty_prompt):
    assert "violates a stated hard dependency" in penalty_prompt
    assert "impossible under the supplied timing or availability constraints" in penalty_prompt


def test_rejecting_a_viable_alternative_is_not_a_planning_penalty(penalty_prompt):
    """The main calibration failure must be priced by the rubric, not twice."""
    assert "Do not apply it merely because the candidate incorrectly rejects a viable" in (
        penalty_prompt
    )
    assert "Option B is impossible, so choose A." in penalty_prompt
    assert "No penalty:" in penalty_prompt


def test_the_prompt_forbids_double_punishment_generally(penalty_prompt):
    assert "Never penalize an" in penalty_prompt
    assert "double punishment" in penalty_prompt


def test_listing_a_stale_task_under_do_not_is_not_a_prohibited_action(penalty_prompt):
    assert "Listing a stale" in penalty_prompt
    assert "must never be penalized" in penalty_prompt
    assert "directs the user to perform the act now" in penalty_prompt


def test_invented_causality_is_still_a_material_hallucination(penalty_prompt):
    """Qwen 3.6's calibration penalty must remain reachable."""
    assert "invented causality" in penalty_prompt.lower()
    assert "causes or explains another when no source establishes the link" in penalty_prompt
    # ...but a clearly-labelled hypothesis must not be.
    assert "explicitly as a hypothesis" in penalty_prompt


def test_all_four_penalty_types_survive(penalty_prompt):
    for name in (
        "MATERIAL_HALLUCINATION",
        "PROHIBITED_ACTION",
        "MAJOR_PLANNING_ERROR",
        "MAJOR_CONTRADICTION",
    ):
        assert name in penalty_prompt


def test_the_rubric_still_declares_all_four_penalty_types(m2):
    assert set(m2.rubric.penalties) >= {
        "MATERIAL_HALLUCINATION",
        "PROHIBITED_ACTION",
        "MAJOR_PLANNING_ERROR",
        "MAJOR_CONTRADICTION",
    }


# --------------------------------------------------------------------------
# 7 & 8. Empty final answer vs truncation
# --------------------------------------------------------------------------


def _sse(events: list[dict]) -> str:
    return "".join(f"data: {json.dumps(e)}\n\n" for e in events) + "data: [DONE]\n\n"


def _delta(**fields) -> dict:
    return {"choices": [{"index": 0, "delta": dict(fields)}]}


def _run_stream(events: list[dict], monkeypatch, budget: int = 32000):
    from tests.test_openai_compatible import _stub_client, make_provider

    _stub_client(_sse(events), monkeypatch)
    provider = make_provider()
    return provider.generate(
        model_id="deepseek-v4-flash",
        system_prompt=None,
        user_prompt="x",
        generation_config={"max_output_tokens": budget, "stream": True},
    )


def test_reasoning_then_stop_with_no_answer_is_not_blamed_on_the_budget(monkeypatch):
    """DeepSeek burned 70k characters of reasoning and then simply stopped.

    Advising a bigger budget there is wrong and expensive: the model was not
    truncated, it ended its turn. The two cases must not share a message.
    """
    events = [
        _delta(reasoning_content="a very long chain of thought " * 500),
        {"choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]},
    ]
    with pytest.raises(ProviderError) as excinfo:
        _run_stream(events, monkeypatch)
    exc = excinfo.value
    assert exc.kind == "empty_final_answer"
    message = str(exc)
    assert "finish_reason=stop" in message
    assert "not a truncation" in message
    assert "the output budget is not the cause" in message


def test_truncation_still_names_the_budget_as_the_cause(monkeypatch):
    events = [
        _delta(reasoning_content="a very long chain of thought " * 500),
        {"choices": [{"index": 0, "delta": {}, "finish_reason": "length"}]},
    ]
    with pytest.raises(ProviderError) as excinfo:
        _run_stream(events, monkeypatch, budget=4000)
    exc = excinfo.value
    assert exc.kind == "truncated_by_budget"
    message = str(exc)
    assert "finish_reason=length" in message
    assert "max_output_tokens" in message


def test_the_two_failure_kinds_are_distinguishable_without_reading_prose():
    """A caller must be able to branch on `kind`, not on message text."""
    truncated = ProviderError("x", kind="truncated_by_budget")
    empty = ProviderError("y", kind="empty_final_answer")
    assert truncated.kind != empty.kind


def test_failed_attempts_record_their_kind(tmp_path):
    from mondaybench import runner

    target = runner.log_failed_attempt(
        scenario_id="monday-002",
        model_slug="deepseek-v4-flash",
        run_number=1,
        error="model produced reasoning and then ended its turn",
        kind="empty_final_answer",
        root=tmp_path,
    )
    entry = json.loads(target.read_text(encoding="utf-8").strip().splitlines()[-1])
    assert entry["kind"] == "empty_final_answer"


# --------------------------------------------------------------------------
# 9. monday-001 integrity
# --------------------------------------------------------------------------


def test_monday_001_frozen_content_is_untouched():
    """#002 work must never move #001's bytes."""
    manifest = REPO_ROOT / "scenarios" / "monday-001" / "FROZEN.yaml"
    import yaml

    data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
    assert data["prompt_sha256"] == (
        "ed4d7beb1d7d1029c36eb8533e449027e0dc1a1047f8a38951a91781a0a5e398"
    )
    for name, expected in data["files"].items():
        actual = hashlib.sha256(
            (REPO_ROOT / "scenarios" / "monday-001" / name).read_bytes()
        ).hexdigest()
        assert actual == expected, f"monday-001/{name} changed"


def test_monday_001_published_leaderboard_is_untouched():
    payload = json.loads(
        (REPO_ROOT / "leaderboard" / "leaderboard.json").read_text(encoding="utf-8")
    )
    assert payload["scenario"] == "monday-001"
    assert payload["evaluator"] == "evaluator-opus5-v0.1"
    ranked = {row["display_name"]: row["score"]["mean"] for row in payload["models"]}
    # The published v0.1 result, to one decimal, as it must stay.
    assert ranked["GLM 5.3 Flash"] == pytest.approx(98.0, abs=0.05)
    assert ranked["Gemma 4"] == pytest.approx(70.7, abs=0.05)


def test_monday_001_runs_all_carry_its_own_prompt_hash():
    for path in sorted((REPO_ROOT / "runs" / "monday-001").rglob("run-*.json")):
        run = json.loads(path.read_text(encoding="utf-8"))
        assert run["scenario_prompt_sha256"] == (
            "ed4d7beb1d7d1029c36eb8533e449027e0dc1a1047f8a38951a91781a0a5e398"
        ), path
