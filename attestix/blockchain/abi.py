"""Minimal contract ABIs for EAS and SchemaRegistry on Base L2.

Only the functions Attestix needs are included. Full ABIs available at:
https://github.com/ethereum-attestation-service/eas-contracts
"""

# EAS contract functions (attest, getAttestation, isAttestationValid,
# timestamp) plus the Attested and Revoked event fragments. The event
# fragments are required for ``contract.events.Attested().process_log(log)``
# ABI decoding.
EAS_ABI = [
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "address", "name": "recipient", "type": "address"},
            {"indexed": True, "internalType": "address", "name": "attester", "type": "address"},
            {"indexed": False, "internalType": "bytes32", "name": "uid", "type": "bytes32"},
            {"indexed": True, "internalType": "bytes32", "name": "schemaUID", "type": "bytes32"},
        ],
        "name": "Attested",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "address", "name": "recipient", "type": "address"},
            {"indexed": True, "internalType": "address", "name": "attester", "type": "address"},
            {"indexed": False, "internalType": "bytes32", "name": "uid", "type": "bytes32"},
            {"indexed": True, "internalType": "bytes32", "name": "schemaUID", "type": "bytes32"},
        ],
        "name": "Revoked",
        "type": "event",
    },
    {
        "inputs": [{
            "components": [
                {"internalType": "bytes32", "name": "schema", "type": "bytes32"},
                {"components": [
                    {"internalType": "address", "name": "recipient", "type": "address"},
                    {"internalType": "uint64", "name": "expirationTime", "type": "uint64"},
                    {"internalType": "bool", "name": "revocable", "type": "bool"},
                    {"internalType": "bytes32", "name": "refUID", "type": "bytes32"},
                    {"internalType": "bytes", "name": "data", "type": "bytes"},
                    {"internalType": "uint256", "name": "value", "type": "uint256"},
                ], "internalType": "struct AttestationRequestData", "name": "data", "type": "tuple"},
            ], "internalType": "struct AttestationRequest", "name": "request", "type": "tuple",
        }],
        "name": "attest",
        "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "stateMutability": "payable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "bytes32", "name": "uid", "type": "bytes32"}],
        "name": "getAttestation",
        "outputs": [{
            "components": [
                {"internalType": "bytes32", "name": "uid", "type": "bytes32"},
                {"internalType": "bytes32", "name": "schema", "type": "bytes32"},
                {"internalType": "uint64", "name": "time", "type": "uint64"},
                {"internalType": "uint64", "name": "expirationTime", "type": "uint64"},
                {"internalType": "uint64", "name": "revocationTime", "type": "uint64"},
                {"internalType": "bytes32", "name": "refUID", "type": "bytes32"},
                {"internalType": "address", "name": "recipient", "type": "address"},
                {"internalType": "address", "name": "attester", "type": "address"},
                {"internalType": "bool", "name": "revocable", "type": "bool"},
                {"internalType": "bytes", "name": "data", "type": "bytes"},
            ], "internalType": "struct Attestation", "name": "", "type": "tuple",
        }],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "bytes32", "name": "uid", "type": "bytes32"}],
        "name": "isAttestationValid",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "bytes32", "name": "data", "type": "bytes32"}],
        "name": "timestamp",
        "outputs": [{"internalType": "uint64", "name": "", "type": "uint64"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
]

# SchemaRegistry contract functions (register, getSchema) plus the Registered
# event fragment used for decoding SchemaRegistry receipts.
SCHEMA_REGISTRY_ABI = [
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "bytes32", "name": "uid", "type": "bytes32"},
            {"indexed": True, "internalType": "address", "name": "registerer", "type": "address"},
            {
                "indexed": False,
                "components": [
                    {"internalType": "bytes32", "name": "uid", "type": "bytes32"},
                    {"internalType": "address", "name": "resolver", "type": "address"},
                    {"internalType": "bool", "name": "revocable", "type": "bool"},
                    {"internalType": "string", "name": "schema", "type": "string"},
                ],
                "internalType": "struct SchemaRecord",
                "name": "schema",
                "type": "tuple",
            },
        ],
        "name": "Registered",
        "type": "event",
    },
    {
        "inputs": [
            {"internalType": "string", "name": "schema", "type": "string"},
            {"internalType": "address", "name": "resolver", "type": "address"},
            {"internalType": "bool", "name": "revocable", "type": "bool"},
        ],
        "name": "register",
        "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "bytes32", "name": "uid", "type": "bytes32"}],
        "name": "getSchema",
        "outputs": [{
            "components": [
                {"internalType": "bytes32", "name": "uid", "type": "bytes32"},
                {"internalType": "address", "name": "resolver", "type": "address"},
                {"internalType": "bool", "name": "revocable", "type": "bool"},
                {"internalType": "string", "name": "schema", "type": "string"},
            ], "internalType": "struct SchemaRecord", "name": "", "type": "tuple",
        }],
        "stateMutability": "view",
        "type": "function",
    },
]

# Contract addresses (predeploy, same on Base mainnet and Base Sepolia)
EAS_CONTRACT_ADDRESS = "0x4200000000000000000000000000000000000021"
SCHEMA_REGISTRY_ADDRESS = "0x4200000000000000000000000000000000000020"

# The Attestix EAS schema definition. Keep this string STABLE: the on-chain
# schema UID is derived from keccak256(abi.encodePacked(schema, resolver,
# revocable)) so any change here produces a different UID and breaks
# verification of previously-anchored attestations.
ATTESTIX_SCHEMA = "bytes32 artifactHash, string artifactType, string artifactId, string issuerDid"

# Canonical schema parameters used by BlockchainService._ensure_schema_registered.
# Resolver is the zero address (no custom resolver); attestations are revocable.
ATTESTIX_SCHEMA_RESOLVER = "0x0000000000000000000000000000000000000000"
ATTESTIX_SCHEMA_REVOCABLE = True

# Pin the known-good schema UIDs here after running the registration SOP
# (see paper/internal/runbooks/eas-schema-registration-sop.md). Until then
# these remain None and the service derives the UID canonically at runtime.
ATTESTIX_SCHEMA_UID_BASE_SEPOLIA: str | None = None
ATTESTIX_SCHEMA_UID_BASE_MAINNET: str | None = None
