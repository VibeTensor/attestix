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

from attestix.auth.crypto import canonicalize_json
from attestix.storage.repository import DEFAULT_TENANT

#: Allowed values for :attr:`VerifyChainResult.broken_field`. Documented here so
#: downstream consumers (importer, CLI, third-party tooling) can branch on the
#: failure cause without re-parsing :attr:`VerifyChainResult.failure_reason`.
BROKEN_FIELD_PREV_HASH = "prev_hash"
BROKEN_FIELD_CHAIN_HASH = "chain_hash"
BROKEN_FIELD_TENANT_ID = "tenant_id"

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


@dataclass(frozen=True)
class VerifyChainResult:
    """Structured outcome of :func:`verify_chain` (forensic chain-tamper report).

    Returned by every call to :func:`verify_chain` from v0.4.0-rc.3 onward. The
    type implements ``__bool__`` so existing ``if verify_chain(...)`` /
    ``assert verify_chain(...)`` call-sites remain source-compatible — only
    callers that compared explicitly to ``True``/``False`` (``is True``,
    ``== False``) need updating to ``.valid`` access.

    Attributes
    ----------
    valid
        ``True`` iff the chain reconciled end-to-end.
    broken_event_id
        ``event_id`` of the first event whose check failed, or ``None`` on a
        clean pass. For chain-link breaks (``broken_field='prev_hash'``) this
        is the event whose stored ``prev_hash`` did **not** match the prior
        event's ``chain_hash``.
    broken_field
        One of :data:`BROKEN_FIELD_PREV_HASH`, :data:`BROKEN_FIELD_CHAIN_HASH`,
        :data:`BROKEN_FIELD_TENANT_ID`, or ``None`` on a clean pass. See
        :func:`verify_chain` for the discrimination order.
    failure_reason
        Short human-readable summary (hash hex truncated to 8 chars for
        readability). Intended for log/CLI display, not machine parsing —
        branch on ``broken_field`` for that.
    events_checked
        Count of events processed. On a clean pass this equals ``len(events)``;
        on failure it is the 1-based index of the failing event (i.e. how many
        events were touched before the abort), which gives the caller enough
        information to locate the break by position as well as by ``event_id``.
    """

    valid: bool
    broken_event_id: Optional[str] = None
    broken_field: Optional[str] = None
    failure_reason: Optional[str] = None
    events_checked: int = 0

    def __bool__(self) -> bool:  # pragma: no cover - trivial delegation
        return self.valid


def _short(h: str) -> str:
    """Truncate a hex digest to 8 chars for human-readable reasons."""
    if not isinstance(h, str):
        return repr(h)
    return h[:8] if len(h) > 8 else h


def _as_audit_event(ev) -> "AuditEvent":
    """Normalize an event input (AuditEvent instance or dict) to AuditEvent."""
    if isinstance(ev, AuditEvent):
        return ev
    return AuditEvent(**{k: ev[k] for k in _AUDIT_FIELDS})


def _recompute_chain_hash_with_tenant(
    event: "AuditEvent", tenant_id: str
) -> str:
    """Recompute ``event.chain_hash`` substituting ``tenant_id``.

    Used by :func:`verify_chain` to attribute a chain-hash mismatch to a
    ``tenant_id`` shift (cross-tenant import error) rather than to generic
    body tampering: if swapping the tenant string makes the recompute match,
    the chain was minted under a different tenant — that is the failure cause
    the importer wants to surface.
    """
    return AuditEvent._link_hash(
        event.prev_hash,
        event_id=event.event_id,
        tenant_id=tenant_id,
        actor=event.actor,
        action=event.action,
        target_id=event.target_id,
        target_collection=event.target_collection,
        occurred_at=event.occurred_at,
        change_digest=event.change_digest,
    )


