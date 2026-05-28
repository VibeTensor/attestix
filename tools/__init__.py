"""Legacy flat-namespace shim for :mod:`attestix.tools`.

This shim exists so that pre-v0.4.0-rc.2 user code that does::

    from tools import ...
    from tools.<submodule> import ...

keeps working after the v0.4.0-rc.2 packaging fix that promoted the canonical
location to :mod:`attestix.tools`. Importing this module (or any of its submodules)
emits a single ``DeprecationWarning`` directing callers at the new path.

The flat-namespace shim is scheduled for removal in Attestix v0.5.0. Update to::

    from attestix.tools import ...
"""

import warnings as _warnings

_warnings.warn(
    "Importing from the top-level `tools` package is deprecated and will be "
    "removed in Attestix v0.5.0. Update your imports to "
    "`from attestix.tools...` (canonical namespace).",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export the public API of the canonical namespace so `from tools import X`
# resolves to the canonical implementation.
from attestix.tools import (  # noqa: F401
    identity_tools,
    agent_card_tools,
    did_tools,
    delegation_tools,
    reputation_tools,
    compliance_tools,
    credential_tools,
    provenance_tools,
    blockchain_tools,
)

del _warnings
