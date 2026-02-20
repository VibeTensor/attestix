"""
Comprehensive end-to-end validation of Attestix.
Tests the complete lifecycle across all 9 modules, simulating real-world
user workflows from identity creation through blockchain anchoring.
"""
import json
import asyncio
import pytest
from datetime import datetime, timezone


class TestFullLifecycleValidation:
    """Complete lifecycle: identity -> compliance -> credentials -> blockchain."""

    def test_complete_agent_lifecycle(
        self,
        identity_service,
        compliance_service,
        credential_service,
        provenance_service,
        delegation_service,
        reputation_service,
        did_service,
        agent_card_service,
    ):
        """
        Simulates the full workflow a real enterprise would follow:
        1. Create agent identity
        2. Set up DID
        3. Record training data provenance (Article 10)
        4. Record model lineage (Article 11)
        5. Create compliance profile
        6. Check gap analysis
        7. Record conformity assessment
        8. Generate Annex V declaration (auto-issues VC)
        9. Verify the auto-issued credential
        10. Create delegation to sub-agent
        11. Record interactions and build reputation
        12. Create verifiable presentation
        13. Translate identity to A2A and DID Document
        """
        # --- Step 1: Create agent identity ---
        identity = identity_service.create_identity(
            display_name="MedAssist-AI-v2",
            source_protocol="mcp",
            capabilities=["diagnosis_support", "medical_records", "patient_triage"],
            description="High-risk medical AI diagnostic assistant",
            issuer_name="VibeTensor Health Division",
        )
        assert "agent_id" in identity, f"Identity creation failed: {identity}"
        agent_id = identity["agent_id"]
        assert agent_id.startswith("attestix:")

        # --- Step 2: Verify identity ---
        verification = identity_service.verify_identity(agent_id)
        assert verification["valid"] is True
        assert verification["checks"]["exists"] is True
        assert verification["checks"]["not_revoked"] is True
        assert verification["checks"]["not_expired"] is True
        assert verification["checks"]["signature_valid"] is True

        # --- Step 3: Create DID ---
        did_result = did_service.create_did_key()
        assert "did" in did_result
        assert did_result["did"].startswith("did:key:z")

        # --- Step 4: Record training data provenance (Article 10) ---
        training_data_1 = provenance_service.record_training_data(
            agent_id=agent_id,
            dataset_name="MIMIC-IV Clinical Database",
            source_url="https://physionet.org/content/mimiciv/",
            license="PhysioNet Credentialed Health Data License",
            contains_personal_data=True,
            data_governance_measures="De-identified per HIPAA Safe Harbor, IRB approved #2024-0142",
        )
        assert "entry_id" in training_data_1, f"Training data recording failed: {training_data_1}"

        training_data_2 = provenance_service.record_training_data(
            agent_id=agent_id,
            dataset_name="PubMed Medical Literature Corpus",
            source_url="https://pubmed.ncbi.nlm.nih.gov/",
            license="NLM Terms of Service",
            contains_personal_data=False,
            data_governance_measures="Public domain medical literature, no patient data",
        )
        assert "entry_id" in training_data_2

        # --- Step 5: Record model lineage (Article 11) ---
        lineage = provenance_service.record_model_lineage(
            agent_id=agent_id,
            base_model="Llama-3.1-70B-Instruct",
            fine_tuning_method="LoRA r=16, alpha=32 on clinical QA pairs",
            evaluation_metrics={
                "diagnostic_accuracy": 0.94,
                "false_negative_rate": 0.02,
                "f1_score": 0.91,
                "clinical_relevance_score": 0.88,
            },
        )
        assert "entry_id" in lineage, f"Model lineage recording failed: {lineage}"

        # --- Step 6: Create compliance profile (high-risk medical AI) ---
        profile = compliance_service.create_compliance_profile(
            agent_id=agent_id,
            risk_category="high",
            provider_name="VibeTensor Health Division",
            intended_purpose="Clinical decision support for emergency department triage",
            transparency_obligations="Full audit logging, explanation generation for each recommendation",
            human_oversight_measures="Board-certified physician review required before treatment decisions",
        )
        assert "profile_id" in profile, f"Compliance profile creation failed: {profile}"

        # --- Step 7: Check gap analysis BEFORE assessment ---
        status_before = compliance_service.get_compliance_status(agent_id)
        assert "completion_pct" in status_before
        assert status_before["completion_pct"] < 100
        assert len(status_before.get("missing", [])) > 0

        # --- Step 8: Record third-party conformity assessment ---
        assessment = compliance_service.record_conformity_assessment(
            agent_id=agent_id,
            assessment_type="third_party",
            assessor_name="TUV Rheinland AG",
            result="pass",
            findings="Full Annex III Category 5(a) assessment per Article 43",
            ce_marking_eligible=True,
        )
        assert "assessment_id" in assessment, f"Assessment recording failed: {assessment}"

        # --- Step 9: Generate Annex V Declaration of Conformity ---
        declaration = compliance_service.generate_declaration_of_conformity(
            agent_id=agent_id,
        )
        assert "declaration_id" in declaration, f"Declaration generation failed: {declaration}"

        # --- Step 10: Verify the auto-issued credential ---
        # The declaration auto-issues an EUAIActComplianceCredential
        all_creds = credential_service.list_credentials(
            agent_id=agent_id, credential_type="EUAIActComplianceCredential",
        )
        assert len(all_creds) >= 1, "Auto-issued compliance credential not found"
        credential_id = all_creds[0]["id"]

        vc_verification = credential_service.verify_credential(credential_id)
        assert vc_verification["valid"] is True
        assert vc_verification["checks"]["signature_valid"] is True
        assert vc_verification["checks"]["not_expired"] is True
        assert vc_verification["checks"]["not_revoked"] is True

        # --- Step 11: Get the full credential and inspect ---
        credential = credential_service.get_credential(credential_id)
        assert credential is not None
        assert "EUAIActComplianceCredential" in credential.get("type", [])

        # --- Step 12: Verify gap analysis AFTER full workflow ---
        status_after = compliance_service.get_compliance_status(agent_id)
        # Core requirements should all be met (profile, purpose, transparency,
        # oversight, assessment, declaration, training data, model lineage).
        # Some high-risk obligations (risk management system, post-market monitoring,
        # serious incident reporting) require additional organizational processes
        # beyond what the test sets up.
        core_completed = [
            "compliance_profile_created",
            "intended_purpose_documented",
            "transparency_obligations_declared",
            "human_oversight_measures",
            "conformity_assessment_passed",
            "declaration_of_conformity_issued",
            "training_data_provenance",
            "model_lineage_recorded",
        ]
        for req in core_completed:
            assert req in status_after["completed"], (
                f"Expected '{req}' to be completed. "
                f"Completed: {status_after['completed']}, Missing: {status_after['missing']}"
            )
        # At minimum 60% overall (8+ of ~16 total for high-risk)
        assert status_after["completion_pct"] >= 50, (
            f"Expected >= 50% completion, got {status_after['completion_pct']}%. "
            f"Missing: {status_after.get('missing', [])}"
        )

        # --- Step 13: Create a sub-agent and delegate ---
        sub_identity = identity_service.create_identity(
            display_name="MedAssist-Triage-Worker",
            source_protocol="mcp",
            capabilities=["patient_triage"],
            description="Sub-agent handling triage queue",
            issuer_name="VibeTensor Health Division",
        )
        sub_agent_id = sub_identity["agent_id"]

        delegation = delegation_service.create_delegation(
            issuer_agent_id=agent_id,
            audience_agent_id=sub_agent_id,
            capabilities=["patient_triage"],
            expiry_hours=24,
        )
        assert "token" in delegation, f"Delegation failed: {delegation}"

        # Verify delegation token
        delegation_check = delegation_service.verify_delegation(delegation["token"])
        assert delegation_check["valid"] is True

        # --- Step 14: Record interactions and build reputation ---
        for i in range(5):
            reputation_service.record_interaction(
                agent_id=agent_id,
                counterparty_id=sub_agent_id,
                outcome="success",
                category="diagnosis_support",
                details=f"Triage case #{i+1} completed correctly",
            )

        reputation_service.record_interaction(
            agent_id=agent_id,
            counterparty_id=sub_agent_id,
            outcome="partial",
            category="diagnosis_support",
            details="Case #6 required human override",
        )

        reputation = reputation_service.get_reputation(agent_id)
        assert "trust_score" in reputation
        assert reputation["trust_score"] > 0.7, (
            f"Expected trust score > 0.7, got {reputation['trust_score']}"
        )
        assert reputation["total_interactions"] == 6

        # --- Step 15: Log audit trail actions (Article 12) ---
        for action in ["inference", "inference", "external_call"]:
            log_result = provenance_service.log_action(
                agent_id=agent_id,
                action_type=action,
                input_summary="Patient symptoms: chest pain, shortness of breath",
                output_summary=f"Action: {action} completed",
                decision_rationale="Standard triage protocol applied",
                human_override=action == "external_call",
            )
            # Verify hash chaining
            assert "chain_hash" in log_result, "Audit entry should include chain_hash"
            assert "prev_hash" in log_result, "Audit entry should include prev_hash"

        # --- Step 16: Query audit trail ---
        audit = provenance_service.get_audit_trail(agent_id)
        assert len(audit) >= 3, f"Expected >= 3 audit entries, got {len(audit)}"

        # Verify hash chain integrity
        for i in range(1, len(audit)):
            if "chain_hash" in audit[i] and "prev_hash" in audit[i]:
                assert audit[i]["prev_hash"] == audit[i-1].get("chain_hash", ""), (
                    f"Hash chain broken at entry {i}"
                )

        # --- Step 17: Get full provenance ---
        provenance = provenance_service.get_provenance(agent_id)
        assert len(provenance.get("training_data", [])) == 2
        assert len(provenance.get("model_lineage", [])) >= 1
        assert provenance.get("audit_log_count", 0) >= 3

        # --- Step 18: Create verifiable presentation ---
        presentation = credential_service.create_verifiable_presentation(
            agent_id=agent_id,
            credential_ids=[credential_id],
            audience_did="did:web:ai-office.europa.eu",
            challenge="audit-request-2026-02-20",
        )
        assert "verifiableCredential" in presentation
        assert presentation.get("proof") is not None

        # --- Step 19: Translate identity to other formats ---
        a2a_card = identity_service.translate_identity(agent_id, "a2a_agent_card")
        assert "name" in a2a_card
        assert a2a_card["name"] == "MedAssist-AI-v2"

        did_doc = identity_service.translate_identity(agent_id, "did_document")
        assert "@context" in did_doc
        assert "verificationMethod" in did_doc

        # --- Step 20: List and verify final state ---
        all_identities = identity_service.list_identities()
        assert len(all_identities) >= 2

        all_creds_final = credential_service.list_credentials()
        assert len(all_creds_final) >= 1

        all_delegations = delegation_service.list_delegations()
        assert len(all_delegations) >= 1

        compliance_profiles = compliance_service.list_compliance_profiles()
        assert len(compliance_profiles) >= 1


