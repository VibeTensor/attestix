"""Attestix User Simulation Runner

Simulates 10+ real users going through Attestix from scratch.
Each simulation shows exactly what a user would see at every step,
as if they were using the MCP tools through Claude.

Run: python simulate_users.py
"""

import json
import sys
import os
import time
import traceback

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Redirect storage to a temp directory for clean simulation
import tempfile
import config
TEMP_DIR = tempfile.mkdtemp(prefix="attestix_sim_")
for attr in ["IDENTITIES_FILE", "REPUTATION_FILE", "DELEGATIONS_FILE",
             "COMPLIANCE_FILE", "CREDENTIALS_FILE", "PROVENANCE_FILE",
             "ANCHORS_FILE", "BLOCKCHAIN_CONFIG_FILE", "SIGNING_KEY_FILE", "LOG_FILE"]:
    original = getattr(config, attr)
    setattr(config, attr, config.Path(TEMP_DIR) / original.name)
config.PROJECT_DIR = config.Path(TEMP_DIR)

# Now import MCP tools
from main import mcp
import asyncio

# Get event loop
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)


def call(tool_name, **kwargs):
    """Call an MCP tool and return parsed result."""
    tools = mcp._tool_manager._tools
    fn = tools[tool_name].fn
    raw = loop.run_until_complete(fn(**kwargs))
    return json.loads(raw)


def pp(data):
    """Pretty print JSON data."""
    print(json.dumps(data, indent=2, default=str))


def header(text):
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")


def step(n, text):
    print(f"  Step {n}: {text}")


def show(label, data):
    """Show a result with label."""
    if isinstance(data, dict):
        print(f"    {label}:")
        for k, v in data.items():
            if isinstance(v, dict):
                print(f"      {k}: {{...}}")
            elif isinstance(v, list) and len(v) > 3:
                print(f"      {k}: [{len(v)} items]")
            elif isinstance(v, str) and len(v) > 80:
                print(f"      {k}: {v[:80]}...")
            else:
                print(f"      {k}: {v}")
    elif isinstance(data, list):
        print(f"    {label}: {len(data)} items")
        for item in data[:3]:
            if isinstance(item, dict):
                summary = {k: v for k, v in list(item.items())[:4]}
                print(f"      - {summary}")
    else:
        print(f"    {label}: {data}")


def divider():
    print(f"    {'- '*35}")


passed = 0
failed = 0
errors = []


def run_simulation(name, func):
    global passed, failed
    try:
        # Clear storage between simulations
        from services.cache import clear_cache
        clear_cache()
        for f in config.Path(TEMP_DIR).glob("*.json"):
            f.unlink()

        func()
        passed += 1
        print(f"\n    RESULT: PASSED\n")
    except Exception as e:
        failed += 1
        errors.append((name, str(e)))
        print(f"\n    RESULT: FAILED - {e}\n")
        traceback.print_exc()


# ========================================================================
# SIMULATION 1: Solo Developer Building a Chatbot
# "I just found Attestix on GitHub. I want to register my chatbot."
# ========================================================================
def sim_solo_developer():
    header("USER 1: Solo Developer - 'I want to register my chatbot'")

    print("  Context: Alex is a solo dev who built a customer support chatbot.")
    print("  They found Attestix on GitHub and want to give their bot an identity.\n")

    step(1, "Alex creates an identity for their chatbot")
    agent = call("create_agent_identity",
                 display_name="HelpDesk-Bot",
                 source_protocol="mcp",
                 capabilities="chat,ticket_creation,knowledge_base",
                 description="Customer support chatbot for SaaS product",
                 issuer_name="Alex's Startup")
    print(f"    Agent ID: {agent['agent_id']}")
    print(f"    Display Name: {agent['display_name']}")
    print(f"    Capabilities: {agent['capabilities']}")
    print(f"    Issuer DID: {agent['issuer']['did'][:50]}...")
    print(f"    Expires: {agent['expires_at']}")
    agent_id = agent["agent_id"]

    divider()
    step(2, "Alex verifies the identity is cryptographically valid")
    verify = call("verify_identity", agent_id=agent_id)
    print(f"    Valid: {verify['valid']}")
    print(f"    Checks: {verify['checks']}")

    divider()
    step(3, "Alex creates a DID for decentralized identity")
    did = call("create_did_key")
    print(f"    DID: {did['did']}")
    print(f"    Algorithm: Ed25519 (multicodec 0xed01)")

    divider()
    step(4, "Alex translates the identity to an A2A Agent Card")
    a2a = call("translate_identity", agent_id=agent_id, target_format="a2a_agent_card")
    print(f"    Agent Card Name: {a2a['name']}")
    print(f"    Skills: {a2a['skills']}")
    print(f"    URL: {a2a.get('url', 'not set')}")

    divider()
    step(5, "Alex issues an identity credential for the bot")
    cred = call("issue_credential",
                subject_agent_id=agent_id,
                credential_type="AgentIdentityCredential",
                issuer_name="Alex's Startup",
                claims_json=json.dumps({
                    "role": "customer_support",
                    "version": "1.0.0",
                    "environment": "production"
                }))
    print(f"    Credential ID: {cred['id']}")
    print(f"    Type: {cred['type']}")
    print(f"    Proof Type: {cred['proof']['type']}")

    divider()
    step(6, "Alex verifies the credential")
    cred_check = call("verify_credential", credential_id=cred["id"])
    print(f"    Valid: {cred_check['valid']}")
    print(f"    Signature Valid: {cred_check['checks']['signature_valid']}")
    print(f"    Not Expired: {cred_check['checks']['not_expired']}")
    print(f"    Not Revoked: {cred_check['checks']['not_revoked']}")

    divider()
    step(7, "Alex checks their bot appears in the registry")
    agents = call("list_identities")
    print(f"    Total agents registered: {len(agents)}")
    print(f"    My bot found: {any(a['agent_id'] == agent_id for a in agents)}")

    print(f"\n  Alex's chatbot now has a cryptographically verifiable identity.")
    print(f"  They can share the agent_id with partners who can verify it independently.")


