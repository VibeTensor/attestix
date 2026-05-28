"""Write Attestix portability bundles (the OSS-side symmetric counterpart).

The :func:`write_bundle` helper is the inverse of
:mod:`attestix.portability.importer`: it reads every OSS-side collection through
the existing :class:`~attestix.storage.Repository` boundary, projects each row
into the cloud wire-format shape the importer expects, JCS-canonicalises every
row, sha-256s every table, and emits a USTAR + gzip tarball whose layout matches
``apps/workers/ts/src/exports.ts`` byte-for-byte.

Why a separate writer and not a method on the Repository? Because the cloud
exporter is the authoritative wire-format definition (the spec page at
``https://attestix.io/spec/bundle/v1`` describes its output); the OSS exporter
mirrors that spec so cloud bundles and OSS bundles are interchangeable. Pinning
that mirror to one module keeps the wire-format coupling auditable in code
review — change the cloud exporter and you must change this file in lock-step.

JCS canonicaliser
-----------------

The writer reuses :func:`attestix.auth.crypto.canonicalize_json` exactly. The
constitution forbids a second canonicaliser anywhere in the codebase, so the
manifest's sha-256 (computed over the canonical manifest bytes with no
``sha256`` field of its own) and every table's sha-256 (computed over the
JSONL bytes) both flow through the same routine the importer reads back.

Determinism
-----------

When ``deterministic=True`` (the default), the tarball is byte-stable across
runs against the same OSS state:

* Members are sorted alphabetically — matches the cloud worker's
  ``sort()`` over its staging directory listing and the fixture generator.
* USTAR ``mtime`` is pinned to ``0``.
* The gzip header is written with ``mtime=0`` (the cloud worker leaves the
  default ``Date.now()``, but the fixture generator pins ``mtime=0`` and that
  is the value the OSS round-trip suite expects).
* Row order inside each table is the order returned by the Repository's
  ``list`` for that collection. The order is itself byte-stable for the
  default :class:`FileRepository` (rows are appended; we never re-sort), so
  two consecutive exports of the same data produce identical bytes.
"""

from __future__ import annotations

import gzip
import hashlib
import io
import json
import tarfile
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from attestix import __version__ as ATTESTIX_VERSION
from attestix.auth.crypto import canonicalize_json
from attestix.portability.bundle_reader import (
    BUNDLE_FORMAT_URL,
    SUPPORTED_DB_MIGRATION_MAX,
    SUPPORTED_MANIFEST_VERSION,
)
from attestix.storage import Repository, default_repository
from attestix.storage.repository import DEFAULT_TENANT


#: The cloud-equivalent core_version stamp. Mirrors the cloud worker's
#: ``CORE_VERSION_PIN`` format ("attestix==<semver>") so a reader cannot tell a
#: well-formed OSS export apart from a well-formed cloud export by version
#: shape alone — both round-trip through the same import path.
CORE_VERSION = f"attestix=={ATTESTIX_VERSION}"


class BundleWriteError(Exception):
    """Raised for a problem writing a portability bundle."""


# ---------------------------------------------------------------------------
# Row projectors — OSS row shape → cloud wire-format shape
# ---------------------------------------------------------------------------
#
# Each projector mirrors the inverse of the importer's row mapper. When the OSS
# row carries `_cloud_id` / `_cloud_workspace_id` metadata (left there by a
# prior import) we re-use those values so the round-trip is idempotent — a
# re-export after a cloud→OSS→export cycle preserves the same cloud UUIDs and
# workspace bindings.


#: A fixed namespace UUID for synthesising cloud-shaped IDs deterministically.
#: Generated once with ``uuid.uuid4()`` and frozen here so two consecutive
#: exports of the same OSS row produce the same synthetic cloud UUID — a
#: prerequisite for the byte-identical re-export guarantee.
_CLOUD_ID_NAMESPACE = uuid.UUID("6b1c1e3e-1f0c-4f0d-9b6f-7a6e1c3f5d8a")


