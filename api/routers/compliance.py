"""Compliance router - REST endpoints wrapping ComplianceService.

EU AI Act compliance profiles, conformity assessments (Article 43),
and declarations of conformity (Annex V).
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from api.deps import get_compliance_service
from services.compliance_service import ComplianceService

router = APIRouter(prefix="/v1/compliance", tags=["compliance"])


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class CreateComplianceProfileRequest(BaseModel):
    agent_id: str = Field(..., description="Agent ID to create profile for")
    risk_category: str = Field(..., description="EU AI Act risk category: minimal, limited, high, or unacceptable")
    provider_name: str = Field(..., description="Name of the AI system provider")
    intended_purpose: str = Field("", description="Intended purpose of the AI system")
    transparency_obligations: str = Field("", description="Transparency obligations description")
    human_oversight_measures: str = Field("", description="Human oversight measures (required for high-risk)")
    provider_address: str = Field("", description="Provider address")
    authorised_representative: str = Field("", description="EU authorised representative (if applicable)")
    annex_iii_category: Optional[int] = Field(
        None,
        description=(
            "Annex III point (1-8) for high-risk systems. Point 1 (biometrics) "
            "mandates third-party assessment per Article 43; Points 2-8 permit "
            "self-assessment via Annex VI internal control."
        ),
    )
    annex_iii_exception: Optional[str] = Field(
        None,
        description=(
            "Carve-out within Points 2-8 that still requires third-party "
            "assessment. Valid values: "
            "'biometric_identification_law_enforcement', "
            "'financial_fraud_detection', 'political_campaign_organization'."
        ),
    )


class RecordAssessmentRequest(BaseModel):
    agent_id: str = Field(..., description="Agent ID being assessed")
    assessment_type: str = Field(..., description="Assessment type: self or third_party")
    assessor_name: str = Field(..., description="Name of the assessor or notified body")
    result: str = Field(..., description="Assessment result: pass, conditional, or fail")
    findings: str = Field("", description="Assessment findings and notes")
    ce_marking_eligible: bool = Field(False, description="Whether CE marking is eligible")


class GenerateDeclarationRequest(BaseModel):
    agent_id: str = Field(..., description="Agent ID to generate declaration for")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/profiles", status_code=201)
def create_compliance_profile(
    body: CreateComplianceProfileRequest,
    svc: ComplianceService = Depends(get_compliance_service),
):
    """Create an EU AI Act compliance profile for an agent."""
    result = svc.create_compliance_profile(
        agent_id=body.agent_id,
        risk_category=body.risk_category,
        provider_name=body.provider_name,
        intended_purpose=body.intended_purpose,
        transparency_obligations=body.transparency_obligations,
        human_oversight_measures=body.human_oversight_measures,
        provider_address=body.provider_address,
        authorised_representative=body.authorised_representative,
        annex_iii_category=body.annex_iii_category,
        annex_iii_exception=body.annex_iii_exception,
    )
    if isinstance(result, dict) and "error" in result:
        if "not found" in result["error"].lower():
            raise HTTPException(status_code=404, detail=result["error"])
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/profiles")
def list_compliance_profiles(
    risk_category: Optional[str] = None,
    compliant_only: bool = False,
    limit: int = 50,
    svc: ComplianceService = Depends(get_compliance_service),
):
    """List compliance profiles with optional filters."""
    results = svc.list_compliance_profiles(
        risk_category=risk_category,
        compliant_only=compliant_only,
        limit=limit,
    )
    if results and isinstance(results[0], dict) and "error" in results[0]:
        raise HTTPException(status_code=500, detail=results[0]["error"])
    return results


@router.get("/profiles/{profile_id}")
def get_compliance_profile(
    profile_id: str,
    svc: ComplianceService = Depends(get_compliance_service),
):
    """Get the compliance profile for an agent by agent_id.

    Note: profile_id here is the agent_id used to look up the profile.
    """
    result = svc.get_compliance_profile(profile_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"No compliance profile found for {profile_id}")
    return result


@router.get("/profiles/{profile_id}/status")
def get_compliance_status(
    profile_id: str,
    svc: ComplianceService = Depends(get_compliance_service),
):
    """Gap analysis: what is done, what is still needed for full compliance.

    Note: profile_id here is the agent_id used to look up the profile.
    """
    result = svc.get_compliance_status(profile_id)
    if isinstance(result, dict) and "error" in result:
        if "not found" in result["error"].lower():
            raise HTTPException(status_code=404, detail=result["error"])
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/assessments", status_code=201)
def record_conformity_assessment(
    body: RecordAssessmentRequest,
    svc: ComplianceService = Depends(get_compliance_service),
):
    """Record a conformity assessment (Article 43)."""
    result = svc.record_conformity_assessment(
        agent_id=body.agent_id,
        assessment_type=body.assessment_type,
        assessor_name=body.assessor_name,
        result=body.result,
        findings=body.findings,
        ce_marking_eligible=body.ce_marking_eligible,
    )
    if isinstance(result, dict) and "error" in result:
        if "not found" in result["error"].lower():
            raise HTTPException(status_code=404, detail=result["error"])
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/declarations", status_code=201)
def generate_declaration_of_conformity(
    body: GenerateDeclarationRequest,
    svc: ComplianceService = Depends(get_compliance_service),
):
    """Generate an EU AI Act Annex V declaration of conformity."""
    result = svc.generate_declaration_of_conformity(body.agent_id)
    if isinstance(result, dict) and "error" in result:
        if "not found" in result["error"].lower():
            raise HTTPException(status_code=404, detail=result["error"])
        raise HTTPException(status_code=400, detail=result["error"])
    return result
