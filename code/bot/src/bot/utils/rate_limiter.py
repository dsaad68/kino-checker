"""Rate limiting functionality for the Telegram bot."""

from __future__ import annotations

import time
from collections import defaultdict
from collections.abc import Callable
from functools import wraps

from telebot import types


class RateLimiter:
    """Simple in-memory rate limiter for bot commands.

    Tracks user requests and enforces rate limits to prevent abuse.
    For production use with multiple instances, consider using Redis.
    """

    def __init__(self, *, max_requests: int = 5, time_window: int = 60) -> None:
        """Initialize rate limiter.

        Args:
            max_requests: Maximum number of requests allowed in time window
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        # user_id -> list of request timestamps
        self._requests: dict[int, list[float]] = defaultdict(list)

    def is_rate_limited(self, user_id: int) -> bool:
        """Check if user is rate limited.

        Args:
            user_id: Telegram user ID

        Returns:
            True if user has exceeded rate limit, False otherwise
        """
        current_time = time.time()
        user_requests = self._requests[user_id]

        # Remove old requests outside the time window
        user_requests[:] = [req_time for req_time in user_requests if current_time - req_time < self.time_window]

        # Check if user has exceeded limit
        if len(user_requests) >= self.max_requests:
            return True

        # Record this request
        user_requests.append(current_time)
        return False

    def get_time_until_reset(self, user_id: int) -> int:
        """Get seconds until rate limit resets for user.

        Args:
            user_id: Telegram user ID

        Returns:
            Seconds until the oldest request expires
        """
        user_requests = self._requests[user_id]
        if not user_requests:
            return 0

        current_time = time.time()
        oldest_request = user_requests[0]
        time_passed = current_time - oldest_request
        time_remaining = max(0, self.time_window - time_passed)

        return int(time_remaining)

    def clear_user(self, user_id: int) -> None:
        """Clear rate limit data for specific user.

        Args:
            user_id: Telegram user ID
        """
        if user_id in self._requests:
            del self._requests[user_id]

    def reset(self) -> None:
        """Clear all rate limit data."""
        self._requests.clear()


def rate_limit(
    limiter: RateLimiter,
    *,
    message_template: str = "You're sending too many requests. Please wait {seconds} seconds before trying again.",
) -> Callable:
    """Decorator to apply rate limiting to bot message handlers.

    Args:
        limiter: RateLimiter instance to use
        message_template: Message template to send when rate limited. Use {seconds} for time remaining.

    Returns:
        Decorator function

    Example:
        >>> limiter = RateLimiter(max_requests=5, time_window=60)
        >>>
        >>> @bot.message_handler(commands=["start"])
        >>> @rate_limit(limiter)
        >>> def start_handler(message):
        >>>     bot.reply_to(message, "Welcome!")
    """

    def decorator(handler: Callable) -> Callable:
        @wraps(handler)
        def wrapper(message: types.Message, *args, **kwargs):
            user_id = message.from_user.id

            if limiter.is_rate_limited(user_id):
                # User is rate limited, send warning
                seconds_remaining = limiter.get_time_until_reset(user_id)
                warning_message = message_template.format(seconds=seconds_remaining)

                # Get bot instance from the handler's context
                # This assumes the bot is available in the global context
                # or passed through args
                try:
                    if hasattr(message, "bot"):
                        message.bot.reply_to(message, warning_message)
                    else:
                        # Try to find bot in args
                        import telebot

                        for arg in args:
                            if isinstance(arg, telebot.TeleBot):
                                arg.reply_to(message, warning_message)
                                break
                except Exception as e:
                    # If we can't send a message, log and skip
                    import logging

                    logging.warning(f"Failed to send rate limit warning: {e}")

                return None

            # User is not rate limited, proceed with handler
            return handler(message, *args, **kwargs)

        return wrapper

    return decorator


# Global rate limiters for different command types
# Stricter limits for resource-intensive operations
COMMAND_LIMITER = RateLimiter(max_requests=10, time_window=60)  # 10 commands per minute
QUERY_LIMITER = RateLimiter(max_requests=5, time_window=60)  # 5 queries per minute
VOICE_LIMITER = RateLimiter(max_requests=3, time_window=60)  # 3 voice requests per minute
