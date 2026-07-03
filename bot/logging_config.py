"""
bot/logging_config.py

Configures a rotating JSON-line logger for the trading bot.
Every log entry is a single JSON object written to logs/trading_bot.log.

Log events:
    request    → before every Binance API call
    response   → after every successful API call
    validation → when user input fails validation
    exception  → when any exception is caught
"""

import json
import logging
import os
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler


# ── Constants ────────────────────────────────────────────────────────────────

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
LOG_FILE = os.path.join(LOG_DIR, "trading_bot.log")
MAX_BYTES = 5 * 1024 * 1024   # 5 MB per file
BACKUP_COUNT = 3               # keep 3 rotated backups


# ── JSON formatter ────────────────────────────────────────────────────────────

class JSONLineFormatter(logging.Formatter):
    """
    Formats each log record as a single JSON object on one line.

    Schema:
        {
            "timestamp": "<ISO-8601 UTC>",
            "level":     "INFO | ERROR | WARNING",
            "event":     "request | response | validation | exception",
            "detail":    { ...event-specific fields... }
        }
    """

    def format(self, record: logging.LogRecord) -> str:
        """Serialize the log record to a JSON string."""
        entry = {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "level": record.levelname,
            "event": getattr(record, "event", "general"),
            "detail": getattr(record, "detail", {}),
        }
        return json.dumps(entry, ensure_ascii=False)


# ── Setup function ────────────────────────────────────────────────────────────

def setup_logger(name: str = "trading_bot") -> logging.Logger:
    """
    Create and return a configured logger.

    The logger writes JSON-line entries to:
        logs/trading_bot.log  (rotated at 5 MB, 3 backups kept)

    Args:
        name: Logger name (default: 'trading_bot').

    Returns:
        Configured logging.Logger instance.
    """
    # Create logs/ directory if it doesn't exist
    os.makedirs(LOG_DIR, exist_ok=True)

    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if called multiple times
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # Rotating file handler
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(JSONLineFormatter())

    logger.addHandler(file_handler)
    logger.propagate = False   # don't bubble up to root logger

    return logger


# ── Helper log functions ──────────────────────────────────────────────────────

def log_request(logger: logging.Logger, endpoint: str, payload: dict) -> None:
    """
    Log an outgoing API request before it is sent.

    Args:
        logger:   The logger instance.
        endpoint: The Binance API endpoint being called (e.g. '/fapi/v1/order').
        payload:  The request parameters (must NOT contain API keys).
    """
    logger.info(
        "API request",
        extra={
            "event": "request",
            "detail": {
                "method": "POST",
                "endpoint": endpoint,
                "payload": payload,
            },
        },
    )


def log_response(logger: logging.Logger, response: dict) -> None:
    """
    Log the API response received from Binance.

    Args:
        logger:   The logger instance.
        response: The parsed JSON response from the Binance API.
    """
    logger.info(
        "API response",
        extra={
            "event": "response",
            "detail": {
                "orderId": response.get("orderId") or response.get("algoId"),
                "status": response.get("status") or response.get("algoStatus"),
                "executedQty": response.get("executedQty") or response.get("quantity"),
                "avgPrice": response.get("avgPrice") or response.get("price"),
                "symbol": response.get("symbol"),
                "side": response.get("side"),
                "type": response.get("type") or response.get("orderType"),
            },
        },
    )


def log_validation_error(logger: logging.Logger, field: str, value: object, reason: str) -> None:
    """
    Log a validation failure before any API call is made.

    Args:
        logger: The logger instance.
        field:  The CLI argument that failed (e.g. '--price').
        value:  The value that was provided (or None).
        reason: Human-readable explanation of why it failed.
    """
    logger.warning(
        "Validation error",
        extra={
            "event": "validation",
            "detail": {
                "field": field,
                "value": value,
                "reason": reason,
            },
        },
    )


def log_exception(logger: logging.Logger, exc: Exception, context: str = "") -> None:
    """
    Log a caught exception with its type and message.

    Args:
        logger:  The logger instance.
        exc:     The exception that was caught.
        context: Optional description of what was happening when the error occurred.
    """
    logger.error(
        "Exception occurred",
        extra={
            "event": "exception",
            "detail": {
                "type": type(exc).__name__,
                "message": str(exc),
                "context": context,
            },
        },
    )
