import { AtxEyebrow } from "@/components/atx/atx-eyebrow";
import { constructMetadata } from "@/lib/utils";
import Link from "next/link";
import { VerifyClient } from "./verify-client";

export const metadata = constructMetadata({
  title: "Verify a credential",
  description:
    "Verify an Attestix-issued W3C Verifiable Credential in your browser. Ed25519 over JCS-canonical form, did:key resolution — fully client-side. Your credential is never uploaded.",
});

const NPM_PKG = "@vibetensor/attestix";

export default function VerifyPage() {
  return (
    <section className="mx-auto max-w-[1080px] px-7 py-24">
      <AtxEyebrow>Verification portal</AtxEyebrow>
      <h1 className="mt-3 font-serif text-[clamp(36px,4.8vw,60px)] leading-[1.05] tracking-[-0.012em] text-atx-ink">
        Verify an Attestix credential —
        <br />
        <em className="italic text-atx-accent">in your browser, nothing uploaded.</em>
      </h1>
      <p className="mt-6 max-w-[760px] text-[15px] leading-[1.65] text-atx-ink-mid">
        Paste a W3C Verifiable Credential, or drop a{" "}
        <code className="font-mono-atx text-[13px] text-atx-ink">.json</code> file.
        The signature is checked entirely on this page using the published{" "}
        <a
          href={`https://www.npmjs.com/package/${NPM_PKG}`}
          target="_blank"
          rel="noopener noreferrer"
          className="font-mono-atx text-[13px] text-atx-accent hover:underline"
        >
          {NPM_PKG}
        </a>{" "}
        verifier. No installation, no account, no backend — your credential never
        leaves your machine. That is a stronger trust story than a server-side
        verifier: there is nothing to log, nothing to intercept, and nothing to
        trust beyond the open-source code running in your own browser tab.
      </p>

      {/* Interactive verifier (client component) -------------------------- */}
      <VerifyClient />

      {/* ----- How this works --------------------------------------------- */}
      <h2 className="mt-20 font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-dim">
        01 / How this works
      </h2>
      <p className="mt-3 max-w-[760px] text-[14px] leading-[1.7] text-atx-ink-mid">
        Attestix credentials carry an{" "}
        <code className="font-mono-atx text-[12.5px] text-atx-ink">
          Ed25519Signature2020
        </code>{" "}
        proof. To verify one, the page:
      </p>
      <ol className="mt-4 max-w-[760px] list-decimal space-y-2 pl-5 text-[14px] leading-[1.7] text-atx-ink-mid">
        <li>
          Strips the mutable{" "}
          <code className="font-mono-atx text-[12.5px] text-atx-ink">proof</code>{" "}
          and{" "}
          <code className="font-mono-atx text-[12.5px] text-atx-ink">
            credentialStatus
          </code>{" "}
          fields, then re-serialises the remainder to its JCS-canonical byte form
          (sorted keys, tightest separators, NFC-normalised).
        </li>
        <li>
          Resolves the issuer&apos;s public key from the{" "}
          <code className="font-mono-atx text-[12.5px] text-atx-ink">did:key</code>{" "}
          embedded in the proof&apos;s{" "}
          <code className="font-mono-atx text-[12.5px] text-atx-ink">
            verificationMethod
          </code>{" "}
          (the key is self-certifying — it is the public key, multibase-encoded).
        </li>
        <li>
          Verifies the Ed25519 signature over those canonical bytes via{" "}
          <code className="font-mono-atx text-[12.5px] text-atx-ink">
            @noble/curves
          </code>
          , checks the credential structure, and compares the validity window
          against your browser&apos;s clock.
        </li>
      </ol>
      <p className="mt-4 max-w-[760px] text-[14px] leading-[1.7] text-atx-ink-mid">
        Every step runs in a WebAssembly-free, pure-JavaScript crypto path inside
        your tab. The same verifier ships in the{" "}
        <a
          href={`https://www.npmjs.com/package/${NPM_PKG}`}
          target="_blank"
          rel="noopener noreferrer"
          className="text-atx-accent hover:underline"
        >
          {NPM_PKG}
        </a>{" "}
        npm package and is byte-compatible with the Python{" "}
        <a
          href="https://pypi.org/project/attestix/"
          target="_blank"
          rel="noopener noreferrer"
          className="text-atx-accent hover:underline"
        >
          attestix
        </a>{" "}
        core. The canonicalisation rules are documented in the{" "}
        <Link href="/spec/bundle/v1" className="text-atx-accent hover:underline">
          bundle wire-format spec
        </Link>
        .
      </p>

      {/* ----- Honest limitations ----------------------------------------- */}
      <h2 className="mt-16 font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-dim">
        02 / What offline verification proves — and what it doesn&apos;t
      </h2>
      <div className="mt-6 grid gap-5 md:grid-cols-2">
        <div className="rounded-atx-md border border-atx-ok/30 bg-atx-ok/[0.06] p-5">
          <div className="font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ok">
            Proven offline
          </div>
          <ul className="mt-3 space-y-2 text-[13.5px] leading-[1.65] text-atx-ink-mid">
            <li>
              <strong className="text-atx-ink">Signature authenticity.</strong>{" "}
              The credential was signed by the private key matching the issuer
              DID, and not modified since — any tampered field breaks the
              signature.
            </li>
            <li>
              <strong className="text-atx-ink">Structural validity.</strong>{" "}
              The document is a well-formed W3C VC with the required fields.
            </li>
            <li>
              <strong className="text-atx-ink">Validity window.</strong>{" "}
              Whether the credential is within its{" "}
              <code className="font-mono-atx text-[12px] text-atx-ink">
                issuanceDate
              </code>
              –
              <code className="font-mono-atx text-[12px] text-atx-ink">
                expirationDate
              </code>{" "}
              range, compared against your clock at view time.
            </li>
          </ul>
        </div>
        <div className="rounded-atx-md border border-atx-warn/40 bg-atx-warn/[0.06] p-5">
          <div className="font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-warn">
            NOT proven offline
          </div>
          <ul className="mt-3 space-y-2 text-[13.5px] leading-[1.65] text-atx-ink-mid">
            <li>
              <strong className="text-atx-ink">Live revocation.</strong>{" "}
              Offline mode reads only the{" "}
              <code className="font-mono-atx text-[12px] text-atx-ink">
                credentialStatus
              </code>{" "}
              embedded in the document. Checking the issuer&apos;s status list in
              real time is a hosted lookup (an{" "}
              <Link href="/pricing" className="text-atx-accent hover:underline">
                Attestix Cloud
              </Link>{" "}
              feature). A signature can be valid and the credential still revoked.
            </li>
            <li>
              <strong className="text-atx-ink">Issuer identity.</strong>{" "}
              A <code className="font-mono-atx text-[12px] text-atx-ink">did:key</code>{" "}
              is self-certifying — it proves control of a key, not who controls
              it. <code className="font-mono-atx text-[12px] text-atx-ink">did:web</code>{" "}
              binds a DID to a domain; <code className="font-mono-atx text-[12px] text-atx-ink">did:key</code>{" "}
              does not. Establish out-of-band that the DID belongs to the party
              you expect.
            </li>
            <li>
              <strong className="text-atx-ink">By-id lookup.</strong>{" "}
              Resolving a credential from just its id needs the hosted API; this
              static page has no store to resolve against.
            </li>
          </ul>
        </div>
      </div>

      {/* ----- See also ---------------------------------------------------- */}
      <div className="mt-14 rounded-atx-md border border-atx-line-soft bg-atx-bg-sunken p-6">
        <div className="font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-dim">
          See also
        </div>
        <div className="mt-2 flex flex-wrap gap-4 text-[13.5px]">
          <a
            href={`https://www.npmjs.com/package/${NPM_PKG}`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-atx-accent hover:underline"
          >
            {NPM_PKG} (npm verifier)
          </a>
          <Link href="/spec/bundle/v1" className="text-atx-accent hover:underline">
            Bundle wire format v1
          </Link>
          <Link href="/security" className="text-atx-accent hover:underline">
            Security
          </Link>
          <Link href="/docs/guides/offline-verify" className="text-atx-accent hover:underline">
            Offline verification docs
          </Link>
        </div>
        <p className="mt-4 text-[12.5px] leading-[1.6] text-atx-ink-dim">
          Attestix is evidence tooling, not a guarantor of compliance. A green
          result proves the credential&apos;s signature and structure — it does
          not by itself establish that the issuer was authorised to make the
          claims, nor that the subject is compliant. Maintained by{" "}
          <a
            href="https://vibetensor.com"
            target="_blank"
            rel="noopener noreferrer"
            className="text-atx-accent hover:underline"
          >
            VibeTensor
          </a>
          .
        </p>
      </div>
    </section>
  );
}
