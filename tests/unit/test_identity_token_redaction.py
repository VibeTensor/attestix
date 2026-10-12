"""Credentials and arbitrary token metadata never survive identity bridging."""

import json

import jwt
import pytest

from attestix.auth.token_parser import extract_identity_from_token


@pytest.mark.parametrize("kind", ["jwt", "api_key", "short", "url", "did"])
def test_identity_creation_does_not_return_or_persist_credentials(
    kind, identity_service, tmp_attestix,
):
    secret = "SyntheticSensitiveValue12345678901234567890"
    if kind == "jwt":
        token = jwt.encode(
            {"sub": secret, "iss": secret, "scope": secret, "private_secret": secret},
            "synthetic-signing-secret-with-at-least-32-bytes",
            algorithm="HS256",
            headers={"kid": secret, "private_header": secret},
        )
    elif kind == "url":
        token = f"https://example.invalid/?api_key={secret}"
    elif kind == "did":
        token = f"did:example:{secret}"
    elif kind == "short":
        secret = "shortkey"
        token = secret
    else:
        token = secret

    identity = identity_service.create_identity("Test agent", "test", token)

    assert identity["identity_token"] == "***"
    assert "original_token" not in identity["token_info"]
    assert token not in json.dumps(identity)
    assert secret not in json.dumps(identity)
    assert identity_service.get_identity(identity["agent_id"]) == identity
    for path in tmp_attestix.rglob("*.json"):
        stored = path.read_text(encoding="utf-8")
        assert token not in stored
        assert secret not in stored
    assert identity_service.verify_identity(identity["agent_id"])["valid"] is True


def test_jwt_extraction_retains_only_allowlisted_display_metadata():
    token = jwt.encode(
        {"sub": {"nested": "synthetic-secret"}},
        "synthetic-signing-secret-with-at-least-32-bytes",
        algorithm="HS256",
        headers={"kid": "synthetic-secret", "jwk": {"secret": "synthetic-secret"}},
    )

    assert extract_identity_from_token(token) == {
        "token_type": "jwt",
        "token_length": len(token),
        "claims_verified": False,
        "jwt_algorithm": "HS256",
    }
