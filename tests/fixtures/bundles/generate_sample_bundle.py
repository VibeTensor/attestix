"""Generate the sample portability bundle the OSS importer tests load.

The bundle this script writes is *byte-equivalent* to what the cloud's
``apps/workers/ts/src/exports.ts`` worker writes: a USTAR + gzip tarball
containing one JCS-canonical ``<table>.jsonl`` per in-scope table, plus a
``manifest.json`` (JCS-canonical) and a ``manifest.sha256`` side-car. The
manifest stamps the ``https://attestix.io/spec/bundle/v1`` format URL and the
``db_migration_max`` the OSS build supports.

We deliberately keep this generator inside the OSS repo (rather than copying a
pre-made tarball over from the cloud repo) so the OSS round-trip suite remains
self-contained and reproducible: any future change to the wire format is
mirrored here in lock-step, and the fixture rebuild is deterministic.

Run with::

    .venv/Scripts/python.exe tests/fixtures/bundles/generate_sample_bundle.py

The output lands at ``tests/fixtures/bundles/sample-v1.tar.gz`` (and an
unpacked staging directory next to it which the script removes after writing).
"""

from __future__ import annotations

import gzip
import hashlib
import io
import os
import sys
import tarfile
from pathlib import Path

# Ensure the project root is on sys.path so this script runs standalone.
HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from attestix.audit.events import AuditEvent, GENESIS_HASH  # noqa: E402
from attestix.auth.crypto import canonicalize_json  # noqa: E402

BUNDLE_FORMAT_URL = "https://attestix.io/spec/bundle/v1"
MANIFEST_VERSION = "1.0"
CORE_VERSION = "attestix==0.4.0rc2"
DB_MIGRATION_MAX = "0010"

WORKSPACE_ID = "11111111-1111-4111-8111-111111111111"
WORKSPACE_SLUG = "fixture-tenant"
REGION = "eu-west-1"
DATA_RESIDENCY = "eu"
EXPORTED_AT = "2026-05-28T12:00:00.000Z"
EXPORTER_USER_ID = "22222222-2222-4222-8222-222222222222"
EXPORTER_EMAIL = "operator@fixture.attestix.io"


def _jsonl_canonical(rows: list[dict]) -> bytes:
    """Serialise rows as JCS-canonical JSONL (one row per line, trailing \\n)."""
    if not rows:
        return b""
    lines = [canonicalize_json(r).decode("utf-8") for r in rows]
    return ("\n".join(lines) + "\n").encode("utf-8")


