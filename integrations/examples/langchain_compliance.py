"""LangChain + Attestix Integration Example

Shows how to add EU AI Act compliance to LangChain agents using
Attestix's audit trail and compliance tools.

This script works in two modes:
  - With LangChain installed: uses real LangChain callback handlers
  - Without LangChain: uses lightweight stand-in classes that mimic
    LangChain's callback interface, so the full flow runs either way

Run: python integrations/examples/langchain_compliance.py
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

# ---------------------------------------------------------------------------
# 1. Resolve imports - LangChain (optional) and Attestix (required)
# ---------------------------------------------------------------------------

# Try importing LangChain; fall back to stand-in classes if unavailable
LANGCHAIN_AVAILABLE = False
Generation = None  # will be set when LangChain is present

try:
    from langchain_core.callbacks import BaseCallbackHandler
    from langchain_core.outputs import LLMResult
    from langchain_core.outputs import Generation as _Generation
    Generation = _Generation
    LANGCHAIN_AVAILABLE = True
except ImportError:
    pass

if not LANGCHAIN_AVAILABLE:
    try:
        from langchain.callbacks.base import BaseCallbackHandler
        from langchain.schema import LLMResult
        from langchain.schema import Generation as _Generation
        Generation = _Generation
        LANGCHAIN_AVAILABLE = True
    except ImportError:
        pass

# Stand-in classes when LangChain is not installed
if not LANGCHAIN_AVAILABLE:
    print("[info] LangChain not found - using stand-in callback classes\n")

    class LLMResult:
        """Minimal stand-in for langchain's LLMResult."""
        def __init__(self, generations=None, llm_output=None):
            self.generations = generations or []
            self.llm_output = llm_output or {}

    class BaseCallbackHandler:
        """Minimal stand-in for langchain's BaseCallbackHandler.

        Mirrors the callback lifecycle methods that LangChain agents
        invoke during execution, so the integration code is identical
        regardless of whether the real library is present.
        """
        def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs) -> None:
            pass

        def on_llm_end(self, response: "LLMResult", **kwargs) -> None:
            pass

        def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs) -> None:
            pass

        def on_tool_end(self, output: str, **kwargs) -> None:
            pass

        def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs) -> None:
            pass

        def on_chain_end(self, outputs: Dict[str, Any], **kwargs) -> None:
            pass

        def on_chain_error(self, error: BaseException, **kwargs) -> None:
            pass


# Add the project root so Attestix services resolve correctly
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from services.identity_service import IdentityService
from services.compliance_service import ComplianceService
from services.provenance_service import ProvenanceService


# ---------------------------------------------------------------------------
# 2. Attestix callback handler - the core integration layer
# ---------------------------------------------------------------------------

