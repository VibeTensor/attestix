"""Attestix signing - re-exports from the flat module for namespace compatibility.

    # Namespaced (recommended)
    from attestix.signing import Signer, InProcessSigner, select_signer

    # Flat (also supported)
    from signing import Signer, InProcessSigner, select_signer
"""

from signing import (
    InProcessSigner,
    Signer,
    select_signer,
)

# Re-export submodules for `from attestix.signing.X import Y` parity.
from signing import signer
from signing import inprocess_signer

__all__ = [
    "Signer",
    "InProcessSigner",
    "select_signer",
    "signer",
    "inprocess_signer",
]
