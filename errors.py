"""Legacy flat-namespace shim for :mod:`attestix.errors`.

Importing this module emits a single ``DeprecationWarning``. The shim is
scheduled for removal in Attestix v0.5.0. Update to::

    from attestix.errors import ErrorCategory, log_and_format_error
"""

import warnings as _warnings

_warnings.warn(
    "Importing from the top-level `errors` module is deprecated and will be "
    "removed in Attestix v0.5.0. Update your imports to "
    "`from attestix.errors import ...` (canonical namespace).",
    DeprecationWarning,
    stacklevel=2,
)

from attestix.errors import *  # noqa: F401, F403

from attestix import errors as _canonical  # noqa: F401
import sys as _sys

_this = _sys.modules[__name__]
for _name in dir(_canonical):
    if _name.startswith("_"):
        continue
    if not hasattr(_this, _name):
        setattr(_this, _name, getattr(_canonical, _name))

del _sys, _name, _this, _canonical, _warnings
