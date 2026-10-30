"""Legacy flat-namespace shim for :mod:`attestix.blockchain`.

This shim exists so that pre-v0.4.0-rc.2 user code that does::

    from blockchain import ...
    from blockchain.<submodule> import ...

keeps working after the v0.4.0-rc.2 packaging fix that promoted the canonical
location to :mod:`attestix.blockchain`. Importing this module (or any of its submodules)
emits a single ``DeprecationWarning`` directing callers at the new path.

The flat-namespace shim is retained for compatibility in this release. Update to::

    from attestix.blockchain import ...
"""

import warnings as _warnings

_warnings.warn(
    "Importing from the top-level `blockchain` package is deprecated and will be "
    "removed in a future Attestix release. Update your imports to "
    "`from attestix.blockchain...` (canonical namespace).",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export the public API of the canonical namespace so `from blockchain import X`
# resolves to the canonical implementation.
from attestix.blockchain import (  # noqa: F401
    EAS_ABI,
    SCHEMA_REGISTRY_ABI,
    abi,
    build_merkle_tree,
    compute_merkle_root,
    hash_leaf,
    hash_pair,
    merkle,
)

del _warnings
