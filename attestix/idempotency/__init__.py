"""Idempotency keys for Attestix (v0.4.0 extensibility layer, US3 / P3).

A client-supplied idempotency key makes a write replay-safe for 24 hours
(Stripe-style): a retried request returns the original result instead of creating
a duplicate. A self-hoster who never sends a key sees no change (FR-022).

This package ships the reusable, surface-agnostic pieces — the
:class:`IdempotencyStore` (default Repository-backed, 24h TTL, reclaim) and the
:func:`run_idempotent` helper — plus an opt-in REST :class:`IdempotencyMiddleware`.
The store stores only a minimal representation of the original response
(status + resource id + response hash), never raw private-key material or a second
unencrypted copy of signed VC / identity data (FR-029).
"""

from attestix.idempotency.store import (
    IDEMPOTENCY_COLLECTION,
    TTL,
    IdempotencyConflictError,
    IdempotencyStore,
    RepositoryIdempotencyStore,
    minimal_stored_response,
    request_fingerprint,
    response_hash,
    run_idempotent,
)
from attestix.idempotency.middleware import (
    IDEMPOTENCY_HEADER,
    WRITE_METHODS,
    IdempotencyMiddleware,
)

# Submodule re-exports for `from attestix.idempotency.X import Y` parity.
from attestix.idempotency import store
from attestix.idempotency import middleware

__all__ = [
    "IdempotencyStore",
    "RepositoryIdempotencyStore",
    "IdempotencyConflictError",
    "run_idempotent",
    "request_fingerprint",
    "response_hash",
    "minimal_stored_response",
    "IDEMPOTENCY_COLLECTION",
    "TTL",
    "IdempotencyMiddleware",
    "IDEMPOTENCY_HEADER",
    "WRITE_METHODS",
    "store",
    "middleware",
]
