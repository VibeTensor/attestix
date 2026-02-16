"""DID resolution service for AURA Protocol.

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

import base64


class DIDService:
    """Resolves and creates DID documents."""

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

            priv_b64 = base64.urlsafe_b64encode(
                private_key_to_bytes(private_key)
            ).decode("ascii")
            pub_b64 = base64.urlsafe_b64encode(
                public_key_to_bytes(public_key)
            ).decode("ascii")

            did_document = self._build_did_key_document(did)

            return {
                "did": did,
                "did_document": did_document,
                "keypair": {
                    "algorithm": "Ed25519",
                    "public_key_b64": pub_b64,
                    "private_key_b64": priv_b64,
                    "note": "Store private key securely. Never share it.",
                },
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
            pub_b64 = base64.urlsafe_b64encode(
                public_key_to_bytes(public_key)
            ).decode("ascii")
            priv_b64 = base64.urlsafe_b64encode(
                private_key_to_bytes(private_key)
            ).decode("ascii")

            did_document = {
                "@context": [
                    "https://www.w3.org/ns/did/v1",
                    "https://w3id.org/security/suites/ed2519-2020/v1",
                ],
                "id": did,
                "controller": did,
                "verificationMethod": [
                    {
                        "id": f"{did}#key-1",
                        "type": "Ed25519VerificationKey2020",
                        "controller": did,
                        "publicKeyBase64": pub_b64,
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

            return {
                "did": did,
                "did_document": did_document,
                "hosting_url": hosting_url,
                "keypair": {
                    "algorithm": "Ed25519",
                    "public_key_b64": pub_b64,
                    "private_key_b64": priv_b64,
                    "note": "Store private key securely.",
                },
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
            pub_b64 = base64.urlsafe_b64encode(
                public_key_to_bytes(public_key)
            ).decode("ascii")
        except ValueError as e:
            return {"error": str(e), "did": did}

        return self._build_did_key_document(did, pub_b64)

    def _build_did_key_document(
        self, did: str, pub_b64: Optional[str] = None
    ) -> dict:
        """Build a DID Document for a did:key."""
        doc = {
            "@context": [
                "https://www.w3.org/ns/did/v1",
                "https://w3id.org/security/suites/ed2519-2020/v1",
            ],
            "id": did,
            "controller": did,
            "verificationMethod": [
                {
                    "id": f"{did}#key-1",
                    "type": "Ed25519VerificationKey2020",
                    "controller": did,
                }
            ],
            "authentication": [f"{did}#key-1"],
            "assertionMethod": [f"{did}#key-1"],
        }
        if pub_b64:
            doc["verificationMethod"][0]["publicKeyBase64"] = pub_b64
        return doc

    def _resolve_did_web(self, did: str) -> dict:
        """Resolve did:web by fetching the DID Document from the web."""
        try:
            # did:web:example.com:path -> https://example.com/path/did.json
            parts = did.replace("did:web:", "").split(":")
            domain = parts[0]
            path = "/".join(parts[1:]) if len(parts) > 1 else ".well-known"
            url = f"https://{domain}/{path}/did.json"

            with httpx.Client(timeout=10) as client:
                resp = client.get(url)
                resp.raise_for_status()
                return resp.json()
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
