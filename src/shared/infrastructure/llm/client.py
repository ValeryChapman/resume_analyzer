import logging

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

_llm_async_client: AsyncOpenAI | None = None


def init_llm_async_client(
    base_url: str, api_key: str, timeout: int = 120
) -> AsyncOpenAI:
    """
    Инициализирует глобальный асинхронный клиент для работы с LLM.

    :param base_url: Базовый URL.
    :param api_key: API ключ.
    :param timeout: Тайм-аут в секундах.
    :return: Экземпляр AsyncOpenAI.
    """
    global _llm_async_client

    if _llm_async_client is None:
        _llm_async_client = AsyncOpenAI(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
        )

    return _llm_async_client


def get_llm_async_client() -> AsyncOpenAI:
    """
    Возвращает асинхронный клиент Ollama.

    :return: Экземпляр AsyncOpenAI.
    """
    if _llm_async_client is None:
        raise RuntimeError(
            "Клиент для работы с LLM не инициализирован. "
            "Вызовите init_llm_async_client(...) перед использованием."
        )

    return _llm_async_client
