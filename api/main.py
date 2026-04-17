"""Attestix REST API - FastAPI application.

Production-ready API wrapper for the Attestix attestation infrastructure.
Provides RESTful endpoints for agent identity, verifiable credentials,
EU AI Act compliance, reputation, provenance, delegation, DIDs,
agent cards, and blockchain anchoring.
"""

import hmac
import ipaddress
import os
import time
import logging
from collections import OrderedDict
from contextlib import asynccontextmanager
from typing import Optional

try:
    from importlib.metadata import version as _pkg_version
    __version__ = _pkg_version("attestix")
except Exception:
    __version__ = "0.3.0"

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from api.routers import (
    identity,
    credentials,
    compliance,
    reputation,
    provenance,
    delegation,
    did,
    agent_cards,
    blockchain,
)

logger = logging.getLogger("attestix.api")


# ---------------------------------------------------------------------------
# Rate limiting (in-memory sliding window)
# ---------------------------------------------------------------------------

class RateLimitState:
    """Simple in-memory rate limiter using a sliding window counter.

    Tracks request timestamps per client IP within a configurable window
    and enforces a maximum number of requests per window. An LRU cap on the
    number of tracked IPs prevents an attacker from exhausting memory by
    cycling through a huge set of source IPs (for example via
    ``X-Forwarded-For`` spoofing when the app is deployed without a trusted
    proxy in front of it).
    """

    def __init__(
        self,
        max_requests: int = 60,
        window_seconds: int = 60,
        max_tracked_ips: int = 10000,
    ):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.max_tracked_ips = max_tracked_ips
        # OrderedDict + move_to_end gives O(1) LRU semantics.
        self._hits: "OrderedDict[str, list[float]]" = OrderedDict()

    def _touch(self, client_ip: str) -> list[float]:
        """Get or create the timestamp list for ``client_ip`` with LRU bookkeeping."""
        if client_ip in self._hits:
            self._hits.move_to_end(client_ip)
            return self._hits[client_ip]
        # Evict least-recently-seen buckets until we have room.
        while len(self._hits) >= self.max_tracked_ips:
            self._hits.popitem(last=False)
        self._hits[client_ip] = []
        return self._hits[client_ip]

    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        cutoff = now - self.window_seconds
        timestamps = self._touch(client_ip)
        # Prune expired timestamps.
        pruned = [t for t in timestamps if t > cutoff]
        self._hits[client_ip] = pruned
        if len(pruned) >= self.max_requests:
            return False
        pruned.append(now)
        return True

    def remaining(self, client_ip: str) -> int:
        now = time.time()
        cutoff = now - self.window_seconds
        timestamps = [t for t in self._hits.get(client_ip, []) if t > cutoff]
        return max(0, self.max_requests - len(timestamps))


_rate_limiter = RateLimitState(
    max_requests=int(os.environ.get("RATE_LIMIT_MAX", "60")),
    window_seconds=int(os.environ.get("RATE_LIMIT_WINDOW", "60")),
    max_tracked_ips=int(os.environ.get("RATE_LIMIT_MAX_TRACKED_IPS", "10000")),
)


# ---------------------------------------------------------------------------
# Client IP resolution
# ---------------------------------------------------------------------------
#
# ``request.client.host`` is the socket peer. Behind any reverse proxy or
# load balancer (ALB, Cloudflare, nginx, Fly.io, Railway, Render, etc.) that
# is the proxy's IP, so every client on Earth would share one rate-limit
# bucket. We therefore honour ``X-Forwarded-For`` / ``X-Real-IP`` only when
# the request actually originated from an operator-configured trusted proxy.

def _parse_trusted_proxies(raw: str) -> list:
    """Parse a comma-separated list of IPs / CIDR blocks into network objects."""
    networks = []
    for entry in raw.split(","):
        entry = entry.strip()
        if not entry:
            continue
        try:
            networks.append(ipaddress.ip_network(entry, strict=False))
        except ValueError:
            logger.warning("Ignoring invalid TRUSTED_PROXIES entry: %r", entry)
    return networks


_TRUSTED_PROXIES = _parse_trusted_proxies(os.environ.get("TRUSTED_PROXIES", ""))
_TRUSTED_PROXIES_WARNED = False


def _ip_in_trusted_networks(ip_str: str) -> bool:
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return False
    return any(ip in net for net in _TRUSTED_PROXIES)


def _extract_first_forwarded(value: str) -> Optional[str]:
    """Return the left-most non-empty entry from an ``X-Forwarded-For`` value."""
    for entry in value.split(","):
        candidate = entry.strip()
        if candidate:
            return candidate
    return None


