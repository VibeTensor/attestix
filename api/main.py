"""Legacy shim for :mod:`attestix.api.main`.

This module is deprecated and may be removed in a future Attestix release. Update to::

    uvicorn attestix.api.main:app
    from attestix.api.main import app
"""

from attestix.api.main import *  # noqa: F401, F403
from attestix.api.main import app  # noqa: F401
