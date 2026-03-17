#!/usr/bin/env python3
"""Attestix Demo Scenario 3: HR Screening AI

Two-part demo showing EU AI Act enforcement, then compliance after redesign.

Part A: TalentScan-v1 uses social scoring to rank job candidates.
        This is PROHIBITED under EU AI Act Article 5 (unacceptable risk).
        Attestix blocks the system from getting a compliance profile.

Part B: TalentMatch-v2 is redesigned to match skills to job requirements.
        This is HIGH-RISK (Annex III, employment domain) but ALLOWED.
        Attestix guides it through full compliance.

Run from the Attestix root directory:
    python demo/scenarios/03-hr-screening/run_demo.py
"""

import json
import os
import sys
import textwrap

# Add project root to path so service imports work
sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ),
)

from services.identity_service import IdentityService
from services.compliance_service import ComplianceService
from services.provenance_service import ProvenanceService
from services.credential_service import CredentialService
from services.did_service import DIDService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SEPARATOR = "=" * 80
THIN_SEP = "-" * 80


def banner(title: str, subtitle: str = ""):
    """Print a bold section banner."""
    print(f"\n{SEPARATOR}")
    print(f"  {title}")
    if subtitle:
        print(f"  {subtitle}")
    print(SEPARATOR)


def step(number: int, title: str):
    """Print a numbered step header."""
    print(f"\n{THIN_SEP}")
    print(f"  Step {number}: {title}")
    print(THIN_SEP)


def show(label: str, data, indent: int = 2):
    """Pretty-print a result with a label."""
    if isinstance(data, dict):
        print(f"\n  {label}:")
        print(textwrap.indent(json.dumps(data, indent=2, default=str), " " * indent))
    elif isinstance(data, list):
        print(f"\n  {label}:")
        print(textwrap.indent(json.dumps(data, indent=2, default=str), " " * indent))
    else:
        print(f"\n  {label}: {data}")


def status_icon(success: bool) -> str:
    return "PASS" if success else "BLOCKED"


# ---------------------------------------------------------------------------
# Initialize services
# ---------------------------------------------------------------------------

identity_svc = IdentityService()
compliance_svc = ComplianceService()
provenance_svc = ProvenanceService()
credential_svc = CredentialService()
did_svc = DIDService()


# =========================================================================
# PART A: THE PROHIBITED SYSTEM
# =========================================================================

banner(
    "PART A: THE PROHIBITED SYSTEM",
    "TalentScan-v1 uses social scoring - BANNED under EU AI Act Article 5",
)

# Step 1: Create agent identity for TalentScan-v1
step(1, "Create agent identity for TalentScan-v1")

v1_identity = identity_svc.create_identity(
    display_name="TalentScan-v1",
    source_protocol="internal",
    capabilities=["social_scoring", "behavioral_profiling", "candidate_ranking"],
    description=(
        "AI system that scores job candidates based on social media behavior, "
        "personal connections, and lifestyle patterns"
    ),
    issuer_name="HireRight AI Inc.",
)
v1_agent_id = v1_identity["agent_id"]

print(f"\n  Agent created: {v1_identity['display_name']}")
print(f"  Agent ID:      {v1_agent_id}")
print(f"  Capabilities:  {', '.join(v1_identity['capabilities'])}")
print(f"  Description:   {v1_identity['description']}")

# Step 2: Attempt to create compliance profile with risk_category = unacceptable
step(2, "Attempt compliance profile (risk_category = unacceptable)")

v1_profile_result = compliance_svc.create_compliance_profile(
    agent_id=v1_agent_id,
    risk_category="unacceptable",
    provider_name="HireRight AI Inc.",
    intended_purpose=(
        "Score and rank job candidates using social media activity, "
        "personal connections, and lifestyle pattern analysis"
    ),
)

if "error" in v1_profile_result:
    print(f"\n  >>> BLOCKED: {v1_profile_result['error']}")
    print("\n  The EU AI Act Article 5 prohibits social scoring systems.")
    print("  Attestix refuses to create a compliance profile for prohibited AI.")
