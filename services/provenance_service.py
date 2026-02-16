"""Provenance service for AURA Protocol.

Manages training data provenance, model lineage tracking, and
Article 12 EU AI Act automatic action logging (audit trail).
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from auth.crypto import load_or_create_signing_key, sign_json_payload
from config import load_provenance, save_provenance
from errors import ErrorCategory, log_and_format_error


VALID_ACTION_TYPES = {"inference", "delegation", "data_access", "external_call"}


class ProvenanceService:
    """Manages training data provenance, model lineage, and audit trails."""

    def __init__(self):
        self._private_key, self._server_did = load_or_create_signing_key()

    def record_training_data(
        self,
        agent_id: str,
        dataset_name: str,
        source_url: str = "",
        license: str = "",
        data_categories: Optional[List[str]] = None,
        contains_personal_data: bool = False,
        data_governance_measures: str = "",
    ) -> dict:
        """Record a training data source for an agent (Article 10 compliance)."""
        try:
            entry_id = f"prov:{uuid.uuid4().hex[:12]}"
            now = datetime.now(timezone.utc).isoformat()

            entry = {
                "entry_id": entry_id,
                "entry_type": "training_data",
                "agent_id": agent_id,
                "dataset_name": dataset_name,
                "source_url": source_url,
                "license": license,
                "data_categories": data_categories or [],
                "contains_personal_data": contains_personal_data,
                "data_governance_measures": data_governance_measures,
                "recorded_at": now,
                "recorded_by": self._server_did,
            }

            signable = {k: v for k, v in entry.items() if k != "signature"}
            entry["signature"] = sign_json_payload(self._private_key, signable)

            data = load_provenance()
            data["entries"].append(entry)
            save_provenance(data)

            return entry
        except Exception as e:
            msg = log_and_format_error(
                "record_training_data", e, ErrorCategory.PROVENANCE,
                agent_id=agent_id, dataset_name=dataset_name,
            )
            return {"error": msg}

    def record_model_lineage(
        self,
        agent_id: str,
        base_model: str,
        base_model_provider: str = "",
        fine_tuning_method: str = "",
        evaluation_metrics: Optional[Dict] = None,
    ) -> dict:
        """Record model lineage chain for an agent (Article 11 compliance)."""
        try:
            entry_id = f"prov:{uuid.uuid4().hex[:12]}"
            now = datetime.now(timezone.utc).isoformat()

            entry = {
                "entry_id": entry_id,
                "entry_type": "model_lineage",
                "agent_id": agent_id,
                "base_model": base_model,
                "base_model_provider": base_model_provider,
                "fine_tuning_method": fine_tuning_method,
                "evaluation_metrics": evaluation_metrics or {},
                "recorded_at": now,
                "recorded_by": self._server_did,
            }

            signable = {k: v for k, v in entry.items() if k != "signature"}
            entry["signature"] = sign_json_payload(self._private_key, signable)

            data = load_provenance()
            data["entries"].append(entry)
            save_provenance(data)

            return entry
        except Exception as e:
            msg = log_and_format_error(
                "record_model_lineage", e, ErrorCategory.PROVENANCE,
                agent_id=agent_id, base_model=base_model,
            )
            return {"error": msg}

    def log_action(
        self,
        agent_id: str,
        action_type: str,
        input_summary: str = "",
        output_summary: str = "",
        decision_rationale: str = "",
        human_override: bool = False,
    ) -> dict:
        """Log an agent action for Article 12 audit trail."""
        try:
            if action_type not in VALID_ACTION_TYPES:
                return {
                    "error": f"Invalid action_type '{action_type}'. "
                    f"Must be one of: {', '.join(sorted(VALID_ACTION_TYPES))}"
                }

            log_id = f"audit:{uuid.uuid4().hex[:12]}"
            now = datetime.now(timezone.utc).isoformat()

            log_entry = {
                "log_id": log_id,
                "agent_id": agent_id,
                "action_type": action_type,
                "input_summary": input_summary,
                "output_summary": output_summary,
                "decision_rationale": decision_rationale,
                "human_override": human_override,
                "timestamp": now,
                "logged_by": self._server_did,
            }

            signable = {k: v for k, v in log_entry.items() if k != "signature"}
            log_entry["signature"] = sign_json_payload(self._private_key, signable)

            data = load_provenance()
            data["audit_log"].append(log_entry)
            save_provenance(data)

            return log_entry
        except Exception as e:
            msg = log_and_format_error(
                "log_action", e, ErrorCategory.PROVENANCE,
                agent_id=agent_id, action_type=action_type,
            )
            return {"error": msg}

    def get_provenance(self, agent_id: str) -> dict:
        """Get full provenance record for an agent (training data + model lineage + audit summary)."""
        try:
            data = load_provenance()

            training_data = [
                e for e in data["entries"]
                if e["agent_id"] == agent_id and e["entry_type"] == "training_data"
            ]
            model_lineage = [
                e for e in data["entries"]
                if e["agent_id"] == agent_id and e["entry_type"] == "model_lineage"
            ]
            audit_entries = [
                e for e in data["audit_log"]
                if e["agent_id"] == agent_id
            ]

            return {
                "agent_id": agent_id,
                "training_data": training_data,
                "model_lineage": model_lineage,
                "audit_log_count": len(audit_entries),
                "latest_audit_entries": audit_entries[-5:] if audit_entries else [],
            }
        except Exception as e:
            msg = log_and_format_error(
                "get_provenance", e, ErrorCategory.PROVENANCE,
                agent_id=agent_id,
            )
            return {"error": msg}

    def get_audit_trail(
        self,
        agent_id: str,
        action_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 50,
    ) -> List[dict]:
        """Query audit trail with filters."""
        try:
            data = load_provenance()
            results = []

            for entry in data["audit_log"]:
                if entry["agent_id"] != agent_id:
                    continue
                if action_type and entry.get("action_type") != action_type:
                    continue
                if start_date:
                    if entry["timestamp"] < start_date:
                        continue
                if end_date:
                    if entry["timestamp"] > end_date:
                        continue
                results.append(entry)
                if len(results) >= limit:
                    break

            return results
        except Exception as e:
            msg = log_and_format_error(
                "get_audit_trail", e, ErrorCategory.PROVENANCE,
                agent_id=agent_id,
            )
            return [{"error": msg}]
