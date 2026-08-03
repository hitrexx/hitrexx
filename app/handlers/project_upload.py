import os

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.database import db
from app.handlers.states import EstimateStates
from app.logger import get_requests_logger

router = Router()

_UPLOADS_DIR = "data/uploads"
_ALLOWED_EXTENSIONS = (".pdf", ".docx", ".png", ".jpg", ".jpeg", ".webp")


async def _save_incoming_file(message: Message, file_id: str, suggested_name: str) -> str:
    user_dir = os.path.join(_UPLOADS_DIR, str(message.from_user.id), "project")
    os.makedirs(user_dir, exist_ok=True)
    file_path = os.path.join(user_dir, suggested_name)
    await message.bot.download(file_id, destination=file_path)
    return file_path


@router.message(EstimateStates.waiting_project_files, F.document)
async def handle_project_document(message: Message, state: FSMContext) -> None:
    filename = message.document.file_name
    if not filename.lower().endswith(_ALLOWED_EXTENSIONS):
        await message.answer("Поддерживаются файлы: PDF, DOCX, PNG, JPG. Попробуйте другой файл.")
        return

    data = await state.get_data()
    project_files: list[str] = data.get("project_files", [])

    unique_name = f"{len(project_files)}_{filename}"
    file_path = await _save_incoming_file(message, message.document.file_id, unique_name)
    project_files.append(file_path)
    await state.update_data(project_files=project_files)

    db.log_request(message.from_user.id, "upload_project_file", filename)
    get_requests_logger().info("user=%s uploaded project file %s", message.from_user.id, filename)

    await message.answer(f"📎 Файл принят ({len(project_files)} шт.). Пришлите ещё или нажмите «Готово».")


@router.message(EstimateStates.waiting_project_files, F.photo)
async def handle_project_photo(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    project_files: list[str] = data.get("project_files", [])

    photo = message.photo[-1]
    unique_name = f"{len(project_files)}_photo.jpg"
    file_path = await _save_incoming_file(message, photo.file_id, unique_name)
    project_files.append(file_path)
    await state.update_data(project_files=project_files)

    db.log_request(message.from_user.id, "upload_project_photo")
    get_requests_logger().info("user=%s uploaded project photo", message.from_user.id)

    await message.answer(f"📎 Фото принято ({len(project_files)} шт.). Пришлите ещё или нажмите «Готово».")
