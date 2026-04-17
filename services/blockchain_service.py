"""Blockchain anchoring service for Attestix.

Anchors cryptographic hashes of off-chain artifacts (UAITs, VCs, audit log
batches, compliance declarations) to Base L2 via Ethereum Attestation Service.

Optional: works only when EVM_PRIVATE_KEY is set in .env.
"""

import hashlib
import json
import threading
import uuid
from datetime import datetime, timezone
from typing import Optional, Tuple

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
        self._tx_lock = threading.Lock()
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

    @staticmethod
    def compute_schema_uid(
        schema: str,
        resolver: str = "0x0000000000000000000000000000000000000000",
        revocable: bool = True,
    ) -> str:
        """Compute the canonical EAS schema UID.

        Mirrors SchemaRegistry._getUID in the EAS contracts:
            keccak256(abi.encodePacked(schema, resolver, revocable))

        Reference:
        https://github.com/ethereum-attestation-service/eas-contracts/blob/master/contracts/SchemaRegistry.sol

        Returns a 0x-prefixed 66-character hex string.
        """
        from web3 import Web3
        from eth_abi.packed import encode_packed

        resolver_checksum = Web3.to_checksum_address(resolver)
        packed = encode_packed(
            ["string", "address", "bool"],
            [schema, resolver_checksum, bool(revocable)],
        )
        digest_hex = Web3.keccak(packed).hex()
        if not digest_hex.startswith("0x"):
            digest_hex = "0x" + digest_hex
        return digest_hex

    def _load_schema_uid(self) -> Optional[str]:
        """Load cached schema UID from blockchain config file."""
        try:
            if BLOCKCHAIN_CONFIG_FILE.exists():
                with open(BLOCKCHAIN_CONFIG_FILE, "r") as f:
                    config = json.load(f)
                return config.get(f"schema_uid_{self._network}")
        except (OSError, json.JSONDecodeError, KeyError):
            pass  # Config file missing or corrupt, return None
        return None

    def _save_schema_uid(self, schema_uid: str):
        """Cache schema UID to blockchain config file."""
        config = {}
        try:
            if BLOCKCHAIN_CONFIG_FILE.exists():
                with open(BLOCKCHAIN_CONFIG_FILE, "r") as f:
                    config = json.load(f)
        except (OSError, json.JSONDecodeError):
            pass  # Start fresh if config is unreadable
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
            revocable = True

            # EAS schema UIDs are deterministic:
            #   keccak256(abi.encodePacked(schema, resolver, revocable))
            # Derive the UID offline so we can (a) skip registration if the
            # schema already exists on-chain and (b) use it as a safe fallback
            # if log parsing ever fails. Hashing the schema string alone
            # produces the WRONG UID and breaks on-chain verification.
            canonical_uid = self.compute_schema_uid(
                ATTESTIX_SCHEMA, zero_addr, revocable
            )

            # If already registered on-chain, reuse without spending gas.
            try:
                uid_bytes = bytes.fromhex(canonical_uid[2:])
                existing = self._schema_registry.functions.getSchema(
                    uid_bytes
                ).call()
                existing_uid = existing[0] if existing else b"\x00" * 32
                if isinstance(existing_uid, (bytes, bytearray)) and any(
                    existing_uid
                ):
                    self._schema_uid = canonical_uid
                    self._save_schema_uid(canonical_uid)
                    return True, canonical_uid
            except Exception:
                # getSchema lookup failed; fall through and register.
                pass

            with self._tx_lock:
                tx = self._schema_registry.functions.register(
                    ATTESTIX_SCHEMA,
                    zero_addr,
                    revocable,
                ).build_transaction({
                    "from": self._account.address,
                    "nonce": self._w3.eth.get_transaction_count(
                        self._account.address, "pending"
                    ),
                    "gas": 200000,
                    "maxFeePerGas": self._w3.eth.gas_price * 2,
                    "maxPriorityFeePerGas": self._w3.eth.max_priority_fee,
                    "chainId": NETWORKS[self._network]["chain_id"],
                })

                signed = self._account.sign_transaction(tx)
                tx_hash = self._w3.eth.send_raw_transaction(
                    signed.raw_transaction
                )
            receipt = self._w3.eth.wait_for_transaction_receipt(
                tx_hash, timeout=60
            )

            if receipt["status"] != 1:
                return False, "Schema registration transaction reverted"

            # Extract schema UID from Registered(bytes32 indexed uid, ...):
            # topics[0] is the event signature, topics[1] is the indexed uid.
            schema_uid_hex = None
            for log in receipt.get("logs", []):
                topics = log.get("topics", [])
                if len(topics) > 1:
                    topic = topics[1]
                    if isinstance(topic, (bytes, bytearray)):
                        topic_hex = bytes(topic).hex()
                    else:
                        topic_hex = str(topic).replace("0x", "")
                    if topic_hex and int(topic_hex, 16) != 0:
                        schema_uid_hex = (
                            topic_hex if topic_hex.startswith("0x")
                            else "0x" + topic_hex
                        )
                        break

            if not schema_uid_hex:
                # Safe fallback: canonical UID matches the on-chain UID by
                # construction. Never hash the schema text alone.
                schema_uid_hex = canonical_uid

            self._schema_uid = schema_uid_hex
            self._save_schema_uid(schema_uid_hex)

            return True, schema_uid_hex
        except Exception as e:
            msg = log_and_format_error(
                "_ensure_schema_registered", e, ErrorCategory.BLOCKCHAIN,
            )
            return False, msg

    # --- Event Decoding ---

    def _extract_attestation_uid(self, receipt) -> str:
        """Decode the Attested event from a tx receipt and return the UID.

        Uses ``contract.events.Attested().process_log(log)`` (web3.py's ABI
        decoder) so we do not rely on fragile byte offsets. Falls back to
        manual decoding when the Attested event is not on the ABI or the log
        is not parseable. Returns "unknown" if no Attested log is present.
        """
        logs = receipt.get("logs") if isinstance(receipt, dict) else getattr(
            receipt, "logs", None
        )
        if not logs:
            return "unknown"

        # Prefer structured ABI decoding when the event is on the ABI.
        attested_event = None
        try:
            attested_event = self._eas_contract.events.Attested()
        except Exception:
            attested_event = None

        if attested_event is not None:
            for log in logs:
                try:
                    decoded = attested_event.process_log(log)
                except Exception:
                    # Not an Attested event or ABI mismatch; try next log.
                    continue
                args = decoded.get("args", {}) if hasattr(decoded, "get") \
                    else getattr(decoded, "args", {})
                uid = None
                if hasattr(args, "get"):
                    uid = args.get("uid")
                else:
                    uid = getattr(args, "uid", None)
                if isinstance(uid, (bytes, bytearray)) and any(uid):
                    return "0x" + bytes(uid).hex()

        # Manual fallback: match Attested event by topic[0] signature and
        # read the single non-indexed ``uid`` word (first 32 bytes of data).
        try:
            from web3 import Web3
            sig_topic = bytes(
                Web3.keccak(text="Attested(address,address,bytes32,bytes32)")
            )
            for log in logs:
                topics = log.get("topics") if isinstance(log, dict) else getattr(
                    log, "topics", []
                )
                if not topics:
                    continue
                first = topics[0]
                first_bytes = (
                    bytes(first) if isinstance(first, (bytes, bytearray))
                    else bytes.fromhex(str(first).replace("0x", ""))
                )
                if first_bytes != sig_topic:
                    continue
                data = log.get("data") if isinstance(log, dict) else getattr(
                    log, "data", b""
                )
                data_bytes = (
                    bytes(data) if isinstance(data, (bytes, bytearray))
                    else bytes.fromhex(str(data).replace("0x", ""))
                )
                if len(data_bytes) >= 32:
                    uid = data_bytes[:32]
                    if any(uid):
                        return "0x" + uid.hex()
        except Exception:
            pass

        return "unknown"

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

            with self._tx_lock:
                tx = self._eas_contract.functions.attest(
                    attestation_request
                ).build_transaction({
                    "from": self._account.address,
                    "nonce": self._w3.eth.get_transaction_count(
                        self._account.address, "pending"
                    ),
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

            # Extract attestation UID via the Attested event ABI decoder.
            # EAS interface:
            #   Attested(address indexed recipient,
            #            address indexed attester,
            #            bytes32 uid,
            #            bytes32 indexed schemaUID)
            # The uid is the single non-indexed field, so naive byte slicing
            # (which was previously used) is fragile: it assumed the first log
            # was always Attested and that log.data started with the uid. We
            # now use contract.events.Attested().process_log(log) with a
            # topic-signature fallback so the uid is decoded correctly even
            # when other contracts emit logs in the same transaction.
            attestation_uid = self._extract_attestation_uid(receipt)

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

                    revocation_time = on_chain[4] if len(on_chain) > 4 else 0
                    results.append({
                        **anchor,
                        "on_chain_valid": is_valid,
                        "on_chain_time": on_chain[2],
                        "on_chain_revocation_time": revocation_time,
                        "on_chain_revoked": revocation_time != 0,
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
            estimated_gas = 300000  # matches actual tx gas limit

            # Use EIP-1559 max fee (gas_price * 2) for worst-case estimate
            max_fee = gas_price * 2
            estimated_cost_wei = estimated_gas * max_fee
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
