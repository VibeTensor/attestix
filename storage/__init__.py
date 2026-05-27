"""Pluggable persistence for Attestix (v0.4.0 extensibility layer).

This package introduces the :class:`Repository` seam so the service layer can
read/write through an abstraction instead of calling ``config.load_*`` /
``config.save_*`` directly. The default install resolves to the file-backed
:class:`FileRepository`, which reproduces v0.3.0 on-disk behavior exactly.

Selecting a non-default backend is opt-in via the ``ATTESTIX_STORAGE`` environment
variable (or the ``config`` argument to :func:`select_repository`); the optional
Postgres adapter lives behind the ``[pg]`` extra and is imported lazily so a
default ``pip install`` pulls no extra runtime dependency (FR-005, FR-026,
SC-010).
"""

import os
from typing import Optional

from storage.repository import DEFAULT_TENANT, Repository
from storage.file_repository import FileRepository
from storage.memory_repository import MemoryRepository

__all__ = [
    "Repository",
    "FileRepository",
    "MemoryRepository",
    "DEFAULT_TENANT",
    "select_repository",
    "default_repository",
]

# Process-wide default instance. The FileRepository is stateless (it resolves
# config paths lazily on each call) so a single shared instance is safe and keeps
# the default path allocation-free.
_DEFAULT = FileRepository()


def default_repository() -> Repository:
    """Return the shared default (file-backed) Repository."""
    return _DEFAULT


def select_repository(config: Optional[dict] = None) -> Repository:
    """Return the configured Repository, defaulting to :class:`FileRepository`.

    Selection precedence:

    1. ``config["storage"]`` if a ``config`` mapping is supplied.
    2. The ``ATTESTIX_STORAGE`` environment variable.
    3. Default: ``"file"`` -> :class:`FileRepository` (v0.3.0 behavior).

    Recognized values:

    - ``"file"`` (default) -> :class:`FileRepository`.
    - ``"memory"`` -> :class:`MemoryRepository` (volatile; tests / smoke).
    - ``"postgres"`` / ``"pg"`` -> the optional Postgres adapter (``[pg]`` extra),
      imported lazily; a clear, actionable error is raised if the extra is not
      installed.
    """
    choice = None
    if config:
        choice = config.get("storage")
    if choice is None:
        choice = os.environ.get("ATTESTIX_STORAGE")
    if choice is None:
        choice = "file"
    choice = str(choice).strip().lower()

    if choice == "file":
        return default_repository()
    if choice == "memory":
        return MemoryRepository()
    if choice in ("postgres", "pg"):
        try:
            from storage.pg_repository import PgRepository  # noqa: F401
        except ImportError as exc:  # pragma: no cover - exercised only with extra
            raise ImportError(
                "ATTESTIX_STORAGE=postgres requires the optional 'pg' extra. "
                "Install it with: pip install 'attestix[pg]'"
            ) from exc
        return PgRepository(config or {})

    raise ValueError(
        f"Unknown ATTESTIX_STORAGE value {choice!r}. "
        "Expected one of: file, memory, postgres."
    )
