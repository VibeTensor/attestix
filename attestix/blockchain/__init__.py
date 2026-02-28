"""Attestix blockchain - re-exports from flat module for namespace compatibility.

Modules:
    - merkle: Merkle tree construction for batch anchoring
    - abi: EAS contract ABI definitions
"""

# Re-export from the flat blockchain module
from blockchain.merkle import (
    build_merkle_tree,
    compute_merkle_root,
    hash_leaf,
    hash_pair,
)

from blockchain.abi import EAS_ABI, SCHEMA_REGISTRY_ABI

# Re-export submodules as relative imports for consistent module identity
from . import abi  # noqa: E402
from . import merkle  # noqa: E402

__all__ = [
    "abi",
    "build_merkle_tree",
    "compute_merkle_root",
    "EAS_ABI",
    "hash_leaf",
    "hash_pair",
    "merkle",
    "SCHEMA_REGISTRY_ABI",
]
