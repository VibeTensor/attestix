"""In-memory :class:`Repository` for tests and ephemeral / smoke deployments.

``MemoryRepository`` keeps records in process memory only. It implements the same
contract as :class:`FileRepository` and is the second implementation the shared
contract suite parametrizes over, proving Liskov substitution at the boundary
without touching disk (and without requiring an external backend such as
Postgres). It is also a convenient stand-in for the cloud's smoke tests.
"""

from copy import deepcopy
from typing import Dict, List, Optional, Tuple

from storage.repository import DEFAULT_TENANT, Repository


class MemoryRepository(Repository):
    """Volatile, process-local persistence satisfying the Repository contract."""

    def __init__(self) -> None:
        # (collection, tenant_id) -> list of records
        self._store: Dict[Tuple[str, str], List[dict]] = {}

    def _bucket(self, collection: str, tenant_id: str) -> List[dict]:
        return self._store.setdefault((collection, tenant_id), [])

    def create(
        self,
        collection: str,
        record: dict,
        *,
        tenant_id: str = DEFAULT_TENANT,
        id_field: str = "id",
    ) -> dict:
        stored = deepcopy(record)
        stored["tenant_id"] = tenant_id
        self._bucket(collection, tenant_id).append(stored)
        return deepcopy(stored)

    def get(
        self,
        collection: str,
        record_id: str,
        *,
        tenant_id: str = DEFAULT_TENANT,
        id_field: str = "id",
    ) -> Optional[dict]:
        for rec in self._bucket(collection, tenant_id):
            if rec.get(id_field) == record_id:
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
        results: List[dict] = []
        for rec in self._bucket(collection, tenant_id):
            if filters and any(rec.get(k) != v for k, v in filters.items()):
                continue
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
        bucket = self._bucket(collection, tenant_id)
        for idx, rec in enumerate(bucket):
            if rec.get(id_field) == record_id:
                stored = deepcopy(record)
                stored["tenant_id"] = tenant_id
                bucket[idx] = stored
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
        bucket = self._bucket(collection, tenant_id)
        for idx, rec in enumerate(bucket):
            if rec.get(id_field) == record_id:
                del bucket[idx]
                return True
        return False
