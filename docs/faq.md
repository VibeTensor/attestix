# Frequently Asked Questions

## General

### What is Attestix?

Attestix (Attestation Infrastructure for AI Agents) is an open-source tool that gives AI agents a verifiable identity, proves their regulatory compliance, and tracks their provenance. It runs as an MCP server or Python library with 47 tools across 9 modules.

### Who is Attestix for?

- **AI/ML engineers** building multi-agent systems who need agent-to-agent identity verification
- **Compliance teams** preparing for EU AI Act enforcement (August 2, 2026)
- **Platform builders** who need to prove their AI agents meet regulatory requirements
- **Researchers** exploring decentralized identity, verifiable credentials, and agent trust

### Is Attestix a replacement for legal compliance?

No. Attestix produces machine-readable, cryptographically signed compliance documentation. It does not replace legal counsel, notified body assessments, or official regulatory submissions. The artifacts it generates support your compliance process -they are not legally binding filings on their own.

### Does Attestix require a blockchain?

No. Attestix works entirely offline with local JSON storage. Blockchain anchoring (6 tools) is available as an optional feature for tamper-proof on-chain verification via Base L2 and Ethereum Attestation Service, but it is not required for any core functionality.

### Does Attestix require cloud services?

No. All core operations (identity creation, credential issuance, compliance profiling, audit logging) work locally without any external API calls. The only features that require network access are:
- `discover_agent` -fetches `/.well-known/agent.json` from a remote URL
- `resolve_did` with `did:web` -resolves via HTTPS
- `resolve_did` with non-key/web methods -uses the Universal Resolver

---

## Identity

### What is a UAIT?

