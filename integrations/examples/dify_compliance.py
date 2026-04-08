"""Dify + Attestix Integration Example

Simulates a Dify workflow that uses Attestix MCP tools to achieve
EU AI Act compliance for an AI-powered customer service agent.

This script shows exactly where Attestix hooks into a Dify workflow:
  - On workflow creation: register agent identity
  - On workflow configuration: classify risk and create compliance profile
  - On each workflow step: log actions to the audit trail
  - On workflow completion: generate a declaration of conformity

No Dify installation required. The script simulates the Dify workflow
engine and demonstrates how Attestix tools would be called at each stage.

Usage:
    python integrations/examples/dify_compliance.py
"""

import json
import sys
import time
from pathlib import Path

# Add Attestix project root to path so we can import services directly
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from services.identity_service import IdentityService
from services.compliance_service import ComplianceService
from services.provenance_service import ProvenanceService
from services.credential_service import CredentialService
from services.agent_card_service import AgentCardService


# ---------------------------------------------------------------------------
# Simulated Dify Workflow Engine
# ---------------------------------------------------------------------------
# In a real Dify deployment, these classes would be replaced by Dify's own
# workflow runner. The Attestix calls (identity creation, audit logging, etc.)
# would be wired in as Dify "Tool" nodes using the Attestix MCP server.
# ---------------------------------------------------------------------------

class DifyWorkflowStep:
    """Represents a single node in a Dify workflow graph."""

    def __init__(self, step_id: str, step_type: str, name: str, config: dict = None):
        self.step_id = step_id
        self.step_type = step_type  # "llm", "tool", "code", "condition"
        self.name = name
        self.config = config or {}

    def __repr__(self):
        return f"<DifyStep {self.step_id}: {self.name} ({self.step_type})>"


class DifyWorkflow:
    """Simulates the Dify workflow execution engine."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.steps: list = []
        self.execution_log: list = []

    def add_step(self, step: DifyWorkflowStep):
        self.steps.append(step)

    def execute(self, user_input: str) -> list:
        """Run all steps sequentially, simulating Dify's DAG execution."""
        results = []
        for step in self.steps:
            result = {
                "step_id": step.step_id,
                "step_name": step.name,
                "step_type": step.step_type,
                "input": user_input if step == self.steps[0] else results[-1].get("output", ""),
                "output": f"[Simulated output from {step.name}]",
                "status": "completed",
            }
            results.append(result)
            self.execution_log.append(result)
        return results


def print_header(title: str):
    print(f"\n{'=' * 64}")
    print(f"  {title}")
    print(f"{'=' * 64}\n")


def print_step(number: int, title: str):
    print(f"\n--- Step {number}: {title} ---\n")


