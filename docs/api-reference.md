# API Reference

All 47 Attestix MCP tools organized by module.

## Identity (8 tools)

### `create_agent_identity`

Create a Unified Agent Identity Token (UAIT) from any identity source.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `display_name` | string | Yes | - | Human-readable name for the agent |
| `source_protocol` | string | No | `"manual"` | Origin protocol: `mcp_oauth`, `a2a`, `did`, `api_key`, `manual` |
| `identity_token` | string | No | `""` | Original token/DID/URL to analyze |
| `capabilities` | string | No | `""` | Comma-separated capabilities (e.g., `"data_analysis,reporting"`) |
| `description` | string | No | `""` | What this agent does |
| `issuer_name` | string | No | `""` | Who issued this identity |
| `expiry_days` | int | No | `365` | Days until expiry |

**Returns:** UAIT object with `agent_id`, `signature`, `issuer.did`, and all metadata.

### `resolve_identity`

Auto-detect token type (JWT/DID/URL/API key) and create a UAIT.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `identity_token` | string | Yes | Any identity string to analyze and register |

### `verify_identity`

Check existence, revocation, expiry, and cryptographic signature.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_id` | string | Yes | Attestix agent ID (e.g., `attestix:abc123...`) |

**Returns:** `{ "valid": bool, "checks": { "exists", "not_revoked", "not_expired", "signature_valid" } }`

### `translate_identity`

Convert a UAIT to another identity format.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `agent_id` | string | Yes | - | Agent ID to translate |
| `target_format` | string | No | `"summary"` | One of: `a2a_agent_card`, `did_document`, `oauth_claims`, `summary` |

### `list_identities`

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `source_protocol` | string | No | `""` | Filter by protocol. Empty = all |
| `include_revoked` | bool | No | `false` | Include revoked identities |
| `limit` | int | No | `50` | Maximum results |

### `get_identity`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_id` | string | Yes | Agent ID to retrieve |

### `revoke_identity`

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `agent_id` | string | Yes | - | Agent ID to revoke |
| `reason` | string | No | `""` | Revocation reason |

### `purge_agent_data`

GDPR Article 17 right to erasure. Removes all data for an agent across all storage files (identities, credentials, compliance, provenance, audit logs, reputation, delegations).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_id` | string | Yes | Agent ID to completely erase |

**Returns:** Summary of purged records per store.

---

## Agent Cards (3 tools)

### `parse_agent_card`

Parse an A2A Agent Card JSON into normalized fields.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_card_json` | string | Yes | JSON string of the agent card |

### `generate_agent_card`

Generate a valid A2A Agent Card (agent.json) for hosting.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | string | Yes | - | Agent display name |
| `url` | string | Yes | - | Base URL where agent is hosted |
| `description` | string | No | `""` | What the agent does |
| `skills_json` | string | No | `"[]"` | JSON array of skill objects |
| `version` | string | No | `"1.0.0"` | Agent version |

### `discover_agent`

Fetch `/.well-known/agent.json` from a URL (HTTPS only, SSRF-protected).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | Yes | Base URL of the agent (e.g., `https://agent.example.com`) |

---

## DID (3 tools)

### `create_did_key`

Generate an ephemeral `did:key` with Ed25519 keypair. Private key stored locally in `.keypairs.json`.

No parameters required.

**Returns:** `{ "did": "did:key:z6Mk...", "did_document": {...}, "keypair_id": "keypair:...", "public_key_multibase": "z..." }`

### `create_did_web`

Generate a `did:web` DID Document for self-hosting.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `domain` | string | Yes | - | Domain name (e.g., `example.com`) |
| `path` | string | No | `""` | Optional path (e.g., `agents/myagent`) |

### `resolve_did`

Resolve any DID to its DID Document. Supports `did:key` (local), `did:web` (HTTPS), others via Universal Resolver.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `did` | string | Yes | DID to resolve (e.g., `did:key:z6Mk...`) |

---

## Delegation (4 tools)

### `create_delegation`

Create a UCAN-style delegation JWT with EdDSA signature.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `issuer_agent_id` | string | Yes | - | Agent granting capabilities |
| `audience_agent_id` | string | Yes | - | Agent receiving capabilities |
| `capabilities` | string | Yes | - | Comma-separated capabilities to delegate |
| `expiry_hours` | int | No | `24` | Hours until delegation expires |
| `parent_token` | string | No | `""` | Parent delegation token for chaining |

