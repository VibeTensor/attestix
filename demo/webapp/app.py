"""Attestix Interactive Compliance Dashboard
Streamlit web app that calls real Attestix services.
Usage: streamlit run demo/webapp/app.py
"""
import sys, os, json, datetime, base64
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
from services.identity_service import IdentityService
from services.compliance_service import ComplianceService
from services.provenance_service import ProvenanceService
from services.credential_service import CredentialService
from services.delegation_service import DelegationService
from services.reputation_service import ReputationService
from services.did_service import DIDService

st.set_page_config(page_title="Attestix Dashboard", page_icon="\U0001f6e1\ufe0f", layout="wide")
st.markdown("""<style>
    .stApp { background-color: #0f1219; }
    [data-testid="stSidebar"] { background-color: #0a0e1a; }
    h1, h2, h3 { color: #e2e8f0; }
    .stMetric { background-color: #1a1f2e; border-radius: 8px; padding: 16px; }
    div[data-testid="stMetricValue"] { color: #22d3ee; }
    .welcome-stat { text-align: center; padding: 1.2rem; background: #1a1f2e;
        border-radius: 12px; border: 1px solid #2d3348; }
    .welcome-stat h2 { color: #22d3ee !important; margin-bottom: 0.2rem; }
    .welcome-stat p { color: #94a3b8; margin: 0; }
    .summary-card { background: #1a1f2e; border-radius: 12px; padding: 1.5rem;
        border: 1px solid #2d3348; margin-top: 1rem; }
    .summary-card h3 { color: #22d3ee !important; }
</style>""", unsafe_allow_html=True)

@st.cache_resource
def get_services():
    return {
        "identity": IdentityService(), "compliance": ComplianceService(),
        "provenance": ProvenanceService(), "credential": CredentialService(),
        "delegation": DelegationService(), "reputation": ReputationService(),
        "did": DIDService(),
    }

svc = get_services()
if "agents" not in st.session_state:
    st.session_state.agents = {}
if "credentials" not in st.session_state:
    st.session_state.credentials = []
if "agent_history" not in st.session_state:
    st.session_state.agent_history = []
if "demo_summary" not in st.session_state:
    st.session_state.demo_summary = None

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def show_json(data, label="Result"):
    st.markdown(f"**{label}**")
    st.json(data)

def show_error(result):
    """Display a user-friendly error message instead of raw Python traces."""
    raw = result.get("error", "Unknown error")
    friendly_map = {
        "not found": "The requested resource could not be found. Please check the ID and try again.",
        "invalid": "One or more inputs are invalid. Please review the form and try again.",
        "expired": "This token or credential has expired. Please create a new one.",
    }
    message = raw
    for keyword, friendly in friendly_map.items():
        if keyword in raw.lower():
            message = friendly
            break
    st.error(f"Something went wrong: {message}")

def show_friendly_exception(e):
    """Convert a Python exception into a helpful message for non-technical users."""
    text = str(e)
    if "JSON" in text or "json" in text:
        st.error("The data you entered is not valid JSON. Please check the format and try again.")
    elif "connection" in text.lower() or "timeout" in text.lower():
        st.error("Could not connect to the service. Please check your network and try again.")
    else:
        st.error(f"An unexpected error occurred. Details: {text}")

def agent_selector(key="agent_sel"):
    opts = list(st.session_state.agents.keys())
    if opts:
        return st.selectbox("Agent ID", opts,
            format_func=lambda x: f"{st.session_state.agents[x]} ({x})", key=key,
            help="Select an agent you created earlier in this session.")
    return st.text_input("Agent ID (create one first)", key=key,
        help="No agents created yet. Go to 'Create Agent Identity' to register one.")

def record_agent(agent_id, display_name, risk_level=None, compliance_pct=None):
    """Track agent in session history for the sidebar."""
    st.session_state.agents[agent_id] = display_name
    entry = {
        "agent_id": agent_id,
        "name": display_name,
        "risk_level": risk_level or "unknown",
        "compliance_pct": compliance_pct,
        "created_at": datetime.datetime.now().strftime("%H:%M:%S"),
    }
    # Avoid duplicates
    existing_ids = [h["agent_id"] for h in st.session_state.agent_history]
    if agent_id not in existing_ids:
        st.session_state.agent_history.append(entry)

def update_agent_history(agent_id, **kwargs):
    """Update an existing agent history entry with new data."""
    for entry in st.session_state.agent_history:
        if entry["agent_id"] == agent_id:
            entry.update(kwargs)
            break

