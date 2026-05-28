"""Attestix tools - re-exports from flat module for namespace compatibility.

MCP tool registration modules (47 tools across 9 modules):
    - identity_tools: 8 tools for UAIT management
    - agent_card_tools: 3 tools for A2A agent cards
    - did_tools: 3 tools for DID operations
    - delegation_tools: 4 tools for UCAN delegation
    - reputation_tools: 3 tools for trust scoring
    - compliance_tools: 7 tools for EU AI Act compliance
    - credential_tools: 8 tools for W3C VCs
    - provenance_tools: 5 tools for audit trails
    - blockchain_tools: 6 tools for EAS anchoring
"""

# Re-export submodules
from attestix.tools import identity_tools
from attestix.tools import agent_card_tools
from attestix.tools import did_tools
from attestix.tools import delegation_tools
from attestix.tools import reputation_tools
from attestix.tools import compliance_tools
from attestix.tools import credential_tools
from attestix.tools import provenance_tools
from attestix.tools import blockchain_tools

__all__ = [
    "identity_tools",
    "agent_card_tools",
    "did_tools",
    "delegation_tools",
    "reputation_tools",
    "compliance_tools",
    "credential_tools",
    "provenance_tools",
    "blockchain_tools",
]
