from typing import Any

import openpyxl

_COLUMN_ALIASES = {
    "code": ["код"],
    "name": ["наименование", "работа", "название"],
    "unit": ["единица", "ед.изм", "ед. изм", "единица измерения"],
    "work_price": ["цена работы", "стоимость работы", "работа, руб"],
    "material_price": ["цена материала", "стоимость материала", "материал, руб"],
}


class PriceListError(Exception):
    pass


def _match_column(header: str) -> str | None:
    normalized = header.strip().lower()
    for field, aliases in _COLUMN_ALIASES.items():
        if any(alias in normalized for alias in aliases):
            return field
    return None


def parse_price_list(file_path: str) -> list[dict[str, Any]]:
    workbook = openpyxl.load_workbook(file_path, data_only=True)
    sheet = workbook.active

    rows = list(sheet.iter_rows(values_only=True))
    if not rows:
        raise PriceListError("Файл прайс-листа пуст")

    header_row = rows[0]
    column_map: dict[int, str] = {}
    for idx, header in enumerate(header_row):
        if header is None:
            continue
        field = _match_column(str(header))
        if field:
            column_map[idx] = field

    required = {"name", "unit"}
    if not required.issubset(set(column_map.values())):
        raise PriceListError(
            "Не найдены обязательные колонки 'Наименование' и 'Единица' в прайс-листе"
        )

    items: list[dict[str, Any]] = []
    for row in rows[1:]:
        if row is None or all(cell is None for cell in row):
            continue
        item: dict[str, Any] = {"code": None, "work_price": 0.0, "material_price": 0.0}
        for idx, field in column_map.items():
            value = row[idx] if idx < len(row) else None
            if field in ("work_price", "material_price"):
                item[field] = float(value) if value not in (None, "") else 0.0
            else:
                item[field] = str(value).strip() if value is not None else None
        if not item.get("name") or not item.get("unit"):
            continue
        items.append(item)

    if not items:
        raise PriceListError("В прайс-листе не найдено ни одной позиции")

    return items
