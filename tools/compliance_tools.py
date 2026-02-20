"""Compliance MCP tools for Attestix (6 tools).

EU AI Act compliance profiles, conformity assessments, and declarations.
"""

import json


def _validate_required(params: dict) -> str:
    for name, value in params.items():
        if not value or (isinstance(value, str) and not value.strip()):
            return json.dumps({"error": f"{name} cannot be empty"})
    return ""


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
        provider_address: str = "",
        authorised_representative: str = "",
    ) -> str:
        """Create an EU AI Act compliance profile for an agent.

        Categorizes the AI system by risk level and tracks all compliance obligations.

        Args:
            agent_id: The Attestix agent ID (e.g., attestix:abc123...).
            risk_category: EU AI Act risk level: minimal, limited, or high.
            provider_name: Name of the AI system provider/company.
            intended_purpose: What the AI system is designed to do.
            transparency_obligations: How transparency requirements are met.
            human_oversight_measures: Human oversight mechanisms in place (required for high-risk).
            provider_address: Registered address of the provider.
            authorised_representative: Name of the EU authorised representative (if provider is outside EU).
        """
        err = _validate_required({"agent_id": agent_id, "risk_category": risk_category,
                                   "provider_name": provider_name})
        if err:
            return err

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
            provider_address=provider_address,
            authorised_representative=authorised_representative,
        )
        return json.dumps(result, indent=2, default=str)

    @mcp.tool()
    async def update_compliance_profile(
        agent_id: str,
        intended_purpose: str = "",
        transparency_obligations: str = "",
        human_oversight_measures: str = "",
        provider_name: str = "",
    ) -> str:
        """Update an existing EU AI Act compliance profile.

        Use this to iteratively fill in compliance information over time.
        Only non-empty fields will be updated.

        Args:
            agent_id: The Attestix agent ID.
            intended_purpose: Updated purpose description.
            transparency_obligations: Updated transparency info.
            human_oversight_measures: Updated human oversight info.
            provider_name: Updated provider name.
        """
        from services.cache import get_service
        from services.compliance_service import ComplianceService

        svc = get_service(ComplianceService)
        result = svc.update_compliance_profile(
            agent_id=agent_id,
            intended_purpose=intended_purpose or None,
            transparency_obligations=transparency_obligations or None,
            human_oversight_measures=human_oversight_measures or None,
            provider_name=provider_name or None,
        )
        return json.dumps(result, indent=2, default=str)

    @mcp.tool()
    async def get_compliance_profile(agent_id: str) -> str:
        """Get the EU AI Act compliance profile for an agent.

        Args:
            agent_id: The Attestix agent ID.
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
            agent_id: The Attestix agent ID.
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
            agent_id: The Attestix agent ID.
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
            agent_id: The Attestix agent ID.
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
