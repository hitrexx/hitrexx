import os

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, Message

from app.ai.base import AIProvider
from app.database import db
from app.handlers.keyboards import remove_keyboard
from app.handlers.states import EstimateStates
from app.logger import get_errors_logger, get_requests_logger
from app.services.estimate_service import run_estimate_pipeline
from app.exports.excel_export import export_estimate_to_excel
from app.exports.pdf_export import export_estimate_to_pdf

router = Router()

_EXPORTS_DIR = "data/exports"
_RENDERS_DIR = "data/renders"


def _format_summary(pipeline_result) -> str:
    lines = ["📋 Предварительная смета\n"]
    for stage in pipeline_result.calculation.stages:
        lines.append(f"<b>{stage.work}</b> ({stage.volume:g} {stage.unit})")
        if stage.matched:
            if stage.material_cost > 0:
                lines.append(f"Работа — {stage.work_cost:,.0f} ₽")
                lines.append(f"Материалы — {stage.material_cost:,.0f} ₽")
            lines.append(f"Итого — {stage.total:,.0f} ₽\n")
        else:
            lines.append("⚠️ Позиция не найдена в прайс-листе")
            if stage.suggestions:
                lines.append("Похожие позиции в прайсе (проверьте вручную):")
                for suggestion in stage.suggestions:
                    lines.append(f"  • {suggestion}")
            lines.append("")

    lines.append(f"<b>Общий итог: {pipeline_result.calculation.grand_total:,.0f} ₽</b>")

    if pipeline_result.recommendations:
        lines.append("\n🔎 Рекомендации (возможно пропущенные этапы):")
        for recommendation in pipeline_result.recommendations:
            lines.append(f"• {recommendation}")

    return "\n".join(lines)


@router.message(EstimateStates.waiting_project_files, F.text == "Готово, всё загрузил")
async def handle_finish_upload(message: Message, state: FSMContext, ai_provider: AIProvider) -> None:
    data = await state.get_data()
    project_files: list[str] = data.get("project_files", [])
    price_list_id = data.get("price_list_id")
    survey = data.get("survey", {})

    if not project_files:
        await message.answer("Пришлите хотя бы один файл проекта, прежде чем нажимать «Готово».")
        return

    await state.set_state(EstimateStates.processing)
    await message.answer("⏳ Анализирую проект и считаю смету, это может занять минуту...", reply_markup=remove_keyboard)

    user_id = db.get_or_create_user(message.from_user.id, message.from_user.username)
    render_dir = os.path.join(_RENDERS_DIR, str(message.from_user.id))

    try:
        result = await run_estimate_pipeline(
            ai_provider=ai_provider,
            user_id=user_id,
            price_list_id=price_list_id,
            survey=survey,
            project_file_paths=project_files,
            render_dir=render_dir,
        )
    except Exception as exc:  # noqa: BLE001 - surface a friendly message, log the real error
        get_errors_logger().error("Ошибка при расчёте сметы user=%s: %s", message.from_user.id, exc)
        await message.answer(
            "⚠️ Не получилось рассчитать смету. Попробуйте ещё раз позже или начните заново командой /start."
        )
        await state.clear()
        return

    get_requests_logger().info("user=%s estimate calculated total=%s", message.from_user.id, result.calculation.grand_total)

    await message.answer(_format_summary(result), parse_mode="HTML")

    export_dir = os.path.join(_EXPORTS_DIR, str(message.from_user.id))
    os.makedirs(export_dir, exist_ok=True)
    excel_path = export_estimate_to_excel(result.calculation, result.recommendations, os.path.join(export_dir, "estimate.xlsx"))
    pdf_path = export_estimate_to_pdf(result.calculation, result.recommendations, os.path.join(export_dir, "estimate.pdf"))

    with open(excel_path, "rb") as excel_file:
        await message.answer_document(BufferedInputFile(excel_file.read(), filename="Смета.xlsx"))
    with open(pdf_path, "rb") as pdf_file:
        await message.answer_document(BufferedInputFile(pdf_file.read(), filename="Смета.pdf"))

    await state.clear()
