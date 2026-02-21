# Examples

Runnable examples for every Attestix module. All examples work standalone after `pip install attestix`.

## 1. Create and Verify an Agent Identity

```python
from services.identity_service import IdentityService

svc = IdentityService()

# Create an agent identity
agent = svc.create_identity(
    display_name="DataAnalyzer",
    source_protocol="manual",
    capabilities=["data_analysis", "chart_generation", "report_writing"],
    description="Analyzes datasets and produces visual reports",
    issuer_name="Acme Analytics Inc.",
    expiry_days=365,
)

print(f"Agent ID: {agent['agent_id']}")
# attestix:f9bdb7a94ccb40f1
print(f"DID: {agent['issuer']['did']}")
# did:key:z6MkkQBTUzQDDXj2rj9N6bViEGZ7Yku5B5zQKpRHznWHPY3e
print(f"Signed: {bool(agent['signature'])}")
# True

# Verify the identity
result = svc.verify_identity(agent["agent_id"])
print(f"Valid: {result['valid']}")
# True
print(f"Checks: {result['checks']}")
# {'exists': True, 'not_revoked': True, 'not_expired': True, 'signature_valid': True}
```

## 2. Translate Identity to A2A Agent Card

Convert any Attestix identity to a Google A2A-compatible Agent Card for interoperability:

```python
from services.identity_service import IdentityService

svc = IdentityService()

agent = svc.create_identity(
    display_name="CustomerBot",
    source_protocol="manual",
    capabilities=["customer_support", "order_tracking", "faq"],
    description="Handles customer inquiries and order status",
    issuer_name="ShopCo",
)

# Convert to A2A Agent Card
card = svc.translate_identity(agent["agent_id"], target_format="a2a_agent_card")
print(card["name"])       # CustomerBot
print(card["skills"])     # [{id: "customer_support", ...}, ...]

# Convert to DID Document
did_doc = svc.translate_identity(agent["agent_id"], target_format="did_document")
print(did_doc["id"])      # did:key:z6Mk...

# Convert to OAuth claims
claims = svc.translate_identity(agent["agent_id"], target_format="oauth_claims")
print(claims["sub"])      # attestix:...
print(claims["scope"])    # customer_support order_tracking faq
```

## 3. Create DIDs

```python
from services.did_service import DIDService

svc = DIDService()

# Create an ephemeral did:key (no network needed)
did_key = svc.create_did_key()
print(f"DID: {did_key['did']}")
# did:key:z6MkkQBTUzQDDXj2rj9N6bViEGZ7Yku5B5zQKpRHznWHPY3e
print(f"Keypair ID: {did_key['keypair_id']}")
print(f"Public Key: {did_key['public_key_multibase']}")

# Create a did:web for self-hosting
did_web = svc.create_did_web(domain="agent.example.com", path="bots/analyzer")
print(f"DID: {did_web['did']}")
# did:web:agent.example.com:bots:analyzer
print(f"Host path: {did_web['hosting_path']}")
# /.well-known/did.json or /bots/analyzer/did.json

# Resolve any DID
doc = svc.resolve_did("did:key:z6MkkQBTUzQDDXj2rj9N6bViEGZ7Yku5B5zQKpRHznWHPY3e")
print(f"Resolved: {doc['id']}")
print(f"Verification methods: {len(doc['verificationMethod'])}")
```

## 4. UCAN Delegation Chains

Delegate capabilities from one agent to another with verifiable authority chains:

```python
from services.identity_service import IdentityService
from services.delegation_service import DelegationService

identity_svc = IdentityService()
delegation_svc = DelegationService()

# Create three agents with different roles
admin = identity_svc.create_identity(
    display_name="Admin",
    source_protocol="manual",
    capabilities=["user_management", "data_access", "reporting"],
    issuer_name="Corp HQ",
)

analyst = identity_svc.create_identity(
    display_name="DataAnalyst",
    source_protocol="manual",
    capabilities=["data_analysis"],
    issuer_name="Corp HQ",
)

reporter = identity_svc.create_identity(
    display_name="ReportBot",
    source_protocol="manual",
    capabilities=["report_generation"],
    issuer_name="Corp HQ",
)

# Admin delegates data_access to analyst (8-hour window)
delegation1 = delegation_svc.create_delegation(
    issuer_agent_id=admin["agent_id"],
    audience_agent_id=analyst["agent_id"],
    capabilities=["data_access"],
    expiry_hours=8,
)
print(f"Admin -> Analyst: {delegation1['delegation']['delegation_id']}")

# Verify the delegation
check = delegation_svc.verify_delegation(delegation1["token"])
print(f"Valid: {check['valid']}")
print(f"Capabilities: {check['payload']['att']}")
# ['data_access']

# Analyst chains delegation to reporter (must be subset of received capabilities)
delegation2 = delegation_svc.create_delegation(
    issuer_agent_id=analyst["agent_id"],
    audience_agent_id=reporter["agent_id"],
    capabilities=["data_access"],
    expiry_hours=4,
    parent_token=delegation1["token"],
)
print(f"Analyst -> Reporter: chained delegation created")

# List all delegations for the analyst
delegations = delegation_svc.list_delegations(
    agent_id=analyst["agent_id"],
    role="any",
)
print(f"Analyst's delegations: {len(delegations)}")
```

