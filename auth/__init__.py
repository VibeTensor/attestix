"""Legacy flat-namespace shim for :mod:`attestix.auth`.

This shim exists so that pre-v0.4.0-rc.2 user code that does::

    from auth import ...
    from auth.<submodule> import ...

keeps working after the v0.4.0-rc.2 packaging fix that promoted the canonical
location to :mod:`attestix.auth`. Importing this module (or any of its submodules)
emits a single ``DeprecationWarning`` directing callers at the new path.

The flat-namespace shim is scheduled for removal in Attestix v0.5.0. Update to::

    from attestix.auth import ...
"""

import warnings as _warnings

_warnings.warn(
    "Importing from the top-level `auth` package is deprecated and will be "
    "removed in Attestix v0.5.0. Update your imports to "
    "`from attestix.auth...` (canonical namespace).",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export the public API of the canonical namespace so `from auth import X`
# resolves to the canonical implementation.
from attestix.auth import (  # noqa: F401
    canonicalize_json,
    crypto,
    did_key_fragment,
    did_key_to_public_key,
    extract_identity_from_token,
    generate_ed25519_keypair,
    load_or_create_signing_key,
    private_key_from_bytes,
    private_key_to_bytes,
    public_key_from_bytes,
    public_key_to_bytes,
    public_key_to_did_key,
    sign_json_payload,
    sign_message,
    ssrf,
    token_parser,
    validate_url_host,
    verify_json_signature,
    verify_signature,
)

del _warnings