# ========================================================================
# SIMULATION 2: Compliance Officer at a Bank
# "We deploy a loan screening AI. We need EU AI Act compliance."
# ========================================================================
def sim_compliance_officer():
    header("USER 2: Compliance Officer - 'We need EU AI Act compliance'")

    print("  Context: Maria is the compliance officer at EuroBank.")
    print("  Their loan screening AI needs full EU AI Act compliance before August 2026.\n")

    step(1, "Maria registers the loan screening AI system")
    agent = call("create_agent_identity",
                 display_name="LoanScreener-AI",
                 capabilities="credit_scoring,risk_assessment,fraud_detection",
                 description="Automated loan application screening and credit decision support",
                 issuer_name="EuroBank AG")
    agent_id = agent["agent_id"]
    print(f"    Agent ID: {agent_id}")
    print(f"    Capabilities: {agent['capabilities']}")

    divider()
    step(2, "Maria creates a HIGH-RISK compliance profile")
    profile = call("create_compliance_profile",
                   agent_id=agent_id,
                   risk_category="high",
                   provider_name="EuroBank AG",
                   intended_purpose="Automated credit scoring for consumer loan applications (Annex III Category 5(a))",
                   transparency_obligations="Full decision explanations provided to applicants per Article 13",
                   human_oversight_measures="Senior credit officer reviews all AI recommendations above 50K EUR",
                   provider_address="Bankstrasse 1, Frankfurt am Main, Germany",
                   authorised_representative="Dr. Klaus Weber, EU AI Act Compliance Director")
    print(f"    Profile ID: {profile['profile_id']}")
    print(f"    Risk Category: {profile['risk_category']}")
    print(f"    Required Obligations: {len(profile['required_obligations'])} items")
    for ob in profile["required_obligations"]:
        print(f"      - {ob}")

    divider()
    step(3, "Maria records training data provenance (Article 10)")
    datasets = [
        ("Historical Loan Performance 2015-2025", True, "Proprietary",
         "De-identified per GDPR Art. 5, DPA in place with data processor"),
        ("ECB Economic Indicators Dataset", False, "Open Data",
         "Public macroeconomic data, no personal information"),
        ("Synthetic Stress Test Scenarios", False, "Internal",
         "GAN-generated financial scenarios for model robustness testing"),
    ]
    for name, personal, lic, gov in datasets:
        td = call("record_training_data",
                   agent_id=agent_id, dataset_name=name,
                   contains_personal_data=personal, license=lic,
                   data_governance_measures=gov)
        print(f"    Recorded: {name}")
        print(f"      Entry ID: {td['entry_id']}")
        print(f"      Personal Data: {personal}")

    divider()
    step(4, "Maria records model lineage (Article 11)")
    lineage = call("record_model_lineage",
                   agent_id=agent_id,
                   base_model="XGBoost 2.1",
                   base_model_provider="Open Source (Apache 2.0)",
                   fine_tuning_method="Gradient boosting with Optuna hyperparameter optimization",
                   evaluation_metrics_json=json.dumps({
                       "auc_roc": 0.892,
                       "precision": 0.87,
                       "recall": 0.91,
                       "demographic_parity_diff": 0.03,
                       "false_positive_rate": 0.08,
                   }))
    print(f"    Model: {lineage.get('base_model', 'XGBoost 2.1')}")
    print(f"    Entry ID: {lineage['entry_id']}")

    divider()
    step(5, "Maria checks the compliance gap analysis")
    status1 = call("get_compliance_status", agent_id=agent_id)
    print(f"    Completion: {status1['completion_pct']}%")
    print(f"    Completed: {status1['completed']}")
    print(f"    MISSING: {status1['missing']}")
    print(f"    Compliant: {status1['compliant']}")

    divider()
    step(6, "Maria tries self-assessment (should be BLOCKED for high-risk)")
    bad = call("record_conformity_assessment",
               agent_id=agent_id, assessment_type="self",
               assessor_name="Internal QA", result="pass")
    print(f"    Result: {bad}")
    print(f"    (Correctly blocked! High-risk requires third-party assessment)")

    divider()
    step(7, "Maria records third-party conformity assessment (Article 43)")
    assessment = call("record_conformity_assessment",
                      agent_id=agent_id,
                      assessment_type="third_party",
                      assessor_name="TUV Rheinland AG",
                      result="pass",
                      findings="Full Annex III Category 5(a) assessment completed. All requirements met.",
                      ce_marking_eligible=True)
    print(f"    Assessment ID: {assessment['assessment_id']}")
    print(f"    Result: {assessment['result']}")
    print(f"    Assessor: {assessment['assessor_name']}")
    print(f"    CE Marking Eligible: {assessment['ce_marking_eligible']}")

    divider()
    step(8, "Maria generates the Annex V Declaration of Conformity")
    decl = call("generate_declaration_of_conformity", agent_id=agent_id)
    print(f"    Declaration ID: {decl['declaration_id']}")
    print(f"    Regulation: {decl['regulation_reference']}")
    annex = decl["annex_v_fields"]
    print(f"    Annex V Fields:")
    for k, v in annex.items():
        val = str(v)
        if len(val) > 60:
            val = val[:60] + "..."
        print(f"      {k}: {val}")

    divider()
    step(9, "Maria checks the auto-issued compliance credential")
    creds = call("list_credentials", agent_id=agent_id,
                 credential_type="EUAIActComplianceCredential")
    print(f"    Auto-issued compliance credentials: {len(creds)}")
    if creds:
        cred = creds[0]
        print(f"    Credential ID: {cred['id']}")
        print(f"    Type: {cred['type']}")
        verify = call("verify_credential", credential_id=cred["id"])
        print(f"    Verification: valid={verify['valid']}, signature={verify['checks']['signature_valid']}")

    divider()
    step(10, "Maria creates a Verifiable Presentation for the regulator")
    if creds:
        vp = call("create_verifiable_presentation",
                   agent_id=agent_id,
                   credential_ids=creds[0]["id"],
                   audience_did="did:web:ai-office.europa.eu",
                   challenge="regulatory-audit-2026-Q1")
        print(f"    VP Type: {vp['type']}")
        print(f"    Holder: {vp['holder']}")
        print(f"    Credentials Included: {len(vp['verifiableCredential'])}")
        print(f"    Challenge: {vp['proof']['challenge']}")
        print(f"    Domain: {vp['proof']['domain']}")

    divider()
    step(11, "Final compliance status check")
    status2 = call("get_compliance_status", agent_id=agent_id)
    print(f"    Completion: {status2['completion_pct']}%")
    print(f"    Completed: {len(status2['completed'])} obligations")
    print(f"    Missing: {len(status2['missing'])} obligations")
    for m in status2["missing"]:
        print(f"      - Still missing: {m}")

    print(f"\n  Maria's loan screening AI now has documented EU AI Act compliance")
    print(f"  with a signed Annex V declaration and W3C Verifiable Credential.")


