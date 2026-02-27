"""Re-export from flat module for namespace compatibility."""
from services.blockchain_service import *
from services.blockchain_service import BlockchainService

__all__ = ["BlockchainService"]
