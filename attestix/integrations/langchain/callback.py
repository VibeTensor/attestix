"""LangChain ``BaseCallbackHandler`` that logs to the Attestix audit chain.

This is the real callback handler referenced by the indie-dev quickstart::

    from attestix.integrations.langchain import AttestixCallback

It is a thin wrapper around :class:`~attestix.services.provenance_service.ProvenanceService`
that maps the LangChain callback surface onto ``log_action(...)`` calls so
every chain / tool / LLM event becomes a hash-chained, Ed25519-signed audit
row. Optionally issues a W3C Verifiable Credential at chain completion via
:class:`~attestix.services.credential_service.CredentialService`.

The framework dependency (``langchain-core``) is imported at *class*-load
time, not at module import time, so that ``import
attestix.integrations.langchain`` itself is always cheap and raises a
focused, actionable ``ImportError`` if the extra is missing.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import UUID

from attestix.services.credential_service import CredentialService
from attestix.services.identity_service import IdentityService
from attestix.services.provenance_service import ProvenanceService


def _require_langchain():
    """Import ``langchain_core`` lazily with a friendly error message."""
    try:
        from langchain_core.callbacks import BaseCallbackHandler  # noqa: F401
        from langchain_core.outputs import LLMResult  # noqa: F401
    except ImportError as exc:  # pragma: no cover - exercised by integration test
        raise ImportError(
            "AttestixCallback requires langchain-core. Install it with:\n"
            "    pip install 'attestix[langchain]'\n"
            "or:\n"
            "    pip install langchain-core"
        ) from exc


_require_langchain()

from langchain_core.callbacks import BaseCallbackHandler  # noqa: E402
from langchain_core.outputs import LLMResult  # noqa: E402


class AttestixCallback(BaseCallbackHandler):
    """LangChain callback that emits one Attestix audit row per event.

    Usage::

        from attestix.integrations.langchain import AttestixCallback
        from attestix.services.identity_service import IdentityService

        agent = IdentityService().create_identity(
            display_name="rag-helper", source_protocol="manual",
        )
        callback = AttestixCallback(agent_id=agent["agent_id"])
        executor.invoke({"input": "..."}, config={"callbacks": [callback]})

    Args:
        agent_id: Existing Attestix agent_id to associate audit rows with.
            If ``None``, a fresh identity is auto-created on first use with
            ``display_name=display_name`` and ``issuer_name=issuer_name``.
        display_name: Display name used only when auto-creating an identity.
        issuer_name: Issuer name used only when auto-creating an identity.
        record_llm_tokens: When True (default), record token-usage counts
            from ``LLMResult.llm_output['token_usage']`` in the audit row.
        issue_vc_on_success: When True (default), issue a
            ``ChainExecutionCredential`` (W3C VC, ``Ed25519Signature2020``) on
            ``on_chain_end``.
    """

    def __init__(
        self,
        agent_id: Optional[str] = None,
        *,
        display_name: str = "LangChainAgent",
        issuer_name: str = "self",
        record_llm_tokens: bool = True,
        issue_vc_on_success: bool = True,
    ) -> None:
        super().__init__()
        self._identity_svc = IdentityService()
        self._provenance_svc = ProvenanceService()
        self._credential_svc = CredentialService()

        if agent_id is None:
            agent = self._identity_svc.create_identity(
                display_name=display_name,
                source_protocol="manual",
                capabilities=["langchain_agent"],
                issuer_name=issuer_name,
            )
            agent_id = agent["agent_id"]

        self.agent_id = agent_id
        self.record_llm_tokens = record_llm_tokens
        self.issue_vc_on_success = issue_vc_on_success
        self.event_count = 0
        self._issuer_name = issuer_name

    # ----- LLM events -----------------------------------------------------

    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        self.event_count += 1
        chars = sum(len(p) for p in prompts)
        self._provenance_svc.log_action(
            agent_id=self.agent_id,
            action_type="inference",
            input_summary=f"LLM prompt ({len(prompts)} prompts, {chars} chars)",
            output_summary="pending",
            decision_rationale=self._llm_name(serialized),
        )

    def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        token_usage = 0
        if self.record_llm_tokens and response.llm_output:
            token_usage = response.llm_output.get("token_usage", {}).get(
                "total_tokens", 0
            )
        self._provenance_svc.log_action(
            agent_id=self.agent_id,
            action_type="inference",
            input_summary="LLM response received",
            output_summary=(
                f"{len(response.generations)} generations, "
                f"{token_usage} tokens"
            ),
        )

    # ----- Tool events ----------------------------------------------------

    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        self.event_count += 1
        tool_name = serialized.get("name", "unknown_tool")
        self._provenance_svc.log_action(
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
        self._provenance_svc.log_action(
            agent_id=self.agent_id,
            action_type="external_call",
            input_summary="Tool execution completed",
            output_summary=f"Output: {str(output)[:200]}",
        )

    # ----- Chain events ---------------------------------------------------

    def on_chain_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        self.event_count += 1
        self._provenance_svc.log_action(
            agent_id=self.agent_id,
            action_type="data_access",
            input_summary=f"Chain started: {self._chain_name(serialized)}",
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
        out_keys = (
            list(outputs.keys())
            if isinstance(outputs, dict)
            else type(outputs).__name__
        )
        self._provenance_svc.log_action(
            agent_id=self.agent_id,
            action_type="data_access",
            input_summary="Chain completed",
            output_summary=f"Output keys: {out_keys}",
        )
        if self.issue_vc_on_success:
            try:
                self._credential_svc.issue_credential(
                    agent_id=self.agent_id,
                    credential_type="ChainExecutionCredential",
                    issuer_name=self._issuer_name,
                    claims={
                        "events_logged": self.event_count,
                        "framework": "LangChain",
                    },
                )
            except Exception:
                # VC issuance is best-effort; never break the chain on it.
                pass

    # ----- Helpers --------------------------------------------------------

    @staticmethod
    def _llm_name(serialized: Dict[str, Any]) -> str:
        ids = serialized.get("id") if serialized else None
        if isinstance(ids, list) and ids:
            return f"LangChain LLM call via {ids[-1]}"
        return "LangChain LLM call"

    @staticmethod
    def _chain_name(serialized: Dict[str, Any]) -> str:
        ids = serialized.get("id") if serialized else None
        if isinstance(ids, list) and ids:
            return str(ids[-1])
        return "unknown"

    # ----- Audit summary --------------------------------------------------

    def get_audit_summary(self) -> dict:
        """Return the audit trail for this callback's agent."""
        trail = self._provenance_svc.get_audit_trail(self.agent_id)
        return {
            "agent_id": self.agent_id,
            "event_count": self.event_count,
            "audit_entries": len(trail),
            "trail": trail,
        }
