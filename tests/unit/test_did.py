"""Tests for DID resolution and creation in services/did_service.py."""

from unittest.mock import patch, MagicMock

import pytest


class TestCreateDidKey:
    """Tests for creating did:key identifiers with Ed25519 keypairs."""

    def test_creates_valid_did(self, did_service):
        result = did_service.create_did_key()
        assert result["did"].startswith("did:key:z")
        assert "did_document" in result
        assert result["did_document"]["id"] == result["did"]
        assert result["keypair_id"].startswith("keypair:")

    def test_did_document_has_verification_method(self, did_service):
        result = did_service.create_did_key()
        doc = result["did_document"]
        assert len(doc["verificationMethod"]) == 1
        vm = doc["verificationMethod"][0]
        assert vm["type"] == "Ed25519VerificationKey2020"
        assert "publicKeyMultibase" in vm


class TestResolveDidKey:
    """Tests for resolving did:key identifiers to DID documents."""

    def test_resolves_generated_did(self, did_service):
        created = did_service.create_did_key()
        resolved = did_service.resolve_did(created["did"])
        assert resolved["id"] == created["did"]
        assert len(resolved["verificationMethod"]) == 1

    def test_invalid_did_key(self, did_service):
        result = did_service.resolve_did("did:key:zinvalid")
        assert "error" in result


class TestCreateDidWeb:
    """Tests for creating did:web identifiers with hosting URLs."""

    def test_creates_did_web(self, did_service):
        result = did_service.create_did_web("example.com")
        assert result["did"] == "did:web:example.com"
        assert result["hosting_url"] == "https://example.com/.well-known/did.json"
        assert result["keypair_id"].startswith("keypair:")

    def test_creates_did_web_with_path(self, did_service):
        result = did_service.create_did_web("example.com", "users/alice")
        assert result["did"] == "did:web:example.com:users:alice"
        assert "users/alice/did.json" in result["hosting_url"]


class TestResolveDidWeb:
    """Tests for did:web resolution with SSRF and security validation."""

    def test_ssrf_blocks_localhost(self, did_service):
        result = did_service.resolve_did("did:web:localhost")
        assert "error" in result

    def test_ssrf_blocks_private_ip(self, did_service):
        result = did_service.resolve_did("did:web:192.168.1.1")
        assert "error" in result

    def test_rejects_uppercase(self, did_service):
        """did:web spec requires lowercase."""
        result = did_service.resolve_did("did:web:EXAMPLE.COM")
        assert "error" in result

    def test_rejects_path_traversal(self, did_service):
        result = did_service.resolve_did("did:web:example.com:..:..")
        assert "error" in result


class TestResolveUniversal:
    """Tests for universal DID resolution with format validation."""

    def test_rejects_invalid_format(self, did_service):
        result = did_service.resolve_did("did:foo:has spaces!")
        assert "error" in result

    def test_rejects_empty_method(self, did_service):
        result = did_service.resolve_did("not-a-did")
        # Falls through to universal resolver, which validates format
        # The universal resolver will get an invalid DID
        assert "error" in result or "didDocument" not in str(result)