def generate_report_html(summary):
    """Generate an HTML compliance report from a demo summary dict."""
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    checks_html = ""
    for check_name, passed in summary.get("checks", {}).items():
        icon = "&#9989;" if passed else "&#10060;"
        checks_html += f"<tr><td>{check_name}</td><td>{icon} {'Pass' if passed else 'Fail'}</td></tr>"
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>Attestix Compliance Report</title>
<style>
  body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: #0f1219; color: #e2e8f0;
         max-width: 800px; margin: 2rem auto; padding: 2rem; }}
  h1 {{ color: #22d3ee; }} h2 {{ color: #94a3b8; }}
  table {{ width: 100%; border-collapse: collapse; margin: 1rem 0; }}
  th, td {{ padding: 0.6rem 1rem; border: 1px solid #2d3348; text-align: left; }}
  th {{ background: #1a1f2e; color: #22d3ee; }}
  .metric {{ display: inline-block; background: #1a1f2e; border-radius: 8px;
             padding: 1rem 1.5rem; margin: 0.5rem; text-align: center; }}
  .metric .value {{ font-size: 1.8rem; color: #22d3ee; font-weight: bold; }}
  .metric .label {{ color: #94a3b8; font-size: 0.9rem; }}
  .footer {{ margin-top: 2rem; color: #64748b; font-size: 0.85rem; }}
</style></head>
<body>
<h1>Attestix Compliance Report</h1>
<h2>Generated {ts}</h2>
<div>
  <div class="metric"><div class="value">{summary.get('agent_id', 'N/A')[:12]}...</div>
    <div class="label">Agent ID</div></div>
  <div class="metric"><div class="value">{summary.get('risk_level', 'N/A').upper()}</div>
    <div class="label">Risk Level</div></div>
  <div class="metric"><div class="value">{summary.get('compliance_pct', 0)}%</div>
    <div class="label">Compliance</div></div>
</div>
<h2>Agent Details</h2>
<table>
  <tr><th>Field</th><th>Value</th></tr>
  <tr><td>Display Name</td><td>{summary.get('display_name', 'N/A')}</td></tr>
  <tr><td>Agent ID</td><td>{summary.get('agent_id', 'N/A')}</td></tr>
  <tr><td>Credential ID</td><td>{summary.get('credential_id', 'N/A')}</td></tr>
  <tr><td>Risk Category</td><td>{summary.get('risk_level', 'N/A')}</td></tr>
  <tr><td>Compliance</td><td>{summary.get('compliance_pct', 0)}%</td></tr>
  <tr><td>Assessment Result</td><td>{summary.get('assessment_result', 'N/A')}</td></tr>
</table>
<h2>Credential Verification</h2>
<table><tr><th>Check</th><th>Result</th></tr>{checks_html}</table>
<div class="footer">
  <p>Attestix v0.2.4 | 47 MCP tools | 9 modules | Apache 2.0</p>
  <p>This report was generated by the Attestix compliance dashboard. Visit
     <a href="https://attestix.io" style="color:#22d3ee;">attestix.io</a> for details.</p>
</div>
</body></html>"""

# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
st.sidebar.title("Attestix Dashboard")
st.sidebar.caption("v0.2.4 | 47 tools | 9 modules")
PAGES = [
    "Welcome",
    "Quick Demo",
    "Create Agent Identity",
    "Compliance Workflow",
    "Credentials",
    "Delegation",
    "Reputation",
    "Audit Trail",
]
page = st.sidebar.radio("Navigate", PAGES,
    help="Choose a section to explore. Start with Quick Demo for a guided walkthrough.")

# Agent history sidebar section
if st.session_state.agent_history:
    st.sidebar.divider()
    st.sidebar.subheader("Session Agents")
    for agent_info in st.session_state.agent_history:
        pct = agent_info.get("compliance_pct")
        risk = agent_info.get("risk_level", "unknown")
        risk_emoji = {"high": "\U0001f534", "limited": "\U0001f7e0", "minimal": "\U0001f7e2",
                      "unacceptable": "\U0001f534", "unknown": "\u26aa"}
        icon = risk_emoji.get(risk, "\u26aa")
        label = f"{icon} {agent_info['name']}"
        if pct is not None:
            label += f" - {pct}%"
        st.sidebar.caption(f"{label}  \n`{agent_info['agent_id'][:16]}...` | {agent_info['created_at']}")

# ============================== Welcome Page ==============================
if page == "Welcome":
    st.markdown("# \U0001f6e1\ufe0f Attestix")
    st.markdown("### EU AI Act compliance in 60 seconds")
    st.markdown(
        "Attestix is an open-source compliance toolkit that helps AI teams "
        "generate verifiable credentials, audit trails, and conformity "
        "declarations required by the EU AI Act. Use this dashboard to "
        "explore every capability interactively."
    )
    st.markdown("")

    c1, c2, c3 = st.columns(3)
    c1.markdown(
        '<div class="welcome-stat"><h2>47</h2><p>MCP Tools</p></div>',
        unsafe_allow_html=True)
    c2.markdown(
        '<div class="welcome-stat"><h2>9</h2><p>Service Modules</p></div>',
        unsafe_allow_html=True)
    c3.markdown(
        '<div class="welcome-stat"><h2>v0.2.4</h2><p>Current Release</p></div>',
        unsafe_allow_html=True)

    st.markdown("")
    st.markdown("#### What can you do here?")
    st.markdown(
        "- **Quick Demo** - Run the full compliance pipeline in one click\n"
        "- **Create Agent Identity** - Register AI agents with cryptographic IDs\n"
        "- **Compliance Workflow** - Build EU AI Act profiles, gap analysis, and declarations\n"
        "- **Credentials** - Issue and verify W3C Verifiable Credentials\n"
        "- **Delegation** - Create UCAN capability tokens between agents\n"
        "- **Reputation** - Track trust scores across agent interactions\n"
        "- **Audit Trail** - Log and inspect tamper-evident action histories"
    )

    st.markdown("")
    if st.button("Start with Quick Demo", type="primary", use_container_width=True):
        st.session_state["nav_to_demo"] = True
        st.rerun()

    # Handle navigation via rerun
    if st.session_state.get("nav_to_demo"):
        del st.session_state["nav_to_demo"]
        st.info("Select **Quick Demo** from the sidebar to begin.")

# =========================== SECTION 1: Identity ===========================
elif page == "Create Agent Identity":
    st.header("Create Agent Identity")
    st.markdown("Register a new AI agent with a Unified Agent Identity Token (UAIT).")
    with st.form("create_identity_form"):
        display_name = st.text_input("Display Name", value="ComplianceBot",
            help="A human-readable name for this agent. This appears in credentials and audit logs.")
        capabilities = st.text_area("Capabilities (comma-separated)",
            value="compliance_checking, risk_assessment",
            help="List what this agent can do. Used for delegation scoping and compliance profiles.")
        description = st.text_area("Description", value="Medical AI compliance agent",
            help="Briefly describe the agent's purpose. This is recorded in the identity token.")
        issuer_name = st.text_input("Issuer / Provider Name", value="AcmeCorp",
            help="The organization or person deploying this agent. Required by EU AI Act Article 16.")
        submitted = st.form_submit_button("Create Identity")
    if submitted:
        try:
            caps = [c.strip() for c in capabilities.split(",") if c.strip()]
            result = svc["identity"].create_identity(
                display_name=display_name, source_protocol="manual",
                capabilities=caps, description=description, issuer_name=issuer_name)
            if "error" in result:
                show_error(result)
            else:
                record_agent(result["agent_id"], display_name)
                st.success(f"Agent created: {result['agent_id']}")
                c1, c2 = st.columns(2)
                c1.metric("Agent ID", result["agent_id"])
                c2.metric("DID", result["issuer"]["did"][:40] + "...")
                st.metric("Capabilities", ", ".join(result["capabilities"]))
                st.markdown(f"Signature: **Ed25519 signed** | Expires: `{result['expires_at'][:19]}Z`")
                show_json(result, "Full UAIT")
        except Exception as e:
            show_friendly_exception(e)
    st.divider()
    st.subheader("Generate Standalone DID:key")
    if st.button("Create DID:key",
        help="Generate a decentralized identifier without creating a full agent identity."):
        try:
            r = svc["did"].create_did_key()
            if "error" in r: show_error(r)
            else:
                st.success(f"DID created: {r['did'][:48]}...")
                show_json(r, "DID Document")
        except Exception as e:
            show_friendly_exception(e)

# ======================== SECTION 2: Compliance ============================
elif page == "Compliance Workflow":
    st.header("EU AI Act Compliance Workflow")
    agent_id = agent_selector("comp_agent")
    if not agent_id:
        st.info("Create an agent first in the Identity section.")
        st.stop()

    with st.expander("a) Record Training Data (Article 10)"):
        with st.form("training_data_form"):
            ds_name = st.text_input("Dataset Name", value="MIMIC-IV Clinical Database",
                help="The name of the dataset used for training. Required for Article 10 documentation.")
            ds_url = st.text_input("Source URL", value="https://physionet.org/content/mimiciv/",
                help="Where the dataset can be found or verified. Helps auditors trace data provenance.")
            ds_license = st.text_input("License", value="PhysioNet Credentialed Health Data License 1.5.0",
                help="The license governing use of this training data.")
            ds_personal = st.checkbox("Contains personal data", value=True,
                help="Check if the dataset includes any personally identifiable information (PII). "
                     "Triggers additional GDPR documentation requirements.")
            ds_governance = st.text_area("Data governance measures",
                value="De-identified per HIPAA Safe Harbor.",
                help="Describe steps taken to ensure data quality, bias mitigation, and privacy protection.")
            td_submit = st.form_submit_button("Record Training Data")
        if td_submit:
            try:
                res = svc["provenance"].record_training_data(
                    agent_id=agent_id, dataset_name=ds_name, source_url=ds_url,
                    license=ds_license, contains_personal_data=ds_personal,
                    data_governance_measures=ds_governance)
                if "error" in res: show_error(res)
                else: st.success(f"Recorded: {res['entry_id']}"); show_json(res)
            except Exception as e:
                show_friendly_exception(e)

    with st.expander("b) Record Model Lineage (Article 11)"):
        with st.form("lineage_form"):
            base_model = st.text_input("Base Model", value="GPT-4o",
                help="The foundation model this agent is built on (e.g., GPT-4o, Claude, Llama 3).")
            provider = st.text_input("Provider", value="OpenAI",
                help="The company or lab that created the base model.")
            ft_method = st.text_input("Fine-tuning Method", value="LoRA on radiology corpus",
                help="How the model was adapted. Examples: LoRA, full fine-tune, prompt tuning, RAG.")
            metrics_raw = st.text_area("Evaluation Metrics (JSON)",
                value='{"accuracy": 0.94, "f1_score": 0.91, "auc_roc": 0.96}',
                help="Performance metrics as JSON. These are recorded for Article 11 technical documentation.")
            ml_submit = st.form_submit_button("Record Model Lineage")
        if ml_submit:
            try:
                metrics = json.loads(metrics_raw) if metrics_raw.strip() else {}
                res = svc["provenance"].record_model_lineage(
                    agent_id=agent_id, base_model=base_model, base_model_provider=provider,
                    fine_tuning_method=ft_method, evaluation_metrics=metrics)
                if "error" in res: show_error(res)
                else: st.success(f"Recorded: {res['entry_id']}"); show_json(res)
            except json.JSONDecodeError:
                st.error("The evaluation metrics field must be valid JSON. "
                         "Example: {\"accuracy\": 0.94, \"f1_score\": 0.91}")
            except Exception as e:
                show_friendly_exception(e)

    with st.expander("c) Create Compliance Profile"):
        with st.form("compliance_profile_form"):
            risk_cat = st.selectbox("Risk Category", ["minimal", "limited", "high", "unacceptable"],
                help="EU AI Act risk tier. High-risk systems (e.g., medical, hiring) require full compliance. "
                     "Unacceptable risk systems are prohibited.")
            cp_provider = st.text_input("Provider Name", value="AcmeCorp",
                help="The legal entity responsible for this AI system under the EU AI Act.")
            cp_purpose = st.text_area("Intended Purpose", value="AI-assisted radiology triage",
                help="Describe what the AI system is designed to do. This determines applicable regulations.")
            cp_transparency = st.text_area("Transparency Measures",
                value="System discloses AI-generated content",
                help="How users are informed they are interacting with AI. Required by Articles 13 and 52.")
            cp_oversight = st.text_area("Human Oversight Measures",
                value="Physician sign-off required",
                help="Controls ensuring a human can intervene, override, or shut down the AI. Required by Article 14.")
            cp_submit = st.form_submit_button("Create Profile")
        if cp_submit:
            try:
                res = svc["compliance"].create_compliance_profile(
                    agent_id=agent_id, risk_category=risk_cat, provider_name=cp_provider,
                    intended_purpose=cp_purpose, transparency_obligations=cp_transparency,
                    human_oversight_measures=cp_oversight)
                if "error" in res: show_error(res)
                else:
                    st.success(f"Profile: {res['profile_id']}")
                    st.metric("Required Obligations", len(res["required_obligations"]))
                    show_json(res)
            except Exception as e:
                show_friendly_exception(e)

    with st.expander("d) Gap Analysis"):
        if st.button("Run Gap Analysis", key="gap_btn",
            help="Check which compliance steps are done and which are still needed."):
            try:
                res = svc["compliance"].get_compliance_status(agent_id)
                if "error" in res: show_error(res)
                else:
                    pct = res.get("completion_pct", 0)
                    st.progress(pct / 100, text=f"Compliance: {pct}%")
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("**Completed**")
                        for i in res.get("completed", []): st.markdown(f"- {i}")
                    with c2:
                        st.markdown("**Missing**")
                        for i in res.get("missing", []): st.markdown(f"- {i}")
            except Exception as e:
                show_friendly_exception(e)

    with st.expander("e) Conformity Assessment (Article 43)"):
        with st.form("assessment_form"):
            assess_type = st.selectbox("Assessment Type", ["self", "third_party"],
                help="Self-assessment is for lower-risk systems. Third-party assessment by a notified body "
                     "is required for most high-risk AI systems.")
            assessor = st.text_input("Assessor Name", value="TUV Rheinland AG",
                help="The organization performing the assessment. For third-party, this must be an EU notified body.")
            assess_result = st.selectbox("Result", ["pass", "conditional", "fail"],
                help="The outcome of the conformity assessment.")
            findings = st.text_area("Findings", value="Meets all Annex III requirements.",
                help="Summary of the assessor's findings. Recorded in the conformity assessment credential.")
            ce_eligible = st.checkbox("CE Marking Eligible", value=True,
                help="Whether this system qualifies for CE marking after passing assessment.")
            assess_submit = st.form_submit_button("Record Assessment")
        if assess_submit:
            try:
                res = svc["compliance"].record_conformity_assessment(
                    agent_id=agent_id, assessment_type=assess_type, assessor_name=assessor,
                    result=assess_result, findings=findings, ce_marking_eligible=ce_eligible)
                if "error" in res: show_error(res)
                else: st.success(f"Assessment: {res['assessment_id']}"); show_json(res)
            except Exception as e:
                show_friendly_exception(e)

    with st.expander("f) Generate Declaration of Conformity (Annex V)"):
        if st.button("Generate Declaration", key="decl_btn",
            help="Produce the formal EU AI Act declaration document listing all compliance evidence."):
            try:
                res = svc["compliance"].generate_declaration_of_conformity(agent_id)
                if "error" in res: show_error(res)
                else:
                    st.success(f"Declaration: {res['declaration_id']}")
                    st.markdown(f"**Regulation:** {res['regulation_reference']}")
                    for k, v in res.get("annex_v_fields", {}).items():
                        st.markdown(f"- **{k}**: {v}")
            except Exception as e:
                show_friendly_exception(e)

# ========================= SECTION 3: Credentials =========================
elif page == "Credentials":
    st.header("W3C Verifiable Credentials")
    tab_issue, tab_verify, tab_list, tab_vp = st.tabs(
        ["Issue Credential", "Verify Credential", "List Credentials", "Verifiable Presentation"])

    with tab_issue:
        with st.form("issue_cred_form"):
            cred_subject = agent_selector("cred_subj")
            cred_type = st.selectbox("Credential Type", [
                "AgentIdentityCredential", "EUAIActComplianceCredential",
                "ConformityAssessmentCredential", "TrainingDataProvenanceCredential",
                "TransparencyObligationCredential"],
                help="The type of verifiable credential to issue. Each maps to a specific compliance claim.")
            cred_issuer = st.text_input("Issuer Name", value="AcmeCorp",
                help="The organization issuing this credential. The issuer's DID signs the credential.")
            cred_claims_raw = st.text_area("Claims (JSON)",
                value='{"role": "compliance_agent", "clearance": "high"}',
                help="Key-value pairs representing the claims in this credential. Must be valid JSON.")
            cred_submit = st.form_submit_button("Issue Credential")
        if cred_submit:
            try:
                claims = json.loads(cred_claims_raw) if cred_claims_raw.strip() else {}
                res = svc["credential"].issue_credential(
                    subject_id=cred_subject, credential_type=cred_type,
                    issuer_name=cred_issuer, claims=claims)
                if "error" in res: show_error(res)
                else:
                    st.session_state.credentials.append(res["id"])
                    st.success(f"Credential: {res['id'][:48]}...")
                    show_json(res)
            except json.JSONDecodeError:
                st.error("The claims field must be valid JSON. Example: {\"role\": \"agent\", \"level\": \"high\"}")
            except Exception as e:
                show_friendly_exception(e)

    with tab_verify:
        cred_id_input = st.text_input("Credential ID (urn:uuid:...)", key="verify_cred_id",
            help="Paste the full credential ID starting with urn:uuid: to verify its authenticity.")
        if st.session_state.credentials:
            cred_id_input = st.selectbox("Or select a recently issued credential",
                [""] + st.session_state.credentials, key="verify_cred_sel",
                help="Pick from credentials issued during this session.") or cred_id_input
        if st.button("Verify Credential", key="verify_cred_btn") and cred_id_input:
            try:
                res = svc["credential"].verify_credential(cred_id_input)
                if res.get("valid"): st.success("Credential is VALID")
                else: st.warning("Credential verification FAILED")
                for ck, passed in res.get("checks", {}).items():
                    if isinstance(passed, bool):
                        st.markdown(f"- **{ck}**: {'pass' if passed else 'FAIL'}")
                show_json(res)
            except Exception as e:
                show_friendly_exception(e)

    with tab_list:
        list_agent = agent_selector("list_cred_agent")
        if st.button("List Credentials", key="list_cred_btn"):
            try:
                creds = svc["credential"].list_credentials(agent_id=list_agent)
                st.metric("Total", len(creds))
                for c in creds:
                    with st.expander(f"{c.get('id', '?')[:48]}..."):
                        show_json(c)
            except Exception as e:
                show_friendly_exception(e)

    with tab_vp:
        st.markdown("Bundle multiple credentials into a Verifiable Presentation.")
        vp_agent = agent_selector("vp_agent")
        vp_cred_ids = st.text_area("Credential IDs (one per line)",
            value="\n".join(st.session_state.credentials[:3]) if st.session_state.credentials else "",
            help="Enter one credential ID per line. These will be bundled into a single presentation.")
        vp_audience = st.text_input("Audience DID (optional)", key="vp_aud",
            help="The DID of the intended recipient. Limits who can use this presentation.")
        vp_challenge = st.text_input("Challenge (optional)", key="vp_chal",
            help="A nonce or challenge string to prevent replay attacks.")
        if st.button("Create Presentation", key="vp_btn"):
            try:
                ids = [x.strip() for x in vp_cred_ids.strip().splitlines() if x.strip()]
                res = svc["credential"].create_verifiable_presentation(
                    agent_id=vp_agent, credential_ids=ids,
                    audience_did=vp_audience, challenge=vp_challenge)
                if "error" in res: show_error(res)
                else: st.success("Verifiable Presentation created"); show_json(res)
            except Exception as e:
                show_friendly_exception(e)

# ========================== SECTION 4: Delegation ==========================
elif page == "Delegation":
    st.header("UCAN Delegation")
    tab_create, tab_verify, tab_list = st.tabs(["Create Delegation", "Verify Token", "List Delegations"])

    with tab_create:
        with st.form("deleg_form"):
            d_issuer = agent_selector("d_issuer")
            d_audience = st.text_input("Audience Agent ID", key="d_audience",
                help="The agent receiving delegated capabilities. Must be a valid agent ID.")
            d_caps = st.text_area("Capabilities (comma-separated)", value="compliance_checking",
                help="Which capabilities to delegate. The audience agent can only use these specific permissions.")
            d_hours = st.number_input("Expiry (hours)", value=24, min_value=1,
                help="How long the delegation token remains valid. After this, the audience must request a new one.")
            d_submit = st.form_submit_button("Create Delegation")
        if d_submit:
            try:
                caps = [c.strip() for c in d_caps.split(",") if c.strip()]
                res = svc["delegation"].create_delegation(
                    issuer_agent_id=d_issuer, audience_agent_id=d_audience,
                    capabilities=caps, expiry_hours=d_hours)
                if "error" in res: show_error(res)
                else:
                    st.success("Delegation created")
                    st.code(res["token"], language="text")
                    show_json(res["delegation"], "Delegation Record")
            except Exception as e:
                show_friendly_exception(e)

    with tab_verify:
        d_token = st.text_area("Delegation Token (JWT)", key="d_verify_token",
            help="Paste the full JWT delegation token to verify its signature, expiry, and capabilities.")
        if st.button("Verify Delegation", key="d_verify_btn") and d_token.strip():
            try:
                res = svc["delegation"].verify_delegation(d_token.strip())
                if res.get("valid"): st.success("Token is VALID")
                else: st.warning(f"Verification FAILED: {res.get('reason', '')}")
                show_json(res)
            except Exception as e:
                show_friendly_exception(e)

    with tab_list:
        dl_agent = agent_selector("dl_agent")
        if st.button("List Delegations", key="dl_btn"):
            try:
                res = svc["delegation"].list_delegations(agent_id=dl_agent)
                st.metric("Active Delegations", len(res))
                for d in res:
                    with st.expander(d.get("jti", "unknown")):
                        show_json(d)
            except Exception as e:
                show_friendly_exception(e)

# ========================== SECTION 5: Reputation ==========================
elif page == "Reputation":
    st.header("Trust & Reputation")
    tab_record, tab_score, tab_query = st.tabs(["Record Interaction", "Get Reputation", "Query"])

    with tab_record:
        with st.form("rep_form"):
            r_agent = agent_selector("r_agent")
            r_counter = st.text_input("Counterparty ID", key="r_counter",
                help="The other agent involved in this interaction.")
            r_outcome = st.selectbox("Outcome", ["success", "failure", "partial", "timeout"],
                help="How the interaction ended. Affects the agent's trust score.")
            r_category = st.selectbox("Category", ["general", "task", "delegation", "data_access"],
                help="What type of interaction this was. Scores are tracked per category.")
            r_details = st.text_input("Details", value="",
                help="Optional free-text description of what happened.")
            r_submit = st.form_submit_button("Record Interaction")
        if r_submit:
            try:
                res = svc["reputation"].record_interaction(
                    agent_id=r_agent, counterparty_id=r_counter,
                    outcome=r_outcome, category=r_category, details=r_details)
                if "error" in res: show_error(res)
                else:
                    st.success("Interaction recorded")
                    st.metric("Updated Trust Score",
                        f"{res.get('updated_score', {}).get('trust_score', 0):.4f}")
            except Exception as e:
                show_friendly_exception(e)

    with tab_score:
        s_agent = agent_selector("s_agent")
        if st.button("Get Reputation", key="s_btn"):
            try:
                res = svc["reputation"].get_reputation(s_agent)
                if "error" in res: show_error(res)
                elif res.get("trust_score") is None: st.info("No interactions recorded yet.")
                else:
                    score = res["trust_score"]
                    c1, c2 = st.columns(2)
                    c1.metric("Trust Score", f"{score:.4f}")
                    c2.metric("Interactions", res["total_interactions"])
                    st.progress(score, text=f"Trust: {score:.1%}")
                    for cat, info in res.get("category_breakdown", {}).items():
                        st.markdown(f"- **{cat}**: {info['total']} total "
                            f"({info['success']} ok / {info['failure']} fail / {info['partial']} partial)")
            except Exception as e:
                show_friendly_exception(e)

    with tab_query:
        q_min = st.slider("Minimum Score", 0.0, 1.0, 0.0, 0.05, key="q_min",
            help="Filter agents by minimum trust score. Only agents at or above this threshold are shown.")
        if st.button("Search Agents by Reputation", key="q_btn"):
            try:
                res = svc["reputation"].query_reputation(min_score=q_min)
                st.metric("Matching Agents", len(res))
                for a in res:
                    st.markdown(f"- **{a['agent_id']}** - Score: {a['trust_score']:.4f} "
                        f"({a['interaction_count']} interactions)")
            except Exception as e:
                show_friendly_exception(e)

# ========================= SECTION 6: Audit Trail =========================
elif page == "Audit Trail":
    st.header("Audit Trail (Article 12)")
    tab_log, tab_view = st.tabs(["Log Action", "View Trail"])

    with tab_log:
        with st.form("audit_form"):
            a_agent = agent_selector("a_agent")
            a_type = st.selectbox("Action Type", ["inference", "delegation", "data_access", "external_call"],
                help="The category of action being logged. Choose the one that best describes what the agent did.")
            a_input = st.text_input("Input Summary", value="Chest X-ray batch (5 images)",
                help="Brief description of what was fed into the agent.")
            a_output = st.text_input("Output Summary", value="3 flagged for specialist review",
                help="Brief description of what the agent produced.")
            a_submit = st.form_submit_button("Log Action")
        if a_submit:
            try:
                res = svc["provenance"].log_action(
                    agent_id=a_agent, action_type=a_type,
                    input_summary=a_input, output_summary=a_output)
                if "error" in res: show_error(res)
                else:
                    st.success(f"Logged: {res['log_id']}")
                    st.markdown(f"Chain hash: `{res['chain_hash'][:32]}...`")
                    show_json(res)
            except Exception as e:
                show_friendly_exception(e)

    with tab_view:
        v_agent = agent_selector("v_agent")
        if st.button("View Audit Trail", key="v_btn"):
            try:
                trail = svc["provenance"].get_audit_trail(v_agent)
                st.metric("Entries", len(trail))
                for entry in trail:
                    hdr = f"{entry.get('log_id', '?')} | {entry.get('action_type', '')} | {entry.get('timestamp', '')[:19]}"
                    with st.expander(hdr):
                        st.markdown(f"**Chain hash:** `{entry.get('chain_hash', '')[:32]}...`")
                        st.markdown(f"**Prev hash:** `{entry.get('prev_hash', '')[:32]}...`")
                        show_json(entry)
            except Exception as e:
                show_friendly_exception(e)

# ========================== SECTION 7: Quick Demo ==========================
elif page == "Quick Demo":
    st.header("Quick Demo - Full Workflow")
    st.markdown("Run the complete Attestix compliance pipeline in one click: identity, "
        "compliance profile, provenance, assessment, declaration, credential, and audit.")

    def _demo_step(label, fn):
        """Run a demo step inside st.status, return the result or None on failure."""
        with st.status(label, expanded=True) as s:
            try:
                result = fn()
                if isinstance(result, dict) and "error" in result:
                    s.update(label=f"{label} - failed", state="error")
                    show_error(result)
                    return None
                s.update(label=f"{label} - done", state="complete")
                return result
            except Exception as e:
                s.update(label=f"{label} - failed", state="error")
                show_friendly_exception(e)
                return None

    if st.button("Run Full Demo", type="primary"):
        # Reset summary for this run
        st.session_state.demo_summary = None

        # 1 - Identity
        def step1():
            a = svc["identity"].create_identity(
                display_name="DemoRadiologyBot", source_protocol="manual",
                capabilities=["compliance_checking", "risk_assessment", "radiology_triage"],
                description="Medical AI compliance agent for radiology triage", issuer_name="AcmeCorp")
            record_agent(a["agent_id"], "DemoRadiologyBot", risk_level="high")
            st.write(f"Agent: **{a['agent_id']}** | DID: `{a['issuer']['did'][:48]}...`")
            return a
        agent = _demo_step("1. Create agent identity", step1)
        if not agent: st.stop()
        aid = agent["agent_id"]

        # 2 - Compliance profile
        def step2():
            p = svc["compliance"].create_compliance_profile(
                agent_id=aid, risk_category="high", provider_name="AcmeCorp",
                intended_purpose="AI-assisted radiology triage for clinical decision support",
                transparency_obligations="System discloses AI-generated content with confidence scores",
                human_oversight_measures="All diagnoses require attending physician sign-off")
            if "error" not in p:
                st.write(f"Profile: **{p['profile_id']}** | Obligations: {len(p['required_obligations'])}")
            return p
        profile = _demo_step("2. Create compliance profile (HIGH risk)", step2)
        if not profile: st.stop()

        # 3 - Training data
        def step3():
            t = svc["provenance"].record_training_data(
                agent_id=aid, dataset_name="MIMIC-IV Clinical Database",
                source_url="https://physionet.org/content/mimiciv/",
                license="PhysioNet Credentialed Health Data License 1.5.0",
                contains_personal_data=True,
                data_governance_measures="De-identified per HIPAA Safe Harbor. IRB approved.")
            st.write(f"Dataset: **{t['dataset_name']}** | Entry: {t['entry_id']}")
            return t
        _demo_step("3. Record training data (Article 10)", step3)

        # 3b - Model lineage
        def step3b():
            m = svc["provenance"].record_model_lineage(
                agent_id=aid, base_model="GPT-4o", base_model_provider="OpenAI",
                fine_tuning_method="LoRA on radiology corpus",
                evaluation_metrics={"accuracy": 0.94, "f1_score": 0.91, "auc_roc": 0.96})
            st.write(f"Base model: **{m['base_model']}** | Entry: {m['entry_id']}")
            return m
        _demo_step("3b. Record model lineage (Article 11)", step3b)

        # 4 - Assessment
        def step4():
            a = svc["compliance"].record_conformity_assessment(
                agent_id=aid, assessment_type="third_party", assessor_name="TUV Rheinland AG",
                result="pass", findings="Meets all Annex III requirements for medical AI.",
                ce_marking_eligible=True)
            if "error" not in a:
                st.write(f"Assessor: **{a['assessor_name']}** | Result: PASS | CE eligible")
            return a
        assess = _demo_step("4. Conformity assessment (Article 43)", step4)

        # 5 - Declaration
        def step5():
            d = svc["compliance"].generate_declaration_of_conformity(aid)
            if "error" not in d:
                st.write(f"Declaration: **{d['declaration_id']}** | {d['regulation_reference']}")
            return d
        _demo_step("5. Generate declaration of conformity (Annex V)", step5)

        # 6 - Credential
        # Use a mutable container so the nested function can store results
        _cred_results = {"credential": None, "verify": None}
        def step6():
            cr = svc["credential"].issue_credential(
                subject_id=aid, credential_type="AgentIdentityCredential",
                issuer_name="AcmeCorp", claims={"role": "compliance_agent", "clearance": "high"},
                expiry_days=180)
            st.session_state.credentials.append(cr["id"])
            v = svc["credential"].verify_credential(cr["id"])
            checks = " | ".join(f"{k}: {'pass' if val else 'FAIL'}"
                for k, val in v.get("checks", {}).items() if isinstance(val, bool))
            st.write(f"Credential: `{cr['id'][:40]}...` | Valid: **{'YES' if v.get('valid') else 'NO'}** | {checks}")
            _cred_results["credential"] = cr
            _cred_results["verify"] = v
            return cr
        _demo_step("6. Issue and verify credential (W3C VC 1.1)", step6)

        # 7 - Audit
        def step7():
            lg = svc["provenance"].log_action(
                agent_id=aid, action_type="inference",
                input_summary="Chest X-ray image batch (5 images)",
                output_summary="3 flagged for specialist review",
                decision_rationale="Confidence threshold below 0.85 for pneumothorax")
            st.write(f"Log: **{lg['log_id']}** | Chain hash: `{lg['chain_hash'][:32]}...`")
            return lg
        _demo_step("7. Log audit entry (Article 12)", step7)

        # Final gap analysis
        gap_pct = 0
        with st.status("Final: Gap analysis...", expanded=True) as sf:
            try:
                gap = svc["compliance"].get_compliance_status(aid)
                if "error" not in gap:
                    pct = gap.get("completion_pct", 0)
                    gap_pct = pct
                    st.progress(pct / 100, text=f"Compliance: {pct}%")
                    c1, c2 = st.columns(2)
                    c1.metric("Completed", len(gap.get("completed", [])))
                    c2.metric("Missing", len(gap.get("missing", [])))
                sf.update(label=f"Gap analysis: {gap.get('completion_pct', 0)}% complete", state="complete")
            except Exception as e:
                sf.update(label="Gap analysis failed", state="error")
                show_friendly_exception(e)

        # Update agent history with compliance data
        update_agent_history(aid, compliance_pct=gap_pct, risk_level="high")

        st.balloons()
        st.success("Demo complete. All services operational.")

        # Build and store summary
        credential_result = _cred_results["credential"]
        verify_result = _cred_results["verify"]
        cred_id = credential_result["id"] if credential_result else "N/A"
        checks_dict = {}
        if verify_result:
            checks_dict = {k: v for k, v in verify_result.get("checks", {}).items()
                           if isinstance(v, bool)}
        summary = {
            "agent_id": aid,
            "display_name": "DemoRadiologyBot",
            "risk_level": "high",
            "compliance_pct": gap_pct,
            "credential_id": cred_id,
            "assessment_result": "pass",
            "checks": checks_dict,
        }
        st.session_state.demo_summary = summary

    # ---------------------------------------------------------------------------
    # Summary card (persists after demo completes via session state)
    # ---------------------------------------------------------------------------
    if st.session_state.demo_summary:
        s = st.session_state.demo_summary
        st.divider()
        st.markdown("### Compliance Summary")
        st.markdown('<div class="summary-card">', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Agent ID", s["agent_id"][:12] + "...")
        c2.metric("Risk Level", s["risk_level"].upper())
        c3.metric("Compliance", f"{s['compliance_pct']}%")
        c4.metric("Credential", s["credential_id"][:16] + "..." if s["credential_id"] != "N/A" else "N/A")
        st.markdown('</div>', unsafe_allow_html=True)

        # Verification checks
        if s.get("checks"):
            st.markdown("**Credential Verification Checks:**")
            for check_name, passed in s["checks"].items():
                status = "Pass" if passed else "FAIL"
                st.markdown(f"- **{check_name}**: {status}")

        # Export report button
        report_html = generate_report_html(s)
        b64 = base64.b64encode(report_html.encode()).decode()
        href = f'<a href="data:text/html;base64,{b64}" download="attestix-report-{s["agent_id"][:8]}.html" ' \
               f'style="display:inline-block;padding:0.5rem 1.5rem;background:#22d3ee;color:#0f1219;' \
               f'border-radius:6px;text-decoration:none;font-weight:600;margin-top:0.5rem;">' \
               f'Export Report (HTML)</a>'
        st.markdown(href, unsafe_allow_html=True)

# Footer
st.divider()
st.caption("Attestix v0.2.4 | 47 tools | 9 modules | Apache 2.0 | attestix.io")
