"""Read and verify Attestix portability bundles (the M6 cloud→OSS round-trip).

A bundle is a USTAR + gzip tarball containing:

* ``manifest.json`` — JCS-canonical body describing the bundle (workspace,
  exported_at, per-table {row_count, bytes, sha256}, core_version,
  ``schemas.db_migration_max``, etc.).
* ``manifest.sha256`` — hex SHA-256 of ``manifest.json`` bytes (the canonical
  form the exporter wrote), with a trailing newline.
* ``<table>.jsonl`` — one JCS-canonical JSON object per line, snake_cased keys
  matching the cloud Postgres column names.

The reader:

* Parses the tarball with the stdlib :mod:`tarfile` (no new deps).
* Recomputes the SHA-256 of every ``<table>.jsonl`` and compares against the
  manifest entry.
* Recomputes the manifest's own SHA-256 by **re-canonicalising the parsed
  manifest** through :func:`attestix.auth.crypto.canonicalize_json` (the same
  RFC-8785 helper the signer and audit chain rely on) and compares against the
  side-car. Refusing to introduce a second canonicaliser is a deliberate
  constraint: the cloud exporter uses the equivalent JS routine, and any
  divergence here breaks the round-trip integrity guarantee.
* Refuses bundles whose ``schemas.db_migration_max`` is newer than this OSS
  build knows how to import — pointing the operator at the upgrade docs.
"""

from __future__ import annotations

import hashlib
import io
import json
import tarfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Tuple, Union

from attestix.auth.crypto import canonicalize_json

#: The bundle wire-format URL the exporter stamps into every manifest.
BUNDLE_FORMAT_URL = "https://attestix.io/spec/bundle/v1"

#: The manifest_version this OSS build understands.
SUPPORTED_MANIFEST_VERSION = "1.0"

#: The highest cloud DB migration this OSS build knows how to import. Bumping
#: this requires updating :mod:`attestix.portability.importer` to map any new
#: columns or tables introduced in the migration.
SUPPORTED_DB_MIGRATION_MAX = "0010"

#: Maximum bundle size we will load into memory (256 MiB). The OSS importer is
#: pure-stdlib and stages each table into memory; very large enterprise tenants
#: should drive the (future) streaming importer instead of this one.
MAX_BUNDLE_BYTES = 256 * 1024 * 1024

#: Maximum single-file size inside the bundle (128 MiB).
MAX_MEMBER_BYTES = 128 * 1024 * 1024


class BundleError(Exception):
    """Base error for portability bundle problems."""


class BundleVerifyError(BundleError):
    """Raised when a bundle fails integrity verification (sha mismatch)."""


class BundleSchemaTooNewError(BundleError):
    """Raised when the bundle's schema version is newer than this OSS build supports."""


@dataclass(frozen=True)
class TableInfo:
    """Metadata about a single table inside a bundle (mirrors the manifest entry)."""

    name: str
    format: str
    row_count: int
    bytes: int
    sha256: str


