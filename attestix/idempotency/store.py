"""Idempotency store + helper (data-model.md §5, FR-019…FR-023, FR-029).

A client-supplied idempotency key makes a write replay-safe for 24 hours
(Stripe-style). This module provides:

- :class:`IdempotencyStore` — the ABC (the seam an alternative backend implements).
- :class:`RepositoryIdempotencyStore` — the default, persisting keys through the
  configured :class:`~storage.Repository` (so self-host uses file storage and the
  cloud uses Postgres automatically), with a 24h TTL enforced on read plus a
  reclaim method.
- :func:`request_fingerprint` — a stable SHA-256 over the JCS-canonical request,
  used to detect a same-key/different-payload conflict.
- :func:`run_idempotent` — the reusable helper that wires reserve → execute →
  record around any write callable, usable from the REST middleware, an MCP tool,
  or a direct service call (surface-agnostic; the REST middleware is the documented
  primary boundary — see :mod:`idempotency.middleware`).

Decisions encoded here (T046):

- **Concurrency (default file store)**: first-writer-wins via the file
  Repository's existing ``filelock`` + atomic rename. The helper reserves the key
  (writes an ``in_progress`` record) before executing; a concurrent same-key call
  that observes a non-expired record does NOT re-execute. Guarantees beyond
  single-process first-writer-wins are out of scope for the default impl.
- **Scope**: the store + helper are surface-agnostic; the REST ``Idempotency-Key``
  header is the primary documented boundary, but MCP/direct callers may use the
  same helper.

Sensitive-data minimization (FR-029): the stored response MUST NOT contain raw
private key material and SHOULD be a minimal representation — ``status`` +
``resource_id`` + ``response_hash`` (SHA-256 over the JCS-canonical original
response). :func:`minimal_stored_response` builds exactly that, so a second
unencrypted copy of a signed VC / identity is never persisted for the TTL window.
"""

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Optional, Tuple

from attestix.auth.crypto import canonicalize_json
from attestix.errors import ErrorCategory
from attestix.storage import Repository, default_repository
from attestix.storage.repository import DEFAULT_TENANT

#: The collection idempotency keys are persisted to via the Repository.
IDEMPOTENCY_COLLECTION = "idempotency"

#: TTL for an idempotency record (FR-021): 24 hours from creation.
TTL = timedelta(hours=24)

STATUS_IN_PROGRESS = "in_progress"
STATUS_COMPLETED = "completed"


class IdempotencyConflictError(Exception):
    """Raised when a key is reused with a different request payload (FR-020).

    The REST boundary maps this to an HTTP 409. The ``category`` mirrors the
    engine's centralized error taxonomy (``ErrorCategory.IDEMPOTENCY``).
    """

    category = ErrorCategory.IDEMPOTENCY


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _parse(ts: str) -> datetime:
    dt = datetime.fromisoformat(ts)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def request_fingerprint(payload: Any) -> str:
    """SHA-256 over the JCS-canonical request payload (data-model §5).

    Two requests with the same key but different fingerprints are a conflict
    (FR-020). ``payload`` is typically ``{"method", "path", "body"}`` at the REST
    boundary, or the call arguments for a direct/MCP caller.
    """
    return hashlib.sha256(canonicalize_json({"req": payload})).hexdigest()


def response_hash(response: Any) -> str:
    """SHA-256 over the JCS-canonical original response (minimal-rep component)."""
    return hashlib.sha256(canonicalize_json({"resp": response})).hexdigest()


def minimal_stored_response(
    response: Any,
    *,
    status: Any = None,
    resource_id: Optional[str] = None,
) -> dict:
    """Build the FR-029 minimal stored representation of a response.

    Stores only ``status`` + ``resource_id`` + ``response_hash`` — never the raw
    response body (which may carry a signed VC / identity data). The hash lets a
    replay confirm it is returning the same logical result without keeping a second
    unencrypted copy of sensitive material for 24h.

    Use this for *direct/MCP* callers (:func:`run_idempotent`), which return the
    live result object on the first call and only need the minimal receipt to prove
    a replay is the same logical result. The REST boundary, by contrast, must echo
    the original HTTP body verbatim on a retry (a client that retries cannot re-read
    the first call's in-memory result), so it uses
    :func:`replayable_stored_response`.
    """
    return {
        "status": status,
        "resource_id": resource_id,
        "response_hash": response_hash(response),
    }


