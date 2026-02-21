# Contributing to Attestix

Thank you for your interest in contributing to Attestix. This guide covers how to get started, the development workflow, and project conventions.

## Getting Started

### Prerequisites

- Python 3.10+
- Git

### Setup

```bash
git clone https://github.com/VibeTensor/attestix.git
cd attestix
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Verify Setup

```bash
python main.py
# Should print "Attestix MCP server loaded: 47 tools registered" to stderr
# Then wait for MCP client connections on stdio
```

Press Ctrl+C to stop.

## Project Structure

```
attestix/
  auth/           # Cryptography and token parsing
  services/       # Business logic (one service per module)
  tools/          # MCP tool definitions (thin wrappers around services)
  docs/           # Documentation
  examples/       # Runnable example scripts
  config.py       # Storage paths and helpers
  errors.py       # Error handling and logging
  main.py         # Entry point
```

### Architecture Rules

1. **Services contain all logic.** Tool files are thin wrappers that call service methods.
2. **Services never import from tools.** Dependencies flow: tools -> services -> config/auth.
3. **All output to stderr.** `builtins.print` is redirected to stderr to protect MCP JSON-RPC on stdout.
4. **JSON storage with file locking.** Use `_safe_load` / `_safe_save` from `config.py` for all file I/O.
5. **Ed25519 signatures.** All persistent records (UAITs, VCs, audit entries) must be signed.

## How to Contribute

### Reporting Issues

Open an issue on GitHub with:
- What you expected
- What happened
- Steps to reproduce
- Python version and OS

### Submitting Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Run the test suite to verify nothing is broken:
   ```bash
   # Run all 284 tests (unit, e2e, conformance benchmarks)
   pytest tests/ -v -m "not live_blockchain"

   # Or run in Docker for a clean environment
   docker build -f Dockerfile.test -t attestix-bench . && docker run --rm attestix-bench
   ```
5. Commit with a descriptive message
6. Push to your fork and open a Pull Request

### Pull Request Guidelines

- One feature or fix per PR
- Keep changes focused - avoid mixing refactoring with new features
- Update documentation if you change tool parameters or behavior
- Add an example script if you add a new module

## Code Conventions

### Style

- Python standard library style (no external formatter enforced)
- Use type hints for function signatures
- Docstrings on all public methods and classes
- Keep imports sorted: stdlib, third-party, local

### Naming

- Services: `{module}_service.py` with a class named `{Module}Service`
- Tools: `{module}_tools.py` with a `register(mcp)` function
- Storage files: lowercase `{module}.json`
- IDs: prefixed with module abbreviation (e.g., `attestix:`, `comp:`, `assess:`, `urn:uuid:`)

### Error Handling

Return error dicts instead of raising exceptions in service methods:

```python
def my_method(self, agent_id: str) -> dict:
    agent = self._find_agent(agent_id)
    if not agent:
        return format_error(
            "Agent not found",
            ErrorCategory.IDENTITY,
            "AGENT_NOT_FOUND",
        )
    # ... do work
    return {"result": "success"}
```

### Adding a New Module

1. Create `services/your_service.py` with a service class
2. Create `tools/your_tools.py` with a `register(mcp)` function
3. Add storage helpers to `config.py` if needed
4. Add error category to `errors.py` if needed
5. Import and register in `main.py`
6. Update tool count in `main.py` docstring
7. Add documentation to `docs/api-reference.md`
8. Create an example in `examples/`

## Security

- Never return private keys in tool responses
- Exclude mutable fields (proof, credentialStatus) from signature payloads
- Use `secrets` module for generating random identifiers
- Validate all URLs before making HTTP requests (SSRF protection)
- Report security vulnerabilities privately via email, not public issues

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.
