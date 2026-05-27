# Feature Specification: Attestix v0.4.0-rc.1 Extensibility Layer

**Feature Branch**: `feature/spec-kit-v0.4.0-specs`

**Created**: 2026-05-27

**Status**: Draft

**Classification**: INTERNAL

**Input**: User description: "Five additive changes that let the hosted cloud wrap the
Attestix OSS engine without forking it, while self-host keeps working unchanged: pluggable
storage, pluggable signer, tenant context, structured audit events, and idempotency keys."

## Overview

Attestix v0.3.0 is a single-tenant engine that writes JSON files to a local data directory
and signs with one in-process Ed25519 key. The hosted cloud (a separate, private product)
needs to run the same engine multi-tenant, on Postgres, with KMS-held keys, an external
hash-chained audit log, and idempotent writes — **without forking the engine**. This feature
introduces five extension seams in the OSS so the cloud can inject its operational backends
while every existing self-host install keeps working with zero configuration change.

Per the open-core contract, these interfaces ship in the OSS (Apache-2.0) so self-hosters
can also run multi-tenant + KMS + Postgres if they choose. This is a MINOR, additive release
(0.3.0 → 0.4.0): no breaking change to any public surface, all new behavior opt-in via
defaults that reproduce v0.3.0 behavior.

## User Scenarios & Testing *(mandatory)*

The "users" of this feature are integrators of the engine: self-hosters running the OSS,
operators standing up a multi-tenant deployment, and the downstream cloud team (cloud
Milestone M2 is the first consumer and is blocked on the P1 stories).

### User Story 1 - Swap storage and signing backends without forking (Priority: P1)

An operator (or the cloud team) wants to run the unchanged Attestix service layer against
Postgres instead of JSON files, and have it sign with AWS KMS instead of an in-process key,
by selecting backends at startup — not by editing service code. A self-hoster who does
nothing keeps file storage and the in-process Ed25519 signer exactly as in v0.3.0.

**Why this priority**: This is the load-bearing seam. Cloud M2 (identities + credentials on
Postgres with KMS keys) cannot start until services read/write through a `Repository`
interface and sign through a `Signer` interface. It is also the highest backward-compat risk
(every service touches storage and signing today), so it must be proven first. Storage and
signer are grouped because the same services and the same contract-test discipline cover
both, and M2 needs both together.

**Independent Test**: Configure the engine with the default file repository and in-process
signer and confirm the full v0.3.0 test suite passes unchanged. Then point the same service
methods at an alternate Repository implementation (e.g., an in-memory or Postgres adapter)
and an alternate Signer (e.g., a stub KMS signer) and confirm both pass the identical
Repository/Signer contract test suites and that issued artifacts still verify.

**Acceptance Scenarios**:

1. **Given** a fresh v0.3.0 install with no extra configuration, **When** any service
   creates and reads a resource, **Then** it reads/writes JSON files under the default data
   directory exactly as v0.3.0 did, with identical on-disk format.
2. **Given** the engine configured to use a Postgres-backed Repository, **When** the same
   service method that previously wrote a JSON file is invoked, **Then** the resource is
   persisted and retrieved through the adapter with no change to the service's public method
   signature.
3. **Given** any concrete Repository implementation, **When** the Repository contract test
   suite runs against it, **Then** all create/get/list/update/delete and isolation
   assertions pass identically for the file adapter and the Postgres adapter.
4. **Given** the engine configured to use the in-process Ed25519 signer (default), **When**
   a credential is issued, **Then** the signature verifies and is byte-identical to v0.3.0
   output for the same input.
5. **Given** the engine configured to use a KMS-backed Signer, **When** a credential is
   issued, **Then** the signature verifies against the signer's public key and the engine
   never holds the private key material in process.
6. **Given** a Signer backend that is unreachable at startup, **When** the engine attempts to
   sign, **Then** it fails loud with a clear error and does NOT silently fall back to a
   different key or regenerate one.

---

### User Story 2 - Isolate tenants and emit a verifiable audit event per change (Priority: P2)

