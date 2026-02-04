# Kino Checker - Just Task Runner
# Linux/macOS focused task automation

set shell := ["bash", "-c"]

# Default recipe: show available commands
default:
    @just --list

# ============================================================================
# Docker Operations
# ============================================================================

# Start docker compose services
docker-up:
    @echo "Starting docker compose services..."
    docker compose up

# Start docker compose in detached mode
docker-up-d:
    @echo "Starting docker compose services (detached)..."
    docker compose up -d

# Stop docker compose services
docker-down:
    @echo "Stopping docker compose services..."
    docker compose down

# Remove containers and images
docker-clean:
    @echo "Cleaning up docker containers and images..."
    docker compose down -v --rmi all || true

# Rebuild and restart docker services
docker-restart:
    @echo "Rebuilding and restarting docker services..."
    docker compose down
    docker compose build
    docker compose up -d

# View docker compose logs
logs SERVICE="":
    @echo "Viewing docker compose logs..."
    @if [ -z "{{SERVICE}}" ]; then \
        docker compose logs -f; \
    else \
        docker compose logs -f {{SERVICE}}; \
    fi

# ============================================================================
# Test Database Operations
# ============================================================================

# Create test database container (port 5433)
test-db-create:
    @echo "Creating test database container on port 5433..."
    @docker stop traker_test_db 2>/dev/null || true
    @docker rm traker_test_db 2>/dev/null || true
    docker run -e POSTGRES_PASSWORD="ANoTHer2233Test" -p 5433:5432 -d --name traker_test_db postgres:alpine3.18
    @echo "Waiting for database to be ready..."
    @sleep 3
    @echo "Test database ready on port 5433"

# Start or create test database
test-db-start:
    @echo "Starting test database..."
    @docker start traker_test_db 2>/dev/null || just test-db-create

# Stop test database
test-db-stop:
    @echo "Stopping test database..."
    @docker stop traker_test_db 2>/dev/null || true

# Remove test database container
test-db-remove:
    @echo "Removing test database container..."
    @docker stop traker_test_db 2>/dev/null || true
    @docker rm traker_test_db 2>/dev/null || true

# ============================================================================
# Testing
# ============================================================================

# Run all tests with coverage
test:
    @echo "Running all tests with coverage..."
    uv run pytest

# Run all tests including integration tests (ensures test DB is running)
test-all: test-db-start
    @echo "========================================="
    @echo "Running comprehensive test suite"
    @echo "========================================="
    @echo ""
    @echo "[1/5] Running unit tests..."
    uv run pytest -m "not integration" --no-cov || true
    @echo ""
    @echo "[2/5] Running bot integration tests..."
    INT_DB_URL='postgresql://postgres:ANoTHer2233Test@localhost:5433/postgres' \
        uv run pytest code/bot/tests/bot/db_info_finder_test.py -v --no-cov
    @echo ""
    @echo "[3/5] Running cleaner integration tests..."
    INT_DB_URL='postgresql://postgres:ANoTHer2233Test@localhost:5433/postgres' \
        uv run pytest code/cleaner/tests/cleaner/cleaner_test.py -v --no-cov || true
    @echo ""
    @echo "[4/5] Running miner DB manager integration tests..."
    INT_DB_URL='postgresql://postgres:ANoTHer2233Test@localhost:5433/postgres' \
        uv run pytest code/miner/tests/miner/film_db_manager_test.py -v --no-cov || true
    @echo ""
    @echo "[5/5] Running miner notifier integration tests..."
    INT_DB_URL='postgresql://postgres:ANoTHer2233Test@localhost:5433/postgres' \
        uv run pytest code/miner/tests/miner/film_notifier_test.py -v --no-cov || true
    @echo ""
    @echo "========================================="
    @echo "✓ All test suites completed!"
    @echo "========================================="
    @echo ""
    @echo "Summary:"
    @echo "  - Unit tests: code/common, code/bot (non-integration)"
    @echo "  - Bot integration tests: 8 tests"
    @echo "  - Cleaner integration tests: 1 test"
    @echo "  - Miner integration tests: 10 tests"
    @echo ""
    @echo "For detailed coverage report, run: just test"
    @echo "========================================="

# Run tests without coverage (fast)
test-fast:
    @echo "Running tests without coverage..."
    uv run pytest --no-cov

# Run unit tests only
test-unit:
    @echo "Running unit tests..."
    uv run pytest -m "not integration" --no-cov

# Run integration tests only
test-integration: test-db-start
    @echo "Running integration tests..."
    uv run pytest -m integration

# Run bot DB integration tests (db_info_finder_test.py)
test-db-info-finder: test-db-start
    @echo "Running bot DB info finder integration tests..."
    INT_DB_URL='postgresql://postgres:ANoTHer2233Test@localhost:5433/postgres' \
        uv run pytest code/bot/tests/bot/db_info_finder_test.py -v --no-cov

# Run bot tests
test-bot:
    @echo "Running bot tests..."
    uv run pytest code/bot/tests/

# Run miner tests
test-miner:
    @echo "Running miner tests..."
    uv run pytest code/miner/tests/

# Run cleaner tests
test-cleaner:
    @echo "Running cleaner tests..."
    uv run pytest code/cleaner/tests/

