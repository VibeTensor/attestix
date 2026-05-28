"""Legacy flat-namespace shim for :mod:`attestix.idempotency`.

This shim exists so that pre-v0.4.0-rc.2 user code that does::

    from idempotency import ...
    from idempotency.<submodule> import ...

keeps working after the v0.4.0-rc.2 packaging fix that promoted the canonical
location to :mod:`attestix.idempotency`. Importing this module (or any of its submodules)
emits a single ``DeprecationWarning`` directing callers at the new path.

The flat-namespace shim is scheduled for removal in Attestix v0.5.0. Update to::

    from attestix.idempotency import ...
"""

import warnings as _warnings

_warnings.warn(
    "Importing from the top-level `idempotency` package is deprecated and will be "
    "removed in Attestix v0.5.0. Update your imports to "
    "`from attestix.idempotency...` (canonical namespace).",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export the public API of the canonical namespace so `from idempotency import X`
# resolves to the canonical implementation.
from attestix.idempotency import (  # noqa: F401
    IdempotencyStore,
    RepositoryIdempotencyStore,
    IdempotencyConflictError,
    run_idempotent,
    request_fingerprint,
    response_hash,
    minimal_stored_response,
    IDEMPOTENCY_COLLECTION,
    TTL,
    IdempotencyMiddleware,
    IDEMPOTENCY_HEADER,
    WRITE_METHODS,
    store,
    middleware,
)

del _warnings
