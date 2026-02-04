# Project Restructuring & Modernization Plan

## Overview
Reorganize the kino-checker project for better maintainability, remove my_logger in favor of loguru, and improve Docker Compose configuration.

---

## 1. REMOVE MY_LOGGER & MIGRATE TO LOGURU

### Current State
- Custom `my_logger` package wraps opencensus with Azure Application Insights
- Used across all services: bot, miner, cleaner
- Adds complexity with opencensus dependencies

### Changes Required

#### A. Remove my_logger Package
**Files to delete:**
- `/code/my_logger/` (entire directory)
- Remove from workspace: `pyproject.toml` [tool.uv.workspace] members

#### B. Add Loguru to Dependencies
**File:** `/pyproject.toml`
```toml
[dependency-groups.dev]
# Add
loguru>=0.7.0
```

**File:** `/code/common/pyproject.toml`
```toml
[project]
dependencies = [
    # Add
    "loguru>=0.7.0",
    # Remove opencensus dependencies
]
```

#### C. Create Centralized Logging Configuration
**New file:** `/code/common/src/common/logging_config.py`
```python
"""Centralized logging configuration using loguru."""

from __future__ import annotations

import sys
from pathlib import Path

from loguru import logger


def setup_logger(
    *,
    service_name: str,
    log_level: str = "INFO",
    log_file: Path | None = None,
    enable_json: bool = False,
) -> None:
    """Configure loguru logger for the service.

    Args:
        service_name: Name of the service (bot, miner, cleaner)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional file path for log output
        enable_json: Enable JSON structured logging
    """
    # Remove default handler
    logger.remove()

    # Console handler with color
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
        level=log_level,
        colorize=True,
    )

    # File handler (if specified)
    if log_file:
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level=log_level,
            rotation="10 MB",
            retention="7 days",
            compression="zip",
            serialize=enable_json,
        )

    # Add service context
    logger.configure(extra={"service": service_name})

    logger.info(f"Logger initialized for {service_name}")


def get_logger():
    """Get the configured logger instance."""
    return logger
```

#### D. Update Service Entry Points

**File:** `/code/bot/src/bot/main.py`
```python
# Replace:
from my_logger import Logger
logger = Logger(file_handler=True)
logger.get_logger()

# With:
from loguru import logger
from common.logging_config import setup_logger

setup_logger(
    service_name="bot",
    log_level="INFO",
    log_file=Path("logs/bot.log")
)
```

**File:** `/code/miner/src/miner/main.py`
```python
# Same pattern
from loguru import logger
from common.logging_config import setup_logger

setup_logger(
    service_name="miner",
    log_level="INFO",
    log_file=Path("logs/miner.log")
)
```

**File:** `/code/cleaner/src/cleaner/main.py`
```python
# Same pattern
from loguru import logger
from common.logging_config import setup_logger

setup_logger(
    service_name="cleaner",
    log_level="INFO",
    log_file=Path("logs/cleaner.log")
)
```

#### E. Update All logging.* Calls
Search and replace throughout codebase:
```python
# Replace
import logging
logging.info("message")
logging.error("message")
logging.warning("message")

# With
from loguru import logger
logger.info("message")
logger.error("message")
logger.warning("message")
```

**Files to update:**
- `/code/bot/src/bot/main.py`
- `/code/bot/src/bot/genai/agent.py`
- `/code/bot/src/bot/utils/db_info_finder.py`
- `/code/miner/src/miner/main.py`
- `/code/miner/src/miner/utils/film_db_manager.py`
- `/code/miner/src/miner/utils/film_fetcher.py`
- `/code/miner/src/miner/utils/film_notifier.py`
- `/code/miner/src/miner/utils/scrapper.py`
- `/code/cleaner/src/cleaner/main.py`
- `/code/cleaner/src/cleaner/utils/db_cleaner.py`
- `/code/common/src/common/db/manager.py`

