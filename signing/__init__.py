"""Pluggable signing for Attestix (v0.4.0 extensibility layer).

This package introduces the :class:`Signer` seam so the service layer can sign
through an abstraction instead of holding a raw Ed25519 private key. The default
install resolves to the in-process :class:`InProcessSigner`, which reproduces
v0.3.0 signatures byte-for-byte.

Selecting a non-default backend is opt-in via the ``ATTESTIX_SIGNER`` environment
variable (or the ``config`` argument to :func:`select_signer`); the optional
KMS/HSM adapter lives behind the ``[kms]`` extra and is imported lazily so a
default ``pip install`` pulls no extra runtime dependency (FR-007, FR-026,
SC-010).
"""

import os
from typing import Optional

from signing.signer import Signer
from signing.inprocess_signer import InProcessSigner

__all__ = [
    "Signer",
    "InProcessSigner",
    "select_signer",
]


def select_signer(config: Optional[dict] = None) -> Signer:
    """Return the configured Signer, defaulting to :class:`InProcessSigner`.

    Selection precedence:

    1. ``config["signer"]`` if a ``config`` mapping is supplied.
    2. The ``ATTESTIX_SIGNER`` environment variable.
    3. Default: ``"inprocess"`` -> :class:`InProcessSigner` (v0.3.0 behavior).

    Recognized values:

    - ``"inprocess"`` / ``"in_process"`` (default) -> :class:`InProcessSigner`.
    - ``"kms"`` / ``"hsm"`` -> the optional KMS/HSM adapter (``[kms]`` extra),
      imported lazily; a clear, actionable error is raised if the extra is not
      installed.

    The default signer is constructed fresh per call so it picks up the current
    ``config.SIGNING_KEY_FILE`` (honoring test monkeypatching); callers that want a
    cached instance should hold the returned signer themselves.
    """
    choice = None
    if config:
        choice = config.get("signer")
    if choice is None:
        choice = os.environ.get("ATTESTIX_SIGNER")
    if choice is None:
        choice = "inprocess"
    choice = str(choice).strip().lower()

    if choice in ("inprocess", "in_process", "in-process", "ed25519"):
        return InProcessSigner()
    if choice in ("kms", "hsm"):
        try:
            from signing.kms_signer import KmsSigner  # noqa: F401
        except ImportError as exc:  # pragma: no cover - exercised only with extra
            raise ImportError(
                "ATTESTIX_SIGNER=kms requires the optional 'kms' extra. "
                "Install it with: pip install 'attestix[kms]'"
            ) from exc
        return KmsSigner(config or {})

    raise ValueError(
        f"Unknown ATTESTIX_SIGNER value {choice!r}. "
        "Expected one of: inprocess, kms."
    )