def verify_chain(events) -> "VerifyChainResult":
    """Verify ``events`` form an unbroken hash chain (SC-007), with forensics.

    Each event's ``chain_hash`` MUST recompute from its fields, and each
    event's ``prev_hash`` MUST equal the prior event's ``chain_hash`` (the
    first event links to :data:`GENESIS_HASH`). Accepts :class:`AuditEvent`
    instances or plain dicts (e.g. records loaded back from storage).

    On the first mismatch, this returns a :class:`VerifyChainResult` with
    ``valid=False`` and ``broken_event_id`` / ``broken_field`` /
    ``failure_reason`` populated. The ``__bool__`` of the result mirrors
    ``valid`` so legacy boolean call-sites (``if verify_chain(events): ...``)
    keep working unchanged.

    Discrimination order (the first check that fires wins):

    1. ``prev_hash`` — the stored ``prev_hash`` does not match the expected
       prior chain_hash (or, at index 0, does not match :data:`GENESIS_HASH`).
       This is a *chain-link* break: someone reordered, dropped, or inserted
       events.
    2. ``tenant_id`` — the ``prev_hash`` reconciled, but the recomputed
       ``chain_hash`` only matches when the event's ``tenant_id`` is swapped
       for the prior event's (or, at index 0, for the next event's) tenant
       string. This indicates a cross-tenant import error: the row body was
       hashed under a different tenant_id than the one now stored.
    3. ``chain_hash`` — generic body tampering: the recompute does not match
       even after the ``tenant_id`` shift check, so some non-tenant field in
       the canonical body (``actor``, ``action``, ``target_id``,
       ``target_collection``, ``occurred_at``, ``change_digest``,
       ``event_id``) has drifted from what was signed into the chain.

    ``broken_field`` values are constants exported alongside this function
    (:data:`BROKEN_FIELD_PREV_HASH`, :data:`BROKEN_FIELD_CHAIN_HASH`,
    :data:`BROKEN_FIELD_TENANT_ID`).
    """
    expected_prev = GENESIS_HASH
    prior_tenant: Optional[str] = None
    events_list = list(events)
    for i, ev in enumerate(events_list):
        event = _as_audit_event(ev)

        # (1) prev_hash / genesis link check.
        if event.prev_hash != expected_prev:
            if i == 0:
                reason = (
                    f"genesis prev_hash != 64-zero "
                    f"(got={_short(event.prev_hash)})"
                )
            else:
                reason = (
                    f"prev_hash mismatch at event_id="
                    f"{_short(event.event_id)} "
                    f"(expected={_short(expected_prev)} "
                    f"got={_short(event.prev_hash)})"
                )
            return VerifyChainResult(
                valid=False,
                broken_event_id=event.event_id,
                broken_field=BROKEN_FIELD_PREV_HASH,
                failure_reason=reason,
                events_checked=i + 1,
            )

        # (2) chain_hash recompute check, with tenant-shift attribution.
        recomputed = event.recompute_chain_hash()
        if recomputed != event.chain_hash:
            # Try to attribute to a tenant_id shift before falling back to a
            # generic chain_hash mismatch. Use the prior event's tenant_id
            # when available, or scan the rest of the chain for a sibling
            # tenant when we are at index 0.
            tenant_candidate: Optional[str] = None
            if prior_tenant is not None and prior_tenant != event.tenant_id:
                tenant_candidate = prior_tenant
            elif i == 0:
                for sibling in events_list[1:]:
                    sib = _as_audit_event(sibling)
                    if sib.tenant_id != event.tenant_id:
                        tenant_candidate = sib.tenant_id
                        break

            if tenant_candidate is not None:
                shifted = _recompute_chain_hash_with_tenant(
                    event, tenant_candidate
                )
                if shifted == event.chain_hash:
                    reason = (
                        f"tenant_id mismatch at event_id="
                        f"{_short(event.event_id)} "
                        f"(stored={event.tenant_id!r} "
                        f"chain-hashed-under={tenant_candidate!r})"
                    )
                    return VerifyChainResult(
                        valid=False,
                        broken_event_id=event.event_id,
                        broken_field=BROKEN_FIELD_TENANT_ID,
                        failure_reason=reason,
                        events_checked=i + 1,
                    )

            reason = (
                f"chain_hash mismatch at event_id="
                f"{_short(event.event_id)} "
                f"(expected={_short(event.chain_hash)} "
                f"got={_short(recomputed)})"
            )
            return VerifyChainResult(
                valid=False,
                broken_event_id=event.event_id,
                broken_field=BROKEN_FIELD_CHAIN_HASH,
                failure_reason=reason,
                events_checked=i + 1,
            )

        expected_prev = event.chain_hash
        prior_tenant = event.tenant_id

    return VerifyChainResult(
        valid=True,
        broken_event_id=None,
        broken_field=None,
        failure_reason=None,
        events_checked=len(events_list),
    )
