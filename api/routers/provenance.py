"""Provenance router - REST endpoints wrapping ProvenanceService.

Manages training data provenance, model lineage tracking, and
Article 12 EU AI Act automatic action logging (audit trail).
"""

import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from api.deps import get_provenance_service
from services.provenance_service import ProvenanceService

logger = logging.getLogger("attestix.api.provenance")

router = APIRouter(prefix="/v1/provenance", tags=["provenance"])


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class RecordTrainingDataRequest(BaseModel):
    agent_id: str = Field(..., description="Agent ID the training data belongs to")
    dataset_name: str = Field(..., description="Name of the training dataset")
    source_url: str = Field("", description="URL where the dataset can be accessed")
    license: str = Field("", description="License of the dataset (e.g., MIT, CC-BY-4.0)")
    data_categories: Optional[List[str]] = Field(None, description="Categories of data in the dataset")
    contains_personal_data: bool = Field(False, description="Whether the dataset contains personal data")
    data_governance_measures: str = Field("", description="Data governance measures applied (Article 10)")


class RecordModelLineageRequest(BaseModel):
    agent_id: str = Field(..., description="Agent ID the model belongs to")
    base_model: str = Field(..., description="Base model name (e.g., gpt-4, claude-3)")
    base_model_provider: str = Field("", description="Provider of the base model")
    fine_tuning_method: str = Field("", description="Fine-tuning method used (e.g., LoRA, full)")
    evaluation_metrics: Optional[Dict] = Field(None, description="Evaluation metrics (accuracy, F1, etc.)")


class LogActionRequest(BaseModel):
    agent_id: str = Field(..., description="Agent ID performing the action")
    action_type: str = Field(..., description="Action type: inference, delegation, data_access, or external_call")
    input_summary: str = Field("", description="Summary of the action input")
    output_summary: str = Field("", description="Summary of the action output")
    decision_rationale: str = Field("", description="Rationale for the decision")
    human_override: bool = Field(False, description="Whether a human overrode the action")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/training-data", status_code=201)
def record_training_data(
    body: RecordTrainingDataRequest,
    svc: ProvenanceService = Depends(get_provenance_service),
):
    """Record a training data source for an agent (Article 10 compliance)."""
    result = svc.record_training_data(
        agent_id=body.agent_id,
        dataset_name=body.dataset_name,
        source_url=body.source_url,
        license=body.license,
        data_categories=body.data_categories,
        contains_personal_data=body.contains_personal_data,
        data_governance_measures=body.data_governance_measures,
    )
    if isinstance(result, dict) and "error" in result:
        logger.warning("Training data recording failed: %s", result["error"])
        raise HTTPException(status_code=400, detail="Training data recording failed")
    return result


@router.post("/model-lineage", status_code=201)
def record_model_lineage(
    body: RecordModelLineageRequest,
    svc: ProvenanceService = Depends(get_provenance_service),
):
    """Record model lineage chain for an agent (Article 11 compliance)."""
    result = svc.record_model_lineage(
        agent_id=body.agent_id,
        base_model=body.base_model,
        base_model_provider=body.base_model_provider,
        fine_tuning_method=body.fine_tuning_method,
        evaluation_metrics=body.evaluation_metrics,
    )
    if isinstance(result, dict) and "error" in result:
        logger.warning("Model lineage recording failed: %s", result["error"])
        raise HTTPException(status_code=400, detail="Model lineage recording failed")
    return result


@router.post("/actions", status_code=201)
def log_action(
    body: LogActionRequest,
    svc: ProvenanceService = Depends(get_provenance_service),
):
    """Log an agent action for Article 12 audit trail."""
    result = svc.log_action(
        agent_id=body.agent_id,
        action_type=body.action_type,
        input_summary=body.input_summary,
        output_summary=body.output_summary,
        decision_rationale=body.decision_rationale,
        human_override=body.human_override,
    )
    if isinstance(result, dict) and "error" in result:
        logger.warning("Action logging failed: %s", result["error"])
        raise HTTPException(status_code=400, detail="Action logging failed")
    return result


@router.get("/audit-trail/{agent_id}")
def get_audit_trail(
    agent_id: str,
    action_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 50,
    svc: ProvenanceService = Depends(get_provenance_service),
):
    """Query audit trail with filters."""
    results = svc.get_audit_trail(
        agent_id=agent_id,
        action_type=action_type,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )
    if results and isinstance(results[0], dict) and "error" in results[0]:
        logger.error("Audit trail query failed: %s", results[0]["error"])
        raise HTTPException(status_code=500, detail="Audit trail query failed")
    return results


@router.get("/{agent_id}")
def get_provenance(
    agent_id: str,
    svc: ProvenanceService = Depends(get_provenance_service),
):
    """Get full provenance record for an agent (training data, model lineage, audit summary)."""
    result = svc.get_provenance(agent_id)
    if isinstance(result, dict) and "error" in result:
        logger.error("Provenance lookup failed for %s: %s", agent_id, result["error"])
        raise HTTPException(status_code=500, detail="Provenance lookup failed")
    return result
