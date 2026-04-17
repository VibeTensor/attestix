# Attestix Competitive Comparison

> Last updated: March 2026. Competitor information is based on publicly available data and may not reflect recent changes. Items marked with (?) indicate uncertainty or limited public information.

---

## Overview

| Company | Category | Funding / Valuation | Founded | Open Source |
|---------|----------|-------------------|---------|-------------|
| **Attestix** | AI agent attestation infrastructure | Pre-seed (bootstrapped) | 2025 | Yes (Apache 2.0) |
| **Credo AI** | AI governance platform | $22.8M (Series A, 2022) | 2020 | No |
| **Holistic AI** | AI risk management | Acquired by Deloitte (2024) | 2018 | No |
| **Vanta** | Compliance automation (SOC 2, ISO, etc.) | $2.45B valuation (Series C, 2024) | 2018 | No |
| **IBM OpenPages** | Governance, Risk, Compliance (GRC) | Part of IBM (enterprise product) | ~2001 (acquired by IBM 2010) | No |
| **Fairly AI** | AI fairness and bias auditing | ~$3M seed (?) | 2020 | No |

---

## Feature Comparison

| Feature | Attestix | Credo AI | Holistic AI | Vanta | IBM OpenPages | Fairly AI |
|---------|----------|----------|-------------|-------|---------------|-----------|
| **Machine-readable proof** | W3C Verifiable Credentials with JSON-LD proofs | PDF/dashboard reports | PDF reports, risk scores | PDF audit reports | GRC reports | Audit reports |
| **Cryptographic signatures** | Ed25519Signature2020 on all artifacts | None (trust the platform) | None | None | None | None |
| **Agent identity (DID)** | W3C DID Core 1.0 (did:key, did:web) | No agent identity layer | No | No | No | No |
| **Verifiable Presentations** | W3C VP bundling multiple VCs | No | No | No | No | No |
| **Delegation chains** | UCAN v0.9.0 with EdDSA JWT | Role-based access (platform) | Role-based access (platform) | Team-based access | Enterprise RBAC | No |
| **Open source** | Apache 2.0, full source on GitHub | Proprietary | Proprietary | Proprietary | Proprietary | Proprietary (?) |
| **Offline capable** | Full core operations, local JSON storage | Cloud-only | Cloud-only | Cloud-only | On-prem option available | Cloud-only (?) |
| **MCP native** | 47 MCP tools, MCP Registry listed | No MCP support | No MCP support | No MCP support | No MCP support | No MCP support |
| **Blockchain anchoring** | EAS on Base L2, Merkle batching | No | No | No | No | No |
| **EU AI Act specific** | Articles 5, 9-15, 43, Annex III, Annex V automated | EU AI Act module (dashboard) | EU AI Act risk assessment | No (SOC 2, ISO, HIPAA focus) | Can be configured for AI regs | Limited EU AI Act coverage |
| **Risk classification enforcement** | Automated - prohibits deployment of Article 5 systems | Manual risk categorization | Automated risk scoring | N/A | Manual configuration | Bias-focused, not risk tiers |
| **Conformity assessment** | Article 43 enforcement (blocks self-assessment for high-risk) | Workflow-based | Audit reports | N/A | Workflow-based | N/A |
| **Annex V declaration** | Auto-generated, wrapped in signed VC | Template-based (?) | Not specifically (?) | N/A | Template-based | N/A |
| **Audit trail** | Hash-chained with SHA-256, Article 12 compliant | Activity logs (platform) | Activity logs (platform) | Activity logs | Full audit trail | Basic logging (?) |
| **GDPR Article 17** | Purge agent data across all stores | Data management features | Data management features | Data management features | Data lifecycle management | Not specifically |
| **Training data provenance** | Article 10 structured records with hashing | Data lineage features | Dataset documentation | N/A | N/A | Dataset bias analysis |
| **Model lineage** | Article 11 chain with metrics and parent tracking | Model cards | Model documentation | N/A | N/A | Model bias reports |
| **Reputation / trust scoring** | Recency-weighted 0.0 - 1.0 score with categories | No | No | Vendor risk scoring | Risk scoring | No |
| **A2A agent cards** | Parse, generate, discover (well-known endpoint) | No | No | No | No | No |
| **Multi-agent support** | Native - identity per agent, cross-agent verification | Organization-level | Organization-level | Organization-level | Organization-level | Per-model |
| **Performance** | Sub-millisecond crypto ops, ~17ms credential issuance | Cloud-dependent | Cloud-dependent | Cloud-dependent | Enterprise infrastructure | Cloud-dependent |

---

## Pricing Comparison

