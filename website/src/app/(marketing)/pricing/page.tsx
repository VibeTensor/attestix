import { Fragment, type ReactNode } from "react";
import Link from "next/link";
import { AtxEyebrow } from "@/components/atx/atx-eyebrow";
import { siteConfig } from "@/lib/config";
import { constructMetadata } from "@/lib/utils";

export const metadata = constructMetadata({
	title: "Pricing",
	description:
		"Self-host the Apache 2.0 toolkit or discuss proposed hosted-service availability. Source features and operating acceptance are documented separately.",
});

type Tier = (typeof siteConfig.pricing)[number];


// ---------------------------------------------------------------------------
// Public capability and planned-service copy.
// ---------------------------------------------------------------------------
type Cell = "yes" | "no" | string;
interface CompareRow {
	label: string;
	cells: [Cell, Cell, Cell, Cell];
}
interface CompareGroup {
	heading: string;
	rows: CompareRow[];
}

const COMPARE: CompareGroup[] = [
  { heading: "Open-source source capabilities", rows: [
    { label: "Python library, MCP, CLI and REST", cells: ["yes", "planned", "planned", "review"] },
    { label: "Signed credential and presentation verification", cells: ["yes", "planned", "planned", "review"] },
    { label: "Governance evidence records", cells: ["yes", "planned", "planned", "review"] },
    { label: "Local JSON storage", cells: ["yes", "review", "review", "review"] },
  ] },
  { heading: "Hosted-service acceptance", rows: [
    { label: "Availability, features and contract scope", cells: ["self-host", "confirm", "confirm", "confirm"] },
    { label: "Custody, residency, recovery and support", cells: ["operator responsibility", "review", "review", "review"] },
  ] },
];

const TIER_COLS = ["OSS", "Cloud Free", "Cloud Pro", "Cloud Enterprise"];

// Public license and implementation references, not hosted-service guarantees.
const FOREVER_FREE: { title: string; note: string }[] = [
  { title: "Apache 2.0 Python toolkit", note: "Review the repository license and release notes" },
  { title: "Credential verification profile", note: "Integrity is separate from trust, authorization and legal conformity" },
  { title: "MCP, CLI and REST interfaces", note: "Configure authentication, storage and key custody before deployment" },
];

const FAQ: { q: string; a: ReactNode }[] = [
  { q: "What is available in source?", a: <>The public Python toolkit and verifier repositories describe their current main implementations. A merge does not imply that registry packages or hosted services have been updated.</> },
  { q: "Are hosted plans available?", a: <>Hosted plans are proposals. Use the availability links to discuss evaluation scope, operating acceptance and terms before relying on a hosted service.</> },
  { q: "Does Attestix establish compliance?", a: <>Attestix records signed evidence for governance workflows. It does not establish legal conformity, certification, issuer trust or the truth of recorded claims.</> },
  { q: "Who operates self-hosted deployments?", a: <>The operator manages authentication, storage, keys, backups, monitoring, trust and replay policy. Review the current repository documentation before production use.</> },
];

function Check() {
	return (
		<span aria-label="included" className="text-atx-ok">
			Included
		</span>
	);
}
function Dash() {
	return (
		<span aria-label="not included" className="text-atx-ink-faint">
			 -
		</span>
	);
}

function Cell({ value }: { value: Cell }) {
	if (value === "yes") return <Check />;
	if (value === "no") return <Dash />;
	return <span className="text-[12px] text-atx-ink-mid">{value}</span>;
}

function ctaClasses(highlight: boolean) {
	return highlight
		? "bg-atx-accent text-[oklch(0.14_0.01_180)] hover:bg-atx-accent-deep"
		: "border border-atx-line text-atx-ink hover:border-atx-ink-dim hover:bg-atx-bg-sunken";
}

