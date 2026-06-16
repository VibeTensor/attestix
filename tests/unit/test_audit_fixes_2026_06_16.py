"""Regression tests for the 2026-06-16 multi-persona audit fixes.

A1 - VC verification must bind the verifying key to ``issuer.id`` (the trust
     anchor), not to the attacker-controlled ``proof.verificationMethod``.
A2 - The HTTP API must fail closed when no ``ATTESTIX_API_KEY`` is configured,
     unless ``ATTESTIX_ALLOW_NO_AUTH`` is explicitly set.
"""

import pytest

from attestix.auth.crypto import (
    did_key_fragment,
    generate_ed25519_keypair,
    public_key_to_did_key,
    sign_json_payload,
)


# ---------------------------------------------------------------------------
# A1 - issuer key-substitution
# ---------------------------------------------------------------------------

class TestIssuerKeyBinding:
    """A credential re-signed by an attacker who points verificationMethod at
    their own did:key (leaving issuer.id naming the trusted server) must NOT
    verify."""

    def _attacker_resign(self, credential, mutable_fields):
        """Re-sign the credential payload with a fresh attacker key and point
        proof.verificationMethod at the attacker's did:key."""
        priv, pub = generate_ed25519_keypair()
        attacker_did = public_key_to_did_key(pub)
        payload = {k: v for k, v in credential.items() if k not in mutable_fields}
        forged_sig = sign_json_payload(priv, payload)
        credential["proof"] = {
            **credential.get("proof", {}),
            "verificationMethod": f"{attacker_did}{did_key_fragment(attacker_did)}",
            "proofValue": forged_sig,
        }
        return credential, attacker_did

    def test_external_verify_rejects_key_substitution(self, credential_service):
        cred = credential_service.issue_credential(
            agent_id="did:example:subject-1",
            credential_type="TestCredential",
            issuer_name="VibeTensor",
            claims={"role": "tester"},
        )
        assert "error" not in cred
        # Sanity: the untampered credential verifies.
        assert credential_service.verify_credential_external(cred)["valid"] is True

        forged, attacker_did = self._attacker_resign(cred, credential_service.MUTABLE_FIELDS)
        # issuer.id still names the trusted server, not the attacker.
        assert forged["issuer"]["id"] != attacker_did

        result = credential_service.verify_credential_external(forged)
        assert result["valid"] is False
        assert result["checks"]["signature_valid"] is False

    def test_external_verify_rejects_bare_vm_mismatch(self, credential_service):
        """Even without a valid forged signature, a verificationMethod naming a
        different DID than issuer.id must be rejected outright."""
        cred = credential_service.issue_credential(
            agent_id="did:example:subject-2",
            credential_type="TestCredential",
            issuer_name="VibeTensor",
        )
        _, pub = generate_ed25519_keypair()
        other_did = public_key_to_did_key(pub)
        cred["proof"]["verificationMethod"] = f"{other_did}{did_key_fragment(other_did)}"
        result = credential_service.verify_credential_external(cred)
        assert result["valid"] is False
        assert result["checks"]["signature_valid"] is False


# ---------------------------------------------------------------------------
# A2 - API fails closed without a key
# ---------------------------------------------------------------------------

class TestApiFailsClosedWithoutKey:
    def _client(self):
        fastapi = pytest.importorskip("fastapi")
        from fastapi.testclient import TestClient
        from attestix.api.main import app
        return TestClient(app)

    def test_protected_path_returns_503_when_no_key_and_no_optin(self, monkeypatch):
        monkeypatch.delenv("ATTESTIX_API_KEY", raising=False)
        monkeypatch.delenv("ATTESTIX_ALLOW_NO_AUTH", raising=False)
        client = self._client()
        resp = client.post("/v1/identities", json={"display_name": "x", "source_protocol": "api_key"})
        assert resp.status_code == 503

    def test_open_paths_served_even_without_key(self, monkeypatch):
        monkeypatch.delenv("ATTESTIX_API_KEY", raising=False)
        monkeypatch.delenv("ATTESTIX_ALLOW_NO_AUTH", raising=False)
        client = self._client()
        assert client.get("/health").status_code == 200

    def test_optin_restores_open_access(self, monkeypatch):
        monkeypatch.delenv("ATTESTIX_API_KEY", raising=False)
        monkeypatch.setenv("ATTESTIX_ALLOW_NO_AUTH", "1")
        client = self._client()
        resp = client.post("/v1/identities", json={"display_name": "x", "source_protocol": "api_key"})
        assert resp.status_code != 503


# ---------------------------------------------------------------------------
# Cloud-bundle finding: credential rows are exported under ``vc_jsonld``
# ---------------------------------------------------------------------------

class TestCloudCredentialRowProjection:
    """The cloud DB exports the signed VC under the ``vc_jsonld`` key
    (schema/credentials.ts); the OSS importer must project that key, not only
    the fixture's ``credential`` alias."""

    def test_vc_jsonld_key_is_projected(self):
        from attestix.portability.importer import _row_credential

        vc = {
            "@context": ["https://www.w3.org/2018/credentials/v1"],
            "id": "urn:uuid:11111111-1111-4111-8111-111111111111",
            "type": ["VerifiableCredential"],
            "credentialSubject": {"id": "did:example:subject"},
        }
        cloud_row = {
            "id": "22222222-2222-4222-8222-222222222222",
            "workspace_id": "33333333-3333-4333-8333-333333333333",
            "vc_jsonld": vc,
        }
        out = _row_credential(cloud_row)
        assert out["id"] == vc["id"]
        assert out["_cloud_id"] == cloud_row["id"]
        assert out["credentialSubject"]["id"] == "did:example:subject"
