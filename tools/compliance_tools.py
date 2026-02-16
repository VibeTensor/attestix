"""Compliance MCP tools for AURA Protocol (6 tools).

EU AI Act compliance profiles, conformity assessments, and declarations.
"""

import json


def register(mcp):
    """Register compliance tools with the MCP server."""

    @mcp.tool()
    async def create_compliance_profile(
        agent_id: str,
        risk_category: str,
        provider_name: str,
        intended_purpose: str = "",
        transparency_obligations: str = "",
        human_oversight_measures: str = "",
    ) -> str:
        """Create an EU AI Act compliance profile for an agent.

        Categorizes the AI system by risk level and tracks all compliance obligations.

        Args:
            agent_id: The AURA agent ID (e.g., aura:abc123...).
            risk_category: EU AI Act risk level: minimal, limited, high, or unacceptable.
            provider_name: Name of the AI system provider/company.
            intended_purpose: What the AI system is designed to do.
            transparency_obligations: How transparency requirements are met.
            human_oversight_measures: Human oversight mechanisms in place (required for high-risk).
        """
        from services.cache import get_service
        from services.compliance_service import ComplianceService

        svc = get_service(ComplianceService)
        result = svc.create_compliance_profile(
            agent_id=agent_id,
            risk_category=risk_category,
            provider_name=provider_name,
            intended_purpose=intended_purpose,
            transparency_obligations=transparency_obligations,
            human_oversight_measures=human_oversight_measures,
        )
        return json.dumps(result, indent=2, default=str)

    @mcp.tool()
    async def get_compliance_profile(agent_id: str) -> str:
        """Get the EU AI Act compliance profile for an agent.

        Args:
            agent_id: The AURA agent ID.
        """
        from services.cache import get_service
        from services.compliance_service import ComplianceService

        svc = get_service(ComplianceService)
        result = svc.get_compliance_profile(agent_id)
        if result is None:
            return json.dumps({"error": f"No compliance profile found for {agent_id}"})
        return json.dumps(result, indent=2, default=str)

    @mcp.tool()
    async def get_compliance_status(agent_id: str) -> str:
        """Get compliance gap analysis: what's done and what's still needed.

        Shows completion percentage and lists completed vs missing requirements.

        Args:
            agent_id: The AURA agent ID.
        """
        from services.cache import get_service
        from services.compliance_service import ComplianceService

        svc = get_service(ComplianceService)
        result = svc.get_compliance_status(agent_id)
        return json.dumps(result, indent=2, default=str)

    @mcp.tool()
    async def record_conformity_assessment(
        agent_id: str,
        assessment_type: str,
        assessor_name: str,
        result: str,
        findings: str = "",
        ce_marking_eligible: bool = False,
    ) -> str:
        """Record a conformity assessment for EU AI Act Article 43.

        High-risk systems require third_party assessment. Limited/minimal can use self-assessment.

        Args:
            agent_id: The AURA agent ID.
            assessment_type: self or third_party.
            assessor_name: Name of the assessor or notified body.
            result: Assessment result: pass, conditional, or fail.
            findings: Detailed findings or conditions.
            ce_marking_eligible: Whether CE marking can be applied (only if result is pass).
        """
        from services.cache import get_service
        from services.compliance_service import ComplianceService

        svc = get_service(ComplianceService)
        assessment = svc.record_conformity_assessment(
            agent_id=agent_id,
            assessment_type=assessment_type,
            assessor_name=assessor_name,
            result=result,
            findings=findings,
            ce_marking_eligible=ce_marking_eligible,
        )
        return json.dumps(assessment, indent=2, default=str)

    @mcp.tool()
    async def generate_declaration_of_conformity(agent_id: str) -> str:
        """Generate an EU AI Act Annex V Declaration of Conformity.

        Requires a passing conformity assessment. Also issues a W3C Verifiable Credential
        as cryptographic proof of compliance.

        Args:
            agent_id: The AURA agent ID.
        """
        from services.cache import get_service
        from services.compliance_service import ComplianceService

        svc = get_service(ComplianceService)
        result = svc.generate_declaration_of_conformity(agent_id)
        return json.dumps(result, indent=2, default=str)

    @mcp.tool()
    async def list_compliance_profiles(
        risk_category: str = "",
        compliant_only: bool = False,
        limit: int = 50,
    ) -> str:
        """List EU AI Act compliance profiles with optional filters.

        Args:
            risk_category: Filter by risk level (minimal, limited, high, unacceptable). Empty = all.
            compliant_only: Only return profiles with completed declarations.
            limit: Maximum number of results.
        """
        from services.cache import get_service
        from services.compliance_service import ComplianceService

        svc = get_service(ComplianceService)
        results = svc.list_compliance_profiles(
            risk_category=risk_category or None,
            compliant_only=compliant_only,
            limit=limit,
        )
        return json.dumps(results, indent=2, default=str)
