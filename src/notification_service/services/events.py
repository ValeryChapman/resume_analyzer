import logging
from uuid import UUID

from aiogram import Bot
from aiogram.enums import ParseMode

from shared.infrastructure.postgres.session import get_postgres_async_session
from shared.infrastructure.telegram_bot.client import get_telegram_bot_client
from shared.services.match_results import get_match_result_by_id_service

logger = logging.getLogger(__name__)


async def process_match_found_event(match_result_id: UUID) -> None:
    """
    Формирует и отправляет уведомление о найденном соответствии.

    :param match_result_id: Идентификатор результата сравнения.
    """
    async with get_postgres_async_session() as session:
        match_result = await get_match_result_by_id_service(
            postgres_session=session, match_result_id=match_result_id
        )
        if not match_result:
            logger.error(
                f"Результат сопоставления не найден: match_result_id={match_result_id}"
            )
            return

        vacancy = match_result.vacancy
        resume = match_result.resume
        user = vacancy.user

    # Формируем сообщение
    resume_url = (
        f"https://hh.ru/resume/{resume.hh_id}" if resume.hh_id else "Ссылка отсутствует"
    )
    message_text = (
        f"🔥 <b>Найден подходящий кандидат!</b>\n\n"
        f"<b>Вакансия:</b> {vacancy.title or 'Без названия'}\n"
        f"<b>Оценка соответствия:</b> {int(match_result.score)}%\n\n"
        f"<b>Краткая сводка:</b> \n<blockquote>{resume.summary or 'Информация отсутствует'}</blockquote>\n\n"
        f"<b>Обоснование:</b> \n<blockquote expandable>{match_result.reasoning}</blockquote>\n\n"
        f'<a href="{resume_url}">Открыть резюме на HeadHunter</a>'
    )

    bot: Bot = await get_telegram_bot_client()
    try:
        await bot.send_message(
            chat_id=user.telegram_id,
            text=message_text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
        logger.info(f"Уведомление успешно отправлено пользователю {user.telegram_id}")
    except Exception as exc:
        logger.error(f"Ошибка при отправке сообщения в Telegram: {exc}", exc_info=True)
        raise
