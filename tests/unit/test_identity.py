"""Tests for services/identity_service.py — UAIT lifecycle."""

from datetime import datetime, timedelta, timezone


class TestCreateIdentity:
    def test_creates_with_required_fields(self, identity_service):
        result = identity_service.create_identity(
            display_name="TestBot",
            source_protocol="mcp",
        )
        assert result["agent_id"].startswith("attestix:")
        assert result["display_name"] == "TestBot"
        assert result["source_protocol"] == "mcp"
        assert result["signature"] is not None
        assert result["revoked"] is False

    def test_creates_with_all_fields(self, identity_service):
        result = identity_service.create_identity(
            display_name="FullBot",
            source_protocol="a2a",
            capabilities=["read", "write"],
            description="Full test agent",
            issuer_name="TestIssuer",
            expiry_days=30,
        )
        assert result["capabilities"] == ["read", "write"]
        assert result["description"] == "Full test agent"
        assert result["issuer"]["name"] == "TestIssuer"

    def test_masks_identity_token(self, identity_service):
        result = identity_service.create_identity(
            display_name="TokenBot",
            source_protocol="api_key",
            identity_token="sk-very-secret-api-key-1234567890",
        )
        token = result["identity_token"]
        assert "very-secret" not in token
        assert token.startswith("sk-v")
        assert token.endswith("7890")


class TestGetIdentity:
    def test_get_existing(self, identity_service):
        created = identity_service.create_identity("Bot", "mcp")
        found = identity_service.get_identity(created["agent_id"])
        assert found is not None
        assert found["agent_id"] == created["agent_id"]

    def test_get_nonexistent(self, identity_service):
        assert identity_service.get_identity("attestix:nonexistent") is None


class TestListIdentities:
    def test_list_all(self, identity_service):
        identity_service.create_identity("A", "mcp")
        identity_service.create_identity("B", "a2a")
        results = identity_service.list_identities()
        assert len(results) == 2

    def test_filter_by_protocol(self, identity_service):
        identity_service.create_identity("A", "mcp")
        identity_service.create_identity("B", "a2a")
        results = identity_service.list_identities(source_protocol="mcp")
        assert len(results) == 1
        assert results[0]["source_protocol"] == "mcp"

    def test_excludes_revoked_by_default(self, identity_service):
        created = identity_service.create_identity("A", "mcp")
        identity_service.revoke_identity(created["agent_id"], "test")
        results = identity_service.list_identities()
        assert len(results) == 0

    def test_includes_revoked_when_asked(self, identity_service):
        created = identity_service.create_identity("A", "mcp")
        identity_service.revoke_identity(created["agent_id"], "test")
        results = identity_service.list_identities(include_revoked=True)
        assert len(results) == 1


class TestVerifyIdentity:
    def test_valid_identity(self, identity_service):
        created = identity_service.create_identity("Bot", "mcp")
        result = identity_service.verify_identity(created["agent_id"])
        assert result["valid"] is True
        assert result["checks"]["exists"] is True
        assert result["checks"]["not_revoked"] is True
        assert result["checks"]["not_expired"] is True
        assert result["checks"]["signature_valid"] is True

    def test_revoked_identity_invalid(self, identity_service):
        created = identity_service.create_identity("Bot", "mcp")
        identity_service.revoke_identity(created["agent_id"], "compromised")
        result = identity_service.verify_identity(created["agent_id"])
        assert result["valid"] is False
        assert result["checks"]["not_revoked"] is False

    def test_nonexistent_identity(self, identity_service):
        result = identity_service.verify_identity("attestix:nope")
        assert result["valid"] is False
        assert result["checks"]["exists"] is False


class TestRevokeIdentity:
    def test_revoke_success(self, identity_service):
        created = identity_service.create_identity("Bot", "mcp")
        result = identity_service.revoke_identity(created["agent_id"], "test reason")
        assert result["revoked"] is True
        assert result["revocation_reason"] == "test reason"
        assert "revoked_at" in result

    def test_revoke_nonexistent(self, identity_service):
        result = identity_service.revoke_identity("attestix:nope")
        assert result is None
