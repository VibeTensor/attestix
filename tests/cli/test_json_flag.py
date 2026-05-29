"""CLI tests for the ``--json`` flag (issue #36).

DevOps / CI use case: every covered command must emit a single parseable
JSON object on stdout when ``--json`` is passed, and the CI-gate commands
must set a non-zero exit code on the failure condition:

* ``attestix compliance <id> --json`` exits 0 when compliant, non-zero
  otherwise (so ``attestix compliance x --json || echo gate-failed`` works).
* ``attestix verify <id> --json`` exits 1 when the identity is invalid.
* ``attestix credential --verify-cred <id> --json`` exits 1 when invalid.

All cases drive the real Click commands through :class:`CliRunner` against the
tmp-redirected storage (``tmp_attestix`` autouse fixture in conftest).
"""

from __future__ import annotations

import json

from click.testing import CliRunner

from attestix.cli import cli
from attestix.services.cache import get_service
from attestix.services.compliance_service import ComplianceService
from attestix.services.credential_service import CredentialService
from attestix.services.identity_service import IdentityService


def _run(args):
    try:
        runner = CliRunner(mix_stderr=False)  # Click <8.3
    except TypeError:
        runner = CliRunner()
    return runner.invoke(cli, args, catch_exceptions=False)


def _parse(result) -> dict:
    """Assert stdout is a single parseable JSON object and return it."""
    payload = json.loads(result.output)
    assert isinstance(payload, dict)
    return payload


def _make_agent(name="JSON Test Agent", protocol="mcp"):
    svc = get_service(IdentityService)
    return svc.create_identity(display_name=name, source_protocol=protocol)["agent_id"]


# --- status ----------------------------------------------------------------

def test_status_json_is_parseable():
    result = _run(["status", "--json"])
    assert result.exit_code == 0
    payload = _parse(result)
    assert "version" in payload
    assert "agents_active" in payload


# --- list ------------------------------------------------------------------

def test_list_json_is_parseable():
    _make_agent()
    result = _run(["list", "--json"])
    assert result.exit_code == 0
    payload = _parse(result)
    assert payload["count"] == 1
    assert isinstance(payload["agents"], list)


def test_list_json_empty():
    result = _run(["list", "--json"])
    assert result.exit_code == 0
    payload = _parse(result)
    assert payload["count"] == 0
    assert payload["agents"] == []


# --- verify ----------------------------------------------------------------

def test_verify_json_valid_exit_zero():
    agent_id = _make_agent()
    result = _run(["verify", agent_id, "--json"])
    assert result.exit_code == 0
    payload = _parse(result)
    assert payload["valid"] is True


def test_verify_json_invalid_exit_one():
    result = _run(["verify", "attestix:doesnotexist", "--json"])
    assert result.exit_code == 1
    payload = _parse(result)
    assert payload["valid"] is False


# --- compliance (CI gate) --------------------------------------------------

def test_compliance_json_non_compliant_exit_nonzero():
    agent_id = _make_agent()
    comp = get_service(ComplianceService)
    comp.create_compliance_profile(
        agent_id=agent_id, risk_category="high", provider_name="VibeTensor",
    )
    result = _run(["compliance", agent_id, "--json"])
    # Fresh high-risk profile has many missing obligations -> not compliant.
    assert result.exit_code != 0
    payload = _parse(result)
    assert payload["compliant"] is False


def test_compliance_json_compliant_exit_zero():
    agent_id = _make_agent()
    comp = get_service(ComplianceService)
    # Minimal-risk profile: drive it all the way to compliant so the CI gate
    # exit code is 0.
    comp.create_compliance_profile(
        agent_id=agent_id,
        risk_category="minimal",
        provider_name="VibeTensor",
        intended_purpose="demo",
        transparency_obligations="Users are informed this is an AI system.",
    )
    comp.record_conformity_assessment(
        agent_id=agent_id, assessment_type="self",
        assessor_name="VibeTensor", result="pass",
    )
    from attestix.services.provenance_service import ProvenanceService
    prov = get_service(ProvenanceService)
    prov.record_training_data(agent_id, "DemoSet")
    prov.record_model_lineage(agent_id, "demo-model")
    comp.generate_declaration_of_conformity(agent_id)

    status = comp.get_compliance_status(agent_id)
    assert status.get("compliant") is True, status  # sanity: fully compliant

    result = _run(["compliance", agent_id, "--json"])
    payload = _parse(result)
    assert result.exit_code == 0
    assert payload["compliant"] is True


def test_compliance_json_no_profile_exit_nonzero():
    agent_id = _make_agent()
    result = _run(["compliance", agent_id, "--json"])
    assert result.exit_code != 0
    payload = _parse(result)
    assert "error" in payload


# --- credential --verify-cred (CI gate) ------------------------------------

def test_credential_verify_json_valid_exit_zero():
    agent_id = _make_agent()
    cred = get_service(CredentialService)
    issued = cred.issue_credential(
        subject_id=agent_id,
        credential_type="AgentIdentityCredential",
        issuer_name="VibeTensor",
        claims={},
    )
    result = _run(["credential", "--verify-cred", issued["id"], "--json"])
    assert result.exit_code == 0
    payload = _parse(result)
    assert payload["valid"] is True


def test_credential_verify_json_invalid_exit_one():
    result = _run(["credential", "--verify-cred", "urn:uuid:nope", "--json"])
    assert result.exit_code == 1
    payload = _parse(result)
    assert payload["valid"] is False


def test_credential_list_json_is_parseable():
    agent_id = _make_agent()
    cred = get_service(CredentialService)
    cred.issue_credential(
        subject_id=agent_id, credential_type="AgentIdentityCredential",
        issuer_name="VibeTensor", claims={},
    )
    result = _run(["credential", "--list", "--agent-id", agent_id, "--json"])
    assert result.exit_code == 0
    payload = _parse(result)
    assert payload["count"] == 1
    assert isinstance(payload["credentials"], list)