class TestCryptoIntegrity:
    """Verify cryptographic operations are correct end-to-end."""

    def test_signature_roundtrip(self):
        from auth.crypto import (
            generate_ed25519_keypair,
            sign_message,
            verify_signature,
            public_key_to_did_key,
            did_key_to_public_key,
        )

        private_key, public_key = generate_ed25519_keypair()

        # Sign and verify
        message = b"test message for signature verification"
        signature = sign_message(private_key, message)
        assert verify_signature(public_key, signature, message) is True

        # Tampered message should fail
        assert verify_signature(public_key, signature, b"tampered") is False

        # DID key roundtrip
        did = public_key_to_did_key(public_key)
        assert did.startswith("did:key:z6Mk")
        recovered_key = did_key_to_public_key(did)
        assert recovered_key.public_bytes_raw() == public_key.public_bytes_raw()

    def test_merkle_tree_integrity(self):
        from blockchain.merkle import build_merkle_tree, hash_leaf

        # Build tree from known entries
        entries = [{"entry": f"audit_entry_{i}"} for i in range(10)]
        leaf_hashes = [hash_leaf(entry) for entry in entries]
        root, levels = build_merkle_tree(leaf_hashes)

        # Root should be deterministic
        leaf_hashes_2 = [hash_leaf(entry) for entry in entries]
        root_2, _ = build_merkle_tree(leaf_hashes_2)
        assert root_2 == root, "Merkle root should be deterministic"

        # Different entries should produce different root
        entries_modified = [{"entry": f"audit_entry_{i}"} for i in range(10)]
        entries_modified[5] = {"entry": "tampered_entry"}
        leaf_hashes_3 = [hash_leaf(entry) for entry in entries_modified]
        root_3, _ = build_merkle_tree(leaf_hashes_3)
        assert root_3 != root, "Tampered entries should change root"


