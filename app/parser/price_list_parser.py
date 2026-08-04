from typing import Any

import openpyxl

_COLUMN_ALIASES = {
    "code": ["код"],
    "name": ["наименование", "работа", "название"],
    "unit": ["единица", "ед.изм", "ед. изм", "единица измерения"],
    "work_price": ["цена работы", "стоимость работы", "работа, руб", "цена за единицу"],
    "material_price": ["цена материала", "стоимость материала", "материал, руб"],
}

_HEADER_SEARCH_LIMIT = 30
_REQUIRED_FIELDS = {"name", "unit"}


class PriceListError(Exception):
    pass


def _match_column(header: str) -> str | None:
    normalized = header.strip().lower()
    for field, aliases in _COLUMN_ALIASES.items():
        if any(alias in normalized for alias in aliases):
            return field
    return None


def _find_header_row(rows: list[tuple]) -> tuple[int, dict[int, str]] | None:
    """Real price lists often have title/summary rows before the actual table
    header, and it isn't always row 0 — scan for the first row that has both
    a name and a unit column."""
    for row_idx, row in enumerate(rows[:_HEADER_SEARCH_LIMIT]):
        column_map: dict[int, str] = {}
        for idx, header in enumerate(row):
            if header is None:
                continue
            field = _match_column(str(header))
            if field:
                column_map[idx] = field
        if _REQUIRED_FIELDS.issubset(set(column_map.values())):
            return row_idx, column_map
    return None


def _extract_items(rows: list[tuple], column_map: dict[int, str]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for row in rows:
        if row is None or all(cell is None for cell in row):
            continue
        item: dict[str, Any] = {"code": None, "work_price": 0.0, "material_price": 0.0}
        for idx, field in column_map.items():
            value = row[idx] if idx < len(row) else None
            if field in ("work_price", "material_price"):
                item[field] = float(value) if isinstance(value, (int, float)) else 0.0
            else:
                item[field] = str(value).strip() if value is not None else None
        # Section-header rows (e.g. "Раздел 1. Фундамент") only fill the name
        # column — skip them, they aren't priceable line items.
        if not item.get("name") or not item.get("unit"):
            continue
        items.append(item)
    return items


def parse_price_list(file_path: str) -> list[dict[str, Any]]:
    workbook = openpyxl.load_workbook(file_path, data_only=True)

    for sheet in workbook.worksheets:
        rows = list(sheet.iter_rows(values_only=True))
        if not rows:
            continue

        found = _find_header_row(rows)
        if found is None:
            continue

        header_idx, column_map = found
        items = _extract_items(rows[header_idx + 1 :], column_map)
        if items:
            return items

    raise PriceListError(
        "Не найдены обязательные колонки 'Наименование' и 'Единица' в прайс-листе"
    )
