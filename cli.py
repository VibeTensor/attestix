"""Legacy flat-namespace shim for :mod:`attestix.cli`.

This shim exists so that pre-v0.4.0-rc.2 user code that does::

    python -m cli
    from cli import cli

keeps working after the v0.4.0-rc.2 packaging fix that promoted the canonical
location to :mod:`attestix.cli`. Importing this module emits a single
``DeprecationWarning`` directing callers at the new path.

The flat-namespace shim is scheduled for removal in Attestix v0.5.0. Update to::

    python -m attestix.cli
"""

import warnings as _warnings

_warnings.warn(
    "Importing or running the top-level `cli` module is deprecated and will be "
    "removed in Attestix v0.5.0. Use `python -m attestix.cli` (or the "
    "`attestix` console script) instead.",
    DeprecationWarning,
    stacklevel=2,
)

from attestix.cli import *  # noqa: F401, F403
from attestix.cli import cli  # noqa: F401

if __name__ == "__main__":
    cli()
