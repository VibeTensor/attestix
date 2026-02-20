"""End-to-end user persona tests for Attestix.

Simulates 5 real-world personas using Attestix from scratch,
exercising the full stack as a user would via the MCP tool layer.

Each persona test is independent and creates its own agents,
credentials, compliance profiles, etc.
"""

import json
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
# Persona 1: Startup AI Developer
#
# Context: A solo developer shipping an AI chatbot. They want to register
# the agent, get a DID, issue an identity credential, translate to an
# A2A card, and verify everything works before going live.
# ===========================================================================
class TestPersona1_StartupDeveloper:
    """Solo dev building an AI chatbot for customer support."""

    def test_full_developer_workflow(self):
        # 1. Register the chatbot
        agent = call_tool(
            "create_agent_identity",
            display_name="SupportBot-v1",
            source_protocol="mcp",
            capabilities="chat,knowledge_base,ticket_creation",
            description="Customer support chatbot for SaaS product",
            issuer_name="IndieAI Labs",
        )
        assert "agent_id" in agent, f"Failed to create agent: {agent}"
        agent_id = agent["agent_id"]
        print(f"\n  [Persona 1] Created agent: {agent_id}")

        # 2. Create a DID for the agent
        did = call_tool("create_did_key")
        assert did["did"].startswith("did:key:z")
        print(f"  [Persona 1] Created DID: {did['did'][:40]}...")

        # 3. Verify the identity is valid
        verification = call_tool("verify_identity", agent_id=agent_id)
        assert verification["valid"] is True
        assert verification["checks"]["signature_valid"] is True
        print(f"  [Persona 1] Identity verified: all checks passed")

        # 4. Issue an identity credential
        cred = call_tool(
            "issue_credential",
            subject_agent_id=agent_id,
            credential_type="AgentIdentityCredential",
            issuer_name="IndieAI Labs",
            claims_json=json.dumps({
                "role": "customer_support",
                "version": "1.0",
                "deployment": "production",
            }),
        )
        assert "id" in cred, f"Failed to issue credential: {cred}"
        cred_id = cred["id"]
        print(f"  [Persona 1] Issued credential: {cred_id}")

        # 5. Verify the credential
        cred_check = call_tool("verify_credential", credential_id=cred_id)
        assert cred_check["valid"] is True
        print(f"  [Persona 1] Credential verified: signature valid")

        # 6. Translate to A2A Agent Card for interop
        a2a = call_tool(
            "translate_identity",
            agent_id=agent_id,
            target_format="a2a_agent_card",
        )
        assert a2a["name"] == "SupportBot-v1"
        assert len(a2a["skills"]) == 3
        print(f"  [Persona 1] A2A card generated with {len(a2a['skills'])} skills")

        # 7. Translate to DID Document
        did_doc = call_tool(
            "translate_identity",
            agent_id=agent_id,
            target_format="did_document",
        )
        assert "verificationMethod" in did_doc
        print(f"  [Persona 1] DID Document generated: {did_doc['id'][:40]}...")

        # 8. List all identities to confirm it shows up
        all_agents = call_tool("list_identities")
        ids = [a["agent_id"] for a in all_agents]
        assert agent_id in ids
        print(f"  [Persona 1] Agent visible in listing ({len(all_agents)} total)")

        print("  [Persona 1] PASS: Full developer workflow complete")


