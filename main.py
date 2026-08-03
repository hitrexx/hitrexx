import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.ai.factory import get_ai_provider
from app.config import load_config
from app.database.db import init_db
from app.handlers import get_main_router
from app.logger import setup_logging


async def main() -> None:
    config = load_config()
    setup_logging(config.log_level)
    init_db(config.database_path)

    if not config.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN не задан в .env")
    if not config.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY не задан в .env")

    ai_provider = get_ai_provider(config)

    bot = Bot(token=config.telegram_bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dispatcher = Dispatcher()
    dispatcher["ai_provider"] = ai_provider
    dispatcher.include_router(get_main_router())

    await bot.delete_webhook(drop_pending_updates=True)
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