An operator running a multi-tenant deployment needs every resource scoped to a `tenant_id`
so tenant A can never read tenant B's data, and needs every state-changing operation to emit
a single structured audit event suitable for feeding an external hash-chained log. A
self-hoster who never sets a tenant transparently uses tenant `"default"` and sees no
behavior change.

**Why this priority**: Tenancy and structured events are what make the engine safe to operate
for more than one customer and auditable at scale, but they sit on top of the P1 seam (an
event needs the repository to record against; tenant scoping is enforced at the repository
boundary). The cloud can begin M2 with P1 alone (single-tenant smoke) and layer P2 in.
Grouped because both are cross-cutting per-resource concerns enforced at the same boundary.

**Independent Test**: With the default configuration, confirm all resources carry
`tenant_id == "default"` and existing reads/lists are unaffected. Then create resources under
two distinct tenant contexts and confirm a list/get under one tenant never returns the other
tenant's resources. Separately, invoke each state-changing operation and assert exactly one
structured audit event is emitted with the documented shape (actor, tenant, action, target,
timestamp, before/after digest) and that a sequence of events forms a verifiable hash chain.

**Acceptance Scenarios**:

1. **Given** a self-host install with no tenant configured, **When** a resource is created,
   **Then** it is stored with `tenant_id == "default"` and all existing lookups behave
   exactly as v0.3.0.
2. **Given** resources created under tenant `acme` and tenant `globex`, **When** a list is
   requested in the `acme` tenant context, **Then** only `acme` resources are returned and
   no `globex` resource is visible.
3. **Given** a request with no resolvable tenant in a context that requires one, **When** a
   write is attempted, **Then** the operation is rejected with a clear error rather than
   defaulting silently to another tenant's scope.
4. **Given** any state-changing service operation, **When** it completes successfully,
   **Then** exactly one structured audit event is emitted containing actor identity, tenant,
   action name, target resource id, UTC timestamp, and a digest of the change.
5. **Given** a sequence of emitted audit events, **When** they are linked, **Then** each event
   references the prior event's hash so tampering with any event invalidates the chain (same
   chaining property as the existing provenance audit log).
6. **Given** a state-changing operation that fails, **When** the failure occurs, **Then** no
   success audit event is emitted (events reflect committed state changes only).

---

### User Story 3 - Make writes idempotent under client retries (Priority: P3)

An API client that retries a `POST`/write (network blip, timeout, at-least-once delivery)
wants to supply an idempotency key so a retried request returns the original result instead
of creating a duplicate resource. Keys expire after 24 hours (Stripe-style). A self-hoster
who never sends an idempotency key sees no change in behavior.

**Why this priority**: Idempotency is a robustness improvement that matters most at cloud
scale and for automated retries; it is valuable but not a prerequisite for cloud M2's core
data path, so it ships last. It depends on the P1 storage seam (keys must be persisted) and
benefits from P2 tenant scoping (keys are scoped per tenant).

**Independent Test**: Send a write with an idempotency key, then replay the identical request
with the same key and confirm the second response matches the first and no second resource is
created. Confirm a different payload with the same key is rejected as a conflict, and that a
key older than the TTL no longer suppresses a new create.

**Acceptance Scenarios**:

1. **Given** a write request carrying an idempotency key not seen before, **When** it
   succeeds, **Then** the result and the key→result mapping are recorded.
2. **Given** an identical write replayed with the same idempotency key within the TTL,
   **When** it is received, **Then** the original stored response is returned and no duplicate
   resource is created.
3. **Given** a request reusing a stored idempotency key but with a different request payload,
   **When** it is received, **Then** the request is rejected with a conflict error.
4. **Given** an idempotency key whose record is older than the 24-hour TTL, **When** the same
   key is used again, **Then** the key is treated as new and the write proceeds normally.
5. **Given** a write that does not carry any idempotency key, **When** it is received, **Then**
   it behaves exactly as v0.3.0 (no idempotency bookkeeping).

