"""Structured Application Logging Module

Provides consistent, formatted logging across all application components.
"""

import logging
import sys
from backend.app.core.config import settings


def setup_logging() -> logging.Logger:
    """Configure root and application loggers."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    log_format = (
        "[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] - %(message)s"
    )

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

    logger = logging.getLogger("buy_together")
    logger.setLevel(log_level)
    return logger


logger = setup_logging()
