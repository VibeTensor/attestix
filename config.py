"""Configuration management for Attestix MCP server."""

import json
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from filelock import FileLock

PROJECT_DIR = Path(__file__).parent
ENV_FILE = PROJECT_DIR / ".env"
IDENTITIES_FILE = PROJECT_DIR / "identities.json"
REPUTATION_FILE = PROJECT_DIR / "reputation.json"
DELEGATIONS_FILE = PROJECT_DIR / "delegations.json"
COMPLIANCE_FILE = PROJECT_DIR / "compliance.json"
CREDENTIALS_FILE = PROJECT_DIR / "credentials.json"
PROVENANCE_FILE = PROJECT_DIR / "provenance.json"
LOG_FILE = PROJECT_DIR / "attestix_errors.log"
SIGNING_KEY_FILE = PROJECT_DIR / ".signing_key.json"

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


# --- Identity storage ---

def load_identities() -> dict:
    return _safe_load(IDENTITIES_FILE, {"agents": []})


def save_identities(data: dict):
    _safe_save(IDENTITIES_FILE, data)


# --- Reputation storage ---

def load_reputation() -> dict:
    return _safe_load(REPUTATION_FILE, {"interactions": [], "scores": {}})


def save_reputation(data: dict):
    _safe_save(REPUTATION_FILE, data)


# --- Delegation storage ---

def load_delegations() -> dict:
    return _safe_load(DELEGATIONS_FILE, {"delegations": []})


def save_delegations(data: dict):
    _safe_save(DELEGATIONS_FILE, data)


# --- Compliance storage ---

def load_compliance() -> dict:
    return _safe_load(COMPLIANCE_FILE, {"profiles": [], "assessments": [], "declarations": []})


def save_compliance(data: dict):
    _safe_save(COMPLIANCE_FILE, data)


# --- Credential storage ---

def load_credentials() -> dict:
    return _safe_load(CREDENTIALS_FILE, {"credentials": []})


def save_credentials(data: dict):
    _safe_save(CREDENTIALS_FILE, data)


# --- Provenance storage ---

def load_provenance() -> dict:
    return _safe_load(PROVENANCE_FILE, {"entries": [], "audit_log": []})


def save_provenance(data: dict):
    _safe_save(PROVENANCE_FILE, data)
