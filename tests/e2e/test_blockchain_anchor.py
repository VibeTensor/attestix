"""E2E: Web3 x AI persona - on-chain anchoring (mock blockchain).

Workflow: Create identity -> anchor -> verify -> batch anchor audit log.
"""
import pytest

web3 = pytest.importorskip("web3", reason="web3 required for blockchain tests")
pytest.importorskip("eth_abi", reason="eth_abi required for blockchain tests")


class TestBlockchainAnchorWorkflow:
    def test_anchor_identity_flow(
        self, identity_service, blockchain_service_mock,
    ):
        # Create agent
        agent = identity_service.create_identity("ChainBot", "mcp")
        agent_id = agent["agent_id"]

        # Hash the identity
        artifact_hash = blockchain_service_mock.hash_artifact(agent)
        assert len(artifact_hash) == 64

        # Anchor on-chain
        anchor = blockchain_service_mock.anchor_artifact(
            artifact_hash=artifact_hash,
            artifact_type="identity",
            artifact_id=agent_id,
        )
        assert "anchor_id" in anchor, f"Anchor failed: {anchor}"
        assert anchor["artifact_type"] == "identity"
        assert anchor["network"] == "sepolia"

    def test_anchor_credential_flow(
        self, credential_service, blockchain_service_mock,
    ):
        # Issue a credential
        cred = credential_service.issue_credential(
            subject_id="attestix:agent1",
            credential_type="TestCred",
            issuer_name="Issuer",
            claims={"certified": True},
        )
        assert "id" in cred, f"Credential issuance failed: {cred}"

        # Hash and anchor
        artifact_hash = blockchain_service_mock.hash_artifact(cred)
        anchor = blockchain_service_mock.anchor_artifact(
            artifact_hash=artifact_hash,
            artifact_type="credential",
            artifact_id=cred["id"],
        )
        assert "anchor_id" in anchor, f"Anchor failed: {anchor}"
        assert anchor["artifact_type"] == "credential"

    def test_verify_anchor(self, identity_service, blockchain_service_mock):
        # Create and anchor
        agent = identity_service.create_identity("VerifyBot", "mcp")
        artifact_hash = blockchain_service_mock.hash_artifact(agent)
        blockchain_service_mock.anchor_artifact(
            artifact_hash, "identity", agent["agent_id"],
        )

        # Verify
        result = blockchain_service_mock.verify_anchor(artifact_hash)
        assert result["verified"] is True
        assert result["anchor_count"] == 1

    def test_get_anchor_status(self, identity_service, blockchain_service_mock):
        agent = identity_service.create_identity("StatusBot", "mcp")
        agent_id = agent["agent_id"]
        artifact_hash = blockchain_service_mock.hash_artifact(agent)
        blockchain_service_mock.anchor_artifact(
            artifact_hash, "identity", agent_id,
        )

        status = blockchain_service_mock.get_anchor_status(agent_id)
        assert status["total_anchors"] == 1
        assert "identity" in status["by_type"]

    def test_batch_anchor_audit_log(
        self, provenance_service, blockchain_service_mock,
    ):
        # Create some audit entries
        agent_id = "attestix:auditbot"
        for i in range(5):
            provenance_service.log_action(
                agent_id=agent_id,
                action_type="inference",
                input_summary=f"query {i}",
            )

        # Batch anchor
        result = blockchain_service_mock.anchor_audit_batch(agent_id)
        assert "anchor_id" in result, f"Batch anchor failed: {result}"
        assert result["batch_metadata"]["entry_count"] == 5
        assert len(result["batch_metadata"]["merkle_root"]) == 64
