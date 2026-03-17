# Attestix - Frequently Asked Questions

---

## Investor Questions

### 1. What is Attestix in one sentence?

Attestix is an open-source attestation infrastructure that gives AI agents cryptographically verifiable proof of identity and EU AI Act compliance, delivered as 47 MCP tools across 9 modules.

### 2. What is the total addressable market?

The AI governance market is projected to reach $4.5B - $7B by 2028 (Gartner, McKinsey estimates). More specifically, every company deploying AI agents in the EU or serving EU customers will need compliance tooling by August 2, 2026. The EU AI Act applies to AI systems "placed on the market or put into service in the Union," which includes non-EU companies serving EU users. The initial beachhead is AI agent developers using MCP-compatible frameworks (Claude, LangChain, CrewAI, AutoGen), estimated at hundreds of thousands of developers globally.

### 3. What is the business model?

Attestix core is free and open source (Apache 2.0). Revenue will come from: (1) a managed cloud service with enterprise features such as team management, compliance dashboards, and SLA-backed anchoring, (2) enterprise support contracts, and (3) a marketplace for pre-built compliance profiles and templates for specific industries and jurisdictions. Blockchain anchoring on Base L2 generates protocol-level revenue at fractions of a cent per anchor.

### 4. Who are the competitors and why will you win?

The main competitors are Credo AI ($22.8M raised), Holistic AI (acquired by Deloitte), Vanta ($2.45B valuation), and IBM OpenPages. All of them produce dashboard reports for human reviewers. None produce machine-readable, cryptographically verifiable proof. In an agent-to-agent world, compliance proof must be machine-verifiable. Attestix is the only tool that combines W3C Verifiable Credentials, agent identity (DIDs), and EU AI Act automation in a single open-source package. Being open source also means zero vendor lock-in, which is a key procurement concern for enterprises burned by SaaS dependencies.

### 5. What traction do you have?

Attestix is published on PyPI (pip install attestix), registered in the MCP Registry (io.github.VibeTensor/attestix), and has a research paper describing the system architecture and evaluation. The project has 284 automated tests including 91 conformance benchmarks validating standards compliance. Early validation includes direct encouragement from Yoshua Bengio (Turing Award, MILA) and business case validation from Matt Pagett (AI safety researcher, NANDA/CBAAC contributor).

### 6. What is the regulatory catalyst?

The EU AI Act enforcement begins August 2, 2026. Fines reach EUR 35 million or 7% of global annual revenue. This is not optional compliance - it is law. Every company deploying high-risk AI in the EU must have conformity assessments, technical documentation, and declarations of conformity. The urgency is real and the deadline is fixed.

### 7. What is the go-to-market strategy?

Bottom-up developer adoption through open source, PyPI distribution, and MCP Registry integration. Developers install Attestix, use it in their agent workflows, and it becomes embedded in their stack. Enterprise conversion happens when compliance teams discover their engineering teams are already using Attestix and need managed features. Secondary GTM through partnerships with AI agent frameworks (LangChain, CrewAI, AutoGen) and notified bodies performing EU AI Act assessments.

---

## Enterprise Client Questions

### 8. How do we integrate Attestix into our existing agent infrastructure?

Three integration paths: (1) as an MCP server that works with any MCP-compatible client (Claude Code, Claude Desktop, custom MCP clients), (2) as a Python library imported directly into your code (from services.identity_service import IdentityService), or (3) as a standalone service behind your API gateway. Integration with LangChain, CrewAI, and AutoGen is documented. A REST API is on the roadmap. Typical integration takes less than a day.

### 9. Where is our data stored?

All data stays in your environment. By default, Attestix stores data in local JSON files on disk. There are no cloud dependencies and no data leaves your infrastructure unless you explicitly configure blockchain anchoring (which only sends artifact hashes, never the artifacts themselves). You have full control over data residency.

### 10. What security guarantees does Attestix provide?

Every artifact is signed with Ed25519 (RFC 8032). Audit trails are hash-chained with SHA-256 for tamper evidence. Private keys can be encrypted with AES-256-GCM using the ATTESTIX_KEY_PASSWORD environment variable. SSRF protection blocks private IP access, metadata endpoints, and DNS rebinding. Private keys are never exposed in tool responses. The codebase has 284 automated tests including cryptographic conformance benchmarks validated against IETF test vectors.

### 11. Does using Attestix guarantee we are EU AI Act compliant?

