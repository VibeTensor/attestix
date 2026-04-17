"""SSRF protection utilities for Attestix.

Validates hostnames and resolved IPs against private/reserved ranges
before making outbound HTTP requests. Returns pinned IPs to prevent
DNS rebinding (TOCTOU) attacks.
"""

import ipaddress
import json as _json
import socket
from typing import Optional, Tuple, List
from urllib.parse import urlparse, urlunparse

import httpx


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


class ResponseTooLargeError(Exception):
    """Raised when an outbound response exceeds the configured size cap."""


def fetch_json_pinned(
    url: str,
    *,
    max_bytes: int,
    timeout: float = 10.0,
) -> Tuple[Optional[str], Optional[dict]]:
    """Fetch a JSON document with DNS pinning and a hard response-size cap.

    This helper closes three related SSRF / DoS holes at the same time:

    1. DNS rebinding (TOCTOU). The hostname is resolved exactly once via
       :func:`validate_and_pin_url` and the HTTP request is then issued to the
       pinned IP with ``Host`` set to the original hostname. The second DNS
       lookup that ``httpx`` would normally perform when it opens the socket
       is therefore bypassed, so an attacker with a short-TTL authoritative
       DNS server cannot flip the address to 169.254.169.254 between
       validation and connection.
    2. Open redirects to internal IPs. Redirects are disabled
       (``follow_redirects=False``) so a public target cannot bounce us to an
       internal address.
    3. Gzip bombs / unbounded responses. The response is streamed and the
       cumulative decoded byte count is capped at ``max_bytes``. Any
       ``Content-Length`` header that already exceeds the cap causes an
       immediate rejection before a single body byte is read.

    Args:
        url: The full URL to fetch. Must be https.
        max_bytes: Maximum allowed decoded response size, in bytes.
        timeout: Per-request timeout in seconds.

    Returns:
        A tuple ``(error, payload)``. Exactly one of the two is not ``None``.
    """
    parsed = urlparse(url)
    if parsed.scheme != "https":
        return ("Only HTTPS URLs are supported", None)

    hostname = parsed.hostname
    if not hostname:
        return ("No hostname in URL", None)

    err, pinned_ips = validate_and_pin_url(url)
    if err:
        return (err, None)
    if not pinned_ips:
        return (f"Could not resolve '{hostname}' to any IP", None)

    # Build a new URL that targets the pinned IP directly. Keep the Host
    # header set to the original hostname so TLS SNI and HTTP routing work
    # correctly at the remote end.
    pinned_ip = pinned_ips[0]

    # IPv6 literal needs brackets in the URL authority.
    if ":" in pinned_ip and not pinned_ip.startswith("["):
        host_for_url = f"[{pinned_ip}]"
    else:
        host_for_url = pinned_ip

    # Preserve the original explicit port if the caller supplied one.
    if parsed.port is not None:
        netloc = f"{host_for_url}:{parsed.port}"
    else:
        netloc = host_for_url

    pinned_url = urlunparse(parsed._replace(netloc=netloc))

    headers = {"Host": hostname}

    try:
        with httpx.Client(timeout=timeout, follow_redirects=False) as client:
            with client.stream("GET", pinned_url, headers=headers) as resp:
                if resp.is_redirect:
                    return (
                        "Redirect responses are not followed to prevent SSRF",
                        None,
                    )
                if resp.status_code >= 400:
                    return (f"HTTP {resp.status_code} fetching {url}", None)

                # Fail fast on oversize Content-Length before reading body.
                cl = resp.headers.get("content-length")
                if cl is not None:
                    try:
                        if int(cl) > max_bytes:
                            return (
                                f"Response too large: Content-Length {cl} "
                                f"exceeds cap of {max_bytes} bytes",
                                None,
                            )
                    except ValueError:
                        pass  # Malformed header, fall through to streaming cap.

                buf = bytearray()
                for chunk in resp.iter_bytes(chunk_size=8192):
                    buf.extend(chunk)
                    if len(buf) > max_bytes:
                        return (
                            f"Response too large: exceeded cap of "
                            f"{max_bytes} bytes",
                            None,
                        )
    except httpx.TimeoutException:
        return (f"Timeout fetching {url}", None)
    except httpx.HTTPError as e:
        return (f"Network error fetching {url}: {e}", None)

    try:
        payload = _json.loads(bytes(buf).decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as e:
        return (f"Invalid JSON response from {url}: {e}", None)

    if not isinstance(payload, dict):
        return (
            f"Expected JSON object from {url}, got {type(payload).__name__}",
            None,
        )

    return (None, payload)


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
