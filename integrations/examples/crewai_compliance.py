"""CrewAI + Attestix Integration Example

Shows how to add DID-based agent identity, delegation chains,
and EU AI Act compliance to CrewAI crews.

This script simulates a CrewAI crew pattern using plain Python
so it works without the crewai package installed. It demonstrates:

  1. DID-based identity for every agent in the crew
  2. UCAN delegation from a manager to specialist agents
  3. Hash-chained audit trail for each agent action
  4. EU AI Act compliance gap analysis per agent
  5. Delegation chain verification and reputation scoring

Run: python integrations/examples/crewai_compliance.py
"""

import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, List, Optional

# Add the project root so Attestix services can be imported directly
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(0, PROJECT_ROOT)

from services.identity_service import IdentityService
from services.delegation_service import DelegationService
from services.provenance_service import ProvenanceService
from services.compliance_service import ComplianceService
from services.reputation_service import ReputationService
from services.did_service import DIDService


# ---------------------------------------------------------------------------
# Simulated CrewAI primitives (no crewai dependency required)
# ---------------------------------------------------------------------------

@dataclass
class AgentRole:
    """Simulates a CrewAI Agent with an Attestix identity attached."""
    role: str
    goal: str
    backstory: str
    capabilities: List[str]
    # Attestix fields (populated during crew setup)
    agent_id: Optional[str] = None
    did: Optional[str] = None
    delegation_token: Optional[str] = None
    delegation_jti: Optional[str] = None


@dataclass
class Task:
    """Simulates a CrewAI Task."""
    description: str
    expected_output: str
    agent: AgentRole
    action_type: str = "inference"


@dataclass
class CrewResult:
    """Simulates CrewAI crew kickoff result."""
    tasks_completed: int = 0
    outputs: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

SEPARATOR = "=" * 64

def section(title: str):
    """Print a section header."""
    print(f"\n{SEPARATOR}")
    print(f"  {title}")
    print(SEPARATOR)


def bullet(label: str, value, indent: int = 2):
    """Print a labelled value."""
    pad = " " * indent
    print(f"{pad}{label}: {value}")


def pp(obj: dict, indent: int = 4):
    """Pretty-print a dict snippet (truncated for readability)."""
    pad = " " * indent
    for key, val in obj.items():
        display = val
        if isinstance(val, str) and len(val) > 60:
            display = val[:57] + "..."
        if isinstance(val, list) and len(val) > 5:
            display = val[:5] + ["..."]
        print(f"{pad}{key}: {display}")


# ---------------------------------------------------------------------------
# 1. Define the crew (simulated CrewAI agents)
# ---------------------------------------------------------------------------

def define_crew() -> tuple:
    """Define three specialist agents and a manager, mimicking CrewAI."""

    researcher = AgentRole(
        role="Researcher",
        goal="Gather accurate data on the target topic",
        backstory=(
            "Senior research analyst specializing in AI regulatory "
            "landscape analysis across EU, US, and APAC markets."
        ),
        capabilities=["data_access", "external_call", "inference"],
    )

    writer = AgentRole(
        role="Writer",
        goal="Produce a well-structured compliance report draft",
        backstory=(
            "Technical writer with deep expertise in EU AI Act "
            "documentation requirements and Annex IV structure."
        ),
        capabilities=["inference", "data_access"],
    )

    reviewer = AgentRole(
        role="Reviewer",
        goal="Validate accuracy and flag compliance gaps",
        backstory=(
            "Compliance officer responsible for final review of all "
            "AI system documentation before submission to regulators."
        ),
        capabilities=["inference"],
    )

    return researcher, writer, reviewer


# ---------------------------------------------------------------------------
# 2. Bootstrap Attestix identities and DIDs
# ---------------------------------------------------------------------------

