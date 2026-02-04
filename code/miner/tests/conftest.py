"""Miner-specific test fixtures.

Shared fixtures are automatically imported from parent conftest.py:
- postgres_container: PostgreSQL test container
- db_engine: SQLAlchemy engine
- db_connection_uri: Connection URI with schema
- db_connection_uri_with_sample_data: Connection URI with sample data
- schemas: List of database schemas
- init_scripts: List of init scripts
"""

from __future__ import annotations

# All shared fixtures are automatically available from parent conftest.py
