"""The default REST installation exposes one authenticated storage context."""

import pytest
from fastapi.testclient import TestClient

from attestix.api.main import app


def test_non_default_tenant_cannot_reach_fresh_or_cached_handlers():
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
