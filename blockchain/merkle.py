"""Merkle tree implementation for audit log batch anchoring.

Uses SHA-256 hashing. Constructs a binary Merkle tree from a list of
leaf hashes (audit log entry hashes) and returns the root hash.
"""

import hashlib
import json
from typing import List, Tuple


def hash_leaf(data: dict) -> bytes:
    """SHA-256 hash of a canonical JSON representation of a dict."""
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).digest()


def hash_pair(left: bytes, right: bytes) -> bytes:
    """SHA-256 hash of two concatenated hashes (sorted for consistency)."""
    if left > right:
        left, right = right, left
    return hashlib.sha256(left + right).digest()


def build_merkle_tree(leaves: List[bytes]) -> Tuple[bytes, List[List[bytes]]]:
    """Build a Merkle tree from leaf hashes.

    Returns (root_hash, tree_levels) where tree_levels[0] are leaves,
    tree_levels[-1] is [root].
    """
    if not leaves:
        raise ValueError("Cannot build Merkle tree from empty list")

    if len(leaves) == 1:
        return leaves[0], [leaves]

    levels = [list(leaves)]
    current = list(leaves)

    while len(current) > 1:
        next_level = []
        for i in range(0, len(current), 2):
            if i + 1 < len(current):
                next_level.append(hash_pair(current[i], current[i + 1]))
            else:
                next_level.append(current[i])
        levels.append(next_level)
        current = next_level

    return current[0], levels


def compute_merkle_root(entries: List[dict]) -> Tuple[str, int]:
    """Compute the Merkle root hex string for a list of audit log entries.

    Returns (root_hex, leaf_count).
    """
    leaf_hashes = [hash_leaf(entry) for entry in entries]
    root, _ = build_merkle_tree(leaf_hashes)
    return root.hex(), len(leaf_hashes)
