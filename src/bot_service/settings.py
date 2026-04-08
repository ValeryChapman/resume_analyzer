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

    @property
    def sync_url(self) -> str:
        """Получить синхронный URL для подключения к базе данных."""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.name}"


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


class BrandingConfig(BaseSettings):
    """Конфигурация брендовых параметров Telegram-бота."""

    model_config = SettingsConfigDict(
        env_file=DOTENV, env_file_encoding="utf-8", extra="ignore"
    )

    bot_name: str = Field("...", alias="TELEGRAM_BOT_NAME")


class ServiceConfig(BaseSettings):
    """Основная конфигурация."""

    # Вложенные блоки конфигурации для отдельных компонентов
    postgres: PostgresConfig = PostgresConfig()
    redis: RedisConfig = RedisConfig()
    telegram_bot: TelegramBotConfig = TelegramBotConfig()
    branding: BrandingConfig = BrandingConfig()


settings: ServiceConfig = ServiceConfig()