else:
    print("\n  Profile created (unexpected):")
    show("Profile", v1_profile_result)

# Step 3: Show that declaration of conformity is impossible
step(3, "Attempt declaration of conformity (should fail)")

v1_declaration_result = compliance_svc.generate_declaration_of_conformity(v1_agent_id)

if "error" in v1_declaration_result:
    print(f"\n  >>> BLOCKED: {v1_declaration_result['error']}")
    print("\n  Without a compliance profile, no declaration can be issued.")
    print("  The system cannot legally operate in the EU market.")
else:
    print("\n  Declaration issued (unexpected):")
    show("Declaration", v1_declaration_result)

# Step 4: Log the enforcement action in the audit trail
step(4, "Log enforcement action in audit trail")

v1_audit = provenance_svc.log_action(
    agent_id=v1_agent_id,
    action_type="inference",
    input_summary="Attempted to register TalentScan-v1 for EU AI Act compliance",
    output_summary="REJECTED: System classified as unacceptable risk (Article 5 - social scoring)",
    decision_rationale=(
        "TalentScan-v1 performs social scoring of natural persons, which is "
        "explicitly prohibited under EU AI Act Article 5(1)(c). The system "
        "evaluates candidates based on social media behavior, personal "
        "connections, and lifestyle patterns - constituting social scoring."
    ),
    human_override=False,
)

print(f"\n  Audit entry logged: {v1_audit['log_id']}")
print(f"  Action type:        {v1_audit['action_type']}")
print(f"  Output:             {v1_audit['output_summary']}")
print(f"  Tamper-proof hash:  {v1_audit['chain_hash'][:32]}...")

# Step 5: Revoke the identity since the system is prohibited
step(5, "Revoke TalentScan-v1 identity (prohibited system)")

v1_revoked = identity_svc.revoke_identity(
    agent_id=v1_agent_id,
    reason="System prohibited under EU AI Act Article 5 - social scoring of natural persons",
)

print(f"\n  Identity revoked:  {v1_revoked['display_name']}")
print(f"  Revoked:           {v1_revoked['revoked']}")
print(f"  Reason:            {v1_revoked['revocation_reason']}")


# =========================================================================
# PART B: THE COMPLIANT REDESIGN
# =========================================================================

banner(
    "PART B: THE COMPLIANT REDESIGN",
    "TalentMatch-v2 uses skill matching - HIGH-RISK but ALLOWED",
)

# Step 6: Create new agent identity for TalentMatch-v2
step(6, "Create agent identity for TalentMatch-v2")

v2_identity = identity_svc.create_identity(
    display_name="TalentMatch-v2",
    source_protocol="internal",
    capabilities=["skill_matching", "resume_parsing", "job_requirement_analysis"],
    description=(
        "AI system that matches candidate skills to job requirements based "
        "on resume content and published job descriptions only"
    ),
    issuer_name="HireRight AI Inc.",
)
v2_agent_id = v2_identity["agent_id"]

print(f"\n  Agent created: {v2_identity['display_name']}")
print(f"  Agent ID:      {v2_agent_id}")
print(f"  Capabilities:  {', '.join(v2_identity['capabilities'])}")
print(f"  Description:   {v2_identity['description']}")
print("\n  KEY CHANGE: No social scoring, no behavioral profiling.")
print("  Only skill-to-job matching using structured resume data.")

# Step 7: Record training data provenance
step(7, "Record training data provenance (Article 10)")

td1 = provenance_svc.record_training_data(
    agent_id=v2_agent_id,
    dataset_name="O*NET Occupational Database",
    source_url="https://www.onetonline.org/",
    license="Public Domain",
    data_categories=["occupational_data", "skill_taxonomies", "job_descriptions"],
    contains_personal_data=False,
    data_governance_measures="Public government dataset, no personal data, freely available",
)

print(f"\n  Dataset 1: {td1['dataset_name']}")
print(f"  License:   {td1['license']}")
print(f"  Personal:  {td1['contains_personal_data']}")

