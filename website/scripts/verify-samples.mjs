// Standalone validation harness for the /verify portal embedded samples.
//
// Proves the two embedded fixtures behave exactly as the UI claims:
//   - sample-valid-vc.json    -> verifyCredential(...).valid === true
//   - sample-tampered-vc.json -> verifyCredential(...).valid === false
//
// Run:  node scripts/verify-samples.mjs
//
// It imports the SAME JSON fixtures the browser page embeds and the SAME
// @vibetensor/attestix verifier the page calls, so a green result here is the
// same green result a visitor sees in the portal.

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import { verifyCredential } from "@vibetensor/attestix";

const here = dirname(fileURLToPath(import.meta.url));
const load = (name) =>
  JSON.parse(readFileSync(resolve(here, "..", "src", "lib", "samples", name), "utf-8"));

const validVc = load("sample-valid-vc.json");
const tamperedVc = load("sample-tampered-vc.json");

let failures = 0;

function check(label, vc, expectValid) {
  const result = verifyCredential(vc);
  const ok = result.valid === expectValid;
  if (!ok) failures += 1;
  console.log(`${ok ? "PASS" : "FAIL"}  ${label}`);
  console.log(`      valid=${result.valid} expected=${expectValid}`);
  console.log(`      reason=${result.reason ?? "(none)"}`);
  console.log(
    `      checks=${JSON.stringify(result.checks)} issuer=${result.issuer ?? "?"}`
  );
}

check("valid sample -> valid", validVc, true);
check("tampered sample -> invalid", tamperedVc, false);

if (failures > 0) {
  console.error(`\n${failures} check(s) failed`);
  process.exit(1);
}
console.log("\nAll sample checks passed.");
