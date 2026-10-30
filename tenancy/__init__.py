"""Legacy flat-namespace shim for :mod:`attestix.tenancy`.

This shim exists so that pre-v0.4.0-rc.2 user code that does::

    from tenancy import ...
    from tenancy.<submodule> import ...

keeps working after the v0.4.0-rc.2 packaging fix that promoted the canonical
location to :mod:`attestix.tenancy`. Importing this module (or any of its submodules)
emits a single ``DeprecationWarning`` directing callers at the new path.

The flat-namespace shim is retained for compatibility in this release. Update to::

    from attestix.tenancy import ...
"""

import warnings as _warnings

_warnings.warn(
    "Importing from the top-level `tenancy` package is deprecated and will be "
    "removed in a future Attestix release. Update your imports to "
    "`from attestix.tenancy...` (canonical namespace).",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export the public API of the canonical namespace so `from tenancy import X`
# resolves to the canonical implementation.
from attestix.tenancy import (  # noqa: F401
    DEFAULT_TENANT,
    TenantContext,
    default_tenant_context,
    resolve_tenant,
    context,
)

del _warnings
