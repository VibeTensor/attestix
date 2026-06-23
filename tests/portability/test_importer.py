"""End-to-end round-trip test for the OSS portability importer.

Loads the committed sample bundle, drives :class:`Importer` against an isolated
storage directory (every test redirects ``DATA_DIR`` via ``conftest.py``), and
asserts that the resulting OSS state matches the bundle's row counts and key
content. Also exercises:

* the audit-chain reconciliation path (a chain-tampered bundle must abort
  before any row commits);
* tenant scoping on the OSS Repository — rows written under the bundle's
  workspace slug are NOT visible under any other tenant id;
* the "skip cloud-only tables" path — rows in ``key_references`` /
  ``memberships`` etc. never reach the Repository.
"""

from __future__ import annotations

import pytest

from attestix.portability import (
    BundleError,
    Importer,
    ImportResult,
    read_bundle,
)
from attestix.portability.bundle_reader import Bundle
from attestix.portability.importer import ImportError as BundleImportError
from attestix.storage import FileRepository
from attestix.storage.repository import DEFAULT_TENANT

from tests.fixtures.bundles.generate_sample_bundle import (
    WORKSPACE_ID,
    WORKSPACE_SLUG,
    write_bundle,
)


FIXTURE_TENANT = WORKSPACE_SLUG  # "fixture-tenant"


@pytest.fixture
def fresh_bundle(tmp_path):
    """Write a fresh sample bundle into tmp_path and return its parsed form."""
    out = tmp_path / "sample.tar.gz"
    write_bundle(out)
    return read_bundle(out)


def test_round_trip_writes_every_expected_collection(fresh_bundle: Bundle):
    importer = Importer(tenant_id=FIXTURE_TENANT)
    assert importer.local_data_is_empty()

    result = importer.run(fresh_bundle)

    # The bundle ships 2 identities, 1 credential, 1 compliance profile,
    # 1 conformity assessment, 3 audit events, 1 anchor (9 rows total going
    # to OSS-writable collections — cloud-only rows are skipped).
    assert result.chain_verified is True
    assert result.target_tenant == FIXTURE_TENANT
    assert result.total_written == 9

    # Verify on the Repository.
    repo = FileRepository()
    identities = repo.list(
        "identities", tenant_id=FIXTURE_TENANT, id_field="agent_id"
    )
    assert len(identities) == 2
    assert {i["agent_id"] for i in identities} == {
        "attestix:fixture0000000001",
        "attestix:fixture0000000002",
    }

    credentials = repo.list("credentials", tenant_id=FIXTURE_TENANT, id_field="id")
    assert len(credentials) == 1
    assert credentials[0]["id"] == "urn:uuid:cred-fixture-0001"

    compliance = repo.list(
        "compliance", tenant_id=FIXTURE_TENANT, id_field="profile_id"
    )
    assert len(compliance) == 1
    assert compliance[0]["profile_id"] == "comp:fixture00001"

    # The audit chain persists under the chain tenant the cloud minted it under
    # (the workspace UUID), decoupled from the storage tenant (the slug). This
    # is the audit B8 fix: a cloud chain minted under the UUID stays verifiable.
    audit = repo.list("audit", tenant_id=WORKSPACE_ID, id_field="event_id")
    assert len(audit) == 3
    # Chain field shape is preserved.
    assert all("chain_hash" in row and "prev_hash" in row for row in audit)
    # Decoupling: the audit chain is NOT stored under the storage/slug tenant.
    assert repo.list("audit", tenant_id=FIXTURE_TENANT, id_field="event_id") == []

    anchors = repo.list("anchors", tenant_id=FIXTURE_TENANT, id_field="anchor_id")
    assert len(anchors) == 1
    assert anchors[0]["anchor_id"] == "anchor:fixture000001"


def test_chain_verification_on_committed_audit_events(fresh_bundle: Bundle):
    """The audit chain in the bundle must be re-verifiable through the OSS helper."""
    importer = Importer(tenant_id=FIXTURE_TENANT)
    importer.run(fresh_bundle)

    repo = FileRepository()
    rows = repo.list("audit", tenant_id=WORKSPACE_ID, id_field="event_id")
    # Order is the bundle's insert order — strip Repository-injected fields.
    from attestix.audit.events import verify_chain

    chain_rows = [
        {k: v for k, v in r.items() if not k.startswith("_") and k != "tenant_id"}
        for r in rows
    ]
    # Add tenant_id back from the row (the FileRepository tags every record).
    for src, dst in zip(rows, chain_rows):
        dst["tenant_id"] = src["tenant_id"]
    assert verify_chain(chain_rows)


