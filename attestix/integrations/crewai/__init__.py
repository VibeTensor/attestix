"""CrewAI integration for Attestix.

Provides :class:`AttestixCrewAdapter`, a thin helper that logs CrewAI
Task/Agent lifecycle events to the Attestix audit chain. CrewAI has a
native MCP adapter (``MCPServerAdapter``) which is the recommended way to
expose Attestix's 47 MCP tools to a Crew. This adapter complements that by
emitting one ``log_action`` row per CrewAI task start/finish so the audit
chain reflects the Crew's task graph.

Install with the opt-in extra::

    pip install 'attestix[crewai]'
"""

from attestix.integrations.crewai.adapter import AttestixCrewAdapter

__all__ = ["AttestixCrewAdapter"]
