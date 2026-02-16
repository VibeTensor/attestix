"""AURA Protocol - Agent Unified Registry & Authentication Protocol

MCP server for cross-protocol agent identity bridging,
delegation chains, reputation scoring, and EU AI Act compliance.

36 tools across 8 modules:
  - Identity (7): create, resolve, verify, translate, list, get, revoke
  - Agent Cards (3): parse, generate, discover
  - DID (3): resolve_did, create_did_key, create_did_web
  - Delegation (3): create, verify, list
  - Reputation (3): record_interaction, get_reputation, query_reputation
  - Compliance (6): create_profile, get_profile, get_status, record_assessment, generate_declaration, list_profiles
  - Credentials (6): issue, verify, revoke, get, list, create_presentation
  - Provenance (5): record_training_data, record_model_lineage, log_action, get_provenance, get_audit_trail
"""

import asyncio
import builtins
import sys

# Redirect all print() to stderr to protect MCP JSON-RPC on stdout
_original_print = builtins.print
def _stderr_print(*args, **kwargs):
    kwargs.setdefault("file", sys.stderr)
    _original_print(*args, **kwargs)
builtins.print = _stderr_print

import nest_asyncio
from mcp.server.fastmcp import FastMCP

from errors import setup_logging

# Initialize logging
setup_logging()

# Create MCP server
mcp = FastMCP("aura-protocol")

# Register tool modules
from tools import (
    identity_tools, agent_card_tools, did_tools, delegation_tools, reputation_tools,
    compliance_tools, credential_tools, provenance_tools,
)

identity_tools.register(mcp)
agent_card_tools.register(mcp)
did_tools.register(mcp)
delegation_tools.register(mcp)
reputation_tools.register(mcp)
compliance_tools.register(mcp)
credential_tools.register(mcp)
provenance_tools.register(mcp)

print(f"AURA Protocol MCP server loaded: 36 tools registered", file=sys.stderr)


def main():
    nest_asyncio.apply()
    asyncio.run(mcp.run_stdio_async())


if __name__ == "__main__":
    main()
