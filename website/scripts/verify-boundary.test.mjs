import assert from "node:assert/strict";
import { generateKeyPairSync, sign } from "node:crypto";
import { readFileSync } from "node:fs";
import test from "node:test";
import { canonicalize, verifyCredential } from "@vibetensor/attestix";
import { ModuleKind, ScriptTarget, transpileModule } from "typescript";

// Pages currently pins Node 20, which cannot strip TypeScript natively.
// Compile the actual local implementation so these remain security regressions.
const boundarySource = readFileSync(new URL("../src/lib/credential-boundary.ts", import.meta.url), "utf8");
const { outputText, diagnostics } = transpileModule(boundarySource, {
  fileName: "credential-boundary.ts",
  compilerOptions: { module: ModuleKind.ESNext, target: ScriptTarget.ES2022 },
  reportDiagnostics: true,
});
assert.equal(diagnostics?.length ?? 0, 0, "credential boundary must transpile without diagnostics");
const { credentialBoundary } = await import(`data:text/javascript;base64,${Buffer.from(outputText).toString("base64")}`);

const NOW = Date.parse("2026-10-11T00:00:00Z");
const sample = JSON.parse(readFileSync(new URL("../src/lib/samples/sample-valid-vc.json", import.meta.url), "utf8"));
const clone = () => structuredClone(sample);
const denied = (value) => assert.equal(credentialBoundary(value, NOW).valid, false);

function publicKeyMultibase(publicKey) {
  const alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz";
  const raw = publicKey.export({ format: "der", type: "spki" }).subarray(-32);
  const encoded = Buffer.concat([Buffer.from([0xed, 0x01]), raw]);
  let integer = BigInt(`0x${encoded.toString("hex")}`);
  let key = "";
  while (integer > 0n) { key = alphabet[Number(integer % 58n)] + key; integer /= 58n; }
  return `z${key}`;
}


test("valid did:key sample passes boundary and the actual published SDK", () => {
  assert.equal(credentialBoundary(sample, NOW).valid, true);
  assert.equal(verifyCredential(sample, { now: NOW }).valid, true);
});

test("stated issuer cannot be replaced by an attacker's proof key", () => {
  const alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz";
  const pair = generateKeyPairSync("ed25519");
  const rawKey = pair.publicKey.export({ format: "der", type: "spki" }).subarray(-32);
  const encoded = Buffer.concat([Buffer.from([0xed, 0x01]), rawKey]);
  let integer = BigInt(`0x${encoded.toString("hex")}`);
  let key = "";
  while (integer > 0n) { key = alphabet[Number(integer % 58n)] + key; integer /= 58n; }
  const credential = clone();
  // The attacker signs a document claiming the sample's unrelated issuer.
  const payload = { ...credential };
  delete payload.proof;
  delete payload.credentialStatus;
  credential.proof.verificationMethod = `did:key:z${key}#key-1`;
  credential.proof.proofValue = sign(null, canonicalize(payload), pair.privateKey).toString("base64");
  assert.equal(verifyCredential(credential, { now: NOW }).valid, true, "published 0.2.0 accepts the substituted issuer fixture");
  denied(credential);
});

test("did:web issuer with embedded key cannot bypass trusted resolution", () => {
  const credential = clone();
  credential.issuer.id = "did:web:example.com";
  credential.proof.verificationMethod = `${credential.issuer.id}#key-1`;
  credential.proof.publicKeyMultibase = sample.issuer.id.slice("did:key:".length);
  denied(credential);
});

test("string issuer is supported only when it matches the proof controller", () => {
  const credential = clone();
  credential.issuer = sample.issuer.id;
  assert.equal(credentialBoundary(credential, NOW).valid, true);
  credential.proof.verificationMethod = `${credential.issuer}evil#key-1`;
  denied(credential);
});

test("missing, malformed, fragment-bearing issuers and empty proof fragments fail closed", () => {
  for (const issuer of [null, 12, {}, [], "", "did:key:z0Invalid", `${sample.issuer.id}#key-1`]) {
    const credential = clone(); credential.issuer = issuer; denied(credential);
  }
  for (const method of [undefined, 1, sample.issuer.id, `${sample.issuer.id}#`, `${sample.issuer.id}#key-1#other`]) {
    const credential = clone(); credential.proof.verificationMethod = method; denied(credential);
  }
});

test("expiration must be a finite, complete RFC 3339 calendar timestamp", () => {
  for (const expiry of [null, 0, NaN, Infinity, true, {}, [], "", "Infinity", "2027-05-30", "2027-02-30T00:00:00Z", "2027-13-01T00:00:00Z", "2027-05-30T24:00:00Z", "2027-05-30T00:00:00+99:00"]) {
    const credential = clone(); credential.expirationDate = expiry; denied(credential);
  }
});

test("expired credentials and exact expiration boundary fail", () => {
  const credential = clone();
  credential.expirationDate = "2026-10-11T00:00:00Z";
  denied(credential);
  assert.equal(credentialBoundary(credential, NOW - 1).valid, true);
});

test("optional expiry and valid leap-year and offset timestamps pass", () => {
  const credential = clone(); delete credential.expirationDate;
  assert.equal(credentialBoundary(credential, NOW).valid, true);
  for (const expiry of ["2028-02-29T00:00:00Z", "2027-05-30T02:58:42.816449+00:00"]) {
    credential.expirationDate = expiry;
    assert.equal(credentialBoundary(credential, NOW).valid, true);
  }
});

test("NFC key collisions fail recursively through objects and arrays", () => {
  for (const nest of [(collision) => collision, (collision) => [{ deeper: collision }]]) {
    const credential = clone();
    credential.credentialSubject.details = nest({ "\u00e9": 1, "e\u0301": 2 });
    denied(credential);
  }
});

test("unambiguous decomposed keys pass and non-finite nested numbers fail", () => {
  const credential = clone(); credential.credentialSubject.details = { "e\u0301": 1 };
  assert.equal(credentialBoundary(credential, NOW).valid, true);
  credential.credentialSubject.details = { amount: Infinity };
  denied(credential);
});

test("boundary acceptance does not replace cryptographic verification", () => {
  const credential = clone(); credential.credentialSubject.id = "tampered";
  assert.equal(credentialBoundary(credential, NOW).valid, true);
  assert.equal(verifyCredential(credential, { now: NOW }).valid, false);
});

test("unsupported proof types, purposes, and proof arrays fail closed", () => {
  for (const proof of [[], [sample.proof], { ...sample.proof, type: "OtherProof" }, { ...sample.proof, proofPurpose: "authentication" }]) {
    const credential = clone(); credential.proof = proof; denied(credential);
  }
});

test("embedded key overrides cannot select a key even with a matching issuer controller", () => {
  const attacker = generateKeyPairSync("ed25519");
  const credential = clone();
  const payload = { ...credential }; delete payload.proof; delete payload.credentialStatus;
  credential.proof.proofValue = sign(null, canonicalize(payload), attacker.privateKey).toString("base64");
  for (const field of ["publicKeyMultibase", "publicKeyJwk", "publicKeyJWK", "publicKeyBase58", "publicKeyHex"]) {
    const attempt = structuredClone(credential);
    attempt.proof[field] = field.toLowerCase().includes("jwk")
      ? attacker.publicKey.export({ format: "jwk" })
      : publicKeyMultibase(attacker.publicKey);
    assert.equal(attempt.proof.verificationMethod.split("#")[0], attempt.issuer.id);
    assert.equal(verifyCredential(attempt, { now: NOW }).valid, false, "published did:key verification uses the issuer key, not the embedded override");
    denied(attempt);
  }
});
