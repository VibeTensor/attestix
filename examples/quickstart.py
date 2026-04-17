"""Attestix Quickstart - Complete Compliance Workflow

A single copy-paste script that demonstrates the full Attestix workflow:
  1. Create an agent identity (UAIT with DID)
  2. Record training data provenance (Article 10)
  3. Record model lineage (Article 11)
  4. Create a compliance profile (EU AI Act risk categorization)
  5. Run a conformity assessment (Article 43)
  6. Generate a declaration of conformity (Annex V)
  7. Issue and verify a credential (W3C VC)
  8. Build reputation via interaction recording
  9. Create a delegation token (UCAN)

Every parameter name in this script matches the actual service method
signatures. Tested against Attestix v0.3.0.

Usage:
    python examples/quickstart.py

Requires:
    pip install attestix
"""

import json
import sys
from pathlib import Path

# Allow running from the repo root or examples/ directory
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.identity_service import IdentityService
from services.compliance_service import ComplianceService
from services.provenance_service import ProvenanceService
from services.credential_service import CredentialService
from services.delegation_service import DelegationService
from services.reputation_service import ReputationService


def pp(obj):
    """Pretty-print a dict as indented JSON."""
    print(json.dumps(obj, indent=2, default=str))


def main():
    # Initialize services
    identity_svc = IdentityService()
    compliance_svc = ComplianceService()
    provenance_svc = ProvenanceService()
    credential_svc = CredentialService()
    delegation_svc = DelegationService()
    reputation_svc = ReputationService()

    # ----------------------------------------------------------------
    # Step 1: Create Agent Identity
    # ----------------------------------------------------------------
    print("=" * 60)
    print("Step 1: Create Agent Identity")
    print("=" * 60)

    agent = identity_svc.create_identity(
        display_name="FinanceBot",
        source_protocol="manual",
        capabilities=["financial_analysis", "risk_assessment", "reporting"],
        description="Automated financial risk analysis for loan applications",
        issuer_name="Acme Finance Ltd.",
        expiry_days=365,
    )
    assert "error" not in agent, f"Identity creation failed: {agent}"
    agent_id = agent["agent_id"]
    print(f"Agent ID:  {agent_id}")
    print(f"DID:       {agent['issuer']['did']}")
    print(f"Signed:    {bool(agent.get('signature'))}")
    print()

    # Verify the identity
    verification = identity_svc.verify_identity(agent_id)
    print(f"Identity valid: {verification['valid']}")
    for check, passed in verification["checks"].items():
        print(f"  {check}: {passed}")
    print()

    # ----------------------------------------------------------------
    # Step 2: Record Training Data Provenance (Article 10)
    # ----------------------------------------------------------------
    print("=" * 60)
    print("Step 2: Record Training Data (Article 10)")
    print("=" * 60)

    training = provenance_svc.record_training_data(
        agent_id=agent_id,
        dataset_name="SEC EDGAR Financial Filings",
        source_url="https://www.sec.gov/edgar/",
        license="Public Domain",
        data_categories=["financial_filings", "public_records"],
        contains_personal_data=False,
        data_governance_measures="Filtered to 10-K and 10-Q filings only. Validated schema.",
    )
    assert "error" not in training, f"Training data recording failed: {training}"
    print(f"Entry ID:  {training['entry_id']}")
    print(f"Dataset:   {training['dataset_name']}")
    print()

    # ----------------------------------------------------------------
    # Step 3: Record Model Lineage (Article 11)
    # ----------------------------------------------------------------
    print("=" * 60)
    print("Step 3: Record Model Lineage (Article 11)")
    print("=" * 60)

    lineage = provenance_svc.record_model_lineage(
        agent_id=agent_id,
        base_model="claude-sonnet-4-20250514",
        base_model_provider="Anthropic",
        fine_tuning_method="Supervised fine-tuning on financial domain corpus",
        evaluation_metrics={
            "accuracy": 0.92,
            "precision": 0.89,
            "recall": 0.94,
            "f1_score": 0.91,
        },
    )
    assert "error" not in lineage, f"Model lineage recording failed: {lineage}"
    print(f"Entry ID:  {lineage['entry_id']}")
    print(f"Model:     {lineage['base_model']} by {lineage['base_model_provider']}")
    print()

    # ----------------------------------------------------------------
    # Step 4: Create Compliance Profile
    # ----------------------------------------------------------------
    print("=" * 60)
    print("Step 4: Create Compliance Profile")
    print("=" * 60)

    profile = compliance_svc.create_compliance_profile(
        agent_id=agent_id,
        risk_category="high",
        provider_name="Acme Finance Ltd.",
        intended_purpose="Automated credit scoring for consumer loan applications",
        transparency_obligations="Discloses AI involvement. Explains key decision factors.",
        human_oversight_measures="Human loan officer reviews all AI recommendations before approval.",
    )
    assert "error" not in profile, f"Compliance profile creation failed: {profile}"
    print(f"Profile ID:    {profile['profile_id']}")
    print(f"Risk Category: {profile['risk_category']}")
    print(f"Obligations:   {len(profile.get('required_obligations', []))} required")
    print()

    # Gap analysis
    status = compliance_svc.get_compliance_status(agent_id)
    print(f"Compliant:  {status['compliant']}")
    print(f"Completion: {status['completion_pct']}%")
    print(f"Missing:    {status.get('missing', [])}")
    print()

    # ----------------------------------------------------------------
    # Step 5: Conformity Assessment (Article 43)
    # ----------------------------------------------------------------
    print("=" * 60)
    print("Step 5: Conformity Assessment (Article 43)")
    print("=" * 60)

    # High-risk systems cannot self-assess (this should fail)
    blocked = compliance_svc.record_conformity_assessment(
        agent_id=agent_id,
        assessment_type="self",
        assessor_name="Internal QA",
        result="pass",
    )
    print(f"Self-assessment blocked: {'error' in blocked}")
    if "error" in blocked:
        print(f"  Reason: {blocked['error'][:70]}...")
    print()

    # Third-party assessment succeeds
    assessment = compliance_svc.record_conformity_assessment(
        agent_id=agent_id,
        assessment_type="third_party",
        assessor_name="Bureau Veritas",
        result="pass",
        findings="System meets EU AI Act Annex III requirements for credit scoring.",
        ce_marking_eligible=True,
    )
    assert "error" not in assessment, f"Assessment failed: {assessment}"
    print(f"Assessment ID:  {assessment['assessment_id']}")
    print(f"Result:         {assessment['result']}")
    print(f"CE Marking:     {assessment['ce_marking_eligible']}")
    print()

    # ----------------------------------------------------------------
    # Step 6: Declaration of Conformity (Annex V)
    # ----------------------------------------------------------------
    print("=" * 60)
    print("Step 6: Declaration of Conformity (Annex V)")
    print("=" * 60)

    declaration = compliance_svc.generate_declaration_of_conformity(agent_id)
    assert "error" not in declaration, f"Declaration failed: {declaration}"
    print(f"Declaration ID: {declaration['declaration_id']}")
    print()

    # Final compliance status
    final_status = compliance_svc.get_compliance_status(agent_id)
    print(f"Final compliant: {final_status['compliant']}")
    print(f"Final completion: {final_status['completion_pct']}%")
    print()

    # ----------------------------------------------------------------
    # Step 7: Issue and Verify a Credential (W3C VC)
    # ----------------------------------------------------------------
    print("=" * 60)
    print("Step 7: Issue and Verify Credential (W3C VC)")
    print("=" * 60)

    credential = credential_svc.issue_credential(
        agent_id=agent_id,
        credential_type="AgentIdentityCredential",
        issuer_name="Acme Finance Ltd.",
        claims={
            "displayName": "FinanceBot",
            "capabilities": ["financial_analysis", "risk_assessment"],
            "complianceStatus": "EU AI Act compliant",
        },
        expiry_days=365,
    )
    assert "error" not in credential, f"Credential issuance failed: {credential}"
    cred_id = credential["id"]
    print(f"Credential ID: {cred_id}")
    print(f"Type:          {credential['type']}")
    print(f"Proof type:    {credential['proof']['type']}")
    print()

    # Verify the credential
    ver = credential_svc.verify_credential(cred_id)
    print(f"Credential valid: {ver['valid']}")
    for check, passed in ver.get("checks", {}).items():
        print(f"  {check}: {passed}")
    print()

    # ----------------------------------------------------------------
    # Step 8: Build Reputation
    # ----------------------------------------------------------------
    print("=" * 60)
    print("Step 8: Build Reputation")
    print("=" * 60)

    interactions = [
        ("success", "task", "Completed loan risk assessment accurately"),
        ("success", "task", "Generated quarterly compliance report"),
        ("partial", "delegation", "Partial data retrieval due to API timeout"),
        ("success", "task", "Processed batch of 500 applications"),
    ]
    for outcome, category, details in interactions:
        reputation_svc.record_interaction(
            agent_id=agent_id,
            counterparty_id="attestix:system",
            outcome=outcome,
            category=category,
            details=details,
        )

    reputation = reputation_svc.get_reputation(agent_id)
    print(f"Trust Score:    {reputation['trust_score']:.4f}")
    print(f"Interactions:   {reputation['total_interactions']}")
    print()

    # ----------------------------------------------------------------
    # Step 9: Create Delegation Token (UCAN)
    # ----------------------------------------------------------------
    print("=" * 60)
    print("Step 9: Create Delegation Token (UCAN)")
    print("=" * 60)

    # Create a second agent to delegate to
    subordinate = identity_svc.create_identity(
        display_name="ReportWriter",
        source_protocol="manual",
        capabilities=["report_writing"],
        description="Generates PDF reports from analysis results",
        issuer_name="Acme Finance Ltd.",
    )
    sub_id = subordinate["agent_id"]

    delegation = delegation_svc.create_delegation(
        issuer_agent_id=agent_id,
        audience_agent_id=sub_id,
        capabilities=["report_writing", "data_read"],
        expiry_hours=8,
    )
    assert "error" not in delegation, f"Delegation failed: {delegation}"
    record = delegation["delegation"]
    print(f"Token ID (jti): {record['jti']}")
    print(f"From:           {agent_id}")
    print(f"To:             {sub_id}")
    print(f"Capabilities:   {record['capabilities']}")
    print(f"Expires:        {record['expires_at']}")
    print()

    # Verify the delegation
    del_verify = delegation_svc.verify_delegation(delegation["token"])
    print(f"Delegation valid: {del_verify['valid']}")
    print()

    # ----------------------------------------------------------------
    # Summary
    # ----------------------------------------------------------------
    print("=" * 60)
    print("QUICKSTART COMPLETE")
    print("=" * 60)
    print()
    print(f"Agent:       {agent_id}")
    print(f"Compliant:   {final_status['compliant']}")
    print(f"Trust Score: {reputation['trust_score']:.4f}")
    print(f"Credentials: 1 manually issued + auto-issued compliance VC")
    print(f"Delegations: 1 UCAN token to {sub_id}")
    print()
    print("All artifacts are cryptographically signed (Ed25519) and stored")
    print("locally in JSON files. No external services required.")


if __name__ == "__main__":
    main()