---

### Edge Cases

- **Missing tenant_id on legacy data**: existing v0.3.0 JSON records have no `tenant_id`
  field. On read, a record without `tenant_id` MUST be treated as belonging to tenant
  `"default"` so existing data remains visible after upgrade.
- **Signer backend unavailable / credentials expired mid-run**: signing MUST fail loud with a
  clear error; the engine MUST NOT silently regenerate or substitute a key (preserves the
  existing `SigningKeyLoadError` fail-loud guarantee).
- **Duplicate idempotency key, same payload**: return the stored original response (success
  path), do not re-execute the write.
- **Duplicate idempotency key, different payload**: reject as a conflict; do not overwrite the
  stored result.
- **Concurrent requests with the same idempotency key**: only one write may take effect;
  concurrent duplicates resolve to the same stored result (the underlying store must support
  a first-writer-wins guarantee). **Resolved (T046):** the default file store is
  first-writer-wins via the file Repository's existing `filelock` + atomic rename; the helper
  reserves the key before executing and a concurrent same-key call observing a non-expired
  record does not re-execute. Multi-worker guarantees require an external store (Postgres).
- **Storage adapter failure mid-write** (DB connection drop, disk full, lock timeout): the
  operation MUST surface an error and MUST NOT emit a success audit event; partial writes MUST
  not corrupt other tenants' data.
- **Cross-tenant id collision**: the same resource id created under two tenants MUST be
  distinct records, never merged.
- **Idempotency key store growth**: expired keys MUST be reclaimable so the store does not
  grow unbounded (TTL-based cleanup).
- **Audit event for a no-op update** (update that changes nothing): **Resolved (T046):** a
  no-op update emits one event like any other committed mutating operation; the `change_digest`
  captures before/after so a downstream consumer can detect the no-op. The engine does not
  special-case suppression (keeps FR-015 "exactly one event per state-changing operation"
  uniform).

## Requirements *(mandatory)*

### Functional Requirements

**Pluggable storage (P1)**

- **FR-001**: The system MUST define a storage abstraction (Repository) that every service
  uses for persistence, replacing direct file-IO calls in the service layer.
- **FR-002**: The system MUST provide a default file-backed Repository implementation that
  reproduces v0.3.0 JSON on-disk behavior (same file locations, same format, same locking and
  atomic-write guarantees).
- **FR-003**: The system MUST allow selecting an alternative Repository implementation (e.g.,
  Postgres-backed) at configuration/startup time without modifying service code.
- **FR-004**: Any Repository implementation MUST satisfy a single shared contract test suite;
  the Postgres adapter MUST pass the same suite as the file adapter.
- **FR-005**: Selecting a non-default Repository MUST be opt-in; a default install MUST use
  the file Repository with no configuration.

**Pluggable signer (P1)**

- **FR-006**: The system MUST define a Signer abstraction that the service layer uses to sign
  and to expose the signer's public key / DID, replacing direct in-process key usage in
  services.
- **FR-007**: The system MUST provide a default in-process Ed25519 Signer that reproduces
  v0.3.0 signatures byte-for-byte for the same input and preserves the existing fail-loud
  key-loading behavior (never silently regenerate an existing key).
- **FR-008**: The system MUST allow selecting an alternative Signer implementation (e.g., AWS
  KMS, HSM) at configuration/startup time; KMS/HSM signers MUST NOT require the engine to hold
  private key material in process.
- **FR-009**: Any Signer implementation MUST satisfy a single shared contract test suite and
  produce signatures verifiable by the standard verification path.
- **FR-010**: When a selected Signer backend is unavailable, the system MUST fail loud and
  MUST NOT fall back to a different signing identity.

**Tenant context (P2)**

- **FR-011**: Every persisted resource MUST carry an optional `tenant_id`, defaulting to
  `"default"` when no tenant is supplied.
- **FR-012**: The system MUST scope reads, lists, and writes to the active tenant context so a
  caller in one tenant cannot observe another tenant's resources.
