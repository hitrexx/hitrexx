from dataclasses import dataclass, field
from typing import Any

from app.calculator.matcher import find_best_price_item, find_top_candidates

_SUGGESTIONS_PER_UNMATCHED_STAGE = 3


@dataclass
class StageCalculation:
    key: str
    work: str
    volume: float
    unit: str
    matched: bool
    work_price: float = 0.0
    material_price: float = 0.0
    work_cost: float = 0.0
    material_cost: float = 0.0
    total: float = 0.0
    suggestions: list[str] = field(default_factory=list)


@dataclass
class EstimateCalculation:
    stages: list[StageCalculation] = field(default_factory=list)
    grand_total: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "stages": [stage.__dict__ for stage in self.stages],
            "grand_total": self.grand_total,
        }


def calculate_estimate(
    analysis: dict[str, dict[str, Any]],
    price_items: list[dict[str, Any]],
) -> EstimateCalculation:
    """All arithmetic happens here — the AI only supplies work names/volumes/units."""
    result = EstimateCalculation()

    for key, stage in analysis.items():
        work = str(stage.get("work", key))
        unit = str(stage.get("unit", ""))
        try:
            volume = float(stage.get("volume", 0))
        except (TypeError, ValueError):
            volume = 0.0

        price_item = find_best_price_item(work, unit, price_items)

        if price_item is None:
            candidates = find_top_candidates(work, price_items, limit=_SUGGESTIONS_PER_UNMATCHED_STAGE)
            suggestions = [f"{c['name']} ({c['unit']})" for c in candidates]
            result.stages.append(
                StageCalculation(
                    key=key, work=work, volume=volume, unit=unit, matched=False, suggestions=suggestions
                )
            )
            continue

        work_price = float(price_item.get("work_price", 0))
        material_price = float(price_item.get("material_price", 0))
        work_cost = round(volume * work_price, 2)
        material_cost = round(volume * material_price, 2)
        total = round(work_cost + material_cost, 2)

        result.stages.append(
            StageCalculation(
                key=key,
                work=work,
                volume=volume,
                unit=unit,
                matched=True,
                work_price=work_price,
                material_price=material_price,
                work_cost=work_cost,
                material_cost=material_cost,
                total=total,
            )
        )

    result.grand_total = round(sum(stage.total for stage in result.stages), 2)
    return result
