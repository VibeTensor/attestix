"""Deny network access before importing the SDK or collecting callback tests."""

import socket
import subprocess


def deny_external_io(*_args, **_kwargs):
    raise AssertionError("Offline LangChain tests cannot use network or subprocesses")


socket.socket.connect = deny_external_io
socket.socket.connect_ex = deny_external_io
socket.create_connection = deny_external_io
socket.getaddrinfo = deny_external_io
subprocess.Popen = deny_external_io

import langchain_core  # noqa: E402,F401 - the dedicated job must not silently skip
import pytest  # noqa: E402

raise SystemExit(pytest.main([
    "tests/integration/test_langchain_sdk_offline.py", "-v", "--tb=short",
]))