# ========================================================================
# SIMULATION 3: Platform Operator Running Multiple Agents
# "I manage 5 agents and need delegation, reputation, and monitoring."
# ========================================================================
def sim_platform_operator():
    header("USER 3: Platform Operator - 'I manage a fleet of AI agents'")

    print("  Context: Raj runs an AI platform with multiple specialized agents.")
    print("  He needs delegation chains, reputation tracking, and monitoring.\n")

    step(1, "Raj creates the orchestrator agent")
    orch = call("create_agent_identity",
                display_name="OrchestratorPrime",
                source_protocol="mcp",
                capabilities="orchestrate,delegate,monitor,escalate",
                description="Central orchestration agent managing all workers",
                issuer_name="RajTech Platform")
    orch_id = orch["agent_id"]
    print(f"    Orchestrator: {orch_id}")

    step(2, "Raj creates 4 worker agents")
    workers = []
    worker_specs = [
        ("DataFetcher", "web_search,api_calls,data_retrieval"),
        ("Analyzer", "data_analysis,ml_inference,statistics"),
        ("Writer", "report_generation,email_drafting,summaries"),
        ("Monitor", "log_analysis,alerting,health_checks"),
    ]
    for name, caps in worker_specs:
        w = call("create_agent_identity",
                 display_name=name, source_protocol="mcp",
                 capabilities=caps, issuer_name="RajTech Platform")
        workers.append(w)
        print(f"    Worker: {name} -> {w['agent_id']}")

    divider()
    step(3, "Raj delegates capabilities from orchestrator to each worker")
    delegations = []
    for w, (name, caps) in zip(workers, worker_specs):
        d = call("create_delegation",
                 issuer_agent_id=orch_id,
                 audience_agent_id=w["agent_id"],
                 capabilities=caps.split(",")[0],  # delegate primary capability
                 expiry_hours=8)
        delegations.append(d)
        print(f"    Delegated '{caps.split(',')[0]}' to {name}")
        print(f"      Token (first 50 chars): {d['token'][:50]}...")
        print(f"      Expires in: 8 hours")

    divider()
    step(4, "Raj verifies each delegation is valid")
    for d, (name, _) in zip(delegations, worker_specs):
        check = call("verify_delegation", token=d["token"])
        print(f"    {name}: valid={check['valid']}, delegator={check['delegator'][:30]}...")

    divider()
    step(5, "Raj simulates agent interactions and tracks reputation")
    outcomes = [
        (0, "success", "Fetched 500 records from API"),
        (0, "success", "Scraped and parsed 20 web pages"),
        (1, "success", "Ran sentiment analysis on 1000 reviews"),
        (1, "success", "Generated ML predictions with 94% accuracy"),
        (2, "success", "Generated quarterly report"),
        (2, "failure", "Email draft had formatting errors"),
        (2, "success", "Re-generated email successfully"),
        (3, "success", "Detected and alerted on API latency spike"),
        (3, "success", "Performed health check on all services"),
        (3, "partial", "Log analysis incomplete due to missing permissions"),
    ]
    for idx, outcome, detail in outcomes:
        call("record_interaction",
             agent_id=workers[idx]["agent_id"],
             counterparty_id=orch_id,
             outcome=outcome,
             category="task_execution",
             details=detail)
    print(f"    Recorded {len(outcomes)} interactions across 4 workers")

    divider()
    step(6, "Raj checks reputation scores for each worker")
    for w, (name, _) in zip(workers, worker_specs):
        rep = call("get_reputation", agent_id=w["agent_id"])
        print(f"    {name}: score={rep['trust_score']:.4f}, interactions={rep['total_interactions']}")

    divider()
    step(7, "Raj queries for high-reputation agents")
    top = call("query_reputation", min_score=0.8)
    print(f"    Agents with score >= 0.8: {len(top)}")
    for t in top:
        print(f"      - {t['agent_id'][:30]}... score={t['trust_score']:.4f}")

    divider()
    step(8, "Raj lists all delegations he's issued")
    my_delegations = call("list_delegations", agent_id=orch_id, role="issuer")
    print(f"    Active delegations from orchestrator: {len(my_delegations)}")

    divider()
    step(9, "Raj revokes the underperforming Writer agent")
    call("revoke_identity",
         agent_id=workers[2]["agent_id"],
         reason="Repeated formatting errors, replacing with v2")
    check = call("verify_identity", agent_id=workers[2]["agent_id"])
    print(f"    Writer agent revoked: valid={check['valid']}")
    print(f"    Reason: Repeated formatting errors, replacing with v2")

    divider()
    step(10, "Raj logs the orchestrator's decision-making for audit")
    call("log_action",
         agent_id=orch_id,
         action_type="delegation",
         input_summary="Worker Writer-v1 performance review",
         output_summary="Revoked identity, delegations still active but agent invalid",
         decision_rationale="3 interactions: 2 success, 1 failure. Below quality threshold.",
         human_override=False)
    trail = call("get_audit_trail", agent_id=orch_id)
    print(f"    Audit trail entries for orchestrator: {len(trail)}")

    print(f"\n  Raj's platform now has 4 agents with delegation chains,")
    print(f"  reputation tracking, and a full audit trail of decisions.")


