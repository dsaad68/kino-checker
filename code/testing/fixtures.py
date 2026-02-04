"""Shared test fixtures using testcontainers for all services."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from testcontainers.postgres import PostgresContainer

# init-db is at code/init-db, fixtures.py is at code/testing/fixtures.py
_init_db_dir = Path(__file__).resolve().parent.parent / "init-db"


@pytest.fixture(scope="session")
def postgres_container() -> PostgresContainer:
    """Start a PostgreSQL container for the test session."""
    container = PostgresContainer("postgres:16-alpine")
    container.start()
    yield container
    container.stop()


@pytest.fixture(scope="session")
def db_engine(postgres_container: PostgresContainer) -> Engine:
    """Create a SQLAlchemy engine connected to the test database."""
    connection_url = postgres_container.get_connection_url()
    engine = create_engine(connection_url, pool_size=2, max_overflow=2)
    return engine


@pytest.fixture
def db_connection_uri(postgres_container: PostgresContainer, db_engine: Engine) -> str:
    """Provide a database connection URI with initialized schema and data."""
    connection_url = postgres_container.get_connection_url()
    init_db_path = _init_db_dir / "init-db.sql"

    with db_engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS tracker"))
        conn.commit()

        if init_db_path.exists():
            with open(init_db_path) as f:
                init_sql = f.read()
                conn.execute(text(init_sql))
                conn.commit()

    yield connection_url

    with db_engine.connect() as conn:
        conn.execute(text("DROP SCHEMA IF EXISTS tracker CASCADE"))
        conn.commit()


@pytest.fixture
def db_connection_uri_with_sample_data(postgres_container: PostgresContainer, db_engine: Engine, request) -> str:
    """Provide a database connection URI with sample data for integration tests."""
    connection_url = postgres_container.get_connection_url()

    test_module_name = request.node.parent.name if request.node.parent else ""
    sample_data_file = "sample-data-cleaner.sql" if "cleaner" in test_module_name else "sample-data.sql"

    init_db_path = _init_db_dir / "init-db.sql"
    sample_data_path = _init_db_dir / sample_data_file

    with db_engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS tracker"))
        conn.commit()

        if init_db_path.exists():
            with open(init_db_path) as f:
                init_sql = f.read()
                conn.execute(text(init_sql))
                conn.commit()

        if sample_data_path.exists():
            with open(sample_data_path) as f:
                sample_sql = f.read()
                conn.execute(text(sample_sql))
                conn.commit()

    yield connection_url

    with db_engine.connect() as conn:
        conn.execute(text("DROP SCHEMA IF EXISTS tracker CASCADE"))
        conn.commit()


@pytest.fixture
def schemas() -> list[str]:
    """Provide list of database schemas for tests."""
    return ["tracker"]


@pytest.fixture
def init_scripts() -> list[str]:
    """Provide list of init scripts for legacy tests."""
    return [
        str(_init_db_dir / "init-db.sql"),
        str(_init_db_dir / "sample-data.sql"),
    ]


@pytest.fixture
def date_ten_days_in_future_date() -> datetime:
    """Returns a date 10 days in the future."""
    return datetime.now().date() + timedelta(days=10)
