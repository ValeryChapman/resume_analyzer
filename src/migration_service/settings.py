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


class ServiceConfig(BaseSettings):
    """Основная конфигурация."""

    # Вложенные блоки конфигурации для отдельных компонентов
    postgres: PostgresConfig = PostgresConfig()


settings: ServiceConfig = ServiceConfig()
