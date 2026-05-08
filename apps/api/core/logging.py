"""Logging configuration for GABOPAY"""

import logging
import sys
from typing import Any

from apps.api.core.config import get_settings


class CustomFormatter(logging.Formatter):
    """Custom formatter with colors for development"""

    grey = "\x1b[38;21m"
    blue = "\x1b[38;5;39m"
    yellow = "\x1b[38;5;226m"
    red = "\x1b[38;5;196m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    FORMATS = {
        logging.DEBUG: grey + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
        logging.INFO: blue + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
        logging.WARNING: yellow + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
        logging.ERROR: red + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
        logging.CRITICAL: bold_red + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
    }

    def format(self, record: logging.LogRecord) -> str:
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


def setup_logging(name: str = "gabopay") -> logging.Logger:
    """Setup application logging"""
    settings = get_settings()

    logger = logging.getLogger(name)
    logger.setLevel(
        logging.DEBUG if settings.APP_ENV == "development" else logging.INFO
    )

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(CustomFormatter())
        logger.addHandler(handler)

    return logger


def log_api_request(
    method: str,
    path: str,
    merchant_id: str | None = None,
    status_code: int | None = None,
    duration_ms: float | None = None,
) -> None:
    """Log API request with structured data"""
    logger = logging.getLogger("gabopay.api")
    logger.info(
        f"{method} {path} | merchant: {merchant_id or 'none'} | status: {status_code or 'pending'} | duration: {duration_ms or 0}ms"
    )


def log_transaction_event(
    event: str,
    transaction_id: str,
    merchant_id: str,
    amount: int,
    status: str,
) -> None:
    """Log transaction event"""
    logger = logging.getLogger("gabopay.transactions")
    logger.info(
        f"transaction.{event} | tx_id: {transaction_id} | merchant: {merchant_id} | amount: {amount} | status: {status}"
    )


def log_security_event(event: str, details: dict[str, Any]) -> None:
    """Log security-related events"""
    logger = logging.getLogger("gabopay.security")
    logger.warning(f"security.{event} | {details}")


def log_provider_event(provider: str, event: str, details: dict[str, Any]) -> None:
    """Log provider API events"""
    logger = logging.getLogger("gabopay.providers")
    logger.info(f"provider.{provider}.{event} | {details}")


# Logger instances
api_logger = setup_logging("gabopay.api")
transaction_logger = setup_logging("gabopay.transactions")
security_logger = setup_logging("gabopay.security")
provider_logger = setup_logging("gabopay.providers")