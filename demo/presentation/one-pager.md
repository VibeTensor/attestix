# Attestix - Compliance Automation for AI Agents

## What It Does

Attestix is an open-source attestation infrastructure that gives AI agents cryptographically verifiable proof of identity and regulatory compliance. It produces machine-readable W3C Verifiable Credentials signed with Ed25519, covering the full EU AI Act compliance workflow from agent identity through declaration of conformity.

## The Problem

The EU AI Act begins enforcement on August 2, 2026, with fines up to EUR 35 million or 7% of global annual revenue. The regulation requires machine-readable technical documentation, conformity assessments, and audit trails for AI systems. Existing compliance tools (Credo AI, Holistic AI, Vanta) are organizational dashboards that produce PDF reports for human reviewers - none produce cryptographically verifiable proof that a machine can verify, which is what an agent-to-agent world demands.

## Key Differentiators

- **Cryptographic proof, not dashboards.** Every artifact is Ed25519-signed and independently verifiable by any party without calling Attestix servers.
- **Agent-native identity.** W3C DIDs and Verifiable Credentials designed for machine-to-machine trust, not human reviewers clicking through checklists.
- **EU AI Act enforcement built in.** Automatically blocks prohibited systems (Article 5) and prevents self-assessment for high-risk systems (Article 43).
- **Offline-first, zero vendor lock-in.** All core operations work without internet. Data stays local. Fully open source under Apache 2.0.
- **MCP-native with 47 tools.** Direct integration with Claude, LangChain, OpenAI Agents SDK, CrewAI, and any MCP-compatible client.

## How It Works

**Step 1 - Identity.** Create a Unified Agent Identity Token (UAIT) with a W3C DID and Ed25519 keypair. This identity anchors all compliance evidence.

**Step 2 - Document.** Record training data provenance (Article 10), model lineage (Article 11), and hash-chained audit logs (Article 12). Create a compliance profile with automated risk classification.

**Step 3 - Prove.** Generate an Annex V declaration of conformity, automatically wrapped in a W3C Verifiable Credential. Bundle into a Verifiable Presentation for regulators. Optionally anchor to Base L2 blockchain for immutable timestamping.

## Standards

W3C Verifiable Credentials 1.1 / W3C DID Core 1.0 / UCAN v0.9.0 / Ed25519 (RFC 8032) / JSON Canonicalization (RFC 8785) / Ethereum Attestation Service / Base L2 / Merkle Trees (RFC 6962) / EU AI Act (11 articles + Annex III + Annex V) / GDPR Article 17

## By the Numbers

47 MCP tools / 9 modules / 358 automated tests (1 skipped on Windows) / 91 conformance benchmarks / 25 standards implemented / Sub-millisecond cryptographic operations / Apache 2.0 license

## Business Model

Attestix core is free and open source. Revenue from a managed cloud service with enterprise features (team management, compliance dashboards, SLA-backed blockchain anchoring), enterprise support contracts, and a marketplace for industry-specific compliance templates.

## Links

- **Website:** [attestix.io](https://attestix.io)
- **Documentation:** [attestix.io/docs](https://attestix.io/docs)
- **GitHub:** [github.com/VibeTensor/attestix](https://github.com/VibeTensor/attestix)
- **PyPI:** `pip install attestix`
- **Company:** [vibetensor.com](https://vibetensor.com)
- **Contact:** hello@vibetensor.com

---

*Built by VibeTensor - v0.2.4*
