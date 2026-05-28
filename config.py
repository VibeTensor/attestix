"""Legacy flat-namespace shim for :mod:`attestix.config`.

This shim exists so that pre-v0.4.0-rc.2 user code that does::

    from config import DEFAULT_EXPIRY_DAYS, load_identities

keeps working after the v0.4.0-rc.2 packaging fix that promoted the canonical
location to :mod:`attestix.config`. Importing this module emits a single
``DeprecationWarning`` directing callers at the new path.

The flat-namespace shim is scheduled for removal in Attestix v0.5.0. Update to::

    from attestix.config import DEFAULT_EXPIRY_DAYS, load_identities
"""

import warnings as _warnings

_warnings.warn(
    "Importing from the top-level `config` module is deprecated and will be "
    "removed in Attestix v0.5.0. Update your imports to "
    "`from attestix.config import ...` (canonical namespace).",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export everything from the canonical module. Star import is intentional:
# `config.py` exposes a large, evolving surface of constants and load_*/save_*
# helpers, and we want any name added there to be visible through the legacy
# shim without manual maintenance.
from attestix.config import *  # noqa: F401, F403

# Star-import skips names without an explicit __all__ that start with underscore
# or that aren't re-exported in __all__; cover the well-known public names
# explicitly so they are always available even if a future refactor tightens
# __all__ in the canonical module.
from attestix import config as _canonical  # noqa: F401

# Expose every public attribute of the canonical module on this shim. This makes
# `from config import X` work for any X that exists in `attestix.config`, not
# just those listed in `__all__`.
import sys as _sys

_this = _sys.modules[__name__]
for _name in dir(_canonical):
    if _name.startswith("_"):
        continue
    if not hasattr(_this, _name):
        setattr(_this, _name, getattr(_canonical, _name))

del _sys, _name, _this, _canonical, _warnings