def create_identities(
    agents: List[AgentRole],
    identity_svc: IdentityService,
    did_svc: DIDService,
) -> dict:
    """Create a DID-based identity for each agent and a manager identity."""

    section("Step 1 - Create DID-Based Agent Identities")

    # Manager identity (the crew orchestrator)
    manager = identity_svc.create_identity(
        display_name="CrewManager",
        source_protocol="did:key",
        capabilities=["full_access", "delegation", "compliance_review"],
        description="CrewAI crew manager that orchestrates task delegation",
        issuer_name="VibeTensor",
    )
    manager_id = manager["agent_id"]
    manager_did = manager["issuer"]["did"]

    print(f"\n  Manager identity created")
    bullet("Agent ID", manager_id)
    bullet("DID", manager_did[:50] + "...")
    bullet("Capabilities", manager["capabilities"])

    # Create identities for each specialist agent
    for agent in agents:
        identity = identity_svc.create_identity(
            display_name=f"Crew-{agent.role}",
            source_protocol="did:key",
            capabilities=agent.capabilities,
            description=f"{agent.backstory[:80]}",
            issuer_name="VibeTensor",
        )
        agent.agent_id = identity["agent_id"]
        agent.did = identity["issuer"]["did"]

        print(f"\n  {agent.role} identity created")
        bullet("Agent ID", agent.agent_id)
        bullet("DID", agent.did[:50] + "...")
        bullet("Capabilities", agent.capabilities)

    # Verify all identities
    print(f"\n  Verifying identities...")
    for agent in agents:
        result = identity_svc.verify_identity(agent.agent_id)
        status = "VALID" if result["valid"] else "INVALID"
        print(f"    {agent.role}: {status} (signature={result['checks'].get('signature_valid', False)})")

    return {"manager_id": manager_id, "manager_did": manager_did}


# ---------------------------------------------------------------------------
# 3. Delegate capabilities via UCAN
# ---------------------------------------------------------------------------

def delegate_capabilities(
    manager_info: dict,
    agents: List[AgentRole],
    delegation_svc: DelegationService,
):
    """Manager delegates UCAN tokens to each specialist agent."""

    section("Step 2 - UCAN Capability Delegation")

    manager_id = manager_info["manager_id"]

    for agent in agents:
        result = delegation_svc.create_delegation(
            issuer_agent_id=manager_id,
            audience_agent_id=agent.agent_id,
            capabilities=agent.capabilities,
            expiry_hours=8,
        )

        if "error" in result:
            print(f"  ERROR delegating to {agent.role}: {result['error']}")
            continue

        agent.delegation_token = result["token"]
        agent.delegation_jti = result["delegation"]["jti"]

        print(f"\n  Manager -> {agent.role}")
        bullet("JTI", result["delegation"]["jti"])
        bullet("Capabilities", result["delegation"]["capabilities"])
        bullet("Expires", result["delegation"]["expires_at"])

    # Verify each delegation
    print(f"\n  Verifying delegation tokens...")
    for agent in agents:
        if not agent.delegation_token:
            continue
        verify = delegation_svc.verify_delegation(agent.delegation_token)
        status = "VALID" if verify.get("valid") else "INVALID"
        proof_count = len(verify.get("proof_chain", []))
        print(f"    {agent.role}: {status} (proof_chain_depth={proof_count})")


# ---------------------------------------------------------------------------
# 4. Execute tasks with audit logging
# ---------------------------------------------------------------------------

def execute_tasks(
    agents: List[AgentRole],
    provenance_svc: ProvenanceService,
    reputation_svc: ReputationService,
) -> CrewResult:
    """Simulate task execution. Each agent logs actions to the audit trail."""

    section("Step 3 - Execute Tasks with Audit Trail")

    researcher, writer, reviewer = agents

    # Define the task pipeline
    tasks = [
        Task(
            description="Research EU AI Act Article 6 high-risk classification criteria",
            expected_output="Structured summary of Annex III use cases and Article 6 criteria",
            agent=researcher,
            action_type="external_call",
        ),
        Task(
            description="Research recent enforcement actions and guidance from EU AI Office",
            expected_output="Timeline of enforcement milestones and key regulatory guidance",
            agent=researcher,
            action_type="data_access",
        ),
        Task(
            description="Draft compliance report covering risk classification methodology",
            expected_output="Report sections 1-3 covering scope, risk analysis, and classification",
            agent=writer,
            action_type="inference",
        ),
        Task(
            description="Draft technical documentation section per Annex IV requirements",
            expected_output="Technical documentation template populated with system details",
            agent=writer,
            action_type="inference",
        ),
        Task(
            description="Review draft for accuracy against EU AI Act text and flag gaps",
            expected_output="Review checklist with pass/fail per Article requirement",
            agent=reviewer,
            action_type="inference",
        ),
    ]

    result = CrewResult()

    for i, task in enumerate(tasks, 1):
        agent = task.agent
        print(f"\n  Task {i}/{len(tasks)} - {agent.role}")
        bullet("Action", task.description[:70])
        bullet("Type", task.action_type)

        # Log the action to the hash-chained audit trail
        log_entry = provenance_svc.log_action(
            agent_id=agent.agent_id,
            action_type=task.action_type,
            input_summary=task.description,
            output_summary=task.expected_output,
            decision_rationale=f"Assigned by CrewManager based on {agent.role} expertise",
        )

        if "error" in log_entry:
            print(f"    AUDIT ERROR: {log_entry['error']}")
            continue

        bullet("Log ID", log_entry["log_id"])
        bullet("Chain Hash", log_entry["chain_hash"][:24] + "...")
        bullet("Prev Hash", log_entry["prev_hash"][:24] + "...")

        # Record a successful interaction for reputation
        reputation_svc.record_interaction(
            agent_id=agent.agent_id,
            counterparty_id=agents[0].agent_id if agent != agents[0] else agents[1].agent_id,
            outcome="success",
            category="task",
            details=f"Completed: {task.description[:50]}",
        )

        result.tasks_completed += 1
        result.outputs.append(task.expected_output)

    print(f"\n  All {result.tasks_completed} tasks completed and audit-logged.")
    return result


