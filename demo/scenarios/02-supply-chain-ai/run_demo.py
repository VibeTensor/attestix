"""Scenario 2: Supply Chain AI - LIMITED-RISK under EU AI Act

Demonstrates a multi-agent supply chain orchestration system where:
- LogiOptimize is the main orchestrator (demand forecasting, route optimization, inventory)
- RegionEU-Agent handles European regional operations
- RegionASIA-Agent handles Asian regional operations

KEY DIFFERENTIATOR: Limited-risk systems can perform SELF-ASSESSMENT for conformity,
unlike high-risk systems (Scenario 1) which require third-party assessment.

Usage (from Attestix root directory):
    python demo/scenarios/02-supply-chain-ai/run_demo.py
"""

import json
import os
import sys
import time

# Ensure imports resolve from the Attestix root directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from services.identity_service import IdentityService
from services.compliance_service import ComplianceService
from services.provenance_service import ProvenanceService
from services.credential_service import CredentialService
from services.delegation_service import DelegationService
from services.reputation_service import ReputationService
from services.did_service import DIDService


def header(step_num, title, subtitle=""):
    """Print a formatted step header."""
    print()
    print("=" * 80)
    print(f"  STEP {step_num}: {title}")
    if subtitle:
        print(f"  {subtitle}")
    print("=" * 80)


def sub(label, value):
    """Print a labeled value with indentation."""
    print(f"  {label}: {value}")


def divider():
    print("-" * 80)


