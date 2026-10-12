"""Recorded workflow completion must never imply assessed legal conformity."""

from copy import deepcopy

from click.testing import CliRunner

from attestix.cli import cli
from attestix.services.report_service import ReportService


def recorded_declaration(compliance_service, sample_agent_id):
    compliance_service.create_compliance_profile(
        sample_agent_id, "limited", "Provider",
        intended_purpose="Testing", transparency_obligations="AI disclosure",
    )
    compliance_service.record_conformity_assessment(
        sample_agent_id, "self", "Recorded assessor", "pass",
    )
    return compliance_service.generate_declaration_of_conformity(sample_agent_id)


def test_complete_recorded_workflow_retains_unassessed_legal_conformity(
    compliance_service, provenance_service, sample_agent_id,
):
    provenance_service.record_training_data(sample_agent_id, "Synthetic data")
    provenance_service.record_model_lineage(sample_agent_id, "Synthetic model", "Provider")
    recorded_declaration(compliance_service, sample_agent_id)
    status = compliance_service.get_compliance_status(sample_agent_id)
    assert status["workflow_complete"] is True
    assert status["compliant"] is True
    assert status["legal_conformity"] == "not_assessed"
    assert "not a legal" in status["deprecated_fields"]["compliant"]


def test_draft_and_credential_never_invent_legal_or_standards_assurance(
    compliance_service, credential_service, sample_agent_id,
):
    declaration = recorded_declaration(compliance_service, sample_agent_id)
    assert declaration["document_status"] == "draft_for_provider_review"
    assert declaration["legal_conformity"] == "not_assessed"
    assert declaration["provider_assertion_verified"] is False
    assert declaration["annex_v_fields"]["7_harmonized_standards"] == []
    credential = credential_service.get_credential(declaration["credential_id"])
    claims = credential["credentialSubject"]
    assert claims["eu_ai_act_compliant"] is None
    assert claims["declaration_generated"] is True
    assert claims["workflow_complete"] is False
    assert claims["legal_conformity"] == "not_assessed"
    assert credential_service.verify_credential_external(credential)["valid"] is True
    altered = deepcopy(credential)
    altered["credentialSubject"]["legal_conformity"] = "compliant"
    assert credential_service.verify_credential_external(altered)["valid"] is False


def test_report_labels_do_not_turn_legacy_alias_into_legal_assurance():
    html = ReportService()._section_compliance_status({"compliant": True, "completion_pct": 100})
    assert "WORKFLOW COMPLETE" in html
    assert "Legal conformity has not been assessed" in html
    assert ">COMPLIANT<" not in html


def test_org_report_exposes_qualified_workflow_counts(compliance_service, sample_agent_id):
    recorded_declaration(compliance_service, sample_agent_id)
    summary = ReportService().generate_org_report([sample_agent_id])["summary"]
    assert summary["workflow_incomplete"] == 1
    assert summary["workflow_complete"] == 0
    assert summary["legal_conformity"] == "not_assessed"
    assert "compliant" in summary["deprecated_fields"]


def test_cli_reports_evidence_status_and_unassessed_legal_conformity(
    compliance_service, sample_agent_id,
):
    recorded_declaration(compliance_service, sample_agent_id)
    result = CliRunner().invoke(cli, ["compliance", sample_agent_id])
    assert result.exit_code == 0
    assert "Evidence Workflow Status" in result.output
    assert "Legal conformity: NOT ASSESSED" in result.output
    assert "Compliant     :" not in result.output