#### F. Remove Opencensus Dependencies
**Files to update:**
- `/code/bot/pyproject.toml` - Remove opencensus dependencies
- `/code/miner/pyproject.toml` - Remove opencensus dependencies
- `/code/cleaner/pyproject.toml` - Remove opencensus dependencies

---

## 2. IMPROVE PROJECT STRUCTURE

### A. Consolidate Test Utilities

**Problem:** Duplicate `integration_db/` folders in each service's tests

**Solution:** Create shared test utilities

**New structure:**
```
code/
├── testing/                          # NEW
│   ├── __init__.py
│   ├── fixtures.py                   # Shared test fixtures
│   └── utils.py                      # Test helpers
└── conftest.py                       # Import from testing/
```

**New file:** `/code/testing/fixtures.py`
```python
"""Shared test fixtures and utilities."""

from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope="session")
def postgres_container() -> PostgresContainer:
    """Start a PostgreSQL container for the test session."""
    container = PostgresContainer("postgres:16-alpine")
    container.start()
    yield container
    container.stop()


# ... move all fixtures from code/conftest.py here
```

**Update:** `/code/conftest.py`
```python
"""Root conftest - imports from testing package."""
from testing.fixtures import *  # noqa: F403, F401
```

**Remove:**
- `/code/bot/tests/bot/integration_db/`
- `/code/miner/tests/miner/integration_db/`
- `/code/cleaner/tests/cleaner/integration_db/`

### B. Centralize Constants

**New file:** `/code/common/src/common/constants.py`
```python
"""Application-wide constants."""

from __future__ import annotations

# Service intervals (seconds)
MINER_POLL_INTERVAL = 600  # 10 minutes
CLEANER_POLL_INTERVAL = 10800  # 3 hours

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
```

**Update services to import from constants:**
```python
from common.constants import MINER_POLL_INTERVAL, DEFAULT_TIMEZONE
```

### C. Standardize Module Organization

**Current issues:** Inconsistent directory structure across services

**Proposed standard:**
```
service/
├── Dockerfile
├── pyproject.toml
├── src/
│   └── service_name/
│       ├── __init__.py
│       ├── main.py              # Entry point
│       ├── config.py            # Service-specific config (optional)
│       ├── models.py            # Pydantic models (optional)
│       └── services/            # Business logic (rename from utils/)
│           ├── __init__.py
│           └── *.py
└── tests/
    ├── conftest.py
    └── service_name/
        ├── __init__.py
        └── *_test.py
```

**Refactor:**
- Rename `utils/` to `services/` in bot, miner, cleaner
- Move business logic to `services/`
- Keep `utils/` only for generic helpers

### D. Add Documentation Directory

**New structure:**
```
docs/
├── README.md                     # Documentation index
├── architecture.md               # System architecture
├── services/
│   ├── bot.md                   # Bot service details
│   ├── miner.md                 # Miner service details
│   └── cleaner.md               # Cleaner service details
├── deployment.md                # Deployment guide
├── development.md               # Development setup
├── api.md                       # API documentation
└── diagrams/
    ├── data-flow.png
    └── architecture.png
```

**Content for `/docs/architecture.md`:**
```markdown
# Kino-Checker Architecture

## System Overview
[Diagram of services and their interactions]

## Services
- **Bot**: Telegram interface with AI-powered queries
- **Miner**: Web scraping and data collection
- **Cleaner**: Database maintenance
- **Common**: Shared libraries and utilities

## Data Flow
[Describe how data moves through the system]

## Database Schema
[Link to schema documentation]
```

---

## 3. IMPROVE DOCKER COMPOSE

### A. Create Development & Production Configs

**Problem:** Single docker-compose.yml mixes dev and prod concerns

**Solution:** Split into multiple files

