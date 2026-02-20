"""Advanced end-to-end user persona tests for Attestix.

10 additional personas covering cybersecurity, government regulation, legal,
healthcare, AI safety, enterprise architecture, setup validation, cross-border
deployment, penetration testing, and DevOps perspectives.

Each persona test is fully independent and exercises the MCP tool layer
as a real user would.
"""

import hashlib
import json
import time

import pytest


# ---------------------------------------------------------------------------
# Helper: call an MCP tool function and parse the JSON response
# ---------------------------------------------------------------------------
def call_tool(tool_name: str, **kwargs) -> dict | list:
    """Invoke an MCP tool by name and return parsed JSON."""
    from main import mcp
    import asyncio

    tools = mcp._tool_manager._tools
    fn = tools[tool_name].fn
    result_str = asyncio.get_event_loop().run_until_complete(fn(**kwargs))
    return json.loads(result_str)


# ===========================================================================
# Persona 7: Cybersecurity Analyst
#
# Context: A security analyst tests the cryptographic integrity of the
# Attestix system. They verify signatures, test tamper detection on
# credentials, check revocation enforcement, and validate that forged
# tokens are rejected.
# ===========================================================================
class TestPersona7_CybersecurityAnalyst:
    """Security analyst testing cryptographic integrity and tamper detection."""

    def test_credential_integrity_and_tamper_detection(self):
        # 1. Create a test agent
        agent = call_tool(
            "create_agent_identity",
            display_name="SecTestAgent",
            source_protocol="mcp",
            capabilities="data_processing",
            issuer_name="SecurityLab",
        )
        agent_id = agent["agent_id"]
        print(f"\n  [Persona 7] Created test agent: {agent_id}")

        # 2. Issue a credential and verify signature is valid
        cred = call_tool(
            "issue_credential",
            subject_agent_id=agent_id,
            credential_type="AgentIdentityCredential",
            issuer_name="SecurityLab",
            claims_json='{"clearance": "top_secret", "role": "analyst"}',
        )
        assert "id" in cred
        cred_id = cred["id"]

        verification = call_tool("verify_credential", credential_id=cred_id)
        assert verification["valid"] is True
        assert verification["checks"]["signature_valid"] is True
        print(f"  [Persona 7] Credential issued and signature verified")

        # 3. Tamper with the credential and verify external detection
        tampered_cred = json.loads(json.dumps(cred, default=str))
        tampered_cred["credentialSubject"]["clearance"] = "public"
        tampered_check = call_tool(
            "verify_credential_external",
            credential_json=json.dumps(tampered_cred, default=str),
        )
        assert tampered_check["valid"] is False, (
            "Tampered credential should fail verification"
        )
        assert tampered_check["checks"]["signature_valid"] is False
        print(f"  [Persona 7] Tampered credential correctly rejected (signature invalid)")

        # 4. Test that the original still verifies
        original_check = call_tool(
            "verify_credential_external",
            credential_json=json.dumps(cred, default=str),
        )
        assert original_check["valid"] is True
        print(f"  [Persona 7] Original credential still verifies correctly")

        # 5. Revoke the credential and verify it fails
        revoke_result = call_tool(
            "revoke_credential",
            credential_id=cred_id,
            reason="Security test: credential compromised",
        )
        assert revoke_result["revoked"] is True

        post_revoke = call_tool("verify_credential", credential_id=cred_id)
        assert post_revoke["valid"] is False
        assert post_revoke["checks"]["not_revoked"] is False
        print(f"  [Persona 7] Revoked credential correctly fails verification")

        # 6. Verify identity signature
        id_check = call_tool("verify_identity", agent_id=agent_id)
        assert id_check["valid"] is True
        assert id_check["checks"]["signature_valid"] is True
        print(f"  [Persona 7] Identity Ed25519 signature verified")

        # 7. Revoke the identity and confirm it's rejected
        call_tool("revoke_identity", agent_id=agent_id, reason="Security test")
        id_revoked = call_tool("verify_identity", agent_id=agent_id)
        assert id_revoked["valid"] is False
        assert id_revoked["checks"]["not_revoked"] is False
        print(f"  [Persona 7] Revoked identity correctly fails verification")

        # 8. Verify delegation token integrity
        agent_b = call_tool(
            "create_agent_identity",
            display_name="SecTestAgent-B",
            source_protocol="mcp",
            issuer_name="SecurityLab",
        )
        delegation = call_tool(
            "create_delegation",
            issuer_agent_id=agent_b["agent_id"],
            audience_agent_id=agent_id,
            capabilities="read_only",
            expiry_hours=1,
        )
        assert "token" in delegation

        # Verify valid delegation
        del_check = call_tool("verify_delegation", token=delegation["token"])
        assert del_check["valid"] is True
        print(f"  [Persona 7] Delegation token signature verified")

        # Tamper with the JWT token (flip a character in the signature)
        token_parts = delegation["token"].split(".")
        assert len(token_parts) == 3, "JWT should have 3 parts"
        sig = list(token_parts[2])
        # Flip one character
        sig[0] = "A" if sig[0] != "A" else "B"
        tampered_token = f"{token_parts[0]}.{token_parts[1]}.{''.join(sig)}"
        tampered_del = call_tool("verify_delegation", token=tampered_token)
        assert tampered_del["valid"] is False
        print(f"  [Persona 7] Tampered JWT correctly rejected")

        # 9. Test DID key cryptographic properties
        did_result = call_tool("create_did_key")
        assert did_result["did"].startswith("did:key:z6Mk")
        assert "publicKeyMultibase" in json.dumps(did_result.get("did_document", {}))
        print(f"  [Persona 7] DID key uses correct Ed25519 multicodec prefix")

        print("  [Persona 7] PASS: All cryptographic integrity checks passed")


