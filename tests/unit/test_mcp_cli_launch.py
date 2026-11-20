"""The additive console subcommand preserves existing CLI behavior."""

import sys
from types import SimpleNamespace
from unittest.mock import Mock

from click.testing import CliRunner

from attestix.cli import cli


def test_mcp_subcommand_delegates_without_printing(monkeypatch):
    main = Mock()
    monkeypatch.setitem(sys.modules, "attestix.main", SimpleNamespace(main=main))

    result = CliRunner().invoke(cli, ["mcp"])

    assert result.exit_code == 0
    assert result.output == ""
    main.assert_called_once_with()


def test_mcp_help_does_not_start_server(monkeypatch):
    main = Mock()
    monkeypatch.setitem(sys.modules, "attestix.main", SimpleNamespace(main=main))

    result = CliRunner().invoke(cli, ["mcp", "--help"])

    assert result.exit_code == 0
    assert "standard input/output" in result.output
    main.assert_not_called()


def test_no_argument_cli_still_returns_help():
    result = CliRunner().invoke(cli, [])

    assert result.exit_code == 2
    assert "Usage:" in result.output