#### Development Configuration
**New file:** `/docker-compose.dev.yml`
```yaml
services:
  db:
    image: postgres:16-alpine
    container_name: kino-db-dev
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-dev_password}
      POSTGRES_DB: ${POSTGRES_DB:-kino_tracker}
    ports:
      - "5432:5432"  # Exposed for local development
    volumes:
      - db-dev:/var/lib/postgresql/data
      - ./code/init-db/init-db.sql:/docker-entrypoint-initdb.d/init-db.sql:ro
    networks:
      - app-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-postgres}"]
      interval: 5s
      timeout: 5s
      retries: 5

  miner:
    build:
      context: .
      dockerfile: ./code/miner/Dockerfile
      target: development  # New dev target
    container_name: kino-miner-dev
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./code/miner/src:/app/code/miner/src:ro  # Mount source for hot reload
      - ./code/common/src:/app/code/common/src:ro
      - ./logs:/app/logs
    networks:
      - app-network
    restart: unless-stopped

  bot:
    build:
      context: .
      dockerfile: ./code/bot/Dockerfile
      target: development
    container_name: kino-bot-dev
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./code/bot/src:/app/code/bot/src:ro
      - ./code/common/src:/app/code/common/src:ro
      - ./logs:/app/logs
    networks:
      - app-network
    restart: unless-stopped

  cleaner:
    build:
      context: .
      dockerfile: ./code/cleaner/Dockerfile
      target: development
    container_name: kino-cleaner-dev
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./code/cleaner/src:/app/code/cleaner/src:ro
      - ./code/common/src:/app/code/common/src:ro
      - ./logs:/app/logs
    networks:
      - app-network
    restart: unless-stopped

  # Optional: pgAdmin for database management
  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: kino-pgadmin
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@example.com
      PGADMIN_DEFAULT_PASSWORD: admin
    ports:
      - "5050:80"
    networks:
      - app-network
    restart: unless-stopped

volumes:
  db-dev:
    driver: local

networks:
  app-network:
    driver: bridge
```

#### Production Configuration
**New file:** `/docker-compose.prod.yml`
```yaml
services:
  db:
    image: postgres:16-alpine
    container_name: kino-db-prod
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - db-prod:/var/lib/postgresql/data
      - ./code/init-db/init-db.sql:/docker-entrypoint-initdb.d/init-db.sql:ro
    networks:
      - app-network
    restart: always
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G

  miner:
    build:
      context: .
      dockerfile: ./code/miner/Dockerfile
      target: production
    container_name: kino-miner-prod
    env_file:
      - .env.production
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./logs:/app/logs
    networks:
      - app-network
    restart: always
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M

  bot:
    build:
      context: .
      dockerfile: ./code/bot/Dockerfile
      target: production
    container_name: kino-bot-prod
    env_file:
      - .env.production
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./logs:/app/logs
    networks:
      - app-network
    restart: always
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M

  cleaner:
    build:
      context: .
      dockerfile: ./code/cleaner/Dockerfile
      target: production
    container_name: kino-cleaner-prod
    env_file:
      - .env.production
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./logs:/app/logs
    networks:
      - app-network
    restart: always
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M
        reservations:
          cpus: '0.25'
          memory: 128M

volumes:
  db-prod:
    driver: local

networks:
  app-network:
    driver: bridge
```

**Keep:** `/docker-compose.yml` as base configuration (can extend with `-f`)

### B. Add Health Check Endpoints

**New file:** `/code/common/src/common/health.py`
```python
"""Health check utilities for services."""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.engine import Engine


def check_database_health(engine: Engine) -> bool:
    """Check if database connection is healthy.

    Returns:
        True if database is accessible, False otherwise
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def get_service_status(
    *,
    service_name: str,
    db_engine: Engine | None = None,
) -> dict[str, str | bool]:
    """Get service health status.

    Returns:
        Dictionary with service status information
    """
    status = {
        "service": service_name,
        "status": "healthy",
        "database": True if db_engine is None else check_database_health(db_engine),
    }

    if not status["database"]:
        status["status"] = "unhealthy"

    return status
```

**Add health endpoints to services:**
- Create simple HTTP endpoint (using aiohttp) in each service
- Expose `/health` endpoint
- Update docker-compose health checks to use HTTP

### C. Add Monitoring & Observability

