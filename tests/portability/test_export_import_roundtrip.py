"""Round-trip test for the OSS portability exporter ↔ importer pair.

The :func:`attestix.portability.bundle_writer.write_bundle` writer is the
inverse of :class:`attestix.portability.importer.Importer`. These tests:

* Seed a fresh tmp-redirected OSS instance with identities + a credential +
  several audit events + a compliance profile + an anchor row.
* Export the seeded state to a tarball on disk.
* Run the existing :class:`Importer` against the produced bundle on a fresh
  empty OSS instance (driven via the ``tmp_attestix`` fixture which already
  redirects storage paths per-test).
* Assert that row counts, audit-chain re-verification, and manifest sha all
  round-trip cleanly.
* Cover the empty-store, ``--workspace`` filter, and ``--no-include-anchors``
  paths.

The round-trip is the strongest guarantee the constitution makes for OSS
portability: a bundle produced by OSS must be importable by OSS, and the
imported state must re-export to a verifiable bundle whose sha matches a
fresh recomputation.
"""

from __future__ import annotations

import hashlib

import pytest

from attestix.audit.events import verify_chain
from attestix.audit import AuditEventEmitter
from attestix.auth.crypto import canonicalize_json
from attestix.portability import (
    Bundle,
    Importer,
    read_bundle,
    write_bundle,
)
from attestix.portability.bundle_writer import EXPORT_PLAN
from attestix.services.credential_service import CredentialService
from attestix.services.identity_service import IdentityService
from attestix.services.compliance_service import ComplianceService
from attestix.storage import FileRepository
from attestix.storage.repository import DEFAULT_TENANT


# ---------------------------------------------------------------------------
# Seed helpers
# ---------------------------------------------------------------------------


def _seed_oss_data(*, tenant: str = DEFAULT_TENANT) -> dict:
    """Populate a fresh OSS instance with a representative mix of rows.

    Returns a dict describing what was seeded so assertions can re-verify.
    """
    identity_svc = IdentityService(tenant_id=tenant)
    cred_svc = CredentialService(tenant_id=tenant)
    compliance_svc = ComplianceService(tenant_id=tenant)

    a1 = identity_svc.create_identity(
        display_name="Alpha Agent",
        source_protocol="manual",
        description="Round-trip seed agent 1",
    )
    a2 = identity_svc.create_identity(
        display_name="Beta Agent",
        source_protocol="manual",
        description="Round-trip seed agent 2",
    )

    cred = cred_svc.issue_credential(
        agent_id=a1["agent_id"],
        credential_type="AgentIdentityCredential",
        issuer_name="VibeTensor Fixture",
        claims={"role": "round-trip"},
    )

    profile = compliance_svc.create_compliance_profile(
        agent_id=a1["agent_id"],
        risk_category="limited",
        provider_name="Round-Trip Provider",
        intended_purpose="Test the OSS exporter ↔ importer pair",
    )

    # Seed an anchor row directly through the FileRepository — the blockchain
    # service is network-dependent and we want a hermetic test.
    repo = FileRepository()
    repo.create(
        "anchors",
        {
            "anchor_id": "anchor:roundtrip000001",
            "artifact_type": "identity",
            "artifact_id": a1["agent_id"],
            "artifact_hash": "ab" * 32,
            "network": "sepolia",
            "chain_id": 84532,
            "tx_hash": "0x" + "cd" * 32,
            "attestation_uid": "0x" + "ef" * 32,
            "schema_uid": "0x" + "12" * 32,
            "attester": "0x" + "34" * 20,
            "block_number": 1,
            "gas_used": 100000,
            "explorer_url": "https://sepolia.basescan.org/tx/0xcd",
            "anchored_at": "2026-05-28T12:00:00Z",
            "issuer_did": "did:key:fixture",
        },
        tenant_id=tenant,
        id_field="anchor_id",
    )

    # Audit events: the service-layer emits some during create above. We add
    # one more via the public emitter API so the chain is non-trivial.
    emitter = AuditEventEmitter()
    emitter.emit(
        action="identity.audit_roundtrip",
        target_id=a1["agent_id"],
        target_collection="identities",
        actor="user:roundtrip@test",
        tenant_id=tenant,
        after={"agent_id": a1["agent_id"]},
    )

    return {
        "tenant": tenant,
        "agent_ids": [a1["agent_id"], a2["agent_id"]],
        "credential_id": cred["id"],
        "profile_id": profile["profile_id"],
        "anchor_id": "anchor:roundtrip000001",
    }


