# Changelog

All notable changes to Attestix are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.3.0] - 2026-04-17

Security hardening release bundling seven previously merged but unreleased
pull requests (PR #45 through PR #51). The release ships a critical delegation
auth bypass fix, corrects Article 43 Annex III conformity logic, lands three
real framework integrations (LangChain, OpenAI Agents SDK, CrewAI), and adds
GitHub Actions CI/CD.

Minor version bump (0.2.5 -> 0.3.0) because the batch contains security
fixes, new public integration surfaces, and an Article 43 behavior change.
No breaking API changes for MCP tool callers.

### Security

- **CRITICAL: delegation chain auth bypass fixed** (PR #45). Parent tokens in
  a delegation chain are now fully verified and capability attenuation is
  strictly enforced. Previously a malicious delegate could craft a child
  token whose claimed capabilities exceeded those of the parent. Any
  long-lived delegation tokens issued prior to this release should be
  reviewed and re-issued.
- **SSRF hardening** (PR #47). Agent discovery, DID resolution, and credential
  fetch paths now go through the centralized SSRF guard (private IP blocking,
  metadata endpoint blocking, DNS rebind defense) on every outbound request.
- **Timing-safe comparisons** (PR #47). Signature and token equality checks
  switched to constant-time comparison (`hmac.compare_digest`) to remove a
  timing oracle on credential and delegation verification.
- **API error sanitization** (PR #47). Seven REST API router exception paths
  no longer leak stack traces, file paths, or internal type names to
  clients; errors are now structured and safe by default.

### Added

- **Real LangChain integration** (PR #42, released now). `integrations/langchain/`
  ships an actual `BaseCallbackHandler` subclass that logs every LLM, chain,
  and tool event into the Attestix audit trail. Replaces the previous
  example-only shim.
- **Real OpenAI Agents SDK integration** (PR #48). `integrations/openai_agents/`
  uses `MCPServerStdio` to connect the OpenAI Agents runtime directly to the
  Attestix MCP server, exposing all 47 tools as native agent capabilities.
- **Real CrewAI integration** (PR #51). `integrations/crewai/` uses
  `MCPServerAdapter` so CrewAI crews can load Attestix tools the same way
  they load any other MCP toolset.

### Fixed

- **Article 43 Annex III conformity assessment correctness** (PR #46). The
  compliance service now differentiates between Annex III categories when
  deciding whether self-assessment is permitted versus notified-body
  assessment being required. High-risk systems covered by Annex III point 1
  (biometrics) and similar categories are blocked from self-assessment per
  the Act.
- **EAS schema UID derivation** (PR #50). On-chain schema UID is now derived
  using the exact encoding EAS itself uses (schema string, resolver address,
  revocable flag), matching anchors created on-chain with anchors looked up
  on-chain. Previously mismatched schema UIDs could cause
  `isAttestationValid` lookups to miss.
- **Attested event decoding hardened** (PR #50). `_extract_attestation_uid`
  now prefers web3.py's ABI-level `events.Attested().process_log` and falls
  back to a topic-signature match on `keccak("Attested(address,address,bytes32,bytes32)")`.
  Removes reliance on fragile byte offsets when reading receipt logs.
- **Test mock log shape** (this release). `tests/conftest.py`
  `blockchain_service_mock` now emits an Attested-event-shaped log with the
  correct topic[0] signature so the hardened decoder path is exercised end
  to end in CI.

### Infrastructure

- **GitHub Actions CI/CD** (PR #49). New `.github/workflows/` pipelines run
  a pytest matrix (Python 3.10, 3.11, 3.12, 3.13) on pull requests, plus
  `ruff`, `mypy`, `bandit`, and `pip-audit` jobs. A separate release
  workflow publishes to PyPI on tag push when `PYPI_API_TOKEN` is set as a
  repo secret.
- **pytest plugin compatibility** (this release). Default `addopts` now
  includes `-p no:logfire` so that transitive installs of
  `opentelemetry-sdk` (pulled via CrewAI) do not abort collection with
  `ImportError: cannot import name 'ReadableLogRecord'` when the installed
  `logfire` version targets a different otel ABI.

## [0.2.3] - 2026-02-27

### Added
- **Namespace package support**: Added `attestix` namespace package for cleaner imports
  - New import pattern: `from attestix.services.identity_service import IdentityService`
  - New import pattern: `from attestix.auth.crypto import generate_ed25519_keypair`
  - Flat imports still work for backward compatibility: `from services.identity_service import IdentityService`

### Changed
- Package structure now includes both flat modules and `attestix.*` namespace
- Updated pyproject.toml to include attestix namespace packages

### Fixed
- Replaced wildcard imports with explicit named imports and `__all__` declarations across all namespace shim modules
- Consistent relative imports in `attestix/auth/__init__.py` and `attestix/blockchain/__init__.py`
- Sorted `__all__` lists per RUF022 (ASCII case-sensitive ordering)
- Removed redundant `# noqa` comments from namespace modules

## [0.2.2] - 2026-02-22

### Added
- MCP Registry listing: published as `io.github.VibeTensor/attestix`
- `server.json` for MCP Registry verification
- Research paper page with citation references (BibTeX, APA, IEEE)

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
