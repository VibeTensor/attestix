"""W3C Verifiable Credentials Data Model 1.1 conformance tests.

Validates credential structure, proof structure, signing exclusions,
verifiable presentations, and replay protection.
"""

import pytest

VC_CONTEXT_V1 = "https://www.w3.org/2018/credentials/v1"
ED25519_SUITE_CONTEXT = "https://w3id.org/security/suites/ed25519-2020/v1"


class TestCredentialStructure:
    """W3C VC 1.1 requires specific fields in the credential object."""

    @pytest.fixture()
    def issued_vc(self, credential_service, sample_agent_id):
        return credential_service.issue_credential(
            subject_id=sample_agent_id,
            credential_type="AgentIdentityCredential",
            issuer_name="Attestix Conformance",
            claims={"role": "tester", "level": "gold"},
        )

    def test_context_field(self, issued_vc):
        assert VC_CONTEXT_V1 in issued_vc["@context"]
        assert ED25519_SUITE_CONTEXT in issued_vc["@context"]

    def test_type_includes_verifiable_credential(self, issued_vc):
        assert "VerifiableCredential" in issued_vc["type"]

    def test_type_includes_specific_type(self, issued_vc):
        assert "AgentIdentityCredential" in issued_vc["type"]

    def test_issuer_field(self, issued_vc):
        issuer = issued_vc["issuer"]
        assert "id" in issuer
        assert issuer["id"].startswith("did:key:z")
        assert issuer["name"] == "Attestix Conformance"

    def test_issuance_date_present(self, issued_vc):
        assert "issuanceDate" in issued_vc
        assert len(issued_vc["issuanceDate"]) > 0

    def test_credential_subject(self, issued_vc, sample_agent_id):
        subject = issued_vc["credentialSubject"]
        assert subject["id"] == sample_agent_id
        assert subject["role"] == "tester"

    def test_credential_id_is_urn_uuid(self, issued_vc):
        assert issued_vc["id"].startswith("urn:uuid:")

    def test_expiration_date_present(self, issued_vc):
        assert "expirationDate" in issued_vc


class TestProofStructure:
    """Ed25519Signature2020 proof must have all required fields."""

    @pytest.fixture()
    def proof(self, credential_service, sample_agent_id):
        vc = credential_service.issue_credential(
            subject_id=sample_agent_id,
            credential_type="AgentIdentityCredential",
            issuer_name="Proof Test",
            claims={"test": True},
        )
        return vc["proof"]

    def test_proof_type(self, proof):
        assert proof["type"] == "Ed25519Signature2020"

    def test_proof_created(self, proof):
        assert "created" in proof
        assert len(proof["created"]) > 0

    def test_proof_verification_method(self, proof):
        vm = proof["verificationMethod"]
        assert "did:key:z" in vm
        assert "#" in vm

    def test_proof_purpose_is_assertion_method(self, proof):
        assert proof["proofPurpose"] == "assertionMethod"

    def test_proof_value_present(self, proof):
        assert "proofValue" in proof
        assert len(proof["proofValue"]) > 0


class TestMutableFieldsExcludedFromSigning:
    """proof and credentialStatus must not be included in the signed payload."""

    def test_revocation_does_not_break_signature(self, credential_service, sample_agent_id):
        vc = credential_service.issue_credential(
            subject_id=sample_agent_id,
            credential_type="AgentIdentityCredential",
            issuer_name="Revocation Test",
            claims={"test": True},
        )
        # Verify before revocation
        check_before = credential_service.verify_credential(vc["id"])
        assert check_before["valid"] is True
        assert check_before["checks"]["signature_valid"] is True

        # Revoke the credential
        credential_service.revoke_credential(vc["id"], reason="test revocation")

        # Signature must still be valid (revocation only changes credentialStatus)
        check_after = credential_service.verify_credential(vc["id"])
        assert check_after["checks"]["signature_valid"] is True
        # But overall validity is False because it's revoked
        assert check_after["valid"] is False
        assert check_after["checks"]["not_revoked"] is False

    def test_credential_status_field_present(self, credential_service, sample_agent_id):
        vc = credential_service.issue_credential(
            subject_id=sample_agent_id,
            credential_type="AgentIdentityCredential",
            issuer_name="Status Test",
            claims={"test": True},
        )
        status = vc["credentialStatus"]
        assert status["type"] == "RevocationList2021Status"
        assert status["revoked"] is False


class TestVerifiablePresentation:
    """VP structure, proof purpose, and replay protection."""

    @pytest.fixture()
    def vp_setup(self, credential_service, sample_agent_id):
        vc = credential_service.issue_credential(
            subject_id=sample_agent_id,
            credential_type="AgentIdentityCredential",
            issuer_name="VP Test",
            claims={"test": True},
        )
        vp = credential_service.create_verifiable_presentation(
            agent_id=sample_agent_id,
            credential_ids=[vc["id"]],
            audience_did="did:key:zAudienceExample",
            challenge="challenge-nonce-12345",
        )
        return {"vc": vc, "vp": vp, "agent_id": sample_agent_id}

    def test_vp_type(self, vp_setup):
        vp = vp_setup["vp"]
        assert "VerifiablePresentation" in vp["type"]

    def test_vp_holder(self, vp_setup):
        vp = vp_setup["vp"]
        assert vp["holder"] == vp_setup["agent_id"]

    def test_vp_contains_credentials(self, vp_setup):
        vp = vp_setup["vp"]
        assert len(vp["verifiableCredential"]) == 1

    def test_vp_proof_purpose_is_authentication(self, vp_setup):
        vp = vp_setup["vp"]
        assert vp["proof"]["proofPurpose"] == "authentication"

    def test_vp_proof_type(self, vp_setup):
        vp = vp_setup["vp"]
        assert vp["proof"]["type"] == "Ed25519Signature2020"

    def test_vp_challenge_replay_protection(self, vp_setup):
        vp = vp_setup["vp"]
        assert vp["proof"]["challenge"] == "challenge-nonce-12345"

    def test_vp_domain_replay_protection(self, vp_setup):
        vp = vp_setup["vp"]
        assert vp["proof"]["domain"] == "did:key:zAudienceExample"

    def test_vp_verification_passes(self, vp_setup, credential_service):
        result = credential_service.verify_presentation(vp_setup["vp"])
        assert result["valid"] is True
        assert result["checks"]["vp_signature_valid"] is True
        assert result["checks"]["credentials_valid"] is True
        assert result["checks"]["holder_matches_subjects"] is True

    def test_vp_without_challenge(self, credential_service, sample_agent_id):
        vc = credential_service.issue_credential(
            subject_id=sample_agent_id,
            credential_type="AgentIdentityCredential",
            issuer_name="No Challenge",
            claims={"test": True},
        )
        vp = credential_service.create_verifiable_presentation(
            agent_id=sample_agent_id,
            credential_ids=[vc["id"]],
        )
        assert "challenge" not in vp.get("proof", {})
        result = credential_service.verify_presentation(vp)
        assert result["valid"] is True


class TestExternalCredentialVerification:
    """Verifiers must be able to verify a VC without local storage."""

    def test_verify_external_credential(self, credential_service, sample_agent_id):
        vc = credential_service.issue_credential(
            subject_id=sample_agent_id,
            credential_type="AgentIdentityCredential",
            issuer_name="External Test",
            claims={"role": "verifier"},
        )
        # Verify the raw credential dict (as an external verifier would)
        result = credential_service.verify_credential_external(vc)
        assert result["valid"] is True
        assert result["checks"]["signature_valid"] is True
        assert result["checks"]["not_expired"] is True
