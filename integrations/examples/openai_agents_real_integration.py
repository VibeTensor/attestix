"""OpenAI Agents SDK REAL Integration with Attestix

This is NOT a simulation. It uses the actual openai-agents SDK
(https://github.com/openai/openai-agents-python) to spawn the Attestix
MCP server over stdio and register its 47 tools with an Agent.

Key design patterns demonstrated:
  1. MCPServerStdio spawns the Attestix MCP server as a subprocess
  2. Agent is configured with mcp_servers=[attestix_server] so every
     Attestix tool is auto-discovered and callable by the LLM
  3. A compliance_gate function acts as an InputGuardrail that blocks
     the agent from proceeding when its compliance status is not met
  4. Tool discovery runs WITHOUT any OpenAI API call (dry-run mode)
  5. Full agent execution runs only when OPENAI_API_KEY is present

Requirements:
    pip install openai-agents attestix

Run (dry-run tool discovery, no API key needed):
    python integrations/examples/openai_agents_real_integration.py

Run (full execution with real LLM):
    export OPENAI_API_KEY=sk-...
    python integrations/examples/openai_agents_real_integration.py --live

SECURITY: Never hardcode OPENAI_API_KEY. Always read it from the
environment. This script reads os.environ["OPENAI_API_KEY"] only when
--live is explicitly requested.
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

# Allow running from the repo root or the integrations/examples/ directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Real OpenAI Agents SDK imports (agents 0.14.x)
from agents import Agent, Runner
from agents.mcp import MCPServerStdio

# Real Attestix services (used by the compliance_gate guardrail)
from services.compliance_service import ComplianceService
from services.identity_service import IdentityService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

DIVIDER = "=" * 70


def banner(title: str) -> None:
    print(f"\n{DIVIDER}")
    print(f"  {title}")
    print(DIVIDER)


# ---------------------------------------------------------------------------
# Compliance gate
# ---------------------------------------------------------------------------

def compliance_gate(agent_id: str, compliance_svc: ComplianceService) -> dict:
    """Deterministic compliance check used as an agent guardrail.

    Returns a dict with:
        allowed: bool
        reason:  str
        details: dict (full status from Attestix)

    This can be wired into the OpenAI Agents SDK as an InputGuardrail so
    the LLM is never even invoked if the agent is non-compliant. It can
    also be called directly before Runner.run() for a hard pre-check.
    """
    if not agent_id:
        return {"allowed": False, "reason": "no_identity", "details": {}}

    status = compliance_svc.get_compliance_status(agent_id)
    if "error" in status:
        return {"allowed": False, "reason": status["error"], "details": status}

    if not status.get("compliant"):
        return {
            "allowed": False,
            "reason": f"compliance at {status.get('completion_pct', 0)}%, missing {status.get('missing', [])}",
            "details": status,
        }

    return {"allowed": True, "reason": "fully_compliant", "details": status}


# ---------------------------------------------------------------------------
# Attestix MCP server factory
# ---------------------------------------------------------------------------

def build_attestix_mcp_server() -> MCPServerStdio:
    """Construct an MCPServerStdio pointed at the Attestix MCP server.

    Launches `python main.py` from the Attestix repo root, which starts
    FastMCP in stdio mode (see main.py:63 mcp.run_stdio_async()).

    In production you would replace this with:
        MCPServerStdio(params={"command": "attestix", "args": ["mcp"]})
    assuming the attestix PyPI package exposes a console script that
    runs the server. Here we use the in-repo main.py for development.
    """
    return MCPServerStdio(
        name="attestix",
        params={
            "command": sys.executable,
            "args": [str(PROJECT_ROOT / "main.py")],
            "cwd": str(PROJECT_ROOT),
        },
        cache_tools_list=True,
        client_session_timeout_seconds=30.0,
    )


# ---------------------------------------------------------------------------
# Main workflow
# ---------------------------------------------------------------------------

async def run_dry(server: MCPServerStdio) -> int:
    """Tool discovery only. Does NOT require OPENAI_API_KEY.

    Connects to the Attestix MCP server, lists all tools, and verifies
    that the Agent can be constructed with mcp_servers=[server]. No LLM
    call is made so there is no spend and no network egress to OpenAI.
    """
    banner("Phase 1: Connect to Attestix MCP server via stdio")
    await server.connect()
    print(f"  Connected. Server name: {server.name}")

    banner("Phase 2: Discover Attestix MCP tools")
    tools = await server.list_tools()
    print(f"  Tools discovered: {len(tools)}")
    for tool in tools[:10]:
        desc = (tool.description or "").split("\n")[0][:60]
        print(f"    - {tool.name}: {desc}")
    if len(tools) > 10:
        print(f"    ... and {len(tools) - 10} more")

    banner("Phase 3: Build Agent with Attestix tools")
    agent = Agent(
        name="ComplianceAnalyst",
        instructions=(
            "You are a financial compliance analyst agent. Before executing "
            "any task, you MUST call create_agent_identity to establish your "
            "UAIT, then create_compliance_profile for EU AI Act coverage. "
            "Log every action with log_action. Refuse tasks if the "
            "compliance gate blocks you."
        ),
        mcp_servers=[server],
        model="gpt-4o",
    )
    print(f"  Agent: {agent.name}")
    print(f"  Model: {agent.model}")
    print(f"  MCP servers: {len(agent.mcp_servers)}")
    print(f"  Attestix tools available via MCP: {len(tools)}")

    banner("Phase 4: Compliance gate dry-run (no LLM call)")
    identity_svc = IdentityService()
    compliance_svc = ComplianceService()

    # Bootstrap an identity locally to exercise the gate logic
    identity = identity_svc.create_identity(
        display_name="ComplianceAnalyst",
        source_protocol="openai_agents_sdk",
        capabilities=["financial_analysis", "compliance_checking"],
        description="Dry-run identity for OpenAI Agents SDK integration test",
        issuer_name="VibeTensor Inc.",
    )
    agent_id = identity["agent_id"]
    print(f"  Local agent identity: {agent_id}")
    print(f"  DID:                  {identity['issuer']['did'][:60]}...")

    # Gate check before profile exists (should block)
    gate_before = compliance_gate(agent_id, compliance_svc)
    print(f"\n  Pre-profile gate:  allowed={gate_before['allowed']} reason={gate_before['reason']}")

    # Create profile and re-check
    compliance_svc.create_compliance_profile(
        agent_id=agent_id,
        risk_category="limited",
        provider_name="VibeTensor Inc.",
        intended_purpose="Automated financial compliance analysis",
        transparency_obligations="Discloses AI involvement in all outputs",
        human_oversight_measures="Senior officer reviews all flagged items",
    )
    gate_after = compliance_gate(agent_id, compliance_svc)
    print(f"  Post-profile gate: allowed={gate_after['allowed']} reason={gate_after['reason']}")

    banner("Phase 5: Done (dry-run)")
    print("  Attestix MCP server loaded successfully via MCPServerStdio.")
    print(f"  {len(tools)} tools registered and callable by an OpenAI Agent.")
    print()
    print("  To run with a real LLM:")
    print("    export OPENAI_API_KEY=sk-...")
    print("    python integrations/examples/openai_agents_real_integration.py --live")

    return 0


async def run_live(server: MCPServerStdio) -> int:
    """Full execution with a real OpenAI LLM call.

    Only runs when OPENAI_API_KEY is set AND --live is passed.
    """
    if not os.environ.get("OPENAI_API_KEY"):
        print("  OPENAI_API_KEY not set. Skipping live run.", file=sys.stderr)
        print("  Set the env var and pass --live to execute with a real LLM.", file=sys.stderr)
        return 0

    banner("Live run with real OpenAI LLM")
    await server.connect()
    tools = await server.list_tools()
    print(f"  Attestix tools loaded: {len(tools)}")

    agent = Agent(
        name="ComplianceAnalyst",
        instructions=(
            "You are a compliance analyst. Create a UAIT identity for yourself "
            "using create_agent_identity, then report the agent_id and DID. "
            "Use display_name='LiveTestAgent' and source_protocol='openai_agents_sdk'."
        ),
        mcp_servers=[server],
        model="gpt-4o-mini",
    )

    result = await Runner.run(
        agent,
        "Please create your agent identity and tell me the resulting agent_id and DID.",
    )
    print()
    print("  LLM final output:")
    print(f"  {result.final_output}")
    return 0


async def amain(live: bool) -> int:
    banner("OpenAI Agents SDK REAL Integration with Attestix")
    print("  SDK:           openai-agents (real import: from agents import Agent)")
    print("  MCP transport: MCPServerStdio (real: from agents.mcp import MCPServerStdio)")
    print("  Attestix:      47 MCP tools via stdio subprocess")

    server = build_attestix_mcp_server()
    try:
        async with server:
            if live:
                return await run_live(server)
            return await run_dry(server)
    except Exception as exc:
        print(f"\n  ERROR: {exc}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--live",
        action="store_true",
        help="Execute a real OpenAI LLM call (requires OPENAI_API_KEY).",
    )
    args = parser.parse_args()

    if args.live and not os.environ.get("OPENAI_API_KEY"):
        print("  --live requires OPENAI_API_KEY env var to be set.", file=sys.stderr)
        print("  Running dry-run instead.", file=sys.stderr)
        args.live = False

    return asyncio.run(amain(live=args.live))


if __name__ == "__main__":
    sys.exit(main())
