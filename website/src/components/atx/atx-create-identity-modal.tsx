"use client";

import { useEffect, useRef, useState } from "react";

interface Props {
  onClose: () => void;
}

type Stage = "form" | "signing" | "done";

interface Result {
  id: string;
  did: string;
  sig: string;
  name: string;
  issuer: string;
  risk: string;
  caps: string[];
  created: string;
}

function rand16() {
  return Array.from({ length: 16 }, () =>
    "0123456789abcdef"[Math.floor(Math.random() * 16)]
  ).join("");
}
function randMulti(n: number) {
  const alpha =
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
  return Array.from({ length: n }, () =>
    alpha[Math.floor(Math.random() * alpha.length)]
  ).join("");
}

export function AtxCreateIdentityModal({ onClose }: Props) {
  const [name, setName] = useState("");
  const [issuer, setIssuer] = useState("VibeTensor");
  const [risk, setRisk] = useState("high");
  const [caps, setCaps] = useState("data_analysis, reporting");
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [stage, setStage] = useState<Stage>("form");
  const [result, setResult] = useState<Result | null>(null);
  const dialogRef = useRef<HTMLDivElement | null>(null);
  const timerRef = useRef<number | null>(null);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    dialogRef.current?.focus();
    return () => {
      window.removeEventListener("keydown", onKey);
      if (timerRef.current) window.clearTimeout(timerRef.current);
    };
  }, [onClose]);

  const submit = () => {
    const e: Record<string, string> = {};
    if (!name.trim()) e.name = "Display name required";
    else if (name.length < 3) e.name = "Too short";
    else if (!/^[a-zA-Z0-9_\-\s]+$/.test(name))
      e.name = "Alphanumeric, dashes, underscores only";
    if (!issuer.trim()) e.issuer = "Issuer required";
    if (!caps.trim()) e.caps = "At least one capability";
    setErrors(e);
    if (Object.keys(e).length) return;
    setStage("signing");
    if (timerRef.current) window.clearTimeout(timerRef.current);
    timerRef.current = window.setTimeout(() => {
      setResult({
        id: `attestix:${rand16()}`,
        did: `did:key:z6Mk${randMulti(44)}`,
        sig: `z${randMulti(88)}`,
        name: name.trim(),
        issuer,
        risk,
        caps: caps
          .split(",")
          .map((c) => c.trim())
          .filter(Boolean),
        created: new Date().toISOString().replace(/\.\d+Z$/, "Z"),
      });
      setStage("done");
    }, 1400);
  };

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm"
      onClick={onClose}
      role="presentation"
    >
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="atx-create-identity-title"
        tabIndex={-1}
        className="w-full max-w-[560px] overflow-hidden rounded-atx-md border border-atx-line bg-atx-panel shadow-[var(--atx-shadow-md)] focus:outline-none"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-start justify-between border-b border-atx-line-soft px-7 py-5">
          <div>
            <div className="font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-dim">
              &sect; attestix / identity / create
            </div>
            <h3
              id="atx-create-identity-title"
              className="mt-1 font-serif text-[22px] leading-tight text-atx-ink"
            >
              New agent identity
            </h3>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close"
            className="font-mono-atx text-[20px] leading-none text-atx-ink-dim hover:text-atx-ink"
          >
            &times;
          </button>
        </div>

        {stage === "form" && (
          <>
            <div className="space-y-4 px-7 py-6">
              <Field label="Display name" error={errors.name}>
                <input
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. quarterly-analyst-v2"
                  className="atx-input"
                />
              </Field>
              <div className="grid gap-4 sm:grid-cols-2">
                <Field label="Issuer" error={errors.issuer}>
                  <input
                    value={issuer}
                    onChange={(e) => setIssuer(e.target.value)}
                    className="atx-input"
                  />
                </Field>
                <Field label="Risk tier">
                  <select
                    value={risk}
                    onChange={(e) => setRisk(e.target.value)}
                    className="atx-input"
                  >
                    <option value="min">Minimal</option>
                    <option value="lim">Limited</option>
                    <option value="high">High-risk (Article 6)</option>
                    <option value="pro">Prohibited-adj. (Article 5)</option>
                  </select>
                </Field>
              </div>
              <Field
                label="Capabilities (comma-separated)"
                error={errors.caps}
              >
                <input
                  value={caps}
                  onChange={(e) => setCaps(e.target.value)}
                  className="atx-input"
                />
              </Field>
              {risk === "high" && (
                <div className="rounded-atx-sm border border-atx-warn/40 bg-atx-warn/[0.08] p-3 font-mono-atx text-[12px] text-atx-warn">
                  HIGH-RISK systems require third-party conformity assessment
                  under Article 43. Self-assessment will be blocked.
                </div>
              )}
            </div>
            <div className="flex items-center justify-between border-t border-atx-line-soft px-7 py-4">
              <span className="font-mono-atx text-[11px] text-atx-ink-dim">
                Preview values. Real signing runs locally via pip install.
              </span>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={onClose}
                  className="inline-flex h-8 items-center rounded-atx-sm border border-atx-line px-3 font-mono-atx text-[11.5px] text-atx-ink"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={submit}
                  className="inline-flex h-8 items-center gap-1.5 rounded-atx-sm bg-atx-accent px-3 font-mono-atx text-[11.5px] font-medium text-[oklch(0.14_0.01_180)] hover:bg-atx-accent-deep"
                >
                  Sign &amp; create &rarr;
                </button>
              </div>
            </div>
          </>
        )}

        {stage === "signing" && (
          <div className="space-y-2 px-7 py-14 text-center font-mono-atx text-[12px] text-atx-ink-dim">
            <div className="text-atx-accent">
              &#9670; simulating Ed25519 keypair generation...
            </div>
            <div>&#9670; deriving did:key from mock public key</div>
            <div>&#9670; signing UAIT payload...</div>
            <div className="text-atx-ink-faint">
              &#9671; registering in local store
            </div>
          </div>
        )}

        {stage === "done" && result && (
          <>
            <div className="px-7 py-6">
              <div className="rounded-atx-sm border border-atx-ok/40 bg-atx-ok/[0.08] p-3 font-mono-atx text-[11px] uppercase tracking-[0.12em] text-atx-ok">
                &#10003; identity created / signature verified
              </div>
              <div className="mt-5 space-y-3 text-[13px]">
                <KV k="Agent ID" v={result.id} />
                <KV k="DID" v={result.did} mono />
                <KV k="Issuer" v={result.issuer} />
                <KV k="Created" v={result.created} />
                <KV
                  k="Proof"
                  v={`Ed25519Signature2020 / ${result.sig.slice(0, 32)}...`}
                  mono
                  accent
                />
              </div>
            </div>
            <div className="flex items-center justify-between border-t border-atx-line-soft px-7 py-4">
              <span className="font-mono-atx text-[11px] text-atx-ink-dim">
                Next: record training data (Article 10)
              </span>
              <button
                type="button"
                onClick={onClose}
                className="inline-flex h-8 items-center rounded-atx-sm bg-atx-accent px-3 font-mono-atx text-[11.5px] font-medium text-[oklch(0.14_0.01_180)] hover:bg-atx-accent-deep"
              >
                Done
              </button>
            </div>
          </>
        )}
      </div>

      <style>{`
        .atx-input {
          width: 100%;
          height: 36px;
          padding: 0 12px;
          border: 1px solid var(--atx-line);
          border-radius: var(--atx-r-sm);
          background: var(--atx-bg-sunken);
          color: var(--atx-ink);
          font-family: var(--font-mono-atx);
          font-size: 12.5px;
          outline: none;
          transition: border-color .15s;
        }
        .atx-input:focus {
          border-color: var(--atx-accent);
        }
      `}</style>
    </div>
  );
}

function Field({
  label,
  error,
  children,
}: {
  label: string;
  error?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="space-y-1.5">
      <label className="block font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-dim">
        {label}
      </label>
      {children}
      {error ? (
        <div className="font-mono-atx text-[11px] text-atx-err">
          &times; {error}
        </div>
      ) : null}
    </div>
  );
}

function KV({
  k,
  v,
  mono,
  accent,
}: {
  k: string;
  v: string;
  mono?: boolean;
  accent?: boolean;
}) {
  return (
    <div className="grid grid-cols-[110px_1fr] items-baseline gap-3">
      <div className="font-mono-atx text-[10.5px] uppercase tracking-[0.12em] text-atx-ink-faint">
        {k}
      </div>
      <div
        className={`break-all ${mono ? "font-mono-atx text-[11.5px]" : ""} ${accent ? "text-atx-ok" : "text-atx-ink"}`}
      >
        {v}
      </div>
    </div>
  );
}
