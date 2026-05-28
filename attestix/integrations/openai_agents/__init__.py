"""OpenAI Agents SDK integration for Attestix.

Provides :class:`AttestixAuditHook`, a small helper that logs Agent
invocations and tool calls to the Attestix audit chain. The OpenAI Agents
SDK already speaks MCP natively, so the canonical wiring is::

    from agents import Agent
    from agents.mcp import MCPServerStdio

    attestix_server = MCPServerStdio(params={"command": "attestix", "args": ["mcp-server"]})
    agent = Agent(..., mcp_servers=[attestix_server])

The :class:`AttestixAuditHook` complements that by emitting a structured
``log_action`` row for every guardrail decision so the audit chain reflects
the agent's decision boundary, not just its tool calls.

Install with the opt-in extra::

    pip install 'attestix[openai-agents]'
"""

from attestix.integrations.openai_agents.hook import AttestixAuditHook

__all__ = ["AttestixAuditHook"]
