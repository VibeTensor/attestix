"""Regression test for v0.4.0rc2 P0 #1: integrations subpackage missing from wheel.

The rc.2 validation (paper/internal/v0.4.0rc2-rc-validation-isolated-2026-05-28.md
P0-A) caught that the published wheel shipped no ``attestix/integrations/``
directory at all, so the indie-dev quickstart's
``from attestix.integrations.langchain import AttestixCallback`` raised
``ModuleNotFoundError`` on every fresh install. v0.4.0rc3 ships the
integrations subpackage; this test pins that contract so the regression
cannot recur silently — if a future packaging change drops the
``attestix.integrations.*`` entry from ``[tool.setuptools] packages`` the
test fails loud.

Skipped when ``python -m build`` is not importable so contributors without
the build extra can still run ``pytest``.
"""

from __future__ import annotations

import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]

REQUIRED_INTEGRATIONS = {
    "attestix/integrations/__init__.py",
    "attestix/integrations/langchain/__init__.py",
    "attestix/integrations/langchain/callback.py",
    "attestix/integrations/openai_agents/__init__.py",
    "attestix/integrations/openai_agents/hook.py",
    "attestix/integrations/crewai/__init__.py",
    "attestix/integrations/crewai/adapter.py",
}


def _have_build() -> bool:
    try:
        import build  # noqa: F401
    except ImportError:
        return False
    return True


@pytest.mark.skipif(not _have_build(), reason="python -m build is not installed")
def test_wheel_ships_attestix_integrations_package(tmp_path):
    """The built wheel must contain every `attestix.integrations.*` module.

    This is the structural assertion that the rc.2 RC validation harness
    would have caught: walk the wheel zip namelist and require the
    integration subpackage files to be present. We do NOT install the wheel
    here — that's covered by tests/install/test_pip_install_smoke.py.
    """
    dist = tmp_path / "dist"
    dist.mkdir()
    subprocess.run(
        [sys.executable, "-m", "build", "--wheel", "--outdir", str(dist)],
        cwd=str(PROJECT_ROOT),
        check=True,
    )
    wheels = sorted(dist.glob("attestix-*.whl"))
    assert wheels, "expected `python -m build --wheel` to produce a wheel"
    wheel = wheels[-1]

    with zipfile.ZipFile(wheel) as z:
        names = set(z.namelist())

    missing = REQUIRED_INTEGRATIONS - names
    assert not missing, (
        "wheel is missing required attestix.integrations.* modules — "
        f"this is the P0 #1 regression from v0.4.0rc2 RC validation. "
        f"Missing: {sorted(missing)}. Wheel name: {wheel.name}."
    )
