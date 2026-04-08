"""OpenAI Agents SDK + Attestix Integration Example

Shows how to add EU AI Act compliance to OpenAI agents using
Attestix MCP tools for identity, audit trails, and credentials.

This script simulates the OpenAI Agents SDK pattern using plain Python
so it runs without the openai package installed. The key design pattern
demonstrated here is the "compliance gate" - an agent that checks its
own compliance status before executing any task and refuses to proceed
if it is not compliant.

Workflow:
  1. Agent bootstraps its own identity (UAIT with DID)
  2. Agent registers its compliance profile (EU AI Act)
  3. Agent records training data provenance and model lineage
  4. Agent undergoes conformity assessment
  5. Agent checks compliance status before each task (compliance gate)
  6. Agent logs every action to the tamper-evident audit trail
  7. Agent issues and verifies a credential as proof of compliance
  8. Agent demonstrates the gate blocking a non-compliant peer

Run: python integrations/examples/openai_agents_compliance.py
"""

import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional

# Allow running from the repo root or the integrations/examples/ directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from services.identity_service import IdentityService
from services.compliance_service import ComplianceService
from services.provenance_service import ProvenanceService
from services.credential_service import CredentialService
from services.reputation_service import ReputationService


# ---------------------------------------------------------------------------
# Simulated OpenAI Agents SDK primitives
# ---------------------------------------------------------------------------
# These classes mirror the structure of the OpenAI Agents SDK without
# requiring the actual package. In a real integration you would import
# from openai.agents and register Attestix tools via MCP.

@dataclass
class ToolResult:
    """Simulates an Agents SDK tool call result."""
    tool_name: str
    output: dict


@dataclass
class AgentTool:
    """Simulates an Agents SDK tool definition."""
    name: str
    description: str
    handler: Callable


@dataclass
class Agent:
    """Simulates an OpenAI Agent with registered tools.

    In production, you would use:
        from openai import Agent
        agent = Agent(name=..., tools=[...], model="gpt-4o")

    The agent here follows the same pattern but calls tools directly.
    """
    name: str
    instructions: str
    tools: List[AgentTool] = field(default_factory=list)
    agent_id: Optional[str] = None
    compliant: bool = False

    def call_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """Find and call a registered tool by name."""
        for tool in self.tools:
            if tool.name == tool_name:
                result = tool.handler(**kwargs)
                return ToolResult(tool_name=tool_name, output=result)
        return ToolResult(tool_name=tool_name, output={"error": f"Tool '{tool_name}' not found"})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

DIVIDER = "=" * 64

def banner(title: str):
    """Print a section banner."""
    print(f"\n{DIVIDER}")
    print(f"  {title}")
    print(DIVIDER)


def pp(obj: dict, indent: int = 2):
    """Pretty-print a dict as indented JSON."""
    print(json.dumps(obj, indent=indent, default=str))


def ok(result: dict, label: str = "Result"):
    """Assert no error and print a compact summary."""
    if "error" in result:
        print(f"  [FAIL] {label}: {result['error']}")
        return False
    print(f"  [OK]   {label}")
    return True


# ---------------------------------------------------------------------------
# Compliance gate - the core pattern
# ---------------------------------------------------------------------------

def compliance_gate(agent: Agent, compliance_svc: ComplianceService) -> bool:
    """Check whether the agent is allowed to proceed.

    This is the central pattern: before every task the agent queries its
    own compliance status. If it is not compliant, it refuses to execute.
    The gate is deterministic and auditable.
    """
    if not agent.agent_id:
        print("  [GATE] BLOCKED - agent has no identity yet")
        return False

    status = compliance_svc.get_compliance_status(agent.agent_id)
    if "error" in status:
        print(f"  [GATE] BLOCKED - {status['error']}")
        return False

    if not status.get("compliant"):
        missing = status.get("missing", [])
        pct = status.get("completion_pct", 0)
        print(f"  [GATE] BLOCKED - compliance at {pct}%, missing: {missing}")
        return False

    print(f"  [GATE] PASSED - agent is fully compliant ({status['completion_pct']}%)")
    agent.compliant = True
    return True


# ---------------------------------------------------------------------------
# Main workflow
# ---------------------------------------------------------------------------

