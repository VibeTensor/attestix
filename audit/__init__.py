"""Legacy flat-namespace shim for :mod:`attestix.audit`.

This shim exists so that pre-v0.4.0-rc.2 user code that does::

    from audit import ...
    from audit.<submodule> import ...

keeps working after the v0.4.0-rc.2 packaging fix that promoted the canonical
location to :mod:`attestix.audit`. Importing this module (or any of its submodules)
emits a single ``DeprecationWarning`` directing callers at the new path.

The flat-namespace shim is scheduled for removal in Attestix v0.5.0. Update to::

    from attestix.audit import ...
"""

import warnings as _warnings

_warnings.warn(
    "Importing from the top-level `audit` package is deprecated and will be "
    "removed in Attestix v0.5.0. Update your imports to "
    "`from attestix.audit...` (canonical namespace).",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export the public API of the canonical namespace so `from audit import X`
# resolves to the canonical implementation.
from attestix.audit import (  # noqa: F401
    AuditEvent,
    AuditEventEmitter,
    AUDIT_COLLECTION,
    GENESIS_HASH,
    compute_change_digest,
    verify_chain,
    resolve_emitter,
    safe_emit,
    events,
    emitter,
    service_hook,
)

del _warnings
