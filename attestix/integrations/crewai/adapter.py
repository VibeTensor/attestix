"""CrewAI adapter for the Attestix audit chain.

The adapter does not import CrewAI itself — the integration is purely a
log-emission helper that callers invoke from their own CrewAI
Task/Process callbacks. This keeps ``import
attestix.integrations.crewai`` cheap and free of an upstream version pin.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from attestix.services.identity_service import IdentityService
from attestix.services.provenance_service import ProvenanceService


class AttestixCrewAdapter:
    """Log CrewAI Task lifecycle events to the Attestix audit chain.

    Wire into a Crew::

        adapter = AttestixCrewAdapter(display_name="ResearchCrew")
        # In your CrewAI Task callback:
        adapter.log_task_start(task_name="research", agent_role="researcher")
        ...
        adapter.log_task_finish(task_name="research", output_summary="3 docs")
    """

    def __init__(
        self,
        agent_id: Optional[str] = None,
        *,
        display_name: str = "CrewAIAgent",
        issuer_name: str = "self",
    ) -> None:
        self._identity_svc = IdentityService()
        self._provenance_svc = ProvenanceService()

        if agent_id is None:
            agent = self._identity_svc.create_identity(
                display_name=display_name,
                source_protocol="manual",
                capabilities=["crewai_agent"],
                issuer_name=issuer_name,
            )
            agent_id = agent["agent_id"]
        self.agent_id = agent_id

    def log_task_start(
        self,
        *,
        task_name: str,
        agent_role: str = "",
        inputs: Optional[Dict[str, Any]] = None,
    ) -> dict:
        return self._provenance_svc.log_action(
            agent_id=self.agent_id,
            action_type="data_access",
            input_summary=f"crewai.task.start: {task_name} ({agent_role})",
            output_summary="pending",
            decision_rationale=str(inputs or {})[:500],
        )

    def log_task_finish(
        self,
        *,
        task_name: str,
        output_summary: str = "",
    ) -> dict:
        return self._provenance_svc.log_action(
            agent_id=self.agent_id,
            action_type="data_access",
            input_summary=f"crewai.task.finish: {task_name}",
            output_summary=output_summary[:500],
        )

    def get_audit_summary(self) -> dict:
        trail = self._provenance_svc.get_audit_trail(self.agent_id)
        return {
            "agent_id": self.agent_id,
            "audit_entries": len(trail),
            "trail": trail,
        }
