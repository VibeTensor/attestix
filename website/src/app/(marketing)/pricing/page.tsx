import { Fragment, type ReactNode } from "react";
import Link from "next/link";
import { AtxEyebrow } from "@/components/atx/atx-eyebrow";
import { siteConfig } from "@/lib/config";
import { constructMetadata } from "@/lib/utils";
import {
	PRO_PRICE_INR_INDICATIVE,
	PRO_PRICE_USD,
} from "@/lib/billing";

export const metadata = constructMetadata({
	title: "Pricing",
	description:
		"Start free, self-host forever, or let us run it. Attestix OSS is Apache 2.0 and free forever; Cloud Free, Cloud Pro ($99/mo), and Enterprise add hosted operations on top of the same open-source capabilities.",
});

type Tier = (typeof siteConfig.pricing)[number];

const INR_INDICATIVE = PRO_PRICE_INR_INDICATIVE.toLocaleString("en-IN");

// ---------------------------------------------------------------------------
// Feature-comparison rows. Pulled directly from
// attestix-cloud-plan/18-TIER-MATRIX.md "The matrix" table. Order: [OSS,
// Cloud Free, Cloud Pro, Cloud Enterprise]. "yes" / "no" / a short string.
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
	{
		heading: "Core capability (OSS — never paywalled)",
		rows: [
			{ label: "Python core + npm verifier", cells: ["yes", "yes", "yes", "yes"] },
			{ label: "MCP server (47 tools)", cells: ["yes", "yes", "yes", "yes"] },
			{
				label: "Framework integrations (LangChain, OpenAI Agents, CrewAI)",
				cells: ["yes", "yes", "yes", "yes"],
			},
			{
				label: "Ed25519 signing, JCS, RFC 6962 Merkle",
				cells: ["yes", "yes", "yes", "yes"],
			},
			{
				label: "W3C VC / DID, UCAN delegation chains",
				cells: ["yes", "yes", "yes", "yes"],
			},
			{
				label: "Compliance MCP tools (Annex IV, Art 47, conformity record)",
				cells: ["yes", "yes", "yes", "yes"],
			},
			{ label: "GDPR Article 17 erasure tooling", cells: ["yes", "yes", "yes", "yes"] },
			{ label: "Bundle import", cells: ["yes", "yes", "yes", "yes"] },
			{
				label: "Bundle export (portability is a right)",
				cells: ["local", "yes", "yes", "yes"],
			},
			{
				label: "CLI (serve, verify-chain, import, export, list)",
				cells: ["yes", "yes", "yes", "yes"],
			},
		],
	},
	{
		heading: "Storage & anchoring",
		rows: [
			{ label: "Local SQLite storage", cells: ["yes", "no", "no", "no"] },
			{ label: "Hosted Postgres (no DB to run)", cells: ["no", "yes", "yes", "yes"] },
			{
				label: "Base L2 Sepolia testnet anchoring",
				cells: ["yes", "100 / mo", "yes", "yes"],
			},
			{
				label: "Base mainnet anchoring (pay-as-you-go gas)",
				cells: ["no", "no", "planned", "planned cadence"],
			},
		],
	},
	{
		heading: "Hosted operations",
		rows: [
			{ label: "Hosted dashboard (app.attestix.io)", cells: ["no", "yes", "yes", "yes"] },
			{
				label: "Workspaces",
				cells: ["self-host", "1", "1 + add-ons", "unlimited"],
			},
			{
				label: "Team members + RBAC",
				cells: ["self-host", "2", "10", "unlimited"],
			},
			{
				label: "Webhooks dispatcher (HMAC-signed, retried)",
				cells: ["self-host", "no", "5 endpoints", "unlimited"],
			},
			{
				label: "Standard data residency (EU or US)",
				cells: ["self-host", "yes", "yes", "yes"],
			},
			{
				label: "Support",
				cells: ["community", "community", "email + Slack", "+ dedicated CSM"],
			},
		],
	},
	{
		heading: "Enterprise controls",
		rows: [
			{ label: "SSO / SAML / SCIM", cells: ["no", "no", "no", "yes"] },
			{ label: "Custom roles + per-route permissions", cells: ["no", "no", "no", "yes"] },
			{
				label: "Custom residency (India, Middle East, country-specific)",
				cells: ["no", "no", "no", "yes"],
			},
			{ label: "BYOK — HSM / KMS signing keys", cells: ["no", "no", "no", "yes"] },
			{
				label: "Audit cold-archive (R2/S3, 7-year retention)",
				cells: ["no", "no", "no", "yes"],
			},
			{
				label: "Dedicated worker pool + SLA (99.9%)",
				cells: ["no", "no", "no", "yes"],
			},
			{ label: "DPA / BAA / custom legal", cells: ["no", "no", "no", "yes"] },
			{
				label: "Customer-funded SOC 2 / ISO 42001 attestation packs",
				cells: ["no", "no", "no", "yes"],
			},
		],
	},
];

