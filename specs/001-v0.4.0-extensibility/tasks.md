---
description: "Task list for Attestix v0.4.0-rc.1 extensibility layer"
---

# Tasks: Attestix v0.4.0-rc.1 Extensibility Layer

**Input**: Design documents from `/specs/001-v0.4.0-extensibility/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), data-model.md

**Tests**: Contract and regression tests are REQUIRED for this feature (Constitution
principle III: new public interfaces require contract tests; the 358 existing tests must stay
green). Test tasks are therefore included.

**Organization**: Tasks are grouped by user story so each story can be implemented, tested,
and delivered independently. Downstream consumer: hosted **cloud Milestone M2**
(identities + credentials on Postgres with KMS keys) depends on P1 landing first.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1 (P1 storage+signer), US2 (P2 tenant+audit), US3 (P3 idempotency)
- Paths are repository-root-relative (canonical flat layout per plan.md).

## Path Conventions

- New packages at repo root: `storage/`, `signing/`, `audit/`, `tenancy/`, `idempotency/`.
- Existing canonical modules: `services/*.py`, `auth/crypto.py`, `config.py`, `errors.py`,
  `api/main.py`, `api/deps.py`, `services/cache.py`.
- Namespace mirror re-exports under `attestix/<pkg>/`.
- Tests: `tests/contract/`, `tests/unit/`, `tests/integration/`, `tests/e2e/`,
  `tests/benchmarks/`.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Scaffold the new packages and the optional-extras wiring without changing behavior.

- [ ] T001 Create empty packages with `__init__.py`: `storage/`, `signing/`, `audit/`,
  `tenancy/`, `idempotency/` (repo root).
- [ ] T002 Register new packages in `pyproject.toml [tool.setuptools] packages` (flat +
  `attestix.*` mirror) and add optional extras `pg` and `kms` under
  `[project.optional-dependencies]`.
- [ ] T003 [P] Add new error categories to `errors.py` for storage / signer / idempotency /
  tenancy failures.
- [ ] T004 [P] Create `tests/contract/` with `__init__.py` and shared fixtures in
  `tests/conftest.py` for an isolated temp `ATTESTIX_DATA_DIR` per test.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The seam definitions and selection plumbing every user story builds on.

**⚠️ CRITICAL**: No user story implementation can begin until this phase is complete.

- [ ] T005 [P] Define `Repository` ABC in `storage/repository.py` (create/get/list/update/
  delete signatures + `tenant_id` param) per data-model.md §1.
- [ ] T006 [P] Define `Signer` ABC in `signing/signer.py` (sign / public_key / did) per
  data-model.md §2.
- [X] T007 [P] Define `TenantContext` + `DEFAULT_TENANT = "default"` + resolver hook in
  `tenancy/context.py` per data-model.md §3.
- [ ] T008 Add `select_repository(config)` to `storage/__init__.py` and
  `select_signer(config)` to `signing/__init__.py` (default-returning, no extra deps imported
  unless selected). Depends on T005, T006.
- [ ] T009 Extend `services/cache.py::get_service` and `api/deps.py` to accept and pass an
  injected Repository, Signer, and tenant into service constructors, defaulting to the
  selected defaults. Depends on T008.
- [X] T046 **(prerequisite for US2/US3)** Resolve open [NEEDS CLARIFICATION] items
  (idempotency concurrency guarantee, REST-only vs MCP idempotency scope, no-op-update audit
  emission, default REST tenant resolution) and update spec/data-model accordingly. These
  decisions define expected behavior for the Phase 4 (US2) and Phase 5 (US3) tests and
  implementation, so they MUST be settled before those stories begin.

**Checkpoint**: Interfaces exist and can be injected; defaults resolve to file storage +
in-process signer + `"default"` tenant. No service behavior changed yet. Open contract
ambiguities are resolved (T046), so US2/US3 can be specified against an unambiguous contract.

---

## Phase 3: User Story 1 - Swap storage and signing backends (Priority: P1) 🎯 MVP

**Goal**: Services persist via `Repository` and sign via `Signer`; defaults reproduce v0.3.0
exactly; alternative backends pass the same contract suites. Unblocks cloud M2.

**Independent Test**: Run the full v0.3.0 suite under defaults (all green); run the
Repository and Signer contract suites against both the default and an alternative impl (all
green); confirm default signer output is byte-identical to v0.3.0.

### Tests for User Story 1 (write first, ensure they FAIL) ⚠️

- [ ] T010 [P] [US1] Repository contract suite in
  `tests/contract/test_repository_contract.py`: round-trip, default-tenant, legacy-read,
  idempotent-delete, durability — parametrized to run against every Repository impl.
- [ ] T011 [P] [US1] Signer contract suite in `tests/contract/test_signer_contract.py`:
  verifiable, stable DID, no-private-leak, fail-loud — parametrized over every Signer impl.
- [ ] T012 [P] [US1] Byte-parity regression test in `tests/unit/test_signer_parity.py`:
  in-process signer output equals v0.3.0 `sign_json_payload` for fixed inputs (SC-005).

### Implementation for User Story 1

- [ ] T013 [P] [US1] Implement default `FileRepository` in `storage/file_repository.py`
  wrapping `config.py` `_safe_load`/`_safe_save`, mapping collections → existing JSON files.
- [ ] T014 [P] [US1] Implement default `InProcessSigner` in `signing/inprocess_signer.py`
  wrapping `auth/crypto.py` (`load_or_create_signing_key`, `sign_json_payload`); preserve
  `SigningKeyLoadError` fail-loud behavior.
- [ ] T015 [US1] Make `config.py` `load_*`/`save_*` thin shims over `FileRepository` (keep
  public functions working for external callers). Depends on T013.
- [ ] T016 [US1] Refactor `services/identity_service.py` to use injected Repository + Signer
  instead of `config.load_*`/`save_*` and `self._private_key`. Depends on T009, T013, T014.
- [ ] T017 [P] [US1] Refactor `services/credential_service.py` (same pattern). Depends on T009,
  T013, T014.
- [ ] T018 [P] [US1] Refactor `services/delegation_service.py` (same pattern).
- [ ] T019 [P] [US1] Refactor `services/compliance_service.py` (same pattern).
- [ ] T020 [P] [US1] Refactor `services/reputation_service.py` (same pattern).
- [ ] T021 [P] [US1] Refactor `services/provenance_service.py` (same pattern; keep its
  existing hash-chained `audit_log` intact for now — aligned in US2).
- [ ] T022 [P] [US1] Refactor `services/agent_card_service.py` and `services/did_service.py`
  (persisting paths only).
- [ ] T023 [P] [US1] Refactor `services/blockchain_service.py` to persist `anchors` via
  Repository.
- [ ] T024 [P] [US1] Implement optional `PgRepository` in `storage/pg_repository.py` (`[pg]`
  extra); register in `select_repository`; run T010 against it.
- [ ] T025 [P] [US1] Implement optional `KmsSigner` in `signing/kms_signer.py` (`[kms]`
  extra) (or a CI stub where live KMS is impractical); register in `select_signer`; run T011
  against it.
- [ ] T026 [US1] Add `attestix/storage/` and `attestix/signing/` one-line re-export mirrors.
- [ ] T027 [US1] Run full existing suite (`tests/unit`, `integration`, `e2e`, `benchmarks`)
  under defaults; confirm all 358 green and 91 benchmarks unaffected (SC-001).

**Checkpoint**: US1 fully functional — default path unchanged, backends swappable, contract
suites green for every impl. **MVP for cloud M2.**

---

## Phase 4: User Story 2 - Tenant isolation + structured audit events (Priority: P2)

**⚠️ Prerequisite**: T046 (resolve open clarifications) MUST be complete before this phase —
the no-op-update audit emission and default REST tenant-resolution decisions define this
story's expected behavior.

**Goal**: Every resource carries `tenant_id` (default `"default"`); reads/lists/writes are
tenant-scoped; every committed state change emits one chainable `AuditEvent`.

**Independent Test**: Default config → all resources `tenant_id=="default"`, existing tests
unaffected; two-tenant test → no cross-tenant leak; each mutating op emits exactly one event;
a sequence verifies as an unbroken hash chain.

### Tests for User Story 2 (write first, ensure they FAIL) ⚠️

- [X] T028 [P] [US2] Tenant-isolation integration test in
  `tests/integration/test_tenant_isolation.py`: create under `acme`/`globex`, assert no
  cross-tenant visibility (SC-006); legacy record reads as `"default"` (FR-013).
- [X] T029 [P] [US2] Audit-event test in `tests/unit/test_audit_events.py`: exactly one event
  per mutating op, documented shape, hash-chain verification, no event on failure (SC-007,
  FR-018).

### Implementation for User Story 2

- [X] T030 [P] [US2] Implement tenant scoping in `storage/file_repository.py` (filter by
  `tenant_id`; absent → `"default"`). **Done in P1** (FileRepository / MemoryRepository already
  scope by tenant); the optional `pg_repository.py` is a separate optional-extra task.
- [X] T031 [P] [US2] Implement `AuditEvent` schema + chaining in `audit/events.py` per
  data-model.md §4 (reuse `auth.crypto.canonicalize_json` + SHA-256; mirror provenance
  `prev_hash`/`chain_hash`).
- [X] T032 [US2] Implement `AuditEventEmitter` in `audit/emitter.py` with default local sink +
  injectable external sink (FR-017). Depends on T031.
- [ ] T033 [US2] **DEFERRED (P1 follow-up):** thread `TenantContext` through `services/cache.py`
  / `api/deps.py` per-request and into all 9 services. The seam exists (cache.py accepts
  injected deps; `resolve_tenant` resolves the context); per-service threading is deferred to
  keep the slice additive and the suite green. Depends on T009, T030.
- [ ] T034 [US2] **DEFERRED (P1 follow-up):** emit one `AuditEvent` on each successful mutating
  method across the 9 services; align `provenance_service` existing audit_log with the shared
  chain. The emitter + chain are implemented and tested standalone; wiring it into every
  service is the follow-up (touches all 9 services — out of safe scope for this pass without
  regression risk). Depends on T032, T033.
- [X] T035 [US2] Added the default per-request tenant resolver (`tenancy.context.resolve_tenant`,
  default `"default"`); added `attestix/audit/`, `attestix/tenancy/` re-export mirrors. (REST
  mounting of the resolver is part of deferred T033.)
- [X] T036 [US2] Re-ran full suite under defaults; 454 green (411 baseline + 43 new), 0
  regressions, 91 benchmarks unaffected, zero cross-tenant leaks (SC-001, SC-006).

**Checkpoint**: US1 + US2 work independently; multi-tenant + auditable, self-host unchanged.

---

## Phase 5: User Story 3 - Idempotency keys (Priority: P3)

**⚠️ Prerequisite**: T046 (resolve open clarifications) MUST be complete before this phase —
the idempotency concurrency guarantee and REST-only-vs-MCP idempotency scope decisions define
this story's expected behavior.

**Goal**: Optional Stripe-style idempotency key on writes; replay within 24h returns the
original result; mismatched payload → conflict; no key → v0.3.0 behavior.

**Independent Test**: Replay same key+payload → no duplicate, original response; same
key+different payload → 409; key past TTL → new create proceeds; no key → unchanged.

### Tests for User Story 3 (write first, ensure they FAIL) ⚠️

- [X] T037 [P] [US3] Idempotency integration test in
  `tests/integration/test_idempotency.py`: dedupe within TTL, conflict on payload mismatch,
  TTL expiry, no-key passthrough, per-tenant scoping (SC-008, FR-019…FR-023). Parametrized over
  file + memory repos; includes the FR-029 minimal-storage assertion and TTL reclaim.

### Implementation for User Story 3

- [X] T038 [P] [US3] Implemented `IdempotencyStore` ABC + default Repository-backed impl with
  24h TTL and reclaim in `idempotency/store.py` per data-model.md §5, plus the reusable
  surface-agnostic `run_idempotent` helper. Depends on T013, T030.
- [X] T039 [US3] Implemented `Idempotency-Key` middleware in `idempotency/middleware.py`
  (`BaseHTTPMiddleware`, write-method scoped, request fingerprint via JCS, tenant via the
  default resolver). Depends on T038.
- [ ] T040 [US3] **DEFERRED (documented seam):** mount the middleware on POST/write endpoints in
  `api/main.py`. Left unmounted this pass (body-replay middleware needs validation against the
  full REST surface before default-on); a clear TODO marks the seam in `api/main.py` and the
  middleware is opt-in today. The `attestix/idempotency/` re-export mirror IS added. Depends on
  T039.
- [X] T041 [US3] Re-ran full suite under defaults; 454 green and the no-key path is unchanged
  (no middleware auto-mounted; FR-022 preserved) (SC-001, FR-022).

**Checkpoint**: All three stories independently functional; self-host zero-config upgrade
verified.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T042 [P] Update `CHANGELOG.md` and `ROADMAP.md` for the v0.4.0 additive seams (testnet
  qualifier preserved for EAS).
- [ ] T043 [P] Update `docs/` and `website/content/docs/` with storage/signer selection,
  tenant, audit, and idempotency guides (mark Postgres/KMS as optional extras).
- [ ] T044 Verify SemVer: bump `pyproject.toml` and `attestix/__init__.py __version__` to
  `0.4.0`; confirm no breaking public-surface change (SC-009).
- [ ] T045 Confirm default `pip install attestix==0.4.0` pulls no new mandatory dependency
  (SC-010).
- [ ] T047 [P] Record EU AI Act risk-classification rationale for the v0.4.0 layer in `docs/`
  (infra component — storage / signing / tenant / audit / idempotency interfaces; performs no
  AI inference or automated decision-making; Annex III non-applicability). MUST be recorded
  before the EU AI Act general-application date (2 August 2026), when most Annex III
  high-risk obligations begin to apply (FR-027).
- [X] T048 [P] Documented encryption-at-rest for audit-event (and PII-bearing) persistence in
  `docs/extensibility-v0.4.0.md` (and inline in the `audit/events.py` module docstring): file
  Repository is plaintext self-host / dev default; production / multi-tenant MUST use an
  encrypted-at-rest Repository (e.g., Postgres + KMS / disk-level at-rest encryption) because
  `AuditEvent.actor` and `target_id` may carry PII (FR-028). (`website/content/docs/` mirror is
  a follow-up.)
- [X] T049 [US3] Implemented minimal-storage in the idempotency store (`idempotency/store.py`):
  never persists raw private key material; stores a minimal representation (status + resource id
  + response hash) via `minimal_stored_response`; retains the 24h TTL (FR-029). Asserted by
  `test_stored_response_is_minimal_no_raw_body`. Depends on T038.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies — start immediately.
- **Foundational (Phase 2)**: depends on Setup — BLOCKS all user stories.
- **US1 (Phase 3 / P1)**: depends on Foundational. **MVP; unblocks cloud M2.**
- **US2 (Phase 4 / P2)**: depends on Foundational **and on T046 (clarifications resolved)**;
  builds on US1 (events record against the Repository; tenant enforced at the Repository
  boundary).
- **US3 (Phase 5 / P3)**: depends on Foundational **and on T046 (clarifications resolved)**;
  depends on US1 (key store via Repository) and benefits from US2 (per-tenant keys).
- **Polish (Phase 6)**: after desired stories complete.

### User Story Dependencies

- **US1 (P1)**: independent once Foundational is done. Highest backward-compat risk → done
  first.
- **US2 (P2)**: layered on US1's Repository/Signer seam; independently testable.
- **US3 (P3)**: layered on US1 (and US2 for tenant scoping); independently testable.

### Within Each User Story

- Contract/regression tests written and FAILING before implementation (principle III).
- Interfaces (Phase 2) before implementations; default impls before alternative adapters.
- Service refactors after the default Repository/Signer exist.
- Story complete and full suite green before moving to the next priority.

### Parallel Opportunities

- Setup: T003, T004 in parallel.
- Foundational: T005, T006, T007 in parallel (different files).
- US1 tests: T010, T011, T012 in parallel.
- US1 service refactors: T017–T023 in parallel after T016 establishes the pattern (each a
  different `services/*.py` file).
- US1 adapters: T024 (Postgres) and T025 (KMS) in parallel.
- US2: T030, T031 in parallel; T028, T029 in parallel.
- Polish: T042, T043 in parallel.

---

## Parallel Example: User Story 1 service refactors

```bash
# After T016 sets the pattern in identity_service, run the rest in parallel:
Task: "Refactor services/credential_service.py to injected Repository + Signer"
Task: "Refactor services/delegation_service.py to injected Repository + Signer"
Task: "Refactor services/compliance_service.py to injected Repository + Signer"
Task: "Refactor services/reputation_service.py to injected Repository + Signer"
Task: "Refactor services/provenance_service.py to injected Repository + Signer"
Task: "Refactor services/agent_card_service.py + did_service.py"
Task: "Refactor services/blockchain_service.py (anchors via Repository)"
```

---

## Implementation Strategy

### MVP First (User Story 1 only)

1. Phase 1: Setup.
2. Phase 2: Foundational (interfaces + injection) — CRITICAL, blocks everything.
3. Phase 3: US1 (pluggable storage + signer).
4. **STOP and VALIDATE**: full 358 tests green under defaults; contract suites green for
   every impl; signer byte-parity confirmed.
5. Hand off to cloud M2 (its dependency is satisfied at this checkpoint).

### Incremental Delivery

1. Setup + Foundational → seams ready.
2. US1 → validate → ship (MVP; cloud M2 unblocked).
3. US2 → validate → ship (multi-tenant + audit).
4. US3 → validate → ship (idempotency).
5. Each story is additive and must keep the prior stories and the default path green.

---

## Notes

- [P] = different files, no dependency.
- Defaults must reproduce v0.3.0 exactly: `"default"` tenant, in-process Ed25519 signer, file
  storage. This is the backward-compatibility gate.
- The 91 RFC conformance benchmarks (`tests/benchmarks/`) are a hard gate and must not change.
- Cloud M2 is the first downstream consumer and is blocked on US1 (P1) only.
- Verify each contract suite passes for BOTH the default impl and the alternative adapter
  before considering a story done.
