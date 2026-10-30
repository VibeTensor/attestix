"""Legacy shim for :mod:`attestix.idempotency.middleware`.

This module is deprecated and may be removed in a future Attestix release. Update to::

    from attestix.idempotency.middleware import ...
"""

from attestix.idempotency.middleware import *  # noqa: F401, F403