td2 = provenance_svc.record_training_data(
    agent_id=v2_agent_id,
    dataset_name="Anonymized Resume Corpus",
    source_url="internal://hireright-ai/datasets/resume-corpus-v3",
    license="Proprietary",
    data_categories=["resumes", "skills", "work_experience"],
    contains_personal_data=True,
    data_governance_measures=(
        "Fully anonymized with k-anonymity (k=10). Individual consent obtained "
        "from all data subjects. GDPR-compliant processing agreement in place. "
        "Data Protection Impact Assessment completed. Right to erasure supported."
    ),
)

print(f"\n  Dataset 2: {td2['dataset_name']}")
print(f"  License:   {td2['license']}")
print(f"  Personal:  {td2['contains_personal_data']}")
print(f"  Governance: {td2['data_governance_measures'][:80]}...")

# Step 8: Record model lineage
step(8, "Record model lineage (Article 11)")

lineage = provenance_svc.record_model_lineage(
    agent_id=v2_agent_id,
    base_model="BERT-base-uncased",
    base_model_provider="Hugging Face / Google Research",
    fine_tuning_method="Supervised fine-tuning on O*NET skill taxonomy + anonymized resume pairs",
    evaluation_metrics={
        "skill_extraction_f1": 0.92,
        "job_match_accuracy": 0.88,
        "bias_audit_gender": "pass (disparity ratio 0.97)",
        "bias_audit_ethnicity": "pass (disparity ratio 0.95)",
        "false_positive_rate": 0.04,
        "false_negative_rate": 0.08,
    },
)

print(f"\n  Base model:     {lineage['base_model']}")
print(f"  Provider:       {lineage['base_model_provider']}")
print(f"  Fine-tuning:    {lineage['fine_tuning_method'][:60]}...")
print(f"  Metrics:")
for metric, value in lineage["evaluation_metrics"].items():
    print(f"    {metric}: {value}")

# Step 9: Create compliance profile (high risk)
step(9, "Create compliance profile (high-risk, Annex III employment)")

v2_profile = compliance_svc.create_compliance_profile(
    agent_id=v2_agent_id,
    risk_category="high",
    provider_name="HireRight AI Inc.",
    intended_purpose=(
        "Automated matching of candidate skills extracted from resumes to "
        "published job requirements. Used as a decision-support tool for "
        "recruiters. Does not make autonomous hiring decisions."
    ),
    transparency_obligations=(
        "Users informed that AI assists in candidate-job matching. "
        "Candidates notified per Article 52 that AI screening is used. "
        "Matching scores explained with contributing skill factors."
    ),
    human_oversight_measures=(
        "All AI-generated matches reviewed by human recruiter before "
        "candidate contact. Override mechanism available. Recruiter can "
        "adjust weights and reject AI recommendations. Monthly bias "
        "audits by independent team."
    ),
    provider_address="456 Innovation Blvd, Berlin, Germany",
    authorised_representative="Dr. Elena Fischer, Chief Compliance Officer",
)

if "error" in v2_profile:
    print(f"\n  ERROR: {v2_profile['error']}")
else:
    print(f"\n  Profile created: {v2_profile['profile_id']}")
    print(f"  Risk category:   {v2_profile['risk_category']}")
    print(f"  Provider:        {v2_profile['provider']['name']}")
    print(f"  Intended purpose (excerpt): {v2_profile['ai_system']['intended_purpose'][:60]}...")
    print(f"  Required obligations: {len(v2_profile['required_obligations'])} items")
    for obligation in v2_profile["required_obligations"]:
        print(f"    - {obligation}")

# Step 10: Run gap analysis
step(10, "Run compliance gap analysis")

gap = compliance_svc.get_compliance_status(v2_agent_id)

if "error" in gap:
    print(f"\n  ERROR: {gap['error']}")
else:
    print(f"\n  Risk category:  {gap['risk_category']}")
    print(f"  Completion:     {gap['completion_pct']}%")
    print(f"  Compliant:      {gap['compliant']}")
    print(f"\n  Completed ({len(gap['completed'])}):")
    for item in gap["completed"]:
        print(f"    [done] {item}")
    print(f"\n  Missing ({len(gap['missing'])}):")
    for item in gap["missing"]:
        print(f"    [todo] {item}")

