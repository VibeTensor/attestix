"""UCAN-style delegation service for Attestix.

Creates, verifies, and manages JWT-based delegation tokens
following the UCAN (User Controlled Authorization Networks) pattern
with capability attenuation.
"""

import secrets
import time
from datetime import datetime, timezone
from typing import List, Optional

import jwt

from auth.crypto import load_or_create_signing_key, did_key_to_public_key
from config import load_delegations, save_delegations
from errors import ErrorCategory, log_and_format_error


class DelegationService:
    """Manages UCAN-style delegation tokens between agents."""

    def __init__(self):
        self._private_key, self._server_did = load_or_create_signing_key()

    def create_delegation(
        self,
        issuer_agent_id: str,
        audience_agent_id: str,
        capabilities: List[str],
        expiry_hours: int = 24,
        parent_token: Optional[str] = None,
    ) -> dict:
        """Create a UCAN-style delegation JWT.

        Args:
            issuer_agent_id: The agent granting capabilities.
            audience_agent_id: The agent receiving capabilities.
            capabilities: List of capability strings being delegated.
            expiry_hours: How long the delegation is valid.
            parent_token: Optional parent delegation token for chaining.

        Security:
            When parent_token is provided, the parent is fully verified
            (signature, expiry, revocation, and recursively its own prf
            chain) BEFORE a new delegation is issued. The requested
            capabilities must also be a subset of the parent's att
            (UCAN capability attenuation). This prevents chain forgery
            and capability escalation attacks.
        """
        try:
            # Verify parent delegation and enforce capability attenuation
            # before issuing a new token. This is critical: without this
            # check, any caller could supply an arbitrary string as a
            # parent and claim delegated authority they never received.
            if parent_token is not None:
                parent_result = self.verify_delegation(parent_token)
                if not parent_result.get("valid"):
                    return {
                        "error": (
                            "Invalid parent delegation: "
                            f"{parent_result.get('reason', 'unknown reason')}"
                        )
                    }

                # Explicitly reject expired parents even if the JWT
                # library did not raise (belt and suspenders).
                if parent_result.get("expired"):
                    return {"error": "Invalid parent delegation: parent token has expired"}

                # Capability attenuation: a child delegation may only
                # grant a subset of the parent's capabilities. Issuing
                # capabilities not held by the parent is a privilege
                # escalation and must be rejected.
                parent_caps = set(parent_result.get("capabilities") or [])
                requested_caps = set(capabilities or [])
                if not requested_caps.issubset(parent_caps):
                    escalated = sorted(requested_caps - parent_caps)
                    return {
                        "error": (
                            "Capability escalation denied: requested capabilities "
                            f"{escalated} are not held by parent delegation"
                        )
                    }

            now = int(time.time())
            exp = now + (expiry_hours * 3600)
            jti = secrets.token_urlsafe(16)

            payload = {
                "iss": self._server_did,
                "aud": audience_agent_id,
                "sub": audience_agent_id,
                "iat": now,
                "exp": exp,
                "nbf": now,
                "jti": jti,
                "att": capabilities,
                "delegator": issuer_agent_id,
                "prf": [parent_token] if parent_token else [],
                "attestix_version": "0.1.0",
                "typ": "ucan/delegation",
            }

            # Sign with server key using Ed25519/EdDSA
            token = jwt.encode(
                payload,
                self._private_key,
                algorithm="EdDSA",
                headers={
                    "typ": "JWT",
                    "ucv": "0.9.0",  # UCAN version
                    "alg": "EdDSA",
                },
            )

            # Record delegation (token omitted from persistent storage for security)
            delegation_record = {
                "jti": jti,
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

    def verify_delegation(self, token: str, _seen: Optional[set] = None) -> dict:
        """Verify a UCAN delegation token.

        Checks: signature validity, expiry, revocation, structure, and
        recursively the validity of every parent token referenced in the
        `prf` (proof) chain. If any ancestor is invalid (bad signature,
        expired, revoked, or itself has a bad parent), the whole chain
        is rejected.

        Args:
            token: The JWT delegation token to verify.
            _seen: Internal set of jti values already seen during
                recursion. Used to detect cycles and prevent infinite
                recursion on malicious/looped proof chains.
        """
        # Track jtis seen in this verification run to prevent cycles.
        if _seen is None:
            _seen = set()

        try:
            # Get server public key for verification
            public_key = did_key_to_public_key(self._server_did)

            claims = jwt.decode(
                token,
                public_key,
                algorithms=["EdDSA"],
                options={"verify_aud": False},
            )

            # Check revocation by jti
            jti = claims.get("jti")
            if jti:
                data = load_delegations()
                for d in data["delegations"]:
                    if d.get("jti") == jti and d.get("revoked"):
                        return {"valid": False, "reason": "Token has been revoked"}

            # Detect cycles in the proof chain. A well-formed chain is
            # acyclic, so seeing the same jti twice indicates tampering
            # or a malicious loop. Bail out rather than recurse forever.
            if jti and jti in _seen:
                return {
                    "valid": False,
                    "reason": "Cycle detected in delegation proof chain",
                }
            if jti:
                _seen.add(jti)

            # Recursively verify every parent token in the prf chain.
            # Without this, an attacker could forge a parent_token value
            # at creation time (if validation is bypassed) or present
            # this token to downstream consumers who rely on the chain
            # for authority. Any invalid ancestor invalidates the whole
            # chain.
            proof_chain = claims.get("prf", []) or []
            for parent_token in proof_chain:
                if not isinstance(parent_token, str) or not parent_token:
                    return {
                        "valid": False,
                        "reason": "Malformed parent token in proof chain",
                    }
                parent_result = self.verify_delegation(parent_token, _seen=_seen)
                if not parent_result.get("valid"):
                    return {
                        "valid": False,
                        "reason": (
                            "Invalid parent in proof chain: "
                            f"{parent_result.get('reason', 'unknown reason')}"
                        ),
                    }
                # Also reject if a parent is expired. jwt.decode raises
                # ExpiredSignatureError by default, but we guard against
                # any future change that might relax that.
                if parent_result.get("expired"):
                    return {
                        "valid": False,
                        "reason": "Parent delegation in proof chain has expired",
                    }

            return {
                "valid": True,
                "jti": jti,
                "delegator": claims.get("delegator"),
                "audience": claims.get("aud"),
                "capabilities": claims.get("att", []),
                "proof_chain": claims.get("prf", []),
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
            # Log the underlying PyJWT error server-side (may include
            # "Signature verification failed", "Not enough segments", etc.)
            # but return a generic message so internal token internals don't
            # leak to API callers.
            log_and_format_error(
                "verify_delegation", e, ErrorCategory.DELEGATION,
                user_message="Invalid delegation token",
            )
            return {"valid": False, "reason": "Invalid token"}
        except Exception as e:
            return {
                "valid": False,
                "reason": log_and_format_error(
                    "verify_delegation", e, ErrorCategory.DELEGATION,
                ),
            }

    def revoke_delegation(self, jti: str, reason: str = "") -> dict:
        """Revoke a delegation by its JTI (JWT ID).

        Args:
            jti: The unique identifier of the delegation token.
            reason: Why this delegation is being revoked.
        """
        try:
            data = load_delegations()
            for d in data["delegations"]:
                if d.get("jti") == jti:
                    if d.get("revoked"):
                        return {"error": f"Delegation {jti} is already revoked"}
                    d["revoked"] = True
                    d["revocation_reason"] = reason
                    d["revoked_at"] = datetime.now(timezone.utc).isoformat()
                    save_delegations(data)
                    return {
                        "revoked": True,
                        "jti": jti,
                        "reason": reason,
                    }
            return {"error": f"Delegation {jti} not found"}
        except Exception as e:
            return {
                "error": log_and_format_error(
                    "revoke_delegation", e, ErrorCategory.DELEGATION,
                    jti=jti,
                )
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
