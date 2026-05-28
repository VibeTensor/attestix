"""Legacy flat-namespace shim for :mod:`attestix.signing`.

This shim exists so that pre-v0.4.0-rc.2 user code that does::

    from signing import ...
    from signing.<submodule> import ...

keeps working after the v0.4.0-rc.2 packaging fix that promoted the canonical
location to :mod:`attestix.signing`. Importing this module (or any of its submodules)
emits a single ``DeprecationWarning`` directing callers at the new path.

The flat-namespace shim is scheduled for removal in Attestix v0.5.0. Update to::

    from attestix.signing import ...
"""

import warnings as _warnings

_warnings.warn(
    "Importing from the top-level `signing` package is deprecated and will be "
    "removed in Attestix v0.5.0. Update your imports to "
    "`from attestix.signing...` (canonical namespace).",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export the public API of the canonical namespace so `from signing import X`
# resolves to the canonical implementation.
from attestix.signing import (  # noqa: F401
    Signer,
    InProcessSigner,
    select_signer,
    signer,
    inprocess_signer,
)

del _warnings
