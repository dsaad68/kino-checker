"""Application-wide constants."""

from __future__ import annotations

# Service intervals (seconds)
MINER_POLL_INTERVAL = 600  # 10 minutes
CLEANER_POLL_INTERVAL = 10800  # 3 hours
CLEANER_TRACKABLE_DAYS = 120  # days to keep released films trackable

# Rate limiting
RATE_LIMIT_COMMANDS = 10  # requests per minute
RATE_LIMIT_QUERIES = 5
RATE_LIMIT_VOICE = 3

# Database
DB_POOL_SIZE = 2
DB_MAX_OVERFLOW = 2

# Timezones
DEFAULT_TIMEZONE = "Europe/Berlin"

# File paths
LOG_DIR = "logs"
