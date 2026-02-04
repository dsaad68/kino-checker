# Development Guide

## Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) for package management
- Docker and Docker Compose (for full stack or test DB)
- [just](https://github.com/casey/just) (optional, for task runner)

## Setup

1. Clone the repo and install dependencies:

   ```bash
   uv sync
   ```

2. Copy environment template and set variables:

   ```bash
   cp .env.example .env
   # Edit .env with your Telegram bot token, OpenAI key, Eleven Labs key, DB URI
   ```

## Running Locally

- **Full stack (Docker, dev overrides, with source mounts):**

  ```bash
  just dev
  # or: docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
  ```

- **Tests (no external DB; testcontainers start Postgres):**

  ```bash
  just test
  # or: uv run pytest
  ```

- **Lint and format:**

  ```bash
  just lint
  just format
  ```

## Project Layout

- `code/bot` — Telegram bot
- `code/miner` — Scraper and notifier
- `code/cleaner` — DB maintenance
- `code/common` — Shared code (db, logging, constants, health)
- `code/testing` — Shared test fixtures and helpers
- `code/init-db` — SQL schema and sample data

Tests live under `code/*/tests` and use fixtures from `code/conftest.py` (which pulls from `code/testing/fixtures.py`).
