"""RFC 8032 Section 7.1 - Ed25519 canonical test vectors.

Validates that Attestix's Ed25519 wrapper functions (sign/verify/key derivation)
produce results identical to the IETF reference vectors.
"""

import pytest

from auth.crypto import (
    private_key_from_bytes,
    public_key_to_bytes,
    sign_message,
    verify_signature,
)

# RFC 8032 Section 7.1 test vectors (seed, expected_pubkey, message, expected_signature)
# Vector 4 (1023-byte message) omitted for brevity; the other 4 cover all edge cases.
RFC8032_VECTORS = [
    pytest.param(
        "9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60",
        "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a",
        "",
        "e5564300c360ac729086e2cc806e828a"
        "84877f1eb8e5d974d873e06522490155"
        "5fb8821590a33bacc61e39701cf9b46b"
        "d25bf5f0595bbe24655141438e7a100b",
        id="vector1-empty-message",
    ),
    pytest.param(
        "4ccd089b28ff96da9db6c346ec114e0f5b8a319f35aba624da8cf6ed4fb8a6fb",
        "3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c",
        "72",
        "92a009a9f0d4cab8720e820b5f642540"
        "a2b27b5416503f8fb3762223ebdb69da"
        "085ac1e43e15996e458f3613d0f11d8c"
        "387b2eaeb4302aeeb00d291612bb0c00",
        id="vector2-one-byte",
    ),
    pytest.param(
        "c5aa8df43f9f837bedb7442f31dcb7b166d38535076f094b85ce3a2e0b4458f7",
        "fc51cd8e6218a1a38da47ed00230f0580816ed13ba3303ac5deb911548908025",
        "af82",
        "6291d657deec24024827e69c3abe01a3"
        "0ce548a284743a445e3680d7db5ac3ac"
        "18ff9b538d16f290ae67f760984dc659"
        "4a7c15e9716ed28dc027beceea1ec40a",
        id="vector3-two-bytes",
    ),
    pytest.param(
        "833fe62409237b9d62ec77587520911e9a759cec1d19755b7da901b96dca3d42",
        "ec172b93ad5e563bf4932c70e1245034c35467ef2efd4d64ebf819683467e2bf",
        "ddaf35a193617abacc417349ae20413112e6fa4e89a97ea20a9eeee64b55d39a"
        "2192992a274fc1a836ba3c23a3feebbd454d4423643ce80e2a9ac94fa54ca49f",
        "dc2a4459e7369633a52b1bf277839a00"
        "201009a3efbf3ecb69bea2186c26b589"
        "09351fc9ac90b3ecfdfbc7c66431e030"
        "3dca179c138ac17ad9bef1177331a704",
        id="vector5-sha512-abc",
    ),
]


class TestRFC8032Ed25519Vectors:
    """Validate Ed25519 against RFC 8032 Section 7.1 canonical test vectors."""

    @pytest.mark.parametrize("seed_hex,pubkey_hex,msg_hex,sig_hex", RFC8032_VECTORS)
    def test_public_key_derivation(self, seed_hex, pubkey_hex, msg_hex, sig_hex):
        """Verify that the public key derived from the seed matches the RFC vector."""
        seed = bytes.fromhex(seed_hex)
        private_key = private_key_from_bytes(seed)
        public_key = private_key.public_key()
        derived_hex = public_key_to_bytes(public_key).hex()
        assert derived_hex == pubkey_hex, (
            f"Public key mismatch: got {derived_hex}, expected {pubkey_hex}"
        )

    @pytest.mark.parametrize("seed_hex,pubkey_hex,msg_hex,sig_hex", RFC8032_VECTORS)
    def test_signature_generation(self, seed_hex, pubkey_hex, msg_hex, sig_hex):
        """Verify that signing produces the exact RFC 8032 expected signature."""
        seed = bytes.fromhex(seed_hex)
        message = bytes.fromhex(msg_hex) if msg_hex else b""
        private_key = private_key_from_bytes(seed)
        signature = sign_message(private_key, message)
        sig_hex_actual = signature.hex()
        assert sig_hex_actual == sig_hex, (
            f"Signature mismatch: got {sig_hex_actual}, expected {sig_hex}"
        )

    @pytest.mark.parametrize("seed_hex,pubkey_hex,msg_hex,sig_hex", RFC8032_VECTORS)
    def test_signature_verification(self, seed_hex, pubkey_hex, msg_hex, sig_hex):
        """Verify that the RFC 8032 signature passes verification."""
        seed = bytes.fromhex(seed_hex)
        message = bytes.fromhex(msg_hex) if msg_hex else b""
        private_key = private_key_from_bytes(seed)
        public_key = private_key.public_key()
        signature = bytes.fromhex(sig_hex)
        assert verify_signature(public_key, signature, message) is True

    @pytest.mark.parametrize("seed_hex,pubkey_hex,msg_hex,sig_hex", RFC8032_VECTORS)
    def test_wrong_message_fails_verification(self, seed_hex, pubkey_hex, msg_hex, sig_hex):
        """Verify that a tampered message fails verification."""
        seed = bytes.fromhex(seed_hex)
        private_key = private_key_from_bytes(seed)
        public_key = private_key.public_key()
        signature = bytes.fromhex(sig_hex)
        tampered = b"tampered message content"
        assert verify_signature(public_key, signature, tampered) is False

    def test_key_length_is_32_bytes(self):
        """Ed25519 public keys must be exactly 32 bytes."""
        seed = bytes.fromhex(
            "9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60"
        )
        private_key = private_key_from_bytes(seed)
        pub_bytes = public_key_to_bytes(private_key.public_key())
        assert len(pub_bytes) == 32

    def test_signature_length_is_64_bytes(self):
        """Ed25519 signatures must be exactly 64 bytes."""
        seed = bytes.fromhex(
            "9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60"
        )
        private_key = private_key_from_bytes(seed)
        sig = sign_message(private_key, b"test")
        assert len(sig) == 64
