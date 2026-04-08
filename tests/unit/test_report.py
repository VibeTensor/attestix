"""Tests for HTML/PDF compliance report generation in services/report_service.py."""


class TestGenerateHtmlReport:
    """Tests for self-contained HTML compliance report generation."""

    def test_report_for_nonexistent_agent(self, report_service):
        result = report_service.generate_html_report("attestix:nope")
        assert "error" in result
        assert "not found" in result["error"]

    def test_minimal_report_agent_only(self, report_service, identity_service):
        """An agent with no compliance profile still produces valid HTML."""
        agent = identity_service.create_identity(
            display_name="Bare Agent",
            source_protocol="mcp",
            capabilities=["read"],
        )
        result = report_service.generate_html_report(agent["agent_id"])
        assert "error" not in result
        assert "html" in result
        html = result["html"]
        assert html.startswith("<!DOCTYPE html>")
        assert "Bare Agent" in html
        assert "Agent Identity" in html

    def test_full_compliance_workflow_report(
        self,
        report_service,
        identity_service,
        compliance_service,
        provenance_service,
    ):
        """End-to-end: create agent, run compliance workflow, generate report."""
        # 1. Create agent
        agent = identity_service.create_identity(
            display_name="Compliant Bot",
            source_protocol="mcp",
            capabilities=["read", "write", "execute"],
            description="A fully compliant demonstration agent",
        )
        agent_id = agent["agent_id"]

        # 2. Create compliance profile
        compliance_service.create_compliance_profile(
            agent_id=agent_id,
            risk_category="limited",
            provider_name="TestCorp Ltd",
            intended_purpose="Automated document review",
            transparency_obligations="Discloses AI usage to end users",
        )

        # 3. Record conformity assessment
        compliance_service.record_conformity_assessment(
            agent_id=agent_id,
            assessment_type="self",
            assessor_name="Internal QA",
            result="pass",
            findings="All checks passed",
        )

        # 4. Generate declaration of conformity
        compliance_service.generate_declaration_of_conformity(agent_id)

        # 5. Record training data provenance
        provenance_service.record_training_data(
            agent_id=agent_id,
            dataset_name="LegalDocs-v2",
            source_url="https://example.com/datasets/legaldocs",
            license="CC-BY-4.0",
            data_categories=["legal", "contracts"],
        )

        # 6. Record model lineage
        provenance_service.record_model_lineage(
            agent_id=agent_id,
            base_model="gpt-4o",
            base_model_provider="OpenAI",
            fine_tuning_method="LoRA",
            evaluation_metrics={"accuracy": 0.95, "f1": 0.93},
        )

        # 7. Log an audit action
        provenance_service.log_action(
            agent_id=agent_id,
            action_type="inference",
            input_summary="Contract review request",
            output_summary="Compliance flags identified",
        )

        # 8. Generate the report
        result = report_service.generate_html_report(agent_id)
        assert "error" not in result
        html = result["html"]
        assert result["agent_id"] == agent_id
        assert result["generated_at"]

        # Validate structure
        assert "<!DOCTYPE html>" in html
        assert "</html>" in html

        # Validate key sections are present
        assert "Agent Identity" in html
        assert "Compliant Bot" in html
        assert "Risk Classification" in html
        assert "LIMITED" in html
        assert "Compliance Status" in html
        assert "Declaration of Conformity" in html
        assert "Training Data Provenance" in html
        assert "LegalDocs-v2" in html
        assert "Model Lineage" in html
        assert "gpt-4o" in html
        assert "Audit Trail" in html
        assert "inference" in html
        assert "Credentials" in html

        # Verify branding
        assert "ATTESTIX" in html
        assert "#4F46E5" in html

    def test_report_contains_inline_css(self, report_service, identity_service):
        """The HTML report must be self-contained with inline styles."""
        agent = identity_service.create_identity(
            display_name="CSS Check Agent",
            source_protocol="mcp",
        )
        result = report_service.generate_html_report(agent["agent_id"])
        html = result["html"]
        assert "<style>" in html
        assert "</style>" in html
        # No external stylesheet references
        assert 'rel="stylesheet"' not in html

    def test_report_escapes_html(self, report_service, identity_service):
        """XSS-sensitive characters must be escaped in the report."""
        agent = identity_service.create_identity(
            display_name='<script>alert("xss")</script>',
            source_protocol="mcp",
        )
        result = report_service.generate_html_report(agent["agent_id"])
        html = result["html"]
        assert "<script>" not in html
        assert "&lt;script&gt;" in html