# ===========================================================================
# Persona 2: Enterprise Compliance Officer
#
# Context: A compliance officer at a large bank needs to register a
# high-risk loan screening AI, document everything for the EU AI Act,
# get third-party assessment, generate the Annex V declaration, and
# produce a verifiable presentation for the regulator.
# ===========================================================================
class TestPersona2_ComplianceOfficer:
    """Enterprise compliance officer for a high-risk financial AI."""

    def test_full_compliance_workflow(self):
        # 1. Register the AI system
        agent = call_tool(
            "create_agent_identity",
            display_name="LoanScreener-AI",
            source_protocol="api_key",
            capabilities="credit_scoring,risk_assessment,fraud_detection",
            description="Automated loan application screening system",
            issuer_name="MegaBank PLC",
        )
        agent_id = agent["agent_id"]
        print(f"\n  [Persona 2] Registered AI system: {agent_id}")

        # 2. Create high-risk compliance profile
        profile = call_tool(
            "create_compliance_profile",
            agent_id=agent_id,
            risk_category="high",
            provider_name="MegaBank PLC",
            intended_purpose="Automated credit decision support for consumer loan applications",
            transparency_obligations="Full decision explanations provided to applicants per Article 13",
            human_oversight_measures="Senior credit officer reviews all AI recommendations above 50K EUR",
            provider_address="1 Banking Street, Frankfurt, Germany",
            authorised_representative="Dr. Compliance, EU AI Act Officer",
        )
        assert "profile_id" in profile, f"Failed to create profile: {profile}"
        print(f"  [Persona 2] Compliance profile created: {profile['profile_id']}")

        # 3. Record training data provenance (Article 10)
        for ds_name, personal in [
            ("Historical Loan Performance 2018-2025", True),
            ("ECB Economic Indicators", False),
            ("Synthetic Stress Test Scenarios", False),
        ]:
            td = call_tool(
                "record_training_data",
                agent_id=agent_id,
                dataset_name=ds_name,
                license="Proprietary" if personal else "Open Data",
                data_categories="financial,credit" if personal else "economic",
                contains_personal_data=personal,
                data_governance_measures="De-identified per GDPR Art. 5" if personal else "Public data",
            )
            assert "entry_id" in td
        print(f"  [Persona 2] Recorded 3 training datasets")

        # 4. Record model lineage (Article 11)
        lineage = call_tool(
            "record_model_lineage",
            agent_id=agent_id,
            base_model="XGBoost 2.1",
            base_model_provider="Open Source (Apache 2.0)",
            fine_tuning_method="Gradient boosting with Optuna hyperparameter search",
            evaluation_metrics_json=json.dumps({
                "auc_roc": 0.892,
                "precision": 0.87,
                "recall": 0.91,
                "demographic_parity_diff": 0.03,
            }),
        )
        assert "entry_id" in lineage
        print(f"  [Persona 2] Model lineage recorded")

        # 5. Check gap analysis BEFORE assessment
        status_before = call_tool("get_compliance_status", agent_id=agent_id)
        assert status_before["completion_pct"] < 100
        missing_before = status_before["missing"]
        print(f"  [Persona 2] Gap analysis: {status_before['completion_pct']}% complete, {len(missing_before)} gaps")

        # 6. Third-party conformity assessment (required for high-risk)
        assessment = call_tool(
            "record_conformity_assessment",
            agent_id=agent_id,
            assessment_type="third_party",
            assessor_name="TUV Rheinland AG",
            result="pass",
            findings="Full Annex III Category 5(a) assessment completed per Article 43",
            ce_marking_eligible=True,
        )
        assert "assessment_id" in assessment
        print(f"  [Persona 2] Third-party assessment recorded: PASS")

        # 7. Generate Annex V declaration of conformity
        declaration = call_tool(
            "generate_declaration_of_conformity",
            agent_id=agent_id,
        )
        assert "declaration_id" in declaration, f"Declaration failed: {declaration}"
        assert "annex_v_fields" in declaration
        annex = declaration["annex_v_fields"]
        assert annex["11_sole_responsibility"] != ""
        assert "MegaBank PLC" in annex["11_sole_responsibility"]
        print(f"  [Persona 2] Annex V declaration generated: {declaration['declaration_id']}")

        # 8. Verify the auto-issued compliance credential
        creds = call_tool(
            "list_credentials",
            agent_id=agent_id,
            credential_type="EUAIActComplianceCredential",
        )
        assert len(creds) >= 1, "Auto-issued compliance credential not found"
        cred_check = call_tool("verify_credential", credential_id=creds[0]["id"])
        assert cred_check["valid"] is True
        print(f"  [Persona 2] Compliance credential verified")

        # 9. Create verifiable presentation for regulator
        vp = call_tool(
            "create_verifiable_presentation",
            agent_id=agent_id,
            credential_ids=creds[0]["id"],
            audience_did="did:web:ai-office.europa.eu",
            challenge="regulatory-audit-2026-Q1",
        )
        assert "VerifiablePresentation" in vp["type"]
        assert vp["proof"]["challenge"] == "regulatory-audit-2026-Q1"
        print(f"  [Persona 2] Verifiable presentation created for regulator")

        # 10. Final gap analysis
        status_after = call_tool("get_compliance_status", agent_id=agent_id)
        assert "conformity_assessment_passed" in status_after["completed"]
        assert "declaration_of_conformity_issued" in status_after["completed"]
        print(f"  [Persona 2] Final compliance: {status_after['completion_pct']}%")

        print("  [Persona 2] PASS: Full compliance workflow complete")


