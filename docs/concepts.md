# Attestix Concepts Explained

Plain-English explanations of the key concepts used in Attestix.

## UAIT (Unified Agent Identity Token)

**What it is:** A digital passport for your AI agent.

A UAIT contains everything that identifies an agent:
- Name and description
- What the agent can do (capabilities)
- Who issued the identity
- When it was created and when it expires
- A cryptographic signature proving the identity is authentic

**Real-world analogy:** Like a passport that combines your photo, nationality, and visa stamps into one document that border agents can verify.

**How it's used:** When your agent needs to prove who it is to another system, agent, or regulator, it presents its UAIT. The recipient can verify the Ed25519 signature without calling any external service.

## DID (Decentralized Identifier)

**What it is:** A globally unique ID for your agent that doesn't depend on any company.

A DID looks like this:
```
did:key:z6Mkija7eQS9kNrvh1kAp7PJFgPEznFpBdDm825vugSQxdW7
```

**Why it matters:** Traditional identifiers (usernames, API keys) are controlled by a single company. If that company goes down, your identity disappears. A DID is cryptographically self-sovereign -- your agent owns its identity.

**Types Attestix supports:**
- `did:key` -- Derived from a public key. No network needed. Instant.
- `did:web` -- Hosted on your domain. Resolvable via HTTPS.
- Any other DID method via Universal Resolver.

**Real-world analogy:** Like a phone number that works across all carriers and countries, except no carrier can revoke it.

## Verifiable Credential (VC)

**What it is:** A digitally signed document that proves something about your agent.

A VC contains:
- Who it's about (the subject)
- What it claims (e.g., "this agent passed EU AI Act conformity assessment")
- Who issued it (the issuer)
- A cryptographic proof that it hasn't been tampered with

**How it differs from a PDF certificate:**
- Machine-readable (any system can parse and verify it)
- Cryptographically signed (tampering is detectable)
- Follows W3C international standard (interoperable)
- Can be selectively disclosed (show only what's needed)

**Real-world analogy:** Like a university diploma, but instead of being a piece of paper that could be forged, it's a digital document signed by the university's private key that anyone can verify.

**Attestix credential types:**
- `EUAIActComplianceCredential` -- Proves EU AI Act compliance
- `ConformityAssessmentCredential` -- Proves assessment results
- `AgentIdentityCredential` -- Proves agent identity claims
- `TrainingDataProvenanceCredential` -- Proves data governance
- Custom types -- Define your own

## Verifiable Presentation (VP)

**What it is:** A bundle of Verifiable Credentials you present to a specific verifier.

**Why not just send the VCs directly?** A VP adds:
- **Audience binding** -- This presentation is for TUV Rheinland, not anyone else
- **Challenge/nonce** -- Prevents replay attacks (someone can't reuse your presentation)
- **Holder signature** -- Proves the presenter authorized this disclosure

**Real-world analogy:** Like bringing your passport + visa + vaccination card to an embassy. You show specific documents to a specific party for a specific purpose.

## UCAN (User Controlled Authorization Network)

**What it is:** A way to delegate capabilities from one agent to another, creating verifiable chains of authority.

**How it works:**
1. Agent A has capability "read_financials"
2. Agent A delegates "read_financials" to Agent B (creates a signed token)
3. Agent B can prove it has this capability by showing the token chain
4. Anyone can verify the chain traces back to Agent A's original authority

**Why this matters:** In multi-agent systems, agents need to act on behalf of other agents. UCAN creates auditable chains of authority, unlike simple API keys that can be shared without accountability.

**Real-world analogy:** Like a power of attorney. Your lawyer can act on your behalf, and anyone can verify the chain of authorization back to you.

## Ed25519

**What it is:** The cryptographic algorithm Attestix uses for all signatures.

**Why Ed25519:**
- Fast (64K signatures per second)
- Small signatures (64 bytes)
- Small keys (32 bytes)
- Deterministic (same input = same signature)
- Widely used (SSH, Signal, Solana, Cosmos, TLS)
- No known vulnerabilities

**How Attestix uses it:**
- Server signing key generated on first run (stored in `.signing_key.json`)
- Every UAIT, VC, compliance record, and audit log entry is signed
- Anyone with the public key (embedded in the DID) can verify signatures

## Reputation Score

**What it is:** A trust score (0.0 to 1.0) for an agent based on its interaction history.

**How it works:**
- Each interaction is recorded with an outcome (success/failure/partial)
- Recent interactions count more (30-day half-life exponential decay)
- Score is computed across categories (e.g., data_quality: 0.95, response_time: 0.80)
- New agents start with no score (not 0.0 -- absence of data, not distrust)

**Why recency-weighted:** An agent that was great 6 months ago but has been failing recently should not ride on its old reputation. The decay function ensures the score reflects current behavior.

## JSON File Storage

Attestix stores all data in local JSON files:

| File | Contains |
|------|---------|
| `identities.json` | All UAITs |
| `credentials.json` | All Verifiable Credentials |
| `compliance.json` | Compliance profiles, assessments, declarations |
| `provenance.json` | Training data records, model lineage, audit logs |
| `reputation.json` | Interaction history and scores |
| `delegations.json` | Delegation tokens |

All files use file locking (cross-platform) and atomic writes to prevent corruption. Backups are created automatically before each write.

## Key Terms Glossary

| Term | Meaning |
|------|---------|
| **Agent** | An AI system with an identity in Attestix |
| **Annex III** | EU AI Act appendix listing high-risk AI categories |
| **Annex V** | EU AI Act appendix defining declaration of conformity format |
| **Article 43** | EU AI Act section on conformity assessments |
| **Conformity assessment** | Process of verifying an AI system meets requirements |
| **Declaration of conformity** | Official statement that an AI system complies |
| **Multibase** | Encoding format for keys (prefix `z` = base58btc) |
| **Multicodec** | Self-describing format prefix (Ed25519 = 0xed01) |
| **Notified body** | Organization authorized to conduct conformity assessments (e.g., TUV, BSI) |
| **Proof** | Cryptographic evidence attached to a credential |
| **Revocation** | Marking an identity or credential as no longer valid |
