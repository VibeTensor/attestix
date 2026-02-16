"""Core identity service for AURA Protocol.

Manages Unified Agent Identity Tokens (UAITs): create, read, list,
revoke, verify, and sign operations.
"""

import hashlib
import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from auth.crypto import (
    load_or_create_signing_key,
    public_key_to_did_key,
    sign_json_payload,
    verify_json_signature,
    did_key_to_public_key,
)
from auth.token_parser import extract_identity_from_token
from config import (
    DEFAULT_EXPIRY_DAYS,
    UAIT_VERSION,
    load_identities,
    save_identities,
)
from errors import ErrorCategory, log_and_format_error


class IdentityService:
    """Manages UAIT lifecycle."""

    # Fields excluded from signature (mutable after creation)
    MUTABLE_FIELDS = {"signature", "revoked", "revocation_reason", "revoked_at",
                      "reputation_score", "eu_compliance"}

    def __init__(self):
        self._private_key, self._server_did = load_or_create_signing_key()

    def _signable_payload(self, uait: dict) -> dict:
        """Extract only immutable fields for signing/verification."""
        return {k: v for k, v in uait.items() if k not in self.MUTABLE_FIELDS}

    @property
    def server_did(self) -> str:
        return self._server_did

    def create_identity(
        self,
        display_name: str,
        source_protocol: str,
        identity_token: str = "",
        capabilities: Optional[List[str]] = None,
        description: str = "",
        issuer_name: str = "",
        expiry_days: Optional[int] = None,
    ) -> dict:
        """Create a new UAIT from any identity source."""
        agent_id = f"aura:{uuid.uuid4().hex[:16]}"
        now = datetime.now(timezone.utc)
        exp_days = expiry_days if expiry_days is not None else DEFAULT_EXPIRY_DAYS
        expires_at = (now + timedelta(days=exp_days)).isoformat()

        # Extract info from token if provided
        token_info = {}
        if identity_token:
            token_info = extract_identity_from_token(identity_token)

        uait = {
            "version": UAIT_VERSION,
            "agent_id": agent_id,
            "display_name": display_name,
            "description": description,
            "source_protocol": source_protocol,
            "identity_token": identity_token,
            "token_info": token_info,
            "capabilities": capabilities or [],
            "issuer": {
                "name": issuer_name or "self",
                "did": self._server_did,
            },
            "created_at": now.isoformat(),
            "expires_at": expires_at,
            "revoked": False,
            "revocation_reason": None,
            "reputation_score": None,
            "eu_compliance": None,
            "signature": None,
        }

        # Sign only immutable fields
        signable = self._signable_payload(uait)
        uait["signature"] = sign_json_payload(self._private_key, signable)

        # Persist
        data = load_identities()
        data["agents"].append(uait)
        save_identities(data)

        return uait

    def get_identity(self, agent_id: str) -> Optional[dict]:
        """Get a single UAIT by agent_id."""
        data = load_identities()
        for agent in data["agents"]:
            if agent["agent_id"] == agent_id:
                return agent
        return None

    def list_identities(
        self,
        source_protocol: Optional[str] = None,
        include_revoked: bool = False,
        limit: int = 50,
    ) -> List[dict]:
        """List UAITs with optional filters."""
        data = load_identities()
        results = []
        for agent in data["agents"]:
            if not include_revoked and agent.get("revoked"):
                continue
            if source_protocol and agent.get("source_protocol") != source_protocol:
                continue
            results.append(agent)
            if len(results) >= limit:
                break
        return results

    def revoke_identity(self, agent_id: str, reason: str = "") -> Optional[dict]:
        """Mark a UAIT as revoked."""
        data = load_identities()
        for agent in data["agents"]:
            if agent["agent_id"] == agent_id:
                agent["revoked"] = True
                agent["revocation_reason"] = reason
                agent["revoked_at"] = datetime.now(timezone.utc).isoformat()
                save_identities(data)
                return agent
        return None

    def verify_identity(self, agent_id: str) -> dict:
        """Verify a UAIT: check existence, revocation, expiry, and signature."""
        agent = self.get_identity(agent_id)
        if not agent:
            return {
                "valid": False,
                "agent_id": agent_id,
                "checks": {"exists": False},
            }

        checks = {"exists": True}

        # Check revocation
        checks["not_revoked"] = not agent.get("revoked", False)

        # Check expiry
        expires_at = agent.get("expires_at")
        if expires_at:
            exp_dt = datetime.fromisoformat(expires_at)
            checks["not_expired"] = datetime.now(timezone.utc) < exp_dt
        else:
            checks["not_expired"] = True

        # Check signature (only immutable fields)
        signature = agent.get("signature")
        if signature:
            signable = self._signable_payload(agent)
            try:
                server_pub = did_key_to_public_key(self._server_did)
                checks["signature_valid"] = verify_json_signature(
                    server_pub, signable, signature
                )
            except ValueError as e:
                checks["signature_valid"] = False
                checks["signature_error"] = f"Key error: {e}"
            except Exception as e:
                checks["signature_valid"] = False
                checks["signature_error"] = str(e)
                log_and_format_error("verify_identity", e, ErrorCategory.CRYPTO,
                                     agent_id=agent_id)
        else:
            checks["signature_valid"] = False

        valid = all(checks.values())
        return {
            "valid": valid,
            "agent_id": agent_id,
            "display_name": agent.get("display_name"),
            "checks": checks,
        }

    def translate_identity(self, agent_id: str, target_format: str) -> Optional[dict]:
        """Convert a UAIT to another format.

        Supported target_format values:
        - a2a_agent_card: Google A2A Agent Card JSON
        - did_document: W3C DID Document
        - oauth_claims: OAuth 2.0 token claims
        - summary: Human-readable summary
        """
        agent = self.get_identity(agent_id)
        if not agent:
            return None

        if target_format == "a2a_agent_card":
            return self._to_agent_card(agent)
        elif target_format == "did_document":
            return self._to_did_document(agent)
        elif target_format == "oauth_claims":
            return self._to_oauth_claims(agent)
        elif target_format == "summary":
            return self._to_summary(agent)
        else:
            return {"error": f"Unknown target format: {target_format}"}

    def update_compliance_ref(self, agent_id: str, profile_id: str):
        """Link an EU AI Act compliance profile to a UAIT."""
        data = load_identities()
        for agent in data["agents"]:
            if agent["agent_id"] == agent_id:
                agent["eu_compliance"] = profile_id
                save_identities(data)
                return
        return

    def update_reputation(self, agent_id: str, score: float):
        """Update the reputation score on a UAIT."""
        data = load_identities()
        for agent in data["agents"]:
            if agent["agent_id"] == agent_id:
                agent["reputation_score"] = round(score, 4)
                save_identities(data)
                return
        return

    # --- Translation helpers ---

    def _to_agent_card(self, agent: dict) -> dict:
        """Convert UAIT to A2A Agent Card format."""
        skills = []
        for cap in agent.get("capabilities", []):
            skills.append({
                "id": hashlib.sha256(cap.encode()).hexdigest()[:8],
                "name": cap,
                "description": f"Capability: {cap}",
            })

        return {
            "name": agent["display_name"],
            "description": agent.get("description", ""),
            "url": f"aura://{agent['agent_id']}",
            "version": agent.get("version", UAIT_VERSION),
            "capabilities": {
                "streaming": False,
                "pushNotifications": False,
            },
            "skills": skills,
            "provider": {
                "organization": agent["issuer"].get("name", ""),
            },
            "authentication": {
                "schemes": ["aura-uait"],
                "credentials": agent["agent_id"],
            },
            "_aura_metadata": {
                "agent_id": agent["agent_id"],
                "source_protocol": agent.get("source_protocol"),
                "reputation_score": agent.get("reputation_score"),
            },
        }

    def _to_did_document(self, agent: dict) -> dict:
        """Convert UAIT to W3C DID Document format."""
        did = agent["issuer"].get("did", f"did:aura:{agent['agent_id']}")
        # Get public key multibase for the server DID
        pub_multibase = None
        if did.startswith("did:key:z"):
            try:
                from auth.crypto import did_key_to_public_key, public_key_to_bytes
                import base58
                pub_key = did_key_to_public_key(did)
                pub_multibase = "z" + base58.b58encode(
                    public_key_to_bytes(pub_key)
                ).decode("ascii")
            except Exception:
                pass

        vm = {
            "id": f"{did}#key-1",
            "type": "Ed25519VerificationKey2020",
            "controller": did,
        }
        if pub_multibase:
            vm["publicKeyMultibase"] = pub_multibase

        return {
            "@context": [
                "https://www.w3.org/ns/did/v1",
                "https://w3id.org/security/suites/ed25519-2020/v1",
            ],
            "id": did,
            "controller": did,
            "verificationMethod": [vm],
            "authentication": [f"{did}#key-1"],
            "service": [
                {
                    "id": f"{did}#aura",
                    "type": "AURAIdentity",
                    "serviceEndpoint": {
                        "agent_id": agent["agent_id"],
                        "display_name": agent["display_name"],
                        "capabilities": agent.get("capabilities", []),
                    },
                }
            ],
        }

    def _to_oauth_claims(self, agent: dict) -> dict:
        """Convert UAIT to OAuth 2.0 token claims."""
        return {
            "sub": agent["agent_id"],
            "iss": agent["issuer"].get("did", "aura-protocol"),
            "name": agent["display_name"],
            "scope": " ".join(agent.get("capabilities", [])),
            "iat": agent.get("created_at"),
            "exp": agent.get("expires_at"),
            "aura_version": agent.get("version"),
            "source_protocol": agent.get("source_protocol"),
        }

    def _to_summary(self, agent: dict) -> dict:
        """Human-readable summary of a UAIT."""
        return {
            "agent_id": agent["agent_id"],
            "display_name": agent["display_name"],
            "description": agent.get("description", ""),
            "source_protocol": agent.get("source_protocol"),
            "capabilities": agent.get("capabilities", []),
            "issuer": agent["issuer"].get("name", ""),
            "created_at": agent.get("created_at"),
            "expires_at": agent.get("expires_at"),
            "revoked": agent.get("revoked", False),
            "reputation_score": agent.get("reputation_score"),
            "eu_compliance": agent.get("eu_compliance"),
            "signature_present": bool(agent.get("signature")),
        }
