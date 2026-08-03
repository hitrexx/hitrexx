from app.ai.base import AIProvider
from app.ai.gemini_provider import GeminiProvider
from app.config import Config


def get_ai_provider(config: Config) -> AIProvider:
    """Single place to swap the AI backend (e.g. Gemini -> Claude Opus) later."""
    return GeminiProvider(api_key=config.gemini_api_key)
