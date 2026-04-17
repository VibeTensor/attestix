"""Re-export from flat module for namespace compatibility."""
from auth.ssrf import (
    MAX_REDIRECTS,
    ResponseTooLargeError,
    fetch_json_pinned,
    validate_and_pin_url,
    validate_redirect_target,
    validate_url_host,
)

__all__ = [
    "MAX_REDIRECTS",
    "ResponseTooLargeError",
    "fetch_json_pinned",
    "validate_and_pin_url",
    "validate_redirect_target",
    "validate_url_host",
]
