"""SSRF protection utilities for Attestix.

Validates hostnames and resolved IPs against private/reserved ranges
before making outbound HTTP requests.
"""

import ipaddress
import re
import socket
from typing import Optional


# Domains that are always blocked (case-insensitive)
_BLOCKED_DOMAINS = {
    "localhost",
    "localhost.localdomain",
    "metadata.google.internal",
}

# Domain suffixes that are always blocked
_BLOCKED_SUFFIXES = (
    ".local",
    ".internal",
    ".localhost",
)


def validate_url_host(hostname: str) -> Optional[str]:
    """Validate a hostname is safe for outbound requests.

    Returns None if safe, or an error string if blocked.
    """
    if not hostname:
        return "Empty hostname"

    clean = hostname.lower().strip("[]")

    # Block known private hostnames
    if clean in _BLOCKED_DOMAINS:
        return f"Blocked: private hostname '{hostname}'"

    for suffix in _BLOCKED_SUFFIXES:
        if clean.endswith(suffix):
            return f"Blocked: private domain suffix '{hostname}'"

    # Try to parse as an IP address directly
    try:
        ip = ipaddress.ip_address(clean)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            return f"Blocked: private/reserved IP address '{hostname}'"
    except ValueError:
        pass  # Not a raw IP, continue to DNS resolution

    # Resolve hostname and check resolved IP
    try:
        resolved = socket.getaddrinfo(clean, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
        for family, _, _, _, addr in resolved:
            ip_str = addr[0]
            try:
                ip = ipaddress.ip_address(ip_str)
                if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                    return f"Blocked: '{hostname}' resolves to private IP {ip_str}"
            except ValueError:
                continue
    except socket.gaierror:
        pass  # DNS resolution failed -- let the HTTP client handle it

    return None
