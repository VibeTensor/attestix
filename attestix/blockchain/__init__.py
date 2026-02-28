"""Attestix blockchain - re-exports from flat module for namespace compatibility.

Modules:
    - merkle: Merkle tree construction for batch anchoring
    - abi: EAS contract ABI definitions
"""

# Re-export from the flat blockchain module via relative imports
from .merkle import (
    build_merkle_tree,
    compute_merkle_root,
    hash_leaf,
    hash_pair,
)

from .abi import EAS_ABI, SCHEMA_REGISTRY_ABI

# Re-export submodules for namespace access
from . import abi
from . import merkle

__all__ = [
    "EAS_ABI",
    "SCHEMA_REGISTRY_ABI",
    "abi",
    "build_merkle_tree",
    "compute_merkle_root",
    "hash_leaf",
    "hash_pair",
    "merkle",
]
