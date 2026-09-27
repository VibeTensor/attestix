"""Claude Code adapter for :mod:`attestix.integrations.agent_hooks`.

Maps Claude Code hook payloads (stdin JSON) to the normalised hook event and
merges / removes the hook entries in Claude Code's settings.json.
"""

from __future__ import annotations

import copy
import os
from pathlib import Path

from attestix.integrations.agent_hooks import digest, now, preview

PRODUCT = "claude-code"
HOOK_COMMAND = "attestix hooks run --agent claude-code"
HOOK_EVENTS = ("SessionStart", "UserPromptSubmit", "PreToolUse", "PostToolUse", "Stop", "SessionEnd")
_EVENT_NAMES = {
    "SessionStart": "session_start",
    "UserPromptSubmit": "prompt",
    "PreToolUse": "tool_start",
    "PostToolUse": "tool_end",
    "Stop": "turn_end",
    "SessionEnd": "session_end",
}


def to_event(payload: dict) -> dict:
    raw_event = str(payload.get("hook_event_name") or "unknown")
    cwd = str(payload.get("cwd") or "")
    # Tool events carry tool_input/tool_response; prompt and Stop events carry
    # prompt/last_assistant_message. tool_output is accepted as an alias.
    inp_key = next((k for k in ("tool_input", "prompt") if k in payload), None)
    out_key = next((k for k in ("tool_response", "tool_output", "last_assistant_message") if k in payload), None)
    inp = payload[inp_key] if inp_key else None
    out = payload[out_key] if out_key else None
    return {
        "agent_product": PRODUCT,
        "event": _EVENT_NAMES.get(raw_event, raw_event),
        "native_event": raw_event,
        "session_id": str(payload.get("session_id") or ""),
        "tool_name": str(payload.get("tool_name") or ""),
        "tool_use_id": str(payload.get("tool_use_id") or ""),
        "cwd": cwd,
        "project_dir": os.environ.get("CLAUDE_PROJECT_DIR") or cwd or os.getcwd(),
        "reason": str(payload.get("source") or payload.get("reason") or payload.get("session_start_reason")
                      or payload.get("session_end_reason") or ""),
        "input_sha256": digest(inp) if inp_key else "",
        "output_sha256": digest(out) if out_key else "",
        "input_preview": preview(inp),
        "output_preview": preview(out),
        "ts": now(),
    }


def settings_path(user: bool) -> Path:
    return (Path.home() if user else Path.cwd()) / ".claude" / "settings.json"


def _is_ours(hook: dict) -> bool:
    return HOOK_COMMAND in str(hook.get("command", ""))


def merge_hooks(settings: dict) -> dict:
    """Return a copy of settings with our hook added to each event. Idempotent."""
    out = copy.deepcopy(settings)
    hooks = out.setdefault("hooks", {})
    for event in HOOK_EVENTS:
        groups = hooks.setdefault(event, [])
        if any(_is_ours(h) for g in groups for h in g.get("hooks", [])):
            continue
        groups.append({"hooks": [{"type": "command", "command": HOOK_COMMAND, "timeout": 10}]})
    return out


def remove_hooks(settings: dict) -> dict:
    """Return a copy of settings with only our hook entries removed."""
    out = copy.deepcopy(settings)
    hooks = out.get("hooks", {})
    for event in list(hooks):
        kept = []
        for group in hooks[event]:
            inner = [h for h in group.get("hooks", []) if not _is_ours(h)]
            if inner or not group.get("hooks"):
                kept.append({**group, "hooks": inner} if inner else group)
        if kept:
            hooks[event] = kept
        else:
            del hooks[event]
    if "hooks" in out and not out["hooks"]:
        del out["hooks"]
    return out
