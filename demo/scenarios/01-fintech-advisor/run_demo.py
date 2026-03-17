#!/usr/bin/env python3
"""
Attestix Demo Scenario 1: FinTech Advisory AI (HIGH-RISK under EU AI Act)

Agent: WealthBot-Pro by FinanceAI Corp
Risk: HIGH - Financial advisory falls under EU AI Act Annex III
      (access to and enjoyment of essential private/public services)

This script exercises the full Attestix lifecycle:
  Identity -> DID -> Provenance -> Compliance -> Credentials ->
  Delegation -> Reputation -> Audit Trail

Run from the Attestix root directory:
    python demo/scenarios/01-fintech-advisor/run_demo.py
"""

import json
import os
import sys

# Ensure imports resolve from the Attestix project root
sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ),
)

from services.identity_service import IdentityService
from services.did_service import DIDService
from services.provenance_service import ProvenanceService
from services.compliance_service import ComplianceService
from services.credential_service import CredentialService
from services.delegation_service import DelegationService
from services.reputation_service import ReputationService

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

WIDTH = 80


def banner(step: int, title: str):
    """Print a step banner."""
    print()
    print("=" * WIDTH)
    print(f"  STEP {step}: {title}")
    print("=" * WIDTH)


def field(label: str, value, indent: int = 2):
    """Print a key-value pair with alignment."""
    pad = " " * indent
    print(f"{pad}{label:<24}: {value}")


def section_end():
    print("=" * WIDTH)


def pretty(obj, indent_level: int = 4):
    """Pretty-print a dict or list."""
    print(json.dumps(obj, indent=indent_level, default=str))


# ---------------------------------------------------------------------------
# Services
# ---------------------------------------------------------------------------

identity_svc = IdentityService()
did_svc = DIDService()
provenance_svc = ProvenanceService()
compliance_svc = ComplianceService()
credential_svc = CredentialService()
delegation_svc = DelegationService()
reputation_svc = ReputationService()

# Artifact collector for the final summary
artifacts = {}

print()
print("*" * WIDTH)
print("  ATTESTIX DEMO - Scenario 1: FinTech Advisory AI")
print("  Agent: WealthBot-Pro | Provider: FinanceAI Corp")
print("  Risk Level: HIGH (EU AI Act Annex III)")
print("*" * WIDTH)

# ============================================================================
# STEP 1: Create Agent Identity
# ============================================================================
banner(1, "Create Agent Identity")

identity = identity_svc.create_identity(
    display_name="WealthBot-Pro",
    source_protocol="mcp",
    capabilities=[
        "investment_advisory",
        "portfolio_optimization",
        "risk_assessment",
        "market_analysis",
    ],
    description="AI-powered wealth management advisor for retail investors",
    issuer_name="FinanceAI Corp",
)

agent_id = identity["agent_id"]
artifacts["agent_id"] = agent_id

field("Agent ID", agent_id)
field("Display Name", identity["display_name"])
field("Source Protocol", identity["source_protocol"])
field("Capabilities", ", ".join(identity["capabilities"]))
field("Issuer", identity["issuer"]["name"])
field("Issuer DID", identity["issuer"]["did"])
field("Signed", bool(identity.get("signature")))
field("Expires", identity["expires_at"])
section_end()

# ============================================================================
# STEP 2: Create DID:key
# ============================================================================
banner(2, "Create DID:key for the Agent")

did_result = did_svc.create_did_key()

agent_did = did_result["did"]
artifacts["agent_did"] = agent_did

field("DID", agent_did)
field("Keypair ID", did_result["keypair_id"])
field("Public Key (multibase)", did_result["public_key_multibase"][:40] + "...")
field("DID Document ID", did_result["did_document"]["id"])
section_end()

# ============================================================================
# STEP 3: Record Training Data (2 datasets)
# ============================================================================
banner(3, "Record Training Data Provenance")

print()
print("  [Dataset 1] Bloomberg Financial Markets Dataset")
print("  " + "-" * 50)

