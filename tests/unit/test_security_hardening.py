"""Regression tests for the security hardening batch.

Covers:
    - Fix 1: SSRF redirect bypass (agent_card_service)
    - Fix 2: API key constant-time comparison (api/main.py)
    - Fix 3: Exception info leakage (log full, return generic)
    - Fix 4: display_name validation (empty / whitespace / overlong)
    - Fix 5: Signing key POSIX 0600 permissions
    - Fix 6: JWT error leak in delegation verification
"""

import hmac
import sys
from pathlib import Path

import httpx
import pytest

from auth.crypto import load_or_create_signing_key


# ---------------------------------------------------------------------------
# Fix 1 - SSRF redirect bypass
# ---------------------------------------------------------------------------


class TestAgentCardRedirectProtection:
    """The discover_agent client must not follow redirects, else a public
    server could redirect us to 169.254.169.254 or another internal IP
    bypassing the initial SSRF host validation."""

    def test_client_has_follow_redirects_disabled(self, monkeypatch):
        """Ensure the httpx.Client used in discover_agent sets
        follow_redirects=False."""
        from services.agent_card_service import AgentCardService

        captured = {}

        def fake_client(*args, **kwargs):
            captured["follow_redirects"] = kwargs.get("follow_redirects")
            # Fail before making any real network call.
            raise httpx.TimeoutException("short-circuit for test")

        monkeypatch.setattr(httpx, "Client", fake_client)

        svc = AgentCardService()
        result = svc.discover_agent("https://example.com")

        assert captured.get("follow_redirects") is False
        assert "error" in result

    def test_redirect_response_is_refused(self, monkeypatch):
        """A 30x response must short-circuit to an error, not be silently
        followed. After switching to fetch_json_pinned, the redirect refusal
        is enforced by the pinned fetcher, so we stub that layer instead."""
        from services.agent_card_service import AgentCardService
        import auth.ssrf as ssrf_mod
        import services.agent_card_service as acs_mod

        def fake_fetch_json_pinned(url, max_bytes=None, timeout=10.0, headers=None):
            return "refused: redirect to 169.254.169.254 blocked", None

        monkeypatch.setattr(acs_mod, "fetch_json_pinned", fake_fetch_json_pinned)

        svc = AgentCardService()
        result = svc.discover_agent("https://example.com")
        assert "error" in result
        assert "redirect" in result["error"].lower()


# ---------------------------------------------------------------------------
# Fix 2 - API key constant-time comparison
# ---------------------------------------------------------------------------


class TestAPIKeyMiddleware:
    """APIKeyMiddleware must use hmac.compare_digest to avoid byte-by-byte
    timing attacks that reveal the configured key."""

    def test_module_imports_hmac(self):
        """Static check that api/main.py imports hmac."""
        src = Path("api/main.py").read_text(encoding="utf-8")
        assert "import hmac" in src
        # Sanity: the compare_digest symbol is what we rely on.
        assert hmac.compare_digest("abc", "abc") is True
        assert hmac.compare_digest("abc", "abd") is False

    def test_source_uses_compare_digest(self):
        """Static check: the middleware must not use plain == on the keys."""
        src = Path("api/main.py").read_text(encoding="utf-8")
        assert "hmac.compare_digest(provided_key, api_key)" in src
        assert "provided_key != api_key" not in src


# ---------------------------------------------------------------------------
# Fix 3 - Exception info leakage
# ---------------------------------------------------------------------------


class TestRoutersDoNotLeakInternalErrors:
    """The error-handling routers must not pass raw service error strings
    straight back to the HTTP caller. A greppable check keeps this honest."""

    ROUTER_FILES = [
        "api/routers/agent_cards.py",
        "api/routers/blockchain.py",
        "api/routers/compliance.py",
        "api/routers/credentials.py",
        "api/routers/identity.py",
        "api/routers/provenance.py",
        "api/routers/reputation.py",
    ]

    def test_no_raw_error_detail_in_routers(self):
        offenders = []
        for path in self.ROUTER_FILES:
            src = Path(path).read_text(encoding="utf-8")
            if 'detail=result["error"]' in src:
                offenders.append(path)
            if 'detail=results[0]["error"]' in src:
                offenders.append(path)
        assert not offenders, (
            "Routers still leak raw service errors to HTTP callers: "
            f"{offenders}"
        )

    def test_routers_log_before_responding(self):
        """Every sanitized router must keep the original error in the logs."""
        for path in self.ROUTER_FILES:
            src = Path(path).read_text(encoding="utf-8")
            assert "logger" in src, f"{path} should log errors server-side"


# ---------------------------------------------------------------------------
# Fix 4 - display_name validation
# ---------------------------------------------------------------------------


class TestDisplayNameValidation:
    """IdentityService.create_identity must reject empty/whitespace-only
    and overlong display_name values (Issue #32)."""

    def test_rejects_empty_string(self, identity_service):
        with pytest.raises(ValueError):
            identity_service.create_identity(
                display_name="",
                source_protocol="mcp",
            )

    def test_rejects_whitespace_only(self, identity_service):
        with pytest.raises(ValueError):
            identity_service.create_identity(
                display_name="   \t  ",
                source_protocol="mcp",
            )

    def test_rejects_overlong(self, identity_service):
        with pytest.raises(ValueError):
            identity_service.create_identity(
                display_name="x" * 501,
                source_protocol="mcp",
            )

    def test_strips_surrounding_whitespace(self, identity_service):
        result = identity_service.create_identity(
            display_name="  Alice  ",
            source_protocol="mcp",
        )
        assert result["display_name"] == "Alice"

    def test_rejects_control_characters(self, identity_service):
        with pytest.raises(ValueError):
            identity_service.create_identity(
                display_name="bad\x00name",
                source_protocol="mcp",
            )

    def test_accepts_max_length(self, identity_service):
        name = "a" * 500
        result = identity_service.create_identity(
            display_name=name,
            source_protocol="mcp",
        )
        assert result["display_name"] == name


# ---------------------------------------------------------------------------
# Fix 5 - Signing key file permissions
# ---------------------------------------------------------------------------


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX chmod only")
class TestSigningKeyPermissions:
    def test_newly_generated_key_is_0600(self, tmp_path):
        key_file = tmp_path / "signing_key.json"
        load_or_create_signing_key(key_file=key_file)
        assert key_file.exists()
        mode = key_file.stat().st_mode
        perm = mode & 0o777
        assert perm == 0o600, f"expected 0600, got {oct(perm)}"


class TestSigningKeyPermissionsWindowsSafe:
    def test_chmod_is_skipped_on_windows(self):
        """The code path must not crash on Windows even though chmod is a
        no-op for POSIX mode bits there."""
        src = Path("auth/crypto.py").read_text(encoding="utf-8")
        assert 'sys.platform != "win32"' in src
        assert "os.chmod(key_path" in src


# ---------------------------------------------------------------------------
# Fix 6 - JWT error leak in delegation verification
# ---------------------------------------------------------------------------


class TestDelegationInvalidTokenIsGeneric:
    """verify_delegation must return a generic 'Invalid token' reason
    rather than echoing PyJWT's internal error message."""

    def test_malformed_token_returns_generic_reason(self, delegation_service):
        result = delegation_service.verify_delegation("not-a-real-jwt")
        assert result["valid"] is False
        assert result["reason"] == "Invalid token"
        assert "segments" not in result["reason"].lower()
        assert "signature" not in result["reason"].lower()
