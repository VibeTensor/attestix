"""Tests for on-chain anchoring in services/blockchain_service.py."""

from unittest.mock import patch


class TestGracefulDegradation:
    """Tests for graceful behavior when blockchain is not configured."""

    def test_not_configured_without_key(self, tmp_attestix):
        """Without EVM_PRIVATE_KEY, service reports not configured."""
        with patch.dict("os.environ", {}, clear=False):
            import os
            os.environ.pop("EVM_PRIVATE_KEY", None)
            from services.blockchain_service import BlockchainService
            svc = BlockchainService()
            assert svc.is_configured is False
            assert svc.wallet_address is None

    def test_anchor_returns_error_when_unconfigured(self, tmp_attestix):
        with patch.dict("os.environ", {}, clear=False):
            import os
            os.environ.pop("EVM_PRIVATE_KEY", None)
            from services.blockchain_service import BlockchainService
            svc = BlockchainService()
            result = svc.anchor_artifact("aa" * 32, "identity", "test:1")
            assert "error" in result

    def test_estimate_returns_error_when_unconfigured(self, tmp_attestix):
        with patch.dict("os.environ", {}, clear=False):
            import os
            os.environ.pop("EVM_PRIVATE_KEY", None)
            from services.blockchain_service import BlockchainService
            svc = BlockchainService()
            result = svc.estimate_anchor_cost()
            assert "error" in result


class TestHashArtifact:
    """Tests for deterministic SHA-256 artifact hashing."""

    def test_deterministic(self, blockchain_service_mock):
        artifact = {"agent_id": "test:1", "name": "Bot"}
        h1 = blockchain_service_mock.hash_artifact(artifact)
        h2 = blockchain_service_mock.hash_artifact(artifact)
        assert h1 == h2
        assert len(h1) == 64  # SHA-256 hex

    def test_different_artifacts_different_hash(self, blockchain_service_mock):
        h1 = blockchain_service_mock.hash_artifact({"a": 1})
        h2 = blockchain_service_mock.hash_artifact({"a": 2})
        assert h1 != h2

    def test_key_order_irrelevant(self, blockchain_service_mock):
        h1 = blockchain_service_mock.hash_artifact({"z": 1, "a": 2})
        h2 = blockchain_service_mock.hash_artifact({"a": 2, "z": 1})
        assert h1 == h2


class TestAnchorArtifact:
    """Tests for anchoring artifacts with type validation."""

    def test_invalid_artifact_type(self, blockchain_service_mock):
        result = blockchain_service_mock.anchor_artifact(
            "aa" * 32, "invalid_type", "test:1",
        )
        assert "error" in result

    def test_valid_types_accepted(self, blockchain_service_mock):
        for atype in ["identity", "credential", "declaration", "audit_batch"]:
            result = blockchain_service_mock.anchor_artifact(
                "bb" * 32, atype, f"test:{atype}",
            )
            # Should not have an error about artifact type
            if "error" in result:
                assert "artifact_type" not in result["error"]


class TestVerifyAnchor:
    """Tests for verifying on-chain anchor records."""

    def test_no_local_records(self, blockchain_service_mock):
        result = blockchain_service_mock.verify_anchor("cc" * 32)
        assert result["verified"] is False
        assert "No local anchor" in result["reason"]


class TestGetAnchorStatus:
    """Tests for retrieving anchor status by agent ID."""

    def test_empty_status(self, blockchain_service_mock):
        result = blockchain_service_mock.get_anchor_status("attestix:unknown")
        assert result["total_anchors"] == 0
        assert result["anchors"] == []


class TestEstimateCost:
    """Tests for estimating gas cost and wallet affordability."""

    def test_returns_estimate(self, blockchain_service_mock):
        result = blockchain_service_mock.estimate_anchor_cost()
        assert "estimated_gas" in result
        assert "balance_eth" in result
        assert "can_afford" in result
        assert result["can_afford"] is True  # 1 ETH balance, should be enough
        assert result["network"] == "sepolia"