def _gen_cloud_id(*parts: str) -> str:
    """Produce a UUID5 deterministically from ``parts``.

    The cloud worker writes a real Postgres UUID for the ``id`` column on every
    row it exports. For OSS rows that never round-tripped through the cloud
    there is no native UUID, so we synthesise a stable one by hashing the row's
    semantic identifier through UUID5. Identical OSS state → identical
    synthesised UUIDs → byte-identical re-exports.
    """
    seed = "|".join(p or "" for p in parts)
    return str(uuid.uuid5(_CLOUD_ID_NAMESPACE, seed))


def _drop_tenant(row: dict) -> dict:
    """Return ``row`` without the Repository-injected ``tenant_id`` tag."""
    return {k: v for k, v in row.items() if k != "tenant_id"}


def _row_identity_to_cloud(oss: dict, *, workspace_id: str) -> dict:
    """Project an OSS identity row into the cloud ``identities`` wire shape.

    Inverse of :func:`attestix.portability.importer._row_identity`.
    """
    cloud_id = oss.get("_cloud_id") or _gen_cloud_id("identity", oss.get("agent_id", ""))
    cloud_ws = oss.get("_cloud_workspace_id") or workspace_id
    issuer = oss.get("issuer") or {}
    did = oss.get("did") or (issuer.get("did") if isinstance(issuer, dict) else None)
    name = oss.get("display_name") or (
        issuer.get("name") if isinstance(issuer, dict) else None
    ) or oss.get("agent_id")
    revoked = bool(oss.get("revoked"))
    return {
        "id": cloud_id,
        "workspace_id": cloud_ws,
        "core_object_ref": oss.get("agent_id"),
        "did": did,
        "did_method": did.split(":", 2)[1] if did and did.startswith("did:") else None,
        "did_document": oss.get("did_document"),
        "name": name,
        "signing_key_kms_ref": None,
        "status": "revoked" if revoked else "active",
        "created_at": oss.get("created_at"),
        "revoked_at": oss.get("revoked_at"),
        "revocation_reason": oss.get("revocation_reason"),
    }


def _row_credential_to_cloud(oss: dict, *, workspace_id: str) -> dict:
    """Project an OSS credential row (the VC body) into the cloud ``credentials`` wire shape."""
    cloud_id = oss.get("_cloud_id") or _gen_cloud_id("credential", oss.get("id", ""))
    cloud_ws = oss.get("_cloud_workspace_id") or workspace_id
    # The OSS row IS the VC body itself — strip OSS-only annotations before
    # nesting it under the cloud row's `credential` column.
    body = {
        k: v
        for k, v in oss.items()
        if k not in {"_cloud_id", "_cloud_workspace_id", "tenant_id"}
    }
    return {
        "id": cloud_id,
        "workspace_id": cloud_ws,
        "credential": body,
    }


def _row_compliance_profile_to_cloud(oss: dict, *, workspace_id: str) -> dict:
    """Project an OSS compliance profile into the cloud ``compliance_profiles`` shape."""
    cloud_id = oss.get("_cloud_id") or _gen_cloud_id("compliance_profile", oss.get("profile_id", ""))
    cloud_ws = oss.get("_cloud_workspace_id") or workspace_id
    body = {
        k: v
        for k, v in oss.items()
        if k not in {"_cloud_id", "_cloud_workspace_id", "tenant_id"}
    }
    return {
        "id": cloud_id,
        "workspace_id": cloud_ws,
        "profile": body,
    }


def _row_conformity_assessment_to_cloud(oss: dict, *, workspace_id: str) -> dict:
    """Project an OSS conformity assessment into the cloud ``conformity_assessments`` shape."""
    cloud_id = oss.get("_cloud_id") or _gen_cloud_id(
        "conformity_assessment", oss.get("assessment_id", "")
    )
    cloud_ws = oss.get("_cloud_workspace_id") or workspace_id
    body = {
        k: v
        for k, v in oss.items()
        if k not in {"_cloud_id", "_cloud_workspace_id", "tenant_id"}
    }
    return {
        "id": cloud_id,
        "workspace_id": cloud_ws,
        "assessment": body,
    }


