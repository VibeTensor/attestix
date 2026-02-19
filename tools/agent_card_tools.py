"""A2A Agent Card MCP tools for Attestix (3 tools)."""

import json


def register(mcp):
    """Register agent card tools with the MCP server."""

    @mcp.tool()
    async def parse_agent_card(agent_card_json: str) -> str:
        """Parse an A2A Agent Card JSON string into normalized fields.

        Args:
            agent_card_json: Raw JSON string of an A2A Agent Card.
        """
        from services.cache import get_service
        from services.agent_card_service import AgentCardService

        svc = get_service(AgentCardService)
        try:
            card = json.loads(agent_card_json)
        except json.JSONDecodeError as e:
            return json.dumps({"error": f"Invalid JSON: {e}"})

        result = svc.parse_agent_card(card)
        return json.dumps(result, indent=2, default=str)

    @mcp.tool()
    async def generate_agent_card(
        name: str,
        url: str,
        description: str = "",
        skills_json: str = "[]",
        version: str = "1.0.0",
    ) -> str:
        """Generate a valid A2A Agent Card (agent.json) for hosting.

        Args:
            name: Agent display name.
            url: Base URL where the agent will be hosted.
            description: What the agent does.
            skills_json: JSON array of skill objects with id, name, description.
            version: Agent version string.
        """
        from services.cache import get_service
        from services.agent_card_service import AgentCardService

        svc = get_service(AgentCardService)
        try:
            skills = json.loads(skills_json) if skills_json else []
        except json.JSONDecodeError:
            skills = []

        result = svc.generate_agent_card(
            name=name, url=url, description=description,
            skills=skills, version=version,
        )
        return json.dumps(result, indent=2, default=str)

    @mcp.tool()
    async def discover_agent(base_url: str) -> str:
        """Fetch and parse /.well-known/agent.json from a URL.

        Args:
            base_url: The base URL of the agent to discover (e.g., https://agent.example.com).
        """
        from services.cache import get_service
        from services.agent_card_service import AgentCardService

        svc = get_service(AgentCardService)
        result = svc.discover_agent(base_url)
        return json.dumps(result, indent=2, default=str)
