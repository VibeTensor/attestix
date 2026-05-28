"""Merkle tree implementation for audit log batch anchoring.

Uses SHA-256 hashing with domain separation (0x00 prefix for leaves,
0x01 prefix for internal nodes) to prevent second-preimage attacks.
Follows the Certificate Transparency (RFC 6962) convention.
"""

import hashlib
import json
from typing import List, Tuple

# Domain separation prefixes (RFC 6962 Section 2.1)
_LEAF_PREFIX = b"\x00"
_NODE_PREFIX = b"\x01"


def hash_leaf(data: dict) -> bytes:
    """SHA-256 hash of a canonical JSON representation with leaf domain prefix."""
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(_LEAF_PREFIX + canonical.encode("utf-8")).digest()


def hash_pair(left: bytes, right: bytes) -> bytes:
    """SHA-256 hash of two child hashes with internal node domain prefix."""
    return hashlib.sha256(_NODE_PREFIX + left + right).digest()


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
