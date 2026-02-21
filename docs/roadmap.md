# Roadmap

The project vision: every AI agent gets a verifiable identity, proves its compliance, and anchors its trust on-chain.

## Phase 1 - Identity & Trust (Complete)

21 MCP tools for cross-protocol agent identity.

| Module | Tools | What it does |
|--------|-------|-------------|
| Identity | 8 | Unified Agent Identity Tokens (UAITs) bridging MCP OAuth, A2A Agent Cards, DIDs, and API keys. GDPR Article 17 erasure |
| Agent Cards | 3 | Parse, generate, and discover Google A2A-compatible agent cards |
| DID | 3 | Create and resolve W3C Decentralized Identifiers (did:key, did:web, Universal Resolver) |
| Delegation | 4 | UCAN-style capability delegation with EdDSA-signed JWT tokens, revocation |
| Reputation | 3 | Recency-weighted trust scoring (0.0-1.0) with category breakdown and 30-day half-life decay |

**Key decisions:**
- Ed25519 for all cryptographic operations (same as SSH, Signal, Solana, Cosmos)
- JSON file storage with file locking - no database dependency
- All records cryptographically signed at creation time
- Server signing key auto-generated on first run
- SSRF protection on all URL-fetching operations
- Hash-chained audit trail with SHA-256 for tamper-evident logging
- 91 conformance benchmark tests validating RFC 8032, W3C VC, W3C DID, UCAN, and MCP standards

## Phase 2 - EU AI Act Compliance (Complete)

20 MCP tools for regulatory compliance documentation.

| Module | Tools | What it does |
|--------|-------|-------------|
| Compliance | 7 | Risk categorization (minimal/limited/high), conformity assessments (Article 43), Annex V declarations, profile updates |
| Credentials | 8 | W3C Verifiable Credentials (VC Data Model 1.1) with Ed25519Signature2020 proofs, external verification, Verifiable Presentations |
| Provenance | 5 | Training data provenance (Article 10), model lineage (Article 11), hash-chained audit trail (Article 12) |

**Key decisions:**
- VC Data Model 1.1 (widely supported, stable specification)
- High-risk systems blocked from self-assessment (requires third-party per Article 43)
- Declaration generation auto-issues a W3C Verifiable Credential
- Mutable fields excluded from signature payloads (revocation doesn't break signatures)
- External VP and credential verification for third-party auditors

**EU AI Act timeline:**
- August 2, 2026 - Enforcement begins for high-risk systems and transparency obligations
- August 2, 2027 - Obligations for AI in regulated products (medical devices, machinery)

## Phase 3 - Blockchain Anchoring (Complete)

6 MCP tools for on-chain tamper-proof verification. Everything still works offline - blockchain adds public verifiability.

| Module | Tools | What it does |
|--------|-------|-------------|
| Blockchain | 6 | Anchor identity and credential hashes to Base L2 via EAS, Merkle batch anchoring, cost estimation |

**Tools:**
- `anchor_identity` - Anchor a UAIT hash on-chain
- `anchor_credential` - Anchor a VC hash via EAS
- `anchor_audit_batch` - Merkle-root a batch of audit entries
- `verify_anchor` - Check on-chain anchor for any artifact
- `get_anchor_status` - Retrieve all on-chain anchors for an agent
- `estimate_anchor_cost` - Gas estimation before anchoring

**Target chain:** Base (Ethereum L2) - sub-$0.01 gas costs, EAS support, growing agent ecosystem.

## Phase 4 - Ecosystem Bridges (Planned)

Connect to existing agent identity ecosystems for interoperability.

### ERC-8004 Identity Registry
- Adapter between UAIT and ERC-8004 on-chain agent identity (ERC-721 compatible)
- Mint agent identity NFTs from UAITs
- Resolve ERC-8004 identities back to UAITs
- Bi-directional sync: changes on either side reflected

### A2A Agent Card Auto-Sync
- Watch for UAIT changes and auto-update hosted agent.json
- Reverse sync: discover agent cards and import as UAITs
- Support for agent card registries

### ANS (Agent Name Service)
- Human-readable agent names (like ENS for agents)
- Resolve `agent.vibetensor.eth` to a UAIT
- Register and manage agent names on-chain

### Polygon ID / Zero-Knowledge Credentials
- Issue ZK-compatible credentials (selective disclosure)
- Prove compliance without revealing underlying data
- Integration with Polygon ID Verifier SDK

**Estimated tools: 8-12**

## Phase 5 - Multi-Chain & Enterprise (Future)

### Multi-Chain Identity
- Solana (SVM): anchor UAITs on Solana for sub-second finality
- Cosmos (IBC): cross-chain identity via IBC protocol
- Polkadot: parachain identity bridging
- Chain-agnostic resolution: given any on-chain anchor, resolve back to UAIT

### Enterprise Features
- Role-based access control for multi-user Attestix instances
- PostgreSQL/MongoDB storage backend (replace JSON for scale)
- REST API server mode (in addition to MCP stdio)
- Webhook notifications for identity/compliance events
- Batch operations for fleet management (100s of agents)
- Audit log export (CSV, SIEM integration)

### Global Regulatory Expansion
- US: NIST AI RMF mapping, Colorado AI Act (SB 24-205), Texas RAIGA
- India: Digital India Act AI provisions
- South Korea: AI Basic Act compliance profiles
- China: Algorithm Registration compliance
- ISO/IEC 42001 AI Management System mapping
- Regulatory framework plugin system (add new regulations without code changes)

### SDK & Integrations
- Python SDK (`pip install attestix-sdk`) with typed client
- TypeScript/JavaScript SDK for Node.js and browser
- LangChain native integration (published to langchain-community)
- CrewAI plugin
- Official MCP tool catalog listing

## Version Plan

| Version | Phase | Target |
|---------|-------|--------|
| 0.1.0 | Phase 1 + 2 | Initial release (36 tools) |
| 0.2.0 | Phase 3 | Blockchain anchoring + security audit + conformance benchmarks (47 tools, 284 tests) |
| 0.3.0 | Phase 4 | ERC-8004, A2A sync, ANS |
| 0.4.0 | Phase 4 | Polygon ID / ZK credentials |
| 0.5.0 | Phase 5 | Multi-chain + enterprise storage |
| 1.0.0 | Stable | Production-ready with full test suite and third-party audit |