# ---------------------------------------------------------------------------
# 5. Audit trail verification
# ---------------------------------------------------------------------------

def show_audit_trail(
    agents: List[AgentRole],
    provenance_svc: ProvenanceService,
):
    """Display the hash-chained audit trail for each agent."""

    section("Step 4 - Hash-Chained Audit Trail")

    for agent in agents:
        entries = provenance_svc.get_audit_trail(agent.agent_id, limit=10)
        print(f"\n  {agent.role} - {len(entries)} audit entries")

        for entry in entries:
            print(f"    [{entry['action_type']:14s}] {entry['log_id']}")
            print(f"      chain: {entry['chain_hash'][:32]}...")
            print(f"      prev:  {entry['prev_hash'][:32]}...")

        # Verify chain integrity
        if len(entries) > 1:
            chain_valid = True
            for j in range(1, len(entries)):
                if entries[j]["prev_hash"] != entries[j - 1]["chain_hash"]:
                    chain_valid = False
                    break
            status = "INTACT" if chain_valid else "BROKEN"
            print(f"    Chain integrity: {status}")


# ---------------------------------------------------------------------------
# 6. Compliance gap analysis
# ---------------------------------------------------------------------------

def run_compliance_analysis(
    agents: List[AgentRole],
    compliance_svc: ComplianceService,
    provenance_svc: ProvenanceService,
):
    """Create compliance profiles and run gap analysis for each agent."""

    section("Step 5 - EU AI Act Compliance Gap Analysis")

    risk_levels = {
        "Researcher": "limited",
        "Writer": "limited",
        "Reviewer": "high",
    }

    purposes = {
        "Researcher": "Automated regulatory data collection and summarization",
        "Writer": "AI-assisted compliance document drafting",
        "Reviewer": "Automated compliance review and gap detection for high-risk AI systems",
    }

    for agent in agents:
        risk = risk_levels.get(agent.role, "minimal")
        purpose = purposes.get(agent.role, "General AI task execution")

        print(f"\n  {agent.role} - Risk Category: {risk.upper()}")

        # Record training data provenance so the gap analysis sees it
        provenance_svc.record_training_data(
            agent_id=agent.agent_id,
            dataset_name=f"{agent.role} training corpus",
            source_url="https://eur-lex.europa.eu/",
            license="CC-BY-4.0",
            data_categories=["regulatory_text", "compliance_data"],
            data_governance_measures="Curated from official EU sources. No personal data.",
        )

        # Record model lineage
        provenance_svc.record_model_lineage(
            agent_id=agent.agent_id,
            base_model="claude-sonnet-4-20250514",
            base_model_provider="Anthropic",
            fine_tuning_method="Prompt engineering with domain-specific instructions",
            evaluation_metrics={"task_accuracy": 0.91, "hallucination_rate": 0.03},
        )

        # Create compliance profile
        profile = compliance_svc.create_compliance_profile(
            agent_id=agent.agent_id,
            risk_category=risk,
            provider_name="VibeTensor",
            intended_purpose=purpose,
            transparency_obligations=f"Agent discloses AI role. Outputs are marked as AI-generated.",
            human_oversight_measures=(
                "Human compliance officer reviews all outputs before regulatory submission."
                if risk == "high"
                else ""
            ),
        )

        if "error" in profile:
            print(f"    Profile creation note: {profile['error'][:80]}")
            # Profile might already exist from a previous run; continue with gap analysis
        else:
            bullet("Profile ID", profile["profile_id"])

        # Run gap analysis
        status = compliance_svc.get_compliance_status(agent.agent_id)

        if "error" in status:
            print(f"    Status error: {status['error']}")
            continue

        bullet("Completion", f"{status['completion_pct']}%")
        bullet("Compliant", status["compliant"])

        if status["completed"]:
            print(f"    Completed obligations:")
            for item in status["completed"]:
                print(f"      [PASS] {item}")

        if status["missing"]:
            print(f"    Missing obligations:")
            for item in status["missing"]:
                print(f"      [GAP]  {item}")


