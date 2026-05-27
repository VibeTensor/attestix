# Implementation Plan: Attestix v0.4.0-rc.1 Extensibility Layer

**Branch**: `feature/spec-kit-v0.4.0-specs` | **Date**: 2026-05-27 | **Spec**: [spec.md](./spec.md)

**Classification**: INTERNAL

## Summary

Introduce five additive extension seams into the Attestix OSS engine so the hosted cloud
(and any self-hoster) can swap operational backends without forking: (1) a `Repository`
interface fronting persistence, (2) a `Signer` interface fronting Ed25519 signing, (3) an
optional `tenant_id` on every resource defaulting to `"default"`, (4) a structured
`AuditEvent` emitted on every committed state change, and (5) Stripe-style idempotency keys
with a 24-hour TTL on writes. The technical approach is to wrap, not rewrite: the canonical
service layer (`services/*.py`) currently calls module-level `config.load_*`/`save_*`
functions directly and holds an in-process Ed25519 private key; we insert the `Repository`
and `Signer` abstractions behind those exact call sites, default them to today's file +
in-process implementations, and inject alternatives through the existing service
construction path (`services/cache.py::get_service` / `api/deps.py`). All new behavior is
opt-in via defaults that reproduce v0.3.0 exactly.

## Technical Context

**Language/Version**: Python 3.10–3.13 (CI matrix per `.github/workflows/`).

**Primary Dependencies**: `cryptography` (Ed25519), `base58`, `PyJWT[crypto]`, `httpx`,
`filelock`, `click`, FastAPI + `starlette` (REST layer), `mcp[cli]` (MCP server). New
optional extras (proposed): `pg` (Postgres driver, e.g. `psycopg`/`asyncpg` or SQLAlchemy)
and `kms` (cloud KMS SDK). Both MUST be optional — default install adds no mandatory runtime
dependency (FR-026, SC-010).

**Storage**: Default = JSON files via `config.py` (`_safe_load`/`_safe_save`, `filelock`,
atomic temp-then-rename) under `DATA_DIR` (`~/.attestix` or `ATTESTIX_DATA_DIR`). New =
optional Postgres-backed adapter behind the same `Repository` contract.

**Testing**: pytest (`asyncio_mode = auto`), `pytest-asyncio`, `respx`, `pytest-cov`.
Existing suite layout: `tests/unit/`, `tests/integration/`, `tests/e2e/`,
`tests/benchmarks/` (the 91 RFC conformance benchmarks). New: `tests/contract/` for the
Repository and Signer contract suites.

**Target Platform**: Library + MCP stdio server (`main.py`) + FastAPI REST app
(`api/main.py`) + Click CLI (`cli.py`). Linux/macOS/Windows (POSIX chmod skipped on Windows).

**Project Type**: Single Python package with a dual layout — canonical flat modules
(`services/`, `auth/`, `blockchain/`, `tools/`, `api/`, plus top-level `config.py`,
`errors.py`, `cli.py`, `main.py`) and a namespace mirror (`attestix/*`) that re-exports the
flat modules for `from attestix.services... import` compatibility. Both ship to PyPI
(see `pyproject.toml [tool.setuptools] packages`).

**Performance Goals**: No regression versus v0.3.0 on the default path; the file Repository
must preserve current locking/atomic-write characteristics. Conformance-benchmark timings
(`tests/benchmarks/test_performance.py`) MUST not regress.

**Constraints**: Backward compatible (zero-config upgrade, FR-024/FR-025); MINOR SemVer bump
(0.3.0 → 0.4.0), additive only; defaults reproduce v0.3.0 byte-for-byte for signing
(SC-005) and on-disk format. EAS anchoring stays Base L2 Sepolia testnet only.

**Scale/Scope**: 9 services, 47 MCP tools, 44 REST endpoints, 358 existing tests. The seams
are uniform across the 7 persisted entity families (identities, credentials, delegations,
compliance, reputation, provenance, anchors).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate | Status |
|---|---|---|
| I. Open-core / never paywall conformance | All five interfaces ship in OSS (Apache-2.0); Postgres adapter + KMS/HSM signers are open; no proprietary primitive enters the verify/attest path. | PASS |
| II. Backward compat & SemVer | MINOR bump 0.3.0 → 0.4.0; all new behavior opt-in via `"default"` tenant, in-process signer, file storage; no public-surface break. | PASS (see Complexity Tracking for the one watched item) |
| III. Test-first & conformance-gated | Repository + Signer contract tests authored failing first; 358 existing tests stay green; 91 conformance benchmarks unaffected; adapters reuse the same contract suite. | PASS |
| IV. Standards fidelity | Ed25519/JCS/Merkle behavior unchanged; default signer output byte-identical (SC-005); EAS stays Base Sepolia testnet only. | PASS |
| V. Portability / zero lock-in | On-disk format preserved; legacy records without `tenant_id` read as `"default"`; exported data and anchors remain offline-verifiable. | PASS |
| VI. Security & least privilege | Fail-loud signer behavior preserved (`SigningKeyLoadError`); KMS/HSM keep private keys out of process; SSRF allowlist unchanged; secrets stay in env/config. | PASS |
| VII. Simplicity / additive | One default implementation per interface that preserves current behavior; Postgres/KMS built only because cloud M2 requires them; no speculative backends. | PASS |

**Initial Constitution Check: PASS.** No violation requires waiver. One backward-compat item
is tracked (the entity-shape addition of `tenant_id`) and shown below to be non-breaking.

