"""Compliance service for Attestix.

EU AI Act compliance profiles, conformity assessments (Article 43),
and declarations of conformity (Annex V).
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from auth.crypto import load_or_create_signing_key, sign_json_payload
from config import load_compliance, save_compliance
from errors import ErrorCategory, log_and_format_error


VALID_RISK_CATEGORIES = {"minimal", "limited", "high", "unacceptable"}
VALID_ASSESSMENT_TYPES = {"self", "third_party"}
VALID_ASSESSMENT_RESULTS = {"pass", "conditional", "fail"}

# EU AI Act Annex V required fields for declaration of conformity
ANNEX_V_REQUIRED = [
    "provider_name",
    "intended_purpose",
    "risk_category",
    "conformity_assessment",
]


class ComplianceService:
    """Manages EU AI Act compliance profiles, assessments, and declarations."""

    def __init__(self):
        self._private_key, self._server_did = load_or_create_signing_key()
        self._identity_svc = None
        self._credential_svc = None

    @property
    def identity_svc(self):
        """Lazy-load to prevent circular imports."""
        if self._identity_svc is None:
            from services.identity_service import IdentityService
            self._identity_svc = IdentityService()
        return self._identity_svc

    @property
    def credential_svc(self):
        """Lazy-load to prevent circular imports."""
        if self._credential_svc is None:
            from services.credential_service import CredentialService
            self._credential_svc = CredentialService()
        return self._credential_svc

    def create_compliance_profile(
        self,
        agent_id: str,
        risk_category: str,
        provider_name: str,
        intended_purpose: str = "",
        transparency_obligations: str = "",
        human_oversight_measures: str = "",
    ) -> dict:
        """Create an EU AI Act compliance profile for an agent."""
        try:
            if risk_category not in VALID_RISK_CATEGORIES:
                return {
                    "error": f"Invalid risk_category '{risk_category}'. "
                    f"Must be one of: {', '.join(sorted(VALID_RISK_CATEGORIES))}"
                }

            if risk_category == "unacceptable":
                return {
                    "error": "Unacceptable-risk AI systems are prohibited under the EU AI Act "
                    "(Article 5). Cannot create a compliance profile for prohibited systems."
                }

            # Verify agent exists
            agent = self.identity_svc.get_identity(agent_id)
            if not agent:
                return {"error": f"Agent {agent_id} not found"}

            # Check for existing profile
            data = load_compliance()
            for p in data["profiles"]:
                if p["agent_id"] == agent_id:
                    return {"error": f"Compliance profile already exists for {agent_id}. Use get_compliance_profile to view it."}

            profile_id = f"comp:{uuid.uuid4().hex[:12]}"
            now = datetime.now(timezone.utc).isoformat()

            # Determine required obligations based on risk category
            required_obligations = self._get_required_obligations(risk_category)

            profile = {
                "profile_id": profile_id,
                "agent_id": agent_id,
                "risk_category": risk_category,
                "provider": {
                    "name": provider_name,
                    "did": self._server_did,
                },
                "ai_system": {
                    "intended_purpose": intended_purpose,
                    "display_name": agent.get("display_name", ""),
                },
                "transparency": {
                    "obligations": transparency_obligations,
                    "human_oversight_measures": human_oversight_measures,
                },
                "required_obligations": required_obligations,
                "conformity": {
                    "assessment_completed": False,
                    "assessment_id": None,
                    "declaration_id": None,
                    "ce_marking_eligible": False,
                },
                "created_at": now,
                "updated_at": now,
            }

            signable = {k: v for k, v in profile.items() if k != "signature"}
            profile["signature"] = sign_json_payload(self._private_key, signable)

            data["profiles"].append(profile)
            save_compliance(data)

            # Link compliance profile to UAIT
            self.identity_svc.update_compliance_ref(agent_id, profile_id)

            return profile
        except Exception as e:
            msg = log_and_format_error(
                "create_compliance_profile", e, ErrorCategory.COMPLIANCE,
                agent_id=agent_id,
            )
            return {"error": msg}

    def get_compliance_profile(self, agent_id: str) -> Optional[dict]:
        """Get the compliance profile for an agent."""
        data = load_compliance()
        for p in data["profiles"]:
            if p["agent_id"] == agent_id:
                return p
        return None

    def record_conformity_assessment(
        self,
        agent_id: str,
        assessment_type: str,
        assessor_name: str,
        result: str,
        findings: str = "",
        ce_marking_eligible: bool = False,
    ) -> dict:
        """Record a conformity assessment (Article 43)."""
        try:
            if assessment_type not in VALID_ASSESSMENT_TYPES:
                return {
                    "error": f"Invalid assessment_type '{assessment_type}'. "
                    f"Must be one of: {', '.join(sorted(VALID_ASSESSMENT_TYPES))}"
                }
            if result not in VALID_ASSESSMENT_RESULTS:
                return {
                    "error": f"Invalid result '{result}'. "
                    f"Must be one of: {', '.join(sorted(VALID_ASSESSMENT_RESULTS))}"
                }

            # Verify compliance profile exists
            profile = self.get_compliance_profile(agent_id)
            if not profile:
                return {"error": f"No compliance profile found for {agent_id}. Create one first."}

            # High-risk systems require third-party assessment
            if profile["risk_category"] == "high" and assessment_type == "self":
                return {
                    "error": "High-risk AI systems require third_party conformity assessment (Article 43)."
                }

            assessment_id = f"assess:{uuid.uuid4().hex[:12]}"
            now = datetime.now(timezone.utc).isoformat()

            assessment = {
                "assessment_id": assessment_id,
                "agent_id": agent_id,
                "assessment_type": assessment_type,
                "assessor_name": assessor_name,
                "result": result,
                "findings": findings,
                "ce_marking_eligible": ce_marking_eligible and result == "pass",
                "assessed_at": now,
                "assessed_by": self._server_did,
            }

            signable = {k: v for k, v in assessment.items() if k != "signature"}
            assessment["signature"] = sign_json_payload(self._private_key, signable)

            data = load_compliance()
            data["assessments"].append(assessment)

            # Update profile with assessment reference
            for p in data["profiles"]:
                if p["agent_id"] == agent_id:
                    p["conformity"]["assessment_completed"] = result in ("pass", "conditional")
                    p["conformity"]["assessment_id"] = assessment_id
                    p["conformity"]["ce_marking_eligible"] = assessment["ce_marking_eligible"]
                    p["updated_at"] = now
                    break

            save_compliance(data)

            return assessment
        except Exception as e:
            msg = log_and_format_error(
                "record_conformity_assessment", e, ErrorCategory.COMPLIANCE,
                agent_id=agent_id,
            )
            return {"error": msg}

    def generate_declaration_of_conformity(self, agent_id: str) -> dict:
        """Generate an EU AI Act Annex V declaration of conformity."""
        try:
            profile = self.get_compliance_profile(agent_id)
            if not profile:
                return {"error": f"No compliance profile found for {agent_id}"}

            # Check prerequisites
            if not profile["conformity"]["assessment_completed"]:
                return {
                    "error": "Cannot generate declaration: conformity assessment not completed or not passed. "
                    "Use record_conformity_assessment first."
                }

            # Validate required Annex V fields
            missing_fields = []
            if not profile["ai_system"].get("intended_purpose", "").strip():
                missing_fields.append("intended_purpose")
            if not profile["transparency"].get("obligations", "").strip():
                missing_fields.append("transparency_obligations")
            if profile["risk_category"] == "high":
                if not profile["transparency"].get("human_oversight_measures", "").strip():
                    missing_fields.append("human_oversight_measures")
                # Re-validate: high-risk requires third-party assessment
                data_check = load_compliance()
                assess_id = profile["conformity"]["assessment_id"]
                if assess_id:
                    assessment = next(
                        (a for a in data_check["assessments"] if a["assessment_id"] == assess_id),
                        None
                    )
                    if assessment and assessment.get("assessment_type") != "third_party":
                        return {
                            "error": "High-risk AI systems require third_party conformity assessment (Article 43). "
                            "Current assessment is self-assessment."
                        }
            if missing_fields:
                return {
                    "error": f"Cannot generate declaration: missing required fields: {', '.join(missing_fields)}. "
                    "Update the compliance profile first."
                }

            declaration_id = f"decl:{uuid.uuid4().hex[:12]}"
            now = datetime.now(timezone.utc).isoformat()

            # Build Annex V declaration
            declaration = {
                "declaration_id": declaration_id,
                "agent_id": agent_id,
                "annex_v_fields": {
                    "1_provider_name": profile["provider"]["name"],
                    "2_ai_system_name": profile["ai_system"]["display_name"],
                    "3_intended_purpose": profile["ai_system"]["intended_purpose"],
                    "4_risk_category": profile["risk_category"],
                    "5_conformity_assessment_id": profile["conformity"]["assessment_id"],
                    "6_transparency_obligations": profile["transparency"]["obligations"],
                    "7_human_oversight": profile["transparency"]["human_oversight_measures"],
                    "8_ce_marking_eligible": profile["conformity"]["ce_marking_eligible"],
                    "9_declaration_date": now,
                    "10_provider_did": profile["provider"]["did"],
                },
                "issued_at": now,
                "issuer_did": self._server_did,
            }

            signable = {k: v for k, v in declaration.items() if k != "signature"}
            declaration["signature"] = sign_json_payload(self._private_key, signable)

            data = load_compliance()
            data["declarations"].append(declaration)

            # Update profile with declaration reference
            for p in data["profiles"]:
                if p["agent_id"] == agent_id:
                    p["conformity"]["declaration_id"] = declaration_id
                    p["updated_at"] = now
                    break

            save_compliance(data)

            # Issue a Verifiable Credential for this declaration
            self.credential_svc.issue_credential(
                subject_id=agent_id,
                credential_type="EUAIActComplianceCredential",
                issuer_name=profile["provider"]["name"],
                claims={
                    "declaration_id": declaration_id,
                    "risk_category": profile["risk_category"],
                    "conformity_assessment_id": profile["conformity"]["assessment_id"],
                    "ce_marking_eligible": profile["conformity"]["ce_marking_eligible"],
                    "eu_ai_act_compliant": True,
                },
                expiry_days=365,
            )

            return declaration
        except Exception as e:
            msg = log_and_format_error(
                "generate_declaration_of_conformity", e, ErrorCategory.COMPLIANCE,
                agent_id=agent_id,
            )
            return {"error": msg}

    def get_compliance_status(self, agent_id: str) -> dict:
        """Gap analysis: what's done, what's still needed for full compliance."""
        try:
            profile = self.get_compliance_profile(agent_id)
            if not profile:
                return {"error": f"No compliance profile found for {agent_id}"}

            status = {
                "agent_id": agent_id,
                "risk_category": profile["risk_category"],
                "compliant": False,
                "completed": [],
                "missing": [],
            }

            # Check each requirement
            # 1. Profile exists
            status["completed"].append("compliance_profile_created")

            # 2. Intended purpose documented
            if profile["ai_system"].get("intended_purpose"):
                status["completed"].append("intended_purpose_documented")
            else:
                status["missing"].append("intended_purpose_documented")

            # 3. Transparency obligations
            if profile["transparency"].get("obligations"):
                status["completed"].append("transparency_obligations_declared")
            else:
                status["missing"].append("transparency_obligations_declared")

            # 4. Human oversight measures (required for high-risk)
            if profile["risk_category"] == "high":
                if profile["transparency"].get("human_oversight_measures"):
                    status["completed"].append("human_oversight_measures")
                else:
                    status["missing"].append("human_oversight_measures")

            # 5. Conformity assessment
            if profile["conformity"]["assessment_completed"]:
                status["completed"].append("conformity_assessment_passed")
            else:
                status["missing"].append("conformity_assessment_passed")

            # 6. Declaration of conformity
            if profile["conformity"]["declaration_id"]:
                status["completed"].append("declaration_of_conformity_issued")
            else:
                status["missing"].append("declaration_of_conformity_issued")

            # 7. Check provenance (training data + model lineage)
            from config import load_provenance
            prov_data = load_provenance()
            has_training = any(
                e["agent_id"] == agent_id and e["entry_type"] == "training_data"
                for e in prov_data["entries"]
            )
            has_lineage = any(
                e["agent_id"] == agent_id and e["entry_type"] == "model_lineage"
                for e in prov_data["entries"]
            )

            if has_training:
                status["completed"].append("training_data_provenance")
            else:
                status["missing"].append("training_data_provenance")

            if has_lineage:
                status["completed"].append("model_lineage_recorded")
            else:
                status["missing"].append("model_lineage_recorded")

            # Overall compliance
            status["compliant"] = len(status["missing"]) == 0
            status["completion_pct"] = round(
                len(status["completed"]) / (len(status["completed"]) + len(status["missing"])) * 100, 1
            )

            return status
        except Exception as e:
            msg = log_and_format_error(
                "get_compliance_status", e, ErrorCategory.COMPLIANCE,
                agent_id=agent_id,
            )
            return {"error": msg}

    def list_compliance_profiles(
        self,
        risk_category: Optional[str] = None,
        compliant_only: bool = False,
        limit: int = 50,
    ) -> List[dict]:
        """List compliance profiles with optional filters."""
        try:
            data = load_compliance()
            results = []

            for profile in data["profiles"]:
                if risk_category and profile["risk_category"] != risk_category:
                    continue
                if compliant_only:
                    if not profile["conformity"]["declaration_id"]:
                        continue

                results.append(profile)
                if len(results) >= limit:
                    break

            return results
        except Exception as e:
            msg = log_and_format_error(
                "list_compliance_profiles", e, ErrorCategory.COMPLIANCE,
            )
            return [{"error": msg}]

    def _get_required_obligations(self, risk_category: str) -> List[str]:
        """Return required obligations based on EU AI Act risk category."""
        base = ["registration_in_eu_database"]

        if risk_category == "minimal":
            return base + ["voluntary_code_of_conduct"]

        if risk_category == "limited":
            return base + [
                "transparency_disclosure",
                "inform_users_of_ai_interaction",
            ]

        if risk_category == "high":
            return base + [
                "conformity_assessment",
                "quality_management_system",
                "risk_management_system",
                "data_governance",
                "technical_documentation",
                "record_keeping",
                "transparency_to_users",
                "human_oversight",
                "accuracy_robustness_cybersecurity",
                "post_market_monitoring",
                "serious_incident_reporting",
            ]

        if risk_category == "unacceptable":
            return ["PROHIBITED_SYSTEM"]

        return base
