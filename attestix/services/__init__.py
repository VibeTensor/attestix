"""Attestix services - re-exports from flat module for namespace compatibility.

Services:
    - IdentityService: Unified Agent Identity Tokens (UAITs)
    - CredentialService: W3C Verifiable Credentials
    - ComplianceService: EU AI Act compliance profiles
    - DelegationService: UCAN-style capability delegation
    - ReputationService: Trust scoring
    - ProvenanceService: Training data, lineage, audit trails
    - AgentCardService: A2A agent card operations
    - BlockchainService: EAS anchoring on Base L2
"""

# Re-export all services from the flat module
from services.identity_service import IdentityService
from services.credential_service import CredentialService
from services.compliance_service import ComplianceService
from services.delegation_service import DelegationService
from services.reputation_service import ReputationService
from services.provenance_service import ProvenanceService
from services.agent_card_service import AgentCardService
from services.blockchain_service import BlockchainService

# Re-export submodules for `from attestix.services.X import Y` pattern
from services import identity_service
from services import credential_service
from services import compliance_service
from services import delegation_service
from services import reputation_service
from services import provenance_service
from services import agent_card_service
from services import blockchain_service

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
    # Submodules
    "identity_service",
    "credential_service",
    "compliance_service",
    "delegation_service",
    "reputation_service",
    "provenance_service",
    "agent_card_service",
    "blockchain_service",
]
