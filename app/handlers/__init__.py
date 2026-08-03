from aiogram import Router

from app.handlers import estimate, price_list, project_upload, start, survey


def get_main_router() -> Router:
    router = Router()
    router.include_router(start.router)
    router.include_router(price_list.router)
    router.include_router(survey.router)
    router.include_router(project_upload.router)
    router.include_router(estimate.router)
    return router
