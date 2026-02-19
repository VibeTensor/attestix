# Getting Started with Attestix

Get your first AI agent identity in under 5 minutes.

## Prerequisites

- Python 3.10 or later
- pip

## Installation

```bash
pip install attestix
```

Or install from source:

```bash
git clone https://github.com/VibeTensor/attestix.git
cd attestix
pip install -r requirements.txt
```

## Option A: Use with Claude Code (MCP Server)

Add to your Claude Code config (`~/.claude.json` on macOS/Linux, `%USERPROFILE%\.claude.json` on Windows):

```json
{
  "mcpServers": {
    "attestix": {
      "type": "stdio",
      "command": "python",
      "args": ["/path/to/attestix/main.py"]
    }
  }
}
```

Restart Claude Code. You now have 36 Attestix tools available.

Then just ask Claude:

> "Create an identity for my data analysis agent with capabilities: data_analysis, report_generation"

Claude will call `create_agent_identity` and return your agent's UAIT.

## Option B: Use as Python Library

```python
import sys
sys.path.insert(0, "/path/to/attestix")

from services.identity_service import IdentityService

svc = IdentityService()
agent = svc.create_identity(
    display_name="MyAgent",
    source_protocol="manual",
    capabilities=["data_analysis", "report_generation"],
    description="Analyzes quarterly financial data",
    issuer_name="Acme Corp",
)

print(f"Agent ID: {agent['agent_id']}")
print(f"DID: {agent['issuer']['did']}")
print(f"Signed: {bool(agent['signature'])}")
```

## Option C: Run as Standalone MCP Server

```bash
cd attestix
python main.py
```

This starts the MCP server on stdio, ready for any MCP client to connect.

## What Just Happened?

When you created an identity, Attestix:

1. Generated a unique agent ID (e.g., `attestix:f9bdb7a94ccb40f1`)
2. Created a Unified Agent Identity Token (UAIT) containing your agent's name, capabilities, and metadata
3. Signed the UAIT with Ed25519 using the server's cryptographic key
4. Stored the UAIT in `identities.json` (created automatically)
5. Assigned a DID (Decentralized Identifier) derived from the signing key

## Verify Your Agent

```python
result = svc.verify_identity(agent["agent_id"])
print(result)
# {
#   "valid": true,
#   "checks": {
#     "exists": true,
#     "not_revoked": true,
#     "not_expired": true,
#     "signature_valid": true
#   }
# }
```

## First-Time Setup Notes

- **Signing key**: On first run, Attestix auto-generates an Ed25519 keypair stored in `.signing_key.json`. This is your server's identity. Keep it safe.
- **Data files**: JSON files (`identities.json`, `credentials.json`, etc.) are created lazily on first use. No database setup needed.
- **No cloud dependency**: Everything runs locally. No external API calls needed for core operations.

## Next Steps

- [EU AI Act Compliance Guide](eu-ai-act-compliance.md) -- Full compliance workflow
- [Concepts Explained](concepts.md) -- What are UAITs, DIDs, VCs?
- [API Reference](api-reference.md) -- All 36 tools documented
- [Examples](../examples/) -- Runnable Python scripts
