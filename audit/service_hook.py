"""Per-service audit-emission hook (T034 wiring helper).

This module is the thin glue the nine services use to emit exactly one
:class:`~audit.events.AuditEvent` per committed state change (create / issue /
revoke / update / record / anchor) without each service re-implementing the
emitter wiring or the error-swallowing contract.

Side-channel contract (CRITICAL): audit emission is a pure side effect. It MUST
NOT change a service method's return value, the exceptions it raises, or the
on-disk record format of the entity being mutated (audit events live in their own
``audit`` collection / file). If emitting an event fails, the failure is logged
and swallowed so the underlying operation — which has *already committed* — is
never broken (FR-018 only suppresses events for *failed* ops; a committed op whose
audit write fails still succeeds).

Tenant defaults to ``"default"`` (FR-011/FR-014), so a single-tenant self-host
install behaves exactly as v0.3.0: the only observable addition is an extra
hash-chained entry in the separate ``audit`` collection, which existing callers
do not read.
"""

from typing import Optional

from audit.emitter import AuditEventEmitter
from errors import ErrorCategory, log_and_format_error
from storage.repository import DEFAULT_TENANT


def resolve_emitter(emitter: Optional[AuditEventEmitter]) -> AuditEventEmitter:
    """Return ``emitter`` or the default Repository-backed local-sink emitter.

    The default constructs an :class:`AuditEventEmitter` over the shared default
    Repository (file storage for self-host), matching the DI seam described in the
    spec: services take an optional ``emitter`` and otherwise construct the local
    sink. Constructed per service instance so an injected non-default backend
    (e.g. Postgres + external sink) is honored when provided.
    """
    return emitter if emitter is not None else AuditEventEmitter()


def safe_emit(
    emitter: Optional[AuditEventEmitter],
    *,
    action: str,
    target_id: str,
    target_collection: str,
    actor: str,
    tenant_id: str = DEFAULT_TENANT,
    before: Optional[dict] = None,
    after: Optional[dict] = None,
) -> None:
    """Emit one audit event for a committed change, swallowing any failure.

    Call this only AFTER the underlying state change has committed. Any exception
    raised while building/persisting the event (e.g. a transient storage error on
    the audit collection) is logged via the centralized error taxonomy and then
    suppressed, so the side channel can never turn a successful operation into a
    failure or alter its result (side-channel contract above).
    """
    if emitter is None:
        return
    try:
        emitter.emit(
            action=action,
            target_id=target_id,
            target_collection=target_collection,
            actor=actor,
            tenant_id=tenant_id,
            before=before,
            after=after,
        )
    except Exception as exc:  # noqa: BLE001 - audit is a best-effort side channel
        # Never propagate: the mutating op already committed. Log for operators.
        log_and_format_error(
            "audit.safe_emit",
            exc,
            ErrorCategory.STORAGE,
            user_message="audit event emission failed (operation unaffected)",
            action=action,
            target_id=target_id,
        )
