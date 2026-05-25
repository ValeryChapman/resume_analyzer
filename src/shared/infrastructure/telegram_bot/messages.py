from shared.infrastructure.postgres.models.match_result import MatchResult


def match_result_details_message(match_result: MatchResult) -> str:
    """
    Формирует текст сообщения с деталями результата сопоставления.

    :param match_result: Объект MatchResult.
    :return: Текст сообщения.
    """
    vacancy = match_result.vacancy
    resume = match_result.resume

    resume_url = (
        f"https://hh.ru/resume/{resume.hh_id}" if resume.hh_id else "Ссылка отсутствует"
    )

    return (
        f"🔥 <b>Найден подходящий кандидат!</b>\n\n"
        f"<b>Вакансия:</b> {vacancy.title or 'Без названия'}\n"
        f"<b>Оценка соответствия:</b> {int(match_result.score)}%\n\n"
        f"<b>Краткая сводка:</b> \n<blockquote>{resume.summary or 'Информация отсутствует'}</blockquote>\n\n"
        f"<b>Обоснование:</b> \n<blockquote expandable>{match_result.reasoning}</blockquote>\n\n"
        f'<a href="{resume_url}">Открыть резюме на HeadHunter</a>'
    )
