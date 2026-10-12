"""The default REST installation exposes one authenticated storage context."""

import pytest
from fastapi.testclient import TestClient

from attestix.api.main import app


def test_non_default_tenant_cannot_reach_fresh_or_cached_handlers(monkeypatch):
    from attestix.api.main import _rate_limiter

    monkeypatch.setenv("ATTESTIX_ALLOW_NO_AUTH", "1")
    monkeypatch.delenv("ATTESTIX_API_KEY", raising=False)
    _rate_limiter._hits.clear()
    with TestClient(app) as client:
        body = {"display_name": "agent", "source_protocol": "test"}
        first = client.post("/v1/identities", json=body, headers={"Idempotency-Key": "same"})
        assert first.status_code == 201
        rejected = client.post("/v1/identities", json=body, headers={"Idempotency-Key": "same", "X-Attestix-Tenant": "other"})
        assert rejected.status_code == 400
        assert "single-tenant" in rejected.json()["error"]


def test_fast_durability_is_refused_for_rest(monkeypatch):
    monkeypatch.setenv("ATTESTIX_DURABILITY", "fast")
    with pytest.raises(RuntimeError, match="safe durability"):
        with TestClient(app):
            pass


def test_tenant_policy_is_not_revealed_before_authentication(monkeypatch):
    from attestix.api.main import _rate_limiter

    _rate_limiter._hits.clear()
    headers = {"X-Attestix-Tenant": "other"}
    monkeypatch.delenv("ATTESTIX_ALLOW_NO_AUTH", raising=False)
    monkeypatch.delenv("ATTESTIX_API_KEY", raising=False)
    with TestClient(app) as client:
        assert client.get("/v1/identities", headers=headers).status_code == 503
    monkeypatch.setenv("ATTESTIX_API_KEY", "secret-key")
    with TestClient(app) as client:
        assert client.get("/v1/identities", headers=headers).status_code == 401
        assert client.get("/v1/identities", headers={**headers, "X-API-Key": "wrong"}).status_code == 403
        assert client.get("/v1/identities", headers={**headers, "X-API-Key": "secret-key"}).status_code == 400
