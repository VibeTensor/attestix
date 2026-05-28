"""Legacy flat-namespace shim for :mod:`attestix.storage`.

This shim exists so that pre-v0.4.0-rc.2 user code that does::

    from storage import ...
    from storage.<submodule> import ...

keeps working after the v0.4.0-rc.2 packaging fix that promoted the canonical
location to :mod:`attestix.storage`. Importing this module (or any of its submodules)
emits a single ``DeprecationWarning`` directing callers at the new path.

The flat-namespace shim is scheduled for removal in Attestix v0.5.0. Update to::

    from attestix.storage import ...
"""

import warnings as _warnings

_warnings.warn(
    "Importing from the top-level `storage` package is deprecated and will be "
    "removed in Attestix v0.5.0. Update your imports to "
    "`from attestix.storage...` (canonical namespace).",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export the public API of the canonical namespace so `from storage import X`
# resolves to the canonical implementation.
from attestix.storage import (  # noqa: F401
    Repository,
    FileRepository,
    MemoryRepository,
    DEFAULT_TENANT,
    select_repository,
    default_repository,
    repository,
    file_repository,
    memory_repository,
)

del _warnings
