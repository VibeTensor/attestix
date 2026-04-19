import { ConsoleWorkspace } from "./console-workspace";
import { ConsoleBanner } from "./console-banner";
import { AtxEyebrow } from "@/components/atx/atx-eyebrow";
import { constructMetadata } from "@/lib/utils";

export const metadata = constructMetadata({
  title: "Attestix Console",
  description:
    "Interactive preview of the Attestix console. Agents, credentials, audit trail, anchors. Data is simulated.",
});

export default function ConsolePage() {
  return (
    <section className="mx-auto max-w-[1400px] px-7 py-16">
      <div className="grid items-start gap-10 lg:grid-cols-[1fr_1.2fr]">
        <div>
          <AtxEyebrow>Console</AtxEyebrow>
          <h1 className="mt-3 font-serif text-[clamp(36px,4.8vw,60px)] leading-[1.05] tracking-[-0.012em] text-atx-ink">
            Your fleet of
            <br />
            <em className="italic text-atx-accent">attested agents.</em>
          </h1>
        </div>
        <p className="text-[15px] leading-[1.65] text-atx-ink-mid">
          A live-feel preview of the Attestix workspace. Browse agent
          identities, inspect credentials and delegations, watch the
          hash-chained audit trail append in real time, and create a new
          identity end-to-end. Data is simulated. Run{" "}
          <code className="rounded-atx-xs border border-atx-line-soft bg-atx-bg-sunken px-1.5 py-0.5 font-mono-atx text-[12px] text-atx-accent">
            pip install attestix
          </code>{" "}
          for the real thing.
        </p>
      </div>

      <div className="mt-12">
        <ConsoleBanner />
        <ConsoleWorkspace />
      </div>
    </section>
  );
}
