"""Attestix - Attestation Infrastructure for AI Agents

MCP server for cross-protocol agent identity bridging,
delegation chains, reputation scoring, EU AI Act compliance,
and blockchain anchoring.

47 tools across 9 modules:
  - Identity (8): create, resolve, verify, translate, list, get, revoke, purge (GDPR)
  - Agent Cards (3): parse, generate, discover
  - DID (3): create_did_key, create_did_web, resolve_did
  - Delegation (4): create, verify, list, revoke
  - Reputation (3): record_interaction, get_reputation, query_reputation
  - Compliance (7): create_profile, get_profile, update_profile, get_status, record_assessment, generate_declaration, list_profiles
  - Credentials (8): issue, verify, verify_external, revoke, get, list, create_presentation, verify_presentation
  - Provenance (5): record_training_data, record_model_lineage, log_action, get_provenance, get_audit_trail
  - Blockchain (6): anchor_identity, anchor_credential, anchor_audit_batch, verify_anchor, get_anchor_status, estimate_anchor_cost
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

from config import LOG_FILE
from errors import setup_logging

# Initialize logging
setup_logging(log_file=str(LOG_FILE))

# Create MCP server
mcp = FastMCP("attestix")

# Register tool modules
from tools import (
    identity_tools, agent_card_tools, did_tools, delegation_tools, reputation_tools,
    compliance_tools, credential_tools, provenance_tools, blockchain_tools,
)

identity_tools.register(mcp)
agent_card_tools.register(mcp)
did_tools.register(mcp)
delegation_tools.register(mcp)
reputation_tools.register(mcp)
compliance_tools.register(mcp)
credential_tools.register(mcp)
provenance_tools.register(mcp)
blockchain_tools.register(mcp)

print(f"Attestix MCP server loaded: 47 tools registered", file=sys.stderr)


def main():
    nest_asyncio.apply()
    asyncio.run(mcp.run_stdio_async())


if __name__ == "__main__":
    main()
