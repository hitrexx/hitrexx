from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

start_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="📐 Создать смету", callback_data="new_estimate")]]
)

done_uploading_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Готово, всё загрузил")]],
    resize_keyboard=True,
)

remove_keyboard = ReplyKeyboardRemove()
