"""Credential service for Attestix.

Issues, verifies, and manages W3C Verifiable Credentials (VC Data Model 1.1)
with Ed25519Signature2020 proofs.
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from auth.crypto import (
    did_key_fragment,
    load_or_create_signing_key,
    sign_json_payload,
    verify_json_signature,
    did_key_to_public_key,
)
from config import load_credentials, save_credentials
from errors import ErrorCategory, log_and_format_error


# W3C VC contexts
VC_CONTEXT = [
    "https://www.w3.org/2018/credentials/v1",
    "https://w3id.org/security/suites/ed25519-2020/v1",
]

# Standard credential types
CREDENTIAL_TYPES = {
    "EUAIActComplianceCredential",
    "ConformityAssessmentCredential",
    "TransparencyObligationCredential",
    "TrainingDataProvenanceCredential",
    "AgentIdentityCredential",
}


class CredentialService:
    """Manages W3C Verifiable Credentials with Ed25519 proofs."""

    # Fields excluded from signing (mutable after issuance)
    MUTABLE_FIELDS = {"proof", "credentialStatus"}

    def __init__(self):
        self._private_key, self._server_did = load_or_create_signing_key()

    def issue_credential(
        self,
        subject_id: str,
        credential_type: str,
        issuer_name: str,
        claims: Dict,
        expiry_days: int = 365,
    ) -> dict:
        """Issue a W3C Verifiable Credential with Ed25519Signature2020 proof."""
        try:
            cred_id = f"urn:uuid:{uuid.uuid4()}"
            now = datetime.now(timezone.utc)
            expires = now + timedelta(days=expiry_days)

            vc_type = credential_type
            credential = {
                "@context": VC_CONTEXT,
                "id": cred_id,
                "type": ["VerifiableCredential", vc_type],
                "issuer": {
                    "id": self._server_did,
                    "name": issuer_name,
                },
                "issuanceDate": now.isoformat(),
                "expirationDate": expires.isoformat(),
                "credentialSubject": {
                    "id": subject_id,
                    **claims,
                },
                "credentialStatus": {
                    "id": f"{cred_id}#status",
                    "type": "RevocationList2021Status",
                    "revoked": False,
                    "revocation_reason": None,
                    "revoked_at": None,
                },
            }

            # Create Ed25519Signature2020 proof (exclude mutable fields)
            proof_payload = {k: v for k, v in credential.items() if k not in self.MUTABLE_FIELDS}
            signature = sign_json_payload(self._private_key, proof_payload)

            credential["proof"] = {
                "type": "Ed25519Signature2020",
                "created": now.isoformat(),
                "verificationMethod": f"{self._server_did}{did_key_fragment(self._server_did)}",
                "proofPurpose": "assertionMethod",
                "proofValue": signature,
            }

            data = load_credentials()
            data["credentials"].append(credential)
            save_credentials(data)

            return credential
        except Exception as e:
            msg = log_and_format_error(
                "issue_credential", e, ErrorCategory.CREDENTIAL,
                subject_id=subject_id, credential_type=credential_type,
            )
            return {"error": msg}

    def verify_credential(self, credential_id: str) -> dict:
        """Verify a credential: check signature, expiry, and revocation status."""
        try:
            cred = self._find_credential(credential_id)
            if not cred:
                return {"valid": False, "credential_id": credential_id, "checks": {"exists": False}}

            checks = {"exists": True}

            # Check revocation
            status = cred.get("credentialStatus", {})
            checks["not_revoked"] = not status.get("revoked", False)

            # Check expiry
            exp_str = cred.get("expirationDate")
            if exp_str:
                exp_dt = datetime.fromisoformat(exp_str)
                checks["not_expired"] = datetime.now(timezone.utc) < exp_dt
            else:
                checks["not_expired"] = True

            # Check signature
            proof = cred.get("proof", {})
            proof_value = proof.get("proofValue")
            if proof_value:
                proof_payload = {k: v for k, v in cred.items() if k not in self.MUTABLE_FIELDS}
                try:
                    issuer_did = cred.get("issuer", {}).get("id", self._server_did)
                    pub_key = did_key_to_public_key(issuer_did)
                    checks["signature_valid"] = verify_json_signature(
                        pub_key, proof_payload, proof_value
                    )
                except Exception:
                    checks["signature_valid"] = False
            else:
                checks["signature_valid"] = False

            valid = all(v for v in checks.values() if isinstance(v, bool))
            return {
                "valid": valid,
                "credential_id": credential_id,
                "type": cred.get("type", []),
                "subject": cred.get("credentialSubject", {}).get("id"),
                "checks": checks,
            }
        except Exception as e:
            msg = log_and_format_error(
                "verify_credential", e, ErrorCategory.CREDENTIAL,
                credential_id=credential_id,
            )
            return {"error": msg}

    def revoke_credential(self, credential_id: str, reason: str = "") -> dict:
        """Revoke a credential."""
        try:
            data = load_credentials()
            for cred in data["credentials"]:
                if cred.get("id") == credential_id:
                    cred["credentialStatus"] = {
                        "id": f"{credential_id}#status",
                        "type": "RevocationList2021Status",
                        "revoked": True,
                        "revocation_reason": reason,
                        "revoked_at": datetime.now(timezone.utc).isoformat(),
                    }
                    save_credentials(data)
                    return {
                        "revoked": True,
                        "credential_id": credential_id,
                        "reason": reason,
                    }
            return {"error": f"Credential {credential_id} not found"}
        except Exception as e:
            msg = log_and_format_error(
                "revoke_credential", e, ErrorCategory.CREDENTIAL,
                credential_id=credential_id,
            )
            return {"error": msg}

    def get_credential(self, credential_id: str) -> Optional[dict]:
        """Get a credential by ID."""
        return self._find_credential(credential_id)

    def list_credentials(
        self,
        agent_id: Optional[str] = None,
        credential_type: Optional[str] = None,
        valid_only: bool = False,
        limit: int = 50,
    ) -> List[dict]:
        """List credentials with optional filters."""
        try:
            data = load_credentials()
            results = []

            for cred in data["credentials"]:
                if agent_id:
                    subject = cred.get("credentialSubject", {}).get("id")
                    if subject != agent_id:
                        continue
                if credential_type:
                    if credential_type not in cred.get("type", []):
                        continue
                if valid_only:
                    status = cred.get("credentialStatus", {})
                    if status.get("revoked"):
                        continue
                    exp_str = cred.get("expirationDate")
                    if exp_str:
                        exp_dt = datetime.fromisoformat(exp_str)
                        if datetime.now(timezone.utc) >= exp_dt:
                            continue

                results.append(cred)
                if len(results) >= limit:
                    break

            return results
        except Exception as e:
            msg = log_and_format_error(
                "list_credentials", e, ErrorCategory.CREDENTIAL,
            )
            return [{"error": msg}]

    def create_verifiable_presentation(
        self,
        agent_id: str,
        credential_ids: List[str],
        audience_did: str = "",
        challenge: str = "",
    ) -> dict:
        """Bundle multiple VCs into a Verifiable Presentation for a verifier."""
        try:
            credentials = []
            for cid in credential_ids:
                cred = self._find_credential(cid)
                if not cred:
                    return {"error": f"Credential {cid} not found"}
                # Verify the credential belongs to this agent
                subject = cred.get("credentialSubject", {}).get("id")
                if subject != agent_id:
                    return {"error": f"Credential {cid} does not belong to agent {agent_id}"}
                credentials.append(cred)

            vp_id = f"urn:uuid:{uuid.uuid4()}"
            now = datetime.now(timezone.utc)

            vp = {
                "@context": VC_CONTEXT,
                "id": vp_id,
                "type": ["VerifiablePresentation"],
                "holder": agent_id,
                "verifiableCredential": credentials,
            }

            if audience_did:
                vp["domain"] = audience_did
            if challenge:
                vp["challenge"] = challenge

            # Sign the presentation (includes challenge/domain for replay protection)
            proof_payload = {k: v for k, v in vp.items() if k != "proof"}
            signature = sign_json_payload(self._private_key, proof_payload)

            vp["proof"] = {
                "type": "Ed25519Signature2020",
                "created": now.isoformat(),
                "verificationMethod": f"{self._server_did}{did_key_fragment(self._server_did)}",
                "proofPurpose": "authentication",
                "proofValue": signature,
            }
            if challenge:
                vp["proof"]["challenge"] = challenge
            if audience_did:
                vp["proof"]["domain"] = audience_did

            return vp
        except Exception as e:
            msg = log_and_format_error(
                "create_verifiable_presentation", e, ErrorCategory.CREDENTIAL,
                agent_id=agent_id,
            )
            return {"error": msg}

    def verify_presentation(self, presentation: dict) -> dict:
        """Verify a Verifiable Presentation: check holder signature, domain, challenge,
        and verify each contained credential."""
        try:
            checks = {}

            # Check VP structure
            vp_types = presentation.get("type", [])
            if "VerifiablePresentation" not in vp_types:
                return {"valid": False, "reason": "Not a VerifiablePresentation"}

            checks["structure_valid"] = True
            holder = presentation.get("holder", "")

            # Verify VP proof/signature
            proof = presentation.get("proof", {})
            proof_value = proof.get("proofValue")
            if proof_value:
                proof_payload = {k: v for k, v in presentation.items() if k != "proof"}
                try:
                    vm = proof.get("verificationMethod", "")
                    # Extract DID from verification method (remove fragment)
                    issuer_did = vm.split("#")[0] if "#" in vm else self._server_did
                    pub_key = did_key_to_public_key(issuer_did)
                    checks["vp_signature_valid"] = verify_json_signature(
                        pub_key, proof_payload, proof_value
                    )
                except Exception:
                    checks["vp_signature_valid"] = False
            else:
                checks["vp_signature_valid"] = False

            # Check challenge (replay protection)
            if proof.get("challenge"):
                checks["challenge_present"] = True
            if proof.get("domain"):
                checks["domain_present"] = True

            # Verify each contained credential
            credentials = presentation.get("verifiableCredential", [])
            checks["credential_count"] = len(credentials)
            checks["credentials_valid"] = True

            for i, cred in enumerate(credentials):
                cred_proof = cred.get("proof", {})
                cred_proof_value = cred_proof.get("proofValue")
                if cred_proof_value:
                    cred_payload = {
                        k: v for k, v in cred.items() if k not in self.MUTABLE_FIELDS
                    }
                    try:
                        vm = cred_proof.get("verificationMethod", "")
                        issuer_did = vm.split("#")[0] if "#" in vm else self._server_did
                        pub_key = did_key_to_public_key(issuer_did)
                        cred_valid = verify_json_signature(
                            pub_key, cred_payload, cred_proof_value
                        )
                        if not cred_valid:
                            checks["credentials_valid"] = False
                    except Exception:
                        checks["credentials_valid"] = False
                else:
                    checks["credentials_valid"] = False

                # Check credential subject matches holder
                subject = cred.get("credentialSubject", {}).get("id")
                if subject != holder:
                    checks["holder_matches_subjects"] = False

            if "holder_matches_subjects" not in checks:
                checks["holder_matches_subjects"] = True

            valid = all(
                v for v in checks.values()
                if isinstance(v, bool)
            )
            return {
                "valid": valid,
                "holder": holder,
                "credential_count": len(credentials),
                "checks": checks,
            }
        except Exception as e:
            msg = log_and_format_error(
                "verify_presentation", e, ErrorCategory.CREDENTIAL,
            )
            return {"error": msg}

    def verify_credential_external(self, credential: dict) -> dict:
        """Verify a credential provided as raw JSON (for external verifiers).

        Does not require the credential to be in local storage.
        """
        try:
            checks = {}

            # Check structure
            vc_types = credential.get("type", [])
            if "VerifiableCredential" not in vc_types:
                return {"valid": False, "reason": "Not a VerifiableCredential"}
            checks["structure_valid"] = True

            # Check revocation (if we have it locally)
            cred_id = credential.get("id")
            local_cred = self._find_credential(cred_id) if cred_id else None
            if local_cred:
                status = local_cred.get("credentialStatus", {})
                checks["not_revoked"] = not status.get("revoked", False)
            else:
                checks["not_revoked"] = True  # Cannot check, assume valid

            # Check expiry
            exp_str = credential.get("expirationDate")
            if exp_str:
                exp_dt = datetime.fromisoformat(exp_str)
                checks["not_expired"] = datetime.now(timezone.utc) < exp_dt
            else:
                checks["not_expired"] = True

            # Verify signature
            proof = credential.get("proof", {})
            proof_value = proof.get("proofValue")
            if proof_value:
                proof_payload = {
                    k: v for k, v in credential.items() if k not in self.MUTABLE_FIELDS
                }
                try:
                    vm = proof.get("verificationMethod", "")
                    issuer_did = vm.split("#")[0] if "#" in vm else ""
                    pub_key = did_key_to_public_key(issuer_did)
                    checks["signature_valid"] = verify_json_signature(
                        pub_key, proof_payload, proof_value
                    )
                except Exception:
                    checks["signature_valid"] = False
            else:
                checks["signature_valid"] = False

            valid = all(v for v in checks.values() if isinstance(v, bool))
            return {
                "valid": valid,
                "credential_id": cred_id,
                "type": vc_types,
                "subject": credential.get("credentialSubject", {}).get("id"),
                "checks": checks,
            }
        except Exception as e:
            msg = log_and_format_error(
                "verify_credential_external", e, ErrorCategory.CREDENTIAL,
            )
            return {"error": msg}

    def _find_credential(self, credential_id: str) -> Optional[dict]:
        """Look up a credential by ID."""
        data = load_credentials()
        for cred in data["credentials"]:
            if cred.get("id") == credential_id:
                return cred
        return None
