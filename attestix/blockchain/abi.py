"""Re-export from flat module for namespace compatibility."""
from blockchain.abi import (
    ATTESTIX_SCHEMA,
    EAS_ABI,
    EAS_CONTRACT_ADDRESS,
    SCHEMA_REGISTRY_ABI,
    SCHEMA_REGISTRY_ADDRESS,
)

__all__ = [
    "ATTESTIX_SCHEMA",
    "EAS_ABI",
    "EAS_CONTRACT_ADDRESS",
    "SCHEMA_REGISTRY_ABI",
    "SCHEMA_REGISTRY_ADDRESS",
]
