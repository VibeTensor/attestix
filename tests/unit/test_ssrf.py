"""Tests for auth/ssrf.py — SSRF protection."""

from unittest.mock import patch

from auth.ssrf import validate_url_host


class TestBlockedHosts:
    def test_blocks_localhost(self):
        assert validate_url_host("localhost") is not None

    def test_blocks_loopback_ipv4(self):
        assert validate_url_host("127.0.0.1") is not None

    def test_blocks_loopback_ipv6(self):
        assert validate_url_host("::1") is not None

    def test_blocks_private_10x(self):
        assert validate_url_host("10.0.0.1") is not None

    def test_blocks_private_192(self):
        assert validate_url_host("192.168.1.1") is not None

    def test_blocks_private_172(self):
        assert validate_url_host("172.16.0.1") is not None

    def test_blocks_metadata_endpoint(self):
        assert validate_url_host("169.254.169.254") is not None

    def test_blocks_local_suffix(self):
        assert validate_url_host("myserver.local") is not None

    def test_blocks_internal_suffix(self):
        assert validate_url_host("api.internal") is not None

    def test_blocks_metadata_google(self):
        assert validate_url_host("metadata.google.internal") is not None

    def test_blocks_zero_address(self):
        assert validate_url_host("0.0.0.0") is not None


class TestAllowedHosts:
    def test_allows_public_ip(self):
        # Mock DNS resolution to return a public IP
        with patch("auth.ssrf.socket.getaddrinfo") as mock_dns:
            mock_dns.return_value = [
                (2, 1, 0, "", ("93.184.216.34", 0)),  # example.com
            ]
            assert validate_url_host("example.com") is None

    def test_allows_public_ip_direct(self):
        assert validate_url_host("8.8.8.8") is None


class TestDnsRebinding:
    def test_blocks_hostname_resolving_to_private(self):
        """A public hostname that resolves to 127.0.0.1 should be blocked."""
        with patch("auth.ssrf.socket.getaddrinfo") as mock_dns:
            mock_dns.return_value = [
                (2, 1, 0, "", ("127.0.0.1", 0)),
            ]
            result = validate_url_host("evil.example.com")
            assert result is not None
            assert "private" in result.lower() or "blocked" in result.lower()


class TestEdgeCases:
    def test_empty_hostname(self):
        assert validate_url_host("") is not None

    def test_ipv6_brackets_stripped(self):
        assert validate_url_host("[::1]") is not None
