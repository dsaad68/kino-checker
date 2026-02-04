"""Bot context management for state handling without global variables."""

from __future__ import annotations

from dataclasses import dataclass, field

import telebot
from telebot.storage import StateMemoryStorage

from bot.utils.db_info_finder import FilmInfoFinder
from bot.utils.rate_limiter import RateLimiter


@dataclass
class BotContext:
    """Holds bot state and dependencies without using global variables."""

    bot: telebot.TeleBot
    db_info_finder: FilmInfoFinder
    openai_api_key: str
    eleven_api_key: str
    db_dialect_connection_uri: str

    # Rate limiters
    command_limiter: RateLimiter = field(default_factory=lambda: RateLimiter(max_requests=10, time_window=60))
    query_limiter: RateLimiter = field(default_factory=lambda: RateLimiter(max_requests=5, time_window=60))
    voice_limiter: RateLimiter = field(default_factory=lambda: RateLimiter(max_requests=3, time_window=60))

    # Session-specific state (cleared after use)
    upcoming_films_dict: dict[int, str] | None = None
    upcoming_films_list: list[str] | None = None

    @classmethod
    def create(
        cls,
        *,
        token: str,
        sql_connection_uri: str,
        db_dialect_connection_uri: str,
        openai_api_key: str,
        eleven_api_key: str,
    ) -> BotContext:
        """Factory method to create a BotContext with initialized dependencies."""
        state_storage = StateMemoryStorage()
        bot = telebot.TeleBot(token, state_storage=state_storage)
        db_info_finder = FilmInfoFinder(sql_connection_uri)

        return cls(
            bot=bot,
            db_info_finder=db_info_finder,
            openai_api_key=openai_api_key,
            eleven_api_key=eleven_api_key,
            db_dialect_connection_uri=db_dialect_connection_uri,
        )

    def set_upcoming_films(self, films_dict: dict[int, str]) -> None:
        """Set the upcoming films state for current session."""
        self.upcoming_films_dict = films_dict.copy()
        self.upcoming_films_list = list(films_dict.values())

    def clear_upcoming_films(self) -> None:
        """Clear the upcoming films state after use."""
        self.upcoming_films_dict = None
        self.upcoming_films_list = None

    def get_upcoming_films_list(self) -> list[str] | None:
        """Get the current upcoming films list."""
        return self.upcoming_films_list

    def get_upcoming_films_dict(self) -> dict[int, str] | None:
        """Get the current upcoming films dictionary."""
        return self.upcoming_films_dict

    def check_rate_limit(self, user_id: int, limiter: RateLimiter) -> bool:
        """Check if user is rate limited.

        Args:
            user_id: Telegram user ID
            limiter: Rate limiter to check

        Returns:
            True if rate limited, False otherwise
        """
        return limiter.is_rate_limited(user_id)