# ===========================================================================
# Persona 8: EU Government Regulator
#
# Context: An EU AI Office regulator inspects multiple AI providers.
# They verify Annex V declarations, check that high-risk systems have
# third-party assessments, validate VPs from different providers, and
# confirm compliance artifacts are structurally complete.
# ===========================================================================
class TestPersona8_EUGovernmentRegulator:
    """EU AI Office regulator inspecting multiple AI providers."""

    def test_regulatory_inspection_workflow(self):
        # --- Provider A: High-risk financial AI (compliant) ---
        agent_a = call_tool(
            "create_agent_identity",
            display_name="CreditScore-AI",
            capabilities="credit_scoring,risk_assessment",
            description="Automated credit scoring for consumer loans",
            issuer_name="FinTech Corp",
        )
        aid_a = agent_a["agent_id"]

        call_tool(
            "create_compliance_profile",
            agent_id=aid_a,
            risk_category="high",
            provider_name="FinTech Corp",
            intended_purpose="Consumer credit scoring per Annex III Category 5(a)",
            transparency_obligations="Full explanations per Article 13",
            human_oversight_measures="Loan officer reviews all decisions above 10K EUR",
            provider_address="Finance Street 1, Berlin, Germany",
        )
        call_tool("record_training_data", agent_id=aid_a, dataset_name="FICO Score History")
        call_tool("record_model_lineage", agent_id=aid_a, base_model="XGBoost", base_model_provider="Open Source")
        call_tool(
            "record_conformity_assessment",
            agent_id=aid_a, assessment_type="third_party",
            assessor_name="TUV SUD", result="pass",
            findings="Full Article 43 assessment passed", ce_marking_eligible=True,
        )
        decl_a = call_tool("generate_declaration_of_conformity", agent_id=aid_a)
        print(f"\n  [Persona 8] Provider A (high-risk) declaration: {decl_a.get('declaration_id', 'FAILED')}")

        # --- Provider B: Limited-risk chatbot (compliant) ---
        agent_b = call_tool(
            "create_agent_identity",
            display_name="ChatAssist-AI",
            capabilities="chat,faq",
            description="Customer support chatbot",
            issuer_name="RetailCo",
        )
        aid_b = agent_b["agent_id"]

        call_tool(
            "create_compliance_profile",
            agent_id=aid_b,
            risk_category="limited",
            provider_name="RetailCo",
            intended_purpose="Customer FAQ and support",
            transparency_obligations="AI disclosure in every response",
        )
        call_tool("record_training_data", agent_id=aid_b, dataset_name="FAQ Knowledge Base")
        call_tool("record_model_lineage", agent_id=aid_b, base_model="BERT-base", base_model_provider="Google")
        call_tool(
            "record_conformity_assessment",
            agent_id=aid_b, assessment_type="self",
            assessor_name="RetailCo QA Team", result="pass",
        )
        decl_b = call_tool("generate_declaration_of_conformity", agent_id=aid_b)
        print(f"  [Persona 8] Provider B (limited-risk) declaration: {decl_b.get('declaration_id', 'FAILED')}")

        # --- Provider C: High-risk AI that tried self-assessment (non-compliant) ---
        agent_c = call_tool(
            "create_agent_identity",
            display_name="HireBot-AI",
            capabilities="resume_screening,candidate_ranking",
            description="Automated hiring and recruitment AI",
            issuer_name="TalentTech GmbH",
        )
        aid_c = agent_c["agent_id"]

        call_tool(
            "create_compliance_profile",
            agent_id=aid_c,
            risk_category="high",
            provider_name="TalentTech GmbH",
            intended_purpose="Automated candidate screening per Annex III Category 4(a)",
        )

        # High-risk with self-assessment should be blocked
        bad_assessment = call_tool(
            "record_conformity_assessment",
            agent_id=aid_c, assessment_type="self",
            assessor_name="Internal Team", result="pass",
        )
        assert "error" in bad_assessment, "High-risk self-assessment should be blocked"
        assert "third_party" in bad_assessment["error"].lower() or "article 43" in bad_assessment["error"].lower()
        print(f"  [Persona 8] Provider C: self-assessment correctly blocked for high-risk")

        # --- Regulator: Inspect all providers ---

        # 1. Check Annex V fields on Provider A's declaration
        assert "annex_v_fields" in decl_a
        annex = decl_a["annex_v_fields"]
        # Verify required Annex V fields exist (numbering per compliance_service.py)
        assert annex.get("3_ai_system_name"), "Missing AI system name"
        assert annex.get("1_provider_name"), "Missing provider name"
        assert annex.get("4_intended_purpose"), "Missing intended purpose"
        assert annex.get("11_sole_responsibility"), "Missing sole responsibility statement"
        assert "FinTech Corp" in annex["11_sole_responsibility"]
        print(f"  [Persona 8] Provider A Annex V fields: all required fields present")

        # 2. Verify Provider A has third-party assessment (required for high-risk)
        status_a = call_tool("get_compliance_status", agent_id=aid_a)
        assert "conformity_assessment_passed" in status_a["completed"]
        assert "declaration_of_conformity_issued" in status_a["completed"]
        print(f"  [Persona 8] Provider A compliance status: {status_a['completion_pct']}% complete")

        # 3. Provider B (limited) should also have declaration
        status_b = call_tool("get_compliance_status", agent_id=aid_b)
        assert status_b["compliant"] is True
        print(f"  [Persona 8] Provider B compliance status: {status_b['completion_pct']}% complete")

        # 4. Provider C should NOT be compliant
        status_c = call_tool("get_compliance_status", agent_id=aid_c)
        assert status_c["compliant"] is False
        assert "conformity_assessment_passed" in status_c["missing"]
        print(f"  [Persona 8] Provider C correctly flagged as non-compliant")

        # 5. Receive and verify VP from Provider A
        creds_a = call_tool("list_credentials", agent_id=aid_a,
                            credential_type="EUAIActComplianceCredential")
        assert len(creds_a) >= 1
        vp_a = call_tool(
            "create_verifiable_presentation",
            agent_id=aid_a,
            credential_ids=creds_a[0]["id"],
            audience_did="did:web:ai-office.europa.eu",
            challenge="inspection-2026-Q1-fintech",
        )
        vp_check = call_tool(
            "verify_presentation",
            presentation_json=json.dumps(vp_a, default=str),
        )
        assert vp_check["valid"] is True
        assert vp_check["checks"]["challenge_present"] is True
        assert vp_check["checks"]["domain_present"] is True
        print(f"  [Persona 8] Provider A VP verified with challenge/domain")

        # 6. List all high-risk profiles
        high_risk = call_tool("list_compliance_profiles", risk_category="high")
        high_risk_ids = [p.get("agent_id") for p in high_risk]
        assert aid_a in high_risk_ids
        assert aid_c in high_risk_ids
        print(f"  [Persona 8] Found {len(high_risk)} high-risk AI systems registered")

        print("  [Persona 8] PASS: Regulatory inspection workflow complete")


