"""Shared fixtures for Attestix test suite.

Provides test isolation by redirecting all JSON storage to tmp_path
and clearing the service cache between tests.
"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure the project root is on sys.path so imports work
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(autouse=True)
def tmp_attestix(tmp_path, monkeypatch):
    """Redirect all Attestix storage to a temp directory.

    This patches every *_FILE path in config.py so that no test
    reads or writes production JSON files.
    """
    import config

    file_attrs = [
        "IDENTITIES_FILE",
        "REPUTATION_FILE",
        "DELEGATIONS_FILE",
        "COMPLIANCE_FILE",
        "CREDENTIALS_FILE",
        "PROVENANCE_FILE",
        "ANCHORS_FILE",
        "BLOCKCHAIN_CONFIG_FILE",
        "SIGNING_KEY_FILE",
        "LOG_FILE",
    ]

    for attr in file_attrs:
        original = getattr(config, attr)
        monkeypatch.setattr(config, attr, tmp_path / original.name)

    # Also patch PROJECT_DIR and DATA_DIR so any code using them resolves to tmp
    monkeypatch.setattr(config, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)

    # Clear the service cache so services re-initialize with patched paths
    from services.cache import clear_cache
    clear_cache()

    yield tmp_path

    # Cleanup: clear cache again after test
    clear_cache()


@pytest.fixture
def identity_service():
    """Fresh IdentityService instance using tmp storage."""
    from services.identity_service import IdentityService
    return IdentityService()


@pytest.fixture
def credential_service():
    """Fresh CredentialService instance using tmp storage."""
    from services.credential_service import CredentialService
    return CredentialService()


@pytest.fixture
def delegation_service():
    """Fresh DelegationService instance using tmp storage."""
    from services.delegation_service import DelegationService
    return DelegationService()


@pytest.fixture
def reputation_service():
    """Fresh ReputationService instance using tmp storage."""
    from services.reputation_service import ReputationService
    return ReputationService()


@pytest.fixture
def compliance_service():
    """Fresh ComplianceService instance using tmp storage."""
    from services.compliance_service import ComplianceService
    return ComplianceService()


@pytest.fixture
def provenance_service():
    """Fresh ProvenanceService instance using tmp storage."""
    from services.provenance_service import ProvenanceService
    return ProvenanceService()


@pytest.fixture
def did_service():
    """Fresh DIDService instance using tmp storage."""
    from services.did_service import DIDService
    return DIDService()


@pytest.fixture
def agent_card_service():
    """Fresh AgentCardService instance."""
    from services.agent_card_service import AgentCardService
    return AgentCardService()


@pytest.fixture
def report_service():
    """Fresh ReportService instance using tmp storage."""
    from services.report_service import ReportService
    return ReportService()


@pytest.fixture
def blockchain_service_mock():
    """BlockchainService with web3 fully mocked.

    Returns a configured service that thinks it's connected to Base Sepolia.
    """
    from services.blockchain_service import BlockchainService

    with patch.dict("os.environ", {"EVM_PRIVATE_KEY": "0x" + "ab" * 32, "BASE_NETWORK": "sepolia"}):
        with patch("services.blockchain_service.BlockchainService._try_init"):
            svc = BlockchainService()
            svc._configured = True
            svc._network = "sepolia"
            svc._schema_uid = "0x" + "ff" * 32
            svc._init_error = None

            # Mock web3 objects
            mock_w3 = MagicMock()
            mock_w3.eth.gas_price = 1000000000  # 1 gwei
            mock_w3.eth.max_priority_fee = 100000000  # 0.1 gwei
            mock_w3.eth.get_balance.return_value = 10**18  # 1 ETH
            mock_w3.eth.get_transaction_count.return_value = 0

            # Build a realistic Attested event log so _extract_attestation_uid
            # can decode it. Topic[0] must be keccak("Attested(address,address,bytes32,bytes32)").
            # The single non-indexed uid bytes32 sits at the first 32 bytes of data.
            from web3 import Web3 as _Web3
            _attested_sig = bytes(
                _Web3.keccak(text="Attested(address,address,bytes32,bytes32)")
            )
            _fake_uid = b"\x01" * 32  # deterministic non-zero UID
            mock_w3.eth.wait_for_transaction_receipt.return_value = {
                "status": 1,
                "blockNumber": 12345,
                "gasUsed": 187000,
                "logs": [{
                    "data": _fake_uid,
                    "topics": [
                        _attested_sig,
                        b"\x00" * 12 + bytes.fromhex("11" * 20),  # recipient
                        b"\x00" * 12 + bytes.fromhex("11" * 20),  # attester
                    ],
                }],
            }
            mock_w3.from_wei = lambda val, unit: val / 10**18 if unit == "ether" else val / 10**9
            mock_w3.is_connected.return_value = True
            svc._w3 = mock_w3

            # Mock account
            mock_account = MagicMock()
            mock_account.address = "0x" + "11" * 20
            mock_account.sign_transaction.return_value = MagicMock(
                raw_transaction=b"\x00" * 100
            )
            svc._account = mock_account

            # Mock contracts
            mock_eas = MagicMock()
            mock_eas.functions.attest.return_value.build_transaction.return_value = {
                "to": "0x" + "42" * 20,
            }
            mock_eas.functions.isAttestationValid.return_value.call.return_value = True
            mock_eas.functions.getAttestation.return_value.call.return_value = [
                b"\x00" * 32,  # uid
                b"\x00" * 32,  # schema
                1700000000,    # time
                0,             # expirationTime
                0,             # revocationTime
                b"\x00" * 32,  # refUID
                "0x" + "11" * 20,  # recipient
                "0x" + "11" * 20,  # attester
                True,          # revocable
                b"\x00" * 100, # data
            ]
            svc._eas_contract = mock_eas

            mock_w3.eth.send_raw_transaction.return_value = b"\xab" * 32

            yield svc


@pytest.fixture
def sample_agent_id(identity_service):
    """Create a sample agent and return its ID."""
    result = identity_service.create_identity(
        display_name="Test Agent",
        source_protocol="mcp",
        capabilities=["read", "write"],
        description="A test agent",
    )
    return result["agent_id"]