### `verify_delegation`

Verify a delegation JWT: signature, expiry, revocation, and structure.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `token` | string | Yes | JWT delegation token |

### `list_delegations`

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `agent_id` | string | No | `""` | Filter by agent ID |
| `role` | string | No | `"any"` | `issuer`, `audience`, or `any` |
| `include_expired` | bool | No | `false` | Include expired delegations |

### `revoke_delegation`

Revoke a delegation token, immediately invalidating the delegated capabilities.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `delegation_id` | string | Yes | - | Delegation ID to revoke |
| `reason` | string | No | `""` | Revocation reason |

---

## Reputation (3 tools)

### `record_interaction`

Record an interaction outcome and update trust score.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `agent_id` | string | Yes | - | Agent being rated |
| `outcome` | string | Yes | - | `success`, `failure`, or `partial` |
| `category` | string | No | `"general"` | Category (e.g., `data_quality`, `response_time`) |
| `details` | string | No | `""` | Additional context |

### `get_reputation`

Get reputation score with category breakdown.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_id` | string | Yes | Agent ID to query |

**Returns:** `{ "score": 0.85, "total_interactions": 42, "category_breakdown": {...} }`

### `query_reputation`

Search agents by reputation criteria.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `min_score` | float | No | `0.0` | Minimum reputation score |
| `category` | string | No | `""` | Filter by interaction category |
| `limit` | int | No | `20` | Maximum results |

---

## Compliance (7 tools)

### `create_compliance_profile`

Create an EU AI Act compliance profile with risk categorization.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `agent_id` | string | Yes | - | Agent ID |
| `risk_category` | string | Yes | - | `minimal`, `limited`, or `high` |
| `provider_name` | string | Yes | - | Company legal name |
| `intended_purpose` | string | No | `""` | What the AI system does |
| `transparency_obligations` | string | No | `""` | How transparency requirements are met |
| `human_oversight_measures` | string | No | `""` | Human oversight mechanisms (required for high-risk) |

### `get_compliance_profile`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_id` | string | Yes | Agent ID |

### `update_compliance_profile`

Update an existing compliance profile's fields.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `agent_id` | string | Yes | - | Agent ID |
| `intended_purpose` | string | No | `""` | Updated intended purpose |
| `transparency_obligations` | string | No | `""` | Updated transparency measures |
| `human_oversight_measures` | string | No | `""` | Updated human oversight |

### `get_compliance_status`

Gap analysis showing completed vs missing requirements with completion percentage.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_id` | string | Yes | Agent ID |

### `record_conformity_assessment`

Record a conformity assessment result (Article 43).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `agent_id` | string | Yes | - | Agent ID |
| `assessment_type` | string | Yes | - | `self` or `third_party` |
| `assessor_name` | string | Yes | - | Assessor or notified body name |
| `result` | string | Yes | - | `pass`, `conditional`, or `fail` |
| `findings` | string | No | `""` | Detailed findings |
| `ce_marking_eligible` | bool | No | `false` | CE marking eligibility |

### `generate_declaration_of_conformity`

Generate Annex V declaration + auto-issue W3C Verifiable Credential.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_id` | string | Yes | Agent ID |

### `list_compliance_profiles`

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `risk_category` | string | No | `""` | Filter by risk level |
| `compliant_only` | bool | No | `false` | Only completed declarations |
| `limit` | int | No | `50` | Maximum results |

---

## Credentials (8 tools)

### `issue_credential`

Issue a W3C Verifiable Credential with Ed25519Signature2020 proof.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `subject_agent_id` | string | Yes | - | Agent this credential is about |
| `credential_type` | string | Yes | - | Type (e.g., `EUAIActComplianceCredential`) |
| `issuer_name` | string | Yes | - | Issuing authority name |
| `claims_json` | string | Yes | - | JSON string of claims |
| `expiry_days` | int | No | `365` | Days until expiry |

### `verify_credential`

Check signature, expiry, and revocation status.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `credential_id` | string | Yes | Credential URN (e.g., `urn:uuid:...`) |

### `revoke_credential`

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `credential_id` | string | Yes | - | Credential URN to revoke |
| `reason` | string | No | `""` | Revocation reason |

### `get_credential`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `credential_id` | string | Yes | Credential URN |