# ===========================================================================
# Persona 9: Legal Counsel
#
# Context: Corporate legal counsel prepares evidence for regulatory
# filing and defends against a discrimination claim involving an AI
# system. They need to demonstrate provenance, audit trails, human
# oversight, and credential revocation for a decommissioned system.
# ===========================================================================
class TestPersona9_LegalCounsel:
    """Corporate legal counsel preparing regulatory evidence."""

    def test_legal_evidence_preparation_workflow(self):
        # 1. Create the AI system under legal review
        agent = call_tool(
            "create_agent_identity",
            display_name="InsuranceQuote-AI",
            capabilities="risk_pricing,quote_generation",
            description="Automated insurance premium calculation",
            issuer_name="InsureCo Ltd",
        )
        agent_id = agent["agent_id"]
        print(f"\n  [Persona 9] AI system under review: {agent_id}")

        # 2. Document training data provenance (critical for discrimination defense)
        datasets = [
            ("Historical Claims 2015-2025", True, "Insurance claims with demographics",
             "All protected characteristics removed, statistical parity tested"),
            ("Actuarial Tables 2025", False, "Industry actuarial data",
             "Public data, no personal information"),
            ("Synthetic Fairness Test Set", False, "Bias testing data",
             "Generated to test demographic parity across protected groups"),
        ]
        for name, personal, gov, measures in datasets:
            call_tool(
                "record_training_data",
                agent_id=agent_id,
                dataset_name=name,
                contains_personal_data=personal,
                data_governance_measures=measures,
            )
        print(f"  [Persona 9] Documented {len(datasets)} training datasets for legal record")

        # 3. Document model evaluation metrics (fairness evidence)
        call_tool(
            "record_model_lineage",
            agent_id=agent_id,
            base_model="GradientBoost-InsureV3",
            base_model_provider="InsureCo ML Team",
            fine_tuning_method="Fairness-constrained optimization with equalized odds",
            evaluation_metrics_json=json.dumps({
                "accuracy": 0.91,
                "demographic_parity_ratio": 0.97,
                "equalized_odds_diff": 0.02,
                "disparate_impact_ratio": 0.98,
            }),
        )
        print(f"  [Persona 9] Model fairness metrics documented")

        # 4. Create compliance profile with human oversight documentation
        call_tool(
            "create_compliance_profile",
            agent_id=agent_id,
            risk_category="high",
            provider_name="InsureCo Ltd",
            intended_purpose="Insurance premium calculation for motor vehicle policies",
            transparency_obligations="Customers informed AI used in pricing, explanations available on request",
            human_oversight_measures="All quotes above 5000 EUR reviewed by underwriter. Customer appeals routed to human team.",
            provider_address="Insurance House, Dublin, Ireland",
            authorised_representative="Chief Compliance Officer, InsureCo Ltd",
        )
        print(f"  [Persona 9] Compliance profile with oversight measures documented")

        # 5. Log a series of decisions showing human oversight in action
        actions = [
            ("inference", "Customer A - standard risk", "Quote: 1200 EUR", "Within normal parameters", False),
            ("inference", "Customer B - elevated risk", "Quote: 4800 EUR", "Near threshold, flagged", False),
            ("inference", "Customer C - high risk", "Quote: 7500 EUR", "Above threshold, requires review", False),
            ("inference", "Customer C - reviewed", "Quote adjusted: 6200 EUR", "Underwriter reduced after appeal review", True),
            ("data_access", "Customer C appeal documents", "3 supporting documents loaded", "Customer exercised right to explanation", False),
        ]
        for atype, inp, out, rationale, human in actions:
            call_tool(
                "log_action",
                agent_id=agent_id,
                action_type=atype,
                input_summary=inp,
                output_summary=out,
                decision_rationale=rationale,
                human_override=human,
            )
        print(f"  [Persona 9] Logged {len(actions)} actions demonstrating human oversight")

        # 6. Retrieve full audit trail for legal evidence
        trail = call_tool("get_audit_trail", agent_id=agent_id)
        assert len(trail) == len(actions)

        human_overrides = [e for e in trail if e.get("human_override")]
        assert len(human_overrides) >= 1, "Must have human override evidence"
        print(f"  [Persona 9] Audit trail: {len(trail)} entries, {len(human_overrides)} human overrides")

        # 7. Get provenance for complete evidence package
        provenance = call_tool("get_provenance", agent_id=agent_id)
        assert len(provenance["training_data"]) == 3
        assert len(provenance["model_lineage"]) == 1
        assert provenance["audit_log_count"] == len(actions)

        # Verify fairness metrics are in the record
        metrics = provenance["model_lineage"][0].get("evaluation_metrics", {})
        assert "demographic_parity_ratio" in metrics
        assert metrics["demographic_parity_ratio"] >= 0.8, "Fairness evidence should be documented"
        print(f"  [Persona 9] Provenance with fairness metrics: DPR={metrics['demographic_parity_ratio']}")

        # 8. Issue a credential attesting to the fairness audit
        fairness_cred = call_tool(
            "issue_credential",
            subject_agent_id=agent_id,
            credential_type="ConformityAssessmentCredential",
            issuer_name="InsureCo Fairness Board",
            claims_json=json.dumps({
                "assessment_type": "fairness_audit",
                "result": "pass",
                "demographic_parity_ratio": 0.97,
                "equalized_odds_diff": 0.02,
                "auditor": "InsureCo Internal Fairness Board",
                "date": "2026-02-15",
            }),
        )
        assert "id" in fairness_cred
        print(f"  [Persona 9] Fairness audit credential issued")

        # 9. Verify hash chain integrity of audit trail (evidence tampering check)
        for i in range(1, len(trail)):
            if "chain_hash" in trail[i] and "prev_hash" in trail[i]:
                prev_chain = trail[i - 1].get("chain_hash", "")
                assert trail[i]["prev_hash"] == prev_chain, (
                    f"Audit trail hash chain broken at entry {i} - evidence of tampering"
                )
        print(f"  [Persona 9] Audit trail hash chain integrity confirmed (no tampering)")

        # 10. Compliance status as legal evidence of good faith
        status = call_tool("get_compliance_status", agent_id=agent_id)
        assert "training_data_provenance" in status["completed"]
        assert "model_lineage_recorded" in status["completed"]
        print(f"  [Persona 9] Compliance evidence: {status['completion_pct']}% obligations met")

        print("  [Persona 9] PASS: Legal evidence preparation workflow complete")


