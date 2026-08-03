from app.calculator.calculator import calculate_estimate

PRICE_ITEMS = [
    {"code": "101", "name": "Устройство ленточного фундамента", "unit": "м3", "work_price": 1500, "material_price": 3200},
    {"code": "102", "name": "Кладка стен из газобетона", "unit": "м2", "work_price": 900, "material_price": 2100},
]

ANALYSIS = {
    "foundation": {"work": "Ленточный фундамент", "volume": 32, "unit": "м3"},
    "walls": {"work": "Газобетонные стены", "volume": 245, "unit": "м2"},
    "unknown_stage": {"work": "Экзотические работы, которых нет в прайсе", "volume": 5, "unit": "шт"},
}


def test_calculate_estimate_matches_and_sums_correctly():
    result = calculate_estimate(ANALYSIS, PRICE_ITEMS)

    foundation = next(s for s in result.stages if s.key == "foundation")
    assert foundation.matched is True
    assert foundation.work_cost == 32 * 1500
    assert foundation.material_cost == 32 * 3200
    assert foundation.total == foundation.work_cost + foundation.material_cost

    walls = next(s for s in result.stages if s.key == "walls")
    assert walls.matched is True
    assert walls.total == 245 * 900 + 245 * 2100

    unknown = next(s for s in result.stages if s.key == "unknown_stage")
    assert unknown.matched is False
    assert unknown.total == 0

    assert result.grand_total == foundation.total + walls.total + unknown.total


def test_calculate_estimate_handles_empty_analysis():
    result = calculate_estimate({}, PRICE_ITEMS)
    assert result.stages == []
    assert result.grand_total == 0
