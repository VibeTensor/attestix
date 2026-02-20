"""E2E: AI Agent Developer persona.

Workflow: Create identity → verify → translate to A2A card → translate to DID doc.
"""


class TestAgentDeveloperWorkflow:
    def test_create_verify_translate(self, identity_service):
        # Step 1: Create an agent identity
        agent = identity_service.create_identity(
            display_name="SearchBot",
            source_protocol="mcp",
            capabilities=["web_search", "summarize"],
            description="An agent that searches and summarizes web content",
            issuer_name="DevCorp",
        )
        agent_id = agent["agent_id"]
        assert agent_id.startswith("attestix:")

        # Step 2: Verify the identity
        verification = identity_service.verify_identity(agent_id)
        assert verification["valid"] is True

        # Step 3: Translate to A2A Agent Card
        a2a_card = identity_service.translate_identity(agent_id, "a2a_agent_card")
        assert a2a_card["name"] == "SearchBot"
        assert len(a2a_card["skills"]) == 2
        assert a2a_card["provider"]["organization"] == "DevCorp"

        # Step 4: Translate to DID Document
        did_doc = identity_service.translate_identity(agent_id, "did_document")
        assert did_doc["id"].startswith("did:key:")
        assert len(did_doc["verificationMethod"]) == 1

        # Step 5: Get a summary
        summary = identity_service.translate_identity(agent_id, "summary")
        assert summary["display_name"] == "SearchBot"
        assert summary["signature_present"] is True

    def test_identity_lifecycle(self, identity_service):
        # Create
        agent = identity_service.create_identity("LifecycleBot", "api_key")
        agent_id = agent["agent_id"]

        # List (should appear)
        agents = identity_service.list_identities()
        assert any(a["agent_id"] == agent_id for a in agents)

        # Revoke
        identity_service.revoke_identity(agent_id, "decomissioned")

        # Verify (should fail)
        v = identity_service.verify_identity(agent_id)
        assert v["valid"] is False

        # List (should not appear by default)
        agents = identity_service.list_identities()
        assert not any(a["agent_id"] == agent_id for a in agents)

        # List with revoked
        agents = identity_service.list_identities(include_revoked=True)
        assert any(a["agent_id"] == agent_id for a in agents)

    def test_multiple_agents_different_protocols(self, identity_service):
        identity_service.create_identity("MCPBot", "mcp")
        identity_service.create_identity("A2ABot", "a2a")
        identity_service.create_identity("OAuthBot", "oauth")

        all_agents = identity_service.list_identities()
        assert len(all_agents) == 3

        mcp_only = identity_service.list_identities(source_protocol="mcp")
        assert len(mcp_only) == 1
        assert mcp_only[0]["display_name"] == "MCPBot"
