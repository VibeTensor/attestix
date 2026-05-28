"""CLI smoke tests for ``attestix export`` (OSS portability bundle write).

Drives the Click command through :class:`CliRunner` against the tmp-redirected
storage directory (``tmp_attestix`` autouse fixture in ``tests/conftest.py``).

Cases:

* Default invocation on an empty store writes a valid bundle and exits 0.
* Refusing to overwrite an existing target without ``--force``.
* Round-trip: ``attestix export`` → ``attestix import --verify-only`` exits 0.
"""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from attestix.cli import cli
from attestix.portability import read_bundle
from attestix.services.identity_service import IdentityService


def _run(args):
    try:
        runner = CliRunner(mix_stderr=False)  # Click <8.3
    except TypeError:
        runner = CliRunner()
    return runner.invoke(cli, args, catch_exceptions=False)


def _combined_output(result) -> str:
    out = result.output or ""
    try:
        err = result.stderr or ""
    except (AttributeError, ValueError):
        err = ""
    return out + err


def test_export_writes_file_and_exits_zero(tmp_path):
    out = tmp_path / "export.tar.gz"
    result = _run(["export", str(out)])
    assert result.exit_code == 0, _combined_output(result)
    assert out.exists()
    assert out.stat().st_size > 0
    # The success line carries the manifest sha.
    assert "manifest_sha256=" in result.output


def test_export_refuses_overwrite_without_force(tmp_path):
    out = tmp_path / "export.tar.gz"
    out.write_bytes(b"already here")

    result = _run(["export", str(out)])
    assert result.exit_code != 0
    combined = _combined_output(result)
    assert "--force" in combined
    # File body was not touched.
    assert out.read_bytes() == b"already here"


def test_export_force_overwrites_existing_file(tmp_path):
    out = tmp_path / "export.tar.gz"
    out.write_bytes(b"already here")

    result = _run(["export", str(out), "--force"])
    assert result.exit_code == 0, _combined_output(result)
    # The new bytes are a gzipped tar, not the placeholder.
    assert out.read_bytes() != b"already here"
    assert out.read_bytes()[:2] == b"\x1f\x8b"  # gzip magic


def test_export_then_verify_only_import_round_trip(tmp_path):
    # Seed at least one identity so the bundle carries real data.
    svc = IdentityService()
    svc.create_identity(
        display_name="CLI Round-Trip",
        source_protocol="manual",
        description="Round-trip seed",
    )

    out = tmp_path / "round-trip.tar.gz"
    export_result = _run(["export", str(out)])
    assert export_result.exit_code == 0, _combined_output(export_result)

    # The bundle's identities table is non-empty.
    bundle = read_bundle(out)
    assert bundle.tables["identities"].row_count >= 1

    # Now run `attestix import --verify-only` against the bundle we just wrote.
    import_result = _run(["import", str(out), "--verify-only"])
    assert import_result.exit_code == 0, _combined_output(import_result)
    assert "Verify-only mode" in import_result.output


def test_export_help_listed_in_main():
    result = _run(["--help"])
    assert result.exit_code == 0
    assert "export" in result.output


def test_no_pretty_suppresses_per_table_progress(tmp_path):
    out = tmp_path / "quiet.tar.gz"
    result = _run(["export", str(out), "--no-pretty"])
    assert result.exit_code == 0, _combined_output(result)
    # Without --no-pretty we'd see "Tables" header; with --no-pretty we don't.
    assert "Tables" not in result.output
    # But the final wrote-line is still emitted.
    assert "manifest_sha256=" in result.output
