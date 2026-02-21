# Changelog

All notable changes to Attestix are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.2.1] - 2026-02-21

### Added
- 91 conformance benchmark test suite (`tests/benchmarks/`) validating standards claims:
  - RFC 8032 Section 7.1 Ed25519 canonical test vectors (4 IETF vectors, 18 tests)
  - W3C VC Data Model 1.1 conformance (credential structure, proof, presentations, 24 tests)
  - W3C DID Core 1.0 conformance (did:key, did:web, roundtrip resolution, 16 tests)
  - UCAN v0.9.0 conformance (JWT header, payload, attenuation, revocation, 16 tests)
  - MCP tool registration conformance (47 tools, 9 modules, naming, 5 tests)
  - Performance benchmarks with hard latency thresholds (7 tests)
- Standards Conformance section in README with measured performance numbers
- Running the Test Suite section in configuration docs
- FAQ entry on standards validation methodology

### Changed
- Total automated tests: 193 -> 284 (193 functional + 91 conformance benchmarks)
- Updated research paper evaluation section with conformance test results and measured latencies
- Updated all documentation (architecture, changelog, contributing, roadmap, FAQ) with benchmark details

## [0.2.0] - 2026-02-21

### Added

**Blockchain Anchoring (6 tools)**
- Blockchain module: anchor identity and credential hashes to Base L2 via Ethereum Attestation Service (EAS)
- Merkle batch anchoring for audit log entries (cost optimization)
- On-chain verification and anchor status queries
- Gas cost estimation before anchoring

**Security Enhancements**
- SSRF protection with private IP blocking, metadata endpoint blocking, and DNS rebinding prevention
- Hash-chained audit trail with SHA-256 chain hashes for tamper-evident logging
- Encrypted key storage with AES-256-GCM when `ATTESTIX_KEY_PASSWORD` is set
- GDPR Article 17 right to erasure via `purge_agent_data` across all data stores

**New Tools**
- `purge_agent_data` - Complete GDPR erasure across all 6 storage files
- `revoke_delegation` - Revoke delegation tokens
- `update_compliance_profile` - Update existing compliance profiles
- `verify_credential_external` - Verify any W3C VC JSON from external sources
- `verify_presentation` - Verify Verifiable Presentations with embedded credentials

**Testing**
- 284 automated tests (unit, integration, e2e, conformance benchmarks)
- 91 conformance benchmark tests validating standards compliance:
  - RFC 8032 Section 7.1 Ed25519 canonical test vectors (4 IETF vectors, 18 tests)
  - W3C VC Data Model 1.1 conformance (credential structure, proof, presentations, 24 tests)
  - W3C DID Core 1.0 conformance (did:key, did:web, roundtrip resolution, 16 tests)
  - UCAN v0.9.0 conformance (JWT header, payload, attenuation, revocation, 16 tests)
  - MCP tool registration conformance (47 tools, 9 modules, naming, 5 tests)
  - Performance benchmarks with hard latency thresholds (7 tests)
- 16 user persona test scenarios (cybersecurity, government regulator, legal, healthcare, DPO, enterprise architect)
- 10 manual workflow simulations with real tool output
- Docker containerized test runner (`Dockerfile.test`)
- AWS CodeBuild CI spec

### Changed
- Identity module: 7 -> 8 tools (added purge_agent_data)
- Delegation module: 3 -> 4 tools (added revoke_delegation)
- Compliance module: 6 -> 7 tools (added update_compliance_profile)
- Credentials module: 6 -> 8 tools (added verify_credential_external, verify_presentation)
- Total tools: 36 -> 47 across 9 modules

## [0.1.0] - 2026-02-19

Initial public release.

### Added

**Identity & Trust (19 tools)**
- Identity module (7 tools): create, resolve, verify, translate, list, get, revoke agent identities via Unified Agent Identity Tokens (UAITs)
- Agent Cards module (3 tools): parse, generate, and discover Google A2A-compatible agent cards
- DID module (3 tools): create did:key and did:web identifiers, resolve any DID via Universal Resolver
- Delegation module (3 tools): UCAN-style capability delegation with EdDSA-signed JWT tokens
- Reputation module (3 tools): recency-weighted trust scoring with category breakdown

**EU AI Act Compliance (17 tools)**
- Compliance module (6 tools): risk categorization (minimal/limited/high), conformity assessments (Article 43), Annex V declarations of conformity
- Credentials module (6 tools): W3C Verifiable Credentials (VC Data Model 1.1) with Ed25519Signature2020 proofs, Verifiable Presentations
- Provenance module (5 tools): training data provenance (Article 10), model lineage (Article 11), audit trail (Article 12)

**Infrastructure**
- Ed25519 cryptographic signing for all persistent records
- JSON file storage with file locking and corruption recovery
- Lazy service initialization with TTL cache
- MCP server via FastMCP with stderr-safe logging
- PyPI packaging via pyproject.toml

**Documentation**
- Getting Started guide
- EU AI Act Compliance workflow guide
- Risk Classification decision tree
- Concepts reference (UAIT, DID, VC, VP, UCAN, Ed25519)
- Complete API reference for all tools
- Integration guide (LangChain, CrewAI, AutoGen, MCP client)
- FAQ
- 5 runnable example scripts

### Security

- Private keys never returned in MCP tool responses (stored locally in .keypairs.json)
- Mutable fields (proof, credentialStatus) excluded from VC signature payloads
- High-risk systems blocked from self-assessment (requires third-party per Article 43)
- SSRF protection on agent discovery URLs
- All sensitive files excluded from git (.signing_key.json, .keypairs.json, .env)
