import { ATX_HERO_STATS } from "@/lib/atx-data";

export function HeroStats() {
  return (
    <div className="mt-16 grid grid-cols-2 gap-px border-y border-atx-line-soft bg-atx-line-soft md:grid-cols-4">
      {ATX_HERO_STATS.map((s) => (
        <div
          key={s.k}
          className="flex flex-col gap-1 bg-atx-bg px-6 py-6"
        >
          <div className="font-serif text-[40px] italic leading-none text-atx-accent">
            {s.v}
          </div>
          <div className="font-mono-atx text-[11px] uppercase tracking-[0.12em] text-atx-ink-dim">
            {s.k}
          </div>
        </div>
      ))}
    </div>
  );
}