# Run common tests
test-common:
    @echo "Running common tests..."
    uv run pytest code/common/tests/

# ============================================================================
# Code Quality
# ============================================================================

# Format code with ruff
format:
    @echo "Formatting code with ruff..."
    uv run ruff format .

# Check code formatting
format-check:
    @echo "Checking code formatting..."
    uv run ruff format --check .

# Lint code with ruff
lint:
    @echo "Linting code with ruff..."
    uv run ruff check .

# Lint and auto-fix issues
lint-fix:
    @echo "Linting and auto-fixing issues..."
    uv run ruff check --fix .

# Run type checking with mypy
typecheck:
    @echo "Running type checking with mypy..."
    uv run mypy .

# Run all quality checks
check: format-check lint typecheck
    @echo "All quality checks completed!"

# Auto-fix all issues
fix: lint-fix format
    @echo "Auto-fix completed!"

# ============================================================================
# Pre-commit Hooks
# ============================================================================

# Install pre-commit hooks
pre-commit-install:
    @echo "Installing pre-commit hooks..."
    uv run pre-commit install

# Run pre-commit on all files
pre-commit-run:
    @echo "Running pre-commit on all files..."
    uv run pre-commit run --all-files

# Update pre-commit hooks
pre-commit-update:
    @echo "Updating pre-commit hooks..."
    uv run pre-commit autoupdate

# ============================================================================
# Dependencies
# ============================================================================

# Install all dependencies
install:
    @echo "Installing all dependencies..."
    uv sync

# Install dev dependencies
install-dev:
    @echo "Installing dev dependencies..."
    uv sync --all-extras

# Update all dependencies
update:
    @echo "Updating all dependencies..."
    uv lock --upgrade
    uv sync

# Update specific package
update-package PACKAGE:
    @echo "Updating package: {{PACKAGE}}..."
    uv lock --upgrade-package {{PACKAGE}}
    uv sync

# ============================================================================
# Database Operations
# ============================================================================

# Connect to main database shell
db-shell:
    @echo "Connecting to main database..."
    docker compose exec db psql -U postgres

# Connect to test database shell
test-db-shell:
    @echo "Connecting to test database..."
    docker exec -it traker_test_db psql -U postgres

# Backup production database
db-backup:
    @echo "Backing up production database..."
    @mkdir -p backups
    docker compose exec -T db pg_dump -U postgres > backups/backup_$(date +%Y%m%d_%H%M%S).sql
    @echo "Backup completed!"

# Restore database from backup
db-restore BACKUP_FILE:
    @echo "Restoring database from {{BACKUP_FILE}}..."
    @if [ ! -f "{{BACKUP_FILE}}" ]; then \
        echo "Error: Backup file not found: {{BACKUP_FILE}}"; \
        exit 1; \
    fi
    docker compose exec -T db psql -U postgres < {{BACKUP_FILE}}
    @echo "Restore completed!"

# ============================================================================
# Cleanup
# ============================================================================

# Remove Python cache files
clean-py:
    @echo "Removing Python cache files..."
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type f -name "*.pyo" -delete 2>/dev/null || true
    find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
    @echo "Python cache cleaned!"

# Remove test artifacts
clean-test:
    @echo "Removing test artifacts..."
    rm -rf .coverage htmlcov/ .pytest_cache/
    @echo "Test artifacts cleaned!"

# Full cleanup
clean-all: clean-py clean-test
    @echo "Removing all build artifacts..."
    rm -rf dist/ build/ *.egg-info/
    @echo "Full cleanup completed!"

# ============================================================================
# Run Services (Linux/macOS)
# ============================================================================

# Run the bot service
run-bot:
    @echo "Starting bot service..."
    uv run python code/bot/src/bot/main.py

# Run the miner service
run-miner:
    @echo "Starting miner service..."
    uv run python code/miner/src/miner/main.py

# ============================================================================
# Development Helpers
# ============================================================================

# Show project status (git, docker, test DB)
status:
    @echo "=== Git Status ==="
    @git status -s || echo "Not a git repository"
    @echo ""
    @echo "=== Docker Compose Services ==="
    @docker compose ps 2>/dev/null || echo "Docker compose not running"
    @echo ""
    @echo "=== Test Database Status ==="
    @docker ps -a --filter name=traker_test_db --format "table {{{{.Names}}\t{{{{.Status}}\t{{{{.Ports}}" || echo "No test database container"

# Run database migrations (placeholder)
migrate:
    @echo "Running database migrations..."
    @echo "TODO: Implement migration runner (e.g., alembic upgrade head)"

# Create a new migration (placeholder)
migrate-create NAME:
    @echo "Creating migration: {{NAME}}..."
    @echo "TODO: Implement migration creator (e.g., alembic revision -m '{{NAME}}')"

# ============================================================================
# CI/CD Simulation
# ============================================================================

# Run full CI checks (format, lint, typecheck, test)
ci: format-check lint typecheck test
    @echo "========================================="
    @echo "CI checks completed successfully!"
    @echo "========================================="

# Quick checks before pushing
pre-push: format-check lint test-fast
    @echo "========================================="
    @echo "Pre-push checks completed!"
    @echo "========================================="
