# syntax=docker/dockerfile:1.4
# Stage 1: Base
FROM python:3.11-slim-bookworm AS base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1
WORKDIR /app

# Stage 2: Builder
FROM base AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
COPY pyproject.toml uv.lock ./
COPY code/common ./code/common
COPY code/miner ./code/miner
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --package miner

# Stage 3: Development
FROM base AS development
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/code /app/code
ENV PATH="/app/.venv/bin:$PATH"
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser
CMD ["python", "-m", "miner.main"]

# Stage 4: Production
FROM base AS production
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH" \
    TZ=Europe/Berlin
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app && \
    apt-get update && \
    apt-get install -y --no-install-recommends tzdata && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
USER appuser
COPY --from=builder --chown=appuser:appuser /app/code /app/code
CMD ["python", "-O", "-m", "miner.main"]
