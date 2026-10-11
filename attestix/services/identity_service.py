"""Core identity service for Attestix.

Manages Unified Agent Identity Tokens (UAITs): create, read, list,
revoke, verify, and sign operations.
"""

from attestix.config import storage_transactional

import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from attestix.auth.crypto import (
    did_key_fragment,
    verify_json_signature,
    did_key_to_public_key,
)
from attestix.auth.token_parser import extract_identity_from_token
from attestix.config import (
    DEFAULT_EXPIRY_DAYS,
    UAIT_VERSION,
    load_identities,
    save_identities,
)
from attestix.audit import AuditEventEmitter, resolve_emitter, safe_emit
from attestix.errors import ErrorCategory, log_and_format_error
from attestix.signing import InProcessSigner, Signer
from attestix.storage.repository import DEFAULT_TENANT


#: Maximum allowed display_name length. Mirrors the API layer constraint so
#: programmatic callers that bypass FastAPI still get a validation error.
MAX_DISPLAY_NAME_LENGTH = 500


class IdentityService:
    """Manages UAIT lifecycle."""

    # Fields excluded from signature (mutable after creation)
    MUTABLE_FIELDS = {"signature", "revoked", "revocation_reason", "revoked_at",
                      "reputation_score", "eu_compliance"}

    def __init__(
        self,
        signer: Optional[Signer] = None,
        emitter: Optional[AuditEventEmitter] = None,
        tenant_id: str = DEFAULT_TENANT,
    ):
        # v0.4.0: sign through the pluggable Signer seam. Defaults to the
        # in-process Ed25519 signer, which wraps load_or_create_signing_key and
        # reproduces v0.3.0 signatures byte-for-byte. Passing an alternate Signer
        # (e.g. KMS) swaps the backend with no change to this method's signature.
        self._signer = signer or InProcessSigner()
        self._server_did = self._signer.did
        # v0.4.0 (T033/T034): per-service audit emitter + tenant context. The
        # emitter is a side channel (see audit.service_hook); tenant defaults to
        # "default" so single-tenant self-host behavior is byte-identical.
        self._emitter = resolve_emitter(emitter)
        self._tenant_id = tenant_id

    def _signable_payload(self, uait: dict) -> dict:
        """Extract only immutable fields for signing/verification."""
        return {k: v for k, v in uait.items() if k not in self.MUTABLE_FIELDS}

    @staticmethod
    def _mask_token(token: str) -> str:
        """Redact credentials before storage, including short or unknown tokens."""
        return "***" if token else ""

    @property
    def server_did(self) -> str:
        return self._server_did

    @storage_transactional
    def create_identity(
        self,
        display_name: str,
        source_protocol: str,
        identity_token: str = "",
        capabilities: Optional[List[str]] = None,
        description: str = "",
        issuer_name: str = "",
        expiry_days: Optional[int] = None,
    ) -> dict:
        """Create a new UAIT from any identity source."""
        # Defense in depth: validate even when callers skip the API layer.
        # Issue #32 - reject empty/whitespace/overlong display_name.
        if display_name is None:
            raise ValueError("display_name is required")
        if not isinstance(display_name, str):
            raise ValueError("display_name must be a string")
        stripped = display_name.strip()
        if not stripped:
            raise ValueError("display_name must not be empty or whitespace-only")
        if len(stripped) > MAX_DISPLAY_NAME_LENGTH:
            raise ValueError(
                f"display_name must be at most {MAX_DISPLAY_NAME_LENGTH} characters"
            )
        if any(ord(ch) < 0x20 and ch != "\t" for ch in stripped):
            raise ValueError("display_name contains disallowed control characters")
        display_name = stripped

        agent_id = f"attestix:{uuid.uuid4().hex[:16]}"
        now = datetime.now(timezone.utc)
        exp_days = expiry_days if expiry_days is not None else DEFAULT_EXPIRY_DAYS
        expires_at = (now + timedelta(days=exp_days)).isoformat()

        # Extract info from token if provided
        token_info = {}
        if identity_token:
            token_info = extract_identity_from_token(identity_token)

        uait = {
            "version": UAIT_VERSION,
            "agent_id": agent_id,
            # v0.4.0-rc.3 (P1 #2 of the rc.2 RC validation): populate the
            # top-level `did` field with the issuer DID so callers reading
            # `agent.get("did")` (the indie-dev quickstart and the public
            # AgentFacts-style consumers) get a value rather than None.
            "did": self._server_did,
            "display_name": display_name,
            "description": description,
            "source_protocol": source_protocol,
            "identity_token": self._mask_token(identity_token),
            "token_info": token_info,
            "capabilities": capabilities or [],
            "issuer": {
                "name": issuer_name or "self",
                "did": self._server_did,
            },
            "created_at": now.isoformat(),
            "expires_at": expires_at,
            "revoked": False,
            "revocation_reason": None,
            "reputation_score": None,
            "eu_compliance": None,
            "signature": None,
        }

        # Sign only immutable fields (through the pluggable Signer seam)
        signable = self._signable_payload(uait)
        uait["signature"] = self._signer.sign(signable)

        # Persist
        data = load_identities()
        data["agents"].append(uait)
        save_identities(data)

        safe_emit(
            self._emitter,
            action="identity.create",
            target_id=agent_id,
            target_collection="identities",
            actor=self._server_did,
            tenant_id=self._tenant_id,
            after={"agent_id": agent_id, "source_protocol": source_protocol},
        )

        return uait

    def get_identity(self, agent_id: str) -> Optional[dict]:
        """Get a single UAIT by agent_id."""
        data = load_identities()
        for agent in data["agents"]:
            if agent["agent_id"] == agent_id:
                return agent
        return None

    def list_identities(
        self,
        source_protocol: Optional[str] = None,
        include_revoked: bool = False,
        limit: int = 50,
        risk_category: Optional[str] = None,
        name_contains: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[dict]:
        """List UAITs with optional filters.

        All filters compose with logical AND and preserve every existing
        parameter and default (issue #37).

        Args:
            source_protocol: Exact-match filter on the identity source protocol.
            include_revoked: Include revoked identities (default excludes them).
            limit: Maximum number of identities to return.
            risk_category: Filter to agents whose EU AI Act compliance profile
                carries this risk category ("minimal"|"limited"|"high"|
                "unacceptable"). Joined in the service layer against the
                compliance profiles keyed by ``agent_id``. Agents without a
                profile are excluded when this filter is set.
            name_contains: Case-insensitive substring match on ``display_name``.
            status: Lifecycle status filter — "active" (not revoked, not
                expired), "revoked", or "expired". When ``status`` is set it is
                authoritative; "revoked"/"expired" implicitly include the
                relevant agents regardless of ``include_revoked``.
        """
        data = load_identities()

        # Build the agent_id -> risk_category join up-front so each agent is
        # O(1) to classify (issue #37). Compliance profiles are keyed by
        # agent_id in ComplianceService storage.
        risk_by_agent: dict = {}
        if risk_category is not None:
            from attestix.config import load_compliance
            comp_data = load_compliance()
            for profile in comp_data.get("profiles", []):
                aid = profile.get("agent_id")
                if aid:
                    risk_by_agent[aid] = profile.get("risk_category")

        wanted_risk = risk_category.lower() if risk_category else None
        wanted_name = name_contains.lower() if name_contains else None
        wanted_status = status.lower() if status else None
        now = datetime.now(timezone.utc)

        results = []
        for agent in data["agents"]:
            revoked = bool(agent.get("revoked"))

            # Compute lifecycle status (active|revoked|expired) for the agent.
            expired = False
            expires_at = agent.get("expires_at")
            if expires_at and not revoked:
                try:
                    expired = now >= datetime.fromisoformat(expires_at)
                except ValueError:
                    expired = False
            if revoked:
                agent_status = "revoked"
            elif expired:
                agent_status = "expired"
            else:
                agent_status = "active"

            if wanted_status is not None:
                # An explicit status filter is authoritative over include_revoked.
                if agent_status != wanted_status:
                    continue
            else:
                # Legacy behaviour: hide revoked unless include_revoked is set.
                if not include_revoked and revoked:
                    continue

            if source_protocol and agent.get("source_protocol") != source_protocol:
                continue

            if wanted_name is not None:
                if wanted_name not in (agent.get("display_name") or "").lower():
                    continue

            if wanted_risk is not None:
                agent_risk = risk_by_agent.get(agent.get("agent_id"))
                if agent_risk is None or agent_risk.lower() != wanted_risk:
                    continue

            results.append(agent)
            if len(results) >= limit:
                break
        return results

    @storage_transactional
    def revoke_identity(self, agent_id: str, reason: str = "") -> Optional[dict]:
        """Mark a UAIT as revoked."""
        data = load_identities()
        for agent in data["agents"]:
            if agent["agent_id"] == agent_id:
                agent["revoked"] = True
                agent["revocation_reason"] = reason
                agent["revoked_at"] = datetime.now(timezone.utc).isoformat()
                save_identities(data)
                safe_emit(
                    self._emitter,
                    action="identity.revoke",
                    target_id=agent_id,
                    target_collection="identities",
                    actor=self._server_did,
                    tenant_id=self._tenant_id,
                    after={"agent_id": agent_id, "revoked": True},
                )
                return agent
        return None

    def verify_identity(self, agent_id: str) -> dict:
        """Verify a UAIT: check existence, revocation, expiry, and signature."""
        agent = self.get_identity(agent_id)
        if not agent:
            return {
                "valid": False,
                "agent_id": agent_id,
                "checks": {"exists": False},
            }

        checks = {"exists": True}

        # Check revocation
        checks["not_revoked"] = not agent.get("revoked", False)

        # Check expiry
        expires_at = agent.get("expires_at")
        if expires_at:
            exp_dt = datetime.fromisoformat(expires_at)
            checks["not_expired"] = datetime.now(timezone.utc) < exp_dt
        else:
            checks["not_expired"] = True

        # Check signature (only immutable fields)
        signature = agent.get("signature")
        if signature:
            signable = self._signable_payload(agent)
            try:
                server_pub = did_key_to_public_key(self._server_did)
                checks["signature_valid"] = verify_json_signature(
                    server_pub, signable, signature
                )
            except ValueError:
                checks["signature_valid"] = False
            except Exception as e:
                checks["signature_valid"] = False
                log_and_format_error("verify_identity", e, ErrorCategory.CRYPTO,
                                     agent_id=agent_id)
        else:
            checks["signature_valid"] = False

        valid = all(v for v in checks.values() if isinstance(v, bool))
        return {
            "valid": valid,
            "agent_id": agent_id,
            "display_name": agent.get("display_name"),
            "checks": checks,
        }

    def translate_identity(self, agent_id: str, target_format: str) -> Optional[dict]:
        """Convert a UAIT to another format.

        Supported target_format values:
        - a2a_agent_card: Google A2A Agent Card JSON
        - did_document: W3C DID Document
        - oauth_claims: OAuth 2.0 token claims
        - summary: Human-readable summary
        """
        agent = self.get_identity(agent_id)
        if not agent:
            return None

        if target_format == "a2a_agent_card":
            return self._to_agent_card(agent)
        elif target_format == "did_document":
            return self._to_did_document(agent)
        elif target_format == "oauth_claims":
            return self._to_oauth_claims(agent)
        elif target_format == "summary":
            return self._to_summary(agent)
        else:
            return {"error": f"Unknown target format: {target_format}"}

    @storage_transactional
    def purge_agent_data(self, agent_id: str) -> dict:
        """Erase agent references from local live and recovery documents.

        Includes related audit targets and cached idempotency responses.
        On-chain anchors and operator-managed external copies require separate
        retention policies. Failures propagate; multiple files have no rollback.
        """
        if not isinstance(agent_id, str) or not agent_id.strip():
            raise ValueError("agent_id must be a non-empty string")
        import json
        from attestix import config
        from attestix.storage.file_repository import _COLLECTIONS

        repository = config._repo()
        documents = {name: repository.load_document(name) for name in _COLLECTIONS}

        def mentions(value, references):
            if isinstance(value, str):
                if value in references:
                    return True
                # Cached HTTP bodies store structured JSON as a string.
                if value.lstrip().startswith(("{", "[")):
                    try:
                        return mentions(json.loads(value), references)
                    except (ValueError, TypeError):
                        pass
                return False
            if isinstance(value, dict):
                return any(mentions(k, references) or mentions(v, references)
                           for k, v in value.items())
            if isinstance(value, list):
                return any(mentions(item, references) for item in value)
            return False

        references = {agent_id}
        id_fields = {"id", "profile_id", "assessment_id", "declaration_id",
                     "entry_id", "jti", "delegation_id", "anchor_id"}
        recovery_documents = [
            document for collection in documents
            for document in repository.recovery_documents(collection)
        ]
        for document in [*documents.values(), *recovery_documents]:
            for rows in document.values():
                if isinstance(rows, list):
                    for row in rows:
                        if isinstance(row, dict) and mentions(row, {agent_id}):
                            for field in id_fields:
                                identifier = row.get(field)
                                if isinstance(identifier, str) and identifier:
                                    references.add(identifier)

        count_names = {
            ("identities", "agents"): "identities",
            ("credentials", "credentials"): "credentials",
            ("compliance", "profiles"): "compliance_profiles",
            ("compliance", "assessments"): "compliance_assessments",
            ("compliance", "declarations"): "compliance_declarations",
            ("delegations", "delegations"): "delegations",
            ("provenance", "entries"): "provenance_entries",
            ("provenance", "audit_log"): "audit_log_entries",
            ("reputation", "interactions"): "reputation_interactions",
            ("audit", "events"): "audit_events",
            ("idempotency", "keys"): "idempotency_responses",
            ("anchors", "anchors"): "local_anchor_references",
        }
        purged = {
            "agent_id": agent_id,
            "purged_at": datetime.now(timezone.utc).isoformat(),
            "counts": {},
            "external_copies": "Operator-managed exports and remote backups require separate erasure",
        }
        for collection in documents:
            def scrub(document, collection=collection):
                counts = {}
                for field, value in list(document.items()):
                    if isinstance(value, list):
                        retained = [row for row in value if not mentions(row, references)]
                        document[field] = retained
                        count_name = count_names.get((collection, field))
                        if count_name:
                            counts[count_name] = len(value) - len(retained)
                    elif collection == "reputation" and field == "scores":
                        document[field] = {
                            key: score for key, score in value.items()
                            if not mentions(key, references) and not mentions(score, references)
                        }
                return document, counts

            # Propagate failures so partial erasure cannot look successful.
            purged["counts"].update(repository.erase_from_document(collection, scrub))
        return purged

    @storage_transactional
    def update_compliance_ref(self, agent_id: str, profile_id: str):
        """Link an EU AI Act compliance profile to a UAIT."""
        data = load_identities()
        for agent in data["agents"]:
            if agent["agent_id"] == agent_id:
                agent["eu_compliance"] = profile_id
                save_identities(data)
                safe_emit(
                    self._emitter,
                    action="identity.update",
                    target_id=agent_id,
                    target_collection="identities",
                    actor=self._server_did,
                    tenant_id=self._tenant_id,
                    after={"agent_id": agent_id, "eu_compliance": profile_id},
                )
                return
        return

    @storage_transactional
    def update_reputation(self, agent_id: str, score: float):
        """Update the reputation score on a UAIT."""
        data = load_identities()
        for agent in data["agents"]:
            if agent["agent_id"] == agent_id:
                agent["reputation_score"] = round(score, 4)
                save_identities(data)
                safe_emit(
                    self._emitter,
                    action="identity.update",
                    target_id=agent_id,
                    target_collection="identities",
                    actor=self._server_did,
                    tenant_id=self._tenant_id,
                    after={"agent_id": agent_id, "reputation_score": round(score, 4)},
                )
                return
        return

    # --- Translation helpers ---

    def _to_agent_card(self, agent: dict) -> dict:
        """Convert UAIT to A2A Agent Card format."""
        skills = []
        for cap in agent.get("capabilities", []):
            skills.append({
                "id": hashlib.sha256(cap.encode()).hexdigest()[:8],
                "name": cap,
                "description": f"Capability: {cap}",
            })

        agent_url = f"attestix://{agent['agent_id']}"
        return {
            "id": hashlib.sha256(agent["agent_id"].encode()).hexdigest()[:16],
            "name": agent["display_name"],
            "description": agent.get("description", ""),
            "url": agent_url,
            "version": agent.get("version", UAIT_VERSION),
            "capabilities": {
                "streaming": False,
                "pushNotifications": False,
            },
            "skills": skills,
            "endpoints": [
                {
                    "url": f"{agent_url}/tasks",
                    "protocol": "attestix",
                    "method": "POST",
                }
            ],
            "provider": {
                "organization": agent["issuer"].get("name", ""),
            },
            "authentication": {
                "schemes": ["attestix-uait"],
                "credentials": agent["agent_id"],
            },
            "_attestix_metadata": {
                "agent_id": agent["agent_id"],
                "source_protocol": agent.get("source_protocol"),
                "reputation_score": agent.get("reputation_score"),
            },
        }

    def _to_did_document(self, agent: dict) -> dict:
        """Convert UAIT to W3C DID Document format."""
        did = agent["issuer"].get("did", f"did:attestix:{agent['agent_id']}")
        # Get public key multibase for the server DID
        pub_multibase = None
        if did.startswith("did:key:z"):
            try:
                from attestix.auth.crypto import did_key_to_public_key, public_key_to_bytes, ED25519_MULTICODEC_PREFIX
                import base58
                pub_key = did_key_to_public_key(did)
                pub_bytes = public_key_to_bytes(pub_key)
                pub_multibase = "z" + base58.b58encode(
                    ED25519_MULTICODEC_PREFIX + pub_bytes
                ).decode("ascii")
            except (ValueError, ImportError):
                pass  # Graceful degradation if crypto libs unavailable

        fragment = did_key_fragment(did) if did.startswith("did:key:z") else "#key-1"
        vm = {
            "id": f"{did}{fragment}",
            "type": "Ed25519VerificationKey2020",
            "controller": did,
        }
        if pub_multibase:
            vm["publicKeyMultibase"] = pub_multibase

        return {
            "@context": [
                "https://www.w3.org/ns/did/v1",
                "https://w3id.org/security/suites/ed25519-2020/v1",
            ],
            "id": did,
            "controller": did,
            "verificationMethod": [vm],
            "authentication": [f"{did}{fragment}"],
            "service": [
                {
                    "id": f"{did}#attestix",
                    "type": "AttestixIdentity",
                    "serviceEndpoint": {
                        "agent_id": agent["agent_id"],
                        "display_name": agent["display_name"],
                        "capabilities": agent.get("capabilities", []),
                    },
                }
            ],
        }

    def _to_oauth_claims(self, agent: dict) -> dict:
        """Convert UAIT to OAuth 2.0 token claims."""
        return {
            "sub": agent["agent_id"],
            "iss": agent["issuer"].get("did", "attestix"),
            "name": agent["display_name"],
            "scope": " ".join(agent.get("capabilities", [])),
            "iat": agent.get("created_at"),
            "exp": agent.get("expires_at"),
            "attestix_version": agent.get("version"),
            "source_protocol": agent.get("source_protocol"),
        }

    def _to_summary(self, agent: dict) -> dict:
        """Human-readable summary of a UAIT."""
        return {
            "agent_id": agent["agent_id"],
            "display_name": agent["display_name"],
            "description": agent.get("description", ""),
            "source_protocol": agent.get("source_protocol"),
            "capabilities": agent.get("capabilities", []),
            "issuer": agent["issuer"].get("name", ""),
            "created_at": agent.get("created_at"),
            "expires_at": agent.get("expires_at"),
            "revoked": agent.get("revoked", False),
            "reputation_score": agent.get("reputation_score"),
            "eu_compliance": agent.get("eu_compliance"),
            "signature_present": bool(agent.get("signature")),
        }
