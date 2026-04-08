"""Dependency injection for Attestix API services.

Provides FastAPI dependency functions that return cached singleton
service instances via the shared service cache.
"""

from services.cache import get_service
from services.identity_service import IdentityService
from services.credential_service import CredentialService
from services.compliance_service import ComplianceService
from services.delegation_service import DelegationService
from services.reputation_service import ReputationService
from services.provenance_service import ProvenanceService
from services.blockchain_service import BlockchainService
from services.did_service import DIDService
from services.agent_card_service import AgentCardService


def get_identity_service() -> IdentityService:
    return get_service(IdentityService)


def get_credential_service() -> CredentialService:
    return get_service(CredentialService)


def get_compliance_service() -> ComplianceService:
    return get_service(ComplianceService)


def get_delegation_service() -> DelegationService:
    return get_service(DelegationService)


def get_reputation_service() -> ReputationService:
    return get_service(ReputationService)


def get_provenance_service() -> ProvenanceService:
    return get_service(ProvenanceService)


def get_blockchain_service() -> BlockchainService:
    return get_service(BlockchainService)


def get_did_service() -> DIDService:
    return get_service(DIDService)


def get_agent_card_service() -> AgentCardService:
    return get_service(AgentCardService)
