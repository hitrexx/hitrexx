import json
import re
from typing import Any

from google import genai
from PIL import Image

from app.ai.base import AIProvider
from app.ai.prompts import (
    ANALYSIS_SYSTEM_PROMPT,
    VERIFICATION_SYSTEM_PROMPT,
    build_analysis_user_prompt,
    build_verification_user_prompt,
)
from app.logger import get_errors_logger

_JSON_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


def _parse_json_response(raw_text: str) -> dict[str, Any]:
    cleaned = _JSON_FENCE_RE.sub("", raw_text.strip()).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        get_errors_logger().error("Не удалось разобрать JSON от ИИ: %s\nОтвет: %s", exc, raw_text)
        raise


class GeminiProvider(AIProvider):
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash"):
        self._client = genai.Client(api_key=api_key)
        self._model_name = model_name

    async def analyze_project(
        self,
        survey: dict[str, Any],
        project_text: str,
        image_paths: list[str],
    ) -> dict[str, Any]:
        contents: list[Any] = [
            ANALYSIS_SYSTEM_PROMPT,
            build_analysis_user_prompt(survey, project_text),
        ]
        for image_path in image_paths:
            contents.append(Image.open(image_path))

        response = await self._client.aio.models.generate_content(
            model=self._model_name, contents=contents
        )
        data = _parse_json_response(response.text)
        return data.get("stages", {})

    async def verify_estimate(
        self,
        survey: dict[str, Any],
        analysis: dict[str, Any],
    ) -> list[str]:
        contents = [
            VERIFICATION_SYSTEM_PROMPT,
            build_verification_user_prompt(survey, analysis),
        ]
        response = await self._client.aio.models.generate_content(
            model=self._model_name, contents=contents
        )
        data = _parse_json_response(response.text)
        return data.get("recommendations", [])