function TierCard({ tier }: { tier: Tier }) {
	const isWaitlist = tier.ctaKind === "waitlist";
	const external = tier.ctaKind === "external";

	const cta = external ? (
		<a
			href={tier.ctaHref}
			target="_blank"
			rel="noopener noreferrer"
			className={`mt-7 inline-flex h-10 items-center justify-center rounded-2xl px-5 text-[13px] font-medium transition-colors ${ctaClasses(tier.highlight)}`}
		>
			{tier.cta} &rarr;
		</a>
	) : (
		<Link
			href={tier.ctaHref}
			className={`mt-7 inline-flex h-10 items-center justify-center rounded-2xl px-5 text-[13px] font-medium transition-colors ${ctaClasses(tier.highlight)}`}
		>
			{tier.cta} &rarr;
		</Link>
	);

	return (
		<div
			className={`relative flex flex-col rounded-2xl border p-6 transition-colors ${
				tier.highlight
					? "border-atx-accent/50 bg-atx-panel-hi"
					: "border-atx-line-soft bg-atx-panel"
			}`}
		>
			<div className="flex items-center justify-between font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-dim">
				<span>{tier.name}</span>
				{tier.name === "OSS" ? (
					<span className="rounded-atx-xs border border-atx-accent/40 bg-atx-accent-soft px-2 py-0.5 text-atx-accent">
						Apache 2.0
					</span>
				) : tier.highlight ? (
					<span className="rounded-atx-xs border border-atx-accent/40 bg-atx-accent-soft px-2 py-0.5 text-atx-accent">
						planned
					</span>
				) : null}
			</div>

			<div className="mt-4 flex items-baseline gap-2">
				<div className="font-serif text-[40px] leading-none text-atx-ink">
					{tier.price.monthly}
				</div>
				<div className="font-mono-atx text-[10.5px] uppercase tracking-[0.1em] text-atx-ink-dim">
					{tier.frequency.monthly}
				</div>
			</div>

			{tier.name === "Cloud Pro" ? (
				<p className="mt-1.5 text-[11.5px] leading-[1.5] text-atx-ink-dim">
					Availability, pricing, currencies and terms must be confirmed separately.
				</p>
			) : null}

			<p className="mt-3 text-[12.5px] leading-[1.55] text-atx-ink-mid">
				{tier.description}
			</p>

			<ul className="mt-5 flex-1 space-y-2">
				{tier.features.map((feature) => (
					<li
						key={feature}
						className="flex gap-2.5 text-[12.5px] leading-[1.5] text-atx-ink-mid"
					>
						<span className="mt-1.5 block h-1 w-1 shrink-0 rounded-full bg-atx-accent" />
						{feature}
					</li>
				))}
			</ul>

			{cta}

			{isWaitlist ? (
				<p className="mt-3 text-[10.5px] leading-[1.5] text-atx-ink-faint">
              Hosted availability, pricing, billing and contract terms require separate confirmation. This is not a checkout.
            </p>
			) : null}
		</div>
	);
}

const WRAP = "mx-auto w-full max-w-[1200px] px-6";
const H2 =
	"text-[32px] font-medium leading-[1.15] tracking-[-0.8px] text-atx-ink";
const LEAD = "text-[17.5px] leading-[1.6] text-atx-ink-mid";

