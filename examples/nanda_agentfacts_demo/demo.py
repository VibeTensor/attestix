"""Attestix x NANDA AgentFacts demo.

NANDA's AgentFacts schema defines trust fields that the index itself leaves
empty for tooling to populate: ``trust_certifications``, ``reputation_scores``,
and ``content_flags``. Attestix is that tooling. This self-contained script:

1. Creates an Attestix agent identity (a did:key).
2. Issues a signed W3C Verifiable Credential (a compliance attestation) and
   places it under AgentFacts ``trust_certifications``.
3. Derives ``content_flags`` from an Attestix EU AI Act compliance profile.
4. Records a few interactions and reads an Attestix reputation/trust score into
   AgentFacts ``reputation_scores``.
5. Assembles an AgentFacts document with those fields populated.
6. Offline-verifies the credential with the Attestix verifier, proving any
   third party (a regulator, another agent) can check the proof without
   trusting our server.

Run:
    python examples/nanda_agentfacts_demo/demo.py

Everything is local and uses Attestix's default file storage in a temp dir, so
the demo is reproducible and leaves no state behind.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

# Make the repo importable and isolate storage to a temp dir.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from attestix import config as _config

_tmp = Path(tempfile.mkdtemp(prefix="attestix-nanda-demo-"))
for _attr in (
    "IDENTITIES_FILE", "CREDENTIALS_FILE", "COMPLIANCE_FILE", "REPUTATION_FILE",
    "PROVENANCE_FILE", "DELEGATIONS_FILE", "AUDIT_FILE", "SIGNING_KEY_FILE",
):
    if hasattr(_config, _attr):
        setattr(_config, _attr, _tmp / getattr(_config, _attr).name)
_config.PROJECT_DIR = _tmp
_config.DATA_DIR = _tmp

from attestix.services.identity_service import IdentityService
from attestix.services.credential_service import CredentialService
from attestix.services.compliance_service import ComplianceService
from attestix.services.reputation_service import ReputationService


def main() -> None:
    identity = IdentityService()
    credentials = CredentialService()
    compliance = ComplianceService()
    reputation = ReputationService()

    print("=== 1. Create the agent identity (Attestix did:key) ===")
    agent = identity.create_identity(
        display_name="quarterly-analyst-v2",
        source_protocol="a2a",
        capabilities=["financial-analysis", "report-generation"],
        description="An autonomous analyst agent discoverable via NANDA.",
        issuer_name="VibeTensor",
    )
    agent_id = agent["agent_id"]
    print(f"   agent did: {agent_id}\n")

    print("=== 2. Issue a signed trust credential (AgentFacts trust_certifications) ===")
    vc = credentials.issue_credential(
        agent_id=agent_id,
        credential_type="EUAIActConformityCredential",
        issuer_name="VibeTensor (NB-0482 conformity)",
        claims={
            "framework": "EU AI Act",
            "risk_tier": "high",
            "annex": "Annex V Declaration of Conformity",
            "assessed": True,
        },
        expiry_days=365,
    )
    print(f"   credential id: {vc['id']}")
    print(f"   proof type:    {vc['proof']['type']}\n")

    print("=== 3. Derive content_flags from an Attestix compliance profile ===")
    content_flags = []
    profile = compliance.create_compliance_profile(
        agent_id=agent_id,
        risk_category="high",
        provider_name="VibeTensor",
        intended_purpose="Financial report generation for regulated filings.",
    )
    if "error" in profile:
        raise SystemExit(f"compliance profile failed: {profile['error']}")
    status = compliance.get_compliance_status(agent_id) or {}
    content_flags.append({
        "flag": "eu_ai_act_risk_category",
        "risk_category": status.get("risk_category", "high_risk"),
        "compliant": status.get("compliant"),
        "source": "attestix-compliance",
        "verifiable": True,
    })
    print(f"   content_flags: {content_flags}\n")

    print("=== 4. Record interactions and read an Attestix reputation score ===")
    for outcome in ("success", "success", "partial", "success"):
        reputation.record_interaction(
            agent_id=agent_id,
            counterparty_id="did:client:acme-fund",
            outcome=outcome,
            category="financial-analysis",
        )
    rep = reputation.get_reputation(agent_id) or {}
    reputation_scores = {
        "attestix_trust": rep.get("trust_score"),
        "total_interactions": rep.get("total_interactions"),
        "source": "attestix-reputation",
    }
    print(f"   reputation_scores: {reputation_scores}\n")

    print("=== 5. Assemble the AgentFacts document (Attestix-populated fields) ===")
    agent_facts = {
        "schema": "nanda/agentfacts/v1 (illustrative)",
        "agent_name": "quarterly-analyst-v2",
        "agent_id": agent_id,
        "capabilities": ["financial-analysis", "report-generation"],
        # Fields NANDA defines but leaves for tooling. Attestix fills them:
        "trust_certifications": [{
            "issuer": vc["issuer"]["id"],
            "type": vc["type"],
            "credential_id": vc["id"],
            "proof": vc["proof"]["type"],
            "credential": vc,
        }],
        "reputation_scores": reputation_scores,
        "content_flags": content_flags,
    }

    print("=== 6. Offline-verify the credential (no server trust required) ===")
    result = credentials.verify_credential_external(vc)
    print(f"   verified: {result.get('valid')}  checks: {result.get('checks')}\n")

    out = Path(__file__).parent / "sample_agentfacts.json"
    out.write_text(json.dumps(agent_facts, indent=2), encoding="utf-8")
    print(f"Wrote {out.name}. NANDA points to the agent; Attestix proves what it is.")

    if not result.get("valid"):
        raise SystemExit("verification failed")


if __name__ == "__main__":
    main()
