"""A2A Agent Card service for Attestix.

Handles fetching, parsing, and generating Google A2A Agent Cards
(the /.well-known/agent.json standard).
"""

from typing import Optional

from auth.ssrf import fetch_json_pinned
from errors import ErrorCategory, log_and_format_error


# Agent cards are small JSON documents describing an agent's capabilities.
# Real-world cards are < 10 KB; we cap at 1 MB to tolerate verbose skill lists
# while still blocking gzip-bomb / memory-exhaustion attacks.
AGENT_CARD_MAX_BYTES = 1 * 1024 * 1024


class AgentCardService:
    """Discover, parse, and generate A2A Agent Cards."""

    def discover_agent(self, base_url: str) -> dict:
        """Fetch /.well-known/agent.json from a URL.

        Uses a DNS-pinned fetcher so the hostname resolves exactly once
        (preventing DNS rebinding TOCTOU against metadata IPs) and caps the
        response body at :data:`AGENT_CARD_MAX_BYTES` so that a maliciously
        crafted gzip-encoded response cannot OOM the process.
        """
        try:
            url = base_url.rstrip("/")
            if not url.startswith("https://"):
                return {"error": "Only HTTPS URLs are supported for agent discovery"}

            agent_json_url = f"{url}/.well-known/agent.json"

            fetch_err, card = fetch_json_pinned(
                agent_json_url, max_bytes=AGENT_CARD_MAX_BYTES, timeout=10.0,
            )
            if fetch_err:
                return {"error": fetch_err, "source_url": agent_json_url}

            return {
                "source_url": agent_json_url,
                "agent_card": card,
                "parsed": self.parse_agent_card(card),
            }
        except Exception as e:
            return {
                "error": log_and_format_error(
                    "discover_agent", e, ErrorCategory.AGENT_CARD,
                    url=base_url,
                    user_message=f"Could not fetch agent card from {base_url}",
                )
            }

    def parse_agent_card(self, card: dict) -> dict:
        """Parse an A2A Agent Card JSON into normalized fields."""
        try:
            skills = card.get("skills", [])
            capabilities = []
            for skill in skills:
                if isinstance(skill, dict):
                    capabilities.append(skill.get("name", skill.get("id", "")))
                elif isinstance(skill, str):
                    capabilities.append(skill)

            auth_schemes = []
            auth = card.get("authentication", {})
            if isinstance(auth, dict):
                auth_schemes = auth.get("schemes", [])
            elif isinstance(auth, list):
                auth_schemes = auth

            provider = card.get("provider", {})
            if isinstance(provider, str):
                provider = {"organization": provider}

            return {
                "name": card.get("name", "Unknown Agent"),
                "description": card.get("description", ""),
                "url": card.get("url", ""),
                "version": card.get("version", ""),
                "capabilities": capabilities,
                "skills_count": len(skills),
                "skills_raw": skills,
                "authentication_schemes": auth_schemes,
                "provider": provider,
                "streaming": card.get("capabilities", {}).get("streaming", False),
                "push_notifications": card.get("capabilities", {}).get(
                    "pushNotifications", False
                ),
            }
        except Exception as e:
            return {
                "error": log_and_format_error(
                    "parse_agent_card", e, ErrorCategory.AGENT_CARD,
                    user_message="Failed to parse agent card JSON",
                )
            }

    def generate_agent_card(
        self,
        name: str,
        url: str,
        description: str = "",
        skills: Optional[list] = None,
        version: str = "1.0.0",
    ) -> dict:
        """Generate a valid A2A Agent Card JSON (agent.json).

        Args:
            name: Agent display name.
            url: Base URL where the agent is hosted.
            description: What the agent does.
            skills: List of skill dicts with id, name, description.
            version: Agent version string.
        """
        import hashlib
        if skills is None:
            skills = []

        card = {
            "id": f"attestix-{hashlib.sha256(url.encode()).hexdigest()[:16]}",
            "name": name,
            "description": description,
            "url": url,
            "version": version,
            "capabilities": {
                "streaming": False,
                "pushNotifications": False,
                "stateTransitionHistory": False,
            },
            "skills": skills,
            "endpoints": [
                {
                    "url": f"{url.rstrip('/')}/tasks",
                    "protocol": "https",
                    "method": "POST",
                }
            ],
            "provider": {
                "organization": "Attestix",
            },
            "authentication": {
                "schemes": ["bearer"],
            },
            "defaultInputModes": ["text/plain"],
            "defaultOutputModes": ["text/plain"],
        }

        return {
            "agent_card": card,
            "hosting_path": "/.well-known/agent.json",
            "instructions": (
                f"Host this JSON at {url}/.well-known/agent.json "
                f"to make the agent discoverable via A2A protocol."
            ),
        }