class AttestixComplianceHandler(BaseCallbackHandler):
    """LangChain callback handler that logs every agent step into
    Attestix's tamper-evident audit trail.

    Attach this handler to any LangChain agent, chain, or LLM to get
    automatic EU AI Act Article 12 record-keeping.

    Usage with a real LangChain agent::

        handler = AttestixComplianceHandler(agent_id="attestix:abc123")
        agent.run("Analyse the dataset", callbacks=[handler])

    Every tool invocation, LLM call, and chain step is recorded as a
    signed, hash-chained audit entry that can later be queried or
    anchored on-chain.
    """

    def __init__(self, agent_id: str):
        super().__init__()
        self.agent_id = agent_id
        self.provenance_svc = ProvenanceService()
        self._step_count = 0

    def _log(self, action_type: str, input_summary: str,
             output_summary: str, rationale: str = "") -> dict:
        """Write one audit entry and return it."""
        self._step_count += 1
        entry = self.provenance_svc.log_action(
            agent_id=self.agent_id,
            action_type=action_type,
            input_summary=input_summary,
            output_summary=output_summary,
            decision_rationale=rationale,
        )
        return entry

    # -- LLM callbacks -----------------------------------------------------

    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs) -> None:
        model_name = serialized.get("name", serialized.get("id", ["unknown"])[-1] if isinstance(serialized.get("id"), list) else "unknown")
        prompt_preview = prompts[0][:120] if prompts else "(empty)"
        self._log(
            action_type="inference",
            input_summary=f"LLM call to {model_name}: {prompt_preview}",
            output_summary="(awaiting response)",
            rationale="LangChain agent initiated LLM inference",
        )

    def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        text = ""
        if response.generations:
            first_gen = response.generations[0]
            if isinstance(first_gen, list) and first_gen:
                gen_obj = first_gen[0]
                text = getattr(gen_obj, "text", str(gen_obj))
            elif hasattr(first_gen, "text"):
                text = first_gen.text
        preview = text[:200] if text else "(no output)"
        self._log(
            action_type="inference",
            input_summary="LLM response received",
            output_summary=preview,
            rationale="LLM inference completed",
        )

    # -- Tool callbacks ----------------------------------------------------

    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs) -> None:
        tool_name = serialized.get("name", "unknown_tool")
        self._log(
            action_type="external_call",
            input_summary=f"Tool '{tool_name}' invoked with: {input_str[:200]}",
            output_summary="(awaiting tool result)",
            rationale=f"Agent decided to use tool '{tool_name}'",
        )

    def on_tool_end(self, output: str, **kwargs) -> None:
        self._log(
            action_type="external_call",
            input_summary="Tool execution completed",
            output_summary=str(output)[:200],
            rationale="Tool returned result to agent",
        )

    # -- Chain callbacks ---------------------------------------------------

    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs) -> None:
        chain_name = serialized.get("name", serialized.get("id", ["chain"])[-1] if isinstance(serialized.get("id"), list) else "chain")
        keys = list(inputs.keys()) if isinstance(inputs, dict) else []
        self._log(
            action_type="data_access",
            input_summary=f"Chain '{chain_name}' started with keys: {keys}",
            output_summary="(chain running)",
            rationale="LangChain chain execution initiated",
        )

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs) -> None:
        preview = json.dumps(outputs, default=str)[:200] if isinstance(outputs, dict) else str(outputs)[:200]
        self._log(
            action_type="data_access",
            input_summary="Chain execution completed",
            output_summary=preview,
            rationale="Chain returned final outputs",
        )

    def on_chain_error(self, error: BaseException, **kwargs) -> None:
        self._log(
            action_type="data_access",
            input_summary="Chain execution failed",
            output_summary=str(error)[:200],
            rationale="Error occurred during chain execution",
        )


# ---------------------------------------------------------------------------
# 3. Simulated LangChain agent workflow
# ---------------------------------------------------------------------------

def make_generation(text: str):
    """Create a generation object compatible with whichever LLMResult is active.

    When LangChain is installed, returns a real Generation instance so
    Pydantic validation passes. Otherwise returns a simple object with
    a .text attribute.
    """
    if Generation is not None:
        return Generation(text=text)

    class _SimpleGeneration:
        def __init__(self, t):
            self.text = t
    return _SimpleGeneration(text)