def _row_audit_event_to_cloud(oss: dict, *, workspace_id: str) -> dict:
    """Project an OSS audit_event into the cloud ``audit_events`` wire shape.

    Chain-relevant fields (``event_id``, ``actor``, ``action``, ``target_id``,
    ``target_collection``, ``occurred_at``, ``change_digest``, ``prev_hash``,
    ``chain_hash``) are passed through verbatim — the chain_hash was computed
    over those fields' JCS canonical form, so any mutation would break the
    importer's :func:`verify_chain` round-trip. The OSS ``tenant_id`` field is
    also preserved verbatim because it participates in the chain_hash body; the
    cloud surrogate ``workspace_id`` is recorded separately for cloud-side
    re-binding (the importer drops it).

    Cloud-only surrogate fields (``id``, ``occurred_at_month``, ``anchor_id``,
    ``retention_days``, ``created_at``) are synthesised from the OSS row when
    a prior import did not stamp them as ``_cloud_*`` metadata.
    """
    cloud_id = oss.get("_cloud_id") or _gen_cloud_id("audit_event", oss.get("event_id", ""))
    cloud_ws = oss.get("_cloud_workspace_id") or workspace_id
    anchor_id = oss.get("_cloud_anchor_id")
    # `occurred_at_month` is a YYYY-MM-DD bucket the cloud uses for retention;
    # we derive it from the chain field so re-imports keep the partitioning.
    occurred_at = oss.get("occurred_at", "")
    month_bucket = occurred_at[:10] if len(occurred_at) >= 10 else occurred_at
    return {
        "id": cloud_id,
        "workspace_id": cloud_ws,
        "occurred_at_month": month_bucket,
        "anchor_id": anchor_id,
        "retention_days": None,
        "created_at": occurred_at,
        # Chain fields — preserved verbatim.
        "event_id": oss["event_id"],
        "tenant_id": oss.get("tenant_id"),
        "actor": oss["actor"],
        "action": oss["action"],
        "target_id": oss["target_id"],
        "target_collection": oss["target_collection"],
        "occurred_at": oss["occurred_at"],
        "change_digest": oss["change_digest"],
        "prev_hash": oss["prev_hash"],
        "chain_hash": oss["chain_hash"],
    }


def _row_anchor_to_cloud(oss: dict, *, workspace_id: str) -> dict:
    """Project an OSS anchor row into the cloud ``anchors`` wire shape."""
    cloud_id = oss.get("_cloud_id") or _gen_cloud_id("anchor", oss.get("anchor_id", ""))
    cloud_ws = oss.get("_cloud_workspace_id") or workspace_id
    body = {
        k: v
        for k, v in oss.items()
        if k not in {"_cloud_id", "_cloud_workspace_id", "tenant_id"}
    }
    return {
        "id": cloud_id,
        "workspace_id": cloud_ws,
        "anchor": body,
    }


# ---------------------------------------------------------------------------
# EXPORT_PLAN — the inverse of IMPORT_PLAN
# ---------------------------------------------------------------------------
#
# Tuple shape:
#   (bundle_table_name, oss_collection, id_field, list_key_in_document, projector)
#
# ``oss_collection`` is the FileRepository collection name (see _COLLECTIONS in
# file_repository.py). ``list_key_in_document`` is the key under which rows live
# in the collection's JSON document — for ``compliance`` we read both
# ``profiles`` and ``assessments`` from the same document, hence two entries.
# ``id_field`` is the per-collection primary-key field the Repository uses.
#
# Order MUST match the cloud worker's ``EXPORT_TABLE_SPECS`` so the manifest
# tables array and the on-disk member order agree byte-for-byte across the two
# implementations.

ProjectorFn = Callable[[dict, str], dict]


@dataclass(frozen=True)
class TableSpec:
    """One row of EXPORT_PLAN."""

    name: str  # bundle table name (e.g. "audit_events")
    oss_collection: Optional[str]  # FileRepository collection, None for cloud-only
    id_field: str
    list_key: str
    projector: Optional[ProjectorFn]


