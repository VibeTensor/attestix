<!-- mcp-name: io.github.VibeTensor/attestix -->

<p align="center">
  <img src="https://raw.githubusercontent.com/VibeTensor/attestix/main/docs/assets/atx_icon.png" alt="Attestix" width="120" height="120" />
</p>

<h1 align="center">Attestix</h1>

<p align="center">
  <strong>Signed identity and evidence for AI agents</strong>
</p>

<p align="center">
  <a href="https://github.com/VibeTensor/attestix/actions/workflows/test.yml"><img src="https://img.shields.io/github/actions/workflow/status/VibeTensor/attestix/test.yml?branch=main&label=tests&style=flat-square" alt="CI"></a>
  <a href="https://github.com/VibeTensor/attestix/actions/workflows/lint.yml"><img src="https://img.shields.io/github/actions/workflow/status/VibeTensor/attestix/lint.yml?branch=main&label=lint&style=flat-square" alt="Lint"></a>
  <a href="https://github.com/VibeTensor/attestix/actions/workflows/security.yml"><img src="https://img.shields.io/github/actions/workflow/status/VibeTensor/attestix/security.yml?branch=main&label=security&style=flat-square" alt="Security"></a>
  <a href="https://codecov.io/gh/VibeTensor/attestix"><img src="https://img.shields.io/codecov/c/github/VibeTensor/attestix?style=flat-square" alt="Coverage"></a>
  <a href="https://pypi.org/project/attestix/"><img src="https://img.shields.io/pypi/v/attestix?color=4f46e5&style=flat-square" alt="PyPI"></a>
  <a href="https://pypi.org/project/attestix/"><img src="https://img.shields.io/pypi/pyversions/attestix?color=4f46e5&style=flat-square" alt="Python"></a>
  <a href="https://github.com/VibeTensor/attestix/blob/main/LICENSE"><img src="https://img.shields.io/github/license/VibeTensor/attestix?color=4f46e5&style=flat-square" alt="License"></a>
  <a href="https://attestix.io/docs"><img src="https://img.shields.io/badge/docs-attestix.io%2Fdocs-4f46e5?style=flat-square" alt="Docs"></a>
  <a href="https://attestix.io"><img src="https://img.shields.io/badge/website-attestix.io-4f46e5?style=flat-square" alt="Website"></a>
</p>

<p align="center">
  Record cryptographically verifiable evidence to support AI governance workflows.<br/>
  Open-source identity, credentials, compliance automation, and trust scoring.<br/>
  MCP and REST interfaces,
  Automated functional tests and Attestix interoperability benchmarks.<br/>
  Real integrations with LangChain, OpenAI Agents SDK, and CrewAI.
</p>

<p align="center">
  <em>Status: pre-1.0 toolkit; this README describes current main source.
  Single-maintainer project, community
  contributions welcome. No independent third-party security audit has been
  performed yet; deploy with the same diligence you would apply to any
  pre-1.0 open-source crypto stack.</em>
</p>

---

## Source and verification status

The readiness changes are released in Python `attestix` 0.4.2 on PyPI. The JavaScript offline verifier is also published as npm `attestix` 0.4.2. Main may contain later changes; compare release notes and pin the version you reviewed. Go and Java 0.4.2 are published. R and Rust have GitHub 0.4.2 releases, while CRAN and crates.io still serve 0.4.1 at this release cutoff.

- Credential verification binds the stated issuer to the supported proof controller. Ambiguous NFC-normalized keys fail before signing or verification.
- Presentation verification requires the caller's expected challenge and domain. A signature alone does not provide replay protection.
- REST use requires an API key by default. The default REST server is single-tenant and rejects non-default tenant headers; a shared API key does not provide cross-tenant authorization.
- JSON updates use the shared storage lock. Protect the local signing key and data directory; test backup restoration, isolation and your selected signer/backend before production.
- `workflow_complete` describes recorded documentation completion. `legal_conformity` is not assessed; the deprecated `compliant` field is a workflow alias. Generated declarations are drafts for provider review.
- Local purge cannot erase external replicas, remote logs, previously shared credentials or third-party backups. Plan historical data and credential migration separately.

## Install

```bash
# Reviewed release (check release notes before upgrading):
pip install attestix==0.4.2
```

> Since 0.4.0, the supported namespace is the canonical
> `attestix.*` namespace. The older flat layout (`from services... import`,
> `from auth... import`, ...) keeps working via thin deprecation shims that
> emit a `DeprecationWarning` on first import and are scheduled for removal in
> v0.5.0. Update imports to `from attestix.services... import` at your earliest
> convenience.

