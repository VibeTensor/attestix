# Attestix

**AURA Protocol - Agent Unified Registry & Authentication Protocol**

The compliance identity layer for the EU AI Act era. Attestix gives every AI agent a verifiable identity, proves its regulatory compliance, tracks its provenance, and scores its trustworthiness. All locally, vendor-neutrally, and natively within MCP.

---

## Why This Exists

On **August 2, 2026**, the EU AI Act's transparency enforcement begins. Fines reach up to EUR 35M or 7% of global revenue. Every high-risk AI system deployed in EU markets must demonstrate compliance with Articles 10-12 (data governance, technical documentation, record-keeping), undergo conformity assessments (Article 43), and produce Annex V declarations of conformity.

The existing compliance tools (Credo AI, Holistic AI, Vanta, IBM OpenPages) all operate as **organizational dashboards**. They help a company document compliance internally. But none of them produce a **machine-readable, cryptographically verifiable proof** that an AI agent can present to another agent, regulator, or system.

Meanwhile, agent identity is fragmenting across walled gardens:
- **Microsoft Entra Agent ID** - Azure-locked
- **AWS Bedrock AgentCore** - AWS-locked
- **Google A2A** - communication protocol, not identity/compliance
- **ERC-8004** - requires Ethereum blockchain

No single tool combines **agent identity + EU AI Act compliance + verifiable credentials** in one protocol. Attestix fills this gap.

---

## What Attestix Does

Attestix is an MCP server providing **47 tools across 9 modules**:

### Identity & Trust (21 tools)

| Module | Tools | Purpose |
|--------|-------|---------|
| **Identity** | 8 | Unified Agent Identity Tokens (UAITs) bridging MCP OAuth, A2A, DIDs, and API keys. Includes GDPR Article 17 erasure |
| **Agent Cards** | 3 | Parse, generate, and discover Google A2A-compatible agent cards |
| **DID** | 3 | Create and resolve W3C Decentralized Identifiers (did:key, did:web) |
| **Delegation** | 4 | UCAN-style capability delegation with EdDSA-signed JWT tokens, revocation |
| **Reputation** | 3 | Recency-weighted trust scoring (0.0-1.0) with category breakdown |

### EU AI Act Compliance (20 tools)

| Module | Tools | Purpose |
|--------|-------|---------|
| **Compliance** | 7 | Risk categorization, conformity assessments (Article 43), Annex V declarations, profile updates |
| **Credentials** | 8 | W3C Verifiable Credentials (VC Data Model 1.1) with Ed25519Signature2020 proofs, external verification, Verifiable Presentations |
| **Provenance** | 5 | Training data provenance (Article 10), model lineage (Article 11), hash-chained audit trail (Article 12) |

### Blockchain Anchoring (6 tools)

| Module | Tools | Purpose |
|--------|-------|---------|
| **Blockchain** | 6 | Anchor artifact hashes to Base L2 via Ethereum Attestation Service (EAS), Merkle batch anchoring, cost estimation |

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
                              Attestix
                         Agent-level compliance
                       Cryptographic VC proofs
                        Vendor-neutral DIDs
                     Works locally, no cloud dependency
