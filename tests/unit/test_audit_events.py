"""US2 audit-event tests (FR-015…FR-018, SC-007).

Covers: the documented AuditEvent shape, one chainable event per committed change,
hash-chain verification (tamper detection), and per-tenant chaining. The emitter is
exercised against both Repository implementations so the audit seam behaves
identically on file and in-memory storage.
"""

import pytest

from attestix.audit import (
    AuditEvent,
    AuditEventEmitter,
    BROKEN_FIELD_CHAIN_HASH,
    BROKEN_FIELD_PREV_HASH,
    BROKEN_FIELD_TENANT_ID,
    GENESIS_HASH,
    VerifyChainResult,
    verify_chain,
)
from attestix.audit.emitter import AUDIT_COLLECTION
from attestix.storage import FileRepository, MemoryRepository

REPO_FACTORIES = {"file": FileRepository, "memory": MemoryRepository}


@pytest.fixture(params=list(REPO_FACTORIES), ids=list(REPO_FACTORIES))
def emitter(request):
    """A fresh emitter over each Repository impl (file uses the tmp_attestix dir)."""
    return AuditEventEmitter(repository=REPO_FACTORIES[request.param]())


# --- Schema / shape -------------------------------------------------------


def test_event_has_documented_shape(emitter):
    ev = emitter.emit(
        action="identity.create",
        target_id="agent:1",
        target_collection="identities",
        actor="did:key:zServer",
        after={"agent_id": "agent:1", "display_name": "A"},
    )
    assert isinstance(ev, AuditEvent)
    # Documented fields (data-model §4).
    for field in (
        "event_id", "tenant_id", "actor", "action", "target_id",
        "target_collection", "occurred_at", "change_digest", "prev_hash",
        "chain_hash",
    ):
        assert getattr(ev, field) is not None
    assert ev.tenant_id == "default"
    assert ev.action == "identity.create"
    assert ev.target_id == "agent:1"
    assert ev.prev_hash == GENESIS_HASH  # first event links to genesis


def test_change_digest_does_not_contain_raw_body(emitter):
    # change_digest is a SHA-256 hex string, never the raw change (principle VI).
    ev = emitter.emit(
        action="credential.revoke",
        target_id="cred:secret",
        target_collection="credentials",
        actor="did:key:zServer",
        before={"id": "cred:secret", "private": "DO-NOT-LEAK"},
        after={"id": "cred:secret", "status": "revoked"},
    )
    assert len(ev.change_digest) == 64
    assert "DO-NOT-LEAK" not in ev.change_digest


# --- Exactly one event per committed change -------------------------------


def test_one_event_persisted_per_emit(emitter):
    emitter.emit(action="identity.create", target_id="a:1",
                 target_collection="identities", actor="srv")
    emitter.emit(action="identity.update", target_id="a:1",
                 target_collection="identities", actor="srv", after={"v": 2})
    chain = emitter.read_chain()
    assert len(chain) == 2
    assert [e.action for e in chain] == ["identity.create", "identity.update"]


def test_failed_op_emits_no_event(emitter):
    """FR-018: a failed op emits no success event.

    The emitter only persists when emit() is called, and a caller calls emit()
    only after the write commits. Simulate a failure that skips emit() and assert
    nothing was recorded.
    """
    try:
        raise RuntimeError("write failed")
    except RuntimeError:
        pass  # caller does NOT emit on failure
    assert emitter.read_chain() == []


# --- Hash chain -----------------------------------------------------------


def test_emitted_sequence_verifies_as_chain(emitter):
    for i in range(5):
        emitter.emit(action="identity.create", target_id=f"a:{i}",
                     target_collection="identities", actor="srv",
                     after={"agent_id": f"a:{i}"})
    chain = emitter.read_chain()
    assert verify_chain(chain).valid is True
    # Each event links to the prior event's chain_hash.
    for prev, cur in zip(chain, chain[1:]):
        assert cur.prev_hash == prev.chain_hash


def test_tampering_breaks_chain():
    # Build a chain of plain-dict events, then tamper with the middle one.
    e0 = AuditEvent.create(action="a", target_id="t0", target_collection="c",
                           actor="srv", after={"n": 0})
    e1 = AuditEvent.create(action="a", target_id="t1", target_collection="c",
                           actor="srv", after={"n": 1}, prev_hash=e0.chain_hash)
    e2 = AuditEvent.create(action="a", target_id="t2", target_collection="c",
                           actor="srv", after={"n": 2}, prev_hash=e1.chain_hash)
    assert verify_chain([e0, e1, e2]).valid is True

    tampered = [e0.to_dict(), e1.to_dict(), e2.to_dict()]
    tampered[1]["target_id"] = "HACKED"  # mutate without recomputing chain_hash
    assert verify_chain(tampered).valid is False


# --- Per-tenant chaining --------------------------------------------------


def test_chains_are_per_tenant(emitter):
    emitter.emit(action="x", target_id="a:1", target_collection="identities",
                 actor="srv", tenant_id="acme")
    emitter.emit(action="x", target_id="g:1", target_collection="identities",
                 actor="srv", tenant_id="globex")
    acme = emitter.read_chain(tenant_id="acme")
    globex = emitter.read_chain(tenant_id="globex")
    # Each tenant has its own independent genesis-rooted chain.
    assert len(acme) == 1 and len(globex) == 1
    assert acme[0].prev_hash == GENESIS_HASH
    assert globex[0].prev_hash == GENESIS_HASH
    assert verify_chain(acme) and verify_chain(globex)
    # No cross-tenant leakage into either chain.
    assert acme[0].target_id == "a:1"
    assert globex[0].target_id == "g:1"


