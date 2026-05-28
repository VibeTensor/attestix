"""Bundle-reader tests for the OSS portability layer (M6 import round-trip).

Cover the wire-format invariants we *promise* to the cloud exporter:

* a valid bundle parses and ``verify_manifest`` + per-table sha both pass;
* a tampered manifest body fails ``verify_manifest`` (and the overall
  ``verify`` returns the problem);
* a tampered table body fails the per-table sha (and the overall ``verify``
  surfaces it without claiming the manifest is broken);
* a bundle stamped with a newer ``db_migration_max`` than this OSS build
  supports raises :class:`BundleSchemaTooNewError`.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from attestix.portability import (
    BUNDLE_FORMAT_URL,
    BundleError,
    BundleSchemaTooNewError,
    SUPPORTED_DB_MIGRATION_MAX,
    SUPPORTED_MANIFEST_VERSION,
    read_bundle,
)

# Import the generator module so each test can produce a fresh bundle variant
# under tmp_path without mutating the committed fixture.
from tests.fixtures.bundles.generate_sample_bundle import (
    TABLES,
    write_bundle,
)

FIXTURE_PATH = (
    Path(__file__).resolve().parents[1] / "fixtures" / "bundles" / "sample-v1.tar.gz"
)


@pytest.fixture
def good_bundle_path(tmp_path) -> Path:
    """Write a fresh, untampered sample bundle into tmp_path."""
    out = tmp_path / "sample.tar.gz"
    write_bundle(out)
    return out


def test_committed_fixture_loads_cleanly():
    """The committed fixture under tests/fixtures/bundles is a valid v1 bundle.

    This guards against the generator script drifting from the wire-format
    spec without regenerating the fixture — a regenerate is mandatory.
    """
    assert FIXTURE_PATH.exists(), (
        f"Fixture {FIXTURE_PATH} missing — regenerate with "
        f"`python tests/fixtures/bundles/generate_sample_bundle.py`."
    )
    bundle = read_bundle(FIXTURE_PATH)
    assert bundle.bundle_format == BUNDLE_FORMAT_URL
    assert bundle.manifest_version == SUPPORTED_MANIFEST_VERSION
    assert bundle.db_migration_max == SUPPORTED_DB_MIGRATION_MAX
    ok, problems = bundle.verify()
    assert ok, f"committed fixture failed verification: {problems}"


def test_read_bundle_parses_expected_tables(good_bundle_path):
    bundle = read_bundle(good_bundle_path)
    # Every table in TABLES is present in the manifest + tarball.
    for name, rows in TABLES:
        assert name in bundle.tables, f"missing {name} in manifest"
        info = bundle.tables[name]
        materialised = list(bundle.iter_rows(name))
        assert len(materialised) == len(rows) == info.row_count


def test_verify_manifest_round_trip(good_bundle_path):
    bundle = read_bundle(good_bundle_path)
    assert bundle.verify_manifest() is True
    # Each per-table sha also round-trips.
    for name in bundle.tables:
        assert bundle.verify_table_sha(name), f"{name}.jsonl sha drifted"


def test_tampered_manifest_sha_fails(tmp_path):
    bad = tmp_path / "bad-manifest.tar.gz"
    write_bundle(bad, tamper_manifest_sha=True)
    bundle = read_bundle(bad)
    assert bundle.verify_manifest() is False
    ok, problems = bundle.verify()
    assert not ok
    assert any("manifest sha256 mismatch" in p for p in problems)


def test_tampered_table_body_fails(tmp_path):
    bad = tmp_path / "bad-table.tar.gz"
    write_bundle(bad, tamper_table_body="identities")
    bundle = read_bundle(bad)
    # Manifest itself is still self-consistent (we did NOT mutate the manifest
    # body, only one table's bytes after sha computation).
    assert bundle.verify_manifest() is True
    assert bundle.verify_table_sha("identities") is False
    ok, problems = bundle.verify()
    assert not ok
    assert any("identities" in p and "sha256 mismatch" in p for p in problems)


def test_schema_too_new_refuses(tmp_path):
    too_new = tmp_path / "too-new.tar.gz"
    write_bundle(too_new, bump_db_migration="9999")
    bundle = read_bundle(too_new)
    with pytest.raises(BundleSchemaTooNewError) as exc:
        bundle.check_schema_compatibility()
    assert "9999" in str(exc.value)
    assert "upgrade" in str(exc.value).lower() or "attestix.io" in str(exc.value)


def test_older_migration_is_accepted(tmp_path):
    # An OSS build that supports up to 0010 must still accept a 0009 bundle.
    older = tmp_path / "older.tar.gz"
    write_bundle(older, bump_db_migration="0009")
    bundle = read_bundle(older)
    # No exception:
    bundle.check_schema_compatibility()


def test_missing_manifest_member_rejected(tmp_path):
    # Truncate the file to a few bytes to force a tarfile error.
    bad = tmp_path / "not-a-bundle.tar.gz"
    bad.write_bytes(b"not a tarball")
    with pytest.raises(BundleError):
        read_bundle(bad)


def test_unknown_format_url_rejected(tmp_path):
    """An exporter that stamps the wrong attestix_bundle_format string is refused."""

    # Build via the helper but mutate the canonicalised manifest to point at a
    # different URL before tarring. We do this by monkey-patching the helper.
    import gzip
    import hashlib
    import io
    import tarfile
    import json

    from attestix.auth.crypto import canonicalize_json

    out = tmp_path / "wrong-format.tar.gz"
    body = canonicalize_json({
        "manifest_version": "1.0",
        "attestix_bundle_format": "https://example.com/not-attestix",
        "workspace": {"id": "x", "slug": "x", "region": "x", "data_residency": "x"},
        "exported_at": "2026-01-01T00:00:00Z",
        "exported_by": {"user_id": None, "email": None},
        "tables": [],
        "core_version": "x",
        "schemas": {"db_migration_max": "0010"},
        "notes": [],
    })
    sha = hashlib.sha256(body).hexdigest()
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w", format=tarfile.USTAR_FORMAT) as tar:
        info = tarfile.TarInfo("manifest.json")
        info.size = len(body)
        tar.addfile(info, io.BytesIO(body))
        sha_bytes = (sha + "\n").encode()
        info = tarfile.TarInfo("manifest.sha256")
        info.size = len(sha_bytes)
        tar.addfile(info, io.BytesIO(sha_bytes))
    with open(out, "wb") as fh:
        with gzip.GzipFile(filename="", fileobj=fh, mode="wb", mtime=0) as gz:
            gz.write(buf.getvalue())
    with pytest.raises(BundleError) as exc:
        read_bundle(out)
    assert "unrecognised bundle format" in str(exc.value)


def test_iter_rows_yields_jcs_canonical_objects(good_bundle_path):
    """Rows are JSON objects whose snake_case keys match Postgres columns."""
    bundle = read_bundle(good_bundle_path)
    rows = bundle.rows("identities")
    assert rows, "fixture should ship identities rows"
    first = rows[0]
    assert "workspace_id" in first
    assert "core_object_ref" in first
    assert "did" in first
    # Camel-case keys should NOT leak through (sanity check on the exporter side).
    assert "workspaceId" not in first
