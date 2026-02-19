"""Blockchain anchoring service for Attestix.

Anchors cryptographic hashes of off-chain artifacts (UAITs, VCs, audit log
batches, compliance declarations) to Base L2 via Ethereum Attestation Service.

Optional: works only when EVM_PRIVATE_KEY is set in .env.
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from auth.crypto import load_or_create_signing_key, _normalize_for_signing
from config import (
    _get_env,
    load_anchors,
    save_anchors,
    BLOCKCHAIN_CONFIG_FILE,
)
from errors import ErrorCategory, log_and_format_error


VALID_ARTIFACT_TYPES = {"identity", "credential", "declaration", "audit_batch"}

NETWORKS = {
    "sepolia": {
        "rpc_url": "https://sepolia.base.org",
        "chain_id": 84532,
        "explorer": "https://sepolia.basescan.org",
    },
    "mainnet": {
        "rpc_url": "https://mainnet.base.org",
        "chain_id": 8453,
        "explorer": "https://basescan.org",
    },
}


class BlockchainService:
    """Manages EAS attestation anchoring on Base L2."""

    def __init__(self):
        self._private_key_ed, self._server_did = load_or_create_signing_key()
        self._w3 = None
        self._account = None
        self._eas_contract = None
        self._schema_registry = None
        self._schema_uid = None
        self._network = _get_env("BASE_NETWORK", "sepolia")
        self._configured = False
        self._init_error = None
        self._try_init()

    def _try_init(self):
        """Attempt to initialize web3 connection. Fail gracefully."""
        evm_key = _get_env("EVM_PRIVATE_KEY")
        if not evm_key:
            self._init_error = (
                "Blockchain anchoring not configured. "
                "Set EVM_PRIVATE_KEY in .env to enable on-chain anchoring. "
                "Generate a wallet: python -c \"from eth_account import Account; "
                "a = Account.create(); print(a.key.hex())\" "
                "Fund on Base Sepolia: https://www.coinbase.com/faucets/base-ethereum-sepolia-faucet"
            )
            return

        try:
            from web3 import Web3
            from eth_account import Account

            network = NETWORKS.get(self._network)
            if not network:
                self._init_error = (
                    f"Unknown network '{self._network}'. Use 'sepolia' or 'mainnet'."
                )
                return

            rpc_url = _get_env("BASE_RPC_URL", network["rpc_url"])
            self._w3 = Web3(Web3.HTTPProvider(rpc_url))

            if not self._w3.is_connected():
                self._init_error = (
                    f"Cannot connect to {rpc_url}. Check network connectivity."
                )
                return

            self._account = Account.from_key(evm_key)

            from blockchain.abi import (
                EAS_ABI, SCHEMA_REGISTRY_ABI,
                EAS_CONTRACT_ADDRESS, SCHEMA_REGISTRY_ADDRESS,
            )

            self._eas_contract = self._w3.eth.contract(
                address=Web3.to_checksum_address(EAS_CONTRACT_ADDRESS),
                abi=EAS_ABI,
            )
            self._schema_registry = self._w3.eth.contract(
                address=Web3.to_checksum_address(SCHEMA_REGISTRY_ADDRESS),
                abi=SCHEMA_REGISTRY_ABI,
            )

            self._schema_uid = self._load_schema_uid()
            self._configured = True

        except ImportError:
            self._init_error = (
                "web3 package not installed. Run: pip install web3>=7.0.0"
            )
        except Exception as e:
            self._init_error = log_and_format_error(
                "BlockchainService._try_init", e, ErrorCategory.BLOCKCHAIN,
            )

    @property
    def is_configured(self) -> bool:
        return self._configured

    @property
    def wallet_address(self) -> Optional[str]:
        return self._account.address if self._account else None

    def _require_configured(self) -> Optional[str]:
        """Return error message if not configured, else None."""
        if not self._configured:
            return self._init_error or "Blockchain not configured"
        return None

    # --- Schema Management ---

    def _load_schema_uid(self) -> Optional[str]:
        """Load cached schema UID from blockchain config file."""
        try:
            if BLOCKCHAIN_CONFIG_FILE.exists():
                with open(BLOCKCHAIN_CONFIG_FILE, "r") as f:
                    config = json.load(f)
                return config.get(f"schema_uid_{self._network}")
        except Exception:
            pass
        return None

    def _save_schema_uid(self, schema_uid: str):
        """Cache schema UID to blockchain config file."""
        config = {}
        try:
            if BLOCKCHAIN_CONFIG_FILE.exists():
                with open(BLOCKCHAIN_CONFIG_FILE, "r") as f:
                    config = json.load(f)
        except Exception:
            pass
        config[f"schema_uid_{self._network}"] = schema_uid
        with open(BLOCKCHAIN_CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)

    def _ensure_schema_registered(self) -> Tuple[bool, str]:
        """Register the Attestix EAS schema if not already registered.

        Returns (success, schema_uid_hex_or_error_message).
        """
        if self._schema_uid:
            return True, self._schema_uid

        try:
            from blockchain.abi import ATTESTIX_SCHEMA
            from web3 import Web3

            zero_addr = Web3.to_checksum_address(
                "0x0000000000000000000000000000000000000000"
            )

            tx = self._schema_registry.functions.register(
                ATTESTIX_SCHEMA,
                zero_addr,
                True,
            ).build_transaction({
                "from": self._account.address,
                "nonce": self._w3.eth.get_transaction_count(self._account.address),
                "gas": 200000,
                "maxFeePerGas": self._w3.eth.gas_price * 2,
                "maxPriorityFeePerGas": self._w3.eth.max_priority_fee,
                "chainId": NETWORKS[self._network]["chain_id"],
            })

            signed = self._account.sign_transaction(tx)
            tx_hash = self._w3.eth.send_raw_transaction(signed.raw_transaction)
            receipt = self._w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)

            if receipt["status"] != 1:
                return False, "Schema registration transaction reverted"

            # Extract schema UID from the Registered event log
            schema_uid_hex = None
            if receipt["logs"]:
                # The first topic after the event signature is the schema UID
                log = receipt["logs"][0]
                if len(log.get("topics", [])) > 1:
                    schema_uid_hex = "0x" + log["topics"][1].hex()
                elif log.get("data"):
                    schema_uid_hex = "0x" + log["data"].hex()[:64]

            if not schema_uid_hex:
                # Fallback: hash the schema deterministically
                schema_uid_hex = "0x" + Web3.keccak(
                    text=ATTESTIX_SCHEMA
                ).hex()

            self._schema_uid = schema_uid_hex
            self._save_schema_uid(schema_uid_hex)

            return True, schema_uid_hex
        except Exception as e:
            msg = log_and_format_error(
                "_ensure_schema_registered", e, ErrorCategory.BLOCKCHAIN,
            )
            return False, msg

    # --- Hashing ---

    def hash_artifact(self, artifact: dict) -> str:
        """Compute SHA-256 hash of a canonical JSON artifact.

        Uses the same normalization as sign_json_payload for consistency.
        Returns hex string (64 chars).
        """
        normalized = _normalize_for_signing(artifact)
        canonical = json.dumps(
            normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    # --- Core Anchoring ---

    def anchor_artifact(
        self,
        artifact_hash: str,
        artifact_type: str,
        artifact_id: str,
    ) -> dict:
        """Submit an artifact hash to EAS on Base L2.

        Returns anchor record with tx_hash, attestation_uid, etc.
        """
        err = self._require_configured()
        if err:
            return {"error": err}

        if artifact_type not in VALID_ARTIFACT_TYPES:
            return {
                "error": (
                    f"Invalid artifact_type '{artifact_type}'. "
                    f"Must be one of: {', '.join(sorted(VALID_ARTIFACT_TYPES))}"
                )
            }

        try:
            ok, schema_uid_or_err = self._ensure_schema_registered()
            if not ok:
                return {"error": f"Schema registration failed: {schema_uid_or_err}"}

            from web3 import Web3
            from eth_abi import encode

            artifact_hash_bytes = bytes.fromhex(artifact_hash)
            encoded_data = encode(
                ["bytes32", "string", "string", "string"],
                [artifact_hash_bytes, artifact_type, artifact_id, self._server_did],
            )

            schema_uid_bytes = bytes.fromhex(self._schema_uid.replace("0x", ""))

            attestation_request = (
                schema_uid_bytes,
                (
                    self._account.address,  # recipient (self-attestation)
                    0,                      # expirationTime (no expiry)
                    True,                   # revocable
                    b"\x00" * 32,           # refUID (no reference)
                    encoded_data,           # data
                    0,                      # value (no ETH)
                ),
            )

            tx = self._eas_contract.functions.attest(
                attestation_request
            ).build_transaction({
                "from": self._account.address,
                "nonce": self._w3.eth.get_transaction_count(self._account.address),
                "gas": 300000,
                "maxFeePerGas": self._w3.eth.gas_price * 2,
                "maxPriorityFeePerGas": self._w3.eth.max_priority_fee,
                "chainId": NETWORKS[self._network]["chain_id"],
                "value": 0,
            })

            signed = self._account.sign_transaction(tx)
            tx_hash = self._w3.eth.send_raw_transaction(signed.raw_transaction)
            receipt = self._w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

            if receipt["status"] != 1:
                return {
                    "error": "Attestation transaction reverted. Check gas and balance."
                }

            # Extract attestation UID from Attested event log
            attestation_uid = "unknown"
            if receipt["logs"]:
                log = receipt["logs"][0]
                if len(log.get("topics", [])) > 1:
                    attestation_uid = "0x" + log["topics"][1].hex()
                elif log.get("data"):
                    attestation_uid = "0x" + log["data"].hex()[:64]

            anchor_id = f"anchor:{uuid.uuid4().hex[:12]}"
            now = datetime.now(timezone.utc).isoformat()
            network_config = NETWORKS[self._network]
            tx_hash_hex = (
                tx_hash.hex() if isinstance(tx_hash, bytes) else str(tx_hash)
            )

            anchor = {
                "anchor_id": anchor_id,
                "artifact_type": artifact_type,
                "artifact_id": artifact_id,
                "artifact_hash": artifact_hash,
                "network": self._network,
                "chain_id": network_config["chain_id"],
                "tx_hash": tx_hash_hex,
                "attestation_uid": attestation_uid,
                "schema_uid": self._schema_uid,
                "attester": self._account.address,
                "block_number": receipt["blockNumber"],
                "gas_used": receipt["gasUsed"],
                "explorer_url": f"{network_config['explorer']}/tx/{tx_hash_hex}",
                "anchored_at": now,
                "issuer_did": self._server_did,
            }

            data = load_anchors()
            data["anchors"].append(anchor)
            save_anchors(data)

            return anchor

        except Exception as e:
            msg = log_and_format_error(
                "anchor_artifact", e, ErrorCategory.BLOCKCHAIN,
                artifact_type=artifact_type, artifact_id=artifact_id,
            )
            return {"error": msg}

    # --- Verification ---

    def verify_anchor(self, artifact_hash: str) -> dict:
        """Verify an on-chain anchor for a given artifact hash.

        Checks local registry first, then verifies on-chain if configured.
        """
        data = load_anchors()
        local_matches = [
            a for a in data["anchors"] if a["artifact_hash"] == artifact_hash
        ]

        err = self._require_configured()
        if err:
            if local_matches:
                return {
                    "verified": "local_only",
                    "note": "Cannot verify on-chain (blockchain not configured). Local record found.",
                    "anchors": local_matches,
                }
            return {"error": err}

        if not local_matches:
            return {
                "verified": False,
                "artifact_hash": artifact_hash,
                "reason": "No local anchor record found for this hash",
            }

        try:
            results = []
            for anchor in local_matches:
                uid = anchor.get("attestation_uid", "")
                if uid and uid != "unknown" and len(uid) == 66:
                    uid_bytes = bytes.fromhex(uid.replace("0x", ""))
                    is_valid = self._eas_contract.functions.isAttestationValid(
                        uid_bytes
                    ).call()
                    on_chain = self._eas_contract.functions.getAttestation(
                        uid_bytes
                    ).call()

                    results.append({
                        **anchor,
                        "on_chain_valid": is_valid,
                        "on_chain_time": on_chain[2],
                        "on_chain_attester": on_chain[7],
                    })
                else:
                    results.append({**anchor, "on_chain_valid": "unknown_uid"})

            all_valid = all(r.get("on_chain_valid") is True for r in results)
            return {
                "verified": all_valid,
                "artifact_hash": artifact_hash,
                "anchor_count": len(results),
                "anchors": results,
            }
        except Exception as e:
            msg = log_and_format_error(
                "verify_anchor", e, ErrorCategory.BLOCKCHAIN,
                artifact_hash=artifact_hash,
            )
            return {"error": msg}

    # --- Batch Anchoring ---

    def anchor_audit_batch(
        self,
        agent_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> dict:
        """Compute Merkle root of audit log entries and anchor on-chain."""
        err = self._require_configured()
        if err:
            return {"error": err}

        try:
            from config import load_provenance
            from blockchain.merkle import compute_merkle_root

            prov_data = load_provenance()
            entries = [
                e for e in prov_data["audit_log"]
                if e.get("agent_id") == agent_id
            ]

            if start_date:
                entries = [
                    e for e in entries if e.get("timestamp", "") >= start_date
                ]
            if end_date:
                entries = [
                    e for e in entries if e.get("timestamp", "") <= end_date
                ]

            if not entries:
                return {
                    "error": (
                        f"No audit log entries found for {agent_id} "
                        f"in the specified range"
                    )
                }

            merkle_root, leaf_count = compute_merkle_root(entries)

            batch_id = f"batch:{uuid.uuid4().hex[:12]}"
            result = self.anchor_artifact(
                artifact_hash=merkle_root,
                artifact_type="audit_batch",
                artifact_id=batch_id,
            )

            if "error" in result:
                return result

            result["batch_metadata"] = {
                "agent_id": agent_id,
                "entry_count": leaf_count,
                "merkle_root": merkle_root,
                "start_date": start_date or entries[0].get("timestamp"),
                "end_date": end_date or entries[-1].get("timestamp"),
            }

            return result
        except Exception as e:
            msg = log_and_format_error(
                "anchor_audit_batch", e, ErrorCategory.BLOCKCHAIN,
                agent_id=agent_id,
            )
            return {"error": msg}

    # --- Status Queries ---

    def get_anchor_status(self, agent_id: str) -> dict:
        """Get all on-chain anchors associated with an agent."""
        try:
            data = load_anchors()

            agent_anchors = []
            for anchor in data["anchors"]:
                aid = anchor.get("artifact_id", "")
                if agent_id in aid:
                    agent_anchors.append(anchor)
                    continue
                batch_meta = anchor.get("batch_metadata", {})
                if batch_meta and batch_meta.get("agent_id") == agent_id:
                    agent_anchors.append(anchor)

            by_type = {}
            for a in agent_anchors:
                t = a.get("artifact_type", "unknown")
                by_type.setdefault(t, []).append(a)

            return {
                "agent_id": agent_id,
                "total_anchors": len(agent_anchors),
                "by_type": {k: len(v) for k, v in by_type.items()},
                "anchors": agent_anchors,
                "network": self._network,
                "wallet": self.wallet_address,
            }
        except Exception as e:
            msg = log_and_format_error(
                "get_anchor_status", e, ErrorCategory.BLOCKCHAIN,
                agent_id=agent_id,
            )
            return {"error": msg}

    # --- Gas Estimation ---

    def estimate_anchor_cost(self, artifact_type: str = "identity") -> dict:
        """Estimate gas cost for an anchoring transaction."""
        err = self._require_configured()
        if err:
            return {"error": err}

        try:
            gas_price = self._w3.eth.gas_price
            max_priority_fee = self._w3.eth.max_priority_fee
            balance = self._w3.eth.get_balance(self._account.address)
            estimated_gas = 250000

            estimated_cost_wei = estimated_gas * gas_price
            estimated_cost_eth = self._w3.from_wei(estimated_cost_wei, "ether")
            balance_eth = self._w3.from_wei(balance, "ether")

            network_config = NETWORKS[self._network]
            return {
                "network": self._network,
                "chain_id": network_config["chain_id"],
                "wallet": self._account.address,
                "balance_eth": str(balance_eth),
                "estimated_gas": estimated_gas,
                "gas_price_gwei": str(self._w3.from_wei(gas_price, "gwei")),
                "max_priority_fee_gwei": str(
                    self._w3.from_wei(max_priority_fee, "gwei")
                ),
                "estimated_cost_eth": str(estimated_cost_eth),
                "can_afford": balance >= estimated_cost_wei,
                "artifact_type": artifact_type,
                "explorer": network_config["explorer"],
            }
        except Exception as e:
            msg = log_and_format_error(
                "estimate_anchor_cost", e, ErrorCategory.BLOCKCHAIN,
            )
            return {"error": msg}
