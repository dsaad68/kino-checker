# Kino-Checker Architecture

## System Overview

Kino-Checker is a film tracking and notification system for cinema schedules. It consists of a Telegram bot, a miner service that scrapes and ingests data, a cleaner service for database maintenance, and a shared common library.

## Services

- **Bot** — Telegram interface with AI-powered natural-language queries and voice answers (Langchain SQL agent, Eleven Labs). See [services/bot.md](services/bot.md).
- **Miner** — Web scraping and data collection from cinema APIs and pages. Populates films, performances, and upcoming films; sends release notifications. See [services/miner.md](services/miner.md).
- **Cleaner** — Database maintenance: marks released films, marks old entries as non-trackable. See [services/cleaner.md](services/cleaner.md).
- **Common** — Shared libraries: database models and manager, logging (loguru), constants, health checks, helpers.

## Data Flow

1. Miner fetches film and performance data from external APIs and scrapes upcoming releases.
2. Data is written to PostgreSQL (films, performances, upcoming_films, users).
3. Bot reads from the same database to answer user queries and list upcoming/showing films.
4. When a film is released, Miner notifies subscribed users and updates notification status.
5. Cleaner periodically marks released films and disables tracking for old entries.

## Database

- PostgreSQL 16. Schema and tables are created from [code/init-db/init-db.sql](../code/init-db/init-db.sql).
- Main tables: films, performances, upcoming_films, users (with tracker schema).

## Technology

- Python 3.11+, uv for dependencies, loguru for logging.
- Docker Compose for running db + bot + miner + cleaner; separate dev/prod compose overrides.
