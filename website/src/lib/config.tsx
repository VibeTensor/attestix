import { Icons } from "@/components/icons";

export const BLUR_FADE_DELAY = 0.15;

export const ATTESTIX_VERSION =
  process.env.NEXT_PUBLIC_ATTESTIX_VERSION || "0.2.4";

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
      "The EU AI Act takes effect August 2, 2026. Non-compliant organizations face fines up to EUR 35 million or 7% of global revenue. Attestix is like TurboTax for AI compliance: it automates the documentation, identity verification, and audit trails your AI agents need to stay legal. Install once, generate cryptographic proof of compliance on every run.",
    cta: "pip install attestix",
    ctaDescription: "Open source. Apache 2.0 license.",
  },
  pricing: [
    {
      name: "Open Source",
      price: { monthly: "$0", yearly: "$0" },
      frequency: { monthly: "open source", yearly: "open source" },
      description: "Everything you need for AI agent attestation.",
      features: [
        "47 MCP tools across 9 modules",
        "W3C Verifiable Credentials",
        "Regulatory compliance tools",
        "Decentralized identity (DID)",
        "UCAN delegation chains",
        "Blockchain anchoring (Base L2)",
        "Apache 2.0 license",
      ],
      cta: "Install Now",
    },
    {
      name: "Enterprise",
      price: { monthly: "Custom", yearly: "Custom" },
      frequency: { monthly: "contact us", yearly: "contact us" },
      description: "For organizations with advanced compliance needs.",
      features: [
        "All open source features",
        "Dedicated support and SLA",
        "Custom compliance profiles",
        "On-premises deployment",
        "Priority feature requests",
        "Security audit reports",
      ],
      cta: "Contact Us",
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

  highlights: [
    {
      id: 4,
      text: "How do we design where we can have trust? This is one of the very active conversations that we are having right now.",
      name: "Julie Zhuo",
      role: "Founder, Sundial",
      company: "Ex-VP Product Design, Meta (14 years)",

      validation: "problem" as const,
      context: "On trust infrastructure for AI agent workflows",
      askedBy: "Pavan Kumar Dubasi",
      question: "As AI agents start making autonomous decisions, who is responsible when an agent makes a bad data-driven decision? How does Sundial think about the trust and accountability layer for agent workflows? Should AI agents have verifiable proof of work before they can act?",
      event: "Fireside Chat with Julie Zhuo | South Park Commons",
      venue: "SPC India, HSR Layout, Bengaluru - March 3, 2026",
      detail: "Julie confirmed that designing trust for AI agents is an active, unsolved problem at Sundial. She described the management chain model where a human somewhere in the chain owns accountability. This maps directly to Attestix's UCAN delegation chains, where every agent action traces back to a human principal through cryptographic proof of authorization.",
    },
    {
      id: 5,
      text: "How do humans trust each other? Benefit of the doubt, then validate work, then trust more. We build structures to minimise mistakes given the context.",
      name: "Julie Zhuo",
      role: "Founder, Sundial",
      company: "Ex-VP Product Design, Meta (14 years)",

      validation: "problem" as const,
      context: "Describing progressive trust, the pattern Attestix implements",
      askedBy: "Pavan Kumar Dubasi",
      question: "As AI agents start making autonomous decisions, who is responsible when an agent makes a bad data-driven decision? How does Sundial think about the trust and accountability layer for agent workflows? Should AI agents have verifiable proof of work before they can act?",
      event: "Fireside Chat with Julie Zhuo | South Park Commons",
      venue: "SPC India, HSR Layout, Bengaluru - March 3, 2026",
      detail: "Julie described how humans build trust progressively: start with benefit of the doubt, validate work, then extend more trust. This is exactly the pattern Attestix's reputation scoring module implements. Agents earn trust scores based on verified actions, compliance history, and audit trail integrity. Progressive trust, but cryptographically verifiable.",
    },
    {
      id: 6,
      text: "Code reviews as a process to generate trust. That is how trust is created, because humans are not perfect. We always need structured verification.",
      name: "Julie Zhuo",
      role: "Founder, Sundial",
      company: "Ex-VP Product Design, Meta (14 years)",

      validation: "problem" as const,
      context: "Structured verification for AI agents is what Attestix automates",
      askedBy: "Pavan Kumar Dubasi",
      question: "As AI agents start making autonomous decisions, who is responsible when an agent makes a bad data-driven decision? How does Sundial think about the trust and accountability layer for agent workflows? Should AI agents have verifiable proof of work before they can act?",
      event: "Fireside Chat with Julie Zhuo | South Park Commons",
      venue: "SPC India, HSR Layout, Bengaluru - March 3, 2026",
      detail: "Julie sees code reviews as the human model for trust generation: structured review processes that catch mistakes before they ship. Attestix automates this exact pattern for AI agents. Instead of code reviews, agents undergo compliance verification, identity attestation, and authorization checks before they can act. Structured verification, but automated and cryptographically signed.",
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
        `Attestix v${ATTESTIX_VERSION} is in active development (beta). It includes 284 tests across functional, end-to-end, and conformance benchmark suites covering all 9 modules. We recommend thorough testing before production deployment.`,
    },
    {
      question: "How does blockchain anchoring work?",
      answer:
        "Attestix anchors identity and credential hashes to Base L2 via the Ethereum Attestation Service (EAS). It supports both individual anchoring and Merkle batch anchoring for cost efficiency. Anchored records are tamper-proof and independently verifiable on-chain.",
    },
    {
      question: "Can I use Attestix without blockchain?",
      answer:
        "Yes. Blockchain anchoring is optional. All core features (identity, credentials, delegation, compliance, provenance, reputation) work fully without any blockchain dependency.",
    },
  ],

};

export type SiteConfig = typeof siteConfig;