class TestDigitalSignatureSection:
    """Tests for the Digital Signature Verification section in HTML reports."""

    def test_signature_section_present(self, report_service, identity_service):
        """Every report must include the Digital Signature Verification section."""
        agent = identity_service.create_identity(
            display_name="Sig Test Agent",
            source_protocol="mcp",
        )
        result = report_service.generate_html_report(agent["agent_id"])
        assert "error" not in result
        html = result["html"]
        assert "Digital Signature Verification" in html

    def test_signature_section_contains_signing_key_did(self, report_service, identity_service):
        """The report must show the signing key DID from agent.issuer.did."""
        agent = identity_service.create_identity(
            display_name="DID Check Agent",
            source_protocol="mcp",
        )
        result = report_service.generate_html_report(agent["agent_id"])
        html = result["html"]
        issuer_did = agent["issuer"]["did"]
        assert issuer_did in html

    def test_signature_section_algorithm(self, report_service, identity_service):
        """The report must declare Ed25519Signature2020 as the algorithm."""
        agent = identity_service.create_identity(
            display_name="Algo Check Agent",
            source_protocol="mcp",
        )
        result = report_service.generate_html_report(agent["agent_id"])
        html = result["html"]
        assert "Ed25519Signature2020" in html

    def test_signature_section_truncated_value(self, report_service, identity_service):
        """The signature value must be truncated with ellipsis."""
        agent = identity_service.create_identity(
            display_name="Truncation Agent",
            source_protocol="mcp",
        )
        result = report_service.generate_html_report(agent["agent_id"])
        html = result["html"]
        # Signature should be truncated: first 40 chars followed by ...
        assert "..." in html
        sig_raw = agent.get("signature", "")
        if sig_raw and len(sig_raw) > 40:
            assert sig_raw[:40] in html

    def test_signature_section_verification_status(self, report_service, identity_service):
        """The report must show a verification status for the signature."""
        agent = identity_service.create_identity(
            display_name="Verify Status Agent",
            source_protocol="mcp",
        )
        result = report_service.generate_html_report(agent["agent_id"])
        html = result["html"]
        # Either VALID or UNVERIFIED must appear
        assert "VALID" in html or "UNVERIFIED" in html

    def test_signature_section_verify_command_hint(self, report_service, identity_service):
        """The report must include the CLI verify command hint."""
        agent = identity_service.create_identity(
            display_name="CLI Hint Agent",
            source_protocol="mcp",
        )
        result = report_service.generate_html_report(agent["agent_id"])
        html = result["html"]
        assert "attestix verify" in html
        assert agent["agent_id"] in html

    def test_signature_section_valid_status_for_fresh_agent(self, report_service, identity_service):
        """A freshly created agent should have a VALID signature in the report."""
        agent = identity_service.create_identity(
            display_name="Fresh Signed Agent",
            source_protocol="mcp",
        )
        result = report_service.generate_html_report(agent["agent_id"])
        html = result["html"]
        assert "VALID" in html

    def test_credentials_section_proof_columns(self, report_service, identity_service, credential_service):
        """Credentials section must include Proof Type, Proof Value, and Verification Method columns."""
        agent = identity_service.create_identity(
            display_name="Cred Proof Agent",
            source_protocol="mcp",
        )
        credential_service.issue_credential(
            agent_id=agent["agent_id"],
            credential_type="ComplianceCertificate",
            claims={"status": "compliant"},
        )
        result = report_service.generate_html_report(agent["agent_id"])
        html = result["html"]
        assert "Proof Type" in html
        assert "Proof Value" in html
        assert "Verification Method" in html
        assert "Ed25519Signature2020" in html

    def test_credentials_section_proof_value_truncated(self, report_service, identity_service, credential_service):
        """The proof value displayed in the credentials table must be truncated."""
        agent = identity_service.create_identity(
            display_name="Proof Trunc Agent",
            source_protocol="mcp",
        )
        cred = credential_service.issue_credential(
            agent_id=agent["agent_id"],
            credential_type="ComplianceCertificate",
            claims={"status": "compliant"},
        )
        result = report_service.generate_html_report(agent["agent_id"])
        html = result["html"]
        proof_value = cred.get("proof", {}).get("proofValue", "")
        if proof_value and len(proof_value) > 40:
            assert proof_value[:40] in html
            assert proof_value not in html  # full value should not appear


class TestGeneratePdfReport:
    """Tests for PDF report generation (fallback when weasyprint missing)."""

    def test_pdf_fallback_without_weasyprint(self, report_service, identity_service):
        """When weasyprint is not installed, returns HTML with fallback flag."""
        agent = identity_service.create_identity(
            display_name="PDF Fallback Agent",
            source_protocol="mcp",
        )
        result = report_service.generate_pdf_report(agent["agent_id"])

        # weasyprint is likely not installed in the test environment,
        # so we expect either a fallback or a successful PDF
        if result.get("fallback"):
            assert "html" in result
            assert "weasyprint" in result["message"]
        else:
            # weasyprint is available
            assert "pdf_bytes" in result or "pdf_path" in result

    def test_pdf_nonexistent_agent(self, report_service):
        result = report_service.generate_pdf_report("attestix:nope")
        assert "error" in result