td1 = provenance_svc.record_training_data(
    agent_id=agent_id,
    dataset_name="Bloomberg Financial Markets Dataset",
    source_url="https://www.bloomberg.com/professional/dataset/",
    license="Proprietary - Bloomberg Enterprise License",
    data_categories=["market_data", "financial_indicators", "price_history"],
    contains_personal_data=False,
    data_governance_measures="Data quality checks, bias testing on sector representation, "
    "temporal validation of historical records",
)

artifacts["training_data_1"] = td1["entry_id"]
field("Entry ID", td1["entry_id"])
field("Dataset", td1["dataset_name"])
field("License", td1["license"])
field("Personal Data", td1["contains_personal_data"])
field("Governance", td1["data_governance_measures"][:60] + "...")

print()
print("  [Dataset 2] SEC EDGAR Filings")
print("  " + "-" * 50)

td2 = provenance_svc.record_training_data(
    agent_id=agent_id,
    dataset_name="SEC EDGAR Filings",
    source_url="https://www.sec.gov/edgar/",
    license="Public Domain - US Government",
    data_categories=["regulatory_filings", "10-K", "10-Q", "8-K"],
    contains_personal_data=False,
    data_governance_measures="Source verification against SEC EDGAR API, "
    "deduplication of amended filings",
)

artifacts["training_data_2"] = td2["entry_id"]
field("Entry ID", td2["entry_id"])
field("Dataset", td2["dataset_name"])
field("License", td2["license"])
field("Personal Data", td2["contains_personal_data"])
section_end()

# ============================================================================
# STEP 4: Record Model Lineage
# ============================================================================
banner(4, "Record Model Lineage")

lineage = provenance_svc.record_model_lineage(
    agent_id=agent_id,
    base_model="GPT-4-Turbo",
    base_model_provider="OpenAI",
    fine_tuning_method="LoRA fine-tuning on proprietary financial Q&A corpus",
    evaluation_metrics={
        "accuracy": 0.94,
        "f1_score": 0.91,
        "hallucination_rate": 0.02,
        "financial_advice_relevance": 0.96,
        "regulatory_compliance_score": 0.98,
    },
)

artifacts["model_lineage"] = lineage["entry_id"]

field("Entry ID", lineage["entry_id"])
field("Base Model", lineage["base_model"])
field("Provider", lineage["base_model_provider"])
field("Fine-tuning", lineage["fine_tuning_method"][:60] + "...")
print()
print("  Evaluation Metrics:")
for metric, value in lineage["evaluation_metrics"].items():
    field(metric, value, indent=4)
section_end()

# ============================================================================
# STEP 5: Create Compliance Profile (HIGH risk)
# ============================================================================
banner(5, "Create EU AI Act Compliance Profile (HIGH risk)")

profile = compliance_svc.create_compliance_profile(
    agent_id=agent_id,
    risk_category="high",
    provider_name="FinanceAI Corp",
    intended_purpose="Providing personalized investment advice and portfolio "
    "optimization for retail investors based on risk tolerance, "
    "financial goals, and market conditions",
    transparency_obligations="Users are informed they are interacting with an AI system. "
    "All investment recommendations include confidence scores and "
    "source citations. Limitations of AI advice are disclosed.",
    human_oversight_measures="Licensed financial advisor reviews all recommendations above "
    "50,000 EUR. Kill-switch available for compliance officers. "
    "Monthly audit by risk management team.",
    provider_address="123 FinTech Boulevard, Frankfurt, Germany 60311",
    authorised_representative="Dr. Maria Schmidt, Chief Compliance Officer",
)

artifacts["compliance_profile"] = profile["profile_id"]

