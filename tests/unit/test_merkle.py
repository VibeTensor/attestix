"""Tests for blockchain/merkle.py — Merkle tree operations."""

import pytest

from blockchain.merkle import (
    hash_leaf,
    hash_pair,
    build_merkle_tree,
    compute_merkle_root,
    _LEAF_PREFIX,
    _NODE_PREFIX,
)


class TestHashLeaf:
    def test_deterministic(self):
        data = {"key": "value"}
        assert hash_leaf(data) == hash_leaf(data)

    def test_different_data_different_hash(self):
        assert hash_leaf({"a": 1}) != hash_leaf({"a": 2})

    def test_key_order_irrelevant(self):
        """Canonical JSON uses sort_keys."""
        assert hash_leaf({"z": 1, "a": 2}) == hash_leaf({"a": 2, "z": 1})


class TestHashPair:
    def test_deterministic(self):
        a = hash_leaf({"a": 1})
        b = hash_leaf({"b": 2})
        assert hash_pair(a, b) == hash_pair(a, b)

    def test_position_matters(self):
        """hash_pair(a, b) != hash_pair(b, a) — position-preserving."""
        a = hash_leaf({"a": 1})
        b = hash_leaf({"b": 2})
        assert hash_pair(a, b) != hash_pair(b, a)

    def test_domain_separation(self):
        """Leaf and node hashes use different prefixes."""
        import hashlib
        data = b"\x00" * 32
        leaf_hash = hashlib.sha256(_LEAF_PREFIX + data).digest()
        node_hash = hashlib.sha256(_NODE_PREFIX + data + data).digest()
        assert leaf_hash != node_hash


class TestBuildMerkleTree:
    def test_single_leaf(self):
        leaf = hash_leaf({"x": 1})
        root, levels = build_merkle_tree([leaf])
        assert root == leaf
        assert len(levels) == 1

    def test_two_leaves(self):
        a = hash_leaf({"a": 1})
        b = hash_leaf({"b": 2})
        root, levels = build_merkle_tree([a, b])
        assert root == hash_pair(a, b)
        assert len(levels) == 2

    def test_three_leaves_odd_promotion(self):
        a = hash_leaf({"a": 1})
        b = hash_leaf({"b": 2})
        c = hash_leaf({"c": 3})
        root, levels = build_merkle_tree([a, b, c])
        # ab = hash_pair(a, b), c promoted
        ab = hash_pair(a, b)
        expected_root = hash_pair(ab, c)
        assert root == expected_root

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="empty"):
            build_merkle_tree([])


class TestComputeMerkleRoot:
    def test_returns_hex_and_count(self):
        entries = [{"i": 1}, {"i": 2}, {"i": 3}]
        root_hex, count = compute_merkle_root(entries)
        assert len(root_hex) == 64  # 32 bytes = 64 hex chars
        assert count == 3

    def test_deterministic(self):
        entries = [{"x": i} for i in range(5)]
        r1, _ = compute_merkle_root(entries)
        r2, _ = compute_merkle_root(entries)
        assert r1 == r2
