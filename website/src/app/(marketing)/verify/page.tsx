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

const WRAP = "mx-auto w-full max-w-[1200px] px-6";
const H2 = "text-[32px] font-medium leading-[1.15] tracking-[-0.8px] text-atx-ink";
const CODE = "font-mono-atx text-[13px] text-atx-ink";
const LINK =
  "text-atx-ink underline decoration-atx-line underline-offset-4 transition-colors duration-200 hover:text-atx-accent hover:decoration-atx-accent";

export default function VerifyPage() {
  return (
    <>
      {/* ----- Hero -------------------------------------------------------- */}
      <section className="bg-atx-bg px-6 pb-20 pt-16 md:pt-20">
        <div className="mx-auto max-w-[860px] text-center">
          <AtxEyebrow>Verification portal</AtxEyebrow>
          <h1 className="mt-3 text-[clamp(34px,5vw,52px)] font-normal leading-[1.09] tracking-[-0.03em] text-atx-ink [text-wrap:balance]">
            Verify an Attestix credential,{" "}
            <span className="text-atx-accent">in your browser, nothing uploaded.</span>
          </h1>
          <p className="mx-auto mt-5 max-w-[640px] text-[17.5px] leading-[1.6] text-atx-ink-mid [text-wrap:balance]">
            Paste a W3C Verifiable Credential, or drop a{" "}
            <code className={CODE}>.json</code> file.
            The signature is checked entirely on this page using the published{" "}
            <a
              href={`https://www.npmjs.com/package/${NPM_PKG}`}
              target="_blank"
              rel="noopener noreferrer"
              className={`font-mono-atx text-[14px] ${LINK}`}
            >
              {NPM_PKG}
            </a>{" "}
            verifier. No installation, no account, no backend — your credential never
            leaves your machine. That is a stronger trust story than a server-side
            verifier: there is nothing to log, nothing to intercept, and nothing to
            trust beyond the open-source code running in your own browser tab.
          </p>
        </div>

        {/* Interactive verifier (client component) -------------------------- */}
        <div className="mx-auto max-w-[1080px]">
          <VerifyClient />
        </div>
      </section>

      {/* ----- How this works --------------------------------------------- */}
      <section className="bg-atx-bg-elev py-20">
        <div className={WRAP}>
          <div className="mx-auto max-w-[720px]">
            <h2 className={H2}>How this works</h2>
            <p className="mt-4 text-[15px] leading-[1.7] text-atx-ink-mid">
              Attestix credentials carry an{" "}
              <code className={CODE}>Ed25519Signature2020</code>{" "}
              proof. To verify one, the page:
            </p>
            <ol className="mt-4 list-decimal space-y-3 pl-5 text-[15px] leading-[1.7] text-atx-ink-mid marker:text-atx-ink-dim">
              <li>
                Strips the mutable <code className={CODE}>proof</code> and{" "}
                <code className={CODE}>credentialStatus</code>{" "}
                fields, then re-serialises the remainder to its JCS-canonical byte form
                (sorted keys, tightest separators, NFC-normalised).
              </li>
              <li>
                Resolves the issuer&apos;s public key from the{" "}
                <code className={CODE}>did:key</code>{" "}
                embedded in the proof&apos;s{" "}
                <code className={CODE}>verificationMethod</code>{" "}
                (the key is self-certifying — it is the public key, multibase-encoded).
              </li>
              <li>
                Verifies the Ed25519 signature over those canonical bytes via{" "}
                <code className={CODE}>@noble/curves</code>
                , checks the credential structure, and compares the validity window
                against your browser&apos;s clock.
              </li>
            </ol>
            <p className="mt-4 text-[15px] leading-[1.7] text-atx-ink-mid">
              Every step runs in a WebAssembly-free, pure-JavaScript crypto path inside
              your tab. The same verifier ships in the{" "}
              <a
                href={`https://www.npmjs.com/package/${NPM_PKG}`}
                target="_blank"
                rel="noopener noreferrer"
                className={LINK}
              >
                {NPM_PKG}
              </a>{" "}
              npm package and is byte-compatible with the Python{" "}
              <a
                href="https://pypi.org/project/attestix/"
                target="_blank"
                rel="noopener noreferrer"
                className={LINK}
              >
                attestix
              </a>{" "}
              core. The canonicalisation rules are documented in the{" "}
              <Link href="/spec/bundle/v1" className={LINK}>
                bundle wire-format spec
              </Link>
              .
            </p>
          </div>
        </div>
      </section>

      {/* ----- Honest limitations ----------------------------------------- */}
      <section className="bg-atx-bg py-20">
        <div className={WRAP}>
          <h2 className={`${H2} text-center`}>
            What offline verification proves, and what it doesn&apos;t
          </h2>
          <div className="mx-auto mt-12 grid max-w-[1040px] gap-5 md:grid-cols-2">
            <div className="rounded-2xl border border-atx-ok/30 bg-atx-ok/[0.05] p-6">
              <h3 className="text-[19px] font-semibold tracking-[-0.48px] text-atx-ok">
                Proven offline
              </h3>
              <ul className="mt-4 space-y-3 text-[15px] leading-[1.6] text-atx-ink-mid">
                <li>
                  <strong className="font-medium text-atx-ink">Signature authenticity.</strong>{" "}
                  The credential was signed by the private key matching the issuer
                  DID, and not modified since — any tampered field breaks the
                  signature.
                </li>
                <li>
                  <strong className="font-medium text-atx-ink">Structural validity.</strong>{" "}
                  The document is a well-formed W3C VC with the required fields.
                </li>
                <li>
                  <strong className="font-medium text-atx-ink">Validity window.</strong>{" "}
                  Whether the credential is within its{" "}
                  <code className={CODE}>issuanceDate</code>
                  –
                  <code className={CODE}>expirationDate</code>{" "}
                  range, compared against your clock at view time.
                </li>
              </ul>
            </div>
            <div className="rounded-2xl border border-atx-warn/30 bg-atx-warn/[0.05] p-6">
              <h3 className="text-[19px] font-semibold tracking-[-0.48px] text-atx-warn">
                Not proven offline
              </h3>
              <ul className="mt-4 space-y-3 text-[15px] leading-[1.6] text-atx-ink-mid">
                <li>
                  <strong className="font-medium text-atx-ink">Live revocation.</strong>{" "}
                  Offline mode reads only the{" "}
                  <code className={CODE}>credentialStatus</code>{" "}
                  embedded in the document. Checking the issuer&apos;s status list in
                  real time is a hosted lookup (an{" "}
                  <Link href="/pricing" className={LINK}>
                    Attestix Cloud
                  </Link>{" "}
                  feature). A signature can be valid and the credential still revoked.
                </li>
                <li>
                  <strong className="font-medium text-atx-ink">Issuer identity.</strong>{" "}
                  A <code className={CODE}>did:key</code>{" "}
                  is self-certifying — it proves control of a key, not who controls
                  it. <code className={CODE}>did:web</code>{" "}
                  binds a DID to a domain; <code className={CODE}>did:key</code>{" "}
                  does not. Establish out-of-band that the DID belongs to the party
                  you expect.
                </li>
                <li>
                  <strong className="font-medium text-atx-ink">By-id lookup.</strong>{" "}
                  Resolving a credential from just its id needs the hosted API; this
                  static page has no store to resolve against.
                </li>
              </ul>
            </div>
          </div>

          {/* ----- See also -------------------------------------------------- */}
          <div className="mx-auto mt-10 max-w-[1040px] rounded-2xl border border-atx-line bg-atx-panel/60 p-6">
            <p className="text-[14px] font-medium text-atx-ink">See also</p>
            <div className="mt-3 flex flex-wrap gap-x-6 gap-y-2 text-[15px]">
              <a
                href={`https://www.npmjs.com/package/${NPM_PKG}`}
                target="_blank"
                rel="noopener noreferrer"
                className={LINK}
              >
                {NPM_PKG} (npm verifier)
              </a>
              <Link href="/spec/bundle/v1" className={LINK}>
                Bundle wire format v1
              </Link>
              <Link href="/security" className={LINK}>
                Security
              </Link>
              <Link href="/docs/guides/offline-verify" className={LINK}>
                Offline verification docs
              </Link>
            </div>
            <p className="mt-5 text-[13px] leading-[1.6] text-atx-ink-dim">
              Attestix is evidence tooling, not a guarantor of compliance. A green
              result proves the credential&apos;s signature and structure — it does
              not by itself establish that the issuer was authorised to make the
              claims, nor that the subject is compliant. Maintained by{" "}
              <a
                href="https://vibetensor.com"
                target="_blank"
                rel="noopener noreferrer"
                className="underline decoration-atx-line underline-offset-4 transition-colors duration-200 hover:text-atx-ink"
              >
                VibeTensor
              </a>
              .
            </p>
          </div>
        </div>
      </section>
    </>
  );
}
