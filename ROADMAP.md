# Roadmap

The project vision: every AI agent gets a verifiable identity, proves its compliance, and anchors its trust on-chain.

## Phase 1 -- Identity & Trust (Complete)

19 MCP tools for cross-protocol agent identity.

| Module | Tools | What it does |
|--------|-------|-------------|
| Identity | 7 | Unified Agent Identity Tokens (UAITs) bridging MCP OAuth, A2A Agent Cards, DIDs, and API keys into one format |
| Agent Cards | 3 | Parse, generate, and discover Google A2A-compatible agent cards |
| DID | 3 | Create and resolve W3C Decentralized Identifiers (did:key, did:web, Universal Resolver) |
| Delegation | 3 | UCAN-style capability delegation with EdDSA-signed JWT tokens and proof chains |
| Reputation | 3 | Recency-weighted trust scoring (0.0-1.0) with category breakdown and 30-day half-life decay |

**Key decisions:**
- Ed25519 for all cryptographic operations (same as SSH, Signal, Solana, Cosmos)
- JSON file storage with file locking -- no database dependency
- All records cryptographically signed at creation time
- Server signing key auto-generated on first run

## Phase 2 -- EU AI Act Compliance (Complete)

17 MCP tools for regulatory compliance documentation.

| Module | Tools | What it does |
|--------|-------|-------------|
| Compliance | 6 | Risk categorization (minimal/limited/high), conformity assessments (Article 43), Annex V declarations of conformity |
| Credentials | 6 | W3C Verifiable Credentials (VC Data Model 1.1) with Ed25519Signature2020 proofs, Verifiable Presentations |
| Provenance | 5 | Training data provenance (Article 10), model lineage (Article 11), audit trail (Article 12) |

**Key decisions:**
- VC Data Model 1.1 (widely supported, stable specification)
- High-risk systems blocked from self-assessment (requires third-party per Article 43)
- Declaration generation auto-issues a W3C Verifiable Credential
- Mutable fields excluded from signature payloads (revocation doesn't break signatures)

**EU AI Act timeline:**
- August 2, 2026 -- Enforcement begins for high-risk systems and transparency obligations
- August 2, 2027 -- Obligations for AI in regulated products (medical devices, machinery)

## Phase 3 -- Blockchain Anchoring (Planned)

Anchor cryptographic proofs on-chain without moving core operations to the blockchain. Everything still works offline -- blockchain adds tamper-proof public verifiability.

| Off-Chain (Current) | On-Chain (Phase 3) | Standard |
|---------------------|-------------------|----------|
| UAIT creation + Ed25519 signing | Hash anchor to Base L2 | Custom attestation |
| W3C VC issuance | VC hash via Ethereum Attestation Service (EAS) | EAS schema |
| Reputation scoring | Score summary on ERC-8004 registry | ERC-8004 |
| Audit trail | Merkle root of periodic audit log batches | Merkle tree |
| Compliance declarations | Declaration hash on-chain | EAS attestation |

**Target chain:** Base (Ethereum L2)
- Sub-$0.01 gas costs for attestations
- ERC-8004 compatibility (agent identity standard)
- Ethereum Attestation Service support
- Growing agent ecosystem (Mantle, Coinbase, etc.)

**Scope:**
- [ ] Base L2 integration (ethers.js / web3.py)
- [ ] EAS schema registration for UAIT and VC hashes
- [ ] Anchor service: signs hash, submits to chain, stores tx receipt
- [ ] Verification service: given a UAIT/VC, verify its on-chain anchor
- [ ] Merkle tree batching for audit log entries (cost optimization)
- [ ] On-chain revocation registry (complement local revocation)
- [ ] Gas estimation and cost reporting tools

**New tools (estimated 6-8):**
- `anchor_identity` -- Anchor a UAIT hash on-chain
- `anchor_credential` -- Anchor a VC hash via EAS
- `verify_anchor` -- Check on-chain anchor for any artifact
- `anchor_audit_batch` -- Merkle-root a batch of audit entries
- `get_anchor_status` -- Retrieve all on-chain anchors for an agent
- `estimate_anchor_cost` -- Gas estimation before anchoring

## Phase 4 -- Ecosystem Bridges (Planned)

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

## Phase 5 -- Multi-Chain & Enterprise (Future)

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
| 0.2.0 | Phase 3 | Blockchain anchoring on Base L2 |
| 0.3.0 | Phase 4 | ERC-8004, A2A sync, ANS |
| 0.4.0 | Phase 4 | Polygon ID / ZK credentials |
| 0.5.0 | Phase 5 | Multi-chain + enterprise storage |
| 1.0.0 | Stable | Production-ready with full test suite |
