"use client";

import {
  SAMPLE_TAMPERED_VC_TEXT,
  SAMPLE_VALID_VC_TEXT,
} from "@/lib/verify-samples";
import {
  canonicalize,
  verifyCredential,
  type JsonValue,
} from "@vibetensor/attestix";
import { useCallback, useEffect, useRef, useState } from "react";

// ---------------------------------------------------------------------------
// Everything below runs ENTIRELY in the visitor's browser. There is no fetch(),
// no API call, no telemetry. The pasted credential never leaves the machine.
// The only crypto is the published @vibetensor/attestix verifier (Ed25519 over
// JCS-canonical bytes via @noble/curves) — we do not reimplement any of it.
// ---------------------------------------------------------------------------

type Outcome = "valid" | "invalid" | "malformed";

interface CredentialChecks {
  structure_valid: boolean;
  signature_valid: boolean;
  not_expired: boolean;
  not_revoked: boolean;
}

interface Report {
  outcome: Outcome;
  reason?: string;
  checks?: CredentialChecks;
  issuer?: string;
  issuerName?: string;
  subject?: string;
  type?: string[];
  verificationMethod?: string;
  didMethod?: string;
  issuanceDate?: string;
  expirationDate?: string;
  expired?: boolean;
  subjectClaims?: Array<{ key: string; value: string }>;
  status?: { type?: string; revoked?: boolean; id?: string };
  canonicalHash?: string;
}

const SUPPORTED_DID_METHODS = ["did:key", "did:web"];

function didMethodOf(did?: string): string | undefined {
  if (!did) return undefined;
  const parts = did.split(":");
  if (parts.length >= 2 && parts[0] === "did") return `did:${parts[1]}`;
  return undefined;
}

