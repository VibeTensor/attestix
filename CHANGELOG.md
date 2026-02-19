# Changelog

All notable changes to Attestix are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.1.0] - 2026-02-19

Initial public release.

### Added

**Phase 1 -- Identity & Trust (19 tools)**
- Identity module (7 tools): create, resolve, verify, translate, list, get, revoke agent identities via Unified Agent Identity Tokens (UAITs)
- Agent Cards module (3 tools): parse, generate, and discover Google A2A-compatible agent cards
- DID module (3 tools): create did:key and did:web identifiers, resolve any DID via Universal Resolver
- Delegation module (3 tools): UCAN-style capability delegation with EdDSA-signed JWT tokens
- Reputation module (3 tools): recency-weighted trust scoring with category breakdown

**Phase 2 -- EU AI Act Compliance (17 tools)**
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
- Complete API reference for all 36 tools
- Integration guide (LangChain, CrewAI, AutoGen, MCP client)
- FAQ
- 5 runnable example scripts

### Security

- Private keys never returned in MCP tool responses (stored locally in .keypairs.json)
- Mutable fields (proof, credentialStatus) excluded from VC signature payloads
- High-risk systems blocked from self-assessment (requires third-party per Article 43)
- SSRF protection on agent discovery URLs
- All sensitive files excluded from git (.signing_key.json, .keypairs.json, .env)
