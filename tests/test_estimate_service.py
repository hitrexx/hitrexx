import os

import pytest

from app.ai.base import AIProvider
from app.database import db
from app.services.estimate_service import run_estimate_pipeline


class FakeAIProvider(AIProvider):
    async def analyze_project(self, survey, project_text, image_paths):
        return {
            "foundation": {"work": "Ленточный фундамент", "volume": 32, "unit": "м3"},
        }

    async def verify_estimate(self, survey, analysis):
        return ["Проверьте гидроизоляцию фундамента"]


@pytest.fixture()
def temp_db(tmp_path):
    db.init_db(str(tmp_path / "test.db"))
    return db


@pytest.mark.asyncio
async def test_run_estimate_pipeline_end_to_end(temp_db, tmp_path):
    user_id = temp_db.get_or_create_user(telegram_id=1, username="tester")
    price_list_id = temp_db.save_price_list(
        user_id,
        "price.xlsx",
        [{"code": "101", "name": "Ленточный фундамент", "unit": "м3", "work_price": 1500, "material_price": 3200}],
    )

    project_file = tmp_path / "notes.txt"
    project_file.write_text("нет проектных файлов, просто заметка")

    result = await run_estimate_pipeline(
        ai_provider=FakeAIProvider(),
        user_id=user_id,
        price_list_id=price_list_id,
        survey={"project_type": "дом"},
        project_file_paths=[],
        render_dir=str(tmp_path / "renders"),
    )

    assert result.calculation.grand_total == 32 * 1500 + 32 * 3200
    assert result.recommendations == ["Проверьте гидроизоляцию фундамента"]
    assert result.calculation.stages[0].matched is True
