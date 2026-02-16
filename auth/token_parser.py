"""Token type detection and JWT parsing for AURA Protocol.

Identifies whether an input string is a JWT, DID, URL, API key, or unknown,
and extracts claims from JWTs without verification (for identity bridging).
"""

import re
from enum import Enum
from typing import Optional

import jwt

from errors import ErrorCategory, log_and_format_error


class TokenType(str, Enum):
    JWT = "jwt"
    DID = "did"
    URL = "url"
    API_KEY = "api_key"
    UNKNOWN = "unknown"


# Patterns for token type detection
DID_PATTERN = re.compile(r"^did:[a-z0-9]+:.+$", re.IGNORECASE)
URL_PATTERN = re.compile(r"^https?://.+$", re.IGNORECASE)
JWT_PATTERN = re.compile(r"^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$")
# API keys: hex strings >= 32 chars, or mixed-case alphanumeric with dashes/underscores >= 32 chars
API_KEY_PATTERN = re.compile(r"^[A-Fa-f0-9]{32,}$|^(?=.*[A-Z])(?=.*[a-z0-9])[A-Za-z0-9_-]{32,}$")


def detect_token_type(token: str) -> TokenType:
    """Detect the type of an identity token string."""
    token = token.strip()

    if DID_PATTERN.match(token):
        return TokenType.DID

    if JWT_PATTERN.match(token):
        # Verify it's actually parseable as JWT
        try:
            jwt.decode(token, options={"verify_signature": False})
            return TokenType.JWT
        except jwt.DecodeError:
            pass

    if URL_PATTERN.match(token):
        return TokenType.URL

    if API_KEY_PATTERN.match(token) and not DID_PATTERN.match(token):
        return TokenType.API_KEY

    return TokenType.UNKNOWN


def parse_jwt_claims(token: str) -> Optional[dict]:
    """Parse JWT without verification and extract claims.

    Returns None if the token is not a valid JWT.
    """
    try:
        claims = jwt.decode(
            token,
            options={
                "verify_signature": False,
                "verify_exp": False,
                "verify_aud": False,
            },
        )
        # Also decode header for algorithm info
        header = jwt.get_unverified_header(token)
        return {
            "header": header,
            "claims": claims,
            "subject": claims.get("sub"),
            "issuer": claims.get("iss"),
            "audience": claims.get("aud"),
            "expiry": claims.get("exp"),
            "issued_at": claims.get("iat"),
            "scopes": claims.get("scope", "").split() if claims.get("scope") else [],
        }
    except Exception as e:
        log_and_format_error(
            "parse_jwt_claims", e, ErrorCategory.IDENTITY,
            user_message="Failed to parse JWT token",
        )
        return None


def extract_identity_from_token(token: str) -> dict:
    """Extract identity information from any supported token type.

    Returns a dict with: token_type, original_token, and extracted fields.
    """
    token_type = detect_token_type(token)
    result = {
        "token_type": token_type.value,
        "original_token": token,
    }

    if token_type == TokenType.JWT:
        parsed = parse_jwt_claims(token)
        if parsed:
            result["subject"] = parsed["subject"]
            result["issuer"] = parsed["issuer"]
            result["scopes"] = parsed["scopes"]
            result["expiry"] = parsed["expiry"]
            result["jwt_header"] = parsed["header"]

    elif token_type == TokenType.DID:
        parts = token.split(":")
        result["did_method"] = parts[1] if len(parts) >= 3 else "unknown"
        result["did_specific_id"] = ":".join(parts[2:]) if len(parts) >= 3 else token

    elif token_type == TokenType.URL:
        result["url"] = token
        result["note"] = "URL-based identity (e.g., A2A Agent Card endpoint)"

    elif token_type == TokenType.API_KEY:
        # Mask the key for safety
        result["key_preview"] = token[:6] + "..." + token[-4:] if len(token) > 12 else "***"
        result["key_length"] = len(token)

    return result
