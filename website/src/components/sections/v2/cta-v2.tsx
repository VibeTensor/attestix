import Link from "next/link";
import { ArrowRight } from "lucide-react";

// Also rendered at the foot of blog posts.
export function CtaV2() {
  return (
    <section className="relative overflow-hidden border-t border-atx-line-soft bg-atx-bg-elev py-20">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            "radial-gradient(720px 100% at 50% 100%, color-mix(in oklch, var(--color-atx-accent) 11%, transparent), transparent 100%)",
        }}
      />
      <div className="relative mx-auto w-full max-w-[1200px] px-6 text-center">
        <h2 className="text-[clamp(32px,4.4vw,44px)] font-medium leading-[1.12] tracking-[-1.1px] text-atx-ink [text-wrap:balance]">
          Compliance <span className="text-atx-accent">by construction,</span> not by hope.
        </h2>
        <p className="mx-auto mt-5 max-w-[560px] text-[17.5px] leading-[1.6] text-atx-ink-mid">
          Install Attestix, create your first identity, and issue your first
          Verifiable Credential in under sixty seconds. Open source under
          Apache 2.0.
        </p>
        <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
          <Link
            href="/console"
            className="group inline-flex items-center gap-2 rounded-full bg-atx-accent px-6 py-3 text-[15px] font-medium text-[oklch(0.14_0.01_180)] transition-colors duration-200 hover:bg-atx-accent-deep"
          >
            Open console
            <ArrowRight className="h-4 w-4 transition-transform duration-200 group-hover:translate-x-0.5" />
          </Link>
          <Link
            href="/research"
            className="inline-flex items-center rounded-full border border-atx-line px-6 py-3 text-[15px] font-medium text-atx-ink-mid transition-colors duration-200 hover:border-atx-ink-dim hover:text-atx-ink"
          >
            Read the paper
          </Link>
          <Link
            href="/demo-call"
            className="inline-flex items-center rounded-full border border-atx-line px-6 py-3 text-[15px] font-medium text-atx-ink-mid transition-colors duration-200 hover:border-atx-ink-dim hover:text-atx-ink"
          >
            Book a demo
          </Link>
        </div>
      </div>
    </section>
  );
}
