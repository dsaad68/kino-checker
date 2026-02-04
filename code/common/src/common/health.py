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
