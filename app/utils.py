"""Utility module for AvocaScan AI Service.

Consolidates logger setup and any other simple helper functions.
"""
import logging
import sys
from app.config import get_settings


def setup_logger(name: str = "avocascan_ai") -> logging.Logger:
    """Configure and return standard logger instance.

    Args:
        name (str): Name of the logger. Defaults to 'avocascan_ai'.

    Returns:
        logging.Logger: Configured logger instance.
    """
    settings = get_settings()
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(settings.log_level.upper())
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False

    return logger
