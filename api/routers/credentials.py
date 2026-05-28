"""Legacy shim for :mod:`attestix.api.routers.credentials`.

This module is deprecated and will be removed in Attestix v0.5.0. Update to::

    from attestix.api.routers.credentials import router
"""

from attestix.api.routers.credentials import *  # noqa: F401, F403