EXPORT_PLAN: List[TableSpec] = [
    TableSpec("identities", "identities", "agent_id", "agents", _row_identity_to_cloud),
    # Cloud-only — emitted as an empty JSONL so the OSS bundle has the same
    # member set as a cloud bundle (the importer skips these on read).
    TableSpec("key_references", None, "id", "", None),
    TableSpec("credentials", "credentials", "id", "credentials", _row_credential_to_cloud),
    TableSpec("credential_schemas", None, "id", "", None),
    TableSpec("memberships", None, "id", "", None),
    TableSpec("team_invites", None, "id", "", None),
    TableSpec("subscriptions", None, "id", "", None),
    TableSpec(
        "compliance_profiles",
        "compliance",
        "profile_id",
        "profiles",
        _row_compliance_profile_to_cloud,
    ),
    TableSpec(
        "conformity_assessments",
        "compliance",
        "assessment_id",
        "assessments",
        _row_conformity_assessment_to_cloud,
    ),
    TableSpec("agent_dependencies", None, "id", "", None),
    TableSpec("audit_events", "audit", "event_id", "events", _row_audit_event_to_cloud),
    TableSpec("anchors", "anchors", "anchor_id", "anchors", _row_anchor_to_cloud),
    TableSpec("webhook_endpoints", None, "id", "", None),
]


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TableResult:
    """Per-table outcome of one export run."""

    name: str
    row_count: int
    bytes: int
    sha256: str


@dataclass
class BundleResult:
    """Aggregate outcome of one export run."""

    path: Path
    bytes: int
    manifest_sha256: str
    tables: List[TableResult] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Implementation
# ---------------------------------------------------------------------------


def _jsonl_canonical(rows: List[dict]) -> bytes:
    """Serialise rows as JCS-canonical JSONL (one row per line, trailing \\n).

    Mirrors :func:`tests.fixtures.bundles.generate_sample_bundle._jsonl_canonical`
    exactly — the cloud worker's output uses the same pattern and the reader
    splits on ``\\n`` skipping empty tail lines, so an empty table writes zero
    bytes (no trailing newline).
    """
    if not rows:
        return b""
    lines = [canonicalize_json(r).decode("utf-8") for r in rows]
    return ("\n".join(lines) + "\n").encode("utf-8")


