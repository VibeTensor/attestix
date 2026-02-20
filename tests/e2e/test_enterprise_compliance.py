"""E2E: Enterprise AI Team persona.

Workflow: Create identity → compliance profile → provenance →
assessment → declaration → verify credential.
"""


class TestEnterpriseComplianceWorkflow:
    def test_full_eu_ai_act_flow(
        self, identity_service, compliance_service,
        provenance_service, credential_service,
    ):
        # Step 1: Create the agent identity
        agent = identity_service.create_identity(
            display_name="EnterpriseClassifier",
            source_protocol="api_key",
            capabilities=["classify", "predict"],
            description="A document classification AI",
            issuer_name="EnterpriseCorp",
        )
        agent_id = agent["agent_id"]

        # Step 2: Create EU AI Act compliance profile
        profile = compliance_service.create_compliance_profile(
            agent_id=agent_id,
            risk_category="limited",
            provider_name="EnterpriseCorp",
            intended_purpose="Automated document classification for internal use",
            transparency_obligations="Users informed of AI-generated classifications",
        )
        assert profile["risk_category"] == "limited"

        # Step 3: Record training data provenance (Article 10)
        training = provenance_service.record_training_data(
            agent_id=agent_id,
            dataset_name="InternalDocs-v3",
            license="proprietary",
            data_categories=["text", "metadata"],
            contains_personal_data=False,
        )
        assert training["entry_type"] == "training_data"

        # Step 4: Record model lineage (Article 11)
        lineage = provenance_service.record_model_lineage(
            agent_id=agent_id,
            base_model="bert-base-uncased",
            base_model_provider="Hugging Face",
            fine_tuning_method="LoRA",
            evaluation_metrics={"f1": 0.92, "accuracy": 0.95},
        )
        assert lineage["entry_type"] == "model_lineage"

        # Step 5: Record conformity assessment (Article 43)
        assessment = compliance_service.record_conformity_assessment(
            agent_id=agent_id,
            assessment_type="self",
            assessor_name="InternalQA",
            result="pass",
        )
        assert assessment["result"] == "pass"

        # Step 6: Generate declaration of conformity (Annex V)
        declaration = compliance_service.generate_declaration_of_conformity(agent_id)
        assert declaration["declaration_id"].startswith("decl:")
        assert "annex_v_fields" in declaration

        # Step 7: Check compliance status (should be 100%)
        status = compliance_service.get_compliance_status(agent_id)
        assert status["compliant"] is True
        assert len(status["missing"]) == 0

        # Step 8: Verify the auto-issued credential
        creds = credential_service.list_credentials(
            agent_id=agent_id,
            credential_type="EUAIActComplianceCredential",
        )
        assert len(creds) >= 1
        vc = creds[0]
        verification = credential_service.verify_credential(vc["id"])
        assert verification["valid"] is True

    def test_high_risk_requires_third_party(
        self, identity_service, compliance_service,
    ):
        agent = identity_service.create_identity(
            "HighRiskBot", "mcp",
            description="High risk AI system",
        )
        agent_id = agent["agent_id"]

        compliance_service.create_compliance_profile(
            agent_id, "high", "Corp",
            intended_purpose="Critical infrastructure",
            transparency_obligations="Full disclosure",
            human_oversight_measures="Human-in-the-loop",
        )

        # Self-assessment should be blocked for high-risk
        result = compliance_service.record_conformity_assessment(
            agent_id, "self", "SelfAssessor", "pass",
        )
        assert "error" in result

        # Third-party should work
        result = compliance_service.record_conformity_assessment(
            agent_id, "third_party", "ExternalAuditor", "pass",
            ce_marking_eligible=True,
        )
        assert result["result"] == "pass"
        assert result["ce_marking_eligible"] is True
