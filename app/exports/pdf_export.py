import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle

from app.calculator.calculator import EstimateCalculation

_FONTS_DIR = os.path.join(os.path.dirname(__file__), "fonts")
_FONT_NAME = "DejaVuSans"
_FONT_NAME_BOLD = "DejaVuSans-Bold"

_fonts_registered = False


def _ensure_fonts_registered() -> None:
    global _fonts_registered
    if _fonts_registered:
        return
    pdfmetrics.registerFont(TTFont(_FONT_NAME, os.path.join(_FONTS_DIR, "DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont(_FONT_NAME_BOLD, os.path.join(_FONTS_DIR, "DejaVuSans-Bold.ttf")))
    _fonts_registered = True


def export_estimate_to_pdf(
    calculation: EstimateCalculation,
    recommendations: list[str],
    output_path: str,
) -> str:
    _ensure_fonts_registered()

    document = SimpleDocTemplate(output_path, pagesize=A4, topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    title_style = ParagraphStyle("Title", fontName=_FONT_NAME_BOLD, fontSize=16, spaceAfter=12)
    heading_style = ParagraphStyle("Heading", fontName=_FONT_NAME_BOLD, fontSize=12, spaceAfter=6)
    body_style = ParagraphStyle("Body", fontName=_FONT_NAME, fontSize=10)

    elements = [Paragraph("Предварительная смета", title_style)]

    table_data = [["Этап", "Работа", "Объём", "Ед.", "Работа, ₽", "Материал, ₽", "Итого, ₽"]]
    for stage in calculation.stages:
        table_data.append(
            [
                stage.key,
                stage.work,
                f"{stage.volume:g}",
                stage.unit,
                f"{stage.work_price:,.2f}" if stage.matched else "нет в прайсе",
                f"{stage.material_price:,.2f}" if stage.matched else "",
                f"{stage.total:,.2f}",
            ]
        )
    table_data.append(["", "", "", "", "", "Общий итог", f"{calculation.grand_total:,.2f}"])

    table = Table(table_data, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), _FONT_NAME),
                ("FONTNAME", (0, 0), (-1, 0), _FONT_NAME_BOLD),
                ("FONTNAME", (0, -1), (-1, -1), _FONT_NAME_BOLD),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
            ]
        )
    )
    elements.append(table)

    if recommendations:
        elements.append(Spacer(1, 16))
        elements.append(Paragraph("Рекомендации (возможно пропущенные этапы):", heading_style))
        for recommendation in recommendations:
            elements.append(Paragraph(f"• {recommendation}", body_style))

    document.build(elements)
    return output_path