export default function PricingPage() {
	return (
		<>
			{/* ----- Hero + tier cards ------------------------------------------- */}
			<section className="bg-atx-bg px-6 pb-20 pt-16 md:pt-20">
				<div className="mx-auto max-w-[860px] text-center">
					<AtxEyebrow>Pricing</AtxEyebrow>
					<h1 className="mt-3 text-[clamp(34px,5vw,52px)] font-normal leading-[1.09] tracking-[-0.03em] text-atx-ink [text-wrap:balance]">
						Self-host the toolkit, or discuss{" "}
						<span className="text-atx-accent">proposed hosted plans.</span>
					</h1>
					<p className={`mx-auto mt-5 max-w-[640px] [text-wrap:balance] ${LEAD}`}>
              The Python toolkit is open source under Apache 2.0. Its documented verification profile supports integrity checks and governance evidence. Hosted plans are proposals, subject to availability and operating acceptance; this page does not promise enterprise controls or a production service.
            </p>
				</div>

				<div className="mx-auto mt-12 w-full max-w-[1200px]">
					<div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
						{siteConfig.pricing.map((tier) => (
							<TierCard key={tier.name} tier={tier} />
						))}
					</div>

					<p className="mx-auto mt-6 max-w-[720px] text-center text-[13px] leading-[1.6] text-atx-ink-dim">
              Hosted availability, pricing, currencies, operating controls and contract scope must be confirmed separately before relying on a service.
            </p>
				</div>
			</section>

			{/* ----- OSS forever-free -------------------------------------------- */}
			<section className="bg-atx-bg-elev py-20">
				<div className={`${WRAP} text-center`}>
					<AtxEyebrow>Open-source capabilities</AtxEyebrow>
					<h2 className={`mt-3 ${H2}`}>
						Evaluate the public source and its{" "}
						<span className="text-atx-accent">documented limits.</span>
					</h2>
					<p className={`mx-auto mt-4 max-w-[760px] ${LEAD}`}>
              Review the Apache 2.0 license and current release documentation. Operators manage authentication, storage, keys, recovery, monitoring, trust and incident handling.
            </p>

					<div className="mt-12 grid gap-4 text-left sm:grid-cols-2 lg:grid-cols-3">
						{FOREVER_FREE.map((item) => (
							<div
								key={item.title}
								className="flex gap-3 rounded-2xl border border-atx-line bg-atx-panel/60 p-5 transition-colors duration-200 hover:border-atx-ink-dim"
							>
								<Check />
								<div>
									<div className="text-[15px] font-medium leading-[1.4] text-atx-ink">
										{item.title}
									</div>
									<div className="mt-1 text-[13px] leading-[1.5] text-atx-ink-dim">
										{item.note}
									</div>
								</div>
							</div>
						))}
					</div>
				</div>
			</section>

			{/* ----- Detailed comparison table ----------------------------------- */}
			<section className="bg-atx-bg py-20">
				<div className={WRAP}>
					<div className="text-center">
						<AtxEyebrow>Source and proposed plans</AtxEyebrow>
						<h2 className={`mt-3 ${H2}`}>Capabilities and acceptance requirements.</h2>
					</div>

					<div className="mt-12 overflow-x-auto rounded-2xl border border-atx-line">
						<table className="w-full min-w-[760px] border-collapse text-left text-[14px]">
							<thead className="bg-atx-bg-sunken">
								<tr>
									<th className="border-b border-atx-line-soft px-4 py-3.5 text-[13px] font-medium text-atx-ink-dim">
										Capability
									</th>
									{TIER_COLS.map((col) => (
										<th
											key={col}
											className="border-b border-atx-line-soft px-4 py-3.5 text-center text-[13px] font-medium text-atx-ink"
										>
											{col}
										</th>
									))}
								</tr>
							</thead>
							<tbody>
								{COMPARE.map((group) => (
									<Fragment key={group.heading}>
										<tr className="bg-atx-panel">
											<td
												colSpan={5}
												className="border-b border-atx-line-soft px-4 py-3 text-[14px] font-medium text-atx-accent"
											>
												{group.heading}
											</td>
										</tr>
										{group.rows.map((row) => (
											<tr key={row.label} className="bg-atx-panel/60">
												<td className="border-b border-atx-line-soft px-4 py-3 text-atx-ink-mid">
													{row.label}
												</td>
												{row.cells.map((cell, ci) => (
													<td
														key={ci}
														className="border-b border-atx-line-soft px-4 py-3 text-center"
													>
														<Cell value={cell} />
													</td>
												))}
											</tr>
										))}
									</Fragment>
								))}
							</tbody>
						</table>
					</div>
					<p className="mx-auto mt-4 max-w-[720px] text-center text-[13px] leading-[1.6] text-atx-ink-dim">
              This table distinguishes public source capabilities from proposed hosted-service acceptance work. Planned or review entries do not establish current availability or production readiness.
            </p>
				</div>
			</section>

			{/* ----- FAQ --------------------------------------------------------- */}
			<section className="bg-atx-bg-elev py-20">
				<div className="mx-auto w-full max-w-[720px] px-6">
					<div className="text-center">
						<AtxEyebrow>Questions</AtxEyebrow>
						<h2 className={`mt-3 ${H2}`}>Honest answers.</h2>
					</div>

					<div className="mt-10 rounded-xl border border-atx-line bg-atx-panel/60 px-6">
						{FAQ.map((item, i) => (
							<div
								key={item.q}
								className={`py-5 ${i ? "border-t border-atx-line-soft" : ""}`}
							>
								<h3 className="text-[15px] font-medium text-atx-ink">{item.q}</h3>
								<p className="mt-2 text-[15px] leading-[1.65] text-atx-ink-mid">
									{item.a}
								</p>
							</div>
						))}
					</div>

					{/* ----- Footer compliance line ------------------------------------ */}
					<p className="mt-10 text-center text-[13px] leading-[1.6] text-atx-ink-dim">
              Attestix records signed evidence for governance workflows. It does not establish SOC 2 or ISO certification, GDPR compliance, EU AI Act conformity, trusted issuers or truth of recorded claims.
            </p>
				</div>
			</section>
		</>
	);
}