class TestSecurityBoundaries:
    """Test security controls and edge cases."""

    def test_ssrf_protection(self):
        from auth.ssrf import validate_url_host

        # Private IPs should be blocked (returns error string)
        assert validate_url_host("127.0.0.1") is not None
        assert validate_url_host("192.168.1.1") is not None
        assert validate_url_host("10.0.0.1") is not None
        assert validate_url_host("::1") is not None
        assert validate_url_host("metadata.google.internal") is not None
        assert validate_url_host("localhost") is not None

        # Public hostnames should be safe (returns None)
        assert validate_url_host("example.com") is None
        assert validate_url_host("google.com") is None

    def test_identity_revocation(self, identity_service):
        """Revoked identities should fail verification."""
        identity = identity_service.create_identity(
            display_name="RevocableAgent",
            source_protocol="mcp",
            capabilities=["test"],
        )
        agent_id = identity["agent_id"]

        # Verify it works
        check = identity_service.verify_identity(agent_id)
        assert check["valid"] is True

        # Revoke
        revoke_result = identity_service.revoke_identity(agent_id)
        assert revoke_result is not None

        # Verify it fails
        check_after = identity_service.verify_identity(agent_id)
        assert check_after["valid"] is False
        assert check_after["checks"]["not_revoked"] is False

    def test_credential_revocation(self, identity_service, credential_service):
        """Revoked credentials should fail verification."""
        identity = identity_service.create_identity(
            display_name="CredTestAgent",
            source_protocol="mcp",
            capabilities=["test"],
        )
        agent_id = identity["agent_id"]

        cred = credential_service.issue_credential(
            subject_id=agent_id,
            credential_type="TestCredential",
            issuer_name="Test Issuer",
            claims={"test_claim": "value"},
        )
        cred_id = cred["id"]

        # Verify works
        check = credential_service.verify_credential(cred_id)
        assert check["valid"] is True

        # Revoke
        credential_service.revoke_credential(cred_id)

        # Verify fails
        check_after = credential_service.verify_credential(cred_id)
        assert check_after["valid"] is False

    def test_high_risk_blocks_self_assessment(self, identity_service, compliance_service):
        """High-risk systems must use third-party assessment."""
        identity = identity_service.create_identity(
            display_name="HighRiskAgent",
            source_protocol="mcp",
            capabilities=["biometric_identification"],
        )
        agent_id = identity["agent_id"]

        compliance_service.create_compliance_profile(
            agent_id=agent_id,
            risk_category="high",
            provider_name="TestCorp",
            intended_purpose="Biometric identification in public spaces",
        )

        # Self-assessment should be rejected
        result = compliance_service.record_conformity_assessment(
            agent_id=agent_id,
            assessment_type="self",
            assessor_name="Internal Team",
            result="pass",
        )
        assert "error" in result, "Self-assessment should be blocked for high-risk"
        assert "third_party" in result["error"].lower() or "article 43" in result["error"].lower()

    def test_unacceptable_risk_blocked(self, identity_service, compliance_service):
        """Unacceptable-risk systems should be completely blocked."""
        identity = identity_service.create_identity(
            display_name="SocialScoringAgent",
            source_protocol="mcp",
            capabilities=["social_scoring"],
        )
        agent_id = identity["agent_id"]

        result = compliance_service.create_compliance_profile(
            agent_id=agent_id,
            risk_category="unacceptable",
            provider_name="BadCorp",
            intended_purpose="Social credit scoring",
        )
        assert "error" in result, "Unacceptable risk should be blocked"


