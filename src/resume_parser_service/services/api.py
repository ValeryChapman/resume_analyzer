from datetime import datetime

import httpx

from resume_parser_service.schemas.get_resume_detail import HHResumeDetailResponseSchema
from resume_parser_service.schemas.get_resume_search import HHResumeSearchResponseSchema
from resume_parser_service.settings import settings


async def get_resume_search_api_service(
    date_from: datetime, date_to: datetime, timeout: int = 30
) -> HHResumeSearchResponseSchema:
    """
    Загружает страницу поиска резюме из HeadHunter.

    :param date_from: Нижняя граница окна поиска.
    :param date_to: Верхняя граница окна поиска.
    :param timeout: Таймаут запроса в секундах.
    :return: Валидированный ответ HeadHunter API.
    """
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(
            url=f"{settings.hh.base_url}/resumes",
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {settings.hh.token}",
            },
            params=[
                ("date_from", date_from.strftime("%Y-%m-%dT%H:%M:%S")),
                ("date_to", date_to.strftime("%Y-%m-%dT%H:%M:%S")),
                ("order_by", settings.hh.order_by),
                ("area", settings.hh.area),
                ("professional_role", settings.hh.professional_role),
                ("per_page", str(settings.hh.per_page)),
            ],
        )
        response.raise_for_status()
        return HHResumeSearchResponseSchema.model_validate(response.json())


async def get_resume_detail_api_service(
    resume_url: str, timeout: int = 30
) -> HHResumeDetailResponseSchema:
    """
    Загружает полное представление резюме по URL из HeadHunter API.

    :param resume_url: URL детального представления резюме.
    :param timeout: Таймаут запроса в секундах.
    :return: Валидированный ответ HeadHunter API.
    """
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(
            url=resume_url,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {settings.hh.token}",
            },
        )
        response.raise_for_status()
        return HHResumeDetailResponseSchema.model_validate(response.json())
