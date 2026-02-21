"""Performance benchmarks for Attestix core operations.

Measures median latency for cryptographic and service-layer operations.
Results are printed to stdout so they appear in the pytest -v output.
"""

import statistics
import time

import pytest

from auth.crypto import (
    canonicalize_json,
    generate_ed25519_keypair,
    public_key_to_did_key,
    sign_json_payload,
    sign_message,
    verify_json_signature,
    verify_signature,
)


def _benchmark(func, iterations=1000):
    """Run func() N times and return (median_ms, all_times_ms)."""
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        func()
        elapsed = (time.perf_counter() - start) * 1000
        times.append(elapsed)
    median = statistics.median(times)
    return median, times


class TestCryptoBenchmarks:
    """Core cryptographic operation benchmarks (1000 iterations each)."""

    def test_ed25519_key_generation(self):
        median, _ = _benchmark(generate_ed25519_keypair, iterations=1000)
        print(f"\n  Ed25519 key generation: {median:.3f} ms median (1000 runs)")
        assert median < 50, f"Key generation too slow: {median:.3f} ms"

    def test_json_canonicalization(self):
        payload = {
            "name": "Test Agent",
            "capabilities": ["read", "write", "admin"],
            "metadata": {"version": 1, "active": True},
            "nested": {"deep": {"value": 42}},
        }
        median, _ = _benchmark(lambda: canonicalize_json(payload), iterations=1000)
        print(f"\n  JSON canonicalization: {median:.3f} ms median (1000 runs)")
        assert median < 10, f"Canonicalization too slow: {median:.3f} ms"

    def test_sign_verify_cycle(self):
        private_key, public_key = generate_ed25519_keypair()
        message = b"benchmark message for sign/verify cycle testing"

        def sign_and_verify():
            sig = sign_message(private_key, message)
            verify_signature(public_key, sig, message)

        median, _ = _benchmark(sign_and_verify, iterations=1000)
        print(f"\n  Ed25519 sign+verify cycle: {median:.3f} ms median (1000 runs)")
        assert median < 20, f"Sign/verify too slow: {median:.3f} ms"


class TestServiceBenchmarks:
    """Service-layer operation benchmarks."""

    def test_identity_creation(self, identity_service):
        def create():
            identity_service.create_identity(
                display_name="Bench Agent",
                source_protocol="mcp",
                capabilities=["read"],
                description="Benchmark identity",
            )

        median, _ = _benchmark(create, iterations=100)
        print(f"\n  Identity creation: {median:.3f} ms median (100 runs)")
        assert median < 200, f"Identity creation too slow: {median:.3f} ms"

    def test_credential_issuance(self, credential_service, sample_agent_id):
        def issue():
            credential_service.issue_credential(
                subject_id=sample_agent_id,
                credential_type="AgentIdentityCredential",
                issuer_name="Benchmark",
                claims={"role": "bench"},
            )

        median, _ = _benchmark(issue, iterations=100)
        print(f"\n  Credential issuance: {median:.3f} ms median (100 runs)")
        assert median < 200, f"Credential issuance too slow: {median:.3f} ms"

    def test_credential_verification(self, credential_service, sample_agent_id):
        vc = credential_service.issue_credential(
            subject_id=sample_agent_id,
            credential_type="AgentIdentityCredential",
            issuer_name="Benchmark",
            claims={"role": "bench"},
        )
        cred_id = vc["id"]

        median, _ = _benchmark(
            lambda: credential_service.verify_credential(cred_id),
            iterations=100,
        )
        print(f"\n  Credential verification: {median:.3f} ms median (100 runs)")
        assert median < 200, f"Credential verification too slow: {median:.3f} ms"

    def test_ucan_token_creation(self, delegation_service):
        def create():
            delegation_service.create_delegation(
                issuer_agent_id="bench-issuer",
                audience_agent_id="bench-audience",
                capabilities=["read"],
            )

        median, _ = _benchmark(create, iterations=100)
        print(f"\n  UCAN token creation: {median:.3f} ms median (100 runs)")
        assert median < 200, f"UCAN creation too slow: {median:.3f} ms"
