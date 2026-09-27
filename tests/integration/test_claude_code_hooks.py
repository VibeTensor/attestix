"""Claude Code hooks integration: payloads -> chained audit rows, installer merge."""

import io
import json
import os
import subprocess
import sys

from click.testing import CliRunner

from attestix.cli import cli
from attestix.config import load_provenance, save_provenance
from attestix.integrations import agent_hooks, claude_code as cc

SESSION = {"session_id": "sess-1", "transcript_path": "/t.jsonl", "cwd": "/work/proj"}
TOOL_INPUT = {"command": "npm test", "description": "run tests"}
TOOL_RESPONSE = {"stdout": "ok", "stderr": "", "interrupted": False}
PAYLOADS = [
    {**SESSION, "hook_event_name": "SessionStart", "source": "startup"},
    {**SESSION, "hook_event_name": "UserPromptSubmit", "prompt": "run the tests"},
    {**SESSION, "hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": TOOL_INPUT, "tool_use_id": "toolu_1"},
    {**SESSION, "hook_event_name": "PostToolUse", "tool_name": "Bash", "tool_input": TOOL_INPUT,
     "tool_response": TOOL_RESPONSE, "tool_use_id": "toolu_1"},
    {**SESSION, "hook_event_name": "Stop", "stop_hook_active": False},
    {**SESSION, "hook_event_name": "SessionEnd", "reason": "logout"},
]


def _feed(monkeypatch, payload):
    raw = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
    return agent_hooks.run("claude-code", io.BytesIO(raw))


def test_all_events_chain_and_verify(monkeypatch, capsys):
    monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
    for p in PAYLOADS:
        assert _feed(monkeypatch, p) == 0
    assert capsys.readouterr().out == ""  # stdout must stay clean for Claude Code

    rows = load_provenance()["audit_log"]
    assert len(rows) == len(PAYLOADS)
    assert len({r["agent_id"] for r in rows}) == 1  # one cached identity per project
    assert rows[0]["prev_hash"] == "0" * 64
    for prev, cur in zip(rows, rows[1:]):
        assert cur["prev_hash"] == prev["chain_hash"]

    details = [json.loads(r["decision_rationale"]) for r in rows]
    assert [d["native_event"] for d in details] == [p["hook_event_name"] for p in PAYLOADS]
    assert [d["event"] for d in details] == ["session_start", "prompt", "tool_start", "tool_end", "turn_end", "session_end"]
    assert {d["agent_product"] for d in details} == {"claude-code"}
    post = details[3]
    assert post["tool_name"] == "Bash" and post["session_id"] == "sess-1" and post["cwd"] == "/work/proj"
    assert post["input_sha256"] == agent_hooks.digest(TOOL_INPUT)
    assert post["output_sha256"] == agent_hooks.digest(TOOL_RESPONSE)
    assert details[1]["input_sha256"] == agent_hooks.digest("run the tests")

    from attestix.auth.crypto import did_key_to_public_key, verify_json_signature
    for r in rows:
        signable = {k: v for k, v in r.items() if k != "signature"}
        assert verify_json_signature(did_key_to_public_key(r["logged_by"]), signable, r["signature"])

    agent_id = rows[0]["agent_id"]
    out = CliRunner().invoke(cli, ["audit", agent_id, "--limit", "1000"]).output
    assert "Chain integrity: VERIFIED" in out

    data = load_provenance()
    data["audit_log"][2]["input_summary"] = "tampered"
    save_provenance(data)
    res = CliRunner().invoke(cli, ["audit", agent_id, "--limit", "1000"])
    assert "BROKEN" in res.output + (res.stderr if res.stderr_bytes else "")


def test_preview_can_be_disabled(monkeypatch):
    monkeypatch.setenv("ATTESTIX_HOOK_PREVIEW", "0")
    _feed(monkeypatch, PAYLOADS[3])
    row = load_provenance()["audit_log"][-1]
    assert "npm test" not in row["input_summary"] and row["output_summary"] == ""


def test_malformed_input_exits_zero(monkeypatch, capsys):
    for bad in (b"not json", b"[1,2]", b"", b"\xff\xfe"):
        assert _feed(monkeypatch, bad) == 0
    captured = capsys.readouterr()
    assert captured.out == "" and "attestix hooks run" in captured.err
    assert load_provenance()["audit_log"] == []


def test_subprocess_exit_code_and_silent_stdout(tmp_path):
    env = {**os.environ, "ATTESTIX_DATA_DIR": str(tmp_path)}
    for stdin in (b"{broken", json.dumps(PAYLOADS[2]).encode()):
        proc = subprocess.run([sys.executable, "-m", "attestix.cli", "hooks", "run", "--agent", "claude-code"],
                              input=stdin, capture_output=True, env=env, timeout=60)
        assert proc.returncode == 0 and proc.stdout == b""
    assert json.loads((tmp_path / "provenance.json").read_text())["audit_log"]


def test_merge_keeps_existing_hooks_and_is_idempotent():
    existing = {
        "model": "opus",
        "hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "guard.sh"}]}]},
    }
    merged = cc.merge_hooks(existing)
    assert merged["model"] == "opus"
    assert merged["hooks"]["PreToolUse"][0] == existing["hooks"]["PreToolUse"][0]
    assert set(merged["hooks"]) == set(cc.HOOK_EVENTS)
    assert cc.merge_hooks(merged) == merged
    assert cc.remove_hooks(merged) == existing


def test_cli_install_dry_run_then_write(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    settings = tmp_path / ".claude" / "settings.json"
    settings.parent.mkdir()
    original = {"hooks": {"Stop": [{"hooks": [{"type": "command", "command": "notify.sh"}]}]}}
    settings.write_text(json.dumps(original))
    runner = CliRunner()

    res = runner.invoke(cli, ["hooks", "install", "--agent", "claude-code"])
    assert res.exit_code == 0 and cc.HOOK_COMMAND in res.output
    assert json.loads(settings.read_text()) == original  # dry run by default

    assert runner.invoke(cli, ["hooks", "install", "--agent", "claude-code", "--write"]).exit_code == 0
    stop = json.loads(settings.read_text())["hooks"]["Stop"]
    assert stop[0]["hooks"][0]["command"] == "notify.sh" and len(stop) == 2

    assert runner.invoke(cli, ["hooks", "uninstall", "--agent", "claude-code", "--write"]).exit_code == 0
    assert json.loads(settings.read_text()) == original


def test_cli_refuses_invalid_settings(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    settings = tmp_path / ".claude" / "settings.json"
    settings.parent.mkdir()
    settings.write_text("{not json")
    res = CliRunner().invoke(cli, ["hooks", "install", "--agent", "claude-code", "--write"])
    assert res.exit_code != 0 and settings.read_text() == "{not json"


def test_unknown_agent_is_observe_only(monkeypatch, capsys):
    assert agent_hooks.run("no-such-agent", io.BytesIO(json.dumps(PAYLOADS[0]).encode())) == 0
    assert "unknown agent" in capsys.readouterr().err
    assert load_provenance()["audit_log"] == []
