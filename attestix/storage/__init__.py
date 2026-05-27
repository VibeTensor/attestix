"""Attestix storage - re-exports from the flat module for namespace compatibility.

    # Namespaced (recommended)
    from attestix.storage import Repository, FileRepository, select_repository

    # Flat (also supported)
    from storage import Repository, FileRepository, select_repository
"""

from storage import (
    DEFAULT_TENANT,
    FileRepository,
    MemoryRepository,
    Repository,
    default_repository,
    select_repository,
)

# Re-export submodules for `from attestix.storage.X import Y` parity.
from storage import repository
from storage import file_repository
from storage import memory_repository

__all__ = [
    "Repository",
    "FileRepository",
    "MemoryRepository",
    "DEFAULT_TENANT",
    "select_repository",
    "default_repository",
    "repository",
    "file_repository",
    "memory_repository",
]