async function sha256Hex(bytes: Uint8Array): Promise<string> {
  const digest = await crypto.subtle.digest("SHA-256", bytes as BufferSource);
  return Array.from(new Uint8Array(digest))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

function stringifyClaim(value: unknown): string {
  if (value === null) return "null";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

export function VerifyClient() {
  const [text, setText] = useState("");
  const [deepLinkId, setDeepLinkId] = useState<string | undefined>(undefined);
  const [report, setReport] = useState<Report | null>(null);
  const [dragging, setDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const runVerify = useCallback(async (raw: string) => {
    const trimmed = raw.trim();
    if (!trimmed) {
      setReport(null);
      return;
    }

    let vc: Record<string, unknown>;
    try {
      vc = JSON.parse(trimmed);
    } catch {
      setReport({
        outcome: "malformed",
        reason:
          "This doesn't look like valid JSON. Paste the full Verifiable Credential, including the surrounding { } and the proof block.",
      });
      return;
    }

    if (typeof vc !== "object" || vc === null || Array.isArray(vc)) {
      setReport({
        outcome: "malformed",
        reason:
          "This JSON is not a credential object. A W3C VC is a JSON object with a credentialSubject and a proof.",
      });
      return;
    }

    const proof = vc.proof as Record<string, unknown> | undefined;
    if (!proof) {
      setReport({
        outcome: "malformed",
        reason:
          "No signature present — this credential has no `proof` block, so there is nothing to verify. An unsigned document carries no cryptographic assurance.",
      });
      return;
    }

    const verificationMethod =
      typeof proof.verificationMethod === "string"
        ? proof.verificationMethod
        : undefined;
    const issuerObj = vc.issuer as Record<string, unknown> | string | undefined;
    const issuerId =
      typeof issuerObj === "string"
        ? issuerObj
        : (issuerObj?.id as string | undefined);
    const issuerDidForMethod =
      verificationMethod?.split("#")[0] ?? issuerId;
    const didMethod = didMethodOf(issuerDidForMethod);

    if (didMethod && !SUPPORTED_DID_METHODS.includes(didMethod)) {
      setReport({
        outcome: "malformed",
        reason: `This verifier supports ${SUPPORTED_DID_METHODS.join(
          " and "
        )}; this credential's issuer uses ${didMethod}, which cannot be resolved client-side here.`,
        issuer: issuerId,
        verificationMethod,
        didMethod,
      });
      return;
    }

    let canonicalHash: string | undefined;
    try {
      // Hash the canonical bytes over the SIGNED field set (proof and the
      // mutable credentialStatus removed) — the exact bytes the Ed25519
      // signature covers. Lets a technical user cross-check independently.
      const signedView: Record<string, unknown> = { ...vc };
      delete signedView.proof;
      delete signedView.credentialStatus;
      canonicalHash = await sha256Hex(
        canonicalize(signedView as unknown as JsonValue)
      );
    } catch {
      // Non-fatal: canonicalisation can throw on values JCS rejects; the
      // verifier below will surface the real reason.
    }

    let result: ReturnType<typeof verifyCredential>;
    try {
      result = verifyCredential(vc);
    } catch (err) {
      setReport({
        outcome: "malformed",
        reason:
          err instanceof Error
            ? err.message
            : "The verifier could not process this document.",
        canonicalHash,
      });
      return;
    }

    const subjectObj = vc.credentialSubject as
      | Record<string, unknown>
      | undefined;
    const subjectClaims = subjectObj
      ? Object.entries(subjectObj)
          .filter(([k]) => k !== "id")
          .map(([key, value]) => ({ key, value: stringifyClaim(value) }))
      : [];

    const status = vc.credentialStatus as Record<string, unknown> | undefined;
    const expirationDate =
      typeof vc.expirationDate === "string" ? vc.expirationDate : undefined;
    const expired = expirationDate
      ? new Date(expirationDate).getTime() < Date.now()
      : false;

    setReport({
      outcome: result.valid ? "valid" : "invalid",
      reason: result.reason,
      checks: result.checks as unknown as CredentialChecks,
      issuer: result.issuer ?? issuerId,
      issuerName:
        typeof issuerObj === "object"
          ? (issuerObj?.name as string | undefined)
          : undefined,
      subject: result.subject ?? (subjectObj?.id as string | undefined),
      type: result.type,
      verificationMethod,
      didMethod,
      issuanceDate:
        typeof vc.issuanceDate === "string" ? vc.issuanceDate : undefined,
      expirationDate,
      expired,
      subjectClaims,
      status: status
        ? {
            type: status.type as string | undefined,
            revoked:
              typeof status.revoked === "boolean"
                ? (status.revoked as boolean)
                : undefined,
            id: status.id as string | undefined,
          }
        : undefined,
      canonicalHash,
    });
  }, []);

  // Honest handling of the /verify/<id> deep link: we cannot resolve a
  // credential by id without the hosted API, so we never fake it — we surface
  // the id and steer the visitor to the offline paste box.
  const [showDeepLinkNotice, setShowDeepLinkNotice] = useState(false);
  useEffect(() => {
    // Read the by-id deep link client-side. Supports the query form
    // /verify?id=<id> (the shipped form — query strings work in a static
    // export without per-id pre-rendering). We never resolve the id; we only
    // surface it and steer the visitor to the offline paste box.
    if (typeof window === "undefined") return;
    const id = new URLSearchParams(window.location.search).get("id");
    if (id) {
      setDeepLinkId(id);
      setShowDeepLinkNotice(true);
    }
  }, []);

  const onFile = useCallback(
    (file: File) => {
      const reader = new FileReader();
      reader.onload = () => {
        const content = String(reader.result ?? "");
        setText(content);
        void runVerify(content);
      };
      reader.readAsText(file);
    },
    [runVerify]
  );

  return (
    <div className="mt-10">
      {showDeepLinkNotice && deepLinkId ? (
        <div className="mb-8 rounded-atx-md border border-atx-warn/40 bg-atx-warn/[0.06] p-5">
          <div className="font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-warn">
            By-id lookup
          </div>
          <p className="mt-2 text-[13.5px] leading-[1.65] text-atx-ink-mid">
            You followed a link for credential{" "}
            <code className="font-mono-atx text-[12px] text-atx-ink">
              {deepLinkId}
            </code>
            . Resolving a credential by id requires a hosted lookup (an{" "}
            <a
              href="/pricing"
              className="text-atx-accent hover:underline"
            >
              Attestix Cloud
            </a>{" "}
            workspace). This page is a static, zero-backend verifier, so there is
            nothing to fetch the credential from. Paste the full credential JSON
            below to verify it offline instead — the result is identical, and
            nothing is uploaded.
          </p>
        </div>
      ) : null}

      {/* Input area --------------------------------------------------------- */}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          const file = e.dataTransfer.files?.[0];
          if (file) onFile(file);
        }}
        className={`rounded-atx-md border ${
          dragging
            ? "border-atx-accent bg-atx-accent/[0.05]"
            : "border-atx-line-soft bg-atx-bg-sunken"
        } p-4 transition-colors`}
      >
        <label
          htmlFor="vc-input"
          className="font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-dim"
        >
          Paste credential JSON · or drop a .json file
        </label>
        <textarea
          id="vc-input"
          value={text}
          onChange={(e) => setText(e.target.value)}
          spellCheck={false}
          placeholder='{ "@context": [...], "type": ["VerifiableCredential", ...], "issuer": {...}, "credentialSubject": {...}, "proof": {...} }'
          className="mt-3 h-64 w-full resize-y rounded-atx-sm border border-atx-line-soft bg-atx-panel px-4 py-3 font-mono-atx text-[12.5px] leading-[1.55] text-atx-ink outline-none focus:border-atx-accent"
        />
        <div className="mt-3 flex flex-wrap items-center gap-3">
          <button
            type="button"
            onClick={() => void runVerify(text)}
            className="rounded-atx-sm bg-atx-accent px-5 py-2 font-mono-atx text-[12px] font-medium uppercase tracking-[0.1em] text-atx-bg transition-opacity hover:opacity-90"
          >
            Verify
          </button>
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="rounded-atx-sm border border-atx-line-soft px-4 py-2 font-mono-atx text-[12px] uppercase tracking-[0.1em] text-atx-ink-mid hover:border-atx-accent hover:text-atx-ink"
          >
            Upload .json
          </button>
          <button
            type="button"
            onClick={() => {
              setText(SAMPLE_VALID_VC_TEXT);
              void runVerify(SAMPLE_VALID_VC_TEXT);
            }}
            className="rounded-atx-sm border border-atx-line-soft px-4 py-2 font-mono-atx text-[12px] uppercase tracking-[0.1em] text-atx-ink-mid hover:border-atx-accent hover:text-atx-ink"
          >
            Load a sample
          </button>
          <button
            type="button"
            onClick={() => {
              setText(SAMPLE_TAMPERED_VC_TEXT);
              void runVerify(SAMPLE_TAMPERED_VC_TEXT);
            }}
            className="rounded-atx-sm border border-atx-line-soft px-4 py-2 font-mono-atx text-[12px] uppercase tracking-[0.1em] text-atx-ink-mid hover:border-atx-warn hover:text-atx-warn"
          >
            Load a tampered sample
          </button>
          {text ? (
            <button
              type="button"
              onClick={() => {
                setText("");
                setReport(null);
              }}
              className="rounded-atx-sm px-3 py-2 font-mono-atx text-[12px] uppercase tracking-[0.1em] text-atx-ink-dim hover:text-atx-ink"
            >
              Clear
            </button>
          ) : null}
          <input
            ref={fileInputRef}
            type="file"
            accept=".json,application/json"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) onFile(file);
              e.target.value = "";
            }}
          />
        </div>
      </div>

      {/* Results ------------------------------------------------------------ */}
      {report ? <ResultPanel report={report} /> : null}
    </div>
  );
}