const TIER_COLS = ["OSS", "Cloud Free", "Cloud Pro", "Cloud Enterprise"];

// OSS forever-free commitments — verbatim list from 18-TIER-MATRIX.md §"The OSS
// forever-free commitment". These never move into a paid tier.
const FOREVER_FREE: { title: string; note: string }[] = [
	{ title: "Ed25519 signing + verification", note: "RFC 8032" },
	{
		title: "JCS canonicalization",
		note: "canonical form published at /spec/canonical/v1",
	},
	{ title: "RFC 6962 Merkle batches", note: "tamper-evident audit trail" },
	{ title: "W3C VC Data Model 1.1", note: "issuance + verification" },
	{ title: "UCAN delegation chains", note: "parent + attenuation" },
	{ title: "did:key + did:web resolvers", note: "offline DID resolution" },
	{ title: "Bundle import", note: "the round-trip is symmetric" },
	{
		title: "Base L2 Sepolia testnet anchoring",
		note: "free, bring your own testnet ETH",
	},
	{ title: "All 47 MCP tools", note: "as of 2026-05-28" },
];

const FAQ: { q: string; a: ReactNode }[] = [
	{
		q: "Is the OSS really free forever?",
		a: (
			<>
				Yes. Attestix OSS is Apache 2.0 and self-hosted. Every cryptographic
				primitive and standards-conformance claim lives in the open-source
				release and is reproducible offline. Nine capabilities are committed to
				never move into a paid tier — they are listed above. The Cloud sells
				hosted <em className="italic text-atx-ink">operations</em>, not capability.
			</>
		),
	},
	{
		q: "What's the difference between self-host and Cloud Free?",
		a: (
			<>
				They run the same capabilities. With OSS you operate the database,
				workers, and dispatcher yourself. Cloud Free runs all of that for you —
				hosted Postgres, one workspace, nothing to manage — capped so you can
				try the hosted path before moving to Pro. No feature is removed from OSS
				to drive the upgrade; you pay Cloud for the operational labour, not for
				access.
			</>
		),
	},
	{
		q: "How does billing work?",
		a: (
			<>
				Self-serve checkout — Stripe for international cards, Razorpay for
				INR/UPI for Indian customers — is being built as we finish the billing
				backend. Until it ships, we onboard Pro and Enterprise customers
				directly: pick &quot;Notify me&quot; or &quot;Contact sales&quot; and we
				reply within one business day. There is no checkout button that does not
				work yet — that is deliberate.
			</>
		),
	},
	{
		q: "Can I export my data?",
		a: (
			<>
				Always, on every tier including Cloud Free. Portability is a right, not a
				paid feature. OSS runs{" "}
				<code className="font-mono-atx text-[12.5px] text-atx-ink">
					attestix export
				</code>
				; Cloud exports the same wire format. See the{" "}
				<Link href="/spec/bundle/v1" className="text-atx-accent hover:underline">
					bundle wire-format spec
				</Link>{" "}
				and verify any bundle offline with the{" "}
				<Link href="/verify" className="text-atx-accent hover:underline">
					verifier
				</Link>
				.
			</>
		),
	},
	{
		q: "Is mainnet anchoring free?",
		a: (
			<>
				No. Sepolia <em className="italic text-atx-ink">testnet</em> anchoring is
				free everywhere (you bring your own testnet ETH). Base{" "}
				<em className="italic text-atx-ink">mainnet</em> anchoring is pay-as-you-go
				gas, available on Cloud Pro and above. Mainnet schema registration is
				planned; today the spec targets Base Sepolia (chain 84532).
			</>
		),
	},
];