**New file:** `/docker-compose.monitoring.yml`
```yaml
services:
  prometheus:
    image: prom/prometheus:latest
    container_name: kino-prometheus
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - app-network
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: kino-grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
    ports:
      - "3000:3000"
    networks:
      - app-network
    restart: unless-stopped
    depends_on:
      - prometheus

volumes:
  prometheus-data:
  grafana-data:

networks:
  app-network:
    external: true
```

**New file:** `/monitoring/prometheus.yml`
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'kino-checker'
    static_configs:
      - targets:
          - 'bot:8000'
          - 'miner:8000'
          - 'cleaner:8000'
```

### D. Improve Dockerfile Multi-Stage Builds

**Update pattern for all services:**

```dockerfile
# Stage 1: Base
FROM python:3.12-slim-bookworm AS base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1
WORKDIR /app

# Stage 2: Builder
FROM base AS builder
RUN pip install --no-cache-dir uv
COPY pyproject.toml uv.lock ./
COPY code/common ./code/common
COPY code/SERVICE ./code/SERVICE
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --package SERVICE

# Stage 3: Development
FROM base AS development
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/code /app/code
ENV PATH="/app/.venv/bin:$PATH"
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser
CMD ["python", "-m", "SERVICE.main"]

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
CMD ["python", "-O", "-m", "SERVICE.main"]
```

**Benefits:**
- Separate development and production targets
- Development includes source code mounting
- Production is optimized (-O flag)
- Clear separation of concerns

---

## 4. ADDITIONAL IMPROVEMENTS

### A. Add Makefile for Common Tasks

**New file:** `/Makefile`
```makefile
.PHONY: help install test lint format clean dev prod

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run linting"
	@echo "  make format     - Format code"
	@echo "  make clean      - Clean build artifacts"
	@echo "  make dev        - Start development environment"
	@echo "  make prod       - Start production environment"

install:
	uv sync --all-packages --dev

test:
	uv run pytest -v

test-cov:
	uv run pytest --cov --cov-report=html

lint:
	uv run ruff check code/

format:
	uv run ruff format code/

typecheck:
	uv run mypy code/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf htmlcov .coverage

dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

prod:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

stop:
	docker compose down

logs:
	docker compose logs -f

shell-bot:
	docker compose exec bot /bin/bash

shell-miner:
	docker compose exec miner /bin/bash

shell-db:
	docker compose exec db psql -U postgres -d kino_tracker
```

### B. Create .dockerignore

**New file:** `/.dockerignore`
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
*.egg-info/
dist/
build/

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# IDE
.vscode/
.idea/
*.swp
*.swo
.DS_Store

# Git
.git/
.gitignore

# Documentation
*.md
docs/

# Logs
logs/
*.log

# Environment
.env
.env.*

# Docker
Dockerfile
docker-compose*.yml
```

### C. Update README.md

**File:** `/README.md`
```markdown
# Kino-Checker

Film tracking and notification system for cinema schedules.

## Quick Start

### Development
```bash
# Install dependencies
make install

# Start services
make dev

# Run tests
make test
```

### Production
```bash
# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Start services
make prod
```

## Architecture

See [docs/architecture.md](docs/architecture.md) for detailed system architecture.

## Services

- **Bot**: Telegram bot with AI-powered queries
- **Miner**: Web scraping and data collection
- **Cleaner**: Database maintenance

## Documentation

- [Development Guide](docs/development.md)
- [Deployment Guide](docs/deployment.md)
- [API Documentation](docs/api.md)

## License

[Your License]
```

---

## 5. MIGRATION CHECKLIST

### Phase 1: Logging Migration
- [ ] Create `/code/common/src/common/logging_config.py`
- [ ] Add loguru to dependencies
- [ ] Update all services to use loguru
- [ ] Remove my_logger from workspace
- [ ] Remove opencensus dependencies
- [ ] Test logging output

### Phase 2: Structure Improvements
- [ ] Create `/code/testing/` package
- [ ] Move test utilities to shared location
- [ ] Remove duplicate integration_db folders
- [ ] Create `/code/common/src/common/constants.py`
- [ ] Update services to use centralized constants
- [ ] Rename `utils/` to `services/` in each service

