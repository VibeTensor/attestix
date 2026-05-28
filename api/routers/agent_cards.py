"""Legacy shim for :mod:`attestix.api.routers.agent_cards`.

This module is deprecated and will be removed in Attestix v0.5.0. Update to::

    from attestix.api.routers.agent_cards import router
"""

from attestix.api.routers.agent_cards import *  # noqa: F401, F403
