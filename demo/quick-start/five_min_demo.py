"""Attestix 5-Minute Demo

Shows the full Attestix capability set in under 2 minutes of runtime.
Covers: identity, compliance, provenance, credentials, delegation,
reputation, and audit trails.

Usage:
    python demo/quick-start/five_min_demo.py
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.identity_service import IdentityService
from services.compliance_service import ComplianceService
from services.provenance_service import ProvenanceService
from services.credential_service import CredentialService
from services.delegation_service import DelegationService
from services.reputation_service import ReputationService


# --- Color helpers (graceful fallback) ---

def _supports_color():
    """Check if the terminal supports ANSI colors."""
    if os.getenv("NO_COLOR"):
        return False
    if os.getenv("FORCE_COLOR"):
        return True
    if sys.platform == "win32":
        # Windows 10+ supports ANSI via VT100 mode
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            # Enable VT100 processing on stdout
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            return True
        except Exception:
            return False
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


USE_COLOR = _supports_color()


def c(code, text):
    """Wrap text in ANSI color if supported."""
    if not USE_COLOR:
        return text
    return f"\033[{code}m{text}\033[0m"


def bold(text):
    return c("1", text)


def green(text):
    return c("32", text)


def cyan(text):
    return c("36", text)


def yellow(text):
    return c("33", text)


def dim(text):
    return c("2", text)


def header(step, title):
    """Print a numbered step header."""
    print(f"\n  {bold(cyan(f'[{step}]'))} {bold(title)}")


def kv(key, value):
    """Print a key-value pair."""
    print(f"      {dim(key + ':')} {value}")


# --- Main demo ---

def main():
    start = time.time()

    print()
    print(f"  {bold('Attestix 5-Minute Demo')}")
    print(f"  {dim('Zero to compliant in 9 steps')}")

    # Initialize services
    identity_svc = IdentityService()
    compliance_svc = ComplianceService()
    provenance_svc = ProvenanceService()
    credential_svc = CredentialService()
    delegation_svc = DelegationService()
    reputation_svc = ReputationService()

    # ---- Step 1: Create agent identity ----
    header("1", "Create Agent Identity")
    agent = identity_svc.create_identity(
        display_name="ComplianceBot",
        source_protocol="manual",
        capabilities=["compliance_checking", "risk_assessment"],
        description="Medical AI compliance agent for radiology triage",
        issuer_name="AcmeCorp",
    )
    agent_id = agent["agent_id"]
    kv("Agent ID", agent_id)
    kv("DID", agent["issuer"]["did"][:48] + "...")
    kv("Capabilities", ", ".join(agent["capabilities"]))
    kv("Signature", green("Ed25519 signed"))

    # ---- Step 2: High-risk compliance profile ----
    header("2", "Create High-Risk Compliance Profile (Medical AI)")
    profile = compliance_svc.create_compliance_profile(
        agent_id=agent_id,
        risk_category="high",
        provider_name="AcmeCorp",
        intended_purpose="AI-assisted radiology triage for clinical decision support",
        transparency_obligations="System discloses AI-generated content with confidence scores",
        human_oversight_measures="All diagnoses require attending physician sign-off",
    )
    if "error" in profile:
        print(f"      {profile['error']}")
        return
    kv("Profile", profile["profile_id"])
    kv("Risk", yellow("HIGH") + dim(f" - {len(profile['required_obligations'])} obligations"))

    # ---- Step 3: Record training data ----
    header("3", "Record Training Dataset (Article 10)")
    training = provenance_svc.record_training_data(
        agent_id=agent_id,
        dataset_name="MIMIC-IV Clinical Database",
        source_url="https://physionet.org/content/mimiciv/",
        license="PhysioNet Credentialed Health Data License 1.5.0",
        data_categories=["clinical_records", "de_identified"],
        contains_personal_data=True,
        data_governance_measures="De-identified per HIPAA Safe Harbor. IRB approved.",
    )
    kv("Dataset", training["dataset_name"])
    kv("Personal data", yellow("yes") + dim(" (de-identified, IRB approved)"))
    kv("Entry", training["entry_id"])

    # ---- Step 4: Conformity assessment ----
    header("4", "Third-Party Conformity Assessment (Article 43)")
    assessment = compliance_svc.record_conformity_assessment(
        agent_id=agent_id,
        assessment_type="third_party",
        assessor_name="TUV Rheinland AG",
        result="pass",
        findings="System meets all Annex III requirements for medical AI.",
        ce_marking_eligible=True,
    )
    if "error" in assessment:
        print(f"      {assessment['error']}")
        return
    kv("Assessor", assessment["assessor_name"])
    kv("Result", green("PASS") + dim(" - CE marking eligible"))

    # ---- Step 5: Declaration of conformity ----
    header("5", "Generate Declaration of Conformity (Annex V)")
    declaration = compliance_svc.generate_declaration_of_conformity(agent_id)
    if "error" in declaration:
        print(f"      {declaration['error']}")
        return
    annex = declaration["annex_v_fields"]
    kv("Declaration", declaration["declaration_id"])
    kv("Regulation", declaration["regulation_reference"])
    kv("CE marking", green("eligible"))
    kv("Credential", green("auto-issued"))

    # ---- Step 6: Issue and verify a credential ----
    header("6", "Issue and Verify Credential (W3C VC 1.1)")
    cred = credential_svc.issue_credential(
        subject_id=agent_id,
        credential_type="AgentIdentityCredential",
        issuer_name="AcmeCorp",
        claims={"role": "compliance_agent", "clearance": "high"},
        expiry_days=180,
    )
    verification = credential_svc.verify_credential(cred["id"])
    kv("Credential", cred["id"][:40] + "...")
    kv("Proof", "Ed25519Signature2020")
    checks = verification.get("checks", {})
    status_parts = []
    for check_name, passed in checks.items():
        if isinstance(passed, bool):
            status_parts.append(green(check_name) if passed else f"FAIL:{check_name}")
    kv("Verification", " | ".join(status_parts))

    # ---- Step 7: Delegation ----
    header("7", "Create Agent and Delegate Capabilities (UCAN)")
    helper = identity_svc.create_identity(
        display_name="HelperBot",
        source_protocol="manual",
        capabilities=["data_collection"],
        issuer_name="AcmeCorp",
    )
    helper_id = helper["agent_id"]
    deleg = delegation_svc.create_delegation(
        issuer_agent_id=agent_id,
        audience_agent_id=helper_id,
        capabilities=["compliance_checking"],
        expiry_hours=24,
    )
    deleg_record = deleg["delegation"]
    deleg_verify = delegation_svc.verify_delegation(deleg["token"])
    kv("From", f"ComplianceBot -> HelperBot")
    kv("Delegated", ", ".join(deleg_record["capabilities"]))
    kv("Token", green("valid") if deleg_verify.get("valid") else "invalid")
    kv("Expires", deleg_record["expires_at"][:19] + "Z")

    # ---- Step 8: Reputation ----
    header("8", "Record Interactions and Compute Reputation")
    interactions = [
        ("success", "task", "Completed radiology scan analysis"),
        ("success", "delegation", "Delegated task finished on time"),
        ("partial", "task", "Triage completed with low confidence"),
    ]
    for outcome, category, details in interactions:
        reputation_svc.record_interaction(
            agent_id=agent_id,
            counterparty_id=helper_id,
            outcome=outcome,
            category=category,
            details=details,
        )
    rep = reputation_svc.get_reputation(agent_id)
    kv("Interactions", str(rep["total_interactions"]))
    score = rep["trust_score"]
    score_bar = int(score * 20) * "=" + (20 - int(score * 20)) * " "
    kv("Trust score", f"{score:.4f}  [{score_bar}]")
    breakdown = rep.get("category_breakdown", {})
    cats = [f"{cat}: {info['total']}" for cat, info in breakdown.items()]
    kv("Breakdown", ", ".join(cats))

    # ---- Step 9: Audit trail ----
    header("9", "Log Action and Show Audit Trail")
    log_entry = provenance_svc.log_action(
        agent_id=agent_id,
        action_type="inference",
        input_summary="Chest X-ray image batch (5 images)",
        output_summary="3 flagged for specialist review",
        decision_rationale="Confidence threshold below 0.85 for pneumothorax",
    )
    kv("Log ID", log_entry["log_id"])
    kv("Chain hash", log_entry["chain_hash"][:32] + "...")
    trail = provenance_svc.get_audit_trail(agent_id)
    kv("Trail length", str(len(trail)) + " entries (tamper-evident chain)")

    # ---- Summary ----
    elapsed = time.time() - start
    print()
    print(f"  {dim(f'Completed in {elapsed:.1f}s')}")
    print()
    print(f"  {bold('Attestix')}: 9 modules, 47 tools, zero to compliant in under 2 minutes.")
    print(f"  Learn more: {cyan('attestix.io')} | {cyan('pip install attestix')}")
    print()


if __name__ == "__main__":
    main()