# Step 11: Third-party conformity assessment
step(11, "Third-party conformity assessment by Bureau Veritas")

assessment = compliance_svc.record_conformity_assessment(
    agent_id=v2_agent_id,
    assessment_type="third_party",
    assessor_name="Bureau Veritas",
    result="pass",
    findings=(
        "TalentMatch-v2 meets all requirements under Annex III Category 4 "
        "(Employment, workers management). Risk management system adequate. "
        "Data governance measures verified. Bias testing methodology sound. "
        "Human oversight mechanisms effective. Transparency measures compliant. "
        "Recommended for CE marking."
    ),
    ce_marking_eligible=True,
)

if "error" in assessment:
    print(f"\n  ERROR: {assessment['error']}")
else:
    print(f"\n  Assessment ID:   {assessment['assessment_id']}")
    print(f"  Type:            {assessment['assessment_type']}")
    print(f"  Assessor:        {assessment['assessor_name']}")
    print(f"  Result:          {assessment['result']}")
    print(f"  CE eligible:     {assessment['ce_marking_eligible']}")
    print(f"  Findings (excerpt): {assessment['findings'][:80]}...")

# Step 12: Generate declaration of conformity
step(12, "Generate EU AI Act declaration of conformity (Annex V)")

declaration = compliance_svc.generate_declaration_of_conformity(v2_agent_id)

if "error" in declaration:
    print(f"\n  ERROR: {declaration['error']}")
else:
    print(f"\n  Declaration ID:  {declaration['declaration_id']}")
    print(f"  Regulation:      {declaration['regulation_reference']}")
    annex = declaration["annex_v_fields"]
    print(f"\n  Annex V Fields:")
    print(f"    1. Provider:           {annex['1_provider_name']}")
    print(f"    2. Representative:     {annex['2_authorised_representative']}")
    print(f"    3. AI System:          {annex['3_ai_system_name']}")
    print(f"    4. Purpose (excerpt):  {annex['4_intended_purpose'][:60]}...")
    print(f"    5. Risk category:      {annex['5_risk_category']}")
    print(f"    6. Assessment:         {annex['6a_assessment_type']} by {annex['6b_assessor_name']}")
    print(f"   10. CE marking:         {annex['10_ce_marking_eligible']}")
    print(f"   12. Declaration date:   {annex['12_declaration_date'][:10]}")

# Step 13: Verify the automatically issued credential
step(13, "Verify EU AI Act compliance credential")

# The declaration step auto-issues a credential; find it
creds = credential_svc.list_credentials(
    agent_id=v2_agent_id,
    credential_type="EUAIActComplianceCredential",
    valid_only=True,
)

if creds:
    cred = creds[0]
    cred_id = cred["id"]
    print(f"\n  Credential ID:   {cred_id}")
    print(f"  Type:            {', '.join(cred['type'])}")
    print(f"  Issuer:          {cred['issuer']['name']}")
    print(f"  Subject:         {cred['credentialSubject']['id']}")
    print(f"  Claims:")
    for k, v in cred["credentialSubject"].items():
        if k != "id":
            print(f"    {k}: {v}")

    # Verify the credential
    verification = credential_svc.verify_credential(cred_id)
    print(f"\n  Verification result:")
    print(f"    Valid:           {verification['valid']}")
    for check, passed in verification["checks"].items():
        print(f"    {check}: {passed}")
else:
    print("\n  No credential found (unexpected)")
    cred_id = None

# Step 14: Log the successful compliance journey in audit trail
step(14, "Log audit entries for the compliance journey")

