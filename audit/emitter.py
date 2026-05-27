"""Audit event emitter: local sink + injectable external sink (FR-015…FR-018).

``AuditEventEmitter`` is the seam that turns a committed state change into exactly
one chained :class:`~audit.events.AuditEvent` (FR-015) and routes it to a sink.

- **Default (self-host)**: a local sink that appends the event to an ``audit``
  collection in the configured :class:`~storage.Repository`, computing
  ``prev_hash`` / ``chain_hash`` per tenant by reading the last event in that
  tenant's chain — preserving today's local audit behavior.
- **External (cloud)**: an integrator injects a ``sink`` callable
  (``Callable[[AuditEvent], None]``) so the hosted product can feed an external
  hash-chained log (FR-017). The emitter still computes the chain locally so the
  chain is verifiable regardless of sink.

No-op-update decision (T046): the emitter emits one event per *committed*
mutating operation, including a no-op update (an update that changes nothing). The
``change_digest`` captures before/after, so a downstream consumer can detect a
no-op without the engine having to special-case suppression in every service —
keeping "exactly one event per state-changing operation" (FR-015) simple and
uniform. A *failed* operation emits no event (FR-018): the caller only emits after
the Repository write commits.
"""

import threading
from typing import Callable, List, Optional

from audit.events import GENESIS_HASH, AuditEvent
from storage import Repository, default_repository
from storage.repository import DEFAULT_TENANT

#: The collection AuditEvents are persisted to by the default local sink.
AUDIT_COLLECTION = "audit"


class AuditEventEmitter:
    """Emit exactly one chained :class:`AuditEvent` per committed change.

    Construct with no arguments for the self-host default (events persisted to the
    default file Repository's ``audit`` collection). Inject ``repository`` to use a
    different backend (e.g. Postgres), and/or ``sink`` to additionally forward each
    event to an external consumer (the cloud's hash-chained log, FR-017).
    """

    def __init__(
        self,
        repository: Optional[Repository] = None,
        sink: Optional[Callable[[AuditEvent], None]] = None,
    ) -> None:
        self._repo = repository or default_repository()
        self._sink = sink
        # Serialize chain computation within this process so two threads reading
        # the same tenant's last hash cannot both append off the same prev_hash.
        # (The file Repository's own filelock guards cross-process atomicity; this
        # guards in-process emitters sharing one Repository instance.)
        self._lock = threading.Lock()

    def _last_chain_hash(self, tenant_id: str) -> str:
        """Return the chain_hash of the most recent event in ``tenant_id``'s chain.

        Falls back to :data:`GENESIS_HASH` when the tenant has no events yet. The
        Repository scopes ``list`` by tenant, so cross-tenant events never enter
        this chain (each tenant has its own chain, data-model §4).
        """
        events = self._repo.list(
            AUDIT_COLLECTION, tenant_id=tenant_id, id_field="event_id"
        )
        if not events:
            return GENESIS_HASH
        # Events are appended in order; the last persisted is the chain head.
        return events[-1].get("chain_hash", GENESIS_HASH)

    def emit(
        self,
        *,
        action: str,
        target_id: str,
        target_collection: str,
        actor: str,
        tenant_id: str = DEFAULT_TENANT,
        before: Optional[dict] = None,
        after: Optional[dict] = None,
    ) -> AuditEvent:
        """Build, persist, and forward one chained event for a committed change.

        Returns the emitted :class:`AuditEvent`. MUST be called only after the
        underlying state change has committed (FR-018): a caller that catches a
        write failure must not call ``emit``.
        """
        with self._lock:
            prev_hash = self._last_chain_hash(tenant_id)
            event = AuditEvent.create(
                action=action,
                target_id=target_id,
                target_collection=target_collection,
                actor=actor,
                tenant_id=tenant_id,
                before=before,
                after=after,
                prev_hash=prev_hash,
            )
            # Persist to the local sink (the audit collection) first so the
            # chain is durable, then forward to any external sink.
            self._repo.create(
                AUDIT_COLLECTION,
                event.to_dict(),
                tenant_id=tenant_id,
                id_field="event_id",
            )
        if self._sink is not None:
            self._sink(event)
        return event

    def read_chain(self, tenant_id: str = DEFAULT_TENANT) -> List[AuditEvent]:
        """Return this tenant's persisted events in chain order (verification)."""
        records = self._repo.list(
            AUDIT_COLLECTION, tenant_id=tenant_id, id_field="event_id"
        )
        return [
            AuditEvent(
                event_id=r["event_id"],
                tenant_id=r["tenant_id"],
                actor=r["actor"],
                action=r["action"],
                target_id=r["target_id"],
                target_collection=r["target_collection"],
                occurred_at=r["occurred_at"],
                change_digest=r["change_digest"],
                prev_hash=r["prev_hash"],
                chain_hash=r["chain_hash"],
            )
            for r in records
        ]