def main():
    # Initialize Attestix services (these are the MCP tool backends)
    identity_svc = IdentityService()
    compliance_svc = ComplianceService()
    provenance_svc = ProvenanceService()
    credential_svc = CredentialService()
    reputation_svc = ReputationService()

    # Build tool list (mirrors MCP tool registration in the Agents SDK)
    tools = [
        AgentTool("create_agent_identity", "Create a UAIT identity", identity_svc.create_identity),
        AgentTool("verify_identity", "Verify a UAIT", identity_svc.verify_identity),
        AgentTool("create_compliance_profile", "Create EU AI Act profile", compliance_svc.create_compliance_profile),
        AgentTool("get_compliance_status", "Check compliance status", compliance_svc.get_compliance_status),
        AgentTool("record_conformity_assessment", "Record Article 43 assessment", compliance_svc.record_conformity_assessment),
        AgentTool("generate_declaration", "Generate Annex V declaration", compliance_svc.generate_declaration_of_conformity),
        AgentTool("record_training_data", "Record Article 10 provenance", provenance_svc.record_training_data),
        AgentTool("record_model_lineage", "Record Article 11 lineage", provenance_svc.record_model_lineage),
        AgentTool("log_action", "Log an action to the audit trail", provenance_svc.log_action),
        AgentTool("get_audit_trail", "Query the audit trail", provenance_svc.get_audit_trail),
        AgentTool("issue_credential", "Issue a W3C Verifiable Credential", credential_svc.issue_credential),
        AgentTool("verify_credential", "Verify a W3C VC", credential_svc.verify_credential),
        AgentTool("record_interaction", "Record a reputation event", reputation_svc.record_interaction),
    ]

    # Create the agent
    agent = Agent(
        name="ComplianceAnalyst",
        instructions=(
            "You are a financial compliance analyst agent. Before executing "
            "any task, you MUST check your compliance status via the compliance "
            "gate. If you are not compliant, you must refuse the task."
        ),
        tools=tools,
    )

    print(f"\nAgent: {agent.name}")
    print(f"Tools: {len(agent.tools)} Attestix MCP tools registered")

    # ------------------------------------------------------------------
    # Phase 1: Agent bootstraps its own identity
    # ------------------------------------------------------------------
    banner("Phase 1: Agent Creates Its Own Identity")

    result = agent.call_tool(
        "create_agent_identity",
        display_name="ComplianceAnalyst",
        source_protocol="openai_agents_sdk",
        capabilities=["financial_analysis", "compliance_checking", "report_generation"],
        description="Autonomous compliance analyst for EU AI Act regulated financial services",
        issuer_name="VibeTensor Inc.",
        expiry_days=365,
    )
    assert "error" not in result.output, f"Identity creation failed: {result.output}"
    agent.agent_id = result.output["agent_id"]

    print(f"  Agent ID:   {agent.agent_id}")
    print(f"  DID:        {result.output['issuer']['did']}")
    print(f"  Protocol:   {result.output['source_protocol']}")
    print(f"  Signed:     {bool(result.output.get('signature'))}")

    # Verify the identity
    verify = agent.call_tool("verify_identity", agent_id=agent.agent_id)
    print(f"  Verified:   {verify.output['valid']}")
    for check, passed in verify.output.get("checks", {}).items():
        print(f"    {check}: {passed}")

    # ------------------------------------------------------------------
    # Phase 2: First compliance gate check (should fail - no profile yet)
    # ------------------------------------------------------------------
    banner("Phase 2: Compliance Gate - Pre-Profile Check")

    print("  Agent attempts to execute a task before setting up compliance...")
    gate_passed = compliance_gate(agent, compliance_svc)
    print(f"  Task execution allowed: {gate_passed}")
    if not gate_passed:
        print("  Agent correctly refuses to proceed without compliance profile.")

    # ------------------------------------------------------------------
    # Phase 3: Agent sets up compliance infrastructure
    # ------------------------------------------------------------------
    banner("Phase 3: Agent Registers Compliance Profile")

    profile_result = agent.call_tool(
        "create_compliance_profile",
        agent_id=agent.agent_id,
        risk_category="limited",
        provider_name="VibeTensor Inc.",
        intended_purpose="Automated financial compliance analysis for EU-regulated institutions",
        transparency_obligations="System discloses AI involvement in all outputs. Provides decision explanations.",
        human_oversight_measures="Senior compliance officer reviews flagged items before final submission.",
    )
    ok(profile_result.output, "Compliance profile created")
    print(f"  Profile ID:     {profile_result.output.get('profile_id')}")
    print(f"  Risk Category:  {profile_result.output.get('risk_category')}")

    # ------------------------------------------------------------------
    # Phase 4: Agent records its training data provenance (Article 10)
    # ------------------------------------------------------------------
    banner("Phase 4: Agent Records Training Data Provenance")

    datasets = [
        {
            "dataset_name": "EU Financial Regulations Corpus",
            "source_url": "https://eur-lex.europa.eu/",
            "license": "EU Open Data Licence",
            "data_categories": ["regulatory_text", "legislation"],
            "contains_personal_data": False,
            "data_governance_measures": "Sourced from official EU publications only. Version-controlled.",
        },
        {
            "dataset_name": "ECB Supervisory Banking Statistics",
            "source_url": "https://www.bankingsupervision.europa.eu/",
            "license": "Public Domain",
            "data_categories": ["banking_statistics", "aggregate_data"],
            "contains_personal_data": False,
            "data_governance_measures": "Aggregate data with no individual records. Quarterly snapshots.",
        },
    ]

    for ds in datasets:
        td_result = agent.call_tool("record_training_data", agent_id=agent.agent_id, **ds)
        ok(td_result.output, f"Training data: {ds['dataset_name']}")

    # ------------------------------------------------------------------
    # Phase 5: Agent records model lineage (Article 11)
    # ------------------------------------------------------------------
    banner("Phase 5: Agent Records Model Lineage")

    lineage_result = agent.call_tool(
        "record_model_lineage",
        agent_id=agent.agent_id,
        base_model="gpt-4o",
        base_model_provider="OpenAI",
        fine_tuning_method="RAG with financial regulation embeddings, no weight updates",
        evaluation_metrics={
            "accuracy": 0.91,
            "regulatory_citation_precision": 0.88,
            "hallucination_rate": 0.03,
        },
    )
    ok(lineage_result.output, "Model lineage recorded")

    # ------------------------------------------------------------------
    # Phase 6: Conformity assessment (Article 43)
    # ------------------------------------------------------------------
    banner("Phase 6: Conformity Assessment (Article 43)")

    # Limited-risk systems can self-assess
    assessment_result = agent.call_tool(
        "record_conformity_assessment",
        agent_id=agent.agent_id,
        assessment_type="self",
        assessor_name="VibeTensor Internal QA",
        result="pass",
        findings="All limited-risk obligations met. Transparency and oversight verified.",
        ce_marking_eligible=True,
    )
    ok(assessment_result.output, "Self-assessment recorded")
    print(f"  Assessment ID:  {assessment_result.output.get('assessment_id')}")
    print(f"  Result:         {assessment_result.output.get('result')}")
    print(f"  CE Marking:     {assessment_result.output.get('ce_marking_eligible')}")

    # Generate declaration of conformity (Annex V)
    decl_result = agent.call_tool(
        "generate_declaration",
        agent_id=agent.agent_id,
    )
    ok(decl_result.output, "Declaration of conformity generated")
    print(f"  Declaration ID: {decl_result.output.get('declaration_id')}")

    # ------------------------------------------------------------------
    # Phase 7: Second compliance gate check (should pass now)
    # ------------------------------------------------------------------
    banner("Phase 7: Compliance Gate - Post-Setup Check")

    gate_passed = compliance_gate(agent, compliance_svc)
    print(f"  Task execution allowed: {gate_passed}")

    # ------------------------------------------------------------------
    # Phase 8: Agent executes tasks with audit logging
    # ------------------------------------------------------------------
    banner("Phase 8: Agent Executes Tasks (with Audit Trail)")

    tasks = [
        {
            "description": "Analyze Q4 2025 compliance report for RegBank AG",
            "action_type": "inference",
            "input_summary": "Q4 2025 financial statements and regulatory filings from RegBank AG",
            "output_summary": "Compliance report: 3 minor findings, 0 critical issues, overall PASS",
            "decision_rationale": "Applied MiFID II and CRD IV checklists. All capital adequacy ratios above thresholds.",
        },
        {
            "description": "Retrieve updated ECB guidelines",
            "action_type": "external_call",
            "input_summary": "API call to ECB supervisory data portal for latest guidelines",
            "output_summary": "Retrieved 12 updated guideline documents dated March 2026",
            "decision_rationale": "Periodic update cycle. Source is an authorised regulatory body.",
        },
        {
            "description": "Delegate sub-analysis to reporting module",
            "action_type": "delegation",
            "input_summary": "Forward RegBank AG data subset to PDF report generator",
            "output_summary": "Delegation token issued with read-only data access for 4 hours",
            "decision_rationale": "Report generation requires formatted output. Least-privilege delegation applied.",
        },
    ]

    for task in tasks:
        # Compliance gate before each task
        if not compliance_gate(agent, compliance_svc):
            print(f"  SKIPPED: {task['description']}")
            continue

        print(f"\n  Executing: {task['description']}")

        # Log the action
        log_result = agent.call_tool(
            "log_action",
            agent_id=agent.agent_id,
            action_type=task["action_type"],
            input_summary=task["input_summary"],
            output_summary=task["output_summary"],
            decision_rationale=task["decision_rationale"],
        )
        ok(log_result.output, f"Audit logged ({task['action_type']})")
        print(f"    Chain hash: {log_result.output.get('chain_hash', 'N/A')[:24]}...")

        # Record interaction for reputation
        agent.call_tool(
            "record_interaction",
            agent_id=agent.agent_id,
            counterparty_id="attestix:system",
            outcome="success",
            category="task",
            details=task["description"],
        )

    # ------------------------------------------------------------------
    # Phase 9: Issue and verify a compliance credential
    # ------------------------------------------------------------------
    banner("Phase 9: Issue and Verify Compliance Credential")

    cred_result = agent.call_tool(
        "issue_credential",
        agent_id=agent.agent_id,
        credential_type="EUAIActComplianceCredential",
        issuer_name="VibeTensor Inc.",
        claims={
            "riskCategory": "limited",
            "complianceStatus": "fully_compliant",
            "assessmentType": "self",
            "assessmentResult": "pass",
            "framework": "EU AI Act (Regulation 2024/1689)",
            "agentName": agent.name,
        },
        expiry_days=365,
    )
    ok(cred_result.output, "Credential issued")
    cred_id = cred_result.output.get("id")
    print(f"  Credential ID:  {cred_id}")
    print(f"  Type:           {cred_result.output.get('type')}")
    print(f"  Proof:          {cred_result.output.get('proof', {}).get('type')}")

    # Verify the credential
    verify_result = agent.call_tool("verify_credential", credential_id=cred_id)
    print(f"\n  Verification result:")
    print(f"    Valid: {verify_result.output.get('valid')}")
    for check, passed in verify_result.output.get("checks", {}).items():
        print(f"    {check}: {passed}")

    # ------------------------------------------------------------------
    # Phase 10: Demonstrate gate blocking a non-compliant agent
    # ------------------------------------------------------------------
    banner("Phase 10: Compliance Gate Blocks Non-Compliant Agent")

    # Create a second agent with no compliance setup
    rogue = Agent(
        name="UncertifiedBot",
        instructions="A rogue agent with no compliance profile.",
        tools=tools,
    )
    rogue_identity = rogue.call_tool(
        "create_agent_identity",
        display_name="UncertifiedBot",
        source_protocol="openai_agents_sdk",
        capabilities=["data_scraping"],
        description="An agent that skipped compliance setup",
        issuer_name="Unknown",
    )
    rogue.agent_id = rogue_identity.output["agent_id"]
    print(f"  Rogue agent ID: {rogue.agent_id}")

    print("\n  Rogue agent attempts to execute a task...")
    rogue_allowed = compliance_gate(rogue, compliance_svc)
    print(f"  Task execution allowed: {rogue_allowed}")
    if not rogue_allowed:
        print("  Non-compliant agent correctly blocked by the compliance gate.")

    # ------------------------------------------------------------------
    # Phase 11: Review the full audit trail
    # ------------------------------------------------------------------
    banner("Phase 11: Review Audit Trail")

    trail = agent.call_tool("get_audit_trail", agent_id=agent.agent_id)
    entries = trail.output if isinstance(trail.output, list) else []
    print(f"  Total audit entries: {len(entries)}")
    for entry in entries:
        print(f"    [{entry.get('action_type', 'N/A'):15s}] {entry.get('log_id', '')} "
              f"- {entry.get('input_summary', '')[:50]}")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    banner("Summary")

    final_status = compliance_svc.get_compliance_status(agent.agent_id)
    reputation = reputation_svc.get_reputation(agent.agent_id)
    trust_score = reputation.get("trust_score", 0) if isinstance(reputation, dict) else 0

    print(f"  Agent:            {agent.name} ({agent.agent_id})")
    print(f"  Compliant:        {final_status.get('compliant')}")
    print(f"  Completion:       {final_status.get('completion_pct')}%")
    print(f"  Risk Category:    {final_status.get('risk_category')}")
    print(f"  Audit Entries:    {len(entries)}")
    print(f"  Trust Score:      {trust_score:.4f}")
    print(f"  Credentials:      1 manually issued + auto-issued compliance VC")
    print()
    print("  Key pattern demonstrated: the compliance gate.")
    print("  Every agent task is preceded by a compliance check.")
    print("  Non-compliant agents are blocked from executing tasks.")
    print("  All actions are logged to a tamper-evident hash-chained audit trail.")
    print("  Credentials are W3C Verifiable Credentials with Ed25519 proofs.")
    print()
    print("  In production, register Attestix tools via MCP in the OpenAI Agents SDK:")
    print("    agent = Agent(")
    print('        name="ComplianceAnalyst",')
    print("        tools=[attestix_mcp_tools],")
    print('        model="gpt-4o",')
    print("    )")
    print()


if __name__ == "__main__":
    main()
