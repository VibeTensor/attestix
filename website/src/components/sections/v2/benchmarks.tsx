const WRAP = "mx-auto w-full max-w-[1200px] px-6";
const H2 = "text-[32px] font-medium leading-[1.15] tracking-[-0.8px] text-atx-ink";
const LEAD = "text-[17.5px] leading-[1.6] text-atx-ink-mid";

interface Bench {
  label: string;
  value: string;
  unit: string;
  detail: string;
  spark: number[];
  // Set when the figure times a third-party library rather than Attestix code.
  measures?: string;
}

const BENCHES: Bench[] = [
  {
    label: "Ed25519 sign + verify",
    value: "0.22",
    unit: "ms median",
    detail: "1,000 iterations on commodity hardware",
    spark: [14, 15, 13, 14, 15, 14, 14, 13, 14, 14, 13, 14],
    measures:
      "Measures the pyca/cryptography Ed25519 library called through a thin Attestix wrapper, not Attestix itself.",
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
    value: "21",
    unit: "ms median",
    detail: "Canonicalise (JCS) + sign (Ed25519) + persist JSON store",
    spark: [23, 22, 21, 22, 21, 21, 20, 21, 20, 21, 20, 21],
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
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} aria-hidden className="text-atx-accent">
      <polyline fill="none" stroke="currentColor" strokeWidth="1.25" points={points} />
    </svg>
  );
}

export function BenchmarksSection() {
  return (
    <section id="benchmarks" className="scroll-mt-20 bg-atx-bg-elev py-20">
      <div className={WRAP}>
        <div className="text-center">
          <h2 className={H2}>
            Fast enough to sit in the <span className="text-atx-accent">hot path</span>
          </h2>
          <p className={`mx-auto mt-4 max-w-[760px] ${LEAD}`}>
            Representative medians from the conformance benchmark suite. The
            underlying Ed25519 library signs and verifies in under a
            millisecond; Attestix issues a credential end-to-end in around
            21 ms and verifies a 10k-entry audit chain in under 50 ms on
            commodity hardware. Run{" "}
            <code className="rounded-md border border-atx-line-soft bg-atx-bg-sunken px-1.5 py-0.5 font-mono-atx text-[13px] text-atx-accent">
              pytest tests/benchmarks/
            </code>{" "}
            to reproduce on your own machine.
          </p>
        </div>

        <div className="mt-12 grid gap-5 md:grid-cols-2 lg:grid-cols-4">
          {BENCHES.map((b) => (
            <div
              key={b.label}
              className="flex flex-col gap-4 rounded-2xl border border-atx-line bg-atx-panel/60 p-6 transition-colors duration-200 hover:border-atx-ink-dim"
            >
              <div>
                <h3 className="text-[15px] font-medium text-atx-ink">{b.label}</h3>
                {b.measures ? (
                  <span className="mt-2 inline-block rounded-full bg-atx-info/15 px-2.5 py-0.5 text-[12px] font-medium text-atx-info">
                    Library benchmark
                  </span>
                ) : null}
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-[40px] leading-none tracking-[-0.03em] text-atx-accent">{b.value}</span>
                <span className="text-[13px] text-atx-ink-dim">{b.unit}</span>
              </div>
              <Sparkline data={b.spark} />
              <p className="text-[14px] leading-[1.55] text-atx-ink-mid">{b.detail}</p>
              {b.measures ? (
                <p className="text-[13px] leading-[1.55] text-atx-ink-dim">{b.measures}</p>
              ) : null}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
