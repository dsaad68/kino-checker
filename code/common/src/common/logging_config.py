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