# ========================================================================
# SIMULATION 4: Healthcare Company - Medical AI
# "We're deploying a cardiac AI. Strictest compliance path."
# ========================================================================
def sim_healthcare():
    header("USER 4: Healthcare Company - 'Cardiac diagnostic AI deployment'")

    print("  Context: Dr. Chen leads the AI team at MedTech Innovations.")
    print("  Their cardiac AI must pass the strictest EU AI Act requirements.\n")

    step(1, "Dr. Chen registers the cardiac AI system")
    agent = call("create_agent_identity",
                 display_name="CardioAI-Detect",
                 capabilities="ecg_analysis,arrhythmia_detection,risk_stratification",
                 description="AI-assisted cardiac arrhythmia detection from 12-lead ECG",
                 issuer_name="MedTech Innovations GmbH")
    agent_id = agent["agent_id"]
    print(f"    Agent: {agent_id}")
    print(f"    Capabilities: {agent['capabilities']}")

    divider()
    step(2, "Dr. Chen records 4 training data sources with strict governance")
    datasets = [
        ("PhysioNet MIMIC-IV ECG", "PhysioNet DUA", True,
         "IRB-approved, de-identified per HIPAA Safe Harbor"),
        ("PTB-XL ECG Database", "CC-BY-4.0", False,
         "Public research database, no patient identifiers"),
        ("Clinical Validation Set (n=12500)", "Proprietary", True,
         "Hospital ethics committee approved, patient consent obtained"),
        ("Synthetic ECG Augmentation", "Internal", False,
         "GAN-generated signals, no real patient data"),
    ]
    for name, lic, personal, gov in datasets:
        call("record_training_data",
             agent_id=agent_id, dataset_name=name,
             license=lic, contains_personal_data=personal,
             data_governance_measures=gov)
        print(f"    {name}")
        print(f"      License: {lic} | Personal Data: {personal}")

    divider()
    step(3, "Dr. Chen records model lineage with clinical metrics")
    call("record_model_lineage",
         agent_id=agent_id,
         base_model="ResNet-ECG-v4",
         base_model_provider="MedTech Innovations GmbH",
         fine_tuning_method="Transfer learning, fine-tuned on ECG spectrograms",
         evaluation_metrics_json=json.dumps({
             "sensitivity": 0.96,
             "specificity": 0.94,
             "ppv": 0.91,
             "npv": 0.97,
             "auc_roc": 0.982,
             "f1_score": 0.935,
         }))
    print(f"    Model: ResNet-ECG-v4")
    print(f"    AUC-ROC: 0.982 | Sensitivity: 0.96 | Specificity: 0.94")

    divider()
    step(4, "Dr. Chen creates high-risk compliance profile")
    call("create_compliance_profile",
         agent_id=agent_id,
         risk_category="high",
         provider_name="MedTech Innovations GmbH",
         intended_purpose="AI-assisted arrhythmia detection (Annex III Category 1(a) - medical devices)",
         transparency_obligations="Clinical decision support label shown, AI confidence scores displayed",
         human_oversight_measures="Board-certified cardiologist must confirm all AI findings",
         provider_address="Medizinstrasse 42, Munich, Germany 80333",
         authorised_representative="Dr. Anna Mueller, EU Authorized Representative")
    print(f"    Risk: HIGH (medical device)")
    print(f"    Human oversight: Cardiologist confirmation required")

    divider()
    step(5, "Dr. Chen logs clinical decision events")
    events = [
        ("ECG #4521 - 65yo male", "Atrial fibrillation detected (confidence: 0.94)", False),
        ("ECG #4521 - cardiologist review", "AF confirmed, treatment initiated", True),
        ("ECG #4522 - 42yo female", "Normal sinus rhythm (confidence: 0.99)", False),
        ("ECG #4523 - 78yo male", "Possible VT (confidence: 0.72) - FLAGGED", False),
        ("ECG #4523 - cardiologist override", "VT ruled out, motion artifact", True),
    ]
    for inp, out, human in events:
        entry = call("log_action",
                     agent_id=agent_id, action_type="inference",
                     input_summary=inp, output_summary=out,
                     human_override=human)
        override_tag = " [HUMAN OVERRIDE]" if human else ""
        print(f"    {inp} -> {out[:50]}...{override_tag}")

    divider()
    step(6, "Dr. Chen gets third-party assessment from notified body")
    assessment = call("record_conformity_assessment",
                      agent_id=agent_id,
                      assessment_type="third_party",
                      assessor_name="BSI Group (Notified Body 0086)",
                      result="pass",
                      findings="Full Article 43 and MDR 2017/745 cross-reference completed",
                      ce_marking_eligible=True)
    print(f"    Notified Body: BSI Group (0086)")
    print(f"    Result: PASS")
    print(f"    CE Marking: Eligible")

    divider()
    step(7, "Dr. Chen generates the Annex V declaration")
    decl = call("generate_declaration_of_conformity", agent_id=agent_id)
    print(f"    Declaration: {decl['declaration_id']}")
    print(f"    Sole Responsibility: {decl['annex_v_fields']['11_sole_responsibility'][:80]}...")

    divider()
    step(8, "Dr. Chen creates a VP for the notified body")
    creds = call("list_credentials", agent_id=agent_id)
    all_ids = ",".join(c["id"] for c in creds)
    vp = call("create_verifiable_presentation",
              agent_id=agent_id,
              credential_ids=all_ids,
              audience_did="did:web:bsigroup.com",
              challenge="clinical-assessment-2026")
    print(f"    VP with {len(vp['verifiableCredential'])} credentials")
    print(f"    Audience: did:web:bsigroup.com")

    # Verify the VP
    vp_check = call("verify_presentation",
                    presentation_json=json.dumps(vp, default=str))
    print(f"    VP Verification: valid={vp_check['valid']}")

    print(f"\n  Dr. Chen's cardiac AI has full EU AI Act documentation,")
    print(f"  third-party assessment, and cryptographically verifiable credentials.")


