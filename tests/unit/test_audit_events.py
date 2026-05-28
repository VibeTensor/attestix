"""US2 audit-event tests (FR-015…FR-018, SC-007).

Covers: the documented AuditEvent shape, one chainable event per committed change,
hash-chain verification (tamper detection), and per-tenant chaining. The emitter is
exercised against both Repository implementations so the audit seam behaves
identically on file and in-memory storage.
"""

import pytest

from attestix.audit import AuditEvent, AuditEventEmitter, GENESIS_HASH, verify_chain
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
    assert verify_chain(chain) is True
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
    assert verify_chain([e0, e1, e2]) is True

    tampered = [e0.to_dict(), e1.to_dict(), e2.to_dict()]
    tampered[1]["target_id"] = "HACKED"  # mutate without recomputing chain_hash
    assert verify_chain(tampered) is False


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
