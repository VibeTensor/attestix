"""W3C DID Core conformance tests.

Validates DID Document structure, required fields, verification method types,
and roundtrip resolution per the W3C DID Core v1.0 specification.
"""

import pytest

from auth.crypto import (
    generate_ed25519_keypair,
    public_key_to_did_key,
    did_key_to_public_key,
    public_key_to_bytes,
)

DID_CORE_CONTEXT = "https://www.w3.org/ns/did/v1"
ED25519_SUITE_CONTEXT = "https://w3id.org/security/suites/ed25519-2020/v1"


class TestDIDKeyDocumentStructure:
    """did:key documents must have all W3C DID Core required fields."""

    @pytest.fixture()
    def did_key_result(self, did_service):
        return did_service.create_did_key()

    def test_context_includes_did_core(self, did_key_result):
        doc = did_key_result["did_document"]
        assert DID_CORE_CONTEXT in doc["@context"]

    def test_context_includes_ed25519_suite(self, did_key_result):
        doc = did_key_result["did_document"]
        assert ED25519_SUITE_CONTEXT in doc["@context"]

    def test_id_field_present(self, did_key_result):
        doc = did_key_result["did_document"]
        assert doc["id"] == did_key_result["did"]

    def test_id_starts_with_did_key(self, did_key_result):
        assert did_key_result["did"].startswith("did:key:z")

    def test_verification_method_present(self, did_key_result):
        doc = did_key_result["did_document"]
        assert len(doc["verificationMethod"]) >= 1

    def test_authentication_present(self, did_key_result):
        doc = did_key_result["did_document"]
        assert "authentication" in doc
        assert len(doc["authentication"]) >= 1

    def test_controller_matches_did(self, did_key_result):
        doc = did_key_result["did_document"]
        did = did_key_result["did"]
        assert doc["controller"] == did
        for vm in doc["verificationMethod"]:
            assert vm["controller"] == did

    def test_verification_method_type_ed25519(self, did_key_result):
        doc = did_key_result["did_document"]
        vm = doc["verificationMethod"][0]
        assert vm["type"] == "Ed25519VerificationKey2020"

    def test_verification_method_has_public_key(self, did_key_result):
        doc = did_key_result["did_document"]
        vm = doc["verificationMethod"][0]
        assert "publicKeyMultibase" in vm
        assert vm["publicKeyMultibase"].startswith("z")

    def test_assertion_method_present(self, did_key_result):
        doc = did_key_result["did_document"]
        assert "assertionMethod" in doc
        assert len(doc["assertionMethod"]) >= 1


class TestDIDKeyRoundtrip:
    """Generate a did:key then resolve it; the document must be consistent."""

    def test_create_then_resolve(self, did_service):
        created = did_service.create_did_key()
        resolved = did_service.resolve_did(created["did"])
        assert resolved["id"] == created["did"]
        assert resolved["@context"] == created["did_document"]["@context"]
        assert len(resolved["verificationMethod"]) == len(
            created["did_document"]["verificationMethod"]
        )

    def test_did_key_to_public_key_roundtrip(self):
        """Generate keypair, convert to did:key, convert back; keys must match."""
        _, public_key = generate_ed25519_keypair()
        did = public_key_to_did_key(public_key)
        recovered = did_key_to_public_key(did)
        assert public_key_to_bytes(public_key) == public_key_to_bytes(recovered)


class TestDIDWebDocumentStructure:
    """did:web documents must follow W3C DID Core structure."""

    @pytest.fixture()
    def did_web_result(self, did_service):
        return did_service.create_did_web("example.com")

    def test_did_web_id_format(self, did_web_result):
        assert did_web_result["did"] == "did:web:example.com"

    def test_did_web_context(self, did_web_result):
        doc = did_web_result["did_document"]
        assert DID_CORE_CONTEXT in doc["@context"]

    def test_did_web_controller(self, did_web_result):
        doc = did_web_result["did_document"]
        assert doc["controller"] == "did:web:example.com"

    def test_did_web_verification_method_type(self, did_web_result):
        doc = did_web_result["did_document"]
        vm = doc["verificationMethod"][0]
        assert vm["type"] == "Ed25519VerificationKey2020"

    def test_did_web_hosting_url(self, did_web_result):
        assert did_web_result["hosting_url"] == "https://example.com/.well-known/did.json"

    def test_did_web_with_path(self, did_service):
        result = did_service.create_did_web("example.com", path="agents/v1")
        assert result["did"] == "did:web:example.com:agents:v1"
        assert result["hosting_url"] == "https://example.com/agents/v1/did.json"