def _sha256_hex(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def _sample_identities() -> list[dict]:
    # Pre-computed did:key (Ed25519) belonging to a deterministic fixture key.
    # We use the same DID across rows so the OSS DID resolver round-trips.
    did = "did:key:z6MkpTHR8VNsBxYAAWHut2Geadd9jSrutDA7vRrZ2FdAB2zZ"
    did_document = {
        "@context": [
            "https://www.w3.org/ns/did/v1",
            "https://w3id.org/security/suites/ed25519-2020/v1",
        ],
        "id": did,
        "controller": did,
        "verificationMethod": [
            {
                "id": f"{did}#key-1",
                "type": "Ed25519VerificationKey2020",
                "controller": did,
            }
        ],
        "authentication": [f"{did}#key-1"],
        "assertionMethod": [f"{did}#key-1"],
    }
    return [
        {
            "id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1",
            "workspace_id": WORKSPACE_ID,
            "core_object_ref": "attestix:fixture0000000001",
            "did": did,
            "did_method": "key",
            "did_document": did_document,
            "name": "Fixture Agent One",
            "signing_key_kms_ref": None,
            "status": "active",
            "created_at": "2026-05-01T09:00:00Z",
            "revoked_at": None,
            "revocation_reason": None,
        },
        {
            "id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa2",
            "workspace_id": WORKSPACE_ID,
            "core_object_ref": "attestix:fixture0000000002",
            "did": did,
            "did_method": "key",
            "did_document": did_document,
            "name": "Fixture Agent Two",
            "signing_key_kms_ref": None,
            "status": "active",
            "created_at": "2026-05-01T09:01:00Z",
            "revoked_at": None,
            "revocation_reason": None,
        },
    ]


def _sample_credentials() -> list[dict]:
    return [
        {
            "id": "cccccccc-cccc-4ccc-8ccc-cccccccccc01",
            "workspace_id": WORKSPACE_ID,
            # Real cloud exports the signed VC under ``vc_jsonld`` (the DB column
            # name in packages/db/src/schema/credentials.ts), not ``credential``.
            "vc_jsonld": {
                "id": "urn:uuid:cred-fixture-0001",
                "type": ["VerifiableCredential", "AgentIdentityCredential"],
                "issuer": {"id": "did:key:fixture-issuer", "name": "Fixture Issuer"},
                "issuanceDate": "2026-05-01T10:00:00Z",
                "expirationDate": "2027-05-01T10:00:00Z",
                "credentialSubject": {
                    "id": "attestix:fixture0000000001",
                    "role": "Fixture Subject",
                },
                "credentialStatus": {
                    "id": "urn:uuid:cred-fixture-0001#status",
                    "type": "RevocationList2021Status",
                    "revoked": False,
                    "revocation_reason": None,
                    "revoked_at": None,
                },
            },
        }
    ]


def _sample_compliance_profiles() -> list[dict]:
    return [
        {
            "id": "ddddddd1-dddd-4ddd-8ddd-dddddddddd01",
            "workspace_id": WORKSPACE_ID,
            "profile": {
                "profile_id": "comp:fixture00001",
                "agent_id": "attestix:fixture0000000001",
                "risk_category": "limited",
                "provider": {"name": "Fixture Provider", "did": "did:key:fixture"},
                "ai_system": {"intended_purpose": "Smoke-test imports"},
                "transparency": {
                    "obligations": "auto-generated",
                    "human_oversight_measures": "review",
                },
                "required_obligations": ["transparency:disclose_ai"],
                "conformity": {
                    "assessment_completed": False,
                    "assessment_id": None,
                    "declaration_id": None,
                    "ce_marking_eligible": False,
                },
                "created_at": "2026-05-01T11:00:00Z",
                "updated_at": "2026-05-01T11:00:00Z",
            },
        }
    ]


def _sample_conformity_assessments() -> list[dict]:
    return [
        {
            "id": "eeeeeeee-eeee-4eee-8eee-eeeeeeeeeee1",
            "workspace_id": WORKSPACE_ID,
            "assessment": {
                "assessment_id": "assess:fixture00001",
                "agent_id": "attestix:fixture0000000001",
                "assessment_type": "self",
                "assessor_name": "Internal",
                "result": "pass",
                "findings": "no findings",
                "ce_marking_eligible": False,
                "assessed_at": "2026-05-01T12:00:00Z",
                "assessed_by": "did:key:fixture",
            },
        }
    ]


def _sample_anchors() -> list[dict]:
    return [
        {
            "id": "ffffffff-ffff-4fff-8fff-ffffffffff01",
            "workspace_id": WORKSPACE_ID,
            "anchor": {
                "anchor_id": "anchor:fixture000001",
                "artifact_type": "identity",
                "artifact_id": "attestix:fixture0000000001",
                "artifact_hash": "abcd" * 16,
                "network": "sepolia",
                "chain_id": 84532,
                "tx_hash": "0x" + ("ab" * 32),
                "attestation_uid": "0x" + ("cd" * 32),
                "schema_uid": "0x" + ("ef" * 32),
                "attester": "0x" + ("11" * 20),
                "block_number": 42,
                "gas_used": 187000,
                "explorer_url": "https://sepolia.basescan.org/tx/0xab",
                "anchored_at": "2026-05-01T13:00:00Z",
                "issuer_did": "did:key:fixture",
            },
        }
    ]


def _sample_audit_events() -> list[dict]:
    """Build a real hash-chain so the OSS chain verifier accepts it.

    We mint events through the same :class:`AuditEvent` helper the cloud's
    audit-chain package mirrors, then project to the cloud row shape (the
    importer's mapper inverts this).
    """
    events: list[dict] = []
    prev = GENESIS_HASH
    for i in range(3):
        ev = AuditEvent.create(
            action="identity.create" if i == 0 else "credential.issue",
            target_id=f"attestix:fixture000000000{i+1}",
            target_collection="identities" if i == 0 else "credentials",
            actor="user:operator@fixture.attestix.io",
            # Mirror real cloud: the chain is minted under the workspace UUID
            # (audit-service.ts computeChainHash uses workspaceId), and the
            # exported row carries tenant_id=WORKSPACE_ID. The OSS importer
            # preserves that chain tenant and persists the audit chain under it,
            # decoupled from the user's storage tenant (audit B8 fix, v0.4.1).
            tenant_id=WORKSPACE_ID,
            after={"id": f"attestix:fixture000000000{i+1}"},
            prev_hash=prev,
            occurred_at=f"2026-05-01T1{i}:00:00+00:00",
            event_id=f"evt:fixture00000{i}",
        )
        prev = ev.chain_hash
        events.append(
            {
                # Cloud-only surrogate fields:
                "id": f"99999999-9999-4999-8999-99999999990{i}",
                "workspace_id": WORKSPACE_ID,
                "occurred_at_month": "2026-05-01",
                "anchor_id": None,
                "retention_days": 7,
                "created_at": f"2026-05-01T1{i}:00:01Z",
                # OSS chain fields (tenant_id mirrors cloud toOssDict = workspace id):
                "tenant_id": WORKSPACE_ID,
                "event_id": ev.event_id,
                "actor": ev.actor,
                "action": ev.action,
                "target_id": ev.target_id,
                "target_collection": ev.target_collection,
                "occurred_at": ev.occurred_at,
                "change_digest": ev.change_digest,
                "prev_hash": ev.prev_hash,
                "chain_hash": ev.chain_hash,
            }
        )
    return events


# Tables — order matters for the manifest (must match the cloud exporter's
# EXPORT_TABLE_SPECS order). Cloud-only tables (memberships, etc.) are written
# as empty rows lists so the OSS importer exercises the "cloud-only skip" path.
TABLES = [
    ("identities", _sample_identities()),
    ("key_references", []),
    ("credentials", _sample_credentials()),
    ("credential_schemas", []),
    ("memberships", []),
    ("team_invites", []),
    ("subscriptions", []),
    ("compliance_profiles", _sample_compliance_profiles()),
    ("conformity_assessments", _sample_conformity_assessments()),
    ("agent_dependencies", []),
    ("audit_events", _sample_audit_events()),
    ("anchors", _sample_anchors()),
    ("webhook_endpoints", []),
]


def build_manifest(
    table_entries: list[dict],
    *,
    bundle_format: str = BUNDLE_FORMAT_URL,
) -> dict:
    return {
        "manifest_version": MANIFEST_VERSION,
        "attestix_bundle_format": bundle_format,
        "workspace": {
            "id": WORKSPACE_ID,
            "slug": WORKSPACE_SLUG,
            "region": REGION,
            "data_residency": DATA_RESIDENCY,
        },
        "exported_at": EXPORTED_AT,
        "exported_by": {"user_id": EXPORTER_USER_ID, "email": EXPORTER_EMAIL},
        "tables": table_entries,
        "core_version": CORE_VERSION,
        "schemas": {"db_migration_max": DB_MIGRATION_MAX},
        "notes": ["format=jsonl", "fixture=oss-roundtrip"],
    }


def write_bundle(
    output_path: Path,
    *,
    tables: list[tuple[str, list[dict]]] = TABLES,
    tamper_manifest_sha: bool = False,
    tamper_table_body: str | None = None,
    bump_db_migration: str | None = None,
) -> None:
    """Write a sample bundle to ``output_path``.

    ``tamper_manifest_sha`` flips the manifest body after sha computation so
    the OSS verifier reports a manifest mismatch.
    ``tamper_table_body`` (table name) flips one byte of that table's JSONL so
    the OSS verifier reports a per-table sha mismatch.
    ``bump_db_migration`` overrides ``schemas.db_migration_max`` so we can
    exercise the schema-too-new refusal.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    table_entries: list[dict] = []
    table_bodies: dict[str, bytes] = {}
    for name, rows in tables:
        body = _jsonl_canonical(rows)
        if tamper_table_body == name and body:
            # Flip a single byte inside the JSONL so the sha no longer matches.
            mutable = bytearray(body)
            mutable[0] = (mutable[0] + 1) % 256
            table_bodies[name] = bytes(mutable)
        else:
            table_bodies[name] = body
        # The manifest sha is over the EXPECTED (untampered) body; this means
        # a `tamper_table_body` produces a real on-disk vs manifest mismatch.
        table_entries.append(
            {
                "name": name,
                "format": "jsonl",
                "row_count": len(rows),
                "bytes": len(body),
                "sha256": _sha256_hex(body),
            }
        )

    manifest = build_manifest(table_entries)
    if bump_db_migration:
        manifest["schemas"]["db_migration_max"] = bump_db_migration
    manifest_canonical = canonicalize_json(manifest)
    manifest_sha = _sha256_hex(manifest_canonical)

    if tamper_manifest_sha:
        # Flip a byte inside the manifest body so the sha no longer matches.
        mutable = bytearray(manifest_canonical)
        # Find a safe byte to flip — pick a quote we know isn't load-bearing.
        for i, c in enumerate(mutable):
            if chr(c).isdigit() and chr(mutable[i - 1]) == ":":
                mutable[i] = ord("9") if chr(c) != "9" else ord("0")
                break
        manifest_canonical = bytes(mutable)

    # Assemble the tar in memory then gzip it. We use Python's tarfile in
    # USTAR format which is byte-compatible with the JS exporter's hand-rolled
    # USTAR for our purposes (the OSS reader does not pin the tar variant; it
    # opens with `r:gz`).
    tar_buffer = io.BytesIO()
    with tarfile.open(
        fileobj=tar_buffer, mode="w", format=tarfile.USTAR_FORMAT
    ) as tar:
        for name, _rows in tables:
            data = table_bodies[name]
            info = tarfile.TarInfo(name=f"{name}.jsonl")
            info.size = len(data)
            info.mtime = 0
            info.mode = 0o644
            tar.addfile(info, io.BytesIO(data))

        info = tarfile.TarInfo(name="manifest.json")
        info.size = len(manifest_canonical)
        info.mtime = 0
        info.mode = 0o644
        tar.addfile(info, io.BytesIO(manifest_canonical))

        sha_body = (manifest_sha + "\n").encode("utf-8")
        info = tarfile.TarInfo(name="manifest.sha256")
        info.size = len(sha_body)
        info.mtime = 0
        info.mode = 0o644
        tar.addfile(info, io.BytesIO(sha_body))

    # gzip.open does not take an mtime kwarg; use GzipFile directly so the
    # output is byte-stable across re-runs (mtime=0 in the gzip header).
    with open(output_path, "wb") as fh:
        with gzip.GzipFile(filename="", fileobj=fh, mode="wb", mtime=0) as gz:
            gz.write(tar_buffer.getvalue())


def main() -> None:
    out = HERE / "sample-v1.tar.gz"
    write_bundle(out)
    print(f"wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
