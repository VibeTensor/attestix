"""US2 per-service audit-emission tests (T033/T034, FR-015…FR-018, SC-007).

Verifies the deferred per-service wiring: every STATE-CHANGING service operation
(create / issue / revoke / update / record / anchor / generate) emits exactly one
chained :class:`~audit.events.AuditEvent` through the injected emitter, the audit
emission is a pure side channel (a failing emitter never breaks the operation, and
the operation's return value is unchanged), and events are tenant-scoped.

Each service is constructed with an emitter backed by an isolated
:class:`~storage.MemoryRepository` so the assertions read back exactly the events
that service produced, independent of the on-disk default audit collection.
"""

import pytest

from attestix.audit import AuditEvent, AuditEventEmitter, verify_chain
from attestix.storage import MemoryRepository


# --- helpers --------------------------------------------------------------


def _emitter():
    """A fresh emitter over an isolated in-memory audit collection."""
    return AuditEventEmitter(repository=MemoryRepository())


class _FailingEmitter(AuditEventEmitter):
    """An emitter whose emit() always raises — to prove failures are swallowed."""

    def emit(self, **kwargs):  # noqa: D401 - test double
        raise RuntimeError("audit sink is down")


def _chain(emitter, tenant_id="default"):
    return emitter.read_chain(tenant_id=tenant_id)


# --- IdentityService ------------------------------------------------------


def test_identity_create_emits_one_event(tmp_attestix):
    from attestix.services.identity_service import IdentityService

    em = _emitter()
    svc = IdentityService(emitter=em)
    result = svc.create_identity(display_name="A", source_protocol="mcp")
    chain = _chain(em)
    assert len(chain) == 1
    ev = chain[0]
    assert isinstance(ev, AuditEvent)
    assert ev.action == "identity.create"
    assert ev.target_id == result["agent_id"]
    assert ev.target_collection == "identities"
    assert verify_chain(chain)


def test_identity_revoke_emits_one_more_event(tmp_attestix):
    from attestix.services.identity_service import IdentityService

    em = _emitter()
    svc = IdentityService(emitter=em)
    agent = svc.create_identity(display_name="A", source_protocol="mcp")
    svc.revoke_identity(agent["agent_id"], reason="test")
    chain = _chain(em)
    assert [e.action for e in chain] == ["identity.create", "identity.revoke"]
    assert verify_chain(chain)


def test_identity_failing_emitter_does_not_break_op(tmp_attestix):
    from attestix.services.identity_service import IdentityService

    svc = IdentityService(emitter=_FailingEmitter(repository=MemoryRepository()))
    # The create must still succeed and return a real UAIT despite the sink error.
    result = svc.create_identity(display_name="A", source_protocol="mcp")
    assert "error" not in result
    assert result["agent_id"].startswith("attestix:")
    assert result["signature"]


def test_identity_no_emitter_when_none_is_silent(tmp_attestix):
    from attestix.services.identity_service import IdentityService

    # An explicit None emitter (resolve_emitter constructs the default), so the op
    # must still work; assert via the injected-emitter path that the result is a
    # valid identity (the default-sink path is exercised by the full suite).
    svc = IdentityService()
    result = svc.create_identity(display_name="A", source_protocol="mcp")
    assert "error" not in result


def test_identity_tenant_scoping(tmp_attestix):
    from attestix.services.identity_service import IdentityService

    em = _emitter()
    svc = IdentityService(emitter=em, tenant_id="acme")
    svc.create_identity(display_name="A", source_protocol="mcp")
    # The event lands in the acme chain, not the default chain.
    assert len(_chain(em, tenant_id="acme")) == 1
    assert _chain(em, tenant_id="default") == []


# --- CredentialService ----------------------------------------------------


def test_credential_issue_and_revoke_emit_events(tmp_attestix):
    from attestix.services.credential_service import CredentialService

    em = _emitter()
    svc = CredentialService(emitter=em)
    cred = svc.issue_credential(agent_id="a:1", credential_type="AgentIdentityCredential",
                                claims={"x": 1})
    svc.revoke_credential(cred["id"], reason="test")
    chain = _chain(em)
    assert [e.action for e in chain] == ["credential.issue", "credential.revoke"]
    assert chain[0].target_id == cred["id"]
    assert verify_chain(chain)


def test_credential_failing_emitter_does_not_break_op(tmp_attestix):
    from attestix.services.credential_service import CredentialService

    svc = CredentialService(emitter=_FailingEmitter(repository=MemoryRepository()))
    cred = svc.issue_credential(agent_id="a:1", credential_type="AgentIdentityCredential")
    assert "error" not in cred
    assert cred["id"].startswith("urn:uuid:")


# --- DelegationService ----------------------------------------------------


def test_delegation_create_and_revoke_emit_events(tmp_attestix):
    from attestix.services.delegation_service import DelegationService

    em = _emitter()
    svc = DelegationService(emitter=em)
    result = svc.create_delegation("iss:1", "aud:1", capabilities=["read"])
    jti = result["delegation"]["jti"]
    svc.revoke_delegation(jti, reason="test")
    chain = _chain(em)
    assert [e.action for e in chain] == ["delegation.create", "delegation.revoke"]
    assert chain[0].target_id == jti
    assert verify_chain(chain)


def test_delegation_failing_emitter_does_not_break_op(tmp_attestix):
    from attestix.services.delegation_service import DelegationService

    svc = DelegationService(emitter=_FailingEmitter(repository=MemoryRepository()))
    result = svc.create_delegation("iss:1", "aud:1", capabilities=["read"])
    assert "error" not in result
    assert "token" in result


# --- ReputationService ----------------------------------------------------