def main():
    # Initialize Attestix services
    # In Dify, these would be accessed via MCP tool calls:
    #   - create_agent_identity
    #   - create_compliance_profile
    #   - log_action
    #   - generate_declaration_of_conformity
    identity_svc = IdentityService()
    compliance_svc = ComplianceService()
    provenance_svc = ProvenanceService()
    credential_svc = CredentialService()
    agent_card_svc = AgentCardService()

    print_header("Dify + Attestix Compliance Integration")
    print("This example simulates a Dify chatbot workflow with full")
    print("EU AI Act compliance powered by Attestix MCP tools.\n")

    # -----------------------------------------------------------------------
    # PHASE 1: Workflow Registration
    # -----------------------------------------------------------------------
    # In Dify, this would happen when the workflow app is first published.
    # The Attestix MCP tool "create_agent_identity" is called as part of
    # the deployment pipeline or as the first node in a setup workflow.
    # -----------------------------------------------------------------------

    print_step(1, "Register Dify App as Agent Identity")
    print("  [Dify Hook: App Publication / Deployment Pipeline]")
    print("  In Dify, add an Attestix 'create_agent_identity' tool node")
    print("  that runs once during app setup.\n")

    agent = identity_svc.create_identity(
        display_name="Dify-CustomerServiceBot",
        source_protocol="manual",
        capabilities=[
            "customer_inquiry",
            "order_lookup",
            "refund_processing",
            "product_recommendation",
        ],
        description="AI-powered customer service chatbot built with Dify. "
                    "Handles order inquiries, refunds, and product questions.",
        issuer_name="RetailCo Europe GmbH",
        expiry_days=365,
    )
    agent_id = agent["agent_id"]
    print(f"  Agent ID:     {agent_id}")
    print(f"  Display Name: {agent['display_name']}")
    print(f"  DID:          {agent['issuer']['did']}")
    print(f"  Signed:       {bool(agent.get('signature'))}")

    # -----------------------------------------------------------------------
    # PHASE 2: Risk Classification and Compliance Profile
    # -----------------------------------------------------------------------
    # In Dify, this maps to a workflow configuration step. The app builder
    # would add Attestix tool nodes for risk classification and profile
    # creation in the setup workflow, or call them from a Dify "Code" node.
    # -----------------------------------------------------------------------

    print_step(2, "Classify Risk Category and Create Compliance Profile")
    print("  [Dify Hook: Workflow Configuration / Code Node]")
    print("  Use 'create_compliance_profile' tool node to set the risk level")
    print("  based on the app's intended use case.\n")

    # Customer service bots are typically "limited" risk under the EU AI Act
    # because they interact with humans but do not make high-stakes decisions
    profile = compliance_svc.create_compliance_profile(
        agent_id=agent_id,
        risk_category="limited",
        provider_name="RetailCo Europe GmbH",
        intended_purpose="Customer service chatbot for order inquiries, "
                         "refund processing, and product recommendations.",
        transparency_obligations="Bot clearly identifies itself as AI in every "
                                 "conversation. Provides escalation to human agent.",
        human_oversight_measures="Human agents can take over any conversation. "
                                 "Refunds above 100 EUR require human approval.",
    )
    print(f"  Profile ID:     {profile['profile_id']}")
    print(f"  Risk Category:  {profile['risk_category']}")
    print(f"  Obligations:    {len(profile.get('required_obligations', []))} items")

    # Record training data provenance (Article 10)
    print_step(3, "Record Training Data Provenance")
    print("  [Dify Hook: Model Configuration / Code Node]")
    print("  Record all data sources used to train or fine-tune the model.\n")

    training_data = provenance_svc.record_training_data(
        agent_id=agent_id,
        dataset_name="RetailCo Customer Interaction Corpus",
        source_url="https://data.retailco.eu/customer-interactions/v3",
        license="Proprietary",
        data_categories=["customer_queries", "product_catalog", "order_history"],
        contains_personal_data=True,
        data_governance_measures="PII removed via NER pipeline. GDPR Article 5 "
                                 "compliance verified. Data retention limited to 24 months.",
    )
    print(f"  Entry ID: {training_data['entry_id']}")
    print(f"  Dataset:  {training_data['dataset_name']}")

    # Record model lineage (Article 11)
    lineage = provenance_svc.record_model_lineage(
        agent_id=agent_id,
        base_model="claude-sonnet-4-20250514",
        base_model_provider="Anthropic",
        fine_tuning_method="RAG with vector store (Dify Knowledge Base). "
                           "No weight modification. Prompt engineering only.",
        evaluation_metrics={
            "response_accuracy": 0.91,
            "customer_satisfaction": 0.88,
            "escalation_rate": 0.12,
            "avg_resolution_time_seconds": 180,
        },
    )
    print(f"  Model:    {lineage['base_model']} by {lineage['base_model_provider']}")

    # -----------------------------------------------------------------------
    # PHASE 3: Build and Execute the Dify Workflow
    # -----------------------------------------------------------------------
    # This simulates a typical Dify chatbot workflow with multiple nodes.
    # Each step is logged to the Attestix audit trail via "log_action".
    # In Dify, you would add an Attestix "log_action" tool node after each
    # critical step, or use a Dify "Code" node to batch-log.
    # -----------------------------------------------------------------------

    print_step(4, "Build Dify Workflow Graph")
    print("  [Dify: Workflow Builder Canvas]\n")

    workflow = DifyWorkflow(
        name="Customer Service Pipeline",
        description="Handles customer queries with AI + human escalation",
    )

    workflow.add_step(DifyWorkflowStep(
        "start", "llm", "Intent Classifier",
        {"model": "claude-sonnet-4-20250514", "temperature": 0.1},
    ))
    workflow.add_step(DifyWorkflowStep(
        "kb_retrieval", "tool", "Knowledge Base Retrieval",
        {"dataset_id": "retailco-products-v3", "top_k": 5},
    ))
    workflow.add_step(DifyWorkflowStep(
        "response_gen", "llm", "Response Generator",
        {"model": "claude-sonnet-4-20250514", "temperature": 0.7},
    ))
    workflow.add_step(DifyWorkflowStep(
        "guardrails", "code", "Safety Guardrails",
        {"check_pii": True, "check_hallucination": True},
    ))

    for step in workflow.steps:
        print(f"  [{step.step_type.upper():9s}] {step.name} ({step.step_id})")

    print_step(5, "Execute Workflow with Audit Logging")
    print("  [Dify Hook: After each workflow node execution]")
    print("  Each step result is logged to Attestix via 'log_action' tool.\n")

    # Simulate a customer query
    user_query = "I ordered a laptop 3 days ago but it has not shipped yet. Can I get a refund?"
    print(f"  Customer Query: \"{user_query}\"\n")

    results = workflow.execute(user_query)

    # Log each workflow step to the Attestix audit trail
    # In Dify, this would be an Attestix tool node wired after each step,
    # or a single "Code" node at the end that logs all steps at once.
    step_actions = [
        {
            "action_type": "inference",
            "input_summary": f"Customer query: {user_query[:60]}...",
            "output_summary": "Intent classified: order_status_inquiry + refund_request",
            "decision_rationale": "Dual intent detected. Route to order lookup first, then refund.",
        },
        {
            "action_type": "data_access",
            "input_summary": "Knowledge base query: laptop order shipping refund policy",
            "output_summary": "Retrieved 5 relevant documents from retailco-products-v3",
            "decision_rationale": "Semantic search against product/policy knowledge base.",
        },
        {
            "action_type": "inference",
            "input_summary": "Context: 5 KB docs + customer order history + query",
            "output_summary": "Generated response explaining shipping timeline and refund eligibility",
            "decision_rationale": "RAG response grounded in retrieved policy documents.",
        },
        {
            "action_type": "inference",
            "input_summary": "Generated response passed through safety guardrails",
            "output_summary": "Response approved. No PII leakage. No hallucination detected.",
            "decision_rationale": "All safety checks passed. Response cleared for delivery.",
        },
    ]

    for i, (step_result, action) in enumerate(zip(results, step_actions)):
        log_entry = provenance_svc.log_action(
            agent_id=agent_id,
            **action,
        )
        print(f"  [{i+1}] {step_result['step_name']:25s} -> audit log: {log_entry['log_id'][:16]}...")

    # -----------------------------------------------------------------------
    # PHASE 4: Conformity Assessment and Declaration
    # -----------------------------------------------------------------------
    # For "limited" risk systems, self-assessment is allowed under the
    # EU AI Act. This would be triggered by a Dify workflow that runs
    # periodically or as part of the deployment pipeline.
    # -----------------------------------------------------------------------

    print_step(6, "Conformity Assessment (Article 43)")
    print("  [Dify Hook: Scheduled compliance workflow / Admin trigger]")
    print("  For limited-risk systems, self-assessment is permitted.\n")

    assessment = compliance_svc.record_conformity_assessment(
        agent_id=agent_id,
        assessment_type="self",
        assessor_name="RetailCo Internal QA Team",
        result="pass",
        findings="Customer service bot meets all transparency requirements. "
                 "AI disclosure present in all conversations. Human escalation "
                 "path verified. Response quality above 90% threshold.",
        ce_marking_eligible=True,
    )
    print(f"  Assessment ID: {assessment['assessment_id']}")
    print(f"  Type:          {assessment['assessment_type']}")
    print(f"  Result:        {assessment['result']}")

    print_step(7, "Generate Declaration of Conformity (Annex V)")
    print("  [Dify Hook: Post-assessment workflow node]")
    print("  Attestix generates a signed, verifiable declaration.\n")

    declaration = compliance_svc.generate_declaration_of_conformity(agent_id)
    print(f"  Declaration ID: {declaration['declaration_id']}")

    # -----------------------------------------------------------------------
    # PHASE 5: Verify Final Compliance Status
    # -----------------------------------------------------------------------

    print_step(8, "Final Compliance Status")
    final_status = compliance_svc.get_compliance_status(agent_id)
    print(f"  Compliant:  {final_status['compliant']}")
    print(f"  Completion: {final_status['completion_pct']}%")

    # Check for auto-issued compliance credential
    creds = credential_svc.list_credentials(
        agent_id=agent_id,
        credential_type="EUAIActComplianceCredential",
    )
    if creds:
        cred_id = creds[0]["id"]
        verification = credential_svc.verify_credential(cred_id)
        print(f"  Credential:  {cred_id}")
        print(f"  Valid:       {verification.get('valid')}")

    # View audit trail
    print_step(9, "Review Audit Trail")
    trail = provenance_svc.get_audit_trail(agent_id=agent_id)
    print(f"  Total audit entries: {len(trail)}")
    for entry in trail:
        print(f"    [{entry['action_type']:15s}] {entry['output_summary'][:55]}...")

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------

    print_header("Integration Summary")
    print("Dify Workflow Nodes That Call Attestix MCP Tools:\n")
    print("  1. App Setup          -> create_agent_identity")
    print("  2. Configuration      -> create_compliance_profile")
    print("  3. Data Config        -> record_training_data, record_model_lineage")
    print("  4. After Each Step    -> log_action (audit trail)")
    print("  5. Compliance Check   -> record_conformity_assessment")
    print("  6. Final Declaration  -> generate_declaration_of_conformity")
    print("  7. Verification       -> get_compliance_status, verify_credential")
    print()
    print(f"Agent: {agent_id}")
    print(f"Compliant: {final_status['compliant']}")
    print(f"Audit entries: {len(trail)}")
    print()
    print("All compliance artifacts are cryptographically signed (Ed25519)")
    print("and stored locally. In production, connect Attestix as a Dify")
    print("Tool Provider via its MCP server endpoint.")


if __name__ == "__main__":
    main()
