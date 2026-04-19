import { AtxEyebrow } from "@/components/atx/atx-eyebrow";
import { siteConfig } from "@/lib/config";

type Highlight = (typeof siteConfig.highlights)[number];

function displayName(h: Highlight) {
  return "anonymous" in h && h.anonymous === true
    ? "Name on file"
    : h.name;
}

export function ValidationSection() {
  return (
    <section id="validation" className="border-t border-atx-line-soft py-24">
      <div className="mx-auto max-w-[1320px] px-7">
        <div className="grid items-start gap-10 lg:grid-cols-[1fr_1.2fr]">
          <div>
            <AtxEyebrow number="05">Correspondence</AtxEyebrow>
            <h2 className="mt-3 font-serif text-[clamp(28px,3.2vw,40px)] leading-[1.15] tracking-[-0.01em] text-atx-ink">
              Reviewed by
              <br />
              the people who
              <br />
              write the rules.
            </h2>
          </div>
          <p className="text-[15px] leading-[1.65] text-atx-ink-mid">
            Attestix has been reviewed by an Ethereum founding member and
            founder of the Ethereum Attestation Service, an INRIA PRIVATICS
            researcher, a GenAI governance director, and senior engineers
            building adjacent infrastructure at enterprise scale. Their exact
            words are preserved below. Full correspondence on file.
          </p>
        </div>

        <div className="mt-14 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
          {siteConfig.highlights.map((h) => (
            <figure
              key={h.id}
              className="flex flex-col rounded-atx-md border border-atx-line-soft bg-atx-panel p-7"
            >
              <div className="font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-faint">
                {h.event}
              </div>
              <blockquote className="mt-5 font-serif text-[22px] leading-[1.3] text-atx-ink">
                &ldquo;{h.text}&rdquo;
              </blockquote>
              <figcaption className="mt-auto pt-6 text-[13px] leading-[1.5]">
                <div className="font-medium text-atx-ink">
                  {displayName(h)}
                </div>
                {h.role ? (
                  <div className="text-atx-ink-mid">{h.role}</div>
                ) : null}
                {h.company ? (
                  <div className="text-atx-ink-dim">{h.company}</div>
                ) : null}
                <div className="mt-3 font-mono-atx text-[10.5px] uppercase tracking-[0.12em] text-atx-ink-faint">
                  {h.venue}
                </div>
              </figcaption>
            </figure>
          ))}
        </div>
      </div>
    </section>
  );
}
