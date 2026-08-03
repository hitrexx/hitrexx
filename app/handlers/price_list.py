import os

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.database import db
from app.handlers.states import SURVEY_QUESTIONS, EstimateStates
from app.logger import get_errors_logger, get_requests_logger
from app.parser.price_list_parser import PriceListError, parse_price_list

router = Router()

_UPLOADS_DIR = "data/uploads"


@router.message(EstimateStates.waiting_price_list)
async def handle_price_list_upload(message: Message, state: FSMContext) -> None:
    if not message.document:
        await message.answer("Пришлите, пожалуйста, файл прайс-листа в формате Excel (.xlsx).")
        return

    if not message.document.file_name.lower().endswith((".xlsx", ".xls")):
        await message.answer("Нужен файл в формате Excel (.xlsx или .xls). Попробуйте ещё раз.")
        return

    user_id = db.get_or_create_user(message.from_user.id, message.from_user.username)
    user_dir = os.path.join(_UPLOADS_DIR, str(message.from_user.id))
    os.makedirs(user_dir, exist_ok=True)
    file_path = os.path.join(user_dir, "price_list.xlsx")

    await message.bot.download(message.document, destination=file_path)
    db.log_request(message.from_user.id, "upload_price_list", message.document.file_name)

    try:
        items = parse_price_list(file_path)
    except PriceListError as exc:
        get_errors_logger().error("Ошибка разбора прайс-листа: %s", exc)
        await message.answer(f"⚠️ {exc}\n\nПришлите файл ещё раз, проверив формат колонок.")
        return
    except Exception as exc:  # noqa: BLE001 - report unexpected parsing errors to the user
        get_errors_logger().error("Неожиданная ошибка разбора прайс-листа: %s", exc)
        await message.answer("⚠️ Не удалось прочитать файл. Убедитесь, что это корректный Excel-файл.")
        return

    price_list_id = db.save_price_list(user_id, message.document.file_name, items)
    await state.update_data(price_list_id=price_list_id, question_index=0, survey={})

    get_requests_logger().info(
        "user=%s price_list saved id=%s items=%s", message.from_user.id, price_list_id, len(items)
    )

    await message.answer(f"✅ Прайс-лист загружен: {len(items)} позиций.\n\nТеперь несколько вопросов о проекте.")
    await state.set_state(EstimateStates.survey)
    await message.answer(SURVEY_QUESTIONS[0][1])
