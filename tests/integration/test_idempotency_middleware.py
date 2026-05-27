"""US3 REST middleware tests (T040 mount, FR-019/FR-020/FR-022, FR-029).

Exercises ``idempotency.middleware.IdempotencyMiddleware`` end-to-end on a minimal
Starlette app (FastAPI is not required to import the middleware — it builds on
``starlette.middleware.base.BaseHTTPMiddleware``). The same middleware instance is
what ``api/main.py`` mounts, so these tests cover the wired REST boundary:

- no ``Idempotency-Key`` header → request passes through untouched, the handler
  runs every time, the response is byte-identical (FR-022, the strict-no-op mount
  contract);
- a GET (read method) is never intercepted even with a key;
- same key + same payload within TTL → second request is deduped (the handler does
  NOT run again) and a replay marker is returned (FR-019);
- same key + different payload → 409 conflict (FR-020);
- the stored idempotency record is the FR-029 minimal representation (no raw body);
- keys are scoped per tenant via ``X-Attestix-Tenant`` (FR-023).
"""

import pytest

from idempotency.middleware import IDEMPOTENCY_HEADER, IdempotencyMiddleware
from idempotency.store import IDEMPOTENCY_COLLECTION, RepositoryIdempotencyStore
from storage import MemoryRepository

# The middleware is only constructible when the Starlette stack is present.
starlette = pytest.importorskip("starlette")
from starlette.applications import Starlette  # noqa: E402
from starlette.responses import JSONResponse, PlainTextResponse  # noqa: E402
from starlette.routing import Route  # noqa: E402
from starlette.testclient import TestClient  # noqa: E402


def _build_app():
    """A tiny app whose handlers count invocations so dedupe is observable."""
    calls = {"create": 0, "read": 0}

    async def create(request):
        calls["create"] += 1
        return JSONResponse({"created": calls["create"]})

    async def read(request):
        calls["read"] += 1
        return PlainTextResponse(f"read-{calls['read']}")

    app = Starlette(routes=[
        Route("/create", create, methods=["POST"]),
        Route("/read", read, methods=["GET"]),
    ])
    # Inject an isolated in-memory store so the test never touches disk and each
    # test starts clean (the default store would persist via the file Repository).
    store = RepositoryIdempotencyStore(repository=MemoryRepository())
    app.add_middleware(IdempotencyMiddleware, store=store)
    return app, calls, store


# --- No key → strict no-op (FR-022) ---------------------------------------


def test_no_key_passthrough_runs_every_time():
    app, calls, store = _build_app()
    client = TestClient(app)

    r1 = client.post("/create", content=b'{"x":1}')
    r2 = client.post("/create", content=b'{"x":1}')
    assert r1.status_code == 200 and r2.status_code == 200
    # No key → no dedupe: the handler runs on every request (v0.3.0 behavior).
    assert calls["create"] == 2
    assert r1.json() == {"created": 1}
    assert r2.json() == {"created": 2}
    # And no idempotency bookkeeping was written.
    assert store._repo.list(IDEMPOTENCY_COLLECTION, id_field="key") == []


def test_read_method_never_intercepted_even_with_key():
    app, calls, _ = _build_app()
    client = TestClient(app)
    r = client.get("/read", headers={IDEMPOTENCY_HEADER: "k1"})
    assert r.status_code == 200
    assert r.text == "read-1"
    assert calls["read"] == 1


# --- Same key + same payload → dedupe (FR-019) ----------------------------


def test_same_key_same_payload_dedupes():
    app, calls, _ = _build_app()
    client = TestClient(app)
    headers = {IDEMPOTENCY_HEADER: "k1"}

    r1 = client.post("/create", headers=headers, content=b'{"x":1}')
    assert r1.status_code == 200
    assert r1.json() == {"created": 1}
    assert calls["create"] == 1

    # Same key + same body within TTL: the handler must NOT run again.
    r2 = client.post("/create", headers=headers, content=b'{"x":1}')
    assert calls["create"] == 1  # deduped (no duplicate side effect)
    assert r2.status_code == 200
    assert r2.json().get("idempotent_replay") is True


# --- Same key + different payload → 409 (FR-020) --------------------------


def test_same_key_different_payload_conflicts():
    app, calls, _ = _build_app()
    client = TestClient(app)
    headers = {IDEMPOTENCY_HEADER: "k1"}

    client.post("/create", headers=headers, content=b'{"x":1}')
    r = client.post("/create", headers=headers, content=b'{"x":2}')
    assert r.status_code == 409
    # The conflicting request never reached the handler a second time.
    assert calls["create"] == 1


# --- FR-029 minimal stored representation ---------------------------------


def test_stored_record_is_minimal():
    app, _, store = _build_app()
    client = TestClient(app)
    client.post("/create", headers={IDEMPOTENCY_HEADER: "k1"}, content=b'{"x":1}')

    rec = store.get("k1")
    assert rec is not None
    assert rec["status"] == "completed"
    stored = rec["stored_response"]
    # Only the minimal triplet is persisted — never the raw response body.
    assert set(stored) == {"status", "resource_id", "response_hash"}


# --- Per-tenant scoping (FR-023) ------------------------------------------


def test_key_scoped_per_tenant():
    app, calls, _ = _build_app()
    client = TestClient(app)

    # Same key value, different tenants, different payloads → no conflict.
    r_a = client.post(
        "/create",
        headers={IDEMPOTENCY_HEADER: "dup", "X-Attestix-Tenant": "acme"},
        content=b'{"x":1}',
    )
    r_b = client.post(
        "/create",
        headers={IDEMPOTENCY_HEADER: "dup", "X-Attestix-Tenant": "globex"},
        content=b'{"x":2}',
    )
    assert r_a.status_code == 200
    assert r_b.status_code == 200  # not a 409 — independent per tenant
    assert calls["create"] == 2