## Project Structure

### Documentation (this feature)

```text
specs/001-v0.4.0-extensibility/
├── spec.md              # Feature specification (input to this plan)
├── plan.md              # This file
├── data-model.md        # Interface contracts (Repository, Signer, AuditEvent, IdempotencyKey, tenant_id)
└── tasks.md             # Task breakdown by user story
```

### Source Code (repository root)

The canonical implementation lives in the flat top-level modules; the `attestix/*` namespace
mirror re-exports them (`attestix/services/identity_service.py` is a one-line re-export of
`services.identity_service`). New modules therefore land in the flat layout and are
re-exported from the namespace mirror.

```text
# --- New extensibility modules (canonical flat layout) ---
storage/                          # NEW package: pluggable persistence
├── __init__.py
├── repository.py                 # Repository ABC (contract) + select_repository(config)
├── file_repository.py            # Default: wraps current config.py _safe_load/_safe_save behavior
└── pg_repository.py              # Optional [pg extra]: Postgres-backed adapter

signing/                          # NEW package: pluggable signer
├── __init__.py
├── signer.py                     # Signer ABC (sign / public_key / did) + select_signer(config)
├── inprocess_signer.py           # Default: wraps auth/crypto.py Ed25519 (byte-identical output)
└── kms_signer.py                 # Optional [kms extra]: KMS/HSM-backed adapter

audit/                            # NEW package: structured audit events
├── __init__.py
├── events.py                     # AuditEvent dataclass/schema + hash-chain linking (mirrors provenance prev_hash/chain_hash)
└── emitter.py                    # AuditEventEmitter: default local sink + injectable external sink

tenancy/                          # NEW module(s): tenant context
└── context.py                    # TenantContext, DEFAULT_TENANT = "default", resolver hook

idempotency/                      # NEW package: idempotency keys
├── __init__.py
├── store.py                      # IdempotencyStore ABC + default (file/Repository-backed) impl, 24h TTL
└── middleware.py                 # FastAPI BaseHTTPMiddleware honoring Idempotency-Key on writes

# --- Existing modules touched (seam insertion, no behavior change at default) ---
config.py                         # Storage functions become the file Repository's backing; keep public load_*/save_* as thin shims
auth/crypto.py                    # Stays the Ed25519 implementation the in-process Signer wraps; fail-loud guarantees preserved
errors.py                         # Add error categories for storage/signer/idempotency failures
services/identity_service.py      # Inject Repository + Signer; add tenant scoping; emit AuditEvent
services/credential_service.py    # (same pattern)
services/delegation_service.py    # (same pattern)
services/compliance_service.py    # (same pattern)
services/reputation_service.py    # (same pattern)
services/provenance_service.py    # (same pattern; already hash-chains its audit_log — align with AuditEvent)
services/did_service.py           # (resolution-only; tenant scoping where it persists)
services/agent_card_service.py    # (same pattern where it persists)
services/blockchain_service.py    # (same pattern; anchors.json via Repository)
services/cache.py                 # get_service(): pass selected Repository/Signer/tenant into constructors
api/deps.py                       # Wire selected backends + per-request tenant into service construction
api/main.py                       # Mount idempotency middleware; resolve tenant per request

# --- Namespace mirror (one-line re-exports added to match new flat modules) ---
attestix/storage/  attestix/signing/  attestix/audit/  attestix/tenancy/  attestix/idempotency/

tests/
├── contract/                     # NEW: Repository contract suite, Signer contract suite (run against every impl)
│   ├── test_repository_contract.py
│   └── test_signer_contract.py
├── unit/                         # Existing 267-functional set + new unit tests for tenancy/audit/idempotency
├── integration/                  # Existing + tenant-isolation + idempotency integration tests
├── e2e/                          # Existing persona/e2e — must stay green unchanged
└── benchmarks/                   # 91 RFC conformance benchmarks — unaffected, hard gate
```

**Structure Decision**: Add five small, self-contained packages (`storage/`, `signing/`,
`audit/`, `tenancy/`, `idempotency/`) at the canonical flat layer, each with a single default
implementation that wraps today's behavior, plus optional adapters (`pg_repository.py`,
`kms_signer.py`) behind optional extras. Services are refactored to depend on the
`Repository` and `Signer` interfaces instead of calling `config.load_*`/`save_*` and holding
a raw private key; `config.py` retains its public `load_*`/`save_*` functions as thin shims
so any external caller relying on them keeps working (II, VII). Backend selection flows
through the existing construction seam (`services/cache.py::get_service` and `api/deps.py`),
so default callers get file storage + in-process signer + `"default"` tenant with no
configuration. The namespace mirror (`attestix/*`) gains matching one-line re-exports.

## Complexity Tracking

> The Constitution Check passed. The table records the one item that touches the
> backward-compatibility gate and must be verified non-breaking during implementation; it is
> NOT an approved deviation.

| Item | Why it is needed | Why it remains non-breaking (gate II / V) |
|---|---|---|
| Adding `tenant_id` to every persisted resource entity | Required for multi-tenant isolation (FR-011/FR-012) and as the scope for audit events and idempotency keys | Field is optional and defaults to `"default"`; legacy records without it are read as `"default"` (FR-013); on-disk format is a superset, so v0.3.0 readers and the existing 358 tests are unaffected. Verified by SC-001/SC-002 and a round-trip test on pre-upgrade fixture data. If any consumer is found to reject unknown fields, that surfaces here as a real violation requiring a MAJOR-bump decision. |
