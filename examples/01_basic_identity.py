"""Example 1: Basic Agent Identity

Creates an agent identity, verifies it, and translates it to different formats.

Usage:
    python examples/01_basic_identity.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.identity_service import IdentityService
from services.did_service import DIDService
from services.reputation_service import ReputationService


def main():
    identity_svc = IdentityService()
    did_svc = DIDService()
    reputation_svc = ReputationService()

    # 1. Create an agent identity
    print("=== Creating Agent Identity ===\n")
    agent = identity_svc.create_identity(
        display_name="DataAnalyzer",
        source_protocol="manual",
        capabilities=["data_analysis", "chart_generation", "report_writing"],
        description="Analyzes datasets and produces visual reports",
        issuer_name="Acme Analytics Inc.",
        expiry_days=365,
    )
    agent_id = agent["agent_id"]
    print(f"Agent ID:     {agent_id}")
    print(f"Display Name: {agent['display_name']}")
    print(f"DID:          {agent['issuer']['did']}")
    print(f"Capabilities: {agent['capabilities']}")
    print(f"Signed:       {bool(agent['signature'])}")

    # 2. Verify the identity
    print("\n=== Verifying Identity ===\n")
    verification = identity_svc.verify_identity(agent_id)
    print(f"Valid:           {verification['valid']}")
    for check, passed in verification["checks"].items():
        print(f"  {check}: {passed}")

    # 3. Translate to different formats
    print("\n=== Translate to A2A Agent Card ===\n")
    card = identity_svc.translate_identity(agent_id, target_format="a2a_agent_card")
    print(f"Agent Card name: {card.get('name')}")
    print(f"Skills:          {len(card.get('skills', []))} skills")
    print(f"Endpoints:       {len(card.get('endpoints', []))} endpoints")

    print("\n=== Translate to DID Document ===\n")
    did_doc = identity_svc.translate_identity(agent_id, target_format="did_document")
    print(f"DID:             {did_doc.get('id')}")
    print(f"Verification:    {len(did_doc.get('verificationMethod', []))} methods")

    # 4. Create a standalone DID
    print("\n=== Create Standalone did:key ===\n")
    did_key = did_svc.create_did_key()
    print(f"DID:             {did_key['did']}")
    print(f"Keypair ID:      {did_key['keypair_id']}")
    print(f"Public Key:      {did_key['public_key_multibase'][:20]}...")

    # 5. Record some interactions for reputation
    print("\n=== Building Reputation ===\n")
    for outcome in ["success", "success", "success", "partial", "success"]:
        reputation_svc.record_interaction(
            agent_id=agent_id,
            counterparty_id="attestix:system",
            outcome=outcome,
            category="data_quality",
        )

    reputation = reputation_svc.get_reputation(agent_id)
    print(f"Trust Score:     {reputation['trust_score']:.2f}")
    print(f"Interactions:    {reputation['total_interactions']}")
    print(f"Categories:      {list(reputation.get('category_breakdown', {}).keys())}")

    # 6. List all identities
    print("\n=== All Registered Agents ===\n")
    all_agents = identity_svc.list_identities()
    print(f"Total agents: {len(all_agents)}")
    for a in all_agents:
        print(f"  - {a['display_name']} ({a['agent_id'][:20]}...)")

    print("\nDone! All data saved to JSON files in the project directory.")


if __name__ == "__main__":
    main()