def _sha256_hex(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def _infer_workspace_slug(repo: Repository) -> str:
    """Infer the bundle's workspace slug from the local audit chain.

    Returns the single tenant_id every audit event was chained against, or
    :data:`DEFAULT_TENANT` if no audit events exist. Raises if events come from
    multiple tenants — the bundle's manifest carries one workspace slug, so a
    multi-tenant install must either pass ``--workspace`` to pick one or run
    one export per tenant.
    """
    if not hasattr(repo, "load_document"):
        return DEFAULT_TENANT
    doc = repo.load_document("audit")
    events = doc.get("events", []) or []
    tenants = {ev.get("tenant_id", DEFAULT_TENANT) for ev in events}
    if not tenants:
        return DEFAULT_TENANT
    if len(tenants) == 1:
        return next(iter(tenants))
    raise BundleWriteError(
        "audit_events span multiple tenants "
        f"({sorted(tenants)!r}); pass --workspace <tenant> to pick one. The "
        "bundle's workspace slug must match the audit chain's tenant so the "
        "importer can re-verify the chain end-to-end."
    )


def _list_rows(
    repo: Repository, oss_collection: str, list_key: str, *, workspace: Optional[str]
) -> List[dict]:
    """Read every row in an OSS collection.

    Uses the Repository's ``load_document`` to read all rows regardless of
    tenant, since portability is a workspace-level concern, not a per-tenant
    one. If ``workspace`` is set, only rows tagged with that ``tenant_id`` are
    returned — the FileRepository tags every row with its tenant on create, so
    rows created under the default tenant carry ``tenant_id == "default"``.

    The list_key lookup mirrors :mod:`attestix.storage.file_repository._COLLECTIONS`:
    every Repository document has one top-level key holding the row list, plus
    optional sibling lists (e.g. ``compliance`` carries ``profiles`` /
    ``assessments`` / ``declarations`` in one file).
    """
    if not hasattr(repo, "load_document"):
        # A Repository without load_document (e.g. a custom backend) still
        # supports list(); fall back to that, scoped by the requested workspace
        # tenant or the default tenant.
        tenant = workspace or DEFAULT_TENANT
        return repo.list(oss_collection, tenant_id=tenant)
    doc = repo.load_document(oss_collection)
    rows = list(doc.get(list_key, []) or [])
    if workspace is not None:
        rows = [r for r in rows if r.get("tenant_id", DEFAULT_TENANT) == workspace]
    return rows


def _build_tar(
    members: List[Tuple[str, bytes]],
    *,
    deterministic: bool,
) -> bytes:
    """Assemble the tarball bytes from ``(name, body)`` pairs.

    ``members`` is consumed in the order provided; callers must pre-sort.
    """
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w", format=tarfile.USTAR_FORMAT) as tar:
        for name, data in members:
            info = tarfile.TarInfo(name=name)
            info.size = len(data)
            info.mode = 0o644
            if deterministic:
                info.mtime = 0
                info.uid = 0
                info.gid = 0
                info.uname = ""
                info.gname = ""
            tar.addfile(info, io.BytesIO(data))
    return buf.getvalue()


def _gzip_bytes(tar_bytes: bytes, *, deterministic: bool) -> bytes:
    """Gzip ``tar_bytes``. With ``deterministic=True`` the gzip header carries ``mtime=0``."""
    out = io.BytesIO()
    mtime = 0 if deterministic else None
    with gzip.GzipFile(filename="", fileobj=out, mode="wb", mtime=mtime) as gz:
        gz.write(tar_bytes)
    return out.getvalue()


def write_bundle(
    output_path: Path,
    *,
    workspace: Optional[str] = None,
    include_anchors: bool = True,
    include_audit: bool = True,
    deterministic: bool = True,
    repository: Optional[Repository] = None,
    now: Optional[datetime] = None,
) -> BundleResult:
    """Write a portability bundle for the local OSS instance.

    Args:
        output_path: Where to write the ``.tar.gz``. Parent directories are
            created if missing.
        workspace: If set, only rows tagged ``tenant_id == workspace`` are
            exported. The bundle's ``workspace.slug`` is set to this value (or
            ``"local"`` when ``None``).
        include_anchors: When ``False`` the ``anchors`` table is emitted with
            zero rows but is still present in the manifest (the reader is
            tolerant of zero-row tables).
        include_audit: When ``False`` the ``audit_events`` table is emitted
            with zero rows. The cloud exporter has the same flag at the export
            request layer; we expose it here for parity.
        deterministic: Byte-stable tar + gzip output (mtime pinned to 0, member
            order alphabetical). Tests that byte-compare two consecutive
            exports require this.
        repository: Override the default file-backed Repository (used by
            tests). Defaults to :func:`attestix.storage.default_repository`.
        now: Override the export timestamp (used by tests for byte stability).

    Returns:
        :class:`BundleResult` with the on-disk size, the manifest sha-256, and
        per-table metadata.

    Raises:
        BundleWriteError: For any structural problem (Repository unavailable,
            row projection failure, etc.).
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    repo = repository or default_repository()

    # The workspace slug stamped into the manifest MUST match the tenant_id the
    # exported audit events were chained against. The importer projects
    # audit_events back using ``bundle.workspace.slug`` as the row's tenant_id,
    # and the chain_hash includes tenant_id in its JCS-canonical body — so a
    # workspace slug that differs from the audit events' tenant breaks chain
    # re-verification on import.
    #
    # Resolution order:
    #   1. Explicit ``workspace`` argument (the user told us which tenant).
    #   2. Inspect the audit_events collection: if every event shares one
    #      tenant, use it.
    #   3. Otherwise fall back to ``DEFAULT_TENANT`` ("default"), which is the
    #      tenant every v0.3.0 / single-tenant self-host install writes under.
    workspace_slug = workspace or _infer_workspace_slug(repo)
    workspace_id = workspace or workspace_slug
    exported_at = (now or datetime.now(timezone.utc)).strftime(
        "%Y-%m-%dT%H:%M:%S.000Z"
    )

    # ---- Stage 1: build every table body + manifest entry ------------------
    table_entries: List[dict] = []
    table_bodies: Dict[str, bytes] = {}
    table_results: List[TableResult] = []

    for spec in EXPORT_PLAN:
        if spec.oss_collection is None or spec.projector is None:
            # Cloud-only table — emit an empty JSONL so the bundle's member set
            # mirrors a cloud-side export. The reader is happy with row_count=0.
            rows_cloud: List[dict] = []
        elif spec.name == "anchors" and not include_anchors:
            rows_cloud = []
        elif spec.name == "audit_events" and not include_audit:
            rows_cloud = []
        else:
            try:
                oss_rows = _list_rows(
                    repo, spec.oss_collection, spec.list_key, workspace=workspace
                )
            except Exception as e:  # noqa: BLE001 — surface storage errors verbosely
                raise BundleWriteError(
                    f"failed to read OSS collection {spec.oss_collection!r} "
                    f"for table {spec.name!r}: {e}"
                ) from e
            try:
                rows_cloud = [
                    spec.projector(_drop_tenant(r), workspace_id=workspace_id)
                    for r in oss_rows
                ]
            except Exception as e:  # noqa: BLE001
                raise BundleWriteError(
                    f"row projection failed for table {spec.name!r}: {e}"
                ) from e

        body = _jsonl_canonical(rows_cloud)
        sha = _sha256_hex(body)
        member = f"{spec.name}.jsonl"
        table_bodies[member] = body
        table_entries.append(
            {
                "name": spec.name,
                "format": "jsonl",
                "row_count": len(rows_cloud),
                "bytes": len(body),
                "sha256": sha,
            }
        )
        table_results.append(
            TableResult(name=spec.name, row_count=len(rows_cloud), bytes=len(body), sha256=sha)
        )

    # ---- Stage 2: build manifest + compute its sha-256 ---------------------
    manifest = {
        "manifest_version": SUPPORTED_MANIFEST_VERSION,
        "attestix_bundle_format": BUNDLE_FORMAT_URL,
        "workspace": {
            "id": workspace_id,
            "slug": workspace_slug,
            "region": "local",
            "data_residency": "self-host",
        },
        "exported_at": exported_at,
        "exported_by": {"user_id": "local", "email": "self-host@local"},
        "tables": table_entries,
        "core_version": CORE_VERSION,
        "schemas": {"db_migration_max": SUPPORTED_DB_MIGRATION_MAX},
        "notes": ["format=jsonl", "exporter=oss"],
    }
    manifest_canonical = canonicalize_json(manifest)
    manifest_sha = _sha256_hex(manifest_canonical)

    # ---- Stage 3: assemble tar + gzip (alphabetical member order) ----------
    members: List[Tuple[str, bytes]] = list(table_bodies.items())
    members.append(("manifest.json", manifest_canonical))
    members.append(("manifest.sha256", (manifest_sha + "\n").encode("utf-8")))
    # Determinism: alphabetical order across every member. Without sorting, the
    # tar's member order depends on Python dict insertion order — stable in
    # CPython 3.7+, but the cloud worker sorts explicitly and the OSS round-
    # trip suite byte-compares against that ordering.
    members.sort(key=lambda kv: kv[0])

    tar_bytes = _build_tar(members, deterministic=deterministic)
    gz_bytes = _gzip_bytes(tar_bytes, deterministic=deterministic)

    output_path.write_bytes(gz_bytes)

    return BundleResult(
        path=output_path,
        bytes=len(gz_bytes),
        manifest_sha256=manifest_sha,
        tables=table_results,
    )
