"""OpenAI Agents SDK audit hook for Attestix.

Unlike LangChain (which exposes a callback class) the OpenAI Agents SDK
already speaks MCP natively. The hook below is a small helper that wraps
the common pattern of "log every guardrail decision to the Attestix audit
chain" so callers do not have to re-implement it.

The hook deliberately does NOT import the ``agents`` SDK at module import
time so that ``import attestix.integrations.openai_agents`` is cheap and
the optional SDK is only needed when an Agent actually invokes the hook.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from attestix.services.identity_service import IdentityService
from attestix.services.provenance_service import ProvenanceService


class AttestixAuditHook:
    """Log Agent guardrail / tool decisions to the Attestix audit chain.

    Args:
        agent_id: Existing Attestix agent_id. If ``None`` a fresh identity
            is created with ``display_name`` / ``issuer_name``.
        display_name: Display name for auto-created identity.
        issuer_name: Issuer name for auto-created identity.
    """

    def __init__(
        self,
        agent_id: Optional[str] = None,
        *,
        display_name: str = "OpenAIAgent",
        issuer_name: str = "self",
    ) -> None:
        self._identity_svc = IdentityService()
        self._provenance_svc = ProvenanceService()

        if agent_id is None:
            agent = self._identity_svc.create_identity(
                display_name=display_name,
                source_protocol="manual",
                capabilities=["openai_agent"],
                issuer_name=issuer_name,
            )
            agent_id = agent["agent_id"]
        self.agent_id = agent_id

    def log_guardrail_decision(
        self,
        *,
        allowed: bool,
        reason: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> dict:
        """Log a guardrail decision (allow/block) to the audit chain."""
        return self._provenance_svc.log_action(
            agent_id=self.agent_id,
            action_type="delegation",
            input_summary=f"guardrail.decision: {'ALLOW' if allowed else 'BLOCK'}",
            output_summary=reason,
            decision_rationale=str(details or {}),
        )

    def log_tool_call(
        self,
        *,
        tool_name: str,
        input_summary: str = "",
        output_summary: str = "",
    ) -> dict:
        """Log a tool invocation to the audit chain."""
        return self._provenance_svc.log_action(
            agent_id=self.agent_id,
            action_type="external_call",
            input_summary=f"Tool: {tool_name} | {input_summary}",
            output_summary=output_summary,
        )

    def get_audit_summary(self) -> dict:
        """Return audit trail entries for this hook's agent."""
        trail = self._provenance_svc.get_audit_trail(self.agent_id)
        return {
            "agent_id": self.agent_id,
            "audit_entries": len(trail),
            "trail": trail,
        }