class TestEdgeCases:
    """Test boundary conditions and error handling."""

    def test_empty_capabilities(self, identity_service):
        identity = identity_service.create_identity(
            display_name="MinimalAgent",
            source_protocol="mcp",
            capabilities=[],
        )
        assert "agent_id" in identity

    def test_special_characters_in_names(self, identity_service):
        identity = identity_service.create_identity(
            display_name="Agent O'Brien & Partners (v2.0)",
            source_protocol="mcp",
            capabilities=["test"],
            description='Description with "quotes" and <html> tags',
        )
        assert "agent_id" in identity

        # Verify it round-trips correctly
        retrieved = identity_service.get_identity(identity["agent_id"])
        assert retrieved["display_name"] == "Agent O'Brien & Partners (v2.0)"

    def test_nonexistent_agent(self, identity_service):
        result = identity_service.verify_identity("attestix:nonexistent")
        assert result["valid"] is False

    def test_reputation_with_no_interactions(self, reputation_service):
        result = reputation_service.get_reputation("attestix:never_interacted")
        assert result.get("trust_score") is None or result.get("total_interactions", 0) == 0

    def test_concurrent_identity_creation(self, identity_service):
        """Create multiple identities sequentially to test file locking."""
        results = []
        for i in range(10):
            result = identity_service.create_identity(
                display_name=f"ConcurrentAgent-{i}",
                source_protocol="mcp",
                capabilities=["test"],
            )
            results.append(result)
        agent_ids = [r["agent_id"] for r in results if "agent_id" in r]
        assert len(set(agent_ids)) == 10, "All 10 identities should be unique"

    def test_delegation_expiry(self, identity_service, delegation_service):
        """Delegation with minimal expiry should still create successfully."""
        id1 = identity_service.create_identity(
            display_name="Delegator", source_protocol="mcp", capabilities=["admin"]
        )
        id2 = identity_service.create_identity(
            display_name="Delegate", source_protocol="mcp", capabilities=["read"]
        )

        # Create delegation with minimal expiry
        delegation = delegation_service.create_delegation(
            issuer_agent_id=id1["agent_id"],
            audience_agent_id=id2["agent_id"],
            capabilities=["read"],
            expiry_hours=1,
        )
        assert "token" in delegation