def _resolve_client_ip(request: Request) -> str:
    """Resolve the true client IP for rate-limiting.

    Behaviour:
    - If ``TRUSTED_PROXIES`` is configured AND the request came in from one of
      those proxies, honour ``X-Real-IP`` or the left-most ``X-Forwarded-For``
      entry. This is the per-true-client IP we want to rate-limit on.
    - Otherwise fall back to ``request.client.host`` and emit a one-shot
      WARNING so operators notice the misconfiguration rather than silently
      buckshotting every request into a single bucket.
    """
    global _TRUSTED_PROXIES_WARNED

    peer = request.client.host if request.client else "unknown"

    if _TRUSTED_PROXIES and _ip_in_trusted_networks(peer):
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        fwd = request.headers.get("X-Forwarded-For")
        if fwd:
            first = _extract_first_forwarded(fwd)
            if first:
                return first
        return peer

    # No trusted proxy configured - or the peer is not one of them. If
    # forwarding headers are present anyway, warn once so operators know we
    # are NOT trusting them.
    if not _TRUSTED_PROXIES and (
        request.headers.get("X-Forwarded-For")
        or request.headers.get("X-Real-IP")
    ):
        if not _TRUSTED_PROXIES_WARNED:
            logger.warning(
                "Received X-Forwarded-For/X-Real-IP but TRUSTED_PROXIES is "
                "not configured. Falling back to socket peer for rate "
                "limiting. Set TRUSTED_PROXIES to the CIDR of your LB/CDN "
                "so per-client rate limits work correctly."
            )
            _TRUSTED_PROXIES_WARNED = True

    return peer


# ---------------------------------------------------------------------------
# API key authentication middleware
# ---------------------------------------------------------------------------

class APIKeyMiddleware(BaseHTTPMiddleware):
    """Validate X-API-Key header against ATTESTIX_API_KEY env var.

    If ATTESTIX_API_KEY is not set, all requests are allowed (dev mode).
    Health check, docs, and OpenAPI schema endpoints are always open.
    Also accepts Authorization: Bearer <key> as a fallback.
    """

    OPEN_PATHS = {"/", "/health", "/docs", "/redoc", "/openapi.json"}

    async def dispatch(self, request: Request, call_next):
        api_key = os.environ.get("ATTESTIX_API_KEY")

        # Dev mode - no key configured, allow everything
        if not api_key:
            return await call_next(request)

        # Allow open paths without auth
        if request.url.path in self.OPEN_PATHS:
            return await call_next(request)

        # Check X-API-Key header first (preferred)
        provided_key = request.headers.get("X-API-Key", "")

        # Fallback: check Authorization: Bearer <key>
        if not provided_key:
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                provided_key = auth_header[len("Bearer "):]

        if not provided_key:
            return JSONResponse(
                status_code=401,
                content={"error": "Missing API key. Provide X-API-Key header or Authorization: Bearer <key>"},
            )

        # Constant-time comparison to prevent byte-by-byte timing attacks
        # that could reveal the configured API key.
        if not hmac.compare_digest(provided_key, api_key):
            return JSONResponse(
                status_code=403,
                content={"error": "Invalid API key"},
            )

        return await call_next(request)


# ---------------------------------------------------------------------------
# Rate limiting middleware
# ---------------------------------------------------------------------------

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Enforce per-IP rate limits using a sliding window counter."""

    OPEN_PATHS = {"/health"}

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in self.OPEN_PATHS:
            return await call_next(request)

        client_ip = _resolve_client_ip(request)
        if not _rate_limiter.is_allowed(client_ip):
            remaining = _rate_limiter.remaining(client_ip)
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded. Try again later."},
                headers={
                    "X-RateLimit-Limit": str(_rate_limiter.max_requests),
                    "X-RateLimit-Remaining": str(remaining),
                    "Retry-After": str(_rate_limiter.window_seconds),
                },
            )

        response = await call_next(request)
        remaining = _rate_limiter.remaining(client_ip)
        response.headers["X-RateLimit-Limit"] = str(_rate_limiter.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response


# ---------------------------------------------------------------------------
# Application lifecycle
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Attestix API starting up")
    yield
    logger.info("Attestix API shutting down")


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Attestix API",
    description=(
        "Attestation infrastructure for AI agents. "
        "Identity, verifiable credentials, EU AI Act compliance, "
        "reputation, provenance, delegation, DIDs, agent cards, "
        "and blockchain anchoring."
    ),
    version=__version__,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS - allow all origins in dev, restrict via env in production
allowed_origins = os.environ.get("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting (applied before auth so abusers get 429 before 401)
app.add_middleware(RateLimitMiddleware)

# API key auth
app.add_middleware(APIKeyMiddleware)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/health", tags=["system"])
def health_check():
    """Health check endpoint for load balancers and uptime monitors."""
    return {
        "status": "healthy",
        "service": "attestix-api",
        "version": __version__,
    }


# ---------------------------------------------------------------------------
# Global exception handler
# ---------------------------------------------------------------------------

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Unhandled exception on %s %s: %s",
        request.method, request.url.path, exc, exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"},
    )


# ---------------------------------------------------------------------------
# Mount routers
# ---------------------------------------------------------------------------

app.include_router(identity.router)
app.include_router(credentials.router)
app.include_router(compliance.router)
app.include_router(reputation.router)
app.include_router(provenance.router)
app.include_router(delegation.router)
app.include_router(did.router)
app.include_router(agent_cards.router)
app.include_router(blockchain.router)


if __name__ == "__main__":
    import uvicorn
    host = os.environ.get("ATTESTIX_API_HOST", "127.0.0.1")
    port = int(os.environ.get("ATTESTIX_API_PORT", "8000"))
    uvicorn.run("api.main:app", host=host, port=port, reload=False)
