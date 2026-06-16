# Extensibility Layer (v0.4.0)

v0.4.0 adds five **additive, opt-in** extension seams so the same engine can be operated
multi-tenant, on an external database, with KMS-held keys, an external audit log, and
idempotent writes, without forking. Every default reproduces v0.3.0 behavior exactly: a
self-host install that changes no configuration sees no difference (file storage, in-process
Ed25519 signer, single implicit `default` tenant, no idempotency bookkeeping).

| Seam | Package | Default | Opt-in alternative |
|---|---|---|---|
| Storage | `storage/` | `FileRepository` (JSON files) | `MemoryRepository`; Postgres (`[pg]` extra) |
| Signer | `signing/` | `InProcessSigner` (Ed25519) | KMS / HSM (`[kms]` extra) |
| Tenant context | `tenancy/` | tenant `"default"` | header / injected resolver |
| Audit events | `audit/` | local sink (Repository) | injected external sink |
| Idempotency | `idempotency/` | unmounted (no key → v0.3.0) | opt-in REST middleware / `run_idempotent` |

## Tenant context

Every persisted record carries an optional `tenant_id` (default `"default"`). Tenant scoping is
enforced at the `Repository` boundary: a record created under tenant A is never returned under
tenant B. **Legacy v0.3.0 records that have no `tenant_id` field read as tenant `"default"`**:
the upgrade path requires no migration. The default resolver
(`tenancy.context.resolve_tenant`) reads an optional `X-Attestix-Tenant` header and otherwise
resolves to `"default"`.

## Structured audit events

Each committed state change can emit exactly one `AuditEvent`, chained with the same
`prev_hash` / `chain_hash` / genesis pattern as the existing provenance audit log, so a
sequence is tamper-evident (`audit.verify_chain`). A no-op update emits an event like any other
committed change; a failed operation emits none.

### Encryption-at-rest for audit events (FR-028)

`AuditEvent.actor` (an identity / DID) and `AuditEvent.target_id` **may constitute personal
data** under DPDP Act 2023 §2(t) and GDPR Art.4(1) when integrators put personal identifiers in
those fields.

- The default **file** `Repository` is the **self-host / dev default** and stores audit events
  as **plaintext JSON on disk**. Hash-chaining provides *tamper-evidence*, NOT *confidentiality*.
- Any **production or multi-tenant** deployment that persists `AuditEvent` records **MUST use an
  encrypted-at-rest Repository** (e.g. Postgres with KMS or disk-level at-rest encryption).
- No raw secret or private-key material is ever placed in the event body: `change_digest` is a
  SHA-256 over the canonical change, not the change itself.

## Idempotency keys

A client may supply an idempotency key so a retried write returns the original result instead of
creating a duplicate. Keys expire after **24 hours** (Stripe-style) and are reclaimable so the
store does not grow unbounded. Keys are scoped per tenant. The default file store is
**first-writer-wins via the existing `filelock`**; multi-worker deployments need an external
store (Postgres).

The store and the `run_idempotent` helper are surface-agnostic (usable from REST, MCP, or direct
service calls). The REST `IdempotencyMiddleware` ships but is **not auto-mounted** in v0.4.0
P3: the default app keeps exact v0.3.0 request handling (no key → no bookkeeping). Operators
opt in with `app.add_middleware(IdempotencyMiddleware)`.

### Minimal stored representation (FR-029)

The idempotency record **never persists raw private-key material** and stores only a **minimal
representation** of the original response: `status` + `resource_id` + `response_hash` (a
SHA-256 over the canonical response). This avoids keeping a second unencrypted copy of a signed
credential or identity data for the 24-hour window while still letting a replay confirm and
return a stable result.
