# Scenario 1: FinTech Advisory AI

## What This Demonstrates

This scenario walks through the full Attestix lifecycle for **WealthBot-Pro**, an AI-powered wealth management advisor built by FinanceAI Corp. It covers identity creation, provenance tracking, EU AI Act compliance, verifiable credentials, capability delegation, reputation scoring, and tamper-evident audit trails.

The demo exercises 7 out of 9 Attestix modules (all except Blockchain anchoring and Agent Card generation) across 18 sequential steps.

## Why FinTech Advisory Is High-Risk

Under the EU AI Act (Regulation 2024/1689), AI systems used in financial services are classified as **high-risk** under **Annex III, Category 5(b)**: systems intended to be used to evaluate the creditworthiness of natural persons or to establish their credit score, as well as systems used for access to and enjoyment of essential private services and public services and benefits.

An AI wealth advisor falls squarely into this category because it:

- Makes or influences investment decisions affecting individuals' financial wellbeing
- Provides personalized financial advice that could lead to significant financial loss
- Operates in a regulated domain (MiFID II) where errors have material consequences
- Processes financial data that requires strict governance under GDPR and sector-specific regulations

High-risk classification triggers the strictest set of obligations under the EU AI Act, including mandatory third-party conformity assessment (Article 43), comprehensive technical documentation (Article 11), automatic logging (Article 12), human oversight mechanisms (Article 14), and a formal declaration of conformity (Annex V).

## How to Run

### Option A: Python Script (Direct)

Run from the Attestix project root directory:

```bash
python demo/scenarios/01-fintech-advisor/run_demo.py
```

The script imports services directly and executes all 18 steps in sequence. No server or MCP client is needed.

**Prerequisites:**
- Python 3.10+
- Attestix dependencies installed (`pip install -e .` or `pip install -r requirements.txt`)

### Option B: MCP Client (Interactive)

1. Start the Attestix MCP server (via Claude Desktop, VS Code, or any MCP client)
2. Open `mcp_prompts.md` and send each numbered prompt in order
3. Replace placeholder IDs (`AGENT_ID`, `CRED_ID`, etc.) with actual values from earlier steps

This option lets you explore interactively and ask follow-up questions at each step.

## What to Look for at Each Step

### Key Demo Moments

| Step | What Happens | Why It Matters |
|------|-------------|----------------|
| **1** | Identity creation | Agent gets a cryptographically signed UAIT with capabilities |
| **3-4** | Training data provenance | Article 10 (data governance) compliance is established |
| **5** | Model lineage with metrics | Article 11 (technical documentation) and Article 15 (accuracy) |
| **6** | Gap analysis at ~62% | Shows exactly what is missing before any assessment |
| **7** | Self-assessment blocked | **The signature moment.** Attestix enforces Article 43 automatically. High-risk systems cannot self-certify. |
| **8** | Third-party assessment passes | Only after Deloitte (third party) certifies does the profile advance |
| **9** | Declaration of conformity | Full Annex V document with all 12 required fields |
| **10** | Compliance jumps to 75% | Some Article 9-15 deep obligations remain (designed to show the depth of the framework) |
| **11-12** | Custom credential + verification | W3C VC 1.1 with Ed25519 proof, fully verifiable |
| **13** | Verifiable Presentation | Bundles multiple credentials for a regulator with replay protection |
| **14** | Delegation with attenuation | UCAN-style JWT - WealthBot delegates only `portfolio_read` (not its full capabilities) to AnalysisBot |
| **15-16** | Reputation scoring | Trust score drops from 1.0 to 0.9 after one partial interaction, demonstrating recency-weighted decay |
| **17-18** | Audit trail with hash chain | SHA-256 linked entries create a tamper-evident log per Article 12 |

### The Three "Aha" Moments

1. **Step 7 - Self-assessment rejection**: The system knows this is a high-risk agent and blocks self-certification. This is not just a warning; it is an enforced policy.

2. **Step 9 - Declaration of conformity**: A real Annex V declaration is generated with all 12 fields, signed cryptographically, and backed by a Verifiable Credential. This is what regulators will ask for.

3. **Step 14 - Capability attenuation**: WealthBot-Pro has 4 capabilities but delegates only 1 to AnalysisBot. The delegation token proves exactly what was delegated, by whom, and for how long.

## Expected Duration

- **Python script**: ~3 seconds (all 18 steps run sequentially)
- **MCP interactive**: ~3 to 5 minutes (depending on reading time between prompts)

## Artifacts Created

After running, the following artifacts exist in the Attestix data files:

| Artifact | Storage File | Count |
|----------|-------------|-------|
| Agent identities | `identities.json` | 2 (WealthBot-Pro + AnalysisBot) |
| DID keypair | `.keypairs.json` | 1 |
| Training data entries | `provenance.json` | 2 |
| Model lineage entry | `provenance.json` | 1 |
| Compliance profile | `compliance.json` | 1 |
| Conformity assessment | `compliance.json` | 1 |
| Declaration of conformity | `compliance.json` | 1 |
| Verifiable Credentials | `credentials.json` | 2 (compliance + license) |
| Delegation token | `delegations.json` | 1 |
| Reputation interactions | `reputation.json` | 5 |
| Audit log entries | `provenance.json` | 3 |

## Standards Covered

This single scenario exercises the following standards and specifications:

- **EU AI Act** (Regulation 2024/1689): Articles 9-15, 43, Annex III, Annex V
- **W3C Verifiable Credentials** Data Model 1.1
- **W3C DID** (Decentralized Identifiers) v1.0
- **UCAN** (User Controlled Authorization Networks) v0.9.0
- **Ed25519** digital signatures (RFC 8032)
- **JCS** (JSON Canonicalization Scheme, RFC 8785) for deterministic signing
- **SHA-256** hash-chained audit trail (RFC 6962 Merkle tree pattern)
