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
				hosted <span className="text-atx-ink">operations</span>, not capability.
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
				<code className="font-mono-atx text-[13px] text-atx-ink">
					attestix export
				</code>
				; Cloud exports the same wire format. See the{" "}
				<Link href="/spec/bundle/v1" className="text-atx-ink underline decoration-atx-line underline-offset-4 transition-colors duration-200 hover:decoration-atx-ink-dim">
					bundle wire-format spec
				</Link>{" "}
				and verify any bundle offline with the{" "}
				<Link href="/verify" className="text-atx-ink underline decoration-atx-line underline-offset-4 transition-colors duration-200 hover:decoration-atx-ink-dim">
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
				No. Sepolia <span className="text-atx-ink">testnet</span> anchoring is
				free everywhere (you bring your own testnet ETH). Base{" "}
				<span className="text-atx-ink">mainnet</span> anchoring is pay-as-you-go
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
	return <span className="text-[13px] text-atx-ink-mid">{value}</span>;
}

function ctaClasses(highlight: boolean) {
	return highlight
		? "bg-atx-accent text-[oklch(0.14_0.01_180)] hover:bg-atx-accent-deep"
		: "border border-atx-line text-atx-ink-mid hover:border-atx-ink-dim hover:text-atx-ink";
}

function TierCard({ tier }: { tier: Tier }) {
	const isWaitlist = tier.ctaKind === "waitlist";
	const external = tier.ctaKind === "external";

	const cta = external ? (
		<a
			href={tier.ctaHref}
			target="_blank"
			rel="noopener noreferrer"
			className={`mt-7 inline-flex items-center justify-center rounded-full px-6 py-3 text-[15px] font-medium transition-colors duration-200 ${ctaClasses(tier.highlight)}`}
		>
			{tier.cta} &rarr;
		</a>
	) : (
		<Link
			href={tier.ctaHref}
			className={`mt-7 inline-flex items-center justify-center rounded-full px-6 py-3 text-[15px] font-medium transition-colors duration-200 ${ctaClasses(tier.highlight)}`}
		>
			{tier.cta} &rarr;
		</Link>
	);

	return (
		<div
			className={`relative flex flex-col rounded-2xl border p-6 transition-colors duration-200 ${
				tier.highlight
					? "border-atx-accent/30 bg-atx-accent/[0.05]"
					: "border-atx-line bg-atx-panel/60 hover:border-atx-ink-dim"
			}`}
		>
			<div className="flex items-center justify-between gap-3">
				<h3 className="text-[19px] font-semibold tracking-[-0.48px] text-atx-ink">
					{tier.name}
				</h3>
				{tier.name === "OSS" ? (
					<span className="rounded-full bg-atx-accent/15 px-2.5 py-0.5 text-[12px] font-medium text-atx-accent">
						Apache 2.0
					</span>
				) : tier.highlight ? (
					<span className="rounded-full bg-atx-accent/15 px-2.5 py-0.5 text-[12px] font-medium text-atx-accent">
						Popular
					</span>
				) : null}
			</div>

			<div className="mt-5 flex items-baseline gap-2">
				<div className="text-[40px] font-normal leading-none tracking-[-0.03em] text-atx-ink">
					{tier.price.monthly}
				</div>
				<div className="text-[13px] text-atx-ink-dim">
					{tier.frequency.monthly}
				</div>
			</div>

			{tier.name === "Cloud Pro" ? (
				<p className="mt-2 text-[13px] leading-[1.5] text-atx-ink-dim">
					≈ ₹{INR_INDICATIVE}/mo, billed in INR for Indian customers via
					Razorpay. Indicative — final INR set at checkout.
				</p>
			) : null}

			<p className="mt-4 text-[15px] leading-[1.6] text-atx-ink-mid">
				{tier.description}
			</p>

			<ul className="mt-5 flex-1 space-y-2.5">
				{tier.features.map((feature) => (
					<li
						key={feature}
						className="flex gap-2.5 text-[14px] leading-[1.55] text-atx-ink-mid"
					>
						<span className="mt-2 block h-1 w-1 shrink-0 rounded-full bg-atx-accent" />
						{feature}
					</li>
				))}
			</ul>

			{cta}

			{isWaitlist ? (
				<p className="mt-3 text-[13px] leading-[1.5] text-atx-ink-dim">
					Not a checkout. Self-serve billing (Stripe for cards, Razorpay for
					UPI/INR) is coming as we finish the billing backend — until then we
					onboard you directly.
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
						Start free, self-host forever, or{" "}
						<span className="text-atx-accent">let us run it.</span>
					</h1>
					<p className={`mx-auto mt-5 max-w-[640px] [text-wrap:balance] ${LEAD}`}>
						Every cryptographic primitive and standards-conformance claim lives in
						the open-source release — Apache 2.0, free forever, reproducible
						offline. Cloud Free, Pro, and Enterprise add hosted{" "}
						<span className="text-atx-ink">operations</span> on top of the same
						capabilities: managed Postgres, workers, webhooks, residency, SSO. You
						never pay to unlock crypto you could run yourself.
					</p>
				</div>

				<div className="mx-auto mt-12 w-full max-w-[1200px]">
					<div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
						{siteConfig.pricing.map((tier) => (
							<TierCard key={tier.name} tier={tier} />
						))}
					</div>

					<p className="mx-auto mt-6 max-w-[720px] text-center text-[13px] leading-[1.6] text-atx-ink-dim">
						Pro is{" "}
						<span className="text-atx-ink">${PRO_PRICE_USD}/mo per workspace</span>;
						the agreed launch target. Enterprise is priced per deployment — SSO,
						BYOK, residency, SLA, and DPA scope drive the quote. Self-serve checkout
						(Stripe + Razorpay) is launching soon; we onboard directly until then.
					</p>
				</div>
			</section>

			{/* ----- OSS forever-free -------------------------------------------- */}
			<section className="bg-atx-bg-elev py-20">
				<div className={`${WRAP} text-center`}>
					<AtxEyebrow>The OSS forever-free commitment</AtxEyebrow>
					<h2 className={`mt-3 ${H2}`}>
						Nine things that never move{" "}
						<span className="text-atx-accent">into a paid tier.</span>
					</h2>
					<p className={`mx-auto mt-4 max-w-[760px] ${LEAD}`}>
						This is the line we hold. No feature is removed from OSS to drive a
						cloud upgrade — paywalls exist only on operational scale (managed
						uptime, SSO config, BYOK HSM, SLA). The capability is always shippable
						by self-hosters.
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
						<AtxEyebrow>Compare every tier</AtxEyebrow>
						<h2 className={`mt-3 ${H2}`}>What ships in each plan.</h2>
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
						&quot;self-host&quot; means the capability exists in OSS for you to run
						yourself — the Cloud tiers run it for you. Derived from the canonical
						tier matrix; if a row is not here, it is not yet a committed public
						claim.
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
		</>
	);
}
