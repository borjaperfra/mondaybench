"""The cost layer's invariants, with GLM 5.3's two pricing bases as the case.

Monday Score is quality only. Nothing here builds a composite, a value score or
a quality-per-dollar ranking; every assertion compares a cost with a cost or a
score with a score.

Read-only. No model is called and no scoring artifact is touched.
"""

from __future__ import annotations

import json

import pytest

from mondaybench.config import repo_root

ROOT = repo_root()
COST = ROOT / "analysis" / "cost-value"
PUB = json.loads((COST / "publication-data.json").read_text(encoding="utf-8"))
PARETO = json.loads((COST / "pareto.json").read_text(encoding="utf-8"))
ROWS = {m["model"]: m for m in PUB["models"]}

# Published before GLM 5.3 was added. A hard gate: adding a model must not
# recalculate the universe.
FROZEN_COSTS = {
    "qwen3.8-flash": [12.61, 15.56],
    "glm5.3-flash": 10.71,
    "claude-fable-5-1": 456.27,
    "deepseek-v4-flash": [12.94, 25.88],
    "mimo-v2.5": 3.33,
    "glm5.2": 39.5,
    "qwen3.6": 7.7,
    "gemma4": 0.44,
}


def high(value):
    return max(value) if isinstance(value, list) else value


# ---------------------------------------------------------------------------
# A + B - each figure declares its own basis
# ---------------------------------------------------------------------------


def test_A_glm5_3_first_party_cost_is_the_zai_list_basis():
    row = ROWS["glm5.3"]
    assert row["price_basis"] == "First-party"
    assert row["pricing_class"] == "FIRST_PARTY_LIST"
    assert row["first_party_vendor"] == "Z.AI"
    assert row["first_party_sku"] == "GLM-5.3"
    assert row["first_party_input_per_million"] == 1.40
    assert row["first_party_output_per_million"] == 4.40
    assert row["normalized_first_party_cost_per_1k"] == pytest.approx(99.20, abs=0.01)
    # and emphatically NOT the gateway meter
    assert row["normalized_cost_per_1k"] != pytest.approx(5.67, abs=0.01)


def test_B_glm5_3_route_cost_is_the_gateway_metered_basis():
    row = ROWS["glm5.3"]
    assert row["provider_pricing_class"] == "GATEWAY_METERED"
    assert row["provider_price_basis"] == "Helmcode route"
    assert row["provider_name"] == "Helmcode"
    assert row["provider_public_cost_per_1k"] == pytest.approx(5.67, abs=0.01)
    assert row["provider_public_cost_per_100k"] == pytest.approx(567.49, abs=0.5)
    assert row["provider_public_cost_per_1m"] == pytest.approx(5674.87, abs=5)


def test_the_route_basis_is_never_labelled_as_a_vendor_price():
    row = ROWS["glm5.3"]
    forbidden = ("Z.AI price", "first-party price", "discounted", "wholesale")
    blob = json.dumps(
        {k: v for k, v in row.items() if k.startswith("provider")}, ensure_ascii=False
    ).lower()
    for phrase in forbidden:
        assert phrase.lower() not in blob, phrase
    # nor is a commercial mechanism asserted anywhere in the row
    for phrase in ("discount", "wholesale", "subsidy", "quantiz", "batching"):
        assert phrase not in row["notes"].lower(), phrase


# ---------------------------------------------------------------------------
# C - the two bases can never be merged
# ---------------------------------------------------------------------------


def test_C_the_two_bases_are_not_merged_into_a_range():
    row = ROWS["glm5.3"]
    assert row["cost_kind"] == "POINT"
    assert not isinstance(row["normalized_cost_per_1k"], list)
    assert not isinstance(row["provider_public_cost_per_1k"], list)
    # the two must not appear as endpoints of one figure anywhere
    for value in (row["normalized_cost_per_1k"], row["provider_public_cost_per_1k"]):
        assert not isinstance(value, (list, tuple))
    assert "never" in PUB["cost_basis"].lower() or "never mixed" in PUB["cost_basis"].lower()


