"""Legacy flat-namespace shim for :mod:`attestix.services`.

This shim exists so that pre-v0.4.0-rc.2 user code that does::

    from services.identity_service import IdentityService
    from services import IdentityService

keeps working after the v0.4.0-rc.2 packaging fix that promoted the canonical
location to :mod:`attestix.services`. Importing this module (or any of its
submodules) emits a single ``DeprecationWarning`` directing callers at the new
path.

The flat-namespace shim is scheduled for removal in v0.5.0. Update imports to::

    from attestix.services.identity_service import IdentityService
"""

import warnings as _warnings

_warnings.warn(
    "Importing from the top-level `services` package is deprecated and will be "
    "removed in Attestix v0.5.0. Update your imports to "
    "`from attestix.services...` (canonical namespace).",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export the public API of attestix.services so `from services import X` works.
from attestix.services import (  # noqa: F401
    IdentityService,
    CredentialService,
    ComplianceService,
    DelegationService,
    ReputationService,
    ProvenanceService,
    AgentCardService,
    BlockchainService,
    DIDService,
)

del _warnings
