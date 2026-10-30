"""Exercise the documented stdio entry point without calling any tool."""

import asyncio
import json
import os
from pathlib import Path
import re
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import pytest


@pytest.mark.asyncio
async def test_documented_stdio_config_initializes_and_lists_tools(tmp_path):
    root = Path(__file__).resolve().parents[2]
    guide = (root / 'website/content/docs/guides/integration-guide.mdx').read_text(encoding='utf-8')
    configs = [json.loads(block) for block in re.findall(r'```json\s+(.*?)```', guide, re.DOTALL)]
    advertised = next(config['mcpServers']['attestix'] for config in configs if 'mcpServers' in config)
    assert advertised['command'] == 'python'
    environment = {
        name: os.environ[name]
        for name in ('SystemRoot', 'PATH', 'USERPROFILE', 'LOCALAPPDATA', 'TEMP', 'TMP', 'APPDATA')
        if name in os.environ
    }
    environment.update(
        ATTESTIX_DATA_DIR=str(tmp_path), PYTHONPATH=str(root), PYTHONDONTWRITEBYTECODE='1',
        OTEL_SDK_DISABLED='true', DO_NOT_TRACK='1',
    )
    parameters = StdioServerParameters(command=sys.executable, args=advertised['args'], env=environment, cwd=tmp_path)
    async with asyncio.timeout(60):
        async with stdio_client(parameters) as (reader, writer):
            async with ClientSession(reader, writer) as session:
                initialized = await session.initialize()
                tools = await session.list_tools()
                assert initialized.serverInfo.name == 'attestix'
                assert tools.tools
    assert not (tmp_path / '.signing_key.json').exists()
