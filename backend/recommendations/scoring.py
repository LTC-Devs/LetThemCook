"""Small, deterministic 0-100 point scorer used by the LTC demo.

No machine learning: each component is shown in the UI and can be explained
independently. All quantities must use the ingredient's canonical base unit.
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Mapping


@dataclass(frozen=True)
class ScoreResult:
    total: float
    coverage: float
    few_missing: float
    expiring: float
    missing_count: int
    ingredient_count: int


def score_recipe(
    required: Mapping[int, Decimal],
    available: Mapping[int, Decimal],
    expiring_soon: Mapping[int, Decimal],
) -> ScoreResult:
    """Score one recipe (quantified, non-optional ingredients only).

    60 points: fraction of quantities already in the pantry.
    25 points: fraction of ingredients available in their full required amount.
    15 points: fraction of required quantities in stock expiring within 48 h.

    Expired batches MUST already be excluded by the caller. No score is ever
    awarded to a recipe without a measurable required ingredient.
    """
    amounts = {ingredient_id: Decimal(qty) for ingredient_id, qty in required.items() if qty > 0}
    count = len(amounts)
    if not count:
        return ScoreResult(0, 0, 0, 0, 0, 0)

    coverage_fraction = Decimal(0)
    urgent_fraction = Decimal(0)
    missing_count = 0
    for ingredient_id, needed in amounts.items():
        in_stock = max(Decimal(0), Decimal(available.get(ingredient_id, 0)))
        urgent = max(Decimal(0), Decimal(expiring_soon.get(ingredient_id, 0)))
        used = min(needed, in_stock)
        coverage_fraction += used / needed
        urgent_fraction += min(needed, used, urgent) / needed
        if in_stock < needed:
            missing_count += 1

    coverage = float(Decimal(60) * coverage_fraction / count)
    few_missing = 25 * (count - missing_count) / count
    expiring = float(Decimal(15) * urgent_fraction / count)
    return ScoreResult(
        total=round(coverage + few_missing + expiring, 1),
        coverage=round(coverage, 1),
        few_missing=round(few_missing, 1),
        expiring=round(expiring, 1),
        missing_count=missing_count,
        ingredient_count=count,
    )
