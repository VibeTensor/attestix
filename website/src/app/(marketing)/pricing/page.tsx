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
			\u2713
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
			className={`mt-7 inline-flex h-10 items-center justify-center rounded-atx-md px-5 text-[13px] font-medium transition-colors ${ctaClasses(tier.highlight)}`}
		>
			{tier.cta} &rarr;
		</a>
	) : (
		<Link
			href={tier.ctaHref}
			className={`mt-7 inline-flex h-10 items-center justify-center rounded-atx-md px-5 text-[13px] font-medium transition-colors ${ctaClasses(tier.highlight)}`}
		>
			{tier.cta} &rarr;
		</Link>
	);

	return (
		<div
			className={`relative flex flex-col rounded-atx-md border p-6 transition-colors ${
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
						popular
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
					Not a checkout. Self-serve billing (Stripe for cards, Razorpay for
					UPI/INR) is coming as we finish the billing backend  -  until then we
					onboard you directly.
				</p>
			) : null}
		</div>
	);
}

export default function PricingPage() {
	return (
		<section className="mx-auto max-w-[1320px] px-7 py-24">
			{/* ----- Hero -------------------------------------------------------- */}
			<div className="grid items-start gap-10 lg:grid-cols-[1fr_1.1fr]">
				<div>
					<AtxEyebrow>Pricing</AtxEyebrow>
					<h1 className="mt-3 font-serif text-[clamp(36px,4.8vw,60px)] leading-[1.05] tracking-[-0.012em] text-atx-ink">
						Start free, self-host
						<br />
						forever, or{" "}
						<em className="italic text-atx-accent">let us run it.</em>
					</h1>
				</div>
				<p className="text-[15px] leading-[1.65] text-atx-ink-mid">
					The Python toolkit is open source under Apache 2.0. Its documented verification profile supports integrity checks and governance evidence. Hosted plans are proposals, subject to availability and operating acceptance; this page does not promise enterprise controls or a production service.
				</p>
			</div>

			{/* ----- Tier cards -------------------------------------------------- */}
			<div className="mt-14 grid gap-5 md:grid-cols-2 xl:grid-cols-4">
				{siteConfig.pricing.map((tier) => (
					<TierCard key={tier.name} tier={tier} />
				))}
			</div>

			<p className="mt-6 text-[12px] leading-[1.6] text-atx-ink-dim">
				Hosted pricing, availability and scope must be confirmed separately. A proposed price or plan label is not a service commitment.
			</p>

			{/* ----- OSS forever-free -------------------------------------------- */}
			<div className="mt-20">
				<AtxEyebrow>Open-source capabilities</AtxEyebrow>
				<h2 className="mt-3 font-serif text-[clamp(26px,3.2vw,38px)] leading-[1.1] tracking-[-0.01em] text-atx-ink">
					Review what is implemented
					<br />
					<em className="italic text-atx-accent">in the public source.</em>
				</h2>
				<p className="mt-4 max-w-[760px] text-[14px] leading-[1.65] text-atx-ink-mid">
					Use the public repositories to review implementation, license and verification limits. Self-hosting requires your own operating controls; hosted terms are agreed separately.
				</p>

				<div className="mt-8 grid gap-px overflow-hidden rounded-atx-md border border-atx-line-soft bg-atx-line-soft sm:grid-cols-2 lg:grid-cols-3">
					{FOREVER_FREE.map((item, i) => (
						<div
							key={item.title}
							className="flex gap-3 bg-atx-panel p-5"
						>
							<span className="mt-0.5 font-mono-atx text-[11px] text-atx-accent">
								{String(i + 1).padStart(2, "0")}
							</span>
							<div>
								<div className="text-[13.5px] leading-[1.4] text-atx-ink">
									{item.title}
								</div>
								<div className="mt-1 text-[11.5px] leading-[1.45] text-atx-ink-dim">
									{item.note}
								</div>
							</div>
						</div>
					))}
				</div>
			</div>

			{/* ----- Detailed comparison table ----------------------------------- */}
			<div className="mt-20">
				<AtxEyebrow>Compare every tier</AtxEyebrow>
				<h2 className="mt-3 font-serif text-[clamp(26px,3.2vw,38px)] leading-[1.1] tracking-[-0.01em] text-atx-ink">
					Source capabilities and proposed services.
				</h2>

				<div className="mt-8 overflow-x-auto rounded-atx-md border border-atx-line-soft">
					<table className="w-full min-w-[760px] border-collapse text-left text-[13px]">
						<thead className="bg-atx-bg-sunken">
							<tr>
								<th className="border-b border-atx-line-soft px-4 py-3 font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-faint">
									Capability
								</th>
								{TIER_COLS.map((col) => (
									<th
										key={col}
										className="border-b border-atx-line-soft px-4 py-3 text-center font-mono-atx text-[10.5px] uppercase tracking-[0.12em] text-atx-ink-faint"
									>
										{col}
									</th>
								))}
							</tr>
						</thead>
						<tbody>
							{COMPARE.map((group) => (
								<Fragment key={group.heading}>
									<tr className="bg-atx-panel-hi">
										<td
											colSpan={5}
											className="border-b border-atx-line-soft px-4 py-2.5 font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-dim"
										>
											{group.heading}
										</td>
									</tr>
									{group.rows.map((row) => (
										<tr key={row.label} className="bg-atx-panel">
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
				<p className="mt-3 text-[11.5px] leading-[1.55] text-atx-ink-dim">
					&quot;self-host&quot; means operator-managed source. Hosted columns are proposals requiring separate availability and acceptance review.
				</p>
			</div>

			{/* ----- FAQ --------------------------------------------------------- */}
			<div className="mt-20">
				<AtxEyebrow>Questions</AtxEyebrow>
				<h2 className="mt-3 font-serif text-[clamp(26px,3.2vw,38px)] leading-[1.1] tracking-[-0.01em] text-atx-ink">
					Honest answers.
				</h2>

				<div className="mt-8 grid gap-px overflow-hidden rounded-atx-md border border-atx-line-soft bg-atx-line-soft">
					{FAQ.map((item) => (
						<div key={item.q} className="bg-atx-panel p-6">
							<div className="font-mono-atx text-[13px] text-atx-ink">
								{item.q}
							</div>
							<p className="mt-2 max-w-[860px] text-[13.5px] leading-[1.65] text-atx-ink-mid">
								{item.a}
							</p>
						</div>
					))}
				</div>
			</div>

			{/* ----- Footer compliance line -------------------------------------- */}
			<div className="mt-16 rounded-atx-md border border-atx-line-soft bg-atx-bg-sunken p-6">
				<p className="text-[12.5px] leading-[1.6] text-atx-ink-dim">
					Attestix records signed evidence for governance workflows. Applicability depends on the system and operator role. Recorded documentation, a signature or a plan label does not establish legal conformity or certification.
				</p>
			</div>
		</section>
	);
}
