from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.database import db
from app.handlers.keyboards import start_keyboard
from app.handlers.states import EstimateStates
from app.logger import get_requests_logger

router = Router()


@router.message(CommandStart())
async def handle_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    db.get_or_create_user(message.from_user.id, message.from_user.username)
    db.log_request(message.from_user.id, "start")
    get_requests_logger().info("user=%s /start", message.from_user.id)

    await message.answer(
        "👋 Привет! Я AI Estimate — помогу быстро рассчитать предварительную смету "
        "на строительство по вашему проекту.\n\n"
        "Нажмите кнопку ниже, чтобы начать.",
        reply_markup=start_keyboard,
    )


@router.callback_query(F.data == "new_estimate")
async def handle_new_estimate(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(EstimateStates.waiting_price_list)
    db.log_request(callback.from_user.id, "new_estimate")

    await callback.message.answer(
        "Отлично! Для начала пришлите Excel-файл с прайс-листом вашей компании.\n\n"
        "Ожидаемые колонки: Код, Наименование, Единица, Цена работы, Цена материала."
    )
    await callback.answer()
