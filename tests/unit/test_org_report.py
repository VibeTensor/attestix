"""Tests for ReportService.generate_org_report (issue #37, part 2).

Covers the all-agents path (agent_ids=None) and the explicit-subset path,
plus aggregation of the single-agent compliance status into an org summary.
"""

import pytest


@pytest.fixture
def org(identity_service, compliance_service):
    """Three agents: one high-risk with a profile, one limited with a
    profile, one with no compliance profile at all."""
    a = identity_service.create_identity(
        display_name="Fraud Detector", source_protocol="mcp",
    )["agent_id"]
    b = identity_service.create_identity(
        display_name="Chatbot", source_protocol="a2a",
    )["agent_id"]
    c = identity_service.create_identity(
        display_name="No Profile Bot", source_protocol="mcp",
    )["agent_id"]

    compliance_service.create_compliance_profile(
        agent_id=a, risk_category="high", provider_name="VibeTensor",
    )
    compliance_service.create_compliance_profile(
        agent_id=b, risk_category="limited", provider_name="VibeTensor",
    )
    return {"a": a, "b": b, "c": c}


class TestAllAgents:
    def test_includes_every_agent(self, report_service, org):
        report = report_service.generate_org_report()
        assert report["agent_count"] == 3
        ids = {rec["agent_id"] for rec in report["agents"]}
        assert ids == set(org.values())

    def test_summary_counts(self, report_service, org):
        report = report_service.generate_org_report()
        summary = report["summary"]
        # Two agents have profiles (both non-compliant fresh), one has none.
        assert summary["no_compliance_profile"] == 1
        assert summary["compliant"] + summary["non_compliant"] == 2

    def test_risk_breakdown(self, report_service, org):
        report = report_service.generate_org_report()
        breakdown = report["summary"]["risk_breakdown"]
        assert breakdown.get("high") == 1
        assert breakdown.get("limited") == 1

    def test_empty_org(self, report_service):
        report = report_service.generate_org_report()
        assert report["agent_count"] == 0
        assert report["agents"] == []


class TestSubset:
    def test_explicit_subset(self, report_service, org):
        report = report_service.generate_org_report(agent_ids=[org["a"]])
        assert report["agent_count"] == 1
        assert report["agents"][0]["agent_id"] == org["a"]

    def test_subset_excludes_others(self, report_service, org):
        report = report_service.generate_org_report(agent_ids=[org["a"], org["b"]])
        ids = {rec["agent_id"] for rec in report["agents"]}
        assert ids == {org["a"], org["b"]}
        assert org["c"] not in ids

    def test_unknown_agent_recorded_as_error(self, report_service, org):
        report = report_service.generate_org_report(
            agent_ids=["attestix:doesnotexist"]
        )
        assert "attestix:doesnotexist" in report["errors"]


class TestShapeReuse:
    def test_per_agent_record_carries_compliance_status(self, report_service, org):
        report = report_service.generate_org_report(agent_ids=[org["a"]])
        rec = report["agents"][0]
        assert rec["has_compliance_profile"] is True
        # Reuses the single-agent get_compliance_status shape.
        assert "compliant" in rec["compliance_status"]
        assert "completion_pct" in rec["compliance_status"]

    def test_no_profile_agent_has_null_status(self, report_service, org):
        report = report_service.generate_org_report(agent_ids=[org["c"]])
        rec = report["agents"][0]
        assert rec["has_compliance_profile"] is False
        assert rec["compliance_status"] is None