@dataclass
class Bundle:
    """Parsed Attestix portability bundle.

    Attributes:
        path: Filesystem path the bundle was read from.
        manifest: Parsed ``manifest.json`` body.
        manifest_sha256: Hex digest read from ``manifest.sha256`` (without the
            trailing newline).
        tables: Per-table metadata indexed by table name.
        raw_payloads: Raw bytes of every member file in the bundle (the body
            the manifest's per-table sha was computed over). Used for both
            verification and row streaming. Not part of the public API.
    """

    path: Path
    manifest: dict
    manifest_sha256: str
    tables: Dict[str, TableInfo]
    raw_payloads: Dict[str, bytes] = field(repr=False)

    # ----- Metadata convenience accessors ------------------------------------

    @property
    def manifest_version(self) -> str:
        return str(self.manifest.get("manifest_version", ""))

    @property
    def bundle_format(self) -> str:
        return str(self.manifest.get("attestix_bundle_format", ""))

    @property
    def workspace(self) -> dict:
        return dict(self.manifest.get("workspace", {}))

    @property
    def exported_at(self) -> str:
        return str(self.manifest.get("exported_at", ""))

    @property
    def exported_by(self) -> dict:
        return dict(self.manifest.get("exported_by", {}))

    @property
    def core_version(self) -> str:
        return str(self.manifest.get("core_version", ""))

    @property
    def db_migration_max(self) -> str:
        return str(self.manifest.get("schemas", {}).get("db_migration_max", ""))

    @property
    def table_names(self) -> List[str]:
        return list(self.tables.keys())

    # ----- Row iteration -----------------------------------------------------

    def iter_rows(self, name: str) -> Iterator[dict]:
        """Yield each row of ``<name>.jsonl`` as a dict.

        Reads from the in-memory payload captured during :func:`read_bundle`.
        Empty payloads yield nothing (row_count==0 is valid).
        """
        if name not in self.tables:
            raise KeyError(f"table {name!r} not present in bundle")
        body = self.raw_payloads[f"{name}.jsonl"]
        if not body:
            return
        # The exporter writes "<line>\n<line>\n..." (trailing newline). Splitting
        # on '\n' and skipping empty tail handles the format without a special case.
        for line in body.decode("utf-8").split("\n"):
            if not line:
                continue
            yield json.loads(line)

    def rows(self, name: str) -> List[dict]:
        """Materialise all rows for ``name`` (convenience for small tables)."""
        return list(self.iter_rows(name))

    # ----- Verification ------------------------------------------------------

    def verify_table_sha(self, name: str) -> bool:
        """Recompute the SHA-256 of ``<name>.jsonl`` and compare to the manifest.

        Returns ``True`` iff the on-disk bytes match the manifest entry.
        """
        if name not in self.tables:
            raise KeyError(f"table {name!r} not present in bundle")
        info = self.tables[name]
        body = self.raw_payloads[f"{name}.jsonl"]
        actual = hashlib.sha256(body).hexdigest()
        return actual == info.sha256

    def verify_manifest(self) -> bool:
        """Recompute SHA-256(canonicalise(manifest)) and compare to ``manifest.sha256``.

        Re-canonicalises the parsed manifest dict through the existing
        :func:`canonicalize_json` so this OSS build does not introduce a second
        canonicaliser. The cloud exporter writes the manifest bytes by piping
        the same canonical form through ``createHash('sha256')``; the two must
        match byte-for-byte if neither side has drifted.
        """
        canonical = canonicalize_json(self.manifest)
        actual = hashlib.sha256(canonical).hexdigest()
        return actual == self.manifest_sha256

    def verify(self) -> Tuple[bool, List[str]]:
        """Run every integrity check and return ``(ok, problems)``.

        ``problems`` is a list of human-readable strings describing each failure;
        an empty list means the bundle verified cleanly.
        """
        problems: List[str] = []
        if not self.verify_manifest():
            problems.append(
                f"manifest sha256 mismatch (expected {self.manifest_sha256!r}, "
                f"recomputed differently — manifest body has been tampered or "
                f"this build's canonicaliser drifted from the exporter's)"
            )
        for name in self.tables:
            if not self.verify_table_sha(name):
                info = self.tables[name]
                actual = hashlib.sha256(self.raw_payloads[f"{name}.jsonl"]).hexdigest()
                problems.append(
                    f"table {name!r} sha256 mismatch (manifest={info.sha256[:16]}…, "
                    f"actual={actual[:16]}…)"
                )
        return (not problems, problems)

    # ----- Schema guard ------------------------------------------------------

    def check_schema_compatibility(
        self, supported_max: str = SUPPORTED_DB_MIGRATION_MAX
    ) -> None:
        """Raise :class:`BundleSchemaTooNewError` if the bundle is too new.

        Migrations are compared lexicographically over their zero-padded numeric
        prefix (``"0010"`` < ``"0011"``). A bundle stamped with an older or equal
        migration is accepted; newer bundles refuse with a pointer to the
        upgrade docs so an out-of-date OSS install never silently drops new
        columns or tables.
        """
        ours = supported_max
        theirs = self.db_migration_max
        if not theirs:
            raise BundleError(
                "manifest is missing schemas.db_migration_max — bundle is not "
                f"a {BUNDLE_FORMAT_URL} payload or was produced by an unreleased "
                "exporter"
            )
        if theirs > ours:
            raise BundleSchemaTooNewError(
                f"Bundle was exported under cloud DB migration {theirs!r} but this "
                f"Attestix build only knows how to import up to {ours!r}. "
                f"Upgrade `attestix` (`pip install -U attestix`) and re-run the "
                f"import. See https://attestix.io/docs/portability/import "
                f"for the supported-migration matrix."
            )


# ---------------------------------------------------------------------------
# Top-level reader
# ---------------------------------------------------------------------------


