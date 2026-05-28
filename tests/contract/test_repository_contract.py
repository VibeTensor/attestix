"""Shared Repository contract suite (v0.4.0, FR-004 / SC-003).

This suite is parametrized over EVERY concrete ``Repository`` implementation so
the default ``FileRepository`` and the alternative ``MemoryRepository`` (and any
future Postgres adapter) must pass identical assertions. This enforces Liskov
substitution at the persistence boundary (constitution principle III).

The ``tmp_attestix`` autouse fixture in ``tests/conftest.py`` redirects the file
repository's paths to a temp dir, so the file adapter is exercised against
isolated storage.
"""

import pytest

from attestix.storage import FileRepository, MemoryRepository, Repository

# A representative collection from the seven entity families. The contract is
# uniform across collections, so one is sufficient to exercise the invariants.
COLLECTION = "identities"
ID_FIELD = "agent_id"


def _file_repo():
    return FileRepository()


def _memory_repo():
    return MemoryRepository()


# Each entry is a zero-arg factory so every test gets a fresh instance.
REPOSITORY_FACTORIES = {
    "file": _file_repo,
    "memory": _memory_repo,
}


@pytest.fixture(params=list(REPOSITORY_FACTORIES), ids=list(REPOSITORY_FACTORIES))
def repo(request) -> Repository:
    """A fresh Repository implementation per parametrized run."""
    return REPOSITORY_FACTORIES[request.param]()


def _record(agent_id: str, **extra) -> dict:
    rec = {ID_FIELD: agent_id, "display_name": f"agent {agent_id}"}
    rec.update(extra)
    return rec


def test_is_repository_subclass(repo):
    assert isinstance(repo, Repository)


def test_create_returns_stored_record(repo):
    stored = repo.create(COLLECTION, _record("a:1"), id_field=ID_FIELD)
    assert stored[ID_FIELD] == "a:1"
    # The stored copy is tenant-tagged with the default tenant.
    assert stored["tenant_id"] == "default"


def test_create_rejects_missing_id_field(repo):
    # A record without the id_field would be unqueryable; create must reject it
    # and must NOT store the record (no identity corruption across adapters).
    with pytest.raises(ValueError):
        repo.create(COLLECTION, {"display_name": "no id here"}, id_field=ID_FIELD)
    assert repo.list(COLLECTION, id_field=ID_FIELD) == []


def test_update_rejects_mismatched_id(repo):
    # update must not silently change a record's identity.
    repo.create(COLLECTION, _record("a:1", v=1), id_field=ID_FIELD)
    with pytest.raises(ValueError):
        repo.update(
            COLLECTION, "a:1", _record("a:2", v=2), id_field=ID_FIELD
        )
    # The original record is untouched.
    assert repo.get(COLLECTION, "a:1", id_field=ID_FIELD)["v"] == 1


def test_round_trip_get(repo):
    repo.create(COLLECTION, _record("a:1", note="hello"), id_field=ID_FIELD)
    got = repo.get(COLLECTION, "a:1", id_field=ID_FIELD)
    assert got is not None
    assert got[ID_FIELD] == "a:1"
    assert got["note"] == "hello"


def test_get_missing_returns_none(repo):
    assert repo.get(COLLECTION, "does-not-exist", id_field=ID_FIELD) is None


def test_default_tenant_equivalence(repo):
    # Creating without tenant_id == creating with tenant_id="default".
    repo.create(COLLECTION, _record("a:1"), id_field=ID_FIELD)
    via_explicit = repo.get(COLLECTION, "a:1", tenant_id="default", id_field=ID_FIELD)
    via_omitted = repo.get(COLLECTION, "a:1", id_field=ID_FIELD)
    assert via_explicit is not None
    assert via_omitted is not None
    assert via_explicit[ID_FIELD] == via_omitted[ID_FIELD]


def test_tenant_isolation_get(repo):
    repo.create(COLLECTION, _record("a:1"), tenant_id="acme", id_field=ID_FIELD)
    # The same id is invisible from a different tenant scope.
    assert repo.get(COLLECTION, "a:1", tenant_id="globex", id_field=ID_FIELD) is None
    assert repo.get(COLLECTION, "a:1", tenant_id="acme", id_field=ID_FIELD) is not None


def test_tenant_isolation_list(repo):
    repo.create(COLLECTION, _record("a:1"), tenant_id="acme", id_field=ID_FIELD)
    repo.create(COLLECTION, _record("g:1"), tenant_id="globex", id_field=ID_FIELD)
    acme = repo.list(COLLECTION, tenant_id="acme", id_field=ID_FIELD)
    globex = repo.list(COLLECTION, tenant_id="globex", id_field=ID_FIELD)
    assert [r[ID_FIELD] for r in acme] == ["a:1"]
    assert [r[ID_FIELD] for r in globex] == ["g:1"]


