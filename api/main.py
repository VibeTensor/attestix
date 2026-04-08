"""Attestix REST API - FastAPI application.

Production-ready API wrapper for the Attestix attestation infrastructure.
Provides RESTful endpoints for agent identity, verifiable credentials,
EU AI Act compliance, reputation, provenance, delegation, DIDs,
agent cards, and blockchain anchoring.
"""

import os
import time
import logging
from collections import defaultdict
from contextlib import asynccontextmanager

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
    and enforces a maximum number of requests per window.
    """

    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        cutoff = now - self.window_seconds
        # Prune expired timestamps
        timestamps = self._hits[client_ip]
        self._hits[client_ip] = [t for t in timestamps if t > cutoff]
        if len(self._hits[client_ip]) >= self.max_requests:
            return False
        self._hits[client_ip].append(now)
        return True

    def remaining(self, client_ip: str) -> int:
        now = time.time()
        cutoff = now - self.window_seconds
        timestamps = [t for t in self._hits.get(client_ip, []) if t > cutoff]
        return max(0, self.max_requests - len(timestamps))


_rate_limiter = RateLimitState(
    max_requests=int(os.environ.get("RATE_LIMIT_MAX", "60")),
    window_seconds=int(os.environ.get("RATE_LIMIT_WINDOW", "60")),
)


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

        if provided_key != api_key:
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

        client_ip = request.client.host if request.client else "unknown"
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
    version="0.2.4",
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
        "version": "0.2.4",
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