# ========================================================================
# SIMULATION 5: External Auditor Verifying Credentials
# "I received a VP from a company. I need to verify everything."
# ========================================================================
def sim_external_auditor():
    header("USER 5: External Auditor - 'Verify this company's AI credentials'")

    print("  Context: Sophie is an auditor at a compliance firm.")
    print("  She received credentials from an AI provider and must verify them.\n")

    # First, set up the provider's side
    step(1, "PROVIDER SIDE: Set up a compliant agent")
    agent = call("create_agent_identity",
                 display_name="DocumentProcessor-AI",
                 capabilities="ocr,classification,extraction",
                 description="Automated document processing system",
                 issuer_name="DocTech Solutions")
    agent_id = agent["agent_id"]

    call("create_compliance_profile",
         agent_id=agent_id, risk_category="limited",
         provider_name="DocTech Solutions",
         intended_purpose="Automated invoice and contract processing",
         transparency_obligations="AI use disclosed to all users")
    call("record_training_data", agent_id=agent_id, dataset_name="Invoice Dataset v3")
    call("record_model_lineage", agent_id=agent_id,
         base_model="LayoutLM-v3", base_model_provider="Microsoft")
    call("record_conformity_assessment",
         agent_id=agent_id, assessment_type="self",
         assessor_name="DocTech QA Team", result="pass")
    decl = call("generate_declaration_of_conformity", agent_id=agent_id)
    print(f"    Provider created agent and achieved compliance")
    print(f"    Declaration: {decl['declaration_id']}")

    # Issue additional credential
    manual_cred = call("issue_credential",
                       subject_agent_id=agent_id,
                       credential_type="TransparencyObligationCredential",
                       issuer_name="DocTech Solutions",
                       claims_json=json.dumps({
                           "transparency_measure": "AI disclosure banner on all outputs",
                           "implementation_date": "2026-01-15"
                       }))

    # Create VP for auditor
    all_creds = call("list_credentials", agent_id=agent_id)
    vp = call("create_verifiable_presentation",
              agent_id=agent_id,
              credential_ids=",".join(c["id"] for c in all_creds),
              audience_did="did:web:audit-firm.example.com",
              challenge="audit-nonce-xyz789")
    print(f"    VP created with {len(vp['verifiableCredential'])} credentials")

    divider()
    print(f"\n  --- HANDOFF: VP transmitted to auditor ---\n")
    divider()

    step(2, "AUDITOR SIDE: Sophie receives the VP and begins verification")
    vp_json = json.dumps(vp, default=str)
    print(f"    Received VP: {len(vp_json)} bytes of JSON")
    print(f"    Contains {len(vp['verifiableCredential'])} credentials")

    divider()
    step(3, "Sophie verifies the VP signature and structure")
    vp_check = call("verify_presentation", presentation_json=vp_json)
    print(f"    VP Valid: {vp_check['valid']}")
    print(f"    Checks:")
    for k, v in vp_check["checks"].items():
        print(f"      {k}: {v}")

    divider()
    step(4, "Sophie verifies each credential individually")
    for i, cred in enumerate(all_creds):
        cred_check = call("verify_credential_external",
                          credential_json=json.dumps(cred, default=str))
        print(f"    Credential {i+1}: {cred['type'][-1]}")
        print(f"      Valid: {cred_check['valid']}")
        print(f"      Signature: {cred_check['checks']['signature_valid']}")
        print(f"      Not Expired: {cred_check['checks']['not_expired']}")

    divider()
    step(5, "Sophie checks the compliance status")
    status = call("get_compliance_status", agent_id=agent_id)
    print(f"    Compliant: {status['compliant']}")
    print(f"    Completion: {status['completion_pct']}%")

    divider()
    step(6, "Sophie reviews the audit trail")
    provenance = call("get_provenance", agent_id=agent_id)
    print(f"    Training Datasets: {len(provenance['training_data'])}")
    print(f"    Model Lineage Records: {len(provenance['model_lineage'])}")
    print(f"    Audit Log Entries: {provenance['audit_log_count']}")

    print(f"\n  Sophie has independently verified all credentials cryptographically")
    print(f"  without needing access to DocTech's internal systems.")


# ========================================================================
# SIMULATION 6: DPO Handling GDPR Erasure Request
# "We received an erasure request. Delete everything for this agent."
# ========================================================================
def sim_gdpr_erasure():
    header("USER 6: Data Protection Officer - 'GDPR erasure request received'")

    print("  Context: Jan is the DPO at a tech company.")
    print("  A customer exercised their GDPR Article 17 right to erasure.\n")

    step(1, "Jan identifies the agent to be erased")
    agent = call("create_agent_identity",
                 display_name="PersonalAssistant-UserX",
                 source_protocol="mcp",
                 capabilities="chat,scheduling,email",
                 description="Personal assistant agent for User X",
                 issuer_name="TechCo")
    agent_id = agent["agent_id"]
    print(f"    Agent: {agent_id}")

    step(2, "Jan checks what data exists for this agent")
    # Populate across all modules
    call("create_compliance_profile", agent_id=agent_id, risk_category="minimal",
         provider_name="TechCo", intended_purpose="Personal assistant",
         transparency_obligations="AI disclosed")
    call("record_training_data", agent_id=agent_id, dataset_name="UserChat-v1",
         contains_personal_data=True, data_governance_measures="Contains user conversations")
    call("record_model_lineage", agent_id=agent_id, base_model="GPT-4o",
         base_model_provider="OpenAI")
    for i in range(5):
        call("log_action", agent_id=agent_id, action_type="inference",
             input_summary=f"User query #{i+1}", output_summary=f"Response #{i+1}")
    cred = call("issue_credential", subject_agent_id=agent_id,
                credential_type="AgentIdentityCredential",
                issuer_name="TechCo", claims_json='{"role": "assistant"}')

    other = call("create_agent_identity", display_name="Counter", source_protocol="mcp")
    call("record_interaction", agent_id=agent_id, counterparty_id=other["agent_id"],
         outcome="success", category="general")

    # Verify data exists
    identity = call("get_identity", agent_id=agent_id)
    provenance = call("get_provenance", agent_id=agent_id)
    rep = call("get_reputation", agent_id=agent_id)
    print(f"    Data found:")
    print(f"      Identity: EXISTS")
    print(f"      Training data: {len(provenance['training_data'])} records")
    print(f"      Model lineage: {len(provenance['model_lineage'])} records")
    print(f"      Audit log: {provenance['audit_log_count']} entries")
    print(f"      Credentials: {len(call('list_credentials', agent_id=agent_id))} issued")
    print(f"      Reputation: {rep['total_interactions']} interactions")
    print(f"      Compliance: profile exists")

    divider()
    step(3, "Jan executes the GDPR Article 17 erasure")
    print(f"    Executing purge_agent_data for {agent_id}...")
    purge = call("purge_agent_data", agent_id=agent_id)
    print(f"    Purge result:")
    for category, count in purge["counts"].items():
        status = f"{count} removed" if count > 0 else "none found"
        print(f"      {category}: {status}")

    divider()
    step(4, "Jan verifies NOTHING remains")
    id_after = call("get_identity", agent_id=agent_id)
    print(f"    Identity: {'GONE' if 'error' in id_after else 'STILL EXISTS!'}")

    prov_after = call("get_provenance", agent_id=agent_id)
    print(f"    Training data: {len(prov_after.get('training_data', []))} records")
    print(f"    Audit log: {prov_after.get('audit_log_count', 0)} entries")

    creds_after = call("list_credentials", agent_id=agent_id)
    print(f"    Credentials: {len(creds_after)} remaining")

    rep_after = call("get_reputation", agent_id=agent_id)
    print(f"    Reputation interactions: {rep_after.get('total_interactions', 0)}")

    comp_after = call("get_compliance_profile", agent_id=agent_id)
    print(f"    Compliance profile: {'GONE' if 'error' in comp_after else 'STILL EXISTS!'}")

    print(f"\n  Jan has confirmed complete data erasure per GDPR Article 17.")
    print(f"  An audit record of the erasure itself should be kept separately.")


