import asyncio
import logging

from resume_parser_service.services.parser import start_resume_parser_service

logger = logging.getLogger(__name__)


async def run_resume_parser_background_task() -> None:
    """
    Запускает фоновую задачу парсинга резюме из HeadHunter.
    """
    logger.info("Фоновая задача Resume Parser запущена")

    try:
        await start_resume_parser_service()
    except asyncio.CancelledError:
        logger.info("Фоновая задача Resume Parser остановлена")
        raise
    except Exception:
        logger.exception("Фоновая задача Resume Parser завершилась с ошибкой")
        raise
