"""Configuration management for AURA Protocol MCP server."""

import json
import os
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).parent
ENV_FILE = PROJECT_DIR / ".env"
IDENTITIES_FILE = PROJECT_DIR / "identities.json"
REPUTATION_FILE = PROJECT_DIR / "reputation.json"
DELEGATIONS_FILE = PROJECT_DIR / "delegations.json"
COMPLIANCE_FILE = PROJECT_DIR / "compliance.json"
CREDENTIALS_FILE = PROJECT_DIR / "credentials.json"
PROVENANCE_FILE = PROJECT_DIR / "provenance.json"
LOG_FILE = PROJECT_DIR / "aura_errors.log"
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


# --- Identity storage ---

def load_identities() -> dict:
    if not IDENTITIES_FILE.exists():
        return {"agents": []}
    with open(IDENTITIES_FILE, "r") as f:
        return json.load(f)


def save_identities(data: dict):
    with open(IDENTITIES_FILE, "w") as f:
        json.dump(data, f, indent=2)


# --- Reputation storage ---

def load_reputation() -> dict:
    if not REPUTATION_FILE.exists():
        return {"interactions": [], "scores": {}}
    with open(REPUTATION_FILE, "r") as f:
        return json.load(f)


def save_reputation(data: dict):
    with open(REPUTATION_FILE, "w") as f:
        json.dump(data, f, indent=2)


# --- Delegation storage ---

def load_delegations() -> dict:
    if not DELEGATIONS_FILE.exists():
        return {"delegations": []}
    with open(DELEGATIONS_FILE, "r") as f:
        return json.load(f)


def save_delegations(data: dict):
    with open(DELEGATIONS_FILE, "w") as f:
        json.dump(data, f, indent=2)


# --- Compliance storage ---

def load_compliance() -> dict:
    if not COMPLIANCE_FILE.exists():
        return {"profiles": [], "assessments": [], "declarations": []}
    with open(COMPLIANCE_FILE, "r") as f:
        return json.load(f)


def save_compliance(data: dict):
    with open(COMPLIANCE_FILE, "w") as f:
        json.dump(data, f, indent=2)


# --- Credential storage ---

def load_credentials() -> dict:
    if not CREDENTIALS_FILE.exists():
        return {"credentials": []}
    with open(CREDENTIALS_FILE, "r") as f:
        return json.load(f)


def save_credentials(data: dict):
    with open(CREDENTIALS_FILE, "w") as f:
        json.dump(data, f, indent=2)


# --- Provenance storage ---

def load_provenance() -> dict:
    if not PROVENANCE_FILE.exists():
        return {"entries": [], "audit_log": []}
    with open(PROVENANCE_FILE, "r") as f:
        return json.load(f)


def save_provenance(data: dict):
    with open(PROVENANCE_FILE, "w") as f:
        json.dump(data, f, indent=2)
