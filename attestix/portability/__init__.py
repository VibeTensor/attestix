"""OSS-side portability layer for Attestix bundles.

This package implements the consumer side of the cloud M6 portability bundle
format (``https://attestix.io/spec/bundle/v1``) — the round-trip partner of
``attestix-cloud/apps/workers/ts/src/exports.ts``. A bundle is a USTAR + gzip
tarball containing one JCS-canonical JSONL file per table, a ``manifest.json``,
and a side-car ``manifest.sha256``.

Public surface:

- :class:`~attestix.portability.bundle_reader.Bundle` — parsed bundle with
  manifest, per-table row iterators, and verification helpers.
- :func:`~attestix.portability.bundle_reader.read_bundle` — open a bundle from
  disk and return a :class:`Bundle`.
- :class:`~attestix.portability.importer.Importer` — apply a bundle's contents
  to the local OSS storage layer through the existing service APIs.

The reader DOES NOT introduce a second JCS canonicaliser: it reuses
``attestix.auth.crypto.canonicalize_json``, the same helper the OSS signer and
audit-event chain depend on. The cloud exporter uses the equivalent JS routine,
so manifest re-hashes match across implementations.
"""

from attestix.portability.bundle_reader import (
    BUNDLE_FORMAT_URL,
    Bundle,
    BundleError,
    BundleSchemaTooNewError,
    BundleVerifyError,
    SUPPORTED_DB_MIGRATION_MAX,
    SUPPORTED_MANIFEST_VERSION,
    read_bundle,
)
from attestix.portability.importer import (
    ImportError as BundleImportError,
    ImportResult,
    Importer,
    LocalDataExistsError,
)

__all__ = [
    "BUNDLE_FORMAT_URL",
    "Bundle",
    "BundleError",
    "BundleImportError",
    "BundleSchemaTooNewError",
    "BundleVerifyError",
    "Importer",
    "ImportResult",
    "LocalDataExistsError",
    "SUPPORTED_DB_MIGRATION_MAX",
    "SUPPORTED_MANIFEST_VERSION",
    "read_bundle",
]
