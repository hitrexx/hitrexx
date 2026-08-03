import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    telegram_bot_token: str
    gemini_api_key: str
    database_path: str
    log_level: str


def load_config() -> Config:
    return Config(
        telegram_bot_token=os.environ.get("TELEGRAM_BOT_TOKEN", ""),
        gemini_api_key=os.environ.get("GEMINI_API_KEY", ""),
        database_path=os.environ.get("DATABASE_PATH", "data/ai_estimate.db"),
        log_level=os.environ.get("LOG_LEVEL", "INFO"),
    )
