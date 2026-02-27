"""Attestix blockchain - re-exports from flat module for namespace compatibility.

Modules:
    - merkle: Merkle tree construction for batch anchoring
    - abi: EAS contract ABI definitions
"""

# Re-export from the flat blockchain module
from blockchain.merkle import (
    hash_leaf,
    hash_pair,
    build_merkle_tree,
    compute_merkle_root,
)

from blockchain.abi import EAS_ABI, SCHEMA_REGISTRY_ABI

# Re-export submodules
from blockchain import merkle
from blockchain import abi

__all__ = [
    # Merkle functions
    "hash_leaf",
    "hash_pair",
    "build_merkle_tree",
    "compute_merkle_root",
    # ABI
    "EAS_ABI",
    "SCHEMA_REGISTRY_ABI",
    # Submodules
    "merkle",
    "abi",
]