No. Attestix is a documentation and evidence tooling system. It automates the generation of machine-readable compliance documentation, enforces correct assessment pathways (blocking self-assessment for high-risk systems), and produces cryptographically verifiable proof. However, it does not replace legal counsel, notified body assessments, or official regulatory submissions. Attestix gives you the evidence infrastructure. Your legal team and notified body make the compliance determination.

### 12. What happens if Attestix as a company disappears?

Because Attestix is fully open source under Apache 2.0, you can fork it, maintain it, and run it independently forever. There is no license key, no phone-home requirement, and no cloud dependency. All cryptographic verification is self-contained. Your compliance evidence remains valid because it is based on open standards (W3C VCs, DIDs, Ed25519) that any party can verify without Attestix infrastructure.

### 13. Can Attestix handle multiple agents across multiple teams?

Yes. Each agent gets its own identity (UAIT with unique DID). UCAN delegation chains allow parent agents to grant scoped capabilities to sub-agents with time-bounded expiry. Credentials and compliance profiles are per-agent. You can list and filter across all agents using the list tools. There is no limit on the number of agents.

---

## Technical Questions

### 14. What cryptographic algorithms does Attestix use?

Ed25519 (RFC 8032) for all digital signatures. SHA-256 for hash chains and audit trail integrity. JSON Canonicalization Scheme (RFC 8785) for deterministic JSON serialization before signing. PBKDF2 for key derivation when password-protected storage is enabled. AES-256-GCM for encrypted key storage. Base58btc and Base64url for encoding. Multibase and Multicodec for DID key encoding. All cryptographic operations use the Python cryptography library (pyca/cryptography) which wraps OpenSSL.

### 15. How does blockchain anchoring work?

Attestix computes the SHA-256 hash of an artifact (identity, credential, or audit batch) and submits it to the Ethereum Attestation Service (EAS) on Base L2. For batch operations, it constructs a Merkle tree (RFC 6962) of multiple audit entries and anchors the Merkle root. The on-chain record contains only the hash, not the artifact itself. Verification compares the local artifact hash against the on-chain record. Cost is typically fractions of a cent per anchor due to Base L2's low gas fees.

### 16. What about scalability? Can this handle thousands of agents?

Core cryptographic operations are sub-millisecond: Ed25519 key generation at 0.08ms, sign+verify at 0.28ms, JSON canonicalization at 0.02ms. Identity creation takes approximately 14ms and credential issuance approximately 17ms. These benchmarks are from 1000-run median measurements. Local JSON storage is suitable for development and small deployments. For production at scale, the storage layer can be swapped to a database backend. The MCP protocol supports concurrent tool calls.

### 17. How are W3C Verifiable Credentials structured?

Attestix issues VCs following W3C Verifiable Credentials Data Model 1.1. Each VC includes a JSON-LD context, credential type, issuer DID, issuance date, credential subject, and an Ed25519Signature2020 proof. The proof is computed over the canonicalized credential with mutable fields (proof itself) excluded. Verifiable Presentations bundle multiple VCs with a separate presentation proof and include a challenge/domain for replay protection.

---

## Regulatory Questions

### 18. Which specific EU AI Act articles does Attestix cover?

Attestix automates documentation and enforcement for: Article 5 (prohibited practices - detection and blocking), Articles 9-15 (high-risk system requirements including risk management, data governance, technical documentation, record-keeping, transparency, human oversight, accuracy and robustness), Article 43 (conformity assessment procedures with enforcement of third-party assessment for high-risk systems), Article 50 (transparency obligations for limited-risk systems), Annex III (high-risk classification categories), and Annex V (EU declaration of conformity auto-generation). A total of 13 articles plus Annex III and Annex V are covered.

### 19. How does Attestix handle GDPR compliance?

Attestix implements GDPR Article 17 (right to erasure) through the purge_agent_data tool, which deletes all data associated with an agent identity across all storage modules - identities, credentials, compliance profiles, provenance records, delegation tokens, reputation data, and audit entries. The tool returns a detailed report of what was purged from each store. Because all data is stored locally by default, data residency and data controller obligations are straightforward.

### 20. Does Attestix support compliance frameworks beyond the EU AI Act?

The core infrastructure - W3C Verifiable Credentials, DIDs, Ed25519 signatures, audit trails, and provenance tracking - is framework-agnostic. The EU AI Act compliance module is the first specialized module, but the same cryptographic evidence model can be extended to other jurisdictions: the UK AI regulation framework, Canada's AIDA (Artificial Intelligence and Data Act), NIST AI Risk Management Framework, and ISO 42001 (AI Management System). The open-source architecture means anyone can build additional compliance modules on top of the existing credential and identity infrastructure.
