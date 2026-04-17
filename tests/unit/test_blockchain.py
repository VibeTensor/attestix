"""Tests for on-chain anchoring in services/blockchain_service.py."""

from unittest.mock import patch

from services.blockchain_service import BlockchainService


class TestSchemaUIDDerivation:
    """Tests for the canonical EAS schema UID formula.

    The EAS SchemaRegistry derives UIDs as:
        keccak256(abi.encodePacked(schema, resolver, revocable))
    (see SchemaRegistry._getUID in ethereum-attestation-service/eas-contracts).

    These tests pin expected UIDs for known inputs so any regression in the
    fallback derivation is caught immediately.
    """

    ATTESTIX_SCHEMA = (
        "bytes32 artifactHash, string artifactType, "
        "string artifactId, string issuerDid"
    )

    def test_attestix_schema_uid_matches_canonical_formula(self):
        """compute_schema_uid must match keccak(encode_packed(...))."""
        from web3 import Web3
        from eth_abi.packed import encode_packed

        resolver = "0x0000000000000000000000000000000000000000"
        revocable = True

        expected_packed = encode_packed(
            ["string", "address", "bool"],
            [
                self.ATTESTIX_SCHEMA,
                Web3.to_checksum_address(resolver),
                revocable,
            ],
        )
        expected_hex = Web3.keccak(expected_packed).hex()
        if not expected_hex.startswith("0x"):
            expected_hex = "0x" + expected_hex

        actual = BlockchainService.compute_schema_uid(
            self.ATTESTIX_SCHEMA, resolver, revocable
        )
        assert actual == expected_hex
        assert len(actual) == 66  # 0x + 32 bytes hex
        assert actual.startswith("0x")

    def test_uid_differs_for_different_revocable_flag(self):
        """Changing only the revocable flag must change the UID."""
        schema = self.ATTESTIX_SCHEMA
        resolver = "0x0000000000000000000000000000000000000000"
        uid_revocable = BlockchainService.compute_schema_uid(
            schema, resolver, True
        )
        uid_irrevocable = BlockchainService.compute_schema_uid(
            schema, resolver, False
        )
        assert uid_revocable != uid_irrevocable

    def test_uid_differs_for_different_resolver(self):
        """Changing only the resolver address must change the UID."""
        schema = self.ATTESTIX_SCHEMA
        uid_zero = BlockchainService.compute_schema_uid(
            schema, "0x0000000000000000000000000000000000000000", True
        )
        uid_other = BlockchainService.compute_schema_uid(
            schema, "0x000000000000000000000000000000000000dEaD", True
        )
        assert uid_zero != uid_other

    def test_uid_differs_from_naive_schema_hash(self):
        """Canonical UID must NOT equal keccak(schema) alone.

        The pre-fix fallback computed ``keccak(text=schema)`` which produces
        a different hash from the canonical on-chain UID. If this regression
        ever returns, verification of every anchored artifact breaks.
        """
        from web3 import Web3

        canonical = BlockchainService.compute_schema_uid(
            self.ATTESTIX_SCHEMA,
            "0x0000000000000000000000000000000000000000",
            True,
        )
        naive_hex = Web3.keccak(text=self.ATTESTIX_SCHEMA).hex()
        naive = naive_hex if naive_hex.startswith("0x") else "0x" + naive_hex
        assert canonical != naive

    def test_known_eas_schema_uid_vote_example(self):
        """Pin a well-known EAS sample schema (vote) to catch formula drift.

        Schema text: "uint256 eventId, uint8 voteIndex"
        Resolver:    0x0000000000000000000000000000000000000000
        Revocable:   True
        Expected UID: keccak256(abi.encodePacked(schema, resolver, revocable))
        """
        from web3 import Web3
        from eth_abi.packed import encode_packed

        schema = "uint256 eventId, uint8 voteIndex"
        resolver = "0x0000000000000000000000000000000000000000"
        revocable = True

        expected_hex = Web3.keccak(
            encode_packed(
                ["string", "address", "bool"],
                [schema, Web3.to_checksum_address(resolver), revocable],
            )
        ).hex()
        expected = expected_hex if expected_hex.startswith("0x") else "0x" + expected_hex

        assert BlockchainService.compute_schema_uid(
            schema, resolver, revocable
        ) == expected

    def test_deterministic(self):
        """UID derivation must be deterministic across calls."""
        a = BlockchainService.compute_schema_uid(self.ATTESTIX_SCHEMA)
        b = BlockchainService.compute_schema_uid(self.ATTESTIX_SCHEMA)
        assert a == b


class TestAttestedEventDecoding:
    """Tests for the hardened Attested-event UID extraction path."""

    def _fake_svc(self):
        """Build a BlockchainService with a real EAS contract for ABI decoding."""
        from unittest.mock import MagicMock
        from web3 import Web3
        from blockchain.abi import EAS_ABI

        svc = BlockchainService.__new__(BlockchainService)
        w3 = Web3()
        svc._w3 = w3
        svc._eas_contract = w3.eth.contract(
            address=Web3.to_checksum_address(
                "0x4200000000000000000000000000000000000021"
            ),
            abi=EAS_ABI,
        )
        svc._account = MagicMock()
        return svc

    def test_returns_unknown_when_no_logs(self):
        svc = self._fake_svc()
        assert svc._extract_attestation_uid({"logs": []}) == "unknown"

    def test_decodes_uid_from_attested_event(self):
        """Synthesize a real Attested log and confirm UID is extracted."""
        from web3 import Web3

        sig = bytes(
            Web3.keccak(text="Attested(address,address,bytes32,bytes32)")
        )
        recipient = b"\x00" * 12 + b"\x11" * 20
        attester = b"\x00" * 12 + b"\x22" * 20
        schema_uid = b"\xaa" * 32
        uid = b"\xbb" * 32

        log = {
            "address": "0x4200000000000000000000000000000000000021",
            "topics": [sig, recipient, attester, schema_uid],
            "data": uid,  # single non-indexed bytes32
            "blockNumber": 1,
            "transactionHash": b"\x00" * 32,
            "transactionIndex": 0,
            "blockHash": b"\x00" * 32,
            "logIndex": 0,
            "removed": False,
        }
        svc = self._fake_svc()
        result = svc._extract_attestation_uid({"logs": [log]})
        assert result == "0x" + ("bb" * 32)

    def test_ignores_unrelated_logs(self):
        """Non-Attested logs must not pollute the UID extraction."""
        from web3 import Web3

        sig = bytes(
            Web3.keccak(text="Attested(address,address,bytes32,bytes32)")
        )
        unrelated = {
            "address": "0x4200000000000000000000000000000000000021",
            "topics": [b"\xff" * 32],
            "data": b"\xcc" * 64,
            "blockNumber": 1,
            "transactionHash": b"\x00" * 32,
            "transactionIndex": 0,
            "blockHash": b"\x00" * 32,
            "logIndex": 0,
            "removed": False,
        }
        attested = {
            "address": "0x4200000000000000000000000000000000000021",
            "topics": [
                sig,
                b"\x00" * 12 + b"\x11" * 20,
                b"\x00" * 12 + b"\x22" * 20,
                b"\xaa" * 32,
            ],
            "data": b"\xbb" * 32,
            "blockNumber": 1,
            "transactionHash": b"\x00" * 32,
            "transactionIndex": 0,
            "blockHash": b"\x00" * 32,
            "logIndex": 1,
            "removed": False,
        }
        svc = self._fake_svc()
        assert svc._extract_attestation_uid(
            {"logs": [unrelated, attested]}
        ) == "0x" + ("bb" * 32)


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
