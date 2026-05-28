"""Legacy shim for :mod:`attestix.api.main`.

This module is deprecated and will be removed in Attestix v0.5.0. Update to::

    uvicorn attestix.api.main:app
    from attestix.api.main import app
"""

from attestix.api.main import *  # noqa: F401, F403
from attestix.api.main import app  # noqa: F401
