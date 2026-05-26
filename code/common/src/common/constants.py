"""Application-wide constants."""

from __future__ import annotations

# Service intervals (seconds)
MINER_POLL_INTERVAL = 1200  # 20 minutes
CLEANER_POLL_INTERVAL = 43200  # 12 hours
CLEANER_TRACKABLE_DAYS = 120  # days to keep released films trackable

# Miner fetch window: API rejects date_from more than 2 days in the past (error C-OL-18)
MINER_FETCH_WINDOW_DAYS = 90

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
