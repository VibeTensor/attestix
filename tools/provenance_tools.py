"""Provenance MCP tools for AURA Protocol (5 tools).

Training data provenance, model lineage, and Article 12 audit trail.
"""

import json
from typing import Optional


def _validate_required(params: dict) -> str:
    for name, value in params.items():
        if not value or (isinstance(value, str) and not value.strip()):
            return json.dumps({"error": f"{name} cannot be empty"})
    return ""


def register(mcp):
    """Register provenance tools with the MCP server."""

    @mcp.tool()
    async def record_training_data(
        agent_id: str,
        dataset_name: str,
        source_url: str = "",
        license: str = "",
        data_categories: str = "",
        contains_personal_data: bool = False,
        data_governance_measures: str = "",
    ) -> str:
        """Record a training data source for EU AI Act Article 10 compliance.

        Args:
            agent_id: The AURA agent ID (e.g., aura:abc123...).
            dataset_name: Name of the training dataset.
            source_url: URL or location of the dataset.
            license: Data license (e.g., CC-BY-4.0, proprietary).
            data_categories: Comma-separated categories (e.g., text,images,structured).
            contains_personal_data: Whether dataset contains personal data (GDPR).
            data_governance_measures: Description of data quality/governance measures.
        """
        err = _validate_required({"agent_id": agent_id, "dataset_name": dataset_name})
        if err:
            return err

        from services.cache import get_service
        from services.provenance_service import ProvenanceService

        svc = get_service(ProvenanceService)
        cats = [c.strip() for c in data_categories.split(",") if c.strip()] if data_categories else []
        result = svc.record_training_data(
            agent_id=agent_id,
            dataset_name=dataset_name,
            source_url=source_url,
            license=license,
            data_categories=cats,
            contains_personal_data=contains_personal_data,
            data_governance_measures=data_governance_measures,
        )
        return json.dumps(result, indent=2, default=str)

    @mcp.tool()
    async def record_model_lineage(
        agent_id: str,
        base_model: str,
        base_model_provider: str = "",
        fine_tuning_method: str = "",
        evaluation_metrics_json: str = "",
    ) -> str:
        """Record model lineage chain for EU AI Act Article 11 compliance.

        Args:
            agent_id: The AURA agent ID.
            base_model: Base model name (e.g., claude-opus-4-6, gpt-4).
            base_model_provider: Model provider (e.g., Anthropic, OpenAI).
            fine_tuning_method: Fine-tuning approach if any (LoRA, full, RLHF, none).
            evaluation_metrics_json: JSON string of evaluation metrics (e.g., {"accuracy": 0.95}).
        """
        from services.cache import get_service
        from services.provenance_service import ProvenanceService

        svc = get_service(ProvenanceService)
        metrics = {}
        if evaluation_metrics_json:
            try:
                metrics = json.loads(evaluation_metrics_json)
            except json.JSONDecodeError:
                return json.dumps({"error": "Invalid JSON in evaluation_metrics_json"})

        result = svc.record_model_lineage(
            agent_id=agent_id,
            base_model=base_model,
            base_model_provider=base_model_provider,
            fine_tuning_method=fine_tuning_method,
            evaluation_metrics=metrics,
        )
        return json.dumps(result, indent=2, default=str)

    @mcp.tool()
    async def log_action(
        agent_id: str,
        action_type: str,
        input_summary: str = "",
        output_summary: str = "",
        decision_rationale: str = "",
        human_override: bool = False,
    ) -> str:
        """Log an agent action for EU AI Act Article 12 automatic logging.

        Args:
            agent_id: The AURA agent ID.
            action_type: One of: inference, delegation, data_access, external_call.
            input_summary: Brief description of the input/request.
            output_summary: Brief description of the output/response.
            decision_rationale: Why the agent made this decision.
            human_override: Whether a human overrode the agent's decision.
        """
        from services.cache import get_service
        from services.provenance_service import ProvenanceService

        svc = get_service(ProvenanceService)
        result = svc.log_action(
            agent_id=agent_id,
            action_type=action_type,
            input_summary=input_summary,
            output_summary=output_summary,
            decision_rationale=decision_rationale,
            human_override=human_override,
        )
        return json.dumps(result, indent=2, default=str)

    @mcp.tool()
    async def get_provenance(agent_id: str) -> str:
        """Get full provenance record for an agent (training data, model lineage, audit summary).

        Args:
            agent_id: The AURA agent ID.
        """
        from services.cache import get_service
        from services.provenance_service import ProvenanceService

        svc = get_service(ProvenanceService)
        result = svc.get_provenance(agent_id)
        return json.dumps(result, indent=2, default=str)

    @mcp.tool()
    async def get_audit_trail(
        agent_id: str,
        action_type: str = "",
        start_date: str = "",
        end_date: str = "",
        limit: int = 50,
    ) -> str:
        """Query the Article 12 audit trail with optional filters.

        Args:
            agent_id: The AURA agent ID.
            action_type: Filter by type (inference, delegation, data_access, external_call). Empty = all.
            start_date: ISO date string for start of range (e.g., 2026-01-01T00:00:00).
            end_date: ISO date string for end of range.
            limit: Maximum number of results.
        """
        from services.cache import get_service
        from services.provenance_service import ProvenanceService

        svc = get_service(ProvenanceService)
        results = svc.get_audit_trail(
            agent_id=agent_id,
            action_type=action_type or None,
            start_date=start_date or None,
            end_date=end_date or None,
            limit=limit,
        )
        return json.dumps(results, indent=2, default=str)
