#!/usr/bin/env python3
"""Generate the cross-language verifier conformance vectors for Attestix.

This script emits ``vectors.json`` next to itself. Every vector is produced
from the REAL ``attestix`` 0.4.0 crypto primitives (``attestix.auth.crypto`` +
the service layer), so the vectors are authoritative: any port (Go, Rust, Java,
R, JS) that reproduces the same booleans/bytes is byte-compatible with the
reference Python verifier.

Determinism:
    * A FIXED 32-byte Ed25519 seed is used for the issuer/server key so the
      did:key, signatures, and canonical bytes are reproducible across runs.
    * All timestamps are FIXED ISO-8601 strings (no ``datetime.now``), so the
      valid/expired vectors are stable.
    * UCAN/JWT vectors use FIXED ``iat``/``exp``/``nbf``/``jti`` so the compact
      JWT serialization (and therefore its EdDSA signature) is reproducible.

Run:
    python spec/verify/v1/generate_vectors.py
    # writes spec/verify/v1/vectors.json

The script does NOT reimplement any crypto. It only *drives* attestix and
records inputs + expected outputs.
"""

import base64
import copy
import json
import os
from pathlib import Path

import jwt
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

# --- REAL attestix crypto (do not reimplement) -----------------------------
from attestix.auth.crypto import (
    ED25519_MULTICODEC_PREFIX,
    canonicalize_json,
    did_key_fragment,
    did_key_to_public_key,
    public_key_to_bytes,
    public_key_to_did_key,
    sign_json_payload,
    verify_json_signature,
)

HERE = Path(__file__).resolve().parent
OUT = HERE / "vectors.json"

# Fixed deterministic Ed25519 seed (32 bytes, hex). This is the ISSUER / server
# root-of-trust key for every vector below. A fixed seed makes the did:key,
# every signature, and every canonical-byte string fully reproducible.
ISSUER_SEED_HEX = (
    "9d61b19deffdeaf3ee2cd05c0fc7d1bbf2b6c5e4e6b3d2c1a0f9e8d7c6b5a4f3"
)
# A second fixed seed for the delegation child (audience) key, used only so the
# child has a stable DID in the chain vectors (the chain is signed by the SERVER
# key, matching attestix DelegationService which signs all tokens with one key).
CHILD_SEED_HEX = (
    "4ccd089b28ff96da9db6c346ec114e0f5b8a319f35aba624da8cf6ed4fb8a6f3"
)


def hexbytes(h: str) -> bytes:
    return bytes.fromhex(h)


def b64u_pad(raw: bytes) -> str:
    """base64url WITH padding (matches attestix sign_json_payload output)."""
    return base64.urlsafe_b64encode(raw).decode("ascii")


def build_issuer():
    seed = hexbytes(ISSUER_SEED_HEX)
    priv = Ed25519PrivateKey.from_private_bytes(seed)
    pub = priv.public_key()
    did = public_key_to_did_key(pub)
    return seed, priv, pub, did


def vec_canonicalize():
    """JCS-canonical bytes of a deliberately tricky object.

    Exercises: key sorting by codepoint, raw UTF-8 (no \\uXXXX), NFC
    normalization, whole-number float -> int, nested objects, arrays,
    booleans, null, integers.
    """
    # NOTE: the e-with-combining-acute (NFD) MUST normalize to single-codepoint
    # NFC form. We feed the decomposed form; the canonicalizer must compose it.
    decomposed_e = "café"  # 'café' as 'cafe' + COMBINING ACUTE ACCENT
    obj = {
        "z_last": True,
        "a_first": None,
        "unicode": "héllo é ☃ \U0001f600",  # é, snowman, emoji
        "nfc_test": decomposed_e,
        "whole_float": 1.0,        # must serialize as 1
        "real_float": 1.5,         # must stay 1.5
        "neg_int": -42,
        "nested": {"b": 2, "a": 1, "deep": {"y": [3, 2, 1], "x": "z"}},
        "arr": [1, "two", False, None, {"k": "v"}],
        "empty_obj": {},
        "empty_arr": [],
        "big_int": 9007199254740993,  # > 2^53, ports must keep as integer
    }
    canon = canonicalize_json(obj)
    return {
        "id": "canon-001",
        "kind": "canonicalize",
        "description": (
            "JCS-style canonicalization. A port's canonicaliser MUST produce "
            "byte-identical output to canonical_bytes_hex. Note NFC composition "
            "of 'cafe'+U+0301 -> 'café', whole_float 1.0 -> 1, keys sorted "
            "by Unicode codepoint, raw UTF-8 (no \\uXXXX escapes)."
        ),
        "input": obj,
        "expected": {
            "canonical_utf8": canon.decode("utf-8"),
        },
        "canonical_bytes_hex": canon.hex(),
    }