# ---------------------------------------------------------------------------
# 7. Delegation chain summary and reputation scores
# ---------------------------------------------------------------------------

def show_delegation_and_reputation(
    manager_info: dict,
    agents: List[AgentRole],
    delegation_svc: DelegationService,
    reputation_svc: ReputationService,
):
    """Display the full delegation chain and reputation scores."""

    section("Step 6 - Delegation Chain and Reputation Scores")

    manager_id = manager_info["manager_id"]

    # Show delegation chain
    print("\n  Delegation Chain:")
    print(f"    CrewManager ({manager_id[:20]}...)")

    for agent in agents:
        delegations = delegation_svc.list_delegations(
            agent_id=agent.agent_id,
            role="audience",
        )
        for d in delegations:
            print(f"      |")
            print(f"      +-> {agent.role} ({agent.agent_id[:20]}...)")
            print(f"          Capabilities: {d['capabilities']}")
            print(f"          JTI: {d['jti'][:20]}...")
            print(f"          Expires: {d['expires_at']}")

    # Show reputation scores
    print(f"\n  Reputation Scores (recency-weighted, 30-day half-life):")
    print(f"    {'Agent':<14s} {'Score':>8s} {'Interactions':>14s}")
    print(f"    {'-' * 14} {'-' * 8} {'-' * 14}")

    for agent in agents:
        rep = reputation_svc.get_reputation(agent.agent_id)
        score = rep.get("trust_score")
        count = rep.get("total_interactions", 0)
        score_str = f"{score:.4f}" if score is not None else "N/A"
        print(f"    {agent.role:<14s} {score_str:>8s} {count:>14d}")

        if rep.get("category_breakdown"):
            for cat, stats in rep["category_breakdown"].items():
                print(f"      {cat}: {stats['success']}s / {stats['total']} total")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print(SEPARATOR)
    print("  CrewAI + Attestix Integration Example")
    print("  DID Identity | UCAN Delegation | EU AI Act Compliance")
    print(SEPARATOR)

    # Initialize Attestix services
    identity_svc = IdentityService()
    delegation_svc = DelegationService()
    provenance_svc = ProvenanceService()
    compliance_svc = ComplianceService()
    reputation_svc = ReputationService()
    did_svc = DIDService()

    # Step 0: Define the crew
    researcher, writer, reviewer = define_crew()
    agents = [researcher, writer, reviewer]

    # Step 1: Create DID-based identities
    manager_info = create_identities(agents, identity_svc, did_svc)

    # Step 2: Manager delegates capabilities via UCAN
    delegate_capabilities(manager_info, agents, delegation_svc)

    # Step 3: Execute tasks with audit logging
    crew_result = execute_tasks(agents, provenance_svc, reputation_svc)

    # Step 4: Show hash-chained audit trail
    show_audit_trail(agents, provenance_svc)

    # Step 5: Compliance gap analysis per agent
    run_compliance_analysis(agents, compliance_svc, provenance_svc)

    # Step 6: Delegation chain and reputation
    show_delegation_and_reputation(
        manager_info, agents, delegation_svc, reputation_svc,
    )

    # Final summary
    section("Summary")
    print(f"\n  Crew size:         3 agents + 1 manager")
    print(f"  Tasks completed:   {crew_result.tasks_completed}")
    print(f"  Audit entries:     {crew_result.tasks_completed} (hash-chained)")
    print(f"  Delegations:       {len(agents)} UCAN tokens issued")
    print(f"  Compliance scans:  {len(agents)} gap analyses run")
    print(f"\n  All agent actions are cryptographically signed, hash-chained,")
    print(f"  and linked to DID-based identities with UCAN delegation proofs.")
    print(f"  No crewai dependency required - pure Python simulation.\n")


if __name__ == "__main__":
    main()
