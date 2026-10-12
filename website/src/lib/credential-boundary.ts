type BoundaryResult =
  | { valid: true; issuer: string; verificationMethod: string }
  | { valid: false; reason: string };

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function expirationTime(value: unknown): number | undefined {
  if (typeof value !== "string") return undefined;
  const match = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.\d{1,9})?(Z|[+-]\d{2}:\d{2})$/.exec(value);
  if (!match) return undefined;
  const [, yearText, monthText, dayText, hourText, minuteText, secondText, zone] = match;
  const year = Number(yearText);
  const month = Number(monthText);
  const day = Number(dayText);
  const leap = year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0);
  const days = [31, leap ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
  if (month < 1 || month > 12 || day < 1 || day > days[month - 1] ||
      Number(hourText) > 23 || Number(minuteText) > 59 || Number(secondText) > 59 ||
      (zone !== "Z" && (Number(zone.slice(1, 3)) > 23 || Number(zone.slice(4)) > 59))) {
    return undefined;
  }
  const time = Date.parse(value);
  return Number.isFinite(time) ? time : undefined;
}

// The published verifier normalizes JSON keys. Ambiguous normalized keys must
// fail before canonicalization, and a proof key must identify the stated issuer.
export function credentialBoundary(value: unknown, now = Date.now()): BoundaryResult {
  const reject = (reason: string): BoundaryResult => ({ valid: false, reason });
  if (!isRecord(value) || !Number.isFinite(now)) return reject("Malformed credential or verification time.");
  const pending: Array<{ value: unknown; depth: number }> = [{ value, depth: 0 }];
  let visited = 0;
  while (pending.length > 0) {
    const entry = pending.pop()!;
    if (++visited > 100_000 || entry.depth > 64) return reject("Credential nesting or size exceeds the offline verification limit.");
    if (typeof entry.value === "number" && !Number.isFinite(entry.value)) return reject("Non-finite JSON numbers are not supported.");
    if (Array.isArray(entry.value)) {
      for (const child of entry.value) pending.push({ value: child, depth: entry.depth + 1 });
    } else if (isRecord(entry.value)) {
      const keys = new Set<string>();
      for (const [key, child] of Object.entries(entry.value)) {
        const normalized = key.normalize("NFC");
        if (keys.has(normalized)) return reject("Credential contains colliding NFC-normalized JSON keys.");
        keys.add(normalized);
        pending.push({ value: child, depth: entry.depth + 1 });
      }
    }
  }
  const issuer = typeof value.issuer === "string"
    ? value.issuer
    : isRecord(value.issuer) && Object.hasOwn(value.issuer, "id") ? value.issuer.id : undefined;
  if (typeof issuer !== "string" || !/^did:key:z[1-9A-HJ-NP-Za-km-z]+$/.test(issuer)) {
    return reject("This offline verifier requires a did:key issuer. did:web requires a trusted resolver and is not supported here.");
  }
  if (!isRecord(value.proof)) return reject("Credential must contain a single proof object.");
  if (["publicKeyMultibase", "publicKeyJwk", "publicKeyJWK", "publicKeyBase58", "publicKeyHex"].some((key) => Object.hasOwn(value.proof as Record<string, unknown>, key))) {
    return reject("Embedded proof keys are not supported. The verification key must come from the stated did:key issuer.");
  }
  if (value.proof.type !== "Ed25519Signature2020" || value.proof.proofPurpose !== "assertionMethod") {
    return reject("This verifier supports Ed25519Signature2020 assertionMethod proofs only.");
  }
  const verificationMethod = value.proof.verificationMethod;
  if (typeof verificationMethod !== "string" ||
      !verificationMethod.startsWith(`${issuer}#`) ||
      !/^[A-Za-z0-9._:-]+$/.test(verificationMethod.slice(issuer.length + 1))) {
    return reject("Proof verificationMethod must identify the credential's stated issuer and a non-empty key fragment.");
  }
  if (Object.hasOwn(value, "expirationDate")) {
    const time = expirationTime(value.expirationDate);
    if (time === undefined) return reject("expirationDate must be a finite RFC 3339 timestamp with a valid calendar date and timezone.");
    if (time <= now) return reject("Credential has expired.");
  }
  return { valid: true, issuer, verificationMethod };
}
