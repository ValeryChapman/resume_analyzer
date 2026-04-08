from aiogram import Router

from bot_service.controllers.telegram.handlers.start import router as start_router

router = Router(name="main")
router.include_router(start_router)

__all__ = ["router"]
