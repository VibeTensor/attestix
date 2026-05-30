"""End-to-end REST idempotency-replay tests against the live FastAPI app.

Regression guard for the v0.4.0-rc.5 P1 (rc4 Linux 10-persona validation,
``paper/internal/v0.4.0rc4-linux-validation-2026-05-30.md``):

A retried ``POST /v1/identities`` with the same ``Idempotency-Key`` used to return
a receipt envelope — ``{"idempotent_replay": true, "stored_response": {...,
"resource_id": null}}`` — so a CI client doing ``resp.json()["agent_id"]`` on a
retry got ``None``. The fix makes the replay echo the ORIGINAL cached response body
verbatim (same status, same JSON including ``agent_id``), with replay metadata moved
to an ``Idempotency-Replayed`` header.

These tests exercise the real ``attestix.api.main.app`` (the auto-mounted
``IdempotencyMiddleware``), so they cover the wired boundary the validation hit. The
``tmp_attestix`` autouse fixture isolates all storage to a temp dir.
"""

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402


@pytest.fixture
def client():
    # Import inside the fixture so the autouse tmp_attestix path patching is in
    # effect before the app's services are first constructed.
    from attestix.api.main import app

    return TestClient(app)


def _create_payload(name="Replay Agent"):
    return {"display_name": name, "source_protocol": "api_key"}


def test_retry_returns_same_body_with_agent_id(client):
    """The headline fix: retry returns the SAME body, not a receipt envelope."""
    headers = {"Idempotency-Key": "rc5-key-1"}

    r1 = client.post("/v1/identities", json=_create_payload(), headers=headers)
    assert r1.status_code == 201
    first_body = r1.json()
    agent_id = first_body["agent_id"]
    assert agent_id  # non-empty

    r2 = client.post("/v1/identities", json=_create_payload(), headers=headers)
    # Same status, same body (incl. agent_id) — indistinguishable from the first.
    assert r2.status_code == 201
    assert r2.json() == first_body
    assert r2.json()["agent_id"] == agent_id
    # No receipt envelope leaks into the body.
    assert "idempotent_replay" not in r2.json()
    assert "stored_response" not in r2.json()
    # Replay metadata is exposed via a header, not the body.
    assert r2.headers.get("Idempotency-Replayed") == "true"
    assert r1.headers.get("Idempotency-Replayed") is None


def test_exactly_one_identity_after_n_replays(client):
    """The dedup guarantee still holds: N same-key POSTs → exactly 1 identity."""
    headers = {"Idempotency-Key": "rc5-key-dedup"}

    bodies = [
        client.post("/v1/identities", json=_create_payload(), headers=headers).json()
        for _ in range(3)
    ]
    # All three replays returned the identical identity.
    assert bodies[0] == bodies[1] == bodies[2]
    agent_id = bodies[0]["agent_id"]

    # Only one identity persisted (no duplicate writes).
    listed = client.get("/v1/identities").json()
    matching = [a for a in listed if a["agent_id"] == agent_id]
    assert len(matching) == 1
    # And the create endpoint never minted a second agent under this key.
    assert sum(1 for b in bodies if b["agent_id"] == agent_id) == 3


def test_same_key_different_payload_conflicts(client):
    """Conflict behavior preserved: same key + different body → 409 (not a replay)."""
    headers = {"Idempotency-Key": "rc5-key-conflict"}

    r1 = client.post("/v1/identities", json=_create_payload("Agent A"), headers=headers)
    assert r1.status_code == 201

    r2 = client.post("/v1/identities", json=_create_payload("Agent B"), headers=headers)
    assert r2.status_code == 409
    assert r2.headers.get("Idempotency-Replayed") is None


def test_different_keys_create_distinct_identities(client):
    """A different key is a fresh write (dedup is keyed correctly)."""
    r1 = client.post(
        "/v1/identities", json=_create_payload(), headers={"Idempotency-Key": "rc5-a"}
    )
    r2 = client.post(
        "/v1/identities", json=_create_payload(), headers={"Idempotency-Key": "rc5-b"}
    )
    assert r1.status_code == r2.status_code == 201
    assert r1.json()["agent_id"] != r2.json()["agent_id"]
