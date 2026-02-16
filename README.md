# AURA Protocol

**Agent Unified Registry & Authentication Protocol**

The compliance identity layer for the EU AI Act era. AURA gives every AI agent a verifiable identity, proves its regulatory compliance, tracks its provenance, and scores its trustworthiness -- all locally, vendor-neutrally, and natively within MCP.

---

## Why This Exists

On **August 2, 2026**, the EU AI Act's transparency enforcement begins. Fines reach up to EUR 35M or 7% of global revenue. Every high-risk AI system deployed in EU markets must demonstrate compliance with Articles 10-12 (data governance, technical documentation, record-keeping), undergo conformity assessments (Article 43), and produce Annex V declarations of conformity.

The existing compliance tools -- Credo AI, Holistic AI, Vanta, IBM OpenPages -- all operate as **organizational dashboards**. They help a company document compliance internally. But none of them produce a **machine-readable, cryptographically verifiable proof** that an AI agent can present to another agent, regulator, or system.

Meanwhile, agent identity is fragmenting across walled gardens:
- **Microsoft Entra Agent ID** -- Azure-locked
- **AWS Bedrock AgentCore** -- AWS-locked
- **Google A2A** -- communication protocol, not identity/compliance
- **ERC-8004** -- requires Ethereum blockchain

No single tool combines **agent identity + EU AI Act compliance + verifiable credentials** in one protocol. AURA fills this gap.

---

## What AURA Does

AURA is an MCP server providing 36 tools across 8 modules:

### Phase 1 -- Identity & Trust (19 tools)

| Module | Tools | Purpose |
|--------|-------|---------|
| **Identity** | 7 | Unified Agent Identity Tokens (UAITs) bridging MCP OAuth, A2A, DIDs, and API keys |
| **Agent Cards** | 3 | Parse, generate, and discover Google A2A-compatible agent cards |
| **DID** | 3 | Create and resolve W3C Decentralized Identifiers (did:key, did:web) |
| **Delegation** | 3 | UCAN-style capability delegation with EdDSA-signed JWT tokens |
| **Reputation** | 3 | Recency-weighted trust scoring (0.0-1.0) with category breakdown |

### Phase 2 -- EU AI Act Compliance (17 tools)

| Module | Tools | Purpose |
|--------|-------|---------|
| **Compliance** | 6 | Risk categorization, conformity assessments (Article 43), Annex V declarations |
| **Credentials** | 6 | W3C Verifiable Credentials (VC Data Model 2.0) with Ed25519Signature2020 proofs |
| **Provenance** | 5 | Training data provenance (Article 10), model lineage (Article 11), audit trail (Article 12) |

---

## The Problem No One Else Solves

```
                Compliance Dashboards          Agent Identity Platforms
                (Credo AI, Vanta, etc.)        (Entra, AWS, Okta)
                         |                              |
                    Org-level only                  Vendor-locked
                    No machine proofs               No compliance
                    No agent identity               No VCs
                         |                              |
                         +--------- GAP ----------------+
                                     |
                              AURA Protocol
                         Agent-level compliance
                       Cryptographic VC proofs
                        Vendor-neutral DIDs
                     Works locally, no cloud dependency
```

### Competitive Gap Map

| Capability | Credo AI | Vanta | Okta | Entra | AWS | A2A | ERC-8004 | Dock.io | **AURA** |
|-----------|---------|-------|------|-------|-----|-----|----------|---------|---------|
| Agent Identity (DID) | - | - | - | - | - | - | On-chain | Yes | **Yes** |
| EU AI Act Compliance | Yes | Yes | - | - | - | - | - | - | **Yes** |
| W3C Verifiable Credentials | - | - | - | - | - | - | - | Yes | **Yes** |
| Compliance-as-a-VC | - | - | - | - | - | - | - | - | **Only AURA** |
| Reputation Scoring | - | - | - | - | - | - | On-chain | - | **Yes** |
| Delegation Chains | - | - | OAuth | OAuth | IAM | - | - | - | **UCAN** |
| Training Data Provenance | - | - | - | - | - | - | - | - | **Yes** |
| Model Lineage | - | - | - | - | - | - | - | - | **Yes** |
| Vendor Neutral | - | - | - | - | - | Yes | Yes | Partial | **Yes** |
| Works Offline | - | - | - | - | - | - | - | - | **Yes** |
| MCP Native | - | - | - | - | - | - | - | - | **Yes** |

---

## Architecture

