"""MCP server tool registration conformance tests.

Validates that all 47 tools across 9 modules are registered correctly
and follow the Attestix naming convention.
"""

import asyncio

from main import mcp


EXPECTED_MODULES = {
    "identity",
    "agent_card",
    "did",
    "delegation",
    "reputation",
    "compliance",
    "credential",
    "provenance",
    "blockchain",
}

# Tool names grouped by module (authoritative list from main.py docstring)
EXPECTED_TOOL_NAMES = [
    # Identity (8)
    "create_agent_identity",
    "resolve_identity",
    "verify_identity",
    "translate_identity",
    "list_identities",
    "get_identity",
    "revoke_identity",
    "purge_agent_data",
    # Agent Cards (3)
    "parse_agent_card",
    "generate_agent_card",
    "discover_agent",
    # DID (3)
    "create_did_key",
    "create_did_web",
    "resolve_did",
    # Delegation (4)
    "create_delegation",
    "verify_delegation",
    "list_delegations",
    "revoke_delegation",
    # Reputation (3)
    "record_interaction",
    "get_reputation",
    "query_reputation",
    # Compliance (7)
    "create_compliance_profile",
    "get_compliance_profile",
    "update_compliance_profile",
    "get_compliance_status",
    "record_conformity_assessment",
    "generate_declaration_of_conformity",
    "list_compliance_profiles",
    # Credentials (8)
    "issue_credential",
    "verify_credential",
    "verify_credential_external",
    "revoke_credential",
    "get_credential",
    "list_credentials",
    "create_verifiable_presentation",
    "verify_presentation",
    # Provenance (5)
    "record_training_data",
    "record_model_lineage",
    "log_action",
    "get_provenance",
    "get_audit_trail",
    # Blockchain (6)
    "anchor_identity",
    "anchor_credential",
    "anchor_audit_batch",
    "verify_anchor",
    "get_anchor_status",
    "estimate_anchor_cost",
]


class TestToolRegistration:
    """All 47 tools must be registered with the MCP server."""

    def test_total_tool_count(self):
        tools = mcp._tool_manager._tools
        assert len(tools) >= 47, (
            f"Expected at least 47 tools, got {len(tools)}: {sorted(tools.keys())}"
        )

    def test_each_tool_registered(self):
        tools = mcp._tool_manager._tools
        missing = [name for name in EXPECTED_TOOL_NAMES if name not in tools]
        assert missing == [], f"Missing tools: {missing}"

    def test_nine_modules_represented(self):
        tools = mcp._tool_manager._tools
        tool_names = set(tools.keys())
        found_modules = set()
        for module in EXPECTED_MODULES:
            # Check that at least one tool from each module is present
            module_tools = [
                t for t in EXPECTED_TOOL_NAMES
                if t in tool_names and _belongs_to_module(t, module)
            ]
            if module_tools:
                found_modules.add(module)
        assert found_modules == EXPECTED_MODULES, (
            f"Missing modules: {EXPECTED_MODULES - found_modules}"
        )


class TestToolConventions:
    """Tool naming and interface conventions."""

    def test_all_tools_are_async(self):
        tools = mcp._tool_manager._tools
        non_async = [
            name for name, tool in tools.items()
            if not asyncio.iscoroutinefunction(tool.fn)
        ]
        assert non_async == [], f"Non-async tools: {non_async}"

    def test_tool_names_are_snake_case(self):
        tools = mcp._tool_manager._tools
        for name in tools:
            assert name == name.lower(), f"Tool name not lowercase: {name}"
            assert " " not in name, f"Tool name has spaces: {name}"
            assert "-" not in name, f"Tool name has hyphens: {name}"


def _belongs_to_module(tool_name: str, module: str) -> bool:
    """Heuristic: check if a tool name belongs to a given module."""
    module_prefixes = {
        "identity": ["create_agent", "resolve_identity", "verify_identity",
                      "translate_identity", "list_identit", "get_identity",
                      "revoke_identity", "purge_agent"],
        "agent_card": ["parse_agent_card", "generate_agent_card", "discover_agent"],
        "did": ["create_did", "resolve_did"],
        "delegation": ["create_delegation", "verify_delegation",
                        "list_delegation", "revoke_delegation"],
        "reputation": ["record_interaction", "get_reputation", "query_reputation"],
        "compliance": ["compliance", "conformity_assessment", "declaration_of_conformity"],
        "credential": ["credential", "presentation"],
        "provenance": ["training_data", "model_lineage", "log_action",
                        "provenance", "audit_trail"],
        "blockchain": ["anchor", "estimate_anchor"],
    }
    prefixes = module_prefixes.get(module, [])
    return any(prefix in tool_name for prefix in prefixes)
