import Link from "next/link";
import type { Metadata } from "next";
import { AtxEyebrow } from "@/components/atx/atx-eyebrow";

export const metadata: Metadata = {
  title: "Demos moved / Attestix Console",
  description: "The Attestix demos have moved to the interactive console.",
  alternates: {
    canonical: "/console",
  },
};

export default function DemoRedirectPage() {
  return (
    <section className="mx-auto max-w-[1080px] px-7 py-24">
      <noscript>
        <meta httpEquiv="refresh" content="0;url=/console" />
      </noscript>
      <AtxEyebrow>Demos moved</AtxEyebrow>
      <h1 className="mt-3 font-serif text-[clamp(36px,4.8vw,60px)] leading-[1.05] tracking-[-0.012em] text-atx-ink">
        The playground is now
        <br />
        the <em className="italic text-atx-accent">full console.</em>
      </h1>
      <p className="mt-6 max-w-[640px] text-[15px] leading-[1.65] text-atx-ink-mid">
        The individual demo widgets have been rolled into the interactive
        Attestix console at <code className="rounded-atx-xs border border-atx-line-soft bg-atx-bg-sunken px-1.5 py-0.5 font-mono-atx text-[12px] text-atx-accent">/console</code>. You are being redirected now. If the
        redirect does not fire, use the link below.
      </p>
      <div className="mt-8 flex flex-wrap gap-3">
        <Link
          href="/console"
          className="inline-flex h-10 items-center gap-2 rounded-atx-md bg-atx-accent px-5 text-[13px] font-medium text-[oklch(0.14_0.01_180)] transition-colors hover:bg-atx-accent-deep"
        >
          Go to the console &rarr;
        </Link>
        <Link
          href="/"
          className="inline-flex h-10 items-center rounded-atx-md border border-atx-line px-5 text-[13px] font-medium text-atx-ink transition-colors hover:border-atx-ink-dim hover:bg-atx-panel"
        >
          Home
        </Link>
      </div>

      <div className="mt-16 rounded-atx-md border border-atx-line-soft bg-atx-panel p-6">
        <div className="font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-dim">
          Single-purpose widgets still live at
        </div>
        <ul className="mt-3 grid gap-2 font-mono-atx text-[12.5px]">
          <li>
            <Link
              href="/demo/compliance-checker"
              className="text-atx-accent hover:underline"
            >
              /demo/compliance-checker
            </Link>
            <span className="text-atx-ink-dim"> / EU AI Act risk classifier</span>
          </li>
          <li>
            <Link
              href="/demo/fine-calculator"
              className="text-atx-accent hover:underline"
            >
              /demo/fine-calculator
            </Link>
            <span className="text-atx-ink-dim"> / potential fine by revenue</span>
          </li>
          <li>
            <Link
              href="/demo/identity-explorer"
              className="text-atx-accent hover:underline"
            >
              /demo/identity-explorer
            </Link>
            <span className="text-atx-ink-dim"> / sample agent identity</span>
          </li>
          <li>
            <Link
              href="/demo/reputation-dashboard"
              className="text-atx-accent hover:underline"
            >
              /demo/reputation-dashboard
            </Link>
            <span className="text-atx-ink-dim"> / reputation scoring demo</span>
          </li>
        </ul>
      </div>
      <script
        dangerouslySetInnerHTML={{
          __html: `setTimeout(function(){ window.location.replace('/console'); }, 50);`,
        }}
      />
    </section>
  );
}
