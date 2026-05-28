"""Regression test for v0.4.0rc2 P0 #2: fastapi/uvicorn not declared, no [api] extra.

The rc.2 validation (paper/internal/v0.4.0rc2-rc-validation-isolated-2026-05-28.md
P0-C) caught that ``attestix.api.main`` does ``from fastapi import …`` at
import time but fastapi was neither a runtime dep nor an opt-in extra.
v0.4.0rc3 declares an ``[api]`` extra. This test verifies both halves of
the contract:

1. Importing ``attestix.api.main`` without fastapi installed raises a
   clear ``ImportError`` that names the ``[api]`` extra — not a confusing
   ``ModuleNotFoundError: No module named 'fastapi'``.
2. The wheel's METADATA declares the ``api`` extra in ``Provides-Extra``
   so ``pip install 'attestix[api]'`` resolves something real.
"""

from __future__ import annotations

import importlib
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _have_build() -> bool:
    try:
        import build  # noqa: F401
    except ImportError:
        return False
    return True


def _have_fastapi() -> bool:
    try:
        import fastapi  # noqa: F401
    except ImportError:
        return False
    return True


@pytest.mark.skipif(
    _have_fastapi(),
    reason=(
        "fastapi is installed in this env — the missing-extra ImportError "
        "contract can only be exercised when fastapi is absent. The dev "
        "venv intentionally does not pull in fastapi so this assertion "
        "runs in CI."
    ),
)
def test_attestix_api_main_raises_clear_error_without_fastapi():
    """Without fastapi installed, importing ``attestix.api.main`` must hint at the extra."""
    # Make sure no cached import survives from another test.
    sys.modules.pop("attestix.api.main", None)
    with pytest.raises(ImportError) as exc:
        importlib.import_module("attestix.api.main")
    msg = str(exc.value)
    assert "[api]" in msg, (
        "ImportError must mention the `attestix[api]` extra so callers know "
        f"how to fix it. Got: {msg!r}"
    )
    assert "fastapi" in msg.lower() or "uvicorn" in msg.lower(), (
        f"ImportError should mention fastapi or uvicorn. Got: {msg!r}"
    )


@pytest.mark.skipif(not _have_build(), reason="python -m build is not installed")
def test_wheel_metadata_declares_api_extra(tmp_path):
    """The built wheel must declare ``Provides-Extra: api``."""
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
        metadata_paths = [n for n in z.namelist() if n.endswith(".dist-info/METADATA")]
        assert metadata_paths, "wheel has no METADATA file"
        metadata = z.read(metadata_paths[0]).decode("utf-8")

    extras = sorted({
        line.split(":", 1)[1].strip().split(";")[0].strip()
        for line in metadata.splitlines()
        if line.startswith("Provides-Extra:")
    })

    for required in ("api", "langchain", "crewai", "openai-agents"):
        assert required in extras, (
            f"wheel METADATA is missing `Provides-Extra: {required}`. "
            f"Present extras: {extras}. This is the v0.4.0rc2 P0 #2 / P1 #7 "
            f"regression — pip would silently install nothing for "
            f"`attestix[{required}]`."
        )

    # The Requires-Dist for the api extra must mention fastapi.
    api_requires = [
        line for line in metadata.splitlines()
        if line.startswith("Requires-Dist:") and 'extra == "api"' in line
    ]
    assert any("fastapi" in r for r in api_requires), (
        f"`[api]` extra must require fastapi. Got: {api_requires}"
    )
    assert any("uvicorn" in r for r in api_requires), (
        f"`[api]` extra must require uvicorn. Got: {api_requires}"
    )
