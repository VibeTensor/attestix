"""Tests for auth/crypto.py — Ed25519 key operations, signing, verification."""

from auth.crypto import (
    generate_ed25519_keypair,
    private_key_to_bytes,
    public_key_to_bytes,
    private_key_from_bytes,
    public_key_from_bytes,
    sign_message,
    verify_signature,
    public_key_to_did_key,
    did_key_to_public_key,
    sign_json_payload,
    verify_json_signature,
    load_or_create_signing_key,
    _normalize_for_signing,
)


class TestKeypairGeneration:
    def test_generate_keypair(self):
        priv, pub = generate_ed25519_keypair()
        assert priv is not None
        assert pub is not None

    def test_private_key_roundtrip(self):
        priv, _ = generate_ed25519_keypair()
        raw = private_key_to_bytes(priv)
        assert len(raw) == 32
        restored = private_key_from_bytes(raw)
        assert private_key_to_bytes(restored) == raw

    def test_public_key_roundtrip(self):
        _, pub = generate_ed25519_keypair()
        raw = public_key_to_bytes(pub)
        assert len(raw) == 32
        restored = public_key_from_bytes(raw)
        assert public_key_to_bytes(restored) == raw


class TestSignVerify:
    def test_sign_and_verify(self):
        priv, pub = generate_ed25519_keypair()
        msg = b"hello attestix"
        sig = sign_message(priv, msg)
        assert len(sig) == 64
        assert verify_signature(pub, sig, msg)

    def test_wrong_message_fails(self):
        priv, pub = generate_ed25519_keypair()
        sig = sign_message(priv, b"correct message")
        assert not verify_signature(pub, sig, b"wrong message")

    def test_wrong_key_fails(self):
        priv1, _ = generate_ed25519_keypair()
        _, pub2 = generate_ed25519_keypair()
        sig = sign_message(priv1, b"message")
        assert not verify_signature(pub2, sig, b"message")


class TestDidKey:
    def test_did_key_roundtrip(self):
        priv, pub = generate_ed25519_keypair()
        did = public_key_to_did_key(pub)
        assert did.startswith("did:key:z")
        recovered = did_key_to_public_key(did)
        assert public_key_to_bytes(recovered) == public_key_to_bytes(pub)

    def test_invalid_did_key_raises(self):
        import pytest
        with pytest.raises(ValueError, match="Invalid did:key"):
            did_key_to_public_key("did:web:example.com")

    def test_wrong_multicodec_raises(self):
        import pytest
        import base58
        # Craft a did:key with wrong prefix
        bad_bytes = bytes([0x00, 0x00]) + b"\x00" * 32
        encoded = base58.b58encode(bad_bytes).decode("ascii")
        with pytest.raises(ValueError, match="wrong multicodec"):
            did_key_to_public_key(f"did:key:z{encoded}")


class TestJsonSigning:
    def test_sign_verify_payload(self):
        priv, pub = generate_ed25519_keypair()
        payload = {"name": "test", "value": 42}
        sig = sign_json_payload(priv, payload)
        assert isinstance(sig, str)
        assert verify_json_signature(pub, payload, sig)

    def test_tampered_payload_fails(self):
        priv, pub = generate_ed25519_keypair()
        payload = {"name": "test", "value": 42}
        sig = sign_json_payload(priv, payload)
        tampered = {"name": "test", "value": 99}
        assert not verify_json_signature(pub, tampered, sig)

    def test_key_order_irrelevant(self):
        """JSON signing uses sort_keys, so dict order shouldn't matter."""
        priv, pub = generate_ed25519_keypair()
        payload_a = {"z": 1, "a": 2}
        payload_b = {"a": 2, "z": 1}
        sig = sign_json_payload(priv, payload_a)
        assert verify_json_signature(pub, payload_b, sig)


class TestNormalize:
    def test_nfc_normalization(self):
        # Combining e + acute accent should normalize to e-acute
        import unicodedata
        combining = "e\u0301"  # e + combining acute
        composed = "\u00e9"    # e-acute
        assert _normalize_for_signing(combining) == composed

    def test_nested_normalization(self):
        data = {"key": ["e\u0301", {"inner": "e\u0301"}]}
        result = _normalize_for_signing(data)
        assert result["key"][0] == "\u00e9"
        assert result["key"][1]["inner"] == "\u00e9"


class TestLoadOrCreateSigningKey:
    def test_creates_key_on_first_call(self, tmp_path):
        key_file = tmp_path / ".test_key.json"
        priv, did = load_or_create_signing_key(key_file)
        assert did.startswith("did:key:z")
        assert key_file.exists()

    def test_loads_existing_key(self, tmp_path):
        key_file = tmp_path / ".test_key.json"
        priv1, did1 = load_or_create_signing_key(key_file)
        priv2, did2 = load_or_create_signing_key(key_file)
        assert did1 == did2
        assert private_key_to_bytes(priv1) == private_key_to_bytes(priv2)
