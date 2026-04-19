import { AtxEyebrow } from "@/components/atx/atx-eyebrow";

interface Bench {
  label: string;
  value: string;
  unit: string;
  detail: string;
  spark: number[];
}

const BENCHES: Bench[] = [
  {
    label: "Ed25519 sign + verify",
    value: "0.28",
    unit: "ms median",
    detail: "p95 = 0.41 ms / 10,000 iterations on commodity hardware",
    spark: [14, 15, 13, 14, 15, 14, 14, 13, 14, 14, 13, 14],
  },
  {
    label: "Merkle batch anchor",
    value: "1000",
    unit: "artifacts / tx",
    detail: "Proof: 32 bytes per artifact. Depth log2(n).",
    spark: [4, 6, 8, 10, 12, 14, 16, 20, 24, 30, 40, 64],
  },
  {
    label: "VC issuance end-to-end",
    value: "3.2",
    unit: "ms median",
    detail: "Canonicalise (JCS) + sign (Ed25519) + persist",
    spark: [18, 17, 16, 17, 15, 16, 15, 15, 14, 15, 14, 14],
  },
  {
    label: "Audit chain verify",
    value: "42",
    unit: "ms / 10k entries",
    detail: "SHA-256 re-chain + signature batch verify",
    spark: [30, 32, 34, 34, 36, 38, 38, 40, 40, 41, 41, 42],
  },
];

function Sparkline({ data }: { data: number[] }) {
  const max = Math.max(...data, 1);
  const min = Math.min(...data);
  const range = max - min || 1;
  const w = 140;
  const h = 36;
  const step = w / (data.length - 1);
  const points = data
    .map((v, i) => {
      const x = i * step;
      const y = h - ((v - min) / range) * h;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");
  return (
    <svg
      width={w}
      height={h}
      viewBox={`0 0 ${w} ${h}`}
      aria-hidden
      className="text-atx-accent"
    >
      <polyline
        fill="none"
        stroke="currentColor"
        strokeWidth="1.25"
        points={points}
      />
    </svg>
  );
}

export function BenchmarksSection() {
  return (
    <section id="benchmarks" className="border-t border-atx-line-soft py-24">
      <div className="mx-auto max-w-[1320px] px-7">
        <div className="grid items-start gap-10 lg:grid-cols-[1fr_1.2fr]">
          <div>
            <AtxEyebrow number="08">Benchmarks</AtxEyebrow>
            <h2 className="mt-3 font-serif text-[clamp(28px,3.2vw,40px)] leading-[1.15] tracking-[-0.01em] text-atx-ink">
              Fast enough
              <br />
              to sit in the
              <br />
              <em className="italic text-atx-accent">hot path.</em>
            </h2>
          </div>
          <p className="text-[15px] leading-[1.65] text-atx-ink-mid">
            Illustrative performance targets derived from the conformance
            benchmark suite. Attestix stays under a millisecond for
            sign-verify, under 5 ms end-to-end for credential issuance, and
            verifies a 10k-entry audit chain in under 50 ms on commodity
            hardware. Run{" "}
            <code className="rounded-atx-xs border border-atx-line-soft bg-atx-bg-sunken px-1.5 py-0.5 font-mono-atx text-[12px] text-atx-accent">
              pytest tests/benchmarks/
            </code>{" "}
            to reproduce on your own machine.
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
              <Sparkline data={b.spark} />
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
