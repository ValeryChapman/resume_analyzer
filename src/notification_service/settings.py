from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DOTENV = BASE_DIR / ".env"


class PostgresConfig(BaseSettings):
    """Конфигурация для базы данных PostgreSQL."""

    model_config = SettingsConfigDict(
        env_file=DOTENV, env_file_encoding="utf-8", extra="ignore"
    )

    name: str = Field("...", alias="POSTGRES_DB")
    username: str = Field("...", alias="POSTGRES_USER")
    password: str = Field("...", alias="POSTGRES_PASSWORD")
    host: str = Field("localhost", alias="POSTGRES_HOST")
    port: int = Field(
        5432,
        validation_alias=AliasChoices("POSTGRES_PORT", "POSTGRES_PORT_EXTERNAL"),
    )

    @property
    def url(self) -> str:
        """Получить URL для подключения к базе данных."""
        return f"postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.name}"


class RedisConfig(BaseSettings):
    """Конфигурация для Redis."""

    model_config = SettingsConfigDict(
        env_file=DOTENV, env_file_encoding="utf-8", extra="ignore"
    )

    host: str = Field("localhost", alias="REDIS_HOST")
    port: int = Field(
        6379,
        validation_alias=AliasChoices("REDIS_PORT", "REDIS_PORT_EXTERNAL"),
    )
    db: int = Field(0, alias="REDIS_DB")
    username: str | None = Field(default=None, alias="REDIS_USERNAME")
    password: str | None = Field(default=None, alias="REDIS_PASSWORD")

    @property
    def url(self) -> str:
        """Получить URL для подключения к Redis."""
        credentials = ""
        if self.username and self.password:
            credentials = f"{self.username}:{self.password}@"
        elif self.password:
            credentials = f":{self.password}@"
        elif self.username:
            credentials = f"{self.username}@"

        return f"redis://{credentials}{self.host}:{self.port}/{self.db}"


class TelegramBotConfig(BaseSettings):
    """Конфигурация работы с Telegram Bot."""

    model_config = SettingsConfigDict(
        env_file=DOTENV, env_file_encoding="utf-8", extra="ignore"
    )

    token: str = Field("...", alias="TELEGRAM_BOT_TOKEN")


class NotificationProcessingConfig(BaseSettings):
    """Конфигурация Notification Service."""

    model_config = SettingsConfigDict(
        env_file=DOTENV, env_file_encoding="utf-8", extra="ignore"
    )

    consumer_group: str = Field(
        "notification_service_group", alias="NOTIFICATION_SERVICE_CONSUMER_GROUP"
    )
    consumer_name: str = Field(
        "notification_service_consumer",
        alias="NOTIFICATION_SERVICE_CONSUMER_NAME",
    )
    max_parallel_tasks: int = Field(
        5,
        alias="NOTIFICATION_SERVICE_MAX_PARALLEL_TASKS",
        ge=1,
        le=20,
    )
    read_block_ms: int = Field(5000, alias="NOTIFICATION_SERVICE_READ_BLOCK_MS")
    error_sleep_seconds: int = Field(
        5, alias="NOTIFICATION_SERVICE_ERROR_SLEEP_SECONDS"
    )
    stale_task_idle_ms: int = Field(
        60000,
        alias="NOTIFICATION_SERVICE_STALE_TASK_IDLE_MS",
        ge=1,
    )
    reclaim_batch_size: int = Field(
        5,
        alias="NOTIFICATION_SERVICE_RECLAIM_BATCH_SIZE",
        ge=1,
        le=100,
    )
    max_delivery_attempts: int = Field(
        3,
        alias="NOTIFICATION_SERVICE_MAX_DELIVERY_ATTEMPTS",
        ge=1,
    )


class ServiceConfig(BaseSettings):
    """Основная конфигурация."""

    postgres: PostgresConfig = PostgresConfig()
    redis: RedisConfig = RedisConfig()
    telegram_bot: TelegramBotConfig = TelegramBotConfig()
    notification_processing: NotificationProcessingConfig = (
        NotificationProcessingConfig()
    )


settings: ServiceConfig = ServiceConfig()
