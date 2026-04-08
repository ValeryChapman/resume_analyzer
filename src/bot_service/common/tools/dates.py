from datetime import datetime
from zoneinfo import ZoneInfo

MOSCOW_TZ = ZoneInfo("Europe/Moscow")


def format_datetime_moscow(dt: datetime) -> str:
    """
    Преобразует объект datetime в строку в московском часовом поясе (MSK).

    :param dt: Объект datetime в любом часовом поясе или UTC.
    :return: Строковое представление даты и времени в МСК.
    """
    if dt is None:
        return "не указано"

    dt = dt.astimezone(tz=MOSCOW_TZ)
    return dt.strftime("%d-%m-%Y %H:%M:%S (%Z)")