```
aura-protocol/
  auth/
    crypto.py          # Ed25519 signing, did:key creation, signature verification
    token_parser.py    # Auto-detect JWT, DID, API key, URL tokens
  services/
    identity_service.py    # UAIT lifecycle (create, verify, translate, revoke)
    agent_card_service.py  # A2A Agent Card operations
    did_service.py         # DID resolution (did:key, did:web, Universal Resolver)
    delegation_service.py  # UCAN delegation token management
    reputation_service.py  # Recency-weighted trust scoring
    compliance_service.py  # EU AI Act profiles, assessments, declarations
    credential_service.py  # W3C VC issuance, verification, revocation
    provenance_service.py  # Training data, model lineage, audit trail
    cache.py               # Service instance cache with TTL
  tools/
    identity_tools.py      # 7 MCP tools
    agent_card_tools.py    # 3 MCP tools
    did_tools.py           # 3 MCP tools
    delegation_tools.py    # 3 MCP tools
    reputation_tools.py    # 3 MCP tools
    compliance_tools.py    # 6 MCP tools
    credential_tools.py    # 6 MCP tools
    provenance_tools.py    # 5 MCP tools
  config.py       # Storage paths, environment, defaults
  errors.py       # Centralized error handling with JSON logging
  main.py         # FastMCP server entry point
```

### Key Design Decisions

- **Ed25519 cryptography** -- Same algorithm used by Solana, Cosmos, SSH. Auto-generated keypair stored in `.signing_key.json`
- **JSON file storage** -- No database dependency. Files created lazily on first use
- **Lazy service initialization** -- Services instantiated on first tool call, cached with TTL
- **stderr-safe** -- All print() redirected to stderr to protect MCP JSON-RPC on stdout
- **Modular registration** -- Each tool module exposes a `register(mcp)` function

---

## Quick Start

### Prerequisites

```bash
pip install mcp[cli] cryptography base58 python-dotenv nest-asyncio python-json-logger httpx
```

### Run Standalone

```bash
python main.py
```

### Configure as MCP Server

Add to your Claude Code config (`~/.claude.json`):

```json
{
  "mcpServers": {
    "aura-protocol": {
      "type": "stdio",
      "command": "path/to/.venv/Scripts/python.exe",
      "args": ["path/to/aura-protocol/main.py"]
    }
  }
}
```

Restart Claude Code. You now have 36 AURA tools available.

---

## End-to-End Example: EU AI Act Compliance

This walkthrough takes a high-risk medical AI agent from zero to fully compliant.

### 1. Create Agent Identity

```
create_agent_identity(
  display_name="MedAssist-AI",
  capabilities="medical_diagnosis,patient_triage",
  description="AI-assisted medical diagnosis for clinical decision support",
  issuer_name="VibeTensor Inc."
)
--> agent_id: aura:f9bdb7a94ccb40f1
--> eu_compliance: null
```

### 2. Record Training Data Provenance (Article 10)

```
record_training_data(
  agent_id="aura:f9bdb7a94ccb40f1",
  dataset_name="PubMed Central Open Access",
  license="CC-BY-4.0",
  contains_personal_data=false,
  data_governance_measures="Peer-reviewed only, quality-checked"
)
```

### 3. Record Model Lineage (Article 11)

```
record_model_lineage(
  agent_id="aura:f9bdb7a94ccb40f1",
  base_model="claude-opus-4-6",
  base_model_provider="Anthropic",
  fine_tuning_method="LoRA + RLHF with physician feedback",
  evaluation_metrics_json='{"diagnostic_accuracy": 0.94}'
)
```

### 4. Create Compliance Profile

```
create_compliance_profile(
  agent_id="aura:f9bdb7a94ccb40f1",
  risk_category="high",
  provider_name="VibeTensor Inc.",
  intended_purpose="Medical diagnosis assistance",
  transparency_obligations="Discloses AI-generated content, provides confidence scores",
  human_oversight_measures="Physician approval required for all treatment recommendations"
)
--> 12 required obligations listed for high-risk
```

### 5. Check Compliance Status (Gap Analysis)

```
get_compliance_status(agent_id="aura:f9bdb7a94ccb40f1")
--> completion_pct: 75.0%
--> missing: ["conformity_assessment_passed", "declaration_of_conformity_issued"]
```

### 6. Record Conformity Assessment (Article 43)

High-risk systems require third-party assessment. Self-assessment is blocked:

```
record_conformity_assessment(
  agent_id="aura:f9bdb7a94ccb40f1",
  assessment_type="self", ...
)
--> ERROR: "High-risk AI systems require third_party conformity assessment (Article 43)."

record_conformity_assessment(
  agent_id="aura:f9bdb7a94ccb40f1",
  assessment_type="third_party",
  assessor_name="TUV Rheinland AG",
  result="pass",
  ce_marking_eligible=true
)
--> PASS
```

### 7. Generate Declaration of Conformity (Annex V)

```
generate_declaration_of_conformity(agent_id="aura:f9bdb7a94ccb40f1")
--> Annex V declaration with 10 required fields
--> Auto-issues EUAIActComplianceCredential (W3C Verifiable Credential)
```

### 8. Verify Full Compliance

```
get_compliance_status(agent_id="aura:f9bdb7a94ccb40f1")
--> compliant: true
--> completion_pct: 100.0%
--> eu_compliance: "comp:14f05fb98b20" (linked on UAIT)
```

### 9. Present Compliance to a Verifier

