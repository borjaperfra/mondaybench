"""The committed-secret check must catch values and ignore prose.

The first version flagged the word "Bearer" inside an explanatory comment in
models.yaml, failing validation on a file that held no secret at all. A check
that cries wolf gets switched off, so precision matters here.
"""

from __future__ import annotations

from pathlib import Path

from mondaybench.config import find_literal_credentials, repo_root


# --------------------------------------------------------------------------
# must catch
# --------------------------------------------------------------------------


def test_catches_an_sk_key_assigned_in_yaml():
    hits = find_literal_credentials("  api_key: sk-abcdef0123456789abcdef\n")
    assert len(hits) == 1
    assert hits[0][0] == 1


def test_catches_a_bearer_token():
    hits = find_literal_credentials('  header: "Bearer abcdef0123456789abcdef"\n')
    assert len(hits) == 1
    assert "bearer" in hits[0][1]


def test_catches_an_inline_api_key_value():
    hits = find_literal_credentials("api_key: someLongLiteralValue\n")
    assert len(hits) == 1


def test_reports_the_right_line_number():
    text = "models:\n  a:\n    model_id: x\n    api_key: sk-abcdef0123456789abcdef\n"
    assert find_literal_credentials(text)[0][0] == 4


# --------------------------------------------------------------------------
# must not flag
# --------------------------------------------------------------------------


def test_prose_mention_of_bearer_in_a_comment_is_ignored():
    text = "  # Verified that Bearer is the right scheme and /v1/models the right path\n"
    assert find_literal_credentials(text) == []


def test_api_key_env_is_correct_usage():
    assert find_literal_credentials("    api_key_env: HELMCODE_API_KEY\n") == []


def test_base_url_env_is_correct_usage():
    assert find_literal_credentials("    base_url_env: NAN_BASE_URL\n") == []


def test_short_sk_lookalikes_are_not_flagged():
    # Ordinary words and hyphenated identifiers must not trip the sk- pattern.
    for line in ("  notes: risk-adjusted\n", "  slug: task-runner\n", "  x: sk-short\n"):
        assert find_literal_credentials(line) == [], line


def test_null_api_key_env_is_fine():
    assert find_literal_credentials("  api_key_env: null\n") == []


# --------------------------------------------------------------------------
# the real files
# --------------------------------------------------------------------------


def test_repo_configs_hold_no_credentials():
    paths = [repo_root() / "models.yaml", *(repo_root() / "evaluators").glob("*.yaml")]
    for path in paths:
        assert find_literal_credentials(path.read_text(encoding="utf-8")) == [], path.name


def test_env_example_holds_no_filled_key():
    # The template must ship with blank values.
    text = (repo_root() / ".env.example").read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.startswith(("HELMCODE_API_KEY", "NAN_API_KEY", "ANTHROPIC_API_KEY", "JUDGE_API_KEY")):
            assert line.split("=", 1)[1].strip() == "", line.split("=")[0]


def test_dotenv_is_gitignored():
    gitignore = (repo_root() / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert ".env" in [line.strip() for line in gitignore]