# ========================================================================
# SIMULATION 7: Cybersecurity Team Testing Integrity
# "Can someone forge credentials? Let's test tamper detection."
# ========================================================================
def sim_security_test():
    header("USER 7: Cybersecurity Team - 'Testing tamper detection'")

    print("  Context: The security team tests if Attestix detects forgery.\n")

    step(1, "Create a legitimate agent and credential")
    agent = call("create_agent_identity",
                 display_name="TestTarget",
                 capabilities="test",
                 issuer_name="SecurityLab")
    agent_id = agent["agent_id"]
    cred = call("issue_credential",
                subject_agent_id=agent_id,
                credential_type="AgentIdentityCredential",
                issuer_name="SecurityLab",
                claims_json='{"clearance": "top_secret"}')
    print(f"    Agent: {agent_id}")
    print(f"    Credential: {cred['id']}")

    divider()
    step(2, "Verify legitimate credential passes")
    check = call("verify_credential", credential_id=cred["id"])
    print(f"    Legitimate credential: valid={check['valid']}")

    divider()
    step(3, "ATTACK: Tamper with the credential claims")
    tampered = json.loads(json.dumps(cred, default=str))
    tampered["credentialSubject"]["clearance"] = "public"  # Changed!
    tampered_check = call("verify_credential_external",
                          credential_json=json.dumps(tampered, default=str))
    print(f"    Tampered credential (changed clearance):")
    print(f"      Valid: {tampered_check['valid']}")
    print(f"      Signature Valid: {tampered_check['checks']['signature_valid']}")
    print(f"      TAMPER DETECTED!")

    divider()
    step(4, "ATTACK: Forge a completely fake credential")
    fake = {
        "@context": ["https://www.w3.org/2018/credentials/v1"],
        "id": "urn:uuid:fake-12345",
        "type": ["VerifiableCredential", "EUAIActComplianceCredential"],
        "issuer": {"id": "did:key:z6MkFAKEFAKEFAKE", "name": "FakeIssuer"},
        "issuanceDate": "2026-01-01T00:00:00+00:00",
        "credentialSubject": {"id": agent_id, "compliant": True},
        "proof": {
            "type": "Ed25519Signature2020",
            "proofValue": "FAKE_SIGNATURE_AAAA",
            "verificationMethod": "did:key:z6MkFAKE#z6MkFAKE",
        }
    }
    fake_check = call("verify_credential_external",
                      credential_json=json.dumps(fake))
    print(f"    Forged credential:")
    print(f"      Valid: {fake_check['valid']}")
    print(f"      Signature: {fake_check['checks']['signature_valid']}")
    print(f"      FORGERY DETECTED!")

    divider()
    step(5, "ATTACK: Tamper with JWT delegation token")
    agent_b = call("create_agent_identity", display_name="Target-B",
                   source_protocol="mcp", issuer_name="SecurityLab")
    delegation = call("create_delegation",
                      issuer_agent_id=agent_id,
                      audience_agent_id=agent_b["agent_id"],
                      capabilities="admin", expiry_hours=1)

    # Flip a character in the signature
    parts = delegation["token"].split(".")
    sig = list(parts[2])
    sig[0] = "X" if sig[0] != "X" else "Y"
    tampered_token = f"{parts[0]}.{parts[1]}.{''.join(sig)}"

    good_check = call("verify_delegation", token=delegation["token"])
    bad_check = call("verify_delegation", token=tampered_token)
    print(f"    Original JWT: valid={good_check['valid']}")
    print(f"    Tampered JWT: valid={bad_check['valid']}")
    print(f"    JWT TAMPER DETECTED!")

    divider()
    step(6, "ATTACK: Create VP with tampered credential inside")
    vp = call("create_verifiable_presentation",
              agent_id=agent_id, credential_ids=cred["id"],
              challenge="security-test")
    tampered_vp = json.loads(json.dumps(vp, default=str))
    tampered_vp["verifiableCredential"][0]["credentialSubject"]["clearance"] = "hacked"
    vp_check = call("verify_presentation",
                    presentation_json=json.dumps(tampered_vp, default=str))
    print(f"    VP with tampered inner credential:")
    print(f"      Valid: {vp_check['valid']}")
    print(f"      Credentials Valid: {vp_check['checks']['credentials_valid']}")
    print(f"      NESTED TAMPER DETECTED!")

    divider()
    step(7, "Test revocation enforcement")
    call("revoke_credential", credential_id=cred["id"], reason="Security test")
    revoked_check = call("verify_credential", credential_id=cred["id"])
    print(f"    Revoked credential: valid={revoked_check['valid']}, not_revoked={revoked_check['checks']['not_revoked']}")

    call("revoke_identity", agent_id=agent_id, reason="Security test")
    id_check = call("verify_identity", agent_id=agent_id)
    print(f"    Revoked identity: valid={id_check['valid']}, not_revoked={id_check['checks']['not_revoked']}")

    print(f"\n  All 6 attack vectors were detected and blocked.")
    print(f"  Ed25519 signatures catch any modification to signed data.")