def test_reputation_record_emits_one_event(tmp_attestix):
    from attestix.services.reputation_service import ReputationService

    em = _emitter()
    svc = ReputationService(emitter=em)
    svc.record_interaction("a:1", "b:1", outcome="success")
    chain = _chain(em)
    assert len(chain) == 1
    assert chain[0].action == "reputation.record"
    assert chain[0].target_id == "a:1"


def test_reputation_failing_emitter_does_not_break_op(tmp_attestix):
    from attestix.services.reputation_service import ReputationService

    svc = ReputationService(emitter=_FailingEmitter(repository=MemoryRepository()))
    result = svc.record_interaction("a:1", "b:1", outcome="success")
    assert result["recorded"] is True


# --- ProvenanceService ----------------------------------------------------


def test_provenance_record_methods_emit_events(tmp_attestix):
    from attestix.services.provenance_service import ProvenanceService

    em = _emitter()
    svc = ProvenanceService(emitter=em)
    svc.record_training_data("a:1", "ds")
    svc.record_model_lineage("a:1", "gpt")
    svc.log_action("a:1", "inference")
    chain = _chain(em)
    assert [e.action for e in chain] == [
        "provenance.record_training_data",
        "provenance.record_model_lineage",
        "provenance.log_action",
    ]
    assert verify_chain(chain)


def test_provenance_failing_emitter_does_not_break_op(tmp_attestix):
    from attestix.services.provenance_service import ProvenanceService

    svc = ProvenanceService(emitter=_FailingEmitter(repository=MemoryRepository()))
    entry = svc.record_training_data("a:1", "ds")
    assert "error" not in entry
    assert entry["entry_id"].startswith("prov:")


# --- ComplianceService ----------------------------------------------------


def test_compliance_create_profile_emits_one_event(tmp_attestix):
    from attestix.services.compliance_service import ComplianceService
    from attestix.services.identity_service import IdentityService

    # Compliance verifies the agent exists via the shared service cache, so create
    # the agent through a cache-resident IdentityService first.
    from attestix.services.cache import get_service
    id_svc = get_service(IdentityService)
    agent = id_svc.create_identity(display_name="A", source_protocol="mcp")

    em = _emitter()
    svc = ComplianceService(emitter=em)
    profile = svc.create_compliance_profile(
        agent_id=agent["agent_id"], risk_category="limited", provider_name="VibeTensor"
    )
    chain = _chain(em)
    assert len(chain) == 1
    assert chain[0].action == "compliance.create_profile"
    assert chain[0].target_id == profile["profile_id"]


def test_compliance_failing_emitter_does_not_break_op(tmp_attestix):
    from attestix.services.compliance_service import ComplianceService
    from attestix.services.identity_service import IdentityService
    from attestix.services.cache import get_service

    id_svc = get_service(IdentityService)
    agent = id_svc.create_identity(display_name="A", source_protocol="mcp")

    svc = ComplianceService(emitter=_FailingEmitter(repository=MemoryRepository()))
    profile = svc.create_compliance_profile(
        agent_id=agent["agent_id"], risk_category="limited", provider_name="VibeTensor"
    )
    assert "error" not in profile
    assert profile["profile_id"].startswith("comp:")


# --- DIDService -----------------------------------------------------------


def test_did_create_key_emits_one_event(tmp_attestix):
    from attestix.services.did_service import DIDService

    em = _emitter()
    svc = DIDService(emitter=em)
    result = svc.create_did_key()
    chain = _chain(em)
    assert len(chain) == 1
    assert chain[0].action == "did.create_did_key"
    assert chain[0].target_id == result["did"]


def test_did_failing_emitter_does_not_break_op(tmp_attestix):
    from attestix.services.did_service import DIDService

    svc = DIDService(emitter=_FailingEmitter(repository=MemoryRepository()))
    result = svc.create_did_key()
    assert "error" not in result
    assert result["did"].startswith("did:key:")


# --- AgentCardService -----------------------------------------------------


def test_agent_card_generate_emits_one_event(tmp_attestix):
    from attestix.services.agent_card_service import AgentCardService

    em = _emitter()
    svc = AgentCardService(emitter=em)
    result = svc.generate_agent_card(name="A", url="https://example.com")
    chain = _chain(em)
    assert len(chain) == 1
    assert chain[0].action == "agent_card.generate"
    assert chain[0].target_id == result["agent_card"]["id"]


def test_agent_card_failing_emitter_does_not_break_op(tmp_attestix):
    from attestix.services.agent_card_service import AgentCardService

    svc = AgentCardService(emitter=_FailingEmitter(repository=MemoryRepository()))
    result = svc.generate_agent_card(name="A", url="https://example.com")
    assert "agent_card" in result


# --- BlockchainService (mocked web3) --------------------------------------


def test_blockchain_anchor_emits_one_event(blockchain_service_mock):
    em = _emitter()
    # Re-wire the mocked service's emitter to our isolated sink.
    blockchain_service_mock._emitter = em
    blockchain_service_mock._tenant_id = "default"
    anchor = blockchain_service_mock.anchor_artifact(
        artifact_hash="ab" * 32, artifact_type="identity", artifact_id="a:1"
    )
    assert "error" not in anchor
    chain = _chain(em)
    assert len(chain) == 1
    assert chain[0].action == "blockchain.anchor"
    assert chain[0].target_id == anchor["anchor_id"]


def test_blockchain_failing_emitter_does_not_break_op(blockchain_service_mock):
    blockchain_service_mock._emitter = _FailingEmitter(repository=MemoryRepository())
    anchor = blockchain_service_mock.anchor_artifact(
        artifact_hash="cd" * 32, artifact_type="identity", artifact_id="a:2"
    )
    assert "error" not in anchor
    assert anchor["anchor_id"].startswith("anchor:")
