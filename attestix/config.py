"""Configuration management for Attestix MCP server."""

import json
import os
import shutil
import sys
import time
import tempfile
from contextlib import contextmanager
from functools import wraps
from threading import RLock, local
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from filelock import FileLock

PROJECT_DIR = Path(__file__).parent

# Data directory: use ATTESTIX_DATA_DIR env var, or ~/.attestix/ by default.
# This ensures fresh installs start with empty data (no demo artifacts)
# and avoids writing into the package install location (site-packages).
_data_dir_env = os.environ.get("ATTESTIX_DATA_DIR")
if _data_dir_env:
    DATA_DIR = Path(_data_dir_env)
else:
    DATA_DIR = Path.home() / ".attestix"
DATA_DIR.mkdir(parents=True, exist_ok=True)

ENV_FILE = PROJECT_DIR / ".env"
IDENTITIES_FILE = DATA_DIR / "identities.json"
REPUTATION_FILE = DATA_DIR / "reputation.json"
DELEGATIONS_FILE = DATA_DIR / "delegations.json"
COMPLIANCE_FILE = DATA_DIR / "compliance.json"
CREDENTIALS_FILE = DATA_DIR / "credentials.json"
PROVENANCE_FILE = DATA_DIR / "provenance.json"
ANCHORS_FILE = DATA_DIR / "anchors.json"
# v0.4.0 extensibility layer (US2 structured audit events, US3 idempotency keys).
# Both are file-backed by default through the same FileRepository as every other
# collection, so the self-host default needs no new services.
AUDIT_FILE = DATA_DIR / "audit.json"
IDEMPOTENCY_FILE = DATA_DIR / "idempotency.json"
BLOCKCHAIN_CONFIG_FILE = DATA_DIR / ".blockchain_config.json"
LOG_FILE = DATA_DIR / "attestix_errors.log"
SIGNING_KEY_FILE = DATA_DIR / ".signing_key.json"

load_dotenv(ENV_FILE)


def _get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    return os.getenv(key, default)


# Universal Resolver endpoint (for DID resolution)
UNIVERSAL_RESOLVER_URL = _get_env(
    "UNIVERSAL_RESOLVER_URL",
    default="https://dev.uniresolver.io/1.0/identifiers/",
)

# UAIT defaults
UAIT_VERSION = "0.1.0"
DEFAULT_EXPIRY_DAYS = int(_get_env("DEFAULT_EXPIRY_DAYS", default="365"))


# --- Safe JSON storage helpers ---


_STORAGE_THREAD_LOCK = RLock()
_STORAGE_STATE = local()


@contextmanager
def storage_transaction():
    """Serialize local storage operations across threads and processes.

    This synchronous context must never span an asynchronous await.
    It provides isolation, not rollback of writes to multiple collections.
    """
    lock_path = str(DATA_DIR.resolve() / ".storage.lock")
    with _STORAGE_THREAD_LOCK:
        held = getattr(_STORAGE_STATE, "held", {})
        depth = held.get(lock_path, 0)
        held[lock_path] = depth + 1
        _STORAGE_STATE.held = held
        try:
            if depth:
                yield
            else:
                DATA_DIR.mkdir(parents=True, exist_ok=True)
                with FileLock(lock_path, timeout=30):
                    yield
        finally:
            if depth:
                held[lock_path] = depth
            else:
                held.pop(lock_path, None)


def storage_transactional(method):
    """Keep a synchronous read-modify-write operation under one storage lock."""
    @wraps(method)
    def wrapped(*args, **kwargs):
        with storage_transaction():
            return method(*args, **kwargs)
    return wrapped


