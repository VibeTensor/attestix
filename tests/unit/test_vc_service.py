"""Tests for services/credential_service.py — W3C Verifiable Credentials."""


class TestIssueCredential:
    def test_issues_with_proof(self, credential_service):
        result = credential_service.issue_credential(
            subject_id="attestix:agent1",
            credential_type="AgentIdentityCredential",
            issuer_name="TestIssuer",
            claims={"role": "tester"},
        )
        assert result["id"].startswith("urn:uuid:")
        assert "VerifiableCredential" in result["type"]
        assert "AgentIdentityCredential" in result["type"]
        assert result["proof"]["type"] == "Ed25519Signature2020"
        assert result["credentialSubject"]["role"] == "tester"

    def test_custom_expiry(self, credential_service):
        result = credential_service.issue_credential(
            subject_id="attestix:agent1",
            credential_type="TestCredential",
            issuer_name="Issuer",
            claims={"x": 1},
            expiry_days=7,
        )
        from datetime import datetime, timezone
        exp = datetime.fromisoformat(result["expirationDate"])
        issued = datetime.fromisoformat(result["issuanceDate"])
        delta = exp - issued
        assert 6 <= delta.days <= 7


class TestVerifyCredential:
    def test_valid_credential(self, credential_service):
        cred = credential_service.issue_credential(
            subject_id="attestix:agent1",
            credential_type="TestCred",
            issuer_name="Issuer",
            claims={"a": 1},
        )
        result = credential_service.verify_credential(cred["id"])
        assert result["valid"] is True
        assert result["checks"]["exists"] is True
        assert result["checks"]["not_revoked"] is True
        assert result["checks"]["signature_valid"] is True

    def test_revoked_credential_invalid(self, credential_service):
        cred = credential_service.issue_credential(
            subject_id="attestix:agent1",
            credential_type="TestCred",
            issuer_name="Issuer",
            claims={"a": 1},
        )
        credential_service.revoke_credential(cred["id"], "test")
        result = credential_service.verify_credential(cred["id"])
        assert result["valid"] is False
        assert result["checks"]["not_revoked"] is False

    def test_nonexistent_credential(self, credential_service):
        result = credential_service.verify_credential("urn:uuid:nonexistent")
        assert result["valid"] is False
        assert result["checks"]["exists"] is False


class TestRevokeCredential:
    def test_revoke_success(self, credential_service):
        cred = credential_service.issue_credential(
            subject_id="attestix:agent1",
            credential_type="TestCred",
            issuer_name="Issuer",
            claims={},
        )
        result = credential_service.revoke_credential(cred["id"], "compromised")
        assert result["revoked"] is True

    def test_revoke_nonexistent(self, credential_service):
        result = credential_service.revoke_credential("urn:uuid:nope")
        assert "error" in result


class TestListCredentials:
    def test_list_all(self, credential_service):
        credential_service.issue_credential("a:1", "T", "I", {"x": 1})
        credential_service.issue_credential("a:2", "T", "I", {"x": 2})
        results = credential_service.list_credentials()
        assert len(results) == 2

    def test_filter_by_agent(self, credential_service):
        credential_service.issue_credential("a:1", "T", "I", {"x": 1})
        credential_service.issue_credential("a:2", "T", "I", {"x": 2})
        results = credential_service.list_credentials(agent_id="a:1")
        assert len(results) == 1
        assert results[0]["credentialSubject"]["id"] == "a:1"


class TestVerifiablePresentation:
    def test_create_vp(self, credential_service):
        cred = credential_service.issue_credential(
            subject_id="attestix:agent1",
            credential_type="TestCred",
            issuer_name="Issuer",
            claims={"role": "test"},
        )
        vp = credential_service.create_verifiable_presentation(
            agent_id="attestix:agent1",
            credential_ids=[cred["id"]],
            audience_did="did:key:z123",
            challenge="nonce123",
        )
        assert "VerifiablePresentation" in vp["type"]
        assert vp["holder"] == "attestix:agent1"
        assert len(vp["verifiableCredential"]) == 1
        assert vp["proof"]["challenge"] == "nonce123"
        assert vp["domain"] == "did:key:z123"
