"""Configuration management using pydantic-settings for type-safe environment variables."""

from __future__ import annotations

from urllib.parse import quote_plus

from pydantic import AliasChoices, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseSettings):
    """Database configuration settings.

    Either set POSTGRES_DB_CONNECTION_URI, or set POSTGRES_USER, POSTGRES_PASSWORD,
    POSTGRES_DB (and optionally POSTGRES_HOST, POSTGRES_PORT) to build the URI.
    Host defaults to "db" for Docker Compose.
    """

    model_config = SettingsConfigDict(
        env_prefix="POSTGRES_",
        populate_by_name=True,
        env_file=None,  # use only os.environ (e.g. Docker/K8s); no .env file
    )

    # Explicit env name so deployment can set POSTGRES_DB_CONNECTION_URI (prefix can override alias)
    connection_uri_raw: str | None = Field(
        default=None,
        validation_alias=AliasChoices("POSTGRES_DB_CONNECTION_URI", "DB_CONNECTION_URI"),
    )
    user: str = "postgres"
    password: str = ""
    db: str = "kino_tracker"
    host: str = "db"
    port: int = 5432
    pool_size: int = 2
    max_overflow: int = 2

    @model_validator(mode="after")
    def require_uri_or_parts(self) -> DatabaseConfig:
        if self.connection_uri_raw:
            return self
        if not (self.user and self.password and self.db):
            raise ValueError("Set POSTGRES_DB_CONNECTION_URI or POSTGRES_USER, POSTGRES_PASSWORD, and POSTGRES_DB")
        return self

    @property
    def connection_uri(self) -> str:
        """Resolved connection URI (from env or built from user/password/db/host/port)."""
        if self.connection_uri_raw:
            return self.connection_uri_raw
        u = quote_plus(self.user)
        p = quote_plus(self.password)
        return f"postgresql://{u}:{p}@{self.host}:{self.port}/{self.db}"


class TelegramConfig(BaseSettings):
    """Telegram bot configuration settings."""

    model_config = SettingsConfigDict(env_prefix="TELEGRAM_", env_file=None)

    bot_token: str = Field(alias="TELEGRAM_BOT_TOKEN")


class OpenAIConfig(BaseSettings):
    """OpenAI API configuration settings."""

    model_config = SettingsConfigDict(env_prefix="OPENAI_", env_file=None)

    api_key: str = Field(alias="OPENAI_API_KEY")
    model: str = "gpt-4-0125-preview"


class ElevenLabsConfig(BaseSettings):
    """ElevenLabs API configuration settings."""

    model_config = SettingsConfigDict(env_prefix="ELEVEN_", env_file=None)

    api_key: str = Field(alias="ELEVEN_API_KEY")


class AppConfig(BaseSettings):
    """Main application configuration combining all sub-configurations."""

    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    telegram: TelegramConfig = Field(default_factory=TelegramConfig)
    openai: OpenAIConfig = Field(default_factory=OpenAIConfig)
    elevenlabs: ElevenLabsConfig = Field(default_factory=ElevenLabsConfig)