```

### Competitive Gap Map

| Capability | Credo AI | Vanta | Okta | Entra | AWS | A2A | ERC-8004 | Dock.io | **Attestix** |
|-----------|---------|-------|------|-------|-----|-----|----------|---------|---------|
| Agent Identity (DID) | - | - | - | - | - | - | On-chain | Yes | **Yes** |
| EU AI Act Compliance | Yes | Yes | - | - | - | - | - | - | **Yes** |
| W3C Verifiable Credentials | - | - | - | - | - | - | - | Yes | **Yes** |
| Compliance-as-a-VC | - | - | - | - | - | - | - | - | **Only Attestix** |
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
attestix/
  auth/
    crypto.py          # Ed25519 signing, did:key creation, signature verification
    ssrf.py            # SSRF protection for URL fetching (private IP blocking)
    token_parser.py    # Auto-detect JWT, DID, API key, URL tokens
  blockchain/
    merkle.py          # Merkle tree construction for batch anchoring
  services/
    identity_service.py    # UAIT lifecycle (create, verify, translate, revoke, purge)
    agent_card_service.py  # A2A Agent Card operations
    did_service.py         # DID resolution (did:key, did:web, Universal Resolver)
    delegation_service.py  # UCAN delegation token management
    reputation_service.py  # Recency-weighted trust scoring
    compliance_service.py  # EU AI Act profiles, assessments, Annex V declarations
    credential_service.py  # W3C VC issuance, verification, presentations
    provenance_service.py  # Training data, model lineage, hash-chained audit trail
    blockchain_service.py  # Base L2 anchoring via Ethereum Attestation Service
    cache.py               # Service instance cache with TTL
  tools/
    identity_tools.py      # 8 MCP tools (includes GDPR erasure)
    agent_card_tools.py    # 3 MCP tools
    did_tools.py           # 3 MCP tools
    delegation_tools.py    # 4 MCP tools
    reputation_tools.py    # 3 MCP tools
    compliance_tools.py    # 7 MCP tools
    credential_tools.py    # 8 MCP tools (includes external verification)
    provenance_tools.py    # 5 MCP tools
    blockchain_tools.py    # 6 MCP tools
  config.py       # Storage paths, environment, defaults
  errors.py       # Centralized error handling with JSON logging
  main.py         # FastMCP server entry point
```

### Key Design Decisions

- **Ed25519 cryptography** - Same algorithm used by Solana, Cosmos, SSH. Auto-generated keypair stored in `.signing_key.json`
- **JSON file storage** - No database dependency. Files created lazily on first use
- **Hash-chained audit trail** - SHA-256 chain hashes on every audit entry for tamper-evident logging
- **SSRF protection** - Private IP blocking on all URL-fetching operations (DID resolution, agent discovery)
- **Lazy service initialization** - Services instantiated on first tool call, cached with TTL
- **stderr-safe** - All print() redirected to stderr to protect MCP JSON-RPC on stdout
- **Modular registration** - Each tool module exposes a `register(mcp)` function

---

## Quick Start

### Install from PyPI

```bash
pip install attestix
```

Or install from source:

```bash
git clone https://github.com/VibeTensor/attestix.git
cd attestix
pip install -r requirements.txt
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
    "attestix": {
      "type": "stdio",
      "command": "python",
      "args": ["/path/to/attestix/main.py"]
    }
  }
}
```

Restart Claude Code. You now have 47 Attestix tools available.

### Run Examples

