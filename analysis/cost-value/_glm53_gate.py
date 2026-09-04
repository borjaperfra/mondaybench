"""GLM 5.3 cost gate: Pareto, comparisons and the editorial claims, computed
under each internally consistent pricing basis.

READ-ONLY over scoring artifacts. Calls no model. Publishes nothing: it decides
whether GLM 5.3 CAN be published, and on what basis.

THE PROBLEM THIS EXISTS TO SETTLE. Z.AI's own pricing page lists GLM-5.3 at
$1.4 / $4.4 per million. The Helmcode gateway metered the 15 scored runs at
$0.075 / $0.25 - 5.4% of that list. For the sibling SKU GLM-5.2 the same gateway
metered exactly 50% of list, which the 2026-09-02 gate documented. So the two
figures cannot both describe the same SKU on the same basis, and a comparison
that mixes them is not a comparison.
"""
from __future__ import annotations

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

PUB = json.loads((HERE / "publication-data.json").read_text(encoding="utf-8"))


def existing_rows() -> dict[str, dict]:
    return {m["model"]: m for m in PUB["models"]}


def cost_for(row: dict, end: str = "high") -> float:
    """A single number for ordering. RANGE models use the conservative end."""
    value = row["normalized_cost_per_1k"]
    if isinstance(value, list):
        return max(value) if end == "high" else min(value)
    return value


def pareto(points: list[tuple[str, float, float]]) -> list[str]:
    """A dominates B iff score >= and cost <=, with at least one strict."""
    frontier = []
    for name, score, price in points:
        dominated = any(
            (other_score >= score and other_price <= price)
            and (other_score > score or other_price < price)
            for other, other_score, other_price in points
            if other != name
        )
        if not dominated:
            frontier.append(name)
    return sorted(frontier, key=lambda n: -next(s for m, s, _ in points if m == n))


