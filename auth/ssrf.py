"""SSRF protection utilities for Attestix.

Validates hostnames and resolved IPs against private/reserved ranges
before making outbound HTTP requests. Returns pinned IPs to prevent
DNS rebinding (TOCTOU) attacks.
"""

import ipaddress
import socket
from typing import Optional, Tuple, List
from urllib.parse import urlparse


# Domains that are always blocked (case-insensitive)
_BLOCKED_DOMAINS = {
    "localhost",
    "localhost.localdomain",
    "metadata.google.internal",
    "metadata.google.com",
    "169.254.169.254",
}

# Domain suffixes that are always blocked
_BLOCKED_SUFFIXES = (
    ".local",
    ".internal",
    ".localhost",
)

# Maximum redirects to follow (0 = no redirects)
MAX_REDIRECTS = 0


def _is_private_ip(ip_str: str) -> bool:
    """Check whether an IP address is private, loopback, link-local, or reserved."""
    try:
        ip = ipaddress.ip_address(ip_str)
        return ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved
    except ValueError:
        return False


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

    # Resolve hostname and check ALL resolved IPs
    try:
        resolved = socket.getaddrinfo(clean, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
        for family, _, _, _, addr in resolved:
            ip_str = addr[0]
            if _is_private_ip(ip_str):
                return f"Blocked: '{hostname}' resolves to private IP {ip_str}"
    except socket.gaierror:
        pass  # DNS resolution failed - let the HTTP client handle it

    return None


def validate_and_pin_url(url: str) -> Tuple[Optional[str], List[str]]:
    """Validate a URL and return pinned resolved IPs.

    This prevents DNS rebinding attacks by resolving DNS once during validation
    and returning the IPs so the caller can connect directly to them.

    Returns:
        (error_or_none, pinned_ips): error string if blocked, else None with safe IPs.
    """
    try:
        parsed = urlparse(url)
    except Exception:
        return ("Invalid URL", [])

    hostname = parsed.hostname
    if not hostname:
        return ("No hostname in URL", [])

    clean = hostname.lower().strip("[]")

    # Block known private hostnames
    if clean in _BLOCKED_DOMAINS:
        return (f"Blocked: private hostname '{hostname}'", [])

    for suffix in _BLOCKED_SUFFIXES:
        if clean.endswith(suffix):
            return (f"Blocked: private domain suffix '{hostname}'", [])

    # Try to parse as an IP address directly
    try:
        ip = ipaddress.ip_address(clean)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            return (f"Blocked: private/reserved IP address '{hostname}'", [])
        return (None, [str(ip)])
    except ValueError:
        pass  # Not a raw IP, resolve via DNS

    # Resolve hostname and pin all safe IPs
    safe_ips = []
    try:
        resolved = socket.getaddrinfo(clean, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
        for family, _, _, _, addr in resolved:
            ip_str = addr[0]
            if _is_private_ip(ip_str):
                return (f"Blocked: '{hostname}' resolves to private IP {ip_str}", [])
            if ip_str not in safe_ips:
                safe_ips.append(ip_str)
    except socket.gaierror:
        pass  # DNS resolution failed - let the HTTP client handle it

    return (None, safe_ips)


def validate_redirect_target(redirect_url: str, original_hostname: str) -> Optional[str]:
    """Validate a redirect target URL.

    Blocks redirects to private IPs or different hosts (open redirect to internal).

    Returns None if safe, or an error string if blocked.
    """
    try:
        parsed = urlparse(redirect_url)
    except Exception:
        return "Invalid redirect URL"

    redirect_host = parsed.hostname
    if not redirect_host:
        return "No hostname in redirect URL"

    # Validate the redirect target the same way as the original
    error = validate_url_host(redirect_host)
    if error:
        return f"Redirect blocked: {error}"

    return None
