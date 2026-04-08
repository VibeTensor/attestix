"""Integration tests for framework-specific Attestix integration patterns.

Tests that the exact integration patterns proposed in GitHub issues
(LangChain, CrewAI, OpenAI Agents, Semantic Kernel, Dify, ADK, Strands)
actually work end-to-end with real Attestix services.

Run: python -m pytest tests/integration/test_framework_integrations.py -v
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.identity_service import IdentityService
from services.compliance_service import ComplianceService
from services.provenance_service import ProvenanceService
from services.credential_service import CredentialService
from services.delegation_service import DelegationService
from services.reputation_service import ReputationService


@pytest.fixture
def identity_svc(tmp_attestix):
    return IdentityService()


@pytest.fixture
def compliance_svc(tmp_attestix):
    return ComplianceService()


@pytest.fixture
def provenance_svc(tmp_attestix):
    return ProvenanceService()


@pytest.fixture
def credential_svc(tmp_attestix):
    return CredentialService()


@pytest.fixture
def delegation_svc(tmp_attestix):
    return DelegationService()


@pytest.fixture
def reputation_svc(tmp_attestix):
    return ReputationService()


class TestLangChainIntegration:
    """Tests for LangChain callback handler pattern (GitHub issue #36617)."""

    def test_agent_identity_creation_with_mcp_protocol(self, identity_svc):
        """LangChain agents register with source_protocol='mcp'."""
        agent = identity_svc.create_identity(
            display_name="LangChainResearchAgent",
            source_protocol="mcp",
            capabilities=["web_search", "data_analysis"],
            issuer_name="AcmeCorp",
        )
        assert agent["agent_id"].startswith("attestix:")
        assert agent["source_protocol"] == "mcp"
        assert agent["issuer"]["did"].startswith("did:key:")
        assert agent["signature"]

    def test_callback_audit_trail_logging(self, identity_svc, provenance_svc):
        """Each LangChain callback event creates an audit trail entry."""
        agent = identity_svc.create_identity(
            display_name="CallbackAgent",
            source_protocol="mcp",
            capabilities=["search"],
            issuer_name="Test",
        )
        aid = agent["agent_id"]

        # Simulate: on_tool_start
        log1 = provenance_svc.log_action(
            agent_id=aid,
            action_type="external_call",
            input_summary="web_search: EU AI Act deadlines",
            output_summary="Found 5 results",
        )
        assert log1["log_id"].startswith("audit:")
        assert log1["chain_hash"]

        # Simulate: on_llm_start
        log2 = provenance_svc.log_action(
            agent_id=aid,
            action_type="inference",
            input_summary="Summarize search results",
            output_summary="Generated 3-paragraph summary",
        )
        assert log2["chain_hash"] != log1["chain_hash"]
        assert log2["prev_hash"] == log1["chain_hash"]

    def test_compliance_check_after_chain(self, identity_svc, compliance_svc):
        """Compliance status is checkable after agent chain completes."""
        agent = identity_svc.create_identity(
            display_name="ComplianceCheckAgent",
            source_protocol="mcp",
            capabilities=["analysis"],
            issuer_name="Test",
        )
        compliance_svc.create_compliance_profile(
            agent_id=agent["agent_id"],
            risk_category="limited",
            provider_name="Test",
            intended_purpose="Data analysis",
        )
        status = compliance_svc.get_compliance_status(agent["agent_id"])
        assert "completion_pct" in status
        assert isinstance(status["completion_pct"], (int, float))


class TestCrewAIIntegration:
    """Tests for CrewAI crew pattern with delegation (GitHub issue #5360)."""

    def test_multi_agent_crew_identity(self, identity_svc):
        """Each CrewAI agent role gets a unique DID-based identity."""
        agents = {}
        for role in ["Manager", "Researcher", "Writer"]:
            agent = identity_svc.create_identity(
                display_name=f"Crew{role}",
                source_protocol="mcp",
                capabilities=[role.lower()],
                issuer_name="AcmeCrew",
            )
            agents[role] = agent

        # Each agent gets a unique agent_id (DIDs share the server key by design)
        agent_ids = [a["agent_id"] for a in agents.values()]
        assert len(set(agent_ids)) == 3  # All unique agent IDs
        # All signed by the same server key
        assert all(a["signature"] for a in agents.values())

    def test_ucan_delegation_chain(self, identity_svc, delegation_svc):
        """Manager delegates capabilities to crew members via UCAN."""
        manager = identity_svc.create_identity(
            display_name="CrewManager",
            source_protocol="mcp",
            capabilities=["manage", "delegate", "research", "write"],
            issuer_name="AcmeCrew",
        )
        researcher = identity_svc.create_identity(
            display_name="Researcher",
            source_protocol="mcp",
            capabilities=["research"],
            issuer_name="AcmeCrew",
        )

        delegation = delegation_svc.create_delegation(
            issuer_agent_id=manager["agent_id"],
            audience_agent_id=researcher["agent_id"],
            capabilities=["research"],
            expiry_hours=8,
        )
        assert "token" in delegation
        assert delegation["delegation"]["issuer"] == manager["agent_id"]

        verify = delegation_svc.verify_delegation(delegation["token"])
        assert verify["valid"] is True

    def test_crew_reputation_tracking(self, identity_svc, reputation_svc):
        """Each crew member builds reputation from task outcomes."""
        agent = identity_svc.create_identity(
            display_name="ReliableWorker",
            source_protocol="mcp",
            capabilities=["research"],
            issuer_name="Test",
        )
        for _ in range(3):
            reputation_svc.record_interaction(
                agent_id=agent["agent_id"],
                counterparty_id="crew:manager",
                outcome="success",
                category="task",
            )
        rep = reputation_svc.get_reputation(agent["agent_id"])
        assert rep["trust_score"] > 0.9


class TestOpenAIAgentsIntegration:
    """Tests for OpenAI Agents SDK MCP pattern (GitHub issue #2862)."""

    def test_compliance_gate_blocks_without_profile(self, identity_svc, compliance_svc):
        """Agent without compliance profile is blocked by compliance gate."""
        agent = identity_svc.create_identity(
            display_name="UncertifiedAgent",
            source_protocol="mcp",
            capabilities=["analysis"],
            issuer_name="Test",
        )
        status = compliance_svc.get_compliance_status(agent["agent_id"])
        assert "error" in status  # No profile exists

    def test_compliance_gate_passes_after_setup(
        self, identity_svc, compliance_svc, provenance_svc
    ):
        """Agent passes compliance gate after full setup."""
        agent = identity_svc.create_identity(
            display_name="CertifiedAgent",
            source_protocol="mcp",
            capabilities=["analysis"],
            issuer_name="TestCorp",
        )
        aid = agent["agent_id"]

        compliance_svc.create_compliance_profile(
            agent_id=aid,
            risk_category="limited",
            provider_name="TestCorp",
            intended_purpose="Market analysis",
        )
        provenance_svc.record_training_data(
            agent_id=aid,
            dataset_name="Public Market Data",
            license="CC-BY-4.0",
            contains_personal_data=False,
        )
        compliance_svc.record_conformity_assessment(
            agent_id=aid,
            assessment_type="self",
            assessor_name="Internal QA",
            result="pass",
        )
        status = compliance_svc.get_compliance_status(aid)
        assert "error" not in status
        assert status["completion_pct"] > 0

    def test_credential_issuance_and_verification(
        self, identity_svc, credential_svc
    ):
        """Agent can issue and verify W3C Verifiable Credentials."""
        agent = identity_svc.create_identity(
            display_name="CredentialAgent",
            source_protocol="mcp",
            capabilities=["compliance"],
            issuer_name="Test",
        )
        cred = credential_svc.issue_credential(
            agent_id=agent["agent_id"],
            credential_type="EUAIActComplianceCredential",
            issuer_name="TestCorp",
            claims={"risk_category": "limited", "status": "conformant"},
        )
        assert cred["id"].startswith("urn:uuid:")
        assert cred["proof"]["type"] == "Ed25519Signature2020"

        verify = credential_svc.verify_credential(cred["id"])
        assert verify["valid"] is True
        assert verify["checks"]["signature_valid"] is True


class TestSemanticKernelIntegration:
    """Tests for Semantic Kernel plugin pattern (GitHub issue #13853)."""

    def test_compliance_plugin_functions(
        self, identity_svc, compliance_svc, provenance_svc, credential_svc
    ):
        """All 4 compliance plugin functions work as kernel functions would."""
        # KernelFunction: create_agent_identity
        agent = identity_svc.create_identity(
            display_name="SKAgent",
            source_protocol="mcp",
            capabilities=["document_analysis"],
            issuer_name="EnterpriseCorp",
        )
        assert agent["agent_id"]

        # KernelFunction: create_compliance_profile
        profile = compliance_svc.create_compliance_profile(
            agent_id=agent["agent_id"],
            risk_category="limited",
            provider_name="EnterpriseCorp",
            intended_purpose="Document analysis and summarization",
        )
        assert profile["profile_id"]

        # KernelFunction: log_action
        log = provenance_svc.log_action(
            agent_id=agent["agent_id"],
            action_type="inference",
            input_summary="Analyze quarterly report",
            output_summary="Generated executive summary",
        )
        assert log["log_id"]
        assert log["signature"]

        # KernelFunction: issue_credential
        cred = credential_svc.issue_credential(
            agent_id=agent["agent_id"],
            credential_type="AgentIdentityCredential",
            issuer_name="EnterpriseCorp",
            claims={"role": "document_analyst", "clearance": "internal"},
        )
        assert cred["proof"]["type"] == "Ed25519Signature2020"


class TestDifyIntegration:
    """Tests for Dify workflow compliance pattern (GitHub issue #34766)."""

    def test_workflow_step_logging(self, identity_svc, provenance_svc):
        """Each Dify workflow step produces an audit trail entry."""
        agent = identity_svc.create_identity(
            display_name="DifyWorkflowApp",
            source_protocol="mcp",
            capabilities=["chatbot", "rag"],
            issuer_name="DifyEnterprise",
        )
        aid = agent["agent_id"]

        steps = ["user_input", "rag_retrieval", "llm_generation", "response"]
        for step in steps:
            provenance_svc.log_action(
                agent_id=aid,
                action_type="inference" if "llm" in step else "data_access",
                input_summary=f"Workflow step: {step}",
                output_summary=f"Completed: {step}",
            )

        trail = provenance_svc.get_audit_trail(aid)
        assert len(trail) == 4
        # Verify hash chain integrity
        for i in range(1, len(trail)):
            assert trail[i]["prev_hash"] == trail[i - 1]["chain_hash"]


class TestGoogleADKIntegration:
    """Tests for Google ADK MCPToolset pattern (GitHub issue #5212)."""

    def test_agent_card_with_compliance(self, identity_svc, compliance_svc):
        """ADK agent gets identity + compliance for A2A Agent Card."""
        agent = identity_svc.create_identity(
            display_name="ADKComplianceAgent",
            source_protocol="a2a",
            capabilities=["compliance_check", "risk_assessment"],
            issuer_name="GoogleCloudUser",
        )
        assert agent["source_protocol"] == "a2a"

        profile = compliance_svc.create_compliance_profile(
            agent_id=agent["agent_id"],
            risk_category="minimal",
            provider_name="GoogleCloudUser",
            intended_purpose="Internal compliance checking tool",
        )
        assert profile["risk_category"] == "minimal"


class TestStrandsIntegration:
    """Tests for AWS Strands agent pattern (GitHub issue #2096)."""

    def test_agent_startup_registration(self, identity_svc, compliance_svc):
        """Strands agent registers with Attestix on startup."""
        agent = identity_svc.create_identity(
            display_name="StrandsBedrockAgent",
            source_protocol="mcp",
            capabilities=["bedrock_inference", "tool_use"],
            issuer_name="AWSEnterprise",
        )
        profile = compliance_svc.create_compliance_profile(
            agent_id=agent["agent_id"],
            risk_category="high",
            provider_name="AWSEnterprise",
            intended_purpose="Financial advisory AI agent",
            transparency_obligations="Discloses AI to users",
            human_oversight_measures="Human approval for trades over $10K",
        )
        assert profile["risk_category"] == "high"
        assert len(profile["required_obligations"]) >= 10

    def test_high_risk_blocks_self_assessment(self, identity_svc, compliance_svc):
        """High-risk Strands agent cannot self-assess (Article 43)."""
        agent = identity_svc.create_identity(
            display_name="HighRiskAgent",
            source_protocol="mcp",
            capabilities=["financial_advisory"],
            issuer_name="Test",
        )
        compliance_svc.create_compliance_profile(
            agent_id=agent["agent_id"],
            risk_category="high",
            provider_name="Test",
            intended_purpose="Financial advisory",
        )
        result = compliance_svc.record_conformity_assessment(
            agent_id=agent["agent_id"],
            assessment_type="self",
            assessor_name="Internal",
            result="pass",
        )
        assert "error" in result

    def test_prohibited_system_blocked(self, identity_svc, compliance_svc):
        """Unacceptable-risk system is blocked entirely (Article 5)."""
        agent = identity_svc.create_identity(
            display_name="SocialScoringBot",
            source_protocol="mcp",
            capabilities=["social_scoring"],
            issuer_name="BadCorp",
        )
        result = compliance_svc.create_compliance_profile(
            agent_id=agent["agent_id"],
            risk_category="unacceptable",
            provider_name="BadCorp",
            intended_purpose="Social credit scoring",
        )
        assert "error" in result
        assert "prohibited" in result["error"].lower() or "Article 5" in result["error"]