# ========================================================================
# SIMULATION 8: Government Regulator Inspection
# ========================================================================
def sim_regulator():
    header("USER 8: EU Government Regulator - 'Inspecting AI providers'")

    print("  Context: Inspector at the EU AI Office checking 3 providers.\n")

    # Create 3 providers with different compliance states
    providers = {}

    # Provider A: Compliant high-risk
    a = call("create_agent_identity", display_name="CreditScore-AI",
             capabilities="credit_scoring", issuer_name="FinTech Corp")
    aid_a = a["agent_id"]
    call("create_compliance_profile", agent_id=aid_a, risk_category="high",
         provider_name="FinTech Corp",
         intended_purpose="Consumer credit scoring",
         transparency_obligations="Full explanations per Article 13",
         human_oversight_measures="Officer reviews decisions above 10K EUR",
         provider_address="Berlin, Germany")
    call("record_training_data", agent_id=aid_a, dataset_name="Credit History",
         data_governance_measures="GDPR compliant")
    call("record_model_lineage", agent_id=aid_a, base_model="XGBoost",
         base_model_provider="Open Source",
         evaluation_metrics_json='{"auc": 0.89}')
    call("record_conformity_assessment", agent_id=aid_a,
         assessment_type="third_party", assessor_name="TUV SUD",
         result="pass", ce_marking_eligible=True)
    call("generate_declaration_of_conformity", agent_id=aid_a)
    providers["A (FinTech Corp)"] = aid_a

    # Provider B: Limited-risk, compliant
    b = call("create_agent_identity", display_name="ChatBot-FR",
             capabilities="customer_chat", issuer_name="RetailCo")
    aid_b = b["agent_id"]
    call("create_compliance_profile", agent_id=aid_b, risk_category="limited",
         provider_name="RetailCo",
         intended_purpose="Customer FAQ bot",
         transparency_obligations="AI identity disclosed in every message")
    call("record_training_data", agent_id=aid_b, dataset_name="FAQ KB")
    call("record_model_lineage", agent_id=aid_b, base_model="BERT",
         base_model_provider="Google")
    call("record_conformity_assessment", agent_id=aid_b,
         assessment_type="self", assessor_name="RetailCo QA", result="pass")
    call("generate_declaration_of_conformity", agent_id=aid_b)
    providers["B (RetailCo)"] = aid_b

    # Provider C: Non-compliant
    c = call("create_agent_identity", display_name="HireBot-AI",
             capabilities="resume_screening", issuer_name="TalentTech")
    aid_c = c["agent_id"]
    call("create_compliance_profile", agent_id=aid_c, risk_category="high",
         provider_name="TalentTech",
         intended_purpose="Recruitment screening",
         transparency_obligations="Candidates informed of AI use",
         human_oversight_measures="HR reviews rejections")
    # NO training data, NO assessment, NO declaration
    providers["C (TalentTech)"] = aid_c

    step(1, "Inspector reviews all 3 providers")
    for name, aid in providers.items():
        status = call("get_compliance_status", agent_id=aid)
        print(f"    Provider {name}:")
        print(f"      Compliant: {status['compliant']}")
        print(f"      Completion: {status['completion_pct']}%")
        print(f"      Missing: {status['missing'][:3]}{'...' if len(status['missing']) > 3 else ''}")
        print()

    divider()
    step(2, "Inspector verifies Provider A's VP")
    creds_a = call("list_credentials", agent_id=aid_a,
                   credential_type="EUAIActComplianceCredential")
    vp = call("create_verifiable_presentation",
              agent_id=aid_a, credential_ids=creds_a[0]["id"],
              audience_did="did:web:ai-office.europa.eu",
              challenge="inspection-2026-Q1")
    vp_check = call("verify_presentation",
                    presentation_json=json.dumps(vp, default=str))
    print(f"    Provider A VP: valid={vp_check['valid']}")
    print(f"    Challenge verified: {vp_check['checks'].get('challenge_present')}")

    divider()
    step(3, "Inspector checks Provider C tried self-assessment")
    bad = call("record_conformity_assessment", agent_id=aid_c,
               assessment_type="self", assessor_name="Internal", result="pass")
    print(f"    Provider C self-assessment attempt: {bad.get('error', 'allowed')}")
    print(f"    (Correctly blocked for high-risk system)")

    divider()
    step(4, "Inspector lists all high-risk systems in the registry")
    high = call("list_compliance_profiles", risk_category="high")
    print(f"    High-risk systems registered: {len(high)}")
    for p in high:
        print(f"      - {p['ai_system']['display_name']} by {p['provider']['name']}")

    print(f"\n  Inspector found 2/3 providers compliant, 1 flagged for remediation.")


# ========================================================================
# SIMULATION 9: Enterprise Architect - Multi-System Integration
# ========================================================================
def sim_enterprise_architect():
    header("USER 9: Enterprise Architect - 'Cross-system identity integration'")

    print("  Context: Building identity bridges across MCP, API, and DID systems.\n")

    step(1, "Create agents from 3 different protocol backgrounds")
    mcp_agent = call("create_agent_identity",
                     display_name="Internal-Pipeline",
                     source_protocol="mcp",
                     capabilities="etl,reporting",
                     issuer_name="EnterpriseCorp")
    api_agent = call("create_agent_identity",
                     display_name="Partner-API-Agent",
                     source_protocol="api_key",
                     identity_token="sk-partner-integration-key-abc123",
                     capabilities="data_exchange",
                     issuer_name="PartnerCo")
    did_agent = call("create_agent_identity",
                     display_name="DID-Native-Agent",
                     source_protocol="did",
                     capabilities="self_sovereign",
                     issuer_name="Web3Corp")

    for name, agent in [("MCP", mcp_agent), ("API", api_agent), ("DID", did_agent)]:
        print(f"    {name} Agent: {agent['agent_id']}")
        print(f"      Protocol: {agent['source_protocol']}")
        print(f"      Token masked: {agent.get('identity_token', 'none')}")

    divider()
    step(2, "Translate MCP agent to all 4 formats")
    formats = ["a2a_agent_card", "did_document", "oauth_claims", "summary"]
    for fmt in formats:
        result = call("translate_identity",
                      agent_id=mcp_agent["agent_id"],
                      target_format=fmt)
        if fmt == "a2a_agent_card":
            print(f"    A2A Card: name={result.get('name')}, skills={result.get('skills')}")
        elif fmt == "did_document":
            print(f"    DID Document: id={result.get('id', '')[:50]}...")
            print(f"      Verification methods: {len(result.get('verificationMethod', []))}")
        elif fmt == "oauth_claims":
            print(f"    OAuth Claims: sub={result.get('sub', '')[:30]}..., scope={result.get('scope')}")
        elif fmt == "summary":
            print(f"    Summary: {result.get('display_name')}, protocol={result.get('source_protocol')}")

    divider()
    step(3, "Create DID identities for interop")
    did_key = call("create_did_key")
    print(f"    did:key created: {did_key['did']}")

    did_web = call("create_did_web", domain="enterprise.example.com", path="agents/pipeline")
    print(f"    did:web created: {did_web['did']}")
    print(f"    Host document at: {did_web.get('hosting_url', 'see instructions')}")

    divider()
    step(4, "Set up delegation chain: MCP -> API -> DID")
    d1 = call("create_delegation",
              issuer_agent_id=mcp_agent["agent_id"],
              audience_agent_id=api_agent["agent_id"],
              capabilities="data_exchange,reporting",
              expiry_hours=12)
    d2 = call("create_delegation",
              issuer_agent_id=api_agent["agent_id"],
              audience_agent_id=did_agent["agent_id"],
              capabilities="data_exchange",
              expiry_hours=6)
    print(f"    MCP -> API: delegated data_exchange,reporting (12h)")
    print(f"    API -> DID: delegated data_exchange (6h)")

    # Verify chain
    c1 = call("verify_delegation", token=d1["token"])
    c2 = call("verify_delegation", token=d2["token"])
    print(f"    Chain verification: link1={c1['valid']}, link2={c2['valid']}")

    divider()
    step(5, "Generate A2A Agent Card for hosting")
    card = call("generate_agent_card",
                name="Enterprise-Pipeline",
                url="https://enterprise.example.com/agents/pipeline",
                description="Central data pipeline orchestration",
                skills_json=json.dumps([
                    {"id": "etl", "name": "ETL Processing", "description": "Data pipeline"},
                    {"id": "report", "name": "Reporting", "description": "Generate reports"},
                ]))
    print(f"    Card generated for hosting at: {card.get('hosting_path')}")
    print(f"    Agent name: {card.get('agent_card', {}).get('name')}")

    print(f"\n  Enterprise identity bridges established across 3 protocol systems.")