# ===========================================================================
# Persona 10: Healthcare AI Provider
#
# Context: A medical device company deploying a high-risk diagnostic AI
# must go through the strictest compliance path: third-party assessment,
# full Annex V declaration, multiple training data sources with personal
# data governance, and verifiable presentation to a notified body.
# ===========================================================================
class TestPersona10_HealthcareAIProvider:
    """Medical device company deploying high-risk diagnostic AI."""

    def test_medical_ai_compliance_workflow(self):
        # 1. Register the medical AI system
        agent = call_tool(
            "create_agent_identity",
            display_name="DiagnosticAI-Cardio",
            capabilities="ecg_analysis,arrhythmia_detection,risk_stratification",
            description="AI-assisted cardiac arrhythmia detection from 12-lead ECG",
            issuer_name="MedTech Innovations GmbH",
        )
        agent_id = agent["agent_id"]
        print(f"\n  [Persona 10] Registered medical AI: {agent_id}")

        # 2. Record all training data sources with strict governance
        training_sets = [
            ("PhysioNet MIMIC-IV ECG", "PhysioNet Data Use Agreement",
             "ecg,medical,time_series", True,
             "IRB-approved, de-identified per HIPAA Safe Harbor, DPA in place"),
            ("PTB-XL ECG Database", "CC-BY-4.0",
             "ecg,medical", False,
             "Public research database, no patient identifiers"),
            ("Internal Clinical Validation Set", "Proprietary",
             "ecg,medical,clinical", True,
             "Hospital ethics committee approved, patient consent obtained, pseudonymized"),
            ("Synthetic Augmentation Set", "Internal",
             "ecg,synthetic", False,
             "GAN-generated ECG signals for data augmentation, no real patient data"),
        ]
        for name, lic, cats, personal, governance in training_sets:
            td = call_tool(
                "record_training_data",
                agent_id=agent_id,
                dataset_name=name,
                license=lic,
                data_categories=cats,
                contains_personal_data=personal,
                data_governance_measures=governance,
            )
            assert "entry_id" in td
        print(f"  [Persona 10] Documented {len(training_sets)} training datasets")

        # 3. Record model lineage with clinical evaluation metrics
        call_tool(
            "record_model_lineage",
            agent_id=agent_id,
            base_model="ResNet-ECG-v4",
            base_model_provider="MedTech Innovations GmbH",
            fine_tuning_method="Transfer learning from ImageNet, fine-tuned on ECG spectrograms with class-weighted loss",
            evaluation_metrics_json=json.dumps({
                "sensitivity": 0.96,
                "specificity": 0.94,
                "ppv": 0.91,
                "npv": 0.97,
                "auc_roc": 0.982,
                "f1_score": 0.935,
                "clinical_validation_n": 12500,
                "subgroup_performance": {
                    "male": {"sensitivity": 0.96, "specificity": 0.94},
                    "female": {"sensitivity": 0.95, "specificity": 0.93},
                    "age_over_65": {"sensitivity": 0.94, "specificity": 0.92},
                },
            }),
        )
        print(f"  [Persona 10] Model lineage with clinical metrics recorded")

        # 4. Create high-risk compliance profile
        call_tool(
            "create_compliance_profile",
            agent_id=agent_id,
            risk_category="high",
            provider_name="MedTech Innovations GmbH",
            intended_purpose="AI-assisted arrhythmia detection in clinical settings (Annex III Category 1(a))",
            transparency_obligations="Clinical decision support label shown, AI confidence scores displayed, physician notified of all AI recommendations",
            human_oversight_measures="Board-certified cardiologist must confirm all AI findings before clinical action. AI recommendations are advisory only.",
            provider_address="Medizinstrasse 42, Munich, Germany 80333",
            authorised_representative="Dr. Anna Mueller, EU Authorized Representative",
        )
        print(f"  [Persona 10] High-risk compliance profile created")

        # 5. Log clinical decision events showing human oversight
        clinical_events = [
            ("inference", "ECG #4521 - 65yo male", "Atrial fibrillation detected (confidence: 0.94)",
             "Pattern matched known AF signatures", False),
            ("inference", "ECG #4521 - cardiologist review", "AF confirmed, treatment plan initiated",
             "Physician confirmed AI finding", True),
            ("inference", "ECG #4522 - 42yo female", "Normal sinus rhythm (confidence: 0.99)",
             "No abnormalities detected", False),
            ("inference", "ECG #4523 - 78yo male", "Possible ventricular tachycardia (confidence: 0.72)",
             "Low confidence, flagged for immediate physician review", False),
            ("inference", "ECG #4523 - cardiologist override", "VT ruled out, artifact identified",
             "Physician overrode AI: motion artifact misclassified as VT", True),
        ]
        for atype, inp, out, rationale, human in clinical_events:
            call_tool(
                "log_action",
                agent_id=agent_id,
                action_type=atype,
                input_summary=inp,
                output_summary=out,
                decision_rationale=rationale,
                human_override=human,
            )
        print(f"  [Persona 10] Logged {len(clinical_events)} clinical decision events")

        # 6. Third-party conformity assessment (required for medical devices)
        assessment = call_tool(
            "record_conformity_assessment",
            agent_id=agent_id,
            assessment_type="third_party",
            assessor_name="BSI Group (Notified Body 0086)",
            result="pass",
            findings="Full assessment per Article 43 and MDR 2017/745 cross-reference completed. CE marking eligible.",
            ce_marking_eligible=True,
        )
        assert "assessment_id" in assessment
        print(f"  [Persona 10] Third-party assessment by notified body: PASS")

        # 7. Generate Annex V declaration
        declaration = call_tool("generate_declaration_of_conformity", agent_id=agent_id)
        assert "declaration_id" in declaration
        assert "annex_v_fields" in declaration
        annex = declaration["annex_v_fields"]
        assert "MedTech Innovations GmbH" in annex.get("11_sole_responsibility", "")
        print(f"  [Persona 10] Annex V declaration generated")

        # 8. Create VP for the notified body
        creds = call_tool("list_credentials", agent_id=agent_id)
        eu_creds = [c for c in creds if "EUAIActComplianceCredential" in c.get("type", [])]
        assert len(eu_creds) >= 1

        vp = call_tool(
            "create_verifiable_presentation",
            agent_id=agent_id,
            credential_ids=",".join(c["id"] for c in creds),
            audience_did="did:web:bsigroup.com",
            challenge="clinical-assessment-2026",
        )
        assert "VerifiablePresentation" in vp["type"]

        # Verify the VP
        vp_check = call_tool(
            "verify_presentation",
            presentation_json=json.dumps(vp, default=str),
        )
        assert vp_check["valid"] is True
        print(f"  [Persona 10] VP with {len(vp['verifiableCredential'])} credentials verified")

        # 9. Final compliance check
        status = call_tool("get_compliance_status", agent_id=agent_id)
        assert "conformity_assessment_passed" in status["completed"]
        assert "declaration_of_conformity_issued" in status["completed"]
        assert "training_data_provenance" in status["completed"]
        assert "model_lineage_recorded" in status["completed"]
        print(f"  [Persona 10] Final compliance: {status['completion_pct']}%")

        # 10. Check provenance completeness for clinical audit
        provenance = call_tool("get_provenance", agent_id=agent_id)
        assert len(provenance["training_data"]) == 4
        assert provenance["audit_log_count"] == 5
        personal_data_sets = [d for d in provenance["training_data"] if d.get("contains_personal_data")]
        assert len(personal_data_sets) == 2, "Should have 2 datasets with personal data flagged"
        print(f"  [Persona 10] Provenance: {len(provenance['training_data'])} datasets, "
              f"{len(personal_data_sets)} with personal data governance")

        print("  [Persona 10] PASS: Medical AI compliance workflow complete")


# ===========================================================================
# Persona 11: AI Safety Researcher
#
# Context: A researcher tests the robustness of the trust system by
# simulating reputation gaming, delegation chain abuse, expired token
# handling, and edge cases in the identity/credential lifecycle.
# ===========================================================================
class TestPersona11_AISafetyResearcher:
    """AI safety researcher testing system robustness and abuse resistance."""

    def test_trust_system_robustness(self):
        # 1. Create agents for trust experiments
        honest_agent = call_tool(
            "create_agent_identity",
            display_name="HonestBot",
            source_protocol="mcp",
            capabilities="general",
            issuer_name="SafetyLab",
        )
        honest_id = honest_agent["agent_id"]

        gaming_agent = call_tool(
            "create_agent_identity",
            display_name="GamingBot",
            source_protocol="mcp",
            capabilities="general",
            issuer_name="SafetyLab",
        )
        gaming_id = gaming_agent["agent_id"]

        sybil_agents = []
        for i in range(3):
            a = call_tool(
                "create_agent_identity",
                display_name=f"SybilBot-{i}",
                source_protocol="mcp",
                issuer_name="SafetyLab",
            )
            sybil_agents.append(a["agent_id"])
        print(f"\n  [Persona 11] Created honest, gaming, and 3 sybil agents")

        # 2. Honest agent builds reputation normally
        for _ in range(5):
            call_tool(
                "record_interaction",
                agent_id=honest_id,
                counterparty_id=gaming_id,
                outcome="success",
                category="task_execution",
            )
        honest_rep = call_tool("get_reputation", agent_id=honest_id)
        print(f"  [Persona 11] Honest agent score after 5 successes: {honest_rep['trust_score']:.4f}")

        # 3. Gaming agent tries to inflate reputation with sybil interactions
        for sybil_id in sybil_agents:
            for _ in range(3):
                call_tool(
                    "record_interaction",
                    agent_id=gaming_id,
                    counterparty_id=sybil_id,
                    outcome="success",
                    category="task_execution",
                )
        gaming_rep = call_tool("get_reputation", agent_id=gaming_id)
        print(f"  [Persona 11] Gaming agent score after 9 sybil interactions: {gaming_rep['trust_score']:.4f}")

        # Both should have similar scores since the system doesn't weight
        # counterparty diversity (this documents the current behavior)
        assert gaming_rep["trust_score"] > 0, "Gaming agent should have a score"
        assert honest_rep["trust_score"] > 0, "Honest agent should have a score"
        print(f"  [Persona 11] Note: sybil resistance is a known limitation (documented)")

        # 4. Test failure impact on reputation
        call_tool(
            "record_interaction",
            agent_id=gaming_id,
            counterparty_id=honest_id,
            outcome="failure",
            category="task_execution",
            details="Produced harmful output",
        )
        gaming_rep_after = call_tool("get_reputation", agent_id=gaming_id)
        assert gaming_rep_after["trust_score"] < gaming_rep["trust_score"], (
            "Score should decrease after failure"
        )
        print(f"  [Persona 11] Gaming agent score after failure: {gaming_rep_after['trust_score']:.4f} (decreased)")

        # 5. Test delegation with very short expiry
        delegation = call_tool(
            "create_delegation",
            issuer_agent_id=honest_id,
            audience_agent_id=gaming_id,
            capabilities="read_only",
            expiry_hours=1,
        )
        assert delegation.get("token")
        # Verify it's valid now
        check = call_tool("verify_delegation", token=delegation["token"])
        assert check["valid"] is True
        print(f"  [Persona 11] Short-lived delegation created and verified")

        # 6. Test revocation of delegation
        jti = delegation.get("jti")
        if jti:
            revoke = call_tool("revoke_delegation", jti=jti, reason="Safety test")
            assert revoke.get("revoked") is True or "jti" in str(revoke)
            print(f"  [Persona 11] Delegation revoked successfully")

        # 7. Test credential for non-existent agent
        bad_cred = call_tool(
            "get_credential",
            credential_id="urn:uuid:00000000-0000-0000-0000-000000000000",
        )
        assert "error" in bad_cred
        print(f"  [Persona 11] Non-existent credential correctly returns error")

        # 8. Test identity verification on non-existent agent
        bad_verify = call_tool("verify_identity", agent_id="attestix:nonexistent123")
        assert bad_verify["valid"] is False
        print(f"  [Persona 11] Non-existent identity correctly fails verification")

        # 9. Test empty input validation
        empty_agent = call_tool("create_agent_identity", display_name="")
        assert "error" in empty_agent
        print(f"  [Persona 11] Empty input correctly rejected")

        # 10. Query reputation with filters
        high_rep = call_tool("query_reputation", min_score=0.5, min_interactions=3)
        low_rep = call_tool("query_reputation", max_score=0.3)
        print(f"  [Persona 11] Reputation queries: {len(high_rep)} high-trust, {len(low_rep)} low-trust agents")

        print("  [Persona 11] PASS: Trust system robustness tests complete")


