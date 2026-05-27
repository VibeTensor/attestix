"""Structured audit events + hash chaining (data-model.md §4, FR-015…FR-018).

An :class:`AuditEvent` is the structured record of a single committed state change
(create / update / delete / revoke). A sequence of events is chained into a
tamper-evident log using the **same** ``prev_hash`` / ``chain_hash`` / genesis
pattern already proven in ``services/provenance_service.py`` — this module reuses
that approach rather than inventing a new one.

Chaining is per ``(tenant_id, ...)`` scope as decided by the emitter; tampering
with any event breaks every subsequent ``chain_hash`` (FR-016, SC-007).

Determinism / canonicalization reuses ``auth.crypto.canonicalize_json`` (RFC 8785
JCS), the same helper the signer uses, so event hashes are stable across runs and
platforms (data-model §Conventions).

PII / encryption-at-rest (FR-028): ``actor`` (an identity / DID) and ``target_id``
may constitute personal data under DPDP Act 2023 §2(t) and GDPR Art.4(1). The
default **file** Repository (the self-host / dev default) stores these events as
**plaintext JSON on disk**; hash-chaining provides tamper-evidence, NOT
confidentiality. Any production / multi-tenant deployment persisting AuditEvents
MUST use an encrypted-at-rest Repository (e.g. Postgres + KMS / disk-level at-rest
encryption). No raw secret / private-key material is ever placed in the event body
(principle VI): ``change_digest`` is a SHA-256 over the JCS-canonical change, not
the change itself.
"""

import hashlib
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Optional

from auth.crypto import canonicalize_json
from storage.repository import DEFAULT_TENANT

#: Genesis hash for the first event in a chain. Matches the provenance precedent
#: (``ProvenanceService.GENESIS_HASH``): 64 hex zeros (the hex width of SHA-256).
GENESIS_HASH = "0" * 64


def _now_iso() -> str:
    """UTC ISO-8601 timestamp, matching the existing services."""
    return datetime.now(timezone.utc).isoformat()


def compute_change_digest(before: Optional[dict], after: Optional[dict]) -> str:
    """SHA-256 over the JCS-canonical form of ``{before?, after}`` (data-model §4).

    ``before`` is omitted for creates; ``after`` is omitted (``None``) for deletes.
    No raw secret material is included — this digests the change, it does not store
    it.
    """
    payload: dict = {}
    if before is not None:
        payload["before"] = before
    payload["after"] = after
    return hashlib.sha256(canonicalize_json(payload)).hexdigest()


@dataclass(frozen=True)
class AuditEvent:
    """One committed state change, linkable into a tamper-evident chain.

    Fields mirror the provenance hash-chain shape (data-model.md §4). The class is
    frozen so a constructed event cannot be mutated after its ``chain_hash`` is
    computed.
    """

    event_id: str           # e.g. "evt:<uuid12>"
    tenant_id: str          # default "default"
    actor: str              # acting identity / DID (server DID or caller)
    action: str             # e.g. "identity.create", "credential.revoke"
    target_id: str          # id of the affected resource
    target_collection: str  # e.g. "identities"
    occurred_at: str        # ISO-8601 UTC
    change_digest: str      # SHA-256 over JCS-canonical {before?, after}
    prev_hash: str          # chain_hash of the prior event (GENESIS for first)
    chain_hash: str         # SHA-256 linking this event to prev_hash

    @staticmethod
    def _link_hash(
        prev_hash: str,
        *,
        event_id: str,
        tenant_id: str,
        actor: str,
        action: str,
        target_id: str,
        target_collection: str,
        occurred_at: str,
        change_digest: str,
    ) -> str:
        """Compute the chain_hash linking this event to ``prev_hash``.

        Hashes the JCS-canonical form of the fully-specified event body (minus the
        chain_hash itself) prefixed by ``prev_hash``, so any tampering with any
        field or any earlier event invalidates the chain — the same property as
        ``ProvenanceService._chain_hash``.
        """
        body = {
            "event_id": event_id,
            "tenant_id": tenant_id,
            "actor": actor,
            "action": action,
            "target_id": target_id,
            "target_collection": target_collection,
            "occurred_at": occurred_at,
            "change_digest": change_digest,
            "prev_hash": prev_hash,
        }
        combined = prev_hash.encode("utf-8") + b":" + canonicalize_json(body)
        return hashlib.sha256(combined).hexdigest()

    @classmethod
    def create(
        cls,
        *,
        action: str,
        target_id: str,
        target_collection: str,
        actor: str,
        tenant_id: str = DEFAULT_TENANT,
        before: Optional[dict] = None,
        after: Optional[dict] = None,
        prev_hash: str = GENESIS_HASH,
        occurred_at: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> "AuditEvent":
        """Build a chained :class:`AuditEvent` for a committed change.

        ``prev_hash`` is the ``chain_hash`` of the previous event in scope (or
        :data:`GENESIS_HASH` for the first). The ``change_digest`` is derived from
        ``before`` / ``after``; pass neither for a pure action with no body diff.
        """
        eid = event_id or f"evt:{uuid.uuid4().hex[:12]}"
        ts = occurred_at or _now_iso()
        digest = compute_change_digest(before, after)
        chain_hash = cls._link_hash(
            prev_hash,
            event_id=eid,
            tenant_id=tenant_id,
            actor=actor,
            action=action,
            target_id=target_id,
            target_collection=target_collection,
            occurred_at=ts,
            change_digest=digest,
        )
        return cls(
            event_id=eid,
            tenant_id=tenant_id,
            actor=actor,
            action=action,
            target_id=target_id,
            target_collection=target_collection,
            occurred_at=ts,
            change_digest=digest,
            prev_hash=prev_hash,
            chain_hash=chain_hash,
        )

    def to_dict(self) -> dict:
        """Plain-dict form for persistence / transport (JSON-serializable)."""
        return asdict(self)

    def recompute_chain_hash(self) -> str:
        """Recompute this event's chain_hash from its own fields.

        Verification helper: a stored event is intact iff this equals the stored
        :attr:`chain_hash`.
        """
        return self._link_hash(
            self.prev_hash,
            event_id=self.event_id,
            tenant_id=self.tenant_id,
            actor=self.actor,
            action=self.action,
            target_id=self.target_id,
            target_collection=self.target_collection,
            occurred_at=self.occurred_at,
            change_digest=self.change_digest,
        )


def verify_chain(events) -> bool:
    """Return ``True`` iff ``events`` form an unbroken hash chain (SC-007).

    Each event's ``chain_hash`` MUST recompute from its fields, and each event's
    ``prev_hash`` MUST equal the prior event's ``chain_hash`` (the first event
    links to :data:`GENESIS_HASH`). Accepts :class:`AuditEvent` instances or plain
    dicts (e.g. records loaded back from storage).
    """
    expected_prev = GENESIS_HASH
    for ev in events:
        if isinstance(ev, AuditEvent):
            event = ev
        else:
            event = AuditEvent(**{k: ev[k] for k in _AUDIT_FIELDS})
        if event.prev_hash != expected_prev:
            return False
        if event.recompute_chain_hash() != event.chain_hash:
            return False
        expected_prev = event.chain_hash
    return True


_AUDIT_FIELDS = (
    "event_id",
    "tenant_id",
    "actor",
    "action",
    "target_id",
    "target_collection",
    "occurred_at",
    "change_digest",
    "prev_hash",
    "chain_hash",
)