def main() -> None:
    rows = existing_rows()
    glm53 = cost.normalized_cost(cost.official_runs("glm5.3"), cost.LIST["glm5.3"])
    meter_runs = cost.official_runs("glm5.3")
    metered = sum(
        ((r.get("economics") or {}).get("total_cost_usd") or 0) for r in meter_runs
    ) / len(meter_runs)

    bases = {
        "FIRST_PARTY_LIST": {
            "glm5.3_per_1k": glm53["per_1k"],
            "what_it_is": ("Z.AI's published list price for GLM-5.3, the same basis every other "
                           "non-provisional row in this table uses."),
        },
        "GATEWAY_METERED": {
            "glm5.3_per_1k": round(metered * 1000, 2),
            "what_it_is": ("What the Helmcode gateway actually charged, read from each scored "
                           "run's own `economics` block. Not a list price, and no other Z.AI row "
                           "in this table is on this basis."),
        },
    }

    report: dict = {
        "read_only": True,
        "model_calls": 0,
        "published_nothing": True,
        "bases": bases,
        "pareto": {},
        "comparisons": {},
        "editorial_claims": {},
    }

    # ---- Pareto under each basis ------------------------------------------
    official = [m for m, r in rows.items() if not r.get("provisional")]
    for basis, block in bases.items():
        points_before = [
            (m, rows[m]["score"], cost_for(rows[m])) for m in official
        ]
        points_after = points_before + [("glm5.3", 93.73, block["glm5.3_per_1k"])]
        before = pareto(points_before)
        after = pareto(points_after)
        report["pareto"][basis] = {
            "official_frontier_before": before,
            "official_frontier_after": after,
            "glm5.3_on_frontier": "glm5.3" in after,
            "displaced": sorted(set(before) - set(after)),
            "note": ("RANGE models are placed at the conservative (expensive) end, as the "
                     "2026-09-02 gate specifies, so no model is flattered."),
        }
        # provisional-inclusive frontier, kept separate
        points_all = [
            (m, r["score"], cost_for(r)) for m, r in rows.items()
        ] + [("glm5.3", 93.73, block["glm5.3_per_1k"])]
        report["pareto"][basis]["extended_frontier_with_provisional"] = pareto(points_all)

    # ---- pairwise comparisons ----------------------------------------------
    def perf(slug):
        runs = cost.official_runs(slug)
        us = [cost.usage_of(r) for r in runs]
        ps = [(r.get("performance") or {}) for r in runs]
        ttfa = sorted(p["ttfa_ms"] for p in ps if p.get("ttfa_ms"))
        return {
            "mean_output": round(sum(u["output"] for u in us) / len(us), 1),
            "median_ttfa_s": round(ttfa[len(ttfa) // 2] / 1000, 1) if ttfa else None,
        }

    me = perf("glm5.3")
    for other in ("glm5.3-flash", "qwen3.8-flash", "deepseek-v4-flash", "glm5.2"):
        o = rows[other]
        op = perf(other)
        entry = {
            "score_delta_glm5_3_minus_other": round(93.73 - o["score"], 2),
            "other_cost_per_1k": o["normalized_cost_per_1k"],
            "other_basis": o.get("price_basis"),
            "ttfa_delta_s": (None if not (me["median_ttfa_s"] and op["median_ttfa_s"])
                             else round(me["median_ttfa_s"] - op["median_ttfa_s"], 1)),
            "output_token_delta": round(me["mean_output"] - op["mean_output"], 1),
        }
        for basis, block in bases.items():
            mine = block["glm5.3_per_1k"]
            theirs = cost_for(o)
            entry[f"cost_delta_per_1k__{basis}"] = round(mine - theirs, 2)
            entry[f"cost_multiple__{basis}"] = round(mine / theirs, 2)
            entry[f"like_for_like__{basis}"] = (basis == "FIRST_PARTY_LIST"
                                                and o.get("price_basis") == "First-party")
        report["comparisons"][other] = entry

    # ---- the two editorial claims -------------------------------------------
    flash = rows["glm5.3-flash"]
    report["editorial_claims"]["half_the_cost_of_flash"] = {
        "claim": ("GLM 5.3 gives up ~1.2 Monday Score points versus GLM 5.3 Flash while "
                  "costing roughly half as much."),
        "score_delta": round(93.73 - flash["score"], 2),
        "on_first_party_list": {
            "glm5.3": bases["FIRST_PARTY_LIST"]["glm5.3_per_1k"],
            "flash": flash["normalized_cost_per_1k"],
            "multiple": round(bases["FIRST_PARTY_LIST"]["glm5.3_per_1k"]
                              / flash["normalized_cost_per_1k"], 2),
            "supported": False,
        },
        "on_mixed_basis": {
            "glm5.3_metered": bases["GATEWAY_METERED"]["glm5.3_per_1k"],
            "flash_list": flash["normalized_cost_per_1k"],
            "multiple": round(bases["GATEWAY_METERED"]["glm5.3_per_1k"]
                              / flash["normalized_cost_per_1k"], 2),
            "supported_but_invalid": True,
            "why_invalid": ("compares a metered gateway invoice against a public list price; "
                            "the 2026-09-02 gate forbids mixing two pricing bases in one "
                            "canonical number"),
        },
        "verdict": "NOT SUPPORTED on any consistent basis - inverted on the like-for-like one",
    }
    above_90 = {m: cost_for(r) for m, r in rows.items()
                if r["score"] > 90 and not r.get("provisional")}
    report["editorial_claims"]["cheapest_above_90"] = {
        "claim": "GLM 5.3 is one of the cheapest ways to get above 90 Monday Score.",
        "field_above_90_first_party_basis": dict(sorted(above_90.items(), key=lambda kv: kv[1])),
        "glm5.3_first_party": bases["FIRST_PARTY_LIST"]["glm5.3_per_1k"],
        "rank_on_first_party": (
            1 + sum(1 for v in above_90.values()
                    if v < bases["FIRST_PARTY_LIST"]["glm5.3_per_1k"])),
        "of": len(above_90) + 1,
        "verdict": "NOT SUPPORTED on the first-party basis - it would be the most expensive",
    }

    report["gate"] = {
        "usage_reconstruction": "PASS",
        "method_validated_against_published_figures": "PASS",
        "billing_semantics": "PASS",
        "reasoning_double_count": "NONE",
        "pricing_identity": "FAIL",
        "pricing_identity_detail": (
            "Z.AI lists GLM-5.3 at $1.4/$4.4. The gateway metered $0.075/$0.25 - which is "
            "exactly GLM-5.3-Flash's promotional price, and exactly 50% of GLM-5.3-Flash's "
            "list. For GLM-5.2 the same gateway metered exactly 50% of ITS list. So either "
            "the route is not GLM-5.3-as-listed, or the gateway prices it on a basis "
            "unrelated to Z.AI list. A client cannot tell which."
        ),
        "publishable": False,
        "consequence": ("No cost figure for GLM 5.3 is published, and the website Cost and "
                        "Efficiency tabs are not changed."),
    }

    (HERE / "_glm53-gate.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8", newline="\n")

    print("BASES")
    for basis, block in bases.items():
        print(f"  {basis:<20} GLM 5.3 = ${block['glm53_per_1k'] if False else block['glm5.3_per_1k']}/1k")
    print("\nPARETO (official, provisional excluded)")
    for basis, block in report["pareto"].items():
        print(f"  {basis}")
        print(f"    before: {block['official_frontier_before']}")
        print(f"    after : {block['official_frontier_after']}")
        print(f"    GLM 5.3 on frontier: {block['glm5.3_on_frontier']}   "
              f"displaced: {block['displaced'] or 'none'}")
    print("\nEDITORIAL CLAIMS")
    for key, block in report["editorial_claims"].items():
        print(f"  {key}: {block['verdict']}")
    print(f"\nGATE: pricing_identity {report['gate']['pricing_identity']} -> "
          f"publishable {report['gate']['publishable']}")


if __name__ == "__main__":
    main()
