from aiogram import Router

from app.handlers import estimate, fallback, price_list, project_upload, start, survey


def get_main_router() -> Router:
    router = Router()
    router.include_router(start.router)
    router.include_router(price_list.router)
    router.include_router(survey.router)
    router.include_router(project_upload.router)
    router.include_router(estimate.router)
    # Must stay last — it matches any message and is the fallback for
    # everything the routers above didn't claim.
    router.include_router(fallback.router)
    return router