# ===========================================================================
# Persona 3: Multi-Agent Orchestrator
#
# Context: A platform operator manages multiple AI agents. They need to
# create agents, delegate capabilities between them, track reputation
# across interactions, and revoke a misbehaving agent.
# ===========================================================================
class TestPersona3_MultiAgentOrchestrator:
    """Platform operator managing a fleet of AI agents."""

    def test_full_orchestration_workflow(self):
        # 1. Create orchestrator agent
        orchestrator = call_tool(
            "create_agent_identity",
            display_name="Orchestrator-Prime",
            source_protocol="mcp",
            capabilities="orchestrate,delegate,monitor",
            description="Central orchestration agent",
            issuer_name="PlatformCorp",
        )
        orch_id = orchestrator["agent_id"]
        print(f"\n  [Persona 3] Created orchestrator: {orch_id}")

        # 2. Create 3 worker agents
        workers = []
        for name, caps in [
            ("DataFetcher", "web_search,api_calls"),
            ("Analyzer", "data_analysis,ml_inference"),
            ("Reporter", "report_generation,email"),
        ]:
            w = call_tool(
                "create_agent_identity",
                display_name=name,
                source_protocol="mcp",
                capabilities=caps,
                issuer_name="PlatformCorp",
            )
            workers.append(w)
        worker_ids = [w["agent_id"] for w in workers]
        print(f"  [Persona 3] Created 3 workers: {[w['display_name'] for w in workers]}")

        # 3. Delegate capabilities from orchestrator to workers
        delegations = []
        for worker, caps in zip(workers, ["web_search,api_calls", "data_analysis", "report_generation"]):
            d = call_tool(
                "create_delegation",
                issuer_agent_id=orch_id,
                audience_agent_id=worker["agent_id"],
                capabilities=caps,
                expiry_hours=8,
            )
            assert "token" in d, f"Delegation failed: {d}"
            delegations.append(d)
        print(f"  [Persona 3] Created 3 delegations")

        # 4. Verify each delegation
        for i, d in enumerate(delegations):
            check = call_tool("verify_delegation", token=d["token"])
            assert check["valid"] is True
            assert check["delegator"] == orch_id
        print(f"  [Persona 3] All 3 delegations verified")

        # 5. Simulate interactions and build reputation
        for worker_id in worker_ids:
            for outcome in ["success", "success", "success"]:
                call_tool(
                    "record_interaction",
                    agent_id=worker_id,
                    counterparty_id=orch_id,
                    outcome=outcome,
                    category="task_execution",
                    details="Completed assigned task",
                )

        # One worker has a failure
        call_tool(
            "record_interaction",
            agent_id=worker_ids[2],
            counterparty_id=orch_id,
            outcome="failure",
            category="task_execution",
            details="Reporter agent produced malformed output",
        )
        print(f"  [Persona 3] Recorded 10 interactions (9 success, 1 failure)")

        # 6. Check reputations
        rep_fetcher = call_tool("get_reputation", agent_id=worker_ids[0])
        rep_reporter = call_tool("get_reputation", agent_id=worker_ids[2])
        assert rep_fetcher["trust_score"] > rep_reporter["trust_score"], (
            "DataFetcher (all success) should have higher score than Reporter (1 failure)"
        )
        print(f"  [Persona 3] DataFetcher score: {rep_fetcher['trust_score']:.4f}")
        print(f"  [Persona 3] Reporter score: {rep_reporter['trust_score']:.4f}")

        # 7. Query top-reputation agents
        top = call_tool("query_reputation", min_score=0.9)
        top_ids = [r["agent_id"] for r in top]
        assert worker_ids[0] in top_ids  # DataFetcher should be top
        print(f"  [Persona 3] {len(top)} agents with score >= 0.9")

        # 8. List delegations for orchestrator
        orch_delegations = call_tool(
            "list_delegations",
            agent_id=orch_id,
            role="issuer",
        )
        assert len(orch_delegations) == 3
        print(f"  [Persona 3] Orchestrator has 3 active delegations")

        # 9. Revoke the misbehaving reporter agent
        revoke_result = call_tool(
            "revoke_identity",
            agent_id=worker_ids[2],
            reason="Repeated malformed output, decommissioned",
        )
        assert revoke_result.get("revoked") is True

        # Verify it's now invalid
        check = call_tool("verify_identity", agent_id=worker_ids[2])
        assert check["valid"] is False
        print(f"  [Persona 3] Reporter agent revoked and verified as invalid")

        print("  [Persona 3] PASS: Full orchestration workflow complete")