```bash
python examples/01_basic_identity.py        # Create and verify an agent identity
python examples/02_full_compliance.py        # Full EU AI Act compliance workflow
python examples/03_delegation_chain.py       # UCAN-style capability delegation
python examples/04_verifiable_credentials.py # W3C VC issuance and verification
python examples/05_audit_trail.py            # Article 12 audit logging
```

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
--> agent_id: attestix:f9bdb7a94ccb40f1
--> eu_compliance: null
```

### 2. Record Training Data Provenance (Article 10)

```
record_training_data(
  agent_id="attestix:f9bdb7a94ccb40f1",
  dataset_name="PubMed Central Open Access",
  license="CC-BY-4.0",
  contains_personal_data=false,
  data_governance_measures="Peer-reviewed only, quality-checked"
)
```

### 3. Record Model Lineage (Article 11)

```
record_model_lineage(
  agent_id="attestix:f9bdb7a94ccb40f1",
  base_model="claude-opus-4-6",
  base_model_provider="Anthropic",
  fine_tuning_method="LoRA + RLHF with physician feedback",
  evaluation_metrics_json='{"diagnostic_accuracy": 0.94}'
)
```

### 4. Create Compliance Profile

```
create_compliance_profile(
  agent_id="attestix:f9bdb7a94ccb40f1",
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
get_compliance_status(agent_id="attestix:f9bdb7a94ccb40f1")
--> completion_pct: 75.0%
--> missing: ["conformity_assessment_passed", "declaration_of_conformity_issued"]
```

### 6. Record Conformity Assessment (Article 43)

High-risk systems require third-party assessment. Self-assessment is blocked:

```
record_conformity_assessment(
  agent_id="attestix:f9bdb7a94ccb40f1",
  assessment_type="self", ...
)
--> ERROR: "High-risk AI systems require third_party conformity assessment (Article 43)."

record_conformity_assessment(
  agent_id="attestix:f9bdb7a94ccb40f1",
  assessment_type="third_party",
  assessor_name="TUV Rheinland AG",
  result="pass",
  ce_marking_eligible=true
)
--> PASS
```

### 7. Generate Declaration of Conformity (Annex V)

```
generate_declaration_of_conformity(agent_id="attestix:f9bdb7a94ccb40f1")
--> Annex V declaration with 10 required fields
--> Auto-issues EUAIActComplianceCredential (W3C Verifiable Credential)
```

### 8. Verify Full Compliance

```
get_compliance_status(agent_id="attestix:f9bdb7a94ccb40f1")
--> compliant: true
--> completion_pct: 100.0%
--> eu_compliance: "comp:14f05fb98b20" (linked on UAIT)
```

### 9. Present Compliance to a Verifier

```
create_verifiable_presentation(
  agent_id="attestix:f9bdb7a94ccb40f1",
  credential_ids="urn:uuid:7161cb5e-...",
  audience_did="did:web:eu-regulator.europa.eu"
)
--> Signed VP with embedded VCs, ready for cryptographic verification
```

---

## All 47 Tools Reference

<details>
<summary>Identity (8 tools)</summary>

| Tool | Description |
|------|-------------|
| `create_agent_identity` | Create a UAIT from any identity source |
| `resolve_identity` | Auto-detect token type and register |
| `verify_identity` | Check existence, revocation, expiry, signature |
| `translate_identity` | Convert to A2A, DID Document, OAuth, or summary |
| `list_identities` | List UAITs with protocol/revocation filters |
| `get_identity` | Get full UAIT details |
| `revoke_identity` | Mark a UAIT as revoked |
| `purge_agent_data` | GDPR Article 17 right to erasure across all stores |

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
<summary>Delegation (4 tools)</summary>

| Tool | Description |
|------|-------------|
| `create_delegation` | UCAN-style capability delegation token |
| `verify_delegation` | Verify JWT signature, expiry, structure |
| `list_delegations` | List delegations by agent and role |
| `revoke_delegation` | Revoke a delegation token |

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
<summary>Compliance (7 tools)</summary>

| Tool | Description |
|------|-------------|
| `create_compliance_profile` | Create EU AI Act profile with risk categorization |
| `get_compliance_profile` | Retrieve full compliance profile |
| `update_compliance_profile` | Update an existing compliance profile |
| `get_compliance_status` | Gap analysis: completed vs missing requirements |
| `record_conformity_assessment` | Record self or third-party assessment (Article 43) |
| `generate_declaration_of_conformity` | Generate Annex V declaration + auto-issue VC |
| `list_compliance_profiles` | Filter by risk category and compliance status |

</details>

<details>
<summary>Credentials (8 tools)</summary>

| Tool | Description |
|------|-------------|
| `issue_credential` | Issue W3C VC with Ed25519Signature2020 proof |
| `verify_credential` | Check signature, expiry, revocation (local credentials) |
| `verify_credential_external` | Verify any VC JSON from an external source |
| `revoke_credential` | Revoke a Verifiable Credential |
| `get_credential` | Get full VC details |
| `list_credentials` | Filter by agent, type, validity |
| `create_verifiable_presentation` | Bundle VCs into a signed VP for a verifier |
| `verify_presentation` | Verify a VP with embedded credentials |

</details>

<details>
<summary>Provenance (5 tools)</summary>

| Tool | Description |
|------|-------------|
| `record_training_data` | Record training data source (Article 10) |
| `record_model_lineage` | Record model chain and evaluation metrics (Article 11) |
| `log_action` | Log agent action with hash-chained audit trail (Article 12) |
| `get_provenance` | Get full provenance record |
| `get_audit_trail` | Query audit log with filters |

</details>

<details>
<summary>Blockchain (6 tools)</summary>

| Tool | Description |
|------|-------------|
| `anchor_identity` | Anchor identity hash to Base L2 via EAS |
| `anchor_credential` | Anchor credential hash to Base L2 via EAS |
| `anchor_audit_batch` | Merkle batch anchor of audit log entries |
| `verify_anchor` | Verify an on-chain anchor against local data |
| `get_anchor_status` | Get anchoring status for an artifact |
| `estimate_anchor_cost` | Estimate gas cost for anchoring |

</details>

---

## Roadmap

### Completed

- **Identity & Trust** - 21 tools for agent identity, DID, delegation, reputation, agent cards
- **EU AI Act Compliance** - 20 tools for risk profiles, conformity assessments, Annex V declarations, W3C VCs
- **Blockchain Anchoring** - 6 tools for Base L2 anchoring via EAS, Merkle batch anchoring
- **GDPR Compliance** - Article 17 right to erasure across all data stores
- **External Verification** - Third-party VP and credential verification without internal access
- **Hash-Chained Audit Trail** - Tamper-evident SHA-256 chain hashes on all audit entries
- **SSRF Protection** - Private IP blocking on DID resolution and agent discovery

### Next: Ecosystem Bridges

- ERC-8004 Identity Registry adapter (UAIT <-> ERC-721)
- A2A Agent Card auto-sync
- ANS (Agent Name Service) resolution
- Polygon ID zero-knowledge credential support

---

## Documentation

| Document | Description |
|----------|-------------|
| [Getting Started](docs/getting-started.md) | Installation and first identity in 5 minutes |
| [EU AI Act Compliance](docs/eu-ai-act-compliance.md) | Step-by-step compliance workflow |
| [Risk Classification](docs/risk-classification.md) | How to determine your AI system's risk category |
| [Concepts](docs/concepts.md) | UAIT, DID, VC, VP, UCAN, Ed25519 explained |
| [API Reference](docs/api-reference.md) | All 47 tools with full parameter tables |
| [Integration Guide](docs/integration-guide.md) | LangChain, CrewAI, AutoGen, MCP client patterns |
| [FAQ](docs/faq.md) | Common questions answered |

---

## Important Disclaimer

Attestix generates machine-readable, cryptographically signed compliance documentation for AI agents. It is a documentation and evidence tooling system.

**Attestix does not replace legal counsel, notified body assessments, or official regulatory submissions.** The declarations and artifacts produced by Attestix are structured evidence to support your compliance process, not legally binding regulatory filings on their own. Always consult qualified legal professionals for compliance decisions.

---

## Security

- **Ed25519** signatures on all UAITs, VCs, assessments, declarations, and audit entries
- **Hash-chained audit trail** with SHA-256 chain hashes for tamper-evident logging
- **SSRF protection** blocks private IPs, metadata endpoints, and DNS rebinding on all URL operations
- **did:key** identifiers derived from server signing key (multicodec 0xed01)
- **Encrypted key storage** with AES-256-GCM when `ATTESTIX_KEY_PASSWORD` is set
- Private keys never returned in tool responses (stored locally)
- Signing key stored in `.signing_key.json` (excluded from git)
- No external API calls required for core operations
- All sensitive files excluded via `.gitignore`: `.env`, `.signing_key.json`, `.keypairs.json`, runtime data files

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

---

## License

Apache License 2.0. See [LICENSE](LICENSE) for details.

---

Built by [VibeTensor](https://vibetensor.com)
