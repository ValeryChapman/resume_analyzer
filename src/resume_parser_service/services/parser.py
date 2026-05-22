import asyncio
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from resume_parser_service.services.api import get_resume_search_api_service
from resume_parser_service.services.resumes import process_resume_from_hh
from resume_parser_service.settings import settings

logger = logging.getLogger(__name__)

MOSCOW_TZ = ZoneInfo("Europe/Moscow")


async def sync_resumes_from_hh_service() -> tuple[int, int]:
    """
    Синхронизирует новые резюме из HeadHunter за фиксированное окно времени.

    :return: Кортеж (просмотрено, создано).
    """
    processed_count, created_count = 0, 0

    date_to = datetime.now(tz=MOSCOW_TZ)
    date_from = date_to - timedelta(seconds=settings.resume_parser.lookback_seconds)

    response_data = await get_resume_search_api_service(
        date_from=date_from,
        date_to=date_to,
        timeout=settings.hh.timeout,
    )

    response_resumes = response_data.items
    if not response_resumes:
        return processed_count, created_count

    for resume in response_resumes:
        processed_count += 1

        created: bool = await process_resume_from_hh(resume=resume)
        created_count += int(created)

    return processed_count, created_count


async def start_resume_parser_service() -> None:
    """
    Основной цикл фонового парсинга резюме из HeadHunter.
    """
    while True:
        try:
            processed_count, created_count = await sync_resumes_from_hh_service()
            logger.info(
                "Синхронизация резюме HeadHunter завершена: processed=%s created=%s",
                processed_count,
                created_count,
            )
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.error(
                "Ошибка синхронизации резюме HeadHunter: %s",
                exc,
                exc_info=True,
            )
            await asyncio.sleep(settings.resume_parser.error_sleep_seconds)
            continue

        await asyncio.sleep(settings.resume_parser.poll_interval_seconds)
