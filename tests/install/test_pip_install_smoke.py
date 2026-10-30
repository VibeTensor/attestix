"""Real `pip install attestix` smoke test (v0.4.0-rc.2 packaging gate).

This is the regression test for the ICP-funnel blocker fixed in v0.4.0-rc.2:
prior to rc.2 the wheel dropped flat top-level packages (``services/``,
``auth/``, ``storage/``, ...) into site-packages, polluting every consumer's
namespace and forcing the documented import to be ``from services.X import Y``
instead of ``from attestix.services.X import Y``. 9/12 ICP personas dropped at
Integrate because of this.

This test rebuilds the wheel from the source tree (via ``python -m build``),
installs it into a throwaway venv, and asserts three invariants:

1. The wheel's top-level set is the canonical ``attestix`` namespace plus the
   deprecated compatibility deprecation shims (and nothing else weird like
   ``tests`` or ``paper``).
2. The canonical imports work: ``from attestix.services.identity_service
   import IdentityService`` and friends.
3. The legacy flat imports still work *and* emit a ``DeprecationWarning``
   pointing at the canonical namespace (``-W error::DeprecationWarning`` makes
   the import raise — this is the contract the shims must keep).

The test is opt-in (``ATTESTIX_RUN_INSTALL_SMOKE=1``) because building a wheel
on a developer laptop is multi-second and a fresh-venv pip install needs
network + disk. CI runs it as a release gate.

If ``python -m build`` is not importable in the current environment the test
skips cleanly so contributors without it can still run ``pytest``.
"""

from __future__ import annotations

import asyncio
import configparser
import json
import os
import subprocess
import sys
import tomllib
import zipfile
from pathlib import Path

import pytest

# Anchor the project root from this file so the test is location-independent.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

EXPECTED_CANONICAL_TOPLEVEL = {"attestix"}

# These are the deprecated compatibility deprecation shims. They exist on purpose
# so pre-rc.2 user code keeps working; this test pins the exact set so any
# future packaging change that accidentally ships extra top-level dirs fails
# loud.
EXPECTED_SHIM_TOPLEVEL = {
    "api",
    "audit",
    "auth",
    "blockchain",
    "cli.py",
    "config.py",
    "errors.py",
    "idempotency",
    "main.py",
    "services",
    "signing",
    "storage",
    "tenancy",
    "tools",
}


def _have_build() -> bool:
    try:
        import build  # noqa: F401
    except ImportError:
        return False
    return True


pytestmark = pytest.mark.skipif(
    os.environ.get("ATTESTIX_RUN_INSTALL_SMOKE") != "1",
    reason=(
        "Install smoke test is opt-in; set ATTESTIX_RUN_INSTALL_SMOKE=1 to "
        "rebuild the wheel and install it into a throwaway venv."
    ),
)