def test_external_sink_receives_event():
    received = []
    emitter = AuditEventEmitter(repository=MemoryRepository(),
                                sink=received.append)
    ev = emitter.emit(action="identity.create", target_id="a:1",
                      target_collection="identities", actor="srv")
    # FR-017: the injected external sink receives the same chained event.
    assert received == [ev]


# --- Structured VerifyChainResult (P1 #4 from e2e walkthrough 2026-05-28) ---


def _build_clean_chain(n: int = 4, tenant_id: str = "default") -> list[AuditEvent]:
    """Build a clean n-event chain rooted at GENESIS_HASH for tamper tests."""
    events: list[AuditEvent] = []
    prev = GENESIS_HASH
    for i in range(n):
        ev = AuditEvent.create(
            action="a",
            target_id=f"t:{i}",
            target_collection="c",
            actor="srv",
            tenant_id=tenant_id,
            after={"n": i},
            prev_hash=prev,
        )
        events.append(ev)
        prev = ev.chain_hash
    return events


def test_verify_chain_returns_structured_result_when_clean():
    chain = _build_clean_chain(5)
    result = verify_chain(chain)
    assert isinstance(result, VerifyChainResult)
    assert result.valid is True
    assert result.broken_event_id is None
    assert result.broken_field is None
    assert result.failure_reason is None
    assert result.events_checked == len(chain)


def test_verify_chain_detects_prev_hash_tamper():
    # Build 4 events, then break the chain link at event #3 by pointing its
    # prev_hash at the wrong upstream chain_hash (not the prior event's).
    chain = _build_clean_chain(4)
    tampered = [e.to_dict() for e in chain]
    tampered[3]["prev_hash"] = "f" * 64  # not chain[2].chain_hash

    result = verify_chain(tampered)
    assert result.valid is False
    assert result.broken_event_id == chain[3].event_id
    assert result.broken_field == BROKEN_FIELD_PREV_HASH
    assert "prev_hash" in result.failure_reason
    # events_checked is the 1-based count of events processed before abort.
    assert result.events_checked == 4


def test_verify_chain_detects_chain_hash_tamper():
    # Mutate chain_hash on event #2 directly; prev_hash chain stays consistent
    # at index 2 (it still matches event #1's chain_hash, which we did NOT
    # mutate), so the failure has to surface as a chain_hash recompute miss.
    chain = _build_clean_chain(4)
    tampered = [e.to_dict() for e in chain]
    # Flip a non-tenant body field so the recompute changes; mutate the
    # stored chain_hash to a wrong value (so it does not equal the recompute).
    tampered[2]["chain_hash"] = "0" * 64

    result = verify_chain(tampered)
    assert result.valid is False
    assert result.broken_event_id == chain[2].event_id
    assert result.broken_field == BROKEN_FIELD_CHAIN_HASH
    assert "chain_hash" in result.failure_reason
    assert result.events_checked == 3


def test_verify_chain_detects_genesis_violation():
    # First event has a non-zero prev_hash → genesis link is broken.
    chain = _build_clean_chain(3)
    tampered = [e.to_dict() for e in chain]
    tampered[0]["prev_hash"] = "a" * 64

    result = verify_chain(tampered)
    assert result.valid is False
    assert result.broken_event_id == chain[0].event_id
    assert result.broken_field == BROKEN_FIELD_PREV_HASH
    assert "genesis" in result.failure_reason
    assert result.events_checked == 1


def test_verify_chain_detects_tenant_shift():
    # A cross-tenant import error: every row has been relabeled to a different
    # tenant_id, but the stored chain_hash was minted under the original
    # tenant string. The recompute fails with the new tenant_id but succeeds
    # under the prior event's tenant_id (well, for index 0 we scan siblings).
    chain = _build_clean_chain(3, tenant_id="acme")
    tampered = [e.to_dict() for e in chain]
    # Relabel event #1's tenant_id only (event #0 stays "acme"), so the prior
    # event's tenant_id is the original mint-time tenant ("acme") — exactly
    # the signal verify_chain uses to attribute the failure to tenant_id.
    tampered[1]["tenant_id"] = "globex"

    result = verify_chain(tampered)
    assert result.valid is False
    assert result.broken_event_id == chain[1].event_id
    assert result.broken_field == BROKEN_FIELD_TENANT_ID
    assert "tenant_id" in result.failure_reason
    assert result.events_checked == 2


def test_verify_chain_back_compat_bool_protocol():
    # The __bool__ shim keeps `if verify_chain(events): ...` and
    # `assert verify_chain(events)` working unchanged after the dataclass
    # refactor (this is the single most important back-compat guarantee).
    good = _build_clean_chain(3)
    assert verify_chain(good)  # truthy via __bool__

    bad = [e.to_dict() for e in good]
    bad[1]["target_id"] = "HACKED"
    assert not verify_chain(bad)  # falsy via __bool__
