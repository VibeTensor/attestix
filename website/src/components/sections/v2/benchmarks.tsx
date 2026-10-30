import { AtxEyebrow } from "@/components/atx/atx-eyebrow";

interface Bench {
  label: string;
  value: string;
  unit: string;
  detail: string;
}

const BENCHES: Bench[] = [
  {
    label: "Ed25519 sign + verify",
    value: "Pending",
    unit: "release evidence",
    detail: "Installed-wheel comparison with raw samples and environment metadata.",
  },
  {
    label: "Crypto import",
    value: "Pending",
    unit: "release evidence",
    detail: "Fresh-process crypto import; this does not measure MCP readiness.",
  },
  {
    label: "JSON sign + verify",
    value: "Pending",
    unit: "release evidence",
    detail: "Custom Attestix canonical JSON and memory-only signing keys.",
  },
  {
    label: "CLI help startup",
    value: "Pending",
    unit: "release evidence",
    detail: "Installed console entry point, when both releases pass offline gates.",
  },
];

export function BenchmarksSection() {
  return (
    <section id="benchmarks" className="border-t border-atx-line-soft py-24">
      <div className="mx-auto max-w-[1320px] px-7">
        <div className="grid items-start gap-10 lg:grid-cols-[1fr_1.2fr]">
          <div>
            <AtxEyebrow number="08">Benchmarks</AtxEyebrow>
            <h2 className="mt-3 font-serif text-[clamp(28px,3.2vw,40px)] leading-[1.15] tracking-[-0.01em] text-atx-ink">
              Measurements
              <br />
              linked to
              <br />
              <em className="italic text-atx-accent">evidence.</em>
            </h2>
          </div>
          <p className="text-[15px] leading-[1.65] text-atx-ink-mid">
            Release comparisons require verified installed artifacts, offline
            correctness checks, raw samples and a recorded environment. See the{" "}
            <a href="https://github.com/VibeTensor/attestix/tree/main/benchmarks" className="underline">
              benchmark methodology
            </a>{" "}
            for workloads and exclusions. Numeric results remain pending until
            an actual run is linked; these measurements are not a service SLA.
          </p>
        </div>

        <div className="mt-14 grid gap-5 md:grid-cols-2 lg:grid-cols-4">
          {BENCHES.map((b) => (
            <div
              key={b.label}
              className="flex flex-col gap-4 rounded-atx-md border border-atx-line-soft bg-atx-panel p-6"
            >
              <div className="font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-dim">
                {b.label}
              </div>
              <div className="flex items-baseline gap-2">
                <span className="font-serif text-[44px] leading-none text-atx-ink">
                  {b.value}
                </span>
                <span className="font-mono-atx text-[11px] uppercase tracking-[0.1em] text-atx-ink-dim">
                  {b.unit}
                </span>
              </div>
              <p className="text-[12.5px] leading-[1.55] text-atx-ink-mid">
                {b.detail}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