| Solution | Pricing Model | Approximate Cost |
|----------|--------------|------------------|
| **Attestix** | Free and open source (Apache 2.0). Blockchain anchoring costs gas fees on Base L2 (fractions of a cent per anchor) | $0 for software. ~$0.001 - $0.01 per blockchain anchor |
| **Credo AI** | Enterprise SaaS, annual contract | ~$100K - $500K/year (?) based on modules and scale |
| **Holistic AI** | Enterprise SaaS (now part of Deloitte consulting) | Consulting engagement pricing, likely $200K+ (?) |
| **Vanta** | SaaS per framework, per employee | ~$10K - $50K/year depending on company size and frameworks |
| **IBM OpenPages** | Enterprise license + IBM consulting | $250K - $1M+ (?) depending on deployment |
| **Fairly AI** | SaaS, per-audit or subscription | ~$20K - $100K/year (?) |

> Pricing marked with (?) is estimated from public sources and industry norms. Actual pricing varies by contract.

---

## Target User Comparison

| Solution | Primary User | Secondary User |
|----------|-------------|----------------|
| **Attestix** | AI engineers and agent developers who need machine-readable compliance proof | Compliance teams who need verifiable evidence |
| **Credo AI** | Chief AI Officers, AI governance teams | Data science teams |
| **Holistic AI** | Enterprise risk and compliance officers | Legal teams, Deloitte audit clients |
| **Vanta** | Security and compliance teams (SOC 2 focused) | Engineering teams doing vendor assessments |
| **IBM OpenPages** | GRC professionals in large enterprises | Internal audit, risk management |
| **Fairly AI** | Data scientists concerned with bias | Compliance teams needing fairness audits |

---

## Architecture Comparison

| Aspect | Attestix | Credo AI | Holistic AI | Vanta | IBM OpenPages | Fairly AI |
|--------|----------|----------|-------------|-------|---------------|-----------|
| **Deployment** | Local (pip install), Docker, or any Python environment | Cloud SaaS | Cloud SaaS | Cloud SaaS | On-prem or cloud | Cloud SaaS (?) |
| **Integration model** | MCP protocol (tool-based), Python library, REST API planned | API + web UI | API + web UI | API + web UI + agents | API + web UI | API + web UI |
| **Data storage** | Local JSON files (default), configurable | Vendor cloud | Vendor cloud | Vendor cloud | Customer infrastructure | Vendor cloud (?) |
| **Data residency** | Full control, data never leaves your environment | Vendor-managed | Vendor-managed | SOC 2 compliant hosting | Customer-managed | Vendor-managed (?) |
| **Standards used** | W3C VC 1.1, W3C DID 1.0, UCAN 0.9.0, RFC 8032, RFC 8785, EAS | NIST AI RMF, ISO 42001 (?) | ISO 42001, NIST (?) | SOC 2, ISO 27001, HIPAA | IBM GRC frameworks | Fairness metrics |

---

## Key Differentiators Summary

### What Attestix does that no competitor does:

1. **Cryptographic proof, not trust-the-platform.** Every artifact is Ed25519-signed. Verification does not require calling Attestix servers. Any party with the public key can verify independently.

2. **Agent-native identity.** W3C DIDs and Verifiable Credentials are designed for machine-to-machine trust. Dashboard-based tools produce reports for humans. Attestix produces proof for machines.

3. **EU AI Act enforcement, not just documentation.** Attestix actively blocks prohibited systems (Article 5) and prevents self-assessment for high-risk systems (Article 43). Competitors provide checklists.

4. **Offline-first, zero vendor lock-in.** All core operations work without internet. Data stays local. Open source under Apache 2.0. No subscription fees.

5. **MCP-native integration.** Direct integration with Claude, LangChain, OpenAI Agents SDK, CrewAI, and any MCP-compatible client. No custom API integration needed.

6. **Blockchain timestamping.** Immutable proof of existence via EAS on Base L2. Sub-cent anchoring costs. No other AI compliance tool offers on-chain evidence anchoring.

---

## Where Competitors Are Stronger

To be fair and balanced:

| Area | Competitor Advantage |
|------|---------------------|
| **Enterprise sales motion** | Credo AI, Holistic AI, and IBM have established enterprise sales teams and existing customer bases |
| **SOC 2 / ISO 27001 coverage** | Vanta is purpose-built for these frameworks with deep integrations (HR, cloud providers, code repos) |
| **Bias and fairness auditing** | Holistic AI and Fairly AI have deeper statistical fairness testing capabilities |
| **Consulting and advisory** | Holistic AI (via Deloitte) and IBM offer advisory services alongside the tooling |
| **UI and dashboards** | All competitors have mature web interfaces for non-technical users. Attestix is CLI and MCP-first |
| **Maturity and track record** | Competitors have multi-year production deployments. Attestix is v0.2.4 (beta) |
| **NIST AI RMF** | Credo AI has deep NIST AI Risk Management Framework mapping |
