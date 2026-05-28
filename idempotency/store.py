"""Legacy shim for :mod:`attestix.idempotency.store`.

This module is deprecated and will be removed in Attestix v0.5.0. Update to::

    from attestix.idempotency.store import ...
"""

from attestix.idempotency.store import *  # noqa: F401, F403
