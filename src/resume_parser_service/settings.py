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


class HeadHunterConfig(BaseSettings):
    """Конфигурация для работы с HeadHunter API."""

    model_config = SettingsConfigDict(
        env_file=DOTENV, env_file_encoding="utf-8", extra="ignore"
    )

    base_url: str = Field("https://api.hh.ru", alias="HEADHUNTER_BASE_URL")
    token: str = Field("...", alias="HEADHUNTER_TOKEN")
    timeout: int = Field(30, alias="HEADHUNTER_TIMEOUT", ge=1)
    area: str = Field("1", alias="HEADHUNTER_AREA")
    professional_role: str = Field("11", alias="HEADHUNTER_PROFESSIONAL_ROLE")
    order_by: str = Field("publication_time", alias="HEADHUNTER_ORDER_BY")
    per_page: int = Field(10, alias="HEADHUNTER_PER_PAGE", ge=1, le=100)


class ResumeParserConfig(BaseSettings):
    """Конфигурация фонового парсера резюме."""

    model_config = SettingsConfigDict(
        env_file=DOTENV, env_file_encoding="utf-8", extra="ignore"
    )

    poll_interval_seconds: int = Field(
        300, alias="RESUME_PARSER_SERVICE_POLL_INTERVAL_SECONDS", ge=1
    )
    lookback_seconds: int = Field(
        600,
        alias="RESUME_PARSER_SERVICE_LOOKBACK_SECONDS",
        ge=1,
        description="Окно поиска резюме в секундах. Для последних 10 минут используйте 600.",
    )
    error_sleep_seconds: int = Field(
        30, alias="RESUME_PARSER_SERVICE_ERROR_SLEEP_SECONDS", ge=1
    )


class ServiceConfig(BaseSettings):
    """Основная конфигурация."""

    # Вложенные блоки конфигурации для отдельных компонентов
    postgres: PostgresConfig = PostgresConfig()
    redis: RedisConfig = RedisConfig()
    hh: HeadHunterConfig = HeadHunterConfig()
    resume_parser: ResumeParserConfig = ResumeParserConfig()


settings: ServiceConfig = ServiceConfig()