- **FR-013**: Legacy records lacking a `tenant_id` MUST be treated as tenant `"default"` on
  read, so v0.3.0 data remains accessible after upgrade with no migration required.
- **FR-014**: A self-host caller that never sets a tenant MUST observe identical behavior to
  v0.3.0 (single implicit `"default"` tenant).

**Structured audit events (P2)**

- **FR-015**: Every successful state-changing operation MUST emit exactly one structured
  audit event with a documented schema (actor, tenant, action, target resource id, UTC
  timestamp, and a digest of the change).
- **FR-016**: Audit events MUST be chainable such that each event references the prior event's
  hash, yielding a tamper-evident sequence consistent with the existing provenance
  hash-chain approach.
- **FR-017**: The system MUST allow an external consumer (e.g., the cloud) to receive these
  events for an external hash-chained log, while the default self-host behavior records them
  locally as today.
- **FR-018**: A failed operation MUST NOT emit a success audit event.

**Idempotency keys (P3)**

- **FR-019**: Write operations MUST accept an optional idempotency key; when present and
  previously seen with the same payload within the TTL, the system MUST return the original
  result without creating a duplicate.
- **FR-020**: An idempotency key reused with a different payload MUST be rejected as a
  conflict.
- **FR-021**: Idempotency records MUST expire 24 hours after creation and MUST be reclaimable
  so the store does not grow unbounded.
- **FR-022**: Write operations without an idempotency key MUST behave exactly as v0.3.0.
- **FR-023**: Idempotency records MUST be scoped per tenant.

**Cross-cutting**

- **FR-024**: All five capabilities MUST be additive and opt-in; the system MUST NOT introduce
  a breaking change to any public Python API, MCP tool, REST endpoint, CLI flag, or on-disk
  format in this MINOR release.
- **FR-025**: The full v0.3.0 test suite (358 tests: 267 functional + 91 RFC conformance
  benchmarks) MUST pass unchanged under the default configuration; conformance benchmarks
  MUST be unaffected by these changes.
- **FR-026**: Backends requiring heavy or external dependencies (Postgres driver, KMS SDK)
  MUST be optional extras; a default `pip install` MUST remain file-storage +
  in-process-signer with no external services.
- **FR-027**: The system MUST record, before the EU AI Act general-application date
  (2 August 2026), when most Annex III high-risk obligations begin to apply, a
  risk-classification rationale documenting that this extensibility layer is platform
  infrastructure (storage / signing / tenant / audit-event / idempotency interfaces) and is
  NOT itself a high-risk AI system under EU AI Act Annex III. The layer performs no AI
  inference, profiling, or automated decision-making about persons; it persists, signs, scopes,
  and audits records on behalf of the engine and its integrators. The rationale MUST be factual
  (the layer is an evidence/operational tool, not an AI system that determines outcomes) and
  recorded in `docs/`.
- **FR-028**: The system MUST document and support encryption-at-rest for audit-event
  persistence in non-default Repositories. The default file Repository is the self-host / dev
  default and stores records as plaintext on disk; any production or multi-tenant deployment
  persisting `AuditEvent` records (whose `actor` and `target_id` fields may carry PII) MUST use
  an encrypted-at-rest Repository (e.g., Postgres with KMS / disk-level at-rest encryption).
- **FR-029**: The idempotency record MUST NOT persist raw private key material (never), and
  SHOULD store a minimal representation of the original response (status + resource id +
  response hash) OR redact / encrypt sensitive fields (e.g., signed VCs, identity data) before
  storage. The 24-hour TTL is retained regardless of representation.

### Key Entities *(include if feature involves data)*

- **Repository**: The persistence boundary the service layer depends on. Represents the
  ability to create, get, list, update, and delete resources of a given type within a tenant
  scope. Has at least two realizations: the default file-backed store and a Postgres-backed
  store. Described independent of any specific database or file format.
