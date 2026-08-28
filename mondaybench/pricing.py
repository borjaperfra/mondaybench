"""Cost calculation. Never estimates - an unknown price yields null.

Cost is recorded alongside every run but does not affect the Monday Score.
"""

from __future__ import annotations

from .config import Pricing
from .schemas import RunEconomics

UNKNOWN = RunEconomics(input_cost_usd=None, output_cost_usd=None, total_cost_usd=None)


def compute_economics(
    pricing: Pricing,
    *,
    input_tokens: int | None,
    output_tokens: int | None,
    reasoning_tokens: int | None = None,
) -> RunEconomics:
    """Return costs in USD, or all-null when price or token counts are unknown.

    A partially-configured price is treated as unknown: publishing half a cost
    would be worse than publishing none.
    """
    if pricing.input_per_million_usd is None or pricing.output_per_million_usd is None:
        return UNKNOWN
    if input_tokens is None or output_tokens is None:
        return UNKNOWN

    input_cost = input_tokens / 1_000_000 * pricing.input_per_million_usd
    output_cost = output_tokens / 1_000_000 * pricing.output_per_million_usd

    # Only add a separate reasoning line when the model prices it separately;
    # otherwise reasoning tokens are already inside output_tokens.
    if pricing.reasoning_per_million_usd is not None and reasoning_tokens:
        output_cost += reasoning_tokens / 1_000_000 * pricing.reasoning_per_million_usd

    return RunEconomics(
        input_cost_usd=round(input_cost, 6),
        output_cost_usd=round(output_cost, 6),
        total_cost_usd=round(input_cost + output_cost, 6),
    )
