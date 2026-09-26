import { ATX_STANDARDS } from "@/lib/atx-data";

export function StandardsStrip() {
  return (
    <div
      className="border-y border-atx-line-soft bg-atx-bg-elev py-6"
      aria-label="Supported standards"
    >
      <ul className="mx-auto flex w-full max-w-[1200px] flex-wrap items-center justify-center gap-x-7 gap-y-2.5 px-6 text-[13px] text-atx-ink-dim">
        {ATX_STANDARDS.map((t) => (
          <li key={t} className="inline-flex items-center gap-2">
            <span aria-hidden className="inline-block h-1 w-1 rounded-full bg-atx-accent" />
            {t}
          </li>
        ))}
      </ul>
    </div>
  );
}
