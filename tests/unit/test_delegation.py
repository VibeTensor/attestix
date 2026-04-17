"""Tests for UCAN delegation token operations in services/delegation_service.py."""


class TestCreateDelegation:
    """Tests for creating UCAN delegation tokens as signed JWTs."""

    def test_creates_jwt_token(self, delegation_service):
        result = delegation_service.create_delegation(
            issuer_agent_id="attestix:issuer",
            audience_agent_id="attestix:audience",
            capabilities=["read", "write"],
            expiry_hours=24,
        )
        assert "token" in result
        assert "delegation" in result
        token = result["token"]
        # JWT has 3 parts separated by dots
        assert len(token.split(".")) == 3

    def test_token_not_in_stored_record(self, delegation_service):
        result = delegation_service.create_delegation(
            issuer_agent_id="attestix:issuer",
            audience_agent_id="attestix:audience",
            capabilities=["read"],
        )
        record = result["delegation"]
        assert "token" not in record
        assert record["issuer"] == "attestix:issuer"
        assert record["audience"] == "attestix:audience"
        assert record["capabilities"] == ["read"]


class TestVerifyDelegation:
    """Tests for verifying delegation tokens including tamper detection."""

    def test_verify_valid_token(self, delegation_service):
        created = delegation_service.create_delegation(
            issuer_agent_id="attestix:issuer",
            audience_agent_id="attestix:audience",
            capabilities=["read"],
        )
        result = delegation_service.verify_delegation(created["token"])
        assert result["valid"] is True
        assert result["delegator"] == "attestix:issuer"
        assert result["audience"] == "attestix:audience"
        assert result["capabilities"] == ["read"]

    def test_verify_invalid_token(self, delegation_service):
        result = delegation_service.verify_delegation("not.a.valid.jwt")
        assert result["valid"] is False

    def test_verify_tampered_token(self, delegation_service):
        created = delegation_service.create_delegation(
            issuer_agent_id="attestix:issuer",
            audience_agent_id="attestix:audience",
            capabilities=["read"],
        )
        # Tamper with the token
        token = created["token"]
        parts = token.split(".")
        parts[1] = parts[1] + "tampered"
        tampered = ".".join(parts)
        result = delegation_service.verify_delegation(tampered)
        assert result["valid"] is False


class TestListDelegations:
    """Tests for listing and filtering delegations by issuer or audience."""

    def test_list_all(self, delegation_service):
        delegation_service.create_delegation("a:1", "a:2", ["read"])
        delegation_service.create_delegation("a:2", "a:3", ["write"])
        results = delegation_service.list_delegations()
        assert len(results) == 2

    def test_filter_by_issuer(self, delegation_service):
        delegation_service.create_delegation("a:1", "a:2", ["read"])
        delegation_service.create_delegation("a:2", "a:3", ["write"])
        results = delegation_service.list_delegations(agent_id="a:1", role="issuer")
        assert len(results) == 1
        assert results[0]["issuer"] == "a:1"

    def test_filter_by_audience(self, delegation_service):
        delegation_service.create_delegation("a:1", "a:2", ["read"])
        delegation_service.create_delegation("a:2", "a:3", ["write"])
        results = delegation_service.list_delegations(agent_id="a:2", role="audience")
        assert len(results) == 1
        assert results[0]["audience"] == "a:2"

    def test_stored_records_have_no_token(self, delegation_service):
        delegation_service.create_delegation("a:1", "a:2", ["read"])
        results = delegation_service.list_delegations()
        for record in results:
            assert "token" not in record


