"""Attestix services.

Identity, credentials, compliance, delegation, reputation, provenance,
agent cards, blockchain anchoring, DID operations.

Services:
    - IdentityService: Unified Agent Identity Tokens (UAITs)
    - CredentialService: W3C Verifiable Credentials
    - ComplianceService: EU AI Act compliance profiles
    - DelegationService: UCAN-style capability delegation
    - ReputationService: Trust scoring
    - ProvenanceService: Training data, lineage, audit trails
    - AgentCardService: A2A agent card operations
    - BlockchainService: EAS anchoring on Base L2
    - DIDService: DID document operations
"""

from attestix.services.identity_service import IdentityService
from attestix.services.credential_service import CredentialService
from attestix.services.compliance_service import ComplianceService
from attestix.services.delegation_service import DelegationService
from attestix.services.reputation_service import ReputationService
from attestix.services.provenance_service import ProvenanceService
from attestix.services.agent_card_service import AgentCardService
from attestix.services.blockchain_service import BlockchainService
from attestix.services.did_service import DIDService

# Re-export submodules for `from attestix.services.X import Y` pattern
from attestix.services import identity_service
from attestix.services import credential_service
from attestix.services import compliance_service
from attestix.services import delegation_service
from attestix.services import reputation_service
from attestix.services import provenance_service
from attestix.services import agent_card_service
from attestix.services import blockchain_service
from attestix.services import did_service

__all__ = [
    # Service classes
    "IdentityService",
    "CredentialService",
    "ComplianceService",
    "DelegationService",
    "ReputationService",
    "ProvenanceService",
    "AgentCardService",
    "BlockchainService",
    "DIDService",
    # Submodules
    "identity_service",
    "credential_service",
    "compliance_service",
    "delegation_service",
    "reputation_service",
    "provenance_service",
    "agent_card_service",
    "blockchain_service",
    "did_service",
]
