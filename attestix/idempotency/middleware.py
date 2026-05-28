"""REST ``Idempotency-Key`` middleware (data-model.md §5 boundary).

``IdempotencyMiddleware`` is a Starlette ``BaseHTTPMiddleware`` that honors an
``Idempotency-Key`` header on write methods (POST/PUT/PATCH/DELETE), matching the
existing middleware pattern in ``api/main.py`` (``APIKeyMiddleware`` /
``RateLimitMiddleware``). It is the documented *primary* boundary for idempotency
(T046: REST-first, with the store + helper usable from MCP/direct callers too).

Status — NOT auto-mounted (deliberate, see TODO in ``api/main.py``):

Mounting body-reading middleware on the live app changes request-stream handling
for every endpoint and must be validated against the full REST test surface before
it ships on by default. To keep the v0.4.0 P2/P3 slice green and additive (FR-024),
this middleware is provided as an importable, tested component and the wiring seam
in ``api/main.py`` carries a clear TODO. An operator (or the cloud) can opt in with
``app.add_middleware(IdempotencyMiddleware)`` today; the default app is unchanged
(no key → exact v0.3.0 behavior, FR-022).

This module imports Starlette lazily inside the class so importing
``idempotency`` (store + helper) never requires the REST stack.
"""

from typing import Optional

from attestix.idempotency.store import (
    IdempotencyConflictError,
    IdempotencyStore,
    RepositoryIdempotencyStore,
    request_fingerprint,
)

#: Methods that carry side effects and therefore honor an idempotency key.
WRITE_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})

#: The request header carrying the client-supplied key (Stripe-style).
IDEMPOTENCY_HEADER = "Idempotency-Key"


def _build_middleware_class():
    """Construct the middleware class, importing Starlette lazily.

    Returns ``None`` if Starlette is unavailable (e.g. a default install without
    the REST extras), so the store + helper remain importable on their own.
    """
    try:
        from starlette.middleware.base import BaseHTTPMiddleware
        from starlette.requests import Request
        from starlette.responses import JSONResponse, Response
    except Exception:  # pragma: no cover - REST stack absent
        return None

    class IdempotencyMiddleware(BaseHTTPMiddleware):
        """Honor ``Idempotency-Key`` on write requests (opt-in; see module docs).

        On a write request carrying the header:

        - same key + same request fingerprint within TTL → returns the stored
          minimal response without re-dispatching (FR-019);
        - same key + different fingerprint → ``409`` conflict (FR-020);
        - no header → request proceeds untouched (FR-022, v0.3.0 parity).

        Tenant scope is read from :data:`~tenancy.context.TENANT_HEADER` via the
        default resolver, so keys never collide across tenants (FR-023).
        """

        def __init__(self, app, store: Optional[IdempotencyStore] = None) -> None:
            super().__init__(app)
            self._store = store or RepositoryIdempotencyStore()

        async def dispatch(self, request: "Request", call_next):
            if request.method.upper() not in WRITE_METHODS:
                return await call_next(request)

            key = request.headers.get(IDEMPOTENCY_HEADER)
            if not key:
                return await call_next(request)

            from attestix.tenancy.context import resolve_tenant

            tenant_id = resolve_tenant(request.headers).tenant_id

            body = await request.body()
            payload = {
                "method": request.method.upper(),
                "path": request.url.path,
                "body": body.decode("utf-8", "replace"),
            }
            fingerprint = request_fingerprint(payload)

            existing = self._store.get(key, tenant_id=tenant_id)
            if existing is not None:
                if existing.get("request_fingerprint") != fingerprint:
                    return JSONResponse(
                        status_code=409,
                        content={
                            "error": "Idempotency-Key reused with a different "
                            "request payload."
                        },
                    )
                if existing.get("status") == "completed":
                    return JSONResponse(
                        status_code=200,
                        content={"idempotent_replay": True,
                                 "stored_response": existing.get("stored_response")},
                    )
                return JSONResponse(
                    status_code=409,
                    content={"error": "Request with this Idempotency-Key is "
                             "already in progress."},
                )

            # First writer: reserve, dispatch, record minimal representation.
            self._store.put(
                {
                    "key": key,
                    "tenant_id": tenant_id,
                    "request_fingerprint": fingerprint,
                    "stored_response": None,
                    "status": "in_progress",
                    "created_at": _now_iso(),
                },
                tenant_id=tenant_id,
            )

            # Re-inject the consumed body so downstream handlers can read it.
            async def _receive():
                return {"type": "http.request", "body": body, "more_body": False}

            request._receive = _receive  # noqa: SLF001 - Starlette body replay idiom

            response = await call_next(request)

            from attestix.idempotency.store import minimal_stored_response

            reserved = self._store.get(key, tenant_id=tenant_id)
            created_at = reserved["created_at"] if reserved else _now_iso()
            self._store.update(
                key,
                {
                    "key": key,
                    "tenant_id": tenant_id,
                    "request_fingerprint": fingerprint,
                    "stored_response": minimal_stored_response(
                        {"status_code": response.status_code},
                        status=response.status_code,
                    ),
                    "status": "completed",
                    "created_at": created_at,
                },
                tenant_id=tenant_id,
            )
            return response

    return IdempotencyMiddleware


def _now_iso() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()


# Resolved at import: the middleware class, or None if Starlette is unavailable.
IdempotencyMiddleware = _build_middleware_class()

__all__ = [
    "IdempotencyMiddleware",
    "WRITE_METHODS",
    "IDEMPOTENCY_HEADER",
    "IdempotencyConflictError",
]