class TestDelegationChainSecurity:
    """Security tests for UCAN delegation chain verification.

    These tests cover the fix for the delegation chain auth bypass,
    where create_delegation previously embedded an unverified
    parent_token into the new JWT and verify_delegation never walked
    the prf chain. The attacker could forge UCAN chains claiming
    authority from any agent.
    """

    def test_forged_parent_token_is_rejected(self, delegation_service):
        """A bogus string passed as parent_token must not produce a new delegation."""
        result = delegation_service.create_delegation(
            issuer_agent_id="attestix:issuer",
            audience_agent_id="attestix:audience",
            capabilities=["read"],
            parent_token="this.is.not.a.real.jwt",
        )
        assert "error" in result
        assert "token" not in result
        assert "parent" in result["error"].lower()

    def test_forged_parent_with_valid_structure_but_bad_signature_is_rejected(
        self, delegation_service
    ):
        """A syntactically valid JWT signed by some other key must be rejected."""
        import jwt as pyjwt
        from cryptography.hazmat.primitives.asymmetric.ed25519 import (
            Ed25519PrivateKey,
        )

        attacker_key = Ed25519PrivateKey.generate()
        forged = pyjwt.encode(
            {
                "iss": "did:key:attacker",
                "aud": "attestix:victim",
                "sub": "attestix:victim",
                "iat": 1_000_000_000,
                "exp": 9_999_999_999,
                "nbf": 1_000_000_000,
                "jti": "forged-jti",
                "att": ["admin", "read", "write"],
                "delegator": "attestix:victim-delegator",
                "prf": [],
                "typ": "ucan/delegation",
            },
            attacker_key,
            algorithm="EdDSA",
        )

        # Attacker tries to create a downstream delegation using the forged parent.
        result = delegation_service.create_delegation(
            issuer_agent_id="attestix:attacker",
            audience_agent_id="attestix:target",
            capabilities=["admin"],
            parent_token=forged,
        )
        assert "error" in result
        assert "token" not in result

    def test_capability_escalation_is_blocked(self, delegation_service):
        """Child capabilities must be a subset of parent capabilities."""
        parent = delegation_service.create_delegation(
            issuer_agent_id="attestix:root",
            audience_agent_id="attestix:middle",
            capabilities=["read"],
        )
        assert "token" in parent

        # Middle tries to escalate to 'write' which the parent never granted.
        child = delegation_service.create_delegation(
            issuer_agent_id="attestix:middle",
            audience_agent_id="attestix:leaf",
            capabilities=["read", "write"],
            parent_token=parent["token"],
        )
        assert "error" in child
        assert "token" not in child
        assert "escal" in child["error"].lower() or "subset" in child["error"].lower() or "not held" in child["error"].lower()

    def test_capability_attenuation_allows_subset(self, delegation_service):
        """A child may legitimately narrow capabilities vs its parent."""
        parent = delegation_service.create_delegation(
            issuer_agent_id="attestix:root",
            audience_agent_id="attestix:middle",
            capabilities=["read", "write", "admin"],
        )
        child = delegation_service.create_delegation(
            issuer_agent_id="attestix:middle",
            audience_agent_id="attestix:leaf",
            capabilities=["read"],
            parent_token=parent["token"],
        )
        assert "token" in child
        assert "error" not in child

    def test_expired_parent_is_rejected(self, delegation_service):
        """A parent whose exp is in the past must not be usable to mint children."""
        # Create a parent that is already expired by patching time.time
        # at creation so exp <= now when verify runs later.
        import time as time_mod
        from unittest.mock import patch

        # Issue a parent in the far past so it expires immediately.
        # expiry_hours must be positive, so we shift now backwards.
        past = int(time_mod.time()) - (48 * 3600)
        with patch("services.delegation_service.time.time", return_value=past):
            parent = delegation_service.create_delegation(
                issuer_agent_id="attestix:root",
                audience_agent_id="attestix:middle",
                capabilities=["read"],
                expiry_hours=1,  # exp = past + 1h, long gone by real now
            )
        assert "token" in parent

        # Now, at real current time, the parent's exp is in the past.
        child = delegation_service.create_delegation(
            issuer_agent_id="attestix:middle",
            audience_agent_id="attestix:leaf",
            capabilities=["read"],
            parent_token=parent["token"],
        )
        assert "error" in child
        assert "token" not in child

    def test_revoked_parent_is_rejected(self, delegation_service):
        """A revoked parent must not be usable to mint children."""
        parent = delegation_service.create_delegation(
            issuer_agent_id="attestix:root",
            audience_agent_id="attestix:middle",
            capabilities=["read", "write"],
        )
        assert "token" in parent
        parent_jti = parent["delegation"]["jti"]

        revoke_result = delegation_service.revoke_delegation(
            parent_jti, reason="security incident"
        )
        assert revoke_result.get("revoked") is True

        child = delegation_service.create_delegation(
            issuer_agent_id="attestix:middle",
            audience_agent_id="attestix:leaf",
            capabilities=["read"],
            parent_token=parent["token"],
        )
        assert "error" in child
        assert "token" not in child
        assert "revoke" in child["error"].lower() or "parent" in child["error"].lower()

    def test_valid_chain_passes(self, delegation_service):
        """A well-formed grandparent -> parent -> child chain verifies end-to-end."""
        grandparent = delegation_service.create_delegation(
            issuer_agent_id="attestix:root",
            audience_agent_id="attestix:middle",
            capabilities=["read", "write", "admin"],
        )
        assert "token" in grandparent

        parent = delegation_service.create_delegation(
            issuer_agent_id="attestix:middle",
            audience_agent_id="attestix:sub",
            capabilities=["read", "write"],
            parent_token=grandparent["token"],
        )
        assert "token" in parent

        child = delegation_service.create_delegation(
            issuer_agent_id="attestix:sub",
            audience_agent_id="attestix:leaf",
            capabilities=["read"],
            parent_token=parent["token"],
        )
        assert "token" in child
        assert "error" not in child

        # verify_delegation must walk the prf chain successfully.
        verified = delegation_service.verify_delegation(child["token"])
        assert verified["valid"] is True
        assert verified["capabilities"] == ["read"]
        assert verified["proof_chain"] == [parent["token"]]

    def test_verify_walks_chain_and_rejects_when_ancestor_revoked(
        self, delegation_service
    ):
        """verify_delegation must fail if any ancestor in prf is revoked,
        even if the leaf token itself is otherwise valid."""
        grandparent = delegation_service.create_delegation(
            issuer_agent_id="attestix:root",
            audience_agent_id="attestix:middle",
            capabilities=["read", "write"],
        )
        parent = delegation_service.create_delegation(
            issuer_agent_id="attestix:middle",
            audience_agent_id="attestix:sub",
            capabilities=["read"],
            parent_token=grandparent["token"],
        )
        # Grandparent revoked AFTER the chain was built.
        delegation_service.revoke_delegation(
            grandparent["delegation"]["jti"], reason="key compromised"
        )

        result = delegation_service.verify_delegation(parent["token"])
        assert result["valid"] is False
        assert "parent" in result["reason"].lower() or "revoke" in result["reason"].lower()
