"""Tests for the MCP tool layer — generic patterns across all tools."""

import json

import pytest

from main import mcp


def get_tool_func(name: str):
    """Get a tool function by name from the registered MCP tools."""
    tools = mcp._tool_manager._tools
    if name in tools:
        return tools[name].fn
    raise KeyError(f"Tool '{name}' not found. Available: {list(tools.keys())}")


class TestToolRegistration:
    def test_tools_registered(self):
        tools = mcp._tool_manager._tools
        assert len(tools) >= 42, (
            f"Expected at least 42 tools, got {len(tools)}"
        )

    def test_all_tools_are_async(self):
        import asyncio
        tools = mcp._tool_manager._tools
        for name, tool in tools.items():
            assert asyncio.iscoroutinefunction(tool.fn), (
                f"Tool '{name}' is not async"
            )


class TestValidateRequired:
    """Tools using _validate_required return error JSON for empty params."""

    @pytest.mark.asyncio
    async def test_create_identity_empty_name(self):
        fn = get_tool_func("create_agent_identity")
        result = await fn(display_name="")
        data = json.loads(result)
        assert "error" in data
        assert "display_name" in data["error"]

    @pytest.mark.asyncio
    async def test_anchor_identity_empty_agent(self):
        fn = get_tool_func("anchor_identity")
        result = await fn(agent_id="")
        data = json.loads(result)
        assert "error" in data
        assert "agent_id" in data["error"]

    @pytest.mark.asyncio
    async def test_issue_credential_empty_fields(self):
        fn = get_tool_func("issue_credential")
        result = await fn(
            subject_agent_id="",
            credential_type="Test",
            issuer_name="I",
            claims_json='{"x":1}',
        )
        data = json.loads(result)
        assert "error" in data

    @pytest.mark.asyncio
    async def test_record_training_data_empty_agent(self):
        fn = get_tool_func("record_training_data")
        result = await fn(agent_id="", dataset_name="DS")
        data = json.loads(result)
        assert "error" in data

    @pytest.mark.asyncio
    async def test_create_compliance_empty_fields(self):
        fn = get_tool_func("create_compliance_profile")
        result = await fn(agent_id="", risk_category="limited", provider_name="Corp")
        data = json.loads(result)
        assert "error" in data


class TestJsonReturn:
    """All tools return valid JSON strings."""

    @pytest.mark.asyncio
    async def test_list_identities_returns_json(self):
        fn = get_tool_func("list_identities")
        result = await fn()
        parsed = json.loads(result)
        assert isinstance(parsed, list)

    @pytest.mark.asyncio
    async def test_create_did_key_returns_json(self):
        fn = get_tool_func("create_did_key")
        result = await fn()
        parsed = json.loads(result)
        assert "did" in parsed

    @pytest.mark.asyncio
    async def test_query_reputation_returns_json(self):
        fn = get_tool_func("query_reputation")
        result = await fn()
        parsed = json.loads(result)
        assert isinstance(parsed, list)


class TestNotFoundPattern:
    """Tools return consistent error for non-existent IDs."""

    @pytest.mark.asyncio
    async def test_get_identity_not_found(self):
        fn = get_tool_func("get_identity")
        result = await fn(agent_id="attestix:nonexistent")
        data = json.loads(result)
        assert "error" in data
        assert "not found" in data["error"].lower()

    @pytest.mark.asyncio
    async def test_get_credential_not_found(self):
        fn = get_tool_func("get_credential")
        result = await fn(credential_id="urn:uuid:nonexistent")
        data = json.loads(result)
        assert "error" in data
        assert "not found" in data["error"].lower()

    @pytest.mark.asyncio
    async def test_get_compliance_not_found(self):
        fn = get_tool_func("get_compliance_profile")
        result = await fn(agent_id="attestix:nonexistent")
        data = json.loads(result)
        assert "error" in data


class TestCsvSplitting:
    """Tools that accept CSV strings split them correctly."""

    @pytest.mark.asyncio
    async def test_create_identity_splits_capabilities(self):
        fn = get_tool_func("create_agent_identity")
        result = await fn(
            display_name="Bot",
            capabilities="read, write, admin",
        )
        data = json.loads(result)
        assert data["capabilities"] == ["read", "write", "admin"]
