"""US2 tenant-isolation + backward-compat integration tests (FR-011…FR-014, SC-006).

Exercises tenant scoping end-to-end through the Repository (the boundary where
tenancy is enforced) plus the TenantContext resolver, parametrized across the file
and in-memory implementations. Also pins the v0.3.0 upgrade path: a record written
WITHOUT a tenant_id field must read back under tenant "default" (FR-013).
"""

import pytest

from attestix.storage import FileRepository, MemoryRepository
from attestix.tenancy import DEFAULT_TENANT, TenantContext, default_tenant_context, resolve_tenant

COLLECTION = "identities"
ID_FIELD = "agent_id"

REPO_FACTORIES = {"file": FileRepository, "memory": MemoryRepository}


@pytest.fixture(params=list(REPO_FACTORIES), ids=list(REPO_FACTORIES))
def repo(request):
    return REPO_FACTORIES[request.param]()


def _rec(agent_id, **extra):
    r = {ID_FIELD: agent_id, "display_name": agent_id}
    r.update(extra)
    return r


# --- Cross-tenant isolation (SC-006) --------------------------------------


def test_no_cross_tenant_read(repo):
    repo.create(COLLECTION, _rec("a:1"), tenant_id="acme", id_field=ID_FIELD)
    repo.create(COLLECTION, _rec("g:1"), tenant_id="globex", id_field=ID_FIELD)

    # acme context sees only acme.
    assert repo.get(COLLECTION, "a:1", tenant_id="acme", id_field=ID_FIELD) is not None
    assert repo.get(COLLECTION, "g:1", tenant_id="acme", id_field=ID_FIELD) is None
    assert [r[ID_FIELD] for r in repo.list(COLLECTION, tenant_id="acme", id_field=ID_FIELD)] == ["a:1"]

    # globex context sees only globex.
    assert repo.get(COLLECTION, "a:1", tenant_id="globex", id_field=ID_FIELD) is None
    assert [r[ID_FIELD] for r in repo.list(COLLECTION, tenant_id="globex", id_field=ID_FIELD)] == ["g:1"]


def test_same_id_distinct_per_tenant(repo):
    repo.create(COLLECTION, _rec("shared", owner="acme"), tenant_id="acme", id_field=ID_FIELD)
    repo.create(COLLECTION, _rec("shared", owner="globex"), tenant_id="globex", id_field=ID_FIELD)
    assert repo.get(COLLECTION, "shared", tenant_id="acme", id_field=ID_FIELD)["owner"] == "acme"
    assert repo.get(COLLECTION, "shared", tenant_id="globex", id_field=ID_FIELD)["owner"] == "globex"


# --- Default-tenant parity (FR-011, FR-014) -------------------------------


def test_default_tenant_is_implicit(repo):
    repo.create(COLLECTION, _rec("a:1"), id_field=ID_FIELD)  # no tenant_id
    # Visible under explicit "default" and under the omitted-tenant default.
    assert repo.get(COLLECTION, "a:1", tenant_id=DEFAULT_TENANT, id_field=ID_FIELD) is not None
    assert repo.get(COLLECTION, "a:1", id_field=ID_FIELD) is not None
    # And invisible to a named tenant.
    assert repo.get(COLLECTION, "a:1", tenant_id="acme", id_field=ID_FIELD) is None


# --- Backward compat: legacy records with NO tenant_id (FR-013) -----------


def test_legacy_record_without_tenant_reads_as_default():
    """A v0.3.0 on-disk record (no tenant_id) loads as tenant 'default', no error.

    This is the zero-migration upgrade guarantee (SC-002). Only the file
    repository represents the legacy on-disk shape.
    """
    repo = FileRepository()
    doc = repo.load_document(COLLECTION)
    # Pre-upgrade record: NO tenant_id key at all.
    doc["agents"].append({ID_FIELD: "legacy:1", "display_name": "old"})
    repo.save_document(COLLECTION, doc)

    got = repo.get(COLLECTION, "legacy:1", id_field=ID_FIELD)
    assert got is not None
    assert got[ID_FIELD] == "legacy:1"
    listed = repo.list(COLLECTION, tenant_id=DEFAULT_TENANT, id_field=ID_FIELD)
    assert any(r[ID_FIELD] == "legacy:1" for r in listed)
    # And a named tenant must NOT see the legacy default-tenant record.
    assert repo.get(COLLECTION, "legacy:1", tenant_id="acme", id_field=ID_FIELD) is None


def test_mixed_legacy_and_tenanted_records():
    """Legacy (no tenant_id) and new tenant-tagged records coexist correctly."""
    repo = FileRepository()
    doc = repo.load_document(COLLECTION)
    doc["agents"].append({ID_FIELD: "legacy:1", "display_name": "old"})  # default
    repo.save_document(COLLECTION, doc)
    repo.create(COLLECTION, _rec("a:1"), tenant_id="acme", id_field=ID_FIELD)

    default_ids = {r[ID_FIELD] for r in repo.list(COLLECTION, id_field=ID_FIELD)}
    acme_ids = {r[ID_FIELD] for r in repo.list(COLLECTION, tenant_id="acme", id_field=ID_FIELD)}
    assert default_ids == {"legacy:1"}
    assert acme_ids == {"a:1"}


# --- TenantContext resolver (T046 default REST resolution) ----------------


def test_default_context_is_default_tenant():
    ctx = default_tenant_context()
    assert ctx.tenant_id == DEFAULT_TENANT
    assert ctx.require_tenant() == "default"


def test_resolve_tenant_from_header():
    ctx = resolve_tenant({"X-Attestix-Tenant": "acme"})
    assert ctx.tenant_id == "acme"
    # Case-insensitive header key.
    ctx2 = resolve_tenant({"x-attestix-tenant": "globex"})
    assert ctx2.tenant_id == "globex"


def test_resolve_tenant_missing_header_is_default():
    assert resolve_tenant({}).tenant_id == DEFAULT_TENANT
    assert resolve_tenant(None).tenant_id == DEFAULT_TENANT
    # A blank value does not silently become a tenant.
    assert resolve_tenant({"X-Attestix-Tenant": "   "}).tenant_id == DEFAULT_TENANT


def test_blank_tenant_context_rejects_require():
    with pytest.raises(ValueError):
        TenantContext(tenant_id="").require_tenant()
