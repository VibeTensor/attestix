"use client";

import {
  CONSOLE_CREDENTIALS,
  type ConsoleCredential,
} from "@/lib/atx-console-data";
import { AtxIcon } from "@/components/atx/atx-icons";

export function CredentialsPane() {
  return (
    <div>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="font-serif text-[32px] leading-none text-atx-ink">
            Credentials
          </h2>
          <div className="mt-1 font-mono-atx text-[11px] uppercase tracking-[0.06em] text-atx-ink-dim">
            W3C VC Data Model 1.1 / Ed25519Signature2020 /{" "}
            {CONSOLE_CREDENTIALS.length} active
          </div>
        </div>
        <button
          type="button"
          disabled
          title="Demo preview. Runs in the installed package."
          className="inline-flex h-8 cursor-not-allowed items-center gap-1.5 rounded-atx-sm border border-atx-accent/40 bg-atx-accent-soft px-3 font-mono-atx text-[11.5px] font-medium text-atx-accent opacity-60"
        >
          <AtxIcon name="plus" /> issue credential
        </button>
      </div>

      <div className="mt-6 space-y-4">
        {CONSOLE_CREDENTIALS.map((c) => (
          <CredentialCard key={c.id} c={c} />
        ))}
      </div>
    </div>
  );
}

export function CredentialCard({ c }: { c: ConsoleCredential }) {
  return (
    <div className="overflow-hidden rounded-atx-md border border-atx-line-soft bg-atx-panel">
      <div className="flex items-center justify-between border-b border-dashed border-atx-line-soft px-5 py-3 font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-dim">
        <span>
          <span className="text-atx-accent">&#9670;</span>{" "}
          <strong className="font-medium text-atx-accent">{c.type}</strong>
        </span>
        <span>{c.article}</span>
      </div>

      <div className="px-5 py-4">
        <VcRow k="id" v={c.id} />
        <VcRow k="subject" v={c.subject} />
        <VcRow k="issuer" v={`${c.issuer} / ${c.issuerDid}`} />
        <VcRow k="issued" v={c.issued} />
        <VcRow k="expires" v={c.expiry} />
        <div className="grid grid-cols-[90px_1fr] gap-4 py-1.5">
          <div className="font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-faint">
            claims
          </div>
          <div className="overflow-hidden rounded-atx-sm border border-atx-line-soft bg-atx-bg-sunken">
            {Object.entries(c.claims).map(([k, v]) => (
              <div
                key={k}
                className="border-b border-atx-line-soft px-3 py-1.5 font-mono-atx text-[11.5px] last:border-b-0"
              >
                <span className="text-atx-accent">{k}</span>
                <span className="text-atx-ink-dim"> = </span>
                <span className="text-atx-ink">{String(v)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="mx-5 mb-4 rounded-atx-sm border border-atx-line-soft bg-atx-bg-sunken p-3 font-mono-atx text-[11px] text-atx-ok">
        proof.type = Ed25519Signature2020
        <br />
        <span className="break-all">
          proofValue = {c.signature.slice(0, 80)}&hellip;
        </span>
      </div>

      <div className="flex items-center justify-between border-t border-atx-line-soft px-5 py-3 font-mono-atx text-[11px] text-atx-ink-dim">
        <span>
          status <span className="text-atx-ok">{c.status}</span>
        </span>
        <span
          className="flex gap-4 text-atx-ink-faint"
          aria-label="Demo actions, available in the installed package"
        >
          <span>verify signature</span>
          <span>present</span>
          <span>download JSON</span>
        </span>
      </div>
    </div>
  );
}

function VcRow({ k, v }: { k: string; v: string }) {
  return (
    <div className="grid grid-cols-[90px_1fr] gap-4 py-1.5">
      <div className="font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-faint">
        {k}
      </div>
      <div className="break-all font-mono-atx text-[11.5px] text-atx-ink">
        {v}
      </div>
    </div>
  );
}
