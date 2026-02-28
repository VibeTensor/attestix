"""Re-export from flat module for namespace compatibility."""
from blockchain.merkle import (
    build_merkle_tree,
    compute_merkle_root,
    hash_leaf,
    hash_pair,
)

__all__ = [
    "build_merkle_tree",
    "compute_merkle_root",
    "hash_leaf",
    "hash_pair",
]
