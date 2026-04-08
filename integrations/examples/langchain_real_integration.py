"""LangChain REAL Integration with Attestix

This is NOT a simulation. It uses actual LangChain classes and
integrates real Attestix services as a LangChain callback handler.

Requirements: pip install langchain langchain-core attestix
Run: python integrations/examples/langchain_real_integration.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from typing import Any, Dict, List, Optional
from uuid import UUID

from services.identity_service import IdentityService
from services.compliance_service import ComplianceService
from services.provenance_service import ProvenanceService
from services.credential_service import CredentialService


class AttestixComplianceHandler(BaseCallbackHandler):
    """Real LangChain callback handler that logs to Attestix audit trail.

    Drop this into any LangChain agent to get EU AI Act compliance:

        handler = AttestixComplianceHandler(agent_name="MyAgent", issuer="MyCorp")
        agent.invoke({"input": "..."}, config={"callbacks": [handler]})
    """

    def __init__(self, agent_name: str = "LangChainAgent", issuer: str = "Default"):
        super().__init__()
        self.identity_svc = IdentityService()
        self.provenance_svc = ProvenanceService()

        # Create Attestix identity for this agent
        agent = self.identity_svc.create_identity(
            display_name=agent_name,
            source_protocol="mcp",
            capabilities=["langchain_agent"],
            issuer_name=issuer,
        )
        self.agent_id = agent["agent_id"]
        self.agent_did = agent["issuer"]["did"]
        self._action_count = 0

    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Log LLM invocation to Attestix audit trail."""
        self._action_count += 1
        self.provenance_svc.log_action(
            agent_id=self.agent_id,
            action_type="inference",
            input_summary=f"LLM prompt ({len(prompts)} prompts, {sum(len(p) for p in prompts)} chars)",
            output_summary="pending",
            decision_rationale=f"LangChain LLM call via {serialized.get('id', ['unknown'])[-1] if serialized.get('id') else 'unknown'}",
        )

    def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Log LLM completion."""
        generations = response.generations
        total_tokens = 0
        if response.llm_output and "token_usage" in response.llm_output:
            total_tokens = response.llm_output["token_usage"].get("total_tokens", 0)

        self.provenance_svc.log_action(
            agent_id=self.agent_id,
            action_type="inference",
            input_summary=f"LLM response received",
            output_summary=f"{len(generations)} generations, {total_tokens} tokens",
        )

    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Log tool invocation to audit trail."""
        self._action_count += 1
        tool_name = serialized.get("name", "unknown_tool")
        self.provenance_svc.log_action(
            agent_id=self.agent_id,
            action_type="external_call",
            input_summary=f"Tool: {tool_name} | Input: {input_str[:200]}",
            output_summary="pending",
        )

    def on_tool_end(
        self,
        output: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Log tool completion."""
        self.provenance_svc.log_action(
            agent_id=self.agent_id,
            action_type="external_call",
            input_summary="Tool execution completed",
            output_summary=f"Output: {str(output)[:200]}",
        )

    def on_chain_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Log chain start."""
        self._action_count += 1
        chain_type = serialized.get("id", ["unknown"])[-1] if serialized.get("id") else "unknown"
        self.provenance_svc.log_action(
            agent_id=self.agent_id,
            action_type="data_access",
            input_summary=f"Chain started: {chain_type}",
            output_summary="pending",
        )

    def on_chain_end(
        self,
        outputs: Dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Log chain completion."""
        self.provenance_svc.log_action(
            agent_id=self.agent_id,
            action_type="data_access",
            input_summary="Chain completed",
            output_summary=f"Output keys: {list(outputs.keys()) if isinstance(outputs, dict) else type(outputs).__name__}",
        )

    def get_audit_summary(self) -> dict:
        """Get the full audit trail for this agent."""
        trail = self.provenance_svc.get_audit_trail(self.agent_id)
        return {
            "agent_id": self.agent_id,
            "agent_did": self.agent_did,
            "total_actions": self._action_count,
            "audit_entries": len(trail),
            "trail": trail,
        }


def main():
    print("=" * 70)
    print("  LangChain REAL Integration with Attestix")
    print("  Using actual langchain_core.callbacks.BaseCallbackHandler")
    print("=" * 70)
    print()

    # 1. Create the handler (this IS the integration)
    print("[1] Creating AttestixComplianceHandler (real LangChain BaseCallbackHandler)...")
    handler = AttestixComplianceHandler(
        agent_name="FinancialAnalyst",
        issuer="AcmeCorp",
    )
    print(f"    Agent ID: {handler.agent_id}")
    print(f"    Agent DID: {handler.agent_did[:50]}...")
    print(f"    Handler class: {handler.__class__.__bases__[0].__module__}.{handler.__class__.__bases__[0].__name__}")
    print()

    # 2. Simulate LangChain events (as if an agent is running)
    print("[2] Simulating LangChain agent events...")
    from uuid import uuid4

    run_id = uuid4()

    # on_chain_start
    handler.on_chain_start(
        serialized={"id": ["langchain", "chains", "LLMChain"]},
        inputs={"query": "What are the top EU AI Act compliance requirements?"},
        run_id=run_id,
    )
    print("    Chain started: LLMChain")

    # on_llm_start
    handler.on_llm_start(
        serialized={"id": ["langchain", "llms", "OpenAI"]},
        prompts=["Analyze EU AI Act compliance requirements for financial AI systems."],
        run_id=uuid4(),
        parent_run_id=run_id,
    )
    print("    LLM invoked: OpenAI")

    # on_llm_end
    handler.on_llm_end(
        response=LLMResult(
            generations=[[]],
            llm_output={"token_usage": {"total_tokens": 450}},
        ),
        run_id=uuid4(),
        parent_run_id=run_id,
    )
    print("    LLM completed: 450 tokens")

    # on_tool_start
    handler.on_tool_start(
        serialized={"name": "web_search"},
        input_str="EU AI Act Article 43 conformity assessment requirements",
        run_id=uuid4(),
        parent_run_id=run_id,
    )
    print("    Tool started: web_search")

    # on_tool_end
    handler.on_tool_end(
        output="Found 5 results about Article 43 conformity assessment...",
        run_id=uuid4(),
        parent_run_id=run_id,
    )
    print("    Tool completed: 5 results")

    # on_chain_end
    handler.on_chain_end(
        outputs={"result": "EU AI Act requires conformity assessment for high-risk AI systems..."},
        run_id=run_id,
    )
    print("    Chain completed")
    print()

    # 3. Get audit summary
    print("[3] Audit Trail Summary...")
    summary = handler.get_audit_summary()
    print(f"    Agent: {summary['agent_id']}")
    print(f"    DID: {summary['agent_did'][:50]}...")
    print(f"    Actions logged: {summary['total_actions']}")
    print(f"    Audit entries: {summary['audit_entries']}")
    print()

    # 4. Verify hash chain integrity
    print("[4] Hash Chain Integrity...")
    trail = summary["trail"]
    chain_ok = True
    for i in range(1, len(trail)):
        if trail[i].get("prev_hash") != trail[i - 1].get("chain_hash"):
            chain_ok = False
            break
    print(f"    Entries: {len(trail)}")
    print(f"    Chain integrity: {'VERIFIED' if chain_ok else 'BROKEN'}")
    print(f"    All entries signed: {all(e.get('signature') for e in trail)}")
    print()

    # 5. Compliance status
    print("[5] EU AI Act Compliance...")
    compliance_svc = ComplianceService()
    compliance_svc.create_compliance_profile(
        agent_id=handler.agent_id,
        risk_category="limited",
        provider_name="AcmeCorp",
        intended_purpose="Financial analysis and reporting",
        transparency_obligations="Discloses AI-generated content to users",
    )
    status = compliance_svc.get_compliance_status(handler.agent_id)
    print(f"    Risk category: limited")
    print(f"    Completion: {status.get('completion_pct', 0)}%")
    print(f"    Completed: {status.get('completed', [])}")
    print(f"    Missing: {status.get('missing', [])}")
    print()

    # 6. Issue credential
    print("[6] W3C Verifiable Credential...")
    credential_svc = CredentialService()
    cred = credential_svc.issue_credential(
        agent_id=handler.agent_id,
        credential_type="EUAIActComplianceCredential",
        issuer_name="AcmeCorp",
        claims={
            "risk_category": "limited",
            "framework": "LangChain",
            "articles_assessed": ["Article 50", "Article 52"],
        },
    )
    verify = credential_svc.verify_credential(cred["id"])
    print(f"    Credential: {cred['id'][:50]}...")
    print(f"    Proof: {cred['proof']['type']}")
    print(f"    Valid: {verify['valid']}")
    print(f"    Checks: {verify['checks']}")
    print()

    print("=" * 70)
    print("  Integration complete. This handler works with ANY LangChain agent:")
    print()
    print("    from integrations.examples.langchain_real_integration import AttestixComplianceHandler")
    print("    handler = AttestixComplianceHandler('MyAgent', 'MyCorp')")
    print("    agent.invoke({'input': '...'}, config={'callbacks': [handler]})")
    print("=" * 70)


if __name__ == "__main__":
    main()