@pytest.mark.skipif(not _have_build(), reason="python -m build is not installed")
def test_wheel_layout_and_install_smoke(tmp_path):
    """The wheel installs cleanly and exposes the v0.4.0-rc.2 packaging contract."""
    # 1) Build a wheel from the working tree.
    prebuilt = os.environ.get("ATTESTIX_RELEASE_WHEEL")
    if prebuilt:
        wheel = Path(prebuilt).resolve()
        assert wheel.is_file(), "the validated release wheel must exist"
    else:
        dist = tmp_path / "dist"
        dist.mkdir()
        subprocess.run(
            [sys.executable, "-m", "build", "--no-isolation", "--wheel", "--outdir", str(dist)],
            cwd=str(PROJECT_ROOT),
            check=True,
        )
        wheels = sorted(dist.glob("attestix-*.whl"))
        assert len(wheels) == 1, "expected one newly built wheel"
        wheel = wheels[0]

    # 2) Inspect the wheel's top-level entries.
    with zipfile.ZipFile(wheel) as z:
        names = z.namelist()
    tops = {n.split("/")[0] for n in names}
    # Strip the dist-info dir (versioned name).
    dist_info_dirs = {t for t in tops if t.endswith(".dist-info")}
    tops -= dist_info_dirs
    expected = EXPECTED_CANONICAL_TOPLEVEL | EXPECTED_SHIM_TOPLEVEL
    unexpected = tops - expected
    missing = expected - tops
    assert not unexpected, (
        "wheel ships unexpected top-level entries (namespace pollution): "
        f"{sorted(unexpected)}"
    )
    assert not missing, (
        "wheel is missing expected top-level entries: "
        f"{sorted(missing)}"
    )

    # 3) Spin up a throwaway venv and install the wheel.
    venv = tmp_path / "venv"
    subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True)
    bin_dir = "Scripts" if os.name == "nt" else "bin"
    py = str(venv / bin_dir / ("python.exe" if os.name == "nt" else "python"))
    subprocess.run([py, "-m", "pip", "install", "--quiet", str(wheel)], check=True)

    # 4) Canonical imports work (the v0.4.0-rc.2 contract).
    canonical_check = (
        "import attestix\n"
        "from importlib.metadata import version\n"
        f"assert attestix.__version__ == version('attestix') == {tomllib.loads((PROJECT_ROOT / 'pyproject.toml').read_text())['project']['version']!r}\n"
        "from attestix.services.identity_service import IdentityService\n"
        "from attestix.signing.inprocess_signer import InProcessSigner\n"
        "from attestix.auth.crypto import sign_json_payload, generate_ed25519_keypair, sign_message, verify_signature\n"
        "key, public = generate_ed25519_keypair()\n"
        "signature = sign_message(key, b'release-smoke')\n"
        "assert verify_signature(public, signature, b'release-smoke')\n"
        "from attestix.storage.repository import Repository\n"
        "from attestix.audit.events import AuditEvent\n"
        "from attestix.tenancy import TenantContext\n"
        "from attestix.idempotency.store import IdempotencyStore\n"
        "print('OK')\n"
    )
    proc = subprocess.run(
        [py, "-I", "-c", canonical_check],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, (
        f"canonical imports failed: stdout={proc.stdout!r} stderr={proc.stderr!r}"
    )
    assert proc.stdout.strip() == "OK"

    # 5) Legacy flat imports emit DeprecationWarning (the shim contract).
    deprecation_check = (
        "import warnings\n"
        "with warnings.catch_warnings(record=True) as caught:\n"
        "    warnings.simplefilter('always')\n"
        "    from services.identity_service import IdentityService  # noqa: F401\n"
        "import json, sys\n"
        "msgs = [str(w.message) for w in caught "
        "if issubclass(w.category, DeprecationWarning)]\n"
        "print(json.dumps(msgs))\n"
    )
    proc = subprocess.run(
        [py, "-I", "-c", deprecation_check],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, (
        f"legacy import smoke failed: stdout={proc.stdout!r} stderr={proc.stderr!r}"
    )
    msgs = json.loads(proc.stdout.strip())
    assert any("attestix.services" in m for m in msgs), (
        f"legacy `from services...` import did not emit the canonical-namespace "
        f"DeprecationWarning. Captured: {msgs}"
    )

    # Exercise the candidate registry launch from its installed wheel, outside
    # the checkout. This source manifest is staged for the next release only.
    manifest = json.loads((PROJECT_ROOT / "server.json").read_text(encoding="utf-8"))
    package = next(item for item in manifest["packages"] if item["registryType"] == "pypi")
    with zipfile.ZipFile(wheel) as archive:
        entrypoints = configparser.ConfigParser()
        entrypoints.read_string(archive.read(next(
            name for name in archive.namelist() if name.endswith(".dist-info/entry_points.txt")
        )).decode("utf-8"))
    binary = package["identifier"]
    assert entrypoints["console_scripts"][binary] == "attestix.cli:cli"
    fixed_arguments = package["packageArguments"]
    assert fixed_arguments == [{"type": "positional", "value": "mcp"}]
    console = str(venv / bin_dir / (f"{binary}.exe" if os.name == "nt" else binary))
    environment = {
        name: os.environ[name]
        for name in ("SystemRoot", "PATH", "USERPROFILE", "LOCALAPPDATA", "TEMP", "TMP", "APPDATA")
        if name in os.environ
    }
    data_dir = tmp_path / "mcp-data"
    environment.update(
        ATTESTIX_DATA_DIR=str(data_dir), PYTHONDONTWRITEBYTECODE="1",
        OTEL_SDK_DISABLED="true", DO_NOT_TRACK="1",
    )

    async def initialize_candidate_console(command, arguments):
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        parse_errors = []

        async def message_handler(message):
            if isinstance(message, Exception):
                parse_errors.append(message)

        parameters = StdioServerParameters(
            command=command, args=arguments,
            env=environment, cwd=tmp_path,
        )
        async with asyncio.timeout(60):
            async with stdio_client(parameters) as (reader, writer):
                async with ClientSession(reader, writer, message_handler=message_handler) as session:
                    initialized = await session.initialize()
                    tools = await session.list_tools()
                    assert initialized.serverInfo.name == "attestix"
                    assert tools.tools
        assert not parse_errors, "MCP stdout contained malformed protocol frames"

    asyncio.run(initialize_candidate_console(console, [argument["value"] for argument in fixed_arguments]))
    # SDK initialization alone also succeeds after malformed stdout; prove this
    # smoke guard rejects that regression using the same installed candidate.
    noisy_fixture = (
        "import sys\n"
        "sys.stdout.write('synthetic malformed frame\\n'); sys.stdout.flush()\n"
        "from attestix.cli import cli\n"
        "cli(args=['mcp'], prog_name='attestix')\n"
    )
    with pytest.raises(AssertionError, match="MCP stdout contained malformed protocol frames"):
        asyncio.run(initialize_candidate_console(py, ["-I", "-c", noisy_fixture]))
    assert not (data_dir / ".signing_key.json").exists()
