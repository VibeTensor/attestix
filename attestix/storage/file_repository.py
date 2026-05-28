"""Default file-backed :class:`Repository` (v0.3.0 behavior, byte-for-byte).

``FileRepository`` is the OSS / self-host default. It wraps the existing
``config.py`` machinery (``_safe_load`` / ``_safe_save`` with ``filelock`` and
atomic temp-then-rename), mapping each logical *collection* to its current JSON
file under ``DATA_DIR``. The on-disk format, file locations, locking, and
atomic-write guarantees are exactly those of v0.3.0 (FR-002, SC-001/SC-002).

The module reads the ``*_FILE`` paths from ``config`` *lazily* on each call rather
than caching them at import time, so the test suite's ``conftest.py`` (which
monkeypatches ``config.IDENTITIES_FILE`` etc. onto a temp dir) keeps working
unchanged.

Tenant scoping is applied as a thin in-memory filter over the loaded list so that
the default single-tenant install behaves identically to v0.3.0: every legacy
record (no ``tenant_id``) is treated as tenant ``"default"`` (FR-013), and a caller
that never sets a tenant uses ``"default"`` throughout (FR-014).
"""

from copy import deepcopy
from typing import List, Optional

from attestix import config
from attestix.storage.repository import DEFAULT_TENANT, Repository

#: Maps a logical collection name to the metadata needed to read/write it in the
#: legacy file layout: the ``config`` attribute holding the file path, the
#: top-level JSON key holding the record list, and the default document written
#: when the file does not yet exist (mirrors ``config.load_*`` defaults exactly).
_COLLECTIONS = {
    "identities": ("IDENTITIES_FILE", "agents", {"agents": []}),
    "credentials": ("CREDENTIALS_FILE", "credentials", {"credentials": []}),
    "delegations": ("DELEGATIONS_FILE", "delegations", {"delegations": []}),
    "compliance": (
        "COMPLIANCE_FILE",
        "profiles",
        {"profiles": [], "assessments": [], "declarations": []},
    ),
    "reputation": (
        "REPUTATION_FILE",
        "interactions",
        {"interactions": [], "scores": {}},
    ),
    "provenance": (
        "PROVENANCE_FILE",
        "entries",
        {"entries": [], "audit_log": []},
    ),
    "anchors": ("ANCHORS_FILE", "anchors", {"anchors": []}),
    # v0.4.0 US2: structured audit events (one document, hash-chained per tenant).
    "audit": ("AUDIT_FILE", "events", {"events": []}),
    # v0.4.0 US3: idempotency keys (24h TTL, minimal stored representation).
    "idempotency": ("IDEMPOTENCY_FILE", "keys", {"keys": []}),
}


def _resolve(collection: str):
    """Return ``(file_path, list_key, default_doc)`` for a known collection."""
    if collection not in _COLLECTIONS:
        raise KeyError(
            f"Unknown repository collection {collection!r}. "
            f"Known collections: {sorted(_COLLECTIONS)}"
        )
    file_attr, list_key, default = _COLLECTIONS[collection]
    # Read the path from config at call time so test monkeypatching is honored.
    # deepcopy the default so the shared template (and its nested lists/dicts) is
    # never mutated or aliased into loaded data — matching v0.3.0 load_* which
    # passed a fresh dict literal on every call.
    return getattr(config, file_attr), list_key, deepcopy(default)


def _tenant_of(record: dict) -> str:
    """Return a record's tenant, treating a missing field as ``"default"`` (FR-013)."""
    return record.get("tenant_id", DEFAULT_TENANT)


class FileRepository(Repository):
    """JSON-file persistence reproducing v0.3.0 on-disk behavior.

    Each collection is a single JSON document loaded/saved through the shared
    ``config._safe_load`` / ``config._safe_save`` helpers (filelock + atomic
    rename). This is the default backend: a fresh install with no configuration
    uses it, and ``config.load_*`` / ``config.save_*`` remain as thin public shims
    over the same helpers so external callers are unaffected.
    """

    def load_document(self, collection: str) -> dict:
        """Load the entire JSON document for ``collection`` (whole-file load).

        This is the backing for ``config.load_*`` shims: it returns the same dict
        v0.3.0 ``load_*`` returned (the full document, default-populated), so
        external callers relying on the public ``config`` functions are unaffected.
        """
        file_path, list_key, default = _resolve(collection)
        return config._safe_load(file_path, default)

    def save_document(self, collection: str, data: dict) -> None:
        """Persist the entire JSON document for ``collection`` (whole-file save)."""
        file_path, _, _ = _resolve(collection)
        config._safe_save(file_path, data)

    def _load_list(self, collection: str):
        file_path, list_key, default = _resolve(collection)
        data = config._safe_load(file_path, default)
        return data, data.setdefault(list_key, []), file_path, list_key

    def _save(self, file_path, data) -> None:
        config._safe_save(file_path, data)

    def create(
        self,
        collection: str,
        record: dict,
        *,
        tenant_id: str = DEFAULT_TENANT,
        id_field: str = "id",
    ) -> dict:
        if id_field not in record:
            raise ValueError(
                f"record must include the id field {id_field!r} on create"
            )
        data, records, file_path, _ = self._load_list(collection)
        stored = dict(record)
        # Tag the record with its tenant. The field defaults to "default" so the
        # on-disk shape is a strict superset of v0.3.0 (Complexity Tracking item).
        stored["tenant_id"] = tenant_id
        records.append(stored)
        self._save(file_path, data)
        return stored

    def get(
        self,
        collection: str,
        record_id: str,
        *,
        tenant_id: str = DEFAULT_TENANT,
        id_field: str = "id",
    ) -> Optional[dict]:
        _, records, _, _ = self._load_list(collection)
        for rec in records:
            if rec.get(id_field) == record_id and _tenant_of(rec) == tenant_id:
                return rec
        return None

    def list(
        self,
        collection: str,
        *,
        tenant_id: str = DEFAULT_TENANT,
        filters: Optional[dict] = None,
        limit: Optional[int] = None,
        id_field: str = "id",
    ) -> List[dict]:
        _, records, _, _ = self._load_list(collection)
        results: List[dict] = []
        for rec in records:
            if _tenant_of(rec) != tenant_id:
                continue
            if filters and any(rec.get(k) != v for k, v in filters.items()):
                continue
            results.append(rec)
            if limit is not None and len(results) >= limit:
                break
        return results

    def update(
        self,
        collection: str,
        record_id: str,
        record: dict,
        *,
        tenant_id: str = DEFAULT_TENANT,
        id_field: str = "id",
    ) -> Optional[dict]:
        if id_field in record and record[id_field] != record_id:
            raise ValueError(
                f"{id_field!r} in record ({record[id_field]!r}) must match "
                f"record_id {record_id!r}; update must not change identity"
            )
        data, records, file_path, _ = self._load_list(collection)
        for idx, rec in enumerate(records):
            if rec.get(id_field) == record_id and _tenant_of(rec) == tenant_id:
                stored = dict(record)
                # Persist the canonical id so an id-less payload stays queryable.
                stored[id_field] = record_id
                stored["tenant_id"] = tenant_id
                records[idx] = stored
                self._save(file_path, data)
                return stored
        return None

    def delete(
        self,
        collection: str,
        record_id: str,
        *,
        tenant_id: str = DEFAULT_TENANT,
        id_field: str = "id",
    ) -> bool:
        data, records, file_path, _ = self._load_list(collection)
        for idx, rec in enumerate(records):
            if rec.get(id_field) == record_id and _tenant_of(rec) == tenant_id:
                del records[idx]
                self._save(file_path, data)
                return True
        return False