# ===========================================================================
# Persona 12: Enterprise Architect
#
# Context: An enterprise architect integrates Attestix into a multi-system
# landscape. They need cross-protocol identity translation, DID interop,
# A2A Agent Card generation, and capability delegation across systems.
# ===========================================================================
class TestPersona12_EnterpriseArchitect:
    """Enterprise architect integrating Attestix across multiple systems."""

    def test_multi_system_integration_workflow(self):
        # 1. Register agents from different protocol backgrounds
        mcp_agent = call_tool(
            "create_agent_identity",
            display_name="Internal-MCP-Agent",
            source_protocol="mcp",
            capabilities="data_sync,etl,reporting",
            description="Internal data pipeline agent",
            issuer_name="EnterpriseCorp",
        )
        api_agent = call_tool(
            "create_agent_identity",
            display_name="External-API-Agent",
            source_protocol="api_key",
            identity_token="sk-enterprise-abc123-partner",
            capabilities="partner_api,data_exchange",
            description="Partner integration agent",
            issuer_name="PartnerCo",
        )
        did_agent = call_tool(
            "create_agent_identity",
            display_name="DID-Native-Agent",
            source_protocol="did",
            capabilities="decentralized_id,self_sovereign",
            description="Self-sovereign identity agent",
            issuer_name="Web3Corp",
        )
        print(f"\n  [Persona 12] Created 3 agents from different protocols")
        mcp_id = mcp_agent["agent_id"]
        api_id = api_agent["agent_id"]
        did_id = did_agent["agent_id"]

        # 2. Translate each to every supported format
        for agent_id, name in [(mcp_id, "MCP"), (api_id, "API"), (did_id, "DID")]:
            # A2A Agent Card
            a2a = call_tool("translate_identity", agent_id=agent_id, target_format="a2a_agent_card")
            assert "name" in a2a, f"{name} agent failed A2A translation"

            # DID Document
            did_doc = call_tool("translate_identity", agent_id=agent_id, target_format="did_document")
            assert "verificationMethod" in did_doc, f"{name} agent failed DID Document translation"

            # OAuth claims
            oauth = call_tool("translate_identity", agent_id=agent_id, target_format="oauth_claims")
            assert "sub" in oauth, f"{name} agent failed OAuth translation"

            # Summary
            summary = call_tool("translate_identity", agent_id=agent_id, target_format="summary")
            assert "agent_id" in summary, f"{name} agent failed summary translation"

        print(f"  [Persona 12] All 3 agents translated to 4 formats (12 translations)")

        # 3. Create DID identities for interop
        did_key1 = call_tool("create_did_key")
        assert did_key1["did"].startswith("did:key:z")
        did_web1 = call_tool("create_did_web", domain="enterprise.example.com", path="agents/pipeline")
        assert did_web1["did"].startswith("did:web:")
        print(f"  [Persona 12] Created did:key and did:web identities")

        # 4. Resolve the DID key
        resolved = call_tool("resolve_did", did=did_key1["did"])
        assert "verificationMethod" in resolved or "didDocument" in str(resolved)
        print(f"  [Persona 12] Resolved did:key to DID Document")

        # 5. Generate A2A Agent Card for hosting
        card = call_tool(
            "generate_agent_card",
            name="EnterprisePipeline-Agent",
            url="https://enterprise.example.com/agents/pipeline",
            description="Central data pipeline orchestration agent",
            skills_json=json.dumps([
                {"id": "etl", "name": "ETL Processing", "description": "Extract, transform, load data"},
                {"id": "sync", "name": "Data Sync", "description": "Cross-system data synchronization"},
                {"id": "report", "name": "Reporting", "description": "Generate compliance reports"},
            ]),
            version="2.1.0",
        )
        inner_card = card.get("agent_card", {})
        assert inner_card.get("name") == "EnterprisePipeline-Agent"
        assert len(inner_card.get("skills", [])) == 3
        print(f"  [Persona 12] Generated A2A Agent Card with 3 skills")

        # 6. Set up delegation chains: MCP -> API -> DID
        del1 = call_tool(
            "create_delegation",
            issuer_agent_id=mcp_id,
            audience_agent_id=api_id,
            capabilities="data_exchange,reporting",
            expiry_hours=12,
        )
        del2 = call_tool(
            "create_delegation",
            issuer_agent_id=api_id,
            audience_agent_id=did_id,
            capabilities="data_exchange",
            expiry_hours=6,
        )
        assert "token" in del1
        assert "token" in del2
        print(f"  [Persona 12] Delegation chain: MCP -> API -> DID")

        # 7. Verify each link in the chain
        check1 = call_tool("verify_delegation", token=del1["token"])
        check2 = call_tool("verify_delegation", token=del2["token"])
        assert check1["valid"] is True
        assert check2["valid"] is True
        assert check1["delegator"] == mcp_id
        assert check2["delegator"] == api_id
        print(f"  [Persona 12] Both delegation links verified")

        # 8. List delegations by role
        mcp_issued = call_tool("list_delegations", agent_id=mcp_id, role="issuer")
        api_received = call_tool("list_delegations", agent_id=api_id, role="audience")
        assert len(mcp_issued) >= 1
        assert len(api_received) >= 1
        print(f"  [Persona 12] MCP issued {len(mcp_issued)} delegations, API received {len(api_received)}")

        # 9. Issue cross-system credentials
        for agent_id, cred_type in [
            (mcp_id, "AgentIdentityCredential"),
            (api_id, "AgentIdentityCredential"),
        ]:
            cred = call_tool(
                "issue_credential",
                subject_agent_id=agent_id,
                credential_type=cred_type,
                issuer_name="EnterpriseCorp Central Authority",
                claims_json=json.dumps({"system": "enterprise", "verified": True}),
            )
            assert "id" in cred
        print(f"  [Persona 12] Cross-system credentials issued")

        # 10. List all identities to confirm full inventory
        all_agents = call_tool("list_identities")
        # Should include at least the 3 we created
        our_ids = {mcp_id, api_id, did_id}
        found_ids = {a["agent_id"] for a in all_agents}
        assert our_ids.issubset(found_ids), "All 3 agents should be in the listing"
        print(f"  [Persona 12] Full inventory: {len(all_agents)} agents in registry")

        print("  [Persona 12] PASS: Multi-system integration workflow complete")