def test_no_cross_tenant_merge(repo):
    # The SAME record_id under two tenants are two distinct records.
    repo.create(COLLECTION, _record("dup", who="acme"), tenant_id="acme", id_field=ID_FIELD)
    repo.create(COLLECTION, _record("dup", who="globex"), tenant_id="globex", id_field=ID_FIELD)
    a = repo.get(COLLECTION, "dup", tenant_id="acme", id_field=ID_FIELD)
    g = repo.get(COLLECTION, "dup", tenant_id="globex", id_field=ID_FIELD)
    assert a["who"] == "acme"
    assert g["who"] == "globex"


def test_list_filters_and_limit(repo):
    repo.create(COLLECTION, _record("a:1", kind="x"), id_field=ID_FIELD)
    repo.create(COLLECTION, _record("a:2", kind="y"), id_field=ID_FIELD)
    repo.create(COLLECTION, _record("a:3", kind="x"), id_field=ID_FIELD)
    only_x = repo.list(COLLECTION, filters={"kind": "x"}, id_field=ID_FIELD)
    assert {r[ID_FIELD] for r in only_x} == {"a:1", "a:3"}
    limited = repo.list(COLLECTION, limit=2, id_field=ID_FIELD)
    assert len(limited) == 2


def test_update_replaces_record(repo):
    repo.create(COLLECTION, _record("a:1", v=1), id_field=ID_FIELD)
    updated = repo.update(COLLECTION, "a:1", _record("a:1", v=2), id_field=ID_FIELD)
    assert updated is not None
    assert updated["v"] == 2
    assert repo.get(COLLECTION, "a:1", id_field=ID_FIELD)["v"] == 2


def test_update_missing_returns_none(repo):
    assert repo.update(COLLECTION, "nope", _record("nope"), id_field=ID_FIELD) is None


def test_update_respects_tenant(repo):
    repo.create(COLLECTION, _record("a:1", v=1), tenant_id="acme", id_field=ID_FIELD)
    # Updating under the wrong tenant must not touch the acme record.
    assert repo.update(
        COLLECTION, "a:1", _record("a:1", v=99), tenant_id="globex", id_field=ID_FIELD
    ) is None
    assert repo.get(COLLECTION, "a:1", tenant_id="acme", id_field=ID_FIELD)["v"] == 1


def test_delete_returns_true_when_removed(repo):
    repo.create(COLLECTION, _record("a:1"), id_field=ID_FIELD)
    # Evaluate the side-effectful call outside the assert so it is not stripped
    # under `python -O` (assertions are removed but their expressions vanish too).
    deleted = repo.delete(COLLECTION, "a:1", id_field=ID_FIELD)
    assert deleted is True
    assert repo.get(COLLECTION, "a:1", id_field=ID_FIELD) is None


def test_idempotent_delete_of_missing(repo):
    # Deleting a missing id returns False and does NOT raise.
    deleted = repo.delete(COLLECTION, "ghost", id_field=ID_FIELD)
    assert deleted is False


def test_delete_respects_tenant(repo):
    repo.create(COLLECTION, _record("a:1"), tenant_id="acme", id_field=ID_FIELD)
    deleted = repo.delete(COLLECTION, "a:1", tenant_id="globex", id_field=ID_FIELD)
    assert deleted is False
    assert repo.get(COLLECTION, "a:1", tenant_id="acme", id_field=ID_FIELD) is not None


def test_legacy_record_without_tenant_reads_as_default():
    """A record persisted WITHOUT a tenant_id field reads under 'default' (FR-013).

    This is the upgrade path for v0.3.0 data. Only the file repository represents
    the legacy on-disk shape, so this targets it directly by writing a record that
    lacks tenant_id and confirming it surfaces under the default tenant.
    """
    repo = FileRepository()
    # Write a legacy-shaped document (no tenant_id) straight through the document
    # API, mimicking pre-upgrade data on disk.
    doc = repo.load_document(COLLECTION)
    doc["agents"].append({ID_FIELD: "legacy:1", "display_name": "old"})
    repo.save_document(COLLECTION, doc)

    got = repo.get(COLLECTION, "legacy:1", id_field=ID_FIELD)
    assert got is not None
    assert got[ID_FIELD] == "legacy:1"
    # And it is visible in the default-tenant listing.
    listed = repo.list(COLLECTION, tenant_id="default", id_field=ID_FIELD)
    assert any(r[ID_FIELD] == "legacy:1" for r in listed)