def vec_didkey(pub, did):
    raw = public_key_to_bytes(pub)
    multicodec = ED25519_MULTICODEC_PREFIX + raw
    # round-trip sanity: decode back through the real function
    decoded_pub = did_key_to_public_key(did)
    assert public_key_to_bytes(decoded_pub) == raw
    multibase = did[len("did:key:"):]  # the 'z....' part
    return {
        "id": "didkey-001",
        "kind": "did_key_decode",
        "description": (
            "did:key for Ed25519. multibase = 'z' + base58btc(0xed01 || raw32). "
            "A port MUST decode pubkey_multibase to the raw 32-byte key. The "
            "multicodec prefix is 0xed 0x01 (varint for ed25519-pub)."
        ),
        "input": {"did": did},
        "expected": {
            "multicodec_prefix_hex": ED25519_MULTICODEC_PREFIX.hex(),  # "ed01"
            "pubkey_raw_hex": raw.hex(),
            "multibase_prefix": "z",
            "fragment": did_key_fragment(did),  # "#z..."
            "verification_method": f"{did}{did_key_fragment(did)}",
        },
        "pubkey_multibase": multibase,
        "pubkey_raw_hex": raw.hex(),
        "multicodec_full_hex": multicodec.hex(),
    }


def _base_credential(did):
    """A fixed W3C VC body (pre-proof). Timestamps are frozen for determinism."""
    return {
        "@context": [
            "https://www.w3.org/2018/credentials/v1",
            "https://w3id.org/security/suites/ed25519-2020/v1",
        ],
        "id": "urn:uuid:11111111-2222-3333-4444-555555555555",
        "type": ["VerifiableCredential", "EUAIActComplianceCredential"],
        "issuer": {"id": did, "name": "VibeTensor"},
        "issuanceDate": "2026-01-01T00:00:00+00:00",
        "expirationDate": "2027-01-01T00:00:00+00:00",
        "credentialSubject": {
            "id": "did:key:zSubjectAgentPlaceholder",
            "riskTier": "high",
            "conformityAssessed": True,
        },
        "credentialStatus": {
            "id": "urn:uuid:11111111-2222-3333-4444-555555555555#status",
            "type": "RevocationList2021Status",
            "revoked": False,
            "revocation_reason": None,
            "revoked_at": None,
        },
    }


# Fields excluded from the VC signing payload (matches
# CredentialService.MUTABLE_FIELDS).
MUTABLE_FIELDS = {"proof", "credentialStatus"}


def _sign_vc(priv, did, cred):
    payload = {k: v for k, v in cred.items() if k not in MUTABLE_FIELDS}
    sig = sign_json_payload(priv, payload)
    out = copy.deepcopy(cred)
    out["proof"] = {
        "type": "Ed25519Signature2020",
        "created": "2026-01-01T00:00:00+00:00",
        "verificationMethod": f"{did}{did_key_fragment(did)}",
        "proofPurpose": "assertionMethod",
        "proofValue": sig,
    }
    return out, payload, sig


def vec_vc_valid(priv, pub, did):
    cred = _base_credential(did)
    signed, payload, sig = _sign_vc(priv, did, cred)
    # self-check via the real verifier primitive
    assert verify_json_signature(pub, payload, sig) is True
    canon = canonicalize_json(payload)
    return {
        "id": "vc-valid-001",
        "kind": "verify_credential",
        "description": (
            "Valid W3C VC with Ed25519 proof. Signed payload = the VC with "
            "'proof' and 'credentialStatus' REMOVED, then JCS-canonicalized. "
            "Expected: signature valid, not expired, not revoked -> verify true."
        ),
        "input": signed,
        "expected": {
            "verify": True,
            "signature_valid": True,
            "not_expired": True,
            "not_revoked": True,
        },
        "signing_payload": payload,
        "canonical_bytes_hex": canon.hex(),
        "signature_b64url": sig,
        "pubkey_multibase": did[len("did:key:"):],
        "pubkey_raw_hex": public_key_to_bytes(pub).hex(),
    }


