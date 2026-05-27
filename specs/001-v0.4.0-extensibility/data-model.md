# Data Model & Interface Contracts: v0.4.0 Extensibility Layer

**Branch**: `feature/spec-kit-v0.4.0-specs` | **Date**: 2026-05-27 | **Spec**: [spec.md](./spec.md)

**Classification**: INTERNAL

This document defines the contract-level shape of the five extension seams: the `Repository`
and `Signer` interfaces, the `AuditEvent` schema, the `IdempotencyKey` record, and the
`tenant_id` field. Signatures are given at the contract level (method names, inputs,
outputs, invariants) and are illustrative Python; the binding requirements are the
invariants, not the exact type hints. Each section also notes how the Postgres adapter and
KMS signer map onto the contract.

## Conventions

- `tenant_id: str` — defaults to `"default"`. A record with no `tenant_id` is read as
  `"default"` (FR-013).
- Timestamps are ISO-8601 UTC strings (matching existing services, e.g.
  `datetime.now(timezone.utc).isoformat()`).
- Resource collections map to today's seven entity families: `identities`, `credentials`,
  `delegations`, `compliance`, `reputation`, `provenance`, `anchors`.
- Canonicalization for any signing/hashing reuses the existing JCS (RFC 8785) helper
  `auth.crypto.canonicalize_json`.

## 1. Repository (FR-001…FR-005)

