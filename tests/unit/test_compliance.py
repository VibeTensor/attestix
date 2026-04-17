"""Tests for EU AI Act compliance in services/compliance_service.py."""


class TestCreateComplianceProfile:
    """Tests for creating compliance profiles with risk categorization."""

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
    """Tests for recording conformity assessments and risk-based requirements."""

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
        """Unspecified Annex III category should fail-safe to requiring third-party."""
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


class TestArticle43AnnexIIIDifferentiation:
    """Article 43 differentiates Annex III categories for conformity assessment.

    Point 1 (biometrics) requires third-party via Annex VII. Points 2-8 permit
    self-assessment via Annex VI internal control, except for three carve-outs.
    """

    def test_annex_iii_point_1_biometrics_blocks_self_assessment(
        self, compliance_service, sample_agent_id
    ):
        """Point 1 (biometrics) must use third-party / notified body assessment."""
        compliance_service.create_compliance_profile(
            sample_agent_id, "high", "BiometricCorp",
            intended_purpose="Remote biometric identification in public spaces",
            human_oversight_measures="Human review",
            annex_iii_category=1,
        )
        result = compliance_service.record_conformity_assessment(
            agent_id=sample_agent_id,
            assessment_type="self",
            assessor_name="Internal QA",
            result="pass",
        )
        assert "error" in result
        assert "Annex III Point 1" in result["error"]
        assert "third_party" in result["error"].lower() or "third-party" in result["error"].lower()

    def test_annex_iii_point_1_biometrics_allows_third_party(
        self, compliance_service, sample_agent_id
    ):
        """Point 1 (biometrics) accepts third-party assessment."""
        compliance_service.create_compliance_profile(
            sample_agent_id, "high", "BiometricCorp",
            intended_purpose="Remote biometric identification in public spaces",
            human_oversight_measures="Human review",
            annex_iii_category=1,
        )
        result = compliance_service.record_conformity_assessment(
            agent_id=sample_agent_id,
            assessment_type="third_party",
            assessor_name="TUV SUD (Notified Body)",
            result="pass",
            ce_marking_eligible=True,
        )
        assert "assessment_id" in result
        assert result["result"] == "pass"

    def test_annex_iii_point_2_critical_infrastructure_allows_self_assessment(
        self, compliance_service, sample_agent_id
    ):
        """Point 2 (critical infrastructure) permits Annex VI internal control."""
        compliance_service.create_compliance_profile(
            sample_agent_id, "high", "GridCorp",
            intended_purpose="Management of electricity grid operations",
            human_oversight_measures="SCADA operator supervision",
            annex_iii_category=2,
        )
        result = compliance_service.record_conformity_assessment(
            agent_id=sample_agent_id,
            assessment_type="self",
            assessor_name="Internal QA",
            result="pass",
        )
        assert "assessment_id" in result, f"Self-assessment should be allowed for Point 2: {result}"
        assert result["result"] == "pass"

    def test_annex_iii_point_3_education_allows_self_assessment(
        self, compliance_service, sample_agent_id
    ):
        """Point 3 (education) permits Annex VI internal control."""
        compliance_service.create_compliance_profile(
            sample_agent_id, "high", "EduCorp",
            intended_purpose="Student exam scoring and evaluation",
            human_oversight_measures="Teacher review of flagged cases",
            annex_iii_category=3,
        )
        result = compliance_service.record_conformity_assessment(
            agent_id=sample_agent_id,
            assessment_type="self",
            assessor_name="Internal QA",
            result="pass",
        )
        assert "assessment_id" in result, f"Self-assessment should be allowed for Point 3: {result}"
        assert result["result"] == "pass"

    def test_annex_iii_point_4_employment_allows_self_assessment(
        self, compliance_service, sample_agent_id
    ):
        """Point 4 (employment) permits Annex VI internal control."""
        compliance_service.create_compliance_profile(
            sample_agent_id, "high", "HRCorp",
            intended_purpose="Candidate screening and ranking",
            human_oversight_measures="HR review of final decisions",
            annex_iii_category=4,
        )
        result = compliance_service.record_conformity_assessment(
            agent_id=sample_agent_id,
            assessment_type="self",
            assessor_name="Internal QA",
            result="pass",
        )
        assert "assessment_id" in result

    def test_unspecified_annex_iii_category_blocks_self_assessment(
        self, compliance_service, sample_agent_id
    ):
        """Fail-safe: unspecified Annex III category defaults to third-party."""
        compliance_service.create_compliance_profile(
            sample_agent_id, "high", "UnknownCorp",
            intended_purpose="Unspecified high-risk AI",
            human_oversight_measures="Human review",
            # annex_iii_category intentionally omitted
        )
        result = compliance_service.record_conformity_assessment(
            agent_id=sample_agent_id,
            assessment_type="self",
            assessor_name="Internal QA",
            result="pass",
        )
        assert "error" in result
        assert "not specified" in result["error"].lower() or "fail-safe" in result["error"].lower()

    def test_exception_biometric_law_enforcement_blocks_self_assessment(
        self, compliance_service, sample_agent_id
    ):
        """Exception: biometric identification for law enforcement still requires third-party."""
        compliance_service.create_compliance_profile(
            sample_agent_id, "high", "LawEnforceCorp",
            intended_purpose="Biometric identification for law enforcement investigations",
            human_oversight_measures="Officer review",
            annex_iii_category=6,
            annex_iii_exception="biometric_identification_law_enforcement",
        )
        result = compliance_service.record_conformity_assessment(
            agent_id=sample_agent_id,
            assessment_type="self",
            assessor_name="Internal QA",
            result="pass",
        )
        assert "error" in result
        assert "biometric_identification_law_enforcement" in result["error"]

    def test_exception_financial_fraud_blocks_self_assessment(
        self, compliance_service, sample_agent_id
    ):
        """Exception: financial fraud detection still requires third-party."""
        compliance_service.create_compliance_profile(
            sample_agent_id, "high", "BankCorp",
            intended_purpose="Detection of financial fraud affecting account access",
            human_oversight_measures="Fraud analyst review",
            annex_iii_category=5,
            annex_iii_exception="financial_fraud_detection",
        )
        result = compliance_service.record_conformity_assessment(
            agent_id=sample_agent_id,
            assessment_type="self",
            assessor_name="Internal QA",
            result="pass",
        )
        assert "error" in result
        assert "financial_fraud_detection" in result["error"]

    def test_exception_political_campaign_blocks_self_assessment(
        self, compliance_service, sample_agent_id
    ):
        """Exception: political campaign organization still requires third-party."""
        compliance_service.create_compliance_profile(
            sample_agent_id, "high", "PolitechCorp",
            intended_purpose="Voter outreach and campaign message personalization",
            human_oversight_measures="Campaign manager review",
            annex_iii_category=8,
            annex_iii_exception="political_campaign_organization",
        )
        result = compliance_service.record_conformity_assessment(
            agent_id=sample_agent_id,
            assessment_type="self",
            assessor_name="Internal QA",
            result="pass",
        )
        assert "error" in result
        assert "political_campaign_organization" in result["error"]

    def test_invalid_annex_iii_category_rejected(
        self, compliance_service, sample_agent_id
    ):
        """Profile creation should reject invalid Annex III values."""
        result = compliance_service.create_compliance_profile(
            sample_agent_id, "high", "Corp",
            intended_purpose="Test",
            human_oversight_measures="Human review",
            annex_iii_category=9,
        )
        assert "error" in result
        assert "annex_iii_category" in result["error"].lower() or "annex iii" in result["error"].lower()

    def test_invalid_annex_iii_exception_rejected(
        self, compliance_service, sample_agent_id
    ):
        """Profile creation should reject unknown exception flags."""
        result = compliance_service.create_compliance_profile(
            sample_agent_id, "high", "Corp",
            intended_purpose="Test",
            human_oversight_measures="Human review",
            annex_iii_category=5,
            annex_iii_exception="bogus_flag",
        )
        assert "error" in result
        assert "annex_iii_exception" in result["error"].lower()

    def test_profile_persists_annex_iii_fields(
        self, compliance_service, sample_agent_id
    ):
        """Profile should store annex_iii_category and annex_iii_exception."""
        compliance_service.create_compliance_profile(
            sample_agent_id, "high", "Corp",
            intended_purpose="Test",
            human_oversight_measures="Human review",
            annex_iii_category=3,
        )
        profile = compliance_service.get_compliance_profile(sample_agent_id)
        assert profile["annex_iii_category"] == 3
        assert profile["annex_iii_exception"] is None


class TestDeclarationOfConformity:
    """Tests for generating EU AI Act declarations of conformity."""

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
    """Tests for compliance status gap analysis and completion tracking."""

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