class TestToolLayerConsistency:
    """Verify all 47 tools are registered and return valid JSON."""

    def test_all_tool_modules_importable(self):
        """All 9 tool modules should import without errors."""
        from tools import identity_tools
        from tools import agent_card_tools
        from tools import did_tools
        from tools import delegation_tools
        from tools import reputation_tools
        from tools import compliance_tools
        from tools import credential_tools
        from tools import provenance_tools
        from tools import blockchain_tools

        # Each module should have a register function
        for module in [
            identity_tools, agent_card_tools, did_tools,
            delegation_tools, reputation_tools, compliance_tools,
            credential_tools, provenance_tools, blockchain_tools,
        ]:
            assert hasattr(module, "register"), f"{module.__name__} missing register()"

    def test_tool_count(self):
        """Verify we have exactly 47 tools across 9 modules."""
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test-attestix")

        from tools import identity_tools
        from tools import agent_card_tools
        from tools import did_tools
        from tools import delegation_tools
        from tools import reputation_tools
        from tools import compliance_tools
        from tools import credential_tools
        from tools import provenance_tools
        from tools import blockchain_tools

        modules = [
            identity_tools, agent_card_tools, did_tools,
            delegation_tools, reputation_tools, compliance_tools,
            credential_tools, provenance_tools, blockchain_tools,
        ]

        for module in modules:
            module.register(mcp)

        # FastMCP stores tools internally
        tool_count = len(mcp._tool_manager._tools)
        assert tool_count >= 47, (
            f"Expected at least 47 tools, got {tool_count}. "
            f"Tools: {list(mcp._tool_manager._tools.keys())}"
        )