- **Signer**: The signing boundary the service layer depends on. Represents the ability to
  produce a signature over a canonicalized payload and to disclose the corresponding public
  key / DID, without exposing private key material. Realizations include the default
  in-process Ed25519 signer, a KMS-backed signer, and an HSM-backed signer.
- **TenantContext**: The ambient scope for an operation. Carries a `tenant_id` (defaulting to
  `"default"`) and the acting identity. Determines which resources are visible and which
  tenant new resources and audit events belong to.
- **AuditEvent**: The structured record of a single committed state change. Carries actor,
  tenant, action, target resource id, UTC timestamp, a digest of the change, and a link to
  the prior event's hash so a sequence is tamper-evident.
- **IdempotencyKey**: A client-supplied token associated with a write. Carries the key value,
  tenant scope, a fingerprint of the request payload, the stored original result, and a
  creation timestamp governing a 24-hour TTL.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 358 existing tests (267 functional + 91 conformance benchmarks) pass
  unchanged with the default configuration.
- **SC-002**: Zero configuration change is required for an existing v0.3.0 self-host install to
  upgrade to v0.4.0 and keep working (no migration, no new env vars, no new services).
- **SC-003**: A Postgres-backed Repository adapter passes the identical Repository contract
  test suite that the default file adapter passes (100% of contract assertions).
- **SC-004**: An alternative Signer (e.g., KMS stub) passes the identical Signer contract test
  suite that the default in-process Ed25519 signer passes, and its signatures verify through
  the standard verification path.
- **SC-005**: Default in-process signing output is byte-identical to v0.3.0 for the same input
  (regression-locked by test).
- **SC-006**: For two distinct tenants, no read or list in one tenant context returns any
  resource belonging to the other (0 cross-tenant leaks across the test matrix).
- **SC-007**: Every state-changing operation emits exactly one structured audit event, and a
  generated sequence of events verifies as an unbroken hash chain (tampering with any event is
  detected).
- **SC-008**: A replayed write with the same idempotency key and payload within 24 hours
  produces 0 duplicate resources and returns the original result; a key older than 24 hours
  no longer suppresses a new create.
- **SC-009**: The change is a MINOR version bump with no breaking change to any documented
  public surface; any unavoidable break is enumerated in the plan's Complexity Tracking.
- **SC-010**: A default `pip install attestix==0.4.0` pulls no new mandatory runtime
  dependency (Postgres/KMS support is an optional extra).

## Assumptions

- The downstream consumer is the hosted `attestix-cloud` product (Milestone M2:
  identities + credentials on Postgres with KMS keys), which depends on the P1 stories first.
- The Postgres adapter and KMS/HSM signers are validated in this work via their contract test
  suites (and stub/in-memory equivalents where a live backend is impractical in CI); a live
  Postgres adapter and a live KMS signer are delivered as optional extras, while the
  contracts and the file/in-process defaults are the OSS guarantee.
- "Resource" covers the existing engine entities persisted today (identities, credentials,
  delegations, compliance records, reputation, provenance, anchors); the abstraction is
  uniform across them.
- The existing provenance hash-chained audit log (`prev_hash`/`chain_hash` with a genesis
  hash) is the precedent and reference behavior for AuditEvent chaining.
- The REST layer is the primary surface for idempotency keys (Stripe-style header); whether
  MCP tools also accept idempotency keys is left to the plan. **Resolved (T046):** the store +
  `run_idempotent` helper are surface-agnostic — REST is the documented primary boundary, but
  MCP/direct callers may use the same helper. The opt-in `IdempotencyMiddleware` ships but is
  not auto-mounted in v0.4.0 P3 (TODO seam in `api/main.py`).
- Tenant resolution at the boundary (how a REST request or MCP call maps to a `tenant_id`) is
  defined by the integrator/cloud; the OSS provides the slot and the default. [NEEDS
  CLARIFICATION: whether the OSS ships a default tenant-resolution mechanism for the REST
  layer or leaves it entirely to the integrator.]
- "v0.4.0-rc.1" denotes a release candidate; the public release is `0.4.0` and the SemVer
  contract in this spec refers to the `0.3.0 → 0.4.0` MINOR boundary.