```
create_verifiable_presentation(
  agent_id="aura:f9bdb7a94ccb40f1",
  credential_ids="urn:uuid:7161cb5e-...",
  audience_did="did:web:eu-regulator.europa.eu"
)
--> Signed VP with embedded VCs, ready for cryptographic verification
```

---

## All 36 Tools Reference

<details>
<summary>Identity (7 tools)</summary>

| Tool | Description |
|------|-------------|
| `create_agent_identity` | Create a UAIT from any identity source |
| `resolve_identity` | Auto-detect token type and register |
| `verify_identity` | Check existence, revocation, expiry, signature |
| `translate_identity` | Convert to A2A, DID Document, OAuth, or summary |
| `list_identities` | List UAITs with protocol/revocation filters |
| `get_identity` | Get full UAIT details |
| `revoke_identity` | Mark a UAIT as revoked |

</details>

<details>
<summary>Agent Cards (3 tools)</summary>

| Tool | Description |
|------|-------------|
| `parse_agent_card` | Parse an A2A Agent Card JSON |
| `generate_agent_card` | Generate agent.json for hosting |
| `discover_agent` | Fetch /.well-known/agent.json from a URL |

</details>

<details>
<summary>DID (3 tools)</summary>

| Tool | Description |
|------|-------------|
| `create_did_key` | Generate ephemeral did:key with Ed25519 keypair |
| `create_did_web` | Generate did:web DID Document for self-hosting |
| `resolve_did` | Resolve any DID to its DID Document |

</details>

<details>
<summary>Delegation (3 tools)</summary>

| Tool | Description |
|------|-------------|
| `create_delegation` | UCAN-style capability delegation token |
| `verify_delegation` | Verify JWT signature, expiry, structure |
| `list_delegations` | List delegations by agent and role |

</details>

<details>
<summary>Reputation (3 tools)</summary>

| Tool | Description |
|------|-------------|
| `record_interaction` | Record outcome and update trust score |
| `get_reputation` | Get score with category breakdown |
| `query_reputation` | Search agents by reputation criteria |

</details>

<details>
<summary>Compliance (6 tools)</summary>

| Tool | Description |
|------|-------------|
| `create_compliance_profile` | Create EU AI Act profile with risk categorization |
| `get_compliance_profile` | Retrieve full compliance profile |
| `get_compliance_status` | Gap analysis: completed vs missing requirements |
| `record_conformity_assessment` | Record self or third-party assessment (Article 43) |
| `generate_declaration_of_conformity` | Generate Annex V declaration + auto-issue VC |
| `list_compliance_profiles` | Filter by risk category and compliance status |

</details>

<details>
<summary>Credentials (6 tools)</summary>

| Tool | Description |
|------|-------------|
| `issue_credential` | Issue W3C VC with Ed25519Signature2020 proof |
| `verify_credential` | Check signature, expiry, revocation |
| `revoke_credential` | Revoke a Verifiable Credential |
| `get_credential` | Get full VC details |
| `list_credentials` | Filter by agent, type, validity |
| `create_verifiable_presentation` | Bundle VCs into a signed VP for a verifier |

</details>

<details>
<summary>Provenance (5 tools)</summary>

| Tool | Description |
|------|-------------|
| `record_training_data` | Record training data source (Article 10) |
| `record_model_lineage` | Record model chain and evaluation metrics (Article 11) |
| `log_action` | Log agent action for audit trail (Article 12) |
| `get_provenance` | Get full provenance record |
| `get_audit_trail` | Query audit log with filters |

</details>

---

## Roadmap

### Phase 3 -- Blockchain Anchoring (Planned)

AURA's Ed25519 signatures can be anchored on-chain for tamper-proof verification without moving core operations to the blockchain.

| Off-Chain (Current) | On-Chain (Planned) |
|---------------------|-------------------|
| UAIT creation + signing | Hash anchor to Base L2 |
| W3C VC issuance | VC hash via Ethereum Attestation Service |
| Reputation scoring | Score summary on ERC-8004 registry |
| Audit trail | Merkle root of audit log |

Target chain: **Base (Ethereum L2)** -- sub-$0.01 gas costs, ERC-8004 compatibility, EAS support.

### Phase 4 -- Ecosystem Bridges (Planned)

- ERC-8004 Identity Registry adapter (UAIT <-> ERC-721)
- A2A Agent Card auto-sync
- ANS (Agent Name Service) resolution
- Polygon ID zero-knowledge credential support

---

## Security

- **Ed25519** signatures on all UAITs, VCs, assessments, declarations, and audit entries
- **did:key** identifiers derived from server signing key
- Signing key stored in `.signing_key.json` (excluded from git)
- No external API calls required for core operations
- All sensitive files excluded via `.gitignore`: `.env`, `.signing_key.json`, runtime data files

---

## License

Private. Contact VibeTensor Inc. for licensing inquiries.

---

Built by [VibeTensor](https://vibetensor.com)