def _atomic_write_json(filepath: Path, data: dict):
    """Write without retaining a pre-erasure recovery copy."""
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=filepath.parent,
            prefix=filepath.name + ".", suffix=".tmp", delete=False,
        ) as stream:
            temp_path = Path(stream.name)
            json.dump(data, stream, indent=2, ensure_ascii=False, allow_nan=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_path, filepath)
        temp_path = None
        # Persist the rename so an erased document cannot reappear after power loss.
        if hasattr(os, "O_DIRECTORY"):
            dir_fd = os.open(filepath.parent, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()


@storage_transactional
def _safe_load(filepath: Path, default: dict) -> dict:
    """Load JSON with file locking and corruption recovery."""
    lock = FileLock(str(filepath) + ".lock", timeout=5)
    with lock:
        if not filepath.exists():
            return default.copy()
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError) as e:
            # Try backup
            backup = filepath.with_suffix(".json.bak")
            if backup.exists():
                try:
                    with open(backup, "r") as f:
                        print(f"WARNING: Recovered {filepath.name} from backup",
                              file=sys.stderr)
                        return json.load(f)
                except (json.JSONDecodeError, ValueError):
                    pass
            # Move corrupted file aside, start fresh
            corrupted = filepath.with_suffix(f".corrupted.{int(time.time())}")
            shutil.move(str(filepath), str(corrupted))
            print(f"ERROR: Corrupted {filepath.name} moved to {corrupted.name}. "
                  f"Starting fresh.", file=sys.stderr)
            return default.copy()


@storage_transactional
def _safe_save(filepath: Path, data: dict):
    """Save JSON with file locking and atomic write."""
    lock = FileLock(str(filepath) + ".lock", timeout=5)
    with lock:
        # Backup existing file
        if filepath.exists():
            backup = filepath.with_suffix(".json.bak")
            shutil.copy2(str(filepath), str(backup))
        # Write to temp file, then atomic rename
        temp = filepath.with_suffix(".json.tmp")
        with open(temp, "w") as f:
            json.dump(data, f, indent=2)
        temp.replace(filepath)


# --- Default file Repository backing for the public load_*/save_* shims ---
#
# v0.4.0 introduces a pluggable storage seam (storage.Repository). The public
# load_*/save_* functions below are retained as thin shims over the default
# file-backed Repository so external callers that import them keep working
# unchanged (backward compatibility, constitution principle II). The Repository
# is resolved lazily to avoid an import cycle (storage.file_repository imports
# this module) and so test monkeypatching of the *_FILE paths is still honored
# (FileRepository reads those paths from this module on each call).

_file_repository = None


def _repo():
    """Return the process-wide default file Repository (lazy, cycle-safe)."""
    global _file_repository
    if _file_repository is None:
        from attestix.storage.file_repository import FileRepository
        _file_repository = FileRepository()
    return _file_repository


# --- Identity storage ---

def load_identities() -> dict:
    return _repo().load_document("identities")


def save_identities(data: dict):
    _repo().save_document("identities", data)


# --- Reputation storage ---

def load_reputation() -> dict:
    return _repo().load_document("reputation")


def save_reputation(data: dict):
    _repo().save_document("reputation", data)


# --- Delegation storage ---

def load_delegations() -> dict:
    return _repo().load_document("delegations")


def save_delegations(data: dict):
    _repo().save_document("delegations", data)


# --- Compliance storage ---

def load_compliance() -> dict:
    return _repo().load_document("compliance")


def save_compliance(data: dict):
    _repo().save_document("compliance", data)


# --- Credential storage ---

def load_credentials() -> dict:
    return _repo().load_document("credentials")


def save_credentials(data: dict):
    _repo().save_document("credentials", data)


def append_credential(credential: dict) -> dict:
    """Append one credential to the store without a full load+rewrite.

    Performance shim for the issuance hot path (issue #108): a pure append avoids
    the O(N) deep copy that ``load_credentials() -> append -> save_credentials()``
    incurs on every call. The on-disk ``{"credentials": [...]}`` shape is
    unchanged (the record is written verbatim, no tenant tagging).
    """
    return _repo().append_to_document("credentials", credential)


# --- Provenance storage ---

def load_provenance() -> dict:
    return _repo().load_document("provenance")


def save_provenance(data: dict):
    _repo().save_document("provenance", data)


# --- Anchor storage ---

def load_anchors() -> dict:
    return _repo().load_document("anchors")


def save_anchors(data: dict):
    _repo().save_document("anchors", data)
