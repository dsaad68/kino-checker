# Kino-Checker Quick Start Guide

## Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose
- Git

## Installation

### 1. Install UV Package Manager

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Or on macOS with Homebrew:
```bash
brew install uv
```

### 2. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd kino-checker

# Install dependencies
uv sync --all-packages
```

### 3. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

Required environment variables:
- `POSTGRES_USER` - Database username
- `POSTGRES_PASSWORD` - Database password
- `POSTGRES_DB` - Database name
- `TELEGRAM_BOT_TOKEN` - Your Telegram bot token
- `OPENAI_API_KEY` - OpenAI API key
- `ELEVEN_API_KEY` - ElevenLabs API key

## Running the Application

### Using Docker Compose (Recommended)

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down
```

### Local Development

```bash
# Ensure PostgreSQL is running
docker compose up -d db

# Run individual services
python -m bot.main      # Telegram bot
python -m miner.main    # Film scraper
python -m cleaner.main  # Database cleaner
```

## Development Commands

### Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov --cov-report=html

# Run specific test file
uv run pytest code/bot/tests/bot/db_info_finder_test.py

# Run tests with markers
uv run pytest -m unit
uv run pytest -m integration
```

### Code Quality

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Fix linting issues automatically
uv run ruff check . --fix

# Type check
uv run mypy code/
```

### Pre-commit Hooks

```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files

# Update hooks
pre-commit autoupdate
```

## Project Structure

```
kino-checker/
├── code/
│   ├── bot/          # Telegram bot service
│   ├── miner/        # Web scraper service
│   ├── cleaner/      # Database cleanup service
│   ├── common/       # Shared code and utilities
│   ├── my_logger/    # Custom logging module
│   └── init-db/      # Database initialization scripts
├── pyproject.toml    # Workspace configuration
├── uv.lock          # Locked dependencies
└── docker-compose.yml
```

## Troubleshooting

### UV Sync Fails

```bash
# Clear cache
rm -rf .venv
uv sync --all-packages
```

### Docker Build Issues

```bash
# Rebuild without cache
docker compose build --no-cache

# Check logs
docker compose logs <service-name>
```

### Database Connection Issues

```bash
# Check database is running
docker compose ps db

# Restart database
docker compose restart db

# View database logs
docker compose logs db
```

### Import Errors

```bash
# Ensure you're in the project root
cd /path/to/kino-checker

# Reinstall dependencies
uv sync --all-packages

# Verify virtual environment
which python  # Should point to .venv/bin/python
```

## Common Tasks

### Add New Dependencies

```bash
# Add to appropriate pyproject.toml
cd code/<service>
nano pyproject.toml  # Add dependency

# Update lock file
cd ../..
uv sync --all-packages
```

### Update Dependencies

```bash
# Update all dependencies
uv sync --upgrade

# Update specific package
uv sync --upgrade-package <package-name>
```

### Database Operations

```bash
# Access database shell
docker compose exec db psql -U postgres -d kino_tracker

# Run SQL script
docker compose exec db psql -U postgres -d kino_tracker -f /path/to/script.sql

# Backup database
docker compose exec db pg_dump -U postgres kino_tracker > backup.sql

# Restore database
docker compose exec -T db psql -U postgres -d kino_tracker < backup.sql
```

## Getting Help

- Check the [MODERNIZATION_CHANGES.md](MODERNIZATION_CHANGES.md) for recent changes
- Review the main [README.md](README.md) for project overview
- File issues on GitHub

## Next Steps

1. Read the full README for project details
2. Review the architecture diagram (diagram.jpg)
3. Check the modernization changes document
4. Set up your development environment
5. Run the tests to ensure everything works
6. Start contributing!
