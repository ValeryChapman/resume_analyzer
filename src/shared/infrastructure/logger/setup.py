import logging
from datetime import datetime, timezone
from typing import Any

import orjson


class JsonFormatter(logging.Formatter):
    """Форматтер для логирования в формате JSON."""

    def format(self, record: logging.LogRecord) -> str:
        log_data: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "extra"):
            log_data.update(record.extra)

        # Используем orjson для быстрой сериализации
        return orjson.dumps(log_data).decode("utf-8")


def setup_logging(level: int = logging.INFO) -> None:
    """
    Настройка логирования.

    :param level: Уровень логирования.
    """
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    # Настраиваем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Очищаем существующие обработчики, чтобы избежать дублирования
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    root_logger.addHandler(handler)