def test_C_no_published_figure_spans_two_bases():
    for slug, row in ROWS.items():
        figure = row["normalized_cost_per_1k"]
        if isinstance(figure, list):
            # a range is a range WITHIN one basis - time of day, or region
            assert row["pricing_class"] == "FIRST_PARTY_LIST", slug
            assert len(figure) == 2 and figure[0] <= figure[1], slug


# ---------------------------------------------------------------------------
# D + E - Pareto under each basis, computed not asserted
# ---------------------------------------------------------------------------


def _frontier(points):
    return sorted(
        name
        for name, score, price in points
        if not any(
            other_score >= score and other_price <= price
            and (other_score > score or other_price < price)
            for other, other_score, other_price in points
            if other != name
        )
    )


def test_D_glm5_3_is_dominated_on_the_first_party_frontier():
    points = [
        (m["model"], m["score"], high(m["normalized_cost_per_1k"]))
        for m in PUB["models"]
        if m.get("normalized_first_party_cost_per_1k") not in (None, "UNKNOWN")
    ]
    computed = _frontier(points)
    assert "glm5.3" not in computed
    assert computed == sorted(e["model"] for e in PARETO["primary"]["frontier"])
    entry = next(e for e in PARETO["primary"]["dominated"] if e["model"] == "glm5.3")
    assert entry["dominated_by"], "a dominated model must name what dominates it"


def test_D_the_first_party_frontier_did_not_move():
    assert sorted(e["model"] for e in PARETO["primary"]["frontier"]) == [
        "glm5.3-flash", "qwen3.8-flash",
    ]


def test_E_glm5_3_joins_the_provider_frontier():
    points = []
    for m in PUB["models"]:
        provider = m.get("provider_public_cost_per_1k")
        value = provider if isinstance(provider, (int, float)) else m["normalized_cost_per_1k"]
        points.append((m["model"], m["score"], high(value)))
    computed = _frontier(points)
    assert "glm5.3" in computed
    assert computed == sorted(e["model"] for e in PARETO["extended_provider"]["frontier"])


def test_E_glm5_3_displaces_nobody_on_the_provider_frontier():
    """It is added to the frontier, not swapped for a member of it."""
    after = {e["model"] for e in PARETO["extended_provider"]["frontier"]}
    assert {"gemma4", "mimo-v2.5", "glm5.3-flash", "qwen3.8-flash"} <= after


# ---------------------------------------------------------------------------
# F - no provisional rows remain (suite v1.10 made every row official)
# ---------------------------------------------------------------------------
#
# Until v1.10 this test asserted that provisional models could not move an
# official frontier, against a recorded `frontier_without_provisional`. Claude
# Opus 5 and Claude Fable 5.1 became official in v1.10, so there is one
# frontier per view and the "without" lists are retired. A row that turns
# provisional again would need that guarantee back; this fails first.


@pytest.mark.parametrize("view", ["primary", "extended_provider"])
def test_F_every_cost_row_is_official_and_there_is_one_frontier(view):
    assert not [m["model"] for m in PUB["models"] if m.get("provisional")]
    assert "frontier_without_provisional" not in PARETO[view]
    assert PARETO[view]["frontier"]


# ---------------------------------------------------------------------------
# G + H - basis changes cost, never quality; efficiency is independent
# ---------------------------------------------------------------------------


def test_G_switching_basis_changes_cost_and_not_the_monday_score():
    row = ROWS["glm5.3"]
    assert row["score"] == 93.73
    assert row["normalized_first_party_cost_per_1k"] != row["provider_public_cost_per_1k"]
    # the score is a single value on the row; there is no per-basis score
    assert not any(k.endswith("_score") and k != "score" for k in row)


def test_H_efficiency_is_published_despite_the_contested_pricing_identity():
    row = ROWS["glm5.3"]
    assert row["identity_confidence"] == "CONTESTED"
    # ...and the efficiency figures are present and real anyway
    assert row["median_ttfa_ms"] == pytest.approx(253260.4, abs=1)
    assert row["mean_output_tokens"] == pytest.approx(21298.6, abs=0.5)
    assert row["mean_reasoning_tokens"] == pytest.approx(19288.1, abs=0.5)
    assert row["provisional"] is False


# ---------------------------------------------------------------------------
# I + J - unit and billing discipline
# ---------------------------------------------------------------------------