def simulate_langchain_agent(handler: AttestixComplianceHandler) -> str:
    """Walk through a realistic LangChain agent execution, calling the
    handler at every lifecycle point exactly as LangChain would.

    The scenario: a financial analysis agent receives a user question,
    uses a search tool, runs an LLM chain, and produces a final answer.
    """

    # -- Step A: Chain starts ----------------------------------------------
    handler.on_chain_start(
        serialized={"name": "FinancialAnalysisChain", "id": ["langchain", "chains", "FinancialAnalysisChain"]},
        inputs={"question": "What are the key risk factors for EU fintech companies in 2026?"},
    )

    # -- Step B: Agent calls a search tool ---------------------------------
    handler.on_tool_start(
        serialized={"name": "regulatory_search"},
        input_str="EU AI Act fintech risk factors 2026",
    )
    tool_output = (
        "Key risk factors include: (1) High-risk classification under EU AI Act Annex III "
        "for credit scoring systems, (2) DORA operational resilience requirements effective "
        "Jan 2025, (3) MiCA stablecoin reserve obligations, (4) Cross-border data transfer "
        "restrictions under GDPR adequacy decisions."
    )
    handler.on_tool_end(output=tool_output)

    # -- Step C: LLM processes the tool output -----------------------------
    handler.on_llm_start(
        serialized={"name": "claude-sonnet-4-20250514", "id": ["anthropic", "claude-sonnet-4-20250514"]},
        prompts=[
            "Based on the following research, provide a structured risk analysis "
            "for EU fintech companies:\n\n" + tool_output
        ],
    )
    llm_response_text = (
        "Risk Analysis for EU Fintech Companies (2026):\n\n"
        "1. AI COMPLIANCE RISK (HIGH): Credit scoring and fraud detection systems "
        "fall under EU AI Act Annex III high-risk category. Requires third-party "
        "conformity assessment, continuous monitoring, and human oversight.\n\n"
        "2. OPERATIONAL RESILIENCE (MEDIUM): DORA mandates ICT risk management "
        "frameworks, incident reporting within 4 hours, and regular testing.\n\n"
        "3. DATA GOVERNANCE (MEDIUM): GDPR cross-border transfers require Standard "
        "Contractual Clauses or adequacy decisions for non-EU processing.\n\n"
        "Recommendation: Prioritize EU AI Act compliance for all ML-based decision "
        "systems. Implement Attestix for automated compliance tracking."
    )
    handler.on_llm_end(
        response=LLMResult(
            generations=[[make_generation(llm_response_text)]],
            llm_output={"model": "claude-sonnet-4-20250514", "usage": {"total_tokens": 847}},
        ),
    )

    # -- Step D: Agent calls a second tool to check internal data ----------
    handler.on_tool_start(
        serialized={"name": "portfolio_analyzer"},
        input_str="current_portfolio_risk_exposure region=EU sector=fintech",
    )
    portfolio_output = (
        "Portfolio exposure: 12 EU fintech positions. "
        "3 flagged as high-risk AI systems (credit scoring). "
        "Compliance gap: 2 systems missing conformity assessment."
    )
    handler.on_tool_end(output=portfolio_output)

    # -- Step E: Final LLM synthesis ---------------------------------------
    handler.on_llm_start(
        serialized={"name": "claude-sonnet-4-20250514", "id": ["anthropic", "claude-sonnet-4-20250514"]},
        prompts=[
            "Synthesize the risk analysis and portfolio data into a final executive summary."
        ],
    )
    final_answer = (
        "EXECUTIVE SUMMARY: EU fintech portfolio carries elevated regulatory risk. "
        "3 of 12 positions use high-risk AI systems under the EU AI Act. "
        "2 systems lack required conformity assessments - immediate remediation "
        "recommended via Attestix compliance workflow. Estimated compliance "
        "timeline: 4-6 weeks with automated tooling."
    )
    handler.on_llm_end(
        response=LLMResult(
            generations=[[make_generation(final_answer)]],
            llm_output={"model": "claude-sonnet-4-20250514", "usage": {"total_tokens": 312}},
        ),
    )

    # -- Step F: Chain completes -------------------------------------------
    handler.on_chain_end(
        outputs={"answer": final_answer, "sources": ["regulatory_search", "portfolio_analyzer"]},
    )

    return final_answer


# ---------------------------------------------------------------------------
# 4. Main - end-to-end demonstration
# ---------------------------------------------------------------------------

def pp(label: str, obj: Any) -> None:
    """Print a labelled JSON blob."""
    print(f"  {label}:")
    print(json.dumps(obj, indent=4, default=str))
    print()


