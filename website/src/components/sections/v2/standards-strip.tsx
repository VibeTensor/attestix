import { ATX_STANDARDS } from "@/lib/atx-data";

export function StandardsStrip() {
  const items = [...ATX_STANDARDS, ...ATX_STANDARDS];
  return (
    <div
      className="overflow-hidden border-y border-atx-line-soft bg-atx-bg-sunken py-4"
      aria-label="Supported standards"
    >
      <div
        className="atx-marquee flex min-w-max items-center gap-10 whitespace-nowrap font-mono-atx text-[11px] uppercase tracking-[0.1em] text-atx-ink-dim motion-reduce:animate-none"
        style={{
          animation: "atxMarqueeScroll 45s linear infinite",
          willChange: "transform",
        }}
      >
        {items.map((t, i) => (
          <span
            key={`${i}-${t.slice(0, 8)}`}
            className="inline-flex items-center gap-2"
          >
            <span className="inline-block h-1 w-1 rounded-full bg-atx-accent" />
            {t}
          </span>
        ))}
      </div>
    </div>
  );
}