# ===========================================================================
# Persona 4: Data Protection Officer (DPO)
#
# Context: A DPO receives a GDPR erasure request. They need to create
# an agent, populate it with data across multiple modules, then purge
# all data and verify nothing remains.
# ===========================================================================
class TestPersona4_DataProtectionOfficer:
    """DPO handling a GDPR Article 17 erasure request."""

    def test_gdpr_erasure_workflow(self):
        # 1. Create agent with full data across all modules
        agent = call_tool(
            "create_agent_identity",
            display_name="ErasableBot",
            source_protocol="mcp",
            capabilities="chat,search",
            description="Agent that will be erased",
            issuer_name="PrivacyCorp",
        )
        agent_id = agent["agent_id"]
        print(f"\n  [Persona 4] Created agent to be erased: {agent_id}")

        # 2. Add compliance profile
        call_tool(
            "create_compliance_profile",
            agent_id=agent_id,
            risk_category="minimal",
            provider_name="PrivacyCorp",
            intended_purpose="General chat assistant",
        )

        # 3. Add training data
        call_tool(
            "record_training_data",
            agent_id=agent_id,
            dataset_name="ChatCorpus-v1",
            contains_personal_data=True,
            data_governance_measures="Contains user conversations",
        )

        # 4. Add model lineage
        call_tool(
            "record_model_lineage",
            agent_id=agent_id,
            base_model="gpt-4",
            base_model_provider="OpenAI",
        )

        # 5. Log some actions
        for i in range(3):
            call_tool(
                "log_action",
                agent_id=agent_id,
                action_type="inference",
                input_summary=f"User query #{i+1}",
                output_summary=f"Response #{i+1}",
            )

        # 6. Issue a credential
        cred = call_tool(
            "issue_credential",
            subject_agent_id=agent_id,
            credential_type="AgentIdentityCredential",
            issuer_name="PrivacyCorp",
            claims_json='{"role": "chat"}',
        )

        # 7. Record reputation interaction
        other = call_tool(
            "create_agent_identity",
            display_name="OtherBot",
            source_protocol="mcp",
        )
        call_tool(
            "record_interaction",
            agent_id=agent_id,
            counterparty_id=other["agent_id"],
            outcome="success",
        )

        # 8. Verify data exists
        provenance = call_tool("get_provenance", agent_id=agent_id)
        assert len(provenance["training_data"]) > 0
        assert provenance["audit_log_count"] > 0

        identity_check = call_tool("get_identity", agent_id=agent_id)
        assert "agent_id" in identity_check

        rep = call_tool("get_reputation", agent_id=agent_id)
        assert rep["total_interactions"] > 0
        print(f"  [Persona 4] Agent has data in all modules, ready for erasure")

        # 9. GDPR ERASURE - purge all data
        purge = call_tool("purge_agent_data", agent_id=agent_id)
        assert purge["agent_id"] == agent_id
        counts = purge["counts"]
        print(f"  [Persona 4] Purge complete:")
        for key, count in counts.items():
            if count > 0:
                print(f"    - {key}: {count} removed")

        # 10. Verify nothing remains
        identity_after = call_tool("get_identity", agent_id=agent_id)
        assert "error" in identity_after, "Identity should be gone after purge"

        provenance_after = call_tool("get_provenance", agent_id=agent_id)
        assert len(provenance_after.get("training_data", [])) == 0
        assert provenance_after.get("audit_log_count", 0) == 0

        rep_after = call_tool("get_reputation", agent_id=agent_id)
        assert rep_after.get("total_interactions", 0) == 0

        creds_after = call_tool("list_credentials", agent_id=agent_id)
        assert len(creds_after) == 0

        compliance_after = call_tool("get_compliance_profile", agent_id=agent_id)
        assert "error" in compliance_after

        print(f"  [Persona 4] Verified: all data purged, nothing remains")
        print("  [Persona 4] PASS: GDPR erasure workflow complete")


