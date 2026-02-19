"""Centralized error handling and logging for Attestix."""

import sys
import logging
from enum import Enum
from typing import Optional, Union
from pythonjsonlogger import json as jsonlogger

logger = logging.getLogger("attestix")


class ErrorCategory(str, Enum):
    IDENTITY = "IDENTITY"
    DID = "DID"
    AGENT_CARD = "AGENT_CARD"
    DELEGATION = "DELEGATION"
    REPUTATION = "REPUTATION"
    CRYPTO = "CRYPTO"
    CONFIG = "CONFIG"
    STORAGE = "STORAGE"
    NETWORK = "NETWORK"
    COMPLIANCE = "COMPLIANCE"
    CREDENTIAL = "CREDENTIAL"
    PROVENANCE = "PROVENANCE"


def setup_logging(log_file: str = "attestix_errors.log"):
    """Configure dual logging: stderr (human-readable) + file (JSON structured)."""
    logger.setLevel(logging.DEBUG)

    # Console handler (stderr)
    console = logging.StreamHandler(sys.stderr)
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(console)

    # File handler (JSON)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.WARNING)
    json_formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    file_handler.setFormatter(json_formatter)
    logger.addHandler(file_handler)

    # Suppress noisy third-party loggers
    for name in ("httpx", "urllib3", "httpcore"):
        logging.getLogger(name).setLevel(logging.WARNING)


def log_and_format_error(
    function_name: str,
    error: Exception,
    category: Optional[Union[ErrorCategory, str]] = None,
    user_message: Optional[str] = None,
    **context,
) -> str:
    """Log error with context and return user-friendly message."""
    cat = category.value if isinstance(category, ErrorCategory) else (category or "UNKNOWN")
    ctx_str = ", ".join(f"{k}={v}" for k, v in context.items()) if context else ""

    logger.error(
        f"[{cat}] {function_name}: {error}" + (f" | {ctx_str}" if ctx_str else ""),
        exc_info=True,
        extra={"category": cat, "function": function_name, **context},
    )

    if user_message:
        return f"Error [{cat}]: {user_message}"
    return f"Error [{cat}] in {function_name}: {str(error)}"