function Badge({
  pass,
  pendingLabel,
  passLabel,
  failLabel,
  state,
}: {
  pass?: boolean;
  pendingLabel?: string;
  passLabel: string;
  failLabel: string;
  state?: "pending";
}) {
  if (state === "pending") {
    return (
      <span className="rounded-atx-xs border border-atx-line-soft px-2 py-0.5 font-mono-atx text-[10.5px] uppercase tracking-[0.12em] text-atx-ink-dim">
        {pendingLabel}
      </span>
    );
  }
  return (
    <span
      className={`rounded-atx-xs border px-2 py-0.5 font-mono-atx text-[10.5px] uppercase tracking-[0.12em] ${
        pass
          ? "border-atx-ok/40 bg-atx-ok/[0.08] text-atx-ok"
          : "border-atx-err/40 bg-atx-err/[0.08] text-atx-err"
      }`}
    >
      {pass ? passLabel : failLabel}
    </span>
  );
}

function Row({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col gap-1 border-b border-atx-line-soft px-5 py-3.5 sm:flex-row sm:items-start sm:gap-6">
      <div className="w-44 shrink-0 font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-faint">
        {label}
      </div>
      <div className="min-w-0 flex-1 break-words text-[13px] leading-[1.6] text-atx-ink-mid">
        {children}
      </div>
    </div>
  );
}

