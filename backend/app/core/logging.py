"""Logging configuration for Commerce Insights."""

import logging
import sys


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Configures application-wide structured stdout logging.

    Args:
        log_level: Desired log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL).

    Returns:
        The configured root logger for the application.
    """
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    log_format = "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
    date_format = "%Y-%m-%dT%H:%M:%S"

    formatter = logging.Formatter(fmt=log_format, datefmt=date_format)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    logger = logging.getLogger("commerce_insights")
    logger.setLevel(numeric_level)
    
    # Avoid duplicate handlers if re-initialized
    if not logger.handlers:
        logger.addHandler(handler)
    logger.propagate = False

    return logger
