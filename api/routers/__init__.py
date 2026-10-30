"""Legacy shim for :mod:`attestix.api.routers`.

This module is deprecated and may be removed in a future Attestix release. Update to::

    from attestix.api.routers import ...
"""

from attestix.api.routers import *  # noqa: F401, F403
from attestix.api.routers import (  # noqa: F401
    identity,
    credentials,
    compliance,
    reputation,
    provenance,
    delegation,
    did,
    agent_cards,
    blockchain,
)
