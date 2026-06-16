# Changelog

All notable changes to Attestix are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.4.1rc1] - 2026-06-16

Pre-release. Security hardening from a multi-persona audit. Available on the
`--pre` channel only; `pip install attestix` still resolves `0.4.0` stable.

### Security
- **Credential verification key-binding (High).** `verify_credential`,
  `verify_credential_external` and `verify_presentation` decoded the Ed25519
  key from `proof.verificationMethod`, which sits outside the signed payload
  and is attacker-controlled — enabling an issuer key-substitution masquerade.
  Verification now decodes the key from the trust anchor (`issuer.id` for
  credentials, the server DID for presentations) and rejects a
  `verificationMethod` that names a different DID. Aligns with W3C VC Data
  Integrity controller-authorization.
- **Fail-closed API auth (High).** The REST `APIKeyMiddleware` served every
  endpoint when `ATTESTIX_API_KEY` was unset. It now refuses non-public
  requests (503) unless `ATTESTIX_ALLOW_NO_AUTH` is explicitly set
  (development/tests only).
- **Dependency CVE floors (High).** `requirements.txt` now pins
  `cryptography>=46.0.7` and `PyJWT[crypto]>=2.12.0` to match `pyproject.toml`,
  so installs from that file cannot resolve pre-CVE-patch versions.

### Fixed
- Bundle import now reads the cloud `vc_jsonld` credential key, so credentials
  in real cloud bundles import correctly.

### Known issues
- Cloud→OSS audit-chain re-verification can fail because the cloud mints the
  chain under the workspace UUID while the importer re-tags rows with the
  storage tenant. A fix decoupling the chain tenant from the storage tenant is
  tracked for a later 0.4.1 pre-release.

## [0.4.0] - 2026-05-30

First stable 0.4.0 — the embeddable, multi-tenant, portable foundation. Promotes
`0.4.0rc5` unchanged after a clean 10/10 Linux source-blind RC validation (the
convergence of a 5-RC cycle that caught and fixed 5 P0 install crashes, 4
doc/contract breaks, and 1 idempotency-replay defect across Windows + Linux).

### Headline since 0.3.0
- **Pluggable storage + signer** — swap the in-memory defaults for Postgres + HSM/KMS without forking (`Storage` / `Signer` protocols).
- **Multi-tenancy** — every resource carries `tenant_id`; structured, hash-chained, idempotency-aware audit events that don't leak across tenants.
- **Portability** — bundle EXPORT + IMPORT (`attestix export` / `attestix import`), byte-stable JCS wire-format published at https://attestix.io/spec/bundle/v1. Cloud-workspace ⇆ self-host round-trip.
- **Cross-engine offline verifier** — `npm install @vibetensor/attestix` (unscoped `attestix` migration in progress) verifies Python-issued credentials in any JS runtime.
- **Structured `verify_chain`** — `VerifyChainResult` with `broken_event_id` + `failure_reason`.
- **Canonical `attestix.*` namespace** with back-compat shims; `[api]` / `[langchain]` / `[crewai]` / `[openai-agents]` install extras; LangChain / OpenAI Agents / CrewAI integrations shipped in the wheel.
- **REST idempotency** replays the original cached body verbatim (`Idempotency-Replayed` header), exactly-1-resource dedup, 24h TTL.
- **Compliance** — `generate_declaration_of_conformity` raises on all missing prerequisites; declarations surface `credential_id`.
- **Docs** — 10 per-ICP quickstarts, `/uk` + `/india` geo-pages, OWASP Agentic Top 10 (2026) + ISO 42001 + NIST AI RMF + SOC 2 + FRIA mappings, `/verify` browser portal, `/pricing`, the bundle spec page.
- **Supply chain** — Docker base images SHA-pinned, CI deps hash-pinned (`--require-hashes`).

### Validated
585 tests (Ubuntu + Windows × py3.11-3.13). Clean 10/10 cross-family persona validation on Linux (source-blind against the PyPI wheel). signing-key 0600.

### Known, deferred to v0.4.1
- `get_audit_trail` surfaces only the legacy Article-12 chain (the `identity.create` event IS emitted + counted by `get_provenance`); contract change deferred.
- `create_delegation` refuses capability-escalation via error-dict not a raise (secure; escalation IS blocked).

## [0.4.0-rc.5] - 2026-05-30

