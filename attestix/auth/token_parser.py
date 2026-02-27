"""Re-export from flat module for namespace compatibility."""
from auth.token_parser import (
    API_KEY_PATTERN,
    DID_PATTERN,
    JWT_PATTERN,
    TokenType,
    URL_PATTERN,
    detect_token_type,
    extract_identity_from_token,
    parse_jwt_claims,
)

__all__ = [
    "API_KEY_PATTERN",
    "DID_PATTERN",
    "JWT_PATTERN",
    "TokenType",
    "URL_PATTERN",
    "detect_token_type",
    "extract_identity_from_token",
    "parse_jwt_claims",
]
