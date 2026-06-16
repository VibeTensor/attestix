// Embedded "try it" fixtures for the /verify portal.
//
// SAMPLE_VALID_VC is a genuine, Ed25519-signed W3C Verifiable Credential issued
// by the Python `attestix` core (issuer DID
// did:key:z6Mkija7eQS9kNrvh1kAp7PJFgPEznFpBdDm825vugSQxdW7, name VibeTensor). It
// verifies green under the same @vibetensor/attestix verifier the page imports.
//
// SAMPLE_TAMPERED_VC is the identical credential with one signed field mutated
// (credentialSubject.risk_level "high" -> "low") while the original proofValue
// is left in place. Because the signature no longer covers the body, the
// verifier reports INVALID, demonstrating tamper detection.
//
// Both fixtures are validated in CI-style by scripts/verify-samples.mjs, which
// imports the exact same JSON and runs verifyCredential against it.

import sampleValid from "./samples/sample-valid-vc.json";
import sampleTampered from "./samples/sample-tampered-vc.json";

export const SAMPLE_VALID_VC: Record<string, unknown> = sampleValid;
export const SAMPLE_TAMPERED_VC: Record<string, unknown> = sampleTampered;

export const SAMPLE_VALID_VC_TEXT = JSON.stringify(sampleValid, null, 2);
export const SAMPLE_TAMPERED_VC_TEXT = JSON.stringify(sampleTampered, null, 2);