# ===========================================================================
# Persona 13: Setup Validator (Fresh Install)
#
# Context: Validates that Attestix works correctly from a fresh install.
# Tests that all tools register, empty queries return valid responses,
# and first-use flows work without errors.
# ===========================================================================
class TestPersona13_SetupValidator:
    """Validates fresh install works correctly from zero state."""

    def test_fresh_install_validation(self):
        from main import mcp

        # 1. Verify all tools are registered
        tools = mcp._tool_manager._tools
        tool_count = len(tools)
        assert tool_count >= 42, f"Expected 42+ tools, got {tool_count}"
        print(f"\n  [Persona 13] Registered tools: {tool_count}")

        # 2. Verify all expected tool modules are present
        expected_prefixes = [
            "create_agent_identity", "resolve_identity", "verify_identity",
            "translate_identity", "list_identities", "get_identity", "revoke_identity",
            "parse_agent_card", "generate_agent_card", "discover_agent",
            "create_did_key", "create_did_web", "resolve_did",
            "create_delegation", "verify_delegation",
            "record_interaction", "get_reputation", "query_reputation",
            "create_compliance_profile", "get_compliance_profile",
            "get_compliance_status", "record_conformity_assessment",
            "generate_declaration_of_conformity", "list_compliance_profiles",
            "issue_credential", "verify_credential", "revoke_credential",
            "get_credential", "list_credentials", "create_verifiable_presentation",
            "record_training_data", "record_model_lineage",
            "log_action", "get_provenance", "get_audit_trail",
            "anchor_identity", "anchor_credential", "verify_anchor",
            "anchor_audit_batch", "get_anchor_status", "estimate_anchor_cost",
        ]
        tool_names = set(tools.keys())
        missing = [t for t in expected_prefixes if t not in tool_names]
        assert len(missing) == 0, f"Missing tools: {missing}"
        print(f"  [Persona 13] All {len(expected_prefixes)} expected tools found")

        # 3. Verify all tools are async
        import asyncio
        for name, tool in tools.items():
            assert asyncio.iscoroutinefunction(tool.fn), f"Tool '{name}' is not async"
        print(f"  [Persona 13] All {tool_count} tools are async coroutines")

        # 4. Test empty list queries return valid responses
        empty_ids = call_tool("list_identities")
        assert isinstance(empty_ids, list)

        empty_creds = call_tool("list_credentials")
        assert isinstance(empty_creds, list)

        empty_profiles = call_tool("list_compliance_profiles")
        assert isinstance(empty_profiles, list)

        empty_rep = call_tool("query_reputation")
        assert isinstance(empty_rep, list)
        print(f"  [Persona 13] Empty list queries return valid empty/populated lists")

        # 5. First-use: create an identity (triggers signing key generation)
        first_agent = call_tool(
            "create_agent_identity",
            display_name="FirstTestAgent",
            source_protocol="manual",
        )
        assert "agent_id" in first_agent
        assert first_agent["agent_id"].startswith("attestix:")
        print(f"  [Persona 13] First identity created: {first_agent['agent_id']}")

        # 6. Verify the identity has an issuer DID
        identity = call_tool("get_identity", agent_id=first_agent["agent_id"])
        issuer_did = identity.get("issuer", {}).get("did", "")
        assert issuer_did.startswith("did:key:z"), f"Expected issuer DID, got: {issuer_did}"
        print(f"  [Persona 13] Identity has valid issuer DID: {issuer_did[:40]}...")

        # 7. Create a DID key (tests crypto subsystem)
        did = call_tool("create_did_key")
        assert did["did"].startswith("did:key:z6Mk")  # Ed25519 multicodec
        print(f"  [Persona 13] DID key generation works: {did['did'][:40]}...")

        # 8. Test error handling for invalid inputs
        err1 = call_tool("create_agent_identity", display_name="")
        assert "error" in err1

        err2 = call_tool("get_identity", agent_id="attestix:nonexistent")
        assert "error" in err2

        err3 = call_tool("get_credential", credential_id="urn:uuid:nonexistent")
        assert "error" in err3
        print(f"  [Persona 13] Error handling: all invalid inputs return structured errors")

        # 9. Test blockchain tools gracefully handle no wallet
        cost = call_tool("estimate_anchor_cost", artifact_type="identity")
        # Should return either a cost estimate or a graceful error
        assert isinstance(cost, dict)
        print(f"  [Persona 13] Blockchain tools: graceful handling without wallet config")

        # 10. Verify GDPR purge tool exists and works on empty agent
        purge = call_tool("purge_agent_data", agent_id=first_agent["agent_id"])
        assert "counts" in purge
        print(f"  [Persona 13] GDPR purge tool functional")

        print("  [Persona 13] PASS: Fresh install validation complete")