# ===========================================================================
# Persona 5: External Auditor / Verifier
#
# Context: A third-party auditor receives credentials and presentations
# from an AI provider. They need to verify everything cryptographically
# without having direct access to the provider's system.
# ===========================================================================
class TestPersona5_ExternalAuditor:
    """Third-party auditor verifying credentials externally."""

    def test_external_verification_workflow(self):
        # --- Provider side: set up a compliant agent ---
        agent = call_tool(
            "create_agent_identity",
            display_name="AuditableBot",
            source_protocol="api_key",
            capabilities="data_processing",
            description="Agent being audited",
            issuer_name="AuditedCorp",
        )
        agent_id = agent["agent_id"]

        # Compliance + assessment + declaration
        call_tool(
            "create_compliance_profile",
            agent_id=agent_id,
            risk_category="limited",
            provider_name="AuditedCorp",
            intended_purpose="Automated document processing",
            transparency_obligations="AI use disclosed to all users",
        )
        call_tool(
            "record_training_data",
            agent_id=agent_id,
            dataset_name="DocCorpus",
        )
        call_tool(
            "record_model_lineage",
            agent_id=agent_id,
            base_model="BERT-base",
            base_model_provider="Google",
        )
        call_tool(
            "record_conformity_assessment",
            agent_id=agent_id,
            assessment_type="self",
            assessor_name="InternalQA",
            result="pass",
        )
        call_tool(
            "generate_declaration_of_conformity",
            agent_id=agent_id,
        )

        # Issue an additional manual credential
        manual_cred = call_tool(
            "issue_credential",
            subject_agent_id=agent_id,
            credential_type="TransparencyObligationCredential",
            issuer_name="AuditedCorp",
            claims_json=json.dumps({
                "transparency_measure": "AI disclosure banner on all outputs",
                "implementation_date": "2026-01-15",
            }),
        )

        # Get all credentials for this agent
        all_creds = call_tool("list_credentials", agent_id=agent_id)
        assert len(all_creds) >= 2
        cred_ids = [c["id"] for c in all_creds]
        print(f"\n  [Persona 5] Provider has {len(all_creds)} credentials")

        # Create VP for the auditor
        vp = call_tool(
            "create_verifiable_presentation",
            agent_id=agent_id,
            credential_ids=",".join(cred_ids),
            audience_did="did:web:audit-firm.example.com",
            challenge="audit-nonce-abc123",
        )
        assert "proof" in vp
        print(f"  [Persona 5] VP created with {len(vp['verifiableCredential'])} credentials")

        # --- Auditor side: verify the VP externally ---
        vp_check = call_tool(
            "verify_presentation",
            presentation_json=json.dumps(vp, default=str),
        )
        assert vp_check["valid"] is True
        assert vp_check["checks"]["vp_signature_valid"] is True
        assert vp_check["checks"]["credentials_valid"] is True
        assert vp_check["checks"]["challenge_present"] is True
        print(f"  [Persona 5] VP verified: all checks passed")

        # Verify each credential individually
        for cred in all_creds:
            cred_check = call_tool(
                "verify_credential_external",
                credential_json=json.dumps(cred, default=str),
            )
            assert cred_check["valid"] is True, (
                f"Credential {cred['id']} failed: {cred_check}"
            )
        print(f"  [Persona 5] All {len(all_creds)} credentials individually verified")

        # Check audit trail
        trail = call_tool("get_audit_trail", agent_id=agent_id)
        provenance = call_tool("get_provenance", agent_id=agent_id)
        print(f"  [Persona 5] Provenance: {len(provenance['training_data'])} datasets, "
              f"{len(provenance['model_lineage'])} lineage records")

        # Check compliance status
        status = call_tool("get_compliance_status", agent_id=agent_id)
        assert status["compliant"] is True
        assert len(status["missing"]) == 0
        print(f"  [Persona 5] Compliance: {status['completion_pct']}% complete")

        print("  [Persona 5] PASS: External audit workflow complete")