function Check() {
	return (
		<span aria-label="included" className="text-atx-ok">
			✓
		</span>
	);
}
function Dash() {
	return (
		<span aria-label="not included" className="text-atx-ink-faint">
			—
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
					≈ ₹{INR_INDICATIVE}/mo, billed in INR for Indian customers via
					Razorpay. Indicative — final INR set at checkout.
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
					UPI/INR) is coming as we finish the billing backend — until then we
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
					Every cryptographic primitive and standards-conformance claim lives in
					the open-source release — Apache 2.0, free forever, reproducible
					offline. Cloud Free, Pro, and Enterprise add hosted{" "}
					<em className="italic text-atx-ink">operations</em> on top of the same
					capabilities: managed Postgres, workers, webhooks, residency, SSO. You
					never pay to unlock crypto you could run yourself.
				</p>
			</div>

			{/* ----- Tier cards -------------------------------------------------- */}
			<div className="mt-14 grid gap-5 md:grid-cols-2 xl:grid-cols-4">
				{siteConfig.pricing.map((tier) => (
					<TierCard key={tier.name} tier={tier} />
				))}
			</div>

			<p className="mt-6 text-[12px] leading-[1.6] text-atx-ink-dim">
				Pro is{" "}
				<span className="text-atx-ink">${PRO_PRICE_USD}/mo per workspace</span>;
				the agreed launch target. Enterprise is priced per deployment — SSO,
				BYOK, residency, SLA, and DPA scope drive the quote. Self-serve checkout
				(Stripe + Razorpay) is launching soon; we onboard directly until then.
			</p>

			{/* ----- OSS forever-free -------------------------------------------- */}
			<div className="mt-20">
				<AtxEyebrow>The OSS forever-free commitment</AtxEyebrow>
				<h2 className="mt-3 font-serif text-[clamp(26px,3.2vw,38px)] leading-[1.1] tracking-[-0.01em] text-atx-ink">
					Nine things that never move
					<br />
					<em className="italic text-atx-accent">into a paid tier.</em>
				</h2>
				<p className="mt-4 max-w-[760px] text-[14px] leading-[1.65] text-atx-ink-mid">
					This is the line we hold. No feature is removed from OSS to drive a
					cloud upgrade — paywalls exist only on operational scale (managed
					uptime, SSO config, BYOK HSM, SLA). The capability is always shippable
					by self-hosters.
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
					What ships in each plan.
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
					&quot;self-host&quot; means the capability exists in OSS for you to run
					yourself — the Cloud tiers run it for you. Derived from the canonical
					tier matrix; if a row is not here, it is not yet a committed public
					claim.
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
					Attestix is evidence tooling, not a guarantor of compliance. The
					provider of an AI system remains liable under EU AI Act Articles
					16&ndash;22; Attestix produces the cryptographic evidence — identity,
					credentials, hash-chained audit trail, conformity records — that
					supports your own assessment. Compliance attestation packs (SOC 2, ISO
					42001) on Enterprise are customer-funded and scoped per engagement, not
					a shipped certification.
				</p>
			</div>
		</section>
	);
}
