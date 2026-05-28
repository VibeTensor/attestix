"""Legacy flat-namespace shim for :mod:`attestix.api`.

This shim exists so that pre-v0.4.0-rc.2 user code (and deployment configs that
spawn uvicorn with ``api.main:app``) keep working after the v0.4.0-rc.2
packaging fix that promoted the canonical location to :mod:`attestix.api`.
Importing this module emits a single ``DeprecationWarning`` directing callers
at the new path.

The flat-namespace shim is scheduled for removal in Attestix v0.5.0. Update to::

    uvicorn attestix.api.main:app
    from attestix.api.main import app
"""

import warnings as _warnings

_warnings.warn(
    "Importing from the top-level `api` package is deprecated and will be "
    "removed in Attestix v0.5.0. Update your imports / deployment config to "
    "`attestix.api...` (canonical namespace).",
    DeprecationWarning,
    stacklevel=2,
)

from attestix.api import *  # noqa: F401, F403

del _warnings
