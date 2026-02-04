# Deployment Guide

## Production with Docker Compose

1. Set production environment variables (e.g. in `.env` or `.env.production`). Do not commit secrets.

2. Build and start with production overrides:

   ```bash
   just prod
   # or: docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
   ```

3. Base [docker-compose.yml](../docker-compose.yml) defines db, bot, miner, cleaner. [docker-compose.prod.yml](../docker-compose.prod.yml) adds:
   - Production build target (optimized images, `python -O`)
   - Resource limits and reservations
   - Separate volume for prod DB (`db-prod`)

## Environment Variables

See [.env.example](../.env.example) for required variables, including:

- `POSTGRES_*` — Database credentials and DB name
- `POSTGRES_DB_CONNECTION_URI` / `TELEGRAM_BOT_TOKEN` — Used by all services
- `OPENAI_API_KEY`, `ELEVEN_API_KEY` — For bot GenAI and voice

## Logs

Application logs (loguru) can be written to `./logs/` when configured; ensure this directory is created and writable, or use volume mounts as in the compose files.
