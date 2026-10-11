"""Compliance MCP tools for Attestix (7 tools).

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
        annex_iii_category: int = 0,
        annex_iii_exception: str = "",
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
            annex_iii_category: For high-risk systems, the Annex III point 1-8.
                Point 1 (biometrics) requires third-party assessment; Points 2-8
                permit self-assessment via Annex VI internal control. Use 0 or
                omit to leave unspecified (defaults to requiring third-party).
            annex_iii_exception: For Points 2-8, one of the documented carve-outs
                that still require third-party assessment per Article 43:
                'biometric_identification_law_enforcement',
                'financial_fraud_detection', 'political_campaign_organization'.
                Leave empty if no exception applies.
        """
        err = _validate_required({"agent_id": agent_id, "risk_category": risk_category,
                                   "provider_name": provider_name})
        if err:
            return err

        from attestix.services.cache import get_service
        from attestix.services.compliance_service import ComplianceService

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
            annex_iii_category=annex_iii_category if annex_iii_category else None,
            annex_iii_exception=annex_iii_exception or None,
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
        from attestix.services.cache import get_service
        from attestix.services.compliance_service import ComplianceService

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
        from attestix.services.cache import get_service
        from attestix.services.compliance_service import ComplianceService

        svc = get_service(ComplianceService)
        result = svc.get_compliance_profile(agent_id)
        if result is None:
            return json.dumps({"error": f"No compliance profile found for {agent_id}"})
        return json.dumps(result, indent=2, default=str)

    @mcp.tool()
    async def get_compliance_status(agent_id: str) -> str:
        """Check completeness of the recorded evidence workflow.

        Shows completed and missing evidence checks. Legal applicability,
        evidence quality, and conformity are not assessed by this tool.

        Args:
            agent_id: The Attestix agent ID.
        """
        from attestix.services.cache import get_service
        from attestix.services.compliance_service import ComplianceService

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

        Stores the provider's assessment record; assessor authority and legal
        conformity are not verified by Attestix. Assessment procedure rules
        depend on the profile's recorded classification.

        Args:
            agent_id: The Attestix agent ID.
            assessment_type: self or third_party.
            assessor_name: Name of the assessor or notified body.
            result: Assessment result: pass, conditional, or fail.
            findings: Detailed findings or conditions.
            ce_marking_eligible: Provider-recorded eligibility claim, not a legal determination.
        """
        from attestix.services.cache import get_service
        from attestix.services.compliance_service import ComplianceService

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
        """Generate a draft Annex V document for provider review.

        Requires the configured assessment prerequisites. Also issues a W3C
        credential binding the recorded workflow evidence. Neither document
        generation nor a valid signature establishes legal conformity.

        Args:
            agent_id: The Attestix agent ID.
        """
        from attestix.services.cache import get_service
        from attestix.services.compliance_service import (
            ComplianceService,
            InvalidComplianceProfileError,
        )

        svc = get_service(ComplianceService)
        try:
            result = svc.generate_declaration_of_conformity(agent_id)
        except InvalidComplianceProfileError as exc:
            # v0.4.0-rc.3 (P0 #4): surface missing-fields as a structured
            # error in the MCP tool response (LLMs cannot raise exceptions
            # but they can read an explicit error.missing_fields list).
            result = {
                "error": str(exc),
                "missing_fields": exc.missing_fields,
                "error_type": "invalid_compliance_profile",
            }
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
            compliant_only: Deprecated filter for recorded declaration presence, not legal conformity.
            limit: Maximum number of results.
        """
        from attestix.services.cache import get_service
        from attestix.services.compliance_service import ComplianceService

        svc = get_service(ComplianceService)
        results = svc.list_compliance_profiles(
            risk_category=risk_category or None,
            compliant_only=compliant_only,
            limit=limit,
        )
        return json.dumps(results, indent=2, default=str)
