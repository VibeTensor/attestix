"""Performance guard for credential issuance scaling (issue #108).

Before the fix, ``issue_credential`` did, per call, a full read + deep copy +
rewrite of the whole (growing) ``credentials.json`` *and* two full reads + a
rewrite of the whole ``audit.json`` — so an N-issuance loop was O(N^2) in bytes
moved, measuring ~183 ms median per issuance at N=1000.

The fix makes the append path O(1)-amortized:

- :func:`attestix.config.append_credential` appends one record to the live
  cached document instead of ``load -> deep-copy -> append -> rewrite``.
- The audit emitter finds the chain head via
  :meth:`FileRepository.last_record` instead of copying the whole event list.
- An opt-in ``durability="fast"`` mode batches the disk writes so even the
  per-write ``json.dump`` is amortized (the default ``safe`` mode stays
  crash-safe and flushes every write).

These tests guard against an O(N^2) regression. Timing assertions use generous
thresholds so they are not flaky on shared CI, but tight enough that a return to
quadratic behavior trips them. A deterministic (non-timing) guard backs them up.
"""

import time

import pytest

from attestix.audit import AuditEventEmitter, verify_chain
from attestix.services.credential_service import CredentialService
from attestix.storage import default_repository
from attestix.storage.file_repository import FileRepository

pytestmark = pytest.mark.perf


@pytest.fixture
def repo_factory(monkeypatch):
    """Rebuild the process-default repositories under a chosen durability mode.

    Saves and restores ``config._file_repository`` and ``storage._DEFAULT`` so a
    fast-mode repo built for one test never leaks into the rest of the suite.
    """
    from attestix import config
    import attestix.storage as storage

    saved_cfg = config._file_repository
    saved_default = storage._DEFAULT

    def _build(mode: str):
        monkeypatch.setenv("ATTESTIX_DURABILITY", mode)
        config._file_repository = None  # rebuilt lazily by config._repo()
        storage._DEFAULT = FileRepository()
        return storage._DEFAULT

    yield _build

    config._file_repository = saved_cfg
    storage._DEFAULT = saved_default


def _issue_n(svc: CredentialService, n: int) -> None:
    for i in range(n):
        result = svc.issue_credential(
            agent_id=f"did:key:zPerf{i}",
            credential_type="AgentIdentityCredential",
            issuer_name="VibeTensor",
            claims={"n": i},
        )
        assert "error" not in result, result


def test_issuing_200_is_fast_in_fast_mode(tmp_attestix, repo_factory):
    """Fast (batched) durability issues 200 credentials well under 5s on CI."""
    repo = repo_factory("fast")
    svc = CredentialService()
    start = time.perf_counter()
    _issue_n(svc, 200)
    repo.flush()
    elapsed = time.perf_counter() - start

    assert elapsed < 5.0, (
        f"issuing 200 credentials took {elapsed:.2f}s in fast mode; "
        f"expected < 5s (O(N^2) regression?)"
    )


def test_issuance_scales_near_linearly(tmp_attestix, repo_factory):
    """Total issuance time must grow ~linearly, not quadratically, with N.

    Quadratic growth would make the 4x-larger batch ~16x slower; linear ~4x. We
    allow a very loose ceiling (9x) to absorb CI jitter and fixed per-call crypto
    cost while still failing hard on a true O(N^2) regression.
    """
    def _time_for(n: int) -> float:
        repo = repo_factory("fast")
        svc = CredentialService()
        start = time.perf_counter()
        _issue_n(svc, n)
        repo.flush()
        return time.perf_counter() - start

    small = max(_time_for(100), 1e-3)
    large = _time_for(400)
    ratio = large / small

    assert ratio < 9.0, (
        f"issuance time scaled {ratio:.1f}x from N=100 to N=400 "
        f"(small={small:.3f}s large={large:.3f}s); near-linear is ~4x, "
        f"quadratic would be ~16x — likely an O(N^2) regression"
    )


def test_issue_path_does_not_reload_whole_store(tmp_attestix):
    """Deterministic guard: issuance must append, not load+rewrite the store.

    A reload-the-whole-store-per-append implementation is exactly the O(N^2)
    pattern this issue fixed. We assert the hot path calls ``append_to_document``
    (O(1) append) and never ``load_document('credentials')`` (which deep-copies
    the whole — growing — collection on every call).
    """
    from attestix import config

    calls = {"append": 0, "load_credentials": 0}
    real_append = config.append_credential
    real_load = config.load_credentials

    def spy_append(credential):
        calls["append"] += 1
        return real_append(credential)

    def spy_load():
        calls["load_credentials"] += 1
        return real_load()

    config.append_credential = spy_append
    config.load_credentials = spy_load
    # The service imported the names at module load; patch there too.
    import attestix.services.credential_service as cs
    cs.append_credential = spy_append
    cs.load_credentials = spy_load
    try:
        svc = CredentialService()
        for i in range(10):
            svc.issue_credential(
                agent_id=f"did:key:zSpy{i}",
                credential_type="AgentIdentityCredential",
                issuer_name="VibeTensor",
                claims={"n": i},
            )
    finally:
        config.append_credential = real_append
        config.load_credentials = real_load
        cs.append_credential = real_append
        cs.load_credentials = real_load

    assert calls["append"] == 10, "issuance should append once per credential"
    assert calls["load_credentials"] == 0, (
        "issuance must not load+copy the whole credential store per call "
        "(O(N^2) regression)"
    )


@pytest.mark.parametrize("mode", ["safe", "fast"])
def test_audit_chain_intact_after_bulk_issuance(tmp_attestix, repo_factory, mode):
    """Both durability modes keep the audit chain verifiable end-to-end."""
    repo = repo_factory(mode)
    svc = CredentialService()
    _issue_n(svc, 40)
    # Flush both the audit default repo and the credential-store repo so the
    # fast-mode tail is on disk before we read the chain back.
    repo.flush()
    from attestix import config
    config._repo().flush()

    emitter = AuditEventEmitter()
    events = emitter.read_chain()
    assert len(events) == 40
    result = verify_chain(events)
    assert result.valid, result.failure_reason