- This extensibility layer is platform infrastructure (storage, signing, tenant context,
  structured audit events, idempotency interfaces) and is NOT itself a high-risk AI system
  under EU AI Act Annex III: it performs no AI inference or automated decision-making about
  persons; it persists, signs, scopes, and audits records on behalf of the engine. A
  risk-classification rationale to this effect MUST be recorded in `docs/` before the
  EU AI Act general-application date (2 August 2026), when most Annex III high-risk
  obligations begin to apply (FR-027). Compliance records the engine handles on
  behalf of integrators do not make this operational layer a regulated AI system; provider
  liability for the integrator's own AI system remains with the provider (Articles 16–22).
- `AuditEvent.actor` (an identity / DID) and `AuditEvent.target_id` may constitute personal
  data under DPDP Act 2023 §2(t) and GDPR Art.4(1) when integrators store personal identifiers.
  The default file Repository stores these as plaintext on disk and is the self-host / dev
  default only; production and multi-tenant deployments MUST use an encrypted-at-rest
  Repository (FR-028).

## Persona-Review Remediation — 2026-05-27

Source run: `reviews/20260527T200952-review_oss_v040` (verdict: pass-with-revisions; 6-persona
panel, 100% consensus, cross-family adversary 0 gaps, would-block: no). The three revisions are
addressed as follows.

- **FINDING 1 [high] — No EU AI Act risk classification for this feature.** FIXED. Added an
  Assumption (this layer is platform infrastructure, NOT a high-risk AI system under EU AI Act
  Annex III) and **FR-027** requiring a factual risk-classification rationale recorded in
  `docs/` before the EU AI Act general-application date (2 August 2026), when most Annex III
  high-risk obligations begin to apply — `spec.md`. Added task **T047** to record it
  — `tasks.md`.
- **FINDING 2 [medium] — AuditEvent.actor/target_id may be PII; file sink stores plaintext.**
  FIXED. Added a PII / encryption-at-rest note on the `AuditEvent` schema (`actor`/`target_id`
  may be PII under DPDP Act §2(t) / GDPR Art.4(1); file Repository is plaintext self-host / dev
  default; production / multi-tenant MUST use an encrypted-at-rest Repository) — `data-model.md`
  §4. Added matching **FR-028** — `spec.md`. Added task **T048** to document it — `tasks.md`.
- **FINDING 3 [medium] — Idempotency middleware stores full stored_response unencrypted for
  24h.** FIXED. Specified that the idempotency record MUST NOT persist raw private key material
  and SHOULD store a minimal representation (status + resource id + response hash) OR redact /
  encrypt sensitive fields (signed VCs, identity data) before storage, with the 24h TTL retained
  — `data-model.md` §5 (updated `stored_response` field + new rule) and **FR-029** in `spec.md`.
  Added implementation task **T049** — `tasks.md`.

## Compliance accuracy pass — 2026-05-27

Wording corrections applied per the legal cross-check report at
`legal/attestix/reference/COMPLIANCE_CROSSCHECK_2026-05-27.md` (§5 "Should-tighten", item 1).
No requirement, scope, or behavior changed — these are precision-only edits to legal phrasing.

- **EU AI Act "enforcement date" → "general-application date".** The Act applies in phases
  (in force 1 Aug 2024; Art 5 prohibitions 2 Feb 2025; GPAI 2 Aug 2025; general application +
  most Annex III high-risk obligations 2 Aug 2026; Annex I product-related high-risk under
  Art 6(1) 2 Aug 2027). Replaced "the 2026-08-02 EU AI Act enforcement date" with "the EU AI
  Act general-application date (2 August 2026), when most Annex III high-risk obligations begin
  to apply" in **FR-027**, the platform-infrastructure Assumption, and FINDING 1 above; the
  same correction was made to **T047** in `tasks.md`. The dated deadline itself (record the
  rationale before 2 Aug 2026) is unchanged.
