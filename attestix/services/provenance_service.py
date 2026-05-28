"""Provenance service for Attestix.

Manages training data provenance, model lineage tracking, and
Article 12 EU AI Act automatic action logging (audit trail).
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from attestix.audit import AuditEventEmitter, resolve_emitter, safe_emit
from attestix.config import load_provenance, save_provenance
from attestix.errors import ErrorCategory, log_and_format_error
from attestix.signing import InProcessSigner, Signer
from attestix.storage.repository import DEFAULT_TENANT


VALID_ACTION_TYPES = {"inference", "delegation", "data_access", "external_call"}


class ProvenanceService:
    """Manages training data provenance, model lineage, and audit trails."""

    # Genesis hash for the first entry in a chain
    GENESIS_HASH = "0" * 64

    def __init__(
        self,
        signer: Optional[Signer] = None,
        emitter: Optional[AuditEventEmitter] = None,
        tenant_id: str = DEFAULT_TENANT,
    ):
        # v0.4.0: sign through the pluggable Signer seam (default = in-process
        # Ed25519, byte-for-byte identical to v0.3.0).
        self._signer = signer or InProcessSigner()
        self._server_did = self._signer.did
        # v0.4.0 (T033/T034): per-service audit emitter + tenant context. NOTE:
        # this service keeps its OWN hash-chained `audit_log` (Article 12) intact;
        # the shared AuditEvent emission here is the additive structured-audit
        # side channel and does not replace the existing provenance chain.
        self._emitter = resolve_emitter(emitter)
        self._tenant_id = tenant_id

    @staticmethod
    def _chain_hash(previous_hash: str, entry_data: dict) -> str:
        """Compute SHA-256 hash linking this entry to the previous one.

        Creates a tamper-evident chain: modifying any earlier entry
        invalidates all subsequent hashes.
        """
        canonical = json.dumps(entry_data, sort_keys=True, separators=(",", ":"))
        combined = f"{previous_hash}:{canonical}"
        return hashlib.sha256(combined.encode("utf-8")).hexdigest()

    def _get_last_chain_hash(self, audit_log: list, agent_id: str) -> str:
        """Get the chain_hash of the last audit entry for this agent."""
        for entry in reversed(audit_log):
            if entry["agent_id"] == agent_id and "chain_hash" in entry:
                return entry["chain_hash"]
        return self.GENESIS_HASH

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
            entry["signature"] = self._signer.sign(signable)

            data = load_provenance()
            data["entries"].append(entry)
            save_provenance(data)

            safe_emit(
                self._emitter,
                action="provenance.record_training_data",
                target_id=entry_id,
                target_collection="provenance",
                actor=self._server_did,
                tenant_id=self._tenant_id,
                after={"entry_id": entry_id, "agent_id": agent_id,
                       "entry_type": "training_data"},
            )

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
            entry["signature"] = self._signer.sign(signable)

            data = load_provenance()
            data["entries"].append(entry)
            save_provenance(data)

            safe_emit(
                self._emitter,
                action="provenance.record_model_lineage",
                target_id=entry_id,
                target_collection="provenance",
                actor=self._server_did,
                tenant_id=self._tenant_id,
                after={"entry_id": entry_id, "agent_id": agent_id,
                       "entry_type": "model_lineage"},
            )

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

            # Hash-chain: link this entry to the previous one for tamper evidence
            data = load_provenance()
            prev_hash = self._get_last_chain_hash(data["audit_log"], agent_id)
            log_entry["prev_hash"] = prev_hash
            log_entry["chain_hash"] = self._chain_hash(prev_hash, log_entry)

            signable = {k: v for k, v in log_entry.items() if k != "signature"}
            log_entry["signature"] = self._signer.sign(signable)

            data["audit_log"].append(log_entry)
            save_provenance(data)

            safe_emit(
                self._emitter,
                action="provenance.log_action",
                target_id=log_id,
                target_collection="provenance",
                actor=self._server_did,
                tenant_id=self._tenant_id,
                after={"log_id": log_id, "agent_id": agent_id,
                       "action_type": action_type},
            )

            return log_entry
        except Exception as e:
            msg = log_and_format_error(
                "log_action", e, ErrorCategory.PROVENANCE,
                agent_id=agent_id, action_type=action_type,
            )
            return {"error": msg}

    def get_provenance(self, agent_id: str) -> dict:
        """Get full provenance record for an agent (training data + model lineage + audit summary).

        v0.4.0-rc.3 (P0 #5 of the rc.2 RC validation): ``audit_log_count`` now
        reflects BOTH the legacy ``provenance.json::audit_log`` chain (written
        by :meth:`log_action`) AND the new ``audit.json::events`` chain
        (written by every ``record_*`` / ``create_*`` / ``issue_*`` / ``revoke_*``
        service method via the per-service audit emitter, plumbed through the
        Identity / Compliance / Credential / Reputation / Provenance / DID /
        AgentCard / Delegation / Blockchain services in #84).

        Cross-referencing audit events to a specific ``agent_id`` walks the
        owning collection (``identities`` / ``compliance`` / ``credentials`` /
        ``provenance`` / ``delegations`` / ``reputation`` / ``anchors``) to
        translate ``target_id`` into the underlying agent, because the audit
        event itself stores only the SHA-256 ``change_digest`` of the
        before/after diff — never the raw fields (cf.
        ``attestix/audit/events.py`` for the rationale; the digest is the
        tamper-evidence anchor and is NOT a queryable index).

        Previously the documented GRC quickstart ran the full workflow but
        reported ``audit_log_count: 0`` because nothing it called wrote to
        the legacy chain.
        """
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

            # v0.4.0-rc.3 (P0 #5): also count rows in the new audit collection
            # that pertain to this agent. Resolve ``target_id`` through each
            # owning collection so events like ``compliance.create_profile``
            # (target_id = profile_id) and ``credential.issue`` (target_id =
            # credential id) still attribute back to the correct agent.
            #
            # The whole block is wrapped in try/except so a missing /
            # unreadable audit.json never makes get_provenance fail — the
            # legacy chain remains the conservative fallback count.
            audit_events_count = 0
            audit_events_latest: list = []
            try:
                from attestix.config import (
                    AUDIT_FILE,
                    load_compliance,
                    load_credentials,
                )
                import json as _json

                # Build per-collection lookups (target_id -> agent_id) up-front
                # so each event is O(1) to attribute.
                related_target_ids: set = {agent_id}
                comp_data = load_compliance()
                for prof in comp_data.get("profiles", []):
                    if prof.get("agent_id") == agent_id:
                        related_target_ids.add(prof.get("profile_id", ""))
                for assess in comp_data.get("assessments", []):
                    if assess.get("agent_id") == agent_id:
                        related_target_ids.add(assess.get("assessment_id", ""))
                for decl in comp_data.get("declarations", []):
                    if decl.get("agent_id") == agent_id:
                        related_target_ids.add(decl.get("declaration_id", ""))
                cred_data = load_credentials()
                for cred in cred_data.get("credentials", []):
                    subj = (cred.get("credentialSubject") or {}).get("id")
                    if subj == agent_id:
                        related_target_ids.add(cred.get("id", ""))
                for entry in data.get("entries", []):
                    if entry.get("agent_id") == agent_id:
                        related_target_ids.add(entry.get("entry_id", ""))
                for ent in data.get("audit_log", []):
                    if ent.get("agent_id") == agent_id:
                        related_target_ids.add(ent.get("log_id", ""))
                related_target_ids.discard("")

                if AUDIT_FILE.exists():
                    audit_doc = _json.loads(AUDIT_FILE.read_text(encoding="utf-8"))
                    for ev in audit_doc.get("events", []):
                        if ev.get("target_id") in related_target_ids:
                            audit_events_count += 1
                            audit_events_latest.append(ev)
            except Exception:
                pass

            total = len(audit_entries) + audit_events_count
            latest = (audit_entries + audit_events_latest)[-5:]
            return {
                "agent_id": agent_id,
                "training_data": training_data,
                "model_lineage": model_lineage,
                "audit_log_count": total,
                "audit_chain_count_legacy": len(audit_entries),
                "audit_events_count": audit_events_count,
                "latest_audit_entries": latest,
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
