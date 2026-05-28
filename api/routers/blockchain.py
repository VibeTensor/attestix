"""Legacy shim for :mod:`attestix.api.routers.blockchain`.

This module is deprecated and will be removed in Attestix v0.5.0. Update to::

    from attestix.api.routers.blockchain import router
"""

from attestix.api.routers.blockchain import *  # noqa: F401, F403
