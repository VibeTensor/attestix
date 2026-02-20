"""Tests for services/compliance_service.py — EU AI Act compliance."""


class TestCreateComplianceProfile:
    def test_creates_profile(self, compliance_service, sample_agent_id):
        result = compliance_service.create_compliance_profile(
            agent_id=sample_agent_id,
            risk_category="limited",
            provider_name="TestCorp",
            intended_purpose="Testing AI",
        )
        assert result["profile_id"].startswith("comp:")
        assert result["risk_category"] == "limited"
        assert result["provider"]["name"] == "TestCorp"

    def test_rejects_unacceptable_risk(self, compliance_service, sample_agent_id):
        result = compliance_service.create_compliance_profile(
            agent_id=sample_agent_id,
            risk_category="unacceptable",
            provider_name="BadCorp",
        )
        assert "error" in result
        assert "prohibited" in result["error"].lower()

    def test_rejects_invalid_risk(self, compliance_service, sample_agent_id):
        result = compliance_service.create_compliance_profile(
            agent_id=sample_agent_id,
            risk_category="invalid",
            provider_name="Corp",
        )
        assert "error" in result

    def test_rejects_duplicate_profile(self, compliance_service, sample_agent_id):
        compliance_service.create_compliance_profile(
            sample_agent_id, "limited", "Corp",
        )
        result = compliance_service.create_compliance_profile(
            sample_agent_id, "limited", "Corp",
        )
        assert "error" in result
        assert "already exists" in result["error"]

    def test_nonexistent_agent(self, compliance_service):
        result = compliance_service.create_compliance_profile(
            agent_id="attestix:nope",
            risk_category="minimal",
            provider_name="Corp",
        )
        assert "error" in result


class TestConformityAssessment:
    def test_record_assessment(self, compliance_service, sample_agent_id):
        compliance_service.create_compliance_profile(
            sample_agent_id, "limited", "Corp",
            intended_purpose="Testing",
        )
        result = compliance_service.record_conformity_assessment(
            agent_id=sample_agent_id,
            assessment_type="self",
            assessor_name="TestAssessor",
            result="pass",
        )
        assert result["assessment_id"].startswith("assess:")
        assert result["result"] == "pass"

    def test_high_risk_requires_third_party(self, compliance_service, sample_agent_id):
        compliance_service.create_compliance_profile(
            sample_agent_id, "high", "Corp",
            intended_purpose="High-risk AI",
            human_oversight_measures="Human review",
        )
        result = compliance_service.record_conformity_assessment(
            agent_id=sample_agent_id,
            assessment_type="self",
            assessor_name="SelfAssessor",
            result="pass",
        )
        assert "error" in result
        assert "third_party" in result["error"]


class TestDeclarationOfConformity:
    def test_full_flow(self, compliance_service, sample_agent_id):
        compliance_service.create_compliance_profile(
            sample_agent_id, "limited", "Corp",
            intended_purpose="Testing AI",
            transparency_obligations="Disclose AI use",
        )
        compliance_service.record_conformity_assessment(
            sample_agent_id, "self", "Assessor", "pass",
        )
        result = compliance_service.generate_declaration_of_conformity(sample_agent_id)
        assert result["declaration_id"].startswith("decl:")
        assert "annex_v_fields" in result

    def test_requires_assessment(self, compliance_service, sample_agent_id):
        compliance_service.create_compliance_profile(
            sample_agent_id, "limited", "Corp",
            intended_purpose="Testing",
            transparency_obligations="Disclose",
        )
        result = compliance_service.generate_declaration_of_conformity(sample_agent_id)
        assert "error" in result
        assert "assessment" in result["error"].lower()


class TestComplianceStatus:
    def test_gap_analysis(self, compliance_service, sample_agent_id):
        compliance_service.create_compliance_profile(
            sample_agent_id, "limited", "Corp",
            intended_purpose="Testing",
        )
        status = compliance_service.get_compliance_status(sample_agent_id)
        assert "compliance_profile_created" in status["completed"]
        assert "intended_purpose_documented" in status["completed"]
        assert status["compliant"] is False
        assert status["completion_pct"] > 0
