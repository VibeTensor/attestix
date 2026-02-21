"""UCAN (User Controlled Authorization Networks) conformance tests.

Validates JWT header, payload fields, capability attenuation,
expiry enforcement, and revocation per the UCAN 0.9.0 specification.
"""

import base64
import json
import time

import jwt
import pytest

from auth.crypto import did_key_to_public_key


class TestUCANJWTHeader:
    """UCAN tokens must use EdDSA with JWT type and declare UCAN version."""

    def test_header_algorithm_is_eddsa(self, delegation_service):
        result = delegation_service.create_delegation(
            issuer_agent_id="agent-issuer",
            audience_agent_id="agent-audience",
            capabilities=["read"],
        )
        token = result["token"]
        header = jwt.get_unverified_header(token)
        assert header["alg"] == "EdDSA"

    def test_header_type_is_jwt(self, delegation_service):
        result = delegation_service.create_delegation(
            issuer_agent_id="agent-issuer",
            audience_agent_id="agent-audience",
            capabilities=["read"],
        )
        header = jwt.get_unverified_header(result["token"])
        assert header["typ"] == "JWT"

    def test_header_ucan_version(self, delegation_service):
        result = delegation_service.create_delegation(
            issuer_agent_id="agent-issuer",
            audience_agent_id="agent-audience",
            capabilities=["read"],
        )
        header = jwt.get_unverified_header(result["token"])
        assert header["ucv"] == "0.9.0"


class TestUCANPayloadFields:
    """UCAN payload must contain all required fields per spec."""

    @pytest.fixture()
    def ucan_claims(self, delegation_service):
        result = delegation_service.create_delegation(
            issuer_agent_id="agent-issuer",
            audience_agent_id="agent-audience",
            capabilities=["read", "write"],
            expiry_hours=1,
        )
        token = result["token"]
        public_key = did_key_to_public_key(delegation_service._server_did)
        return jwt.decode(token, public_key, algorithms=["EdDSA"], options={"verify_aud": False})

    def test_issuer_is_did(self, ucan_claims):
        assert ucan_claims["iss"].startswith("did:key:z")

    def test_audience_present(self, ucan_claims):
        assert ucan_claims["aud"] == "agent-audience"

    def test_capabilities_field(self, ucan_claims):
        assert ucan_claims["att"] == ["read", "write"]

    def test_proof_chain_field(self, ucan_claims):
        assert isinstance(ucan_claims["prf"], list)

    def test_expiry_field(self, ucan_claims):
        assert isinstance(ucan_claims["exp"], int)
        assert ucan_claims["exp"] > int(time.time())

    def test_not_before_field(self, ucan_claims):
        assert isinstance(ucan_claims["nbf"], int)
        assert ucan_claims["nbf"] <= int(time.time())

    def test_jti_field(self, ucan_claims):
        assert isinstance(ucan_claims["jti"], str)
        assert len(ucan_claims["jti"]) > 0

    def test_type_field(self, ucan_claims):
        assert ucan_claims["typ"] == "ucan/delegation"


class TestUCANCapabilityAttenuation:
    """A child delegation must not exceed parent capabilities."""

    def test_child_subset_of_parent(self, delegation_service):
        parent = delegation_service.create_delegation(
            issuer_agent_id="root-agent",
            audience_agent_id="mid-agent",
            capabilities=["read", "write", "admin"],
        )
        child = delegation_service.create_delegation(
            issuer_agent_id="mid-agent",
            audience_agent_id="leaf-agent",
            capabilities=["read"],
            parent_token=parent["token"],
        )
        child_verified = delegation_service.verify_delegation(child["token"])
        assert child_verified["valid"] is True
        assert child_verified["capabilities"] == ["read"]
        assert set(child_verified["capabilities"]).issubset({"read", "write", "admin"})

    def test_proof_chain_references_parent(self, delegation_service):
        parent = delegation_service.create_delegation(
            issuer_agent_id="root-agent",
            audience_agent_id="mid-agent",
            capabilities=["read", "write"],
        )
        child = delegation_service.create_delegation(
            issuer_agent_id="mid-agent",
            audience_agent_id="leaf-agent",
            capabilities=["read"],
            parent_token=parent["token"],
        )
        child_verified = delegation_service.verify_delegation(child["token"])
        assert parent["token"] in child_verified["proof_chain"]


class TestUCANExpiryEnforcement:
    """Expired tokens must be rejected."""

    def test_expired_token_is_invalid(self, delegation_service):
        result = delegation_service.create_delegation(
            issuer_agent_id="agent-a",
            audience_agent_id="agent-b",
            capabilities=["read"],
            expiry_hours=0,
        )
        # expiry_hours=0 means exp == iat, so token is expired immediately
        verified = delegation_service.verify_delegation(result["token"])
        assert verified["valid"] is False

    def test_valid_token_not_expired(self, delegation_service):
        result = delegation_service.create_delegation(
            issuer_agent_id="agent-a",
            audience_agent_id="agent-b",
            capabilities=["read"],
            expiry_hours=24,
        )
        verified = delegation_service.verify_delegation(result["token"])
        assert verified["valid"] is True
        assert verified["expired"] is False


class TestUCANRevocation:
    """Revoked tokens must fail verification."""

    def test_revoked_token_is_invalid(self, delegation_service):
        result = delegation_service.create_delegation(
            issuer_agent_id="agent-a",
            audience_agent_id="agent-b",
            capabilities=["read"],
        )
        jti = result["delegation"]["jti"]
        delegation_service.revoke_delegation(jti, reason="compromised")
        verified = delegation_service.verify_delegation(result["token"])
        assert verified["valid"] is False

    def test_revocation_records_reason(self, delegation_service):
        result = delegation_service.create_delegation(
            issuer_agent_id="agent-a",
            audience_agent_id="agent-b",
            capabilities=["read"],
        )
        jti = result["delegation"]["jti"]
        revoke_result = delegation_service.revoke_delegation(jti, reason="key rotation")
        assert revoke_result["revoked"] is True
        assert revoke_result["reason"] == "key rotation"

    def test_double_revocation_returns_error(self, delegation_service):
        result = delegation_service.create_delegation(
            issuer_agent_id="agent-a",
            audience_agent_id="agent-b",
            capabilities=["read"],
        )
        jti = result["delegation"]["jti"]
        delegation_service.revoke_delegation(jti)
        second = delegation_service.revoke_delegation(jti)
        assert "error" in second
