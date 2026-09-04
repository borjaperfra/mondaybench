"""Rebuild the cost publication data and the dual Pareto, adding GLM 5.3.

REPRODUCIBLE, NOT HAND-EDITED. Every existing row is carried through untouched
and asserted unchanged; the only new content is derived from the run artifacts
and the frozen pricing snapshots. Calls no model. Touches no score, run, verdict
or evaluation.

WHY GLM 5.3 IS THE FIRST TWO-BASIS ROW. Z.AI lists GLM-5.3 at $1.4 / $4.4;
the Helmcode route the benchmark ran on metered $0.075 / $0.25. Those are two
different questions - "what does this model cost at the vendor's price" and
"what did this route cost" - and the schema already separates them:
`normalized_first_party_cost_per_1k` and `provider_public_cost_per_1k`, with
`cost_basis` stating they are never mixed. Every other model answers one of the
two questions. GLM 5.3 answers both, and neither answer is a range over the
other.

WHAT THIS DELIBERATELY DOES NOT DO. It does not explain WHY the route is
cheaper. No discount, wholesale, batching, quantization or deployment claim is
made or implied anywhere in the output.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).parent
sys.path.insert(0, str(ROOT))

spec = importlib.util.spec_from_file_location("glm53cost", HERE / "_glm53_cost.py")
cost = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cost)

PUB = HERE / "publication-data.json"
PARETO = HERE / "pareto.json"
SLUG = "glm5.3"

FIRST_PARTY_SNAPSHOT = "pricing-2026-09-03"
FIRST_PARTY_FILE = HERE / "pricing-snapshot-2026-09-03.yaml"


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dominated_by(point, others):
    """A dominates B iff A.score >= B.score AND A.cost <= B.cost, one strict."""
    slug, score, price = point
    return sorted(
        other
        for other, other_score, other_price in others
        if other != slug
        and other_score >= score
        and other_price <= price
        and (other_score > score or other_price < price)
    )


def frontier(points):
    on, off = [], []
    for point in points:
        losers = dominated_by(point, points)
        entry = {"model": point[0], "score": point[1], "cost_per_1k": point[2],
                 "dominated_by": losers}
        (off if losers else on).append(entry)
    on.sort(key=lambda e: e["cost_per_1k"])
    off.sort(key=lambda e: e["cost_per_1k"])
    return on, off


def figure_high(value):
    """The conservative end of a published figure, as the 2026-09-02 gate sets."""
    return max(value) if isinstance(value, list) else value


def main() -> None:
    pub = json.loads(PUB.read_text(encoding="utf-8"))
    before = {m["model"]: json.dumps(m, sort_keys=True) for m in pub["models"]}
    before_costs = {
        m["model"]: (m.get("normalized_cost_per_1k"),
                     m.get("normalized_first_party_cost_per_1k"),
                     m.get("provider_public_cost_per_1k"))
        for m in pub["models"]
    }

    if any(m["model"] == SLUG for m in pub["models"]):
        pub["models"] = [m for m in pub["models"] if m["model"] != SLUG]

    # ---- derive GLM 5.3 from the run artifacts ----------------------------
    runs = cost.official_runs(SLUG)
    usages = [cost.usage_of(r) for r in runs]
    perfs = [(r.get("performance") or {}) for r in runs]
    ttfas = sorted(p["ttfa_ms"] for p in perfs if p.get("ttfa_ms"))

    first_party = cost.normalized_cost(runs, cost.LIST[SLUG])
    metered_total = sum(
        ((r.get("economics") or {}).get("total_cost_usd") or 0) for r in runs
    )
    metered_per_task = metered_total / len(runs)

    assert all(u["reasoning"] <= u["output"] for u in usages), (
        "reasoning must sit inside output; billing output once bills it once"
    )

    row = {
        "model": SLUG,
        "display_name": "GLM 5.3",
        "score": 93.73,
        "quality_band": "SECOND",
        "median_ttfa_ms": round(ttfas[len(ttfas) // 2], 1),
        "mean_output_tokens": round(sum(u["output"] for u in usages) / len(usages), 1),
        "mean_reasoning_tokens": round(sum(u["reasoning"] for u in usages) / len(usages), 1),
        "pricing_confidence": "HIGH",
        # The PRICE is high confidence and first-party. What is contested is
        # whether that price describes the route the benchmark ran on.
        "identity_confidence": "CONTESTED",
        "provisional": False,
        "notes": (
            "Two bases, never merged. Z.AI's public GLM-5.3 list price normalizes to "
            "$99.20/1k; the Helmcode route the benchmark ran on metered $5.67/1k, read from "
            "each scored run's own economics block. The gateway does not expose enough "
            "deployment information to reconcile them, and no commercial explanation is "
            "asserted. The served model id was glm5.3 on all 15 runs, never glm5.3-flash, so "
            "generation identity is unaffected and the Monday Score stands."
        ),
        # PRIMARY = first-party, matching `cost_basis`: the primary Pareto is
        # first-party only.
        "normalized_cost_per_task": first_party["per_task"],
        "normalized_cost_per_1k": first_party["per_1k"],
        "cost_kind": "POINT",
        "pricing_class": "FIRST_PARTY_LIST",
        "price_basis": "First-party",
        "pricing_snapshot": FIRST_PARTY_SNAPSHOT,
        "normalized_first_party_cost_per_1k": first_party["per_1k"],
        "normalized_first_party_cost_per_100k": first_party["per_100k"],
        "normalized_first_party_cost_per_1m": first_party["per_1m"],
        "first_party_vendor": "Z.AI",
        "first_party_sku": "GLM-5.3",
        "first_party_input_per_million": cost.LIST[SLUG]["in"],
        "first_party_output_per_million": cost.LIST[SLUG]["out"],
        "first_party_pricing_identity": "CONTESTED",
        # SECOND BASIS - the route the benchmark actually ran on.
        "provider_public_cost_per_1k": round(metered_per_task * 1_000, 2),
        "provider_public_cost_per_task": round(metered_per_task, 6),
        "provider_public_cost_per_100k": round(metered_per_task * 100_000, 2),
        "provider_public_cost_per_1m": round(metered_per_task * 1_000_000, 2),
        "provider_name": "Helmcode",
        "provider_model_id": SLUG,
        "provider_pricing_class": "GATEWAY_METERED",
        "provider_price_basis": "Helmcode route",
        "provider_pricing_identity": "OBSERVED_ROUTE",
        "provider_pricing_snapshot": FIRST_PARTY_SNAPSHOT,
        "benchmark_run_identity": "STRONG_MATCH",
        "publication_pricing_ref": "DUAL_BASIS",
    }

    pub["models"].append(row)
    pub["models"].sort(key=lambda m: -m["score"])

    # ---- invariance gate --------------------------------------------------
    changed = []
    for model, blob in before.items():
        now = next((m for m in pub["models"] if m["model"] == model), None)
        if now is None:
            changed.append(f"{model}: row disappeared")
        elif json.dumps(now, sort_keys=True) != blob:
            changed.append(f"{model}: row content changed")
    for model, costs in before_costs.items():
        now = next((m for m in pub["models"] if m["model"] == model), None)
        if now and (now.get("normalized_cost_per_1k"),
                    now.get("normalized_first_party_cost_per_1k"),
                    now.get("provider_public_cost_per_1k")) != costs:
            changed.append(f"{model}: a published cost moved")
    if changed:
        raise SystemExit("STOP - existing cost data would change:\n  " + "\n  ".join(changed))

    pub["generated_at"] = "2026-09-03"
    pub["pricing_snapshots"]["first_party_addendum"] = {
        "id": FIRST_PARTY_SNAPSHOT,
        "sha256": sha256_of(FIRST_PARTY_FILE),
        "adds": [SLUG],
        "inherits": pub["pricing_snapshots"]["first_party"]["id"],
    }
    pub["price_basis_labels"]["Helmcode route"] = (
        "Cost metered by the Helmcode gateway on the benchmark runs themselves. An observed "
        "route cost, not a vendor list price."
    )
    pub["cost_basis"] = (
        "Two classes, never mixed: normalized_first_party_cost (vendor list price) and "
        "provider_public_cost (third-party route or observed route cost). The primary Pareto "
        "uses first-party only. A model may carry both; they are two answers to two questions "
        "and are never combined into a range."
    )

    PUB.write_text(json.dumps(pub, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8", newline="\n")

    # ---- dual Pareto ------------------------------------------------------
    pareto = json.loads(PARETO.read_text(encoding="utf-8"))

    # A model is in the first-party pool iff it HAS a first-party price. That
    # includes ranges: qwen3.8-flash and deepseek-v4-flash publish
    # [low, high] and both sit in the published primary frontier. Testing for a
    # bare number silently dropped them and moved a frontier that must not move.
    def has_first_party(m):
        return m.get("normalized_first_party_cost_per_1k") not in (None, "UNKNOWN")

    primary_points = [
        (m["model"], m["score"], figure_high(m["normalized_cost_per_1k"]))
        for m in pub["models"] if has_first_party(m)
    ]
    on, off = frontier(primary_points)
    excluded = sorted(m["model"] for m in pub["models"] if not has_first_party(m))
    pareto["primary"]["frontier"] = on
    pareto["primary"]["dominated"] = off
    pareto["primary"]["excluded_no_first_party_price"] = excluded

    # extended: first-party where that is all a model has, provider cost where
    # it has one. GLM 5.3 contributes its ROUTE cost here, which is the whole
    # point of the second basis.
    extended_points = []
    for m in pub["models"]:
        provider = m.get("provider_public_cost_per_1k")
        value = provider if isinstance(provider, (int, float)) else m.get("normalized_cost_per_1k")
        if isinstance(value, (int, float, list)):
            extended_points.append((m["model"], m["score"], figure_high(value)))
    on_e, off_e = frontier(extended_points)
    pareto["extended_provider"]["frontier"] = on_e
    pareto["extended_provider"]["dominated"] = off_e
    pareto["extended_provider"]["basis"] = (
        "FIRST_PARTY_LIST + PROVIDER_PUBLIC (v2) + observed route cost (glm5.3)"
    )

    # provisional models must not be able to change the official frontier
    for view in ("primary", "extended_provider"):
        pool = primary_points if view == "primary" else extended_points
        provisional = {m["model"] for m in pub["models"] if m.get("provisional")}
        without, _ = frontier([p for p in pool if p[0] not in provisional])
        pareto[view]["frontier_without_provisional"] = [e["model"] for e in without]
        assert [e["model"] for e in without] == [
            e["model"] for e in (on if view == "primary" else on_e)
            if e["model"] not in provisional
        ], f"{view}: a provisional model changed the official frontier"

    pareto["first_party_snapshot_addendum_sha256"] = sha256_of(FIRST_PARTY_FILE)
    PARETO.write_text(json.dumps(pareto, indent=2, ensure_ascii=False) + "\n",
                      encoding="utf-8", newline="\n")

    flash = next(m for m in pub["models"] if m["model"] == "glm5.3-flash")
    print(f"GLM 5.3 added. existing rows unchanged: {len(before)}")
    print(f"  first-party  ${row['normalized_cost_per_task']:.6f}/task  "
          f"${row['normalized_cost_per_1k']}/1k  ${row['normalized_first_party_cost_per_100k']}/100k  "
          f"${row['normalized_first_party_cost_per_1m']}/1M")
    print(f"  route        ${row['provider_public_cost_per_task']:.6f}/task  "
          f"${row['provider_public_cost_per_1k']}/1k  ${row['provider_public_cost_per_100k']}/100k  "
          f"${row['provider_public_cost_per_1m']}/1M")
    print(f"  ratio list/route: {row['normalized_cost_per_task'] / row['provider_public_cost_per_task']:.2f}x")
    print(f"  vs GLM 5.3 Flash: score {93.73 - flash['score']:+.2f}, "
          f"first-party cost x{row['normalized_cost_per_1k'] / flash['normalized_cost_per_1k']:.2f}")
    print(f"\nprimary frontier      : {[e['model'] for e in on]}")
    print(f"  glm5.3 dominated by : {next(e['dominated_by'] for e in off if e['model'] == SLUG) if any(e['model'] == SLUG for e in off) else 'ON FRONTIER'}")
    print(f"extended frontier     : {[e['model'] for e in on_e]}")
    print(f"  glm5.3 on it        : {any(e['model'] == SLUG for e in on_e)}")


if __name__ == "__main__":
    main()