The persistence boundary. Replaces direct `config.load_*`/`save_*` calls in services. A
collection is identified by name; records are dicts (the engine's existing in-memory shape).
The Repository is responsible for tenant scoping at the boundary.

```python
class Repository(ABC):
    @abstractmethod
    def create(self, collection: str, record: dict, *, tenant_id: str = "default") -> dict: ...
    @abstractmethod
    def get(self, collection: str, record_id: str, *, tenant_id: str = "default") -> dict | None: ...
    @abstractmethod
    def list(self, collection: str, *, tenant_id: str = "default",
             filters: dict | None = None, limit: int | None = None) -> list[dict]: ...
    @abstractmethod
    def update(self, collection: str, record_id: str, record: dict,
               *, tenant_id: str = "default") -> dict: ...
    @abstractmethod
    def delete(self, collection: str, record_id: str, *, tenant_id: str = "default") -> bool: ...
```

**Invariants (the contract test asserts all of these against every implementation):**

- **Round-trip**: `get(c, create(c, r).id) == r` (modulo storage-assigned metadata).
- **Tenant isolation**: a record created under tenant A is never returned by `get`/`list`
  under tenant B (FR-012, SC-006).
- **Default tenant**: omitting `tenant_id` is equivalent to passing `"default"` (FR-011,
  FR-014).
- **Legacy read**: a record persisted without a `tenant_id` field is returned under tenant
  `"default"` (FR-013).
- **Idempotent delete**: `delete` of a missing id returns `False`, does not raise.
- **No cross-tenant merge**: identical `record_id` under two tenants are two distinct records.
- **Durability/atomicity**: a failed write surfaces an error and does not partially corrupt
  other records (the file impl preserves the current temp-then-rename + filelock guarantee).

**Selection**: `select_repository(config) -> Repository` returns the file impl by default;
returns the Postgres impl only when explicitly configured (e.g.
`ATTESTIX_STORAGE=postgres` + DSN). Default install → file (FR-005).

### Default file adapter (`storage/file_repository.py`)

Wraps the existing `config.py` machinery. Each `collection` maps to its current JSON file
(`IDENTITIES_FILE`, `CREDENTIALS_FILE`, …) under `DATA_DIR`. Read/write go through the
existing `_safe_load`/`_safe_save` (filelock + atomic rename), preserving v0.3.0 on-disk
format and concurrency behavior. `config.load_*`/`save_*` remain as thin public shims over
this adapter so external callers are unaffected.

### Postgres adapter (`storage/pg_repository.py`, `[pg]` extra)

Each `collection` maps to a table (or a shared `resources` table keyed by `(collection,
tenant_id, record_id)` with a JSONB body). `tenant_id` is a first-class indexed column;
tenant isolation is enforced in the query layer (and optionally Postgres RLS in the cloud).
Must pass the identical `Repository` contract suite (FR-004, SC-003). Connection/driver is an
optional dependency; importing it without the extra installed raises a clear, actionable
error.

## 2. Signer (FR-006…FR-010)

The signing boundary. Replaces services holding `self._private_key` directly. Exposes signing
over a canonicalized payload and disclosure of the public identity, never the private key.

```python
class Signer(ABC):
    @abstractmethod
    def sign(self, payload: dict) -> str:        # base64url signature over JCS-canonical payload
        ...
    @abstractmethod
    def public_key(self) -> Ed25519PublicKey:    # for verification
        ...
    @property
    @abstractmethod
    def did(self) -> str:                         # did:key (or did:web) of the signer
        ...
```

**Invariants (Signer contract test, run against every implementation):**

- **Verifiable**: `verify_json_signature(signer.public_key(), payload, signer.sign(payload))`
  is `True` (uses the existing `auth.crypto` verify path) (FR-009).
- **Deterministic identity**: `did` is stable for the life of the signer and matches
  `public_key()`.
- **No private-key leakage**: the interface exposes no API returning private key bytes; KMS/
  HSM impls hold no private material in process (FR-008, principle VI).
- **Fail loud**: if the backend is unavailable, `sign`/construction raises a clear error and
  never substitutes or regenerates a key (FR-010; preserves
  `auth.crypto.SigningKeyLoadError` semantics).
- **Default parity**: the in-process Ed25519 signer's `sign(payload)` is byte-identical to
  v0.3.0 `sign_json_payload(self._private_key, payload)` for the same input (SC-005).

**Selection**: `select_signer(config) -> Signer` returns the in-process Ed25519 signer by
default; returns KMS/HSM only when explicitly configured (e.g. `ATTESTIX_SIGNER=kms` + key
ARN). Default install → in-process (FR-007).

### Default in-process adapter (`signing/inprocess_signer.py`)

Wraps `auth/crypto.py`: constructs via `load_or_create_signing_key()` (keeping its fail-loud
behavior), `sign()` delegates to `sign_json_payload`, `public_key()` derives from the loaded
key, `did` is the loaded `did:key`. Byte-for-byte identical to v0.3.0.

### KMS / HSM adapter (`signing/kms_signer.py`, `[kms]` extra)

`sign()` canonicalizes with `auth.crypto.canonicalize_json` locally, then calls the KMS/HSM
to sign the canonical bytes with an Ed25519 key held in the HSM; `public_key()`/`did` are
fetched from KMS metadata. The engine never sees private bytes. Must pass the identical
Signer contract suite (SC-004).

## 3. tenant_id field (FR-011…FR-014)

A single optional field added to every persisted resource and to audit/idempotency records.

| Field | Type | Default | Notes |
|---|---|---|---|
| `tenant_id` | string | `"default"` | Indexed in Postgres; absent in legacy JSON records → read as `"default"`. |

The on-disk JSON shape becomes a **superset** of v0.3.0 (one new optional key), so existing
readers and the 358 tests are unaffected (Complexity Tracking item, SC-001/SC-002). Tenant
resolution at the boundary (REST/MCP → `tenant_id`) is provided via a resolver hook in
`tenancy/context.py`; the OSS default resolves to `"default"`. [NEEDS CLARIFICATION: whether
the OSS ships a concrete REST tenant-resolution mechanism or leaves it to the integrator —
see spec Assumptions.]

## 4. AuditEvent (FR-015…FR-018)

A structured record emitted once per committed state change, chainable into a tamper-evident
log. The shape mirrors the precedent already in `services/provenance_service.py`
(`prev_hash` / `chain_hash` / `GENESIS_HASH`).

```python
@dataclass(frozen=True)
class AuditEvent:
    event_id: str           # e.g. "evt:<uuid12>"
    tenant_id: str          # default "default"
    actor: str              # acting identity / DID (e.g. server DID or caller)
    action: str             # e.g. "identity.create", "credential.revoke"
    target_id: str          # id of the affected resource
    target_collection: str  # e.g. "identities"
    occurred_at: str        # ISO-8601 UTC
    change_digest: str      # SHA-256 over JCS-canonical {before?, after} of the change
    prev_hash: str          # chain_hash of the prior event (GENESIS for first)
    chain_hash: str         # SHA-256( prev_hash + change_digest + occurred_at + ... )
```

**Schema rules:**

- Emitted **after** a successful commit; a failed operation emits no success event (FR-018).
- Exactly one event per state-changing operation (FR-015, SC-007).
- `chain_hash` links to `prev_hash` so any tampering breaks verification (FR-016, SC-007),
  consistent with the existing provenance hash chain.
- `change_digest` uses SHA-256 over the JCS-canonical form of the change (no raw secret/key
  material is included in the event body — principle VI).

**Emitter** (`audit/emitter.py`): default sink appends locally (preserving today's local
audit behavior); an injectable sink lets an external consumer (cloud) receive events for an
external hash-chained log (FR-017). The emitter computes `prev_hash`/`chain_hash` per tenant.
[NEEDS CLARIFICATION: whether a no-op update emits an event or is suppressed — see spec Edge
Cases.]

> **PII / encryption-at-rest note (FR-028).** `actor` (an identity / DID) and `target_id`
> may constitute personal data under DPDP Act 2023 §2(t) and GDPR Art.4(1) when integrators
> store personal identifiers in these fields. The default **file** Repository is the
> self-host / dev default and stores audit events as **plaintext JSON on disk** (it only
> provides hash-chaining for tamper-evidence, not confidentiality). Any production or
> multi-tenant deployment that persists `AuditEvent` records MUST use an **encrypted-at-rest**
> Repository — e.g., Postgres with KMS / disk-level at-rest encryption — so PII-bearing audit
> fields are not stored in cleartext. Hash-chaining is an integrity control and is NOT a
> substitute for encryption-at-rest.

## 5. IdempotencyKey (FR-019…FR-023)

A client-supplied token that makes a write replay-safe for 24 hours.

```python
@dataclass
class IdempotencyKey:
    key: str                # client-supplied (e.g. Idempotency-Key header)
    tenant_id: str          # scope; default "default"
    request_fingerprint: str  # SHA-256 over JCS-canonical request payload (+ method + path)
    stored_response: dict   # minimal replay record: {status, resource_id, response_hash}
                            #   (NEVER raw private key material; sensitive fields such as
                            #    signed VCs / identity data are redacted or encrypted — FR-029)
    status: str             # "in_progress" | "completed"
    created_at: str         # ISO-8601 UTC; TTL = created_at + 24h
```

**Rules:**

- First use with a given `(tenant_id, key)`: record `in_progress`, perform the write, store
  the result, mark `completed` (FR-019).
- Replay with same key + same `request_fingerprint` within TTL: return `stored_response`, do
  not re-execute (FR-019, SC-008).
- Same key + different `request_fingerprint`: reject with a conflict (HTTP 409-style)
  (FR-020).
- Record older than 24h: treated as new; write proceeds (FR-021, SC-008).
- No key supplied: no bookkeeping, behaves as v0.3.0 (FR-022).
- Scoped per tenant: keys never collide across tenants (FR-023).
- Expired records reclaimable (TTL cleanup) so the store does not grow unbounded (FR-021).
- **Sensitive-data minimization (FR-029)**: the idempotency record MUST NOT persist raw
  private key material (never). The stored response SHOULD be a **minimal representation**
  — `status` + resource id + a `response_hash` (SHA-256 over the JCS-canonical original
  response) sufficient to confirm a replay and return a stable result — OR sensitive fields
  (signed VCs, identity data) MUST be redacted / encrypted before storage. This avoids keeping
  a second unencrypted copy of signed credentials or identity data for the 24-hour window. The
  24-hour TTL is retained regardless of which representation is chosen.

**Storage of idempotency keys**: persisted through the `Repository` (a dedicated
`idempotency` collection) so the default install uses file storage and the cloud uses
Postgres automatically. TTL is enforced on read (expired → ignored) plus a periodic reclaim.
The default file-backed store is single-process; concurrency guarantees beyond
first-writer-wins-via-lock are out of scope for the default impl. [NEEDS CLARIFICATION:
exact concurrency guarantee for the default (file) idempotency store under concurrent
same-key requests — see spec Edge Cases.]

**Boundary**: enforced primarily at the REST layer via `idempotency/middleware.py`
(a `BaseHTTPMiddleware`, matching the existing middleware pattern in `api/main.py`) reading
an `Idempotency-Key` header on `POST`/write endpoints. [NEEDS CLARIFICATION: whether MCP
tools and direct service calls also accept idempotency keys, or REST-only — see spec
Assumptions.]

## Cross-reference: where each contract attaches in the codebase

| Contract | Attaches at | Default preserves |
|---|---|---|
| Repository | `services/*.py` (replaces `config.load_*`/`save_*` calls); selected in `services/cache.py` / `api/deps.py` | `config.py` file format, filelock, atomic write |
| Signer | `services/*.py` (replaces `self._private_key`); selected in same place | `auth/crypto.py` Ed25519 byte-for-byte |
| tenant_id | every persisted record; resolver in `tenancy/context.py` | absent → `"default"` |
| AuditEvent | emitted by each service on commit; emitter in `audit/` | provenance-style local hash chain |
| IdempotencyKey | `idempotency/middleware.py` on `api/main.py` writes; stored via Repository | no key → v0.3.0 behavior |
