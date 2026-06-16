"""Tests for the post-quantum / hybrid signing module (attestix.auth.pqc).

Skipped unless the [pqc] extra (dilithium-py) is installed.
"""

import pytest

pytest.importorskip("dilithium_py", reason="requires the [pqc] extra (dilithium-py)")

from attestix.auth.crypto import generate_ed25519_keypair, public_key_to_did_key
from attestix.auth import pqc


PAYLOAD = {"id": "urn:uuid:1", "claim": "agent-is-authorized", "n": 7}


class TestMlDsa:
    def test_sign_verify_roundtrip(self):
        pub, sec = pqc.generate_mldsa_keypair()
        sig = pqc.mldsa_sign(sec, PAYLOAD)
        assert pqc.mldsa_verify(pub, PAYLOAD, sig) is True

    def test_tampered_payload_rejected(self):
        pub, sec = pqc.generate_mldsa_keypair()
        sig = pqc.mldsa_sign(sec, PAYLOAD)
        assert pqc.mldsa_verify(pub, {**PAYLOAD, "claim": "tampered"}, sig) is False

    def test_wrong_key_rejected(self):
        _, sec = pqc.generate_mldsa_keypair()
        other_pub, _ = pqc.generate_mldsa_keypair()
        sig = pqc.mldsa_sign(sec, PAYLOAD)
        assert pqc.mldsa_verify(other_pub, PAYLOAD, sig) is False

    def test_did_key_roundtrip(self):
        pub, _ = pqc.generate_mldsa_keypair()
        did = pqc.mldsa_public_key_to_did_key(pub)
        assert did.startswith("did:key:z")
        assert pqc.did_key_to_mldsa_public_key(did) == pub

    def test_did_key_rejects_ed25519(self):
        _, ed_pub = generate_ed25519_keypair()
        ed_did = public_key_to_did_key(ed_pub)
        with pytest.raises(ValueError):
            pqc.did_key_to_mldsa_public_key(ed_did)


class TestHybridAntiStripping:
    def _keys(self):
        ed_priv, ed_pub = generate_ed25519_keypair()
        pq_pub, pq_sec = pqc.generate_mldsa_keypair()
        return ed_priv, ed_pub, pq_pub, pq_sec

    def test_hybrid_roundtrip(self):
        ed_priv, ed_pub, pq_pub, pq_sec = self._keys()
        proof = pqc.hybrid_sign(ed_priv, pq_sec, PAYLOAD)
        assert "~" in proof
        assert pqc.hybrid_verify(ed_pub, pq_pub, PAYLOAD, proof) is True

    def test_tampered_payload_rejected(self):
        ed_priv, ed_pub, pq_pub, pq_sec = self._keys()
        proof = pqc.hybrid_sign(ed_priv, pq_sec, PAYLOAD)
        assert pqc.hybrid_verify(ed_pub, pq_pub, {**PAYLOAD, "n": 8}, proof) is False

    def test_cannot_strip_to_ed25519_only(self):
        # Drop the ML-DSA half: a downgraded classical-only proof must NOT verify.
        ed_priv, ed_pub, pq_pub, pq_sec = self._keys()
        proof = pqc.hybrid_sign(ed_priv, pq_sec, PAYLOAD)
        ed_only = proof.split("~", 1)[0]
        assert pqc.hybrid_verify(ed_pub, pq_pub, PAYLOAD, ed_only) is False
        assert pqc.hybrid_verify(ed_pub, pq_pub, PAYLOAD, ed_only + "~") is False

    def test_cannot_strip_to_mldsa_only(self):
        ed_priv, ed_pub, pq_pub, pq_sec = self._keys()
        proof = pqc.hybrid_sign(ed_priv, pq_sec, PAYLOAD)
        pq_only = proof.split("~", 1)[1]
        assert pqc.hybrid_verify(ed_pub, pq_pub, PAYLOAD, "~" + pq_only) is False

    def test_forged_pq_half_rejected(self):
        # Valid Ed25519 half + a PQ signature from a DIFFERENT key must fail.
        ed_priv, ed_pub, pq_pub, pq_sec = self._keys()
        _, other_sec = pqc.generate_mldsa_keypair()
        ed_sig = pqc.hybrid_sign(ed_priv, pq_sec, PAYLOAD).split("~", 1)[0]
        forged = f"{ed_sig}~{pqc.mldsa_sign(other_sec, PAYLOAD)}"
        assert pqc.hybrid_verify(ed_pub, pq_pub, PAYLOAD, forged) is False