field("Profile ID", profile["profile_id"])
field("Risk Category", profile["risk_category"])
field("Provider", profile["provider"]["name"])
field("Provider Address", profile["provider"]["address"])
field("Representative", profile["provider"]["authorised_representative"])
field("Intended Purpose", profile["ai_system"]["intended_purpose"][:60] + "...")
field("Assessment Done?", profile["conformity"]["assessment_completed"])
field("CE Marking?", profile["conformity"]["ce_marking_eligible"])
print()
print("  Required Obligations:")
for i, ob in enumerate(profile["required_obligations"], 1):
    print(f"    {i:2d}. {ob}")
section_end()

# ============================================================================
# STEP 6: Gap Analysis (before assessment)
# ============================================================================
banner(6, "Gap Analysis - What Is Missing?")

status_before = compliance_svc.get_compliance_status(agent_id)

field("Compliant?", status_before["compliant"])
field("Completion", f"{status_before['completion_pct']}%")
print()
print("  Completed:")
for item in status_before["completed"]:
    print(f"    [x] {item}")
print()
print("  Missing:")
for item in status_before["missing"]:
    print(f"    [ ] {item}")
section_end()

# ============================================================================
# STEP 7: Self-Assessment Attempt (MUST FAIL for high-risk)
# ============================================================================
banner(7, "Self-Assessment Attempt (Expected to FAIL)")

self_assess = compliance_svc.record_conformity_assessment(
    agent_id=agent_id,
    assessment_type="self",
    assessor_name="FinanceAI Corp Internal QA",
    result="pass",
    findings="All internal quality checks passed.",
    ce_marking_eligible=True,
)

if "error" in self_assess:
    print()
    print("  >>> BLOCKED (as expected for HIGH-risk systems) <<<")
    print()
    field("Error", self_assess["error"])
    print()
    print("  EU AI Act Article 43 requires third-party conformity")
    print("  assessment for high-risk AI systems. Self-assessment")
    print("  is not sufficient.")
else:
    print("  WARNING: Self-assessment was accepted (unexpected for high-risk)")
section_end()

# ============================================================================
# STEP 8: Third-Party Assessment by Deloitte Digital Assurance
# ============================================================================
banner(8, "Third-Party Conformity Assessment")

assessment = compliance_svc.record_conformity_assessment(
    agent_id=agent_id,
    assessment_type="third_party",
    assessor_name="Deloitte Digital Assurance",
    result="pass",
    findings="All high-risk obligations verified. Risk management system adequate. "
    "Data governance measures meet Article 10 requirements. Technical "
    "documentation is comprehensive. Logging and record-keeping systems "
    "are operational. Human oversight mechanisms verified.",
    ce_marking_eligible=True,
)

artifacts["assessment_id"] = assessment["assessment_id"]

field("Assessment ID", assessment["assessment_id"])
field("Type", assessment["assessment_type"])
field("Assessor", assessment["assessor_name"])
field("Result", assessment["result"])
field("CE Marking Eligible", assessment["ce_marking_eligible"])
field("Findings", assessment["findings"][:70] + "...")
section_end()

# ============================================================================
# STEP 9: Declaration of Conformity (Annex V)
# ============================================================================
banner(9, "Generate Declaration of Conformity (Annex V)")

declaration = compliance_svc.generate_declaration_of_conformity(agent_id)

artifacts["declaration_id"] = declaration["declaration_id"]

field("Declaration ID", declaration["declaration_id"])
field("Regulation", declaration["regulation_reference"])
print()
print("  Annex V Fields:")
annex = declaration["annex_v_fields"]
field("1. Provider", annex["1_provider_name"], indent=4)
field("1a. Address", annex["1a_provider_address"], indent=4)
field("2. Representative", annex["2_authorised_representative"], indent=4)
field("3. AI System", annex["3_ai_system_name"], indent=4)
field("3a. System ID", annex["3a_ai_system_id"], indent=4)
field("5. Risk Category", annex["5_risk_category"], indent=4)
field("6. Assessment ID", annex["6_conformity_assessment_id"], indent=4)
field("6a. Assessment Type", annex["6a_assessment_type"], indent=4)
field("6b. Assessor", annex["6b_assessor_name"], indent=4)
field("10. CE Marking", annex["10_ce_marking_eligible"], indent=4)
print()
print("  Sole Responsibility Statement:")
print(f"    {annex['11_sole_responsibility']}")
section_end()