Narrow convergence on rc.4. The internal Linux RC validation
(source-blind 10-persona harness inside WSL Ubuntu 24.04 / CPython 3.12
against the published `attestix==0.4.0rc4` wheel) confirmed all 4 rc.3
blockers stayed CLOSED and all 5 rc.2 P0s held on Linux, and surfaced one
new **P1 DX/contract defect** (plus two P2s) reachable only once rc.4 fixed
the `/v1/` REST paths. rc.5 lands the P1; both P2s are documented and
deferred to v0.4.1 (neither is a security or data-integrity issue, and
forcing either into the RC carries more regression risk than the defect it
removes). A clean Linux re-run of the same harness
(target: an idempotent retry returns the cached identity body — `agent_id`
present — and 0 BLOCK verdicts) is the gate before promoting to stable 0.4.0.

### Fixed

- **P1 — REST idempotency replay now echoes the original cached response
  body, not a receipt envelope.** A retried `POST /v1/identities` with the
  same `Idempotency-Key` correctly created **no duplicate** (the dedup
  guarantee was always intact — 3× same-key POST persisted exactly 1
  identity), but the *replay body* was a middleware envelope —
  `{"idempotent_replay": true, "stored_response": {"resource_id": null,
  "response_hash": …}}` — instead of the original response. A CI client
  retrying and reading `resp.json()["agent_id"]` got `None`, defeating the
  purpose of idempotency on the retry path. rc.5 makes the middleware
  persist the original HTTP response (status + body + content-type) and
  replay it **verbatim** on a key hit, Stripe-style, so a retry is
  indistinguishable from the first success (`agent_id` survives, status code
  is preserved — e.g. `201` is replayed as `201`, not coerced to `200`).
  Replay metadata moved to an `Idempotency-Replayed: true` **response
  header** so clients can still detect a replay without the body shape
  changing. The same-key/**different**-payload conflict (HTTP 409) and the
  24h TTL are unchanged. The direct/MCP `run_idempotent` helper keeps the
  FR-029 minimal receipt (it returns the live result on the first call and
  never needs to re-serialize a body); only the REST boundary stores the
  replayable body, which is the exact JSON the client already received.
  Covered by new end-to-end tests against the live FastAPI app (retry
  returns the same `agent_id`/status, N replays → exactly 1 identity,
  different payload → 409).

### Known issues (deferred to v0.4.1)

- **P2 — a bare REST identity-create shows 0 rows on
  `GET /v1/provenance/audit-trail/{id}`.** The service layer DOES emit an
  `identity.create` event into the structured audit collection on every
  create path (verified), but `get_audit_trail` reads only the legacy
  Article-12 provenance chain (written by `log_action`), so a brand-new
  identity with no logged actions returns `[]`. This is *arguably correct* —
  a freshly created identity has no Article-12 provenance yet — but reads as
  "provenance broken" to a first-time evaluator. Surfacing the
  `audit.json::events` rows through `get_audit_trail` is the right fix, but
  it changes that read API's contract for **every** consumer: it breaks the
  contiguous hash-chain ordering the trail guarantees today and the
  exact-row-count expectations several existing tests and consumers rely on.
  That is a semantic change to a core read surface, not a one-line wiring
  fix, so it is deferred to v0.4.1 (where the trail can be reshaped to merge
  both chains in a single, ordering-stable, documented response). The
  `identity.create` event is already recorded and counted by
  `get_provenance` (rc.3 P0 #5); only the audit-trail *read* lags. Not a
  data-integrity issue — the event exists.
- **P2 — capability-escalation in `create_delegation` is refused via an
  error-dict, not a raised exception.** The delegation control correctly and
  securely blocks an over-broad sub-delegation (fails closed; an attenuated
  subset succeeds), but returns `{"error": "Capability escalation denied: …"}`
  rather than raising — inconsistent with the rc.4 direction of having
  `generate_declaration_of_conformity` raise. This is intentionally **not**
  changed in rc.5: the entire `create_delegation` method returns error-dicts
  on every failure branch, and both the REST router and the MCP tool layer
  depend on that dict shape (`isinstance(result, dict) and "error" in
  result`). Converting one branch would be internally inconsistent; converting
  the whole method touches every caller and risks destabilizing delegation
  this late in the RC cycle. Tracked as a consistency item for v0.4.1. Not a
  security issue — the escalation IS blocked.

Credit: internal Linux RC validation
(`paper/internal/v0.4.0rc4-linux-validation-2026-05-30.md`).

## [0.4.0-rc.4] - 2026-05-30

Honest follow-up to rc.3. The internal Linux RC validation report
(source-blind 10-persona harness run inside WSL Ubuntu 24.04 / CPython
3.12 against the published `attestix==0.4.0rc3` wheel — the cross-OS gate
the rc.2 report owed) confirmed that 4 of the 5 rc.2 P0s held on Linux and
the 0600 signing-key fix is enforced, but it surfaced **4 release blockers**
that only became reachable once rc.3 fixed the install-time crashes that
had masked them. rc.4 lands all 4. A clean Linux re-run of the same harness
(target: 10/10 quickstarts exit 0, 0 BLOCK verdicts, DoC raises on every
path) is the gate before promoting to stable 0.4.0.

### Fixed

- **P0 — `generate_declaration_of_conformity` now raises on ALL
  prerequisite-failure branches (finishes the rc.3 P0 #4 fix).** rc.3 made
  the method raise `InvalidComplianceProfileError` when the Annex V
  *content* fields were missing, but it still returned `{"error": ...}`
  (no `declaration_id`) on the **prerequisite** branches — no compliance
  profile, and conformity assessment not completed — reproducing the exact
  "move forward with `declaration_id=None`" footgun rc.3 claimed to have
  eliminated. rc.4 adds `MissingCompliancePrerequisiteError` (a subclass of
  `InvalidComplianceProfileError`, so the existing MCP-tool and REST-router
  handlers surface it as a structured error / HTTP 422 unchanged) and
  raises it on every early-return path: no profile, no completed
  assessment, and the high-risk self-assessment-where-third-party-required
  case. Each message names exactly which prerequisite is missing and the
  method to call to satisfy it. No silent `{"error": ...}` survives at the
  service layer for this method. Covered by new unit tests asserting it
  *raises* (not returns an error dict) for the no-profile and
  no-assessment paths.
- **P0 — grc-consultant quickstart no longer crashes with
  `KeyError: 'credential_id'`.** The published quickstart bundled the
  declaration into a Verifiable Presentation via
  `declaration["credential_id"]`, but the DoC return had no such key (it
  issued the backing `EUAIActComplianceCredential` VC internally and then
  discarded its id). rc.4 surfaces the issued VC's id on the declaration
  return as `credential_id` (the honest shape — that VC is exactly what the
  VP step needs), and fixes the quickstart's
  `create_verifiable_presentation(...)` call to use the real keyword
  arguments (`agent_id`, `credential_ids`, `audience_did`). The signed,
  persisted Annex V declaration is unchanged — `credential_id` is added to
  the in-memory return only, after signing, so declaration signatures stay
  valid.
- **P0 — enterprise-architect / mlops-engineer REST paths corrected to the
  `/v1/` prefix.** The quickstarts POSTed to `/identities` and GET
  `/audit/{id}`, but every FastAPI router mounts under `/v1` — the real
  routes are `POST /v1/identities` and
  `GET /v1/provenance/audit-trail/{agent_id}`. Both documented paths
  returned HTTP 404 live. All REST paths in the quickstart docs (including
  the mlops `curl` and the enterprise-architect endpoint-surface list) now
  carry the `/v1/` prefix, verified against the router prefixes in
  `attestix/api/routers/`.
- **P1 — mlops-engineer requirements pin bumped off `0.4.0rc2`.** The
  published `requirements-attestix.txt` snippet pinned `attestix==0.4.0rc2`;
  bumped to `0.4.0rc4`. Stale `v0.4.0-rc.2` / `v0.4.0-rc.3` version
  references across the quickstart docs (devtools-skeptic, index, indie-dev,
  fintech-compliance) were bumped to `v0.4.0-rc.4` for consistency.

## [0.4.0-rc.3] - 2026-05-28

Honest follow-up to rc.2. The isolated 10-persona RC validation (run with
`python -I` + `PYTHONNOUSERSITE=1` so each persona quickstart resolved
against the published wheel, not the dev tree) caught 5 P0 release
blockers — three of which crashed the documented quickstart on a fresh
`pip install --pre attestix==0.4.0rc2`, two of which silently produced
broken output on a compliance-critical path. rc.3 lands fixes for all 5,
plus the top 4 P1s from the same report. See the internal RC validation
report for the full per-persona artefact set; below is the
ship-with-fixes change set.

### Fixed

- **P0 #1 — `attestix.integrations.*` now in wheel.** The published rc.2
  wheel shipped no `attestix/integrations/` directory at all, so the
  indie-dev quickstart's `from attestix.integrations.langchain import
  AttestixCallback` raised `ModuleNotFoundError` on every fresh install.
  rc.3 adds `attestix.integrations`, `attestix.integrations.langchain`
  (real `BaseCallbackHandler` named `AttestixCallback`),
  `attestix.integrations.openai_agents` (`AttestixAuditHook`), and
  `attestix.integrations.crewai` (`AttestixCrewAdapter`) to
  `[tool.setuptools] packages`. Each module imports its framework lazily
  so `import attestix.integrations` itself is always cheap and the
  framework SDK is only required at first use of the wrapper class.
  Verified by `tests/release/test_wheel_includes_integrations.py` which
  builds the wheel + walks its namelist.
- **P0 #2 — `[api]` extra declared (fastapi + uvicorn).** `attestix.api.main`
  did `from fastapi import FastAPI, Request` at module load time, but
  fastapi was neither a runtime dep nor an opt-in extra. Following the
  enterprise-architect quickstart (`uvicorn attestix.api.main:app`)
  raised a confusing `ModuleNotFoundError: No module named 'fastapi'`
  on first invocation. rc.3:
  - Adds `[project.optional-dependencies] api = ["fastapi>=0.115,<0.130",
    "uvicorn[standard]>=0.32,<0.40"]`.
  - Wraps the `attestix.api.main` import in a `try/except` that raises a
    targeted `ImportError` pointing at `pip install --pre 'attestix[api]'`
    when the extra is missing.
  - Verified by `tests/release/test_api_extra_install.py` which asserts
    both halves of the contract (clear error without fastapi; METADATA
    declares the extra and requires fastapi+uvicorn).
- **P0 #3 — web3-onchain doc uses property syntax.**
  `BlockchainService.is_configured` and `wallet_address` are decorated
  `@property` in the code, but the published web3-onchain quickstart at
  `website/content/docs/quickstart/web3-onchain.mdx` called them as
  methods (`chain.is_configured()` / `chain.wallet_address()`), raising
  `TypeError: 'bool' object is not callable` / `'NoneType' object is not
  callable` on the very next line. The properties are the more pythonic
  design and stay; the docs are fixed.
- **P0 #4 — `generate_declaration_of_conformity` raises on missing
  Annex V fields.** Previously the method returned `{"error": "...missing
  required fields: transparency_obligations..."}` and the doc snippet
  read `print(declaration["declaration_id"])` which silently printed
  `None`. For an EU AI Act compliance product, silent fall-through to a
  `None` declaration on the documented fintech happy path is the worst
  possible failure mode. rc.3 introduces a new exception
  `attestix.services.compliance_service.InvalidComplianceProfileError`
  (subclass of `ValueError`, carries a `missing_fields: list[str]`
  attribute) and raises it from the Annex V validation branch. The REST
  router translates it to HTTP `422` with `{"error":
  "invalid_compliance_profile", "missing_fields": [...]}`; the MCP tool
  surfaces it as a structured error JSON body.
- **P0 #5 — `audit_log_count` reflects the new audit chain.** Running
  the documented GRC quickstart end-to-end left
  `ProvenanceService.get_provenance(agent_id)["audit_log_count"]` at
  `0` and `attestix status` showing `Audit log entries: 0` because only
  `log_action` wrote to the legacy `provenance.json::audit_log` chain.
  rc.3:
  - Every state-changing service method already emits to the new
    `audit.json::events` chain via the per-service `safe_emit` hook
    (T033/T034 wiring landed in #84) — no service-side change needed.
  - `ProvenanceService.get_provenance` now ALSO counts rows in the new
    audit collection that pertain to this agent, by resolving each
    event's `target_id` through the owning collection (compliance
    profile_id → agent_id, credential id → subject id, etc.). The
    legacy per-`log_action` count is still exposed via
    `audit_chain_count_legacy` so callers that want the old semantics
    don't break.
  - `IdentityService.purge_agent_data` now also strips audit events
    whose `target_id` matches the agent so GDPR Article 17 erasure
    parity is preserved. The chain integrity guarantee
    (`verify_chain(chain).valid is True`) holds across the
    record/create/issue emissions — covered by the new
    `tests/integration/test_grc_quickstart_audit_chain.py` end-to-end
    test that mirrors the live grc-consultant quickstart.

### Changed

- **`[langchain]`, `[crewai]`, `[openai-agents]` extras declared.** Memory
  said three real framework integrations existed; none were reachable
  via `pip install attestix[<framework>]` because the bracket extras
  weren't in METADATA. rc.3 declares all three with the version
  constraints the integration code actually uses
  (`langchain-core>=0.3,<0.5`, `crewai>=0.95,<0.200`,
  `openai-agents>=0.0.20`).
- **`agent['did']` populated at create-time.** The published indie-dev
  quickstart read `agent.get('did')` which returned `None` because the
  identity record only populated `agent['issuer']['did']`. rc.3 sets
  the top-level `did` field to the issuer DID so both shapes work.
- **`.signing_key.json` chmod is now cross-platform best-effort.**
  Previously the chmod was skipped on Windows; rc.3 calls
  `os.chmod(key_path, 0o600)` on every platform inside a try/except so
  POSIX gets the 0600 enforcement and Windows gets at least the
  read-only bit flipped. Production-grade protection on Windows still
  requires NTFS ACL hardening (`icacls`).

### Verification

- Test suite: 531 passing, 2 skipped (525 baseline → 531 = +6 net new
  tests: 2 GRC end-to-end + 3 release-gate wheel/extra/install + 1
  InvalidComplianceProfileError unit test). Zero regressions in the
  rc.2 baseline once existing strict-equality `audit_log_count == N`
  assertions were updated to use `audit_chain_count_legacy` for the
  legacy-chain count (the new aggregate is documented and asserted via
  `>=`).
- `ruff check attestix/ tests/release/ tests/integration/...` clean.
- `python -m build --wheel` produces `attestix-0.4.0rc3-py3-none-any.whl`;
  `unzip -l` confirms every `attestix/integrations/{__init__,langchain,
  openai_agents,crewai}/*.py` is shipped. METADATA declares
  `Provides-Extra: api`, `langchain`, `crewai`, `openai-agents`.

### Reference

- Internal RC validation report (gitignored, paper/internal/) for the
  full per-persona artefact set: install logs, quickstart-run logs,
  Bedrock persona-review reports, source-blindness audit, and the
  Linux re-validation note.

## [0.4.0-rc.2] - 2026-05-28

Packaging-correctness and honesty pass. No functional changes vs. rc.1 — the
service code, REST API, MCP tools, conformance benchmarks, and on-disk formats
are byte-identical. This release exists to fix two release blockers that the
ICP funnel evaluation flagged on rc.1.

### Fixed

- **Packaging — proper `attestix.*` namespace.** Pre-rc.2 wheels dropped flat
  top-level packages (`services/`, `auth/`, `storage/`, `signing/`, `audit/`,
  `tenancy/`, `idempotency/`, `blockchain/`, `api/`, `tools/`, plus
  `config.py`, `errors.py`, `main.py`, `cli.py`) into site-packages on every
  install. That polluted every consumer's namespace and forced the documented
  import to be `from services.X import Y` instead of `from attestix.services.X
  import Y`. The funnel evaluation found 9 of 12 ICP personas dropped at
  Integrate because of this. The canonical source has been promoted into the
  `attestix/` package; the wheel now ships the `attestix.*` namespace plus
  thin deprecation shims at the legacy paths. The shims re-export from the
  canonical namespace and emit a single `DeprecationWarning` on first import,
  pointing at the new path. They are scheduled for removal in **v0.5.0**.

  Update your imports:

  ```python
  # before (still works in v0.4.0-rc.2; emits DeprecationWarning)
  from services.identity_service import IdentityService
  from signing.inprocess_signer import InProcessSigner
  from auth.crypto import sign_json_payload

  # after (canonical, recommended)
  from attestix.services.identity_service import IdentityService
  from attestix.signing.inprocess_signer import InProcessSigner
  from attestix.auth.crypto import sign_json_payload
  ```

  Deployment configs that spawn uvicorn with `api.main:app` should be updated
  to `attestix.api.main:app`. The `attestix` console script entry-point now
  resolves to `attestix.cli:cli`.

### Changed

- **Honesty pass on rc.1 marketing copy.** The funnel evaluation flagged
  pairings of "production-ready" / "battle-tested" / "Production ready"
  framework labels with our actual maturity (15 GitHub stars, single
  maintainer, no third-party security audit). The numbers themselves
  (481 tests, 91 conformance benchmarks, 47 MCP tools, 9 modules,
  44 REST endpoints, real LangChain / OpenAI Agents SDK / CrewAI
  integrations) are real and are kept — they're now framed honestly as
  "v0.4.0-rc.2 release candidate, single-maintainer project, community
  contributions welcome, no independent third-party security audit yet."
  Updated locations: `README.md`, `website/src/lib/config.tsx`,
  `website/src/lib/atx-data.ts`, `website/public/llms.txt`,
  `website/content/docs/guides/{integration-guide,langchain,crewai,openai-agents-sdk}.mdx`,
  `website/src/components/sections/v2/frameworks.tsx`,
  `website/src/app/(marketing)/research/page.tsx`,
  and the FastAPI app docstring.

### Verification

- Test suite: 481 passing, 1 skipped (POSIX chmod on Windows). **Zero
  regressions** vs. rc.1 baseline (481 passing).
- RFC / W3C conformance benchmarks: 91/91 passing.
- `ruff check .` clean.
- Wheel top-level set asserted via `tests/install/test_pip_install_smoke.py`
  (opt-in; `ATTESTIX_RUN_INSTALL_SMOKE=1`). The smoke test rebuilds the wheel,
  installs it into a throwaway venv, and verifies (a) canonical imports work,
  (b) legacy flat imports emit the canonical-namespace `DeprecationWarning`.

## [0.4.0-rc.1] - 2026-05-28

First v0.4.0 release candidate. Ships the extensibility layer that lets the
engine be wrapped (e.g. by a hosted control plane) without forking, while
self-host behavior is unchanged. Additive and backward-compatible: existing
v0.3.0 installs require no config change and all prior tests pass unmodified.

### Added

- **Pluggable storage** — a `Repository` interface with a default
  `FileRepository` (on-disk format byte-for-byte unchanged) plus a
  `MemoryRepository`; optional `pg` extra for a Postgres-backed adapter.
- **Pluggable signer** — a `Signer` interface with a default `InProcessSigner`
  (output byte-identical to v0.3.0); optional `kms` extra for AWS KMS.
- **Tenant context** — an optional `tenant_id` on resources (defaults to
  `"default"`; legacy records with no tenant_id read as `"default"`).
- **Structured audit events** — every state change across the 9 services emits
  one hash-chained `AuditEvent` (side-channel; service outputs and on-disk
  format unchanged); per-tenant chains with `verify_chain` tamper detection.
- **Idempotency keys** — first-class on POST/write endpoints via an opt-in
  `IdempotencyMiddleware` (strict no-op without an `Idempotency-Key` header,
  24h TTL, minimal stored representation — no raw key material or signed bodies).

### Notes

- Backward compatible: no breaking public-API changes; all new behavior is
  opt-in with defaults that reproduce v0.3.0.
- Test suite grew from 358 to 481 passing; the RFC conformance benchmarks are
  unaffected.
- Closes the cloud-prerequisite issues #66, #67, #68, #69, #70.

## [0.3.0] - 2026-04-17

Security hardening release bundling seven previously merged but unreleased
pull requests (PR #45 through PR #51). The release ships a critical delegation
auth bypass fix, corrects Article 43 Annex III conformity logic, lands three
real framework integrations (LangChain, OpenAI Agents SDK, CrewAI), and adds
GitHub Actions CI/CD.

Minor version bump (0.2.5 -> 0.3.0) because the batch contains security
fixes, new public integration surfaces, and an Article 43 behavior change.
No breaking API changes for MCP tool callers.

### Security

- **CRITICAL: delegation chain auth bypass fixed** (PR #45). Parent tokens in
  a delegation chain are now fully verified and capability attenuation is
  strictly enforced. Previously a malicious delegate could craft a child
  token whose claimed capabilities exceeded those of the parent. Any
  long-lived delegation tokens issued prior to this release should be
  reviewed and re-issued.
- **SSRF hardening** (PR #47). Agent discovery, DID resolution, and credential
  fetch paths now go through the centralized SSRF guard (private IP blocking,
  metadata endpoint blocking, DNS rebind defense) on every outbound request.
- **Timing-safe comparisons** (PR #47). Signature and token equality checks
  switched to constant-time comparison (`hmac.compare_digest`) to remove a
  timing oracle on credential and delegation verification.
- **API error sanitization** (PR #47). Seven REST API router exception paths
  no longer leak stack traces, file paths, or internal type names to
  clients; errors are now structured and safe by default.

### Added

- **Real LangChain integration** (PR #42, released now). `integrations/langchain/`
  ships an actual `BaseCallbackHandler` subclass that logs every LLM, chain,
  and tool event into the Attestix audit trail. Replaces the previous
  example-only shim.
- **Real OpenAI Agents SDK integration** (PR #48). `integrations/openai_agents/`
  uses `MCPServerStdio` to connect the OpenAI Agents runtime directly to the
  Attestix MCP server, exposing all 47 tools as native agent capabilities.
- **Real CrewAI integration** (PR #51). `integrations/crewai/` uses
  `MCPServerAdapter` so CrewAI crews can load Attestix tools the same way
  they load any other MCP toolset.

### Fixed

- **Article 43 Annex III conformity assessment correctness** (PR #46). The
  compliance service now differentiates between Annex III categories when
  deciding whether self-assessment is permitted versus notified-body
  assessment being required. High-risk systems covered by Annex III point 1
  (biometrics) and similar categories are blocked from self-assessment per
  the Act.
- **EAS schema UID derivation** (PR #50). On-chain schema UID is now derived
  using the exact encoding EAS itself uses (schema string, resolver address,
  revocable flag), matching anchors created on-chain with anchors looked up
  on-chain. Previously mismatched schema UIDs could cause
  `isAttestationValid` lookups to miss.
- **Attested event decoding hardened** (PR #50). `_extract_attestation_uid`
  now prefers web3.py's ABI-level `events.Attested().process_log` and falls
  back to a topic-signature match on `keccak("Attested(address,address,bytes32,bytes32)")`.
  Removes reliance on fragile byte offsets when reading receipt logs.
- **Test mock log shape** (this release). `tests/conftest.py`
  `blockchain_service_mock` now emits an Attested-event-shaped log with the
  correct topic[0] signature so the hardened decoder path is exercised end
  to end in CI.

### Infrastructure

- **GitHub Actions CI/CD** (PR #49). New `.github/workflows/` pipelines run
  a pytest matrix (Python 3.10, 3.11, 3.12, 3.13) on pull requests, plus
  `ruff`, `mypy`, `bandit`, and `pip-audit` jobs. A separate release
  workflow publishes to PyPI on tag push when `PYPI_API_TOKEN` is set as a
  repo secret.
- **pytest plugin compatibility** (this release). Default `addopts` now
  includes `-p no:logfire` so that transitive installs of
  `opentelemetry-sdk` (pulled via CrewAI) do not abort collection with
  `ImportError: cannot import name 'ReadableLogRecord'` when the installed
  `logfire` version targets a different otel ABI.

## [0.2.3] - 2026-02-27

### Added
- **Namespace package support**: Added `attestix` namespace package for cleaner imports
  - New import pattern: `from attestix.services.identity_service import IdentityService`
  - New import pattern: `from attestix.auth.crypto import generate_ed25519_keypair`
  - Flat imports still work for backward compatibility: `from services.identity_service import IdentityService`

### Changed
- Package structure now includes both flat modules and `attestix.*` namespace
- Updated pyproject.toml to include attestix namespace packages

### Fixed
- Replaced wildcard imports with explicit named imports and `__all__` declarations across all namespace shim modules
- Consistent relative imports in `attestix/auth/__init__.py` and `attestix/blockchain/__init__.py`
- Sorted `__all__` lists per RUF022 (ASCII case-sensitive ordering)
- Removed redundant `# noqa` comments from namespace modules

## [0.2.2] - 2026-02-22

### Added
- MCP Registry listing: published as `io.github.VibeTensor/attestix`
- `server.json` for MCP Registry verification
- Research paper page with citation references (BibTeX, APA, IEEE)

## [0.2.1] - 2026-02-21

### Added
- 91 conformance benchmark test suite (`tests/benchmarks/`) validating standards claims:
  - RFC 8032 Section 7.1 Ed25519 canonical test vectors (4 IETF vectors, 18 tests)
  - W3C VC Data Model 1.1 conformance (credential structure, proof, presentations, 24 tests)
  - W3C DID Core 1.0 conformance (did:key, did:web, roundtrip resolution, 16 tests)
  - UCAN v0.9.0 conformance (JWT header, payload, attenuation, revocation, 16 tests)
  - MCP tool registration conformance (47 tools, 9 modules, naming, 5 tests)
  - Performance benchmarks with hard latency thresholds (7 tests)
- Standards Conformance section in README with measured performance numbers
- Running the Test Suite section in configuration docs
- FAQ entry on standards validation methodology

### Changed
- Total automated tests: 193 -> 284 (193 functional + 91 conformance benchmarks)
- Updated research paper evaluation section with conformance test results and measured latencies
- Updated all documentation (architecture, changelog, contributing, roadmap, FAQ) with benchmark details

## [0.2.0] - 2026-02-21

### Added

**Blockchain Anchoring (6 tools)**
- Blockchain module: anchor identity and credential hashes to Base L2 via Ethereum Attestation Service (EAS)
- Merkle batch anchoring for audit log entries (cost optimization)
- On-chain verification and anchor status queries
- Gas cost estimation before anchoring

**Security Enhancements**
- SSRF protection with private IP blocking, metadata endpoint blocking, and DNS rebinding prevention
- Hash-chained audit trail with SHA-256 chain hashes for tamper-evident logging
- Encrypted key storage with AES-256-GCM when `ATTESTIX_KEY_PASSWORD` is set
- GDPR Article 17 right to erasure via `purge_agent_data` across all data stores

**New Tools**
- `purge_agent_data` - Complete GDPR erasure across all 6 storage files
- `revoke_delegation` - Revoke delegation tokens
- `update_compliance_profile` - Update existing compliance profiles
- `verify_credential_external` - Verify any W3C VC JSON from external sources
- `verify_presentation` - Verify Verifiable Presentations with embedded credentials

**Testing**
- 284 automated tests (unit, integration, e2e, conformance benchmarks)
- 91 conformance benchmark tests validating standards compliance:
  - RFC 8032 Section 7.1 Ed25519 canonical test vectors (4 IETF vectors, 18 tests)
  - W3C VC Data Model 1.1 conformance (credential structure, proof, presentations, 24 tests)
  - W3C DID Core 1.0 conformance (did:key, did:web, roundtrip resolution, 16 tests)
  - UCAN v0.9.0 conformance (JWT header, payload, attenuation, revocation, 16 tests)
  - MCP tool registration conformance (47 tools, 9 modules, naming, 5 tests)
  - Performance benchmarks with hard latency thresholds (7 tests)
- 16 user persona test scenarios (cybersecurity, government regulator, legal, healthcare, DPO, enterprise architect)
- 10 manual workflow simulations with real tool output
- Docker containerized test runner (`Dockerfile.test`)
- AWS CodeBuild CI spec

### Changed
- Identity module: 7 -> 8 tools (added purge_agent_data)
- Delegation module: 3 -> 4 tools (added revoke_delegation)
- Compliance module: 6 -> 7 tools (added update_compliance_profile)
- Credentials module: 6 -> 8 tools (added verify_credential_external, verify_presentation)
- Total tools: 36 -> 47 across 9 modules

## [0.1.0] - 2026-02-19

Initial public release.

### Added

**Identity & Trust (19 tools)**
- Identity module (7 tools): create, resolve, verify, translate, list, get, revoke agent identities via Unified Agent Identity Tokens (UAITs)
- Agent Cards module (3 tools): parse, generate, and discover Google A2A-compatible agent cards
- DID module (3 tools): create did:key and did:web identifiers, resolve any DID via Universal Resolver
- Delegation module (3 tools): UCAN-style capability delegation with EdDSA-signed JWT tokens
- Reputation module (3 tools): recency-weighted trust scoring with category breakdown

**EU AI Act Compliance (17 tools)**
- Compliance module (6 tools): risk categorization (minimal/limited/high), conformity assessments (Article 43), Annex V declarations of conformity
- Credentials module (6 tools): W3C Verifiable Credentials (VC Data Model 1.1) with Ed25519Signature2020 proofs, Verifiable Presentations
- Provenance module (5 tools): training data provenance (Article 10), model lineage (Article 11), audit trail (Article 12)

**Infrastructure**
- Ed25519 cryptographic signing for all persistent records
- JSON file storage with file locking and corruption recovery
- Lazy service initialization with TTL cache
- MCP server via FastMCP with stderr-safe logging
- PyPI packaging via pyproject.toml

**Documentation**
- Getting Started guide
- EU AI Act Compliance workflow guide
- Risk Classification decision tree
- Concepts reference (UAIT, DID, VC, VP, UCAN, Ed25519)
- Complete API reference for all tools
- Integration guide (LangChain, CrewAI, AutoGen, MCP client)
- FAQ
- 5 runnable example scripts

### Security

- Private keys never returned in MCP tool responses (stored locally in .keypairs.json)
- Mutable fields (proof, credentialStatus) excluded from VC signature payloads
- High-risk systems blocked from self-assessment (requires third-party per Article 43)
- SSRF protection on agent discovery URLs
- All sensitive files excluded from git (.signing_key.json, .keypairs.json, .env)
