"""Repository contract: the persistence boundary the service layer depends on.

The ``Repository`` abstract base class defines the persistence seam introduced in
v0.4.0. Every concrete implementation (the default :class:`FileRepository`, an
in-memory test double, or an optional Postgres adapter) MUST satisfy the same
contract test suite (``tests/contract/test_repository_contract.py``), enforcing
Liskov substitution at the boundary.

A *collection* is identified by name (one of the seven existing entity families:
``identities``, ``credentials``, ``delegations``, ``compliance``, ``reputation``,
``provenance``, ``anchors``). Records are plain ``dict`` objects (the engine's
existing in-memory shape). Tenant scoping is enforced at this boundary: a record
created under one ``tenant_id`` is never returned under another.

This module is additive (v0.3.0 -> v0.4.0 MINOR). The default install resolves to
:class:`FileRepository`, which reproduces v0.3.0 on-disk behavior byte-for-byte.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

#: The default tenant. A record with no ``tenant_id`` is read as this tenant
#: (FR-013), so v0.3.0 data remains visible after upgrade with no migration.
DEFAULT_TENANT = "default"


class Repository(ABC):
    """Persistence boundary for the service layer.

    Replaces direct ``config.load_*`` / ``config.save_*`` calls in services with a
    create / get / list / update / delete contract, scoped by ``tenant_id``.

    Contract invariants (asserted against every implementation by
    ``tests/contract/test_repository_contract.py``):

    - **Round-trip**: a record stored via :meth:`create` is returned unchanged
      (modulo storage-assigned metadata) by :meth:`get`.
    - **Tenant isolation**: a record created under tenant A is never returned by
      :meth:`get` / :meth:`list` under tenant B (FR-012).
    - **Default tenant**: omitting ``tenant_id`` is equivalent to passing
      ``"default"`` (FR-011, FR-014).
    - **Legacy read**: a record persisted without a ``tenant_id`` field is returned
      under tenant ``"default"`` (FR-013).
    - **Idempotent delete**: :meth:`delete` of a missing id returns ``False`` and
      does not raise.
    - **Id integrity**: :meth:`create` rejects a record missing ``id_field`` and
      :meth:`update` rejects a record whose ``id_field`` disagrees with
      ``record_id`` (both raise ``ValueError``), so identity cannot be corrupted.
    - **No cross-tenant merge**: an identical ``record_id`` under two tenants is two
      distinct records.
    - **Durability / atomicity**: a failed write surfaces an error and does not
      partially corrupt other records.

    Records are identified within a collection by the value of their ``id_field``
    key (``"agent_id"`` for identities, ``"id"`` for credentials, etc.). The
    ``id_field`` is supplied per call so the abstraction stays uniform across the
    engine's heterogeneous entity shapes without forcing a schema change on disk.
    """

    @abstractmethod
    def create(
        self,
        collection: str,
        record: dict,
        *,
        tenant_id: str = DEFAULT_TENANT,
        id_field: str = "id",
    ) -> dict:
        """Persist a new record into ``collection`` under ``tenant_id``.

        Returns the stored record. The returned record is tenant-tagged
        (``tenant_id`` is set on the persisted copy); callers MUST treat the return
        value as authoritative rather than the input ``record``.

        ``record`` MUST contain ``id_field``; implementations raise ``ValueError``
        if it is absent (an id-less record would be unqueryable). This layer does
        not deduplicate: ``create`` does not check whether the same ``id_field``
        value already exists under ``tenant_id`` and does not raise/return the
        existing record on collision — callers needing upsert semantics use
        :meth:`update`, and idempotency-by-key is enforced at a higher layer.
        """
        raise NotImplementedError

    @abstractmethod
    def get(
        self,
        collection: str,
        record_id: str,
        *,
        tenant_id: str = DEFAULT_TENANT,
        id_field: str = "id",
    ) -> Optional[dict]:
        """Return the record in ``collection`` whose ``id_field`` equals
        ``record_id`` within ``tenant_id``, or ``None`` if absent."""
        raise NotImplementedError

    @abstractmethod
    def list(
        self,
        collection: str,
        *,
        tenant_id: str = DEFAULT_TENANT,
        filters: Optional[dict] = None,
        limit: Optional[int] = None,
        id_field: str = "id",
    ) -> List[dict]:
        """Return records in ``collection`` for ``tenant_id``.

        ``filters`` is an optional mapping of exact-match field constraints; records
        not matching every filter are excluded. ``limit`` caps the number returned.
        """
        raise NotImplementedError

    @abstractmethod
    def update(
        self,
        collection: str,
        record_id: str,
        record: dict,
        *,
        tenant_id: str = DEFAULT_TENANT,
        id_field: str = "id",
    ) -> Optional[dict]:
        """Replace the record identified by ``record_id`` within ``tenant_id``.

        Returns the stored record, or ``None`` if no matching record exists in the
        tenant scope. If ``record`` carries ``id_field``, it MUST equal
        ``record_id`` — implementations raise ``ValueError`` rather than silently
        change a record's identity. The persisted copy always carries
        ``id_field == record_id`` so an id-less payload stays queryable.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(
        self,
        collection: str,
        record_id: str,
        *,
        tenant_id: str = DEFAULT_TENANT,
        id_field: str = "id",
    ) -> bool:
        """Remove the record identified by ``record_id`` within ``tenant_id``.

        Returns ``True`` if a record was removed, ``False`` if none matched.
        Deleting a missing record MUST NOT raise (idempotent delete).
        """
        raise NotImplementedError