# ============================================================================
# STEP 10: Verify Compliance Status (should be improved)
# ============================================================================
banner(10, "Verify Compliance Status (Post-Assessment)")

status_after = compliance_svc.get_compliance_status(agent_id)

field("Compliant?", status_after["compliant"])
field("Completion", f"{status_after['completion_pct']}%")
print()
print("  Completed:")
for item in status_after["completed"]:
    print(f"    [x] {item}")
if status_after["missing"]:
    print()
    print("  Still Missing:")
    for item in status_after["missing"]:
        print(f"    [ ] {item}")
section_end()

# ============================================================================
# STEP 11: Issue Custom Credential
# ============================================================================
banner(11, "Issue FinancialAdvisorLicenseCredential")

license_cred = credential_svc.issue_credential(
    subject_id=agent_id,
    credential_type="FinancialAdvisorLicenseCredential",
    issuer_name="FinanceAI Corp",
    claims={
        "license_number": "FAL-2026-DE-00847",
        "jurisdiction": "European Union",
        "regulator": "BaFin (Federal Financial Supervisory Authority)",
        "license_class": "Robo-Advisory (MiFID II compliant)",
        "max_portfolio_value": "500,000 EUR",
        "restrictions": "Retail investors only; no derivatives trading",
    },
    expiry_days=365,
)

cred_id = license_cred["id"]
artifacts["license_credential_id"] = cred_id

field("Credential ID", cred_id)
field("Type", license_cred["type"])
field("Issuer", license_cred["issuer"]["name"])
field("Issuer DID", license_cred["issuer"]["id"])
field("Subject", license_cred["credentialSubject"]["id"])
field("License Number", license_cred["credentialSubject"]["license_number"])
field("Jurisdiction", license_cred["credentialSubject"]["jurisdiction"])
field("Regulator", license_cred["credentialSubject"]["regulator"])
field("Proof Type", license_cred["proof"]["type"])
field("Expires", license_cred["expirationDate"])
section_end()

# ============================================================================
# STEP 12: Verify the Credential
# ============================================================================
banner(12, "Verify the Credential")

verification = credential_svc.verify_credential(cred_id)

field("Credential ID", verification["credential_id"])
field("Valid", verification["valid"])
field("Type", verification["type"])
field("Subject", verification["subject"])
print()
print("  Checks:")
for check, result in verification["checks"].items():
    symbol = "[x]" if result else "[ ]"
    print(f"    {symbol} {check}: {result}")
section_end()

# ============================================================================
# STEP 13: Create Verifiable Presentation
# ============================================================================
banner(13, "Create Verifiable Presentation")

# Gather all credentials for this agent (compliance + license)
all_creds = credential_svc.list_credentials(agent_id=agent_id)
cred_ids = [c["id"] for c in all_creds]

print(f"  Bundling {len(cred_ids)} credential(s) into a Verifiable Presentation:")
for i, cid in enumerate(cred_ids, 1):
    cred = credential_svc.get_credential(cid)
    cred_type = cred["type"][-1] if cred else "Unknown"
    print(f"    {i}. {cred_type} ({cid[:30]}...)")

vp = credential_svc.create_verifiable_presentation(
    agent_id=agent_id,
    credential_ids=cred_ids,
    audience_did="did:web:regulator.bafin.de",
    challenge="audit-request-2026-03",
)

artifacts["vp_id"] = vp["id"]

print()
field("VP ID", vp["id"])
field("Holder", vp["holder"])
field("Audience (domain)", vp.get("domain", "N/A"))
field("Challenge", vp.get("challenge", "N/A"))
field("Credentials Included", len(vp["verifiableCredential"]))
field("Proof Type", vp["proof"]["type"])
field("Proof Purpose", vp["proof"]["proofPurpose"])
section_end()

