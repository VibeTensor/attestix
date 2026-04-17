import { Icons } from "@/components/icons";

export const BLUR_FADE_DELAY = 0.15;

export const ATTESTIX_VERSION =
  process.env.NEXT_PUBLIC_ATTESTIX_VERSION || "0.3.0";

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
    ctaDescription: "v0.3.0 - 358 tests passing. Real LangChain, OpenAI Agents SDK, and CrewAI integrations. Apache 2.0 license.",
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
      id: 1,
      text: "I encourage you to continue with your project.",
      name: "Yoshua Bengio",
      role: "Turing Award Laureate",
      company: "Scientific Director, MILA",

      validation: "problem" as const,
      context: "Direct encouragement on the Attestix mission",
      askedBy: "Pavan Kumar Dubasi",
      question: "Shared the Attestix mission and verifiable trust infrastructure approach for AI agents under the EU AI Act.",
      event: "Email Correspondence",
      venue: "February 21, 2026",
      detail: "Professor Bengio, one of the three Turing Award recipients for deep learning and a leading voice in AI safety, reviewed the Attestix pitch and replied with direct encouragement. His endorsement underscores the importance of building verifiable, open source trust infrastructure for autonomous AI agents.",
    },
    {
      id: 2,
      text: "The fact you are open source is really interesting.",
      name: "Alvaro Cabrejas Egea",
      role: "AI Policy Officer",
      company: "EU AI Office, European Commission",

      validation: "problem" as const,
      context: "On the value of open source compliance tooling for the EU AI Act",
      askedBy: "Pavan Kumar Dubasi",
      question: "Walked through how Attestix produces cryptographically verifiable evidence for EU AI Act Articles 16 to 22 while the provider remains legally liable.",
      event: "Direct Discussion on EU AI Act Enforcement",
      venue: "European Commission Outreach - 2026",
      detail: "Alvaro raised the critical liability question of who is responsible when a deployed system is found non compliant. The answer is that providers remain liable under Articles 16 to 22. Attestix is positioned as the evidence generation tool, not a guarantor. Alvaro expressed genuine interest in the open source angle and said he would share the approach with the appropriate team.",
    },
    {
      id: 3,
      text: "I can see how to put a register of compliance and self certify or get a third party certifier to cryptographically sign.",
      name: "Matt Pagett",
      role: "AI Safety Researcher",
      company: "CBAAC Author, NANDA Contributor",

      validation: "problem" as const,
      context: "Describing the exact primitives Attestix already ships",
      askedBy: "Pavan Kumar Dubasi",
      question: "Walked through the Attestix automated compliance attestation flow: UAIT identity, compliance profile, training data records, model lineage, audit trail, Annex V declaration, and auto issued W3C Verifiable Credentials.",
      event: "1 on 1 Discovery Call",
      venue: "Remote - February 27, 2026",
      detail: "Matt framed Attestix as TurboTax for AI compliance: layers of audit protection chosen by risk exposure and budget, with the company still owning final responsibility. He validated the business case, signaled strong alignment with CBAAC and NANDA, and agreed to re engage once he moves to Munich in April or May 2026 to connect Attestix with European compliance buyers.",
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
        `Attestix v${ATTESTIX_VERSION} is in active development (beta). It includes 358 tests across functional, end-to-end, and conformance benchmark suites covering all 9 modules, plus real integrations with LangChain, OpenAI Agents SDK, and CrewAI. GitHub Actions CI runs the full pytest matrix, lint, and security scans on every push. We still recommend thorough testing before production deployment.`,
    },
    {
      question: "Does Attestix work with LangChain, OpenAI Agents SDK, or CrewAI?",
      answer:
        "Yes, all three are real integrations shipped in v0.3.0 rather than examples or shims. LangChain uses a BaseCallbackHandler that writes every tool call, LLM call, and chain step to the Attestix audit trail with hash chaining. OpenAI Agents SDK uses MCPServerStdio so Attestix tools appear as native MCP tools. CrewAI attaches Attestix to the mcps field on every agent, giving each crew member full attestation capabilities. You can also use Attestix via its MCP server from any MCP-compatible client (Claude Desktop, Cursor, Continue, Windsurf, VS Code).",
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