def replayable_stored_response(
    *,
    status_code: int,
    body: bytes,
    media_type: Optional[str] = None,
) -> dict:
    """Build the REST replay representation: the original HTTP response, verbatim.

    Unlike :func:`minimal_stored_response` (a receipt), this persists the original
    status code, body bytes, and content type so a retry with the same
    ``Idempotency-Key`` is *indistinguishable* from the first success — the client's
    ``resp.json()["agent_id"]`` works on the retry (v0.4.0-rc.5 P1 fix; previously
    the replay returned a ``{"idempotent_replay": …}`` receipt envelope and the
    ``agent_id`` was lost).

    Sensitive-data note (FR-029): the body is the *exact same JSON the client just
    received over the wire on the first call* — no new secret is exposed by storing
    it that the client did not already hold. ``response_hash`` is retained so the
    integrity check still holds. Persisting the raw private signing key is still
    avoided because the REST response itself never contains it (signatures are
    public).
    """
    text = body.decode("utf-8", "replace")
    return {
        "status": status_code,
        "media_type": media_type,
        "body": text,
        "response_hash": response_hash({"status": status_code, "body": text}),
    }


class IdempotencyStore:
    """Persistence seam for idempotency records (the alternative-backend ABC).

    The default :class:`RepositoryIdempotencyStore` satisfies this; a cloud impl
    may back it with Postgres + RLS. All records are scoped per tenant (FR-023).
    """

    def get(self, key: str, *, tenant_id: str = DEFAULT_TENANT) -> Optional[dict]:
        raise NotImplementedError

    def put(self, record: dict, *, tenant_id: str = DEFAULT_TENANT) -> dict:
        raise NotImplementedError

    def update(self, key: str, record: dict, *, tenant_id: str = DEFAULT_TENANT) -> dict:
        raise NotImplementedError

    def reclaim_expired(self, *, tenant_id: Optional[str] = None) -> int:
        raise NotImplementedError


class RepositoryIdempotencyStore(IdempotencyStore):
    """Default idempotency store backed by the configured Repository (FR-021).

    Records live in the ``idempotency`` collection keyed by ``key`` within a
    tenant. TTL is enforced on read: a record older than 24h is treated as absent
    (so the write proceeds as new), and :meth:`reclaim_expired` purges them so the
    store does not grow unbounded.
    """

    ID_FIELD = "key"

    def __init__(self, repository: Optional[Repository] = None) -> None:
        self._repo = repository or default_repository()

    def _is_expired(self, record: dict, *, now: Optional[datetime] = None) -> bool:
        now = now or _now()
        try:
            created = _parse(record["created_at"])
        except (KeyError, ValueError):
            return True
        return now - created >= TTL

    def get(self, key: str, *, tenant_id: str = DEFAULT_TENANT) -> Optional[dict]:
        """Return the live (non-expired) record for ``key``, else ``None`` (FR-021)."""
        record = self._repo.get(
            IDEMPOTENCY_COLLECTION, key, tenant_id=tenant_id, id_field=self.ID_FIELD
        )
        if record is None:
            return None
        if self._is_expired(record):
            # Expired: treat as new. Purge opportunistically so a replay past TTL
            # starts a fresh record rather than colliding on the stale id.
            self._repo.delete(
                IDEMPOTENCY_COLLECTION, key, tenant_id=tenant_id, id_field=self.ID_FIELD
            )
            return None
        return record

    def put(self, record: dict, *, tenant_id: str = DEFAULT_TENANT) -> dict:
        return self._repo.create(
            IDEMPOTENCY_COLLECTION, record, tenant_id=tenant_id, id_field=self.ID_FIELD
        )

    def update(self, key: str, record: dict, *, tenant_id: str = DEFAULT_TENANT) -> dict:
        return self._repo.update(
            IDEMPOTENCY_COLLECTION, key, record, tenant_id=tenant_id, id_field=self.ID_FIELD
        )

    def reclaim_expired(self, *, tenant_id: Optional[str] = None) -> int:
        """Purge expired records (TTL cleanup, FR-021). Returns the count removed.

        With ``tenant_id`` set, only that tenant is reclaimed. The default file
        store lists per tenant, so a caller reclaiming all tenants iterates the
        tenants it knows; the cloud's Postgres impl can reclaim with a single
        ``DELETE ... WHERE created_at < now() - interval '24h'``.
        """
        scopes = [tenant_id] if tenant_id is not None else [DEFAULT_TENANT]
        removed = 0
        for scope in scopes:
            for record in self._repo.list(
                IDEMPOTENCY_COLLECTION, tenant_id=scope, id_field=self.ID_FIELD
            ):
                if self._is_expired(record):
                    if self._repo.delete(
                        IDEMPOTENCY_COLLECTION,
                        record[self.ID_FIELD],
                        tenant_id=scope,
                        id_field=self.ID_FIELD,
                    ):
                        removed += 1
        return removed


