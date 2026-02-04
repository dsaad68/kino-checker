# syntax=docker/dockerfile:1.4

# Build stage
FROM python:3.11-slim-bookworm AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set environment variables
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Copy workspace files
COPY pyproject.toml uv.lock ./
COPY code/my_logger ./code/my_logger
COPY code/common ./code/common
COPY code/miner ./code/miner

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --package miner

# Runtime stage
FROM python:3.11-slim-bookworm

# Create non-root user
RUN useradd -m -u 1000 appuser

# Set timezone
ENV TZ="Europe/Berlin"
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv
COPY --from=builder --chown=appuser:appuser /app/code /app/code

# Add venv to PATH
ENV PATH="/app/.venv/bin:$PATH"

USER appuser

EXPOSE 80

CMD ["python", "-m", "miner.main"]
