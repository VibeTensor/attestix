"""Example 4: Verifiable Credentials

Demonstrates W3C Verifiable Credential issuance, verification,
revocation, and presentation bundling.

Usage:
    python examples/04_verifiable_credentials.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.identity_service import IdentityService
from services.credential_service import CredentialService


def main():
    identity_svc = IdentityService()
    credential_svc = CredentialService()

    # Create an agent
    print("=== Creating Agent ===\n")
    agent = identity_svc.create_identity(
        display_name="CertifiedBot",
        capabilities=["data_processing", "customer_service"],
        description="A certified customer service agent",
        issuer_name="BotCert Authority",
    )
    agent_id = agent["agent_id"]
    print(f"Agent ID: {agent_id}")

    # Issue a custom credential
    print("\n=== Issuing Verifiable Credential ===\n")
    vc1 = credential_svc.issue_credential(
        subject_agent_id=agent_id,
        credential_type="CustomerServiceCertification",
        issuer_name="BotCert Authority",
        claims_json=json.dumps({
            "certification_level": "gold",
            "languages": ["en", "es", "fr"],
            "max_concurrent_sessions": 100,
            "response_time_sla_ms": 500,
            "audit_date": "2026-02-19",
        }),
        expiry_days=180,
    )
    cred_id_1 = vc1["id"]
    print(f"Credential ID: {cred_id_1}")
    print(f"Type: {vc1['type']}")
    print(f"Issuer: {vc1['issuer']['name']}")
    print(f"Proof type: {vc1['proof']['type']}")

    # Issue a second credential
    print("\n=== Issuing Second Credential ===\n")
    vc2 = credential_svc.issue_credential(
        subject_agent_id=agent_id,
        credential_type="DataProcessingCompliance",
        issuer_name="DataGuard EU",
        claims_json=json.dumps({
            "gdpr_compliant": True,
            "data_residency": "EU",
            "encryption_standard": "AES-256",
            "dpo_contact": "dpo@example.com",
        }),
        expiry_days=365,
    )
    cred_id_2 = vc2["id"]
    print(f"Credential ID: {cred_id_2}")
    print(f"Type: {vc2['type']}")

    # Verify credentials
    print("\n=== Verifying Credentials ===\n")
    for cid, label in [(cred_id_1, "CustomerService"), (cred_id_2, "DataProcessing")]:
        v = credential_svc.verify_credential(cid)
        print(f"{label}: valid={v['valid']}")
        for check, passed in v["checks"].items():
            print(f"  {check}: {passed}")

    # Revoke the first credential
    print("\n=== Revoking First Credential ===\n")
    revoke_result = credential_svc.revoke_credential(
        credential_id=cred_id_1,
        reason="Certification expired early due to policy change",
    )
    print(f"Revoked: {revoke_result.get('credential_id', cred_id_1)}")
    print(f"Reason: {revoke_result.get('reason', 'N/A')}")

    # Verify again -- first should show revoked
    print("\n=== Verify After Revocation ===\n")
    v1_after = credential_svc.verify_credential(cred_id_1)
    print(f"CustomerService: valid={v1_after['valid']}")
    print(f"  not_revoked: {v1_after['checks'].get('not_revoked')}")

    v2_after = credential_svc.verify_credential(cred_id_2)
    print(f"DataProcessing: valid={v2_after['valid']}")
    print(f"  not_revoked: {v2_after['checks'].get('not_revoked')}")

    # Create a Verifiable Presentation with the valid credential
    print("\n=== Creating Verifiable Presentation ===\n")
    vp = credential_svc.create_verifiable_presentation(
        agent_id=agent_id,
        credential_ids=cred_id_2,  # Only include the valid one
        audience_did="did:web:regulator.europa.eu",
        challenge="nonce-abc-123-xyz",
    )
    print(f"VP Type: {vp.get('type')}")
    print(f"Holder: {vp.get('holder', {}).get('id', 'N/A')[:30]}...")
    print(f"Credentials included: {len(vp.get('verifiableCredential', []))}")
    print(f"Proof type: {vp.get('proof', {}).get('type')}")
    print(f"Challenge: {vp.get('proof', {}).get('challenge')}")
    print(f"Domain: {vp.get('proof', {}).get('domain')}")

    # List all credentials for the agent
    print("\n=== List All Credentials ===\n")
    all_creds = credential_svc.list_credentials(agent_id=agent_id)
    print(f"Total: {all_creds['total']}")
    for c in all_creds["credentials"]:
        status = "REVOKED" if c.get("credentialStatus", {}).get("revoked") else "ACTIVE"
        ctype = c["type"][-1] if isinstance(c["type"], list) else c["type"]
        print(f"  [{status}] {ctype} - {c['id'][:30]}...")

    # List only valid credentials
    print("\n=== Valid Credentials Only ===\n")
    valid_creds = credential_svc.list_credentials(agent_id=agent_id, valid_only=True)
    print(f"Valid: {valid_creds['total']}")

    print("\nDone!")


if __name__ == "__main__":
    main()
