"""US3 idempotency-store tests (FR-019…FR-023, FR-029, SC-008).

Covers: dedupe within TTL (same key → same stored result, write runs once),
conflict on payload mismatch, TTL expiry (key past 24h treated as new),
no-key passthrough (v0.3.0 parity), per-tenant scoping, the FR-029 minimal stored
representation, and TTL reclaim. Parametrized across the file and in-memory
Repository implementations.
"""

from datetime import datetime, timedelta, timezone

import pytest

from idempotency import (
    IDEMPOTENCY_COLLECTION,
    IdempotencyConflictError,
    RepositoryIdempotencyStore,
    minimal_stored_response,
    request_fingerprint,
    run_idempotent,
)
from idempotency.store import TTL
from storage import FileRepository, MemoryRepository

REPO_FACTORIES = {"file": FileRepository, "memory": MemoryRepository}


@pytest.fixture(params=list(REPO_FACTORIES), ids=list(REPO_FACTORIES))
def store_and_repo(request):
    repo = REPO_FACTORIES[request.param]()
    return RepositoryIdempotencyStore(repository=repo), repo


def _counter():
    """Returns an execute() that counts how many times it actually runs."""
    calls = {"n": 0}

    def execute():
        calls["n"] += 1
        return {"id": "res:1", "value": calls["n"]}

    return execute, calls


# --- Same key + same payload → run once, replay returns original ----------


def test_replay_same_key_runs_once(store_and_repo):
    store, _ = store_and_repo
    execute, calls = _counter()
    payload = {"method": "POST", "path": "/x", "body": "data"}

    first, replayed1 = run_idempotent(store, "k1", payload, execute,
                                      summarize=lambda r: ("ok", r["id"]))
    assert replayed1 is False
    assert calls["n"] == 1

    # Replay with the SAME key + payload: execute must NOT run again.
    stored, replayed2 = run_idempotent(store, "k1", payload, execute,
                                       summarize=lambda r: ("ok", r["id"]))
    assert replayed2 is True
    assert calls["n"] == 1  # no duplicate execution (SC-008)
    # The replay returns the stored minimal representation, not a new result.
    assert stored["resource_id"] == "res:1"
    assert stored["status"] == "ok"
    assert stored["response_hash"] == minimal_stored_response(first)["response_hash"]


# --- Same key + different payload → conflict (FR-020) ---------------------


def test_conflict_on_payload_mismatch(store_and_repo):
    store, _ = store_and_repo
    execute, _ = _counter()
    run_idempotent(store, "k1", {"body": "A"}, execute)
    with pytest.raises(IdempotencyConflictError):
        run_idempotent(store, "k1", {"body": "B"}, execute)


# --- TTL expiry → key treated as new (FR-021) -----------------------------


def test_expired_key_treated_as_new(store_and_repo):
    store, repo = store_and_repo
    execute, calls = _counter()
    payload = {"body": "A"}
    run_idempotent(store, "k1", payload, execute)
    assert calls["n"] == 1

    # Age the stored record beyond the 24h TTL by rewriting created_at.
    rec = repo.get(IDEMPOTENCY_COLLECTION, "k1", id_field="key")
    old = (datetime.now(timezone.utc) - TTL - timedelta(minutes=1)).isoformat()
    rec["created_at"] = old
    repo.update(IDEMPOTENCY_COLLECTION, "k1", rec, id_field="key")

    # The same key now proceeds as a brand-new write.
    _, replayed = run_idempotent(store, "k1", payload, execute)
    assert replayed is False
    assert calls["n"] == 2


def test_store_get_ignores_expired(store_and_repo):
    store, repo = store_and_repo
    store.put({
        "key": "old", "tenant_id": "default", "request_fingerprint": "x",
        "stored_response": None, "status": "completed",
        "created_at": (datetime.now(timezone.utc) - TTL - timedelta(seconds=1)).isoformat(),
    })
    assert store.get("old") is None  # expired → None (FR-021)


# --- No key → v0.3.0 behavior (FR-022) ------------------------------------


def test_no_key_passthrough(store_and_repo):
    store, repo = store_and_repo
    execute, calls = _counter()
    result, replayed = run_idempotent(store, None, {"body": "A"}, execute)
    assert replayed is False
    assert calls["n"] == 1
    assert result["id"] == "res:1"
    # No bookkeeping record was written.
    assert repo.list(IDEMPOTENCY_COLLECTION, id_field="key") == []


# --- Per-tenant scoping (FR-023) ------------------------------------------


def test_keys_scoped_per_tenant(store_and_repo):
    store, _ = store_and_repo
    execute_a, calls_a = _counter()
    execute_b, calls_b = _counter()
    # Same key value under two tenants must not collide.
    run_idempotent(store, "dup", {"body": "A"}, execute_a, tenant_id="acme")
    _, replayed = run_idempotent(store, "dup", {"body": "B"}, execute_b, tenant_id="globex")
    # globex's "dup" is independent — no conflict despite a different payload.
    assert replayed is False
    assert calls_a["n"] == 1
    assert calls_b["n"] == 1


# --- FR-029 minimal stored representation ---------------------------------


def test_stored_response_is_minimal_no_raw_body(store_and_repo):
    store, repo = store_and_repo

    def execute():
        # A sensitive result the store must NOT keep a raw copy of.
        return {"id": "cred:1", "signed_vc": "PRIVATE-SIGNED-MATERIAL"}

    run_idempotent(store, "k1", {"body": "A"}, execute,
                   summarize=lambda r: ("ok", r["id"]))
    rec = repo.get(IDEMPOTENCY_COLLECTION, "k1", id_field="key")
    stored = rec["stored_response"]
    assert set(stored) == {"status", "resource_id", "response_hash"}
    assert stored["resource_id"] == "cred:1"
    # The raw signed material is never persisted in the idempotency record.
    assert "PRIVATE-SIGNED-MATERIAL" not in repr(rec)


# --- TTL reclaim (FR-021 unbounded-growth guard) --------------------------


def test_reclaim_expired_purges(store_and_repo):
    store, repo = store_and_repo
    # One fresh, one expired.
    store.put({
        "key": "fresh", "tenant_id": "default", "request_fingerprint": "x",
        "stored_response": None, "status": "completed",
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    store.put({
        "key": "stale", "tenant_id": "default", "request_fingerprint": "y",
        "stored_response": None, "status": "completed",
        "created_at": (datetime.now(timezone.utc) - TTL - timedelta(hours=1)).isoformat(),
    })
    removed = store.reclaim_expired(tenant_id="default")
    assert removed == 1
    remaining = {r["key"] for r in repo.list(IDEMPOTENCY_COLLECTION, id_field="key")}
    assert remaining == {"fresh"}


def test_request_fingerprint_is_stable():
    a = request_fingerprint({"x": 1, "y": [1, 2, 3]})
    b = request_fingerprint({"y": [1, 2, 3], "x": 1})  # key order irrelevant (JCS)
    assert a == b
    assert a != request_fingerprint({"x": 2})
