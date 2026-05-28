"""Default in-process Ed25519 :class:`Signer` (v0.3.0 behavior, byte-for-byte).

``InProcessSigner`` wraps the existing ``auth/crypto.py`` machinery: it loads the
server signing key via ``load_or_create_signing_key`` (preserving the fail-loud
``SigningKeyLoadError`` guarantee — never silently regenerate an existing key),
delegates :meth:`sign` to ``sign_json_payload``, and derives :meth:`public_key`
from the loaded private key. Its output is byte-for-byte identical to v0.3.0 for
the same input (FR-007, SC-005).

This is the OSS / self-host default: a fresh install with no configuration signs
with this in-process key, exactly as v0.3.0.
"""

from typing import Optional

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from attestix.auth.crypto import (
    load_or_create_signing_key,
    sign_json_payload,
)
from attestix.signing.signer import Signer


class InProcessSigner(Signer):
    """Signs in-process with the server's Ed25519 key (the v0.3.0 root of trust).

    Construction loads (or, on first run, creates) the signing key through
    ``auth.crypto.load_or_create_signing_key``. Any failure to load an *existing*
    key propagates as ``SigningKeyLoadError`` — this signer never falls back to a
    different signing identity (FR-010, principle VI).
    """

    def __init__(
        self,
        private_key: Optional[Ed25519PrivateKey] = None,
        did: Optional[str] = None,
    ) -> None:
        """Build the signer.

        With no arguments, the key is loaded via ``load_or_create_signing_key``
        (the v0.3.0 path). A ``(private_key, did)`` pair may be injected directly
        for advanced callers/tests; both MUST be supplied together.
        """
        if private_key is not None and did is not None:
            self._private_key = private_key
            self._did = did
        elif private_key is None and did is None:
            # Fail-loud key loading is delegated to auth.crypto; any
            # SigningKeyLoadError from an unreadable existing key propagates.
            self._private_key, self._did = load_or_create_signing_key()
        else:
            raise ValueError(
                "InProcessSigner requires either both 'private_key' and 'did' "
                "or neither."
            )

    def sign(self, payload: dict) -> str:
        # Delegates to the exact v0.3.0 signing routine, so output is byte-identical.
        return sign_json_payload(self._private_key, payload)

    def public_key(self) -> Ed25519PublicKey:
        return self._private_key.public_key()

    @property
    def did(self) -> str:
        return self._did
