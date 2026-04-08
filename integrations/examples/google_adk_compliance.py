"""Google ADK + Attestix Integration Example

Simulates a Google Agent Development Kit (ADK) agent that uses Attestix
for compliance via MCPToolset. Demonstrates:

  - Agent creates its own identity on startup
  - Uses compliance tools alongside regular tools
  - Generates an A2A Agent Card with compliance credentials
  - Shows a multi-agent workflow with compliance checkpoints

No google-adk installation required. The script simulates the ADK agent
runtime and shows exactly where Attestix hooks into the ADK lifecycle.

Usage:
    python integrations/examples/google_adk_compliance.py
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
from services.agent_card_service import AgentCardService
from services.delegation_service import DelegationService
from services.reputation_service import ReputationService


# ---------------------------------------------------------------------------
# Simulated Google ADK Classes
# ---------------------------------------------------------------------------
# In a real ADK deployment, you would import from google.adk:
#   from google.adk import Agent, MCPToolset, Runner
#   from google.adk.tools import ToolContext
#
# The classes below simulate the ADK runtime behavior. Each place where
# Attestix integrates is marked with [ADK Integration Point].
# ---------------------------------------------------------------------------

class SimulatedMCPToolset:
    """Simulates google.adk.tools.MCPToolset.

    In real ADK code, you would connect to the Attestix MCP server:
        attestix_tools = MCPToolset(
            server_params=StdioServerParameters(
                command="attestix", args=["serve", "--mcp"]
            )
        )
    """

    def __init__(self, name: str, tools: dict):
        self.name = name
        self.tools = tools
        print(f"    MCPToolset '{name}' loaded with {len(tools)} tools")

    def call(self, tool_name: str, **kwargs):
        """Simulate calling an MCP tool."""
        if tool_name in self.tools:
            return self.tools[tool_name](**kwargs)
        return {"error": f"Tool '{tool_name}' not found in toolset '{self.name}'"}


class SimulatedADKAgent:
    """Simulates a Google ADK Agent with tool access.

    In real ADK code:
        agent = Agent(
            model="gemini-2.5-pro",
            name="ResearchAssistant",
            instruction="You are a research assistant...",
            tools=[attestix_toolset, search_toolset],
        )
    """

    def __init__(self, name: str, model: str, instruction: str, tools: list = None):
        self.name = name
        self.model = model
        self.instruction = instruction
        self.tools = tools or []
        self.agent_id = None
        self.history = []

    def run(self, user_message: str) -> str:
        """Simulate agent execution."""
        response = f"[{self.name}] Processed: {user_message[:50]}..."
        self.history.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        self.history.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        return response


class SimulatedADKRunner:
    """Simulates the ADK Runner that orchestrates agent execution.

    In real ADK code:
        runner = Runner(
            agent=agent,
            app_name="research_app",
            session_service=InMemorySessionService(),
        )
    """

    def __init__(self, agent: SimulatedADKAgent, app_name: str):
        self.agent = agent
        self.app_name = app_name

    def run(self, user_id: str, session_id: str, message: str) -> str:
        print(f"    Runner [{self.app_name}] session={session_id[:12]}...")
        return self.agent.run(message)


def print_header(title: str):
    print(f"\n{'=' * 64}")
    print(f"  {title}")
    print(f"{'=' * 64}\n")


def print_step(number: int, title: str):
    print(f"\n--- Step {number}: {title} ---\n")


def main():
    # Initialize Attestix services (in real ADK, accessed via MCPToolset)
    identity_svc = IdentityService()
    compliance_svc = ComplianceService()
    provenance_svc = ProvenanceService()
    credential_svc = CredentialService()
    agent_card_svc = AgentCardService()
    delegation_svc = DelegationService()
    reputation_svc = ReputationService()

    print_header("Google ADK + Attestix Compliance Integration")
    print("This example simulates a Google ADK multi-agent system")
    print("with EU AI Act compliance powered by Attestix.\n")

    # -----------------------------------------------------------------------
    # PHASE 1: Create Attestix MCPToolset
    # -----------------------------------------------------------------------
    # [ADK Integration Point: Agent Definition]
    # In real ADK, you would create the MCPToolset when defining the agent:
    #
    #   attestix = MCPToolset(
    #       server_params=StdioServerParameters(
    #           command="attestix", args=["serve", "--mcp"]
    #       )
    #   )
    #   agent = Agent(model="gemini-2.5-pro", tools=[attestix, ...])
    # -----------------------------------------------------------------------

    print_step(1, "Initialize Attestix MCPToolset for ADK")
    print("  [ADK Integration Point: MCPToolset in Agent constructor]\n")

    attestix_toolset = SimulatedMCPToolset("attestix", {
        "create_agent_identity": lambda **kw: identity_svc.create_identity(**kw),
        "create_compliance_profile": lambda **kw: compliance_svc.create_compliance_profile(**kw),
        "log_action": lambda **kw: provenance_svc.log_action(**kw),
        "record_training_data": lambda **kw: provenance_svc.record_training_data(**kw),
        "record_model_lineage": lambda **kw: provenance_svc.record_model_lineage(**kw),
        "record_conformity_assessment": lambda **kw: compliance_svc.record_conformity_assessment(**kw),
        "generate_declaration_of_conformity": lambda **kw: compliance_svc.generate_declaration_of_conformity(**kw),
        "get_compliance_status": lambda **kw: compliance_svc.get_compliance_status(**kw),
        "generate_agent_card": lambda **kw: agent_card_svc.generate_agent_card(**kw),
        "issue_credential": lambda **kw: credential_svc.issue_credential(**kw),
        "verify_credential": lambda **kw: credential_svc.verify_credential(**kw),
        "translate_identity": lambda **kw: identity_svc.translate_identity(**kw),
        "create_delegation": lambda **kw: delegation_svc.create_delegation(**kw),
        "verify_delegation": lambda **kw: delegation_svc.verify_delegation(**kw),
    })

    # -----------------------------------------------------------------------
    # PHASE 2: Agent Creates Its Own Identity
    # -----------------------------------------------------------------------
    # [ADK Integration Point: Agent Startup / before_agent_start callback]
    # The agent calls create_agent_identity as its first action.
    # In ADK, this can be done in the agent's instruction or as a startup hook.
    # -----------------------------------------------------------------------

    print_step(2, "Agent Self-Registration with Attestix")
    print("  [ADK Integration Point: Agent startup / first tool call]\n")

    # Primary research agent
    research_agent_identity = attestix_toolset.call(
        "create_agent_identity",
        display_name="ADK-ResearchAssistant",
        source_protocol="manual",
        capabilities=["web_search", "document_analysis", "summarization", "citation"],
        description="Google ADK research assistant that searches the web, "
                    "analyzes documents, and produces cited summaries.",
        issuer_name="ResearchLab AI Inc.",
        expiry_days=180,
    )
    research_agent_id = research_agent_identity["agent_id"]
    print(f"  Research Agent ID: {research_agent_id}")
    print(f"  DID:               {research_agent_identity['issuer']['did']}")

    # Sub-agent for fact-checking (multi-agent pattern)
    factcheck_identity = attestix_toolset.call(
        "create_agent_identity",
        display_name="ADK-FactChecker",
        source_protocol="manual",
        capabilities=["fact_verification", "source_validation", "bias_detection"],
        description="Specialized sub-agent for verifying claims and sources.",
        issuer_name="ResearchLab AI Inc.",
        expiry_days=180,
    )
    factcheck_agent_id = factcheck_identity["agent_id"]
    print(f"  FactCheck Agent ID: {factcheck_agent_id}")

    # -----------------------------------------------------------------------
    # PHASE 3: Compliance Profile with Regular Tool Integration
    # -----------------------------------------------------------------------
    # [ADK Integration Point: Agent uses compliance tools alongside search/analysis]
    # The agent treats Attestix tools the same as any other tool in its toolset.
    # -----------------------------------------------------------------------

    print_step(3, "Create Compliance Profiles")
    print("  [ADK Integration Point: Tool calls within agent execution]\n")

    # Research agent - limited risk (information retrieval, no high-stakes decisions)
    research_profile = attestix_toolset.call(
        "create_compliance_profile",
        agent_id=research_agent_id,
        risk_category="limited",
        provider_name="ResearchLab AI Inc.",
        intended_purpose="Research assistant for web search, document analysis, "
                         "and summarization. Provides information, not decisions.",
        transparency_obligations="Clearly labels AI-generated content. Cites all sources. "
                                 "Discloses confidence levels for each claim.",
        human_oversight_measures="All research outputs are reviewed by the human researcher "
                                 "before publication. Agent cannot publish autonomously.",
    )
    print(f"  Research Agent Profile: {research_profile['profile_id']}")
    print(f"  Risk: {research_profile['risk_category']}")

    # Fact-checker - also limited risk
    factcheck_profile = attestix_toolset.call(
        "create_compliance_profile",
        agent_id=factcheck_agent_id,
        risk_category="limited",
        provider_name="ResearchLab AI Inc.",
        intended_purpose="Fact-checking sub-agent. Verifies claims made by the "
                         "primary research agent against authoritative sources.",
        transparency_obligations="Reports verification status (confirmed/unconfirmed/disputed) "
                                 "for each claim. Cites verification sources.",
        human_oversight_measures="Fact-check results are advisory only. Human researcher "
                                 "makes final editorial decisions.",
    )
    print(f"  FactCheck Profile:      {factcheck_profile['profile_id']}")

    # Record model provenance for both agents
    for aid, name, model in [
        (research_agent_id, "Research Agent", "gemini-2.5-pro"),
        (factcheck_agent_id, "FactCheck Agent", "gemini-2.5-flash"),
    ]:
        attestix_toolset.call(
            "record_training_data",
            agent_id=aid,
            dataset_name="Common Crawl + Curated Academic Sources",
            source_url="https://commoncrawl.org/",
            license="CC-BY-4.0 (Common Crawl)",
            data_categories=["web_content", "academic_papers"],
            contains_personal_data=False,
            data_governance_measures="Pre-training data filtered for quality. "
                                     "No PII in fine-tuning data.",
        )
        attestix_toolset.call(
            "record_model_lineage",
            agent_id=aid,
            base_model=model,
            base_model_provider="Google DeepMind",
            fine_tuning_method="Prompt engineering with system instructions. "
                               "No weight modification.",
            evaluation_metrics={
                "factual_accuracy": 0.89,
                "citation_precision": 0.93,
                "hallucination_rate": 0.04,
            },
        )
        print(f"  Provenance recorded for {name}")

    # -----------------------------------------------------------------------
    # PHASE 4: Multi-Agent Delegation
    # -----------------------------------------------------------------------
    # [ADK Integration Point: Agent-to-agent delegation via Runner]
    # The research agent delegates fact-checking capability to the sub-agent
    # using a UCAN delegation token tracked by Attestix.
    # -----------------------------------------------------------------------

    print_step(4, "Multi-Agent Delegation (UCAN)")
    print("  [ADK Integration Point: Runner orchestration / sub-agent dispatch]\n")

    delegation = attestix_toolset.call(
        "create_delegation",
        issuer_agent_id=research_agent_id,
        audience_agent_id=factcheck_agent_id,
        capabilities=["fact_verification", "source_validation"],
        expiry_hours=4,
    )
    delegation_record = delegation["delegation"]
    print(f"  Delegation: {research_agent_id[:20]}... -> {factcheck_agent_id[:20]}...")
    print(f"  Token (jti): {delegation_record['jti']}")
    print(f"  Capabilities: {delegation_record['capabilities']}")

    # Verify the delegation
    verify_result = attestix_toolset.call(
        "verify_delegation",
        token=delegation["token"],
    )
    print(f"  Delegation valid: {verify_result['valid']}")

    # -----------------------------------------------------------------------
    # PHASE 5: Simulate Multi-Agent Workflow Execution
    # -----------------------------------------------------------------------
    # [ADK Integration Point: Within agent.run() / Runner.run()]
    # Each agent action is logged to the Attestix audit trail.
    # -----------------------------------------------------------------------

    print_step(5, "Execute Multi-Agent Research Workflow")
    print("  [ADK Integration Point: Tool calls during agent execution]\n")

    # Create simulated ADK agents
    research_agent = SimulatedADKAgent(
        name="ResearchAssistant",
        model="gemini-2.5-pro",
        instruction="You are a research assistant with access to Attestix compliance tools.",
        tools=[attestix_toolset],
    )
    research_agent.agent_id = research_agent_id

    factcheck_agent = SimulatedADKAgent(
        name="FactChecker",
        model="gemini-2.5-flash",
        instruction="You verify factual claims from the research agent.",
        tools=[attestix_toolset],
    )
    factcheck_agent.agent_id = factcheck_agent_id

    runner = SimulatedADKRunner(agent=research_agent, app_name="research_app")

    # Simulate research query
    query = "What are the key provisions of the EU AI Act for foundation model providers?"
    print(f"  User Query: \"{query[:60]}...\"\n")

    # Step A: Research agent searches and summarizes
    response = runner.run("user_123", "session_abc", query)
    attestix_toolset.call(
        "log_action",
        agent_id=research_agent_id,
        action_type="inference",
        input_summary=f"Research query: {query[:50]}...",
        output_summary="Generated 5-paragraph summary with 12 citations on EU AI Act provisions.",
        decision_rationale="Web search + document analysis. Confidence: high.",
    )
    print(f"  [Research Agent] Searched and summarized -> logged to audit trail")

    # Step B: Fact-checker verifies claims
    factcheck_response = factcheck_agent.run("Verify: EU AI Act requires foundation model providers to...")
    attestix_toolset.call(
        "log_action",
        agent_id=factcheck_agent_id,
        action_type="inference",
        input_summary="Fact-check request: 12 claims from research summary",
        output_summary="11/12 claims verified. 1 claim updated (Article number corrected).",
        decision_rationale="Cross-referenced with EUR-Lex official text and EU AI Office guidance.",
    )
    print(f"  [FactCheck Agent] Verified claims -> logged to audit trail")

    # Step C: Research agent incorporates corrections
    attestix_toolset.call(
        "log_action",
        agent_id=research_agent_id,
        action_type="inference",
        input_summary="Incorporated fact-check corrections into final summary",
        output_summary="Final summary updated. All 12 citations verified.",
        decision_rationale="Merged fact-checker corrections. Confidence: very high.",
    )
    print(f"  [Research Agent] Incorporated corrections -> logged to audit trail")

    # Record successful interaction for reputation
    reputation_svc.record_interaction(
        agent_id=research_agent_id,
        counterparty_id=factcheck_agent_id,
        outcome="success",
        category="research_quality",
        details="Multi-agent research workflow completed successfully.",
    )
    reputation_svc.record_interaction(
        agent_id=factcheck_agent_id,
        counterparty_id=research_agent_id,
        outcome="success",
        category="fact_verification",
        details="Verified 12 claims, corrected 1.",
    )

    # -----------------------------------------------------------------------
    # PHASE 6: A2A Agent Card with Compliance Credentials
    # -----------------------------------------------------------------------
    # [ADK Integration Point: Agent discovery via /.well-known/agent.json]
    # Generate an A2A Agent Card that includes Attestix compliance data.
    # Other agents can discover and verify this agent's compliance status.
    # -----------------------------------------------------------------------

    print_step(6, "Generate A2A Agent Card with Compliance Credentials")
    print("  [ADK Integration Point: /.well-known/agent.json endpoint]\n")

    agent_card_result = attestix_toolset.call(
        "generate_agent_card",
        name="ADK-ResearchAssistant",
        url="https://research.example.com",
        description="EU AI Act compliant research assistant built with Google ADK.",
        skills=[
            {"id": "web_search", "name": "Web Search", "description": "Search and retrieve web content"},
            {"id": "doc_analysis", "name": "Document Analysis", "description": "Analyze and extract from documents"},
            {"id": "summarization", "name": "Summarization", "description": "Generate cited summaries"},
        ],
        version="1.0.0",
    )
    card = agent_card_result["agent_card"]
    print(f"  Agent Card ID:   {card['id']}")
    print(f"  Name:            {card['name']}")
    print(f"  Skills:          {len(card['skills'])}")
    print(f"  Hosting path:    {agent_card_result['hosting_path']}")

    # Also translate the Attestix identity to A2A format for verification
    a2a_translation = attestix_toolset.call(
        "translate_identity",
        agent_id=research_agent_id,
        target_format="a2a_agent_card",
    )
    print(f"  A2A Card name:   {a2a_translation.get('name', 'N/A')}")
    print(f"  A2A Skills:      {len(a2a_translation.get('skills', []))}")

    # -----------------------------------------------------------------------
    # PHASE 7: Conformity Assessment and Declaration
    # -----------------------------------------------------------------------

    print_step(7, "Conformity Assessment and Declaration")
    print("  [ADK Integration Point: Periodic compliance workflow]\n")

    for aid, name in [
        (research_agent_id, "Research Agent"),
        (factcheck_agent_id, "FactCheck Agent"),
    ]:
        assessment = attestix_toolset.call(
            "record_conformity_assessment",
            agent_id=aid,
            assessment_type="self",
            assessor_name="ResearchLab AI QA",
            result="pass",
            findings=f"{name} meets all transparency and oversight requirements.",
            ce_marking_eligible=True,
        )
        print(f"  {name} assessment: {assessment['result']}")

        declaration = attestix_toolset.call(
            "generate_declaration_of_conformity",
            agent_id=aid,
        )
        print(f"  {name} declaration: {declaration['declaration_id']}")

    # -----------------------------------------------------------------------
    # PHASE 8: Final Status and Verification
    # -----------------------------------------------------------------------

    print_step(8, "Final Compliance Verification")

    for aid, name in [
        (research_agent_id, "Research Agent"),
        (factcheck_agent_id, "FactCheck Agent"),
    ]:
        status = attestix_toolset.call(
            "get_compliance_status",
            agent_id=aid,
        )
        print(f"  {name}: compliant={status['compliant']}, completion={status['completion_pct']}%")

    # Check audit trails
    research_trail = provenance_svc.get_audit_trail(agent_id=research_agent_id)
    factcheck_trail = provenance_svc.get_audit_trail(agent_id=factcheck_agent_id)
    print(f"\n  Research Agent audit entries:  {len(research_trail)}")
    print(f"  FactCheck Agent audit entries: {len(factcheck_trail)}")

    # Check reputation
    research_rep = reputation_svc.get_reputation(research_agent_id)
    factcheck_rep = reputation_svc.get_reputation(factcheck_agent_id)
    print(f"\n  Research Agent trust score:    {research_rep['trust_score']:.4f}")
    print(f"  FactCheck Agent trust score:   {factcheck_rep['trust_score']:.4f}")

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------

    print_header("Integration Summary")
    print("Google ADK Integration Points for Attestix:\n")
    print("  1. MCPToolset        -> Connect Attestix as MCP tool provider")
    print("  2. Agent Startup     -> create_agent_identity (self-registration)")
    print("  3. Agent Config      -> create_compliance_profile per agent")
    print("  4. Runner Dispatch   -> create_delegation for sub-agent auth")
    print("  5. Tool Execution    -> log_action after each tool call")
    print("  6. Agent Discovery   -> generate_agent_card for A2A protocol")
    print("  7. Compliance Check  -> record_conformity_assessment + declaration")
    print("  8. Verification      -> get_compliance_status, verify_credential")
    print()
    print("ADK-Specific Patterns:\n")
    print("  - MCPToolset wraps the Attestix MCP server as a standard ADK tool")
    print("  - Multi-agent delegation uses UCAN tokens via Attestix")
    print("  - A2A Agent Cards embed compliance status for agent discovery")
    print("  - Each agent in the ADK graph has its own identity and audit trail")
    print()
    print("All compliance artifacts are cryptographically signed (Ed25519).")


if __name__ == "__main__":
    main()