def vec_vc_tampered(priv, pub, did):
    cred = _base_credential(did)
    signed, payload, sig = _sign_vc(priv, did, cred)
    tampered = copy.deepcopy(signed)
    # Flip one byte in a signed claim: change riskTier "high" -> "hivh".
    tampered["credentialSubject"]["riskTier"] = "hivh"
    tampered_payload = {
        k: v for k, v in tampered.items() if k not in MUTABLE_FIELDS
    }
    # self-check: signature must now FAIL against the tampered payload
    assert verify_json_signature(pub, tampered_payload, sig) is False
    return {
        "id": "vc-tampered-001",
        "kind": "verify_credential",
        "description": (
            "Tampered VC: one claim byte flipped (riskTier 'high' -> 'hivh') "
            "AFTER signing. The original proofValue no longer matches the "
            "canonical bytes of the tampered payload -> signature invalid -> "
            "verify false."
        ),
        "input": tampered,
        "expected": {
            "verify": False,
            "signature_valid": False,
            "not_expired": True,
            "not_revoked": True,
        },
        "signature_b64url": sig,
        "canonical_bytes_hex": canonicalize_json(tampered_payload).hex(),
        "pubkey_multibase": did[len("did:key:"):],
        "pubkey_raw_hex": public_key_to_bytes(pub).hex(),
    }


def vec_vc_expired(priv, pub, did):
    cred = _base_credential(did)
    cred["id"] = "urn:uuid:99999999-8888-7777-6666-555555555555"
    cred["credentialStatus"]["id"] = cred["id"] + "#status"
    # expirationDate in the past; issuanceDate also past.
    cred["issuanceDate"] = "2020-01-01T00:00:00+00:00"
    cred["expirationDate"] = "2021-01-01T00:00:00+00:00"
    signed, payload, sig = _sign_vc(priv, did, cred)
    # Signature itself is VALID (we signed the past-dated body); only expiry fails.
    assert verify_json_signature(pub, payload, sig) is True
    return {
        "id": "vc-expired-001",
        "kind": "verify_credential",
        "description": (
            "Expired VC. expirationDate is 2021-01-01 (past). The signature is "
            "cryptographically valid; only the expiry check fails. Expected: "
            "not_expired false -> verify false. Compare expirationDate against "
            "the verifier's current time (here, any time after 2021-01-01)."
        ),
        "input": signed,
        "expected": {
            "verify": False,
            "signature_valid": True,
            "not_expired": False,
            "not_revoked": True,
        },
        "signature_b64url": sig,
        "canonical_bytes_hex": canonicalize_json(payload).hex(),
        "now_reference": "2026-01-01T00:00:00+00:00",
        "pubkey_multibase": did[len("did:key:"):],
        "pubkey_raw_hex": public_key_to_bytes(pub).hex(),
    }


# --- UCAN delegation chain vectors -----------------------------------------
# attestix DelegationService signs EVERY token (root and child) with the single
# SERVER key using PyJWT EdDSA (alg=EdDSA). The signed message is the JWT compact
# form: base64url(header) + "." + base64url(payload). This is NOT the JCS path.
# We reproduce that here with the same fixed key so ports can verify the JWT.

# Frozen UCAN timestamps (well within validity for a verifier running ~2026).
UCAN_IAT = 1767225600   # 2026-01-01T00:00:00Z
UCAN_EXP = 4102444800   # 2100-01-01T00:00:00Z (far future -> not expired)
ROOT_JTI = "root-jti-fixed-0001"
CHILD_JTI = "child-jti-fixed-0002"
BAD_JTI = "child-bad-jti-0003"


def _make_token(priv, did, *, jti, aud, delegator, att, prf):
    payload = {
        "iss": did,
        "aud": aud,
        "sub": aud,
        "iat": UCAN_IAT,
        "exp": UCAN_EXP,
        "nbf": UCAN_IAT,
        "jti": jti,
        "att": att,
        "delegator": delegator,
        "prf": prf,
        "attestix_version": "0.1.0",
        "typ": "ucan/delegation",
    }
    token = jwt.encode(
        payload,
        priv,
        algorithm="EdDSA",
        headers={"typ": "JWT", "ucv": "0.9.0", "alg": "EdDSA"},
    )
    return token, payload


