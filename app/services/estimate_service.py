import os
from dataclasses import dataclass
from typing import Any

from app.ai.base import AIProvider
from app.calculator.calculator import EstimateCalculation, calculate_estimate
from app.database import db
from app.parser.project_parser import collect_project_content


@dataclass
class PipelineResult:
    analysis: dict[str, Any]
    calculation: EstimateCalculation
    recommendations: list[str]


async def run_estimate_pipeline(
    ai_provider: AIProvider,
    user_id: int,
    price_list_id: int,
    survey: dict[str, Any],
    project_file_paths: list[str],
    render_dir: str,
) -> PipelineResult:
    project_id = db.create_project(user_id, price_list_id, survey)
    for file_path in project_file_paths:
        db.add_project_file(project_id, file_path, os.path.splitext(file_path)[1].lstrip("."))

    price_items = db.get_price_items(price_list_id)
    content = collect_project_content(project_file_paths, render_dir)

    analysis = await ai_provider.analyze_project(survey, content.text, content.image_paths)
    calculation = calculate_estimate(analysis, price_items)
    recommendations = await ai_provider.verify_estimate(survey, analysis)

    db.save_estimate(project_id, analysis, calculation.to_dict(), recommendations)

    return PipelineResult(analysis=analysis, calculation=calculation, recommendations=recommendations)