# ============================================================================
# STEP 14: Create Delegation Chain
# ============================================================================
banner(14, "Create Delegation (WealthBot-Pro -> AnalysisBot)")

# First, create the junior agent identity
analysis_bot = identity_svc.create_identity(
    display_name="AnalysisBot",
    source_protocol="mcp",
    capabilities=["market_analysis", "portfolio_read"],
    description="Junior analysis agent for portfolio data retrieval",
    issuer_name="FinanceAI Corp",
)
analysis_bot_id = analysis_bot["agent_id"]
artifacts["analysis_bot_id"] = analysis_bot_id

print(f"  Created junior agent: {analysis_bot['display_name']} ({analysis_bot_id})")
print()

delegation_result = delegation_svc.create_delegation(
    issuer_agent_id=agent_id,
    audience_agent_id=analysis_bot_id,
    capabilities=["portfolio_read"],
    expiry_hours=4,
)

delegation = delegation_result["delegation"]
token = delegation_result["token"]
artifacts["delegation_jti"] = delegation["jti"]

field("JTI (Delegation ID)", delegation["jti"])
field("Issuer (Delegator)", delegation["issuer"])
field("Audience (Delegate)", delegation["audience"])
field("Capabilities", delegation["capabilities"])
field("Expires At", delegation["expires_at"])
field("Token (first 40)", token[:40] + "...")

print()
print("  Verifying the delegation token...")
verify_deleg = delegation_svc.verify_delegation(token)
field("Valid", verify_deleg["valid"])
field("Delegator", verify_deleg["delegator"])
field("Audience", verify_deleg["audience"])
field("Capabilities", verify_deleg["capabilities"])
field("Expired", verify_deleg["expired"])
section_end()

# ============================================================================
# STEP 15: Record Interactions for Reputation
# ============================================================================
banner(15, "Record 5 Interactions for Reputation Scoring")

interactions = [
    {
        "counterparty_id": "attestix:client_alice_01",
        "outcome": "success",
        "category": "task",
        "details": "Portfolio rebalancing recommendation accepted by client",
    },
    {
        "counterparty_id": "attestix:client_bob_02",
        "outcome": "success",
        "category": "task",
        "details": "Risk assessment completed for retirement portfolio",
    },
    {
        "counterparty_id": "attestix:client_carol_03",
        "outcome": "success",
        "category": "task",
        "details": "Market analysis report delivered on time",
    },
    {
        "counterparty_id": "attestix:client_dave_04",
        "outcome": "success",
        "category": "task",
        "details": "Investment advisory session completed successfully",
    },
    {
        "counterparty_id": "attestix:client_eve_05",
        "outcome": "partial",
        "category": "task",
        "details": "Portfolio optimization limited by missing client risk profile data",
    },
]

for i, inter in enumerate(interactions, 1):
    result = reputation_svc.record_interaction(
        agent_id=agent_id,
        **inter,
    )
    outcome_display = inter["outcome"].upper()
    score_display = result["updated_score"]["trust_score"]
    print(f"  [{i}] {outcome_display:8s} | Score: {score_display:.4f} | {inter['details'][:50]}")

section_end()

# ============================================================================
# STEP 16: Get Reputation Score
# ============================================================================
banner(16, "Get Reputation Score")

reputation = reputation_svc.get_reputation(agent_id)

field("Agent ID", reputation["agent_id"])
field("Trust Score", reputation["trust_score"])
field("Total Interactions", reputation["total_interactions"])
field("Last Interaction", reputation["last_interaction"])
print()
print("  Category Breakdown:")
for cat, breakdown in reputation["category_breakdown"].items():
    print(f"    {cat}:")
    field("Success", breakdown["success"], indent=6)
    field("Partial", breakdown["partial"], indent=6)
    field("Failure", breakdown["failure"], indent=6)
    field("Timeout", breakdown["timeout"], indent=6)
    field("Total", breakdown["total"], indent=6)
section_end()

# ============================================================================
# STEP 17: Log Audit Entries
# ============================================================================
banner(17, "Log 3 Audit Trail Entries")