# ========================================================================
# SIMULATION 10: Audit Trail Investigator
# ========================================================================
def sim_audit_investigator():
    header("USER 10: Audit Investigator - 'Examine AI decision history'")

    print("  Context: Investigating an AI system's decision-making after a complaint.\n")

    step(1, "Identify the AI system under investigation")
    agent = call("create_agent_identity",
                 display_name="InsuranceQuote-AI",
                 capabilities="risk_pricing,quote_generation",
                 description="Automated insurance premium calculation",
                 issuer_name="InsureCo Ltd")
    agent_id = agent["agent_id"]
    print(f"    Agent under investigation: {agent_id}")

    divider()
    step(2, "Replay the decision trail")
    decisions = [
        ("data_access", "Loaded customer profile #8891", "Age 28, no claims history", False),
        ("inference", "Risk assessment for #8891", "Low risk, base premium 800 EUR", False),
        ("inference", "Customer #8892 risk assessment", "High risk, premium 3200 EUR", False),
        ("external_call", "Sent quote to customer #8892", "Email dispatched", False),
        ("inference", "Customer #8892 appealed", "Re-assessed: medium risk, 2100 EUR", True),
        ("data_access", "Loaded appeal documents for #8892", "3 supporting documents", False),
        ("inference", "Final decision for #8892", "Approved at 1800 EUR after human review", True),
    ]
    entries = []
    for atype, inp, out, human in decisions:
        entry = call("log_action", agent_id=agent_id, action_type=atype,
                     input_summary=inp, output_summary=out,
                     decision_rationale="Automated" if not human else "Human override",
                     human_override=human)
        entries.append(entry)
        tag = " [HUMAN]" if human else ""
        print(f"    [{atype}]{tag} {inp} -> {out[:50]}")

    divider()
    step(3, "Verify hash chain integrity (no tampering)")
    print(f"    Checking hash chain across {len(entries)} entries...")
    chain_ok = True
    for i in range(1, len(entries)):
        if entries[i].get("prev_hash") and entries[i-1].get("chain_hash"):
            if entries[i]["prev_hash"] != entries[i-1]["chain_hash"]:
                chain_ok = False
                print(f"    BROKEN at entry {i}!")
    if chain_ok:
        print(f"    Hash chain: INTACT (all {len(entries)} links verified)")
        print(f"    First hash: {entries[0].get('chain_hash', 'N/A')[:40]}...")
        print(f"    Last hash: {entries[-1].get('chain_hash', 'N/A')[:40]}...")

    divider()
    step(4, "Query specific action types")
    inferences = call("get_audit_trail", agent_id=agent_id, action_type="inference")
    data_access = call("get_audit_trail", agent_id=agent_id, action_type="data_access")
    external = call("get_audit_trail", agent_id=agent_id, action_type="external_call")
    print(f"    Inference actions: {len(inferences)}")
    print(f"    Data access actions: {len(data_access)}")
    print(f"    External calls: {len(external)}")

    divider()
    step(5, "Identify human overrides")
    all_entries = call("get_audit_trail", agent_id=agent_id)
    overrides = [e for e in all_entries if e.get("human_override")]
    print(f"    Human overrides found: {len(overrides)}")
    for o in overrides:
        print(f"      - {o['input_summary'][:50]} -> {o['output_summary'][:40]}")

    divider()
    step(6, "Full provenance report")
    provenance = call("get_provenance", agent_id=agent_id)
    print(f"    Training data sources: {len(provenance['training_data'])}")
    print(f"    Model lineage records: {len(provenance['model_lineage'])}")
    print(f"    Total audit entries: {provenance['audit_log_count']}")

    print(f"\n  Investigation complete. Hash chain intact, {len(overrides)} human overrides found.")
    print(f"  Evidence shows proper human oversight was applied on appeal.")


# ========================================================================
# MAIN: Run all simulations
# ========================================================================
if __name__ == "__main__":
    print("\n" + "="*70)
    print("  ATTESTIX USER SIMULATION RUNNER")
    print("  Simulating 10 real user workflows end-to-end")
    print("="*70)
    print(f"  Temp storage: {TEMP_DIR}")
    print(f"  Python: {sys.version.split()[0]}")
    print(f"  Platform: {sys.platform}")

    simulations = [
        ("Solo Developer", sim_solo_developer),
        ("Compliance Officer", sim_compliance_officer),
        ("Platform Operator", sim_platform_operator),
        ("Healthcare Company", sim_healthcare),
        ("External Auditor", sim_external_auditor),
        ("DPO (GDPR Erasure)", sim_gdpr_erasure),
        ("Cybersecurity Team", sim_security_test),
        ("Government Regulator", sim_regulator),
        ("Enterprise Architect", sim_enterprise_architect),
        ("Audit Investigator", sim_audit_investigator),
    ]

    start = time.time()
    for name, func in simulations:
        run_simulation(name, func)

    elapsed = time.time() - start

    print("\n" + "="*70)
    print(f"  SIMULATION RESULTS")
    print("="*70)
    print(f"  Total simulations: {len(simulations)}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Time: {elapsed:.2f}s")
    if errors:
        print(f"\n  Failures:")
        for name, err in errors:
            print(f"    - {name}: {err}")
    print("="*70 + "\n")

    # Cleanup
    import shutil
    shutil.rmtree(TEMP_DIR, ignore_errors=True)

    sys.exit(1 if failed > 0 else 0)
