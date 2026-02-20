"""Tests for services/agent_card_service.py — A2A Agent Cards."""


class TestParseAgentCard:
    def test_parses_standard_card(self, agent_card_service):
        card = {
            "name": "TestAgent",
            "description": "A test agent",
            "url": "https://example.com",
            "version": "1.0",
            "skills": [
                {"id": "s1", "name": "search", "description": "Search things"},
            ],
            "authentication": {"schemes": ["bearer"]},
            "provider": {"organization": "TestCorp"},
            "capabilities": {"streaming": True, "pushNotifications": False},
        }
        result = agent_card_service.parse_agent_card(card)
        assert result["name"] == "TestAgent"
        assert result["capabilities"] == ["search"]
        assert result["skills_count"] == 1
        assert result["authentication_schemes"] == ["bearer"]
        assert result["streaming"] is True

    def test_handles_string_skills(self, agent_card_service):
        card = {"skills": ["read", "write"], "name": "Bot"}
        result = agent_card_service.parse_agent_card(card)
        assert result["capabilities"] == ["read", "write"]

    def test_handles_empty_card(self, agent_card_service):
        result = agent_card_service.parse_agent_card({})
        assert result["name"] == "Unknown Agent"
        assert result["skills_count"] == 0


class TestGenerateAgentCard:
    def test_generates_valid_card(self, agent_card_service):
        result = agent_card_service.generate_agent_card(
            name="MyAgent",
            url="https://myagent.example.com",
            description="My AI agent",
        )
        card = result["agent_card"]
        assert card["name"] == "MyAgent"
        assert card["url"] == "https://myagent.example.com"
        assert card["description"] == "My AI agent"
        assert result["hosting_path"] == "/.well-known/agent.json"

    def test_includes_skills(self, agent_card_service):
        skills = [{"id": "s1", "name": "search", "description": "Search"}]
        result = agent_card_service.generate_agent_card(
            name="Bot", url="https://bot.com", skills=skills,
        )
        assert len(result["agent_card"]["skills"]) == 1


class TestDiscoverAgent:
    def test_requires_https(self, agent_card_service):
        result = agent_card_service.discover_agent("http://example.com")
        assert "error" in result
        assert "HTTPS" in result["error"]

    def test_ssrf_blocks_private(self, agent_card_service):
        result = agent_card_service.discover_agent("https://localhost")
        assert "error" in result
