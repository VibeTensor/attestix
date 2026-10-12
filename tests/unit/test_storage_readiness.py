"""Behavioral regressions for local persistence and signed context boundaries."""

import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

import pytest

from attestix import config
from attestix.audit import AuditEventEmitter
from attestix.auth.crypto import canonicalize_json
from attestix.storage.file_repository import FileRepository


def test_independent_repositories_keep_all_concurrent_creates():
    repositories = [FileRepository(), FileRepository()]

    def create(index):
        repositories[index % 2].create("identities", {"agent_id": str(index)}, id_field="agent_id")

    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(create, range(32)))
    assert {row["agent_id"] for row in FileRepository().list("identities")} == {str(i) for i in range(32)}


def test_independent_processes_keep_all_creates(tmp_attestix):
    source = """
import sys
from attestix.storage.file_repository import FileRepository
repo = FileRepository()
for i in range(12):
    repo.create('identities', {'agent_id': sys.argv[1] + str(i)}, id_field='agent_id')
"""
    environment = dict(os.environ, ATTESTIX_DATA_DIR=str(tmp_attestix))
    processes = [subprocess.Popen([sys.executable, "-c", source, prefix], env=environment,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                 for prefix in ("a", "b")]
    for process in processes:
        stdout, stderr = process.communicate(timeout=30)
        assert process.returncode == 0, stderr.decode()
    assert len(FileRepository().list("identities")) == 24


def test_parallel_identity_service_creates_remain_readable(identity_service):
    with ThreadPoolExecutor(max_workers=4) as executor:
        created = list(executor.map(lambda i: identity_service.create_identity(str(i), "test"), range(12)))
    assert {a["agent_id"] for a in identity_service.list_identities()} == {a["agent_id"] for a in created}


def test_independent_emitters_extend_one_chain():
    emitters = [AuditEventEmitter(repository=FileRepository()), AuditEventEmitter(repository=FileRepository())]
    with ThreadPoolExecutor(max_workers=4) as executor:
        list(executor.map(lambda i: emitters[i % 2].emit(action="test", target_id=str(i),
                         target_collection="identities", actor="tester"), range(20)))
    chain = emitters[0].read_chain()
    assert len(chain) == 20
    assert all(current.prev_hash == previous.chain_hash for previous, current in zip(chain, chain[1:]))


def test_nested_unicode_key_collision_fails_closed():
    with pytest.raises(ValueError, match="collide"):
        canonicalize_json({"claims": {"\u00e9": "one", "e\u0301": "two"}})
    assert canonicalize_json({"value": "\u00e9"}) == canonicalize_json({"value": "e\u0301"})


def test_purge_scrubs_recovery_copies_and_cached_responses(identity_service):
    agent = identity_service.create_identity("erase", "test")
    retained = identity_service.create_identity("retain", "test")
    cached = FileRepository()
    cached.load_document("identities")
    cached.create("idempotency", {"key": "cached", "stored_response": {"body": json.dumps(agent)}}, id_field="key")
    result = identity_service.purge_agent_data(agent["agent_id"])
    assert result["counts"]["idempotency_responses"] == 1
    assert [a["agent_id"] for a in cached.load_document("identities")["agents"]] == [retained["agent_id"]]
    config.IDENTITIES_FILE.write_text("{broken", encoding="utf-8")
    recovered = config._safe_load(config.IDENTITIES_FILE, {"agents": []})
    assert all(a["agent_id"] != agent["agent_id"] for a in recovered["agents"])
    assert not FileRepository().list("idempotency")


def test_purge_rejects_empty_identifier(identity_service):
    agent = identity_service.create_identity("retain", "test")
    with pytest.raises(ValueError, match="non-empty"):
        identity_service.purge_agent_data("")
    assert identity_service.get_identity(agent["agent_id"]) is not None


def test_unreadable_recovery_copy_does_not_report_erasure_success(identity_service):
    agent = identity_service.create_identity("erase", "test")
    config.IDENTITIES_FILE.with_suffix(".json.bak").write_text("{broken", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        identity_service.purge_agent_data(agent["agent_id"])


def test_fast_batch_erasure_cannot_reappear_on_flush(identity_service):
    batch = FileRepository(durability="fast")
    batch.create("identities", {"agent_id": "erase-me"}, id_field="agent_id")
    identity_service.purge_agent_data("erase-me")
    batch.flush()
    assert not FileRepository().get("identities", "erase-me", id_field="agent_id")


def test_presentation_requires_expected_signed_context(credential_service, sample_agent_id):
    credential = credential_service.issue_credential(sample_agent_id, "AgentIdentityCredential", "test", {})
    presentation = credential_service.create_verifiable_presentation(sample_agent_id, [credential["id"]],
                                                                   audience_did="verifier", challenge="nonce")
    assert credential_service.verify_presentation(presentation, expected_domain="verifier", expected_challenge="nonce")["valid"]
    assert not credential_service.verify_presentation(presentation, expected_challenge="wrong")["valid"]
    presentation["proof"]["challenge"] = "replacement"
    assert not credential_service.verify_presentation(presentation)["valid"]


def test_purge_removes_unparseable_quarantined_copy(identity_service):
    agent = identity_service.create_identity("erase", "test")
    quarantined = config.IDENTITIES_FILE.parent / (config.IDENTITIES_FILE.stem + ".corrupted.123")
    quarantined.write_text("{broken " + agent["agent_id"], encoding="utf-8")
    identity_service.purge_agent_data(agent["agent_id"])
    assert not quarantined.exists()