def main():
    print("=" * 64)
    print("  LangChain + Attestix  -  EU AI Act Compliance Integration")
    print("=" * 64)
    print()
    mode = "LangChain callbacks" if LANGCHAIN_AVAILABLE else "stand-in callbacks (no LangChain)"
    print(f"  Mode: {mode}")
    print()

    # -- Step 1: Create an agent identity ----------------------------------
    print("-" * 64)
    print("  STEP 1: Create Agent Identity (UAIT)")
    print("-" * 64)

    identity_svc = IdentityService()
    agent = identity_svc.create_identity(
        display_name="FinancialAnalysisAgent",
        source_protocol="langchain",
        capabilities=["financial_analysis", "regulatory_search", "portfolio_analysis"],
        description="LangChain agent for EU fintech risk analysis with tool use",
        issuer_name="Acme Fintech Ltd.",
        expiry_days=365,
    )
    agent_id = agent["agent_id"]
    print(f"  Agent ID:    {agent_id}")
    print(f"  DID:         {agent['issuer']['did']}")
    print(f"  Protocol:    {agent['source_protocol']}")
    print(f"  Signed:      {bool(agent.get('signature'))}")
    print()

    # -- Step 2: Create a compliance profile -------------------------------
    print("-" * 64)
    print("  STEP 2: Create EU AI Act Compliance Profile")
    print("-" * 64)

    compliance_svc = ComplianceService()
    profile = compliance_svc.create_compliance_profile(
        agent_id=agent_id,
        risk_category="limited",
        provider_name="Acme Fintech Ltd.",
        intended_purpose="Automated financial risk analysis and portfolio monitoring",
        transparency_obligations=(
            "System discloses AI involvement in all outputs. "
            "Users are informed that analysis is AI-generated."
        ),
    )
    if "error" in profile:
        print(f"  [error] {profile['error']}")
    else:
        print(f"  Profile ID:     {profile['profile_id']}")
        print(f"  Risk Category:  {profile['risk_category']}")
        print(f"  Obligations:    {len(profile.get('required_obligations', []))} required")
    print()

    # -- Step 3: Run the simulated LangChain agent -------------------------
    print("-" * 64)
    print("  STEP 3: Execute LangChain Agent (with Attestix callback)")
    print("-" * 64)
    print()
    print("  Simulating a multi-step agent workflow:")
    print("    Chain start -> Tool call -> LLM inference -> Tool call -> LLM -> Chain end")
    print()

    handler = AttestixComplianceHandler(agent_id=agent_id)
    final_answer = simulate_langchain_agent(handler)

    print(f"  Audit entries created: {handler._step_count}")
    print()
    print("  Agent final answer (truncated):")
    print(f"    {final_answer[:120]}...")
    print()

    # -- Step 4: Query the audit trail -------------------------------------
    print("-" * 64)
    print("  STEP 4: Query Attestix Audit Trail")
    print("-" * 64)

    provenance_svc = ProvenanceService()
    trail = provenance_svc.get_audit_trail(agent_id=agent_id, limit=20)
    print(f"  Total audit entries for this agent: {len(trail)}")
    print()

    for entry in trail:
        action = entry.get("action_type", "?")
        ts = entry.get("timestamp", "")[:19]
        summary = entry.get("input_summary", "")[:70]
        chain_ok = "chain_hash" in entry
        print(f"    [{ts}] {action:14s} | {summary}{'...' if len(entry.get('input_summary', '')) > 70 else ''}")
        if not chain_ok:
            print(f"      WARNING: missing chain hash")
    print()

    # Show hash-chain integrity
    print("  Hash-chain integrity:")
    if trail:
        first = trail[0]
        last = trail[-1]
        print(f"    First entry prev_hash: {first.get('prev_hash', 'N/A')[:16]}... (genesis)")
        print(f"    Last entry chain_hash: {last.get('chain_hash', 'N/A')[:16]}...")
        print(f"    All entries signed:    {all(e.get('signature') for e in trail)}")
    print()

    # -- Step 5: Check compliance status -----------------------------------
    print("-" * 64)
    print("  STEP 5: Compliance Gap Analysis")
    print("-" * 64)

    status = compliance_svc.get_compliance_status(agent_id)
    if "error" in status:
        print(f"  [error] {status['error']}")
    else:
        print(f"  Risk Category: {status['risk_category']}")
        print(f"  Compliant:     {status['compliant']}")
        print(f"  Completion:    {status['completion_pct']}%")
        print()
        if status.get("completed"):
            print("  Completed:")
            for item in status["completed"]:
                print(f"    [done] {item}")
        if status.get("missing"):
            print("  Missing:")
            for item in status["missing"]:
                print(f"    [todo] {item}")
    print()

    # -- Step 6: Verify the identity ---------------------------------------
    print("-" * 64)
    print("  STEP 6: Verify Agent Identity")
    print("-" * 64)

    verification = identity_svc.verify_identity(agent_id)
    print(f"  Valid: {verification['valid']}")
    for check, passed in verification.get("checks", {}).items():
        symbol = "pass" if passed else "FAIL"
        print(f"    {check}: {symbol}")
    print()

    # -- Summary -----------------------------------------------------------
    print("=" * 64)
    print("  INTEGRATION COMPLETE")
    print("=" * 64)
    print()
    print(f"  Agent:            {agent_id}")
    print(f"  Display Name:     FinancialAnalysisAgent")
    print(f"  Protocol:         langchain")
    print(f"  Audit Entries:    {handler._step_count} (hash-chained, Ed25519 signed)")
    print(f"  Compliance:       {status.get('completion_pct', 0)}% of obligations met")
    print(f"  Identity Valid:   {verification['valid']}")
    print()
    print("  To use this in a real LangChain project:")
    print()
    print("    from attestix_langchain import AttestixComplianceHandler")
    print()
    print("    handler = AttestixComplianceHandler(agent_id=your_agent_id)")
    print("    agent.run('your prompt', callbacks=[handler])")
    print()
    print("  Every tool call, LLM inference, and chain step will be logged")
    print("  to Attestix's tamper-evident audit trail automatically.")
    print()


if __name__ == "__main__":
    main()
