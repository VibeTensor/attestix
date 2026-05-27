"""Attestix idempotency - re-exports from the flat module for namespace parity.

    # Namespaced (recommended)
    from attestix.idempotency import RepositoryIdempotencyStore, run_idempotent

    # Flat (also supported)
    from idempotency import RepositoryIdempotencyStore, run_idempotent
"""

from idempotency import (
    IDEMPOTENCY_COLLECTION,
    IDEMPOTENCY_HEADER,
    TTL,
    WRITE_METHODS,
    IdempotencyConflictError,
    IdempotencyMiddleware,
    IdempotencyStore,
    RepositoryIdempotencyStore,
    minimal_stored_response,
    request_fingerprint,
    response_hash,
    run_idempotent,
)

# Re-export submodules for `from attestix.idempotency.X import Y` parity.
from idempotency import store
from idempotency import middleware

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
