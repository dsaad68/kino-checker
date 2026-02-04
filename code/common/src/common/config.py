"""Configuration management using pydantic-settings for type-safe environment variables."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseSettings):
    """Database configuration settings."""

    model_config = SettingsConfigDict(env_prefix="POSTGRES_")

    connection_uri: str = Field(alias="POSTGRES_DB_CONNECTION_URI")
    pool_size: int = 2
    max_overflow: int = 2


class TelegramConfig(BaseSettings):
    """Telegram bot configuration settings."""

    model_config = SettingsConfigDict(env_prefix="TELEGRAM_")

    bot_token: str = Field(alias="TELEGRAM_BOT_TOKEN")


class OpenAIConfig(BaseSettings):
    """OpenAI API configuration settings."""

    model_config = SettingsConfigDict(env_prefix="OPENAI_")

    api_key: str = Field(alias="OPENAI_API_KEY")
    model: str = "gpt-4-0125-preview"


class ElevenLabsConfig(BaseSettings):
    """ElevenLabs API configuration settings."""

    model_config = SettingsConfigDict(env_prefix="ELEVEN_")

    api_key: str = Field(alias="ELEVEN_API_KEY")


class AppConfig(BaseSettings):
    """Main application configuration combining all sub-configurations."""

    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    telegram: TelegramConfig = Field(default_factory=TelegramConfig)
    openai: OpenAIConfig = Field(default_factory=OpenAIConfig)
    elevenlabs: ElevenLabsConfig = Field(default_factory=ElevenLabsConfig)
