import { Icons } from "@/components/icons";

export const BLUR_FADE_DELAY = 0.15;

export const ATTESTIX_VERSION =
  process.env.NEXT_PUBLIC_ATTESTIX_VERSION || "0.4.1";

export const siteConfig = {
  name: "Attestix",
  version: ATTESTIX_VERSION,
  description: "Make your AI agents EU AI Act compliant with cryptographically verifiable proof. Open-source compliance automation, identity, and trust scoring.",
  cta: "Get Started",
  url: process.env.NEXT_PUBLIC_APP_URL || "https://attestix.io",
  keywords: [
    "AI Agent Identity",
    "W3C Verifiable Credentials",
    "EU AI Act Compliance",
    "MCP Tools",
    "Decentralized Identity",
    "UCAN Delegation",
    "Blockchain Anchoring",
    "AI Attestation",
  ],
  links: {
    email: "info@vibetensor.com",
    twitter: "https://x.com/vibetensor",
    github: "https://github.com/VibeTensor/attestix",
    pypi: "https://pypi.org/project/attestix/",
    docs: "/docs",
    mcpRegistry:
      "https://registry.modelcontextprotocol.io",
  },
  hero: {
    title: "Attestix",
    description:
      "The EU AI Act takes effect August 2, 2026. Non-compliant organizations face fines up to EUR 35 million or 7% of global revenue. Attestix is like TurboTax for AI compliance: it automates the documentation, identity verification, and audit trails your AI agents need to stay legal. Install once, drop into LangChain, OpenAI Agents SDK, or CrewAI, and generate cryptographic proof of compliance on every run.",
    cta: "pip install attestix",
    ctaDescription: "Stable 0.4.1 - 585 tests passing (494 functional + 91 RFC / W3C conformance benchmarks). Real LangChain, OpenAI Agents SDK, and CrewAI integrations. Apache 2.0. Single-maintainer project; no independent third-party security audit yet.",
  },
  // 4-tier model. Single source of truth: attestix-cloud-plan/18-TIER-MATRIX.md
  // (OSS free, self-host / Cloud Free / Cloud Pro / Cloud Enterprise).
  // CTA destinations are honest: checkout is NOT wired (no payment keys, no M4
  // billing backend). Pro/Free route to the waitlist, OSS to GitHub/PyPI,
  // Enterprise to sales. See src/lib/billing.ts for the documented seam.
  pricing: [
    {
      name: "OSS",
      tagline: "Self-host, free forever",
      price: { monthly: "$0", yearly: "$0" },
      frequency: { monthly: "forever · Apache 2.0", yearly: "forever · Apache 2.0" },
      description:
        "The complete attestation toolkit. Every cryptographic primitive and standards-conformance claim is here, reproducible offline. Run it on your own infrastructure.",
      features: [
        "47 MCP tools, full Python core + npm verifier (attestix)",
        "Ed25519 / JCS / RFC 6962 Merkle, W3C VC + DID, UCAN",
        "Local SQLite storage",
        "Base L2 Sepolia testnet anchoring (BYO testnet ETH)",
        "Compliance MCP tools + GDPR Article 17 erasure",
        "Bundle import + export, CLI",
      ],
      cta: "Get started",
      ctaHref: "https://github.com/VibeTensor/attestix",
      ctaKind: "external" as const,
      highlight: false,
    },
    {
      name: "Cloud Free",
      tagline: "Hosted, no card",
      price: { monthly: "$0", yearly: "$0" },
      frequency: { monthly: "hosted · capped usage", yearly: "hosted · capped usage" },
      description:
        "The same OSS capabilities, run by us. One workspace, hosted Postgres, nothing to operate. The funnel step: start here, then move to Pro when you outgrow the caps.",
      features: [
        "Hosted dashboard, no database to run",
        "1 workspace (capped usage)",
        "Up to 2 team members",
        "Sepolia testnet anchoring (100 / month)",
        "Bundle export (portability is a right)",
        "Community support",
      ],
      cta: "Join the waitlist",
      ctaHref: "/demo-call?plan=free",
      ctaKind: "waitlist" as const,
      highlight: false,
    },
    {
      name: "Cloud Pro",
      tagline: "Hosted, production",
      price: { monthly: "$99", yearly: "$99" },
      frequency: { monthly: "/ month / workspace", yearly: "/ month / workspace" },
      description:
        "Production hosting with team management, webhooks, and mainnet anchoring (planned). You pay us to run the operation (managed Postgres, workers, dispatcher), not for capability.",
      features: [
        "Everything in Cloud Free, uncapped",
        "Up to 10 team members + RBAC",
        "Webhooks: 5 endpoints, HMAC + dual-sign rotation",
        "Base mainnet anchoring (planned; testnet today)",
        "EU or US data residency",
        "Email + Slack support",
      ],
      cta: "Notify me",
      ctaHref: "/demo-call?plan=pro",
      ctaKind: "waitlist" as const,
      highlight: true,
    },
    {
      name: "Cloud Enterprise",
      tagline: "Regulated scale",
      price: { monthly: "Custom", yearly: "Custom" },
      frequency: { monthly: "contact sales", yearly: "contact sales" },
      description:
        "For regulated operators with SSO, BYOK, residency, and SLA requirements. Custom legal and customer-funded compliance attestation packs.",
      features: [
        "Everything in Pro, unlimited",
        "SSO / SAML / SCIM + custom roles",
        "Custom residency (India, Middle East, country-specific)",
        "BYOK: HSM / KMS signing keys",
        "Cold archive (R2/S3, 7-year), dedicated workers, SLA",
        "DPA / BAA + customer-funded SOC 2 / ISO 42001 packs",
      ],
      cta: "Contact sales",
      ctaHref: "/demo-call?plan=enterprise",
      ctaKind: "sales" as const,
      highlight: false,
    },
  ],
  footer: {
    socialLinks: [
      {
        icon: <Icons.github className="h-5 w-5" />,
        url: "https://github.com/VibeTensor/attestix",
      },
      {
        icon: <Icons.twitter className="h-5 w-5" />,
        url: "https://x.com/vibetensor",
      },
    ],
    linkGroups: [
      {
        title: "Resources",
        links: [
          { text: "Documentation", url: "/docs", external: false },
          { text: "Research Paper", url: "/docs/project/research", external: false },
          { text: "Blog", url: "/blog", external: false },
        ],
      },
      {
        title: "Project",
        links: [
          { text: "PyPI", url: "https://pypi.org/project/attestix/", external: true },
          { text: "MCP Registry", url: "https://registry.modelcontextprotocol.io", external: true },
          { text: "GitHub", url: "https://github.com/VibeTensor/attestix", external: true },
        ],
      },
      {
        title: "Company",
        links: [
          { text: "Pricing", url: "/pricing", external: false },
          { text: "FAQ", url: "/faq", external: false },
          { text: "Community", url: "/community", external: false },
        ],
      },
    ],
    bottomText: "Apache 2.0 License. Built by VibeTensor.",
    brandText: "ATTESTIX",
  },

  problem: {
    title: "The Problem",
    stats: [
      "EUR 35M maximum fine",
      "7% of global annual revenue",
      "August 2, 2026 enforcement date",
    ],
    description:
      "Every organization deploying AI in the European Union will need to prove their systems are compliant with the EU AI Act. Today, most teams rely on manual documentation, static PDFs, and spreadsheets that cannot be independently verified. There is no standard way for AI agents to carry proof of identity, authorization, or regulatory compliance. Attestix closes that gap with open-source tooling that generates cryptographic proof of compliance, identity, and trust for every AI agent in your stack.",
  },

  // Named testimonials are quoted with the reviewer's explicit permission,
  // but rendered anonymously on the public site. The renderer hides `name`
  // when `anonymous` is true and shows "Name on file" instead. Keep `name`
  // populated internally for our own records; only `role`, `company`,
  // `event`, `venue` and the quote itself are visible to the public.
  highlights: [
    {
      id: 1,
      text: "This looks great. I would love to see exactly how the anchoring layer is being used in Attestix.",
      name: "Steve Dakh",
      anonymous: true as const,
      role: "Public attestation infrastructure engineer",
      company: "Speaking in personal capacity",
      validation: "technical" as const,
      context: "On the cryptographic anchoring layer",
      event: "Direct Correspondence",
      venue: "2026",
    },
    {
      id: 2,
      text: "Very well positioned product. I was building something very similar.",
      name: "Laisha Wadhwa",
      anonymous: true as const,
      role: "Web3 integration engineer",
      company: "Speaking in personal capacity",
      validation: "product" as const,
      context: "On Attestix positioning in the agent-identity space",
      event: "Discovery Call",
      venue: "Remote / 2026",
    },
    {
      id: 3,
      text: "Very aligned with the GenAI governance architectures I have been working on.",
      name: "Anindya Biswas",
      anonymous: true as const,
      role: "Director, GenAI governance",
      company: "Enterprise AI risk practice",
      validation: "architecture" as const,
      context: "On Attestix fit with enterprise AI governance",
      event: "Direct Discussion",
      venue: "2026",
    },
    {
      id: 5,
      text: "Highly relevant to EU AI Act compliance. Focus on articles 9 to 15.",
      name: "Hanene Brachemi Meftah",
      anonymous: true as const,
      role: "AI privacy researcher",
      company: "European public research lab",
      validation: "research" as const,
      context: "On Attestix scope against the EU AI Act high-risk article set",
      event: "Direct Correspondence",
      venue: "2026",
    },
    {
      id: 6,
      text: "This is something even I had been working on, around AI provenance.",
      name: "Rishabh Pathak",
      anonymous: true as const,
      role: "Senior software engineer",
      company: "Fortune 500 transportation",
      validation: "product" as const,
      context: "On AI provenance as an enterprise need",
      event: "Direct Correspondence",
      venue: "2026",
    },
  ],

  faq: [
    {
      question: "Why does my organization need Attestix?",
      answer:
        "The EU AI Act enforcement begins August 2, 2026 with fines up to EUR 35 million or 7% of global annual revenue for non-compliance. Most compliance tools only generate static PDF reports that cannot be independently verified. Attestix produces cryptographically signed, machine-verifiable proof of compliance that auditors and regulators can validate in seconds. Every credential, audit trail, and identity attestation is backed by digital signatures and optional blockchain anchoring.",
    },
    {
      question: "Who is Attestix for?",
      answer:
        "Attestix serves AI startups selling into the EU market, compliance teams preparing for EU AI Act enforcement, enterprises deploying AI agents at scale, and any developer building with the Model Context Protocol (MCP). If your AI systems need to demonstrate accountability, traceability, or regulatory compliance, Attestix provides the infrastructure to prove it.",
    },
    {
      question: "What happens if I'm not EU AI Act compliant by August 2026?",
      answer:
        "Organizations deploying non-compliant AI systems face fines of up to EUR 35 million or 7% of global annual revenue, whichever is higher. National market surveillance authorities can order non-compliant systems to be withdrawn from the market entirely. The regulation applies to any organization offering AI systems in the EU, regardless of where the organization is headquartered. Attestix helps you build compliance into your AI agents from day one rather than retrofitting before the deadline.",
    },
    {
      question: "What is Attestix?",
      answer:
        "Attestix is an open-source attestation infrastructure for AI agents. It covers verifiable identity, W3C credentials, delegation chains, compliance declarations, provenance tracking, reputation scoring, and blockchain anchoring across 9 modules.",
    },
    {
      question: "How do I install Attestix?",
      answer:
        'Install via pip: "pip install attestix". Then configure your MCP client to connect to the Attestix server. Full setup takes under 5 minutes.',
    },
    {
      question: "What standards does Attestix implement?",
      answer:
        "Attestix implements W3C Verifiable Credentials (VC Data Model 1.1), W3C Decentralized Identifiers (DIDs), UCAN delegation (based on JWT), Ed25519 signatures (RFC 8032), and Ethereum Attestation Service (EAS) for blockchain anchoring.",
    },
    {
      question: "What is the current maturity level?",
      answer:
        `Attestix v${ATTESTIX_VERSION} is the current stable release. It includes 585 tests across functional, end-to-end, and conformance benchmark suites (494 functional + 91 RFC / W3C conformance) covering all 9 modules, plus real integrations with LangChain, OpenAI Agents SDK, and CrewAI. GitHub Actions CI runs the full pytest matrix, lint, and security scans on every push. Single-maintainer project; no independent third-party security audit has been performed yet. Treat it as you would any pre-1.0 open-source crypto stack: pin the version, review the diff, and test thoroughly before relying on it in production.`,
    },
    {
      question: "Does Attestix work with LangChain, OpenAI Agents SDK, or CrewAI?",
      answer:
        "Yes, all three are real integrations rather than examples or shims. LangChain uses a BaseCallbackHandler that writes every tool call, LLM call, and chain step to the Attestix audit trail with hash chaining. OpenAI Agents SDK uses MCPServerStdio so Attestix tools appear as native MCP tools. CrewAI attaches Attestix to the mcps field on every agent, giving each crew member full attestation capabilities. You can also use Attestix via its MCP server from any MCP-compatible client (Claude Desktop, Cursor, Continue, Windsurf, VS Code).",
    },
    {
      question: "How does blockchain anchoring work?",
      answer:
        "Attestix anchors identity and credential hashes to Base L2 testnet via the Ethereum Attestation Service (EAS). It supports both individual anchoring and Merkle batch anchoring for cost efficiency. Anchored records are tamper-proof and independently verifiable on Base Sepolia testnet. Mainnet schema registration is planned for a future release.",
    },
    {
      question: "Can I use Attestix without blockchain?",
      answer:
        "Yes. Blockchain anchoring is optional. All core features (identity, credentials, delegation, compliance, provenance, reputation) work fully without any blockchain dependency.",
    },
  ],

};

export type SiteConfig = typeof siteConfig;
