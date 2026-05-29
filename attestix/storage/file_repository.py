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

import atexit
import os
from copy import deepcopy
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

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


#: Recognized durability modes (``durability`` arg / ``ATTESTIX_DURABILITY`` env).
DURABILITY_SAFE = "safe"
DURABILITY_FAST = "fast"
_DURABILITY_MODES = (DURABILITY_SAFE, DURABILITY_FAST)


def _resolve_durability(durability: Optional[str]) -> str:
    """Resolve the effective durability mode (arg > env > ``safe`` default)."""
    choice = durability or os.environ.get("ATTESTIX_DURABILITY") or DURABILITY_SAFE
    choice = str(choice).strip().lower()
    if choice not in _DURABILITY_MODES:
        raise ValueError(
            f"Unknown durability mode {choice!r}. "
            f"Expected one of: {', '.join(_DURABILITY_MODES)}."
        )
    return choice


class FileRepository(Repository):
    """JSON-file persistence reproducing v0.3.0 on-disk behavior.

    Each collection is a single JSON document loaded/saved through the shared
    ``config._safe_load`` / ``config._safe_save`` helpers (filelock + atomic
    rename). This is the default backend: a fresh install with no configuration
    uses it, and ``config.load_*`` / ``config.save_*`` remain as thin public shims
    over the same helpers so external callers are unaffected.

    Performance (issue #108)
    ------------------------
    A write-through *document cache* keeps the parsed JSON document for each file
    in memory, validated against the file's ``(st_mtime_ns, st_size)`` so an
    out-of-band write (another process, or a direct ``config._safe_save``) is
    detected and the cache transparently reloaded. This removes the redundant
    full-file *reads* that previously happened on every ``create`` / ``list`` /
    ``_load_list`` — most importantly the audit-emit path, which read the whole
    ``audit.json`` twice per event (once to find the chain head, once to append).
    Paired with :meth:`append_to_document` (used by the credential issuance hot
    path) and :meth:`last_record` (used by the audit emitter), a pure append no
    longer copies the whole — and ever-growing — collection, so an N-append loop
    is linear in N instead of quadratic. The on-disk format, file locations,
    locking, and atomic-write guarantees are unchanged (FR-002, SC-001/SC-002).

    Durability modes (issue #108)
    -----------------------------
    - ``"safe"`` (default): every mutating call flushes to disk immediately, with
      the v0.3.0 backup + atomic-rename guarantees. No behavior change.
    - ``"fast"``: opt-in batched durability for high-throughput issuance. Mutating
      calls update the in-memory document and mark it dirty; the disk write is
      deferred until :meth:`flush` or process exit (an ``atexit`` hook). This also
      amortizes the per-write ``json.dump``, at the cost of losing at most the
      un-flushed tail on a hard crash. Speed is therefore strictly opt-in; the
      default stays crash-safe.

    Select ``"fast"`` per instance (``FileRepository(durability="fast")``) or
    process-wide via ``ATTESTIX_DURABILITY=fast``.
    """

    def __init__(self, durability: Optional[str] = None) -> None:
        self._durability = _resolve_durability(durability)
        # file_path(str) -> (document, stat_token). stat_token is
        # (st_mtime_ns, st_size) of the file the document was last read/written
        # from, or None when the file did not exist at read time.
        self._doc_cache: Dict[str, Tuple[dict, Optional[Tuple[int, int]]]] = {}
        # file paths with un-flushed in-memory writes (fast mode only).
        self._dirty: Set[str] = set()
        if self._durability == DURABILITY_FAST:
            # Best-effort: never lose a batched tail on a clean interpreter exit.
            atexit.register(self.flush)

    # --- document cache -------------------------------------------------------

    @staticmethod
    def _stat_token(file_path) -> Optional[Tuple[int, int]]:
        """Return ``(st_mtime_ns, st_size)`` for ``file_path`` or ``None``."""
        try:
            st = os.stat(file_path)
        except OSError:
            return None
        return (st.st_mtime_ns, st.st_size)

    def _cached_document(self, file_path, default: dict) -> dict:
        """Return the *live* cached document for ``file_path`` (reload if stale).

        Returns the cache's own object (not a copy): internal callers mutate it in
        place and then :meth:`_write_document` to persist. Public reads
        (:meth:`load_document`, :meth:`get`, :meth:`list`) copy before returning so
        the cache cannot be corrupted by a caller mutating a read result.
        """
        key = str(file_path)
        cached = self._doc_cache.get(key)
        if cached is not None:
            doc, token = cached
            # A dirty (un-flushed) document is authoritative regardless of disk.
            if key in self._dirty:
                return doc
            # Otherwise trust the cache only while the file is byte-identical to
            # what we last saw (cheap stat, not a full re-read).
            if token == self._stat_token(file_path):
                return doc
        # Cold or stale: read through the shared safe loader (filelock + recovery).
        doc = config._safe_load(file_path, default)
        self._doc_cache[key] = (doc, self._stat_token(file_path))
        self._dirty.discard(key)
        return doc

    def _write_document(self, file_path, data: dict) -> None:
        """Persist ``data`` for ``file_path`` honoring the durability mode."""
        key = str(file_path)
        if self._durability == DURABILITY_FAST:
            # Defer the disk write; the in-memory doc is authoritative until flush.
            self._doc_cache[key] = (data, None)
            self._dirty.add(key)
            return
        config._safe_save(file_path, data)
        # Refresh the stat token to the just-written file so subsequent reads hit
        # the cache instead of re-parsing.
        self._doc_cache[key] = (data, self._stat_token(file_path))
        self._dirty.discard(key)

    def flush(self) -> None:
        """Flush all pending in-memory writes to disk (no-op in ``safe`` mode).

        Idempotent. Call this to make a batch of ``fast``-mode writes durable
        without exiting the process (e.g. at the end of a bulk issuance run).
        """
        if not self._dirty:
            return
        for key in list(self._dirty):
            doc, _ = self._doc_cache[key]
            file_path = Path(key)
            config._safe_save(file_path, doc)
            self._doc_cache[key] = (doc, self._stat_token(file_path))
        self._dirty.clear()

    # --- document API (public shims back FR-002 load_*/save_* helpers) --------

    def load_document(self, collection: str) -> dict:
        """Load the entire JSON document for ``collection`` (whole-file load).

        This is the backing for ``config.load_*`` shims: it returns the same dict
        v0.3.0 ``load_*`` returned (the full document, default-populated), so
        external callers relying on the public ``config`` functions are unaffected.
        Served from the document cache when the on-disk file is unchanged; a deep
        copy is returned so a caller mutating the result cannot corrupt the cache
        (the historical contract: each ``load_*`` returned a fresh dict).
        """
        file_path, _, default = _resolve(collection)
        return deepcopy(self._cached_document(file_path, default))

    def save_document(self, collection: str, data: dict) -> None:
        """Persist the entire JSON document for ``collection`` (whole-file save)."""
        file_path, _, _ = _resolve(collection)
        self._write_document(file_path, data)

    def append_to_document(self, collection: str, record: dict) -> dict:
        """Append ``record`` to ``collection``'s primary list and persist (O(1)).

        Performance (issue #108): the document API's :meth:`load_document` returns a
        deep copy for caller isolation, so the historical
        ``load -> list.append -> save`` issuance pattern paid an O(N) copy of the
        whole (growing) collection on every single append — O(N^2) over a loop.
        This appends one record directly to the *live* cached list and writes
        through, so a pure append never copies the existing records.

        Unlike :meth:`create`, the record is written **verbatim** (no ``tenant_id``
        tagging), preserving the exact on-disk shape of the legacy document
        collections (``credentials``, ``identities``, ...). Returns the stored
        record (the same object that was appended).
        """
        data, records, file_path, _ = self._load_list(collection)
        records.append(record)
        self._save(file_path, data)
        return record

    def last_record(
        self,
        collection: str,
        *,
        tenant_id: str = DEFAULT_TENANT,
    ) -> Optional[dict]:
        """Return the last record for ``tenant_id`` without copying the collection.

        Hot-path accessor for append-chained collections (the audit log): the
        emitter needs only the chain head to extend the chain, so copying the
        entire (growing) event list on every emit — as a full :meth:`list` would —
        is part of what made issuance O(N^2) (issue #108). Walks the live cached
        list from the tail and returns a copy of just the one matching record (or
        ``None``). Single-tenant (the self-host default) hits the last element
        immediately.
        """
        _, records, _, _ = self._load_list(collection)
        for rec in reversed(records):
            if _tenant_of(rec) == tenant_id:
                return deepcopy(rec)
        return None

    def _load_list(self, collection: str):
        file_path, list_key, default = _resolve(collection)
        data = self._cached_document(file_path, default)
        return data, data.setdefault(list_key, []), file_path, list_key

    def _save(self, file_path, data) -> None:
        self._write_document(file_path, data)

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
        # The stored dict is now owned by the cache; return a copy.
        return deepcopy(stored)

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
                # Copy so a caller mutating the result cannot corrupt the cache.
                return deepcopy(rec)
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
            # Copy so a caller mutating a result cannot corrupt the cache.
            results.append(deepcopy(rec))
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
                # deepcopy so a caller mutating ``record`` after the call cannot
                # reach into the cache through the shared reference.
                stored = deepcopy(record)
                # Persist the canonical id so an id-less payload stays queryable.
                stored[id_field] = record_id
                stored["tenant_id"] = tenant_id
                records[idx] = stored
                self._save(file_path, data)
                return deepcopy(stored)
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
