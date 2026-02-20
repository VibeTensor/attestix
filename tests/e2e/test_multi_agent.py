"""E2E: Multi-Agent Orchestrator persona.

Workflow: Create 2 agents → delegate capabilities → verify delegation →
record interactions → check reputation.
"""


class TestMultiAgentWorkflow:
    def test_delegation_chain(self, identity_service, delegation_service):
        # Create two agents
        agent_a = identity_service.create_identity("AgentA", "mcp", capabilities=["read", "write", "admin"])
        agent_b = identity_service.create_identity("AgentB", "mcp", capabilities=["read"])

        # A delegates read+write to B
        deleg = delegation_service.create_delegation(
            issuer_agent_id=agent_a["agent_id"],
            audience_agent_id=agent_b["agent_id"],
            capabilities=["read", "write"],
            expiry_hours=1,
        )
        assert "token" in deleg

        # Verify the delegation
        verified = delegation_service.verify_delegation(deleg["token"])
        assert verified["valid"] is True
        assert verified["capabilities"] == ["read", "write"]
        assert verified["delegator"] == agent_a["agent_id"]

        # List delegations for agent B
        b_delegations = delegation_service.list_delegations(
            agent_id=agent_b["agent_id"], role="audience",
        )
        assert len(b_delegations) == 1
        # Verify token is not leaked in the stored record
        assert "token" not in b_delegations[0]

    def test_reputation_tracking(self, identity_service, reputation_service):
        agent = identity_service.create_identity("ReputedBot", "mcp")
        partner = identity_service.create_identity("Partner", "a2a")
        aid = agent["agent_id"]
        pid = partner["agent_id"]

        # Record positive interactions
        reputation_service.record_interaction(aid, pid, "success", category="task")
        reputation_service.record_interaction(aid, pid, "success", category="task")

        # Record a failure
        reputation_service.record_interaction(aid, pid, "failure", category="task")

        # Check reputation
        rep = reputation_service.get_reputation(aid)
        assert rep["trust_score"] is not None
        assert 0.0 < rep["trust_score"] < 1.0  # not perfect due to failure
        assert rep["total_interactions"] == 3
        assert rep["category_breakdown"]["task"]["success"] == 2
        assert rep["category_breakdown"]["task"]["failure"] == 1

    def test_delegation_and_reputation_combined(
        self, identity_service, delegation_service, reputation_service,
    ):
        a = identity_service.create_identity("Orchestrator", "mcp")
        b = identity_service.create_identity("Worker", "mcp")
        a_id, b_id = a["agent_id"], b["agent_id"]

        # Delegate
        deleg = delegation_service.create_delegation(a_id, b_id, ["execute"], expiry_hours=2)

        # Worker completes tasks
        reputation_service.record_interaction(b_id, a_id, "success", "delegation")
        reputation_service.record_interaction(b_id, a_id, "success", "delegation")

        # Worker reputation should be high
        rep = reputation_service.get_reputation(b_id)
        assert rep["trust_score"] > 0.9

        # Query high-reputation agents
        top = reputation_service.query_reputation(min_score=0.8)
        ids = [r["agent_id"] for r in top]
        assert b_id in ids
