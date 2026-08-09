from abc import ABC, abstractmethod
from typing import Any


class AIProvider(ABC):
    """Abstract AI provider. Only analyzes projects and flags missing stages —
    never computes prices; that stays in app/calculator."""

    @abstractmethod
    async def analyze_project(
        self,
        survey: dict[str, Any],
        project_text: str,
        image_paths: list[str],
        price_items: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Return a structured mapping of construction stages to work/volume/unit.

        price_items (names/units only, no prices) are passed so the model can
        phrase each stage using the company's own price-list wording — this
        is what the programmatic matcher in app/calculator relies on."""

    @abstractmethod
    async def verify_estimate(
        self,
        survey: dict[str, Any],
        analysis: dict[str, Any],
    ) -> list[str]:
        """Return a list of human-readable recommendations about possibly missing stages."""