def test_I_ttfa_is_stored_in_milliseconds_and_converted_once():
    """The stored field is named for its unit; seconds are a rendering.

    The invariant is that there is exactly ONE latency field per row and it is
    the millisecond one, so no consumer can divide by 1000 twice. A magnitude
    threshold would be the wrong test: qwen3.6's median TTFA really is 978 ms,
    because it does not reason before answering.
    """
    for slug, row in ROWS.items():
        latency_fields = [k for k in row if "ttfa" in k or "ttft" in k or "latency" in k]
        assert latency_fields == ["median_ttfa_ms"], f"{slug}: {latency_fields}"
        assert isinstance(row["median_ttfa_ms"], (int, float)), slug
    # and the one conversion the page performs
    assert ROWS["glm5.3"]["median_ttfa_ms"] / 1000 == pytest.approx(253.26, abs=0.01)
    assert ROWS["glm5.3"]["median_ttfa_ms"] == pytest.approx(253260.4, abs=1)


def test_J_reasoning_tokens_are_not_added_to_output_for_billing():
    """`reasoning_tokens` sits inside `output_tokens`; billing output bills it."""
    for slug, row in ROWS.items():
        if row.get("mean_reasoning_tokens"):
            assert row["mean_reasoning_tokens"] <= row["mean_output_tokens"], slug
    row = ROWS["glm5.3"]
    # the first-party figure must reconcile with output alone, not output+reasoning
    inflated = (
        4669.2 * 1.40 + (row["mean_output_tokens"] + row["mean_reasoning_tokens"]) * 4.40
    ) / 1e6 * 1000
    assert row["normalized_cost_per_1k"] < inflated * 0.9


# ---------------------------------------------------------------------------
# K - nothing that was published moved
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("slug,expected", sorted(FROZEN_COSTS.items()))
def test_K_existing_published_costs_are_invariant(slug, expected):
    assert ROWS[slug]["normalized_cost_per_1k"] == expected


def test_K_adding_a_model_did_not_change_any_other_row_basis():
    for slug, row in ROWS.items():
        if slug == "glm5.3":
            continue
        assert row["pricing_class"] in {"FIRST_PARTY_LIST", "PROVIDER_PUBLIC"}
        # no pre-existing row acquired a second basis
        assert row.get("provider_pricing_class") is None, slug


# ---------------------------------------------------------------------------
# L - pricing artifacts are outside the frozen quality release
# ---------------------------------------------------------------------------


def test_L_updating_pricing_does_not_break_the_quality_release():
    from mondaybench.suite import GROUP_EXCLUDES, GROUP_POLICY, GROUPS, collect_group

    pricing = collect_group(GROUPS["pricing"], ROOT, GROUP_EXCLUDES.get("pricing", ()))
    assert "analysis/cost-value/publication-data.json" in pricing
    assert "analysis/cost-value/pareto.json" in pricing
    assert GROUP_POLICY["pricing"] == "mutable"
    for name, policy in GROUP_POLICY.items():
        if policy == "mutable":
            continue
        files = collect_group(GROUPS[name], ROOT, GROUP_EXCLUDES.get(name, ()))
        assert not any(p.startswith("analysis/cost-value/") for p in files), name


def test_the_pricing_snapshots_are_versioned_and_the_old_one_is_preserved():
    import hashlib

    snapshots = PUB["pricing_snapshots"]
    assert snapshots["first_party"]["sha256"].startswith("ec4dcc85")
    addendum = snapshots["first_party_addendum"]
    assert addendum["id"] == "pricing-2026-09-03"
    assert addendum["inherits"] == snapshots["first_party"]["id"]
    assert addendum["adds"] == ["glm5.3"]
    for snapshot_id, sha in (
        ("pricing-snapshot-2026-09-02", snapshots["first_party"]["sha256"]),
        ("pricing-snapshot-2026-09-03", addendum["sha256"]),
    ):
        path = COST / f"{snapshot_id}.yaml"
        assert hashlib.sha256(path.read_bytes()).hexdigest() == sha, snapshot_id
        companion = COST / f"{snapshot_id}.sha256"
        assert companion.read_text(encoding="utf-8").split()[0] == sha, snapshot_id
