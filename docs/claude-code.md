# Claude Code hooks

Attestix can record every Claude Code session event and tool call in its hash-chained audit log, using Claude Code's command hooks. No extra dependency is needed.

## Install

```bash
pip install attestix
attestix hooks install --agent claude-code                 # dry run: prints the settings.json diff
attestix hooks install --agent claude-code --write         # writes ./.claude/settings.json
attestix hooks install --agent claude-code --user --write  # writes ~/.claude/settings.json instead
```

The installer merges into the existing file. Your other hooks and settings are kept, re-running it is a no-op, and a copy of the previous file is saved as `settings.json.bak`. It refuses to touch a settings file that is not valid JSON. `attestix hooks uninstall --agent claude-code [--user] --write` removes only the Attestix entries.

For each of `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `Stop` and `SessionEnd` it adds:

```json
{ "hooks": [ { "type": "command", "command": "attestix hooks run --agent claude-code", "timeout": 10 } ] }
```

`attestix` must be on the `PATH` that Claude Code sees. The hook core (`attestix.integrations.agent_hooks`) is agent-neutral; Claude Code is the only adapter so far (`attestix.integrations.claude_code`).

## What gets recorded

Each hook event becomes one `log_action` row for an Attestix agent identity created once per project directory (`CLAUDE_PROJECT_DIR`, else the event's `cwd`). The agent id is cached in `$ATTESTIX_DATA_DIR/agent_hooks_identities.json`.

- `decision_rationale` holds a normalised event as JSON: `agent_product`, `event` (`session_start`, `prompt`, `tool_start`, `tool_end`, `turn_end`, `session_end`), `native_event`, `session_id`, `cwd`, `project_dir`, `tool_name`, `tool_use_id`, `reason`, `ts`, and `input_sha256` / `output_sha256` over `tool_input` or `prompt` and `tool_response` or `last_assistant_message` (whichever the event carries).
- Digests are SHA-256 over canonical JSON (`sort_keys=True`, separators `(",", ":")`, UTF-8), so you can recompute them from a transcript.
- `input_summary` / `output_summary` carry a 200-character preview, like the LangChain callback. Tool inputs can contain secrets; set `ATTESTIX_HOOK_PREVIEW=0` in the environment to store digests only.

The hook is observe-only. It always exits 0, prints nothing to stdout, reports its own errors on stderr (visible in Claude Code's debug log), and makes no network calls. It cannot block or change a tool call.

## Verify the trail

```bash
attestix list --name-contains claude-code   # find the agent id
attestix audit <agent_id> --limit 100000    # prints rows and "Chain integrity: VERIFIED" or "BROKEN"
```

Use a `--limit` larger than the number of rows: verification walks the chain from the first row.

`attestix audit` checks the hash links only. To also check each row's Ed25519 signature against the server key named in `logged_by`:

```python
from attestix.auth.crypto import did_key_to_public_key, verify_json_signature
from attestix.services.provenance_service import ProvenanceService

for r in ProvenanceService().get_audit_trail("<agent_id>", limit=100000):
    body = {k: v for k, v in r.items() if k != "signature"}
    assert verify_json_signature(did_key_to_public_key(r["logged_by"]), body, r["signature"]), r["log_id"]
```

## What this does and does not prove

Every row is SHA-256 hash-chained to the previous row for the same agent and signed with the Attestix server key in `$ATTESTIX_DATA_DIR`. Editing or deleting a row in the middle of the chain breaks the hash links, and rewriting the chain to hide that breaks the signatures unless the rewriter holds the key. So the log is tamper-evident against people who do not hold that key, provided you check signatures (see above) and not only the hash links. It is not tamper-evident against the operator: whoever holds the data directory and signing key can rewrite and re-sign the whole chain, or truncate its tail. Anchor chain heads externally if you need protection against that.

Limitations: the hook sees only what Claude Code puts in the hook payload. It does not see model reasoning, MCP server internals, subprocesses spawned by a tool, or events that are not hooked (for example `PostToolUseFailure`, `SubagentStop`, `PreCompact`). If the hook fails (for example a lock timeout), that event is missing from the trail and the error is only on stderr.
