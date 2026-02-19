"""Example 3: Delegation Chains

Demonstrates UCAN-style capability delegation between agents.

An orchestrator agent delegates capabilities to specialist agents,
who can then prove their authority chain.

Usage:
    python examples/03_delegation_chain.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.identity_service import IdentityService
from services.delegation_service import DelegationService


def main():
    identity_svc = IdentityService()
    delegation_svc = DelegationService()

    # Create three agents with different roles
    print("=== Creating Agent Hierarchy ===\n")

    admin = identity_svc.create_identity(
        display_name="SystemAdmin",
        capabilities=["full_access", "user_management", "data_access", "delegation"],
        description="System administrator with full access",
        issuer_name="Acme Corp",
    )
    print(f"Admin:   {admin['agent_id'][:24]}... (SystemAdmin)")

    analyst = identity_svc.create_identity(
        display_name="DataAnalyst",
        capabilities=["data_analysis"],
        description="Analyzes datasets on behalf of admin",
        issuer_name="Acme Corp",
    )
    print(f"Analyst: {analyst['agent_id'][:24]}... (DataAnalyst)")

    reporter = identity_svc.create_identity(
        display_name="ReportGenerator",
        capabilities=["report_generation"],
        description="Generates reports from analysis results",
        issuer_name="Acme Corp",
    )
    print(f"Reporter: {reporter['agent_id'][:24]}... (ReportGenerator)")

    # Admin delegates data_access to analyst
    print("\n=== Delegation: Admin -> Analyst ===\n")
    delegation1 = delegation_svc.create_delegation(
        issuer_agent_id=admin["agent_id"],
        audience_agent_id=analyst["agent_id"],
        capabilities="data_access,data_analysis",
        expiry_hours=8,
    )
    print(f"Token: {delegation1['token'][:40]}...")
    print(f"Capabilities delegated: {delegation1['capabilities']}")
    print(f"Expires in: {delegation1['expiry_hours']} hours")

    # Verify the delegation
    print("\n=== Verifying Admin -> Analyst Delegation ===\n")
    verify1 = delegation_svc.verify_delegation(delegation1["token"])
    print(f"Valid:        {verify1['valid']}")
    print(f"Issuer:       {verify1['payload']['iss'][:24]}...")
    print(f"Audience:     {verify1['payload']['aud'][:24]}...")
    print(f"Capabilities: {verify1['payload']['att']}")

    # Analyst delegates a subset to reporter (chained delegation)
    print("\n=== Chained Delegation: Analyst -> Reporter ===\n")
    delegation2 = delegation_svc.create_delegation(
        issuer_agent_id=analyst["agent_id"],
        audience_agent_id=reporter["agent_id"],
        capabilities="data_access",  # Can only delegate what was received
        expiry_hours=4,
        parent_token=delegation1["token"],  # Chain to parent
    )
    print(f"Token: {delegation2['token'][:40]}...")
    print(f"Capabilities delegated: {delegation2['capabilities']}")
    print(f"Has parent proof: {bool(delegation2.get('parent_token'))}")

    # Verify chained delegation
    print("\n=== Verifying Chained Delegation ===\n")
    verify2 = delegation_svc.verify_delegation(delegation2["token"])
    print(f"Valid:        {verify2['valid']}")
    print(f"Issuer:       {verify2['payload']['iss'][:24]}... (Analyst)")
    print(f"Audience:     {verify2['payload']['aud'][:24]}... (Reporter)")
    print(f"Capabilities: {verify2['payload']['att']}")
    if verify2["payload"].get("prf"):
        print(f"Proof chain:  {verify2['payload']['prf'][:40]}...")

    # List all delegations
    print("\n=== All Delegations ===\n")
    all_delegations = delegation_svc.list_delegations()
    print(f"Total delegations: {all_delegations['total']}")
    for d in all_delegations["delegations"]:
        print(f"  {d['delegation_id'][:16]}... | "
              f"{d['issuer_agent_id'][:16]}... -> {d['audience_agent_id'][:16]}... | "
              f"Caps: {d['capabilities']}")

    # List delegations for a specific agent
    print(f"\n=== Analyst's Delegations (as issuer) ===\n")
    analyst_issued = delegation_svc.list_delegations(
        agent_id=analyst["agent_id"],
        role="issuer",
    )
    print(f"Issued by analyst: {analyst_issued['total']}")

    print(f"\n=== Analyst's Delegations (as audience) ===\n")
    analyst_received = delegation_svc.list_delegations(
        agent_id=analyst["agent_id"],
        role="audience",
    )
    print(f"Received by analyst: {analyst_received['total']}")

    print("\nDone! Delegation chain: Admin -> Analyst -> Reporter")


if __name__ == "__main__":
    main()