def read_bundle(path: Union[str, Path]) -> Bundle:
    """Open ``path`` and return a parsed :class:`Bundle`.

    The file is opened as ``r:gz`` so any USTAR-compatible tar stream is
    accepted. Member sizes and the total bundle size are capped (see
    :data:`MAX_BUNDLE_BYTES` / :data:`MAX_MEMBER_BYTES`) so a maliciously
    crafted gzip-bomb cannot exhaust memory.

    Raises:
        BundleError: for any structural problem (missing manifest, bad JSON,
            oversize member, no recognisable bundle-format URL).
    """
    p = Path(path)
    if not p.exists():
        raise BundleError(f"bundle file does not exist: {p}")

    size = p.stat().st_size
    if size > MAX_BUNDLE_BYTES:
        raise BundleError(
            f"bundle is {size} bytes; refusing to load (cap {MAX_BUNDLE_BYTES})"
        )

    payloads: Dict[str, bytes] = {}
    try:
        with tarfile.open(p, mode="r:gz") as tar:
            for member in tar.getmembers():
                # Refuse anything that is not a plain file (no dirs, symlinks,
                # hardlinks, devices) so a maliciously crafted bundle cannot
                # smuggle a path-escape via a symlink. The cloud exporter writes
                # only regular files, so legitimate bundles never trip this.
                if not member.isfile():
                    continue
                if member.size > MAX_MEMBER_BYTES:
                    raise BundleError(
                        f"bundle member {member.name!r} is {member.size} bytes; "
                        f"refusing to load (cap {MAX_MEMBER_BYTES})"
                    )
                # Defence-in-depth: reject member names that try to escape the
                # bundle root via "..", absolute paths, or non-ASCII control
                # characters. We never extract to disk (read into memory only)
                # so this is belt-and-braces, but it makes a hostile bundle
                # impossible to mis-route.
                raw = member.name.replace("\\", "/")
                if raw.startswith("/") or ".." in raw.split("/"):
                    raise BundleError(
                        f"bundle member {member.name!r} has a suspicious path; "
                        f"refusing to load"
                    )
                # Use the base name so an exporter that writes "staging/<file>"
                # vs a bare "<file>" both work. The cloud exporter currently
                # writes bare names.
                name = Path(raw).name
                f = tar.extractfile(member)
                if f is None:
                    continue
                payloads[name] = f.read()
    except tarfile.TarError as e:
        raise BundleError(f"not a valid tar.gz bundle: {e}") from e

    if "manifest.json" not in payloads:
        raise BundleError("bundle is missing manifest.json")
    if "manifest.sha256" not in payloads:
        raise BundleError("bundle is missing manifest.sha256")

    try:
        manifest = json.loads(payloads["manifest.json"].decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise BundleError(f"manifest.json is not valid JSON: {e}") from e

    if not isinstance(manifest, dict):
        raise BundleError("manifest.json must be a JSON object")

    fmt = manifest.get("attestix_bundle_format")
    if fmt != BUNDLE_FORMAT_URL:
        raise BundleError(
            f"unrecognised bundle format {fmt!r}; expected {BUNDLE_FORMAT_URL!r}"
        )

    ver = manifest.get("manifest_version")
    if ver != SUPPORTED_MANIFEST_VERSION:
        raise BundleError(
            f"unsupported manifest_version {ver!r}; expected "
            f"{SUPPORTED_MANIFEST_VERSION!r}"
        )

    manifest_sha = payloads["manifest.sha256"].decode("utf-8").strip()
    if len(manifest_sha) != 64 or any(c not in "0123456789abcdef" for c in manifest_sha):
        raise BundleError(
            f"manifest.sha256 side-car is not a 64-char lowercase hex digest: "
            f"{manifest_sha!r}"
        )

    tables: Dict[str, TableInfo] = {}
    for entry in manifest.get("tables", []):
        if not isinstance(entry, dict):
            raise BundleError(f"manifest tables entry is not an object: {entry!r}")
        try:
            info = TableInfo(
                name=str(entry["name"]),
                format=str(entry.get("format", "jsonl")),
                row_count=int(entry["row_count"]),
                bytes=int(entry["bytes"]),
                sha256=str(entry["sha256"]),
            )
        except (KeyError, TypeError, ValueError) as e:
            raise BundleError(f"malformed table entry in manifest: {entry!r} ({e})") from e

        # Each table must have a corresponding <name>.jsonl payload.
        member_name = f"{info.name}.jsonl"
        if member_name not in payloads:
            raise BundleError(
                f"manifest references table {info.name!r} but {member_name!r} is "
                f"missing from the bundle"
            )
        tables[info.name] = info

    return Bundle(
        path=p,
        manifest=manifest,
        manifest_sha256=manifest_sha,
        tables=tables,
        raw_payloads=payloads,
    )