## 5. EU AI Act Compliance (Full Workflow)

Complete workflow for a high-risk medical AI system:

```python
from services.identity_service import IdentityService
from services.compliance_service import ComplianceService
from services.provenance_service import ProvenanceService
from services.credential_service import CredentialService

identity_svc = IdentityService()
compliance_svc = ComplianceService()
provenance_svc = ProvenanceService()
credential_svc = CredentialService()

# Step 1: Create agent identity
agent = identity_svc.create_identity(
    display_name="MedAssist-AI",
    source_protocol="manual",
    capabilities=["medical_diagnosis", "patient_triage"],
    description="AI-assisted medical diagnosis for radiology",
    issuer_name="HealthTech Corp.",
)
agent_id = agent["agent_id"]

# Step 2: Record training data (Article 10)
provenance_svc.record_training_data(
    agent_id=agent_id,
    dataset_name="PubMed Central Open Access",
    source_url="https://www.ncbi.nlm.nih.gov/pmc/tools/openftlist/",
    license="CC-BY-4.0",
    contains_personal_data=False,
    data_governance_measures="Peer-reviewed articles only. Bias review conducted.",
)

provenance_svc.record_training_data(
    agent_id=agent_id,
    dataset_name="MIMIC-IV Clinical Database",
    license="PhysioNet License 1.5.0",
    contains_personal_data=True,
    data_governance_measures="De-identified per HIPAA Safe Harbor. IRB approved.",
)

# Step 3: Record model lineage (Article 11)
provenance_svc.record_model_lineage(
    agent_id=agent_id,
    base_model="claude-opus-4-6",
    base_model_provider="Anthropic",
    fine_tuning_method="LoRA + RLHF with physician feedback",
    evaluation_metrics={
        "diagnostic_accuracy": 0.94,
        "sensitivity": 0.91,
        "specificity": 0.96,
    },
)

# Step 4: Create compliance profile
profile = compliance_svc.create_compliance_profile(
    agent_id=agent_id,
    risk_category="high",
    provider_name="HealthTech Corp.",
    intended_purpose="AI-assisted medical diagnosis in radiology",
    transparency_obligations="Discloses AI content. Shows confidence scores.",
    human_oversight_measures="Physician approval required for all diagnoses.",
)
print(f"Risk: {profile['risk_category']}")
print(f"Obligations: {len(profile['required_obligations'])}")

# Step 5: Gap analysis
status = compliance_svc.get_compliance_status(agent_id)
print(f"Completion: {status['completion_pct']}%")
print(f"Missing: {status.get('missing', [])}")

# Step 6: Conformity assessment (Article 43)
# Self-assessment is blocked for high-risk:
blocked = compliance_svc.record_conformity_assessment(
    agent_id=agent_id,
    assessment_type="self",
    assessor_name="Internal QA",
    result="pass",
)
print(f"Self-assessment blocked: {'error' in blocked}")  # True

# Third-party assessment:
assessment = compliance_svc.record_conformity_assessment(
    agent_id=agent_id,
    assessment_type="third_party",
    assessor_name="TUV Rheinland AG",
    result="pass",
    findings="Meets all Annex III requirements for medical AI.",
    ce_marking_eligible=True,
)

# Step 7: Generate declaration of conformity (Annex V)
declaration = compliance_svc.generate_declaration_of_conformity(agent_id)
print(f"Declaration: {declaration['declaration_id']}")

# Step 8: Verify final status
final = compliance_svc.get_compliance_status(agent_id)
print(f"Compliant: {final['compliant']}")    # True
print(f"Completion: {final['completion_pct']}%")  # 100.0

# Step 9: Get the auto-issued credential
creds = credential_svc.list_credentials(
    agent_id=agent_id,
    credential_type="EUAIActComplianceCredential",
)
if creds:
    v = credential_svc.verify_credential(creds[0]["id"])
    print(f"Compliance VC valid: {v['valid']}")  # True
```