A Unified Agent Identity Token. It is a digital passport for your AI agent containing its name, capabilities, description, issuer information, creation/expiry dates, and an Ed25519 cryptographic signature. See [Concepts](concepts.md#uait-unified-agent-identity-token) for details.

### Can I use Attestix identities with Google A2A?

Yes. Use `translate_identity(agent_id, target_format="a2a_agent_card")` to convert any UAIT into an A2A-compatible Agent Card JSON. You can also use `generate_agent_card` to create a standalone agent.json file for hosting.

### What happens if I lose my signing key?

The signing key in `.signing_key.json` is used to sign all UAITs, credentials, and audit entries. If you lose it:
- Existing signed artifacts remain valid (signatures can be verified by anyone with the public key)
- You will not be able to create new artifacts that chain to the same DID
- Generate a new key by deleting `.signing_key.json` and restarting Attestix

Keep `.signing_key.json` backed up securely. It is excluded from git by default.

### Can multiple Attestix instances share identities?

Yes, if they share the same `.signing_key.json` and JSON data files. Point multiple instances to the same data directory or use symlinks.

---

## EU AI Act Compliance

### When does the EU AI Act take effect?

- **August 2, 2026** -Enforcement begins for high-risk systems (Annex III) and Article 50 transparency obligations
- **August 2, 2027** -Obligations for AI in regulated products (Annex I: medical devices, machinery)

### How do I determine my risk category?

See the [Risk Classification Guide](risk-classification.md). In short:
- **Unacceptable** -Banned (social scoring, manipulation, etc.)
- **High** -Annex III categories (biometrics, employment, credit scoring, etc.)
- **Limited** -Interacts with people, generates synthetic content, or performs emotion recognition
- **Minimal** -Everything else (spam filters, code completion, etc.)

### Can high-risk systems use self-assessment?

Attestix currently requires third-party assessment for all high-risk systems. If you attempt `record_conformity_assessment` with `assessment_type="self"` on a high-risk agent, it will return an error. This is more conservative than the Act requires (which allows self-assessment for some Annex III categories) but errs on the side of compliance safety.

### What is an Annex V declaration?

The EU AI Act's Annex V specifies the required contents of a Declaration of Conformity. When you call `generate_declaration_of_conformity`, Attestix produces a structured document with all required fields and auto-issues a W3C Verifiable Credential as cryptographic proof.

### Can I update a compliance profile?

Yes. Use `update_compliance_profile` to modify an existing compliance profile's fields (intended purpose, transparency obligations, human oversight measures, etc.) without recreating the agent identity.

---

## Credentials

### What standard do Attestix credentials follow?

W3C Verifiable Credentials Data Model 1.1. Credentials use the `https://www.w3.org/2018/credentials/v1` context and `Ed25519Signature2020` proof type.

### Can Attestix credentials be verified by other systems?

Yes, if the verifying system supports Ed25519Signature2020 proofs. The public key is embedded in the credential's `verificationMethod` field as a DID. Any system that resolves the DID can verify the signature without contacting Attestix.

### What is a Verifiable Presentation?

A bundle of Verifiable Credentials presented to a specific verifier, with audience binding and replay protection. Use `create_verifiable_presentation` to bundle credentials for a regulator, partner, or auditor. See [Concepts](concepts.md#verifiable-presentation-vp) for details.

### Can I issue custom credential types?

Yes. The `credential_type` parameter accepts any string. Common types include:
- `EUAIActComplianceCredential` (auto-issued by `generate_declaration_of_conformity`)
- `AgentIdentityCredential`
- `TrainingDataProvenanceCredential`
- Any custom type you define

---

## Provenance

### What training data information should I record?

At minimum: dataset name, license, and whether it contains personal data. For high-risk systems, also include source URL, data categories, and data governance measures (quality checks, bias mitigation, cleaning processes). See the [compliance guide](eu-ai-act-compliance.md#step-2-record-training-data-provenance-article-10).

### How detailed should audit trail entries be?

Each `log_action` call records a single agent action. Include:
- `action_type`: What kind of action (inference, delegation, data_access, external_call)
- `input_summary`: What went in (keep concise -summaries, not raw data)
- `output_summary`: What came out
- `decision_rationale`: Why the agent made this decision (important for Article 14 human oversight)
- `human_override`: Whether a human intervened

For high-risk systems, Article 12 requires automatic logging of all events during operation. Log at least every inference and every external call.

---

## Technical

### How are the standards claims validated?

Attestix includes 91 conformance benchmark tests that run alongside the main test suite. These validate every standards claim against official specifications:

- **RFC 8032**: Ed25519 signatures verified against 4 IETF canonical test vectors (exact byte-level match)
- **W3C VC Data Model 1.1**: credential structure, Ed25519Signature2020 proof fields, mutable field exclusion, Verifiable Presentations with replay protection
- **W3C DID Core 1.0**: `did:key` and `did:web` document structure, roundtrip resolution, Ed25519VerificationKey2020 verification method
- **UCAN v0.9.0**: JWT header fields (alg=EdDSA, typ=JWT, ucv=0.9.0), capability attenuation, expiry enforcement, revocation
- **MCP**: all 47 tools registered, 9 modules, async interface, snake\_case naming

Run them yourself: `docker build -f Dockerfile.test -t attestix-bench . && docker run --rm attestix-bench`

### What cryptographic algorithm does Attestix use?

Ed25519 (EdDSA with Curve25519). The signing key is auto-generated on first run and stored in `.signing_key.json`. See [Concepts](concepts.md#ed25519) for why Ed25519 was chosen. The Ed25519 implementation is validated against all RFC 8032 Section 7.1 canonical test vectors.

### Where is data stored?

Six JSON files in the Attestix directory, plus two key files:

| File | Contents |
|------|----------|
| `identities.json` | Agent UAITs |
| `credentials.json` | Verifiable Credentials |
| `compliance.json` | Compliance profiles, assessments, declarations |
| `provenance.json` | Training data, model lineage, audit log |
| `reputation.json` | Interaction history and scores |
| `delegations.json` | Delegation tokens |
| `.signing_key.json` | Server Ed25519 signing key |
| `.keypairs.json` | Generated DID keypairs |

All files use file locking and atomic writes to prevent corruption.

### Is there a size limit for JSON storage?

No hard limit, but JSON files are loaded entirely into memory on each operation. For systems with thousands of agents or millions of audit entries, consider periodic archival. Database backend support is on the roadmap.

### Can I use Attestix without MCP?

Yes. Import the service classes directly in Python:

```python
from services.identity_service import IdentityService
svc = IdentityService()
agent = svc.create_identity(display_name="MyAgent")
```

### What Python version is required?

Python 3.10 or later.

### Does Attestix support Windows?

Yes. Attestix runs on Windows, macOS, and Linux. File locking uses the `filelock` library which is cross-platform.