def test_verify_only_writes_nothing(fresh_bundle: Bundle):
    importer = Importer(tenant_id=FIXTURE_TENANT)
    result = importer.run(fresh_bundle, verify_only=True)
    assert isinstance(result, ImportResult)
    # No rows landed in the repository despite the verifier walking everything.
    assert importer.local_data_is_empty()


def test_cross_tenant_isolation_after_import(fresh_bundle: Bundle):
    """Rows imported under tenant=fixture-tenant must not leak to other tenants."""
    importer = Importer(tenant_id=FIXTURE_TENANT)
    importer.run(fresh_bundle)

    repo = FileRepository()
    # The "default" tenant (and any other tenant string) sees nothing.
    for other in (DEFAULT_TENANT, "globex", "acme"):
        if other == FIXTURE_TENANT:
            continue
        assert repo.list("identities", tenant_id=other, id_field="agent_id") == []
        assert repo.list("audit", tenant_id=other, id_field="event_id") == []
        assert repo.list("credentials", tenant_id=other, id_field="id") == []


def test_force_required_when_local_data_present(fresh_bundle: Bundle):
    # Pre-populate one identity so the importer sees non-empty local data.
    repo = FileRepository()
    repo.create(
        "identities",
        {"agent_id": "attestix:preexisting", "display_name": "Pre-existing"},
        tenant_id=FIXTURE_TENANT,
        id_field="agent_id",
    )
    importer = Importer(tenant_id=FIXTURE_TENANT)
    assert not importer.local_data_is_empty()
    # The Importer itself does not refuse — the CLI guard does. But the
    # summary helper must report the row count for the guard.
    assert importer.local_data_summary()["identities"] == 1
    # With force=True the import proceeds and the count includes the new rows.
    result = importer.run(fresh_bundle, force=True)
    assert result.total_written == 9
    after = repo.list("identities", tenant_id=FIXTURE_TENANT, id_field="agent_id")
    assert len(after) == 3  # 1 pre-existing + 2 imported


def test_schema_too_new_aborts(tmp_path):
    out = tmp_path / "too-new.tar.gz"
    write_bundle(out, bump_db_migration="9999")
    bundle = read_bundle(out)
    importer = Importer(tenant_id=FIXTURE_TENANT)
    # BundleSchemaTooNewError IS-A BundleError — both the bundle-reader and the
    # importer module raise into the same base error type, so callers can
    # catch BundleError to handle every portability problem.
    with pytest.raises(BundleError) as exc:
        importer.run(bundle)
    assert "9999" in str(exc.value)


def test_corrupt_bundle_aborts_before_any_write(tmp_path):
    out = tmp_path / "bad-table.tar.gz"
    write_bundle(out, tamper_table_body="identities")
    bundle = read_bundle(out)
    importer = Importer(tenant_id=FIXTURE_TENANT)
    with pytest.raises(BundleImportError) as exc:
        importer.run(bundle)
    assert "verification failed" in str(exc.value)
    # And nothing landed.
    repo = FileRepository()
    assert repo.list("identities", tenant_id=FIXTURE_TENANT, id_field="agent_id") == []


def test_cloud_only_tables_are_skipped(fresh_bundle: Bundle):
    importer = Importer(tenant_id=FIXTURE_TENANT)
    result = importer.run(fresh_bundle)
    # No OSS collection picked up the cloud-only tables — those summaries have
    # oss_collection=None.
    cloud_only = [t for t in result.tables if t.oss_collection is None]
    assert {t.name for t in cloud_only} >= {
        "memberships",
        "subscriptions",
        "team_invites",
        "key_references",
        "credential_schemas",
        "agent_dependencies",
        "webhook_endpoints",
    }
    for t in cloud_only:
        # rows_written stays 0 for cloud-only tables.
        assert t.rows_written == 0


def test_conformity_assessment_lands_in_compliance_document(fresh_bundle: Bundle):
    importer = Importer(tenant_id=FIXTURE_TENANT)
    importer.run(fresh_bundle)
    repo = FileRepository()
    # The FileRepository document API is the public seam services use.
    doc = repo.load_document("compliance")
    assert doc["assessments"], "imported assessment did not land in compliance.assessments"
    assert doc["assessments"][0]["assessment_id"] == "assess:fixture00001"
