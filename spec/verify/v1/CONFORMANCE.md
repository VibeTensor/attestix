# Attestix Verifier Conformance Suite (v1)

A port (Go, Rust, Java, R, JS, …) is **conformant** when it passes every vector
in [`vectors.json`](./vectors.json). The vectors are generated from the real
attestix 0.4.0 crypto by [`generate_vectors.py`](./generate_vectors.py), so they
are authoritative. The exact canonical-form rules a port must reproduce are in
[`README.md`](./README.md) — read it first.

## The verifier surface a port MUST implement

| Function | Input | Output |
|---|---|---|
| `canonicalize(obj) -> bytes` | any JSON value | canonical UTF-8 bytes (README §1) |
| `decodeDidKey(multibase) -> rawPubKey[32]` | `z…` multibase | 32-byte Ed25519 public key (README §2) |
| `verifyCredential(vc, now) -> {verify, signature_valid, not_expired, not_revoked}` | full W3C VC + current time | booleans (README §1.5) |
| `verifyDelegationChain(token, parentToken, serverPubKey, now) -> {verify, …}` | EdDSA JWTs | booleans (README §3) |

Notes:
- `verifyCredential` strips `proof` and `credentialStatus`, canonicalizes the
  rest, then Ed25519-verifies `proof.proofValue` (padded base64url) against the
  issuer public key decoded from `issuer.id` (a did:key). `verify` =
  `signature_valid AND not_expired AND not_revoked`.
- `verifyDelegationChain` verifies each JWT's EdDSA signature over the compact
  signing input `b64url(header).b64url(payload)` (unpadded), then checks the
  child's `att` is a subset of the parent's `att`.

## Vector schema

Each entry in `vectors[]`:

```jsonc
{
  "id":   "vc-valid-001",          // stable id
  "kind": "verify_credential",     // canonicalize | did_key_decode | verify_credential | verify_delegation_chain
  "description": "...",            // human-readable intent
  "input": { ... },                // the JSON the port feeds its verifier
  "expected": { ... },             // the booleans/structs the port must produce
  // present where relevant:
  "canonical_bytes_hex": "7b...",  // hex of canonical UTF-8 bytes
  "signature_b64url": "ksv...==",  // padded base64url Ed25519 signature (VC)
  "pubkey_multibase": "z6Mk...",   // did:key body
  "pubkey_raw_hex": "8022..."      // raw 32-byte Ed25519 public key
}
```

Top-level: `issuer_did`, `issuer_pubkey_raw_hex`, `issuer_seed_hex` (the fixed
seed), `attestix_version`, `vector_count`.

## The 7 vectors

| id | kind | asserts |
|---|---|---|
| `canon-001` | canonicalize | byte-identical JCS-style output (NFC, codepoint sort, raw UTF-8, whole-float→int, big int) |
| `didkey-001` | did_key_decode | `0xed01 ‖ raw32` base58btc → 32-byte key round-trip |
| `vc-valid-001` | verify_credential | valid VC ⇒ verify **true** |
| `vc-tampered-001` | verify_credential | one claim byte flipped ⇒ signature invalid ⇒ verify **false** |
| `vc-expired-001` | verify_credential | past `expirationDate` ⇒ not_expired false ⇒ verify **false** (signature still valid) |
| `ucan-chain-valid-001` | verify_delegation_chain | child att subset of parent ⇒ verify **true** |
| `ucan-chain-escalation-002` | verify_delegation_chain | child att NOT a subset (`admin`) ⇒ verify **false** |

## How to run the vectors (port-side pattern)

1. Load `vectors.json`.
2. For each vector, switch on `kind` and call the matching verifier function.
3. Compare every key in `expected` against your output.
4. For `verify_credential` vectors, use a fixed "now" **after** 2021 and
   **before** 2027 (e.g. the `now_reference` in `vc-expired-001`) so the valid
   credential is in-window and the expired one is out-of-window.
5. For `canonicalize`, compare your `hex(canonical_bytes)` to
   `canonical_bytes_hex`. **This is the highest-signal test** — if it passes,
   signatures will verify; if it fails, nothing downstream will.

## Reference: the suite passes the JS path

The committed vectors were independently spot-checked against an Ed25519
verifier built on `@noble/curves`: the JS canonicaliser reproduces every
`canonical_bytes_hex`, the VC signatures verify against the did:key-decoded raw
key, the tampered VC fails, and the UCAN JWT signatures verify with correct
attenuation logic. A JS port therefore passes this suite.

## Regenerating

```bash
pip install attestix==0.4.0     # or use the local dev tree
python spec/verify/v1/generate_vectors.py
```

Output is deterministic (fixed seed + frozen timestamps); a clean run produces
byte-identical `vectors.json`.