function ResultPanel({ report }: { report: Report }) {
  const tone =
    report.outcome === "valid"
      ? {
          border: "border-atx-ok/40",
          bg: "bg-atx-ok/[0.05]",
          text: "text-atx-ok",
          label: "Valid",
        }
      : report.outcome === "invalid"
        ? {
            border: "border-atx-err/40",
            bg: "bg-atx-err/[0.05]",
            text: "text-atx-err",
            label: "Invalid",
          }
        : {
            border: "border-atx-warn/40",
            bg: "bg-atx-warn/[0.05]",
            text: "text-atx-warn",
            label: "Malformed",
          };

  return (
    <div className={`mt-8 overflow-hidden rounded-atx-md border ${tone.border}`}>
      <div className={`flex items-center gap-3 ${tone.bg} px-5 py-4`}>
        <span
          className={`font-serif text-[26px] leading-none ${tone.text}`}
          aria-hidden
        >
          {report.outcome === "valid"
            ? "✓"
            : report.outcome === "invalid"
              ? "✗"
              : "!"}
        </span>
        <div>
          <div
            className={`font-mono-atx text-[11px] uppercase tracking-[0.16em] ${tone.text}`}
          >
            {tone.label}
          </div>
          <div className="mt-0.5 text-[13px] text-atx-ink-mid">
            {report.outcome === "valid"
              ? "The signature is authentic and the credential is well-formed and within its validity window."
              : report.outcome === "invalid"
                ? report.reason ?? "Verification failed."
                : report.reason ?? "This document could not be parsed as a credential."}
          </div>
        </div>
      </div>

      {report.outcome !== "malformed" ? (
        <div className="bg-atx-panel">
          {report.checks ? (
            <Row label="Signature">
              <span className="inline-flex flex-wrap items-center gap-3">
                <Badge
                  pass={report.checks.signature_valid}
                  passLabel="Ed25519 verified"
                  failLabel="Signature failed"
                />
                {report.verificationMethod ? (
                  <code className="font-mono-atx text-[11.5px] text-atx-ink-dim">
                    {report.verificationMethod}
                  </code>
                ) : null}
              </span>
            </Row>
          ) : null}

          {report.checks ? (
            <Row label="Structure">
              <Badge
                pass={report.checks.structure_valid}
                passLabel="Well-formed VC"
                failLabel="Malformed"
              />
            </Row>
          ) : null}

          <Row label="Issuer">
            <div className="flex flex-col gap-0.5">
              {report.issuerName ? (
                <span className="text-atx-ink">{report.issuerName}</span>
              ) : null}
              <code className="font-mono-atx text-[11.5px] text-atx-ink-dim">
                {report.issuer ?? "—"}
              </code>
            </div>
          </Row>

          <Row label="Subject">
            <div className="flex flex-col gap-1">
              <code className="font-mono-atx text-[11.5px] text-atx-ink-dim">
                {report.subject ?? "—"}
              </code>
              {report.subjectClaims && report.subjectClaims.length > 0 ? (
                <div className="mt-1 flex flex-col gap-1">
                  {report.subjectClaims.map((c) => (
                    <div key={c.key} className="flex gap-2 text-[12.5px]">
                      <span className="font-mono-atx text-atx-ink-faint">
                        {c.key}
                      </span>
                      <span className="text-atx-ink-mid">{c.value}</span>
                    </div>
                  ))}
                </div>
              ) : null}
            </div>
          </Row>

          {report.type && report.type.length > 0 ? (
            <Row label="Type">
              <span className="font-mono-atx text-[12px] text-atx-ink-mid">
                {report.type.join(", ")}
              </span>
            </Row>
          ) : null}

          <Row label="Validity window">
            <div className="flex flex-col gap-1">
              <div className="flex flex-wrap items-center gap-3">
                <span className="font-mono-atx text-[12px] text-atx-ink-dim">
                  issued {report.issuanceDate ?? "—"}
                </span>
                {report.expirationDate ? (
                  <span className="font-mono-atx text-[12px] text-atx-ink-dim">
                    expires {report.expirationDate}
                  </span>
                ) : null}
              </div>
              {report.expirationDate ? (
                <Badge
                  pass={!report.expired}
                  passLabel="Within validity window"
                  failLabel="Expired"
                />
              ) : (
                <span className="font-mono-atx text-[11.5px] text-atx-ink-faint">
                  no expirationDate declared
                </span>
              )}
            </div>
          </Row>

          <Row label="Revocation">
            {report.status?.revoked === true ? (
              <Badge pass={false} passLabel="" failLabel="Declared revoked" />
            ) : report.status ? (
              <div className="flex flex-col gap-1">
                <Badge state="pending" pendingLabel="Status list not checked (offline)" passLabel="" failLabel="" />
                <span className="text-[12.5px] leading-[1.55] text-atx-ink-mid">
                  This credential declares a{" "}
                  <code className="font-mono-atx text-[11.5px] text-atx-ink">
                    {report.status.type ?? "credentialStatus"}
                  </code>{" "}
                  endpoint{report.status.id ? " " : ""}
                  {report.status.id ? (
                    <code className="font-mono-atx text-[11.5px] text-atx-ink-dim">
                      {report.status.id}
                    </code>
                  ) : null}
                  . Its <code className="font-mono-atx text-[11.5px] text-atx-ink">revoked</code>{" "}
                  flag reads{" "}
                  <code className="font-mono-atx text-[11.5px] text-atx-ink">
                    {String(report.status.revoked)}
                  </code>{" "}
                  in the document, but a live revocation check against the
                  issuer&apos;s status list is a hosted lookup and is not
                  performed in this offline verifier.
                </span>
              </div>
            ) : (
              <span className="text-[12.5px] text-atx-ink-mid">
                No <code className="font-mono-atx text-[11.5px] text-atx-ink">credentialStatus</code>{" "}
                present — this credential carries no revocation endpoint to check.
              </span>
            )}
          </Row>

          {report.canonicalHash ? (
            <Row label="Canonical form">
              <div className="flex flex-col gap-1">
                <span className="text-[12px] text-atx-ink-mid">
                  SHA-256 of the JCS-canonical signed bytes (proof and
                  credentialStatus removed):
                </span>
                <code className="break-all font-mono-atx text-[11.5px] text-atx-accent">
                  {report.canonicalHash}
                </code>
              </div>
            </Row>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
