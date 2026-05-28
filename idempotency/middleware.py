"""Legacy shim for :mod:`attestix.idempotency.middleware`.

This module is deprecated and will be removed in Attestix v0.5.0. Update to::

    from attestix.idempotency.middleware import ...
"""

from attestix.idempotency.middleware import *  # noqa: F401, F403
