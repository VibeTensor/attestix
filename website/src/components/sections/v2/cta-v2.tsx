import Link from "next/link";
import { AtxEyebrow } from "@/components/atx/atx-eyebrow";

export function CtaV2() {
  return (
    <section className="border-t border-atx-line-soft bg-atx-bg-sunken py-24">
      <div className="mx-auto flex max-w-[1320px] flex-col items-start gap-10 px-7 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <AtxEyebrow number="10" className="mb-5">
            Next
          </AtxEyebrow>
          <h2 className="font-serif text-[clamp(36px,4.8vw,60px)] leading-[1.05] tracking-[-0.012em] text-atx-ink">
            Compliance{" "}
            <em className="italic text-atx-accent">by construction,</em>
            <br />
            not by hope.
          </h2>
          <p className="mt-5 max-w-[560px] text-[15px] leading-[1.65] text-atx-ink-mid">
            Install Attestix, create your first identity, and issue your first
            Verifiable Credential in under sixty seconds. Open source under
            Apache 2.0.
          </p>
        </div>
        <div className="flex flex-col gap-3 sm:flex-row">
          <Link
            href="/console"
            className="group inline-flex h-10 items-center gap-2 rounded-atx-md bg-atx-accent px-5 text-[13px] font-medium text-[oklch(0.14_0.01_180)] transition-colors hover:bg-atx-accent-deep"
          >
            Open console
            <span className="font-mono-atx transition-transform group-hover:translate-x-0.5">
              &rarr;
            </span>
          </Link>
          <Link
            href="/research"
            className="inline-flex h-10 items-center rounded-atx-md border border-atx-line px-5 text-[13px] font-medium text-atx-ink transition-colors hover:border-atx-ink-dim hover:bg-atx-panel"
          >
            Read the paper
          </Link>
          <Link
            href="/demo-call"
            className="inline-flex h-10 items-center rounded-atx-md border border-atx-line px-5 text-[13px] font-medium text-atx-ink transition-colors hover:border-atx-ink-dim hover:bg-atx-panel"
          >
            Book a demo
          </Link>
        </div>
      </div>
    </section>
  );
}
