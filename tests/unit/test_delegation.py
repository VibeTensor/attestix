"""Tests for services/delegation_service.py — UCAN delegation tokens."""


class TestCreateDelegation:
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
