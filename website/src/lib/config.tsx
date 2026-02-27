import { Icons } from "@/components/icons";
import {
  FingerprintIcon,
  GitForkIcon,
  FileSearchIcon,
  LinkIcon,
  ScaleIcon,
  ShieldCheckIcon,
} from "lucide-react";

export const BLUR_FADE_DELAY = 0.15;

export const siteConfig = {
  name: "Attestix",
  description: "Attestation Infrastructure for AI Agents",
  cta: "Get Started",
  url: process.env.NEXT_PUBLIC_APP_URL || "https://attestix.vibetensor.com",
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
    twitter: "https://twitter.com/vibetensor",
    github: "https://github.com/VibeTensor/attestix",
    pypi: "https://pypi.org/project/attestix/",
    docs: "https://docs.attestix.vibetensor.com",
    mcpRegistry:
      "https://registry.modelcontextprotocol.io",
  },
  hero: {
    title: "Attestix",
    description:
      "Verifiable identity, W3C credentials, delegation chains, and reputation scoring for every AI agent. Built to support regulatory documentation workflows.",
    cta: "pip install attestix",
    ctaDescription: "Open source. Apache 2.0 license.",
  },
  features: [
    {
      name: "W3C Verifiable Credentials",
      description:
        "Issue and verify Ed25519Signature2020 credentials and verifiable presentations following W3C standards.",
      icon: <ShieldCheckIcon className="h-6 w-6" />,
    },
    {
      name: "Regulatory Compliance Tools",
      description:
        "Risk classification, conformity assessments, and structured declaration generation for compliance workflows.",
      icon: <ScaleIcon className="h-6 w-6" />,
    },
    {
      name: "Decentralized Identity",
      description:
        "did:key and did:web resolution with UAIT bridge connecting MCP, A2A, and DID ecosystems.",
      icon: <FingerprintIcon className="h-6 w-6" />,
    },
    {
      name: "UCAN Delegation",
      description:
        "Capability-based delegation with signed JWT tokens, permission scoping, and revocation support.",
      icon: <GitForkIcon className="h-6 w-6" />,
    },
    {
      name: "Provenance Tracking",
      description:
        "Record training data, model lineage, and hash-chained audit trails for complete transparency.",
      icon: <FileSearchIcon className="h-6 w-6" />,
    },
    {
      name: "Blockchain Anchoring",
      description:
        "Anchor identities and credentials to Base L2 via EAS with Merkle batch support for tamper-proof records.",
      icon: <LinkIcon className="h-6 w-6" />,
    },
  ],
  pricing: [
    {
      name: "Open Source",
      price: { monthly: "Free", yearly: "Free" },
      frequency: { monthly: "forever", yearly: "forever" },
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
        url: "https://twitter.com/vibetensor",
      },
    ],
    links: [
      { text: "Documentation", url: "https://docs.attestix.vibetensor.com" },
      { text: "PyPI", url: "https://pypi.org/project/attestix/" },
      {
        text: "MCP Registry",
        url: "https://registry.modelcontextprotocol.io",
      },
      {
        text: "Research Paper",
        url: "https://docs.attestix.vibetensor.com/research/",
      },
      { text: "GitHub", url: "https://github.com/VibeTensor/attestix" },
    ],
    bottomText: "Apache 2.0 License. Built by VibeTensor.",
    brandText: "ATTESTIX",
  },

  highlights: [
    {
      id: 1,
      text: "Attestix provides the cryptographic identity layer that every AI agent needs. W3C Verifiable Credentials, UCAN delegation, and blockchain anchoring in a single MCP server.",
      name: "Pavan Kumar Dubasi",
      role: "Creator",
      company: "VibeTensor",
      image: "https://avatars.githubusercontent.com/u/52927921?v=4",
    },
    {
      id: 2,
      text: "Attestix generates machine-readable, cryptographically signed declarations that can be independently verified without trusting the issuer. It is a documentation and evidence tooling system, not a compliance guarantee.",
      name: "Design Principle",
      role: "From the Whitepaper",
      company: "Architecture Overview",
      image: undefined,
    },
    {
      id: 3,
      text: "47 MCP tools across 9 modules with 272+ tests and conformance benchmarks validating 5 W3C and IETF standards for verifiable agent identity.",
      name: "By the Numbers",
      role: "Open Source",
      company: "Apache 2.0 License",
      image: undefined,
    },
  ],

  faq: [
    {
      question: "What is Attestix?",
      answer:
        "Attestix is an open-source attestation infrastructure for AI agents. It provides 47 MCP tools across 9 modules for verifiable identity, W3C credentials, delegation chains, compliance declarations, provenance tracking, reputation scoring, and blockchain anchoring.",
    },
    {
      question: "How do I install Attestix?",
      answer:
        'Install via pip: "pip install attestix". Then configure your MCP client to connect to the Attestix server. Full setup takes under 5 minutes.',
    },
    {
      question: "What standards does Attestix implement?",
      answer:
        "Attestix implements W3C Verifiable Credentials (VC Data Model 2.0), W3C Decentralized Identifiers (DIDs), UCAN delegation (based on JWT), Ed25519 signatures (RFC 8032), and Ethereum Attestation Service (EAS) for blockchain anchoring.",
    },
    {
      question: "What is the current maturity level?",
      answer:
        "Attestix v0.2.2 is in active development (beta). It includes 272+ tests across functional, end-to-end, and conformance benchmark suites covering all 9 modules. We recommend thorough testing before production deployment.",
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
