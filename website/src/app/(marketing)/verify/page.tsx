import { AtxEyebrow } from "@/components/atx/atx-eyebrow";
import { constructMetadata } from "@/lib/utils";
import Link from "next/link";
import { VerifyClient } from "./verify-client";

export const metadata = constructMetadata({
  title: "Verify a credential",
  description:
    "Verify an Attestix-issued W3C Verifiable Credential in your browser. Ed25519 over the SDK canonical form, did:key resolution  -  fully client-side. Your credential is never uploaded.",
});

const NPM_PKG = "attestix";

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
              The credential is processed locally by this page and is not posted to an Attestix verification backend. Page delivery and browser extensions have separate trust considerations. This page uses the published attestix 0.4.2 SDK and local input boundaries; it does not establish issuer trust or legal validity.
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
          Strips the mutable{" "}
          <code className="font-mono-atx text-[12.5px] text-atx-ink">proof</code>{" "}
          and{" "}
          <code className="font-mono-atx text-[12.5px] text-atx-ink">
            credentialStatus
          </code>{" "}
          fields, then serialises the remainder using the Attestix SDK
          canonical form (sorted keys and NFC normalization). This profile
          is not strict RFC 8785 JCS, which does not normalize Unicode.
        </li>
        <li>
          Resolves the issuer&apos;s public key from the{" "}
          <code className="font-mono-atx text-[12.5px] text-atx-ink">did:key</code>{" "}
          embedded in the proof&apos;s{" "}
          <code className="font-mono-atx text-[12.5px] text-atx-ink">
            verificationMethod
          </code>{" "}
          after requiring its controller to match the stated issuer. The key is
          self-certifying; no domain resolver or network lookup is used.
        </li>
        <li>
          Verifies the Ed25519 signature over those canonical bytes via{" "}
          <code className="font-mono-atx text-[12.5px] text-atx-ink">
            @noble/curves
          </code>
          , checks the supported proof profile and unambiguous JSON keys, and
          compares any valid expiration timestamp against your browser clock.
        </li>
      </ol>
            <p className="mt-4 text-[15px] leading-[1.7] text-atx-ink-mid">
              Cryptographic checks use published attestix 0.4.2 within the documented Attestix canonical profile. Language-specific validation boundaries differ. Shared fixtures do not establish arbitrary cross-language equivalence, identical trust or fresh revocation policy.
            </p>
          </div>
        </div>
      </section>

      {/* ----- Honest limitations ----------------------------------------- */}
      <section className="bg-atx-bg py-20">
        <div className={WRAP}>
          <h2 className={`${H2} text-center`}>
            What this page checks, and what remains separate
          </h2>
          <div className="mx-auto mt-12 grid max-w-[1040px] gap-5 md:grid-cols-2">
            <div className="rounded-2xl border border-atx-ok/30 bg-atx-ok/[0.05] p-6">
              <h3 className="text-[19px] font-semibold tracking-[-0.48px] text-atx-ok">
                Supported local checks
              </h3>
              <ul className="mt-4 space-y-3 text-[15px] leading-[1.6] text-atx-ink-mid">
            <li>
              <strong className="text-atx-ink">Signature authenticity.</strong>{" "}
              The credential was signed by the private key matching the issuer
              DID. Changes to signed fields break the signature; mutable
              credentialStatus and proof metadata are excluded.
            </li>
            <li>
              <strong className="text-atx-ink">Supported local checks.</strong>{" "}
              The stated did:key issuer matches the proof controller, supported
              proof fields pass local checks, and normalized JSON keys are
              unambiguous. This is not a complete W3C conformance assessment.
            </li>
            <li>
              <strong className="text-atx-ink">Expiration.</strong>{" "}
              If expirationDate is present, it must be a valid RFC 3339 calendar
              timestamp later than your browser clock. An absent expiration is
              allowed. This check does not enforce issuanceDate or establish
              that the credential is currently authorized for use.
            </li>
          </ul>
            </div>
            <div className="rounded-2xl border border-atx-warn/30 bg-atx-warn/[0.05] p-6">
              <h3 className="text-[19px] font-semibold tracking-[-0.48px] text-atx-warn">
                Not proven offline
              </h3>
              <ul className="mt-4 space-y-3 text-[15px] leading-[1.6] text-atx-ink-mid">
            <li>
              <strong className="text-atx-ink">Live revocation.</strong>{" "}
              Offline mode reads only the{" "}
              <code className="font-mono-atx text-[12px] text-atx-ink">
                credentialStatus
              </code>{" "}
              embedded in the document. Fresh revocation status requires a separate trusted status check, which this page does not perform. A signature can be valid and the credential still revoked.
            </li>
            <li>
              <strong className="text-atx-ink">Issuer identity.</strong>{" "}
              A <code className="font-mono-atx text-[12px] text-atx-ink">did:key</code>{" "}
              is self-certifying  -  it proves control of a key, not who controls
              it. This offline verifier supports only did:key. did:web requires
              a trusted resolver and is rejected here. Establish out-of-band
              that the DID belongs to the party
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
              A valid result supports the tested signature and local input checks. It does not establish issuer authority, claim truth, fresh revocation status, replay policy, legal conformity or certification.
            </p>
          </div>
        </div>
      </section>
    </>
  );
}
