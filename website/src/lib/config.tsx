import { Icons } from "@/components/icons";

export const BLUR_FADE_DELAY = 0.15;

export const ATTESTIX_VERSION =
  process.env.NEXT_PUBLIC_ATTESTIX_VERSION || "0.4.1";

export const siteConfig = {
  name: "Attestix",
  version: ATTESTIX_VERSION,
  description: "Build verifiable identity and signed evidence for AI-agent governance. Open-source documentation tooling, audit trails, and trust scoring.",
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
      "The EU AI Act applies in stages, with obligations depending on your role and system classification. Attestix helps record identity, documentation, and signed audit evidence. Cryptographic integrity supports your assessment; it does not establish legal compliance.",
    cta: "pip install attestix",
    ctaDescription: "Review the current source, tests and verifier boundaries. Registry releases and hosted deployment are separate from main-branch changes.",
  },
  // (OSS free, self-host / Cloud Free / Cloud Pro / Cloud Enterprise).
  // CTA destinations are honest: checkout is NOT wired (no payment keys, no M4
  // billing backend). Pro/Free route to the waitlist, OSS to GitHub/PyPI,
  // Enterprise to sales. See src/lib/billing.ts for the documented seam.
  pricing: [
    {
      name: "OSS", tagline: "Self-host the open-source toolkit",
      price: { monthly: "$0", yearly: "$0" },
      frequency: { monthly: "Apache 2.0", yearly: "Apache 2.0" },
      description: "Python identity, credentials, delegation and provenance tools. Review the documented verification profile and deployment boundaries.",
      features: ["Python library, CLI, MCP and REST", "Signed credentials and presentations", "Local JSON storage", "Operator-recorded governance evidence", "Public verifier repositories"],
      cta: "Get started", ctaHref: "https://github.com/VibeTensor/attestix",
      ctaKind: "external" as const, highlight: false,
    },
    {
      name: "Cloud Free", tagline: "Planned hosted evaluation",
      price: { monthly: "Planned", yearly: "Planned" },
      frequency: { monthly: "availability subject to review", yearly: "availability subject to review" },
      description: "A proposed hosted evaluation path. Availability, included features, operating terms and data location require confirmation.",
      features: ["Join the availability list", "Evaluation scope agreed separately"],
      cta: "Join the waitlist", ctaHref: "/demo-call?plan=free",
      ctaKind: "waitlist" as const, highlight: false,
    },
    {
      name: "Cloud Pro", tagline: "Planned hosted service",
      price: { monthly: "Planned", yearly: "Planned" },
      frequency: { monthly: "terms to be confirmed", yearly: "terms to be confirmed" },
      description: "Discuss your hosted-service requirements. This page is not a commitment that a paid service, production deployment or enterprise control is available.",
      features: ["Availability and scope reviewed separately", "Operational acceptance required before production"],
      cta: "Notify me", ctaHref: "/demo-call?plan=pro",
      ctaKind: "waitlist" as const, highlight: false,
    },
    {
      name: "Cloud Enterprise", tagline: "Requirements discussion",
      price: { monthly: "Discuss", yearly: "Discuss" },
      frequency: { monthly: "scope agreed separately", yearly: "scope agreed separately" },
      description: "Discuss identity, custody, residency, recovery and support requirements. Contract terms and controls must be reviewed and accepted before service use.",
      features: ["Requirements and operating scope review", "No automatic conformity or certification assurance"],
      cta: "Contact sales", ctaHref: "/demo-call?plan=enterprise",
      ctaKind: "sales" as const, highlight: false,
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
      "Violation-specific penalty ceilings",
      "Lower applicable caps for SMEs",
      "Role-specific application dates",
    ],
    description:
      "AI governance requires evidence that teams can inspect and verify. Attestix records signed identity claims, delegated authority, and audit trails. Determine applicable EU AI Act obligations through a role- and system-specific assessment; signed records alone do not establish conformity.",
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
        "Attestix provides signed, machine-verifiable records for your governance and audit workflows. Verify their integrity and evaluate the underlying claims separately. EU AI Act obligations and application dates depend on your role, system classification, and the amended legislation.",
    },
    {
      question: "Who is Attestix for?",
      answer:
        "Attestix serves AI startups selling into the EU market, compliance teams preparing for EU AI Act enforcement, enterprises deploying AI agents at scale, and any developer building with the Model Context Protocol (MCP). If your AI systems need to demonstrate accountability, traceability, or regulatory compliance, Attestix provides infrastructure to record supporting evidence.",
    },
    {
      question: "How do I determine my EU AI Act obligations?",
      answer:
        "Applicable duties and sanctions depend on the infringement, your role, and system classification, with specific treatment for SMEs. Attestix helps organize evidence for an assessment; it does not provide legal advice or guarantee compliance. Review Regulation (EU) 2024/1689 as amended, including Regulation (EU) 2026/1744.",
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
        `This site describes current main source. Check the selected package release notes and repository validation; source merges do not publish registry artifacts or establish operating acceptance.`,
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