def vec_delegation_chain(priv, did, child_did):
    # ROOT: server delegates ["read","write","delete"] to child agent.
    root_token, root_payload = _make_token(
        priv, did,
        jti=ROOT_JTI,
        aud=child_did,
        delegator=did,
        att=["read", "write", "delete"],
        prf=[],
    )
    # CHILD (valid attenuation): subset ["read","write"].
    child_token, child_payload = _make_token(
        priv, did,
        jti=CHILD_JTI,
        aud="did:key:zGrandchildAgentPlaceholder",
        delegator=child_did,
        att=["read", "write"],          # subset of parent -> valid
        prf=[root_token],
    )
    # CHILD (escalation): adds "admin" not held by parent -> NOT a subset.
    bad_child_token, bad_child_payload = _make_token(
        priv, did,
        jti=BAD_JTI,
        aud="did:key:zGrandchildAgentPlaceholder",
        delegator=child_did,
        att=["read", "admin"],          # 'admin' not in parent -> escalation
        prf=[root_token],
    )

    valid_vec = {
        "id": "ucan-chain-valid-001",
        "kind": "verify_delegation_chain",
        "description": (
            "UCAN delegation chain root->child with valid attenuation. Tokens "
            "are EdDSA JWTs signed by the SERVER key (compact JWT form is the "
            "signed message, NOT JCS). Child att ['read','write'] is a SUBSET "
            "of parent att ['read','write','delete']. Expected: each token "
            "signature verifies AND child att subset-of parent att -> verify "
            "true. Verify the whole prf chain recursively."
        ),
        "input": {
            "token": child_token,
            "parent_token": root_token,
            "child_att": child_payload["att"],
            "parent_att": root_payload["att"],
        },
        "expected": {
            "verify": True,
            "child_signature_valid": True,
            "parent_signature_valid": True,
            "attenuation_is_subset": True,
        },
        "signing_alg": "EdDSA",
        "pubkey_multibase": did[len("did:key:"):],
        "pubkey_raw_hex": public_key_to_bytes(
            did_key_to_public_key(did)
        ).hex(),
    }

    bad_vec = {
        "id": "ucan-chain-escalation-002",
        "kind": "verify_delegation_chain",
        "description": (
            "UCAN delegation chain where the child att ['read','admin'] is NOT "
            "a subset of parent att ['read','write','delete'] ('admin' is "
            "escalated). Both JWT signatures verify, but capability attenuation "
            "fails. Expected: verify false on the subset check."
        ),
        "input": {
            "token": bad_child_token,
            "parent_token": root_token,
            "child_att": bad_child_payload["att"],
            "parent_att": root_payload["att"],
        },
        "expected": {
            "verify": False,
            "child_signature_valid": True,
            "parent_signature_valid": True,
            "attenuation_is_subset": False,
        },
        "signing_alg": "EdDSA",
        "pubkey_multibase": did[len("did:key:"):],
        "pubkey_raw_hex": public_key_to_bytes(
            did_key_to_public_key(did)
        ).hex(),
    }
    return valid_vec, bad_vec


def main():
    seed, priv, pub, did = build_issuer()
    child_priv = Ed25519PrivateKey.from_private_bytes(hexbytes(CHILD_SEED_HEX))
    child_did = public_key_to_did_key(child_priv.public_key())

    vectors = []
    vectors.append(vec_canonicalize())
    vectors.append(vec_didkey(pub, did))
    vectors.append(vec_vc_valid(priv, pub, did))
    vectors.append(vec_vc_tampered(priv, pub, did))
    vectors.append(vec_vc_expired(priv, pub, did))
    valid_chain, bad_chain = vec_delegation_chain(priv, did, child_did)
    vectors.append(valid_chain)
    vectors.append(bad_chain)

    doc = {
        "spec": "attestix-verify-conformance",
        "version": "v1",
        "generator": "spec/verify/v1/generate_vectors.py",
        "attestix_version": __import__("attestix").__version__,
        "description": (
            "Authoritative cross-language verifier conformance vectors, "
            "generated from the real attestix crypto. Every port (Go, Rust, "
            "Java, R, JS) MUST reproduce the 'expected' values. See README.md "
            "for the exact canonical-form rules and CONFORMANCE.md for the "
            "verifier surface."
        ),
        "issuer_did": did,
        "issuer_pubkey_raw_hex": public_key_to_bytes(pub).hex(),
        "issuer_seed_hex": seed.hex(),
        "vector_count": len(vectors),
        "vectors": vectors,
    }

    # Deterministic, stable on-disk form (sorted keys, 2-space indent, LF).
    text = json.dumps(doc, indent=2, ensure_ascii=False, sort_keys=True)
    OUT.write_text(text + "\n", encoding="utf-8")
    print(f"Wrote {OUT} ({len(vectors)} vectors)")
    for v in vectors:
        print(f"  - {v['id']} [{v['kind']}]")


if __name__ == "__main__":
    main()
