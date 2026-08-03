from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.database import db
from app.handlers.keyboards import done_uploading_keyboard
from app.handlers.states import SURVEY_QUESTIONS, EstimateStates
from app.logger import get_requests_logger

router = Router()


@router.message(EstimateStates.survey)
async def handle_survey_answer(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    question_index: int = data.get("question_index", 0)
    survey: dict = data.get("survey", {})

    key, _ = SURVEY_QUESTIONS[question_index]
    survey[key] = message.text
    question_index += 1

    db.log_request(message.from_user.id, f"survey_answer:{key}", message.text)

    if question_index < len(SURVEY_QUESTIONS):
        await state.update_data(question_index=question_index, survey=survey)
        await message.answer(SURVEY_QUESTIONS[question_index][1])
        return

    await state.update_data(survey=survey, project_files=[])
    await state.set_state(EstimateStates.waiting_project_files)
    get_requests_logger().info("user=%s survey completed: %s", message.from_user.id, survey)

    await message.answer(
        "Спасибо! Теперь пришлите проект: PDF, Word или фото чертежей — можно несколько файлов "
        "подряд. Когда закончите — нажмите «Готово, всё загрузил».",
        reply_markup=done_uploading_keyboard,
    )
