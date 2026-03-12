# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.2.x   | :white_check_mark: |
| < 0.2   | :x:                |

## Reporting a Vulnerability

We take the security of Attestix seriously. As a trust and attestation infrastructure project, security is foundational to our mission.

### Please Do

- **Report privately**: Use [GitHub Security Advisories](https://github.com/VibeTensor/attestix/security/advisories/new) to report vulnerabilities privately
- **Email us**: Send details to info@vibetensor.com
- **Provide details**: Include steps to reproduce, potential impact, and suggested fixes if any
- **Give us time**: Allow reasonable time for us to address the issue before public disclosure

### Please Don't

- **Don't open public issues** for security vulnerabilities
- **Don't exploit** the vulnerability beyond what's necessary to demonstrate it
- **Don't attempt** to access other users' data, credentials, or signing keys
- **Don't perform** denial of service attacks

## What to Include

When reporting a vulnerability, please include:

1. **Description** of the vulnerability
2. **Steps to reproduce** the issue
3. **Affected versions** of Attestix
4. **Affected module(s)** (identity, credentials, delegation, compliance, provenance, reputation, blockchain, DID, agent card)
5. **Potential impact** (what could an attacker do?)
6. **Suggested fix** (if you have one)

## Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 5 business days
- **Fix Timeline**: Depends on severity
  - Critical: 24-72 hours
  - High: 1-2 weeks
  - Medium: 2-4 weeks
  - Low: Next release cycle

## Security Architecture

### Cryptographic Foundation

- **Ed25519 signatures** (RFC 8032) for all identity and credential signing
- **SHA-256 hash chains** for tamper-evident audit trails
- **JSON Canonicalization Scheme** (RFC 8785) for deterministic hashing
- **PBKDF2** (480,000 iterations, SHA-256) for optional key encryption
- **RFC 6962 Merkle trees** with domain separation for batch anchoring

### Local-First Model

Attestix runs entirely on your local machine as an MCP server. There is no Attestix-hosted backend, no telemetry, and no data transmission to third parties unless you explicitly use blockchain anchoring.

### Key Management

- Ed25519 signing keys are generated locally and stored in the project directory
- Optional PBKDF2-based encryption when `ATTESTIX_KEY_PASSWORD` environment variable is set
- Private keys are never transmitted, logged, or included in MCP tool responses

### Blockchain (Optional)

- Blockchain anchoring is opt-in via Ethereum Attestation Service on Base L2
- Only cryptographic hashes are stored on-chain, never the underlying data
- Requires explicit user configuration of RPC endpoint and wallet private key

### Input Validation

- All 47 MCP tool parameters validated at entry points
- SSRF protection on DID resolution (did:web) with private IP blocking
- No shell command execution from user input
- No dynamic code evaluation

### Credential Integrity

- W3C Verifiable Credentials 1.1 with Ed25519Signature2020 proofs
- Mutable fields (proof, credentialStatus) excluded from signature per spec
- Credential verification re-derives public key from issuer DID for independent verification

## Files That Should Never Be Committed

| File Pattern | Contents |
|-------------|----------|
| `.env` | API keys, wallet private keys |
| `*.pem` / `*.key` | Private keys |
| `signing_key.json` | Ed25519 signing key |
| `credentials.json` | Service credentials |

If you accidentally commit any of these files:
1. Immediately rotate the exposed credentials
2. Remove the file from git history (BFG Repo-Cleaner or git filter-branch)
3. Regenerate all affected signing keys

## Contact

- **Security Email**: info@vibetensor.com
- **GitHub Security Advisories**: [Report here](https://github.com/VibeTensor/attestix/security/advisories/new)
