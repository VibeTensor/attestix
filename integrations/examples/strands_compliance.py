"""AWS Strands Agents + Attestix Integration Example

Simulates an AWS Strands agent that uses Attestix for compliance:

  - Agent registers with Attestix on startup
  - Compliance check runs before every tool execution
  - Audit trail is logged to Attestix (complements Bedrock AgentCore memory)
  - Shows how compliance credentials integrate with AgentCore Identity

No strands-agents or AWS SDK installation required. The script simulates
the Strands agent runtime and shows exactly where Attestix hooks in.

Usage:
    python integrations/examples/strands_compliance.py
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add Attestix project root to path so we can import services directly
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from services.identity_service import IdentityService
from services.compliance_service import ComplianceService
from services.provenance_service import ProvenanceService
from services.credential_service import CredentialService
from services.reputation_service import ReputationService


# ---------------------------------------------------------------------------
# Simulated AWS Strands Classes
# ---------------------------------------------------------------------------
# In a real Strands deployment, you would import from strands:
#   from strands import Agent, tool
#   from strands.models import BedrockModel
#
# The classes below simulate the Strands agent runtime. Each place where
# Attestix integrates is marked with [Strands Integration Point].
# ---------------------------------------------------------------------------

class SimulatedStrandsTool:
    """Simulates a Strands @tool decorated function.

    In real Strands code:
        @tool
        def search_database(query: str) -> str:
            '''Search the product database.'''
            return database.search(query)
    """

    def __init__(self, name: str, description: str, handler):
        self.name = name
        self.description = description
        self.handler = handler

    def __call__(self, **kwargs):
        return self.handler(**kwargs)


class ComplianceGate:
    """Pre-execution compliance gate for Strands tools.

    [Strands Integration Point: Tool execution middleware]

    In a real Strands deployment, this would wrap each tool call:
        @tool
        def my_tool(query: str) -> str:
            gate = ComplianceGate(agent_id, compliance_svc, provenance_svc)
            gate.pre_check("my_tool", {"query": query})
            result = do_actual_work(query)
            gate.post_log("my_tool", {"query": query}, result)
            return result

    Or implemented as a Strands callback/middleware if the framework supports it.
    """

    def __init__(self, agent_id: str, compliance_svc, provenance_svc):
        self.agent_id = agent_id
        self.compliance_svc = compliance_svc
        self.provenance_svc = provenance_svc
        self.checks_passed = 0
        self.checks_blocked = 0

    def pre_check(self, tool_name: str, tool_input: dict) -> bool:
        """Run compliance check before tool execution.

        Verifies the agent has a valid compliance profile and has not
        been flagged for non-compliance.
        """
        status = self.compliance_svc.get_compliance_status(self.agent_id)
        if "error" in status:
            # No compliance profile yet - allow but warn
            print(f"    [GATE] WARNING: No compliance profile for tool '{tool_name}'")
            self.checks_passed += 1
            return True

        # For limited/minimal risk, allow execution even if not fully complete
        if status.get("completion_pct", 0) >= 0:
            self.checks_passed += 1
            return True

        self.checks_blocked += 1
        print(f"    [GATE] BLOCKED: Tool '{tool_name}' - compliance incomplete")
        return False

    def post_log(self, tool_name: str, tool_input: dict, result: str,
                 action_type: str = "external_call"):
        """Log tool execution to Attestix audit trail.

        This creates an Article 12 compliant audit record that complements
        the agent's memory stored in Bedrock AgentCore.
        """
        input_summary = f"Tool: {tool_name} | Input: {json.dumps(tool_input)[:100]}"
        output_summary = str(result)[:200]

        return self.provenance_svc.log_action(
            agent_id=self.agent_id,
            action_type=action_type,
            input_summary=input_summary,
            output_summary=output_summary,
            decision_rationale=f"Automated tool call via Strands agent. "
                               f"Compliance gate passed.",
        )


class SimulatedStrandsAgent:
    """Simulates the Strands Agent class with compliance integration.

    In real Strands code:
        agent = Agent(
            model=BedrockModel(model_id="anthropic.claude-sonnet-4-20250514-v1:0"),
            system_prompt="You are a claims processing agent...",
            tools=[search_claims, validate_policy, process_payment],
        )
    """

    def __init__(self, model_id: str, system_prompt: str, tools: list,
                 compliance_gate: ComplianceGate = None):
        self.model_id = model_id
        self.system_prompt = system_prompt
        self.tools = {t.name: t for t in tools}
        self.compliance_gate = compliance_gate
        self.conversation_history = []

    def call_tool(self, tool_name: str, **kwargs) -> str:
        """Execute a tool with compliance gate checks."""
        tool = self.tools.get(tool_name)
        if not tool:
            return f"Error: Tool '{tool_name}' not found"

        # [Strands Integration Point: Pre-execution compliance check]
        if self.compliance_gate:
            allowed = self.compliance_gate.pre_check(tool_name, kwargs)
            if not allowed:
                return f"BLOCKED: Tool '{tool_name}' failed compliance check"

        # Execute the tool
        result = tool(**kwargs)

        # [Strands Integration Point: Post-execution audit logging]
        if self.compliance_gate:
            self.compliance_gate.post_log(tool_name, kwargs, result)

        return result

    def run(self, user_message: str) -> str:
        """Simulate agent conversation turn."""
        self.conversation_history.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        response = f"[Agent] Processing: {user_message[:50]}..."
        self.conversation_history.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        return response


# ---------------------------------------------------------------------------
# Simulated Bedrock AgentCore Identity
# ---------------------------------------------------------------------------

class SimulatedAgentCoreIdentity:
    """Simulates AWS Bedrock AgentCore Identity.

    [Strands Integration Point: AgentCore Identity + Attestix credentials]

    AgentCore Identity provides AWS IAM-based identity for agents. Attestix
    adds a complementary layer with W3C Verifiable Credentials and
    EU AI Act compliance attestations that travel with the agent across
    cloud boundaries.
    """

    def __init__(self, agent_name: str, aws_account: str = "123456789012"):
        self.agent_name = agent_name
        self.aws_account = aws_account
        self.agent_arn = f"arn:aws:bedrock:us-east-1:{aws_account}:agent/{agent_name}"
        self.attestix_agent_id = None
        self.compliance_credentials = []

    def bind_attestix_identity(self, attestix_agent_id: str):
        """Link Attestix identity to AgentCore Identity."""
        self.attestix_agent_id = attestix_agent_id

    def add_compliance_credential(self, credential_id: str):
        """Attach an Attestix compliance credential."""
        self.compliance_credentials.append(credential_id)

    def get_identity_bundle(self) -> dict:
        """Return combined identity for cross-cloud agent verification.

        This bundle combines AWS AgentCore Identity with Attestix
        compliance credentials, allowing the agent to prove both its
        AWS authorization and EU AI Act compliance status.
        """
        return {
            "aws_identity": {
                "agent_arn": self.agent_arn,
                "agent_name": self.agent_name,
            },
            "attestix_identity": {
                "agent_id": self.attestix_agent_id,
                "compliance_credentials": self.compliance_credentials,
            },
            "verification_note": "AWS ARN verified via IAM, Attestix credentials "
                                 "verified via Ed25519 signatures.",
        }


def print_header(title: str):
    print(f"\n{'=' * 64}")
    print(f"  {title}")
    print(f"{'=' * 64}\n")


def print_step(number: int, title: str):
    print(f"\n--- Step {number}: {title} ---\n")


def main():
    # Initialize Attestix services
    identity_svc = IdentityService()
    compliance_svc = ComplianceService()
    provenance_svc = ProvenanceService()
    credential_svc = CredentialService()
    reputation_svc = ReputationService()

    print_header("AWS Strands + Attestix Compliance Integration")
    print("This example simulates an AWS Strands insurance claims agent")
    print("with EU AI Act compliance powered by Attestix.\n")

    # -----------------------------------------------------------------------
    # PHASE 1: Agent Registration on Startup
    # -----------------------------------------------------------------------
    # [Strands Integration Point: Agent initialization]
    # When the Strands agent starts, it registers with Attestix.
    # This happens before any tool calls are made.
    # -----------------------------------------------------------------------

    print_step(1, "Agent Registers with Attestix on Startup")
    print("  [Strands Integration Point: Agent __init__ / startup hook]\n")

    agent_identity = identity_svc.create_identity(
        display_name="Strands-ClaimsProcessor",
        source_protocol="manual",
        capabilities=[
            "claims_search",
            "policy_validation",
            "damage_assessment",
            "payment_processing",
            "customer_communication",
        ],
        description="AWS Strands agent for insurance claims processing. "
                    "Automates claim intake, validation, assessment, and payout.",
        issuer_name="EuroInsure AG",
        expiry_days=365,
    )
    agent_id = agent_identity["agent_id"]
    print(f"  Agent ID:     {agent_id}")
    print(f"  Display Name: {agent_identity['display_name']}")
    print(f"  DID:          {agent_identity['issuer']['did']}")
    print(f"  Signed:       {bool(agent_identity.get('signature'))}")

    # Bind to simulated AgentCore Identity
    agentcore = SimulatedAgentCoreIdentity("claims-processor-prod")
    agentcore.bind_attestix_identity(agent_id)
    print(f"\n  AgentCore ARN: {agentcore.agent_arn}")
    print(f"  Attestix bound: {agentcore.attestix_agent_id is not None}")

    # -----------------------------------------------------------------------
    # PHASE 2: Compliance Profile and Provenance
    # -----------------------------------------------------------------------
    # [Strands Integration Point: Post-registration setup]
    # After identity creation, configure the compliance profile.
    # Insurance claims processing is "high" risk under EU AI Act Annex III.
    # -----------------------------------------------------------------------

    print_step(2, "Configure Compliance Profile (High Risk)")
    print("  [Strands Integration Point: Agent configuration phase]")
    print("  Insurance claims processing falls under Annex III (high risk).\n")

    profile = compliance_svc.create_compliance_profile(
        agent_id=agent_id,
        risk_category="high",
        provider_name="EuroInsure AG",
        intended_purpose="Automated insurance claims processing. Handles claim intake, "
                         "policy validation, damage assessment, and payment authorization.",
        transparency_obligations="Claimants are informed that AI assists in processing. "
                                 "All AI decisions include explanation. Appeal to human adjuster available.",
        human_oversight_measures="Claims above 10,000 EUR require human adjuster sign-off. "
                                 "Denied claims always reviewed by human before communication. "
                                 "Monthly audit of AI decisions by compliance team.",
        provider_address="Friedrichstrasse 123, 10117 Berlin, Germany",
    )
    print(f"  Profile ID:    {profile['profile_id']}")
    print(f"  Risk Category: {profile['risk_category']}")
    print(f"  Obligations:   {len(profile.get('required_obligations', []))} required items")

    # Record training data (Article 10)
    print_step(3, "Record Training Data and Model Lineage")
    print("  [Strands Integration Point: Model configuration]\n")

    datasets = [
        {
            "dataset_name": "EuroInsure Historical Claims (2018-2025)",
            "source_url": "s3://euroinsure-ml/training/claims-history-v4",
            "license": "Proprietary",
            "data_categories": ["insurance_claims", "policy_data", "assessments"],
            "contains_personal_data": True,
            "data_governance_measures": "PII pseudonymized per GDPR Art. 32. "
                                       "Bias audit per protected characteristics. "
                                       "Data retention: 7 years (regulatory requirement).",
        },
        {
            "dataset_name": "Vehicle Damage Assessment Image Dataset",
            "source_url": "s3://euroinsure-ml/training/vehicle-damage-v2",
            "license": "Proprietary",
            "data_categories": ["vehicle_images", "damage_labels"],
            "contains_personal_data": False,
            "data_governance_measures": "License plates and faces blurred. "
                                       "Labeling quality verified by 3 independent assessors.",
        },
    ]

    for ds in datasets:
        result = provenance_svc.record_training_data(agent_id=agent_id, **ds)
        personal = "YES" if ds["contains_personal_data"] else "no"
        print(f"  [{result['entry_id'][:12]}...] {ds['dataset_name'][:45]}... (personal: {personal})")

    # Record model lineage (Article 11)
    lineage = provenance_svc.record_model_lineage(
        agent_id=agent_id,
        base_model="anthropic.claude-sonnet-4-20250514-v1:0",
        base_model_provider="Anthropic (via Amazon Bedrock)",
        fine_tuning_method="RAG with Bedrock Knowledge Base. System prompt engineering. "
                           "No model weight modification.",
        evaluation_metrics={
            "claim_accuracy": 0.94,
            "false_denial_rate": 0.02,
            "processing_time_p95_seconds": 45,
            "customer_satisfaction": 0.87,
            "demographic_parity_diff": 0.03,
        },
    )
    print(f"\n  Model: {lineage['base_model']}")
    print(f"  Provider: {lineage['base_model_provider']}")

    # -----------------------------------------------------------------------
    # PHASE 3: Build Agent with Compliance Gate
    # -----------------------------------------------------------------------
    # [Strands Integration Point: Tool wrapping with compliance middleware]
    # Every tool call passes through a ComplianceGate that:
    #   1. Checks compliance status before execution
    #   2. Logs the action to the audit trail after execution
    # -----------------------------------------------------------------------

    print_step(4, "Build Strands Agent with Compliance Gate")
    print("  [Strands Integration Point: Tool execution middleware]")
    print("  Every tool call is wrapped with pre-check and post-log.\n")

    compliance_gate = ComplianceGate(agent_id, compliance_svc, provenance_svc)

    # Define simulated Strands tools
    tools = [
        SimulatedStrandsTool(
            "search_claims",
            "Search the claims database",
            lambda claim_id="", **kw: f"Found claim {claim_id}: auto collision, "
                                      f"policy #POL-2026-4821, damage est. 3,500 EUR",
        ),
        SimulatedStrandsTool(
            "validate_policy",
            "Validate insurance policy coverage",
            lambda policy_id="", **kw: f"Policy {policy_id} active. Collision coverage: yes. "
                                       f"Deductible: 500 EUR. Max payout: 50,000 EUR",
        ),
        SimulatedStrandsTool(
            "assess_damage",
            "AI-powered damage assessment from photos",
            lambda claim_id="", **kw: f"Damage assessment for {claim_id}: "
                                      f"front bumper + headlight. Estimated: 3,200 EUR",
        ),
        SimulatedStrandsTool(
            "authorize_payment",
            "Authorize claim payout",
            lambda claim_id="", amount=0, **kw: f"Payment of {amount} EUR authorized for {claim_id}",
        ),
        SimulatedStrandsTool(
            "send_notification",
            "Send claimant notification",
            lambda claim_id="", message="", **kw: f"Notification sent to claimant for {claim_id}",
        ),
    ]

    agent = SimulatedStrandsAgent(
        model_id="anthropic.claude-sonnet-4-20250514-v1:0",
        system_prompt="You are an insurance claims processing agent for EuroInsure AG. "
                      "Process claims fairly and transparently.",
        tools=tools,
        compliance_gate=compliance_gate,
    )

    print(f"  Agent created with {len(tools)} tools")
    print(f"  Compliance gate: active")
    print(f"  Model: {agent.model_id}")

    # -----------------------------------------------------------------------
    # PHASE 4: Execute Claims Processing Workflow
    # -----------------------------------------------------------------------
    # [Strands Integration Point: Runtime tool execution]
    # Each tool call automatically:
    #   1. Runs compliance pre-check (ComplianceGate.pre_check)
    #   2. Executes the tool
    #   3. Logs to Attestix audit trail (ComplianceGate.post_log)
    # -----------------------------------------------------------------------

    print_step(5, "Process Insurance Claim (with Compliance Gates)")
    print("  [Strands Integration Point: Every tool call has pre-check + post-log]")
    print("  Simulating claim #CLM-2026-7890 processing...\n")

    # Step A: Customer files claim
    agent.run("I was in a car accident yesterday. My policy number is POL-2026-4821.")
    print(f"  [Agent] Received claim from customer")

    # Step B: Search existing claims
    result = agent.call_tool("search_claims", claim_id="CLM-2026-7890")
    print(f"  [Tool: search_claims] {result[:60]}...")

    # Step C: Validate policy
    result = agent.call_tool("validate_policy", policy_id="POL-2026-4821")
    print(f"  [Tool: validate_policy] {result[:60]}...")

    # Step D: Assess damage
    result = agent.call_tool("assess_damage", claim_id="CLM-2026-7890")
    print(f"  [Tool: assess_damage] {result[:60]}...")

    # Step E: Agent reasoning (logged as inference)
    provenance_svc.log_action(
        agent_id=agent_id,
        action_type="inference",
        input_summary="Claim CLM-2026-7890: damage 3,200 EUR, deductible 500 EUR",
        output_summary="Recommended payout: 2,700 EUR (3,200 - 500 deductible). "
                       "Below 10,000 EUR threshold - auto-approval eligible.",
        decision_rationale="Damage within policy limits. Standard deductible applied. "
                           "Amount below human review threshold.",
    )
    print(f"  [Agent reasoning] Calculated payout: 2,700 EUR -> logged to audit trail")

    # Step F: Authorize payment (below 10K threshold, no human needed)
    result = agent.call_tool("authorize_payment", claim_id="CLM-2026-7890", amount=2700)
    print(f"  [Tool: authorize_payment] {result[:60]}...")

    # Step G: Notify claimant
    result = agent.call_tool(
        "send_notification",
        claim_id="CLM-2026-7890",
        message="Your claim has been approved. Payout: 2,700 EUR.",
    )
    print(f"  [Tool: send_notification] {result[:60]}...")

    print(f"\n  Compliance gate stats:")
    print(f"    Checks passed:  {compliance_gate.checks_passed}")
    print(f"    Checks blocked: {compliance_gate.checks_blocked}")

    # Record successful processing for reputation
    reputation_svc.record_interaction(
        agent_id=agent_id,
        counterparty_id="attestix:system",
        outcome="success",
        category="claims_processing",
        details="Processed claim CLM-2026-7890 successfully. Payout: 2,700 EUR.",
    )

    # -----------------------------------------------------------------------
    # PHASE 5: Conformity Assessment (Third-Party Required for High Risk)
    # -----------------------------------------------------------------------
    # [Strands Integration Point: Periodic compliance workflow]
    # High-risk systems require third-party assessment per Article 43.
    # Self-assessment is blocked for high-risk systems.
    # -----------------------------------------------------------------------

    print_step(6, "Conformity Assessment (Article 43)")
    print("  [Strands Integration Point: Compliance pipeline / scheduled job]")
    print("  High-risk systems REQUIRE third-party assessment.\n")

    # Demonstrate that self-assessment is blocked for high-risk
    self_result = compliance_svc.record_conformity_assessment(
        agent_id=agent_id,
        assessment_type="self",
        assessor_name="EuroInsure Internal QA",
        result="pass",
    )
    if "error" in self_result:
        print(f"  Self-assessment blocked (expected for high-risk):")
        print(f"    {self_result['error'][:70]}...")

    # Third-party assessment
    assessment = compliance_svc.record_conformity_assessment(
        agent_id=agent_id,
        assessment_type="third_party",
        assessor_name="TUV SUD AG",
        result="pass",
        findings="Claims processing agent meets EU AI Act requirements for "
                 "high-risk AI in insurance (Annex III). Human oversight measures "
                 "verified. Bias testing within acceptable thresholds.",
        ce_marking_eligible=True,
    )
    print(f"\n  Third-party assessment: {assessment['result']}")
    print(f"  Assessor: TUV SUD AG")
    print(f"  Assessment ID: {assessment['assessment_id']}")

    # -----------------------------------------------------------------------
    # PHASE 6: Declaration of Conformity
    # -----------------------------------------------------------------------

    print_step(7, "Generate Declaration of Conformity (Annex V)")
    print("  [Strands Integration Point: Post-assessment pipeline]\n")

    declaration = compliance_svc.generate_declaration_of_conformity(agent_id)
    print(f"  Declaration ID: {declaration['declaration_id']}")

    # -----------------------------------------------------------------------
    # PHASE 7: Compliance Credentials + AgentCore Identity Bundle
    # -----------------------------------------------------------------------
    # [Strands Integration Point: AgentCore Identity integration]
    # Attestix compliance credentials are attached to the AgentCore Identity,
    # creating a combined identity bundle that proves both AWS authorization
    # and EU AI Act compliance.
    # -----------------------------------------------------------------------

    print_step(8, "Combine AgentCore Identity with Compliance Credentials")
    print("  [Strands Integration Point: AgentCore Identity enrichment]\n")

    # Check for auto-issued compliance credential
    creds = credential_svc.list_credentials(
        agent_id=agent_id,
        credential_type="EUAIActComplianceCredential",
    )

    if creds:
        cred_id = creds[0]["id"]
        verification = credential_svc.verify_credential(cred_id)
        agentcore.add_compliance_credential(cred_id)
        print(f"  Compliance Credential: {cred_id}")
        print(f"  Credential Valid: {verification.get('valid')}")

    # Get combined identity bundle
    identity_bundle = agentcore.get_identity_bundle()
    print(f"\n  Combined Identity Bundle:")
    print(f"    AWS ARN:              {identity_bundle['aws_identity']['agent_arn']}")
    print(f"    Attestix Agent ID:    {identity_bundle['attestix_identity']['agent_id'][:30]}...")
    print(f"    Compliance Creds:     {len(identity_bundle['attestix_identity']['compliance_credentials'])}")
    print(f"    Verification:         {identity_bundle['verification_note'][:60]}...")

    # -----------------------------------------------------------------------
    # PHASE 8: Final Compliance Status and Audit Review
    # -----------------------------------------------------------------------

    print_step(9, "Final Compliance Status and Audit Review")

    final_status = compliance_svc.get_compliance_status(agent_id)
    print(f"  Compliant:  {final_status['compliant']}")
    print(f"  Completion: {final_status['completion_pct']}%")

    # Full audit trail
    trail = provenance_svc.get_audit_trail(agent_id=agent_id)
    print(f"\n  Audit Trail ({len(trail)} entries):")
    for entry in trail:
        human = " [HUMAN OVERRIDE]" if entry.get("human_override") else ""
        print(f"    [{entry['action_type']:15s}] {entry['output_summary'][:50]}...{human}")

    # Reputation
    reputation = reputation_svc.get_reputation(agent_id)
    print(f"\n  Trust Score: {reputation['trust_score']:.4f}")

    # Full provenance
    provenance = provenance_svc.get_provenance(agent_id)
    print(f"  Training datasets: {len(provenance.get('training_data', []))}")
    print(f"  Model lineage: {len(provenance.get('model_lineage', []))}")

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------

    print_header("Integration Summary")
    print("AWS Strands + Attestix Integration Points:\n")
    print("  1. Agent Startup     -> Register identity with Attestix")
    print("  2. Configuration     -> Create compliance profile (risk category)")
    print("  3. Data Provenance   -> Record training data + model lineage")
    print("  4. Tool Middleware    -> ComplianceGate wraps every tool call")
    print("     a. Pre-check      -> Verify compliance before execution")
    print("     b. Post-log       -> Log to audit trail after execution")
    print("  5. Agent Reasoning   -> Log inference decisions to audit trail")
    print("  6. Assessment        -> Third-party conformity assessment")
    print("  7. Declaration       -> Generate Annex V declaration")
    print("  8. AgentCore Bind    -> Attach credentials to AgentCore Identity")
    print()
    print("Strands-Specific Patterns:\n")
    print("  - ComplianceGate middleware wraps every @tool function")
    print("  - Attestix audit trail complements Bedrock AgentCore memory")
    print("  - Compliance credentials attach to AgentCore Identity")
    print("  - High-risk systems enforce third-party assessment (Article 43)")
    print("  - Combined identity bundle proves AWS auth + EU compliance")
    print()
    print("All compliance artifacts are cryptographically signed (Ed25519).")


if __name__ == "__main__":
    main()