### `list_credentials`

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `agent_id` | string | No | `""` | Filter by subject |
| `credential_type` | string | No | `""` | Filter by type |
| `valid_only` | bool | No | `false` | Exclude revoked/expired |
| `limit` | int | No | `50` | Maximum results |

### `create_verifiable_presentation`

Bundle multiple VCs into a signed VP for a specific verifier.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `agent_id` | string | Yes | - | Holder/presenter agent ID |
| `credential_ids` | string | Yes | - | Comma-separated credential URNs |
| `audience_did` | string | No | `""` | Verifier's DID |
| `challenge` | string | No | `""` | Nonce from verifier for replay protection |

### `verify_credential_external`

Verify any W3C Verifiable Credential JSON from an external source (does not need to be in the local store).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `credential_json` | string | Yes | Full JSON string of the Verifiable Credential |

**Returns:** `{ "valid": bool, "checks": { "structure_valid", "signature_valid", "not_expired" } }`

### `verify_presentation`

Verify a Verifiable Presentation including all embedded credentials.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `presentation_json` | string | Yes | Full JSON string of the Verifiable Presentation |

**Returns:** `{ "valid": bool, "checks": { "structure_valid", "vp_signature_valid", "challenge_present", "domain_present", "credentials_valid", "holder_matches_subjects" } }`

---

## Provenance (5 tools)

### `record_training_data`

Record a training data source (Article 10 compliance).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `agent_id` | string | Yes | - | Agent ID |
| `dataset_name` | string | Yes | - | Dataset name |
| `source_url` | string | No | `""` | Where the data came from |
| `license` | string | No | `""` | Data license (e.g., `CC-BY-4.0`) |
| `data_categories` | string | No | `""` | Comma-separated categories |
| `contains_personal_data` | bool | No | `false` | Personal data flag |
| `data_governance_measures` | string | No | `""` | Quality, bias, cleaning measures |

### `record_model_lineage`

Record model lineage chain (Article 11 compliance).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `agent_id` | string | Yes | - | Agent ID |
| `base_model` | string | Yes | - | Foundation model name |
| `base_model_provider` | string | No | `""` | Model provider (e.g., `Anthropic`) |
| `fine_tuning_method` | string | No | `""` | Adaptation method |
| `evaluation_metrics_json` | string | No | `"{}"` | JSON of metrics |

### `log_action`

Log an agent action for Article 12 audit trail.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `agent_id` | string | Yes | - | Agent ID |
| `action_type` | string | Yes | - | `inference`, `delegation`, `data_access`, or `external_call` |
| `input_summary` | string | No | `""` | What was input |
| `output_summary` | string | No | `""` | What was output |
| `decision_rationale` | string | No | `""` | Why this decision |
| `human_override` | bool | No | `false` | Was there human intervention? |

### `get_provenance`

Get full provenance record (training data + model lineage + audit summary).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_id` | string | Yes | Agent ID |

### `get_audit_trail`

Query audit trail with filters.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `agent_id` | string | Yes | - | Agent ID |
| `action_type` | string | No | `""` | Filter by action type |
| `start_date` | string | No | `""` | ISO date filter (start) |
| `end_date` | string | No | `""` | ISO date filter (end) |
| `limit` | int | No | `50` | Maximum results |

---

## Blockchain (6 tools)

### `anchor_identity`

Anchor an identity hash to Base L2 via Ethereum Attestation Service.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_id` | string | Yes | Agent ID to anchor |

### `anchor_credential`

Anchor a credential hash to Base L2 via EAS.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `credential_id` | string | Yes | Credential URN to anchor |

### `anchor_audit_batch`

Merkle batch anchor of audit log entries for an agent.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `agent_id` | string | Yes | - | Agent ID |
| `limit` | int | No | `100` | Maximum entries to include in batch |

**Returns:** Merkle root hash, entry count, and transaction receipt.

### `verify_anchor`

Verify an on-chain anchor against local data.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `artifact_id` | string | Yes | Agent ID or credential URN to verify |

### `get_anchor_status`

Get all anchoring records for an artifact.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `artifact_id` | string | Yes | Agent ID or credential URN |

### `estimate_anchor_cost`

Estimate gas cost for anchoring an artifact.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `artifact_type` | string | Yes | - | `identity`, `credential`, or `audit_batch` |
