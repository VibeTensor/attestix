"""Re-export from flat module for namespace compatibility."""
from services.provenance_service import *
from services.provenance_service import ProvenanceService

__all__ = ["ProvenanceService"]
