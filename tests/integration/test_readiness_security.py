"""Security boundaries must apply to cached and ordinary requests alike."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def authenticated_client(monkeypatch):
    from attestix.api.main import app, _rate_limiter

    monkeypatch.setenv('ATTESTIX_API_KEY', 'audit-test-key')
    monkeypatch.delenv('ATTESTIX_ALLOW_NO_AUTH', raising=False)
    _rate_limiter._hits.clear()
    return TestClient(app)


@pytest.mark.parametrize('provided_key', ['', 'wrong-key'])
def test_cached_response_requires_authentication(authenticated_client, provided_key):
    payload = {'display_name': 'Audit Agent', 'source_protocol': 'api_key'}
    headers = {'Idempotency-Key': 'private-result', 'X-API-Key': 'audit-test-key'}
    first = authenticated_client.post('/v1/identities', json=payload, headers=headers)
    assert first.status_code == 201

    headers['X-API-Key'] = provided_key
    replay = authenticated_client.post('/v1/identities', json=payload, headers=headers)
    assert replay.status_code == (403 if provided_key else 401)
    assert 'agent_id' not in replay.json()


def test_unauthorized_request_cannot_poison_idempotency_key(authenticated_client):
    payload = {'display_name': 'Audit Agent', 'source_protocol': 'api_key'}
    headers = {'Idempotency-Key': 'not-yet-authorized'}
    rejected = authenticated_client.post('/v1/identities', json=payload, headers=headers)
    assert rejected.status_code == 401

    headers['X-API-Key'] = 'audit-test-key'
    accepted = authenticated_client.post('/v1/identities', json=payload, headers=headers)
    assert accepted.status_code == 201


def test_cached_response_obeys_rate_limit(authenticated_client, monkeypatch):
    from attestix.api.main import _rate_limiter

    monkeypatch.setattr(_rate_limiter, 'max_requests', 1)
    payload = {'display_name': 'Audit Agent', 'source_protocol': 'api_key'}
    headers = {'Idempotency-Key': 'limited-result', 'X-API-Key': 'audit-test-key'}
    assert authenticated_client.post('/v1/identities', json=payload, headers=headers).status_code == 201
    assert authenticated_client.post('/v1/identities', json=payload, headers=headers).status_code == 429
