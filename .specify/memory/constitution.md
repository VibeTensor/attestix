# Attestix Constitution

Attestix is the open-source (`VibeTensor/attestix`, Apache-2.0) attestation engine for
AI agents: DID-based identity, W3C Verifiable Credentials, UCAN delegation, EU AI Act /
GDPR conformance records, reputation, provenance, and EAS anchoring on Base L2 (Sepolia
testnet only). This constitution governs how the OSS engine evolves. It binds every
specification, plan, and pull request in this repository. Where the open-core contract
(`attestix-cloud-plan/02-OPEN-CORE.md`) and this document overlap, the open-core promises
quoted below are authoritative.

## Core Principles

### I. Open-Core, Never Paywall Conformance

The engine ships under Apache-2.0 and stays that way. Every primitive in the critical path
is open: all 9 services, all 47 MCP tools, all 44 REST endpoints, the CLI, Ed25519
signing/verification, JCS canonicalisation, RFC 6962 Merkle, EAS schema encoding, W3C VC
issuance/verification, W3C DID resolution, and UCAN delegation. We will NEVER paywall
standards conformance: every claim Attestix makes about EU AI Act, GDPR, W3C VC, W3C DID,
UCAN, EAS, RFC 8032, RFC 8785, or RFC 6962 MUST be auditable from the OSS alone, with no
proprietary dependency. New extensibility interfaces (storage, signer, tenancy, audit,
idempotency) that the hosted cloud needs MUST land in the OSS so self-hosters can run the
same multi-tenant / KMS / Postgres deployments. No proprietary primitive may sit in the
verification or attestation path.

### II. Backward Compatibility & SemVer Discipline

The public API (Python service classes, MCP tool surface, REST endpoints, CLI flags,
on-disk data formats, and the documented wire format of exported bundles) is a contract.
Releases follow SemVer (MAJOR.MINOR.PATCH). A MINOR bump (e.g., 0.3.0 → 0.4.0) is additive
only: new behavior MUST be opt-in via defaults that reproduce the prior version's behavior
exactly. A breaking change to any public surface requires a MAJOR bump AND a documented
migration path. Existing installs MUST keep working with zero configuration change across a
MINOR or PATCH upgrade. Any unavoidable break in a non-MAJOR release is a constitution
violation and MUST be justified in the plan's Complexity Tracking before work begins.

### III. Test-First & Conformance-Gated (NON-NEGOTIABLE)

The full suite (358 tests: 267 functional + 91 RFC conformance benchmarks) MUST stay green
on every PR across Python 3.10–3.13. The 91 conformance benchmarks
(`tests/benchmarks/`, covering RFC 8032 Ed25519, RFC 8785 JCS, W3C VC, W3C DID, UCAN, MCP)
encode the standards-fidelity guarantees and MUST NOT regress; a change that alters
conformance behavior is presumed wrong until proven a standards correction. Every new public
interface (e.g., a Repository or Signer abstraction) ships with contract tests written and
failing before the implementation, and any concrete adapter MUST pass the same contract test
suite as the default implementation. No PR merges with a failing or skipped-for-convenience
test.

### IV. Standards Fidelity

Attestix's value is that its conformance is real and verifiable. Cryptography and encoding
MUST follow the cited specifications precisely: Ed25519 (RFC 8032), JSON Canonicalization
Scheme (RFC 8785), Merkle audit logs (RFC 6962), SHA-256, PBKDF2; W3C Verifiable
Credentials 1.1, W3C DID 1.0, UCAN v0.9.0, MCP 1.8+, and EAS schema encoding. On-chain
anchoring targets EAS on Base L2 Sepolia **testnet only** — all code, docs, and copy MUST
preserve the testnet qualifier; mainnet schema registration is out of scope until explicitly
ratified. Standards claims without a passing conformance benchmark are not permitted.

### V. Portability & Zero Lock-In

