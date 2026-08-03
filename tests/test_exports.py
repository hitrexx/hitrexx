import os

from app.calculator.calculator import calculate_estimate
from app.exports.excel_export import export_estimate_to_excel
from app.exports.pdf_export import export_estimate_to_pdf

PRICE_ITEMS = [
    {"code": "101", "name": "Устройство ленточного фундамента", "unit": "м3", "work_price": 1500, "material_price": 3200},
]

ANALYSIS = {
    "foundation": {"work": "Ленточный фундамент", "volume": 32, "unit": "м3"},
}


def test_export_estimate_to_excel(tmp_path):
    calculation = calculate_estimate(ANALYSIS, PRICE_ITEMS)
    output_path = tmp_path / "estimate.xlsx"

    result_path = export_estimate_to_excel(calculation, ["Проверьте гидроизоляцию"], str(output_path))

    assert os.path.exists(result_path)
    assert os.path.getsize(result_path) > 0


def test_export_estimate_to_pdf(tmp_path):
    calculation = calculate_estimate(ANALYSIS, PRICE_ITEMS)
    output_path = tmp_path / "estimate.pdf"

    result_path = export_estimate_to_pdf(calculation, ["Проверьте гидроизоляцию"], str(output_path))

    assert os.path.exists(result_path)
    with open(result_path, "rb") as pdf_file:
        assert pdf_file.read(4) == b"%PDF"
