"""DID resolution service for Attestix.

Supports:
- did:key (local resolution, Ed25519)
- did:web (HTTP-based resolution)
- Universal Resolver fallback for all other DID methods
"""

import json
from typing import Optional

import httpx

from auth.crypto import (
    generate_ed25519_keypair,
    private_key_to_bytes,
    public_key_to_bytes,
    public_key_to_did_key,
    did_key_to_public_key,
)
from config import UNIVERSAL_RESOLVER_URL
from errors import ErrorCategory, log_and_format_error

import base58
import base64


class DIDService:
    """Resolves and creates DID documents."""

    def _store_keypair(self, keypair_id: str, priv_b64: str, pub_multibase: str, did: str):
        """Store a generated keypair locally (never return private keys in tool responses)."""
        import shutil
        from datetime import datetime, timezone
        from filelock import FileLock
        from config import PROJECT_DIR

        keypair_file = PROJECT_DIR / ".keypairs.json"
        lock = FileLock(str(keypair_file) + ".lock", timeout=5)

        with lock:
            data = {}
            if keypair_file.exists():
                try:
                    with open(keypair_file, "r") as f:
                        data = json.load(f)
                except (json.JSONDecodeError, ValueError):
                    data = {}
            data[keypair_id] = {
                "did": did,
                "algorithm": "Ed25519",
                "public_key_multibase": pub_multibase,
                "private_key_b64": priv_b64,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            # Atomic write: temp file then rename
            temp = keypair_file.with_suffix(".json.tmp")
            with open(temp, "w") as f:
                json.dump(data, f, indent=2)
            temp.replace(keypair_file)

    def resolve_did(self, did: str) -> dict:
        """Resolve a DID to its DID Document.

        Uses local resolution for did:key and did:web,
        falls back to Universal Resolver for others.
        """
        try:
            if did.startswith("did:key:"):
                return self._resolve_did_key(did)
            elif did.startswith("did:web:"):
                return self._resolve_did_web(did)
            else:
                return self._resolve_universal(did)
        except Exception as e:
            return {
                "error": log_and_format_error(
                    "resolve_did", e, ErrorCategory.DID, did=did
                )
            }

    def create_did_key(self) -> dict:
        """Generate a new ephemeral did:key with Ed25519 keypair."""
        try:
            private_key, public_key = generate_ed25519_keypair()
            did = public_key_to_did_key(public_key)

            pub_bytes = public_key_to_bytes(public_key)
            pub_multibase = "z" + base58.b58encode(pub_bytes).decode("ascii")
            priv_b64 = base64.urlsafe_b64encode(
                private_key_to_bytes(private_key)
            ).decode("ascii")

            did_document = self._build_did_key_document(did, pub_multibase)

            # Store keypair locally instead of returning private key in tool response
            keypair_id = f"keypair:{did.split(':')[-1][:16]}"
            self._store_keypair(keypair_id, priv_b64, pub_multibase, did)

            return {
                "did": did,
                "did_document": did_document,
                "keypair_id": keypair_id,
                "public_key_multibase": pub_multibase,
                "note": "Private key stored locally in .keypairs.json. Use keypair_id to reference it.",
            }
        except Exception as e:
            return {
                "error": log_and_format_error(
                    "create_did_key", e, ErrorCategory.DID
                )
            }

    def create_did_web(self, domain: str, path: str = "") -> dict:
        """Generate a did:web DID Document for self-hosting.

        The user must host the returned document at:
        https://{domain}/.well-known/did.json (no path)
        or https://{domain}/{path}/did.json (with path)
        """
        try:
            did_path = f":{path.replace('/', ':')}" if path else ""
            did = f"did:web:{domain}{did_path}"

            private_key, public_key = generate_ed25519_keypair()
            pub_bytes = public_key_to_bytes(public_key)
            pub_multibase = "z" + base58.b58encode(pub_bytes).decode("ascii")
            priv_b64 = base64.urlsafe_b64encode(
                private_key_to_bytes(private_key)
            ).decode("ascii")

            did_document = {
                "@context": [
                    "https://www.w3.org/ns/did/v1",
                    "https://w3id.org/security/suites/ed25519-2020/v1",
                ],
                "id": did,
                "controller": did,
                "verificationMethod": [
                    {
                        "id": f"{did}#key-1",
                        "type": "Ed25519VerificationKey2020",
                        "controller": did,
                        "publicKeyMultibase": pub_multibase,
                    }
                ],
                "authentication": [f"{did}#key-1"],
                "assertionMethod": [f"{did}#key-1"],
            }

            # Hosting path
            if path:
                hosting_url = f"https://{domain}/{path}/did.json"
            else:
                hosting_url = f"https://{domain}/.well-known/did.json"

            # Store keypair locally instead of returning private key in tool response
            keypair_id = f"keypair:{domain}:{did.split(':')[-1][:8]}"
            self._store_keypair(keypair_id, priv_b64, pub_multibase, did)

            return {
                "did": did,
                "did_document": did_document,
                "hosting_url": hosting_url,
                "keypair_id": keypair_id,
                "public_key_multibase": pub_multibase,
                "note": "Private key stored locally in .keypairs.json. Use keypair_id to reference it.",
                "instructions": (
                    f"Host the did_document JSON at {hosting_url} "
                    f"to make this DID resolvable."
                ),
            }
        except Exception as e:
            return {
                "error": log_and_format_error(
                    "create_did_web", e, ErrorCategory.DID, domain=domain
                )
            }

    # --- Internal resolution methods ---

    def _resolve_did_key(self, did: str) -> dict:
        """Locally resolve did:key to DID Document."""
        try:
            public_key = did_key_to_public_key(did)
            pub_bytes = public_key_to_bytes(public_key)
            pub_multibase = "z" + base58.b58encode(pub_bytes).decode("ascii")
        except ValueError as e:
            return {"error": str(e), "did": did}

        return self._build_did_key_document(did, pub_multibase)

    def _build_did_key_document(
        self, did: str, pub_multibase: Optional[str] = None
    ) -> dict:
        """Build a DID Document for a did:key."""
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
            "assertionMethod": [f"{did}#key-1"],
        }

    def _resolve_did_web(self, did: str) -> dict:
        """Resolve did:web by fetching the DID Document from the web."""
        try:
            # Validate format: did:web:<domain>(:<path>)*
            import re
            raw = did.replace("did:web:", "")
            if not re.match(r"^[a-z0-9._-]+(?::[a-z0-9._-]+)*$", raw):
                return {"error": f"Invalid did:web format: {did}"}

            parts = raw.split(":")
            domain = parts[0]

            # SSRF protection: block private/local/reserved IPs
            from auth.ssrf import validate_url_host
            ssrf_err = validate_url_host(domain)
            if ssrf_err:
                return {"error": ssrf_err}

            # Reject path traversal
            for p in parts[1:]:
                if ".." in p or p.startswith("."):
                    return {"error": f"Invalid path in did:web: {did}"}

            path = "/".join(parts[1:]) if len(parts) > 1 else ".well-known"
            url = f"https://{domain}/{path}/did.json"

            with httpx.Client(timeout=10) as client:
                resp = client.get(url)
                resp.raise_for_status()
                return resp.json()
        except httpx.TimeoutException:
            return {"error": f"Timeout resolving {did}", "retry_suggested": True}
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP {e.response.status_code} resolving {did}"}
        except Exception as e:
            return {
                "error": log_and_format_error(
                    "_resolve_did_web", e, ErrorCategory.NETWORK,
                    did=did, user_message=f"Could not resolve {did}",
                )
            }

    def _resolve_universal(self, did: str) -> dict:
        """Resolve any DID via the Universal Resolver."""
        try:
            import re
            if not re.match(r"^did:[a-z0-9]+:[a-zA-Z0-9._:%-]+$", did):
                return {"error": f"Invalid DID format: {did}"}
            url = f"{UNIVERSAL_RESOLVER_URL}{did}"
            with httpx.Client(timeout=15) as client:
                resp = client.get(url)
                resp.raise_for_status()
                result = resp.json()
                return result.get("didDocument", result)
        except Exception as e:
            return {
                "error": log_and_format_error(
                    "_resolve_universal", e, ErrorCategory.NETWORK,
                    did=did,
                    user_message=f"Universal Resolver failed for {did}",
                )
            }