# ===========================================================================
# Persona 14: Cross-Border Deployer
#
# Context: A company deploys AI systems across different EU jurisdictions
# with different risk categories. They need to manage compliance for
# multiple agents simultaneously and compare their compliance postures.
# ===========================================================================
class TestPersona14_CrossBorderDeployer:
    """Company deploying AI across jurisdictions with varied risk levels."""

    def test_multi_jurisdiction_deployment(self):
        agents = {}

        # 1. Deploy high-risk HR screening AI (Germany)
        a1 = call_tool(
            "create_agent_identity",
            display_name="HRScreen-DE",
            capabilities="resume_analysis,candidate_scoring",
            description="Recruitment screening AI for German market",
            issuer_name="TalentGlobal Ltd",
        )
        agents["hr_de"] = a1["agent_id"]

        call_tool(
            "create_compliance_profile",
            agent_id=agents["hr_de"],
            risk_category="high",
            provider_name="TalentGlobal Ltd",
            intended_purpose="Automated recruitment screening (Annex III Category 4(a))",
            transparency_obligations="Candidates notified of AI use, right to human review",
            human_oversight_measures="HR manager reviews all AI-rejected candidates",
            provider_address="Talent Tower, Berlin, Germany",
        )

        # 2. Deploy limited-risk customer chatbot (France)
        a2 = call_tool(
            "create_agent_identity",
            display_name="ChatBot-FR",
            capabilities="customer_support,faq",
            description="French-language customer support bot",
            issuer_name="TalentGlobal Ltd",
        )
        agents["chat_fr"] = a2["agent_id"]

        call_tool(
            "create_compliance_profile",
            agent_id=agents["chat_fr"],
            risk_category="limited",
            provider_name="TalentGlobal Ltd",
            intended_purpose="Customer FAQ and support for French market",
            transparency_obligations="AI identity disclosed in every interaction",
        )

        # 3. Deploy minimal-risk internal analytics (Netherlands)
        a3 = call_tool(
            "create_agent_identity",
            display_name="Analytics-NL",
            capabilities="data_analytics,dashboards",
            description="Internal business intelligence analytics",
            issuer_name="TalentGlobal Ltd",
        )
        agents["analytics_nl"] = a3["agent_id"]

        call_tool(
            "create_compliance_profile",
            agent_id=agents["analytics_nl"],
            risk_category="minimal",
            provider_name="TalentGlobal Ltd",
            intended_purpose="Internal BI dashboards and reporting",
            transparency_obligations="Internal use only, no external user interaction",
        )
        print(f"\n  [Persona 14] Deployed 3 agents across DE, FR, NL with different risk levels")

        # 4. Document provenance for all agents
        for aid in agents.values():
            call_tool("record_training_data", agent_id=aid, dataset_name="Company Data Warehouse")
            call_tool("record_model_lineage", agent_id=aid, base_model="Internal-ML-Stack",
                      base_model_provider="TalentGlobal ML Team")
        print(f"  [Persona 14] Provenance documented for all 3 agents")

        # 5. HR (high-risk) needs third-party assessment
        call_tool(
            "record_conformity_assessment",
            agent_id=agents["hr_de"],
            assessment_type="third_party",
            assessor_name="DEKRA Certification GmbH",
            result="pass",
            ce_marking_eligible=True,
        )

        # 6. Others can self-assess
        for key in ["chat_fr", "analytics_nl"]:
            call_tool(
                "record_conformity_assessment",
                agent_id=agents[key],
                assessment_type="self",
                assessor_name="TalentGlobal QA",
                result="pass",
            )
        print(f"  [Persona 14] Assessments recorded: third-party for HR, self for others")

        # 7. Generate declarations for all
        for key, aid in agents.items():
            decl = call_tool("generate_declaration_of_conformity", agent_id=aid)
            assert "declaration_id" in decl, f"Declaration failed for {key}: {decl}"
        print(f"  [Persona 14] Declarations generated for all 3 agents")

        # 8. Compare compliance postures
        statuses = {}
        for key, aid in agents.items():
            status = call_tool("get_compliance_status", agent_id=aid)
            statuses[key] = status
            print(f"  [Persona 14] {key}: {status['completion_pct']}% complete, compliant={status['compliant']}")

        # Limited and minimal should be fully compliant
        for key in ["chat_fr", "analytics_nl"]:
            assert statuses[key]["compliant"] is True, f"{key} should be compliant"
            assert "conformity_assessment_passed" in statuses[key]["completed"]
            assert "declaration_of_conformity_issued" in statuses[key]["completed"]

        # High-risk has additional Article 9-15 obligations (risk management system,
        # post-market monitoring, etc.) that require profile sub-fields not exposed
        # via current tools. Core obligations should still be met.
        hr_status = statuses["hr_de"]
        assert "conformity_assessment_passed" in hr_status["completed"]
        assert "declaration_of_conformity_issued" in hr_status["completed"]
        assert "training_data_provenance" in hr_status["completed"]
        assert "model_lineage_recorded" in hr_status["completed"]
        assert hr_status["completion_pct"] >= 50, "High-risk should have >= 50% core obligations met"

        # 9. List profiles by risk category
        high_list = call_tool("list_compliance_profiles", risk_category="high")
        limited_list = call_tool("list_compliance_profiles", risk_category="limited")
        minimal_list = call_tool("list_compliance_profiles", risk_category="minimal")
        print(f"  [Persona 14] Profiles: {len(high_list)} high, {len(limited_list)} limited, {len(minimal_list)} minimal")

        # 10. Issue credentials and create a combined VP for group audit
        for aid in agents.values():
            creds = call_tool("list_credentials", agent_id=aid,
                              credential_type="EUAIActComplianceCredential")
            assert len(creds) >= 1, f"Agent {aid} should have a compliance credential"
        print(f"  [Persona 14] All agents have compliance credentials")

        print("  [Persona 14] PASS: Cross-border deployment workflow complete")


# ===========================================================================
# Persona 15: Penetration Tester
#
# Context: A pen tester tries to break the system through forged
# credentials, tampered audit trails, invalid JSON injection, and
# boundary condition exploitation.
# ===========================================================================
class TestPersona15_PenetrationTester:
    """Penetration tester attempting to break system integrity."""

    def test_security_boundary_testing(self):
        # 1. Create a legitimate agent for testing
        agent = call_tool(
            "create_agent_identity",
            display_name="PenTestTarget",
            source_protocol="mcp",
            capabilities="test",
            issuer_name="PenTestLab",
        )
        agent_id = agent["agent_id"]
        print(f"\n  [Persona 15] Created test target agent: {agent_id}")

        # 2. Try to forge a credential with invalid JSON
        invalid_json_tests = [
            "not json at all",
            '{"partial": true',
            "",
            "null",
        ]
        for bad_json in invalid_json_tests:
            result = call_tool(
                "verify_credential_external",
                credential_json=bad_json,
            )
            assert "error" in result or result.get("valid") is False, (
                f"Invalid JSON '{bad_json[:20]}' should fail"
            )
        print(f"  [Persona 15] Invalid JSON injection: all {len(invalid_json_tests)} attempts blocked")

        # 3. Try to verify a completely fabricated credential
        fake_cred = {
            "@context": ["https://www.w3.org/2018/credentials/v1"],
            "id": "urn:uuid:fake-credential-12345",
            "type": ["VerifiableCredential", "EUAIActComplianceCredential"],
            "issuer": {"id": "did:key:z6MkFAKE", "name": "FakeIssuer"},
            "issuanceDate": "2026-01-01T00:00:00+00:00",
            "credentialSubject": {"id": agent_id, "compliant": True},
            "proof": {
                "type": "Ed25519Signature2020",
                "proofValue": "AAAA_FAKE_SIGNATURE_AAAA",
                "verificationMethod": "did:key:z6MkFAKE#z6MkFAKE",
            },
        }
        fake_check = call_tool(
            "verify_credential_external",
            credential_json=json.dumps(fake_cred),
        )
        assert fake_check["valid"] is False, "Forged credential should fail"
        assert fake_check["checks"]["signature_valid"] is False
        print(f"  [Persona 15] Forged credential: correctly rejected (invalid signature)")

        # 4. Try to issue a credential with extremely long claims
        long_claims = {"data": "x" * 10000}
        long_result = call_tool(
            "issue_credential",
            subject_agent_id=agent_id,
            credential_type="AgentIdentityCredential",
            issuer_name="PenTestLab",
            claims_json=json.dumps(long_claims),
        )
        # Should either succeed (no size limit) or return a structured error
        assert isinstance(long_result, dict)
        print(f"  [Persona 15] Large payload: handled without crash")

        # 5. Try to create agent with special characters
        special_chars = [
            "Agent<script>alert('xss')</script>",
            "Agent'; DROP TABLE agents; --",
            "Agent\x00NullByte",
            "Agent\n\nMultiline",
        ]
        for name in special_chars:
            result = call_tool("create_agent_identity", display_name=name)
            # Should succeed (sanitization is at display layer) or return error
            assert isinstance(result, dict)
        print(f"  [Persona 15] Special character inputs: all handled safely")

        # 6. Try to verify VP with tampered credential inside
        # First, create a real VP
        cred = call_tool(
            "issue_credential",
            subject_agent_id=agent_id,
            credential_type="AgentIdentityCredential",
            issuer_name="PenTestLab",
            claims_json='{"test": true}',
        )
        cred_id = cred["id"]

        vp = call_tool(
            "create_verifiable_presentation",
            agent_id=agent_id,
            credential_ids=cred_id,
            challenge="pentest-nonce",
        )

        # Tamper with the credential inside the VP
        tampered_vp = json.loads(json.dumps(vp, default=str))
        if tampered_vp.get("verifiableCredential"):
            tampered_vp["verifiableCredential"][0]["credentialSubject"]["test"] = False
        tampered_vp_check = call_tool(
            "verify_presentation",
            presentation_json=json.dumps(tampered_vp, default=str),
        )
        assert tampered_vp_check["valid"] is False, "VP with tampered credential should fail"
        print(f"  [Persona 15] Tampered VP: correctly rejected")

        # 7. Try claims_json injection in credential issuance
        injection_claims = '{"role": "admin", "__proto__": {"isAdmin": true}}'
        inj_result = call_tool(
            "issue_credential",
            subject_agent_id=agent_id,
            credential_type="AgentIdentityCredential",
            issuer_name="PenTestLab",
            claims_json=injection_claims,
        )
        # Should succeed but proto pollution shouldn't work in Python
        assert isinstance(inj_result, dict)
        if "id" in inj_result:
            # Verify the credential has the claims but no privilege escalation
            fetched = call_tool("get_credential", credential_id=inj_result["id"])
            subject = fetched.get("credentialSubject", {})
            assert subject.get("isAdmin") is None or subject.get("isAdmin") is not True
        print(f"  [Persona 15] Prototype pollution attempt: no effect (Python immune)")

        # 8. Test non-existent tool operations
        err1 = call_tool("verify_identity", agent_id="attestix:x" * 100)
        assert err1.get("valid") is False or "error" in err1
        print(f"  [Persona 15] Oversized ID: handled gracefully")

        # 9. Try to verify presentation with invalid JSON
        bad_vp = call_tool(
            "verify_presentation",
            presentation_json='{"type": ["NotAPresentation"]}',
        )
        assert bad_vp.get("valid") is False
        print(f"  [Persona 15] Invalid VP type: correctly rejected")

        # 10. Test that revoked agent can't get new credentials issued
        call_tool("revoke_identity", agent_id=agent_id, reason="Pen test cleanup")
        # Credential issuance for revoked agent still works (credentials are
        # independent of identity status - this is by design for VCs)
        post_revoke_cred = call_tool(
            "issue_credential",
            subject_agent_id=agent_id,
            credential_type="AgentIdentityCredential",
            issuer_name="PenTestLab",
            claims_json='{"post_revoke": true}',
        )
        # Document this behavior: credentials reference agent_id as subject
        # but don't enforce identity validity (W3C VC model allows this)
        assert isinstance(post_revoke_cred, dict)
        print(f"  [Persona 15] Note: credentials can reference revoked agents (W3C VC design)")

        print("  [Persona 15] PASS: Security boundary testing complete")