def _count_audit_rows(tenant: str = DEFAULT_TENANT) -> int:
    repo = FileRepository()
    return len(repo.list("audit", tenant_id=tenant, id_field="event_id"))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_empty_store_export_produces_valid_zero_row_bundle(tmp_path):
    out = tmp_path / "empty.tar.gz"
    result = write_bundle(out)
    assert out.exists()
    assert result.bytes > 0

    bundle = read_bundle(out)
    ok, problems = bundle.verify()
    assert ok, problems

    # Every table in the EXPORT_PLAN appears in the bundle (even if zero rows).
    for spec in EXPORT_PLAN:
        assert spec.name in bundle.tables
        assert bundle.tables[spec.name].row_count == 0
        assert bundle.tables[spec.name].bytes == 0

    # Manifest carries the OSS exporter signature.
    assert bundle.manifest["exported_by"]["user_id"] == "local"
    assert bundle.workspace.get("region") == "local"
    assert bundle.workspace.get("data_residency") == "self-host"
    assert bundle.db_migration_max == "0010"


def test_seeded_export_round_trips_through_importer(tmp_path):
    """Export seeded OSS state, re-import it on a *fresh* OSS instance, assert equivalence.

    The ``tmp_attestix`` autouse fixture redirects storage paths per-test —
    inside this test we first seed, then export to a tmp file, then *reset*
    the FileRepository state by clearing the documents (the fixture's tmp_path
    persists for the duration of the test), then import and re-verify.
    """
    seeded = _seed_oss_data()
    audit_count_pre = _count_audit_rows()

    out = tmp_path / "seeded.tar.gz"
    result = write_bundle(out)

    # The bundle should carry our seeded rows.
    bundle = read_bundle(out)
    ok, problems = bundle.verify()
    assert ok, problems

    assert bundle.tables["identities"].row_count == 2
    assert bundle.tables["credentials"].row_count == 1
    assert bundle.tables["compliance_profiles"].row_count == 1
    assert bundle.tables["anchors"].row_count == 1
    # Audit count: equal to whatever the OSS emitter+services accumulated.
    assert bundle.tables["audit_events"].row_count == audit_count_pre

    # Wipe OSS state (re-write empty documents through the same Repository the
    # importer uses). Then import the bundle and confirm every row reappears.
    repo = FileRepository()
    repo.save_document("identities", {"agents": []})
    repo.save_document("credentials", {"credentials": []})
    repo.save_document(
        "compliance",
        {"profiles": [], "assessments": [], "declarations": []},
    )
    repo.save_document("anchors", {"anchors": []})
    repo.save_document("audit", {"events": []})

    # Re-parse the bundle so the in-memory payload is fresh.
    bundle = read_bundle(out)
    importer = Importer(tenant_id=bundle.workspace.get("slug", DEFAULT_TENANT))
    assert importer.local_data_is_empty()
    import_result = importer.run(bundle)
    assert import_result.chain_verified is True

    # Round-trip equivalence.
    workspace_tenant = bundle.workspace.get("slug")
    assert (
        len(repo.list("identities", tenant_id=workspace_tenant, id_field="agent_id"))
        == 2
    )
    assert (
        len(repo.list("credentials", tenant_id=workspace_tenant, id_field="id"))
        == 1
    )
    assert (
        len(repo.list("compliance", tenant_id=workspace_tenant, id_field="profile_id"))
        == 1
    )
    assert (
        len(repo.list("anchors", tenant_id=workspace_tenant, id_field="anchor_id"))
        == 1
    )

    # Re-verify the audit chain end-to-end through the OSS helper.
    audit_rows = repo.list(
        "audit", tenant_id=workspace_tenant, id_field="event_id"
    )
    chain_rows = [
        {
            k: v
            for k, v in r.items()
            if not k.startswith("_")
        }
        for r in audit_rows
    ]
    assert verify_chain(chain_rows)