def main():
    print()
    print("=" * 80)
    print("  ATTESTIX DEMO SCENARIO 2: Supply Chain AI")
    print("  EU AI Act Risk Category: LIMITED-RISK (transparency obligations)")
    print("  Multi-agent supply chain orchestration")
    print("=" * 80)
    print()

    # Initialize services
    identity_svc = IdentityService()
    compliance_svc = ComplianceService()
    provenance_svc = ProvenanceService()
    credential_svc = CredentialService()
    delegation_svc = DelegationService()
    reputation_svc = ReputationService()
    did_svc = DIDService()

    # =========================================================================
    # STEP 1: Create Multi-Agent Supply Chain
    # =========================================================================
    header(1, "Create Multi-Agent Supply Chain")

    agent1 = identity_svc.create_identity(
        display_name="LogiOptimize",
        source_protocol="manual",
        capabilities=["demand_forecasting", "route_optimization", "inventory_management"],
        description="Main supply chain orchestrator for global logistics optimization",
        issuer_name="GlobalSupply Ltd",
    )
    agent1_id = agent1["agent_id"]
    sub("Agent 1 (orchestrator)", f"LogiOptimize - {agent1_id}")

    agent2 = identity_svc.create_identity(
        display_name="RegionEU-Agent",
        source_protocol="manual",
        capabilities=["inventory_read", "warehouse_status", "eu_customs_check"],
        description="European regional operations agent for warehouse and customs management",
        issuer_name="GlobalSupply Ltd",
    )
    agent2_id = agent2["agent_id"]
    sub("Agent 2 (EU region)", f"RegionEU-Agent - {agent2_id}")

    agent3 = identity_svc.create_identity(
        display_name="RegionASIA-Agent",
        source_protocol="manual",
        capabilities=["inventory_read", "shipping_status", "asia_customs_check"],
        description="Asian regional operations agent for shipping and customs management",
        issuer_name="GlobalSupply Ltd",
    )
    agent3_id = agent3["agent_id"]
    sub("Agent 3 (Asia region)", f"RegionASIA-Agent - {agent3_id}")

    divider()
    print("  All 3 agents created under GlobalSupply Ltd")

    # =========================================================================
    # STEP 2: Create DID:key for Orchestrator
    # =========================================================================
    header(2, "Create DID:key for LogiOptimize")

    did_result = did_svc.create_did_key()
    sub("DID", did_result["did"][:60] + "...")
    sub("Keypair ID", did_result["keypair_id"])
    sub("Public Key", did_result["public_key_multibase"][:40] + "...")

    # =========================================================================
    # STEP 3: Record Training Data Provenance
    # =========================================================================
    header(3, "Record Training Data Provenance (Article 10)")

    ds1 = provenance_svc.record_training_data(
        agent_id=agent1_id,
        dataset_name="Global Shipping Routes Dataset 2020-2025",
        source_url="https://data.globalsupply.example/shipping-routes",
        license="CC-BY-4.0",
        data_categories=["shipping_routes", "port_data", "transit_times"],
        contains_personal_data=False,
        data_governance_measures="Aggregated from public maritime databases. No personal data included.",
    )
    sub("Dataset 1", f"{ds1['dataset_name']} ({ds1['entry_id']})")
    sub("License", ds1["license"])
    sub("Personal Data", ds1["contains_personal_data"])

    print()

    ds2 = provenance_svc.record_training_data(
        agent_id=agent1_id,
        dataset_name="Warehouse Inventory Records",
        source_url="https://internal.globalsupply.example/warehouse-data",
        license="proprietary",
        data_categories=["inventory_levels", "stock_movements", "demand_patterns"],
        contains_personal_data=False,
        data_governance_measures="Internal proprietary data. Access-controlled. No personal data.",
    )
    sub("Dataset 2", f"{ds2['dataset_name']} ({ds2['entry_id']})")
    sub("License", ds2["license"])
    sub("Personal Data", ds2["contains_personal_data"])

    # =========================================================================
    # STEP 4: Record Model Lineage
    # =========================================================================
    header(4, "Record Model Lineage (Article 11)")

    lineage = provenance_svc.record_model_lineage(
        agent_id=agent1_id,
        base_model="gpt-4-turbo",
        base_model_provider="OpenAI",
        fine_tuning_method="Supervised fine-tuning on logistics optimization tasks with domain expert feedback",
        evaluation_metrics={
            "demand_forecast_mape": 0.08,
            "route_optimization_savings": 0.15,
            "inventory_accuracy": 0.96,
            "latency_p99_ms": 450,
        },
    )
    sub("Base Model", f"{lineage['base_model']} by {lineage['base_model_provider']}")
    sub("Fine-tuning", lineage["fine_tuning_method"][:60] + "...")
    sub("Entry ID", lineage["entry_id"])

    # =========================================================================
    # STEP 5: Create Compliance Profile (Limited Risk)
    # =========================================================================
    header(5, "Create Compliance Profile - LIMITED RISK")

    profile = compliance_svc.create_compliance_profile(
        agent_id=agent1_id,
        risk_category="limited",
        provider_name="GlobalSupply Ltd",
        intended_purpose=(
            "AI-powered supply chain optimization including demand forecasting, "
            "route planning, and inventory management for global logistics operations."
        ),
        transparency_obligations=(
            "System discloses AI-generated recommendations to human operators. "
            "All forecasts include confidence intervals. Route suggestions are "
            "clearly labeled as AI-generated."
        ),
    )
    sub("Profile ID", profile["profile_id"])
    sub("Risk Category", profile["risk_category"])
    sub("Required Obligations", ", ".join(profile.get("required_obligations", [])))

    # =========================================================================
    # STEP 6: Gap Analysis
    # =========================================================================
    header(6, "Gap Analysis - Compliance Status")

    status = compliance_svc.get_compliance_status(agent1_id)
    sub("Compliant", status["compliant"])
    sub("Completion", f"{status['completion_pct']}%")
    print()
    print("  Completed:")
    for item in status.get("completed", []):
        print(f"    [x] {item}")
    print()
    print("  Missing:")
    for item in status.get("missing", []):
        print(f"    [ ] {item}")

    # =========================================================================
    # STEP 7: Self-Assessment (KEY DEMO MOMENT)
    # =========================================================================
    header(
        7,
        "Conformity Self-Assessment (KEY DEMO MOMENT)",
        "Limited-risk allows SELF-ASSESSMENT - unlike high-risk in Scenario 1!",
    )

    print()
    print("  *** THIS IS THE KEY DIFFERENTIATOR ***")
    print("  In Scenario 1 (FinTech high-risk), self-assessment is BLOCKED.")
    print("  For limited-risk systems, self-assessment is ALLOWED per Article 43.")
    print()

    assessment = compliance_svc.record_conformity_assessment(
        agent_id=agent1_id,
        assessment_type="self",
        assessor_name="GlobalSupply Ltd Internal QA",
        result="pass",
        findings=(
            "System meets transparency requirements. All AI-generated outputs "
            "are clearly labeled. Confidence intervals provided on forecasts. "
            "Human operators have full override capability."
        ),
        ce_marking_eligible=True,
    )

    if "error" in assessment:
        print(f"  UNEXPECTED ERROR: {assessment['error']}")
        print("  Self-assessment should succeed for limited-risk systems!")
    else:
        print("  *** SELF-ASSESSMENT SUCCEEDED! ***")
        print()
        sub("Assessment ID", assessment["assessment_id"])
        sub("Type", assessment["assessment_type"])
        sub("Assessor", assessment["assessor_name"])
        sub("Result", assessment["result"])
        sub("CE Marking Eligible", assessment["ce_marking_eligible"])
        print()
        print("  Unlike high-risk systems, limited-risk AI does not need")
        print("  third-party notified body assessment. Internal QA suffices.")

    # =========================================================================
    # STEP 8: Generate Declaration of Conformity
    # =========================================================================
    header(8, "Generate Declaration of Conformity (Annex V)")

    declaration = compliance_svc.generate_declaration_of_conformity(agent1_id)

    if "error" in declaration:
        print(f"  Error: {declaration['error']}")
    else:
        sub("Declaration ID", declaration["declaration_id"])
        sub("Regulation", declaration["regulation_reference"])
        annex = declaration["annex_v_fields"]
        sub("Provider", annex["1_provider_name"])
        sub("AI System", annex["3_ai_system_name"])
        sub("Risk Category", annex["5_risk_category"])
        sub("Assessment Type", annex["6a_assessment_type"])
        sub("CE Marking", annex["10_ce_marking_eligible"])
        print()
        print("  Declaration of conformity issued with self-assessment.")
        print("  High-risk systems would require third-party assessment here.")

    # =========================================================================
    # STEP 9: Delegation Chain
    # =========================================================================
    header(
        9,
        "Create Delegation Chain",
        "LogiOptimize -> RegionEU-Agent -> RegionASIA-Agent",
    )

    # LogiOptimize delegates inventory_read to RegionEU-Agent (8 hours)
    print()
    print("  Delegation 1: LogiOptimize -> RegionEU-Agent")
    deleg1 = delegation_svc.create_delegation(
        issuer_agent_id=agent1_id,
        audience_agent_id=agent2_id,
        capabilities=["inventory_read"],
        expiry_hours=8,
    )
    if "error" in deleg1:
        print(f"  Error: {deleg1['error']}")
    else:
        sub("Token (truncated)", deleg1["token"][:50] + "...")
        sub("Capabilities", deleg1["delegation"]["capabilities"])
        sub("Expires", deleg1["delegation"]["expires_at"])

    print()

    # RegionEU-Agent chain-delegates subset to RegionASIA-Agent (4 hours)
    print("  Delegation 2: RegionEU-Agent -> RegionASIA-Agent (chained)")
    deleg2 = delegation_svc.create_delegation(
        issuer_agent_id=agent2_id,
        audience_agent_id=agent3_id,
        capabilities=["inventory_read"],
        expiry_hours=4,
        parent_token=deleg1["token"],
    )
    if "error" in deleg2:
        print(f"  Error: {deleg2['error']}")
    else:
        sub("Token (truncated)", deleg2["token"][:50] + "...")
        sub("Capabilities", deleg2["delegation"]["capabilities"])
        sub("Expires", deleg2["delegation"]["expires_at"])
        sub("Parent chain", "1 parent token (LogiOptimize -> RegionEU)")

    # =========================================================================
    # STEP 10: Verify Delegations
    # =========================================================================
    header(10, "Verify Delegations")

    print("  Verifying Delegation 1 (LogiOptimize -> RegionEU-Agent):")
    v1 = delegation_svc.verify_delegation(deleg1["token"])
    sub("Valid", v1["valid"])
    sub("Delegator", v1.get("delegator", "N/A"))
    sub("Audience", v1.get("audience", "N/A"))
    sub("Capabilities", v1.get("capabilities", []))

    print()

    print("  Verifying Delegation 2 (RegionEU -> RegionASIA, chained):")
    v2 = delegation_svc.verify_delegation(deleg2["token"])
    sub("Valid", v2["valid"])
    sub("Delegator", v2.get("delegator", "N/A"))
    sub("Audience", v2.get("audience", "N/A"))
    sub("Capabilities", v2.get("capabilities", []))
    sub("Proof Chain Length", len(v2.get("proof_chain", [])))

    # =========================================================================
    # STEP 11: Record Interactions
    # =========================================================================
    header(11, "Record Interactions for All Agents")

    interactions = [
        # LogiOptimize interactions (mostly successful)
        (agent1_id, agent2_id, "success", "task", "Route optimization for EU shipment batch"),
        (agent1_id, agent2_id, "success", "delegation", "Delegated inventory access to EU agent"),
        (agent1_id, agent3_id, "success", "task", "Demand forecast for Asia region Q2"),
        (agent1_id, agent3_id, "partial", "task", "Asia route optimization - partial due to data lag"),
        # RegionEU-Agent interactions (good performance)
        (agent2_id, agent1_id, "success", "task", "EU warehouse inventory sync completed"),
        (agent2_id, agent1_id, "success", "task", "EU customs clearance check passed"),
        (agent2_id, agent3_id, "success", "delegation", "Chain-delegated inventory read to Asia"),
        # RegionASIA-Agent interactions (some failures)
        (agent3_id, agent1_id, "success", "task", "Asia shipping status report generated"),
        (agent3_id, agent1_id, "failure", "task", "Asia customs API timeout - service unavailable"),
        (agent3_id, agent2_id, "partial", "task", "Cross-region inventory reconciliation incomplete"),
    ]

    for agent_id, counterparty, outcome, category, details in interactions:
        result = reputation_svc.record_interaction(
            agent_id=agent_id,
            counterparty_id=counterparty,
            outcome=outcome,
            category=category,
            details=details,
        )
        agent_name = {agent1_id: "LogiOptimize", agent2_id: "RegionEU", agent3_id: "RegionASIA"}[agent_id]
        outcome_icon = {"success": "[OK]", "partial": "[~~]", "failure": "[!!]"}[outcome]
        print(f"  {outcome_icon} {agent_name}: {details[:55]}")

    # =========================================================================
    # STEP 12: Compare Reputation Scores
    # =========================================================================
    header(12, "Reputation Scores - All Agents Compared")

    scores = {}
    for aid, name in [(agent1_id, "LogiOptimize"), (agent2_id, "RegionEU-Agent"), (agent3_id, "RegionASIA-Agent")]:
        rep = reputation_svc.get_reputation(aid)
        scores[name] = rep
        sub(f"{name} Trust Score", f"{rep.get('trust_score', 'N/A')}")
        sub(f"{name} Total Interactions", rep.get("total_interactions", 0))
        breakdown = rep.get("category_breakdown", {})
        for cat, stats in breakdown.items():
            print(f"    {cat}: {stats['success']}s / {stats.get('partial', 0)}p / {stats['failure']}f")
        print()

    # =========================================================================
    # STEP 13: Issue Compliance Credentials
    # =========================================================================
    header(13, "Issue Compliance Credentials for All Agents")

    cred_ids = {}
    for aid, name in [(agent1_id, "LogiOptimize"), (agent2_id, "RegionEU-Agent"), (agent3_id, "RegionASIA-Agent")]:
        cred = credential_svc.issue_credential(
            subject_id=aid,
            credential_type="TransparencyObligationCredential",
            issuer_name="GlobalSupply Ltd",
            claims={
                "transparency_status": "compliant",
                "risk_category": "limited",
                "disclosure_method": "AI-labeled outputs with confidence intervals",
                "agent_role": name,
            },
            expiry_days=365,
        )
        cred_ids[name] = cred["id"]
        sub(f"{name} Credential ID", cred["id"])

    print()
    print("  Verifying all credentials...")
    for name, cid in cred_ids.items():
        verification = credential_svc.verify_credential(cid)
        print(f"    {name}: valid={verification.get('valid')}")

    # =========================================================================
    # STEP 14: Audit Trail Logging
    # =========================================================================
    header(14, "Audit Trail Logging for Orchestrator")

    audit_entries = [
        {
            "action_type": "inference",
            "input_summary": "Q2 demand data for 12 EU warehouses",
            "output_summary": "Demand forecast with 92% confidence, recommended stock increases for 3 warehouses",
            "decision_rationale": "Historical pattern matching plus seasonal adjustment",
        },
        {
            "action_type": "delegation",
            "input_summary": "Delegation request from RegionEU-Agent for inventory_read",
            "output_summary": "Delegation token issued with 8-hour expiry",
            "decision_rationale": "Agent verified, capability within allowed scope",
        },
        {
            "action_type": "external_call",
            "input_summary": "API call to GlobalShipping rate service",
            "output_summary": "Retrieved 47 shipping rate quotes for Asia-EU routes",
            "decision_rationale": "Rate comparison needed for route optimization step",
        },
        {
            "action_type": "data_access",
            "input_summary": "Read warehouse inventory levels for Frankfurt, Rotterdam, Mumbai",
            "output_summary": "Retrieved current stock levels for 3 facilities, 1,247 SKUs total",
            "decision_rationale": "Inventory data needed for demand-supply gap analysis",
        },
    ]

    for entry in audit_entries:
        result = provenance_svc.log_action(agent_id=agent1_id, **entry)
        sub(f"[{entry['action_type']}]", f"{result['log_id']} - {entry['input_summary'][:50]}")

    # =========================================================================
    # STEP 15: Query Audit Trail
    # =========================================================================
    header(15, "Query Audit Trail")

    trail = provenance_svc.get_audit_trail(agent_id=agent1_id, limit=10)
    sub("Total audit entries", len(trail))
    print()
    for entry in trail:
        print(f"    [{entry['action_type']:15s}] {entry['log_id']}")
        print(f"      Input:     {entry['input_summary'][:60]}")
        print(f"      Output:    {entry['output_summary'][:60]}")
        print(f"      Rationale: {entry['decision_rationale'][:60]}")
        print(f"      Chain:     prev={entry['prev_hash'][:16]}... this={entry['chain_hash'][:16]}...")
        print()

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print()
    print("=" * 80)
    print("  SCENARIO 2 SUMMARY: Supply Chain AI (Limited-Risk)")
    print("=" * 80)
    print()

    # Reputation comparison table
    print("  Agent Reputation Comparison:")
    print("  " + "-" * 70)
    print(f"  {'Agent':<22s} {'Trust Score':>12s} {'Interactions':>14s} {'Success Rate':>14s}")
    print("  " + "-" * 70)

    for aid, name in [(agent1_id, "LogiOptimize"), (agent2_id, "RegionEU-Agent"), (agent3_id, "RegionASIA-Agent")]:
        rep = reputation_svc.get_reputation(aid)
        trust = rep.get("trust_score", 0)
        total = rep.get("total_interactions", 0)
        breakdown = rep.get("category_breakdown", {})
        successes = sum(cat.get("success", 0) for cat in breakdown.values())
        rate = f"{(successes / total * 100):.0f}%" if total > 0 else "N/A"
        print(f"  {name:<22s} {trust:>12.4f} {total:>14d} {rate:>14s}")

    print("  " + "-" * 70)
    print()

    # Key takeaways
    print("  Key Takeaways:")
    print("  1. Limited-risk AI systems have transparency obligations only")
    print("  2. Self-assessment is ALLOWED (unlike high-risk in Scenario 1)")
    print("  3. Multi-agent delegation chains work across regional boundaries")
    print("  4. Each agent maintains independent reputation scores")
    print("  5. Tamper-evident audit trails use SHA-256 hash chains")
    print("  6. All artifacts are cryptographically signed with Ed25519")
    print()

    # Compliance status recap
    final_status = compliance_svc.get_compliance_status(agent1_id)
    print(f"  LogiOptimize Compliance: {final_status['completion_pct']}% complete")
    print(f"  Fully Compliant: {final_status['compliant']}")
    if final_status.get("missing"):
        print(f"  Remaining items: {', '.join(final_status['missing'])}")
    print()
    print("=" * 80)
    print("  Demo complete. All data stored in Attestix root JSON files.")
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