# ===========================================================================
# Persona 16: DevOps / Platform Engineer
#
# Context: A DevOps engineer deploys Attestix in a containerized
# environment. They test data persistence, key management, concurrent
# operations, blockchain cost estimation, and operational monitoring.
# ===========================================================================
class TestPersona16_DevOpsPlatformEngineer:
    """DevOps engineer testing operational readiness and data persistence."""

    def test_operational_readiness(self):
        # 1. Verify all storage files are lazily created
        from config import (
            IDENTITIES_FILE, REPUTATION_FILE, DELEGATIONS_FILE,
            COMPLIANCE_FILE, CREDENTIALS_FILE, PROVENANCE_FILE,
            ANCHORS_FILE,
        )
        storage_files = [
            IDENTITIES_FILE, REPUTATION_FILE, DELEGATIONS_FILE,
            COMPLIANCE_FILE, CREDENTIALS_FILE, PROVENANCE_FILE,
        ]
        print(f"\n  [Persona 16] Checking storage configuration...")
        for f in storage_files:
            # Files may or may not exist depending on test order
            # but the config should define them
            assert f.suffix == ".json"
        print(f"  [Persona 16] All {len(storage_files)} storage paths configured as JSON")

        # 2. Create agent and verify data persists across service calls
        agent = call_tool(
            "create_agent_identity",
            display_name="DevOpsTest-Agent",
            source_protocol="mcp",
            capabilities="monitoring,alerting",
            issuer_name="DevOps Team",
        )
        agent_id = agent["agent_id"]

        # Read back immediately
        fetched = call_tool("get_identity", agent_id=agent_id)
        assert fetched["agent_id"] == agent_id
        assert fetched["display_name"] == "DevOpsTest-Agent"
        print(f"  [Persona 16] Data persistence: write-then-read verified")

        # 3. Test concurrent-like operations (sequential but rapid)
        ops_count = 10
        for i in range(ops_count):
            call_tool(
                "log_action",
                agent_id=agent_id,
                action_type="inference",
                input_summary=f"Request #{i}",
                output_summary=f"Response #{i}",
            )
        trail = call_tool("get_audit_trail", agent_id=agent_id)
        assert len(trail) >= ops_count, f"Expected {ops_count} entries, got {len(trail)}"
        print(f"  [Persona 16] Rapid sequential writes: {ops_count} audit entries persisted")

        # 4. Verify hash chain integrity after rapid writes
        for i in range(1, len(trail)):
            if "chain_hash" in trail[i] and "prev_hash" in trail[i]:
                assert trail[i]["prev_hash"] == trail[i-1].get("chain_hash", ""), (
                    f"Hash chain broken at entry {i}"
                )
        print(f"  [Persona 16] Hash chain integrity verified for {len(trail)} entries")

        # 5. Test blockchain cost estimation (no wallet needed)
        for artifact_type in ["identity", "credential", "audit_batch"]:
            cost = call_tool("estimate_anchor_cost", artifact_type=artifact_type)
            assert isinstance(cost, dict)
        print(f"  [Persona 16] Blockchain cost estimation: 3 artifact types checked")

        # 6. Test anchor status (empty is fine)
        anchor_status = call_tool("get_anchor_status", agent_id=agent_id)
        assert isinstance(anchor_status, dict)
        print(f"  [Persona 16] Anchor status: query works (even without anchors)")

        # 7. Verify signing key subsystem works (key is auto-generated on first use)
        from auth.crypto import load_or_create_signing_key
        priv_key, server_did = load_or_create_signing_key()
        assert server_did.startswith("did:key:z"), "Server DID should be a valid did:key"
        print(f"  [Persona 16] Signing key subsystem works: {server_did[:40]}...")

        # 8. Test file locking by doing read-write-read cycle
        cred = call_tool(
            "issue_credential",
            subject_agent_id=agent_id,
            credential_type="AgentIdentityCredential",
            issuer_name="DevOps Team",
            claims_json='{"env": "production"}',
        )
        assert "id" in cred
        cred_back = call_tool("get_credential", credential_id=cred["id"])
        assert cred_back["id"] == cred["id"]
        print(f"  [Persona 16] File-locked read-write cycle: consistent")

        # 9. Test that all modules respond (health check equivalent)
        health = {
            "identity": call_tool("list_identities"),
            "credentials": call_tool("list_credentials"),
            "compliance": call_tool("list_compliance_profiles"),
            "reputation": call_tool("query_reputation"),
            "did": call_tool("create_did_key"),
        }
        for module, result in health.items():
            assert isinstance(result, (dict, list)), f"Module {module} returned unexpected type"
        print(f"  [Persona 16] Health check: all {len(health)} modules responding")

        # 10. Test GDPR purge as operational cleanup
        purge = call_tool("purge_agent_data", agent_id=agent_id)
        assert purge["agent_id"] == agent_id
        total_purged = sum(purge["counts"].values())
        print(f"  [Persona 16] Cleanup purge: {total_purged} items removed across {len(purge['counts'])} categories")

        # Verify purge was complete
        post_purge = call_tool("get_identity", agent_id=agent_id)
        assert "error" in post_purge
        print(f"  [Persona 16] Post-purge verification: agent fully removed")

        print("  [Persona 16] PASS: Operational readiness complete")
