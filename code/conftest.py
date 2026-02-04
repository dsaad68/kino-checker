"""Shared test fixtures using testcontainers for all services."""

from __future__ import annotations

from datetime import datetime, timedelta
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


@pytest.fixture(scope="session")
def db_engine(postgres_container: PostgresContainer) -> Engine:
    """Create a SQLAlchemy engine connected to the test database."""
    connection_url = postgres_container.get_connection_url()
    engine = create_engine(connection_url, pool_size=2, max_overflow=2)
    return engine


@pytest.fixture
def db_connection_uri(postgres_container: PostgresContainer, db_engine: Engine) -> str:
    """Provide a database connection URI with initialized schema and data."""
    # Get the connection URL
    connection_url = postgres_container.get_connection_url()

    # Initialize the database schema
    init_db_path = Path(__file__).parent / "init-db" / "init-db.sql"

    with db_engine.connect() as conn:
        # Create schema
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS tracker"))
        conn.commit()

        # Execute init script
        if init_db_path.exists():
            with open(init_db_path) as f:
                init_sql = f.read()
                conn.execute(text(init_sql))
                conn.commit()

    yield connection_url

    # Cleanup after test
    with db_engine.connect() as conn:
        conn.execute(text("DROP SCHEMA IF EXISTS tracker CASCADE"))
        conn.commit()


@pytest.fixture
def db_connection_uri_with_sample_data(postgres_container: PostgresContainer, db_engine: Engine, request) -> str:
    """Provide a database connection URI with sample data for integration tests."""
    connection_url = postgres_container.get_connection_url()

    # Determine which sample data to use based on the test module
    test_module_name = request.node.parent.name if request.node.parent else ""

    if "cleaner" in test_module_name:
        sample_data_file = "sample-data-cleaner.sql"
    else:
        sample_data_file = "sample-data.sql"

    init_db_path = Path(__file__).parent / "init-db" / "init-db.sql"
    sample_data_path = Path(__file__).parent / "init-db" / sample_data_file

    with db_engine.connect() as conn:
        # Create schema
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS tracker"))
        conn.commit()

        # Execute init script
        if init_db_path.exists():
            with open(init_db_path) as f:
                init_sql = f.read()
                conn.execute(text(init_sql))
                conn.commit()

        # Execute sample data script
        if sample_data_path.exists():
            with open(sample_data_path) as f:
                sample_sql = f.read()
                conn.execute(text(sample_sql))
                conn.commit()

    yield connection_url

    # Cleanup after test
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
    base_path = Path(__file__).parent / "init-db"
    return [
        str(base_path / "init-db.sql"),
        str(base_path / "sample-data.sql"),
    ]


@pytest.fixture
def date_ten_days_in_future_date() -> datetime:
    """Returns a date 10 days in the future."""
    return datetime.now().date() + timedelta(days=10)
