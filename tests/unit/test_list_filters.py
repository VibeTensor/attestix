"""Tests for IdentityService.list_identities filters (issue #37, part 1).

Covers each new filter (risk_category, name_contains, status) in isolation
and in composition, plus confirmation that existing params/behaviour are
preserved.
"""

import pytest


@pytest.fixture
def populated(identity_service, compliance_service):
    """Create a small, deterministic population of agents.

    Returns a dict of label -> agent_id.
    """
    fraud = identity_service.create_identity(
        display_name="Fraud Detector", source_protocol="mcp",
    )["agent_id"]
    chat = identity_service.create_identity(
        display_name="Chatbot Assistant", source_protocol="a2a",
    )["agent_id"]
    recsys = identity_service.create_identity(
        display_name="Recommendation Engine", source_protocol="mcp",
    )["agent_id"]

    # Compliance profiles for the risk_category join.
    compliance_service.create_compliance_profile(
        agent_id=fraud, risk_category="high", provider_name="VibeTensor",
    )
    compliance_service.create_compliance_profile(
        agent_id=chat, risk_category="limited", provider_name="VibeTensor",
    )
    # recsys intentionally has NO compliance profile.

    return {"fraud": fraud, "chat": chat, "recsys": recsys}


class TestRiskCategoryFilter:
    def test_high_only(self, identity_service, populated):
        results = identity_service.list_identities(risk_category="high")
        ids = {a["agent_id"] for a in results}
        assert ids == {populated["fraud"]}

    def test_limited_only(self, identity_service, populated):
        results = identity_service.list_identities(risk_category="limited")
        ids = {a["agent_id"] for a in results}
        assert ids == {populated["chat"]}

    def test_excludes_agents_without_profile(self, identity_service, populated):
        results = identity_service.list_identities(risk_category="high")
        ids = {a["agent_id"] for a in results}
        assert populated["recsys"] not in ids

    def test_case_insensitive(self, identity_service, populated):
        results = identity_service.list_identities(risk_category="HIGH")
        assert len(results) == 1


class TestNameContainsFilter:
    def test_substring(self, identity_service, populated):
        results = identity_service.list_identities(name_contains="Fraud")
        ids = {a["agent_id"] for a in results}
        assert ids == {populated["fraud"]}

    def test_case_insensitive(self, identity_service, populated):
        results = identity_service.list_identities(name_contains="chatbot")
        ids = {a["agent_id"] for a in results}
        assert ids == {populated["chat"]}

    def test_no_match(self, identity_service, populated):
        results = identity_service.list_identities(name_contains="nonexistent")
        assert results == []


class TestStatusFilter:
    def test_active(self, identity_service, populated):
        results = identity_service.list_identities(status="active")
        assert len(results) == 3

    def test_revoked(self, identity_service, populated):
        identity_service.revoke_identity(populated["chat"], reason="test")
        results = identity_service.list_identities(status="revoked")
        ids = {a["agent_id"] for a in results}
        assert ids == {populated["chat"]}

    def test_active_excludes_revoked(self, identity_service, populated):
        identity_service.revoke_identity(populated["chat"], reason="test")
        results = identity_service.list_identities(status="active")
        ids = {a["agent_id"] for a in results}
        assert populated["chat"] not in ids
        assert len(results) == 2

    def test_expired(self, identity_service):
        # Create an already-expired identity (expiry 0 days -> expires "now").
        agent = identity_service.create_identity(
            display_name="Expired Agent", source_protocol="mcp", expiry_days=0,
        )
        results = identity_service.list_identities(status="expired")
        ids = {a["agent_id"] for a in results}
        assert agent["agent_id"] in ids


class TestFilterComposition:
    def test_risk_and_name(self, identity_service, populated):
        # high-risk AND name contains "Fraud" -> the fraud agent.
        results = identity_service.list_identities(
            risk_category="high", name_contains="Fraud",
        )
        assert len(results) == 1
        assert results[0]["agent_id"] == populated["fraud"]

    def test_risk_and_name_no_overlap(self, identity_service, populated):
        # high-risk AND name contains "Chatbot" -> nothing (chat is limited).
        results = identity_service.list_identities(
            risk_category="high", name_contains="Chatbot",
        )
        assert results == []

    def test_protocol_and_status(self, identity_service, populated):
        results = identity_service.list_identities(
            source_protocol="mcp", status="active",
        )
        ids = {a["agent_id"] for a in results}
        assert ids == {populated["fraud"], populated["recsys"]}


class TestBackwardCompatibility:
    def test_default_call_unchanged(self, identity_service, populated):
        # No new filters -> same as before: all non-revoked agents.
        results = identity_service.list_identities()
        assert len(results) == 3

    def test_protocol_filter_unchanged(self, identity_service, populated):
        results = identity_service.list_identities(source_protocol="mcp")
        assert len(results) == 2

    def test_limit_unchanged(self, identity_service, populated):
        results = identity_service.list_identities(limit=1)
        assert len(results) == 1

    def test_include_revoked_unchanged(self, identity_service, populated):
        identity_service.revoke_identity(populated["chat"], reason="test")
        assert len(identity_service.list_identities()) == 2
        assert len(identity_service.list_identities(include_revoked=True)) == 3
