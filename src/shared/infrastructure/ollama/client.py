import logging

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

_ollama_async_client: AsyncOpenAI | None = None


def init_ollama_async_client(
    base_url: str, api_key: str, timeout: int = 120
) -> AsyncOpenAI:
    """
    Инициализирует глобальный асинхронный клиент Ollama.

    :param base_url: Базовый URL Ollama API.
    :param api_key: API ключ.
    :param timeout: Таймаут в секундах.
    :return: Экземпляр AsyncOpenAI.
    """
    global _ollama_async_client

    if _ollama_async_client is None:
        _ollama_async_client = AsyncOpenAI(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
        )

    return _ollama_async_client


def get_ollama_async_client() -> AsyncOpenAI:
    """
    Возвращает асинхронный клиент Ollama.

    :return: Экземпляр AsyncOpenAI.
    """
    if _ollama_async_client is None:
        raise RuntimeError(
            "Клиент Ollama не инициализирован. "
            "Вызовите init_ollama_async_client(...) перед использованием."
        )

    return _ollama_async_client
