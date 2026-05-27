"""Structured audit events for Attestix (v0.4.0 extensibility layer, US2 / P2).

This package emits one tamper-evident :class:`AuditEvent` per committed state
change, chained with the same ``prev_hash`` / ``chain_hash`` / genesis pattern as
``services/provenance_service.py``. The default sink persists events locally
(through the configured :class:`~storage.Repository`); the hosted cloud injects an
external sink to feed its own hash-chained log (FR-017), while self-host behavior
is unchanged.
"""

from audit.events import (
    GENESIS_HASH,
    AuditEvent,
    compute_change_digest,
    verify_chain,
)
from audit.emitter import AUDIT_COLLECTION, AuditEventEmitter
from audit.service_hook import resolve_emitter, safe_emit

__all__ = [
    "AuditEvent",
    "AuditEventEmitter",
    "AUDIT_COLLECTION",
    "GENESIS_HASH",
    "compute_change_digest",
    "verify_chain",
    "resolve_emitter",
    "safe_emit",
]
