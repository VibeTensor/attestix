"""Attestix audit - re-exports from the flat module for namespace compatibility.

    # Namespaced (recommended)
    from attestix.audit import AuditEvent, AuditEventEmitter, verify_chain

    # Flat (also supported)
    from audit import AuditEvent, AuditEventEmitter, verify_chain
"""

from audit import (
    AUDIT_COLLECTION,
    GENESIS_HASH,
    AuditEvent,
    AuditEventEmitter,
    compute_change_digest,
    verify_chain,
)

# Re-export submodules for `from attestix.audit.X import Y` parity.
from audit import events
from audit import emitter

__all__ = [
    "AuditEvent",
    "AuditEventEmitter",
    "AUDIT_COLLECTION",
    "GENESIS_HASH",
    "compute_change_digest",
    "verify_chain",
    "events",
    "emitter",
]