audit_entries = [
    {
        "input_summary": "TalentScan-v1 prohibited, initiating system redesign",
        "output_summary": "Redesigned as TalentMatch-v2: removed social scoring, behavioral profiling",
        "decision_rationale": (
            "Original system violated Article 5 (social scoring). Redesigned to use "
            "only skill-to-job matching on structured resume data."
        ),
    },
    {
        "input_summary": "TalentMatch-v2 compliance process completed",
        "output_summary": "Declaration of conformity issued, CE marking eligible, credential verified",
        "decision_rationale": (
            "System passed third-party conformity assessment by Bureau Veritas. "
            "All Annex III Category 4 requirements met. System authorized for EU market."
        ),
    },
]

for i, entry_data in enumerate(audit_entries):
    audit = provenance_svc.log_action(
        agent_id=v2_agent_id,
        action_type="inference",
        input_summary=entry_data["input_summary"],
        output_summary=entry_data["output_summary"],
        decision_rationale=entry_data["decision_rationale"],
        human_override=False,
    )
    print(f"\n  Audit entry {i + 1}: {audit['log_id']}")
    print(f"  Output: {audit['output_summary'][:70]}...")

# Step 15: Final gap analysis (should be more complete now)
step(15, "Final compliance status check")

final_gap = compliance_svc.get_compliance_status(v2_agent_id)

if "error" not in final_gap:
    print(f"\n  Risk category:  {final_gap['risk_category']}")
    print(f"  Completion:     {final_gap['completion_pct']}%")
    print(f"  Compliant:      {final_gap['compliant']}")
    print(f"\n  Completed ({len(final_gap['completed'])}):")
    for item in final_gap["completed"]:
        print(f"    [done] {item}")
    if final_gap["missing"]:
        print(f"\n  Still missing ({len(final_gap['missing'])}):")
        for item in final_gap["missing"]:
            print(f"    [todo] {item}")


# =========================================================================
# SIDE-BY-SIDE COMPARISON
# =========================================================================

banner("SIDE-BY-SIDE COMPARISON")

v1_status = "PROHIBITED"
v2_status = "COMPLIANT" if (not final_gap.get("error") and final_gap.get("compliant")) else f"{final_gap.get('completion_pct', '?')}% COMPLETE"
v1_declaration = "BLOCKED"
v2_declaration = declaration.get("declaration_id", "ISSUED") if "error" not in declaration else "FAILED"
v1_credential = "NONE"
v2_credential = "VERIFIED" if (creds and verification.get("valid")) else "NONE"

col1 = 40
col2 = 40

print()
print(f"  {'TalentScan-v1 (social scoring)':<{col1}}  {'TalentMatch-v2 (skill matching)':<{col2}}")
print(f"  {'=' * (col1 - 2)}    {'=' * (col2 - 2)}")
print(f"  {'Risk: Unacceptable':<{col1}}  {'Risk: High':<{col2}}")
print(f"  {f'Status: {v1_status}':<{col1}}  {f'Status: {v2_status}':<{col2}}")
print(f"  {f'Declaration: {v1_declaration}':<{col1}}  {f'Declaration: {v2_declaration}':<{col2}}")
print(f"  {f'Credential: {v1_credential}':<{col1}}  {f'Credential: {v2_credential}':<{col2}}")
print(f"  {'Capabilities:':<{col1}}  {'Capabilities:':<{col2}}")
print(f"  {'  - social_scoring':<{col1}}  {'  - skill_matching':<{col2}}")
print(f"  {'  - behavioral_profiling':<{col1}}  {'  - resume_parsing':<{col2}}")
print(f"  {'  - candidate_ranking':<{col1}}  {'  - job_requirement_analysis':<{col2}}")
print()

print(SEPARATOR)
print("  KEY TAKEAWAY")
print(SEPARATOR)
print(textwrap.fill(
    "The EU AI Act does not ban AI in hiring. It bans social scoring. "
    "By redesigning TalentScan-v1 (which profiled candidates based on "
    "social media and lifestyle) into TalentMatch-v2 (which matches "
    "skills to job requirements), HireRight AI Inc. went from a "
    "prohibited system to a fully compliant one. Attestix enforced "
    "the prohibition AND guided the compliant path.",
    width=76,
    initial_indent="  ",
    subsequent_indent="  ",
))
print()
print(f"  Demo complete. {15} steps executed across both systems.")
print()