### Phase 3: Docker Improvements
- [ ] Create `docker-compose.dev.yml`
- [ ] Create `docker-compose.prod.yml`
- [ ] Update Dockerfiles with dev/prod targets
- [ ] Create `.dockerignore`
- [ ] Add health check endpoints
- [ ] Test development environment
- [ ] Test production build

### Phase 4: Documentation
- [ ] Create `/docs/` directory
- [ ] Write architecture documentation
- [ ] Document each service
- [ ] Create deployment guide
- [ ] Create development guide
- [ ] Create Makefile
- [ ] Update README.md

### Phase 5: Testing & Validation
- [ ] Run full test suite
- [ ] Test docker-compose dev
- [ ] Test docker-compose prod
- [ ] Verify logging works correctly
- [ ] Check all services start properly
- [ ] Validate configuration management

---

## 6. VERIFICATION PLAN

### After Implementation

#### 1. Logging Verification
```bash
# Start services
make dev

# Check logs
make logs

# Verify loguru output format
docker compose logs bot | grep "service"
```

#### 2. Docker Compose Verification
```bash
# Development
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
# Check services start
# Check database connection
# Check log volumes

# Production
docker compose -f docker-compose.yml -f docker-compose.prod.yml build
# Verify image sizes reduced
# Check resource limits applied
```

#### 3. Test Suite Verification
```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Check no import errors from removed my_logger
```

#### 4. Code Quality Verification
```bash
# Linting
make lint

# Formatting
make format

# Type checking
make typecheck
```

---

## EXPECTED OUTCOMES

### Benefits
1. **Simplified Logging**: loguru is more intuitive than opencensus wrapper
2. **Better Organization**: Clear separation of dev/prod configs
3. **Reduced Duplication**: Shared test utilities
4. **Improved Developer Experience**: Makefile for common tasks
5. **Better Documentation**: Centralized in /docs
6. **Easier Deployment**: Separate docker-compose files
7. **Health Monitoring**: Built-in health checks
8. **Resource Management**: Proper limits and reservations

### Metrics
- **Reduced Dependencies**: ~5 fewer packages (opencensus libs)
- **Smaller Images**: Development target slightly larger (source mounts), production unchanged
- **Faster Development**: Hot reload with volume mounts
- **Code Reduction**: ~200 lines removed (my_logger + duplicates)
- **Improved Maintainability**: Centralized configuration and constants

---

## CRITICAL FILES

### To Create
- `/code/common/src/common/logging_config.py`
- `/code/common/src/common/constants.py`
- `/code/common/src/common/health.py`
- `/code/testing/fixtures.py`
- `/docker-compose.dev.yml`
- `/docker-compose.prod.yml`
- `/Makefile`
- `/.dockerignore`
- `/docs/architecture.md`
- `/docs/development.md`
- `/docs/deployment.md`

### To Modify
- `/pyproject.toml` (remove my_logger, add loguru)
- `/code/*/pyproject.toml` (remove opencensus, add loguru)
- `/code/*/Dockerfile` (add dev/prod targets)
- All service main.py files (use loguru)
- All files with `logging.*` imports
- `/README.md`

### To Delete
- `/code/my_logger/` (entire directory)
- `/code/*/tests/*/integration_db/` (4 directories)

---

## IMPLEMENTATION ORDER

1. **Logging Migration** (1-2 hours)
   - Create logging_config.py
   - Update dependencies
   - Replace imports
   - Remove my_logger

2. **Structure Improvements** (1 hour)
   - Create testing package
   - Create constants.py
   - Remove duplicates

3. **Docker Improvements** (2 hours)
   - Create dev/prod compose files
   - Update Dockerfiles
   - Test builds

4. **Documentation** (1 hour)
   - Create docs directory
   - Write key documentation
   - Create Makefile

5. **Testing & Validation** (1 hour)
   - Run test suite
   - Test docker environments
   - Verify all changes

**Total Estimated Time: 6-7 hours**