## 6. W3C Verifiable Credentials

Issue, verify, revoke, and present credentials:

```python
from services.identity_service import IdentityService
from services.credential_service import CredentialService

identity_svc = IdentityService()
credential_svc = CredentialService()

# Create an agent
agent = identity_svc.create_identity(
    display_name="CertifiedBot",
    source_protocol="manual",
    capabilities=["certified_analysis"],
    issuer_name="CertAuthority",
)
agent_id = agent["agent_id"]

# Issue a custom credential
cred = credential_svc.issue_credential(
    subject_id=agent_id,
    credential_type="SecurityClearanceCredential",
    issuer_name="Federal Security Office",
    claims={
        "clearance_level": "secret",
        "department": "cyber_defense",
        "valid_until": "2027-01-01",
    },
)
cred_id = cred["id"]
print(f"Credential: {cred_id}")
print(f"Type: {cred['type']}")
print(f"Proof type: {cred['proof']['type']}")
# Ed25519Signature2020

# Verify the credential
result = credential_svc.verify_credential(cred_id)
print(f"Valid: {result['valid']}")

# Revoke it
credential_svc.revoke_credential(cred_id, reason="Clearance downgraded")

# Verify after revocation
result2 = credential_svc.verify_credential(cred_id)
print(f"Valid after revoke: {result2['valid']}")  # False

# Issue another credential for presentation
cred2 = credential_svc.issue_credential(
    subject_id=agent_id,
    credential_type="AgentIdentityCredential",
    issuer_name="CertAuthority",
    claims={"role": "analyst", "org": "Acme"},
)

# Bundle into a Verifiable Presentation for a specific verifier
vp = credential_svc.create_presentation(
    holder_id=agent_id,
    credential_ids=[cred2["id"]],
    audience_did="did:web:auditor.example.com",
    challenge="nonce-from-verifier-12345",
)
print(f"VP type: {vp['type']}")
print(f"Credentials in VP: {len(vp['verifiableCredential'])}")
```

## 7. Reputation Scoring

Track agent trustworthiness with recency-weighted scoring:

```python
from services.identity_service import IdentityService
from services.reputation_service import ReputationService

identity_svc = IdentityService()
reputation_svc = ReputationService()

# Create two agents
agent_a = identity_svc.create_identity(
    display_name="ReliableBot",
    source_protocol="manual",
    capabilities=["analysis"],
)

agent_b = identity_svc.create_identity(
    display_name="UnreliableBot",
    source_protocol="manual",
    capabilities=["analysis"],
)

# Record interactions for agent A (mostly successful)
for _ in range(10):
    reputation_svc.record_interaction(
        agent_id=agent_a["agent_id"],
        counterparty_id="attestix:system",
        outcome="success",
        category="data_quality",
    )

# Record interactions for agent B (mixed results)
for outcome in ["success", "failure", "failure", "partial", "failure"]:
    reputation_svc.record_interaction(
        agent_id=agent_b["agent_id"],
        counterparty_id="attestix:system",
        outcome=outcome,
        category="data_quality",
    )

# Compare scores
score_a = reputation_svc.get_reputation(agent_a["agent_id"])
score_b = reputation_svc.get_reputation(agent_b["agent_id"])

print(f"ReliableBot:   {score_a['trust_score']:.2f}")   # ~0.95+
print(f"UnreliableBot: {score_b['trust_score']:.2f}")   # ~0.30-0.40

# Query agents above a threshold
top_agents = reputation_svc.query_agents(min_score=0.8)
print(f"Agents above 0.8: {len(top_agents)}")
```

## 8. Audit Trail (Article 12)

Log every agent action with hash-chained tamper-evident entries:

