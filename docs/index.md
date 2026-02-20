# Attestix

**Attestation Infrastructure for AI Agents**

The compliance identity layer for the EU AI Act era. Attestix gives every AI agent a verifiable identity, proves its regulatory compliance, tracks its provenance, and scores its trustworthiness -- all locally, vendor-neutrally, and natively within MCP.

## Why This Exists

On **August 2, 2026**, the EU AI Act's transparency enforcement begins. Fines reach up to EUR 35M or 7% of global revenue. Every high-risk AI system deployed in EU markets must demonstrate compliance.

The existing compliance tools (Credo AI, Holistic AI, Vanta) all operate as **organizational dashboards**. None produce a **machine-readable, cryptographically verifiable proof** that an AI agent can present to another agent, regulator, or system.

Meanwhile, agent identity is fragmenting across walled gardens (Microsoft Entra, AWS AgentCore, Google A2A, ERC-8004). No single tool combines **agent identity + EU AI Act compliance + verifiable credentials** in one protocol.

## What Attestix Does

42+ MCP tools across 9 modules:

| Module | Tools | Purpose |
|--------|-------|---------|
| **Identity** | 7 | Unified Agent Identity Tokens (UAITs) bridging MCP OAuth, A2A, DIDs, and API keys |
| **Agent Cards** | 3 | Parse, generate, and discover A2A-compatible agent cards |
| **DID** | 3 | Create and resolve W3C Decentralized Identifiers |
| **Delegation** | 3 | UCAN-style capability delegation with signed JWT tokens |
| **Reputation** | 3 | Recency-weighted trust scoring with category breakdown |
| **Compliance** | 6 | EU AI Act risk profiles, conformity assessments, Annex V declarations |
| **Credentials** | 6 | W3C Verifiable Credentials with Ed25519Signature2020 proofs |
| **Provenance** | 5 | Training data provenance, model lineage, audit trail |
| **Blockchain** | 6 | Anchor artifact hashes to Base L2 via EAS, Merkle batch anchoring |

## Quick Start

```bash
pip install attestix
```

Or from source:

```bash
git clone https://github.com/VibeTensor/attestix.git
cd attestix
pip install -r requirements.txt
python main.py
```

See the [Getting Started](getting-started.md) guide for detailed setup.

## Important Disclaimer

Attestix generates machine-readable, cryptographically signed compliance documentation for AI agents. It is a documentation and evidence tooling system.

**Attestix does not replace legal counsel, notified body assessments, or official regulatory submissions.** Always consult qualified legal professionals for compliance decisions.

## License

Apache License 2.0. See [LICENSE](https://github.com/VibeTensor/attestix/blob/main/LICENSE).

---

Built by [VibeTensor](https://vibetensor.com)