Users own their data and trust. All resources MUST be exportable in standard, documented
formats (JSON/JSONL and the published bundle wire format). Anchor proofs MUST verify
offline against Base independently of any Attestix service. DIDs and VCs MUST be verifiable
by any third party without contacting Attestix infrastructure. A self-hoster MUST be able to
leave at any time with their data intact and their attestations independently checkable. No
feature may introduce a dependency that makes exported data unusable outside Attestix.

### VI. Security & Least Privilege

The server signing key is the root of trust for every UAIT, delegation, credential, and
anchor; it MUST NEVER be silently rotated or regenerated when an existing key is present
(see `auth/crypto.py::SigningKeyLoadError`). Key material MUST be stored with least-privilege
permissions and may be encrypted at rest. Outbound requests MUST pass SSRF allowlist checks
(`auth/ssrf.py`). Secrets MUST come from environment/config, never source or data files.
New signer backends (KMS, HSM) MUST keep private key material out of the engine's process
when the backend supports it, and MUST NOT weaken the existing fail-loud key-loading
guarantees. Inputs at every boundary (REST, MCP, CLI) MUST be validated.

### VII. Simplicity & Additive Change

Prefer the smallest change that satisfies the requirement. New abstractions are justified
only when they remove a concrete, present duplication or enable a committed requirement
(YAGNI). Extensibility seams are introduced behind interfaces with a single default
implementation that preserves current behavior; speculative backends are not built without a
consuming requirement. Complexity that cannot be tied to a principle or a committed need is
rejected in review.

## Additional Constraints

- **Language/runtime**: Python 3.10–3.13. Public dependencies are pinned with lower and
  upper bounds (see `pyproject.toml`) to prevent silent breakage on fresh installs.
- **Optional, never required**: Heavy or operational dependencies (Postgres driver, web3,
  KMS SDKs, WeasyPrint) MUST be optional extras. A default `pip install attestix` MUST
  remain file-storage + in-process-signer with no external services.
- **Defaults reproduce v0.3.0**: tenant context defaults to `"default"`; signer defaults to
  the in-process Ed25519 key; storage defaults to the JSON/file repository writing to
  `DATA_DIR` (`~/.attestix` or `ATTESTIX_DATA_DIR`).

## Development Workflow & Quality Gates

- Specifications and plans MUST include a Constitution Check that maps each principle to a
  concrete gate (PASS / violation). Violations MUST be recorded in Complexity Tracking with a
  justification and the simpler alternative that was rejected.
- CI gates (per `.github/workflows/`): pytest matrix on Python 3.10–3.13, lint (ruff), type
  (mypy), security (bandit / pip-audit), SBOM, and publish. All MUST pass before merge.
- New public interfaces require contract tests under `tests/`; adapters reuse the same
  contract suite. Conformance benchmarks under `tests/benchmarks/` are a hard gate.
- The CHANGELOG and ROADMAP MUST be updated for any user-visible change.

## Governance

This constitution supersedes ad-hoc practice. Amendments require a PR that updates this file,
states the rationale, and bumps the version line per the policy below; reviewers MUST verify
that every gate is addressed.

- **License**: The OSS remains Apache-2.0. We will not change the OSS license away from
  Apache-2.0 without at least 12 months public notice, and every release made under Apache-2.0
  stays Apache-2.0.
- **Contributions**: Community PRs are accepted under the Developer Certificate of Origin
  (DCO) sign-off (no CLA). Cloud-only changes are out of scope for this repo.
- **Trademark**: "Attestix" is a registered trademark of VIBETENSOR PRIVATE LIMITED. Forks
  may use the code under Apache-2.0 but MUST NOT use the Attestix name or logo for
  distribution.
- **Amendment versioning**: MAJOR for a backward-incompatible governance/principle removal or
  redefinition; MINOR for a new principle or materially expanded guidance; PATCH for
  clarifications and wording. The version line below MUST be updated on every amendment.

**Version**: 1.0.0 | **Ratified**: 2026-05-27 | **Last Amended**: 2026-05-27
