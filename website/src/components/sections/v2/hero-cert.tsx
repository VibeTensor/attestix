import { ATX_CERT_SAMPLE } from "@/lib/atx-data";

export function HeroCert() {
  const c = ATX_CERT_SAMPLE;
  return (
    <>
      <div className="atx-cert">
        <div className="atx-cert-head">
          <span>&#9670;</span>
          <span>
            <strong>Declaration of Conformity</strong> &middot; Annex V
          </span>
          <span className="atx-cert-uuid">{c.uuid}</span>
        </div>

        <div className="atx-cert-seal">
          <span>A</span>
        </div>

        <div className="atx-cert-row">
          <div className="k">Agent</div>
          <div className="v">{c.agentName}</div>
        </div>
        <div className="atx-cert-row">
          <div className="k">ID</div>
          <div className="v">
            <span className="hl">attestix:</span>
            {c.agentId.replace("attestix:", "")}
          </div>
        </div>
        <div className="atx-cert-row">
          <div className="k">DID</div>
          <div className="v">{c.did}</div>
        </div>
        <div className="atx-cert-row">
          <div className="k">Issuer</div>
          <div className="v">
            {c.issuerName} &middot; {c.issuerDid}
          </div>
        </div>

        <div className="atx-cert-sep" />

        <div className="atx-cert-row">
          <div className="k">Risk tier</div>
          <div className="v">{c.riskTier}</div>
        </div>
        <div className="atx-cert-row">
          <div className="k">Basis</div>
          <div className="v">{c.basis}</div>
        </div>
        <div className="atx-cert-row">
          <div className="k">Sample</div>
          <div className="v">illustrative &middot; not a real certificate</div>
        </div>
        <div className="atx-cert-row">
          <div className="k">Issued</div>
          <div className="v">{c.issued}</div>
        </div>
        <div className="atx-cert-row">
          <div className="k">Valid through</div>
          <div className="v">{c.validThru}</div>
        </div>

        <div className="atx-cert-sig">
          proof.type = Ed25519Signature2020
          <br />
          proofValue = {c.proofValue.slice(0, 32)}&hellip;
          {c.proofValue.slice(-16)}
        </div>

        <div className="atx-cert-foot">
          <span>&#9673; Anchored &middot; <span className="mono">base-l2</span> testnet</span>
          <span className="ok">Verified &#10003;</span>
        </div>
      </div>

      <style>{`
        .atx-cert {
          position: relative;
          background: var(--atx-panel);
          border: 1px solid var(--atx-line);
          border-radius: 16px;
          padding: 24px;
          font-family: var(--font-mono-atx);
          font-size: 12px;
          line-height: 1.65;
          color: var(--atx-ink);
          box-shadow: var(--atx-shadow-md);
        }
        .atx-cert-head {
          display: flex;
          flex-wrap: wrap; /* the seal padding must not widen the hero on phones */
          align-items: center;
          gap: 10px;
          border-bottom: 1px dashed var(--atx-line);
          padding-bottom: 14px;
          padding-right: 64px; /* clear the 56px absolute seal */
          margin-bottom: 16px;
          font-family: var(--font-sans);
          font-size: 13px;
          color: var(--atx-ink-dim);
        }
        .atx-cert-uuid {
          margin-left: auto;
          font-family: var(--font-mono-atx);
          font-size: 11px;
          overflow-wrap: anywhere;
        }
        .atx-cert-head strong {
          color: var(--atx-accent);
          font-weight: 500;
        }
        .atx-cert-seal {
          position: absolute;
          top: 22px;
          right: 22px;
          width: 56px;
          height: 56px;
          border: 1.5px solid var(--atx-accent);
          border-radius: 50%;
          display: grid;
          place-items: center;
          color: var(--atx-accent);
          font-family: var(--font-sans);
          font-size: 15px;
          font-weight: 500;
        }
        .atx-cert-seal::before {
          content: "";
          position: absolute;
          inset: 3px;
          border: 1px dashed var(--atx-accent);
          border-radius: 50%;
          opacity: 0.55;
        }
        .atx-cert-seal span {
          line-height: 1;
        }
        .atx-cert-row {
          display: flex;
          gap: 14px;
        }
        .atx-cert-row .k {
          color: var(--atx-ink-dim);
          min-width: 92px;
          font-family: var(--font-sans);
          font-size: 13px;
        }
        .atx-cert-row .v {
          color: var(--atx-ink);
          /* break long DIDs only when they overflow; prose wraps at spaces */
          overflow-wrap: anywhere;
        }
        .atx-cert-row .v .hl {
          color: var(--atx-accent);
        }
        .atx-cert-sep {
          height: 1px;
          background: var(--atx-line-soft);
          margin: 12px 0;
        }
        .atx-cert-sig {
          margin-top: 18px;
          padding: 12px;
          background: var(--atx-bg-sunken);
          border: 1px solid var(--atx-line-soft);
          border-radius: 12px;
          color: var(--atx-ok);
          font-size: 11px;
          word-break: break-all;
        }
        .atx-cert-foot {
          display: flex;
          justify-content: space-between;
          flex-wrap: wrap;
          gap: 8px;
          margin-top: 16px;
          font-family: var(--font-sans);
          font-size: 13px;
          color: var(--atx-ink-dim);
        }
        .atx-cert-foot .mono {
          font-family: var(--font-mono-atx);
          font-size: 12px;
        }
        .atx-cert-foot .ok {
          color: var(--atx-ok);
        }
      `}</style>
    </>
  );
}