### CLI

```bash
attestix status                          # System overview
attestix init --name MyBot               # Create agent identity
attestix compliance <agent-id>           # Check recorded documentation gaps
attestix verify <agent-id>               # Verify identity cryptographically
attestix audit <agent-id>                # View hash-chained audit trail
attestix credential --list               # List W3C Verifiable Credentials
```

### REST API

```bash
pip install 'attestix[api]'
# Configure ATTESTIX_API_KEY in your environment before starting the API.
uvicorn attestix.api.main:app --reload   # Swagger docs at http://localhost:8000/docs
```

### Web Dashboard

```bash
pip install streamlit
streamlit run demo/webapp/app.py         # Opens at http://localhost:8501
```

### Quick Demo

```bash
python examples/quickstart.py            # Local synthetic workflow
```

## Verify in any language

Attestix credentials use a published canonical-JSON and Ed25519 verification profile.
Language-specific verifier repositories share conformance fixtures, but their trust-input
and delegation-chain checks differ. Read each verifier README and pin a reviewed version.
Cryptographic validity is separate from issuer trust, authorization, revocation and replay policy.

| Language | Install | Status |
|----------|---------|--------|
| **Python** | `pip install attestix==0.4.2` | PyPI 0.4.2 |
| **JS / TS** | `npm install attestix@0.4.2` | npm 0.4.2; verifier source ([attestix-js](https://github.com/VibeTensor/attestix-js)) |
| **Go** | `go get github.com/VibeTensor/attestix-go@v0.4.2` | Go module v0.4.2; verifier source ([attestix-go](https://github.com/VibeTensor/attestix-go)) |
| **Rust** | `cargo add attestix` | crates.io 0.4.1; GitHub v0.4.2 source ([attestix-rs](https://github.com/VibeTensor/attestix-rs)) |
| **Java** | Maven `com.vibetensor:attestix:0.4.2` | Maven 0.4.2; verifier source ([attestix-java](https://github.com/VibeTensor/attestix-java)) |
| **R** | See repository installation instructions | CRAN 0.4.1; GitHub 0.4.2 source ([attestix-r](https://github.com/VibeTensor/attestix-r)) |

Every verifier targets the Attestix canonical-JSON profile, which differs from strict [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785),
and Ed25519 signatures ([RFC 8032](https://www.rfc-editor.org/rfc/rfc8032)) against
the shared [`spec/verify/v1`](https://github.com/VibeTensor/attestix/tree/main/spec/verify/v1)
vectors. Verify in the browser at <https://attestix.io/verify>, or read the
bundle wire-format at <https://attestix.io/spec/bundle/v1>.

## Why Attestix

The EU AI Act has a staged application timeline. The European Commission currently lists
2 December 2027 for specified high-risk use cases and 2 August 2028 for high-risk systems
embedded in regulated products. Applicability depends on the system and the operator's role.
See the [European Commission's current AI Act guidance](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai).

Attestix helps organize evidence; a signature or generated declaration does not establish
legal conformity or replace the applicable assessment process.

Attestix provides agent identity, signed credentials, delegation, and offline verification
for developers who need portable evidence in their applications. Broader governance
platforms also offer APIs, SDKs, agent governance, and compliance workflows; evaluate
their current capabilities against your requirements.

Agent identity is fragmenting across walled gardens (Microsoft Entra, AWS AgentCore, ERC-8004). Attestix combines **agent identity, AI governance evidence and verifiable credentials** in one toolkit.

Attestix fills this gap.

---

## Modules

| Module | What it does |
|--------|-------------|
| **Identity** | Unified Agent Identity Tokens (UAITs) bridging MCP OAuth, A2A, DIDs, and API keys. local data erasure tooling |
| **Agent Cards** | Parse, generate, and discover A2A-compatible agent cards |
| **DID** | Create and resolve W3C Decentralized Identifiers (`did:key`, `did:web`) |
| **Delegation** | UCAN-style capability delegation with EdDSA-signed JWT tokens |
| **Reputation** | Recency-weighted trust scoring (0.0 - 1.0) with category breakdown |
| **Compliance** | EU AI Act risk profiles, conformity assessments (Article 43), Annex V declarations |
| **Credentials** | W3C Verifiable Credentials with Ed25519Signature2020 proofs, presentations |
| **Provenance** | Training data provenance (Article 10), model lineage (Article 11), hash-chained audit trail (Article 12) |
| **Blockchain** | Anchor artifact hashes to Base L2 via Ethereum Attestation Service, Merkle batching |

---

## Quick Start

### As an MCP Server (Claude Code)

Add to your Claude Code config (`~/.claude.json`):

```json
{
  "mcpServers": {
    "attestix": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "attestix.main"]
    }
  }
}
```

Then ask Claude:

> "Create an identity for my data analysis agent with capabilities: data_analysis, reporting"

### As a Python Library

```python
from attestix.services.identity_service import IdentityService
from attestix.services.compliance_service import ComplianceService
from attestix.services.credential_service import CredentialService

identity_svc = IdentityService()
compliance_svc = ComplianceService()
credential_svc = CredentialService()

# 1. Create an agent identity
agent = identity_svc.create_identity(
    display_name="MyAgent",
    source_protocol="manual",
    capabilities=["data_analysis", "reporting"],
    description="Analyzes quarterly financial data",
    issuer_name="VibeTensor",
    expiry_days=365,
)
agent_id = agent["agent_id"]      # attestix:f9bdb7a94ccb40f1
agent_did = agent["issuer"]["did"]  # did:key:z6Mk...

# 2. Create a compliance profile
profile = compliance_svc.create_compliance_profile(
    agent_id=agent_id,
    risk_category="limited",
    provider_name="VibeTensor",
    intended_purpose="Analyzes quarterly financial data",
)

# 3. Issue a verifiable credential
credential = credential_svc.issue_credential(
    subject_id=agent_id,
    credential_type="AgentIdentityCredential",
    issuer_name="VibeTensor",
    claims={"capabilities": ["data_analysis", "reporting"]},
    expiry_days=365,
)
print(credential["proof"]["type"])  # Ed25519Signature2020
```

For a complete end-to-end walkthrough covering all 9 modules, run the quickstart:

```bash
python examples/quickstart.py
```

### From Source

```bash
git clone https://github.com/VibeTensor/attestix.git
cd attestix
pip install -r requirements.txt
python -m attestix.main
```

---

## AI governance evidence workflow

Record a high-risk AI agent documentation workflow for provider review:

```
1. create_agent_identity        --> UAIT with DID (Ed25519 signed)
2. record_training_data         --> Article 10 data governance
3. record_model_lineage         --> Article 11 technical documentation
4. create_compliance_profile    --> Risk categorization + obligations
5. record_conformity_assessment --> Operator-recorded assessment details
6. generate_declaration_of_conformity --> Annex V declaration + W3C VC
7. create_verifiable_presentation     --> Signed VP for a verifier with a fresh challenge
```

The current Attestix workflow blocks self-assessment for a profile marked high-risk. This application policy is not a universal determination of the legally applicable assessment route:

```
record_conformity_assessment(assessment_type="self", ...)
--> ERROR: "High-risk AI systems require third_party conformity assessment"
```

Full walkthrough: [EU AI Act Compliance Guide](https://attestix.io/docs/guides/eu-ai-act-compliance)

---

## How It Works

Credentials and presentations carry signatures; audit chains carry integrity hashes.
Not every record or external artifact is independently signed:

| Artifact | Standard | Signed |
|----------|----------|--------|
| Agent Identity (UAIT) | Custom + DID | Ed25519 |
| Verifiable Credential | W3C VC Data Model 1.1 | Ed25519Signature2020 |
| Verifiable Presentation | W3C VP | Ed25519Signature2020 |
| Delegation Token | UCAN-style JWT | EdDSA |
| Draft evidence credential | Attestix documentation profile | Ed25519 |
| Audit Trail | Hash-chained log | SHA-256 chain |
| Blockchain Anchor | EAS on Base L2 | On-chain |

**Local operation.** Core identity and credential operations can use local JSON storage.
Remote DID resolution, hosted signers and blockchain integrations require their configured services.

---

## Architecture

```
attestix/                  # Canonical Python package (v0.4.0)
  main.py                  # MCP server entry point (MCP tools)
  cli.py                   # `attestix` console script
  config.py                # Environment-based configuration
  errors.py                # Error handling with JSON logging
  api/                     # FastAPI REST surface
    main.py                # uvicorn entry: `attestix.api.main:app`
    routers/               # REST routers
  auth/
    crypto.py              # Ed25519 key management
    ssrf.py                # SSRF protection for outbound HTTP
  services/
    identity_service.py    # UAIT lifecycle, local data erasure
    agent_card_service.py  # A2A agent card operations
    did_service.py         # DID creation and resolution
    delegation_service.py  # UCAN delegation tokens
    reputation_service.py  # Trust scoring
    compliance_service.py  # Operator-recorded profiles and assessment evidence
    credential_service.py  # W3C VCs and VPs
    provenance_service.py  # Training data, lineage, audit trail
    blockchain_service.py  # Base L2 anchoring via EAS
  storage/                 # Repository seam (file / memory / pg)
  signing/                 # Signer seam (in-process / kms)
  audit/                   # Tamper-evident event chain
  tenancy/                 # Tenant context
  idempotency/             # Stripe-style idempotency keys + middleware
  blockchain/
    merkle.py              # Merkle tree for batch anchoring
  tools/                   # MCP tool definitions (one file per module)
```

The pre-v0.4.0 flat layout (`services/`, `auth/`, `storage/`, ...) is
preserved as deprecation shims at the same paths. They re-export from the
canonical `attestix.*` namespace and emit a `DeprecationWarning` on first
import. The shims are scheduled for removal in v0.5.0.

---

## MCP tools

<details>
<summary><strong>Identity</strong></summary>

| Tool | Description |
|------|-------------|
| `create_agent_identity` | Create a UAIT from any identity source |
| `resolve_identity` | Auto-detect token type and register |
| `verify_identity` | Check existence, revocation, expiry, signature |
| `translate_identity` | Convert to A2A, DID Document, OAuth, or summary |
| `list_identities` | List UAITs with protocol/revocation filters |
| `get_identity` | Get full UAIT details |
| `revoke_identity` | Mark a UAIT as revoked |
| `purge_agent_data` | Remove locally managed records and parseable local backups; external copies need separate handling |

</details>

<details>
<summary><strong>Agent Cards</strong></summary>

| Tool | Description |
|------|-------------|
| `parse_agent_card` | Parse an A2A Agent Card JSON |
| `generate_agent_card` | Generate agent.json for hosting |
| `discover_agent` | Fetch `/.well-known/agent.json` from a URL |

</details>

<details>
<summary><strong>DID</strong></summary>

| Tool | Description |
|------|-------------|
| `create_did_key` | Generate ephemeral `did:key` with Ed25519 keypair |
| `create_did_web` | Generate `did:web` DID Document for self-hosting |
| `resolve_did` | Resolve any DID to its DID Document |

</details>

<details>
<summary><strong>Delegation</strong></summary>

| Tool | Description |
|------|-------------|
| `create_delegation` | UCAN-style capability delegation token |
| `verify_delegation` | Verify JWT signature, expiry, structure |
| `list_delegations` | List delegations by agent and role |
| `revoke_delegation` | Revoke a delegation token |

</details>

<details>
<summary><strong>Reputation</strong></summary>

| Tool | Description |
|------|-------------|
| `record_interaction` | Record outcome and update trust score |
| `get_reputation` | Get score with category breakdown |
| `query_reputation` | Search agents by reputation criteria |

</details>

<details>
<summary><strong>Compliance</strong></summary>

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
<summary><strong>Credentials</strong></summary>

| Tool | Description |
|------|-------------|
| `issue_credential` | Issue W3C VC with Ed25519Signature2020 proof |
| `verify_credential` | Check signature, expiry, revocation |
| `verify_credential_external` | Verify any VC JSON from an external source |
| `revoke_credential` | Revoke a Verifiable Credential |
| `get_credential` | Get full VC details |
| `list_credentials` | Filter by agent, type, validity |
| `create_verifiable_presentation` | Bundle VCs into a signed VP for a verifier |
| `verify_presentation` | Verify a VP with embedded credentials |

</details>

<details>
<summary><strong>Provenance</strong></summary>

| Tool | Description |
|------|-------------|
| `record_training_data` | Record training data source (Article 10) |
| `record_model_lineage` | Record model chain and metrics (Article 11) |
| `log_action` | Log agent action with hash-chained audit trail (Article 12) |
| `get_provenance` | Get full provenance record |
| `get_audit_trail` | Query audit log with filters |

</details>

<details>
<summary><strong>Blockchain</strong></summary>

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

## Standards Conformance

Public tests and conformance fixtures cover selected signature, canonicalization,
credential, delegation and interface behavior. They do not establish universal W3C
interoperability, legal conformity, certification or operating acceptance. Consult
the test cases and the selected verifier's documented boundaries.
Run them yourself:

```bash
docker build -f Dockerfile.test -t attestix-bench . && docker run --rm attestix-bench
```

| Standard | What is tested | Tests |
|----------|---------------|:-----:|
| **RFC 8032 (Ed25519)** | 4 IETF canonical vectors: key derivation, signature generation (exact match), verification, tamper rejection | 18 |
| **W3C VC Data Model 1.1** | Credential structure, Ed25519Signature2020 proof, mutable field exclusion, VP structure, replay protection | 25 |
| **W3C DID Core 1.0** | `did:key` and `did:web` document structure, roundtrip resolution, Ed25519VerificationKey2020 | 18 |
| **UCAN v0.9.0** | JWT header (alg/typ/ucv), all payload fields, capability attenuation, expiry enforcement, revocation | 18 |
| **MCP Protocol** | MCP tools registered, 9 modules, async convention, snake\_case naming | 5 |
| **Performance** | Ed25519 key gen, JSON canonicalization, sign/verify, identity creation, credential ops | 7 |

### Performance

Benchmark results depend on interpreter, hardware, storage and workload. Run the
repository benchmarks on your target environment; no static latency figure here is
an operating guarantee.

## Security

- **Ed25519** signatures on all UAITs, VCs, assessments, declarations, and audit entries
- **Hash-chained audit trail** with SHA-256 for tamper-evident logging
- **SSRF protection** blocks private IPs, metadata endpoints, and DNS rebinding
- **Encrypted key storage** with AES-256-GCM when `ATTESTIX_KEY_PASSWORD` is set
- Private keys never exposed in tool responses
- No external API calls required for core operations

---

## Research Paper

Attestix is described in a research paper covering system architecture, cryptographic pipeline, governance evidence workflows, and evaluation with 531 automated tests (440 functional + 91 RFC / W3C conformance benchmarks).

**[Attestix: A Unified Attestation Infrastructure for Autonomous AI Agents](https://github.com/VibeTensor/attestix/blob/main/paper/attestix-paper.pdf)**
Pavan Kumar Dubasi, VibeTensor Private Limited, 2026.

### Citing Attestix

If you use Attestix in your research, please cite:

```bibtex
@article{dubasi2026attestix,
  title     = {Attestix: A Unified Attestation Infrastructure for Autonomous AI Agents},
  author    = {Dubasi, Pavan Kumar},
  year      = {2026},
  url       = {https://github.com/VibeTensor/attestix},
  note      = {Open-source. Apache License 2.0}
}
```

---

## Documentation

Full documentation at **[attestix.io/docs](https://attestix.io/docs)**

| Guide | Description |
|-------|-------------|
| [Getting Started](https://attestix.io/docs/getting-started) | Installation and first identity in 5 minutes |
| [EU AI Act Compliance](https://attestix.io/docs/guides/eu-ai-act-compliance) | Step-by-step compliance workflow |
| [Risk Classification](https://attestix.io/docs/guides/risk-classification) | How to determine your AI system's risk category |
| [Architecture](https://attestix.io/docs/guides/architecture) | System design and data flows |
| [API Reference](https://attestix.io/docs/reference/api-reference) | MCP tools with parameter tables |
| [Integration Guide](https://attestix.io/docs/guides/integration-guide) | LangChain, OpenAI Agents SDK, CrewAI, MCP client |
| [Configuration](https://attestix.io/docs/reference/configuration) | Environment variables, storage, Docker |
| [Research Paper](https://attestix.io/docs/project/research) | Paper, citation formats, evaluation highlights |
| [Reputation Scoring](https://attestix.io/docs/guides/reputation) | Recency-weighted trust scoring and categories |
| [Examples](https://attestix.io/docs/examples) | End-to-end code examples for common workflows |

---

## Disclaimer

Attestix generates machine-readable, cryptographically signed compliance documentation. It is a documentation and evidence tooling system. **It does not replace legal counsel, notified body assessments, or official regulatory submissions.** Always consult qualified legal professionals for compliance decisions.

---

## Sponsors

Attestix is free and open-source. If you or your organization benefit from it, please consider sponsoring to support continued development, security audits, and infrastructure.

<a href="https://github.com/sponsors/VibeTensor"><img src="https://img.shields.io/badge/Sponsor-GitHub%20Sponsors-ea4aaa?style=flat-square&logo=github" alt="GitHub Sponsors" /></a>

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

Apache License 2.0. See [LICENSE](LICENSE).

---

<p align="center">
  <a href="https://vibetensor.com">
    <img src="https://raw.githubusercontent.com/VibeTensor/attestix/main/docs/assets/atx_gold.svg" alt="Attestix" width="48" />
  </a>
</p>

<p align="center">
  Built by <a href="https://vibetensor.com">VibeTensor</a>
</p>
