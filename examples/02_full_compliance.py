"""Example 2: Full EU AI Act Compliance Workflow

Takes a high-risk medical AI agent from zero to fully compliant,
following the complete Article 10-12, 43, and Annex V workflow.

Usage:
    python examples/02_full_compliance.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.identity_service import IdentityService
from services.compliance_service import ComplianceService
from services.provenance_service import ProvenanceService
from services.credential_service import CredentialService


def main():
    identity_svc = IdentityService()
    compliance_svc = ComplianceService()
    provenance_svc = ProvenanceService()
    credential_svc = CredentialService()

    # Step 1: Create Agent Identity
    print("=== Step 1: Create Agent Identity ===\n")
    agent = identity_svc.create_identity(
        display_name="MedAssist-AI",
        source_protocol="manual",
        capabilities=["medical_diagnosis", "patient_triage", "radiology_analysis"],
        description="AI-assisted medical diagnosis for clinical decision support in radiology",
        issuer_name="HealthTech Corp.",
    )
    agent_id = agent["agent_id"]
    print(f"Agent ID: {agent_id}")
    print(f"EU Compliance: {agent.get('eu_compliance', 'None (not yet created)')}")

    # Step 2: Record Training Data Provenance (Article 10)
    print("\n=== Step 2: Record Training Data (Article 10) ===\n")
    datasets = [
        {
            "dataset_name": "PubMed Central Open Access",
            "source_url": "https://www.ncbi.nlm.nih.gov/pmc/tools/openftlist/",
            "license": "CC-BY-4.0",
            "contains_personal_data": False,
            "data_categories": ["medical_literature", "peer_reviewed"],
            "data_governance_measures": "Peer-reviewed articles only. Quality-checked for relevance.",
        },
        {
            "dataset_name": "MIMIC-IV Clinical Database",
            "source_url": "https://physionet.org/content/mimiciv/",
            "license": "PhysioNet Credentialed Health Data License 1.5.0",
            "contains_personal_data": True,
            "data_categories": ["clinical_records", "de_identified"],
            "data_governance_measures": "De-identified per HIPAA Safe Harbor. IRB approval obtained.",
        },
    ]

    for ds in datasets:
        result = provenance_svc.record_training_data(agent_id=agent_id, **ds)
        print(f"  Recorded: {ds['dataset_name']} ({result['entry_id'][:16]}...)")

    # Step 3: Record Model Lineage (Article 11)
    print("\n=== Step 3: Record Model Lineage (Article 11) ===\n")
    lineage = provenance_svc.record_model_lineage(
        agent_id=agent_id,
        base_model="claude-opus-4-6",
        base_model_provider="Anthropic",
        fine_tuning_method="LoRA + RLHF with board-certified physician feedback",
        evaluation_metrics={
            "diagnostic_accuracy": 0.94,
            "sensitivity": 0.91,
            "specificity": 0.96,
            "auc_roc": 0.97,
            "f1_score": 0.93,
        },
    )
    print(f"  Model: {lineage['base_model']} by {lineage['base_model_provider']}")
    print(f"  Entry ID: {lineage['entry_id'][:16]}...")

    # Step 4: Create Compliance Profile
    print("\n=== Step 4: Create Compliance Profile ===\n")
    profile = compliance_svc.create_compliance_profile(
        agent_id=agent_id,
        risk_category="high",
        provider_name="HealthTech Corp.",
        intended_purpose="AI-assisted medical diagnosis for clinical decision support in radiology.",
        transparency_obligations="System clearly discloses AI-generated content. Provides confidence scores.",
        human_oversight_measures="All diagnoses require attending physician approval before delivery.",
    )
    print(f"  Profile ID: {profile['profile_id']}")
    print(f"  Risk Category: {profile['risk_category']}")
    print(f"  Obligations: {len(profile.get('required_obligations', []))} required items")

    # Step 5: Check Compliance Status (Gap Analysis)
    print("\n=== Step 5: Gap Analysis ===\n")
    status = compliance_svc.get_compliance_status(agent_id)
    print(f"  Compliant: {status['compliant']}")
    print(f"  Completion: {status['completion_pct']}%")
    print(f"  Completed: {status.get('completed', [])}")
    print(f"  Missing: {status.get('missing', [])}")

    # Step 6: Record Conformity Assessment (Article 43)
    print("\n=== Step 6: Conformity Assessment (Article 43) ===\n")

    # Demonstrate that self-assessment is blocked for high-risk
    self_result = compliance_svc.record_conformity_assessment(
        agent_id=agent_id,
        assessment_type="self",
        assessor_name="Internal QA",
        result="pass",
    )
    if "error" in self_result:
        print(f"  Self-assessment blocked (expected): {self_result['error'][:60]}...")

    # Third-party assessment passes
    assessment = compliance_svc.record_conformity_assessment(
        agent_id=agent_id,
        assessment_type="third_party",
        assessor_name="TUV Rheinland AG",
        result="pass",
        findings="System meets all Annex III requirements for medical AI.",
        ce_marking_eligible=True,
    )
    print(f"  Assessment ID: {assessment['assessment_id']}")
    print(f"  Result: {assessment['result']}")
    print(f"  CE Marking: {assessment['ce_marking_eligible']}")

    # Step 7: Generate Declaration of Conformity (Annex V)
    print("\n=== Step 7: Declaration of Conformity (Annex V) ===\n")
    declaration = compliance_svc.generate_declaration_of_conformity(agent_id)
    print(f"  Declaration ID: {declaration['declaration_id']}")

    # Step 8: Final Compliance Check
    print("\n=== Step 8: Final Compliance Status ===\n")
    final_status = compliance_svc.get_compliance_status(agent_id)
    print(f"  Compliant: {final_status['compliant']}")
    print(f"  Completion: {final_status['completion_pct']}%")
    print(f"  Missing: {final_status.get('missing', [])}")

    # Step 9: Verify the auto-issued credential
    print("\n=== Step 9: Verify Compliance Credential ===\n")
    creds = credential_svc.list_credentials(
        agent_id=agent_id, credential_type="EUAIActComplianceCredential",
    )
    if creds:
        cred_id = creds[0]["id"]
        verification = credential_svc.verify_credential(cred_id)
        print(f"  Credential ID: {cred_id}")
        print(f"  Valid: {verification.get('valid')}")
        for check, passed in verification.get("checks", {}).items():
            print(f"    {check}: {passed}")
    else:
        print("  No compliance credential found")

    # Step 10: View full provenance
    print("\n=== Step 10: Full Provenance Record ===\n")
    provenance = provenance_svc.get_provenance(agent_id)
    print(f"  Training datasets: {len(provenance.get('training_data', []))}")
    print(f"  Model lineage entries: {len(provenance.get('model_lineage', []))}")
    print(f"  Audit log count: {provenance.get('audit_log_count', 0)}")

    print("\n=== Compliance Workflow Complete ===")
    print(f"\nAgent {agent_id} is now EU AI Act compliant.")
    print("All artifacts are cryptographically signed and stored locally.")


if __name__ == "__main__":
    main()