def run_idempotent(
    store: IdempotencyStore,
    key: Optional[str],
    payload: Any,
    execute: Callable[[], Any],
    *,
    tenant_id: str = DEFAULT_TENANT,
    summarize: Optional[Callable[[Any], Tuple[Any, Optional[str]]]] = None,
) -> Tuple[Any, bool]:
    """Run ``execute`` at most once per ``(tenant_id, key)`` within the TTL.

    Returns ``(result_or_stored_response, replayed)``:

    - ``key is None`` → no bookkeeping; ``execute()`` runs and ``replayed`` is
      ``False`` (FR-022, exact v0.3.0 behavior).
    - First use of ``key`` → reserve (``in_progress``), run ``execute()``, store the
      FR-029 minimal representation, mark ``completed``; ``replayed`` is ``False``.
    - Replay within TTL, same fingerprint → return the stored minimal response;
      ``execute()`` does NOT run; ``replayed`` is ``True`` (FR-019).
    - Same key, different fingerprint → :class:`IdempotencyConflictError` (FR-020).
    - Record past 24h TTL → treated as new; ``execute()`` runs (FR-021).

    ``summarize`` optionally maps the raw result to ``(status, resource_id)`` for
    the stored minimal representation; if omitted, ``status``/``resource_id`` are
    ``None`` and only the ``response_hash`` is stored.
    """
    if key is None:
        return execute(), False

    fingerprint = request_fingerprint(payload)
    existing = store.get(key, tenant_id=tenant_id)
    if existing is not None:
        if existing.get("request_fingerprint") != fingerprint:
            raise IdempotencyConflictError(
                f"Idempotency key {key!r} was already used with a different request "
                f"payload; refusing to overwrite the prior result."
            )
        if existing.get("status") == STATUS_COMPLETED:
            return existing.get("stored_response"), True
        # in_progress: a concurrent/earlier attempt holds the key. First-writer
        # wins; we do not re-execute. Return the in-progress marker so the caller
        # can surface a 409-style "request in flight" rather than duplicating.
        raise IdempotencyConflictError(
            f"Idempotency key {key!r} is already in progress; not re-executing."
        )

    # First writer: reserve the key, then execute.
    store.put(
        {
            "key": key,
            "tenant_id": tenant_id,
            "request_fingerprint": fingerprint,
            "stored_response": None,
            "status": STATUS_IN_PROGRESS,
            "created_at": _now().isoformat(),
        },
        tenant_id=tenant_id,
    )
    result = execute()

    status, resource_id = (None, None)
    if summarize is not None:
        status, resource_id = summarize(result)
    stored = minimal_stored_response(result, status=status, resource_id=resource_id)

    store.update(
        key,
        {
            "key": key,
            "tenant_id": tenant_id,
            "request_fingerprint": fingerprint,
            "stored_response": stored,
            "status": STATUS_COMPLETED,
            # Preserve the original creation time so the TTL is measured from the
            # first attempt, not from completion.
            "created_at": existing["created_at"] if existing else _reserved_created_at(store, key, tenant_id),
        },
        tenant_id=tenant_id,
    )
    return result, False


def _reserved_created_at(store: IdempotencyStore, key: str, tenant_id: str) -> str:
    """Return the created_at of the just-reserved record (TTL anchored to reserve)."""
    record = store.get(key, tenant_id=tenant_id)
    if record and "created_at" in record:
        return record["created_at"]
    return _now().isoformat()
