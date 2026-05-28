"""CLI smoke tests for ``attestix import`` (M6 portability bundle ingest).

These tests drive the Click command through :class:`CliRunner` against a
tmp-redirected storage directory (see the autouse ``tmp_attestix`` fixture in
``tests/conftest.py``). Each invocation is hermetic: no real ``~/.attestix``
data is touched.

Cases:

* ``--verify-only`` on a valid bundle: exit 0 + integrity report.
* ``--verify-only`` on a tampered bundle: non-zero exit + error printed.
* Default on a fresh install: writes 9 rows and prints next-step hints.
* Default on a non-empty store: refuses without ``--force``.
* ``--force`` on a non-empty store: proceeds.
"""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from attestix.cli import cli
from attestix.storage import FileRepository
from tests.fixtures.bundles.generate_sample_bundle import (
    WORKSPACE_SLUG,
    write_bundle,
)


FIXTURE_TENANT = WORKSPACE_SLUG


@pytest.fixture
def good_bundle_path(tmp_path):
    out = tmp_path / "sample.tar.gz"
    write_bundle(out)
    return out


@pytest.fixture
def tampered_bundle_path(tmp_path):
    out = tmp_path / "bad.tar.gz"
    write_bundle(out, tamper_table_body="identities")
    return out


def _run(args):
    # Click 8.3 removed the `mix_stderr` kwarg; with the new default stderr is
    # captured separately on `result.stderr` (Click 8.2+ behaviour). Older
    # Click versions still accept the kwarg, so we probe.
    try:
        runner = CliRunner(mix_stderr=False)  # Click <8.3
    except TypeError:
        runner = CliRunner()
    return runner.invoke(cli, args, catch_exceptions=False)


def _combined_output(result) -> str:
    """Return stdout + stderr as a single string regardless of Click version."""
    out = result.output or ""
    try:
        err = result.stderr or ""
    except (AttributeError, ValueError):  # pragma: no cover — stderr unavailable
        err = ""
    return out + err


def test_verify_only_on_good_bundle_exits_zero(good_bundle_path):
    result = _run(["import", str(good_bundle_path), "--verify-only"])
    assert result.exit_code == 0, result.output
    assert "Verify-only mode" in result.output
    assert "VERIFIED" in result.output


def test_verify_only_on_tampered_bundle_exits_non_zero(tampered_bundle_path):
    result = _run(["import", str(tampered_bundle_path), "--verify-only"])
    assert result.exit_code != 0
    # The error string lands on stderr via the helper; CliRunner captures it.
    combined = _combined_output(result)
    assert "verification failed" in combined or "sha256 mismatch" in combined


def test_default_writes_when_empty(good_bundle_path):
    result = _run(["import", str(good_bundle_path)])
    assert result.exit_code == 0, _combined_output(result)
    assert "Import complete" in result.output

    # Rows landed under the bundle's workspace slug.
    repo = FileRepository()
    assert (
        len(repo.list("identities", tenant_id=FIXTURE_TENANT, id_field="agent_id"))
        == 2
    )


def test_default_refuses_on_non_empty_store(good_bundle_path):
    # Seed the FileRepository so the guard trips.
    repo = FileRepository()
    repo.create(
        "identities",
        {"agent_id": "attestix:preexisting", "display_name": "Pre-existing"},
        tenant_id=FIXTURE_TENANT,
        id_field="agent_id",
    )
    result = _run(["import", str(good_bundle_path)])
    assert result.exit_code != 0
    combined = _combined_output(result)
    assert "not empty" in combined
    assert "--force" in combined


def test_force_proceeds_on_non_empty_store(good_bundle_path):
    repo = FileRepository()
    repo.create(
        "identities",
        {"agent_id": "attestix:preexisting", "display_name": "Pre-existing"},
        tenant_id=FIXTURE_TENANT,
        id_field="agent_id",
    )
    result = _run(["import", str(good_bundle_path), "--force"])
    assert result.exit_code == 0, _combined_output(result)
    assert "Import complete" in result.output
    rows = repo.list("identities", tenant_id=FIXTURE_TENANT, id_field="agent_id")
    assert len(rows) == 3


def test_workspace_override_lets_user_pick_tenant(good_bundle_path):
    result = _run(
        ["import", str(good_bundle_path), "--workspace", "acme-imports"]
    )
    assert result.exit_code == 0, _combined_output(result)
    repo = FileRepository()
    # Rows landed under the user-chosen tenant.
    assert (
        len(repo.list("identities", tenant_id="acme-imports", id_field="agent_id"))
        == 2
    )
    # And NOT under the original workspace slug.
    assert (
        repo.list("identities", tenant_id=FIXTURE_TENANT, id_field="agent_id") == []
    )


def test_import_help_listed_in_main():
    result = _run(["--help"])
    assert result.exit_code == 0
    assert "import" in result.output