# ===========================================================================
# Persona 6 (bonus): Audit Trail Investigator
#
# Context: An investigator needs to examine the full audit trail of an
# AI system, verify hash chain integrity, check for human overrides,
# and query specific action types.
# ===========================================================================
class TestPersona6_AuditInvestigator:
    """Investigator examining AI system audit trails."""

    def test_audit_investigation_workflow(self):
        # 1. Create the AI system under investigation
        agent = call_tool(
            "create_agent_identity",
            display_name="InvestigatedBot",
            source_protocol="mcp",
            capabilities="decision_making,data_access",
            issuer_name="Corp Under Review",
        )
        agent_id = agent["agent_id"]
        print(f"\n  [Persona 6] Created agent under investigation: {agent_id}")

        # 2. Simulate a series of logged actions
        actions = [
            ("data_access", "Accessed customer database", "Retrieved 500 records", False),
            ("inference", "Credit scoring batch #42", "Generated 500 risk scores", False),
            ("inference", "Flagged applicant #1234 as high risk", "Risk score: 0.92", False),
            ("external_call", "Sent notification to review team", "Email dispatched", False),
            ("inference", "Re-scored applicant #1234 after appeal", "Risk score: 0.45", True),
            ("data_access", "Accessed applicant #1234 appeal documents", "3 documents loaded", False),
            ("inference", "Final recommendation: approve with conditions", "Approved at 7.5% APR", True),
        ]

        logged_entries = []
        for action_type, input_s, output_s, human in actions:
            entry = call_tool(
                "log_action",
                agent_id=agent_id,
                action_type=action_type,
                input_summary=input_s,
                output_summary=output_s,
                decision_rationale=f"Automated step" if not human else "Human override applied",
                human_override=human,
            )
            assert "log_id" in entry, f"Failed to log action: {entry}"
            logged_entries.append(entry)

        print(f"  [Persona 6] Logged {len(actions)} actions")

        # 3. Verify hash chain integrity
        for i in range(1, len(logged_entries)):
            curr = logged_entries[i]
            prev = logged_entries[i - 1]
            if "chain_hash" in curr and "chain_hash" in prev:
                assert curr["prev_hash"] == prev["chain_hash"], (
                    f"Hash chain broken between entry {i-1} and {i}"
                )
        print(f"  [Persona 6] Hash chain integrity verified across {len(logged_entries)} entries")

        # 4. Query only inference actions
        inferences = call_tool(
            "get_audit_trail",
            agent_id=agent_id,
            action_type="inference",
        )
        assert len(inferences) == 4
        print(f"  [Persona 6] Found {len(inferences)} inference actions")

        # 5. Find human overrides
        all_entries = call_tool("get_audit_trail", agent_id=agent_id)
        human_overrides = [e for e in all_entries if e.get("human_override")]
        assert len(human_overrides) == 2
        print(f"  [Persona 6] Found {len(human_overrides)} human override actions")

        # 6. Get full provenance summary
        provenance = call_tool("get_provenance", agent_id=agent_id)
        assert provenance["audit_log_count"] == 7
        print(f"  [Persona 6] Full provenance: {provenance['audit_log_count']} audit entries")

        print("  [Persona 6] PASS: Audit investigation workflow complete")