def test_deterministic_re_export_is_byte_identical(tmp_path):
    """Two consecutive exports of identical OSS state must produce identical bytes."""
    _seed_oss_data()

    out_a = tmp_path / "a.tar.gz"
    out_b = tmp_path / "b.tar.gz"

    # Pin the exporter clock so the manifest timestamp is identical across runs.
    from datetime import datetime, timezone

    fixed_now = datetime(2026, 5, 28, 12, 0, 0, tzinfo=timezone.utc)
    result_a = write_bundle(out_a, now=fixed_now)
    result_b = write_bundle(out_b, now=fixed_now)

    bytes_a = out_a.read_bytes()
    bytes_b = out_b.read_bytes()
    assert hashlib.sha256(bytes_a).hexdigest() == hashlib.sha256(bytes_b).hexdigest()
    assert bytes_a == bytes_b
    assert result_a.manifest_sha256 == result_b.manifest_sha256


def test_workspace_filter_excludes_other_tenants(tmp_path):
    """Rows tagged with another tenant must not appear in a workspace-scoped export.

    Goes through the Repository directly so the rows carry an explicit
    ``tenant_id`` tag (the high-level IdentityService writes without one and
    the FR-013 legacy-fallback would otherwise lump every row under
    ``"default"``).
    """
    repo = FileRepository()
    for i in range(2):
        repo.create(
            "identities",
            {
                "agent_id": f"attestix:primary-tenant-{i}",
                "display_name": f"Primary {i}",
                "did": f"did:key:primary-{i}",
                "issuer": {"name": "Fixture", "did": f"did:key:primary-{i}"},
                "created_at": "2026-05-28T12:00:00Z",
            },
            tenant_id="primary",
            id_field="agent_id",
        )
    repo.create(
        "identities",
        {
            "agent_id": "attestix:other-tenant-only",
            "display_name": "Other",
            "did": "did:key:other",
            "issuer": {"name": "Fixture", "did": "did:key:other"},
            "created_at": "2026-05-28T12:00:00Z",
        },
        tenant_id="secondary",
        id_field="agent_id",
    )

    out = tmp_path / "primary-only.tar.gz"
    write_bundle(out, workspace="primary")
    bundle = read_bundle(out)

    # 2 identities in `primary`; the `secondary` row must be filtered out.
    assert bundle.tables["identities"].row_count == 2
    seen = [row["core_object_ref"] for row in bundle.iter_rows("identities")]
    assert "attestix:other-tenant-only" not in seen
    # And the workspace identity in the manifest is the chosen tenant.
    assert bundle.workspace.get("slug") == "primary"


def test_no_include_anchors_emits_zero_anchor_rows(tmp_path):
    _seed_oss_data()
    out = tmp_path / "no-anchors.tar.gz"
    write_bundle(out, include_anchors=False)
    bundle = read_bundle(out)
    # The table is still in the manifest (cloud parity); the row count is 0.
    assert "anchors" in bundle.tables
    assert bundle.tables["anchors"].row_count == 0
    assert bundle.tables["anchors"].bytes == 0


def test_manifest_sha_matches_fresh_recomputation(tmp_path):
    _seed_oss_data()
    out = tmp_path / "manifest-sha.tar.gz"
    result = write_bundle(out)

    bundle = read_bundle(out)
    # The reader recomputes via the same canonicaliser.
    assert bundle.verify_manifest()
    # And the recomputed sha matches the result's reported sha.
    assert (
        hashlib.sha256(canonicalize_json(bundle.manifest)).hexdigest()
        == result.manifest_sha256
    )
