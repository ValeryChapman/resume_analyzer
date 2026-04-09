from aiogram import Router

from bot_service.controllers.telegram.handlers.start import router as start_router
from bot_service.controllers.telegram.handlers.vacancies import (
    router as vacancies_router,
)

router = Router(name="main")
router.include_router(start_router)
router.include_router(vacancies_router)