```python
from services.identity_service import IdentityService
from services.provenance_service import ProvenanceService

identity_svc = IdentityService()
provenance_svc = ProvenanceService()

agent = identity_svc.create_identity(
    display_name="DiagnosticAI",
    source_protocol="manual",
    capabilities=["diagnosis"],
    issuer_name="Hospital Corp",
)
agent_id = agent["agent_id"]

# Log agent actions
provenance_svc.log_action(
    agent_id=agent_id,
    action_type="inference",
    input_summary="Chest X-ray image, patient age 45",
    output_summary="Suspected pneumonia, confidence 0.87",
    decision_rationale="Opacity in lower right lobe consistent with pneumonia",
    human_override=False,
)

provenance_svc.log_action(
    agent_id=agent_id,
    action_type="inference",
    input_summary="Follow-up CT scan, same patient",
    output_summary="Confirmed bacterial pneumonia",
    decision_rationale="CT confirms consolidation. Recommended antibiotic course.",
    human_override=True,  # Doctor reviewed and approved
)

provenance_svc.log_action(
    agent_id=agent_id,
    action_type="external_call",
    input_summary="Query drug interaction database",
    output_summary="No interactions found for prescribed antibiotics",
)

# Query the audit trail
trail = provenance_svc.get_audit_trail(agent_id=agent_id)
print(f"Total entries: {len(trail)}")

# Filter by action type
inferences = provenance_svc.get_audit_trail(
    agent_id=agent_id,
    action_type="inference",
)
print(f"Inference entries: {len(inferences)}")

# Each entry has a chain_hash linking to the previous entry
for entry in trail:
    print(f"  [{entry['action_type']}] {entry['input_summary'][:40]}...")
    print(f"    chain_hash: {entry.get('chain_hash', 'N/A')[:16]}...")
```

## 9. Agent Card Discovery

Discover and parse A2A agent cards from remote services:

```python
from services.agent_card_service import AgentCardService

svc = AgentCardService()

# Generate an agent card for hosting
card = svc.generate_agent_card(
    name="WeatherBot",
    url="https://weather.example.com",
    description="Provides real-time weather forecasts",
    skills=[
        {"id": "get_forecast", "name": "Get Forecast", "description": "Returns weather forecast"},
        {"id": "get_alerts", "name": "Get Alerts", "description": "Returns weather alerts"},
    ],
    version="2.1.0",
)
print(f"Card name: {card['name']}")
print(f"Skills: {len(card['skills'])}")
# Host this JSON at https://weather.example.com/.well-known/agent.json

# Parse an existing agent card
import json
parsed = svc.parse_agent_card(json.dumps(card))
print(f"Parsed: {parsed['name']}")
print(f"Capabilities: {parsed['capabilities']}")
```

## 10. Compliance Middleware Pattern

Wrap any agent with compliance checks and audit logging:

```python
from services.identity_service import IdentityService
from services.compliance_service import ComplianceService
from services.provenance_service import ProvenanceService


class AttestixMiddleware:
    """Compliance wrapper for any AI agent."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.compliance = ComplianceService()
        self.provenance = ProvenanceService()

    def check_compliance(self):
        """Call before processing. Raises if non-compliant."""
        status = self.compliance.get_compliance_status(self.agent_id)
        if not status.get("compliant"):
            missing = status.get("missing", [])
            raise RuntimeError(f"Non-compliant. Missing: {missing}")
        return True

    def log(self, action_type, input_summary, output_summary,
            rationale="", human_override=False):
        """Call after processing to record audit entry."""
        return self.provenance.log_action(
            agent_id=self.agent_id,
            action_type=action_type,
            input_summary=input_summary,
            output_summary=output_summary,
            decision_rationale=rationale,
            human_override=human_override,
        )


# Usage in your agent pipeline:
svc = IdentityService()
agent = svc.create_identity(
    display_name="MyAgent",
    source_protocol="manual",
    capabilities=["analysis"],
    issuer_name="Corp",
)

middleware = AttestixMiddleware(agent["agent_id"])

# Before processing
try:
    middleware.check_compliance()
except RuntimeError as e:
    print(f"Blocked: {e}")
    # Handle non-compliance (create profile, run assessment, etc.)

# After processing
middleware.log(
    action_type="inference",
    input_summary="User query about revenue trends",
    output_summary="Generated quarterly revenue chart",
    rationale="Time-series analysis of Q1-Q4 data",
)
```

## 11. MCP Client Integration

Connect to Attestix from any MCP client:

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    server = StdioServerParameters(
        command="python",
        args=["/path/to/attestix/main.py"],
    )

    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List all 47 tools
            tools = await session.list_tools()
            print(f"Tools available: {len(tools.tools)}")

            # Create an identity via MCP
            result = await session.call_tool(
                "create_agent_identity",
                arguments={
                    "display_name": "RemoteAgent",
                    "capabilities": "data_analysis,reporting",
                    "description": "Agent created via MCP client",
                    "issuer_name": "MyCorp",
                },
            )
            print(result.content)


asyncio.run(main())
```

## Running the Examples

All examples are also available as standalone scripts in the `examples/` directory:

```bash
git clone https://github.com/VibeTensor/attestix.git
cd attestix
pip install -r requirements.txt

python examples/01_basic_identity.py
python examples/02_full_compliance.py
python examples/03_delegation_chain.py
python examples/04_verifiable_credentials.py
python examples/05_audit_trail.py
```
