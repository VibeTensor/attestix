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
          <span style={{ marginLeft: "auto" }}>{c.uuid}</span>
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
          <div className="v">HIGH &middot; EU AI Act Article 6(2)</div>
        </div>
        <div className="atx-cert-row">
          <div className="k">Basis</div>
          <div className="v">
            Article 43 third-party conformity &middot; NB-0482 Notified Body
          </div>
        </div>
        <div className="atx-cert-row">
          <div className="k">Issued</div>
          <div className="v">{c.issued}</div>
        </div>
        <div className="atx-cert-row">
          <div className="k">Valid thru</div>
          <div className="v">{c.validThru}</div>
        </div>

        <div className="atx-cert-sig">
          proof.type = Ed25519Signature2020
          <br />
          proofValue = {c.proofValue}&hellip;xqLbFgH2NvQrWsEd
        </div>

        <div className="atx-cert-foot">
          <span>&#9673; anchored &middot; base-l2</span>
          <span>verified &#10003;</span>
        </div>
      </div>

      <style>{`
        .atx-cert {
          position: relative;
          background: var(--atx-panel);
          border: 1px solid var(--atx-line);
          border-radius: var(--atx-r-md);
          padding: 28px;
          font-family: var(--font-mono-atx);
          font-size: 12px;
          line-height: 1.65;
          color: var(--atx-ink);
          box-shadow: var(--atx-shadow-md);
        }
        .atx-cert-head {
          display: flex;
          align-items: center;
          gap: 10px;
          border-bottom: 1px dashed var(--atx-line);
          padding-bottom: 14px;
          margin-bottom: 16px;
          font-size: 10px;
          letter-spacing: 0.18em;
          text-transform: uppercase;
          color: var(--atx-ink-dim);
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
          font-family: var(--font-serif);
          font-size: 13px;
          letter-spacing: 0.06em;
          text-transform: uppercase;
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
          font-family: var(--font-serif);
          font-size: 13px;
          line-height: 1;
          letter-spacing: 0.06em;
        }
        .atx-cert-row {
          display: flex;
          gap: 14px;
        }
        .atx-cert-row .k {
          color: var(--atx-ink-dim);
          min-width: 78px;
          text-transform: uppercase;
          font-size: 10px;
          letter-spacing: 0.1em;
          padding-top: 1px;
        }
        .atx-cert-row .v {
          color: var(--atx-ink);
          word-break: break-all;
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
          border-radius: var(--atx-r-sm);
          color: var(--atx-ok);
          font-size: 11px;
          word-break: break-all;
        }
        .atx-cert-foot {
          display: flex;
          justify-content: space-between;
          margin-top: 16px;
          font-size: 10px;
          color: var(--atx-ink-dim);
          letter-spacing: 0.1em;
          text-transform: uppercase;
        }
      `}</style>
    </>
  );
}
