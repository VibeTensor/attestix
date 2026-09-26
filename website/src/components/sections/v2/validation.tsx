import { siteConfig } from "@/lib/config";

const WRAP = "mx-auto w-full max-w-[1200px] px-6";
const H2 = "text-[32px] font-medium leading-[1.15] tracking-[-0.8px] text-atx-ink";
const LEAD = "text-[17.5px] leading-[1.6] text-atx-ink-mid";

type Highlight = (typeof siteConfig.highlights)[number];

function displayName(h: Highlight) {
  if ("anonymous" in h && h.anonymous === true) {
    return h.role ?? "Name on file";
  }
  return h.name;
}

function displaySubline(h: Highlight) {
  if ("anonymous" in h && h.anonymous === true) {
    return h.company ?? null;
  }
  return h.role ?? null;
}

export function ValidationSection() {
  return (
    <section id="validation" className="scroll-mt-20 bg-atx-bg py-20">
      <div className={WRAP}>
        <div className="text-center">
          <h2 className={H2}>
            Reviewed by the people who <span className="text-atx-accent">write the rules</span>
          </h2>
          <p className={`mx-auto mt-4 max-w-[760px] ${LEAD}`}>
            Attestix has been reviewed by senior engineers building public
            attestation infrastructure, a European AI-privacy researcher, a
            GenAI governance director, and engineers building adjacent
            systems at enterprise scale. Names are kept on file. Their
            exact words are preserved below.
          </p>
        </div>

        <div className="mt-12 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
          {siteConfig.highlights.map((h) => {
            const subline = displaySubline(h);
            return (
              <figure
                key={h.id}
                className="flex flex-col rounded-2xl border border-atx-line bg-atx-panel/60 p-6 transition-colors duration-200 hover:border-atx-ink-dim"
              >
                <div className="text-[13px] font-medium text-atx-accent">{h.event}</div>
                <blockquote className="mt-4 text-[17px] leading-[1.55] text-atx-ink">
                  &ldquo;{h.text}&rdquo;
                </blockquote>
                <figcaption className="mt-auto border-t border-atx-line-soft pt-5 text-[14px] leading-[1.5]">
                  <div className="mt-1 font-medium text-atx-ink">{displayName(h)}</div>
                  {subline ? <div className="text-atx-ink-mid">{subline}</div> : null}
                  <div className="mt-2 text-[13px] text-atx-ink-dim">{h.venue}</div>
                </figcaption>
              </figure>
            );
          })}
        </div>
      </div>
    </section>
  );
}