audit_entries_data = [
    {
        "action_type": "inference",
        "input_summary": "Client requested portfolio allocation for 100K EUR "
        "with moderate risk tolerance",
        "output_summary": "Recommended 60/30/10 stocks/bonds/alternatives split",
        "decision_rationale": "Based on Monte Carlo simulation with 10,000 scenarios "
        "and historical data from 2000 to 2026",
    },
    {
        "action_type": "external_call",
        "input_summary": "Real-time market data fetch for DAX, S&P 500, FTSE 100",
        "output_summary": "Received current prices and 24h change percentages",
        "decision_rationale": "Required for up-to-date portfolio valuation before "
        "rebalancing recommendation",
    },
    {
        "action_type": "data_access",
        "input_summary": "Query client portfolio positions and transaction history",
        "output_summary": "Generated quarterly performance report (Q4 2025)",
        "decision_rationale": "Scheduled quarterly report generation per client agreement",
    },
]

for i, entry in enumerate(audit_entries_data, 1):
    result = provenance_svc.log_action(agent_id=agent_id, **entry)
    print(f"  [{i}] {entry['action_type']:15s} | Log ID: {result['log_id']}")
    print(f"      Chain Hash: {result['chain_hash'][:40]}...")

artifacts["audit_log_count"] = len(audit_entries_data)
section_end()

# ============================================================================
# STEP 18: Query Audit Trail
# ============================================================================
banner(18, "Query Audit Trail")

audit_trail = provenance_svc.get_audit_trail(agent_id=agent_id)

field("Total Entries", len(audit_trail))
print()
for i, entry in enumerate(audit_trail, 1):
    print(f"  Entry {i}:")
    field("Log ID", entry["log_id"], indent=4)
    field("Action Type", entry["action_type"], indent=4)
    field("Timestamp", entry["timestamp"], indent=4)
    field("Input", entry["input_summary"][:60] + "...", indent=4)
    field("Output", entry["output_summary"][:60] + "...", indent=4)
    field("Chain Hash", entry["chain_hash"][:40] + "...", indent=4)
    has_sig = bool(entry.get("signature"))
    field("Signed", has_sig, indent=4)
    print()

section_end()

# ============================================================================
# SUMMARY
# ============================================================================
print()
print("*" * WIDTH)
print("  DEMO COMPLETE - Summary of All Artifacts Created")
print("*" * WIDTH)
print()
field("Agent ID", artifacts["agent_id"])
field("Agent DID", artifacts["agent_did"])
field("Training Data 1", artifacts["training_data_1"])
field("Training Data 2", artifacts["training_data_2"])
field("Model Lineage", artifacts["model_lineage"])
field("Compliance Profile", artifacts["compliance_profile"])
field("Assessment ID", artifacts["assessment_id"])
field("Declaration ID", artifacts["declaration_id"])
field("License Credential", artifacts["license_credential_id"])
field("Verifiable Pres.", artifacts["vp_id"])
field("Analysis Bot ID", artifacts["analysis_bot_id"])
field("Delegation JTI", artifacts["delegation_jti"])
field("Audit Log Entries", artifacts["audit_log_count"])
field("Reputation Score", reputation["trust_score"])
print()
print(f"  Compliance: {status_after['completion_pct']}% "
      f"({len(status_after['completed'])} of "
      f"{len(status_after['completed']) + len(status_after['missing'])} obligations met)")
print()
if status_after["missing"]:
    print("  Remaining obligations (Article 9-15 deep checks):")
    for item in status_after["missing"]:
        print(f"    [ ] {item}")
    print()
print("  All cryptographic signatures: Ed25519 (RFC 8032)")
print("  All credentials: W3C Verifiable Credentials 1.1")
print("  Delegation tokens: UCAN v0.9.0 (EdDSA/JWT)")
print("  Audit chain: SHA-256 hash-linked (RFC 6962 style)")
print()
print("*" * WIDTH)
