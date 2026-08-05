from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.handlers.keyboards import start_keyboard

router = Router()


@router.message()
async def handle_unmatched_message(message: Message, state: FSMContext) -> None:
    """Catches anything no other handler matched — most commonly a bot
    restart wiping in-memory FSM state mid-conversation, which otherwise
    leaves the user's messages silently ignored with no explanation."""
    await state.clear()
    await message.answer(
        "🤔 Не понял это сообщение — возможно, диалог сбросился (например, бот "
        "перезапускался). Нажмите /start, чтобы начать заново.",
        reply_markup=start_keyboard,
    )
