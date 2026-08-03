import openpyxl
import pytest

from app.parser.price_list_parser import PriceListError, parse_price_list


def _make_price_list(tmp_path, rows):
    path = tmp_path / "price_list.xlsx"
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(["Код", "Наименование", "Единица", "Цена работы", "Цена материала"])
    for row in rows:
        sheet.append(row)
    workbook.save(path)
    return str(path)


def test_parse_price_list_happy_path(tmp_path):
    path = _make_price_list(
        tmp_path,
        [
            ["101", "Устройство ленточного фундамента", "м3", 1500, 3200],
            ["102", "Кладка стен из газобетона", "м2", 900, 2100],
        ],
    )

    items = parse_price_list(path)

    assert len(items) == 2
    assert items[0]["name"] == "Устройство ленточного фундамента"
    assert items[0]["unit"] == "м3"
    assert items[0]["work_price"] == 1500.0
    assert items[0]["material_price"] == 3200.0


def test_parse_price_list_skips_empty_rows(tmp_path):
    path = _make_price_list(
        tmp_path,
        [
            ["101", "Устройство фундамента", "м3", 1500, 3200],
            [None, None, None, None, None],
        ],
    )

    items = parse_price_list(path)
    assert len(items) == 1


def test_parse_price_list_missing_columns_raises(tmp_path):
    path = tmp_path / "bad.xlsx"
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(["Что-то", "Другое"])
    sheet.append(["a", "b"])
    workbook.save(path)

    with pytest.raises(PriceListError):
        parse_price_list(str(path))
