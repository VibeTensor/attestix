"""Coding-agent hooks core for Attestix.

Coding agents (Claude Code today) run a shell command on lifecycle and tool
events and pipe the event on stdin. ``attestix hooks run --agent <name>``
reads that payload, maps it with the agent's adapter module to a normalised
event, and appends one hash-chained, signed row to the Attestix audit log via
:meth:`ProvenanceService.log_action`, under one Attestix agent identity per
(agent product, project directory).

Normalised event (produced by each adapter's ``to_event(payload)``)::

    agent_product, event, session_id, tool_name, tool_use_id, cwd,
    project_dir, reason, input_sha256, output_sha256, input_preview,
    output_preview, ts

Only SHA-256 digests are stored for full content; previews are truncated to
200 chars like the LangChain callback, and dropped entirely when
``ATTESTIX_HOOK_PREVIEW=0``.

The runner is observe-only: nothing on stdout, always exit 0, own errors on
stderr, no network calls.

Adding an agent = one adapter module exposing ``to_event``, ``settings_path``,
``merge_hooks``, ``remove_hooks``, registered in :data:`ADAPTERS`.
"""

from __future__ import annotations

import contextlib
import hashlib
import importlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

ADAPTERS = {"claude-code": "attestix.integrations.claude_code"}
PREVIEW_CHARS = 200
_AGENT_CACHE_NAME = "agent_hooks_identities.json"
_TOOL_EVENTS = {"tool_start", "tool_end"}


def adapter(agent: str):
    if agent not in ADAPTERS:
        raise ValueError(f"unknown agent {agent!r}; supported: {', '.join(sorted(ADAPTERS))}")
    return importlib.import_module(ADAPTERS[agent])


def digest(value: Any) -> str:
    """SHA-256 over canonical JSON (sorted keys, compact separators, UTF-8)."""
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def preview(value: Any) -> str:
    if value is None or os.environ.get("ATTESTIX_HOOK_PREVIEW", "1") == "0":
        return ""
    text = value if isinstance(value, str) else json.dumps(value, sort_keys=True, default=str)
    return text[:PREVIEW_CHARS]


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _data_dir() -> Path:
    from attestix import config  # read at call time so ATTESTIX_DATA_DIR / test patches apply

    return Path(config.DATA_DIR)


def get_or_create_agent(product: str, project_dir: str) -> str:
    """Return the cached Attestix agent_id for (product, project), creating it once."""
    from attestix.services.identity_service import IdentityService

    cache_file = _data_dir() / _AGENT_CACHE_NAME
    cache = json.loads(cache_file.read_text(encoding="utf-8")) if cache_file.exists() else {}
    key = f"{product}:{project_dir}"
    svc = IdentityService()
    agent_id = cache.get(key)
    if agent_id and svc.get_identity(agent_id):
        return agent_id
    agent = svc.create_identity(
        display_name=f"{product}:{Path(project_dir).name or 'project'}"[:120],
        source_protocol="manual",
        capabilities=["coding_agent", product],
        description=f"{product} sessions in {project_dir}",
        issuer_name="self",
    )
    cache[key] = agent["agent_id"]
    cache_file.write_text(json.dumps(cache, indent=2), encoding="utf-8")
    return agent["agent_id"]


def record(ev: dict) -> dict:
    """Append one audit row for a normalised event. Returns the row."""
    from filelock import FileLock

    from attestix.services.provenance_service import ProvenanceService

    label = f"{ev['agent_product']}.{ev['event']}" + (f": {ev['tool_name']}" if ev.get("tool_name") else "")
    details = {k: v for k, v in ev.items() if k not in ("input_preview", "output_preview") and v not in ("", None)}

    # Agents fire hooks concurrently (parallel tool calls) and log_action is
    # load-then-save, so serialise to avoid dropped rows or forked chains.
    with FileLock(str(_data_dir() / "agent_hooks.lock"), timeout=10):
        agent_id = get_or_create_agent(ev["agent_product"], ev["project_dir"])
        row = ProvenanceService().log_action(
            agent_id=agent_id,
            action_type="external_call" if ev["event"] in _TOOL_EVENTS else "inference",
            input_summary=f"{label} | {ev['input_preview']}" if ev.get("input_preview") else label,
            output_summary=ev.get("output_preview", ""),
            decision_rationale=json.dumps(details, sort_keys=True, separators=(",", ":")),
        )
    if "error" in row:
        raise RuntimeError(row["error"])
    return row


def run(agent: str, stdin: Optional[Any] = None) -> int:
    """Hook entry point. Always returns 0 so the coding agent is never blocked."""
    try:
        stream = stdin if stdin is not None else sys.stdin.buffer
        payload = json.loads(stream.read().decode("utf-8", errors="replace"))
        if not isinstance(payload, dict):
            raise ValueError("hook payload is not a JSON object")
        # Nothing may reach stdout: agents parse it as hook output.
        with contextlib.redirect_stdout(sys.stderr):
            record(adapter(agent).to_event(payload))
    except Exception as exc:  # observe-only: report and carry on
        print(f"attestix hooks run: {type(exc).__name__}: {exc}", file=sys.stderr)
    return 0
