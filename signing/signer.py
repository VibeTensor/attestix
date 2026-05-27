"""Signer contract: the signing boundary the service layer depends on.

The ``Signer`` abstract base class defines the signing seam introduced in v0.4.0.
It replaces services holding a raw ``self._private_key`` with an abstraction that
produces a signature over a canonicalized payload and discloses the corresponding
public identity (``public_key`` / ``did``) — but never exposes private key
material.

Every concrete implementation (the default :class:`InProcessSigner` wrapping the
v0.3.0 Ed25519 key, or an optional KMS/HSM-backed signer) MUST satisfy the same
contract test suite (``tests/contract/test_signer_contract.py``), enforcing Liskov
substitution at the boundary.
"""

from abc import ABC, abstractmethod

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


class Signer(ABC):
    """Signing boundary for the service layer.

    Contract invariants (asserted against every implementation by
    ``tests/contract/test_signer_contract.py``):

    - **Verifiable**: ``verify_json_signature(s.public_key(), payload,
      s.sign(payload))`` is ``True`` via the standard ``auth.crypto`` verify path
      (FR-009).
    - **Deterministic identity**: :attr:`did` is stable for the life of the signer
      and matches :meth:`public_key`.
    - **No private-key leakage**: the interface exposes no method returning private
      key bytes; KMS/HSM implementations hold no private material in process
      (FR-008, principle VI).
    - **Fail loud**: if the backend is unavailable, construction / :meth:`sign`
      raises a clear error and never substitutes or regenerates a key (FR-010;
      preserves ``auth.crypto.SigningKeyLoadError`` semantics).
    """

    @abstractmethod
    def sign(self, payload: dict) -> str:
        """Sign ``payload`` over its JCS (RFC 8785) canonical form.

        Returns a base64url-encoded Ed25519 signature string, matching the wire
        format produced by ``auth.crypto.sign_json_payload``.
        """
        raise NotImplementedError

    @abstractmethod
    def public_key(self) -> Ed25519PublicKey:
        """Return the Ed25519 public key for verifying this signer's signatures."""
        raise NotImplementedError

    @property
    @abstractmethod
    def did(self) -> str:
        """Return the ``did:key`` (or ``did:web``) identifier of this signer."""
        raise NotImplementedError
