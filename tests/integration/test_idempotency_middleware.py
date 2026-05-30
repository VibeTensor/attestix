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

import json

import pytest

from attestix.idempotency.middleware import IDEMPOTENCY_HEADER, IdempotencyMiddleware
from attestix.idempotency.store import IDEMPOTENCY_COLLECTION, RepositoryIdempotencyStore
from attestix.storage import MemoryRepository

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

    # Same key + same body within TTL: the handler must NOT run again, and the
    # replay must echo the ORIGINAL response body verbatim (same status, same JSON
    # — v0.4.0-rc.5 P1: NOT a {"idempotent_replay": …} receipt envelope).
    r2 = client.post("/create", headers=headers, content=b'{"x":1}')
    assert calls["create"] == 1  # deduped (no duplicate side effect)
    assert r2.status_code == r1.status_code
    assert r2.json() == r1.json() == {"created": 1}
    # No receipt envelope leaks into the body.
    assert "idempotent_replay" not in r2.json()
    assert "stored_response" not in r2.json()
    # Replay metadata is in a header, not the body.
    assert r2.headers.get("Idempotency-Replayed") == "true"
    # The first response is NOT marked as a replay.
    assert r1.headers.get("Idempotency-Replayed") is None


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


# --- REST replay stores the verbatim body (v0.4.0-rc.5 P1) ----------------


def test_stored_record_holds_replayable_body():
    app, _, store = _build_app()
    client = TestClient(app)
    client.post("/create", headers={IDEMPOTENCY_HEADER: "k1"}, content=b'{"x":1}')

    rec = store.get("k1")
    assert rec is not None
    assert rec["status"] == "completed"
    stored = rec["stored_response"]
    # The REST boundary persists the original status + body + media-type so a
    # retry can echo the response verbatim, plus the integrity hash (FR-029 hash
    # retained; the body is the same JSON the client already received).
    assert set(stored) == {"status", "media_type", "body", "response_hash"}
    assert stored["status"] == 200
    assert json.loads(stored["body"]) == {"created": 1}
    assert stored["response_hash"]


def test_replay_echoes_original_status_code():
    """A non-2xx status (e.g. 201) is replayed verbatim, not coerced to 200."""
    calls = {"n": 0}

    async def create_201(request):
        calls["n"] += 1
        return JSONResponse({"id": f"res-{calls['n']}"}, status_code=201)

    app = Starlette(routes=[Route("/create201", create_201, methods=["POST"])])
    store = RepositoryIdempotencyStore(repository=MemoryRepository())
    app.add_middleware(IdempotencyMiddleware, store=store)
    client = TestClient(app)

    headers = {IDEMPOTENCY_HEADER: "k201"}
    r1 = client.post("/create201", headers=headers, content=b'{"x":1}')
    r2 = client.post("/create201", headers=headers, content=b'{"x":1}')
    assert r1.status_code == 201
    assert r2.status_code == 201  # replayed verbatim, not 200
    assert r2.json() == r1.json() == {"id": "res-1"}  # same resource id on retry
    assert calls["n"] == 1  # handler ran exactly once
    assert r2.headers.get("Idempotency-Replayed") == "true"


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
