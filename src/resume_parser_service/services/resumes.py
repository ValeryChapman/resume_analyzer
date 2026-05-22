import logging

import httpx

from resume_parser_service.schemas.get_resume_search import HHResumeSearchItemSchema
from resume_parser_service.services.api import get_resume_detail_api_service
from resume_parser_service.services.formatters import format_resume_details_to_text
from shared.infrastructure.postgres import get_postgres_async_session
from shared.services.resumes import (
    create_resume_from_hh_service,
    get_resume_by_hh_id_service,
)
from shared.services.tasks import send_resume_processing_task_service

logger = logging.getLogger(__name__)


async def process_resume_from_hh(resume: HHResumeSearchItemSchema) -> bool:
    """
    Импортирует одно резюме из выдачи HeadHunter.

    :param resume: Один элемент выдачи поиска резюме HeadHunter.
    :return: True, если было создано новое резюме.
    """
    hh_id = resume.id.strip()
    if not hh_id:
        return False

    async with get_postgres_async_session() as postgres_session:
        if await get_resume_by_hh_id_service(
            postgres_session=postgres_session, hh_id=hh_id
        ):
            return False

    resume_url = resume.url
    if not resume_url:
        return False

    try:
        resume_detail_response = await get_resume_detail_api_service(
            resume_url=resume_url
        )
    except httpx.HTTPError as exc:
        logger.warning(
            "Не удалось получить полную версию резюме HeadHunter: hh_id=%s error=%s",
            hh_id,
            exc,
        )
        return False

    raw_text = format_resume_details_to_text(resume_detail_response)
    return await create_resume_and_enqueue(
        hh_id=hh_id,
        raw_text=raw_text,
    )


async def create_resume_and_enqueue(hh_id: str, raw_text: str) -> bool:
    """
    Создает резюме в БД и ставит задачу на последующую обработку.

    :param hh_id: Идентификатор резюме на hh.ru.
    :param raw_text: Исходный текст резюме.
    :return: True, если резюме было создано и отправлено в очередь.
    """
    async with get_postgres_async_session() as postgres_session:
        resume, created = await create_resume_from_hh_service(
            postgres_session=postgres_session,
            hh_id=hh_id,
            raw_text=raw_text,
        )
        if not created:
            return False

        await postgres_session.commit()

    await send_resume_processing_task_service(resume_id=resume.id)
    return True
