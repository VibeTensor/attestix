"""UCAN-style delegation service for AURA Protocol.

Creates, verifies, and manages JWT-based delegation tokens
following the UCAN (User Controlled Authorization Networks) pattern
with capability attenuation.
"""

import json
import time
from datetime import datetime, timezone
from typing import List, Optional

import jwt

from auth.crypto import load_or_create_signing_key, did_key_to_public_key, public_key_to_bytes
from config import load_delegations, save_delegations
from errors import ErrorCategory, log_and_format_error

import base64


class DelegationService:
    """Manages UCAN-style delegation tokens between agents."""

    def __init__(self):
        self._private_key, self._server_did = load_or_create_signing_key()
        # EdDSA signing requires the raw seed bytes for PyJWT
        from auth.crypto import private_key_to_bytes
        self._private_key_bytes = private_key_to_bytes(self._private_key)

    def create_delegation(
        self,
        issuer_agent_id: str,
        audience_agent_id: str,
        capabilities: List[str],
        expiry_hours: int = 24,
    ) -> dict:
        """Create a UCAN-style delegation JWT.

        Args:
            issuer_agent_id: The agent granting capabilities.
            audience_agent_id: The agent receiving capabilities.
            capabilities: List of capability strings being delegated.
            expiry_hours: How long the delegation is valid.
        """
        try:
            now = int(time.time())
            exp = now + (expiry_hours * 3600)

            payload = {
                "iss": issuer_agent_id,
                "aud": audience_agent_id,
                "sub": audience_agent_id,
                "iat": now,
                "exp": exp,
                "nbf": now,
                "cap": capabilities,
                "prf": [],  # proof chain (empty for root delegation)
                "aura_version": "0.1.0",
                "typ": "ucan/delegation",
            }

            # Sign with server key using Ed25519/EdDSA
            token = jwt.encode(
                payload,
                self._private_key,
                algorithm="EdDSA",
                headers={
                    "typ": "JWT",
                    "ucv": "0.10.0",  # UCAN version
                    "alg": "EdDSA",
                },
            )

            # Record delegation
            delegation_record = {
                "token": token,
                "issuer": issuer_agent_id,
                "audience": audience_agent_id,
                "capabilities": capabilities,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "expires_at": datetime.fromtimestamp(exp, tz=timezone.utc).isoformat(),
                "revoked": False,
            }

            data = load_delegations()
            data["delegations"].append(delegation_record)
            save_delegations(data)

            return {
                "token": token,
                "delegation": delegation_record,
            }
        except Exception as e:
            return {
                "error": log_and_format_error(
                    "create_delegation", e, ErrorCategory.DELEGATION,
                    issuer=issuer_agent_id, audience=audience_agent_id,
                )
            }

    def verify_delegation(self, token: str) -> dict:
        """Verify a UCAN delegation token.

        Checks: signature validity, expiry, and structure.
        """
        try:
            # Get server public key for verification
            public_key = did_key_to_public_key(self._server_did)

            claims = jwt.decode(
                token,
                public_key,
                algorithms=["EdDSA"],
                options={"verify_aud": False},
            )

            return {
                "valid": True,
                "issuer": claims.get("iss"),
                "audience": claims.get("aud"),
                "capabilities": claims.get("cap", []),
                "issued_at": datetime.fromtimestamp(
                    claims["iat"], tz=timezone.utc
                ).isoformat(),
                "expires_at": datetime.fromtimestamp(
                    claims["exp"], tz=timezone.utc
                ).isoformat(),
                "expired": claims["exp"] < int(time.time()),
                "type": claims.get("typ"),
            }
        except jwt.ExpiredSignatureError:
            return {"valid": False, "reason": "Token has expired"}
        except jwt.InvalidTokenError as e:
            return {"valid": False, "reason": f"Invalid token: {str(e)}"}
        except Exception as e:
            return {
                "valid": False,
                "reason": log_and_format_error(
                    "verify_delegation", e, ErrorCategory.DELEGATION,
                ),
            }

    def list_delegations(
        self,
        agent_id: Optional[str] = None,
        role: str = "any",
        include_expired: bool = False,
    ) -> List[dict]:
        """List delegation records.

        Args:
            agent_id: Filter by this agent (as issuer or audience).
            role: 'issuer', 'audience', or 'any'.
            include_expired: Whether to include expired delegations.
        """
        data = load_delegations()
        results = []
        now = datetime.now(timezone.utc)

        for d in data["delegations"]:
            # Filter by agent_id and role
            if agent_id:
                if role == "issuer" and d.get("issuer") != agent_id:
                    continue
                elif role == "audience" and d.get("audience") != agent_id:
                    continue
                elif role == "any" and (
                    d.get("issuer") != agent_id and d.get("audience") != agent_id
                ):
                    continue

            # Filter expired
            if not include_expired:
                expires_at = d.get("expires_at")
                if expires_at:
                    exp_dt = datetime.fromisoformat(expires_at)
                    if now >= exp_dt:
                        continue

            # Filter revoked
            if d.get("revoked"):
                continue

            results.append(d)

        return results
